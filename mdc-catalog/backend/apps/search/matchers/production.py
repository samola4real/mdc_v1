from typing import Any

from apps.search.matchers.common import as_number


def evaluate_batch_size_optional_match(
    *,
    requested_batch_size: Any,
    provided_batch: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Evaluate optional batch size.

    Rule:
    provider_min <= requested_batch_size <= provider_max
    """
    requested = as_number(requested_batch_size)

    if requested is None:
        return None

    provider_min = as_number(provided_batch.get("min"))
    provider_max = as_number(provided_batch.get("max"))

    provided_summary = {
        "min": provider_min,
        "max": provider_max,
        "unit": provided_batch.get("unit"),
        "confidence": provided_batch.get("confidence"),
        "source_type": provided_batch.get("source_type"),
    }

    if provider_min is None or provider_max is None:
        return {
            "field": "batch_size",
            "match_type": "optional_criterion",
            "requested": requested,
            "provided": provided_summary,
            "score": 0.0,
            "status": "unknown",
            "reason": "No confirmed batch size range is available for this offering.",
        }

    matched = provider_min <= requested <= provider_max

    return {
        "field": "batch_size",
        "match_type": "optional_criterion",
        "requested": requested,
        "provided": provided_summary,
        "score": 1.0 if matched else 0.0,
        "status": "matched" if matched else "unmatched",
        "reason": None
        if matched
        else "Requested batch size is outside the provider batch range.",
    }

