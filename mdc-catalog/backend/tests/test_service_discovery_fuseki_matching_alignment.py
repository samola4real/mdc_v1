import os
from unittest import skipUnless

from django.conf import settings
from django.test import SimpleTestCase

from apps.api.service_discovery_search_serializers import (
    ServiceDiscoverySearchRequestSerializer,
    ServiceDiscoverySearchResponseSerializer,
)
from apps.ontology.service_discovery_rdf_generator import default_service_discovery_turtle_path
from apps.providers.service_discovery_loaders import load_service_discovery_providers
from apps.search.service_discovery_local_matcher import search_service_discovery_catalog
from apps.search.service_discovery_matching_alignment import (
    normalize_search_response_for_alignment_comparison,
    search_service_discovery_catalog_via_fuseki,
    search_service_discovery_catalog_via_local_rdf,
)
from apps.search.service_discovery_normalizer import normalize_service_discovery_search_request


def integration_enabled() -> bool:
    return (
        os.getenv("RUN_SERVICE_DISCOVERY_FUSEKI_TESTS") == "1"
        and bool(getattr(settings, "SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT", ""))
        and default_service_discovery_turtle_path().exists()
    )


def canonical_request(
    *,
    service_category="precision_gears",
    part_family="gear",
    part_type="spur_gear",
    requirements=None,
    unknown_policy="keep_as_unknown",
    optional_match_mode="any",
    minimum_score=None,
):
    payload = {
        "request_id": "req_h9_remote",
        "consumer_id": "consumer_h9",
        "service_category": service_category,
        "part_family": part_family,
        "part_type": part_type,
        "requirements": requirements or {},
        "match_policy": {
            "optional_match_mode": optional_match_mode,
            "unknown_policy": unknown_policy,
            "minimum_score": minimum_score,
        },
    }
    serializer = ServiceDiscoverySearchRequestSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors
    return normalize_service_discovery_search_request(serializer.validated_data)


def gear_request(part_type="spur_gear", **kwargs):
    return canonical_request(part_type=part_type, **kwargs)


def shaft_request(part_type="splined_shaft", **kwargs):
    return canonical_request(
        service_category="precision_shafts",
        part_family="shaft",
        part_type=part_type,
        **kwargs,
    )


def result_by_provider(response: dict, provider_id: str):
    for result in response["results"]:
        if result["provider"]["provider_id"] == provider_id:
            return result
    return None


EXPECTED_TASOWHEEL_PROCESSES = [
    "machining",
    "hobbing",
    "gear_shaping",
    "deburring",
    "hard_turning",
    "grinding",
    "tooth_grinding",
    "gear_grinding",
    "gear_cutting",
    "surface_grinding",
    "milling",
    "turn_mill",
]

EXPECTED_TASOWHEEL_CERTIFICATIONS = [
    "ISO9001_2015",
    "ISO14001_2015",
    "ISO_TS_16949_partial",
    "APQP",
]


