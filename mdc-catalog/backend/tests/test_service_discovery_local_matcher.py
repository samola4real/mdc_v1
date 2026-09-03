from copy import deepcopy

from django.test import SimpleTestCase

from apps.api.service_discovery_search_serializers import (
    ServiceDiscoverySearchRequestSerializer,
)
from apps.providers.service_discovery_loaders import load_service_discovery_providers
from apps.search.service_discovery_local_matcher import search_service_discovery_catalog
from apps.search.service_discovery_normalizer import (
    normalize_service_discovery_search_request,
)


def canonical_request(payload: dict):
    serializer = ServiceDiscoverySearchRequestSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors
    return normalize_service_discovery_search_request(serializer.validated_data)


def gear_request(
    part_type: str = "spur_gear",
    *,
    unknown_policy: str = "keep_as_unknown",
    requirements: dict | None = None,
    minimum_score=None,
    optional_match_mode: str = "any",
):
    payload = {
        "request_id": "req_gears",
        "consumer_id": "consumer_001",
        "service_category": "precision_gears",
        "part_family": "gear",
        "part_type": part_type,
        "requirements": requirements or {},
        "match_policy": {
            "optional_match_mode": optional_match_mode,
            "unknown_policy": unknown_policy,
            "minimum_score": minimum_score,
        },
    }
    return canonical_request(payload)


def shaft_request(
    part_type: str = "hollow_shaft",
    *,
    unknown_policy: str = "keep_as_unknown",
    requirements: dict | None = None,
):
    return canonical_request(
        {
            "request_id": "req_shafts",
            "consumer_id": "consumer_001",
            "service_category": "precision_shafts",
            "part_family": "shaft",
            "part_type": part_type,
            "requirements": requirements or {},
            "match_policy": {
                "optional_match_mode": "any",
                "unknown_policy": unknown_policy,
                "minimum_score": None,
            },
        }
    )


def result_by_provider(response: dict, provider_id: str):
    for result in response["results"]:
        if result["provider"]["provider_id"] == provider_id:
            return result
    return None


def synthetic_confirmed_spur_provider() -> list[dict]:
    return [
        {
            "provider": {
                "provider_id": "confirmed_provider",
                "display_name": "Confirmed Provider",
                "country": "Finland",
                "certifications": [
                    {
                        "code": "ISO9001_2015",
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    }
                ],
            },
            "offerings": [
                {
                    "offering_id": "confirmed_provider_precision_gears",
                    "provider_id": "confirmed_provider",
                    "service_category": "precision_gears",
                    "name": "Precision gears",
                    "part_family": "gear",
                    "support_status": "confirmed",
                    "supported_part_types": [
                        {
                            "part_type": "spur_gear",
                            "support_status": "confirmed",
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        }
                    ],
                    "family_capabilities": {
                        "module": {
                            "min": 1,
                            "max": 5,
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        },
                        "outside_diameter_mm": {
                            "min": 10,
                            "max": 150,
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        },
                    },
                    "part_type_capabilities": {
                        "spur_gear": {
                            "face_width_mm": {
                                "min": 5,
                                "max": 80,
                                "source_type": "provider_confirmed",
                                "confidence": "declared",
                            }
                        }
                    },
                    "generic_capabilities": {
                        "materials": [
                            {
                                "material": "steel",
                                "source_type": "provider_confirmed",
                                "confidence": "declared",
                            }
                        ],
                        "processes": [
                            {
                                "process": "hobbing",
                                "delivery_mode": "unspecified",
                                "source_type": "provider_confirmed",
                                "confidence": "declared",
                            }
                        ],
                        "batch_size": {
                            "min": 10,
                            "max": 1000,
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        },
                        "lead_time_weeks": {
                            "min": 4,
                            "max": 8,
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        },
                        "weight_kg": {
                            "max": 100,
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        },
                    },
                }
            ],
        }
    ]


