from copy import deepcopy
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient

from apps.api.public_contract import build_public_service_discovery_response
from apps.api.service_discovery_search_serializers import (
    ServiceDiscoverySearchRequestSerializer,
    ServiceDiscoverySearchResponseSerializer,
)
from apps.ontology.service_discovery_rdf_generator import build_service_discovery_graph
from apps.providers.service_discovery_loaders import load_service_discovery_providers
from apps.search.service_discovery_local_matcher import search_service_discovery_catalog
from apps.search.service_discovery_matching_alignment import (
    search_service_discovery_catalog_via_fuseki,
    search_service_discovery_catalog_via_local_rdf,
)
from apps.search.service_discovery_normalizer import normalize_service_discovery_search_request


STRICT = {"discovery_mode": "strict"}
LENIENT = {"discovery_mode": "lenient"}
LENIENT_LEGACY = {"discovery_mode": "lenient", "optional_match_mode": "all",
                  "unknown_policy": "reject_unknown", "minimum_score": None}


def payload(generic=None, family=None, *, policy=LENIENT, part_type="spur_gear"):
    data = {
        "contract_version": "1.0",
        "request_id": "req_16d",
        "consumer_id": "consumer_test",
        "service_category": "precision_gears",
        "part_family": "gear",
        "part_type": part_type,
        "requirements": {
            "generic_requirements": generic or {},
            "part_family_specifications": family or {},
        },
    }
    if policy is not None:
        data["match_policy"] = policy
    return data


def canonicalize(data):
    serializer = ServiceDiscoverySearchRequestSerializer(data={
        key: value for key, value in data.items() if key != "contract_version"
    })
    serializer.is_valid(raise_exception=True)
    return normalize_service_discovery_search_request(serializer.validated_data)


def search(data, records=None):
    request = canonicalize(data)
    internal = search_service_discovery_catalog(request, provider_records=records)
    return build_public_service_discovery_response(internal, canonical_request=request)["results"]


def offering_ids(results):
    return [result["offering_id"] for result in results]


def fixture():
    # A small scoped catalogue, separate from the published services.
    evidence = {"source_type": "provider_confirmed", "confidence": "declared"}
    provider = {"provider_id": "lenient_fixture", "display_name": "Fixture", "certifications": [
        {"code": "ISO9001_2015", **evidence},
    ]}
    offering = {
        "offering_id": "line_a",
        "provider_id": provider["provider_id"],
        "service_category": "precision_gears",
        "name": "Fixture line",
        "part_family": "gear",
        "support_status": "confirmed",
        "supported_part_types": [{"part_type": "spur_gear", "support_status": "confirmed", **evidence}],
        "family_capabilities": {
            "module": {"min": 0.3, "max": 10, **evidence},
            "outside_diameter_mm": {"min": 10, "max": 450, **evidence},
            "diametral_pitch": {"min": 2.5, "max": 85, **evidence},
            "gear_quality": {"standard": "DIN", "best_class": 5, **evidence},
        },
        "part_type_capabilities": {"spur_gear": {"face_width_mm": {"exact": 25, **evidence}}},
        "generic_capabilities": {
            "materials": [{"material": "alloyed_carburizing_steel", "available_grades": ["16MnCr5"], **evidence}],
            "processes": [{"process": "hobbing", "delivery_mode": "unspecified", **evidence}],
            "certifications": [{"code": "ISO14001_2015", **evidence}],
            "batch_size": {"min": 100, "max": 2000, **evidence},
            "lead_time_weeks": {"max": 5, **evidence},
            "weight_kg": {"max": 10, **evidence},
        },
    }
    return [{"provider": provider, "offerings": [offering]}]


