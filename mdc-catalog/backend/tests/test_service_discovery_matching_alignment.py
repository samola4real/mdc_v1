from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase

from apps.api.service_discovery_search_serializers import ServiceDiscoverySearchRequestSerializer
from apps.ontology.service_discovery_rdf_generator import build_service_discovery_graph
from apps.providers.service_discovery_loaders import load_service_discovery_providers
from apps.search.service_discovery_local_matcher import search_service_discovery_catalog
from apps.search.service_discovery_matching_alignment import (
    ServiceDiscoveryMatchingAlignmentError,
    build_request_scoped_provider_records_from_retrieval,
    normalize_search_response_for_alignment_comparison,
    search_service_discovery_catalog_via_fuseki,
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


class StrictEligibilityAlignmentTests(SimpleTestCase):
    def fixture(self, category, family, part_type, family_caps, type_caps):
        evidence = {"source_type": "provider_confirmed", "confidence": "declared"}
        offering = {
            "offering_id": "eligibility_line_a",
            "provider_id": "eligibility",
            "name": "Eligibility line",
            "service_category": category,
            "part_family": family,
            "support_status": "confirmed",
            "supported_part_types": [
                {"part_type": part_type, "support_status": "confirmed", **evidence}
            ],
            "family_capabilities": family_caps,
            "part_type_capabilities": {part_type: type_caps} if type_caps else {},
            "generic_capabilities": {
                "materials": [
                    {"material": "steel", "available_grades": ["42CrMo4"], **evidence},
                    {"material": "aluminum", "available_grades": [], **evidence},
                ],
                "processes": [
                    {"process": "machining", "delivery_mode": "unspecified", **evidence},
                    {"process": "milling", "delivery_mode": "unspecified", **evidence},
                ],
                "certifications": [{"code": "ISO14001_2015", **evidence}],
                "batch_size": {"min": 1, "max": 20, **evidence},
                "lead_time_weeks": {"max": 3, **evidence},
                "surface_finish_ra_um": {"max": 1.6, **evidence},
                "quality": {"standard": "ISO", "best_class": 5, **evidence},
                "weight_kg": {"max": 10, **evidence},
            },
        }
        return [{
            "provider": {
                "provider_id": "eligibility",
                "display_name": "Eligibility Workshop",
                "certifications": [{"code": "ISO9001_2015", **evidence}],
            },
            "offerings": [offering],
        }]

    def assert_paths(self, request, records, expected_ids):
        graph = build_service_discovery_graph(records)
        direct = search_service_discovery_catalog(request, provider_records=records)
        local = search_service_discovery_catalog_via_local_rdf(request, graph=graph)
        with patch(
            "apps.search.service_discovery_fuseki_service.execute_fuseki_sparql_query",
            side_effect=lambda query, **kwargs: list(graph.query(query)),
        ):
            remote = search_service_discovery_catalog_via_fuseki(request)

        self.assertEqual([item["offering"]["offering_id"] for item in direct["results"]], expected_ids)
        self.assertEqual(direct["result_count"], len(expected_ids))
        self.assertTrue(all(item["match"]["status"] == "full_match" for item in direct["results"]))
        assert_equivalent(self, direct, local)
        assert_equivalent(self, direct, remote)

    def test_all_requirement_groups_and_inclusive_boundaries_across_families(self):
        families = (
            ("precision_gears", "gear", "spur_gear",
             {"module": {"min": 1, "max": 5}}, {"module": {"min": 1, "max": 5}},
             "face_width_mm", 30),
            ("precision_shafts", "shaft", "plain_shaft",
             {"length_mm": {"min": 20, "max": 100}}, {"length_mm": {"exact": 100}},
             "principal_diameter_mm", 10),
            ("precision_metal_parts", "metal_part", "block",
             {"bounding_box_mm": {"length_mm": {"max": 60}, "width_mm": {"max": 25}}},
             {"bounding_box_mm": {"length_mm": {"max": 60}, "width_mm": {"max": 25}}},
             "number_of_holes", 4),
        )
        for category, family, part_type, evidence, specs, type_field, exact in families:
            with self.subTest(family=family):
                records = self.fixture(
                    category, family, part_type, evidence, {type_field: {"exact": exact}},
                )
                original = records[0]["offerings"][0]
                sibling = deepcopy(original)
                sibling["offering_id"] = "eligibility_line_b"
                records[0]["offerings"].insert(0, sibling)

                generic = {
                    "materials": ["steel", "aluminum"],
                    "processes": ["machining", "milling"],
                    "certifications": ["ISO9001_2015", "ISO14001_2015"],
                    "batch_size": 20,
                    "delivery": {"max_weeks": 3},
                    "surface_finish_ra_um": {"min": 1, "exact": 1.6, "max": 2},
                    "quality": {"standard": "ISO", "max_class": 5},
                    "weight_kg": 10,
                }
                if family == "metal_part":
                    original["generic_capabilities"]["tolerance_mm"] = {"max": 0.02}
                    sibling["generic_capabilities"]["tolerance_mm"] = {"max": 0.02}
                    generic["tolerance_mm"] = {"min": 0.02}
                request = canonical_request(
                    service_category=category, part_family=family, part_type=part_type,
                    requirements={"part_family_specifications": specs,
                                  "part_type_specifications": {type_field: {"exact": exact}},
                                  "generic_requirements": generic},
                )
                self.assert_paths(request, records, ["eligibility_line_a", "eligibility_line_b"])
                request = replace(request, match_policy={
                    "optional_match_mode": "score_only", "unknown_policy": "keep_as_unknown",
                })
                if family == "gear":
                    sibling["family_capabilities"]["module"]["max"] = 3
                elif family == "shaft":
                    sibling["generic_capabilities"]["certifications"].clear()
                else:
                    sibling["family_capabilities"]["bounding_box_mm"].pop("width_mm")
                self.assert_paths(request, records, ["eligibility_line_a"])

    def test_partial_lists_unknown_evidence_and_unconfirmed_types_are_excluded(self):
        records = self.fixture(
            "precision_gears", "gear", "spur_gear",
            {"module": {"min": 1, "max": 5}}, {},
        )
        request = gear_request(
            requirements={"part_family_specifications": {"module": {"exact": 5}},
                          "generic_requirements": {"processes": ["machining", "milling"]}},
        )
        for case in ("partial_list", "unknown_module", "candidate", "unknown_type", "absent_type"):
            with self.subTest(case=case):
                changed = deepcopy(records)
                offering = changed[0]["offerings"][0]
                if case == "partial_list":
                    offering["generic_capabilities"]["processes"].pop()
                elif case == "unknown_module":
                    offering["family_capabilities"]["module"].update(
                        source_type="not_confirmed", confidence="unknown"
                    )
                elif case == "absent_type":
                    offering["supported_part_types"].clear()
                else:
                    offering["supported_part_types"][0]["support_status"] = (
                        "unknown" if case == "unknown_type" else "candidate_requiring_confirmation"
                    )
                self.assert_paths(request, changed, [])
        omitted = gear_request(requirements={"generic_requirements": {"materials": []}})
        self.assert_paths(omitted, records, ["eligibility_line_a"])

    def test_all_supplied_numeric_bounds_are_checked(self):
        records = self.fixture(
            "precision_gears", "gear", "spur_gear",
            {"module": {"min": 1, "max": 5}}, {},
        )
        for group, field, value in (
            ("part_family_specifications", "module", {"min": 6}),
            ("part_family_specifications", "module", {"max": 0.5}),
            ("generic_requirements", "surface_finish_ra_um", {"min": 2}),
            ("generic_requirements", "surface_finish_ra_um", {"exact": 1, "max": 2}),
        ):
            with self.subTest(field=field, value=value):
                self.assert_paths(gear_request(requirements={group: {field: value}}), records, [])


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

    def test_missing_face_width_and_general_tolerance_exclude_equivalently(self):
        for group, field, criterion in (
            ("part_type_specifications", "face_width_mm", {"exact": 20}),
            ("part_family_specifications", "tolerance_mm", {"max": 0.02}),
        ):
            with self.subTest(field=field):
                response = self.assert_direct_equals_local_rdf(
                    gear_request(requirements={group: {field: criterion}})
                )
                self.assertIsNone(result_by_provider(response, "tasowheel"))

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
        for policy in ("keep_as_unknown", "reject_unknown"):
            with self.subTest(policy=policy):
                response = self.assert_direct_equals_local_rdf(
                    gear_request("crown_gear", unknown_policy=policy)
                )
                self.assertIsNone(result_by_provider(response, "tasowheel"))

    def test_precipart_candidate_crown_gear_is_equivalently_excluded(self):
        response = self.assert_direct_equals_local_rdf(gear_request("crown_gear"))
        self.assertIsNone(result_by_provider(response, "precipart"))
        self.assertEqual(response["result_count"], 0)

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
