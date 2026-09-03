from typing import Any

from apps.search.matchers.common import as_number
from apps.search.request import CanonicalSearchRequest


def extract_requested_quality(
    canonical_request: CanonicalSearchRequest,
) -> dict[str, Any]:
    """
    Extract requested quality from canonical optional criteria.
    """
    gear_parameters = canonical_request.optional_criteria.get("gear_parameters", {})

    if not isinstance(gear_parameters, dict):
        return {}

    quality = gear_parameters.get("quality", {})

    if not isinstance(quality, dict):
        return {}

    return quality


def evaluate_quality_optional_match(
    *,
    requested_quality: dict[str, Any],
    provided_quality: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Evaluate optional quality.

    For DIN/ISO class numbers, lower or equal provider best_class is better.
    Example:
    provider DIN4 can satisfy requested max_class 5.
    provider DIN4 cannot satisfy requested max_class 3.
    """
    if not requested_quality:
        return None

    requested_standard = requested_quality.get("standard")
    requested_max_class = as_number(requested_quality.get("max_class"))

    provided_standard = provided_quality.get("standard")
    provided_best_class = as_number(provided_quality.get("best_class"))

    requested_summary = {
        "standard": requested_standard,
        "max_class": requested_max_class,
    }

    provided_summary = {
        "standard": provided_standard,
        "best_class": provided_best_class,
        "comparison_rule": provided_quality.get("comparison_rule"),
        "confidence": provided_quality.get("confidence"),
        "source_type": provided_quality.get("source_type"),
    }

    if not provided_standard and provided_best_class is None:
        return {
            "field": "quality",
            "match_type": "optional_criterion",
            "requested": requested_summary,
            "provided": provided_summary,
            "score": 0.0,
            "status": "unknown",
            "reason": "No confirmed quality capability is available for this offering.",
        }

    if requested_standard and provided_standard != requested_standard:
        return {
            "field": "quality",
            "match_type": "optional_criterion",
            "requested": requested_summary,
            "provided": provided_summary,
            "score": 0.0,
            "status": "unmatched",
            "reason": "Requested quality standard does not match provider quality standard.",
        }

    if requested_max_class is not None:
        if provided_best_class is None:
            return {
                "field": "quality",
                "match_type": "optional_criterion",
                "requested": requested_summary,
                "provided": provided_summary,
                "score": 0.0,
                "status": "unknown",
                "reason": "Provider quality class is not confirmed.",
            }

        matched = provided_best_class <= requested_max_class

        return {
            "field": "quality",
            "match_type": "optional_criterion",
            "requested": requested_summary,
            "provided": provided_summary,
            "score": 1.0 if matched else 0.0,
            "status": "matched" if matched else "unmatched",
            "reason": None
            if matched
            else "Provider best quality class does not satisfy requested class.",
        }

    return {
        "field": "quality",
        "match_type": "optional_criterion",
        "requested": requested_summary,
        "provided": provided_summary,
        "score": 1.0,
        "status": "matched",
    }

