from typing import Any

from apps.search.matchers.common import as_number


def evaluate_delivery_optional_match(
    *,
    requested_delivery: dict[str, Any],
    provided_lead_time: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Evaluate optional delivery max weeks.

    Rule:
    - request >= provider max -> matched
    - provider min <= request < provider max -> partial_match
    - request < provider min -> unmatched
    """
    if not requested_delivery:
        return None

    requested_max_weeks = as_number(requested_delivery.get("max_weeks"))

    if requested_max_weeks is None:
        return None

    provider_min = as_number(provided_lead_time.get("min"))
    provider_max = as_number(provided_lead_time.get("max"))

    provided_summary = {
        "min": provider_min,
        "max": provider_max,
        "qualifier": provided_lead_time.get("qualifier"),
        "confidence": provided_lead_time.get("confidence"),
        "source_type": provided_lead_time.get("source_type"),
    }

    if provider_min is None or provider_max is None:
        return {
            "field": "delivery.max_weeks",
            "match_type": "optional_criterion",
            "requested": requested_max_weeks,
            "provided": provided_summary,
            "score": 0.0,
            "status": "unknown",
            "reason": "No confirmed lead-time range is available for this offering.",
        }

    if requested_max_weeks >= provider_max:
        return {
            "field": "delivery.max_weeks",
            "match_type": "optional_criterion",
            "requested": requested_max_weeks,
            "provided": provided_summary,
            "score": 1.0,
            "status": "matched",
        }

    if provider_min <= requested_max_weeks < provider_max:
        return {
            "field": "delivery.max_weeks",
            "match_type": "optional_criterion",
            "requested": requested_max_weeks,
            "provided": provided_summary,
            "score": 0.5,
            "status": "partial_match",
            "reason": "Requested delivery is inside the provider normal range but below the usual maximum; confirmation may be needed.",
        }

    return {
        "field": "delivery.max_weeks",
        "match_type": "optional_criterion",
        "requested": requested_max_weeks,
        "provided": provided_summary,
        "score": 0.0,
        "status": "unmatched",
        "reason": "Requested delivery is shorter than the provider normal lead-time range.",
    }

