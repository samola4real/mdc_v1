from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.providers.models import Provider, ProviderPublication


@override_settings(
    MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True,
    MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN="p32-test-token",
    MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True,
    MDC_PROVIDER_CONCURRENCY_REQUIRED=True,
    MDC_PROVIDER_PUBLICATION_ENABLED=True,
)
class P32VercelConcurrencyHeaderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Provider.objects.create(
            provider_id="p32_header_provider",
            provider_name="P3.2 Header Provider",
            country="Finland",
            status=Provider.Status.ACTIVE,
        )

    def setUp(self):
        self.client = APIClient()

    def headers(self, **extra):
        return {
            "HTTP_AUTHORIZATION": "Bearer p32-test-token",
            "HTTP_X_MDC_ACTOR_ID": "p32:test",
            **extra,
        }

    def etag(self):
        response = self.client.get(
            "/api/providers/p32_header_provider",
            **self.headers(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response["ETag"]

    def test_custom_pilot_concurrency_header_accepts_current_etag(self):
        current = self.etag()
        response = self.client.patch(
            "/api/providers/p32_header_provider",
            {"country": "Sweden"},
            format="json",
            **self.headers(HTTP_X_MDC_IF_MATCH=current),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProviderPublication.objects.count(), 1)
        provider = Provider.objects.get(provider_id="p32_header_provider")
        self.assertEqual(provider.country, "Sweden")

    def test_custom_pilot_concurrency_header_rejects_stale_etag(self):
        stale = self.etag()
        first = self.client.patch(
            "/api/providers/p32_header_provider",
            {"country": "Sweden"},
            format="json",
            **self.headers(HTTP_X_MDC_IF_MATCH=stale),
        )
        self.assertEqual(first.status_code, status.HTTP_200_OK)

        second = self.client.patch(
            "/api/providers/p32_header_provider",
            {"country": "Norway"},
            format="json",
            **self.headers(HTTP_X_MDC_IF_MATCH=stale),
        )
        self.assertEqual(second.status_code, status.HTTP_412_PRECONDITION_FAILED)
        provider = Provider.objects.get(provider_id="p32_header_provider")
        self.assertEqual(provider.country, "Sweden")
        self.assertEqual(ProviderPublication.objects.count(), 1)

    def test_conflicting_standard_and_pilot_headers_are_rejected(self):
        current = self.etag()
        response = self.client.patch(
            "/api/providers/p32_header_provider",
            {"country": "Sweden"},
            format="json",
            **self.headers(
                HTTP_IF_MATCH=current,
                HTTP_X_MDC_IF_MATCH='"different"',
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_concurrency_precondition",
        )
        self.assertFalse(ProviderPublication.objects.exists())
