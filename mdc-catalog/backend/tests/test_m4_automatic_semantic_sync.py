from copy import deepcopy
from datetime import timedelta
import uuid
from unittest.mock import patch

from django.test import TransactionTestCase, override_settings
from django.utils import timezone
from rdflib import Graph
from rest_framework import status
from rest_framework.test import APIClient

from apps.ontology.service_discovery_rdf_mappings import MDC
from apps.providers.catalogue_sync_service import (
    CatalogueSyncTransportError,
    process_pending_catalogue_sync,
    process_publication_sync,
)
from apps.providers.models import (
    CatalogueSyncEvent,
    CatalogueSyncLease,
    Offering,
    Provider,
    ProviderPublication,
)
from apps.search.service_discovery_fuseki_service import (
    ServiceDiscoveryFusekiRetrievalError,
)
from apps.search.service_discovery_matching_alignment import (
    search_service_discovery_catalog_via_local_rdf,
)
from tests.test_service_discovery_publication_serializer import (
    make_valid_family_level_gears_payload,
)


AUTO_SETTINGS = {
    "MDC_PROVIDER_PUBLICATION_ENABLED": True,
    "MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED": False,
    "MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED": False,
    "MDC_PROVIDER_CONCURRENCY_REQUIRED": True,
    "MDC_CATALOG_SYNC_ENABLED": True,
    "MDC_CATALOG_AUTO_SYNC_ENABLED": True,
    "SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT": (
        "http://example.invalid/mdc/sparql"
    ),
    "SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT": (
        "http://example.invalid/mdc/data?default"
    ),
    "FUSEKI_TIMEOUT_SECONDS": 1,
    "FUSEKI_SYNC_TIMEOUT_SECONDS": 1,
}


