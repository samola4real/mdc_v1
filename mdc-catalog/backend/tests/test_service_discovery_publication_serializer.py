from copy import deepcopy

from django.test import SimpleTestCase

from apps.api.service_discovery_publication_serializers import (
    ServiceDiscoveryPublicationSerializer,
)


def make_valid_family_level_gears_payload() -> dict:
    return {
        "provider_id": "tasowheel",
        "provider_name": "Tasowheel Oy",
        "country": "Finland",
        "certifications": [
            {
                "code": "ISO9001_2015",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            }
        ],
        "offerings": [
            {
                "service_category": "precision_gears",
                "offering_name": "Precision gears",
                "part_family": "gear",
                "support_status": "confirmed",
                "supported_part_types": [],
                "family_capabilities": {
                    "module": {
                        "min": 0.3,
                        "max": 10,
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    },
                    "diametral_pitch": {
                        "min": 2.5,
                        "max": 85,
                        "raw": "DP 85-2.5",
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    },
                    "outside_diameter_mm": {
                        "min": 10,
                        "max": 450,
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    },
                    "gear_quality": {
                        "standard": "DIN",
                        "best_class": 4,
                        "comparison_rule": "lower_or_equal_is_better",
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    },
                },
                "generic_capabilities": {
                    "materials": [
                        {
                            "material": "alloyed_carburizing_steel",
                            "available_grades": [
                                "18CrNiMo7-6",
                                "16MnCr5",
                                "20MnCr5",
                            ],
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        }
                    ],
                    "batch_size": {
                        "min": 100,
                        "max": 2000,
                        "unit": "pcs",
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    },
                    "lead_time_weeks": {
                        "min": 8,
                        "max": 12,
                        "qualifier": "normal_case_dependent",
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    },
                    "weight_kg": {
                        "max": 200,
                        "approximate": True,
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    },
                },
            }
        ],
    }


def make_valid_bracket_payload() -> dict:
    return {
        "provider_id": "example_provider",
        "provider_name": "Example Provider",
        "country": "Finland",
        "offerings": [
            {
                "service_category": "precision_metal_parts",
                "offering_name": "Precision metal parts",
                "part_family": "metal_part",
                "support_status": "confirmed",
                "supported_part_types": [
                    {
                        "part_type": "bracket",
                        "support_status": "confirmed",
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    }
                ],
                "part_type_capabilities": {
                    "bracket": {
                        "bounding_box_mm": {
                            "length_mm": {"max": 160},
                            "width_mm": {"max": 80},
                            "height_mm": {"max": 70},
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        },
                        "vertical_flange_length_mm": {
                            "max": 70,
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        },
                        "horizontal_flange_length_mm": {
                            "max": 120,
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        },
                    }
                },
            }
        ],
    }


def is_valid(payload: dict) -> bool:
    return ServiceDiscoveryPublicationSerializer(data=payload).is_valid()


