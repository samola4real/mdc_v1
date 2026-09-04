from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from tests.test_provider_publication_api import make_valid_provider_publication_payload
from tests.test_service_discovery_search_endpoint import endpoint_response
from tests.test_service_discovery_search_serializer import complete_spur_gear_request


PRODUCTION_ROUTE_SETTINGS = {
    "DEBUG": False,
    "MDC_DEMO_API_ENABLED": False,
    "MDC_PROVIDER_PUBLICATION_ENABLED": False,
    "SECURE_SSL_REDIRECT": True,
}


@override_settings(**PRODUCTION_ROUTE_SETTINGS)
class ProductionRouteSafetyTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_canonical_health_available(self):
        response = self.client.get("/api/health", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["contract_version"], "1.0")

    def test_canonical_catalog_filters_available(self):
        response = self.client.get("/api/catalog/filters", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["contract_version"], "1.0")

    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    def test_canonical_service_discovery_search_available(self, fuseki):
        fuseki.return_value = endpoint_response("harmonized_fuseki_with_h5_policy")

        response = self.client.post(
            "/api/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["contract_version"], "1.0")

    def test_url_versioned_routes_are_unavailable(self):
        self.assertEqual(
            self.client.get("/api/v1/health", secure=True).status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.get("/api/v1/catalog/filters", secure=True).status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.post(
                "/api/v1/service-discovery/search",
                data=complete_spur_gear_request(),
                format="json",
                secure=True,
            ).status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_demo_routes_unavailable_by_default_in_production(self):
        response = self.client.get("/api/demo/health", secure=True)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_provider_publication_unavailable_by_default_in_production(self):
        response = self.client.post(
            "/api/provider-publication",
            data=make_valid_provider_publication_payload(),
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.json()["error"]["code"],
            "provider_publication_disabled",
        )
