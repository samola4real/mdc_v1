import json
from copy import deepcopy

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.providers.models import Offering, Provider, ProviderPublication
from tests.test_service_discovery_publication_serializer import (
    make_valid_family_level_gears_payload,
)


@override_settings(
    MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True,
    MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN="m76-test-service-token",
    MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True,
    MDC_PROVIDER_CONCURRENCY_REQUIRED=True,
    MDC_PROVIDER_PUBLICATION_ENABLED=True,
    MDC_PROVIDER_VALIDATION_ENABLED=True,
)
class M76ExternalExposureReadinessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.provider = Provider.objects.create(
            provider_id="m76_provider",
            provider_name="M76 Provider",
            country="Finland",
            status=Provider.Status.ACTIVE,
            publication_metadata={
                "source_type": "provider_confirmed",
                "confidence": "declared",
            },
        )
        cls.offering = Offering.objects.create(
            provider=cls.provider,
            offering_id="m76_provider_precision_gears",
            offering_name="M76 gears",
            service_category="precision_gears",
            part_family="gear",
            support_status=Offering.SupportStatus.CONFIRMED,
            sequence_index=0,
        )

    def setUp(self):
        self.client = APIClient()

    def trusted_headers(self, *, actor=True, etag=None):
        headers = {"HTTP_AUTHORIZATION": "Bearer m76-test-service-token"}
        if actor:
            headers["HTTP_X_MDC_ACTOR_ID"] = "marketplace:user-42"
        if etag is not None:
            headers["HTTP_IF_MATCH"] = etag
        return headers

    def provider_etag(self):
        response = self.client.get(
            "/api/providers/m76_provider",
            **self.trusted_headers(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response["ETag"]

    def offering_etag(self):
        response = self.client.get(
            "/api/offerings/m76_provider_precision_gears",
            **self.trusted_headers(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response["ETag"]

    def test_public_discovery_boundary_is_not_given_lifecycle_auth(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lifecycle_reads_and_validation_require_trusted_bearer(self):
        requests = [
            self.client.get("/api/providers/m76_provider"),
            self.client.get("/api/providers/m76_provider/offerings"),
            self.client.get("/api/offerings/m76_provider_precision_gears"),
            self.client.post("/api/provider-publication/validation", {}, format="json"),
        ]
        for response in requests:
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(
                response.json()["error"]["code"],
                "trusted_lifecycle_auth_required",
            )
            self.assertEqual(response["WWW-Authenticate"], "Bearer")

    def test_invalid_token_is_rejected_without_echo(self):
        response = self.client.get(
            "/api/providers/m76_provider",
            HTTP_AUTHORIZATION="Bearer wrong-secret-value",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("wrong-secret-value", response.content.decode("utf-8"))
        self.assertNotIn("m76-test-service-token", response.content.decode("utf-8"))

    @override_settings(MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN="")
    def test_required_auth_without_server_token_fails_closed(self):
        response = self.client.get("/api/providers/m76_provider")
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            response.json()["error"]["code"],
            "trusted_lifecycle_auth_unavailable",
        )

    def test_valid_token_allows_lifecycle_read_and_returns_opaque_etag(self):
        response = self.client.get(
            "/api/providers/m76_provider",
            **self.trusted_headers(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response["ETag"].startswith('"'))
        self.assertTrue(response["ETag"].endswith('"'))
        self.assertNotIn("updated_at", response.json())
        self.assertNotIn("_etag", response.json())

    def test_actor_is_required_before_write_and_invalid_actor_is_rejected(self):
        etag = self.provider_etag()
        response = self.client.patch(
            "/api/providers/m76_provider",
            {"country": "Sweden"},
            format="json",
            **self.trusted_headers(actor=False, etag=etag),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["error"]["code"],
            "actor_attribution_required",
        )

        response = self.client.patch(
            "/api/providers/m76_provider",
            {"country": "Sweden"},
            format="json",
            HTTP_AUTHORIZATION="Bearer m76-test-service-token",
            HTTP_X_MDC_ACTOR_ID="bad\x00actor",
            HTTP_IF_MATCH=etag,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_actor_attribution",
        )
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.country, "Finland")

    def test_accepted_write_records_actor_but_never_bearer_token(self):
        etag = self.provider_etag()
        response = self.client.patch(
            "/api/providers/m76_provider",
            {"country": "Sweden"},
            format="json",
            **self.trusted_headers(etag=etag),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        publication = ProviderPublication.objects.get()
        self.assertEqual(
            publication.submitted_by_external_id,
            "marketplace:user-42",
        )
        persisted = json.dumps(
            {
                "submitted": publication.submitted_payload,
                "normalized": publication.normalized_payload,
                "actor": publication.submitted_by_external_id,
            }
        )
        self.assertNotIn("m76-test-service-token", persisted)

    def test_missing_required_if_match_is_428_and_non_mutating(self):
        response = self.client.patch(
            "/api/providers/m76_provider",
            {"country": "Sweden"},
            format="json",
            **self.trusted_headers(),
        )
        self.assertEqual(response.status_code, 428)
        self.assertEqual(
            response.json()["error"]["code"],
            "concurrency_precondition_required",
        )
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.country, "Finland")
        self.assertFalse(ProviderPublication.objects.exists())

    def test_provider_stale_if_match_is_412_and_does_not_overwrite(self):
        stale = self.provider_etag()
        first = self.client.patch(
            "/api/providers/m76_provider",
            {"country": "Sweden"},
            format="json",
            **self.trusted_headers(etag=stale),
        )
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        current = first["ETag"]
        self.assertNotEqual(current, stale)

        second = self.client.patch(
            "/api/providers/m76_provider",
            {"country": "Norway"},
            format="json",
            **self.trusted_headers(etag=stale),
        )
        self.assertEqual(second.status_code, status.HTTP_412_PRECONDITION_FAILED)
        self.assertEqual(
            second.json()["error"]["code"],
            "provider_precondition_failed",
        )
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.country, "Sweden")
        self.assertEqual(ProviderPublication.objects.count(), 1)

    def test_provider_etag_changes_for_certification_replacement(self):
        before = self.provider_etag()
        response = self.client.patch(
            "/api/providers/m76_provider",
            {
                "certifications": [
                    {
                        "code": "ISO9001_2015",
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    }
                ]
            },
            format="json",
            **self.trusted_headers(etag=before),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response["ETag"], before)
        self.assertEqual(response["ETag"], self.provider_etag())

    def test_offering_etag_changes_and_stale_patch_is_rejected(self):
        stale = self.offering_etag()
        first = self.client.patch(
            "/api/offerings/m76_provider_precision_gears",
            {"offering_name": "Updated M76 gears"},
            format="json",
            **self.trusted_headers(etag=stale),
        )
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertNotEqual(first["ETag"], stale)
        self.assertEqual(first["ETag"], self.offering_etag())

        second = self.client.patch(
            "/api/offerings/m76_provider_precision_gears",
            {"offering_name": "Stale overwrite"},
            format="json",
            **self.trusted_headers(etag=stale),
        )
        self.assertEqual(second.status_code, status.HTTP_412_PRECONDITION_FAILED)
        self.offering.refresh_from_db()
        self.assertEqual(self.offering.offering_name, "Updated M76 gears")

    def test_provider_aggregate_etag_changes_after_offering_patch(self):
        provider_before = self.provider_etag()
        offering_before = self.offering_etag()
        response = self.client.patch(
            "/api/offerings/m76_provider_precision_gears",
            {"support_status": "unknown"},
            format="json",
            **self.trusted_headers(etag=offering_before),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.provider_etag(), provider_before)

    def test_registration_actor_attribution_is_not_body_controlled(self):
        payload = deepcopy(make_valid_family_level_gears_payload())
        payload["provider_id"] = "m76_registered"
        payload["provider_name"] = "M76 Registered"
        response = self.client.post(
            "/api/provider-publication",
            payload,
            format="json",
            **self.trusted_headers(),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publication = ProviderPublication.objects.get(
            provider_id_snapshot="m76_registered"
        )
        self.assertEqual(
            publication.submitted_by_external_id,
            "marketplace:user-42",
        )