class ServiceDiscoveryPublicationSerializerTests(SimpleTestCase):
    def test_valid_family_level_precision_gears_publication_is_accepted(self):
        payload = make_valid_family_level_gears_payload()

        serializer = ServiceDiscoveryPublicationSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_provider_id_accepts_lower_snake_case_values(self):
        for provider_id in ["tasowheel", "example_provider_01"]:
            payload = make_valid_family_level_gears_payload()
            payload["provider_id"] = provider_id

            serializer = ServiceDiscoveryPublicationSerializer(data=payload)

            self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_provider_id_rejects_non_lower_snake_case_values(self):
        for provider_id in ["TasoWheel", "taso-wheel", "taso wheel"]:
            payload = make_valid_family_level_gears_payload()
            payload["provider_id"] = provider_id

            serializer = ServiceDiscoveryPublicationSerializer(data=payload)

            self.assertFalse(serializer.is_valid())
            self.assertIn("provider_id", serializer.errors)

    def test_supplied_valid_publication_metadata_is_accepted(self):
        payload = make_valid_family_level_gears_payload()
        payload["publication_metadata"] = {
            "source_type": "provider_confirmed",
            "confidence": "declared",
            "source_note": "Submitted through provider discovery form.",
        }

        serializer = ServiceDiscoveryPublicationSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_publication_metadata_defaults_are_applied(self):
        payload = make_valid_family_level_gears_payload()

        serializer = ServiceDiscoveryPublicationSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["publication_metadata"]["source_type"],
            "provider_confirmed",
        )
        self.assertEqual(
            serializer.validated_data["publication_metadata"]["confidence"],
            "declared",
        )

    def test_invalid_publication_metadata_source_type_is_rejected(self):
        payload = make_valid_family_level_gears_payload()
        payload["publication_metadata"] = {
            "source_type": "invented_source",
            "confidence": "declared",
        }

        serializer = ServiceDiscoveryPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("publication_metadata", str(serializer.errors))

    def test_invalid_publication_metadata_confidence_is_rejected(self):
        payload = make_valid_family_level_gears_payload()
        payload["publication_metadata"] = {
            "source_type": "provider_confirmed",
            "confidence": "invented_confidence",
        }

        serializer = ServiceDiscoveryPublicationSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("publication_metadata", str(serializer.errors))

    def test_valid_precision_gears_plus_precision_shafts_publication_is_accepted(self):
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

        self.assertTrue(is_valid(payload))

    def test_updated_tasowheel_publication_with_processes_and_shaft_modelling_is_accepted(self):
        processes = [
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
        shared_generic = {
            "processes": [
                {
                    "process": process,
                    "delivery_mode": "unspecified",
                    "source_type": "provider_confirmed",
                    "confidence": "declared",
                }
                for process in processes
            ],
            "materials": [
                {
                    "material": "alloyed_carburizing_steel",
                    "available_grades": ["18CrNiMo7-6", "16MnCr5", "20MnCr5"],
                    "source_type": "provider_confirmed",
                    "confidence": "declared",
                    "source_note": (
                        "Additional commonly used alloyed carburizing steels are supported, "
                        "but individual additional grades are not enumerated in the current evidence."
                    ),
                }
            ],
            "batch_size": {
                "min": 100,
                "max": 2000,
                "unit": "pcs",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            },
            "lead_time_weeks": {
                "min": 8,
                "max": 12,
                "qualifier": "normal_case_dependent",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            },
            "weight_kg": {
                "max": 200,
                "approximate": True,
                "source_type": "provider_confirmed",
                "confidence": "declared",
            },
        }
        payload = {
            "provider_id": "tasowheel",
            "provider_name": "Tasowheel Oy",
            "country": "Finland",
            "certifications": [
                {
                    "code": code,
                    "source_type": "provider_confirmed",
                    "confidence": "declared",
                }
                for code in [
                    "ISO9001_2015",
                    "ISO_TS_16949_partial",
                    "APQP",
                    "ISO14001_2015",
                ]
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
                    "family_capabilities": make_valid_family_level_gears_payload()[
                        "offerings"
                    ][0]["family_capabilities"],
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
                    "generic_capabilities": shared_generic,
                },
            ],
        }

        serializer = ServiceDiscoveryPublicationSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_valid_confirmed_bracket_publication_is_accepted(self):
        self.assertTrue(is_valid(make_valid_bracket_payload()))

    def test_provider_name_is_accepted(self):
        payload = make_valid_family_level_gears_payload()

        serializer = ServiceDiscoveryPublicationSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["provider_name"], "Tasowheel Oy")

    def test_external_display_name_is_rejected(self):
        payload = make_valid_family_level_gears_payload()
        payload["display_name"] = "Tasowheel Oy"

        self.assertFalse(is_valid(payload))

    def test_external_offering_id_is_rejected(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["offering_id"] = "tasowheel_precision_gears"

        self.assertFalse(is_valid(payload))

    def test_facility_material_and_grade_ids_are_rejected(self):
        for path, key, value in [
            ([], "facility_id", "tasowheel_main"),
            (
                ["offerings", 0, "generic_capabilities", "materials", 0],
                "material_id",
                "steel",
            ),
            (
                ["offerings", 0, "generic_capabilities", "materials", 0],
                "grade_id",
                "18CrNiMo7-6",
            ),
        ]:
            payload = make_valid_family_level_gears_payload()
            target = payload
            for part in path:
                target = target[part]
            target[key] = value

            self.assertFalse(is_valid(payload), key)

    def test_duplicate_service_categories_are_rejected(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"].append(deepcopy(payload["offerings"][0]))

        self.assertFalse(is_valid(payload))

    def test_service_category_and_part_family_mismatch_is_rejected(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["part_family"] = "shaft"

        self.assertFalse(is_valid(payload))

    def test_part_type_outside_selected_family_is_rejected(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["supported_part_types"] = [
            {
                "part_type": "bracket",
                "support_status": "confirmed",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            }
        ]

        self.assertFalse(is_valid(payload))

    def test_duplicate_supported_part_types_are_rejected(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["supported_part_types"] = [
            {
                "part_type": "spur_gear",
                "support_status": "confirmed",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            },
            {
                "part_type": "spur_gear",
                "support_status": "confirmed",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            },
        ]

        self.assertFalse(is_valid(payload))

    def test_gear_family_capability_accepts_outside_diameter(self):
        payload = make_valid_family_level_gears_payload()

        self.assertTrue(is_valid(payload))

    def test_gear_family_capability_rejects_diameter_mm(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["family_capabilities"]["diameter_mm"] = {
            "max": 300,
            "source_type": "provider_confirmed",
            "confidence": "declared",
        }

        self.assertFalse(is_valid(payload))

    def test_gear_family_capability_rejects_outer_diameter_mm(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["family_capabilities"]["outer_diameter_mm"] = {
            "max": 300,
            "source_type": "provider_confirmed",
            "confidence": "declared",
        }

        self.assertFalse(is_valid(payload))

    def test_shaft_family_capability_accepts_outer_diameter(self):
        payload = {
            "provider_id": "shaft_provider",
            "provider_name": "Shaft Provider",
            "country": "Finland",
            "offerings": [
                {
                    "service_category": "precision_shafts",
                    "offering_name": "Precision shafts",
                    "part_family": "shaft",
                    "support_status": "confirmed",
                    "family_capabilities": {
                        "outer_diameter_mm": {
                            "max": 120,
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        }
                    },
                }
            ],
        }

        self.assertTrue(is_valid(payload))

    def test_shaft_family_capability_rejects_outside_diameter(self):
        payload = {
            "provider_id": "shaft_provider",
            "provider_name": "Shaft Provider",
            "country": "Finland",
            "offerings": [
                {
                    "service_category": "precision_shafts",
                    "offering_name": "Precision shafts",
                    "part_family": "shaft",
                    "support_status": "confirmed",
                    "family_capabilities": {
                        "outside_diameter_mm": {
                            "max": 120,
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        }
                    },
                }
            ],
        }

        self.assertFalse(is_valid(payload))

    def test_metal_part_family_capabilities_must_be_empty(self):
        payload = make_valid_bracket_payload()
        payload["offerings"][0]["family_capabilities"] = {
            "bounding_box_mm": {
                "source_type": "provider_confirmed",
                "confidence": "declared",
            }
        }

        self.assertFalse(is_valid(payload))

    def test_confirmed_bracket_part_type_fields_are_accepted(self):
        self.assertTrue(is_valid(make_valid_bracket_payload()))

    def test_bracket_rejects_unrelated_module_field(self):
        payload = make_valid_bracket_payload()
        payload["offerings"][0]["part_type_capabilities"]["bracket"]["module"] = {
            "min": 1,
            "max": 3,
            "source_type": "provider_confirmed",
            "confidence": "declared",
        }

        self.assertFalse(is_valid(payload))

    def test_candidate_part_type_cannot_publish_numeric_capabilities(self):
        payload = make_valid_bracket_payload()
        payload["offerings"][0]["supported_part_types"][0][
            "support_status"
        ] = "candidate_requiring_confirmation"

        self.assertFalse(is_valid(payload))

    def test_material_grades_are_accepted_as_evidence_strings(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["generic_capabilities"]["materials"][0][
            "available_grades"
        ].append("42CrMo4")

        self.assertTrue(is_valid(payload))

    def test_grade_strings_are_not_constrained_to_legacy_public_filter_values(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["generic_capabilities"]["materials"][0][
            "available_grades"
        ] = ["42CrMo4"]

        self.assertTrue(is_valid(payload))

    def test_unknown_material_is_rejected(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["generic_capabilities"]["materials"][0][
            "material"
        ] = "unobtainium"

        self.assertFalse(is_valid(payload))

    def test_invalid_process_or_delivery_mode_is_rejected(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["generic_capabilities"]["processes"] = [
            {
                "process": "magic_cutting",
                "delivery_mode": "unspecified",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            }
        ]
        self.assertFalse(is_valid(payload))

        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["generic_capabilities"]["processes"] = [
            {
                "process": "hobbing",
                "delivery_mode": "onsite",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            }
        ]
        self.assertFalse(is_valid(payload))

    def test_negative_number_and_invalid_range_are_rejected(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["generic_capabilities"]["batch_size"]["max"] = -1
        self.assertFalse(is_valid(payload))

        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["generic_capabilities"]["batch_size"]["min"] = 20
        payload["offerings"][0]["generic_capabilities"]["batch_size"]["max"] = 10
        self.assertFalse(is_valid(payload))

    def test_forbidden_route_machine_price_keys_are_rejected_recursively(self):
        payload = make_valid_family_level_gears_payload()
        payload["offerings"][0]["part_type_capabilities"] = {
            "spur_gear": {
                "face_width_mm": {
                    "max": 80,
                    "route_steps": ["hobbing"],
                    "source_type": "provider_confirmed",
                    "confidence": "declared",
                }
            }
        }
        payload["offerings"][0]["supported_part_types"] = [
            {
                "part_type": "spur_gear",
                "support_status": "confirmed",
                "source_type": "provider_confirmed",
                "confidence": "declared",
            }
        ]

        self.assertFalse(is_valid(payload))
