from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from rdflib import Graph

from apps.ontology.service_discovery_rdf_generator import build_service_discovery_graph
from apps.ontology.service_discovery_rdf_mappings import offering_resource
from apps.providers.catalogue_sync_service import (
    CatalogueSyncDisabled,
    CatalogueSyncTransportError,
    process_pending_catalogue_sync,
    process_publication_sync,
    rebuild_service_discovery_catalogue,
)
from apps.providers.models import CatalogueSyncEvent, Offering, Provider, ProviderPublication
from apps.providers.service_discovery_db_repository import import_service_discovery_provider_records
from apps.providers.service_discovery_loaders import load_service_discovery_providers


class _Response:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@override_settings(
    MDC_CATALOG_SYNC_ENABLED=True,
    SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT="http://example.invalid/mdc/data?default",
    FUSEKI_SYNC_TIMEOUT_SECONDS=2,
)
class CatalogueSyncServiceTests(TestCase):
    def make_provider(self, suffix="one"):
        provider = Provider.objects.create(
            provider_id=f"sync_{suffix}",
            provider_name=f"Sync {suffix}",
            country="Finland",
            status=Provider.Status.ACTIVE,
        )
        offering = Offering.objects.create(
            provider=provider,
            offering_id=f"sync_{suffix}_precision_gears",
            offering_name="Precision gears",
            service_category="precision_gears",
            part_family="gear",
            support_status=Offering.SupportStatus.CONFIRMED,
            sequence_index=0,
        )
        publication = ProviderPublication.objects.create(
            provider=provider,
            provider_id_snapshot=provider.provider_id,
            operation=ProviderPublication.Operation.UPDATE,
            status=ProviderPublication.Status.SYNC_PENDING,
        )
        provider_event = CatalogueSyncEvent.objects.create(
            publication=publication,
            entity_type=CatalogueSyncEvent.EntityType.PROVIDER,
            entity_id=provider.provider_id,
            operation=CatalogueSyncEvent.Operation.UPSERT,
        )
        offering_event = CatalogueSyncEvent.objects.create(
            publication=publication,
            entity_type=CatalogueSyncEvent.EntityType.OFFERING,
            entity_id=offering.offering_id,
            operation=CatalogueSyncEvent.Operation.UPSERT,
        )
        return provider, offering, publication, [provider_event, offering_event]

    @override_settings(MDC_CATALOG_SYNC_ENABLED=False)
    def test_disabled_sync_does_not_claim_or_call_http(self):
        _provider, _offering, publication, events = self.make_provider()
        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki"
        ) as replace:
            with self.assertRaises(CatalogueSyncDisabled):
                process_publication_sync(publication.id)
        replace.assert_not_called()
        for event in events:
            event.refresh_from_db()
            self.assertEqual(event.status, CatalogueSyncEvent.Status.PENDING)
            self.assertEqual(event.attempt_count, 0)

    @override_settings(SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT="")
    def test_missing_endpoint_fails_safely_after_claim(self):
        _provider, _offering, publication, events = self.make_provider()
        result = process_publication_sync(publication.id)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["failure_code"], "sync_configuration_error")
        publication.refresh_from_db()
        self.assertEqual(publication.status, ProviderPublication.Status.SYNC_FAILED)
        self.assertIsNone(publication.completed_at)
        for event in events:
            event.refresh_from_db()
            self.assertEqual(event.status, CatalogueSyncEvent.Status.FAILED)
            self.assertEqual(event.attempt_count, 1)
            self.assertEqual(event.last_error, "sync_configuration_error")

    def test_graph_store_put_uses_db_backed_turtle(self):
        records = load_service_discovery_providers()
        import_service_discovery_provider_records(records)
        expected = build_service_discovery_graph(provider_records=records)
        self.assertEqual(len(expected), 673)
        captured = {}

        def fake_urlopen(request, timeout):
            captured["method"] = request.get_method()
            captured["content_type"] = request.get_header("Content-type")
            captured["body"] = request.data
            captured["timeout"] = timeout
            return _Response()

        with patch("apps.providers.catalogue_sync_service.urlopen", side_effect=fake_urlopen):
            result = rebuild_service_discovery_catalogue()

        self.assertEqual(result["triple_count"], 673)
        self.assertEqual(captured["method"], "PUT")
        self.assertIn("text/turtle", captured["content_type"])
        self.assertEqual(captured["timeout"], 2)
        actual = Graph()
        actual.parse(data=captured["body"].decode("utf-8"), format="turtle")
        self.assertEqual(set(actual), set(expected))

    def test_success_settles_all_events_with_one_graph_replace(self):
        _provider, _offering, publication, events = self.make_provider()
        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki"
        ) as replace:
            result = process_publication_sync(publication.id)
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["event_count"], 2)
        replace.assert_called_once()
        publication.refresh_from_db()
        self.assertEqual(publication.status, ProviderPublication.Status.SYNCED)
        self.assertIsNotNone(publication.completed_at)
        for event in events:
            event.refresh_from_db()
            self.assertEqual(event.status, CatalogueSyncEvent.Status.SUCCEEDED)
            self.assertEqual(event.attempt_count, 1)
            self.assertEqual(event.last_error, "")
            self.assertIsNotNone(event.processed_at)

    def test_failure_is_retryable_without_operational_rollback(self):
        provider, offering, publication, events = self.make_provider()
        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki",
            side_effect=CatalogueSyncTransportError("secret server detail"),
        ):
            failed = process_publication_sync(publication.id)
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(failed["failure_code"], "fuseki_transport_error")
        self.assertTrue(Provider.objects.filter(pk=provider.pk).exists())
        self.assertTrue(Offering.objects.filter(pk=offering.pk).exists())
        publication.refresh_from_db()
        self.assertEqual(publication.status, ProviderPublication.Status.SYNC_FAILED)
        for event in events:
            event.refresh_from_db()
            self.assertEqual(event.status, CatalogueSyncEvent.Status.FAILED)
            self.assertEqual(event.attempt_count, 1)
            self.assertNotIn("secret", event.last_error)

        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki"
        ) as replace:
            succeeded = process_publication_sync(publication.id)
        self.assertEqual(succeeded["status"], "succeeded")
        replace.assert_called_once()
        publication.refresh_from_db()
        self.assertEqual(publication.status, ProviderPublication.Status.SYNCED)
        for event in events:
            event.refresh_from_db()
            self.assertEqual(event.status, CatalogueSyncEvent.Status.SUCCEEDED)
            self.assertEqual(event.attempt_count, 2)

    def test_succeeded_publication_is_noop_on_repeated_processing(self):
        _provider, _offering, publication, _events = self.make_provider()
        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki"
        ) as replace:
            first = process_publication_sync(publication.id)
            second = process_publication_sync(publication.id)
        self.assertEqual(first["status"], "succeeded")
        self.assertEqual(second["status"], "noop")
        replace.assert_called_once()

    def test_inactive_offering_is_absent_from_rebuilt_graph(self):
        _provider, offering, _publication, _events = self.make_provider()
        offering.is_active = False
        offering.save(update_fields=["is_active", "updated_at"])
        captured = {}

        def capture(graph, **_kwargs):
            captured["graph"] = graph

        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki",
            side_effect=capture,
        ):
            rebuild_service_discovery_catalogue()
        subject = offering_resource(offering.offering_id)
        self.assertFalse(any(captured["graph"].triples((subject, None, None))))

    def test_suspended_provider_disappears_from_rebuilt_graph(self):
        provider, _offering, _publication, _events = self.make_provider()
        provider.status = Provider.Status.SUSPENDED
        provider.save(update_fields=["status", "updated_at"])
        captured = {}

        def capture(graph, **_kwargs):
            captured["graph"] = graph

        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki",
            side_effect=capture,
        ):
            result = rebuild_service_discovery_catalogue()
        self.assertEqual(result["triple_count"], 0)
        self.assertEqual(len(captured["graph"]), 0)

    def test_batch_limit_processes_each_selected_publication_once(self):
        self.make_provider("one")
        self.make_provider("two")
        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki"
        ) as replace:
            summary = process_pending_catalogue_sync(limit=1)
        self.assertEqual(summary["selected"], 1)
        self.assertEqual(summary["succeeded"], 1)
        self.assertEqual(summary["failed"], 0)
        replace.assert_called_once()
        self.assertEqual(
            CatalogueSyncEvent.objects.filter(status=CatalogueSyncEvent.Status.SUCCEEDED).count(),
            2,
        )
        self.assertEqual(
            CatalogueSyncEvent.objects.filter(status=CatalogueSyncEvent.Status.PENDING).count(),
            2,
        )

    def test_rebuild_command_does_not_create_history_or_outbox(self):
        records = load_service_discovery_providers()
        import_service_discovery_provider_records(records)
        out = StringIO()
        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki"
        ):
            call_command("sync_service_discovery_catalogue", "--rebuild", stdout=out)
        self.assertIn("triples synchronized: 673", out.getvalue())
        self.assertEqual(ProviderPublication.objects.count(), 0)
        self.assertEqual(CatalogueSyncEvent.objects.count(), 0)

    def test_failed_command_returns_nonzero_without_sensitive_error(self):
        self.make_provider()
        out = StringIO()
        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki",
            side_effect=CatalogueSyncTransportError("private endpoint response body"),
        ):
            with self.assertRaises(CommandError) as context:
                call_command("sync_service_discovery_catalogue", stdout=out)
        combined = out.getvalue() + str(context.exception)
        self.assertIn("failed=1", combined)
        self.assertNotIn("private endpoint", combined)
        self.assertNotIn("response body", combined)
