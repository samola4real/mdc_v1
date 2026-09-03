from django.test import SimpleTestCase

from apps.search.fuseki_search_service import (
    normalize_candidate_binding,
    optional_float,
    optional_int,
    split_uri_list,
    uri_fragment,
    uri_list_fragments,
)


def make_literal(value):
    return {
        "type": "literal",
        "value": value,
    }


def make_uri(value):
    return {
        "type": "uri",
        "value": value,
    }


class FusekiSearchServiceUnitTests(SimpleTestCase):
    def test_optional_float_converts_values(self):
        self.assertEqual(optional_float("10"), 10.0)
        self.assertEqual(optional_float("10.5"), 10.5)
        self.assertIsNone(optional_float(None))

    def test_optional_int_converts_values(self):
        self.assertEqual(optional_int("100"), 100)
        self.assertEqual(optional_int("100.0"), 100)
        self.assertIsNone(optional_int(None))

    def test_split_uri_list_handles_empty_values(self):
        self.assertEqual(split_uri_list(None), [])
        self.assertEqual(split_uri_list(""), [])

    def test_split_uri_list_splits_group_concat_value(self):
        value = (
            "https://maasai-project.eu/ontology/mdc#Shaft,"
            "https://maasai-project.eu/ontology/mdc#Gear"
        )

        self.assertEqual(
            split_uri_list(value),
            [
                "https://maasai-project.eu/ontology/mdc#Shaft",
                "https://maasai-project.eu/ontology/mdc#Gear",
            ],
        )

    def test_uri_fragment_returns_hash_fragment(self):
        self.assertEqual(
            uri_fragment("https://maasai-project.eu/ontology/mdc#Shaft"),
            "Shaft",
        )

    def test_uri_list_fragments_returns_readable_values(self):
        value = (
            "https://maasai-project.eu/ontology/mdc#Steel,"
            "https://maasai-project.eu/ontology/mdc#AlloyedCarburizingSteel"
        )

        self.assertEqual(
            uri_list_fragments(value),
            [
                "Steel",
                "AlloyedCarburizingSteel",
            ],
        )

    def test_normalize_candidate_binding_returns_candidate_row(self):
        binding = {
            "providerId": make_literal("tasowheel"),
            "providerName": make_literal("Tasowheel Oy"),
            "offeringId": make_literal("tasowheel_gears_shafts_precision"),
            "offeringName": make_literal("High-quality gears and shafts"),
            "matchedPartFamilyCount": make_literal("2"),
            "matchedPartFamilyUris": make_literal(
                "https://maasai-project.eu/ontology/mdc#Shaft,"
                "https://maasai-project.eu/ontology/mdc#Gear"
            ),
            "materialUris": make_literal(
                "https://maasai-project.eu/ontology/mdc#Steel,"
                "https://maasai-project.eu/ontology/mdc#AlloyedCarburizingSteel"
            ),
            "diameterMinMm": make_literal("10.0"),
            "diameterMaxMm": make_literal("450.0"),
            "batchMin": make_literal("100"),
            "batchMax": make_literal("2000"),
            "leadTimeMinWeeks": make_literal("8.0"),
            "leadTimeMaxWeeks": make_literal("12.0"),
        }

        row = normalize_candidate_binding(binding)

        self.assertEqual(row["provider"]["provider_id"], "tasowheel")
        self.assertEqual(row["provider"]["display_name"], "Tasowheel Oy")

        self.assertEqual(
            row["offering"]["offering_id"],
            "tasowheel_gears_shafts_precision",
        )
        self.assertEqual(
            row["offering"]["name"],
            "High-quality gears and shafts",
        )

        self.assertEqual(
            row["primary_match"]["matched_part_family_count"],
            2,
        )
        self.assertEqual(
            row["primary_match"]["matched_part_families"],
            ["Shaft", "Gear"],
        )

        self.assertEqual(
            row["evidence"]["materials"],
            ["Steel", "AlloyedCarburizingSteel"],
        )
        self.assertEqual(row["evidence"]["diameter_mm"]["min"], 10.0)
        self.assertEqual(row["evidence"]["diameter_mm"]["max"], 450.0)
        self.assertEqual(row["evidence"]["batch_size"]["min"], 100)
        self.assertEqual(row["evidence"]["batch_size"]["max"], 2000)
        self.assertEqual(row["evidence"]["lead_time_weeks"]["min"], 8.0)
        self.assertEqual(row["evidence"]["lead_time_weeks"]["max"], 12.0)

    def test_normalize_candidate_binding_preserves_missing_optional_values(self):
        binding = {
            "providerId": make_literal("demo_heat_treatment_provider"),
            "providerName": make_literal("Demo Heat Treatment Provider"),
            "offeringId": make_literal("demo_heat_treatment_provider_heat_treatment"),
            "offeringName": make_literal("Demo heat treatment service"),
            "matchedPartFamilyCount": make_literal("2"),
            "matchedPartFamilyUris": make_literal(
                "https://maasai-project.eu/ontology/mdc#Shaft,"
                "https://maasai-project.eu/ontology/mdc#Gear"
            ),
            "materialUris": make_literal(
                "https://maasai-project.eu/ontology/mdc#Steel"
            ),
            "leadTimeMinWeeks": make_literal("2.0"),
            "leadTimeMaxWeeks": make_literal("6.0"),
        }

        row = normalize_candidate_binding(binding)

        self.assertEqual(
            row["offering"]["offering_id"],
            "demo_heat_treatment_provider_heat_treatment",
        )

        self.assertIsNone(row["evidence"]["diameter_mm"]["min"])
        self.assertIsNone(row["evidence"]["diameter_mm"]["max"])
        self.assertIsNone(row["evidence"]["batch_size"]["min"])
        self.assertIsNone(row["evidence"]["batch_size"]["max"])

        self.assertEqual(row["evidence"]["lead_time_weeks"]["min"], 2.0)
        self.assertEqual(row["evidence"]["lead_time_weeks"]["max"], 6.0)