
from django.test import SimpleTestCase

from apps.api.search_serializers import SearchRequestSerializer
from apps.ontology.rdf_generator import build_catalog_graph
from apps.providers.services import clear_seed_cache
from apps.search.normalizer import normalize_search_request
from apps.search.query_builder import (
    SparqlQueryBuildError,
    build_candidate_evidence_query,
    build_part_family_search_query,
    build_values_clause,
    get_part_family_concepts,
)


def make_canonical_request(payload: dict):
    """
    Build a CanonicalSearchRequest from the same serializer/normalizer path
    used by the real API.
    """
    serializer = SearchRequestSerializer(data=payload)

    assert serializer.is_valid(), serializer.errors

    return normalize_search_request(
        serializer.validated_data,
        warnings=getattr(serializer, "unsupported_field_warnings", []),
    )


def rdf_row_to_dict(row) -> dict:
    """
    Convert one RDFLib SPARQL row into an easier Python dictionary.
    """
    return {
        "provider_id": str(row.providerId),
        "provider_name": str(row.providerName),
        "offering_id": str(row.offeringId),
        "offering_name": str(row.offeringName),
        "matched_count": int(row.matchedPartFamilyCount),
        "matched_part_families": str(row.matchedPartFamilyUris),
        "materials": str(row.materialUris) if row.materialUris else "",
        "diameter_min": float(row.diameterMinMm) if row.diameterMinMm else None,
        "diameter_max": float(row.diameterMaxMm) if row.diameterMaxMm else None,
        "batch_min": int(row.batchMin) if row.batchMin else None,
        "batch_max": int(row.batchMax) if row.batchMax else None,
        "lead_time_min": (
            float(row.leadTimeMinWeeks) if row.leadTimeMinWeeks else None
        ),
        "lead_time_max": (
            float(row.leadTimeMaxWeeks) if row.leadTimeMaxWeeks else None
        ),
    }


