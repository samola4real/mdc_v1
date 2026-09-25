from io import StringIO
from datetime import timedelta
import uuid
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.ontology.service_discovery_rdf_mappings import offering_resource

from apps.providers.catalogue_sync_service import (
    CatalogueSyncBusy,
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


@override_settings(
    MDC_CATALOG_SYNC_ENABLED=True,
    SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT="http://example.invalid/mdc/data?default",
)
class CatalogueSyncConcurrencyTests(TestCase):
    def make_publication(self, suffix):
        provider = Provider.objects.create(
            provider_id=f"concurrent_{suffix}",
            provider_name=f"Concurrent {suffix}",
            country="Finland",
            status=Provider.Status.ACTIVE,
        )
        Offering.objects.create(
            provider=provider,
            offering_id=f"concurrent_{suffix}_precision_gears",
            offering_name="Gears",
            service_category="precision_gears",
            part_family="gear",
            support_status=Offering.SupportStatus.CONFIRMED,
        )
        publication = ProviderPublication.objects.create(
            provider=provider,
            provider_id_snapshot=provider.provider_id,
            operation=ProviderPublication.Operation.UPDATE,
            status=ProviderPublication.Status.SYNC_PENDING,
        )
        event = CatalogueSyncEvent.objects.create(
            publication=publication,
            entity_type=CatalogueSyncEvent.EntityType.PROVIDER,
            entity_id=provider.provider_id,
            operation=CatalogueSyncEvent.Operation.UPSERT,
        )
        return provider, publication, event

    def test_new_committed_write_during_put_rebuilds_before_success(self):
        provider, publication, event = self.make_publication("first")
        newer = {"publication": None}

        def commit_newer_write(_graph, **_kwargs):
            if newer["publication"] is not None:
                return
            newer["publication"] = ProviderPublication.objects.create(
                provider=provider,
                provider_id_snapshot=provider.provider_id,
                operation=ProviderPublication.Operation.UPDATE,
                status=ProviderPublication.Status.SYNC_PENDING,
            )
            CatalogueSyncEvent.objects.create(
                publication=newer["publication"],
                entity_type=CatalogueSyncEvent.EntityType.PROVIDER,
                entity_id=provider.provider_id,
                operation=CatalogueSyncEvent.Operation.UPSERT,
            )

        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki",
            side_effect=commit_newer_write,
        ) as replace:
            result = process_publication_sync(publication.id)

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(replace.call_count, 2)
        publication.refresh_from_db()
        event.refresh_from_db()
        self.assertEqual(publication.status, ProviderPublication.Status.SYNCED)
        self.assertEqual(event.status, CatalogueSyncEvent.Status.SUCCEEDED)
        self.assertEqual(event.attempt_count, 1)
        self.assertEqual(
            CatalogueSyncEvent.objects.filter(status=CatalogueSyncEvent.Status.PENDING).count(),
            1,
        )

    def test_single_publication_selection_does_not_process_other_pending_publication(self):
        _provider1, publication1, event1 = self.make_publication("one")
        _provider2, _publication2, event2 = self.make_publication("two")
        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki"
        ) as replace:
            summary = process_pending_catalogue_sync(publication_id=publication1.id)
        self.assertEqual(summary["selected"], 1)
        self.assertEqual(summary["succeeded"], 1)
        replace.assert_called_once()
        event1.refresh_from_db()
        event2.refresh_from_db()
        self.assertEqual(event1.status, CatalogueSyncEvent.Status.SUCCEEDED)
        self.assertEqual(event2.status, CatalogueSyncEvent.Status.PENDING)

    def test_active_global_lease_prevents_overlapping_graph_replace(self):
        _provider, publication, event = self.make_publication("leased")
        CatalogueSyncLease.objects.update_or_create(
            key="service_discovery_catalogue",
            defaults={
                "owner_token": uuid.uuid4(),
                "expires_at": timezone.now() + timedelta(minutes=5),
            },
        )
        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki"
        ) as replace:
            with self.assertRaises(CatalogueSyncBusy):
                process_publication_sync(publication.id)
        replace.assert_not_called()
        event.refresh_from_db()
        self.assertEqual(event.status, CatalogueSyncEvent.Status.PENDING)
        self.assertEqual(event.attempt_count, 0)

    def test_retrying_old_upsert_after_delete_cannot_resurrect_offering(self):
        provider, old_publication, old_event = self.make_publication("deleted")
        offering_id = "concurrent_deleted_precision_gears"
        Offering.objects.get(offering_id=offering_id).delete()
        delete_publication = ProviderPublication.objects.create(
            provider=provider,
            provider_id_snapshot=provider.provider_id,
            operation=ProviderPublication.Operation.DELETE,
            status=ProviderPublication.Status.SYNC_PENDING,
        )
        CatalogueSyncEvent.objects.create(
            publication=delete_publication,
            entity_type=CatalogueSyncEvent.EntityType.OFFERING,
            entity_id=offering_id,
            operation=CatalogueSyncEvent.Operation.DELETE,
        )
        captured = {}

        def capture(graph, **_kwargs):
            captured["graph"] = graph

        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki",
            side_effect=capture,
        ):
            result = process_publication_sync(old_publication.id)

        self.assertEqual(result["status"], "succeeded")
        old_event.refresh_from_db()
        self.assertEqual(old_event.status, CatalogueSyncEvent.Status.SUCCEEDED)
        self.assertFalse(
            any(
                captured["graph"].triples(
                    (offering_resource(offering_id), None, None)
                )
            )
        )

    def test_rebuild_rejects_outbox_selection_options(self):
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command(
                "sync_service_discovery_catalogue",
                "--rebuild",
                "--limit",
                "1",
                stdout=out,
            )

    def test_publication_selection_rejects_limit(self):
        _provider, publication, _event = self.make_publication("selected")
        with self.assertRaises(CommandError):
            call_command(
                "sync_service_discovery_catalogue",
                "--publication-id",
                str(publication.id),
                "--limit",
                "1",
                stdout=StringIO(),
            )
