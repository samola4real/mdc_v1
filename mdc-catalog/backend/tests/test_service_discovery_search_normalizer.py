from django.test import SimpleTestCase

from apps.api.service_discovery_search_serializers import (
    ServiceDiscoverySearchRequestSerializer,
)
from apps.search.service_discovery_normalizer import (
    normalize_service_discovery_search_request,
)
from tests.test_service_discovery_search_serializer import complete_spur_gear_request


def normalize_payload(payload: dict | None = None, warnings: list | None = None):
    serializer = ServiceDiscoverySearchRequestSerializer(
        data=payload or complete_spur_gear_request()
    )
    assert serializer.is_valid(), serializer.errors
    return normalize_service_discovery_search_request(
        serializer.validated_data,
        warnings=warnings,
    )


class ServiceDiscoverySearchNormalizerTests(SimpleTestCase):
    def test_complete_spur_gear_request_normalizes(self):
        normalized = normalize_payload().to_dict()
        family_specs = normalized["requirements"]["part_family_specifications"]
        type_specs = normalized["requirements"]["part_type_specifications"]

        self.assertEqual(family_specs["module"], {"exact": 2.0})
        self.assertEqual(family_specs["diametral_pitch"], {"min": 10.0, "max": 20.0})
        self.assertEqual(family_specs["number_of_teeth"], {"exact": 40})
        self.assertEqual(family_specs["outside_diameter_mm"], {"max": 120.0})
        self.assertEqual(
            family_specs["gear_quality"],
            {"standard": "DIN", "max_class": 5.0},
        )
        self.assertEqual(family_specs["tolerance_mm"], {"max": 0.02})
        self.assertEqual(type_specs["face_width_mm"], {"exact": 20.0})

    def test_request_and_consumer_ids_are_preserved(self):
        normalized = normalize_payload().to_dict()

        self.assertEqual(normalized["request_id"], "req_000001")
        self.assertEqual(normalized["consumer_id"], "consumer_001")

    def test_selection_context_is_preserved(self):
        normalized = normalize_payload().to_dict()

        self.assertEqual(
            normalized["selection"],
            {
                "service_category": "precision_gears",
                "part_family": "gear",
                "part_type": "spur_gear",
            },
        )

    def test_specification_groups_remain_separate(self):
        normalized = normalize_payload().to_dict()

        self.assertIn("module", normalized["requirements"]["part_family_specifications"])
        self.assertNotIn("module", normalized["requirements"]["part_type_specifications"])
        self.assertIn("face_width_mm", normalized["requirements"]["part_type_specifications"])

    def test_generic_requirements_are_preserved(self):
        normalized = normalize_payload().to_dict()
        generic = normalized["requirements"]["generic_requirements"]

        self.assertEqual(generic["materials"], ["alloyed_carburizing_steel"])
        self.assertEqual(generic["processes"], ["hobbing"])
        self.assertEqual(generic["batch_size"], 500)
        self.assertEqual(generic["delivery"], {"max_weeks": 12.0})
        self.assertEqual(generic["certifications"], ["ISO9001_2015"])

    def test_match_policy_defaults_when_absent(self):
        payload = complete_spur_gear_request()
        payload.pop("match_policy")

        normalized = normalize_payload(payload).to_dict()

        self.assertEqual(
            normalized["match_policy"],
            {
                "optional_match_mode": "any",
                "unknown_policy": "keep_as_unknown",
                "minimum_score": None,
            },
        )

    def test_explicit_match_policy_is_preserved(self):
        payload = complete_spur_gear_request()
        payload["match_policy"] = {
            "optional_match_mode": "score_only",
            "unknown_policy": "reject_unknown",
            "minimum_score": 0.75,
        }

        normalized = normalize_payload(payload).to_dict()

        self.assertEqual(
            normalized["match_policy"],
            {
                "optional_match_mode": "score_only",
                "unknown_policy": "reject_unknown",
                "minimum_score": 0.75,
            },
        )

    def test_empty_requirement_groups_remain_present(self):
        payload = {
            "request_id": "req_empty",
            "consumer_id": "consumer_001",
            "service_category": "precision_gears",
            "part_family": "gear",
            "part_type": "spur_gear",
        }

        normalized = normalize_payload(payload).to_dict()

        self.assertEqual(
            normalized["requirements"],
            {
                "part_family_specifications": {},
                "part_type_specifications": {},
                "generic_requirements": {},
            },
        )

    def test_supplied_warnings_are_preserved(self):
        warnings = [{"field": "example", "message": "not active"}]
        normalized = normalize_payload(warnings=warnings).to_dict()

        self.assertEqual(normalized["warnings"], warnings)

    def test_normalization_does_not_return_results_or_response_fields(self):
        normalized = normalize_payload().to_dict()

        self.assertNotIn("results", normalized)
        self.assertNotIn("result_count", normalized)
        self.assertNotIn("status", normalized)
        self.assertNotIn("query_interpretation", normalized)
