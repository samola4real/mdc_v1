"""Task 16E reproducible validation. Only catalogue GETs and discovery POSTs leave localhost."""

import argparse
import csv
import gzip
import json
import os
import re
import sys
import time
from collections import Counter
from copy import deepcopy
from itertools import combinations, product
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import requests
from yaml import safe_load

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
ROUTE = "/api/service-discovery/search"
MODE = ("strict", "lenient")
CATEGORIES = {"gear": "precision_gears", "shaft": "precision_shafts", "metal_part": "precision_metal_parts"}
GEAR = "spur_gear"
OWNERS = ("tasowheel", "precipart", "mdc_stage1b_accept_20261126_a")
PRIVATE = {"source_type", "confidence", "source_note", "publication_metadata"}


def named(field, value):
    unit = " mm" if field.endswith("_mm") or field in {"module", "spline_module"} else ""
    return f"{field.removesuffix('_mm').replace('_', ' ')} {value}{unit}"


def scenarios(vocabulary):
    cases = []

    def add(group, name, *, part=GEAR, family="gear", general=None, specs=None, typed=None,
            modes=MODE, live=False, invalid=False, policy=None):
        requirements = {
            key: value for key, value in [
                ("generic_requirements", general),
                ("part_family_specifications", specs),
                ("part_type_specifications", typed),
            ] if value is not None
        }
        for mode in modes:
            base = {
                "contract_version": "1.0", "consumer_id": "task16e-verification",
                "service_category": CATEGORIES[family], "part_family": family,
                "part_type": part, "requirements": requirements,
            }
            if mode == "lenient":
                base["match_policy"] = {"discovery_mode": "lenient"}
            if policy is not None:
                base["match_policy"] = policy
            cases.append({"id": f"E{len(cases) + 1:03}", "group": group, "input": f"{part.replace('_', ' ')} · {name}",
                          "mode": mode, "live": live, "invalid": invalid, "body": base})

    for family, subtypes in vocabulary["part_types"].items():
        for subtype in subtypes:
            add("selection", "no optional criteria", family=family, part=subtype["value"], live=True)
    add("validation", "uncontrolled gear type", part="unsupported_gear", invalid=True, live=True)
    for field, values, live_values in [
        ("module", [0.1, .124, .125, .126, .2, .299, .3, .301, .5, 1, 1.499, 1.5, 1.51, 2, 3, 4, 5, 9.999, 10, 10.01, 12],
         [.125, .3, 1, 1.5, 1.51, 2, 3, 4, 10, 12]),
        ("diametral_pitch", [2, 2.499, 2.5, 2.501, 5, 10, 15.99, 16, 16.01, 20, 50, 84.99, 85, 86, 199.99, 200, 201],
         [2.5, 16, 85, 200, 201]),
        ("outside_diameter_mm", [5, 6, 6.01, 9, 9.99, 10, 10.01, 50, 101.99, 102, 103, 300, 449.99, 450, 451, 700],
         [6, 50, 102, 300, 450, 700]),
    ]:
        for value in values:
            add("gear", named(field, f"exact {value}"), specs={field: {"exact": value}}, live=value in live_values)
        for bounds in ({"min": values[0]}, {"max": values[-1]}, {"min": 10, "max": 50}, {"min": 16, "max": 16}):
            add("gear", named(field, bounds), specs={field: bounds})
    for module, diameter in product((1, 2, 3, 4), (50, 100, 300)):
        dp = round(25.4 / module, 4)
        add("gear-combined", f"module {module} mm, DP {dp}, outside diameter {diameter} mm",
            specs={"module": {"exact": module}, "diametral_pitch": {"exact": dp}, "outside_diameter_mm": {"exact": diameter}},
            live=diameter == 100)
    add("gear-combined", "independent dimensions: module 1 mm plus DP 85", specs={
        "module": {"exact": 1}, "diametral_pitch": {"exact": 85}}, live=True)
    for standard, quality in product(("ISO", "DIN", "ISO 1328"), (3, 4, 5, 6, 7)):
        add("quality", f"{standard} accuracy class {quality} or better",
            specs={"gear_quality": {"standard": standard, "max_class": quality}}, live=quality == 5)
    add("gear", "20 mm spur face width", typed={"face_width_mm": {"exact": 20}}, live=True)
    add("validation", "face width supplied for Worm gear", part="worm_gear", typed={"face_width_mm": {"exact": 20}}, invalid=True)
    for family, part in (("gear", GEAR), ("shaft", "plain_shaft"), ("metal_part", "roller")):
        for quantity in (99, 100, 500, 2000, 2001, 5000):
            add("batch", f"{quantity} pieces", family=family, part=part, general={"batch_size": quantity}, live=family == "gear" and quantity in {500, 5000})
        for kilos in (1, 50, 200, 200.01):
            add("weight", f"{kilos} kg", family=family, part=part, general={"weight_kg": kilos})
        add("technical", "tolerance at most 0.02 mm and surface Ra at most 0.8 µm", family=family, part=part,
            specs={"tolerance_mm": {"max": .02}}, general={"surface_finish_ra_um": {"max": .8}})
    for key in ("materials", "processes", "certifications"):
        codes = [item["value"] for item in vocabulary[key]]
        for count, values in [(1, [(x,) for x in codes]), (2, combinations(codes, 2))]:
            for selected in values:
                live = count == 1 and (key != "processes" or selected[0] in {"machining", "hobbing", "turning"})
                add(key, f"{key}: {', '.join(selected)}", general={key: list(selected)}, live=live)
        for selected in ((), tuple(codes[:3]), tuple(codes), (codes[0], codes[0])):
            add(key, f"{key}: {', '.join(selected) or 'empty'}", general={key: list(selected)})
    for materials, module in product(
        (["steel", "alloyed_carburizing_steel"], ["steel", "titanium"], ["aluminum", "titanium"]), (1, 2, 3, 4, 12)
    ):
        add("materials-combined", f"module {module} mm and {', '.join(materials)}",
            specs={"module": {"exact": module}}, general={"materials": materials}, live=module in {4, 12})
    for limit in (6, 8, 11, 12, 13, 20):
        add("delivery", f"delivery at most {limit} weeks", general={"delivery": {"max_weeks": limit}}, live=limit in {6, 12})
    for module, certs in product((1, 4), (["ISO9001_2015"], ["ISO9001_2015", "ISO14001_2015"], ["AS9100_D"], ["ISO13485_2016", "AS9100_D"])):
        add("combined", f"module {module} mm, Steel/Titanium, Hobbing/Turning, {', '.join(certs)}",
            specs={"module": {"exact": module}},
            general={"materials": ["steel", "titanium"], "processes": ["hobbing", "turning"], "certifications": certs}, live=True)
    for part, typed in {"plain_shaft": {"principal_diameter_mm": 20}, "stepped_shaft": {"number_of_steps": 3},
                        "splined_shaft": {"spline_module": 2}, "worm_shaft": {"worm_module": 2},
                        "hollow_shaft": {"inner_diameter_mm": 15, "wall_thickness_mm": 5}}.items():
        for size in (20, 100, 500, 501):
            add("shaft", f"length {size} mm and diameter 20 mm", part=part, family="shaft",
                specs={"length_mm": {"exact": size}, "outer_diameter_mm": {"exact": 20}}, live=size == 100)
        for field, value in typed.items():
            for required in (value, value + 1):
                add("shaft", named(field, f"exact {required}"), part=part, family="shaft", typed={field: {"exact": required}})
        add("shaft", "family tolerance at most 0.02 mm", part=part, family="shaft", specs={"tolerance_mm": {"max": .02}})
    for part in ("block", "plate", "bracket", "bushing", "roller", "collar"):
        for width in (25, 26, 60):
            dimensional = ({"bounding_box_mm": {"length_mm": {"max": 60}, "width_mm": {"max": width}, "height_mm": {"max": 20}}}
                           if part in {"block", "plate", "bracket"} else
                           {"overall_length_mm": {"max": 60}, "outer_diameter_mm": {"exact": width},
                            "inner_diameter_mm": {"exact": 10}, "tolerance_mm": {"max": .02}})
            add("metal", f"dimensions {dimensional} mm", part=part, family="metal_part", specs=dimensional, live=width == 25)
        dimensions = {"block": {"number_of_holes": 4}, "plate": {"number_of_holes": 4},
                      "bracket": {"vertical_flange_length_mm": 10, "horizontal_flange_length_mm": 12},
                      "bushing": {"flange_diameter_mm": 30}}.get(part, {})
        for field, exact in dimensions.items():
            for value in (exact, exact + 1):
                add("metal", named(field, f"exact {value}"), part=part, family="metal_part", typed={field: {"exact": value}})
    for value in (0, .9):
        add("validation", f"lenient cutoff {value}", modes=("lenient",), policy={"discovery_mode": "lenient", "minimum_score": value},
            invalid=True, live=True)
    add("validation", "invalid discovery mode", modes=("strict",), policy={"discovery_mode": "any"}, invalid=True, live=True)
    add("validation", "separate material grade search", general={"material_grades": ["16MnCr5"]}, invalid=True, live=True)
    add("validation", "invalid certificate alias", general={"certifications": ["EN9100_2018"]}, invalid=True)
    add("validation", "inverted module interval", specs={"module": {"min": 3, "max": 1}}, invalid=True)
    add("validation", "negative batch", general={"batch_size": -1}, invalid=True)
    add("validation", "unknown industry field", general={"industry": ["aerospace"]}, invalid=True)
    for legacy in ("any", "all", "score_only"):
        add("legacy", f"exact Steel with legacy {legacy}", modes=("strict",), general={"materials": ["steel"]},
            policy={"optional_match_mode": legacy, "unknown_policy": "keep_as_unknown", "minimum_score": 1}, live=True)
    add("certifications", "ISO 13485 with applicability unconfirmed", part="collar", family="metal_part",
        general={"certifications": ["ISO13485_2016"]})
    return cases


