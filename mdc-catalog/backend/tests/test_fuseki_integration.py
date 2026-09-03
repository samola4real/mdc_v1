
import socket
from urllib.parse import urlparse

from django.conf import settings
from django.test import SimpleTestCase, override_settings
from apps.search.fuseki_search_service import search_fuseki_candidates
from apps.api.search_serializers import SearchRequestSerializer
from apps.search.normalizer import normalize_search_request
from apps.search.query_builder import build_candidate_evidence_query
from apps.search.sparql_client import (
    binding_value,
    execute_select_query,
    get_bindings,
)


def is_fuseki_port_open() -> bool:
    """
    Return True if the configured Fuseki host/port is reachable.

    This allows integration tests to skip cleanly when Fuseki is not running.
    """
    endpoint = settings.FUSEKI_QUERY_ENDPOINT
    parsed_url = urlparse(endpoint)

    host = parsed_url.hostname
    port = parsed_url.port

    if not host:
        return False

    if port is None:
        port = 443 if parsed_url.scheme == "https" else 80

    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True

    except OSError:
        return False


def make_canonical_request(payload: dict):
    """
    Build a CanonicalSearchRequest using the same serializer/normalizer
    path used by the API.
    """
    serializer = SearchRequestSerializer(data=payload)

    assert serializer.is_valid(), serializer.errors

    return normalize_search_request(
        serializer.validated_data,
        warnings=getattr(serializer, "unsupported_field_warnings", []),
    )


def optional_float(value):
    if value is None:
        return None

    return float(value)


def optional_int(value):
    if value is None:
        return None

    return int(float(value))


def bindings_to_rows(bindings: list[dict]) -> list[dict]:
    """
    Convert SPARQL JSON bindings into simple dictionaries.
    """
    return [
        {
            "provider_id": binding_value(binding, "providerId"),
            "provider_name": binding_value(binding, "providerName"),
            "offering_id": binding_value(binding, "offeringId"),
            "offering_name": binding_value(binding, "offeringName"),
            "matched_count": binding_value(binding, "matchedPartFamilyCount"),
            "matched_part_families": binding_value(binding, "matchedPartFamilyUris"),
            "materials": binding_value(binding, "materialUris"),
            "diameter_min": optional_float(binding_value(binding, "diameterMinMm")),
            "diameter_max": optional_float(binding_value(binding, "diameterMaxMm")),
            "batch_min": optional_int(binding_value(binding, "batchMin")),
            "batch_max": optional_int(binding_value(binding, "batchMax")),
            "lead_time_min": optional_float(binding_value(binding, "leadTimeMinWeeks")),
            "lead_time_max": optional_float(binding_value(binding, "leadTimeMaxWeeks")),
        }
        for binding in bindings
    ]


def test_search_fuseki_candidates_returns_normalized_tasowheel_candidate(self):
    canonical_request = make_canonical_request(
        {
            "part_families": ["shaft", "gear"],
            "match_policy": {
                "primary_match_mode": "any",
            },
        }
    )

    rows = search_fuseki_candidates(canonical_request)

    offering_ids = {
        row["offering"]["offering_id"]
        for row in rows
    }

    self.assertIn(
        "tasowheel_gears_shafts_precision",
        offering_ids,
    )

    tasowheel_row = next(
        row
        for row in rows
        if row["offering"]["offering_id"] == "tasowheel_gears_shafts_precision"
    )

    self.assertEqual(
        tasowheel_row["provider"]["provider_id"],
        "tasowheel",
    )
    self.assertEqual(
        tasowheel_row["primary_match"]["matched_part_family_count"],
        2,
    )
    self.assertIn(
        "Shaft",
        tasowheel_row["primary_match"]["matched_part_families"],
    )
    self.assertIn(
        "Gear",
        tasowheel_row["primary_match"]["matched_part_families"],
    )
    self.assertIn(
        "Steel",
        tasowheel_row["evidence"]["materials"],
    )
    self.assertEqual(
        tasowheel_row["evidence"]["diameter_mm"]["min"],
        10.0,
    )
    self.assertEqual(
        tasowheel_row["evidence"]["diameter_mm"]["max"],
        450.0,
    )
    self.assertEqual(
        tasowheel_row["evidence"]["batch_size"]["min"],
        100,
    )
    self.assertEqual(
        tasowheel_row["evidence"]["batch_size"]["max"],
        2000,
    )
    self.assertEqual(
        tasowheel_row["evidence"]["lead_time_weeks"]["min"],
        8.0,
    )
    self.assertEqual(
        tasowheel_row["evidence"]["lead_time_weeks"]["max"],
        12.0,
    )

