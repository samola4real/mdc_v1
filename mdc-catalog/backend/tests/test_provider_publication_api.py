from copy import deepcopy
from unittest.mock import patch

from django.db import IntegrityError
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
from apps.api.service_discovery_publication_serializers import (
    ServiceDiscoveryPublicationSerializer,
)
from tests.test_service_discovery_publication_serializer import (
    make_valid_family_level_gears_payload,
)


def make_valid_provider_publication_payload():
    payload = make_valid_family_level_gears_payload()
    payload["provider_id"] = "api_example_provider"
    payload["provider_name"] = "API Example Provider"
    return payload


@override_settings(MDC_PROVIDER_PUBLICATION_ENABLED=True)
class ProviderPublicationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def post(self, payload):
        return self.client.post("/api/provider-publication", payload, format="json")

    def test_registration_commits_complete_graph_history_and_pending_events(self):
        payload = make_valid_provider_publication_payload()
        payload["custom_provider_fields"] = {"erp_label": "staging only"}
        payload["offerings"][0]["custom_offering_fields"] = {"sales_name": "Gears"}
        payload["offerings"][0]["custom_capability_fields"] = {"free_text": "case-specific"}
        response = self.post(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["contract_version"], "1.0")
        self.assertEqual(data["operation"], "create")
        self.assertEqual(data["publication_status"], "sync_pending")
        self.assertEqual(data["sync_status"], "pending")
        self.assertEqual(data["offering_ids"], ["api_example_provider_precision_gears"])
        provider = Provider.objects.get(provider_id="api_example_provider")
        self.assertEqual(provider.status, Provider.Status.ACTIVE)
        self.assertEqual(provider.custom_provider_fields, {"erp_label": "staging only"})
        self.assertEqual(list(provider.certifications.values_list("sequence_index", flat=True)), [0])
        offering = provider.offerings.get()
        self.assertEqual(offering.custom_offering_fields, {"sales_name": "Gears"})
        self.assertEqual(offering.custom_capability_fields, {"free_text": "case-specific"})
        publication = ProviderPublication.objects.get()
        self.assertEqual(str(publication.id), data["publication_id"])
        self.assertIsNotNone(publication.validated_at)
        self.assertIsNotNone(publication.persisted_at)
        self.assertIsNone(publication.completed_at)
        self.assertEqual(publication.submitted_payload["provider_id"], "api_example_provider")
        self.assertEqual(publication.normalized_payload["provider"]["status"], "active")
        self.assertEqual(
            list(publication.sync_events.order_by("entity_type").values_list(
                "entity_type", "entity_id", "status"
            )),
            [("offering", offering.offering_id, "pending"),
             ("provider", provider.provider_id, "pending")],
        )

    def test_registration_preserves_submitted_order(self):
        payload = make_valid_provider_publication_payload()
        payload["certifications"] = [
            {"code": "ISO14001_2015", "source_type": "curated", "confidence": "curated"},
            {"code": "ISO9001_2015", "source_type": "provider_confirmed", "confidence": "declared"},
        ]
        second = deepcopy(payload["offerings"][0])
        second.update(service_category="precision_shafts", offering_name="Shafts", part_family="shaft")
        second["family_capabilities"] = {}
        second["generic_capabilities"] = {}
        payload["offerings"].append(second)
        response = self.post(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        provider = Provider.objects.get()
        self.assertEqual(
            list(provider.certifications.order_by("sequence_index").values_list("code", flat=True)),
            ["ISO14001_2015", "ISO9001_2015"],
        )
        self.assertEqual(
            list(provider.offerings.order_by("sequence_index").values_list("service_category", flat=True)),
            ["precision_gears", "precision_shafts"],
        )
        self.assertEqual(CatalogueSyncEvent.objects.count(), 3)

    def test_duplicate_registration_returns_conflict_without_overwrite(self):
        self.assertEqual(self.post(make_valid_provider_publication_payload()).status_code, 201)
        payload = make_valid_provider_publication_payload()
        payload["provider_name"] = "Replacement"
        response = self.post(payload)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()["error"]["code"], "provider_already_exists")
        self.assertEqual(Provider.objects.get().provider_name, "API Example Provider")
        self.assertEqual(ProviderPublication.objects.count(), 1)

    @override_settings(MDC_PROVIDER_PUBLICATION_ENABLED=False)
    def test_disabled_registration_has_no_mutation(self):
        response = self.post(make_valid_provider_publication_payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error"]["code"], "provider_publication_disabled")
        self.assertFalse(Provider.objects.exists())
        self.assertFalse(ProviderPublication.objects.exists())
        self.assertFalse(CatalogueSyncEvent.objects.exists())

    def test_contract_version_handling(self):
        payload = make_valid_provider_publication_payload()
        payload["contract_version"] = "2.0"
        response = self.post(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"]["code"], "unsupported_contract_version")
        self.assertFalse(Provider.objects.exists())

    def test_invalid_registration_has_no_mutation(self):
        payload = make_valid_provider_publication_payload()
        payload["offerings"][0]["route_steps"] = ["turning"]
        response = self.post(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"]["code"], "invalid_provider_publication")
        for model in (Provider, Offering, ProviderCertification, ProviderPublication, CatalogueSyncEvent):
            self.assertFalse(model.objects.exists())

    def test_custom_fields_reject_nested_route_keys(self):
        payload = make_valid_provider_publication_payload()
        payload["custom_provider_fields"] = {"route_steps": ["turning"]}
        response = self.post(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Provider.objects.exists())

    def test_credential_fields_are_rejected_and_not_echoed(self):
        payload = make_valid_provider_publication_payload()
        payload["custom_provider_fields"] = {"password": "do-not-store-this"}
        response = self.post(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("do-not-store-this", str(response.json()))
        self.assertFalse(ProviderPublication.objects.exists())

    def test_non_finite_custom_value_is_rejected_before_persistence(self):
        payload = make_valid_provider_publication_payload()
        payload["custom_provider_fields"] = {"estimate": float("nan")}
        serializer = ServiceDiscoveryPublicationSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertFalse(Provider.objects.exists())

    def test_mid_write_failure_rolls_back_every_model(self):
        with patch(
            "apps.providers.provider_lifecycle_write_service._create_sync_event",
            side_effect=IntegrityError("injected"),
        ):
            response = self.post(make_valid_provider_publication_payload())
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        for model in (Provider, Offering, ProviderCertification, ProviderPublication, CatalogueSyncEvent):
            self.assertFalse(model.objects.exists())

    def test_registration_integrity_race_is_safe_conflict(self):
        with patch.object(Provider.objects, "filter") as provider_filter, patch(
            "apps.providers.provider_lifecycle_write_service.Provider.objects.create",
            side_effect=IntegrityError("injected"),
        ):
            provider_filter.return_value.exists.side_effect = [False, True]
            response = self.post(make_valid_provider_publication_payload())
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()["error"]["code"], "provider_already_exists")
        self.assertNotIn("injected", str(response.json()))

    def test_registration_never_calls_file_rdf_or_fuseki_paths(self):
        with patch("apps.providers.repositories.save_provider_seed_data") as yaml_write, patch(
            "apps.ontology.service_discovery_rdf_generator.build_service_discovery_graph"
        ) as rdf, patch(
            "apps.search.service_discovery_fuseki_service.retrieve_service_discovery_candidates_from_fuseki"
        ) as fuseki:
            response = self.post(make_valid_provider_publication_payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        yaml_write.assert_not_called()
        rdf.assert_not_called()
        fuseki.assert_not_called()
