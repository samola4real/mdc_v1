from copy import deepcopy

from django.test import SimpleTestCase

from apps.api.service_discovery_search_serializers import (
    ServiceDiscoverySearchResponseSerializer,
)
from tests.test_service_discovery_search_serializer import complete_spur_gear_request


def query_interpretation() -> dict:
    payload = complete_spur_gear_request()
    return {
        "selection": {
            "service_category": payload["service_category"],
            "part_family": payload["part_family"],
            "part_type": payload["part_type"],
        },
        "requirements": payload["requirements"],
        "match_policy": payload["match_policy"],
    }


def empty_response() -> dict:
    return {
        "request_id": "req_000001",
        "consumer_id": "consumer_001",
        "query_interpretation": query_interpretation(),
        "warnings": [],
        "result_count": 0,
        "results": [],
        "status": {
            "search_executed": False,
            "message": "Response contract example only; matching is not active in H4.",
        },
    }


def result_response() -> dict:
    response = empty_response()
    response["result_count"] = 1
    response["results"] = [
        {
            "provider": {
                "provider_id": "tasowheel",
                "provider_name": "Tasowheel Oy",
            },
            "offering": {
                "offering_id": "tasowheel_precision_gears",
                "service_category": "precision_gears",
                "offering_name": "Precision gears",
                "part_family": "gear",
            },
            "match": {
                "status": "partial_match",
                "score": 0.8,
                "hard_filters_passed": True,
                "optional_policy_satisfied": True,
            },
            "matched_attributes": [],
            "unmatched_attributes": [],
            "unknown_attributes": [],
            "evidence": {
                "materials": [
                    {
                        "material": "alloyed_carburizing_steel",
                        "available_grades": [
                            "18CrNiMo7-6",
                            "16MnCr5",
                            "20MnCr5",
                        ],
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    }
                ]
            },
        }
    ]
    return response


def is_valid(payload: dict) -> bool:
    return ServiceDiscoverySearchResponseSerializer(data=payload).is_valid()


class ServiceDiscoverySearchResponseContractTests(SimpleTestCase):
    def test_valid_empty_result_response_is_accepted(self):
        serializer = ServiceDiscoverySearchResponseSerializer(data=empty_response())

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_valid_result_response_is_accepted(self):
        serializer = ServiceDiscoverySearchResponseSerializer(data=result_response())

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_provider_display_name_without_provider_name_is_rejected(self):
        payload = result_response()
        provider = payload["results"][0]["provider"]
        provider.pop("provider_name")
        provider["display_name"] = "Tasowheel Oy"

        self.assertFalse(is_valid(payload))

    def test_offering_internal_name_without_offering_name_is_rejected(self):
        payload = result_response()
        offering = payload["results"][0]["offering"]
        offering.pop("offering_name")
        offering["name"] = "Precision gears"

        self.assertFalse(is_valid(payload))

    def test_required_response_metadata_is_enforced(self):
        for field in ["request_id", "consumer_id"]:
            payload = empty_response()
            payload.pop(field)

            serializer = ServiceDiscoverySearchResponseSerializer(data=payload)

            self.assertFalse(serializer.is_valid(), field)
            self.assertIn(field, serializer.errors)

    def test_negative_result_count_is_rejected(self):
        payload = empty_response()
        payload["result_count"] = -1

        self.assertFalse(is_valid(payload))

    def test_material_grades_are_accepted_only_as_nested_material_evidence(self):
        payload = result_response()

        self.assertTrue(is_valid(payload))

        payload = result_response()
        payload["results"][0]["evidence"]["material_grades"] = ["18CrNiMo7-6"]
        self.assertFalse(is_valid(payload))

    def test_response_contract_does_not_introduce_consumer_material_grade_criteria(self):
        payload = result_response()
        payload["query_interpretation"]["requirements"]["generic_requirements"][
            "material_grades"
        ] = ["18CrNiMo7-6"]

        self.assertFalse(is_valid(payload))

    def test_query_interpretation_contains_complete_gear_example(self):
        payload = result_response()
        serializer = ServiceDiscoverySearchResponseSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        family_specs = serializer.validated_data["query_interpretation"]["requirements"][
            "part_family_specifications"
        ]
        self.assertIn("module", family_specs)
        self.assertIn("diametral_pitch", family_specs)
        self.assertIn("number_of_teeth", family_specs)
        self.assertIn("outside_diameter_mm", family_specs)
        self.assertIn("gear_quality", family_specs)
        self.assertIn("tolerance_mm", family_specs)

    def test_executed_response_accepts_search_engine_metadata(self):
        payload = result_response()
        payload["status"] = {
            "search_executed": True,
            "search_engine": "local_harmonized_service_discovery_matcher",
            "message": "Search executed using harmonized local provider data.",
        }

        serializer = ServiceDiscoverySearchResponseSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_executed_response_requires_search_engine_metadata(self):
        payload = result_response()
        payload["status"] = {
            "search_executed": True,
            "message": "Search executed using harmonized local provider data.",
        }

        self.assertFalse(is_valid(payload))

    def test_optional_policy_satisfied_must_be_boolean_when_present(self):
        payload = result_response()
        payload["results"][0]["match"]["optional_policy_satisfied"] = "yes"

        self.assertFalse(is_valid(payload))
