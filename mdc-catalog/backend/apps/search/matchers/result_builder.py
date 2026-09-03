from typing import Any

from apps.search.matchers.certification import extract_provider_certifications
from apps.search.matchers.common import calculate_total_score, normalize_string_list
from apps.search.matchers.material import (
    extract_supported_material_grades,
    extract_supported_materials,
)


def get_overall_match_status(
    *,
    primary_status: str,
    optional_evaluations: list[dict[str, Any]],
) -> str:
    """
    Determine current overall match status.

    Primary match decides whether a provider is returned.
    Optional criteria can downgrade full_match to partial_match.
    """
    if primary_status == "no_match":
        return "no_match"

    if primary_status == "partial_match":
        return "partial_match"

    for evaluation in optional_evaluations:
        if evaluation["status"] != "matched":
            return "partial_match"

    return "full_match"


def build_matched_attribute(evaluation: dict[str, Any]) -> dict[str, Any]:
    """
    Build a matched-attribute explanation.
    """
    base = {
        "field": evaluation["field"],
        "match_type": evaluation["match_type"],
        "match_mode": evaluation.get("match_mode"),
        "requested": evaluation["requested"],
        "provided": evaluation["provided"],
        "coverage": evaluation["score"],
        "status": evaluation["status"],
    }

    if "matched" in evaluation:
        base["matched"] = evaluation["matched"]

    if "requested_count" in evaluation:
        base["requested_count"] = evaluation["requested_count"]

    if "matched_count" in evaluation:
        base["matched_count"] = evaluation["matched_count"]

    return base


def build_issue_attribute(evaluation: dict[str, Any]) -> dict[str, Any] | None:
    """
    Build partial/unmatched explanation.
    """
    if evaluation["status"] not in {"unmatched", "partial_match"}:
        return None

    unmatched = evaluation.get("unmatched", [])

    if evaluation["field"] in {"part_families", "materials", "material_grades", "processes", "certifications"}:
        if not unmatched:
            return None

    return {
        "field": evaluation["field"],
        "match_type": evaluation["match_type"],
        "match_mode": evaluation.get("match_mode"),
        "requested": evaluation["requested"],
        "provided": evaluation["provided"],
        "unmatched": unmatched,
        "unmatched_count": evaluation.get("unmatched_count"),
        "status": evaluation["status"],
        "reason": evaluation.get("reason")
        or "The offering does not fully satisfy this requested field.",
    }


def build_unknown_attribute(evaluation: dict[str, Any]) -> dict[str, Any] | None:
    """
    Build unknown explanation when provider data is not confirmed.
    """
    if evaluation["status"] != "unknown":
        return None

    return {
        "field": evaluation["field"],
        "match_type": evaluation["match_type"],
        "requested": evaluation["requested"],
        "provided": evaluation.get("provided"),
        "reason": evaluation.get("reason", "Provider data is unknown."),
        "status": "unknown",
    }

def build_search_result(
    *,
    provider: dict[str, Any],
    offering: dict[str, Any],
    part_family_evaluation: dict[str, Any],
    optional_evaluations: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Build local search result shape.
    """
    matched_attributes = [
        build_matched_attribute(part_family_evaluation)
    ]

    unmatched_attributes = []
    unknown_attributes = []

    for evaluation in optional_evaluations:
        if evaluation["status"] in {"matched", "partial_match"}:
            matched_attributes.append(build_matched_attribute(evaluation))

        issue_attribute = build_issue_attribute(evaluation)
        if issue_attribute:
            unmatched_attributes.append(issue_attribute)

        unknown_attribute = build_unknown_attribute(evaluation)
        if unknown_attribute:
            unknown_attributes.append(unknown_attribute)

    part_family_issue_attribute = build_issue_attribute(part_family_evaluation)
    if part_family_issue_attribute:
        unmatched_attributes.append(part_family_issue_attribute)

    optional_scores = [
        evaluation["score"]
        for evaluation in optional_evaluations
        if evaluation["status"] != "unknown"
    ]

    optional_score = None
    if optional_scores:
        optional_score = round(sum(optional_scores) / len(optional_scores), 3)

    primary_score = part_family_evaluation["score"]

    total_score = calculate_total_score(
        primary_score=primary_score,
        optional_score=optional_score,
    )

    overall_status = get_overall_match_status(
        primary_status=part_family_evaluation["status"],
        optional_evaluations=optional_evaluations,
    )

    return {
        "provider": {
            "provider_id": provider["provider_id"],
            "display_name": provider.get("display_name", ""),
            "country": provider.get("country", ""),
        },
        "offering": {
            "offering_id": offering["offering_id"],
            "provider_id": offering["provider_id"],
            "name": offering.get("name", ""),
            "service_type": offering.get("service_type", ""),
        },
        "match": {
            "status": overall_status,
            "score": total_score,
            "primary_score": primary_score,
            "optional_score": optional_score,
            "hard_filters_passed": part_family_evaluation["passed"],
            "primary_match_mode": part_family_evaluation["match_mode"],
            "primary_requested_count": part_family_evaluation["requested_count"],
            "primary_matched_count": part_family_evaluation["matched_count"],
        },
        "matched_attributes": matched_attributes,
        "unmatched_attributes": unmatched_attributes,
        "unknown_attributes": unknown_attributes,
        "evidence": [
            {
                "field": "part_families",
                "value": part_family_evaluation["provided"],
                "source": "provider_seed_data",
            },
            {
                "field": "materials",
                "value": extract_supported_materials(offering),
                "source": "provider_seed_data",
            },
            {
                "field": "material_grades",
                "value": extract_supported_material_grades(offering),
                "source": "provider_seed_data",
            },
            {
                "field": "processes",
                "value": normalize_string_list(offering.get("processes")),
                "source": "provider_seed_data",
            },
            {
                "field": "capabilities",
                "value": offering.get("capabilities", {}),
                "source": "provider_seed_data",
            },
            {
                "field": "certifications",
                "value": extract_provider_certifications(provider),
                "source": "provider_seed_data",
            },
        ],
    }

