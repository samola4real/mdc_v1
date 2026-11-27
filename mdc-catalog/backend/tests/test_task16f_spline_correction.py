from copy import deepcopy
import json
import os
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from django.test import TransactionTestCase, override_settings
from rdflib import Graph
from rest_framework.test import APIClient

from apps.api.public_contract import build_public_service_discovery_response
from apps.providers.catalogue_sync_service import rebuild_service_discovery_catalogue
from apps.providers.models import CatalogueSyncEvent, Offering, ProviderPublication
from apps.providers.service_discovery_db_repository import (
    import_service_discovery_provider_records,
    load_service_discovery_providers_from_db,
)
from apps.search.service_discovery_local_matcher import search_service_discovery_catalog
from apps.search.service_discovery_matching_alignment import (
    search_service_discovery_catalog_via_local_rdf,
)
from tests.test_m4_automatic_semantic_sync import AUTO_SETTINGS
from tests.test_service_discovery_lenient import canonicalize


DEMO = "mdc_stage1b_accept_20261126_a"
DEMO_SHAFT = f"{DEMO}_shaft"
TSW_SHAFT = "tasowheel_precision_shafts"
DEMO_URL = f"/api/offerings/{DEMO_SHAFT}"
SEARCH_URL = "/api/service-discovery/search"
SNAPSHOT = (
    Path(__file__).resolve().parents[2] / "docs/reports_phase4/assets"
    / "task16e-comprehensive-discovery-validation/catalogue-snapshot.json"
)
MODES = ("strict", "lenient")
PROVENANCE = {"confidence": "declared", "source_type": "provider_confirmed"}
MODULES = (None, 0.299, 0.3, 1, 1.99, 2, 2.01, 3, 4, 10, 10.001, 12)


def shaft_request(mode, module, preferences=None):
    request = {
        "contract_version": "1.0",
        "request_id": f"task16f-isolated-{uuid4().hex}",
        "consumer_id": "task16f-isolated",
        "service_category": "precision_shafts",
        "part_family": "shaft",
        "part_type": "splined_shaft",
        "requirements": {},
    }
    if module is not None:
        request["requirements"]["part_type_specifications"] = {"spline_module": {"exact": module}}
    if preferences:
        request["requirements"]["generic_requirements"] = preferences
    if mode == "lenient":
        request["match_policy"] = {"discovery_mode": mode}
    return request


def expected_ids(module, corrected):
    # Independent checks against the frozen confirmed Tasowheel range and
    # the single exact point approved for the isolated Demo shaft.
    demo = module is None or (corrected and module == 2)
    tasowheel = module is None or 0.3 <= module <= 10
    return ([DEMO_SHAFT] if demo else []) + ([TSW_SHAFT] if tasowheel else [])


