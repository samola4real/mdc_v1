from django.test import SimpleTestCase

from apps.api.provider_publication_serializers import ProviderPublicationSerializer


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


class ProviderPublicationSerializerTests(SimpleTestCase):
    def test_valid_provider_publication_payload_is_accepted(self):
        payload = make_valid_provider_publication_payload()

        serializer = ProviderPublicationSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        validated_data = serializer.validated_data

        self.assertEqual(
            validated_data["provider"]["provider_id"],
            "example_provider",
        )
        self.assertEqual(len(validated_data["offerings"]), 1)
        self.assertEqual(
            validated_data["offerings"][0]["service_type"],
            "machining",
        )

    def test_missing_provider_is_rejected(self):
        payload = make_valid_provider_publication_payload()
        payload.pop("provider")

        serializer = ProviderPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("provider", serializer.errors)

    def test_missing_offerings_is_rejected(self):
        payload = make_valid_provider_publication_payload()
        payload.pop("offerings")

        serializer = ProviderPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("offerings", serializer.errors)

    def test_empty_offerings_is_rejected(self):
        payload = make_valid_provider_publication_payload()
        payload["offerings"] = []

        serializer = ProviderPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("offerings", serializer.errors)

    def test_invalid_service_type_is_rejected(self):
        payload = make_valid_provider_publication_payload()
        payload["offerings"][0]["service_type"] = "unknown_service"

        serializer = ProviderPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("offerings", serializer.errors)

    def test_invalid_process_is_rejected(self):
        payload = make_valid_provider_publication_payload()
        payload["offerings"][0]["processes"].append("magic_cutting")

        serializer = ProviderPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("offerings", serializer.errors)

    def test_invalid_material_grade_material_reference_is_rejected(self):
        payload = make_valid_provider_publication_payload()
        payload["offerings"][0]["supported_material_grades"][0][
            "material_id"
        ] = "aluminum"

        serializer = ProviderPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("offerings", serializer.errors)

    def test_negative_diameter_is_rejected(self):
        payload = make_valid_provider_publication_payload()
        payload["offerings"][0]["capabilities"]["diameter_mm"]["max"] = -10

        serializer = ProviderPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("offerings", serializer.errors)

    def test_invalid_range_is_rejected(self):
        payload = make_valid_provider_publication_payload()
        payload["offerings"][0]["capabilities"]["diameter_mm"] = {
            "min": 300,
            "max": 100,
        }

        serializer = ProviderPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("offerings", serializer.errors)

    def test_forbidden_route_field_is_rejected(self):
        payload = make_valid_provider_publication_payload()
        payload["offerings"][0]["route_steps"] = ["turning", "milling"]

        serializer = ProviderPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("forbidden_fields", serializer.errors)
        self.assertIn("route_steps", str(serializer.errors))

    def test_duplicate_offering_ids_are_rejected(self):
        payload = make_valid_provider_publication_payload()
        duplicate = dict(payload["offerings"][0])
        payload["offerings"].append(duplicate)

        serializer = ProviderPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("offerings", serializer.errors)

    def test_offering_id_should_start_with_provider_id(self):
        payload = make_valid_provider_publication_payload()
        payload["offerings"][0]["offering_id"] = "wrong_prefix_machining"

        serializer = ProviderPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("offerings", serializer.errors)