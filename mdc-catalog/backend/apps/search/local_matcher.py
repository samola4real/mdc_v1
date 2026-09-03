from typing import Any

from apps.providers.services import get_provider_by_id, list_offerings
from apps.search.matchers.certification import evaluate_certification_optional_match
from apps.search.matchers.common import (
    DEFAULT_PRIMARY_MATCH_MODE,
    evaluate_list_optional_match,
    normalize_string_list,
)
from apps.search.matchers.delivery import evaluate_delivery_optional_match
from apps.search.matchers.dimensions import (
    evaluate_diametral_pitch_optional_match,
    evaluate_diameter_optional_match,
    evaluate_module_optional_match,
    evaluate_surface_finish_optional_match,
    evaluate_weight_optional_match,
    extract_capability,
)
from apps.search.matchers.material import (
    evaluate_material_grade_optional_match,
    evaluate_material_optional_match,
)
from apps.search.matchers.part_family import evaluate_part_family_primary_match
from apps.search.matchers.production import evaluate_batch_size_optional_match
from apps.search.matchers.quality import (
    evaluate_quality_optional_match,
    extract_requested_quality,
)
from apps.search.matchers.result_builder import build_search_result
from apps.search.matchers.service_type import evaluate_service_type_optional_match
from apps.search.matchers.traceability import evaluate_traceability_optional_match
from apps.search.request import CanonicalSearchRequest


def evaluate_industry_optional_match(
    *,
    requested_industry: str | None,
    offering: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Evaluate industry if offering industries exist.
    """
    if not requested_industry:
        return None

    provided_industries = normalize_string_list(offering.get("industries"))

    if not provided_industries:
        return {
            "field": "industry",
            "match_type": "optional_criterion",
            "requested": requested_industry,
            "provided": [],
            "score": 0.0,
            "status": "unknown",
            "reason": "Industry support is not confirmed for this offering.",
        }

    matched = requested_industry in provided_industries

    return {
        "field": "industry",
        "match_type": "optional_criterion",
        "requested": requested_industry,
        "provided": provided_industries,
        "score": 1.0 if matched else 0.0,
        "status": "matched" if matched else "unmatched",
        "reason": None if matched else "Requested industry is not listed for this offering.",
    }


def collect_optional_evaluations(
    *,
    canonical_request: CanonicalSearchRequest,
    provider: dict[str, Any],
    offering: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Evaluate all currently supported optional criteria.
    """
    optional_criteria = canonical_request.optional_criteria

    evaluations = [
        evaluate_service_type_optional_match(
            requested_service_type=optional_criteria.get("service_type"),
            provided_service_type=offering.get("service_type"),
        ),
        evaluate_material_optional_match(
            requested_materials=normalize_string_list(optional_criteria.get("materials")),
            offering=offering,
        ),
        evaluate_material_grade_optional_match(
            requested_material_grades=normalize_string_list(
                optional_criteria.get("material_grades")
            ),
            offering=offering,
        ),
        evaluate_list_optional_match(
            field="processes",
            requested_values=normalize_string_list(optional_criteria.get("processes")),
            provided_values=normalize_string_list(offering.get("processes")),
            unknown_reason="No confirmed process data is available for this offering.",
        ),
        evaluate_diameter_optional_match(
            canonical_request=canonical_request,
            offering=offering,
        ),
        evaluate_weight_optional_match(
            requested_weight=optional_criteria.get("weight_kg", {}),
            offering=offering,
        ),
        evaluate_batch_size_optional_match(
            requested_batch_size=optional_criteria.get("batch_size"),
            provided_batch=extract_capability(offering, "batch_size"),
        ),
        evaluate_module_optional_match(
            canonical_request=canonical_request,
            offering=offering,
        ),
        evaluate_diametral_pitch_optional_match(
            canonical_request=canonical_request,
            offering=offering,
        ),
        evaluate_quality_optional_match(
            requested_quality=extract_requested_quality(canonical_request),
            provided_quality=extract_capability(offering, "quality"),
        ),
        evaluate_surface_finish_optional_match(
            canonical_request=canonical_request,
            offering=offering,
        ),
    ]

    delivery_request = optional_criteria.get("delivery", {})
    if isinstance(delivery_request, dict):
        evaluations.append(
            evaluate_delivery_optional_match(
                requested_delivery=delivery_request,
                provided_lead_time=extract_capability(offering, "lead_time_weeks"),
            )
        )

    evaluations.extend(
        [
            evaluate_certification_optional_match(
                requested_certifications=normalize_string_list(
                    optional_criteria.get("certifications")
                ),
                provider=provider,
            ),
            evaluate_traceability_optional_match(
                traceability_required=optional_criteria.get("traceability_required")
                is True,
                provided_traceability=extract_capability(offering, "traceability"),
            ),
            evaluate_industry_optional_match(
                requested_industry=optional_criteria.get("industry"),
                offering=offering,
            ),
        ]
    )

    return [evaluation for evaluation in evaluations if evaluation]


def find_offerings_matching_primary_filters(
    canonical_request: CanonicalSearchRequest,
) -> list[dict[str, Any]]:
    """
    Return offerings that pass primary part-family matching.
    """
    requested_part_families = normalize_string_list(
        canonical_request.primary_filters.get("part_families")
    )

    primary_match_mode = canonical_request.match_policy.get(
        "primary_match_mode",
        DEFAULT_PRIMARY_MATCH_MODE,
    )

    if primary_match_mode not in {"any", "all"}:
        primary_match_mode = DEFAULT_PRIMARY_MATCH_MODE

    results = []

    for offering in list_offerings():
        provider = get_provider_by_id(offering["provider_id"])

        part_family_evaluation = evaluate_part_family_primary_match(
            requested_part_families=requested_part_families,
            offered_part_families=normalize_string_list(offering.get("part_families", [])),
            primary_match_mode=primary_match_mode,
        )

        if not part_family_evaluation["passed"]:
            continue

        optional_evaluations = collect_optional_evaluations(
            canonical_request=canonical_request,
            provider=provider,
            offering=offering,
        )

        results.append(
            build_search_result(
                provider=provider,
                offering=offering,
                part_family_evaluation=part_family_evaluation,
                optional_evaluations=optional_evaluations,
            )
        )

    results.sort(
        key=lambda result: result["match"]["score"],
        reverse=True,
    )

    return results