def public(value, omit=PRIVATE):
    if isinstance(value, dict):
        return {key: public(item, omit) for key, item in value.items() if key not in omit}
    if isinstance(value, list):
        return [public(item, omit) for item in value]
    return value


def confirmed(record):
    return bool(record and record.get("source_type") != "not_confirmed" and record.get("confidence") != "unknown"
                and record.get("support_status") not in {"unknown", "candidate_requiring_confirmation"})


def covers(request, capability):
    if not confirmed(capability):
        return False
    if request and set(request) <= {"length_mm", "width_mm", "height_mm"}:
        return all(covers(value, capability.get(key)) for key, value in request.items())
    if "standard" in request:
        return request["standard"] == capability.get("standard") and capability.get("best_class", float("inf")) <= request["max_class"]
    low = capability.get("min", capability.get("exact"))
    high = capability.get("max", capability.get("exact"))
    return all((low is None or low <= value) and (high is None or value <= high)
               and (key != "exact" or low is not None and high is not None)
               and (key != "min" or low is not None) and (key != "max" or high is not None)
               for key, value in request.items())


def expected(case, records):
    """Independent comparison over frozen publication records and the stated contract."""
    if case["invalid"]:
        return {"http": 400, "results": [], "reason": "Request violates the controlled input or policy contract."}
    body = case["body"]
    request = body["requirements"]
    lenient = case["mode"] == "lenient"
    results = []
    rejected = {}
    for item in records:
        provider = item["provider"]
        for offer in item["offerings"]:
            identity = offer["offering_id"]
            if offer["part_family"] != body["part_family"] or offer["service_category"] != body["service_category"]:
                continue
            if not confirmed(offer) or not any(
                row["part_type"] == body["part_type"] and row.get("support_status") == "confirmed" and confirmed(row)
                for row in offer["supported_part_types"]
            ):
                rejected[identity] = "subtype unconfirmed"
                continue
            evidence = {"matched": [], "unmatched": [], "unknown": []}
            hard_failure = []
            scores = []

            def record(field, asked, available, status="matched"):
                item = {"field": field, "requested": asked}
                if available is not None:
                    item["provided"] = public(available)
                evidence[status].append(item)

            generic = offer.get("generic_capabilities", {})
            for section, capabilities in [
                ("part_family_specifications", offer.get("family_capabilities", {})),
                ("part_type_specifications", offer.get("part_type_capabilities", {}).get(body["part_type"], {})),
            ]:
                for field, value in request.get(section, {}).items():
                    available = capabilities.get(field)
                    if covers(value, available):
                        record(field, value, available)
                    else:
                        hard_failure.append(field)
            for field, value in request.get("generic_requirements", {}).items():
                if field in {"materials", "processes", "certifications"}:
                    if not value:
                        continue
                    key = {"materials": "material", "processes": "process", "certifications": "code"}[field]
                    available = list(generic.get(field, []))
                    if field == "certifications":
                        available = [*provider.get("certifications", []), *available]
                    rows = [row for row in available if confirmed(row)]
                    if lenient and field != "certifications":
                        selections = tuple(dict.fromkeys(value))
                        supported = 0
                        for choice in selections:
                            acceptable = {choice}
                            if field == "materials" and choice == "steel":
                                acceptable.update({"alloyed_carburizing_steel", "stainless_steel"})
                            found = [row for row in rows if row[key] in acceptable]
                            record(field, [choice], found or None, "matched" if found else "unknown")
                            supported += bool(found)
                        scores.append(float(bool(supported)) if field == "materials" else supported / len(selections))
                    elif set(value) <= {row[key] for row in rows}:
                        # The strict evidence envelope shows the full applicable published list.
                        record(field, value, available)
                    else:
                        hard_failure.append(field)
                    continue
                available = generic.get("lead_time_weeks" if field == "delivery" else field)
                asked = value
                if field == "delivery":
                    asked = value["max_weeks"]
                if field in {"surface_finish_ra_um", "tolerance_mm"} and set(value) in ({"exact"}, {"max"}):
                    asked = next(iter(value.values()))
                upper = available.get("max", available.get("exact")) if confirmed(available) else None
                lower = available.get("min") if confirmed(available) else None
                ok = False
                if field == "batch_size":
                    ok = lower is not None and upper is not None and lower <= value <= upper
                elif field == "weight_kg":
                    ok = upper is not None and value <= upper
                elif field in {"surface_finish_ra_um", "tolerance_mm", "delivery"}:
                    bounds = value if field != "delivery" else {"max": asked}
                    ok = upper is not None and bounds.get("min", 0) <= upper <= min(
                        bounds.get("max", float("inf")), bounds.get("exact", float("inf")))
                elif field == "quality":
                    ok = covers(value, available)
                if lenient and field == "delivery":
                    record(field, asked, available, "matched" if ok else "unknown" if upper is None else "unmatched")
                    scores.append(float(ok))
                elif ok:
                    record(field, asked, available)
                else:
                    hard_failure.append(field)
            if hard_failure:
                rejected[identity] = "mandatory " + ", ".join(hard_failure) + " unsatisfied or unconfirmed"
                continue
            score = round(sum(scores) / len(scores), 6) if scores else 1.0
            results.append({"provider": provider["provider_id"], "offering": identity, "score": score,
                            "status": "full_match" if all(n == 1 for n in scores) else "partial_match", **evidence})
    ordered = sorted(results, key=lambda row: (row["provider"], row["offering"]))
    explanation = "Confirmed hard requirements" if ordered else "No confirmed eligible offering"
    if rejected:
        explanation += ". " + "; ".join(f"{key}: {why}" for key, why in rejected.items())
    return {"http": 200, "results": ordered, "reason": explanation}


