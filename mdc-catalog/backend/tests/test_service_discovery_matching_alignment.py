from copy import deepcopy
from decimal import Decimal

from django.test import SimpleTestCase

from apps.api.service_discovery_search_serializers import ServiceDiscoverySearchRequestSerializer
from apps.ontology.service_discovery_rdf_generator import build_service_discovery_graph
from apps.providers.service_discovery_loaders import load_service_discovery_providers
from apps.search.service_discovery_local_matcher import search_service_discovery_catalog
from apps.search.service_discovery_matching_alignment import (
    ServiceDiscoveryMatchingAlignmentError,
    build_request_scoped_provider_records_from_retrieval,
    normalize_search_response_for_alignment_comparison,
    search_service_discovery_catalog_via_local_rdf,
)
from apps.search.service_discovery_normalizer import normalize_service_discovery_search_request
from apps.search.service_discovery_sparql_service import retrieve_service_discovery_candidates


def canonical_request(
    *,
    service_category="precision_gears",
    part_family="gear",
    part_type="spur_gear",
    requirements=None,
    unknown_policy="keep_as_unknown",
    optional_match_mode="any",
    minimum_score=None,
    request_id="req_h9",
):
    payload = {
        "request_id": request_id,
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


def assert_equivalent(testcase: SimpleTestCase, direct: dict, aligned: dict) -> None:
    testcase.assertEqual(
        normalize_search_response_for_alignment_comparison(direct),
        normalize_search_response_for_alignment_comparison(aligned),
    )


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


def synthetic_shaft_only_records() -> list[dict]:
    return [
        {
            "provider": {
                "provider_id": "synthetic_shaft_provider",
                "display_name": "Synthetic Shaft Provider",
                "certifications": [],
            },
            "offerings": [
                {
                    "offering_id": "synthetic_shaft_provider_precision_shafts",
                    "provider_id": "synthetic_shaft_provider",
                    "service_category": "precision_shafts",
                    "name": "Precision shafts",
                    "part_family": "shaft",
                    "support_status": "confirmed",
                    "supported_part_types": [
                        {
                            "part_type": "plain_shaft",
                            "support_status": "confirmed",
                            "source_type": "curated",
                            "confidence": "curated",
                        }
                    ],
                    "family_capabilities": {},
                    "part_type_capabilities": {},
                    "generic_capabilities": {},
                }
            ],
        }
    ]


class ServiceDiscoveryMatchingAlignmentTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider_records = load_service_discovery_providers()
        cls.graph = build_service_discovery_graph(cls.provider_records)

    def direct(self, request, provider_records=None):
        return search_service_discovery_catalog(
            request,
            provider_records=provider_records or self.provider_records,
        )

    def local_rdf(self, request, graph=None):
        return search_service_discovery_catalog_via_local_rdf(
            request,
            graph=graph or self.graph,
        )

    def assert_direct_equals_local_rdf(self, request):
        direct = self.direct(request)
        aligned = self.local_rdf(request)
        self.assertTrue(aligned["status"]["search_executed"])
        self.assertEqual(
            aligned["status"]["search_engine"],
            "harmonized_rdf_rdflib_with_h5_policy",
        )
        assert_equivalent(self, direct, aligned)
        return aligned

    def test_adapter_rejects_malformed_projection(self):
        with self.assertRaises(ServiceDiscoveryMatchingAlignmentError):
            build_request_scoped_provider_records_from_retrieval(gear_request(), {})

    def test_adapter_rejects_selection_mismatch(self):
        request = gear_request("spur_gear")
        projection = retrieve_service_discovery_candidates(request, graph=self.graph)
        projection["query_interpretation"]["selection"] = {
            **projection["query_interpretation"]["selection"],
            "part_type": "crown_gear",
        }

        with self.assertRaises(ServiceDiscoveryMatchingAlignmentError):
            build_request_scoped_provider_records_from_retrieval(request, projection)

    def test_adapter_rejects_projection_that_claims_matching_was_executed(self):
        request = gear_request("spur_gear")
        projection = retrieve_service_discovery_candidates(request, graph=self.graph)
        projection["status"]["matching_executed"] = True

        with self.assertRaises(ServiceDiscoveryMatchingAlignmentError):
            build_request_scoped_provider_records_from_retrieval(request, projection)

    def test_adapter_reconstructs_request_scoped_records_and_preserves_evidence_scope(self):
        request = shaft_request(
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
        projection = retrieve_service_discovery_candidates(request, graph=self.graph)
        records = build_request_scoped_provider_records_from_retrieval(request, projection)
        tasowheel = next(record for record in records if record["provider"]["provider_id"] == "tasowheel")
        offering = tasowheel["offerings"][0]

        self.assertEqual(
            offering["supported_part_types"],
            [
                {
                    "part_type": "splined_shaft",
                    "support_status": "confirmed",
                    "source_type": "provider_confirmed",
                    "confidence": "declared",
                }
            ],
        )
        self.assertEqual(offering["family_capabilities"]["length_mm"]["max"], 500)
        self.assertIn("outer_diameter_mm", offering["family_capabilities"])
        self.assertNotIn("spline_module", offering["family_capabilities"])
        self.assertIn(
            "spline_module",
            offering["part_type_capabilities"]["splined_shaft"],
        )
        surface_finish = offering["generic_capabilities"]["surface_finish_ra_um"]
        self.assertIn("max", surface_finish)
        self.assertIsNone(surface_finish["max"])
        self.assertFalse(
            {"diametral_pitch", "gear_quality"} & set(offering["family_capabilities"])
        )

    def test_adapter_normalizes_rdf_decimal_literals_for_h5_provider_records(self):
        request = shaft_request(
            "splined_shaft",
            requirements={
                "part_type_specifications": {
                    "spline_module": {"exact": 2.0},
                },
            },
        )
        projection = retrieve_service_discovery_candidates(request, graph=self.graph)
        tasowheel = next(
            candidate
            for candidate in projection["candidates"]
            if candidate["provider"]["provider_id"] == "tasowheel"
        )
        spline_module = next(
            item
            for item in tasowheel["evidence"]["part_type_capabilities"]
            if item["field_code"] == "spline_module"
        )
        spline_module["min"] = Decimal("0.3")
        spline_module["max"] = Decimal("10")

        records = build_request_scoped_provider_records_from_retrieval(request, projection)
        tasowheel_record = next(
            record for record in records if record["provider"]["provider_id"] == "tasowheel"
        )
        reconstructed = tasowheel_record["offerings"][0]["part_type_capabilities"]["splined_shaft"][
            "spline_module"
        ]

        self.assertEqual(reconstructed["min"], 0.3)
        self.assertIs(type(reconstructed["min"]), float)
        self.assertEqual(reconstructed["max"], 10)
        self.assertIs(type(reconstructed["max"]), int)

    def test_not_asserted_is_reconstructed_as_absent_support_evidence_only(self):
        request = gear_request("crown_gear")
        projection = retrieve_service_discovery_candidates(request, graph=self.graph)
        records = build_request_scoped_provider_records_from_retrieval(request, projection)
        tasowheel = next(record for record in records if record["provider"]["provider_id"] == "tasowheel")

        self.assertEqual(tasowheel["offerings"][0]["supported_part_types"], [])
        self.assertNotIn("unsupported", str(tasowheel))
        self.assertNotIn("candidate_requiring_confirmation", str(tasowheel["offerings"][0]["supported_part_types"]))

    def test_material_grades_certifications_and_processes_retain_accepted_scope(self):
        request = gear_request(
            "spur_gear",
            requirements={
                "generic_requirements": {
                    "materials": ["alloyed_carburizing_steel"],
                    "processes": ["hobbing", "turn_mill"],
                    "certifications": ["ISO9001_2015"],
                }
            },
        )
        response = self.assert_direct_equals_local_rdf(request)
        tasowheel = result_by_provider(response, "tasowheel")

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
        self.assertNotIn("certifications", tasowheel["evidence"]["generic_capabilities"])

    def test_confirmed_spur_gear_without_extra_requirements_is_equivalent(self):
        response = self.assert_direct_equals_local_rdf(gear_request("spur_gear"))
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertEqual(tasowheel["match"]["status"], "full_match")
        self.assertEqual(tasowheel["match"]["score"], 1.0)

    def test_confirmed_spur_gear_family_requirements_are_equivalent(self):
        response = self.assert_direct_equals_local_rdf(
            gear_request(
                "spur_gear",
                requirements={
                    "part_family_specifications": {
                        "module": {"exact": 2.0},
                        "diametral_pitch": {"min": 2.5, "max": 85},
                        "outside_diameter_mm": {"exact": 100},
                        "gear_quality": {"standard": "DIN", "max_class": 5},
                    }
                },
            )
        )
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertEqual(tasowheel["match"]["status"], "full_match")
        for field in ["module", "diametral_pitch", "outside_diameter_mm", "gear_quality"]:
            self.assertTrue(any(item["field"] == field for item in tasowheel["matched_attributes"]))
        self.assertEqual(
            tasowheel["evidence"]["family_capabilities"]["diametral_pitch"]["normalized_order"],
            "ascending",
        )

    def test_face_width_and_general_tolerance_remain_unknown_equivalently(self):
        face_width = self.assert_direct_equals_local_rdf(
            gear_request(
                "spur_gear",
                requirements={"part_type_specifications": {"face_width_mm": {"exact": 20}}},
            )
        )
        tolerance = self.assert_direct_equals_local_rdf(
            gear_request(
                "spur_gear",
                requirements={"part_family_specifications": {"tolerance_mm": {"max": 0.02}}},
            )
        )

        self.assertTrue(
            any(item["field"] == "face_width_mm" for item in result_by_provider(face_width, "tasowheel")["unknown_attributes"])
        )
        self.assertTrue(
            any(item["field"] == "tolerance_mm" for item in result_by_provider(tolerance, "tasowheel")["unknown_attributes"])
        )
        self.assertFalse(
            any(
                item["field"] == "tolerance_mm"
                for item in result_by_provider(tolerance, "tasowheel")["matched_attributes"]
            )
        )

    def test_confirmed_splined_shaft_scope_is_equivalent(self):
        response = self.assert_direct_equals_local_rdf(
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
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertEqual(tasowheel["match"]["status"], "full_match")
        self.assertNotIn("spline_diametral_pitch", str(tasowheel))
        self.assertNotIn("shaft_quality", str(tasowheel))

    def test_unasserted_subtypes_are_equivalent_under_unknown_policies(self):
        keep = self.assert_direct_equals_local_rdf(gear_request("crown_gear"))
        reject = self.assert_direct_equals_local_rdf(
            gear_request("crown_gear", unknown_policy="reject_unknown")
        )

        self.assertEqual(result_by_provider(keep, "tasowheel")["match"]["status"], "unknown_match")
        self.assertNotIn(
            "tasowheel",
            {result["provider"]["provider_id"] for result in reject["results"]},
        )

    def test_precipart_candidate_crown_gear_is_equivalent_and_not_promoted(self):
        response = self.assert_direct_equals_local_rdf(gear_request("crown_gear"))
        precipart = result_by_provider(response, "precipart")

        self.assertEqual(precipart["match"]["status"], "unknown_match")
        self.assertTrue(
            any(
                item["field"] == "part_type"
                and item.get("source_type") == "public_web"
                and item.get("confidence") == "inferred"
                for item in precipart["unknown_attributes"]
            )
        )

    def test_optional_policy_and_minimum_score_cases_are_equivalent(self):
        requirements = {
            "generic_requirements": {
                "materials": ["alloyed_carburizing_steel"],
                "processes": ["hobbing"],
                "certifications": ["ISO9001_2015"],
            }
        }
        for mode in ["any", "all", "score_only"]:
            self.assert_direct_equals_local_rdf(
                gear_request(
                    "spur_gear",
                    requirements=requirements,
                    optional_match_mode=mode,
                )
            )

        self.assert_direct_equals_local_rdf(
            gear_request(
                "spur_gear",
                requirements={"part_family_specifications": {"tolerance_mm": {"max": 0.02}}},
                minimum_score=0.75,
            )
        )

    def test_empty_candidate_case_aligns_with_equivalent_synthetic_provider_input(self):
        request = gear_request("spur_gear")
        graph = build_service_discovery_graph(synthetic_shaft_only_records())
        direct = self.direct(request, provider_records=synthetic_shaft_only_records())
        aligned = self.local_rdf(request, graph=graph)

        self.assertEqual(direct["results"], [])
        self.assertEqual(aligned["results"], [])
        assert_equivalent(self, direct, aligned)

    def test_no_legacy_bundled_tasowheel_offering_appears(self):
        response = self.local_rdf(gear_request("spur_gear"))
        offering_ids = {result["offering"]["offering_id"] for result in response["results"]}

        self.assertIn("tasowheel_precision_gears", offering_ids)
        self.assertNotIn("tasowheel_gears_shafts_precision", offering_ids)
        self.assertNotIn("tasowheel_precision_metal_parts", offering_ids)

    def test_alignment_comparison_suppresses_only_engine_and_message(self):
        response = self.direct(gear_request("spur_gear"))
        changed_status = deepcopy(response)
        changed_status["status"]["search_engine"] = "different"
        changed_status["status"]["message"] = "different"
        self.assertEqual(
            normalize_search_response_for_alignment_comparison(response),
            normalize_search_response_for_alignment_comparison(changed_status),
        )

        changed_score = deepcopy(response)
        changed_score["results"][0]["match"]["score"] = 0.123
        self.assertNotEqual(
            normalize_search_response_for_alignment_comparison(response),
            normalize_search_response_for_alignment_comparison(changed_score),
        )
