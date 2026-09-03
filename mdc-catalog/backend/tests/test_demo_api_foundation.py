from importlib import import_module

from django.test import SimpleTestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient


class DemoApiFoundationTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    @override_settings(DEBUG=True, MDC_DEMO_API_ENABLED=False)
    def test_debug_true_enables_demo_endpoint(self):
        response = self.client.get("/api/demo/health")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(DEBUG=False, MDC_DEMO_API_ENABLED=False)
    def test_debug_false_and_flag_false_disable_demo_endpoint(self):
        response = self.client.get("/api/demo/health")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(DEBUG=False, MDC_DEMO_API_ENABLED=True)
    def test_flag_true_enables_demo_endpoint_when_debug_false(self):
        response = self.client.get("/api/demo/health")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_local_settings_enable_demo_api(self):
        local_settings = import_module("config.settings_local")

        self.assertIs(local_settings.MDC_DEMO_API_ENABLED, True)

    @override_settings(MDC_DEMO_API_ENABLED=True)
    def test_enabled_demo_health_returns_200(self):
        response = self.client.get("/api/demo/health")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["app"], "mdc_demo")
        self.assertIs(data["demo_api_enabled"], True)

    @override_settings(MDC_DEMO_API_ENABLED=True)
    def test_enabled_backend_status_reports_selected_runtime_direction(self):
        response = self.client.get("/api/demo/service-discovery/backend-status")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["active_backend"], "fuseki_with_h5_policy")
        self.assertIn(
            "local_rdflib_with_h5_policy",
            data["fallback_backends"],
        )
        self.assertIn(
            "harmonized_yaml_h5_matcher",
            data["fallback_backends"],
        )
        self.assertIs(data["marketplace_shared_api_unchanged"], True)

    @override_settings(MDC_DEMO_API_ENABLED=True)
    def test_enabled_fuseki_smoke_test_is_safe_placeholder(self):
        response = self.client.get(
            "/api/demo/service-discovery/fuseki-smoke-test"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["status"], "not_implemented")
        self.assertIs(data["mutates_state"], False)

    @override_settings(MDC_DEMO_API_ENABLED=True)
    def test_enabled_service_discovery_demo_mutation_endpoints_return_501(self):
        endpoints = [
            "/api/demo/service-discovery/regenerate-rdf",
            "/api/demo/service-discovery/reload-fuseki",
        ]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(endpoint, data={}, format="json")

                self.assertEqual(
                    response.status_code,
                    status.HTTP_501_NOT_IMPLEMENTED,
                )
                data = response.json()
                self.assertEqual(data["status"], "not_implemented")
                self.assertIs(data["mutates_state"], False)

    def test_shared_health_endpoint_still_works(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "ok")

    def test_shared_catalog_filters_endpoint_still_works(self):
        response = self.client.get("/api/catalog/filters")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("service_types", data)
        self.assertIn("part_families", data)

    @override_settings(MDC_DEMO_API_ENABLED=True)
    def test_demo_routes_do_not_exist_under_shared_service_discovery_paths(self):
        shared_backend_status = self.client.get(
            "/api/service-discovery/backend-status"
        )
        shared_fuseki_smoke_test = self.client.get(
            "/api/service-discovery/fuseki-smoke-test"
        )

        self.assertEqual(
            shared_backend_status.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            shared_fuseki_smoke_test.status_code,
            status.HTTP_404_NOT_FOUND,
        )