def normalized(rows):
    return [{"provider": row["provider_id"], "offering": row["offering_id"], **row["match"],
             **{status: [{key: value for key, value in item.items() if key != "reason"}
                         for item in row[f"{status}_capabilities"]] for status in ("matched", "unknown", "unmatched")}}
            for row in rows]


def compare_rows(expected_rows, actual_rows):
    def with_sorted_evidence(rows):
        return [{**row, **{key: sorted(row[key], key=lambda item: json.dumps(item, sort_keys=True))
                           for key in ("matched", "unmatched", "unknown")}} for row in rows]
    return with_sorted_evidence(expected_rows) == with_sorted_evidence(actual_rows)


def fixed_fixtures():
    source = {"source_type": "curated", "confidence": "curated"}
    unknown = {"source_type": "not_confirmed", "confidence": "unknown"}
    range_at = lambda min_value, max_value: {"min": min_value, "max": max_value, **source}
    offers = []
    for family, models in {
        "shaft": {"plain_shaft": {"principal_diameter_mm": 20}, "stepped_shaft": {"number_of_steps": 3},
                  "splined_shaft": {"spline_module": 2}, "worm_shaft": {"worm_module": 2},
                  "hollow_shaft": {"inner_diameter_mm": 15, "wall_thickness_mm": 5}},
        "metal_part": {"block": {"number_of_holes": 4}, "plate": {"number_of_holes": 4},
                       "bracket": {"vertical_flange_length_mm": 10, "horizontal_flange_length_mm": 12},
                       "bushing": {"flange_diameter_mm": 30}, "roller": {}, "collar": {}},
        "gear": {"spur_gear": {"face_width_mm": 20}},
    }.items():
        for part, typed in models.items():
            if family == "shaft":
                specs = {"length_mm": range_at(20, 500), "outer_diameter_mm": range_at(10, 40),
                         "tolerance_mm": {"max": .02, **source}}
            elif part in {"block", "plate", "bracket"}:
                specs = {"bounding_box_mm": {"length_mm": {"max": 60}, "width_mm": {"max": 25},
                                             "height_mm": {"max": 20}}}
            elif family == "metal_part":
                specs = {"overall_length_mm": range_at(10, 60), "outer_diameter_mm": range_at(15, 25),
                         "inner_diameter_mm": range_at(5, 10), "tolerance_mm": {"max": .02, **source}}
            else:
                specs = {"module": range_at(1, 4), "diametral_pitch": range_at(2.5, 85),
                         "outside_diameter_mm": range_at(10, 450)}
            scoped_cert = ([{"code": "AS9100_D", **source}] if part in {"spur_gear", "roller"}
                           else [{"code": "ISO13485_2016", **unknown}] if part == "collar" else [])
            offers.append({"offering_id": "fixture_" + part, "provider_id": "fixture_line",
                           "service_category": CATEGORIES[family], "part_family": family,
                           "name": "Fixture " + part, "support_status": "confirmed",
                           "supported_part_types": [{"part_type": part, "support_status": "confirmed", **source}],
                           "family_capabilities": specs,
                           "part_type_capabilities": {part: {field: {"exact": value, **source} for field, value in typed.items()}},
                           "generic_capabilities": {
                               "materials": [{"material": "steel", "available_grades": ["16MnCr5"], **source}],
                               "processes": [{"process": "turning", "delivery_mode": "unspecified", **source}],
                               "batch_size": range_at(100, 2000), "weight_kg": {"max": 50, **source},
                               "lead_time_weeks": {"max": 12, **source}, "certifications": scoped_cert,
                           }})
            if part == "roller":
                offers[-1]["generic_capabilities"]["surface_finish_ra_um"] = {"max": .8, **source}
    adjacent = deepcopy(next(offer for offer in offers if offer["offering_id"] == "fixture_spur_gear"))
    adjacent["offering_id"] = "fixture_uncertified_spur"
    adjacent["generic_capabilities"]["certifications"] = [{"code": "AS9100_D", **unknown}]
    offers.append(adjacent)
    return [{"provider": {"provider_id": "fixture_line", "display_name": "Synthetic workshop",
                          "certifications": [{"code": "ISO9001_2015", **source}]}, "offerings": offers}]


