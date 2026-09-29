import json
import re
from copy import deepcopy
from pathlib import Path

from django.test import SimpleTestCase
from django.urls import reverse

from apps.api.provider_lifecycle_serializers import (
    OfferingCreateSerializer,
    OfferingPatchSerializer,
    ProviderPatchSerializer,
)
from apps.api.service_discovery_publication_serializers import (
    ServiceDiscoveryPublicationSerializer,
    validate_lifecycle_offering,
)
from apps.api.service_discovery_search_serializers import (
    ServiceDiscoverySearchRequestSerializer,
)
from apps.api.urls import urlpatterns


CATALOG_ROOT = Path(__file__).resolve().parents[2]
PARTNER_ROOT = CATALOG_ROOT / "docs" / "Partner_API"
GUIDE = PARTNER_ROOT / "MaaSAI_MDC_M6_Marketplace_Integration_Guide.md"
COLLECTION = (
    PARTNER_ROOT
    / "MaaSAI_MDC_M6_Marketplace_Integration.postman_collection.json"
)
ENVIRONMENT = (
    PARTNER_ROOT
    / "MaaSAI_MDC_M6_Marketplace_Integration.postman_environment.json"
)


def documented_json(heading):
    text = GUIDE.read_text(encoding="utf-8")
    match = re.search(
        rf"^### {re.escape(heading)}\s+.*?^```json\s+(.*?)^```",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"Missing JSON example under heading: {heading}")
    return json.loads(match.group(1))


def iter_requests(items):
    for item in items:
        if "item" in item:
            yield from iter_requests(item["item"])
        else:
            yield item


class M6AMarketplaceHandoffTests(SimpleTestCase):
    def test_frozen_unversioned_partner_routes(self):
        patterns = {str(pattern.pattern) for pattern in urlpatterns}
        self.assertTrue(
            {
                "health",
                "catalog/filters",
                "service-discovery/search",
                "provider-publication",
                "provider-publication/validation",
                "providers/<str:provider_id>",
                "providers/<str:provider_id>/offerings",
                "offerings/<str:offering_id>",
            }.issubset(patterns)
        )
        self.assertFalse(any(pattern.startswith("v1/") for pattern in patterns))
        self.assertEqual(reverse("health"), "/api/health")
        self.assertEqual(
            reverse("service-discovery-search"),
            "/api/service-discovery/search",
        )
        self.assertEqual(
            reverse("provider-detail", args=["marketplace_m6_example"]),
            "/api/providers/marketplace_m6_example",
        )

    def test_documented_request_examples_match_current_serializers(self):
        registration = documented_json("Registration")
        registration.pop("contract_version")
        serializer = ServiceDiscoveryPublicationSerializer(data=registration)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        offering = documented_json("Second same-category offering")
        serializer = OfferingCreateSerializer(
            data=offering,
            context={"provider_id": "marketplace_m6_20260929_001"},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        serializer = ProviderPatchSerializer(data=documented_json("Provider PATCH"))
        self.assertTrue(serializer.is_valid(), serializer.errors)

        offering_patch = documented_json("Offering PATCH")
        serializer = OfferingPatchSerializer(data=offering_patch)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        patched_offering = deepcopy(offering)
        patched_offering.update(offering_patch)
        validate_lifecycle_offering(patched_offering)

        removal_patch = documented_json("Whole-selected-map attribute removal")
        serializer = OfferingPatchSerializer(
            data=removal_patch
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        patched_offering.update(removal_patch)
        validate_lifecycle_offering(patched_offering)

        search = documented_json("Canonical search")
        search.pop("contract_version")
        serializer = ServiceDiscoverySearchRequestSerializer(data=search)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_postman_assets_are_secret_free_and_have_expected_flow(self):
        collection = json.loads(COLLECTION.read_text(encoding="utf-8"))
        environment = json.loads(ENVIRONMENT.read_text(encoding="utf-8"))
        requests = list(iter_requests(collection["item"]))
        serialized = json.dumps(collection)

        self.assertEqual(collection["info"]["name"], "MaaSAI MDC M6 Marketplace Integration")
        self.assertEqual(len(requests), 29)
        self.assertNotIn("Authorization", serialized)
        self.assertNotIn("X-MDC-Actor", serialized)
        self.assertNotIn("maasai-mdc-v1.vercel.app", serialized)
        self.assertNotIn("/api/v1/", serialized)
        self.assertIn("DESTRUCTIVE CLEANUP", serialized)
        self.assertIn("pm.execution.skipRequest", serialized)

        values = {item["key"]: item["value"] for item in environment["values"]}
        self.assertEqual(
            values["base_url"],
            "https://replace-with-approved-mdc-backend.example",
        )
        self.assertEqual(values["automatic_sync_enabled"], "true")
        self.assertEqual(values["concurrency_required"], "true")
        self.assertFalse(
            {"token", "password", "secret", "authorization"}
            & {key.casefold() for key in values}
        )
