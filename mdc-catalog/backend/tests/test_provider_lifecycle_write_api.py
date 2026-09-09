from copy import deepcopy
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.providers.models import CatalogueSyncEvent, Offering, Provider, ProviderCertification, ProviderPublication
from tests.test_service_discovery_publication_serializer import make_valid_family_level_gears_payload


@override_settings(MDC_PROVIDER_PUBLICATION_ENABLED=True)
class ProviderLifecycleWriteApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.provider = Provider.objects.create(
            provider_id="lifecycle_writer", provider_name="Lifecycle Writer",
            country="Finland", status=Provider.Status.ACTIVE,
            publication_metadata={"source_type": "curated", "confidence": "curated"},
        )
        ProviderCertification.objects.create(
            provider=cls.provider, code="ISO9001_2015",
            source_type="provider_confirmed", confidence="declared", sequence_index=0,
        )
        cls.offering = Offering.objects.create(
            provider=cls.provider, offering_id="lifecycle_writer_precision_gears",
            offering_name="Gears", service_category="precision_gears", part_family="gear",
            support_status=Offering.SupportStatus.CONFIRMED,
            family_capabilities={"module": {"max": 8}}, sequence_index=4,
        )

    def setUp(self):
        self.client = APIClient()

    def offering_payload(self):
        item = deepcopy(make_valid_family_level_gears_payload()["offerings"][0])
        item.update(service_category="precision_shafts", offering_name="Shafts", part_family="shaft")
        item["family_capabilities"] = {}
        item["generic_capabilities"] = {}
        return item

    def test_provider_patch_replaces_supplied_fields_and_certifications(self):
        payload = {
            "provider_name": "Updated Writer", "status": "suspended",
            "custom_provider_fields": {"free_text": "staging"},
            "certifications": [
                {"code": "ISO14001_2015", "source_type": "curated", "confidence": "curated"},
                {"code": "ISO9001_2015", "source_type": "provider_confirmed", "confidence": "declared"},
            ],
        }
        with patch.object(
            Provider.objects, "select_for_update",
            wraps=Provider.objects.select_for_update,
        ) as provider_lock:
            response = self.client.patch("/api/providers/lifecycle_writer", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        provider_lock.assert_called_once_with()
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.provider_name, "Updated Writer")
        self.assertEqual(self.provider.country, "Finland")
        self.assertEqual(self.provider.status, "suspended")
        self.assertEqual(self.provider.custom_provider_fields, {"free_text": "staging"})
        self.assertEqual(
            list(self.provider.certifications.order_by("sequence_index").values_list("code", flat=True)),
            ["ISO14001_2015", "ISO9001_2015"],
        )
        publication = ProviderPublication.objects.get()
        self.assertEqual(publication.operation, "update")
        self.assertEqual(publication.submitted_payload, payload)
        self.assertEqual(publication.normalized_payload["provider"]["display_name"], "Updated Writer")
        self.assertEqual(publication.sync_events.get().entity_id, "lifecycle_writer")

    def test_provider_patch_rejects_identity_offerings_and_unknown_provider(self):
        for payload in ({"provider_id": "other"}, {"offerings": []}):
            response = self.client.patch("/api/providers/lifecycle_writer", payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch("/api/providers/missing", {"country": "Sweden"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error"]["code"], "provider_not_found")
        self.assertFalse(ProviderPublication.objects.exists())

    def test_provider_patch_validation_failure_is_non_mutating(self):
        response = self.client.patch(
            "/api/providers/lifecycle_writer",
            {"provider_name": "Changed", "certifications": [{"code": "invalid"}]}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.provider_name, "Lifecycle Writer")
        self.assertFalse(ProviderPublication.objects.exists())

    def test_offering_create_uses_next_sequence_and_one_offering_event(self):
        payload = self.offering_payload()
        payload["custom_offering_fields"] = {"sales_note": "free text"}
        payload["custom_capability_fields"] = {"local_metric": {"raw": "A"}}
        with patch.object(
            Provider.objects, "select_for_update",
            wraps=Provider.objects.select_for_update,
        ) as provider_lock:
            response = self.client.post("/api/providers/lifecycle_writer/offerings", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        provider_lock.assert_called_once_with()
        offering = Offering.objects.get(offering_id="lifecycle_writer_precision_shafts")
        self.assertEqual(offering.sequence_index, 5)
        self.assertEqual(offering.custom_offering_fields, {"sales_note": "free text"})
        self.assertEqual(offering.custom_capability_fields, {"local_metric": {"raw": "A"}})
        self.assertNotIn("local_metric", offering.generic_capabilities)
        publication = ProviderPublication.objects.get()
        self.assertEqual(publication.normalized_payload["offerings"][1]["offering_id"], offering.offering_id)
        self.assertEqual(list(publication.sync_events.values_list("entity_type", "entity_id")),
                         [("offering", offering.offering_id)])

    def test_offering_create_rejects_body_identity_unknown_and_duplicate(self):
        payload = self.offering_payload()
        payload["provider_id"] = "other"
        self.assertEqual(self.client.post(
            "/api/providers/lifecycle_writer/offerings", payload, format="json"
        ).status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(
            "/api/providers/missing/offerings", self.offering_payload(), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        duplicate = deepcopy(make_valid_family_level_gears_payload()["offerings"][0])
        response = self.client.post(
            "/api/providers/lifecycle_writer/offerings", duplicate, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()["error"]["code"], "offering_already_exists")
        self.assertEqual(Offering.objects.count(), 1)

    def test_offering_create_integrity_race_rolls_back_history(self):
        with patch.object(Offering.objects, "filter") as offering_filter, patch(
            "apps.providers.provider_lifecycle_write_service.Offering.objects.create",
            side_effect=IntegrityError("injected"),
        ):
            offering_filter.return_value.exists.side_effect = [False, True]
            response = self.client.post(
                "/api/providers/lifecycle_writer/offerings", self.offering_payload(), format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertFalse(ProviderPublication.objects.exists())
        self.assertFalse(CatalogueSyncEvent.objects.exists())

    def test_offering_patch_validates_complete_state_and_preserves_identity_sequence(self):
        payload = {
            "offering_name": "Updated gears", "is_active": False,
            "family_capabilities": {"module": {"max": 12}},
            "custom_capability_fields": {"quote_note": "manual"},
        }
        with patch.object(
            Offering.objects, "select_for_update",
            wraps=Offering.objects.select_for_update,
        ) as offering_lock, patch.object(
            Provider.objects, "select_for_update",
            wraps=Provider.objects.select_for_update,
        ) as provider_lock:
            response = self.client.patch(
                "/api/offerings/lifecycle_writer_precision_gears", payload, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        offering_lock.assert_called_once_with()
        provider_lock.assert_called_once_with()
        self.offering.refresh_from_db()
        self.assertEqual(self.offering.offering_id, "lifecycle_writer_precision_gears")
        self.assertEqual(self.offering.provider_id, self.provider.pk)
        self.assertEqual(self.offering.service_category, "precision_gears")
        self.assertEqual(self.offering.part_family, "gear")
        self.assertEqual(self.offering.sequence_index, 4)
        self.assertEqual(self.offering.offering_name, "Updated gears")
        self.assertFalse(self.offering.is_active)
        self.assertEqual(self.offering.custom_capability_fields, {"quote_note": "manual"})
        publication = ProviderPublication.objects.get()
        self.assertEqual(publication.sync_events.get().entity_id, self.offering.offering_id)

    def test_offering_patch_rejects_immutable_invalid_and_unknown(self):
        for field in ("offering_id", "provider_id", "service_category", "part_family"):
            response = self.client.patch(
                "/api/offerings/lifecycle_writer_precision_gears", {field: "other"}, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(
            "/api/offerings/lifecycle_writer_precision_gears",
            {"family_capabilities": {"outer_diameter_mm": {"max": 20}}}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch("/api/offerings/missing", {"offering_name": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(ProviderPublication.objects.exists())

    @override_settings(MDC_PROVIDER_PUBLICATION_ENABLED=False)
    def test_disabled_patch_and_create_routes_never_mutate(self):
        responses = [
            self.client.patch("/api/providers/lifecycle_writer", {"country": "Sweden"}, format="json"),
            self.client.post("/api/providers/lifecycle_writer/offerings", self.offering_payload(), format="json"),
            self.client.patch("/api/offerings/lifecycle_writer_precision_gears", {"is_active": False}, format="json"),
        ]
        self.assertTrue(all(item.status_code == status.HTTP_403_FORBIDDEN for item in responses))
        self.provider.refresh_from_db()
        self.offering.refresh_from_db()
        self.assertEqual(self.provider.country, "Finland")
        self.assertTrue(self.offering.is_active)
        self.assertFalse(ProviderPublication.objects.exists())

    def test_write_routes_do_not_call_file_rdf_fuseki_or_runtime(self):
        with patch("apps.providers.repositories.save_provider_seed_data") as yaml_write, patch(
            "apps.ontology.service_discovery_rdf_generator.build_service_discovery_graph"
        ) as rdf, patch(
            "apps.search.service_discovery_fuseki_service.retrieve_service_discovery_candidates_from_fuseki"
        ) as fuseki, patch(
            "apps.search.service_discovery_runtime_search.search_service_discovery_with_runtime_backends"
        ) as runtime:
            response = self.client.patch(
                "/api/providers/lifecycle_writer", {"country": "Sweden"}, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        yaml_write.assert_not_called()
        rdf.assert_not_called()
        fuseki.assert_not_called()
        runtime.assert_not_called()

    def test_provider_patch_mid_write_failure_rolls_back(self):
        with patch(
            "apps.providers.provider_lifecycle_write_service._create_sync_event",
            side_effect=IntegrityError("injected"),
        ):
            response = self.client.patch(
                "/api/providers/lifecycle_writer", {"country": "Sweden"}, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.country, "Finland")
        self.assertFalse(ProviderPublication.objects.exists())

    def test_write_routes_are_not_versioned(self):
        requests = [
            self.client.post("/api/v1/provider-publication", {}, format="json"),
            self.client.patch("/api/v1/providers/lifecycle_writer", {}, format="json"),
            self.client.post("/api/v1/providers/lifecycle_writer/offerings", {}, format="json"),
            self.client.patch("/api/v1/offerings/lifecycle_writer_precision_gears", {}, format="json"),
        ]
        self.assertTrue(all(response.status_code == status.HTTP_404_NOT_FOUND for response in requests))
