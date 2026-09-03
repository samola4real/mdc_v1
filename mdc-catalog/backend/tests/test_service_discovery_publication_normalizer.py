from django.test import SimpleTestCase

from apps.api.service_discovery_publication_serializers import (
    ServiceDiscoveryPublicationSerializer,
)
from apps.providers.service_discovery_publication import (
    generate_offering_id,
    normalize_service_discovery_publication,
)
from tests.test_service_discovery_publication_serializer import (
    make_valid_family_level_gears_payload,
)


def get_normalized_publication(payload: dict | None = None) -> dict:
    payload = payload or make_valid_family_level_gears_payload()
    serializer = ServiceDiscoveryPublicationSerializer(data=payload)

    assert serializer.is_valid(), serializer.errors

    return normalize_service_discovery_publication(serializer.validated_data)


class ServiceDiscoveryPublicationNormalizerTests(SimpleTestCase):
    def test_generate_offering_id_for_precision_gears(self):
        self.assertEqual(
            generate_offering_id("tasowheel", "precision_gears"),
            "tasowheel_precision_gears",
        )

    def test_generate_offering_id_for_precision_shafts(self):
        self.assertEqual(
            generate_offering_id("tasowheel", "precision_shafts"),
            "tasowheel_precision_shafts",
        )

    def test_provider_name_normalizes_to_internal_display_name(self):
        normalized = get_normalized_publication()

        self.assertEqual(normalized["provider"]["display_name"], "Tasowheel Oy")
        self.assertNotIn("provider_name", normalized["provider"])

    def test_two_offering_publication_generates_two_internal_offering_ids(self):
        payload = {
            "provider_id": "tasowheel",
            "provider_name": "Tasowheel Oy",
            "country": "Finland",
            "offerings": [
                {
                    "service_category": "precision_gears",
                    "offering_name": "Precision gears",
                    "part_family": "gear",
                    "support_status": "confirmed",
                },
                {
                    "service_category": "precision_shafts",
                    "offering_name": "Precision shafts",
                    "part_family": "shaft",
                    "support_status": "confirmed",
                },
            ],
        }

        normalized = get_normalized_publication(payload)
        offering_ids = [offering["offering_id"] for offering in normalized["offerings"]]

        self.assertEqual(
            offering_ids,
            [
                "tasowheel_precision_gears",
                "tasowheel_precision_shafts",
            ],
        )

    def test_each_normalized_offering_includes_provider_id(self):
        normalized = get_normalized_publication()

        for offering in normalized["offerings"]:
            self.assertEqual(offering["provider_id"], "tasowheel")

    def test_offering_name_normalizes_to_internal_name(self):
        normalized = get_normalized_publication()
        offering = normalized["offerings"][0]

        self.assertEqual(offering["name"], "Precision gears")
        self.assertNotIn("offering_name", offering)

    def test_service_category_family_support_and_capabilities_are_preserved(self):
        normalized = get_normalized_publication()
        offering = normalized["offerings"][0]

        self.assertEqual(offering["service_category"], "precision_gears")
        self.assertEqual(offering["part_family"], "gear")
        self.assertEqual(offering["support_status"], "confirmed")
        self.assertIn("outside_diameter_mm", offering["family_capabilities"])
        self.assertIn("materials", offering["generic_capabilities"])

    def test_material_available_grades_are_preserved_as_evidence(self):
        normalized = get_normalized_publication()
        materials = normalized["offerings"][0]["generic_capabilities"]["materials"]

        self.assertEqual(
            materials[0]["available_grades"],
            ["18CrNiMo7-6", "16MnCr5", "20MnCr5"],
        )

    def test_normalizer_does_not_write_yaml_file(self):
        normalized = get_normalized_publication()

        self.assertIn("provider", normalized)
        self.assertNotIn("metadata", normalized)
        self.assertNotIn("materials", normalized)
        self.assertNotIn("material_grades", normalized)

    def test_normalizer_does_not_insert_legacy_service_type(self):
        normalized = get_normalized_publication()
        offering = normalized["offerings"][0]

        self.assertNotIn("service_type", offering)

    def test_supplied_publication_metadata_is_preserved(self):
        payload = make_valid_family_level_gears_payload()
        payload["publication_metadata"] = {
            "source_type": "provider_confirmed",
            "confidence": "declared",
            "source_note": "Submitted through provider discovery form.",
        }

        normalized = get_normalized_publication(payload)

        self.assertEqual(
            normalized["publication_metadata"],
            {
                "source_type": "provider_confirmed",
                "confidence": "declared",
                "source_note": "Submitted through provider discovery form.",
            },
        )

    def test_defaulted_publication_metadata_is_preserved(self):
        normalized = get_normalized_publication()

        self.assertEqual(
            normalized["publication_metadata"]["source_type"],
            "provider_confirmed",
        )
        self.assertEqual(
            normalized["publication_metadata"]["confidence"],
            "declared",
        )

    def test_updated_tasowheel_shaft_and_process_evidence_is_preserved(self):
        payload = {
            "provider_id": "tasowheel",
            "provider_name": "Tasowheel Oy",
            "country": "Finland",
            "offerings": [
                {
                    "service_category": "precision_shafts",
                    "offering_name": "Precision shafts",
                    "part_family": "shaft",
                    "support_status": "confirmed",
                    "supported_part_types": [
                        {
                            "part_type": "splined_shaft",
                            "support_status": "confirmed",
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        }
                    ],
                    "family_capabilities": {
                        "length_mm": {
                            "max": 500,
                            "source_type": "public_web",
                            "confidence": "publicly_confirmed",
                        },
                        "outer_diameter_mm": {
                            "min": 10,
                            "max": 450,
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        },
                    },
                    "part_type_capabilities": {
                        "splined_shaft": {
                            "spline_module": {
                                "min": 0.3,
                                "max": 10,
                                "source_type": "provider_confirmed",
                                "confidence": "declared",
                            }
                        }
                    },
                    "generic_capabilities": {
                        "processes": [
                            {
                                "process": "turn_mill",
                                "delivery_mode": "unspecified",
                                "source_type": "provider_confirmed",
                                "confidence": "declared",
                            }
                        ]
                    },
                }
            ],
        }

        normalized = get_normalized_publication(payload)
        offering = normalized["offerings"][0]

        self.assertEqual(offering["offering_id"], "tasowheel_precision_shafts")
        self.assertEqual(
            offering["family_capabilities"]["length_mm"]["source_type"],
            "public_web",
        )
        self.assertIn(
            "spline_module",
            offering["part_type_capabilities"]["splined_shaft"],
        )
        self.assertEqual(
            offering["generic_capabilities"]["processes"][0]["process"],
            "turn_mill",
        )