@override_settings(**AUTO_SETTINGS)
class Task16FSplineCorrectionTests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        records = json.loads(SNAPSHOT.read_text(encoding="utf-8"))["records"]
        import_service_discovery_provider_records(records)
        self.graph = Graph()

        def store(graph, **_):
            self.graph = Graph()
            for triple in graph:
                self.graph.add(triple)

        def select(query, **_):
            return [row.asdict() for row in self.graph.query(query)]

        for target, fn in (
            ("apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki", store),
            ("apps.providers.catalogue_sync_service.execute_fuseki_sparql_query", select),
            ("apps.search.service_discovery_fuseki_service.execute_fuseki_sparql_query", select),
        ):
            mock = patch(target, side_effect=fn)
            mock.start()
            self.addCleanup(mock.stop)
        rebuild_service_discovery_catalogue()

    def assert_paths(self, request, ids):
        scoped = canonicalize(request)
        response = self.client.post(SEARCH_URL, request, format="json")
        self.assertEqual(response.status_code, 200, response.json())
        hosted_shape = response.json()
        direct = search_service_discovery_catalog(scoped, provider_records=load_service_discovery_providers_from_db())
        rdflib = search_service_discovery_catalog_via_local_rdf(scoped, graph=self.graph)
        wanted = [((DEMO if offer.startswith(DEMO) else "tasowheel"), offer) for offer in ids]
        for result in (direct, rdflib):
            canonical = build_public_service_discovery_response(result, canonical_request=scoped)
            self.assertEqual(canonical, hosted_shape)
        got = [(row["provider_id"], row["offering_id"]) for row in hosted_shape["results"]]
        self.assertEqual(got, wanted)
        self.assertEqual(hosted_shape["result_count"], len(wanted))
        return hosted_shape

    def assert_module_matrix(self, corrected):
        rows = []
        for module in MODULES:
            for mode in MODES:
                with self.subTest(module=module, mode=mode, corrected=corrected):
                    body = shaft_request(mode, module)
                    expected = expected_ids(module, corrected)
                    result = self.assert_paths(body, expected)
                    self.assertTrue(all(row["match"] == {"status": "full_match", "score": 1.0}
                                        for row in result["results"]))
                    if corrected and module == 2:
                        result_demo = result["results"][0]
                        (evidence,) = result_demo["matched_capabilities"]
                        self.assertEqual((evidence["field"], evidence["provided"]), ("spline_module", {"exact": 2}))
                    rows.append({"mode": mode, "module": module, "expected_offering_ids": expected,
                                 "actual_offering_ids": [row["offering_id"] for row in result["results"]],
                                 "http": 200, "passed": True})
        return rows

    def unchanged_family_searches(self):
        evidence = {}
        for mode in MODES:
            for category, family, part_type, ids in (
                ("precision_gears", "gear", "spur_gear", ["precipart_precision_gears", "tasowheel_precision_gears"]),
                ("precision_metal_parts", "metal_part", "roller", [f"{DEMO}_metal"]),
            ):
                body = shaft_request(mode, None)
                body.update(service_category=category, part_family=family, part_type=part_type)
                received = self.client.post(SEARCH_URL, body, format="json")
                self.assertEqual(received.status_code, 200)
                result = received.json()
                self.assertEqual([item["offering_id"] for item in result["results"]], ids)
                result.pop("request_id")
                evidence[f"{mode}-{part_type}"] = result
        return evidence

    def test_full_scoped_patch_sync_and_before_after_matrix(self):
        provider_url = f"/api/providers/{DEMO}"
        sibling_url = f"/api/offerings/{DEMO}_metal"
        original = self.client.get(DEMO_URL)
        provider_before = self.client.get(provider_url)
        sibling_before = self.client.get(sibling_url)
        for result in (original, provider_before, sibling_before):
            self.assertEqual(result.status_code, 200)
            self.assertRegex(result["ETag"], r'^"[^"]+"$')
        baseline = original.json()
        saved_map = baseline["part_type_capabilities"]
        self.assertEqual(saved_map["splined_shaft"]["spline_module"], {"value": 2, **PROVENANCE})
        expected_map = deepcopy(saved_map)
        target = expected_map["splined_shaft"]["spline_module"]
        target["exact"] = target.pop("value")
        payload = {"part_type_capabilities": expected_map}
        expected_records = load_service_discovery_providers_from_db()
        corrected_record = next(offer for record in expected_records for offer in record["offerings"]
                                if offer["offering_id"] == DEMO_SHAFT)
        corrected_record["part_type_capabilities"] = expected_map
        before_matrix = self.assert_module_matrix(corrected=False)
        ancillary_before = self.unchanged_family_searches()

        for headers, status in (({}, 428), ({"HTTP_IF_MATCH": '"stale"'}, 412)):
            response = self.client.patch(DEMO_URL, payload, format="json", **headers)
            self.assertEqual(response.status_code, status, response.json())
        self.assertEqual(ProviderPublication.objects.count(), 0)
        bad_shape = deepcopy(payload)
        bad_shape["part_type_capabilities"]["splined_shaft"]["spline_module"]["exact"] = -2
        response = self.client.patch(DEMO_URL, bad_shape, format="json", HTTP_IF_MATCH=original["ETag"])
        self.assertEqual(response.status_code, 400, response.json())
        self.assertEqual(self.client.get(DEMO_URL).json(), baseline)

        response = self.client.patch(DEMO_URL, payload, format="json", HTTP_IF_MATCH=original["ETag"])
        self.assertEqual(response.status_code, 200, response.json())
        receipt = response.json()
        statuses = {key: receipt[key] for key in ("status", "publication_status", "sync_status", "offering_id")}
        self.assertEqual(statuses, {"status": "completed", "publication_status": "synced",
                                    "sync_status": "succeeded", "offering_id": DEMO_SHAFT})
        event = CatalogueSyncEvent.objects.get()
        self.assertEqual((event.entity_type, event.entity_id, event.status), ("offering", DEMO_SHAFT, "succeeded"))
        self.assertEqual(Offering.objects.get(offering_id=DEMO_SHAFT).part_type_capabilities, expected_map)
        current = self.client.get(DEMO_URL)
        self.assertEqual(current.json(), {**baseline, "part_type_capabilities": expected_map})
        self.assertRegex(current["ETag"], r'^"[^"]+"$')
        self.assertNotEqual(current["ETag"], original["ETag"])
        parent_tag_changed = self.client.get(provider_url)["ETag"] != provider_before["ETag"]
        self.assertTrue(parent_tag_changed)
        self.assertEqual(self.client.get(sibling_url).json(), sibling_before.json())
        self.assertEqual(load_service_discovery_providers_from_db(), expected_records)
        after_matrix = self.assert_module_matrix(corrected=True)

        preferences = {"materials": ["steel", "titanium"], "processes": ["turning"]}
        self.assert_paths(shaft_request("strict", 2, preferences), [])
        results = self.assert_paths(shaft_request("lenient", 2, preferences), [DEMO_SHAFT, TSW_SHAFT])
        self.assertEqual([item["match"] for item in results["results"]], [
            {"status": "full_match", "score": 1.0}, {"status": "partial_match", "score": 0.5},
        ])
        invalid = self.client.post(SEARCH_URL, shaft_request("lenient", -2), format="json")
        self.assertEqual(invalid.status_code, 400)
        ancillary_after = self.unchanged_family_searches()
        self.assertEqual(ancillary_after, ancillary_before)
        output = os.getenv("TASK16F_ISOLATED_EVIDENCE")
        if output:
            Path(output).write_text(json.dumps({
                "fixture": "isolated SQLite, RDFLib and mocked Fuseki bindings",
                "beforeMap": saved_map, "patch": payload, "afterMap": current.json()["part_type_capabilities"],
                "before": before_matrix, "after": after_matrix, "receipt": statuses,
                "parentStrongEtagChanged": parent_tag_changed, "siblingUnchanged": True,
                "preconditions": {"missing": 428, "stale": 412, "invalidMeasurement": 400},
                "unchangedFamilySearches": {case: [row["offering_id"] for row in reply["results"]]
                                            for case, reply in ancillary_after.items()},
            }, indent=2) + "\n", encoding="utf-8")
