from copy import deepcopy

from django.test import TestCase, override_settings
from rdflib import Literal
from rest_framework import status
from rest_framework.test import APIClient

from apps.ontology.service_discovery_rdf_generator import (
    build_service_discovery_graph,
)
from apps.ontology.service_discovery_rdf_mappings import (
    MDC,
    family_capability_resource,
    offering_resource,
)
from apps.providers.models import (
    CatalogueSyncEvent,
    Offering,
    Provider,
    ProviderPublication,
)
from apps.providers.service_discovery_db_repository import (
    load_service_discovery_providers_from_db,
)
from apps.search.service_discovery_local_matcher import (
    search_service_discovery_catalog,
)
from tests.test_service_discovery_matching_alignment import gear_request
from tests.test_service_discovery_publication_serializer import (
    make_valid_family_level_gears_payload,
)


PILOT_SETTINGS = {
    "MDC_PROVIDER_PUBLICATION_ENABLED": True,
    "MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED": False,
    "MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED": False,
    "MDC_PROVIDER_CONCURRENCY_REQUIRED": True,
}


def provider_payload(provider_id="m2_generic_forge"):
    payload = make_valid_family_level_gears_payload()
    payload["provider_id"] = provider_id
    payload["provider_name"] = "M2 Generic Forge"
    return payload


def same_category_offering(name, *, module_max):
    offering = deepcopy(make_valid_family_level_gears_payload()["offerings"][0])
    offering["offering_name"] = name
    offering["family_capabilities"]["module"]["max"] = module_max
    return offering