@override_settings(**AUTO_SETTINGS)
class M4AutomaticSemanticSyncTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = APIClient()
        self.remote_graph = Graph()
        self.query_available = True

        def replace_graph(graph, **_kwargs):
            replacement = Graph()
            for triple in graph:
                replacement.add(triple)
            self.remote_graph = replacement
        self.replace_graph = replace_graph

        def query_revision(_query, **_kwargs):
            if not self.query_available:
                raise ServiceDiscoveryFusekiRetrievalError("unavailable")
            revisions = list(
                self.remote_graph.objects(MDC.CatalogueState, MDC.catalogueRevision)
            )
            return [{"revision": revision} for revision in revisions]

        def search_remote(canonical_request, **_kwargs):
            if not self.query_available:
                raise ServiceDiscoveryFusekiRetrievalError("unavailable")
            return search_service_discovery_catalog_via_local_rdf(
                canonical_request,
                graph=self.remote_graph,
            )

        self.replace_patcher = patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki",
            side_effect=replace_graph,
        )
        self.query_patcher = patch(
            "apps.providers.catalogue_sync_service.execute_fuseki_sparql_query",
            side_effect=query_revision,
        )
        self.search_patcher = patch(
            "apps.search.service_discovery_runtime_search.search_service_discovery_catalog_via_fuseki",
            side_effect=search_remote,
        )
        self.replace_mock = self.replace_patcher.start()
        self.query_patcher.start()
        self.search_patcher.start()
        self.addCleanup(self.replace_patcher.stop)
        self.addCleanup(self.query_patcher.stop)
        self.addCleanup(self.search_patcher.stop)

    def provider_payload(self, provider_id="m4_primary", name="M4 Primary"):
        payload = make_valid_family_level_gears_payload()
        payload["provider_id"] = provider_id
        payload["provider_name"] = name
        return payload

    def same_category_offering(self, name, module_max):
        offering = deepcopy(make_valid_family_level_gears_payload()["offerings"][0])
        offering["offering_name"] = name
        offering["family_capabilities"]["module"]["max"] = module_max
        return offering

    def search(self, *, requirements=None):
        response = self.client.post(
            "/api/service-discovery/search",
            {
                "request_id": "m4-search",
                "consumer_id": "m4-consumer",
                "service_category": "precision_gears",
                "part_family": "gear",
                "part_type": "spur_gear",
                "requirements": requirements or {},
            },
            format="json",
        )
        return response

    def result(self, response, offering_id):
        for item in response.json()["results"]:
            if item["offering_id"] == offering_id:
                return item
        return None

    def assert_completed(self, response, expected_status):
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response.json()["status"], "completed")
        self.assertEqual(response.json()["publication_status"], "synced")
        self.assertEqual(response.json()["sync_status"], "succeeded")

    def test_complete_lifecycle_is_visible_to_the_very_next_search(self):
        primary_id = "m4_primary_precision_gears"
        sibling_id = "m4_primary_precision_gears_flexible_gear_cell"
        unrelated_id = "m4_unrelated_precision_gears"

        registered = self.client.post(
            "/api/provider-publication",
            self.provider_payload(),
            format="json",
        )
        self.assert_completed(registered, status.HTTP_201_CREATED)
        first_search = self.search()
        self.assertEqual(first_search.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(self.result(first_search, primary_id))

        added = self.client.post(
            "/api/providers/m4_primary/offerings",
            self.same_category_offering("Flexible gear cell", 18),
            format="json",
        )
        self.assert_completed(added, status.HTTP_201_CREATED)
        self.assertEqual(added.json()["offering_id"], sibling_id)
        second_search = self.search()
        self.assertEqual(
            {
                item["offering_id"]
                for item in second_search.json()["results"]
                if item["provider_id"] == "m4_primary"
            },
            {primary_id, sibling_id},
        )

        sibling_row = Offering.objects.get(offering_id=sibling_id)
        updated_capabilities = deepcopy(sibling_row.family_capabilities)
        updated_capabilities["module"]["max"] = 20

        detail = self.client.get(f"/api/offerings/{sibling_id}")
        patched = self.client.patch(
            f"/api/offerings/{sibling_id}",
            {
                "offering_name": "Updated flexible cell",
                "family_capabilities": updated_capabilities,
            },
            format="json",
            HTTP_IF_MATCH=detail["ETag"],
        )
        self.assert_completed(patched, status.HTTP_200_OK)
        self.assertEqual(
            self.result(self.search(), sibling_id)["offering_name"],
            "Updated flexible cell",
        )
        capability_update_search = self.search(
            requirements={
                "part_family_specifications": {"module": {"exact": 19}}
            }
        )
        sibling_result = self.result(capability_update_search, sibling_id)
        primary_result = self.result(capability_update_search, primary_id)
        self.assertIn(
            "module",
            {item["field"] for item in sibling_result["matched_capabilities"]},
        )
        self.assertIn(
            "module",
            {item["field"] for item in primary_result["unmatched_capabilities"]},
        )

        provider_detail = self.client.get("/api/providers/m4_primary")
        provider_patch = self.client.patch(
            "/api/providers/m4_primary",
            {"provider_name": "M4 Primary Updated"},
            format="json",
            HTTP_IF_MATCH=provider_detail["ETag"],
        )
        self.assert_completed(provider_patch, status.HTTP_200_OK)
        self.assertEqual(
            self.result(self.search(), primary_id)["provider_name"],
            "M4 Primary Updated",
        )

        offering = Offering.objects.get(offering_id=primary_id)
        retained = deepcopy(offering.family_capabilities)
        retained.pop("module")
        detail = self.client.get(f"/api/offerings/{primary_id}")
        removed = self.client.patch(
            f"/api/offerings/{primary_id}",
            {"family_capabilities": retained},
            format="json",
            HTTP_IF_MATCH=detail["ETag"],
        )
        self.assert_completed(removed, status.HTTP_200_OK)
        capability_search = self.search(
            requirements={
                "part_family_specifications": {
                    "module": {"exact": 2},
                    "diametral_pitch": {"exact": 10},
                }
            }
        )
        primary = self.result(capability_search, primary_id)
        self.assertIn(
            "module",
            {item["field"] for item in primary["unknown_capabilities"]},
        )
        self.assertNotIn(
            "diametral_pitch",
            {item["field"] for item in primary["unknown_capabilities"]},
        )

        unrelated = self.client.post(
            "/api/provider-publication",
            self.provider_payload("m4_unrelated", "M4 Unrelated"),
            format="json",
        )
        self.assert_completed(unrelated, status.HTTP_201_CREATED)
        self.assertIsNotNone(self.result(self.search(), unrelated_id))

        sibling_detail = self.client.get(f"/api/offerings/{sibling_id}")
        deleted_offering = self.client.delete(
            f"/api/offerings/{sibling_id}",
            HTTP_IF_MATCH=sibling_detail["ETag"],
        )
        self.assert_completed(deleted_offering, status.HTTP_200_OK)
        after_offering_delete = self.search()
        self.assertIsNone(self.result(after_offering_delete, sibling_id))
        self.assertIsNotNone(self.result(after_offering_delete, primary_id))

        primary_detail = self.client.get("/api/providers/m4_primary")
        deleted_provider = self.client.delete(
            "/api/providers/m4_primary",
            HTTP_IF_MATCH=primary_detail["ETag"],
        )
        self.assert_completed(deleted_provider, status.HTTP_200_OK)
        after_provider_delete = self.search()
        self.assertIsNone(self.result(after_provider_delete, primary_id))
        self.assertIsNone(self.result(after_provider_delete, sibling_id))
        self.assertIsNotNone(self.result(after_provider_delete, unrelated_id))

    def test_graph_store_failure_is_noncompleted_and_retry_converges(self):
        self.replace_mock.side_effect = CatalogueSyncTransportError("timeout")
        response = self.client.post(
            "/api/provider-publication",
            self.provider_payload("m4_retry", "M4 Retry"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.json()["status"], "accepted")
        self.assertEqual(response.json()["publication_status"], "sync_failed")
        self.assertEqual(response.json()["sync_status"], "failed")
        self.assertEqual(
            response.json()["error"]["code"],
            "catalogue_publication_incomplete",
        )
        self.assertTrue(Provider.objects.filter(provider_id="m4_retry").exists())
        self.assertEqual(Provider.objects.filter(provider_id="m4_retry").count(), 1)
        publication = ProviderPublication.objects.get(
            id=response.json()["publication_id"]
        )
        self.assertEqual(publication.status, ProviderPublication.Status.SYNC_FAILED)
        self.assertTrue(
            publication.sync_events.filter(
                status=CatalogueSyncEvent.Status.FAILED
            ).exists()
        )

        self.replace_mock.side_effect = self.replace_graph
        recovered = process_pending_catalogue_sync(publication_id=publication.id)
        self.assertEqual(recovered["succeeded"], 1)
        publication.refresh_from_db()
        self.assertEqual(publication.status, ProviderPublication.Status.SYNCED)
        self.assertIsNotNone(
            self.result(self.search(), "m4_retry_precision_gears")
        )
        self.assertEqual(Provider.objects.filter(provider_id="m4_retry").count(), 1)

    def test_query_failure_is_noncompleted_and_search_never_uses_fallback(self):
        self.query_available = False
        response = self.client.post(
            "/api/provider-publication",
            self.provider_payload("m4_query_fail", "M4 Query Fail"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.json()["publication_status"], "sync_failed")
        self.assertTrue(Provider.objects.filter(provider_id="m4_query_fail").exists())
        search = self.search()
        self.assertEqual(search.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            search.json()["error"]["code"],
            "service_discovery_search_unavailable",
        )

        self.query_available = True
        publication = ProviderPublication.objects.get(
            id=response.json()["publication_id"]
        )
        recovered = process_publication_sync(publication.id, verify_visibility=True)
        self.assertEqual(recovered["status"], "succeeded")
        self.assertIsNotNone(
            self.result(self.search(), "m4_query_fail_precision_gears")
        )

    def test_overlapping_publisher_returns_pending_without_false_completion(self):
        CatalogueSyncLease.objects.update_or_create(
            key="service_discovery_catalogue",
            defaults={
                "owner_token": uuid.uuid4(),
                "expires_at": timezone.now() + timedelta(minutes=5),
            },
        )
        response = self.client.post(
            "/api/provider-publication",
            self.provider_payload("m4_busy", "M4 Busy"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.json()["status"], "accepted")
        self.assertEqual(response.json()["publication_status"], "sync_pending")
        self.assertEqual(response.json()["sync_status"], "pending")
        publication = ProviderPublication.objects.get(
            id=response.json()["publication_id"]
        )
        self.assertTrue(
            publication.sync_events.filter(
                status=CatalogueSyncEvent.Status.PENDING,
                attempt_count=0,
            ).exists()
        )

    @override_settings(
        MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True,
        MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN="m4-service-token",
        MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True,
    )
    def test_secure_auto_mode_preserves_bearer_and_actor_boundary(self):
        payload = self.provider_payload("m4_secure", "M4 Secure")
        rejected = self.client.post(
            "/api/provider-publication", payload, format="json"
        )
        self.assertEqual(rejected.status_code, status.HTTP_401_UNAUTHORIZED)

        accepted = self.client.post(
            "/api/provider-publication",
            payload,
            format="json",
            HTTP_AUTHORIZATION="Bearer m4-service-token",
            HTTP_X_MDC_ACTOR_ID="marketplace:m4-user",
        )
        self.assert_completed(accepted, status.HTTP_201_CREATED)
        publication = ProviderPublication.objects.get(
            id=accepted.json()["publication_id"]
        )
        self.assertEqual(
            publication.submitted_by_external_id,
            "marketplace:m4-user",
        )
