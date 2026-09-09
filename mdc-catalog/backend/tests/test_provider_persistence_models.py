import uuid
from copy import deepcopy

from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.providers.models import (
    CatalogueSyncEvent, Offering, Provider, ProviderCertification, ProviderPublication,
)


class ProviderPersistenceModelTests(TestCase):
    def setUp(self):
        self.provider = Provider.objects.create(
            provider_id="example_provider", provider_name="Example", country="Finland"
        )

    def offering(self, **kwargs):
        values = dict(
            provider=self.provider, offering_id="mdc_offering_1",
            offering_name="Gear manufacturing", service_category="precision_gears",
            part_family="gear",
        )
        values.update(kwargs)
        return Offering.objects.create(**values)

    def publication(self, **kwargs):
        values = dict(provider_id_snapshot=self.provider.provider_id, operation="create")
        values.update(kwargs)
        return ProviderPublication.objects.create(**values)

    def test_provider_defaults_and_identity(self):
        self.provider.refresh_from_db()
        self.assertIsInstance(self.provider.pk, uuid.UUID)
        self.assertEqual(self.provider.status, Provider.Status.DRAFT)
        self.assertEqual(self.provider.custom_provider_fields, {})
        self.assertIsNotNone(self.provider.created_at)
        self.assertIsNotNone(self.provider.updated_at)
        other = Provider.objects.create(provider_id="other", provider_name="Example", country="Finland")
        self.assertNotEqual(other.pk, self.provider.pk)

    def test_provider_external_id_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Provider.objects.create(provider_id=self.provider.provider_id, provider_name="Duplicate", country="Finland")

    def test_offering_relationship_and_defaults(self):
        offering = self.offering()
        offering.refresh_from_db()
        self.assertIsInstance(offering.pk, uuid.UUID)
        self.assertEqual(self.provider.offerings.get(), offering)
        self.assertTrue(offering.is_active)
        self.assertEqual(offering.support_status, Offering.SupportStatus.UNKNOWN)
        self.assertEqual(offering.supported_part_types, [])
        for field in ("family_capabilities", "part_type_capabilities", "generic_capabilities",
                      "custom_offering_fields", "custom_capability_fields"):
            self.assertEqual(getattr(offering, field), {})

    def test_offering_external_id_unique(self):
        self.offering()
        other = Provider.objects.create(provider_id="other", provider_name="Other", country="Finland")
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.offering(provider=other)

    def test_multiple_offerings_per_category_allowed(self):
        self.offering()
        self.offering(offering_id="mdc_offering_2")
        self.assertEqual(self.provider.offerings.count(), 2)

    def test_certification_unique_within_provider(self):
        values = dict(code="ISO9001_2015", source_type="provider_confirmed", confidence="declared")
        certification = ProviderCertification.objects.create(provider=self.provider, **values)
        self.assertIsInstance(certification.pk, uuid.UUID)
        self.assertEqual(self.provider.certifications.get(), certification)
        self.assertIsNone(certification.source_note)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ProviderCertification.objects.create(provider=self.provider, **values)
        other = Provider.objects.create(provider_id="other", provider_name="Other", country="Finland")
        ProviderCertification.objects.create(provider=other, **values)

    def test_publication_can_precede_provider(self):
        publication = self.publication()
        publication.refresh_from_db()
        self.assertIsInstance(publication.pk, uuid.UUID)
        self.assertIsNone(publication.provider)
        self.assertEqual(publication.provider_id_snapshot, "example_provider")
        self.assertEqual(publication.status, ProviderPublication.Status.RECEIVED)
        self.assertEqual(publication.contract_version, "1.0")
        for field in ("submitted_payload", "normalized_payload", "validation_errors"):
            self.assertEqual(getattr(publication, field), {})
        for field in ("submitted_by_external_id", "validated_at", "persisted_at", "completed_at"):
            self.assertIsNone(getattr(publication, field))

    def test_provider_deletion_preserves_publication_and_outbox(self):
        self.offering()
        ProviderCertification.objects.create(provider=self.provider, code="ISO9001_2015",
                                             source_type="curated", confidence="curated")
        publication = self.publication(provider=self.provider, submitted_payload={"original": True})
        self.assertEqual(self.provider.publications.get(), publication)
        event = CatalogueSyncEvent.objects.create(publication=publication, entity_type="provider",
                                                  entity_id=self.provider.provider_id, operation="upsert")
        self.provider.delete()
        publication.refresh_from_db()
        event.refresh_from_db()
        self.assertIsNone(publication.provider)
        self.assertEqual(publication.provider_id_snapshot, "example_provider")
        self.assertEqual(publication.submitted_payload, {"original": True})
        self.assertFalse(Offering.objects.exists())
        self.assertFalse(ProviderCertification.objects.exists())

    def test_sync_event_defaults_and_publication_cascade(self):
        publication = self.publication()
        event = CatalogueSyncEvent.objects.create(publication=publication, entity_type="offering",
                                                  entity_id="mdc_offering_1", operation="upsert")
        event.refresh_from_db()
        self.assertIsInstance(event.pk, uuid.UUID)
        self.assertEqual(publication.sync_events.get(), event)
        self.assertEqual(event.status, CatalogueSyncEvent.Status.PENDING)
        self.assertEqual(event.attempt_count, 0)
        self.assertEqual(event.last_error, "")
        self.assertIsNone(event.processed_at)
        publication.delete()
        self.assertFalse(CatalogueSyncEvent.objects.exists())

    def test_json_round_trip_preserves_nested_values(self):
        payload = {"label": "Tarkkuus – 齿轮", "nested": {"values": [None, True, 0, 1.25, ""]}}
        expected = deepcopy(payload)
        self.provider.custom_provider_fields = payload
        self.provider.save()
        fields = ("family_capabilities", "part_type_capabilities", "generic_capabilities",
                  "custom_offering_fields", "custom_capability_fields")
        offering = self.offering(supported_part_types=["spur_gear", "helical_gear"],
                                 **{field: payload for field in fields})
        publication = self.publication(submitted_payload=payload, normalized_payload=payload,
                                       validation_errors=payload)
        self.provider.refresh_from_db()
        offering.refresh_from_db()
        publication.refresh_from_db()
        self.assertEqual(payload, expected)
        self.assertEqual(self.provider.custom_provider_fields, expected)
        self.assertEqual(offering.supported_part_types, ["spur_gear", "helical_gear"])
        for field in fields:
            self.assertEqual(getattr(offering, field), expected)
        for field in ("submitted_payload", "normalized_payload", "validation_errors"):
            self.assertEqual(getattr(publication, field), expected)

    def test_json_defaults_are_independent(self):
        first, second = Offering(), Offering()
        first.supported_part_types.append("spur_gear")
        first.family_capabilities["custom"] = True
        self.assertEqual(second.supported_part_types, [])
        self.assertEqual(second.family_capabilities, {})
        self.assertEqual(first.generic_capabilities, {})