class LenientDiscoveryTests(SimpleTestCase):
    def test_material_or_keeps_each_alternative_and_published_grade_evidence(self):
        cases = (
            (["steel"], ["steel"], [], "full_match"),
            (["alloyed_carburizing_steel"], ["alloyed_carburizing_steel"], [], "full_match"),
            (["steel", "alloyed_carburizing_steel"], ["steel", "alloyed_carburizing_steel"], [], "full_match"),
            (["steel", "titanium"], ["steel"], ["titanium"], "full_match"),
            (["aluminum", "titanium"], [], ["aluminum", "titanium"], "partial_match"),
        )
        for materials, matched, unknown, status in cases:
            with self.subTest(materials=materials):
                (result,) = search(payload({"materials": materials}), fixture())
                self.assertEqual(result["match"], {"status": status, "score": float(bool(matched))})
                self.assertEqual([item["requested"][0] for item in result["matched_capabilities"]], matched)
                self.assertEqual([item["requested"][0] for item in result["unknown_capabilities"]], unknown)
                self.assertEqual(result["unmatched_capabilities"], [])
                for item in result["matched_capabilities"]:
                    (row,) = item["provided"]
                    self.assertEqual(row["material"], "alloyed_carburizing_steel")
                    self.assertEqual(row["available_grades"], ["16MnCr5"])
                for item in result["unknown_capabilities"]:
                    self.assertNotIn("provided", item)

    def test_generic_steel_does_not_confirm_a_child_or_fabricate_grades(self):
        records = fixture()
        generic = records[0]["offerings"][0]["generic_capabilities"]
        generic["materials"] = [{"material": "steel", "available_grades": []}]
        (specific,) = search(payload({"materials": ["alloyed_carburizing_steel"]}), records)
        (parent,) = search(payload({"materials": ["steel"]}), records)
        self.assertEqual(specific["match"], {"status": "partial_match", "score": 0.0})
        self.assertNotIn("provided", specific["unknown_capabilities"][0])
        self.assertEqual(parent["matched_capabilities"][0]["provided"][0]["available_grades"], [])

    def test_preference_groups_score_once_and_cannot_filter_confirmed_offerings(self):
        request = payload({
            "materials": ["steel", "steel", "alloyed_carburizing_steel", "titanium"],
            "processes": ["hobbing", "milling", "hobbing"],
            "delivery": {"max_weeks": 3},
        }, {"module": {"exact": 4}}, policy=LENIENT_LEGACY)
        records = fixture()
        (result,) = search(request, records)
        self.assertEqual(result["match"], {"status": "partial_match", "score": 0.5})
        self.assertEqual([(item["field"], item["requested"]) for item in result["matched_capabilities"]],
                         [("module", {"exact": 4}), ("materials", ["steel"]),
                          ("materials", ["alloyed_carburizing_steel"]), ("processes", ["hobbing"])])
        self.assertEqual([(item["field"], item["requested"]) for item in result["unknown_capabilities"]],
                         [("materials", ["titanium"]), ("processes", ["milling"])])
        (delivery,) = result["unmatched_capabilities"]
        self.assertEqual((delivery["field"], delivery["requested"], delivery["provided"]["max"]), ("delivery", 3, 5))

        generic = records[0]["offerings"][0]["generic_capabilities"]
        generic.pop("lead_time_weeks")
        (unknown_delivery,) = search(payload({"delivery": {"max_weeks": 3}}), records)
        self.assertEqual(unknown_delivery["unknown_capabilities"][0]["field"], "delivery")
        self.assertEqual(unknown_delivery["unmatched_capabilities"], [])
        (empty,) = search(payload({"materials": [], "processes": [], "certifications": []}), records)
        self.assertEqual(empty["match"], {"status": "full_match", "score": 1.0})

    def test_hard_ranges_and_mandatory_certifications_precede_preference_evaluation(self):
        records = fixture()
        base = {"materials": ["titanium"], "batch_size": 500,
                "certifications": ["ISO9001_2015", "ISO14001_2015"]}
        for diameter in (10, 300, 450):
            for module in (0.3, 4, 10):
                results = search(payload(base, {"module": {"exact": module}, "outside_diameter_mm": {"max": diameter}}), records)
                self.assertEqual(offering_ids(results), ["line_a"])
        for generic, family, part_type in (
            (base, {"module": {"exact": 12}}, "spur_gear"),
            (base, {"outside_diameter_mm": {"max": 700}}, "spur_gear"),
            (base, {"diametral_pitch": {"min": 1, "max": 85}}, "spur_gear"),
            (base, {"gear_quality": {"standard": "DIN", "max_class": 4}}, "spur_gear"),
            (base, {"tolerance_mm": {"max": 0.02}}, "spur_gear"),
            ({**base, "batch_size": 5000}, {}, "spur_gear"),
            ({**base, "surface_finish_ra_um": {"max": 0.8}}, {}, "spur_gear"),
            ({**base, "weight_kg": 11}, {}, "spur_gear"),
            (base, {}, "crown_gear"),
        ):
            with self.subTest(generic=generic, family=family, part_type=part_type):
                self.assertEqual(search(payload(generic, family, part_type=part_type), records), [])
        sibling = deepcopy(records[0]["offerings"][0])
        sibling["offering_id"] = "line_b"
        sibling["generic_capabilities"]["certifications"] = []
        records[0]["offerings"].append(sibling)
        self.assertEqual(offering_ids(search(payload(base), records)), ["line_a"])
        records[0]["provider"]["certifications"] = []
        self.assertEqual(search(payload(base), records), [])

    def test_confirmed_hard_evidence_is_required_even_for_high_preference_coverage(self):
        records = fixture()
        offering = records[0]["offerings"][0]
        for capability in (None, {"min": 10, "max": 2}, {"min": 1, "max": 8, "confidence": "unknown"}):
            offering["family_capabilities"]["module"] = capability
            request = payload({"materials": ["steel"]}, {"module": {"exact": 4}})
            self.assertEqual(search(request, records), [])
        offering["supported_part_types"][0]["support_status"] = "candidate_requiring_confirmation"
        self.assertEqual(search(payload({"materials": ["steel"]}), records), [])

    def test_strict_default_legacy_values_and_deterministic_ordering(self):
        records = fixture()
        sibling = deepcopy(records[0]["offerings"][0])
        sibling["offering_id"] = "line_b"
        sibling["generic_capabilities"]["materials"] = [{"material": "titanium"}]
        records[0]["offerings"].insert(0, sibling)
        common = {"materials": ["alloyed_carburizing_steel"], "processes": ["hobbing"]}
        for policy in (None, STRICT, {"minimum_score": 1}, *(
            {"optional_match_mode": optional, "unknown_policy": unknown}
            for optional in ("any", "all", "score_only") for unknown in ("keep_as_unknown", "reject_unknown")
        )):
            result = search(payload(common, policy=policy), records)
            self.assertEqual(result, search(payload(common, policy=None), records))
            self.assertEqual(result[0]["match"], {"status": "full_match", "score": 1.0})
            self.assertEqual(search(payload({**common, "materials": ["steel"]}, policy=policy), records), [])
            self.assertEqual(search(payload({**common, "materials": ["alloyed_carburizing_steel", "titanium"]}, policy=policy), records), [])
            self.assertEqual(search(payload({**common, "processes": ["hobbing", "milling"]}, policy=policy), records), [])
        self.assertEqual(offering_ids(search(payload({"materials": ["titanium"]}), records)), ["line_a", "line_b"])

    def test_direct_local_rdf_and_fuseki_retrieval_bindings_share_both_policies(self):
        curated = load_service_discovery_providers()
        for records in (fixture(), curated):
            graph = build_service_discovery_graph(records)
            for policy in (None, STRICT, LENIENT):
                data = payload({"materials": ["steel", "titanium"], "processes": ["hobbing", "milling"]},
                               {"module": {"exact": 4}}, policy=policy)
                request = canonicalize(data)
                direct = search_service_discovery_catalog(request, provider_records=records)
                local = search_service_discovery_catalog_via_local_rdf(request, graph=graph)
                with patch("apps.search.service_discovery_fuseki_service.execute_fuseki_sparql_query",
                           side_effect=lambda query, **kwargs: list(graph.query(query))):
                    remote = search_service_discovery_catalog_via_fuseki(request)
                for aligned in (local, remote):
                    self.assertEqual(build_public_service_discovery_response(direct, canonical_request=request),
                                     build_public_service_discovery_response(aligned, canonical_request=request))
                    response_serializer = ServiceDiscoverySearchResponseSerializer(data=aligned)
                    self.assertTrue(response_serializer.is_valid(), response_serializer.errors)

    @override_settings(MDC_CATALOG_AUTO_SYNC_ENABLED=False)
    @patch("apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki")
    def test_canonical_endpoint_accepts_new_opt_in_and_rejects_conflicting_or_invalid_inputs(self, fuseki):
        fuseki.side_effect = lambda request, **kwargs: search_service_discovery_catalog(request, provider_records=fixture())
        client = APIClient()
        path = "/api/service-discovery/search"
        success = client.post(path, payload({"materials": ["steel", "titanium"]}, policy=LENIENT_LEGACY), format="json")
        self.assertEqual(success.status_code, 200)
        self.assertEqual(success.json()["results"][0]["match"], {"status": "full_match", "score": 1.0})
        for policy in ({"discovery_mode": "any"}, {"discovery_mode": None}, {"discovery_mode": []},
                       {"discovery_mode": "lenient", "minimum_score": 0},
                       {"discovery_mode": "lenient", "minimum_score": 0.9},
                       {"discovery_mode": "lenient", "optional_match_mode": "invalid"},
                       {"discovery_mode": "lenient", "unknown_policy": "invalid"}):
            with self.subTest(policy=policy):
                error = client.post(path, payload(policy=policy), format="json")
                self.assertEqual(error.status_code, 400)
                self.assertEqual(error.json()["contract_version"], "1.0")
        for policy in (None, LENIENT):
            error = client.post(path, payload({"material_grades": ["16MnCr5"]}, policy=policy), format="json")
            self.assertEqual(error.status_code, 400)
