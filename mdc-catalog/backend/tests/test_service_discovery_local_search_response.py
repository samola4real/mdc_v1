from django.test import SimpleTestCase

from apps.api.service_discovery_search_serializers import (
    ServiceDiscoverySearchResponseSerializer,
)
from apps.providers.service_discovery_loaders import load_service_discovery_providers
from apps.search.service_discovery_local_matcher import search_service_discovery_catalog
from tests.test_service_discovery_local_matcher import gear_request


class ServiceDiscoveryLocalSearchResponseTests(SimpleTestCase):
    def test_matcher_response_validates_against_h4_response_contract(self):
        response = search_service_discovery_catalog(
            gear_request("spur_gear"),
            provider_records=load_service_discovery_providers(),
        )

        serializer = ServiceDiscoverySearchResponseSerializer(data=response)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_response_uses_external_provider_and_offering_names(self):
        response = search_service_discovery_catalog(
            gear_request("spur_gear"),
            provider_records=load_service_discovery_providers(),
        )
        first = response["results"][0]

        self.assertIn("provider_name", first["provider"])
        self.assertNotIn("display_name", first["provider"])
        self.assertIn("offering_name", first["offering"])
        self.assertNotIn("name", first["offering"])

    def test_response_status_is_h4_contract_compatible_and_inactive(self):
        response = search_service_discovery_catalog(
            gear_request("spur_gear"),
            provider_records=load_service_discovery_providers(),
        )

        self.assertTrue(response["status"]["search_executed"])
        self.assertEqual(
            response["status"]["search_engine"],
            "local_harmonized_service_discovery_matcher",
        )
        self.assertIn("harmonized local provider data", response["status"]["message"])

    def test_response_exposes_optional_policy_satisfaction(self):
        response = search_service_discovery_catalog(
            gear_request("spur_gear"),
            provider_records=load_service_discovery_providers(),
        )

        self.assertIn("optional_policy_satisfied", response["results"][0]["match"])
        self.assertIsInstance(
            response["results"][0]["match"]["optional_policy_satisfied"],
            bool,
        )

    def test_response_contains_selection_explanations(self):
        response = search_service_discovery_catalog(
            gear_request("spur_gear"),
            provider_records=load_service_discovery_providers(),
        )
        first = response["results"][0]
        fields = {
            item["field"]
            for item in [
                *first["matched_attributes"],
                *first["unknown_attributes"],
                *first["unmatched_attributes"],
            ]
        }

        self.assertIn("service_category", fields)
        self.assertIn("part_family", fields)
        self.assertIn("part_type", fields)
