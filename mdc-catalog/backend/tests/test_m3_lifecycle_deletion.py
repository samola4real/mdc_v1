import json
from unittest.mock import patch

from django.db import DatabaseError
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.providers.models import (
    CatalogueSyncEvent,
    Offering,
    Provider,
    ProviderCertification,
    ProviderPublication,
)


M3_SETTINGS = {
    "MDC_PROVIDER_PUBLICATION_ENABLED": True,
    "MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED": False,
    "MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED": False,
    "MDC_PROVIDER_CONCURRENCY_REQUIRED": False,
}


@override_settings(**M3_SETTINGS)
class M3LifecycleDeletionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.provider = Provider.objects.create(
            provider_id="m3_provider",
            provider_name="M3 Provider",
            country="Finland",
            status=Provider.Status.ACTIVE,
            custom_provider_fields={
                "remove_me": "sensitive",
                "keep_me": "retained",
                "unknown_fact": {"status": "unknown"},
            },
            publication_metadata={"source_type": "provider_confirmed"},
        )
        ProviderCertification.objects.create(
            provider=self.provider,
            code="ISO9001_2015",
            source_type="provider_confirmed",
            confidence="declared",
        )
        self.target = Offering.objects.create(
            provider=self.provider,
            offering_id="m3_provider_precision_gears_alpha",
            offering_name="Alpha gears",
            service_category="precision_gears",
            part_family="gear",
            support_status=Offering.SupportStatus.CONFIRMED,
            custom_capability_fields={
                "remove_me": {"value": 1},
                "keep_me": {"value": 2},
                "unknown_fact": {"status": "unknown"},
            },
            sequence_index=0,
        )
        self.sibling = Offering.objects.create(
            provider=self.provider,
            offering_id="m3_provider_precision_gears_beta",
            offering_name="Beta gears",
            service_category="precision_gears",
            part_family="gear",
            support_status=Offering.SupportStatus.CONFIRMED,
            custom_capability_fields={"sibling_only": True},
            sequence_index=1,
        )
        self.other_provider = Provider.objects.create(
            provider_id="m3_unrelated",
            provider_name="Unrelated Provider",
            country="Sweden",
            status=Provider.Status.ACTIVE,
        )
        self.other_offering = Offering.objects.create(
            provider=self.other_provider,
            offering_id="m3_unrelated_precision_gears",
            offering_name="Unrelated gears",
            service_category="precision_gears",
            part_family="gear",
            support_status=Offering.SupportStatus.CONFIRMED,
        )
        self.history = ProviderPublication.objects.create(
            provider=self.provider,
            provider_id_snapshot=self.provider.provider_id,
            operation=ProviderPublication.Operation.CREATE,
            status=ProviderPublication.Status.SYNC_PENDING,
            submitted_payload={
                "provider_name": "M3 Provider",
                "secret": "provider-secret",
                "offerings": [
                    {"offering_id": self.target.offering_id, "secret": "target-secret"},
                    {"offering_id": self.sibling.offering_id, "safe": "sibling"},
                ],
            },
            normalized_payload={
                "provider": {
                    "provider_id": self.provider.provider_id,
                    "display_name": "M3 Provider",
                },
                "offerings": [
                    {
                        "offering_id": self.target.offering_id,
                        "custom_capability_fields": {"secret": "target-secret"},
                    },
                    {
                        "offering_id": self.sibling.offering_id,
                        "custom_capability_fields": {"safe": "sibling"},
                    },
                ],
            },
            submitted_by_external_id="historic-actor",
        )

    def provider_etag(self):
        response = self.client.get(f"/api/providers/{self.provider.provider_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response["ETag"]

    def offering_etag(self, offering_id=None):
        response = self.client.get(
            f"/api/offerings/{offering_id or self.target.offering_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response["ETag"]

    def test_provider_delete_is_durable_minimal_and_scoped(self):
        provider_id = self.provider.provider_id
        offering_ids = [self.target.offering_id, self.sibling.offering_id]
        response = self.client.delete(
            f"/api/providers/{provider_id}",
            HTTP_IF_MATCH=self.provider_etag(),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["operation"], "delete")
        self.assertEqual(
            data["target"],
            {"entity_type": "provider", "entity_id": provider_id},
        )
        self.assertEqual(data["publication_status"], "sync_pending")
        self.assertEqual(data["sync_status"], "pending")
        self.assertEqual(data["offering_ids"], offering_ids)

        self.assertFalse(Provider.objects.filter(provider_id=provider_id).exists())
        self.assertFalse(Offering.objects.filter(offering_id__in=offering_ids).exists())
        self.assertFalse(
            ProviderCertification.objects.filter(provider_id=self.provider.pk).exists()
        )
        self.assertTrue(Provider.objects.filter(provider_id="m3_unrelated").exists())
        self.assertTrue(
            Offering.objects.filter(offering_id=self.other_offering.offering_id).exists()
        )
        self.assertEqual(
            self.client.get(f"/api/providers/{provider_id}").status_code,
            status.HTTP_404_NOT_FOUND,
        )

        deletion = ProviderPublication.objects.get(id=data["publication_id"])
        self.assertIsNone(deletion.provider)
        self.assertEqual(deletion.submitted_payload, {})
        self.assertEqual(
            deletion.normalized_payload,
            {
                "tombstone": {
                    "entity_type": "provider",
                    "entity_id": provider_id,
                    "provider_id": provider_id,
                    "offering_ids": offering_ids,
                }
            },
        )
        self.assertEqual(
            set(
                deletion.sync_events.values_list(
                    "entity_type", "entity_id", "operation", "status"
                )
            ),
            {
                ("provider", provider_id, "delete", "pending"),
                ("offering", offering_ids[0], "delete", "pending"),
                ("offering", offering_ids[1], "delete", "pending"),
            },
        )
        self.history.refresh_from_db()
        self.assertIsNone(self.history.provider)
        self.assertEqual(self.history.submitted_payload, {})
        self.assertEqual(self.history.normalized_payload, {})
        self.assertIsNone(self.history.submitted_by_external_id)
        retained = json.dumps(
            list(
                ProviderPublication.objects.filter(provider_id_snapshot=provider_id)
                .values("submitted_payload", "normalized_payload")
            )
        )
        self.assertNotIn("M3 Provider", retained)
        self.assertNotIn("provider-secret", retained)
        self.assertNotIn("target-secret", retained)

    def test_offering_delete_preserves_parent_and_same_category_sibling(self):
        provider_etag = self.provider_etag()
        target_id = self.target.offering_id
        sibling_id = self.sibling.offering_id
        response = self.client.delete(
            f"/api/offerings/{target_id}",
            HTTP_IF_MATCH=self.offering_etag(),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["target"],
            {"entity_type": "offering", "entity_id": target_id},
        )
        self.assertFalse(Offering.objects.filter(offering_id=target_id).exists())
        self.assertTrue(Offering.objects.filter(offering_id=sibling_id).exists())
        self.assertTrue(
            Provider.objects.filter(provider_id=self.provider.provider_id).exists()
        )
        self.assertNotEqual(self.provider_etag(), provider_etag)
        self.assertEqual(
            self.client.get(f"/api/offerings/{target_id}").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        listing = self.client.get(
            f"/api/providers/{self.provider.provider_id}/offerings"
        )
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["offering_id"] for item in listing.json()["offerings"]],
            [sibling_id],
        )

        deletion = ProviderPublication.objects.get(
            id=response.json()["publication_id"]
        )
        self.assertEqual(deletion.submitted_payload, {})
        self.assertEqual(
            deletion.normalized_payload,
            {
                "tombstone": {
                    "entity_type": "offering",
                    "entity_id": target_id,
                    "provider_id": self.provider.provider_id,
                }
            },
        )
        event = deletion.sync_events.get()
        self.assertEqual(
            (event.entity_type, event.entity_id, event.operation, event.status),
            ("offering", target_id, "delete", "pending"),
        )
        self.history.refresh_from_db()
        retained_ids = [
            item["offering_id"]
            for item in self.history.normalized_payload["offerings"]
        ]
        self.assertEqual(retained_ids, [sibling_id])
        self.assertEqual(self.history.submitted_payload, {})
        self.assertNotIn(
            "target-secret",
            json.dumps(self.history.normalized_payload),
        )

    def test_delete_preconditions_are_mandatory_valid_and_current(self):
        url = f"/api/providers/{self.provider.provider_id}"
        self.assertEqual(self.client.delete(url).status_code, 428)
        for value in ("*", 'W/"weak"', '"one", "two"', "not-quoted"):
            response = self.client.delete(url, HTTP_IF_MATCH=value)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        stale = self.provider_etag()
        patch_response = self.client.patch(
            url,
            {"country": "Estonia"},
            format="json",
            HTTP_IF_MATCH=stale,
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url, HTTP_IF_MATCH=stale)
        self.assertEqual(response.status_code, status.HTTP_412_PRECONDITION_FAILED)
        self.assertTrue(Provider.objects.filter(pk=self.provider.pk).exists())

    def test_missing_and_repeated_delete_are_stable_404s(self):
        response = self.client.delete(
            "/api/providers/not-present", HTTP_IF_MATCH='"valid-shape"'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        etag = self.offering_etag()
        url = f"/api/offerings/{self.target.offering_id}"
        self.assertEqual(
            self.client.delete(url, HTTP_IF_MATCH=etag).status_code,
            status.HTTP_200_OK,
        )
        response = self.client.delete(url, HTTP_IF_MATCH=etag)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error"]["code"], "offering_not_found")

    def test_provider_with_zero_offerings_can_be_deleted(self):
        empty = Provider.objects.create(
            provider_id="m3_empty", provider_name="Empty", country="Finland"
        )
        response = self.client.get(f"/api/providers/{empty.provider_id}")
        deleted = self.client.delete(
            f"/api/providers/{empty.provider_id}",
            HTTP_IF_MATCH=response["ETag"],
        )
        self.assertEqual(deleted.status_code, status.HTTP_200_OK)
        self.assertEqual(deleted.json()["offering_ids"], [])

    @override_settings(MDC_PROVIDER_PUBLICATION_ENABLED=False)
    def test_publication_gate_blocks_delete_without_mutation(self):
        response = self.client.delete(
            f"/api/providers/{self.provider.provider_id}",
            HTTP_IF_MATCH=self.provider_etag(),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Provider.objects.filter(pk=self.provider.pk).exists())

    def test_delete_failure_rolls_back_tombstone_and_operational_delete(self):
        with patch(
            "apps.providers.provider_lifecycle_write_service._create_sync_event",
            side_effect=DatabaseError("injected"),
        ):
            response = self.client.delete(
                f"/api/offerings/{self.target.offering_id}",
                HTTP_IF_MATCH=self.offering_etag(),
            )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertTrue(Offering.objects.filter(pk=self.target.pk).exists())
        self.assertEqual(
            ProviderPublication.objects.filter(
                operation=ProviderPublication.Operation.DELETE
            ).count(),
            0,
        )
        self.history.refresh_from_db()
        self.assertIn(
            self.target.offering_id,
            [item["offering_id"] for item in self.history.normalized_payload["offerings"]],
        )

    def test_patch_removes_selected_map_keys_without_touching_other_state(self):
        provider_response = self.client.patch(
            f"/api/providers/{self.provider.provider_id}",
            {
                "custom_provider_fields": {
                    "keep_me": "retained",
                    "unknown_fact": {"status": "unknown"},
                }
            },
            format="json",
            HTTP_IF_MATCH=self.provider_etag(),
        )
        self.assertEqual(provider_response.status_code, status.HTTP_200_OK)
        self.provider.refresh_from_db()
        self.assertEqual(
            self.provider.custom_provider_fields,
            {
                "keep_me": "retained",
                "unknown_fact": {"status": "unknown"},
            },
        )

        stale = self.offering_etag()
        offering_response = self.client.patch(
            f"/api/offerings/{self.target.offering_id}",
            {
                "custom_capability_fields": {
                    "keep_me": {"value": 2},
                    "unknown_fact": {"status": "unknown"},
                }
            },
            format="json",
            HTTP_IF_MATCH=stale,
        )
        self.assertEqual(offering_response.status_code, status.HTTP_200_OK)
        self.target.refresh_from_db()
        self.sibling.refresh_from_db()
        self.assertEqual(
            self.target.custom_capability_fields,
            {
                "keep_me": {"value": 2},
                "unknown_fact": {"status": "unknown"},
            },
        )
        self.assertEqual(self.sibling.custom_capability_fields, {"sibling_only": True})
        self.assertEqual(
            self.client.patch(
                f"/api/offerings/{self.target.offering_id}",
                {"custom_capability_fields": {}},
                format="json",
                HTTP_IF_MATCH=stale,
            ).status_code,
            status.HTTP_412_PRECONDITION_FAILED,
        )

    def test_patch_rejects_null_and_immutable_field_removal(self):
        url = f"/api/offerings/{self.target.offering_id}"
        etag = self.offering_etag()
        for payload in (
            {"custom_capability_fields": None},
            {"service_category": None},
        ):
            response = self.client.patch(
                url, payload, format="json", HTTP_IF_MATCH=etag
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.target.refresh_from_db()
        self.assertIn("remove_me", self.target.custom_capability_fields)


@override_settings(
    MDC_PROVIDER_PUBLICATION_ENABLED=True,
    MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True,
    MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN="m3-service-token",
    MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True,
    MDC_PROVIDER_CONCURRENCY_REQUIRED=False,
)
class M3SecureDeletionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.provider = Provider.objects.create(
            provider_id="m3_secure",
            provider_name="Secure Provider",
            country="Finland",
            status=Provider.Status.ACTIVE,
        )

    def test_secure_delete_requires_auth_and_actor_and_records_actor(self):
        url = f"/api/providers/{self.provider.provider_id}"
        response = self.client.delete(url, HTTP_IF_MATCH='"shape"')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {"HTTP_AUTHORIZATION": "Bearer m3-service-token"}
        read = self.client.get(url, **headers)
        self.assertEqual(read.status_code, status.HTTP_200_OK)
        response = self.client.delete(
            url,
            HTTP_IF_MATCH=read["ETag"],
            **headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"]["code"], "actor_attribution_required")

        response = self.client.delete(
            url,
            HTTP_IF_MATCH=read["ETag"],
            HTTP_X_MDC_ACTOR_ID="marketplace:user-77",
            **headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        publication = ProviderPublication.objects.get(
            id=response.json()["publication_id"]
        )
        self.assertEqual(
            publication.submitted_by_external_id,
            "marketplace:user-77",
        )
        self.assertNotIn(
            "m3-service-token",
            json.dumps(publication.normalized_payload),
        )
