from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from apps.providers.catalogue_sync_service import CatalogueSyncVisibilityError

from apps.search.service_discovery_fuseki_service import (
    ServiceDiscoveryFusekiRetrievalError,
)
from apps.search.service_discovery_runtime_search import (
    FUSEKI_FALLBACK_WARNING,
    ServiceDiscoveryRuntimeSearchError,
    YAML_FALLBACK_WARNING,
    search_service_discovery_with_runtime_backends,
)
from apps.search.service_discovery_sparql_service import (
    ServiceDiscoverySparqlRetrievalError,
)
from tests.test_service_discovery_matching_alignment import gear_request


def response(search_engine: str) -> dict:
    return {
        "request_id": "req_h9",
        "consumer_id": "consumer_h9",
        "query_interpretation": {
            "selection": {
                "service_category": "precision_gears",
                "part_family": "gear",
                "part_type": "spur_gear",
            },
            "requirements": {},
            "match_policy": {
                "optional_match_mode": "any",
                "unknown_policy": "keep_as_unknown",
                "minimum_score": None,
            },
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


class ServiceDiscoveryRuntimeSearchTests(SimpleTestCase):
    def setUp(self):
        self.request = gear_request()

    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_local_rdf"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    def test_uses_fuseki_when_available(self, fuseki, local_rdf, yaml):
        fuseki.return_value = response("harmonized_fuseki_with_h5_policy")

        result = search_service_discovery_with_runtime_backends(self.request)

        self.assertEqual(
            result["status"]["search_engine"],
            "harmonized_fuseki_with_h5_policy",
        )
        fuseki.assert_called_once()
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
    def test_falls_back_to_local_rdf_when_fuseki_fails(
        self,
        fuseki,
        local_rdf,
        yaml,
    ):
        fuseki.side_effect = ServiceDiscoveryFusekiRetrievalError("down")
        local_rdf.return_value = response("harmonized_rdf_rdflib_with_h5_policy")

        result = search_service_discovery_with_runtime_backends(self.request)

        self.assertEqual(
            result["status"]["search_engine"],
            "harmonized_rdf_rdflib_with_h5_policy",
        )
        self.assertIn(FUSEKI_FALLBACK_WARNING, result["warnings"])
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
    def test_falls_back_to_yaml_when_fuseki_and_rdf_fail(
        self,
        fuseki,
        local_rdf,
        yaml,
    ):
        fuseki.side_effect = ServiceDiscoveryFusekiRetrievalError("down")
        local_rdf.side_effect = ServiceDiscoverySparqlRetrievalError("missing rdf")
        yaml.return_value = response("local_harmonized_service_discovery_matcher")

        result = search_service_discovery_with_runtime_backends(self.request)

        self.assertEqual(
            result["status"]["search_engine"],
            "local_harmonized_service_discovery_matcher",
        )
        self.assertIn(YAML_FALLBACK_WARNING, result["warnings"])

    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_local_rdf"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    def test_raises_when_all_backends_fail(self, fuseki, local_rdf, yaml):
        fuseki.side_effect = ServiceDiscoveryFusekiRetrievalError("down")
        local_rdf.side_effect = ServiceDiscoverySparqlRetrievalError("missing rdf")
        yaml.side_effect = OSError("yaml unavailable")

        with self.assertRaises(ServiceDiscoveryRuntimeSearchError):
            search_service_discovery_with_runtime_backends(self.request)

    @override_settings(MDC_CATALOG_AUTO_SYNC_ENABLED=True)
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_local_rdf"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.verify_current_catalogue_visibility"
    )
    def test_auto_mode_never_falls_back_when_authoritative_fuseki_fails(
        self, verify, fuseki, local_rdf, yaml
    ):
        verify.return_value = "current-revision"
        fuseki.side_effect = ServiceDiscoveryFusekiRetrievalError("down")

        with self.assertRaises(ServiceDiscoveryRuntimeSearchError):
            search_service_discovery_with_runtime_backends(self.request)

        verify.assert_called_once()
        local_rdf.assert_not_called()
        yaml.assert_not_called()

    @override_settings(MDC_CATALOG_AUTO_SYNC_ENABLED=True)
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_local_rdf"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.verify_current_catalogue_visibility",
        side_effect=CatalogueSyncVisibilityError("stale"),
    )
    def test_auto_mode_rejects_stale_revision_without_any_search_fallback(
        self, verify, fuseki, local_rdf, yaml
    ):
        with self.assertRaises(ServiceDiscoveryRuntimeSearchError):
            search_service_discovery_with_runtime_backends(self.request)

        verify.assert_called_once()
        fuseki.assert_not_called()
        local_rdf.assert_not_called()
        yaml.assert_not_called()

    @override_settings(MDC_CATALOG_AUTO_SYNC_ENABLED=True)
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_local_rdf"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki"
    )
    @patch(
        "apps.search.service_discovery_runtime_search.verify_current_catalogue_visibility",
        side_effect=["revision-before", "revision-after"],
    )
    def test_auto_mode_rejects_catalogue_change_during_search(
        self, verify, fuseki, local_rdf, yaml
    ):
        fuseki.return_value = response("harmonized_fuseki_with_h5_policy")

        with self.assertRaises(ServiceDiscoveryRuntimeSearchError):
            search_service_discovery_with_runtime_backends(self.request)

        self.assertEqual(verify.call_count, 2)
        local_rdf.assert_not_called()
        yaml.assert_not_called()
