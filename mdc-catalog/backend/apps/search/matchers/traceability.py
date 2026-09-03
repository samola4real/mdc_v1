from typing import Any


def evaluate_traceability_optional_match(
    *,
    traceability_required: bool,
    provided_traceability: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Evaluate optional traceability.

    Only evaluated when traceability_required is True.
    """
    if traceability_required is not True:
        return None

    aerospace_traceability = provided_traceability.get("aerospace_traceability")
    full_traceability = provided_traceability.get("full_traceability")

    provided_summary = {
        "aerospace_traceability": aerospace_traceability,
        "full_traceability": full_traceability,
        "confidence": provided_traceability.get("confidence"),
        "source_type": provided_traceability.get("source_type"),
    }

    if aerospace_traceability is None and full_traceability is None:
        return {
            "field": "traceability_required",
            "match_type": "optional_criterion",
            "requested": True,
            "provided": provided_summary,
            "score": 0.0,
            "status": "unknown",
            "reason": "Traceability support is not confirmed for this offering.",
        }

    matched = aerospace_traceability is True or full_traceability is True

    return {
        "field": "traceability_required",
        "match_type": "optional_criterion",
        "requested": True,
        "provided": provided_summary,
        "score": 1.0 if matched else 0.0,
        "status": "matched" if matched else "unmatched",
        "reason": None if matched else "Requested traceability is not supported.",
    }