class Preview:
    def __init__(self, origin):
        if not re.fullmatch(r"https://maasai-mdc-v1-[a-z0-9]+-mdc19\.vercel\.app", origin):
            raise ValueError("Supply the protected deployment URL for the existing MDC project.")
        self.origin = origin
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json", "Accept-Encoding": "identity",
                                     "x-vercel-protection-bypass": os.environ["MDC_VERCEL_PROTECTION_BYPASS"]})

    def call(self, path, body=None):
        reply = self.session.request("POST" if body is not None else "GET", self.origin + path,
                                     json=body, timeout=25, allow_redirects=False)
        if reply.status_code not in {200, 400, 404}:
            raise RuntimeError(f"Stopped at {path} after HTTP {reply.status_code}.")
        return reply.status_code, reply.json() if "json" in reply.headers.get("content-type", "") else {}

    def snapshot(self):
        records = []
        for owner in OWNERS:
            _, provider = self.call(f"/api/providers/{owner}")
            _, listing = self.call(f"/api/providers/{owner}/offerings")
            provider = {key: provider[key] for key in ("provider_id", "provider_name", "country", "certifications")}
            provider["display_name"] = provider.pop("provider_name")
            offers = []
            for item in listing["offerings"]:
                _, offer = self.call(f"/api/offerings/{item['offering_id']}")
                assert offer["provider_id"] == owner and offer["offering_id"] == item["offering_id"]
                assert offer["is_active"]
                assert offer["contract_version"] == "1.0"
                offer["name"] = offer["offering_name"]
                offers.append({key: offer[key] for key in ("offering_id", "provider_id", "name", "part_family", "service_category",
                              "support_status", "supported_part_types", "family_capabilities", "part_type_capabilities", "generic_capabilities")})
            records.append({"provider": provider, "offerings": offers})
        return public(records, {"source_note", "publication_metadata"})


