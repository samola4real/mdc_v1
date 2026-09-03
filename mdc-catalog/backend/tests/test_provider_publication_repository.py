from tempfile import TemporaryDirectory
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from apps.api.provider_publication_serializers import ProviderPublicationSerializer
from apps.providers.normalizers import normalize_provider_publication
from apps.providers.repositories import (
    ProviderRepositoryError,
    load_saved_provider_seed_file,
    save_provider_seed_data,
)


def make_valid_provider_publication_payload() -> dict:
    return {
        "provider": {
            "provider_id": "example_provider",
            "legal_name": "Example Provider Oy",
            "display_name": "Example Provider",
            "provider_type": "MaaSProvider",
            "country": "Finland",
            "facilities": [
                {
                    "facility_id": "example_provider_main",
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
                "offering_id": "example_provider_precision_machining",
                "name": "Precision machining",
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


def make_normalized_seed_data() -> dict:
    payload = make_valid_provider_publication_payload()
    serializer = ProviderPublicationSerializer(data=payload)

    assert serializer.is_valid(), serializer.errors

    return normalize_provider_publication(serializer.validated_data)


class ProviderPublicationRepositoryTests(SimpleTestCase):
    def test_save_provider_seed_data_writes_yaml_file(self):
        seed_data = make_normalized_seed_data()

        with TemporaryDirectory() as temp_dir:
            provider_seed_dir = Path(temp_dir) / "providers"

            with override_settings(PROVIDER_SEED_DIR=provider_seed_dir):
                saved_path = save_provider_seed_data(seed_data)

                self.assertTrue(saved_path.exists())
                self.assertEqual(saved_path.name, "example_provider.yaml")

    def test_saved_provider_seed_file_can_be_loaded_back(self):
        seed_data = make_normalized_seed_data()

        with TemporaryDirectory() as temp_dir:
            provider_seed_dir = Path(temp_dir) / "providers"

            with override_settings(PROVIDER_SEED_DIR=provider_seed_dir):
                saved_path = save_provider_seed_data(seed_data)
                loaded_data = load_saved_provider_seed_file(saved_path)

                self.assertEqual(
                    loaded_data["providers"][0]["provider_id"],
                    "example_provider",
                )
                self.assertEqual(
                    loaded_data["offerings"][0]["offering_id"],
                    "example_provider_precision_machining",
                )

    def test_save_provider_seed_data_rejects_overwrite_false(self):
        seed_data = make_normalized_seed_data()

        with TemporaryDirectory() as temp_dir:
            provider_seed_dir = Path(temp_dir) / "providers"

            with override_settings(PROVIDER_SEED_DIR=provider_seed_dir):
                save_provider_seed_data(seed_data)

                with self.assertRaises(ProviderRepositoryError):
                    save_provider_seed_data(seed_data, overwrite=False)

    def test_save_provider_seed_data_requires_single_provider(self):
        seed_data = make_normalized_seed_data()
        duplicate_provider = dict(seed_data["providers"][0])
        duplicate_provider["provider_id"] = "second_provider"
        seed_data["providers"].append(duplicate_provider)

        with TemporaryDirectory() as temp_dir:
            provider_seed_dir = Path(temp_dir) / "providers"

            with override_settings(PROVIDER_SEED_DIR=provider_seed_dir):
                with self.assertRaises(Exception):
                    save_provider_seed_data(seed_data)