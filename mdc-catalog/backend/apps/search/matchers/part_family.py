

from typing import Any

from apps.search.matchers.common import calculate_coverage_score


def evaluate_part_family_primary_match(
    *,
    requested_part_families: list[str],
    offered_part_families: list[str],
    primary_match_mode: str,
) -> dict[str, Any]:
    """
    Evaluate whether an offering satisfies requested primary part families.

    primary_match_mode:
    - any: offering passes if it supports at least one requested part family
    - all: offering passes only if it supports all requested part families
    """
    requested_set = set(requested_part_families)
    offered_set = set(offered_part_families)

    matched = sorted(requested_set & offered_set)
    unmatched = sorted(requested_set - offered_set)

    primary_score = calculate_coverage_score(
        requested_values=sorted(requested_set),
        matched_values=matched,
    )

    if primary_match_mode == "all":
        passed = bool(requested_set) and primary_score == 1.0
    else:
        passed = primary_score > 0

    status = get_primary_match_status(
        passed=passed,
        primary_score=primary_score,
    )

    return {
        "field": "part_families",
        "match_type": "primary_filter",
        "match_mode": primary_match_mode,
        "requested": sorted(requested_set),
        "provided": sorted(offered_set),
        "matched": matched,
        "unmatched": unmatched,
        "requested_count": len(requested_set),
        "matched_count": len(matched),
        "unmatched_count": len(unmatched),
        "score": primary_score,
        "passed": passed,
        "status": status,
    }

def get_primary_match_status(
    *,
    passed: bool,
    primary_score: float,
) -> str:
    """
    Convert primary match result into a simple status.
    """
    if not passed:
        return "no_match"

    if primary_score >= 1.0:
        return "full_match"

    return "partial_match"


