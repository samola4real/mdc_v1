from django.test import SimpleTestCase

from apps.api.provider_publication_serializers import ProviderPublicationSerializer
from apps.providers.normalizers import normalize_provider_publication
from apps.providers.validators import validate_seed_data


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


def get_normalized_seed_data() -> dict:
    payload = make_valid_provider_publication_payload()
    serializer = ProviderPublicationSerializer(data=payload)

    assert serializer.is_valid(), serializer.errors

    return normalize_provider_publication(serializer.validated_data)


class ProviderPublicationNormalizerTests(SimpleTestCase):
    def test_normalizer_returns_seed_data_shape(self):
        seed_data = get_normalized_seed_data()

        self.assertIn("metadata", seed_data)
        self.assertIn("providers", seed_data)
        self.assertIn("materials", seed_data)
        self.assertIn("material_grades", seed_data)
        self.assertIn("offerings", seed_data)

    def test_normalized_seed_data_validates(self):
        seed_data = get_normalized_seed_data()

        validated = validate_seed_data(seed_data)

        self.assertEqual(validated["metadata"]["route_fields_included"], False)

    def test_provider_is_normalized(self):
        seed_data = get_normalized_seed_data()

        provider = seed_data["providers"][0]

        self.assertEqual(provider["provider_id"], "example_provider")
        self.assertEqual(provider["display_name"], "Example Provider")
        self.assertEqual(provider["source_type"], "provider_confirmed")
        self.assertEqual(provider["confidence"], "declared")

    def test_offering_is_normalized(self):
        seed_data = get_normalized_seed_data()

        offering = seed_data["offerings"][0]

        self.assertEqual(
            offering["offering_id"],
            "example_provider_precision_machining",
        )
        self.assertEqual(offering["provider_id"], "example_provider")
        self.assertEqual(offering["service_type"], "machining")
        self.assertEqual(
            offering["ontology_service_concept"],
            "mdc:MachiningService",
        )

    def test_supported_materials_are_normalized(self):
        seed_data = get_normalized_seed_data()

        offering = seed_data["offerings"][0]

        self.assertEqual(
            offering["supported_materials"],
            [
                {
                    "material": "steel",
                    "source_type": "provider_confirmed",
                    "confidence": "declared",
                }
            ],
        )

    def test_materials_are_created_from_publication(self):
        seed_data = get_normalized_seed_data()

        material_ids = {material["material_id"] for material in seed_data["materials"]}

        self.assertIn("steel", material_ids)

    def test_material_grades_are_created_from_publication(self):
        seed_data = get_normalized_seed_data()

        grade_ids = {grade["grade_id"] for grade in seed_data["material_grades"]}

        self.assertIn("42CrMo4", grade_ids)

    def test_known_capabilities_get_publication_provenance(self):
        seed_data = get_normalized_seed_data()

        capabilities = seed_data["offerings"][0]["capabilities"]

        self.assertEqual(
            capabilities["diameter_mm"]["source_type"],
            "provider_confirmed",
        )
        self.assertEqual(
            capabilities["diameter_mm"]["confidence"],
            "declared",
        )

    def test_unknown_capabilities_remain_unknown(self):
        seed_data = get_normalized_seed_data()

        capabilities = seed_data["offerings"][0]["capabilities"]

        self.assertEqual(capabilities["module"]["source_type"], "not_confirmed")
        self.assertEqual(capabilities["module"]["confidence"], "unknown")

        self.assertEqual(capabilities["tolerance_mm"]["source_type"], "not_confirmed")
        self.assertEqual(capabilities["tolerance_mm"]["confidence"], "unknown")