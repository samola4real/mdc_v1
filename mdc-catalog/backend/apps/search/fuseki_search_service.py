from typing import Any

from apps.search.query_builder import build_candidate_evidence_query
from apps.search.request import CanonicalSearchRequest
from apps.search.sparql_client import (
    binding_value,
    execute_select_query,
    get_bindings,
)


def optional_float(value: Any) -> float | None:
    """
    Convert optional SPARQL literal value to float.

    Fuseki may return numeric literals as strings such as:
    - "10"
    - "10.0"

    OPTIONAL SPARQL fields may be absent, so None must remain None.
    """
    if value is None:
        return None

    return float(value)


def optional_int(value: Any) -> int | None:
    """
    Convert optional SPARQL literal value to int.

    Some integer-looking values may come back as "100" or "100.0".
    """
    if value is None:
        return None

    return int(float(value))


def split_uri_list(value: str | None) -> list[str]:
    """
    Convert GROUP_CONCAT URI string into a list.

    Example:
    "uri1,uri2" -> ["uri1", "uri2"]
    """
    if not value:
        return []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def uri_fragment(uri: str) -> str:
    """
    Return the fragment part from an RDF URI.

    Example:
    https://maasai-project.eu/ontology/mdc#Shaft -> Shaft
    """
    if "#" in uri:
        return uri.rsplit("#", 1)[-1]

    return uri.rsplit("/", 1)[-1]


def uri_list_fragments(value: str | None) -> list[str]:
    """
    Convert GROUP_CONCAT URI string into readable ontology fragments.
    """
    return [
        uri_fragment(uri)
        for uri in split_uri_list(value)
    ]


def normalize_candidate_binding(binding: dict[str, Any]) -> dict[str, Any]:
    """
    Convert one SPARQL JSON binding into a clean candidate row.

    This is still candidate/evidence data only.
    Final scoring and explanation remain separate.
    """
    matched_part_family_uris = binding_value(
        binding,
        "matchedPartFamilyUris",
    )
    material_uris = binding_value(
        binding,
        "materialUris",
    )

    return {
        "provider": {
            "provider_id": binding_value(binding, "providerId"),
            "display_name": binding_value(binding, "providerName"),
        },
        "offering": {
            "offering_id": binding_value(binding, "offeringId"),
            "name": binding_value(binding, "offeringName"),
        },
        "primary_match": {
            "matched_part_family_count": optional_int(
                binding_value(binding, "matchedPartFamilyCount")
            ),
            "matched_part_family_uris": split_uri_list(matched_part_family_uris),
            "matched_part_families": uri_list_fragments(matched_part_family_uris),
        },
        "evidence": {
            "material_uris": split_uri_list(material_uris),
            "materials": uri_list_fragments(material_uris),
            "diameter_mm": {
                "min": optional_float(binding_value(binding, "diameterMinMm")),
                "max": optional_float(binding_value(binding, "diameterMaxMm")),
            },
            "batch_size": {
                "min": optional_int(binding_value(binding, "batchMin")),
                "max": optional_int(binding_value(binding, "batchMax")),
            },
            "lead_time_weeks": {
                "min": optional_float(binding_value(binding, "leadTimeMinWeeks")),
                "max": optional_float(binding_value(binding, "leadTimeMaxWeeks")),
            },
        },
    }


def normalize_candidate_bindings(
    bindings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert all SPARQL JSON bindings into candidate rows.
    """
    return [
        normalize_candidate_binding(binding)
        for binding in bindings
    ]


def search_fuseki_candidates(
    canonical_request: CanonicalSearchRequest,
) -> list[dict[str, Any]]:
    """
    Run the candidate evidence query against Fuseki.

    This is not the final catalogue search yet.

    It returns candidate rows with RDF evidence, but does not yet build the final
    matched/unmatched/unknown response shape.
    """
    query = build_candidate_evidence_query(canonical_request)
    raw_result = execute_select_query(query)
    bindings = get_bindings(raw_result)

    return normalize_candidate_bindings(bindings)