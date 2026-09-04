from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIClient

from tests.test_service_discovery_search_endpoint import endpoint_response
from tests.test_service_discovery_search_response_contract import result_response
from tests.test_service_discovery_search_serializer import complete_spur_gear_request


class PublicApiContractTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_stable_health_and_v1_alias_match(self):
        stable = self.client.get("/api/health")
        alias = self.client.get("/api/v1/health")

        self.assertEqual(stable.status_code, status.HTTP_200_OK)
        self.assertEqual(alias.status_code, status.HTTP_200_OK)
        self.assertEqual(stable.json(), alias.json())
        self.assertEqual(
            stable.json(),
            {
                "contract_version": "1.0",
                "status": "ok",
                "service": "maasai-mdc",
            },
        )

    def test_stable_filters_and_v1_alias_match(self):
        stable = self.client.get("/api/catalog/filters")
        alias = self.client.get("/api/v1/catalog/filters")

        self.assertEqual(stable.status_code, status.HTTP_200_OK)
        self.assertEqual(alias.status_code, status.HTTP_200_OK)
        self.assertEqual(stable.json(), alias.json())

        data = stable.json()
        self.assertEqual(data["contract_version"], "1.0")
        self.assertEqual(
            set(data),
            {
                "contract_version",
                "service_categories",
                "part_families",
                "part_types",
                "materials",
                "processes",
                "certifications",
            },
        )

    @patch(
        "apps.api.views.post_views.search_service_discovery_with_runtime_backends"
    )
    def test_stable_search_defaults_contract_version_and_shapes_response(self, runtime_search):
        runtime_search.return_value = result_response()

        response = self.client.post(
            "/api/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["contract_version"], "1.0")
        self.assertEqual(
            set(data),
            {
                "contract_version",
                "request_id",
                "service_category",
                "part_family",
                "part_type",
                "result_count",
                "results",
            },
        )
        self.assertNotIn("consumer_id", data)
        self.assertNotIn("query_interpretation", data)
        self.assertNotIn("warnings", data)
        self.assertNotIn("status", data)

        first = data["results"][0]
        self.assertEqual(
            set(first),
            {
                "provider_id",
                "provider_name",
                "offering_id",
                "offering_name",
                "service_category",
                "part_family",
                "match",
                "matched_capabilities",
                "unmatched_capabilities",
                "unknown_capabilities",
            },
        )
        self.assertNotIn("evidence", first)
        self.assertNotIn("hard_filters_passed", first["match"])
        self.assertNotIn("optional_policy_satisfied", first["match"])

    @patch(
        "apps.api.views.post_views.search_service_discovery_with_runtime_backends"
    )
    def test_explicit_contract_version_1_is_accepted(self, runtime_search):
        runtime_search.return_value = endpoint_response("harmonized_fuseki_with_h5_policy")
        payload = complete_spur_gear_request()
        payload["contract_version"] = "1.0"

        response = self.client.post(
            "/api/service-discovery/search",
            data=payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["contract_version"], "1.0")

    def test_unsupported_contract_version_is_rejected(self):
        payload = complete_spur_gear_request()
        payload["contract_version"] = "2.0"

        response = self.client.post(
            "/api/service-discovery/search",
            data=payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["contract_version"], "1.0")
        self.assertEqual(
            response.json()["error"]["code"],
            "unsupported_contract_version",
        )

    @patch(
        "apps.api.views.post_views.search_service_discovery_with_runtime_backends"
    )
    def test_v1_search_alias_uses_same_contract(self, runtime_search):
        runtime_search.return_value = endpoint_response("harmonized_fuseki_with_h5_policy")

        stable = self.client.post(
            "/api/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
        )
        alias = self.client.post(
            "/api/v1/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
        )

        self.assertEqual(stable.status_code, status.HTTP_200_OK)
        self.assertEqual(alias.status_code, status.HTTP_200_OK)
        self.assertEqual(stable.json(), alias.json())

    def test_invalid_selection_uses_public_error_contract(self):
        payload = complete_spur_gear_request()
        payload["service_category"] = "unknown_service_category"

        response = self.client.post(
            "/api/service-discovery/search",
            data=payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["contract_version"], "1.0")
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_service_discovery_request",
        )

    def test_legacy_endpoints_are_not_added_to_v1_alias_contract(self):
        self.assertEqual(
            self.client.post("/api/v1/catalog/search", data={}, format="json").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.post("/api/v1/provider-publication", data={}, format="json").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.get("/api/v1/providers/tasowheel").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.get("/api/v1/offerings/tasowheel_gears_shafts_precision").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_legacy_routes_remain_available_only_under_api(self):
        self.assertNotEqual(
            self.client.post("/api/catalog/search", data={}, format="json").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertNotEqual(
            self.client.post("/api/provider-publication", data={}, format="json").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.get("/api/providers/tasowheel").status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.client.get("/api/offerings/tasowheel_gears_shafts_precision").status_code,
            status.HTTP_200_OK,
        )

    def test_demo_api_is_not_in_v1_alias_contract(self):
        response = self.client.get("/api/v1/demo/health")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