@override_settings(FUSEKI_TIMEOUT_SECONDS=2.0)
class FusekiIntegrationTests(SimpleTestCase):
    """
    Optional integration tests for local Fuseki.

    These tests are skipped when Fuseki is not running.

    They should pass when:
    - Fuseki is running
    - dataset /mdc exists
    - data/generated/mdc_catalog.ttl has been uploaded to /mdc/data
    """

    def setUp(self):
        if not is_fuseki_port_open():
            self.skipTest(
                "Fuseki is not running. Skipping optional Fuseki integration tests."
            )

    def test_fuseki_provider_query_returns_tasowheel(self):
        query = """
        PREFIX mdc: <https://maasai-project.eu/ontology/mdc#>

        SELECT ?providerId ?providerName
        WHERE {
            ?provider a mdc:MaaSProvider ;
                mdc:providerId ?providerId ;
                mdc:displayName ?providerName .
        }
        """

        result = execute_select_query(query)
        bindings = get_bindings(result)

        rows = [
            {
                "provider_id": binding_value(binding, "providerId"),
                "provider_name": binding_value(binding, "providerName"),
            }
            for binding in bindings
        ]

        self.assertIn(
            {
                "provider_id": "tasowheel",
                "provider_name": "Tasowheel Oy",
            },
            rows,
        )

    def test_candidate_evidence_query_any_mode_returns_tasowheel_evidence(self):
        canonical_request = make_canonical_request(
            {
                "part_families": ["shaft", "gear"],
                "match_policy": {
                    "primary_match_mode": "any",
                },
            }
        )

        query = build_candidate_evidence_query(canonical_request)

        result = execute_select_query(query)
        bindings = get_bindings(result)
        rows = bindings_to_rows(bindings)

        offering_ids = {
            row["offering_id"]
            for row in rows
        }

        self.assertIn(
            "tasowheel_gears_shafts_precision",
            offering_ids,
        )

        tasowheel_row = next(
            row
            for row in rows
            if row["offering_id"] == "tasowheel_gears_shafts_precision"
        )

        self.assertEqual(tasowheel_row["provider_id"], "tasowheel")
        self.assertEqual(tasowheel_row["provider_name"], "Tasowheel Oy")
        self.assertEqual(tasowheel_row["matched_count"], "2")

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

    def test_candidate_evidence_query_all_mode_returns_only_complete_primary_matches(self):
        canonical_request = make_canonical_request(
            {
                "part_families": ["shaft", "gear"],
                "match_policy": {
                    "primary_match_mode": "all",
                },
            }
        )

        query = build_candidate_evidence_query(canonical_request)

        result = execute_select_query(query)
        bindings = get_bindings(result)
        rows = bindings_to_rows(bindings)

        self.assertGreaterEqual(len(rows), 1)

        for row in rows:
            self.assertEqual(row["matched_count"], "2")

        offering_ids = {
            row["offering_id"]
            for row in rows
        }

        self.assertIn(
            "tasowheel_gears_shafts_precision",
            offering_ids,
        )

    def test_candidate_evidence_query_single_shaft_returns_tasowheel(self):
        canonical_request = make_canonical_request(
            {
                "part_families": ["shaft"],
            }
        )

        query = build_candidate_evidence_query(canonical_request)

        result = execute_select_query(query)
        bindings = get_bindings(result)
        rows = bindings_to_rows(bindings)

        offering_ids = {
            row["offering_id"]
            for row in rows
        }

        self.assertIn(
            "tasowheel_gears_shafts_precision",
            offering_ids,
        )