class ServiceDiscoveryLocalMatcherTests(SimpleTestCase):
    def setUp(self):
        self.records = load_service_discovery_providers()

    def test_precipart_confirmed_spur_gear_is_full_match(self):
        response = search_service_discovery_catalog(
            gear_request("spur_gear"),
            provider_records=self.records,
        )
        precipart = result_by_provider(response, "precipart")

        self.assertIsNotNone(precipart)
        self.assertEqual(precipart["match"]["status"], "full_match")
        self.assertEqual(precipart["match"]["score"], 1.0)

    def test_tasowheel_confirmed_gear_subtypes_are_full_matches_without_extra_criteria(self):
        for part_type in ["spur_gear", "helical_gear", "bevel_gear", "worm_gear"]:
            response = search_service_discovery_catalog(
                gear_request(part_type),
                provider_records=self.records,
            )
            tasowheel = result_by_provider(response, "tasowheel")

            self.assertIsNotNone(tasowheel, part_type)
            self.assertEqual(tasowheel["match"]["status"], "full_match", part_type)
            self.assertEqual(tasowheel["match"]["score"], 1.0, part_type)
            self.assertTrue(
                any(
                    item["field"] == "part_type" and item["status"] == "matched"
                    for item in tasowheel["matched_attributes"]
                ),
                part_type,
            )

    def test_reject_unknown_keeps_tasowheel_and_precipart_for_confirmed_spur_gear(self):
        response = search_service_discovery_catalog(
            gear_request("spur_gear", unknown_policy="reject_unknown"),
            provider_records=self.records,
        )
        provider_ids = {result["provider"]["provider_id"] for result in response["results"]}

        self.assertIn("precipart", provider_ids)
        self.assertIn("tasowheel", provider_ids)

    def test_precipart_candidate_crown_gear_remains_unknown(self):
        response = search_service_discovery_catalog(
            gear_request("crown_gear"),
            provider_records=self.records,
        )
        precipart = result_by_provider(response, "precipart")

        self.assertIsNotNone(precipart)
        self.assertEqual(precipart["match"]["status"], "unknown_match")
        self.assertTrue(
            any(
                item.get("confidence") == "inferred"
                and item.get("source_type") == "public_web"
                for item in precipart["unknown_attributes"]
            )
        )

        rejected = search_service_discovery_catalog(
            gear_request("crown_gear", unknown_policy="reject_unknown"),
            provider_records=self.records,
        )
        self.assertEqual(rejected["results"], [])

    def test_tasowheel_unconfirmed_gear_subtype_remains_unknown(self):
        response = search_service_discovery_catalog(
            gear_request("crown_gear"),
            provider_records=self.records,
        )
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertIsNotNone(tasowheel)
        self.assertEqual(tasowheel["match"]["status"], "unknown_match")

        rejected = search_service_discovery_catalog(
            gear_request("crown_gear", unknown_policy="reject_unknown"),
            provider_records=self.records,
        )
        self.assertNotIn(
            "tasowheel",
            {result["provider"]["provider_id"] for result in rejected["results"]},
        )

    def test_tasowheel_confirmed_shaft_subtypes_are_full_matches_without_extra_criteria(self):
        for part_type in ["splined_shaft", "plain_shaft", "hollow_shaft"]:
            response = search_service_discovery_catalog(
                shaft_request(part_type),
                provider_records=self.records,
            )
            tasowheel = result_by_provider(response, "tasowheel")

            self.assertIsNotNone(tasowheel, part_type)
            self.assertEqual(tasowheel["match"]["status"], "full_match", part_type)
            self.assertEqual(tasowheel["match"]["score"], 1.0, part_type)

    def test_tasowheel_unconfirmed_shaft_subtypes_remain_unknown(self):
        for part_type in ["stepped_shaft", "worm_shaft"]:
            response = search_service_discovery_catalog(
                shaft_request(part_type),
                provider_records=self.records,
            )
            tasowheel = result_by_provider(response, "tasowheel")

            self.assertIsNotNone(tasowheel, part_type)
            self.assertEqual(tasowheel["match"]["status"], "unknown_match", part_type)

            rejected = search_service_discovery_catalog(
                shaft_request(part_type, unknown_policy="reject_unknown"),
                provider_records=self.records,
            )
            self.assertNotIn(
                "tasowheel",
                {result["provider"]["provider_id"] for result in rejected["results"]},
                part_type,
            )

    def test_tasowheel_process_request_is_matched_from_harmonized_offering_evidence(self):
        response = search_service_discovery_catalog(
            gear_request(
                "spur_gear",
                requirements={
                    "generic_requirements": {
                        "processes": [
                            "hobbing",
                            "gear_shaping",
                            "deburring",
                            "gear_grinding",
                            "surface_grinding",
                            "turn_mill",
                        ],
                    }
                },
            ),
            provider_records=self.records,
        )
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertIsNotNone(tasowheel)
        self.assertTrue(
            any(item["field"] == "processes" for item in tasowheel["matched_attributes"])
        )

    def test_tasowheel_shaft_process_request_is_matched_from_harmonized_offering_evidence(self):
        response = search_service_discovery_catalog(
            shaft_request(
                "hollow_shaft",
                requirements={
                    "generic_requirements": {
                        "processes": ["turn_mill"],
                    }
                },
            ),
            provider_records=self.records,
        )
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertTrue(
            any(item["field"] == "processes" for item in tasowheel["matched_attributes"])
        )

    def test_tasowheel_family_evidence_can_full_match_confirmed_spur_gear(self):
        response = search_service_discovery_catalog(
            gear_request(
                "spur_gear",
                requirements={
                    "part_family_specifications": {
                        "module": {"exact": 2.0},
                        "diametral_pitch": {"min": 5, "max": 40},
                        "outside_diameter_mm": {"exact": 100},
                        "gear_quality": {"standard": "DIN", "max_class": 5},
                    }
                },
            ),
            provider_records=self.records,
        )
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertEqual(tasowheel["match"]["status"], "full_match")
        for field in ["module", "diametral_pitch", "outside_diameter_mm", "gear_quality"]:
            self.assertTrue(
                any(item["field"] == field for item in tasowheel["matched_attributes"]),
                field,
            )
        self.assertEqual(tasowheel["match"]["score"], 1.0)

    def test_tasowheel_face_width_is_unknown_for_confirmed_gear_subtype(self):
        response = search_service_discovery_catalog(
            gear_request(
                "spur_gear",
                requirements={
                    "part_type_specifications": {
                        "face_width_mm": {"exact": 20},
                    }
                },
            ),
            provider_records=self.records,
        )
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertEqual(tasowheel["match"]["status"], "partial_match")
        self.assertTrue(
            any(item["field"] == "part_type" for item in tasowheel["matched_attributes"])
        )
        self.assertTrue(
            any(item["field"] == "face_width_mm" for item in tasowheel["unknown_attributes"])
        )

    def test_tasowheel_tolerance_is_unknown_and_not_satisfied_by_gear_quality(self):
        response = search_service_discovery_catalog(
            gear_request(
                "spur_gear",
                requirements={
                    "part_family_specifications": {
                        "tolerance_mm": {"max": 0.02},
                    }
                },
            ),
            provider_records=self.records,
        )
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertEqual(tasowheel["match"]["status"], "partial_match")
        self.assertTrue(
            any(item["field"] == "tolerance_mm" for item in tasowheel["unknown_attributes"])
        )
        self.assertFalse(
            any(
                item["field"] == "tolerance_mm" and item["status"] == "matched"
                for item in tasowheel["matched_attributes"]
            )
        )

    def test_tasowheel_shaft_tolerance_is_unknown_and_not_satisfied_by_din4(self):
        response = search_service_discovery_catalog(
            shaft_request(
                "hollow_shaft",
                requirements={
                    "part_family_specifications": {
                        "tolerance_mm": {"max": 0.02},
                    }
                },
            ),
            provider_records=self.records,
        )
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertEqual(tasowheel["match"]["status"], "partial_match")
        self.assertTrue(
            any(item["field"] == "tolerance_mm" for item in tasowheel["unknown_attributes"])
        )

    def test_tasowheel_shaft_length_outer_diameter_and_spline_module_match(self):
        response = search_service_discovery_catalog(
            shaft_request(
                "splined_shaft",
                requirements={
                    "part_family_specifications": {
                        "length_mm": {"max": 500},
                        "outer_diameter_mm": {"exact": 100},
                    },
                    "part_type_specifications": {
                        "spline_module": {"exact": 2},
                    },
                },
            ),
            provider_records=self.records,
        )
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertEqual(tasowheel["match"]["status"], "full_match")
        for field in ["length_mm", "outer_diameter_mm", "spline_module"]:
            self.assertTrue(
                any(item["field"] == field for item in tasowheel["matched_attributes"]),
                field,
            )

    def test_material_matching_uses_family_identifier_and_keeps_grades_as_evidence(self):
        response = search_service_discovery_catalog(
            gear_request(
                "spur_gear",
                requirements={
                    "generic_requirements": {
                        "materials": ["alloyed_carburizing_steel"],
                    }
                },
            ),
            provider_records=self.records,
        )
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertTrue(
            any(item["field"] == "materials" for item in tasowheel["matched_attributes"])
        )
        self.assertEqual(
            tasowheel["evidence"]["materials"][0]["available_grades"],
            ["18CrNiMo7-6", "16MnCr5", "20MnCr5"],
        )
        self.assertFalse(
            any("18CrNiMo7-6" in str(item.get("requested")) for item in tasowheel["matched_attributes"])
        )

    def test_tasowheel_provider_level_certification_can_match_request(self):
        response = search_service_discovery_catalog(
            gear_request(
                "spur_gear",
                requirements={
                    "generic_requirements": {
                        "certifications": ["ISO9001_2015"],
                    }
                },
            ),
            provider_records=self.records,
        )
        tasowheel = result_by_provider(response, "tasowheel")

        self.assertTrue(
            any(item["field"] == "certifications" for item in tasowheel["matched_attributes"])
        )
        self.assertTrue(
            any(
                item["code"] == "ISO9001_2015"
                for item in tasowheel["evidence"]["certifications"]
            )
        )

    def test_minimum_score_filters_below_threshold(self):
        response = search_service_discovery_catalog(
            gear_request(
                "spur_gear",
                requirements={
                    "part_family_specifications": {
                        "tolerance_mm": {"max": 0.02},
                    }
                },
                minimum_score=0.75,
            ),
            provider_records=self.records,
        )
        provider_ids = {result["provider"]["provider_id"] for result in response["results"]}

        self.assertNotIn("tasowheel", provider_ids)

        retained = search_service_discovery_catalog(
            gear_request("spur_gear", minimum_score=1.0),
            provider_records=self.records,
        )
        retained_provider_ids = {
            result["provider"]["provider_id"] for result in retained["results"]
        }
        self.assertIn("tasowheel", retained_provider_ids)

    def test_optional_match_policy_modes_are_reported_without_dropping_candidates(self):
        records = synthetic_confirmed_spur_provider()
        requirements = {
            "generic_requirements": {
                "materials": ["steel"],
                "certifications": ["full_traceability"],
            }
        }

        any_response = search_service_discovery_catalog(
            gear_request("spur_gear", requirements=requirements, optional_match_mode="any"),
            provider_records=records,
        )
        all_response = search_service_discovery_catalog(
            gear_request("spur_gear", requirements=requirements, optional_match_mode="all"),
            provider_records=records,
        )
        score_only_response = search_service_discovery_catalog(
            gear_request("spur_gear", requirements=requirements, optional_match_mode="score_only"),
            provider_records=records,
        )

        self.assertEqual(len(any_response["results"]), 1)
        self.assertEqual(len(all_response["results"]), 1)
        self.assertEqual(len(score_only_response["results"]), 1)
        self.assertTrue(any_response["results"][0]["match"]["optional_policy_satisfied"])
        self.assertFalse(all_response["results"][0]["match"]["optional_policy_satisfied"])
        self.assertTrue(score_only_response["results"][0]["match"]["optional_policy_satisfied"])
        self.assertEqual(any_response["results"][0]["match"]["status"], "partial_match")

    def test_confirmed_subtype_with_all_requirements_matched_can_full_match(self):
        response = search_service_discovery_catalog(
            gear_request(
                "spur_gear",
                requirements={
                    "part_family_specifications": {
                        "module": {"exact": 2},
                    },
                    "part_type_specifications": {
                        "face_width_mm": {"exact": 20},
                    },
                    "generic_requirements": {
                        "batch_size": 500,
                        "delivery": {"max_weeks": 12},
                        "weight_kg": 50,
                    },
                },
            ),
            provider_records=synthetic_confirmed_spur_provider(),
        )

        self.assertEqual(response["results"][0]["match"]["status"], "full_match")
        self.assertEqual(response["results"][0]["match"]["score"], 1.0)
