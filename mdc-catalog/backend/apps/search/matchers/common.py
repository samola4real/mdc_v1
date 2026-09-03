


from typing import Any

DEFAULT_PRIMARY_MATCH_MODE = "any"

PRIMARY_SCORE_WEIGHT = 0.7
OPTIONAL_SCORE_WEIGHT = 0.3




def normalize_string_list(values: Any) -> list[str]:
    """
    Normalize a possible string/list value into a clean list of strings.
    """
    if values is None:
        return []

    if isinstance(values, str):
        return [values]

    if isinstance(values, list):
        return [value for value in values if isinstance(value, str)]

    return []


def as_number(value: Any) -> float | None:
    """
    Convert numeric values safely.
    """
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, int | float):
        return float(value)

    return None


def calculate_coverage_score(
    *,
    requested_values: list[str],
    matched_values: list[str],
) -> float:
    """
    Calculate simple list coverage score.

    Example:
    requested = ["shaft", "gear"]
    matched = ["shaft"]
    score = 0.5
    """
    requested_set = set(requested_values)

    if not requested_set:
        return 0.0

    score = len(set(matched_values)) / len(requested_set)

    return round(score, 3)


def calculate_total_score(
    *,
    primary_score: float,
    optional_score: float | None,
) -> float:
    """
    Combine primary and optional scores.

    If no optional criteria were supplied, total score equals primary score.
    """
    if optional_score is None:
        return primary_score

    total_score = (
        primary_score * PRIMARY_SCORE_WEIGHT
        + optional_score * OPTIONAL_SCORE_WEIGHT
    )

    return round(total_score, 3)

def evaluate_list_optional_match(
    *,
    field: str,
    requested_values: list[str],
    provided_values: list[str],
    unknown_reason: str,
) -> dict[str, Any] | None:
    """
    Evaluate optional list-based criteria.

    Used for:
    - materials
    - material_grades
    - processes
    - certifications
    """
    requested_set = set(requested_values)

    if not requested_set:
        return None

    provided_set = set(provided_values)

    if not provided_set:
        return {
            "field": field,
            "match_type": "optional_criterion",
            "requested": sorted(requested_set),
            "provided": [],
            "matched": [],
            "unmatched": [],
            "requested_count": len(requested_set),
            "matched_count": 0,
            "unmatched_count": 0,
            "score": 0.0,
            "status": "unknown",
            "reason": unknown_reason,
        }

    matched = sorted(requested_set & provided_set)
    unmatched = sorted(requested_set - provided_set)

    score = calculate_coverage_score(
        requested_values=sorted(requested_set),
        matched_values=matched,
    )

    if score >= 1.0:
        status = "matched"
    elif score > 0:
        status = "partial_match"
    else:
        status = "unmatched"

    return {
        "field": field,
        "match_type": "optional_criterion",
        "requested": sorted(requested_set),
        "provided": sorted(provided_set),
        "matched": matched,
        "unmatched": unmatched,
        "requested_count": len(requested_set),
        "matched_count": len(matched),
        "unmatched_count": len(unmatched),
        "score": score,
        "status": status,
    }


def evaluate_scalar_optional_match(
    *,
    field: str,
    requested_value: Any,
    provided_value: Any,
    unknown_reason: str,
) -> dict[str, Any] | None:
    """
    Evaluate exact scalar optional criteria.
    """
    if requested_value in [None, ""]:
        return None

    if provided_value in [None, ""]:
        return {
            "field": field,
            "match_type": "optional_criterion",
            "requested": requested_value,
            "provided": provided_value,
            "score": 0.0,
            "status": "unknown",
            "reason": unknown_reason,
        }

    matched = requested_value == provided_value

    return {
        "field": field,
        "match_type": "optional_criterion",
        "requested": requested_value,
        "provided": provided_value,
        "score": 1.0 if matched else 0.0,
        "status": "matched" if matched else "unmatched",
        "reason": None if matched else f"Requested {field} does not match offering value.",
    }


def evaluate_numeric_range_optional_match(
    *,
    field: str,
    requested_range: dict[str, Any],
    provided_range: dict[str, Any],
    unknown_reason: str,
) -> dict[str, Any] | None:
    """
    Evaluate optional numeric range criteria.

    Supported request forms:
    - exact
    - min/max

    Matching rules:
    - exact: provider_min <= exact <= provider_max
    - min/max: requested range overlaps provider range
    """
    if not requested_range:
        return None

    requested_exact = as_number(requested_range.get("exact"))
    requested_min = as_number(requested_range.get("min"))
    requested_max = as_number(requested_range.get("max"))

    provider_min = as_number(provided_range.get("min"))
    provider_max = as_number(provided_range.get("max"))

    requested_summary = {
        "exact": requested_exact,
        "min": requested_min,
        "max": requested_max,
    }

    provided_summary = {
        "min": provider_min,
        "max": provider_max,
        "confidence": provided_range.get("confidence"),
        "source_type": provided_range.get("source_type"),
    }

    if provider_min is None or provider_max is None:
        return {
            "field": field,
            "match_type": "optional_criterion",
            "requested": requested_summary,
            "provided": provided_summary,
            "score": 0.0,
            "status": "unknown",
            "reason": unknown_reason,
        }

    if requested_exact is not None:
        matched = provider_min <= requested_exact <= provider_max

        return {
            "field": field,
            "match_type": "optional_criterion",
            "requested": requested_summary,
            "provided": provided_summary,
            "score": 1.0 if matched else 0.0,
            "status": "matched" if matched else "unmatched",
            "reason": None
            if matched
            else f"Requested exact {field} is outside the provider range.",
        }

    if requested_min is not None or requested_max is not None:
        effective_requested_min = requested_min if requested_min is not None else 0.0
        effective_requested_max = (
            requested_max if requested_max is not None else float("inf")
        )

        overlaps = (
            effective_requested_min <= provider_max
            and effective_requested_max >= provider_min
        )

        return {
            "field": field,
            "match_type": "optional_criterion",
            "requested": requested_summary,
            "provided": provided_summary,
            "score": 1.0 if overlaps else 0.0,
            "status": "matched" if overlaps else "unmatched",
            "reason": None
            if overlaps
            else f"Requested {field} range does not overlap the provider range.",
        }

    return None


def evaluate_max_value_optional_match(
    *,
    field: str,
    requested_max: Any,
    provided_max: Any,
    unknown_reason: str,
) -> dict[str, Any] | None:
    """
    Evaluate optional max-value criteria.
    """
    requested_max_number = as_number(requested_max)

    if requested_max_number is None:
        return None

    provided_max_number = as_number(provided_max)

    if provided_max_number is None:
        return {
            "field": field,
            "match_type": "optional_criterion",
            "requested": {"max": requested_max_number},
            "provided": {"max": provided_max},
            "score": 0.0,
            "status": "unknown",
            "reason": unknown_reason,
        }

    if field == "weight_kg":
        matched = requested_max_number <= provided_max_number
        reason = "Requested weight exceeds the provider maximum weight."
    else:
        matched = provided_max_number <= requested_max_number
        reason = "Provider value does not satisfy the requested maximum."

    return {
        "field": field,
        "match_type": "optional_criterion",
        "requested": {"max": requested_max_number},
        "provided": {"max": provided_max_number},
        "score": 1.0 if matched else 0.0,
        "status": "matched" if matched else "unmatched",
        "reason": None if matched else reason,
    }

