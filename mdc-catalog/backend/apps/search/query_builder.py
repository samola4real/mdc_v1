
from apps.ontology.rdf_mappings import PART_FAMILY_CONCEPTS
from apps.search.request import CanonicalSearchRequest


MDC_PREFIX = "https://maasai-project.eu/ontology/mdc#"


class SparqlQueryBuildError(Exception):
    """
    Raised when a canonical search request cannot be converted into SPARQL.
    """


def get_part_family_concepts(part_families: list[str]) -> list[str]:
    """
    Convert controlled part-family values into ontology concept names.

    Example:
    shaft -> Shaft
    gear -> Gear

    This protects us from injecting raw user input into SPARQL.
    """
    concepts = []

    for part_family in part_families:
        concept = PART_FAMILY_CONCEPTS.get(part_family)

        if concept:
            concepts.append(concept)

    return concepts


def build_values_clause(
    *,
    variable_name: str,
    concept_names: list[str],
) -> str:
    """
    Build a deterministic SPARQL VALUES clause.

    Example:
    VALUES ?requestedPartFamily {
        mdc:Shaft
        mdc:Gear
    }
    """
    if not concept_names:
        raise SparqlQueryBuildError("Cannot build VALUES clause without concepts.")

    values = "\n        ".join(
        f"mdc:{concept_name}"
        for concept_name in concept_names
    )

    return f"""VALUES ?{variable_name} {{
        {values}
    }}"""


def get_primary_match_mode(canonical_request: CanonicalSearchRequest) -> str:
    """
    Return supported primary match mode.
    """
    primary_match_mode = canonical_request.match_policy.get(
        "primary_match_mode",
        "any",
    )

    if primary_match_mode not in {"any", "all"}:
        return "any"

    return primary_match_mode


def build_part_family_having_clause(
    *,
    primary_match_mode: str,
    requested_count: int,
) -> str:
    """
    Build HAVING clause for part-family matching.

    any:
      offering must match at least one requested part family

    all:
      offering must match all requested part families
    """
    if primary_match_mode == "all":
        return f"HAVING (COUNT(DISTINCT ?requestedPartFamily) = {requested_count})"

    return "HAVING (COUNT(DISTINCT ?requestedPartFamily) > 0)"


def build_part_family_search_query(
    canonical_request: CanonicalSearchRequest,
) -> str:
    """
    Build deterministic SPARQL for primary part-family matching.

    Current Day 3.1 scope:
    - ProviderOffering as result entity
    - part-family filtering
    - primary_match_mode any/all
    - provider/offering identity projection

    Not included yet:
    - material filters
    - diameter filters
    - scoring
    - unknown handling
    - optional criteria explanation
    """
    requested_part_families = canonical_request.primary_filters.get(
        "part_families",
        [],
    )

    if not requested_part_families:
        raise SparqlQueryBuildError(
            "Cannot build part-family query without requested part_families."
        )

    part_family_concepts = get_part_family_concepts(requested_part_families)

    if not part_family_concepts:
        raise SparqlQueryBuildError(
            "No requested part_families could be mapped to ontology concepts."
        )

    primary_match_mode = get_primary_match_mode(canonical_request)

    values_clause = build_values_clause(
        variable_name="requestedPartFamily",
        concept_names=part_family_concepts,
    )

    having_clause = build_part_family_having_clause(
        primary_match_mode=primary_match_mode,
        requested_count=len(set(part_family_concepts)),
    )

    return f"""
PREFIX mdc: <{MDC_PREFIX}>

SELECT
    ?provider
    ?providerId
    ?providerName
    ?offering
    ?offeringId
    ?offeringName
    (COUNT(DISTINCT ?requestedPartFamily) AS ?matchedPartFamilyCount)
    (GROUP_CONCAT(DISTINCT STR(?requestedPartFamily); separator=",") AS ?matchedPartFamilyUris)
WHERE {{
    {values_clause}

    ?offering a mdc:ProviderOffering ;
        mdc:offeredBy ?provider ;
        mdc:offeringId ?offeringId ;
        mdc:displayName ?offeringName ;
        mdc:supportsPartFamily ?requestedPartFamily .

    ?provider a mdc:MaaSProvider ;
        mdc:providerId ?providerId ;
        mdc:displayName ?providerName .
}}
GROUP BY
    ?provider
    ?providerId
    ?providerName
    ?offering
    ?offeringId
    ?offeringName
{having_clause}
ORDER BY DESC(?matchedPartFamilyCount)
""".strip()

