from copy import deepcopy

from django.test import SimpleTestCase

from apps.api.service_discovery_search_serializers import (
    ServiceDiscoverySearchRequestSerializer,
)


def complete_spur_gear_request() -> dict:
    return {
        "request_id": "req_000001",
        "consumer_id": "consumer_001",
        "service_category": "precision_gears",
        "part_family": "gear",
        "part_type": "spur_gear",
        "requirements": {
            "part_family_specifications": {
                "module": {"exact": 2.0},
                "diametral_pitch": {"min": 10, "max": 20},
                "number_of_teeth": {"exact": 40},
                "outside_diameter_mm": {"max": 120},
                "gear_quality": {"standard": "DIN", "max_class": 5},
                "tolerance_mm": {"max": 0.02},
            },
            "part_type_specifications": {
                "face_width_mm": {"exact": 20},
            },
            "generic_requirements": {
                "materials": ["alloyed_carburizing_steel"],
                "processes": ["hobbing"],
                "batch_size": 500,
                "delivery": {"max_weeks": 12},
                "certifications": ["ISO9001_2015"],
            },
        },
        "match_policy": {
            "optional_match_mode": "any",
            "unknown_policy": "keep_as_unknown",
            "minimum_score": None,
        },
    }


def is_valid(payload: dict) -> bool:
    return ServiceDiscoverySearchRequestSerializer(data=payload).is_valid()