def offline():
    os.environ.update(DJANGO_SETTINGS_MODULE="config.settings", DATABASE_URL="",
                      MDC_CATALOG_SYNC_ENABLED="false", MDC_CATALOG_AUTO_SYNC_ENABLED="false",
                      SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="", SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT="")
    import django
    from django.conf import settings

    settings.DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
    settings.ALLOWED_HOSTS = ["testserver"]
    settings.DEBUG = False
    django.setup()
    from apps.providers.service_discovery_loaders import load_service_discovery_providers
    from apps.search.service_discovery_local_matcher import search_service_discovery_catalog
    from rest_framework.test import APIClient

    client = APIClient()

    def run(body, records):
        with patch("apps.api.views.post_views.search_service_discovery_with_runtime_backends", side_effect=lambda request:
                   search_service_discovery_catalog(request, provider_records=records)):
            response = client.post(ROUTE, body, format="json")
        return response.status_code, response.json()

    return run, load_service_discovery_providers()


def execution(cases, records, send, tag):
    output = []
    for case in cases:
        goal = expected(case, records)
        body = {**case["body"], "request_id": f"16e-{case['id']}-{uuid4().hex}"}
        status, received = send(body)
        actual = normalized(received.get("results", []))
        passed = status == goal["http"] and received.get("contract_version") == "1.0" and compare_rows(goal["results"], actual)
        if status == 200:
            passed = passed and received["request_id"] == body["request_id"] and received["result_count"] == len(actual)
        output.append({**{k: case[k] for k in ("id", "group", "input", "mode")}, "dataset": tag, "http": status,
                       "result": "PASS" if passed else "FAIL", "expected": goal, "actual": actual,
                       "payload": body, "response": public(received)})
    return output


