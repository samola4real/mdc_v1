from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.providers.catalogue_sync_service import (
    STALE_PROCESSING_FAILURE_CODE,
    process_publication_sync,
    recover_stale_processing_sync,
)
from apps.providers.models import CatalogueSyncEvent, Provider, ProviderPublication


@override_settings(
    MDC_CATALOG_SYNC_ENABLED=True,
    MDC_CATALOG_SYNC_PROCESSING_LEASE_SECONDS=300,
    SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT="http://example.invalid/mdc/data?default",
)
class CatalogueSyncRecoveryTests(TestCase):
    def make_processing(self, suffix, *, age_seconds, attempt_count=1):
        provider = Provider.objects.create(
            provider_id=f"recovery_{suffix}",
            provider_name=f"Recovery {suffix}",
            country="Finland",
            status=Provider.Status.ACTIVE,
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
            status=CatalogueSyncEvent.Status.PROCESSING,
            attempt_count=attempt_count,
            processed_at=timezone.now() - timedelta(seconds=age_seconds),
        )
        return provider, publication, event

    def test_only_expired_processing_lease_is_recovered(self):
        _old_provider, old_publication, old_event = self.make_processing(
            "old", age_seconds=600, attempt_count=3
        )
        _fresh_provider, fresh_publication, fresh_event = self.make_processing(
            "fresh", age_seconds=30, attempt_count=2
        )

        result = recover_stale_processing_sync()
        self.assertEqual(result, {"events": 1, "publications": 1})

        old_event.refresh_from_db()
        old_publication.refresh_from_db()
        self.assertEqual(old_event.status, CatalogueSyncEvent.Status.FAILED)
        self.assertEqual(old_event.last_error, STALE_PROCESSING_FAILURE_CODE)
        self.assertEqual(old_event.attempt_count, 3)
        self.assertEqual(old_publication.status, ProviderPublication.Status.SYNC_FAILED)
        self.assertIsNone(old_publication.completed_at)

        fresh_event.refresh_from_db()
        fresh_publication.refresh_from_db()
        self.assertEqual(fresh_event.status, CatalogueSyncEvent.Status.PROCESSING)
        self.assertEqual(fresh_event.attempt_count, 2)
        self.assertEqual(fresh_publication.status, ProviderPublication.Status.SYNC_PENDING)

    def test_old_null_processing_timestamp_uses_created_at_as_safe_fallback(self):
        _provider, publication, event = self.make_processing(
            "legacy", age_seconds=600
        )
        old = timezone.now() - timedelta(seconds=600)
        CatalogueSyncEvent.objects.filter(pk=event.pk).update(
            processed_at=None,
            created_at=old,
        )

        result = recover_stale_processing_sync()
        self.assertEqual(result["events"], 1)
        event.refresh_from_db()
        publication.refresh_from_db()
        self.assertEqual(event.status, CatalogueSyncEvent.Status.FAILED)
        self.assertEqual(publication.status, ProviderPublication.Status.SYNC_FAILED)

    def test_recovery_command_never_contacts_fuseki(self):
        self.make_processing("command", age_seconds=600)
        out = StringIO()
        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki"
        ) as replace:
            call_command(
                "sync_service_discovery_catalogue",
                "--recover-stale",
                stdout=out,
            )
        replace.assert_not_called()
        self.assertIn("events=1", out.getvalue())
        self.assertIn("publications=1", out.getvalue())

    def test_recovered_event_is_retryable_through_normal_sync_path(self):
        _provider, publication, event = self.make_processing(
            "retry", age_seconds=600, attempt_count=4
        )
        recover_stale_processing_sync()
        event.refresh_from_db()
        self.assertEqual(event.status, CatalogueSyncEvent.Status.FAILED)

        with patch(
            "apps.providers.catalogue_sync_service.replace_service_discovery_graph_in_fuseki"
        ) as replace:
            result = process_publication_sync(publication.id)
        self.assertEqual(result["status"], "succeeded")
        replace.assert_called_once()
        event.refresh_from_db()
        publication.refresh_from_db()
        self.assertEqual(event.status, CatalogueSyncEvent.Status.SUCCEEDED)
        self.assertEqual(event.attempt_count, 5)
        self.assertEqual(publication.status, ProviderPublication.Status.SYNCED)
        self.assertIsNotNone(publication.completed_at)

    @override_settings(MDC_CATALOG_SYNC_PROCESSING_LEASE_SECONDS=float("inf"))
    def test_invalid_lease_configuration_fails_without_mutation(self):
        _provider, publication, event = self.make_processing(
            "invalid", age_seconds=600
        )
        with self.assertRaisesMessage(
            Exception,
            "MDC_CATALOG_SYNC_PROCESSING_LEASE_SECONDS must be a positive number.",
        ):
            recover_stale_processing_sync()
        event.refresh_from_db()
        publication.refresh_from_db()
        self.assertEqual(event.status, CatalogueSyncEvent.Status.PROCESSING)
        self.assertEqual(publication.status, ProviderPublication.Status.SYNC_PENDING)
