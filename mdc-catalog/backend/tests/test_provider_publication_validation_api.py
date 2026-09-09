from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.providers.models import (
    CatalogueSyncEvent, Offering, Provider, ProviderCertification,
    ProviderPublication,
)
from tests.test_service_discovery_publication_serializer import (
    make_valid_family_level_gears_payload,
)


MODELS = (Provider, Offering, ProviderCertification, ProviderPublication, CatalogueSyncEvent)


@override_settings(MDC_PROVIDER_VALIDATION_ENABLED=True)
class ProviderPublicationValidationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/provider-publication/validation"

    def post(self, payload):
        return self.client.post(self.url, data=payload, format="json")

    def identities(self):
        return tuple(set(model.objects.values_list("pk", flat=True)) for model in MODELS)

    def assert_non_mutating(self, payload, expected_status):
        provider = Provider.objects.create(
            provider_id="existing", provider_name="Existing", country="Finland"
        )
        publication = ProviderPublication.objects.create(
            provider=provider, provider_id_snapshot="existing", operation="create"
        )
        CatalogueSyncEvent.objects.create(
            publication=publication, entity_type="provider", entity_id="existing", operation="upsert"
        )
        Offering.objects.create(
            provider=provider, offering_id="existing_gears", offering_name="Existing gears",
            service_category="precision_gears", part_family="gear",
        )
        ProviderCertification.objects.create(
            provider=provider, code="ISO9001_2015", source_type="curated", confidence="curated"
        )
        before = self.identities()
        with patch("pathlib.Path.write_text") as write_text, patch("pathlib.Path.write_bytes") as write_bytes:
            response = self.post(payload)
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(self.identities(), before)
        write_text.assert_not_called()
        write_bytes.assert_not_called()
        return response

    def test_valid_payload_defaults_contract_and_returns_deterministic_preview(self):
        payload = make_valid_family_level_gears_payload()
        first = self.post(deepcopy(payload))
        second = self.post(deepcopy(payload))
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(first.json(), second.json())
        data = first.json()
        self.assertEqual(data["contract_version"], "1.0")
        self.assertTrue(data["valid"])
        self.assertEqual(data["warnings"], [])
        self.assertEqual(data["normalized_payload"]["provider"]["provider_id"], "tasowheel")
        self.assertEqual(data["normalized_payload"]["offerings"][0]["offering_id"],
                         "tasowheel_precision_gears")

    def test_explicit_contract_version_1_is_accepted(self):
        payload = make_valid_family_level_gears_payload()
        payload["contract_version"] = "1.0"
        response = self.post(payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("contract_version", response.json()["normalized_payload"])

    def test_unsupported_version_uses_public_error_contract(self):
        payload = make_valid_family_level_gears_payload()
        payload["contract_version"] = "2.0"
        response = self.post(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["contract_version"], "1.0")
        self.assertEqual(response.json()["error"]["code"], "unsupported_contract_version")

    @override_settings(MDC_PROVIDER_VALIDATION_ENABLED=False)
    def test_feature_disabled_returns_safe_403(self):
        response = self.post(make_valid_family_level_gears_payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error"]["code"], "provider_validation_disabled")

    def test_invalid_controlled_vocabulary(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["service_category"] = "unknown_category"
        response = self.post(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"]["code"], "invalid_provider_publication")

    def test_invalid_category_family_relation(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["part_family"] = "shaft"
        self.assertEqual(self.post(payload).status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_part_type_relation(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["supported_part_types"] = [{
            "part_type": "hollow_shaft", "support_status": "confirmed",
            "source_type": "provider_confirmed", "confidence": "declared",
        }]
        self.assertEqual(self.post(payload).status_code, status.HTTP_400_BAD_REQUEST)

    def test_forbidden_route_field(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["route_steps"] = ["operation"]
        self.assertEqual(self.post(payload).status_code, status.HTTP_400_BAD_REQUEST)

    def test_externally_owned_offering_identifier(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["offering_id"] = "external_id"
        self.assertEqual(self.post(payload).status_code, status.HTTP_400_BAD_REQUEST)

    def test_provider_id_format_rejected(self):
        payload = make_valid_family_level_gears_payload()
        payload["provider_id"] = "Invalid Provider"
        self.assertEqual(self.post(payload).status_code, status.HTTP_400_BAD_REQUEST)

    def test_evidence_metadata_validation_preserved(self):
        payload = make_valid_family_level_gears_payload()
        payload["certifications"][0]["source_type"] = "not_confirmed"
        payload["certifications"][0]["confidence"] = "declared"
        response = self.post(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not_confirmed", str(response.json()["error"]["details"]))

    def test_valid_request_is_non_mutating_for_all_five_models(self):
        self.assert_non_mutating(make_valid_family_level_gears_payload(), status.HTTP_200_OK)

    def test_invalid_request_is_non_mutating_for_all_five_models(self):
        payload = make_valid_family_level_gears_payload()
        payload["provider_id"] = "INVALID"
        self.assert_non_mutating(payload, status.HTTP_400_BAD_REQUEST)

    def test_validation_does_not_call_file_rdf_or_fuseki_side_effects(self):
        with patch("apps.providers.repositories.save_provider_seed_data") as save_yaml, patch(
            "apps.ontology.service_discovery_rdf_generator.build_service_discovery_graph"
        ) as rdf, patch(
            "apps.search.service_discovery_fuseki_service.retrieve_service_discovery_candidates_from_fuseki"
        ) as fuseki:
            response = self.post(make_valid_family_level_gears_payload())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        save_yaml.assert_not_called()
        rdf.assert_not_called()
        fuseki.assert_not_called()

    def test_error_body_is_json_safe_and_has_no_sensitive_diagnostics(self):
        payload = make_valid_family_level_gears_payload()
        payload["provider_id"] = "C:\\private\\credential"
        response = self.post(payload)
        rendered = str(response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for forbidden in ("Traceback", "DATABASE_URL", "password", str(Path.cwd())):
            self.assertNotIn(forbidden, rendered)

    def test_validation_route_does_not_exist_under_api_v1(self):
        response = self.client.post(
            "/api/v1/provider-publication/validation",
            data=make_valid_family_level_gears_payload(), format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_methods_and_registration_routes_are_not_added(self):
        self.assertEqual(self.client.patch("/api/providers/tasowheel", {}, format="json").status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.post("/api/providers/tasowheel/offerings", {}, format="json").status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
