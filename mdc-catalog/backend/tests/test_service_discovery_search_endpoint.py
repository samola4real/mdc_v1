from unittest.mock import patch
import json

from django.test import SimpleTestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.search.service_discovery_fuseki_service import (
    ServiceDiscoveryFusekiRetrievalError,
)
from apps.search.service_discovery_runtime_search import (
    FUSEKI_FALLBACK_WARNING,
    ServiceDiscoveryRuntimeSearchError,
    YAML_FALLBACK_WARNING,
)
from apps.search.service_discovery_sparql_service import (
    ServiceDiscoverySparqlRetrievalError,
)
from tests.test_service_discovery_search_serializer import complete_spur_gear_request


def endpoint_response(search_engine: str) -> dict:
    payload = complete_spur_gear_request()
    return {
        "request_id": payload["request_id"],
        "consumer_id": payload["consumer_id"],
        "query_interpretation": {
            "selection": {
                "service_category": payload["service_category"],
                "part_family": payload["part_family"],
                "part_type": payload["part_type"],
            },
            "requirements": payload["requirements"],
            "match_policy": payload["match_policy"],
        },
        "warnings": [],
        "result_count": 0,
        "results": [],
        "status": {
            "search_executed": True,
            "search_engine": search_engine,
            "message": f"Search executed by {search_engine}.",
        },
    }


def frontend_like_nested_payload() -> dict:
    return {
        "request_id": "demo_request_001",
        "consumer_id": "consumer_demo_001",
        "selection": {
            "service_category": "precision_gears",
            "part_family": "gear",
            "part_type": "spur_gear",
        },
        "requirements": {
            "part_family_specifications": {
                "material": "alloyed_carburizing_steel",
                "processes": ["hobbing", "turn_mill"],
                "certification": "ISO9001_2015",
            },
            "part_type_specifications": {
                "module": 2.0,
                "outside_diameter_mm": 100,
            },
            "generic_requirements": {},
        },
        "match_policy": {
            "unknown_policy": "keep_as_unknown",
            "optional_match_mode": "score_only",
        },
    }


class ServiceDiscoverySearchEndpointTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    def test_post_service_discovery_search_no_longer_returns_404(self, fuseki):
        fuseki.return_value = endpoint_response("harmonized_fuseki_with_h5_policy")

        response = self.client.post(
            "/api/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
        )

        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_existing_shared_health_endpoint_still_works(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "ok")

    def test_existing_shared_catalog_filters_endpoint_still_works(self):
        response = self.client.get("/api/catalog/filters")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("service_types", response.json())

    @override_settings(DEBUG=False, MDC_DEMO_API_ENABLED=False)
    def test_demo_health_remains_disabled_when_debug_and_flag_are_false(self):
        response = self.client.get("/api/demo/health")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(MDC_DEMO_API_ENABLED=True)
    def test_demo_health_remains_controlled_by_feature_flag(self):
        response = self.client.get("/api/demo/health")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["app"], "mdc_demo")

    def test_invalid_payload_returns_400(self):
        response = self.client.post(
            "/api/service-discovery/search",
            data={"request_id": "missing_required_fields"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_frontend_like_nested_payload_returns_400_not_500(self):
        response = self.client.post(
            "/api/service-discovery/search",
            data=frontend_like_nested_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def test_frontend_like_nested_payload_returns_json_safe_errors(self):
        response = self.client.post(
            "/api/service-discovery/search",
            data=frontend_like_nested_payload(),
            format="json",
        )

        data = response.json()
        self.assertEqual(data["status"]["search_executed"], False)
        self.assertEqual(data["status"]["search_engine"], "not_executed")
        self.assertEqual(
            data["status"]["message"],
            "Invalid service-discovery search request.",
        )
        self.assertIn("errors", data)
        json.dumps(data["errors"])

    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    def test_valid_minimal_payload_returns_200(self, fuseki):
        payload = complete_spur_gear_request()
        payload["requirements"] = {}
        fuseki.return_value = endpoint_response("harmonized_fuseki_with_h5_policy")

        response = self.client.post(
            "/api/service-discovery/search",
            data=payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_local_rdf"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    def test_endpoint_uses_fuseki_when_available(self, fuseki, local_rdf, yaml):
        fuseki.return_value = endpoint_response("harmonized_fuseki_with_h5_policy")

        response = self.client.post(
            "/api/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["status"]["search_engine"],
            "harmonized_fuseki_with_h5_policy",
        )
        local_rdf.assert_not_called()
        yaml.assert_not_called()

    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_local_rdf"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    def test_endpoint_falls_back_to_local_rdf_when_fuseki_fails(
        self,
        fuseki,
        local_rdf,
        yaml,
    ):
        fuseki.side_effect = ServiceDiscoveryFusekiRetrievalError("down")
        local_rdf.return_value = endpoint_response(
            "harmonized_rdf_rdflib_with_h5_policy"
        )

        response = self.client.post(
            "/api/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(FUSEKI_FALLBACK_WARNING, response.json()["warnings"])
        yaml.assert_not_called()

    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_local_rdf"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    def test_endpoint_falls_back_to_yaml_when_fuseki_and_rdf_fail(
        self,
        fuseki,
        local_rdf,
        yaml,
    ):
        fuseki.side_effect = ServiceDiscoveryFusekiRetrievalError("down")
        local_rdf.side_effect = ServiceDiscoverySparqlRetrievalError("missing rdf")
        yaml.return_value = endpoint_response(
            "local_harmonized_service_discovery_matcher"
        )

        response = self.client.post(
            "/api/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(YAML_FALLBACK_WARNING, response.json()["warnings"])

    @patch(
        "apps.api.views.post_views.search_service_discovery_with_runtime_backends"
    )
    def test_endpoint_returns_503_when_all_backends_fail(self, runtime_search):
        runtime_search.side_effect = ServiceDiscoveryRuntimeSearchError(
            "All service-discovery search backends failed."
        )

        response = self.client.post(
            "/api/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    def test_response_contract_fields_are_present(self, fuseki):
        fuseki.return_value = endpoint_response("harmonized_fuseki_with_h5_policy")

        response = self.client.post(
            "/api/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
        )

        data = response.json()
        self.assertIs(data["status"]["search_executed"], True)
        self.assertIn("search_engine", data["status"])
        for field in [
            "request_id",
            "consumer_id",
            "result_count",
            "results",
            "warnings",
        ]:
            self.assertIn(field, data)

    def test_endpoint_is_not_registered_under_demo_api(self):
        response = self.client.post(
            "/api/demo/service-discovery/search",
            data=complete_spur_gear_request(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