class SparqlQueryBuilderTests(SimpleTestCase):
    def setUp(self):
        clear_seed_cache()

    def test_get_part_family_concepts_maps_known_values(self):
        concepts = get_part_family_concepts(["shaft", "gear"])

        self.assertEqual(
            concepts,
            ["Shaft", "Gear"],
        )

    def test_get_part_family_concepts_ignores_unknown_values(self):
        concepts = get_part_family_concepts(["shaft", "unknown_part"])

        self.assertEqual(
            concepts,
            ["Shaft"],
        )

    def test_build_values_clause_uses_mapped_concepts(self):
        values_clause = build_values_clause(
            variable_name="requestedPartFamily",
            concept_names=["Shaft", "Gear"],
        )

        self.assertIn("VALUES ?requestedPartFamily", values_clause)
        self.assertIn("mdc:Shaft", values_clause)
        self.assertIn("mdc:Gear", values_clause)

    def test_build_values_clause_rejects_empty_concepts(self):
        with self.assertRaises(SparqlQueryBuildError):
            build_values_clause(
                variable_name="requestedPartFamily",
                concept_names=[],
            )

    def test_part_family_query_contains_required_sparql_blocks_for_any_mode(self):
        canonical_request = make_canonical_request(
            {
                "part_families": ["shaft", "gear"],
                "match_policy": {
                    "primary_match_mode": "any",
                },
            }
        )

        query = build_part_family_search_query(canonical_request)

        self.assertIn("PREFIX mdc:", query)
        self.assertIn("SELECT", query)
        self.assertIn("VALUES ?requestedPartFamily", query)
        self.assertIn("mdc:Shaft", query)
        self.assertIn("mdc:Gear", query)
        self.assertIn("?offering a mdc:ProviderOffering", query)
        self.assertIn("mdc:supportsPartFamily ?requestedPartFamily", query)
        self.assertIn("mdc:providerId ?providerId", query)
        self.assertIn("mdc:offeringId ?offeringId", query)
        self.assertIn(
            "HAVING (COUNT(DISTINCT ?requestedPartFamily) > 0)",
            query,
        )

    def test_part_family_query_uses_all_mode_having_clause(self):
        canonical_request = make_canonical_request(
            {
                "part_families": ["shaft", "gear"],
                "match_policy": {
                    "primary_match_mode": "all",
                },
            }
        )

        query = build_part_family_search_query(canonical_request)

        self.assertIn(
            "HAVING (COUNT(DISTINCT ?requestedPartFamily) = 2)",
            query,
        )

    def test_candidate_evidence_query_contains_evidence_projection(self):
        canonical_request = make_canonical_request(
            {
                "part_families": ["shaft", "gear"],
                "match_policy": {
                    "primary_match_mode": "any",
                },
            }
        )

        query = build_candidate_evidence_query(canonical_request)

        self.assertIn("GROUP_CONCAT(DISTINCT STR(?material)", query)
        self.assertIn("AS ?materialUris", query)

        self.assertIn("mdc:supportsMaterial ?material", query)

        self.assertIn("mdc:diameterMinMm ?diameterMinMmValue", query)
        self.assertIn("mdc:diameterMaxMm ?diameterMaxMmValue", query)

        self.assertIn("mdc:batchMin ?batchMinValue", query)
        self.assertIn("mdc:batchMax ?batchMaxValue", query)

        self.assertIn("mdc:leadTimeMinWeeks ?leadTimeMinWeeksValue", query)
        self.assertIn("mdc:leadTimeMaxWeeks ?leadTimeMaxWeeksValue", query)

    def test_candidate_evidence_query_runs_against_generated_graph(self):
        canonical_request = make_canonical_request(
            {
                "part_families": ["shaft", "gear"],
                "match_policy": {
                    "primary_match_mode": "any",
                },
            }
        )

        query = build_candidate_evidence_query(canonical_request)

        graph = build_catalog_graph()
        rows = list(graph.query(query))

        self.assertGreaterEqual(len(rows), 1)

        row_dicts = [rdf_row_to_dict(row) for row in rows]

        offering_ids = {
            row["offering_id"]
            for row in row_dicts
        }

        self.assertIn(
            "tasowheel_gears_shafts_precision",
            offering_ids,
        )

    def test_candidate_evidence_query_returns_tasowheel_capability_evidence(self):
        canonical_request = make_canonical_request(
            {
                "part_families": ["shaft", "gear"],
                "match_policy": {
                    "primary_match_mode": "any",
                },
            }
        )

        query = build_candidate_evidence_query(canonical_request)

        graph = build_catalog_graph()
        rows = list(graph.query(query))
        row_dicts = [rdf_row_to_dict(row) for row in rows]

        tasowheel_row = next(
            row
            for row in row_dicts
            if row["offering_id"] == "tasowheel_gears_shafts_precision"
        )

        self.assertEqual(tasowheel_row["provider_id"], "tasowheel")
        self.assertEqual(tasowheel_row["provider_name"], "Tasowheel Oy")

        self.assertEqual(tasowheel_row["matched_count"], 2)

        self.assertIn("Shaft", tasowheel_row["matched_part_families"])
        self.assertIn("Gear", tasowheel_row["matched_part_families"])

        self.assertIn("Steel", tasowheel_row["materials"])
        self.assertIn("AlloyedCarburizingSteel", tasowheel_row["materials"])

        self.assertEqual(tasowheel_row["diameter_min"], 10.0)
        self.assertEqual(tasowheel_row["diameter_max"], 450.0)

        self.assertEqual(tasowheel_row["batch_min"], 100)
        self.assertEqual(tasowheel_row["batch_max"], 2000)

        self.assertEqual(tasowheel_row["lead_time_min"], 8.0)
        self.assertEqual(tasowheel_row["lead_time_max"], 12.0)

    def test_candidate_evidence_query_all_mode_returns_only_complete_part_family_matches(self):
        canonical_request = make_canonical_request(
            {
                "part_families": ["shaft", "gear"],
                "match_policy": {
                    "primary_match_mode": "all",
                },
            }
        )

        query = build_candidate_evidence_query(canonical_request)

        graph = build_catalog_graph()
        rows = list(graph.query(query))
        row_dicts = [rdf_row_to_dict(row) for row in rows]

        self.assertGreaterEqual(len(row_dicts), 1)

        for row in row_dicts:
            self.assertEqual(row["matched_count"], 2)

        offering_ids = {
            row["offering_id"]
            for row in row_dicts
        }

        self.assertIn(
            "tasowheel_gears_shafts_precision",
            offering_ids,
        )

    def test_candidate_evidence_query_any_mode_can_return_partial_primary_matches(self):
        canonical_request = make_canonical_request(
            {
                "part_families": ["shaft", "gear"],
                "match_policy": {
                    "primary_match_mode": "any",
                },
            }
        )

        query = build_candidate_evidence_query(canonical_request)

        graph = build_catalog_graph()
        rows = list(graph.query(query))
        row_dicts = [rdf_row_to_dict(row) for row in rows]

        self.assertTrue(
            any(row["matched_count"] == 1 for row in row_dicts)
        )