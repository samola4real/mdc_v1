from django.test import SimpleTestCase

from apps.api.search_serializers import SearchRequestSerializer


def make_valid_search_payload() -> dict:
    return {
        "service_type": "gear_manufacturing",
        "part_family": "spur_gear",
        "materials": ["steel"],
        "material_grades": ["18CrNiMo7-6"],
        "processes": ["gear_grinding"],
        "dimensions": {
            "diameter_mm": {
                "max": 300,
            }
        },
        "weight_kg": {
            "max": 50,
        },
        "gear_parameters": {
            "module": {
                "min": 1,
                "max": 5,
            },
            "diametral_pitch": {
                "min": 5,
                "max": 40,
            },
            "quality": {
                "standard": "DIN",
                "max_class": 4,
            },
        },
        "surface_finish": {
            "ra_um": {
                "max": 1.6,
            }
        },
        "batch_size": 100,
        "delivery": {
            "max_weeks": 12,
        },
        "certifications": ["ISO9001_2015"],
        "traceability_required": False,
        "industry": "power_transmission",
        "match_policy": {
            "optional_match_mode": "any",
            "unknown_policy": "keep_as_unknown",
            "minimum_score": 0.5,
        },
    }


class SearchRequestSerializerTests(SimpleTestCase):
    def test_valid_search_request_is_accepted(self):
        payload = make_valid_search_payload()

        serializer = SearchRequestSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        self.assertEqual(
            serializer.validated_data["service_type"],
            "gear_manufacturing",
        )

    def test_part_family_is_required(self):
        payload = make_valid_search_payload()
        payload.pop("part_family")

        serializer = SearchRequestSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("part_family", serializer.errors)

    def test_invalid_service_type_is_rejected(self):
        payload = make_valid_search_payload()
        payload["service_type"] = "unknown_service"

        serializer = SearchRequestSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("service_type", serializer.errors)

    def test_invalid_material_is_rejected(self):
        payload = make_valid_search_payload()
        payload["materials"] = ["unobtainium"]

        serializer = SearchRequestSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("materials", serializer.errors)

    def test_invalid_process_is_rejected(self):
        payload = make_valid_search_payload()
        payload["processes"] = ["magic_cutting"]

        serializer = SearchRequestSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("processes", serializer.errors)

    def test_negative_diameter_is_rejected(self):
        payload = make_valid_search_payload()
        payload["dimensions"]["diameter_mm"]["max"] = -300

        serializer = SearchRequestSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("dimensions", serializer.errors)

    def test_invalid_module_range_is_rejected(self):
        payload = make_valid_search_payload()
        payload["gear_parameters"]["module"] = {
            "min": 5,
            "max": 1,
        }

        serializer = SearchRequestSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("gear_parameters", serializer.errors)

    def test_batch_size_must_be_positive(self):
        payload = make_valid_search_payload()
        payload["batch_size"] = 0

        serializer = SearchRequestSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("batch_size", serializer.errors)

    def test_minimum_score_must_be_between_zero_and_one(self):
        payload = make_valid_search_payload()
        payload["match_policy"]["minimum_score"] = 1.5

        serializer = SearchRequestSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("match_policy", serializer.errors)

    def test_route_fields_create_warning_but_do_not_fail_serializer(self):
        payload = make_valid_search_payload()
        payload["route_steps"] = ["turning", "milling"]

        serializer = SearchRequestSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(len(serializer.unsupported_field_warnings), 1)
        self.assertEqual(
            serializer.unsupported_field_warnings[0]["field"],
            "route_steps",
        )

    def test_service_type_is_optional(self):
        payload = make_valid_search_payload()
        payload.pop("service_type")

        serializer = SearchRequestSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["part_family"], "spur_gear")
    
    def test_exact_diameter_is_accepted(self):
        payload = make_valid_search_payload()
        payload["dimensions"]["diameter_mm"] = {
            "exact": 50,
        }

        serializer = SearchRequestSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["dimensions"]["diameter_mm"]["exact"],
            50,
        )


    def test_optional_match_mode_any_is_accepted(self):
        payload = make_valid_search_payload()
        payload["match_policy"]["optional_match_mode"] = "any"

        serializer = SearchRequestSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["match_policy"]["optional_match_mode"],
            "any",
        )

    def test_invalid_optional_match_mode_is_rejected(self):
        payload = make_valid_search_payload()
        payload["match_policy"]["optional_match_mode"] = "invalid_mode"

        serializer = SearchRequestSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("match_policy", serializer.errors)