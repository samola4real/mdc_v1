from typing import Any

from apps.search.request import CanonicalSearchRequest


DEFAULT_MATCH_POLICY = {
    "primary_match_mode": "any",
    "optional_match_mode": "any",
    "unknown_policy": "keep_as_unknown",
    "minimum_score": None,
}


def has_meaningful_value(value: Any) -> bool:
    """
    Return True when a value should be included in the canonical request.

    Empty dicts, empty lists, None, and empty strings are ignored.
    False is meaningful for some boolean fields, but for search we only include
    traceability_required when it is True.
    """
    if value is None:
        return False

    if value == "":
        return False

    if value == []:
        return False

    if value == {}:
        return False

    return True


def normalize_to_list(value: Any) -> list[Any]:
    """
    Normalize one value or many values into a list.

    Examples:
    "shaft" -> ["shaft"]
    ["shaft", "gear"] -> ["shaft", "gear"]
    None -> []
    """
    if not has_meaningful_value(value):
        return []

    if isinstance(value, list):
        return value

    return [value]


def clean_nested_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Remove empty nested dictionaries/lists from a dictionary.
    """
    cleaned = {}

    for key, value in data.items():
        if isinstance(value, dict):
            nested = clean_nested_dict(value)
            if has_meaningful_value(nested):
                cleaned[key] = nested
        elif has_meaningful_value(value):
            cleaned[key] = value

    return cleaned


def normalize_match_policy(validated_data: dict[str, Any]) -> dict[str, Any]:
    raw_policy = validated_data.get("match_policy") or {}

    return {
        "primary_match_mode": raw_policy.get(
            "primary_match_mode",
            DEFAULT_MATCH_POLICY["primary_match_mode"],
        ),
        "optional_match_mode": raw_policy.get(
            "optional_match_mode",
            DEFAULT_MATCH_POLICY["optional_match_mode"],
        ),
        "unknown_policy": raw_policy.get(
            "unknown_policy",
            DEFAULT_MATCH_POLICY["unknown_policy"],
        ),
        "minimum_score": raw_policy.get(
            "minimum_score",
            DEFAULT_MATCH_POLICY["minimum_score"],
        ),
    }

def normalize_primary_filters(validated_data: dict[str, Any]) -> dict[str, Any]:
    """
    Extract required primary filters from validated search data.

    Current Phase E primary filter:
    - part_family from the API serializer

    Canonical output is list-based:
    - part_families: ["shaft"]

    This makes the structure ready for future multiple primary filters, e.g.:
    - part_families: ["shaft", "gear"]
    - service_types: ["machining"]
    - required_certifications: ["ISO9001_2015"]
    """
    primary_filters: dict[str, Any] = {}

    # Current serializer field is singular: part_family.
    # Canonical internal field is plural/list-based: part_families.
    part_families = normalize_to_list(validated_data.get("part_family"))

    if part_families:
        primary_filters["part_families"] = part_families

    # Future-ready support:
    # If later the serializer accepts part_families directly, this works too.
    extra_part_families = normalize_to_list(validated_data.get("part_families"))

    if extra_part_families:
        existing = primary_filters.get("part_families", [])
        merged = list(dict.fromkeys(existing + extra_part_families))
        primary_filters["part_families"] = merged

    return primary_filters


def normalize_optional_criteria(validated_data: dict[str, Any]) -> dict[str, Any]:
    """
    Extract optional criteria from validated search data.

    Primary filters are intentionally excluded from optional_criteria.
    """
    optional_criteria: dict[str, Any] = {}

    scalar_or_list_fields = [
        "service_type",
        "materials",
        "material_grades",
        "processes",
        "batch_size",
        "certifications",
        "industry",
    ]

    for field_name in scalar_or_list_fields:
        value = validated_data.get(field_name)

        if has_meaningful_value(value):
            optional_criteria[field_name] = value

    traceability_required = validated_data.get("traceability_required", False)
    if traceability_required is True:
        optional_criteria["traceability_required"] = True

    nested_fields = [
        "dimensions",
        "weight_kg",
        "gear_parameters",
        "surface_finish",
        "delivery",
    ]

    for field_name in nested_fields:
        value = validated_data.get(field_name)

        if isinstance(value, dict):
            cleaned_value = clean_nested_dict(value)
            if has_meaningful_value(cleaned_value):
                optional_criteria[field_name] = cleaned_value

    return optional_criteria


def normalize_search_request(
    validated_data: dict[str, Any],
    *,
    warnings: list[dict[str, Any]] | None = None,
) -> CanonicalSearchRequest:
    """
    Convert validated serializer data into a canonical SearchRequest object.

    Required primary filters:
    - part_families, currently created from API field part_family

    Optional criteria:
    - service_type
    - materials
    - material_grades
    - processes
    - dimensions
    - weight_kg
    - gear parameters
    - surface finish
    - batch size
    - delivery
    - certifications
    - traceability
    - industry
    """
    primary_filters = normalize_primary_filters(validated_data)

    optional_criteria = normalize_optional_criteria(validated_data)
    match_policy = normalize_match_policy(validated_data)

    return CanonicalSearchRequest(
        primary_filters=primary_filters,
        optional_criteria=optional_criteria,
        match_policy=match_policy,
        warnings=warnings or [],
    )