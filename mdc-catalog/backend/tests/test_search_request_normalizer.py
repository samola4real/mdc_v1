from django.test import SimpleTestCase

from apps.api.search_serializers import SearchRequestSerializer
from apps.search.normalizer import normalize_search_request


def make_valid_search_payload() -> dict:
    return {
        "part_family": "shaft",
        "materials": ["nickel_alloy"],
        "dimensions": {
            "diameter_mm": {
                "exact": 50,
            }
        },
        "match_policy": {
            "primary_match_mode": "any",
            "optional_match_mode": "any",
            "unknown_policy": "keep_as_unknown",
            "minimum_score": 0.3,
        },
    }


def get_canonical_request(payload: dict):
    serializer = SearchRequestSerializer(data=payload)

    assert serializer.is_valid(), serializer.errors

    return normalize_search_request(
        serializer.validated_data,
        warnings=getattr(serializer, "unsupported_field_warnings", []),
    )


class SearchRequestNormalizerTests(SimpleTestCase):
    def test_normalizer_returns_primary_part_family_filter(self):
        canonical_request = get_canonical_request(make_valid_search_payload())

        data = canonical_request.to_dict()

        self.assertEqual(
            data["primary_filters"],
            {
                "part_families": ["shaft"],
            },
        )

    def test_normalizer_accepts_part_families_payload(self):
        payload = {
            "part_families": ["shaft", "gear"],
            "match_policy": {
                "primary_match_mode": "any",
                "optional_match_mode": "any",
                "unknown_policy": "keep_as_unknown",
            },
        }

        canonical_request = get_canonical_request(payload)

        data = canonical_request.to_dict()

        self.assertEqual(
            data["primary_filters"]["part_families"],
            ["shaft", "gear"],
        )

    def test_normalizer_merges_part_family_and_part_families(self):
        payload = {
            "part_family": "shaft",
            "part_families": ["gear"],
            "match_policy": {
                "primary_match_mode": "any",
                "optional_match_mode": "any",
                "unknown_policy": "keep_as_unknown",
            },
        }

        canonical_request = get_canonical_request(payload)

        data = canonical_request.to_dict()

        self.assertEqual(
            data["primary_filters"]["part_families"],
            ["shaft", "gear"],
        )

    def test_normalizer_returns_optional_material_and_diameter_criteria(self):
        canonical_request = get_canonical_request(make_valid_search_payload())

        data = canonical_request.to_dict()

        self.assertEqual(
            data["optional_criteria"]["materials"],
            ["nickel_alloy"],
        )
        self.assertEqual(
            data["optional_criteria"]["dimensions"]["diameter_mm"]["exact"],
            50,
        )

    def test_normalizer_returns_match_policy_defaults_when_absent(self):
        payload = {
            "part_family": "shaft",
        }

        canonical_request = get_canonical_request(payload)

        data = canonical_request.to_dict()

        self.assertEqual(
            data["match_policy"]["primary_match_mode"],
            "any",
        )
        self.assertEqual(
            data["match_policy"]["optional_match_mode"],
            "any",
        )
        self.assertEqual(
            data["match_policy"]["unknown_policy"],
            "keep_as_unknown",
        )
        self.assertIsNone(data["match_policy"]["minimum_score"])

    def test_normalizer_preserves_primary_match_mode_all(self):
        payload = {
            "part_families": ["shaft", "gear"],
            "match_policy": {
                "primary_match_mode": "all",
            },
        }

        canonical_request = get_canonical_request(payload)

        data = canonical_request.to_dict()

        self.assertEqual(
            data["match_policy"]["primary_match_mode"],
            "all",
        )

    def test_normalizer_does_not_include_empty_optional_fields(self):
        payload = {
            "part_family": "shaft",
            "materials": [],
            "processes": [],
            "dimensions": {},
            "weight_kg": {},
            "gear_parameters": {},
            "surface_finish": {},
            "delivery": {},
            "certifications": [],
            "traceability_required": False,
        }

        canonical_request = get_canonical_request(payload)

        data = canonical_request.to_dict()

        self.assertEqual(data["optional_criteria"], {})

    def test_normalizer_includes_service_type_when_supplied(self):
        payload = {
            "part_family": "shaft",
            "service_type": "shaft_manufacturing",
        }

        canonical_request = get_canonical_request(payload)

        data = canonical_request.to_dict()

        self.assertEqual(
            data["optional_criteria"]["service_type"],
            "shaft_manufacturing",
        )

    def test_normalizer_includes_processes_when_supplied(self):
        payload = {
            "part_family": "shaft",
            "processes": ["turning", "grinding"],
        }

        canonical_request = get_canonical_request(payload)

        data = canonical_request.to_dict()

        self.assertEqual(
            data["optional_criteria"]["processes"],
            ["turning", "grinding"],
        )

    def test_normalizer_includes_batch_size_when_supplied(self):
        payload = {
            "part_family": "shaft",
            "batch_size": 100,
        }

        canonical_request = get_canonical_request(payload)

        data = canonical_request.to_dict()

        self.assertEqual(
            data["optional_criteria"]["batch_size"],
            100,
        )

    def test_normalizer_includes_traceability_only_when_true(self):
        payload = {
            "part_family": "shaft",
            "traceability_required": True,
        }

        canonical_request = get_canonical_request(payload)

        data = canonical_request.to_dict()

        self.assertTrue(data["optional_criteria"]["traceability_required"])

    def test_normalizer_preserves_unsupported_field_warnings(self):
        payload = {
            "part_family": "shaft",
            "route_steps": ["turning", "grinding"],
        }

        serializer = SearchRequestSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        canonical_request = normalize_search_request(
            serializer.validated_data,
            warnings=serializer.unsupported_field_warnings,
        )

        data = canonical_request.to_dict()

        self.assertEqual(len(data["warnings"]), 1)
        self.assertEqual(data["warnings"][0]["field"], "route_steps")

    def test_normalizer_supports_shaft_and_material_or_diameter_shape(self):
        payload = {
            "part_families": ["shaft"],
            "materials": ["nickel_alloy"],
            "dimensions": {
                "diameter_mm": {
                    "exact": 50,
                }
            },
            "match_policy": {
                "primary_match_mode": "any",
                "optional_match_mode": "any",
            },
        }

        canonical_request = get_canonical_request(payload)

        data = canonical_request.to_dict()

        self.assertEqual(data["primary_filters"]["part_families"], ["shaft"])
        self.assertEqual(
            data["optional_criteria"]["materials"],
            ["nickel_alloy"],
        )
        self.assertEqual(
            data["optional_criteria"]["dimensions"]["diameter_mm"]["exact"],
            50,
        )
        self.assertEqual(
            data["match_policy"]["primary_match_mode"],
            "any",
        )
        self.assertEqual(
            data["match_policy"]["optional_match_mode"],
            "any",
        )