def save(directory, tag, rows):
    directory.mkdir(parents=True, exist_ok=True)
    keys = ("id", "dataset", "group", "input", "mode", "expected_count", "expected", "actual_count", "actual",
            "expected_status_score", "actual_status_score", "http", "result", "reason")
    with (directory / f"{tag}.csv").open("w", encoding="utf-8", newline="") as target:
        csv_writer = csv.DictWriter(target, keys)
        csv_writer.writeheader()
        for row in rows:
            ex, ac = row["expected"]["results"], row["actual"]
            ids = lambda r: " | ".join(f"{x['provider']}/{x['offering']}" for x in r)
            status = lambda r: " | ".join(f"{x['status']}@{x['score']}" for x in r)
            csv_writer.writerow({key: row[key] for key in ("id", "dataset", "group", "input", "mode", "http", "result")} |
                                {"expected_count": len(ex), "expected": ids(ex), "actual_count": len(ac), "actual": ids(ac),
                                 "expected_status_score": status(ex), "actual_status_score": status(ac),
                                 "reason": row["expected"]["reason"]})
    if tag == "offline":
        with (directory / "offline.json.gz").open("wb") as raw, gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, mtime=0
        ) as target:
            target.write(json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode())
    else:
        (directory / f"{tag}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = Counter((row["dataset"], row["mode"], row["result"]) for row in rows)
    print(dict(summary))
    failed = [f"{row['dataset']} {row['id']} {row['input']}" for row in rows if row["result"] != "PASS"]
    if failed:
        print(f"Failure count: {len(failed)}", *failed[:24], sep="\n")
    return not failed


def parity(directory, vectors, shared):
    # The comparison expectation remains independent. The real matcher and graph
    # projection run only on the actual-response side of each comparison.
    live_query = os.getenv("TASK16E_READ_QUERY") or ""
    run, curated = offline()
    from django.conf import settings
    from apps.api.public_contract import build_public_service_discovery_response
    from apps.ontology.service_discovery_rdf_generator import build_service_discovery_graph
    from apps.search.service_discovery_matching_alignment import (
        search_service_discovery_catalog_via_fuseki,
        search_service_discovery_catalog_via_local_rdf,
    )
    from apps.api.service_discovery_search_serializers import ServiceDiscoverySearchRequestSerializer
    from apps.search.service_discovery_normalizer import normalize_service_discovery_search_request

    candidates = [case for case in vectors if case["group"] in {"selection", "materials-combined", "certifications", "delivery"}
                  and not case["invalid"]]
    chosen = []
    for group in ("selection", "materials-combined", "certifications", "delivery"):
        selected = [case for case in candidates if case["group"] == group]
        chosen.extend([*selected[:2], *selected[len(selected) // 2:len(selected) // 2 + 2]])
    chosen.extend(case for case in candidates if case["group"] == "certifications" and
                  case["body"]["requirements"]["generic_requirements"]["certifications"] == ["AS9100_D"])

    def execute_graph(body, search):
        serializer = ServiceDiscoverySearchRequestSerializer(data={key: value for key, value in body.items() if key != "contract_version"})
        serializer.is_valid(raise_exception=True)
        request = normalize_service_discovery_search_request(serializer.validated_data)
        return 200, build_public_service_discovery_response(search(request), canonical_request=request)

    rows = []
    for tag, records in (("curated", curated), ("synthetic", fixed_fixtures())):
        graph = build_service_discovery_graph(records)
        for transport in ("direct", "rdflib", "mocked-fuseki"):
            def send(body):
                if transport == "direct":
                    return run(body, records)
                if transport == "rdflib":
                    return execute_graph(body, lambda request: search_service_discovery_catalog_via_local_rdf(request, graph=graph))
                with patch("apps.search.service_discovery_fuseki_service.execute_fuseki_sparql_query",
                           side_effect=lambda query, **_: list(graph.query(query))):
                    return execute_graph(body, search_service_discovery_catalog_via_fuseki)
            rows.extend(execution(chosen, records, send, f"{tag}-{transport}"))
    connectivity = {"liveReadOnly": False}
    if live_query:
        if not re.fullmatch(r"https://[a-z0-9-]+\.trycloudflare\.com/mdc_validation/sparql", live_query):
            raise ValueError("Unexpected validation read-only SPARQL endpoint.")
        settings.SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT = live_query
        from apps.search.service_discovery_fuseki_service import execute_fuseki_sparql_query
        connectivity = {"liveReadOnly": True, "defaultTriples": int(execute_fuseki_sparql_query(
            "SELECT (COUNT(*) AS ?total) WHERE { ?s ?p ?o }")[0]["total"].toPython())}
        remote_cases = chosen + [case for case in candidates if case["body"]["part_type"] == "roller"]
        rows.extend(execution(remote_cases, shared, lambda body: execute_graph(body, search_service_discovery_catalog_via_fuseki),
                              "shared-live-fuseki"))
    (directory / "graph-connectivity.json").write_text(json.dumps(connectivity, indent=2) + "\n", encoding="utf-8")
    return save(directory, "parity", rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("freeze", "hosted", "offline", "parity"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--origin")
    args = parser.parse_args()
    capture = args.output / "catalogue-snapshot.json"
    if args.mode == "freeze":
        preview = Preview(args.origin)
        _, vocab = preview.call("/api/catalog/filters")
        assert len(vocab["certifications"]) == 8
        snapshot = {"origin": args.origin, "vocabulary": vocab, "records": preview.snapshot()}
        args.output.mkdir(parents=True, exist_ok=True)
        capture.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return
    snapshot = json.loads(capture.read_text(encoding="utf-8"))
    vectors = scenarios(snapshot["vocabulary"])
    if args.mode == "parity":
        raise SystemExit(0 if parity(args.output, vectors, snapshot["records"]) else 1)
    if args.mode == "hosted":
        preview = Preview(snapshot["origin"])
        assert preview.snapshot() == snapshot["records"], "Catalogue changed after the expectation snapshot."

        def paced(body):
            value = preview.call(ROUTE, body)
            time.sleep(.18)
            return value

        rows = execution([case for case in vectors if case["live"]], snapshot["records"], paced, "shared-preview")
        assert preview.snapshot() == snapshot["records"], "Catalogue changed during the acceptance matrix."
    else:
        run, curated = offline()
        enriched = deepcopy(snapshot["records"])
        # Apply only the reviewed curated certification delta to the frozen five-offering catalogue.
        source = next(offer for record in curated for offer in record["offerings"]
                      if offer["offering_id"] == "precipart_precision_gears")
        recipient = next(offer for record in enriched for offer in record["offerings"]
                         if offer["offering_id"] == source["offering_id"])
        recipient["generic_capabilities"]["certifications"] = source["generic_capabilities"]["certifications"]
        rows = execution(vectors, snapshot["records"], lambda body: run(body, snapshot["records"]), "shared-snapshot-local")
        changed = [c for c in vectors if c["group"] in {"certifications", "combined"}]
        rows += execution(changed, enriched, lambda body: run(body, enriched), "enriched-local")
        fixtures = fixed_fixtures()
        synthetic = [c for c in vectors if c["group"] in {"shaft", "metal", "batch", "weight", "technical", "certifications", "gear"}]
        rows += execution(synthetic, fixtures, lambda body: run(body, fixtures), "synthetic-local")
    raise SystemExit(0 if save(args.output, args.mode, rows) else 1)


if __name__ == "__main__":
    main()