class ServiceDiscoverySearchRequestSerializerTests(SimpleTestCase):
    def test_valid_complete_spur_gear_request_is_accepted(self):
        serializer = ServiceDiscoverySearchRequestSerializer(
            data=complete_spur_gear_request()
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_valid_hollow_shaft_request_is_accepted(self):
        payload = {
            "request_id": "req_000002",
            "consumer_id": "consumer_001",
            "service_category": "precision_shafts",
            "part_family": "shaft",
            "part_type": "hollow_shaft",
            "requirements": {
                "part_family_specifications": {
                    "length_mm": {"max": 500},
                    "outer_diameter_mm": {"max": 60},
                    "tolerance_mm": {"max": 0.01},
                },
                "part_type_specifications": {
                    "inner_diameter_mm": {"min": 10},
                    "wall_thickness_mm": {"exact": 5},
                },
            },
        }

        self.assertTrue(is_valid(payload))

    def test_valid_bracket_request_accepts_generic_tolerance(self):
        payload = {
            "request_id": "req_000003",
            "consumer_id": "consumer_001",
            "service_category": "precision_metal_parts",
            "part_family": "metal_part",
            "part_type": "bracket",
            "requirements": {
                "part_family_specifications": {
                    "bounding_box_mm": {
                        "length_mm": {"max": 150},
                        "width_mm": {"max": 80},
                        "height_mm": {"max": 60},
                    }
                },
                "part_type_specifications": {
                    "vertical_flange_length_mm": {"max": 70},
                    "horizontal_flange_length_mm": {"max": 120},
                },
                "generic_requirements": {
                    "tolerance_mm": {"max": 0.05},
                },
            },
        }

        self.assertTrue(is_valid(payload))

    def test_minimal_request_defaults_requirements_and_match_policy(self):
        payload = {
            "request_id": "req_000004",
            "consumer_id": "consumer_001",
            "service_category": "precision_gears",
            "part_family": "gear",
            "part_type": "spur_gear",
        }
        serializer = ServiceDiscoverySearchRequestSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["requirements"],
            {
                "part_family_specifications": {},
                "part_type_specifications": {},
                "generic_requirements": {},
            },
        )
        self.assertEqual(
            serializer.validated_data["match_policy"],
            {
                "optional_match_mode": "any",
                "unknown_policy": "keep_as_unknown",
                "minimum_score": None,
            },
        )

    def test_required_metadata_and_selection_are_enforced(self):
        for field in ["request_id", "consumer_id"]:
            payload = complete_spur_gear_request()
            payload.pop(field)

            serializer = ServiceDiscoverySearchRequestSerializer(data=payload)

            self.assertFalse(serializer.is_valid(), field)
            self.assertIn(field, serializer.errors)

        for field in ["request_id", "consumer_id"]:
            payload = complete_spur_gear_request()
            payload[field] = ""

            self.assertFalse(is_valid(payload), field)

    def test_taxonomy_selection_rejections(self):
        payload = complete_spur_gear_request()
        payload["service_category"] = "unknown_category"
        self.assertFalse(is_valid(payload))

        payload = complete_spur_gear_request()
        payload["part_family"] = "shaft"
        self.assertFalse(is_valid(payload))

        payload = complete_spur_gear_request()
        payload["part_type"] = "hollow_shaft"
        self.assertFalse(is_valid(payload))

    def test_rejects_part_families_and_primary_match_mode(self):
        payload = complete_spur_gear_request()
        payload["part_families"] = ["gear"]
        self.assertFalse(is_valid(payload))

        payload = complete_spur_gear_request()
        payload["match_policy"]["primary_match_mode"] = "any"
        self.assertFalse(is_valid(payload))

    def test_spur_gear_family_fields_are_accepted_individually(self):
        for field, value in {
            "module": {"exact": 2.0},
            "diametral_pitch": {"min": 10, "max": 20},
            "number_of_teeth": {"exact": 40},
            "outside_diameter_mm": {"max": 120},
            "gear_quality": {"standard": "DIN", "max_class": 5},
            "tolerance_mm": {"max": 0.02},
        }.items():
            payload = complete_spur_gear_request()
            payload["requirements"]["part_family_specifications"] = {field: value}
            payload["requirements"]["part_type_specifications"] = {}

            self.assertTrue(is_valid(payload), field)

    def test_spur_gear_part_type_field_is_accepted(self):
        payload = complete_spur_gear_request()
        payload["requirements"]["part_family_specifications"] = {}
        payload["requirements"]["part_type_specifications"] = {
            "face_width_mm": {"exact": 20},
        }

        self.assertTrue(is_valid(payload))

    def test_spur_gear_rejects_invalid_or_wrong_group_fields(self):
        for field in ["diameter_mm", "outer_diameter_mm"]:
            payload = complete_spur_gear_request()
            payload["requirements"]["part_family_specifications"] = {field: {"max": 120}}
            payload["requirements"]["part_type_specifications"] = {}
            self.assertFalse(is_valid(payload), field)

        payload = complete_spur_gear_request()
        payload["requirements"]["part_family_specifications"] = {
            "face_width_mm": {"exact": 20}
        }
        payload["requirements"]["part_type_specifications"] = {}
        self.assertFalse(is_valid(payload))

        payload = complete_spur_gear_request()
        payload["requirements"]["part_family_specifications"] = {}
        payload["requirements"]["part_type_specifications"] = {
            "outside_diameter_mm": {"max": 120}
        }
        self.assertFalse(is_valid(payload))

    def test_scope_precedence_rejects_generic_tolerance_for_scoped_profiles(self):
        for service_category, part_family, part_type in [
            ("precision_gears", "gear", "spur_gear"),
            ("precision_shafts", "shaft", "hollow_shaft"),
            ("precision_metal_parts", "metal_part", "bushing"),
        ]:
            payload = {
                "request_id": "req_scope",
                "consumer_id": "consumer_001",
                "service_category": service_category,
                "part_family": part_family,
                "part_type": part_type,
                "requirements": {
                    "generic_requirements": {
                        "tolerance_mm": {"max": 0.02},
                    }
                },
            }
            self.assertFalse(is_valid(payload), part_type)

    def test_duplicate_field_across_requirement_groups_is_rejected(self):
        payload = complete_spur_gear_request()
        payload["requirements"]["generic_requirements"]["module"] = {"exact": 2}

        self.assertFalse(is_valid(payload))

    def test_hollow_shaft_field_scoping(self):
        payload = {
            "request_id": "req_shaft",
            "consumer_id": "consumer_001",
            "service_category": "precision_shafts",
            "part_family": "shaft",
            "part_type": "hollow_shaft",
            "requirements": {
                "part_family_specifications": {
                    "outer_diameter_mm": {"max": 60},
                    "tolerance_mm": {"max": 0.01},
                },
                "part_type_specifications": {
                    "inner_diameter_mm": {"min": 10},
                    "wall_thickness_mm": {"exact": 5},
                },
            },
        }
        self.assertTrue(is_valid(payload))

        payload["requirements"]["part_family_specifications"]["outside_diameter_mm"] = {
            "max": 70
        }
        self.assertFalse(is_valid(payload))

    def test_splined_shaft_accepts_spline_module_and_rejects_deferred_shaft_fields(self):
        payload = {
            "request_id": "req_splined",
            "consumer_id": "consumer_001",
            "service_category": "precision_shafts",
            "part_family": "shaft",
            "part_type": "splined_shaft",
            "requirements": {
                "part_family_specifications": {
                    "length_mm": {"max": 500},
                    "outer_diameter_mm": {"exact": 100},
                },
                "part_type_specifications": {
                    "spline_module": {"exact": 2},
                },
            },
        }
        self.assertTrue(is_valid(payload))

        for field in [
            "diametral_pitch",
            "gear_quality",
            "shaft_quality",
        ]:
            bad_payload = deepcopy(payload)
            bad_payload["requirements"]["part_family_specifications"][field] = (
                {"max": 5}
                if field != "gear_quality"
                else {"standard": "DIN", "max_class": 4}
            )
            self.assertFalse(is_valid(bad_payload), field)

        bad_payload = deepcopy(payload)
        bad_payload["requirements"]["part_type_specifications"][
            "spline_diametral_pitch"
        ] = {"max": 85}
        self.assertFalse(is_valid(bad_payload))

    def test_bracket_field_scoping(self):
        payload = {
            "request_id": "req_bracket",
            "consumer_id": "consumer_001",
            "service_category": "precision_metal_parts",
            "part_family": "metal_part",
            "part_type": "bracket",
            "requirements": {
                "part_family_specifications": {
                    "bounding_box_mm": {"length_mm": {"max": 150}},
                },
                "part_type_specifications": {
                    "vertical_flange_length_mm": {"max": 70},
                    "horizontal_flange_length_mm": {"max": 120},
                },
            },
        }
        self.assertTrue(is_valid(payload))

        payload["requirements"]["part_family_specifications"]["module"] = {"exact": 1}
        self.assertFalse(is_valid(payload))

    def test_bushing_scoped_diameter_and_flange_fields(self):
        payload = {
            "request_id": "req_bushing",
            "consumer_id": "consumer_001",
            "service_category": "precision_metal_parts",
            "part_family": "metal_part",
            "part_type": "bushing",
            "requirements": {
                "part_family_specifications": {
                    "inner_diameter_mm": {"min": 10},
                    "outer_diameter_mm": {"max": 50},
                    "overall_length_mm": {"max": 80},
                    "tolerance_mm": {"max": 0.02},
                },
                "part_type_specifications": {
                    "flange_diameter_mm": {"max": 70},
                },
            },
        }

        self.assertTrue(is_valid(payload))

    def test_generic_requirement_acceptance_and_rejection(self):
        payload = complete_spur_gear_request()
        self.assertTrue(is_valid(payload))

        payload = complete_spur_gear_request()
        payload["requirements"]["generic_requirements"]["material_grades"] = ["18CrNiMo7-6"]
        self.assertFalse(is_valid(payload))

        payload = complete_spur_gear_request()
        payload["requirements"]["generic_requirements"]["materials"] = ["unobtainium"]
        self.assertFalse(is_valid(payload))

        payload = complete_spur_gear_request()
        payload["requirements"]["generic_requirements"]["processes"] = ["magic_cutting"]
        self.assertFalse(is_valid(payload))

        payload = complete_spur_gear_request()
        payload["requirements"]["generic_requirements"]["certifications"] = ["BAD_CERT"]
        self.assertFalse(is_valid(payload))

    def test_generic_process_requirements_accept_updated_controlled_values(self):
        payload = complete_spur_gear_request()
        payload["requirements"]["generic_requirements"]["processes"] = [
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

        serializer = ServiceDiscoverySearchRequestSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_positive_generic_numeric_validation(self):
        payload = complete_spur_gear_request()
        payload["requirements"]["generic_requirements"]["batch_size"] = 1
        payload["requirements"]["generic_requirements"]["delivery"] = {"max_weeks": 1}
        payload["requirements"]["generic_requirements"]["weight_kg"] = 200
        payload["requirements"]["generic_requirements"]["surface_finish_ra_um"] = {"max": 3.2}
        payload["requirements"]["generic_requirements"]["quality"] = {
            "standard": "ISO",
            "max_class": 5,
        }
        self.assertTrue(is_valid(payload))

        for field, value in [
            ("batch_size", 0),
            ("delivery", {"max_weeks": 0}),
            ("weight_kg", 0),
        ]:
            payload = complete_spur_gear_request()
            payload["requirements"]["generic_requirements"][field] = value
            self.assertFalse(is_valid(payload), field)

    def test_range_or_exact_validation(self):
        for bad_value in [
            {},
            {"max": 0},
            {"min": 10, "max": 5},
            {"min": 10, "exact": 5},
            {"max": 10, "exact": 20},
            {"max": 10, "extra": 1},
        ]:
            payload = complete_spur_gear_request()
            payload["requirements"]["part_family_specifications"]["module"] = bad_value
            self.assertFalse(is_valid(payload), bad_value)

    def test_integer_fields_reject_decimal_values(self):
        payload = complete_spur_gear_request()
        payload["requirements"]["part_family_specifications"]["number_of_teeth"] = {
            "exact": 40.5
        }

        self.assertFalse(is_valid(payload))

    def test_bounding_box_validation(self):
        payload = {
            "request_id": "req_box",
            "consumer_id": "consumer_001",
            "service_category": "precision_metal_parts",
            "part_family": "metal_part",
            "part_type": "bracket",
            "requirements": {
                "part_family_specifications": {
                    "bounding_box_mm": {},
                }
            },
        }
        self.assertFalse(is_valid(payload))

        payload["requirements"]["part_family_specifications"]["bounding_box_mm"] = {
            "depth_mm": {"max": 10}
        }
        self.assertFalse(is_valid(payload))

    def test_unknown_and_forbidden_fields_are_rejected(self):
        payload = complete_spur_gear_request()
        payload["unexpected"] = True
        self.assertFalse(is_valid(payload))

        payload = complete_spur_gear_request()
        payload["requirements"]["unexpected_group"] = {}
        self.assertFalse(is_valid(payload))

        payload = complete_spur_gear_request()
        payload["requirements"]["generic_requirements"]["unknown"] = "value"
        self.assertFalse(is_valid(payload))

        payload = complete_spur_gear_request()
        payload["requirements"]["part_type_specifications"]["face_width_mm"][
            "route_steps"
        ] = ["hobbing"]
        self.assertFalse(is_valid(payload))