def build_candidate_evidence_query(
    canonical_request: CanonicalSearchRequest,
) -> str:
    """
    Build deterministic SPARQL for primary part-family candidate search
    with basic evidence projection.

    Current Day 3.2 scope:
    - primary part-family candidate filtering
    - provider/offering identity projection
    - material evidence
    - diameter evidence
    - batch evidence
    - lead-time evidence

    Not included yet:
    - final scoring
    - matched/unmatched/unknown explanation
    - Fuseki HTTP client
    - replacing local matcher
    """
    requested_part_families = canonical_request.primary_filters.get(
        "part_families",
        [],
    )

    if not requested_part_families:
        raise SparqlQueryBuildError(
            "Cannot build candidate evidence query without requested part_families."
        )

    part_family_concepts = get_part_family_concepts(requested_part_families)

    if not part_family_concepts:
        raise SparqlQueryBuildError(
            "No requested part_families could be mapped to ontology concepts."
        )

    primary_match_mode = get_primary_match_mode(canonical_request)

    values_clause = build_values_clause(
        variable_name="requestedPartFamily",
        concept_names=part_family_concepts,
    )

    having_clause = build_part_family_having_clause(
        primary_match_mode=primary_match_mode,
        requested_count=len(set(part_family_concepts)),
    )

    return f"""
PREFIX mdc: <{MDC_PREFIX}>

SELECT
    ?provider
    ?providerId
    ?providerName
    ?offering
    ?offeringId
    ?offeringName
    (COUNT(DISTINCT ?requestedPartFamily) AS ?matchedPartFamilyCount)
    (GROUP_CONCAT(DISTINCT STR(?requestedPartFamily); separator=",") AS ?matchedPartFamilyUris)
    (GROUP_CONCAT(DISTINCT STR(?material); separator=",") AS ?materialUris)
    (SAMPLE(?diameterMinMmValue) AS ?diameterMinMm)
    (SAMPLE(?diameterMaxMmValue) AS ?diameterMaxMm)
    (SAMPLE(?batchMinValue) AS ?batchMin)
    (SAMPLE(?batchMaxValue) AS ?batchMax)
    (SAMPLE(?leadTimeMinWeeksValue) AS ?leadTimeMinWeeks)
    (SAMPLE(?leadTimeMaxWeeksValue) AS ?leadTimeMaxWeeks)
WHERE {{
    {values_clause}

    ?offering a mdc:ProviderOffering ;
        mdc:offeredBy ?provider ;
        mdc:offeringId ?offeringId ;
        mdc:displayName ?offeringName ;
        mdc:supportsPartFamily ?requestedPartFamily .

    ?provider a mdc:MaaSProvider ;
        mdc:providerId ?providerId ;
        mdc:displayName ?providerName .

    OPTIONAL {{
        ?offering mdc:supportsMaterial ?material .
    }}

    OPTIONAL {{
        ?offering mdc:diameterMinMm ?diameterMinMmValue .
    }}

    OPTIONAL {{
        ?offering mdc:diameterMaxMm ?diameterMaxMmValue .
    }}

    OPTIONAL {{
        ?offering mdc:batchMin ?batchMinValue .
    }}

    OPTIONAL {{
        ?offering mdc:batchMax ?batchMaxValue .
    }}

    OPTIONAL {{
        ?offering mdc:leadTimeMinWeeks ?leadTimeMinWeeksValue .
    }}

    OPTIONAL {{
        ?offering mdc:leadTimeMaxWeeks ?leadTimeMaxWeeksValue .
    }}
}}
GROUP BY
    ?provider
    ?providerId
    ?providerName
    ?offering
    ?offeringId
    ?offeringName
{having_clause}
ORDER BY DESC(?matchedPartFamilyCount)
""".strip()