@skipUnless(
    integration_enabled(),
    (
        "H9 Fuseki matching-alignment tests require "
        "RUN_SERVICE_DISCOVERY_FUSEKI_TESTS=1, SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT, "
        "and an existing H6 harmonized Turtle file."
    ),
)
class ServiceDiscoveryFusekiMatchingAlignmentTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider_records = load_service_discovery_providers()

    def assert_direct_local_remote_equivalent(self, request):
        direct = search_service_discovery_catalog(
            request,
            provider_records=self.provider_records,
        )
        local = search_service_discovery_catalog_via_local_rdf(
            request,
            ttl_path=default_service_discovery_turtle_path(),
        )
        remote = search_service_discovery_catalog_via_fuseki(request)

        self.assertEqual(
            normalize_search_response_for_alignment_comparison(direct),
            normalize_search_response_for_alignment_comparison(local),
        )
        self.assertEqual(
            normalize_search_response_for_alignment_comparison(local),
            normalize_search_response_for_alignment_comparison(remote),
        )
        self.assertEqual(
            remote["status"]["search_engine"],
            "harmonized_fuseki_with_h5_policy",
        )
        serializer = ServiceDiscoverySearchResponseSerializer(data=remote)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        return remote

    def test_spur_gear_direct_local_and_remote_matching_are_equivalent(self):
        remote = self.assert_direct_local_remote_equivalent(gear_request("spur_gear"))
        tasowheel = result_by_provider(remote, "tasowheel")

        self.assertEqual(tasowheel["match"]["status"], "full_match")
        self.assertEqual(tasowheel["match"]["score"], 1.0)
        self.assertEqual(
            tasowheel["evidence"]["family_capabilities"]["diametral_pitch"]["normalized_order"],
            "ascending",
        )
        self.assertIsNone(
            tasowheel["evidence"]["generic_capabilities"]["surface_finish_ra_um"]["max"]
        )

    def test_crown_gear_not_asserted_and_candidate_evidence_are_equivalent(self):
        remote = self.assert_direct_local_remote_equivalent(gear_request("crown_gear"))

        tasowheel = result_by_provider(remote, "tasowheel")
        self.assertEqual(tasowheel["match"]["status"], "unknown_match")
        precipart = result_by_provider(remote, "precipart")
        if precipart is not None:
            self.assertTrue(
                any(
                    item["field"] == "part_type"
                    and item.get("source_type") == "public_web"
                    and item.get("confidence") == "inferred"
                    for item in precipart["unknown_attributes"]
                )
            )

    def test_splined_shaft_scope_direct_local_and_remote_matching_are_equivalent(self):
        remote = self.assert_direct_local_remote_equivalent(
            shaft_request(
                "splined_shaft",
                requirements={
                    "part_family_specifications": {
                        "length_mm": {"max": 500},
                        "outer_diameter_mm": {"exact": 100},
                    },
                    "part_type_specifications": {
                        "spline_module": {"exact": 2.0},
                    },
                },
            )
        )
        tasowheel = result_by_provider(remote, "tasowheel")

        self.assertEqual(tasowheel["match"]["status"], "full_match")
        self.assertNotIn("spline_module", tasowheel["evidence"]["family_capabilities"])
        self.assertIn("spline_module", tasowheel["evidence"]["part_type_capabilities"]["splined_shaft"])

    def test_material_process_and_certification_matching_are_equivalent(self):
        remote = self.assert_direct_local_remote_equivalent(
            gear_request(
                "spur_gear",
                requirements={
                    "generic_requirements": {
                        "materials": ["alloyed_carburizing_steel"],
                        "processes": ["hobbing", "turn_mill"],
                        "certifications": ["ISO9001_2015"],
                    }
                },
            )
        )
        tasowheel = result_by_provider(remote, "tasowheel")

        self.assertEqual(
            tasowheel["evidence"]["materials"][0]["available_grades"],
            ["18CrNiMo7-6", "16MnCr5", "20MnCr5"],
        )
        self.assertEqual(
            [item["process"] for item in tasowheel["evidence"]["generic_capabilities"]["processes"]],
            EXPECTED_TASOWHEEL_PROCESSES,
        )
        self.assertEqual(
            [item["code"] for item in tasowheel["evidence"]["certifications"]],
            EXPECTED_TASOWHEEL_CERTIFICATIONS,
        )
        self.assertIsNone(
            tasowheel["evidence"]["generic_capabilities"]["surface_finish_ra_um"]["max"]
        )
        self.assertNotIn("material_grades", str(tasowheel))
        self.assertTrue(
            any(item["field"] == "processes" for item in tasowheel["matched_attributes"])
        )
        self.assertTrue(
            any(item["code"] == "ISO9001_2015" for item in tasowheel["evidence"]["certifications"])
        )

    def test_remote_matching_excludes_legacy_and_fabricated_deferred_evidence(self):
        remote = self.assert_direct_local_remote_equivalent(
            shaft_request(
                "splined_shaft",
                requirements={
                    "part_family_specifications": {
                        "length_mm": {"max": 500},
                        "outer_diameter_mm": {"exact": 100},
                    },
                    "part_type_specifications": {
                        "spline_module": {"exact": 2.0},
                    },
                },
            )
        )
        offering_ids = {result["offering"]["offering_id"] for result in remote["results"]}

        self.assertNotIn("tasowheel_gears_shafts_precision", offering_ids)
        self.assertNotIn("tasowheel_precision_metal_parts", offering_ids)
        text = str(remote)
        for forbidden in [
            "spline_diametral_pitch",
            "shaft_quality",
            "spline_quality",
            "'tolerance_mm': {'status': 'matched'",
        ]:
            self.assertNotIn(forbidden, text)
