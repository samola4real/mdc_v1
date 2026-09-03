from pathlib import Path

import yaml
from django.test import SimpleTestCase

from apps.api.service_discovery_publication_serializers import (
    ServiceDiscoveryPublicationSerializer,
)
from apps.providers.service_discovery_publication import (
    normalize_service_discovery_publication,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HARMONIZED_PROVIDER_DIR = PROJECT_ROOT / "data" / "curated" / "service_discovery" / "providers"
LEGACY_PROVIDER_DIR = PROJECT_ROOT / "data" / "curated" / "providers"

FORBIDDEN_PUBLICATION_KEYS = {
    "routes",
    "route_steps",
    "operation_sequence",
    "machine_sequence",
    "process_order",
    "subcontractor_route",
    "cycle_time",
    "setup_time",
    "machine_availability",
    "pricing",
    "capacity_calendar",
}


def load_harmonized_provider(provider_id: str) -> dict:
    with (HARMONIZED_PROVIDER_DIR / f"{provider_id}.yaml").open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def normalize_fixture(payload: dict) -> dict:
    serializer = ServiceDiscoveryPublicationSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors
    return normalize_service_discovery_publication(serializer.validated_data)


def tasowheel_payload() -> dict:
    shared_processes = [
        {
            "process": process,
            "delivery_mode": "unspecified",
            "source_type": "provider_confirmed",
            "confidence": "declared",
        }
        for process in [
            "machining",
            "hobbing",
            "gear_shaping",
            "deburring",
            "hard_turning",
            "grinding",
            "tooth_grinding",
            "gear_grinding",
            "gear_cutting",
            "surface_grinding",
            "milling",
            "turn_mill",
        ]
    ]
    shared_materials = [
        {
            "material": "alloyed_carburizing_steel",
            "available_grades": [
                "18CrNiMo7-6",
                "16MnCr5",
                "20MnCr5",
            ],
            "source_type": "provider_confirmed",
            "confidence": "declared",
            "source_note": (
                "Additional commonly used alloyed carburizing steels are supported, "
                "but individual additional grades are not enumerated in the current evidence."
            ),
        }
    ]
    shared_generic = {
        "materials": shared_materials,
        "processes": shared_processes,
        "batch_size": {
            "min": 100,
            "max": 2000,
            "unit": "pcs",
            "source_type": "provider_confirmed",
            "confidence": "declared",
            "source_note": "TSW questionnaire states batch sizes 100-2000 pcs.",
        },
        "lead_time_weeks": {
            "min": 8,
            "max": 12,
            "qualifier": "normal_case_dependent",
            "source_type": "provider_confirmed",
            "confidence": "declared",
            "source_note": (
                "TSW questionnaire states normal delivery time is 8-12 weeks "
                "and case dependent."
            ),
        },
        "weight_kg": {
            "max": 200,
            "approximate": True,
            "source_type": "provider_confirmed",
            "confidence": "declared",
            "source_note": "TSW questionnaire states weights up to approximately 200 kg.",
        },
        "surface_finish_ra_um": {
            "max": None,
            "source_type": "not_confirmed",
            "confidence": "unknown",
            "source_note": "Surface roughness/Ra is not confirmed in v1 data.",
        },
    }
    return {
        "provider_id": "tasowheel",
        "provider_name": "Tasowheel Oy",
        "country": "Finland",
        "certifications": [
            {
                "code": "ISO9001_2015",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            },
            {
                "code": "ISO14001_2015",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            },
            {
                "code": "ISO_TS_16949_partial",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            },
            {
                "code": "APQP",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            },
        ],
        "offerings": [
            {
                "service_category": "precision_gears",
                "offering_name": "Precision gears",
                "part_family": "gear",
                "support_status": "confirmed",
                "supported_part_types": [
                    {
                        "part_type": part_type,
                        "support_status": "confirmed",
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    }
                    for part_type in [
                        "spur_gear",
                        "helical_gear",
                        "bevel_gear",
                        "worm_gear",
                    ]
                ],
                "family_capabilities": {
                    "module": {
                        "min": 0.3,
                        "max": 10,
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                        "source_note": "TSW questionnaire states module range 0.3-10.",
                    },
                    "diametral_pitch": {
                        "min": 2.5,
                        "max": 85,
                        "raw": "DP 85-2.5",
                        "normalized_order": "ascending",
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                        "source_note": "Raw DP value preserved from TSW questionnaire.",
                    },
                    "outside_diameter_mm": {
                        "min": 10,
                        "max": 450,
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                        "source_note": (
                            "Legacy diameter_mm mapped to harmonized gear "
                            "outside_diameter_mm."
                        ),
                    },
                    "gear_quality": {
                        "standard": "DIN",
                        "best_class": 4,
                        "comparison_rule": "lower_or_equal_is_better",
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                        "source_note": "TSW questionnaire states quality demands up to DIN4.",
                    },
                },
                "part_type_capabilities": {},
                "generic_capabilities": shared_generic,
            },
            {
                "service_category": "precision_shafts",
                "offering_name": "Precision shafts",
                "part_family": "shaft",
                "support_status": "confirmed",
                "supported_part_types": [
                    {
                        "part_type": part_type,
                        "support_status": "confirmed",
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    }
                    for part_type in [
                        "splined_shaft",
                        "plain_shaft",
                        "hollow_shaft",
                    ]
                ],
                "family_capabilities": {
                    "length_mm": {
                        "max": 500,
                        "source_type": "public_web",
                        "confidence": "publicly_confirmed",
                        "source_note": (
                            "Tasowheel publicly states that shafts up to 500 mm "
                            "in length can be produced."
                        ),
                    },
                    "outer_diameter_mm": {
                        "min": 10,
                        "max": 450,
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                        "source_note": (
                            "Legacy diameter_mm mapped to harmonized shaft "
                            "outer_diameter_mm."
                        ),
                    }
                },
                "part_type_capabilities": {
                    "splined_shaft": {
                        "spline_module": {
                            "min": 0.3,
                            "max": 10,
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                            "source_note": (
                                "Tasowheel confirms the module range applies to the "
                                "shafts it produces; under the current MDC schema this "
                                "is represented only for the confirmed splined_shaft subtype."
                            ),
                        }
                    }
                },
                "generic_capabilities": shared_generic,
            },
        ],
        "publication_metadata": {
            "source_type": "provider_confirmed",
            "confidence": "declared",
        },
    }


def demo_machining_payload() -> dict:
    return {
        "provider_id": "demo_machining_provider",
        "provider_name": "Demo Machining Provider",
        "country": "Finland",
        "certifications": [
            {
                "code": "ISO9001_2015",
                "source_type": "curated",
                "confidence": "curated",
            }
        ],
        "offerings": [
            {
                "service_category": "precision_shafts",
                "offering_name": "Precision shafts",
                "part_family": "shaft",
                "support_status": "confirmed",
                "supported_part_types": [],
                "family_capabilities": {
                    "outer_diameter_mm": {
                        "min": 5,
                        "max": 300,
                        "source_type": "curated",
                        "confidence": "curated",
                        "source_note": (
                            "Legacy demo diameter_mm mapped to harmonized shaft "
                            "outer_diameter_mm."
                        ),
                    }
                },
                "part_type_capabilities": {},
                "generic_capabilities": {
                    "materials": [
                        {
                            "material": "steel",
                            "available_grades": ["42CrMo4"],
                            "source_type": "curated",
                            "confidence": "curated",
                        },
                        {
                            "material": "aluminum",
                            "available_grades": ["Al6082"],
                            "source_type": "curated",
                            "confidence": "curated",
                        },
                    ],
                    "processes": [
                        {
                            "process": process,
                            "delivery_mode": "unspecified",
                            "source_type": "curated",
                            "confidence": "curated",
                        }
                        for process in ["machining", "turning", "milling", "grinding"]
                    ],
                    "batch_size": {
                        "min": 10,
                        "max": 500,
                        "unit": "pcs",
                        "source_type": "curated",
                        "confidence": "curated",
                    },
                    "lead_time_weeks": {
                        "min": 4,
                        "max": 8,
                        "qualifier": "normal_case_dependent",
                        "source_type": "curated",
                        "confidence": "curated",
                    },
                    "weight_kg": {
                        "max": 100,
                        "approximate": True,
                        "source_type": "curated",
                        "confidence": "curated",
                    },
                    "surface_finish_ra_um": {
                        "max": 3.2,
                        "source_type": "curated",
                        "confidence": "curated",
                    },
                },
            }
        ],
        "publication_metadata": {
            "source_type": "curated",
            "confidence": "curated",
        },
    }


def precipart_payload() -> dict:
    return {
        "provider_id": "precipart",
        "provider_name": "Precipart",
        "country": "Switzerland",
        "offerings": [
            {
                "service_category": "precision_gears",
                "offering_name": "High-precision custom gears",
                "part_family": "gear",
                "support_status": "confirmed",
                "supported_part_types": [
                    {
                        "part_type": "spur_gear",
                        "support_status": "confirmed",
                        "source_type": "public_web",
                        "confidence": "publicly_confirmed",
                    },
                    {
                        "part_type": "helical_gear",
                        "support_status": "confirmed",
                        "source_type": "public_web",
                        "confidence": "publicly_confirmed",
                    },
                    {
                        "part_type": "worm_gear",
                        "support_status": "confirmed",
                        "source_type": "public_web",
                        "confidence": "publicly_confirmed",
                    },
                    {
                        "part_type": "crown_gear",
                        "support_status": "candidate_requiring_confirmation",
                        "source_type": "public_web",
                        "confidence": "inferred",
                        "source_note": (
                            "Source lists face_gear and records crown_gear as a "
                            "candidate mapping requiring confirmation."
                        ),
                    },
                ],
                "family_capabilities": {
                    "module": {
                        "min": 0.125,
                        "max": 1.5,
                        "source_type": "public_web",
                        "confidence": "publicly_confirmed",
                        "source_note": "Source field module_mm mapped to harmonized module.",
                    },
                    "diametral_pitch": {
                        "min": 16,
                        "max": 200,
                        "source_type": "public_web",
                        "confidence": "publicly_confirmed",
                    },
                    "outside_diameter_mm": {
                        "min": 6,
                        "max": 102,
                        "source_type": "public_web",
                        "confidence": "publicly_confirmed",
                    },
                    "gear_quality": {
                        "standard": "ISO",
                        "best_class": 5,
                        "comparison_rule": "lower_or_equal_is_better",
                        "source_type": "public_web",
                        "confidence": "publicly_confirmed",
                        "source_note": "Source lists ISO 5 among supported gear quality references.",
                    },
                },
                "part_type_capabilities": {},
                "generic_capabilities": {},
            }
        ],
        "publication_metadata": {
            "source_type": "public_web",
            "confidence": "publicly_confirmed",
        },
    }


def iter_nested_values(data):
    if isinstance(data, dict):
        for key, value in data.items():
            yield key, value
            yield from iter_nested_values(value)
    elif isinstance(data, list):
        for item in data:
            yield from iter_nested_values(item)


class ServiceDiscoveryProviderYamlMigrationTests(SimpleTestCase):
    def test_harmonized_tasowheel_yaml_file_exists(self):
        self.assertTrue((HARMONIZED_PROVIDER_DIR / "tasowheel.yaml").exists())

    def test_tasowheel_external_fixture_validates(self):
        serializer = ServiceDiscoveryPublicationSerializer(data=tasowheel_payload())

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_tasowheel_yaml_equals_h2_normalized_fixture(self):
        self.assertEqual(
            load_harmonized_provider("tasowheel"),
            normalize_fixture(tasowheel_payload()),
        )

    def test_tasowheel_offering_ids_are_split_and_generated(self):
        loaded = load_harmonized_provider("tasowheel")
        offering_ids = [offering["offering_id"] for offering in loaded["offerings"]]

        self.assertEqual(
            offering_ids,
            [
                "tasowheel_precision_gears",
                "tasowheel_precision_shafts",
            ],
        )
        self.assertNotIn("tasowheel_gears_shafts_precision", offering_ids)
        self.assertNotIn("tasowheel_precision_metal_parts", offering_ids)

    def test_tasowheel_gears_use_harmonized_outside_diameter(self):
        gear_offering = load_harmonized_provider("tasowheel")["offerings"][0]
        family_capabilities = gear_offering["family_capabilities"]

        self.assertEqual(gear_offering["part_family"], "gear")
        self.assertEqual(gear_offering["service_category"], "precision_gears")
        self.assertIn("outside_diameter_mm", family_capabilities)
        self.assertNotIn("diameter_mm", family_capabilities)
        self.assertNotIn("outer_diameter_mm", family_capabilities)

    def test_tasowheel_shafts_use_outer_diameter_without_gear_fields(self):
        shaft_offering = load_harmonized_provider("tasowheel")["offerings"][1]
        family_capabilities = shaft_offering["family_capabilities"]

        self.assertEqual(shaft_offering["part_family"], "shaft")
        self.assertEqual(shaft_offering["service_category"], "precision_shafts")
        self.assertIn("outer_diameter_mm", family_capabilities)
        for gear_field in ["outside_diameter_mm", "module", "diametral_pitch", "gear_quality"]:
            self.assertNotIn(gear_field, family_capabilities)

    def test_tasowheel_represents_new_confirmed_part_types_without_unsupported_types(self):
        gear_offering, shaft_offering = load_harmonized_provider("tasowheel")["offerings"]
        gear_part_types = {
            item["part_type"]
            for item in gear_offering["supported_part_types"]
        }
        shaft_part_types = {
            item["part_type"]
            for item in shaft_offering["supported_part_types"]
        }

        self.assertEqual(
            gear_part_types,
            {"spur_gear", "helical_gear", "bevel_gear", "worm_gear"},
        )
        self.assertEqual(
            shaft_part_types,
            {"splined_shaft", "plain_shaft", "hollow_shaft"},
        )
        self.assertNotIn("crown_gear", gear_part_types)
        self.assertNotIn("internal_gear", gear_part_types)
        self.assertNotIn("stepped_shaft", shaft_part_types)
        self.assertNotIn("worm_shaft", shaft_part_types)

    def test_tasowheel_corrected_shaft_modelling(self):
        shaft_offering = load_harmonized_provider("tasowheel")["offerings"][1]

        self.assertIn("length_mm", shaft_offering["family_capabilities"])
        self.assertEqual(
            shaft_offering["family_capabilities"]["length_mm"]["source_type"],
            "public_web",
        )
        self.assertIn("outer_diameter_mm", shaft_offering["family_capabilities"])
        self.assertIn(
            "spline_module",
            shaft_offering["part_type_capabilities"]["splined_shaft"],
        )
        for deferred_field in [
            "module",
            "diametral_pitch",
            "gear_quality",
            "spline_diametral_pitch",
            "shaft_quality",
            "spline_quality",
            "tolerance_mm",
        ]:
            self.assertNotIn(deferred_field, shaft_offering["family_capabilities"])

    def test_tasowheel_contains_no_route_machine_or_price_fields(self):
        loaded = load_harmonized_provider("tasowheel")
        keys = {key for key, _value in iter_nested_values(loaded)}

        self.assertFalse(FORBIDDEN_PUBLICATION_KEYS & keys)

    def test_tasowheel_material_grades_are_only_nested_material_evidence(self):
        loaded = load_harmonized_provider("tasowheel")

        for forbidden_key in ["material_grades", "supported_material_grades"]:
            keys = {key for key, _value in iter_nested_values(loaded)}
            self.assertNotIn(forbidden_key, keys)

        for offering in loaded["offerings"]:
            materials = offering["generic_capabilities"]["materials"]
            self.assertEqual(
                materials[0]["available_grades"],
                ["18CrNiMo7-6", "16MnCr5", "20MnCr5"],
            )

    def test_tasowheel_processes_are_offering_capabilities_not_routes(self):
        for offering in load_harmonized_provider("tasowheel")["offerings"]:
            process_values = {
                item["process"]
                for item in offering["generic_capabilities"]["processes"]
            }
            self.assertEqual(
                process_values,
                {
                    "machining",
                    "hobbing",
                    "gear_shaping",
                    "deburring",
                    "hard_turning",
                    "grinding",
                    "tooth_grinding",
                    "gear_grinding",
                    "gear_cutting",
                    "surface_grinding",
                    "milling",
                    "turn_mill",
                },
            )
            self.assertTrue(
                all(
                    item["delivery_mode"] == "unspecified"
                    for item in offering["generic_capabilities"]["processes"]
                )
            )

    def test_demo_machining_yaml_equals_h2_normalized_fixture(self):
        self.assertEqual(
            load_harmonized_provider("demo_machining_provider"),
            normalize_fixture(demo_machining_payload()),
        )

    def test_demo_machining_maps_only_to_broad_precision_shafts(self):
        loaded = load_harmonized_provider("demo_machining_provider")
        offerings = loaded["offerings"]

        self.assertEqual(len(offerings), 1)
        self.assertEqual(offerings[0]["service_category"], "precision_shafts")
        self.assertEqual(offerings[0]["part_family"], "shaft")
        self.assertEqual(offerings[0]["supported_part_types"], [])

    def test_precipart_yaml_equals_h2_normalized_fixture(self):
        self.assertEqual(
            load_harmonized_provider("precipart"),
            normalize_fixture(precipart_payload()),
        )

    def test_precipart_preserves_candidate_crown_gear_status(self):
        loaded = load_harmonized_provider("precipart")
        supported_part_types = {
            item["part_type"]: item
            for item in loaded["offerings"][0]["supported_part_types"]
        }

        self.assertEqual(
            supported_part_types["crown_gear"]["support_status"],
            "candidate_requiring_confirmation",
        )
        self.assertEqual(loaded["offerings"][0]["part_type_capabilities"], {})

    def test_h3_data_directory_is_parallel_to_legacy_provider_directory(self):
        self.assertNotEqual(HARMONIZED_PROVIDER_DIR, LEGACY_PROVIDER_DIR)
        self.assertTrue(str(HARMONIZED_PROVIDER_DIR).endswith("service_discovery\\providers"))
        self.assertTrue(LEGACY_PROVIDER_DIR.exists())
        self.assertTrue((LEGACY_PROVIDER_DIR / "tasowheel.yaml").exists())
