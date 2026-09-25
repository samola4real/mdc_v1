import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.providers.models import ProviderPublication
from tests.test_provider_publication_api import (
    make_valid_provider_publication_payload,
)
from tests.test_service_discovery_publication_serializer import (
    make_valid_family_level_gears_payload,
)
from tests.test_service_discovery_search_endpoint import endpoint_response
from tests.test_service_discovery_search_serializer import (
    complete_spur_gear_request,
)


PILOT_SETTINGS = {
    "MDC_PROVIDER_PUBLICATION_ENABLED": True,
    "MDC_PROVIDER_VALIDATION_ENABLED": True,
    "MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED": False,
    "MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN": "",
    "MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED": False,
    "MDC_PROVIDER_CONCURRENCY_REQUIRED": True,
    "MDC_CATALOG_SYNC_ENABLED": False,
}


@override_settings(**PILOT_SETTINGS)
class M1LifecyclePilotReadinessTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @staticmethod
    def second_offering_payload():
        item = deepcopy(make_valid_family_level_gears_payload()["offerings"][0])
        item.update(
            service_category="precision_shafts",
            offering_name="Pilot shafts",
            part_family="shaft",
        )
        item["family_capabilities"] = {}
        item["generic_capabilities"] = {}
        return item

    def test_opt_in_pilot_allows_anonymous_lifecycle_and_keeps_etags_required(self):
        payload = make_valid_provider_publication_payload()
        response = self.client.post(
            "/api/provider-publication", payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(ProviderPublication.objects.get().submitted_by_external_id)

        provider_url = "/api/providers/api_example_provider"
        response = self.client.get(provider_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        provider_etag = response["ETag"]

        response = self.client.patch(
            provider_url, {"country": "Sweden"}, format="json"
        )
        self.assertEqual(response.status_code, 428)
        self.assertEqual(
            response.json()["error"]["code"],
            "concurrency_precondition_required",
        )

        response = self.client.patch(
            provider_url,
            {"country": "Sweden"},
            format="json",
            HTTP_IF_MATCH=provider_etag,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            f"{provider_url}/offerings",
            self.second_offering_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json()["offering_id"],
            "api_example_provider_precision_shafts",
        )

        offering_url = "/api/offerings/api_example_provider_precision_shafts"
        response = self.client.get(offering_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        offering_etag = response["ETag"]
        response = self.client.patch(
            offering_url,
            {"offering_name": "Updated pilot shafts"},
            format="json",
            HTTP_IF_MATCH=offering_etag,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(
            offering_url,
            {"offering_name": "Stale overwrite"},
            format="json",
            HTTP_IF_MATCH=offering_etag,
        )
        self.assertEqual(response.status_code, status.HTTP_412_PRECONDITION_FAILED)

        response = self.client.post(
            "/api/provider-publication/validation",
            make_valid_provider_publication_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["valid"])

    @override_settings(
        MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True,
        MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN="m1-test-service-token",
        MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True,
    )
    def test_secured_mode_remains_restorable(self):
        read_response = self.client.get("/api/providers/missing")
        write_response = self.client.post(
            "/api/provider-publication",
            make_valid_provider_publication_payload(),
            format="json",
        )
        for response in (read_response, write_response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(
                response.json()["error"]["code"],
                "trusted_lifecycle_auth_required",
            )

    @override_settings(
        MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True,
        MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN="m1-test-service-token",
        MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True,
    )
    @patch(
        "apps.api.views.post_views.search_service_discovery_with_runtime_backends"
    )
    def test_canonical_discovery_post_remains_public(self, runtime_search):
        runtime_search.return_value = endpoint_response(
            "harmonized_fuseki_with_h5_policy"
        )
        response = self.client.post(
            "/api/service-discovery/search",
            complete_spur_gear_request(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class M1ProductionPilotConfigurationTests(SimpleTestCase):
    def test_explicit_environment_values_override_secure_production_defaults(self):
        script = """
from config import settings_production as production
assert production.MDC_PROVIDER_PUBLICATION_ENABLED is True
assert production.MDC_PROVIDER_VALIDATION_ENABLED is True
assert production.MDC_CATALOG_SYNC_ENABLED is False
assert production.MDC_CATALOG_AUTO_SYNC_ENABLED is False
assert production.MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED is False
assert production.MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED is False
assert production.MDC_PROVIDER_CONCURRENCY_REQUIRED is True
"""
        inherited = {
            key: os.environ[key]
            for key in ("SYSTEMROOT", "PATH", "TEMP", "TMP")
            if key in os.environ
        }
        inherited.update(
            DJANGO_SECRET_KEY="isolated-m1-test-secret",
            MDC_PROVIDER_PUBLICATION_ENABLED="True",
            MDC_PROVIDER_VALIDATION_ENABLED="True",
            MDC_CATALOG_SYNC_ENABLED="False",
            MDC_CATALOG_AUTO_SYNC_ENABLED="False",
            MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED="False",
            MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN="",
            MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED="False",
            MDC_PROVIDER_CONCURRENCY_REQUIRED="True",
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            env=inherited,
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
