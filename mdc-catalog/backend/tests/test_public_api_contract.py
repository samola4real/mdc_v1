from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIClient

from tests.test_service_discovery_search_endpoint import endpoint_response
from tests.test_service_discovery_search_serializer import complete_spur_gear_request


class PublicApiContractTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_canonical_v1_health_endpoint(self):
        response = self.client.get("/api/v1/health")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "service": "maasai-mdc",
                "version": "v1",
            },
        )

    def test_canonical_v1_catalog_filters_endpoint(self):
        response = self.client.get("/api/v1/catalog/filters")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("service_discovery", data)
        self.assertIs(data["service_discovery"]["search_contract_active"], True)

    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    def test_canonical_v1_service_discovery_search_endpoint(self, fuseki):
        fuseki.return_value = endpoint_response("harmonized_fuseki_with_h5_policy")

        response = self.client.post(
            "/api/v1/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["status"]["search_engine"], "harmonized_fuseki_with_h5_policy")
        self.assertIn("request_id", data)
        self.assertIn("result_count", data)
        self.assertIn("results", data)

    def test_canonical_v1_service_discovery_rejects_invalid_selection(self):
        payload = complete_spur_gear_request()
        payload["service_category"] = "unknown_service_category"

        response = self.client.post(
            "/api/v1/service-discovery/search",
            data=payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["status"]["search_executed"], False)

    def test_canonical_v1_service_discovery_requires_required_fields(self):
        response = self.client.post(
            "/api/v1/service-discovery/search",
            data={"request_id": "missing_required_fields"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["status"]["search_engine"], "not_executed")

    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    def test_existing_service_discovery_search_alias_remains_available(self, fuseki):
        fuseki.return_value = endpoint_response("harmonized_fuseki_with_h5_policy")

        response = self.client.post(
            "/api/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_legacy_endpoints_are_not_added_to_canonical_v1_contract(self):
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

    def test_legacy_compatibility_endpoints_remain_available(self):
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

    def test_demo_api_is_not_in_canonical_v1_contract(self):
        response = self.client.get("/api/v1/demo/health")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
