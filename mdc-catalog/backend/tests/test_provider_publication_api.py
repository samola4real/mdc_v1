from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient


def make_valid_provider_publication_payload() -> dict:
    return {
        "provider": {
            "provider_id": "api_example_provider",
            "legal_name": "API Example Provider Oy",
            "display_name": "API Example Provider",
            "provider_type": "MaaSProvider",
            "country": "Finland",
            "facilities": [
                {
                    "facility_id": "api_example_provider_main",
                    "city": "Tampere",
                    "country": "Finland",
                }
            ],
            "certifications": [
                {
                    "code": "ISO9001_2015",
                    "label": "ISO 9001:2015",
                }
            ],
        },
        "offerings": [
            {
                "offering_id": "api_example_provider_precision_machining",
                "name": "API precision machining",
                "service_type": "machining",
                "part_families": ["shaft"],
                "processes": ["machining", "turning"],
                "supported_materials": ["steel"],
                "supported_material_grades": [
                    {
                        "grade_id": "42CrMo4",
                        "label": "42CrMo4",
                        "material_id": "steel",
                    }
                ],
                "capabilities": {
                    "batch_size": {
                        "min": 10,
                        "max": 500,
                        "unit": "pcs",
                    },
                    "diameter_mm": {
                        "min": 5,
                        "max": 300,
                    },
                    "weight_kg": {
                        "max": 100,
                        "approximate": True,
                    },
                    "module": {
                        "min": None,
                        "max": None,
                    },
                    "diametral_pitch": {
                        "min": None,
                        "max": None,
                        "raw": None,
                        "normalized_order": None,
                    },
                    "quality": {
                        "standard": None,
                        "best_class": None,
                        "comparison_rule": None,
                    },
                    "lead_time_weeks": {
                        "min": 4,
                        "max": 8,
                        "qualifier": "normal_case_dependent",
                    },
                    "surface_finish_ra_um": {
                        "max": None,
                    },
                    "tolerance_mm": {
                        "min": None,
                    },
                    "traceability": {
                        "aerospace_traceability": None,
                        "full_traceability": None,
                    },
                },
            }
        ],
        "publication_metadata": {
            "source_type": "provider_confirmed",
            "confidence": "declared",
            "status": "draft",
        },
    }


class ProviderPublicationApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_provider_publication_endpoint_creates_provider_file(self):
        payload = make_valid_provider_publication_payload()

        with TemporaryDirectory() as temp_dir:
            provider_seed_dir = Path(temp_dir) / "providers"

            with override_settings(PROVIDER_SEED_DIR=provider_seed_dir):
                response = self.client.post(
                    "/api/provider-publication",
                    payload,
                    format="json",
                )

                self.assertEqual(response.status_code, 201)

                data = response.json()

                self.assertEqual(data["status"], "accepted")
                self.assertEqual(data["provider_id"], "api_example_provider")
                self.assertEqual(data["created_or_updated"], "created")
                self.assertEqual(len(data["offerings"]), 1)
                self.assertTrue(data["next_steps"]["rdf_generation_required"])
                self.assertFalse(data["next_steps"]["rdf_generation_done"])

                expected_file = provider_seed_dir / "api_example_provider.yaml"
                self.assertTrue(expected_file.exists())

    @override_settings(MDC_PROVIDER_PUBLICATION_ENABLED=False)
    def test_provider_publication_endpoint_disabled_by_feature_flag(self):
        payload = make_valid_provider_publication_payload()

        with TemporaryDirectory() as temp_dir:
            provider_seed_dir = Path(temp_dir) / "providers"

            with override_settings(PROVIDER_SEED_DIR=provider_seed_dir):
                response = self.client.post(
                    "/api/provider-publication",
                    payload,
                    format="json",
                )

                self.assertEqual(response.status_code, 403)
                self.assertEqual(
                    response.json()["error"]["code"],
                    "provider_publication_disabled",
                )
                self.assertFalse(
                    (provider_seed_dir / "api_example_provider.yaml").exists()
                )

    def test_provider_publication_endpoint_updates_existing_provider_file(self):
        payload = make_valid_provider_publication_payload()

        with TemporaryDirectory() as temp_dir:
            provider_seed_dir = Path(temp_dir) / "providers"

            with override_settings(PROVIDER_SEED_DIR=provider_seed_dir):
                first_response = self.client.post(
                    "/api/provider-publication",
                    payload,
                    format="json",
                )
                second_response = self.client.post(
                    "/api/provider-publication",
                    payload,
                    format="json",
                )

                self.assertEqual(first_response.status_code, 201)
                self.assertEqual(second_response.status_code, 201)

                data = second_response.json()

                self.assertEqual(data["created_or_updated"], "updated")

    def test_provider_publication_endpoint_rejects_invalid_payload(self):
        payload = make_valid_provider_publication_payload()
        payload["offerings"][0]["service_type"] = "unknown_service"

        with TemporaryDirectory() as temp_dir:
            provider_seed_dir = Path(temp_dir) / "providers"

            with override_settings(PROVIDER_SEED_DIR=provider_seed_dir):
                response = self.client.post(
                    "/api/provider-publication",
                    payload,
                    format="json",
                )

                self.assertEqual(response.status_code, 400)

                data = response.json()

                self.assertEqual(
                    data["error"]["code"],
                    "invalid_provider_publication",
                )

    def test_provider_publication_endpoint_rejects_route_fields(self):
        payload = make_valid_provider_publication_payload()
        payload["offerings"][0]["route_steps"] = ["turning", "milling"]

        with TemporaryDirectory() as temp_dir:
            provider_seed_dir = Path(temp_dir) / "providers"

            with override_settings(PROVIDER_SEED_DIR=provider_seed_dir):
                response = self.client.post(
                    "/api/provider-publication",
                    payload,
                    format="json",
                )

                self.assertEqual(response.status_code, 400)

                data = response.json()

                self.assertEqual(
                    data["error"]["code"],
                    "invalid_provider_publication",
                )
                self.assertIn("route_steps", str(data["error"]["details"]))