@override_settings(**PILOT_SETTINGS)
class M2MultiOfferingManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def register(self, payload=None):
        return self.client.post(
            "/api/provider-publication",
            payload or provider_payload(),
            format="json",
        )

    def test_first_registration_preserves_legacy_offering_id(self):
        response = self.register()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json()["offering_ids"],
            ["m2_generic_forge_precision_gears"],
        )
        self.assertTrue(
            Offering.objects.filter(
                offering_id="m2_generic_forge_precision_gears"
            ).exists()
        )

    def test_initial_registration_accepts_two_same_category_offerings(self):
        payload = provider_payload()
        payload["offerings"][0]["offering_name"] = "Standard gear line"
        payload["offerings"][0]["family_capabilities"]["module"]["max"] = 8
        payload["offerings"].append(
            same_category_offering("Heavy duty gear line", module_max=14)
        )

        response = self.register(payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        offering_ids = [
            "m2_generic_forge_precision_gears",
            "m2_generic_forge_precision_gears_heavy_duty_gear_line",
        ]
        self.assertEqual(response.json()["offering_ids"], offering_ids)
        self.assertEqual(
            list(
                Offering.objects.order_by("sequence_index").values_list(
                    "offering_id", flat=True
                )
            ),
            offering_ids,
        )
        self.assertEqual(
            set(
                CatalogueSyncEvent.objects.filter(entity_type="offering").values_list(
                    "entity_id", flat=True
                )
            ),
            set(offering_ids),
        )
        self.assertEqual(
            [
                item["offering_id"]
                for item in ProviderPublication.objects.get().normalized_payload[
                    "offerings"
                ]
            ],
            offering_ids,
        )

    def test_post_same_category_get_list_and_patch_are_independent(self):
        self.assertEqual(self.register().status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            "/api/providers/m2_generic_forge/offerings",
            same_category_offering("Prototype gear cell", module_max=16),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sibling_id = "m2_generic_forge_precision_gears_prototype_gear_cell"
        self.assertEqual(response.json()["offering_id"], sibling_id)

        list_response = self.client.get(
            "/api/providers/m2_generic_forge/offerings"
        )
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["offering_id"] for item in list_response.json()["offerings"]],
            ["m2_generic_forge_precision_gears", sibling_id],
        )

        detail_url = f"/api/offerings/{sibling_id}"
        detail = self.client.get(detail_url)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        response = self.client.patch(
            detail_url,
            {
                "offering_name": "Updated prototype cell",
                "family_capabilities": {"module": {"max": 18}},
            },
            format="json",
            HTTP_IF_MATCH=detail["ETag"],
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        legacy = Offering.objects.get(
            offering_id="m2_generic_forge_precision_gears"
        )
        sibling = Offering.objects.get(offering_id=sibling_id)
        self.assertEqual(legacy.offering_name, "Precision gears")
        self.assertNotEqual(
            legacy.family_capabilities["module"]["max"],
            sibling.family_capabilities["module"]["max"],
        )
        self.assertEqual(sibling.offering_id, sibling_id)

    def test_explicit_ids_are_preserved_and_duplicate_input_is_rejected(self):
        payload = provider_payload()
        payload["offerings"][0]["offering_id"] = (
            "m2_generic_forge_standard_gear_line"
        )
        payload["offerings"].append(
            same_category_offering("Precision cell two", module_max=11)
        )
        payload["offerings"][1]["offering_id"] = (
            "m2_generic_forge_precision_cell_two"
        )

        response = self.register(payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json()["offering_ids"],
            [
                "m2_generic_forge_standard_gear_line",
                "m2_generic_forge_precision_cell_two",
            ],
        )

        duplicate_payload = provider_payload("m2_duplicate_batch")
        duplicate_payload["offerings"][0]["offering_id"] = (
            "m2_duplicate_batch_shared_line"
        )
        duplicate_payload["offerings"].append(
            same_category_offering("Other line", module_max=12)
        )
        duplicate_payload["offerings"][1]["offering_id"] = (
            "m2_duplicate_batch_shared_line"
        )
        response = self.register(duplicate_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Provider.objects.filter(provider_id="m2_duplicate_batch").exists()
        )

    def test_invalid_cross_provider_db_duplicate_and_patch_identity_are_rejected(self):
        self.assertEqual(self.register().status_code, status.HTTP_201_CREATED)

        invalid = same_category_offering("Invalid", module_max=10)
        invalid["offering_id"] = "Invalid-Hyphenated-ID"
        response = self.client.post(
            "/api/providers/m2_generic_forge/offerings", invalid, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        Provider.objects.create(
            provider_id="m2_other_forge",
            provider_name="Other Forge",
            country="Finland",
            status=Provider.Status.ACTIVE,
        )
        cross_provider = same_category_offering("Cross owner", module_max=10)
        cross_provider["offering_id"] = "m2_generic_forge_cross_owner"
        response = self.client.post(
            "/api/providers/m2_other_forge/offerings",
            cross_provider,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        duplicate = same_category_offering("Explicit duplicate", module_max=10)
        duplicate["offering_id"] = "m2_generic_forge_precision_gears"
        response = self.client.post(
            "/api/providers/m2_generic_forge/offerings",
            duplicate,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.json()["error"]["code"], "offering_already_exists"
        )

        detail = self.client.get(
            "/api/offerings/m2_generic_forge_precision_gears"
        )
        response = self.client.patch(
            "/api/offerings/m2_generic_forge_precision_gears",
            {"offering_id": "m2_generic_forge_replacement"},
            format="json",
            HTTP_IF_MATCH=detail["ETag"],
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True,
        MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN="m2-service-token",
        MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True,
    )
    def test_secured_mode_requires_auth_and_actor_for_multi_offering_post(self):
        Provider.objects.create(
            provider_id="m2_secured_forge",
            provider_name="Secured Forge",
            country="Finland",
            status=Provider.Status.ACTIVE,
        )
        payload = same_category_offering("Secured line", module_max=10)
        payload["offering_id"] = "m2_secured_forge_secured_line"
        url = "/api/providers/m2_secured_forge/offerings"

        self.assertEqual(
            self.client.post(url, payload, format="json").status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            self.client.post(
                url,
                payload,
                format="json",
                HTTP_AUTHORIZATION="Bearer m2-service-token",
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        response = self.client.post(
            url,
            payload,
            format="json",
            HTTP_AUTHORIZATION="Bearer m2-service-token",
            HTTP_X_MDC_ACTOR_ID="marketplace:m2-test",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_rdf_and_discovery_keep_same_category_offerings_distinct(self):
        payload = provider_payload()
        payload["offerings"][0]["offering_name"] = "Small module line"
        payload["offerings"][0]["family_capabilities"]["module"]["max"] = 6
        payload["offerings"].append(
            same_category_offering("Large module line", module_max=18)
        )
        self.assertEqual(self.register(payload).status_code, status.HTTP_201_CREATED)

        records = load_service_discovery_providers_from_db()
        graph = build_service_discovery_graph(provider_records=records)
        legacy_id = "m2_generic_forge_precision_gears"
        sibling_id = "m2_generic_forge_precision_gears_large_module_line"
        legacy_node = family_capability_resource(legacy_id, "module")
        sibling_node = family_capability_resource(sibling_id, "module")

        self.assertNotEqual(offering_resource(legacy_id), offering_resource(sibling_id))
        self.assertNotEqual(legacy_node, sibling_node)
        self.assertIn((offering_resource(legacy_id), MDC.hasFamilyCapability, legacy_node), graph)
        self.assertIn((offering_resource(sibling_id), MDC.hasFamilyCapability, sibling_node), graph)
        self.assertIn((legacy_node, MDC.maxValue, Literal(6)), graph)
        self.assertIn((sibling_node, MDC.maxValue, Literal(18)), graph)

        search = search_service_discovery_catalog(
            gear_request(), provider_records=records
        )
        results = {
            item["offering"]["offering_id"]: item
            for item in search["results"]
        }
        self.assertEqual(set(results), {legacy_id, sibling_id})
        self.assertEqual(
            results[legacy_id]["evidence"]["family_capabilities"]["module"]["max"],
            6,
        )
        self.assertEqual(
            results[sibling_id]["evidence"]["family_capabilities"]["module"]["max"],
            18,
        )
