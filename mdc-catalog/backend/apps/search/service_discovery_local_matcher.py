from copy import deepcopy
from typing import Any

from apps.providers.service_discovery_loaders import load_service_discovery_providers
from apps.search.service_discovery_request import CanonicalServiceDiscoverySearchRequest


MATCHER_STATUS = {
    "search_executed": True,
    "search_engine": "local_harmonized_service_discovery_matcher",
    "message": (
        "Search executed using harmonized local provider data. "
        "RDF/SPARQL/Fuseki search is not active in this matcher."
    ),
}


def _is_unknown_record(record: Any) -> bool:
    return isinstance(record, dict) and (
        record.get("source_type") == "not_confirmed"
        or record.get("confidence") == "unknown"
    )


def _evidence_metadata(record: Any) -> dict:
    if not isinstance(record, dict):
        return {}
    return {
        key: record[key]
        for key in ["source_type", "confidence"]
        if key in record
    }


def _coverage_for_status(status: str, coverage: float = 0.0) -> float:
    if status == "matched":
        return 1.0
    if status == "partial_match":
        return coverage
    return 0.0


def _base_explanation(
    *,
    field: str,
    match_type: str,
    requested: Any,
    provided: Any,
    status: str,
    reason: str | None,
    coverage: float,
    evidence: dict | None = None,
) -> dict:
    item = {
        "field": field,
        "match_type": match_type,
        "requested": requested,
        "provided": provided,
        "status": status,
        "reason": reason,
        "coverage": coverage,
    }
    if evidence:
        item.update(_evidence_metadata(evidence))
    return item


def _number(record: dict, key: str):
    value = record.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _evaluate_range(
    *,
    field: str,
    requested: dict,
    provided: Any,
    match_type: str,
) -> dict:
    if not isinstance(provided, dict) or _is_unknown_record(provided):
        return _base_explanation(
            field=field,
            match_type=match_type,
            requested=requested,
            provided=provided,
            status="unknown",
            reason=f"No confirmed comparable evidence is available for {field}.",
            coverage=0.0,
            evidence=provided if isinstance(provided, dict) else None,
        )

    provider_min = _number(provided, "min")
    provider_max = _number(provided, "max")
    requested_exact = requested.get("exact")
    requested_min = requested.get("min")
    requested_max = requested.get("max")

    can_compare = True
    matched = True
    if requested_exact is not None:
        if provider_min is None or provider_max is None:
            can_compare = False
        else:
            matched = provider_min <= requested_exact <= provider_max
    if requested_min is not None:
        if provider_min is None:
            can_compare = False
        else:
            matched = matched and provider_min <= requested_min
    if requested_max is not None:
        if provider_max is None:
            can_compare = False
        else:
            matched = matched and provider_max >= requested_max

    if not can_compare:
        status = "unknown"
        reason = f"Provider evidence for {field} is incomplete for comparison."
    elif matched:
        status = "matched"
        reason = None
    else:
        status = "unmatched"
        reason = f"Provider evidence for {field} does not cover the request."

    return _base_explanation(
        field=field,
        match_type=match_type,
        requested=requested,
        provided=provided,
        status=status,
        reason=reason,
        coverage=_coverage_for_status(status),
        evidence=provided,
    )


def _evaluate_max_requirement(
    *,
    field: str,
    requested: float,
    provided: Any,
    match_type: str,
    provider_max_must_be_at_least: bool,
) -> dict:
    if not isinstance(provided, dict) or _is_unknown_record(provided):
        return _base_explanation(
            field=field,
            match_type=match_type,
            requested=requested,
            provided=provided,
            status="unknown",
            reason=f"No confirmed comparable evidence is available for {field}.",
            coverage=0.0,
            evidence=provided if isinstance(provided, dict) else None,
        )

    provider_max = _number(provided, "max")
    if provider_max is None:
        status = "unknown"
        reason = f"Provider evidence for {field} has no comparable maximum."
    else:
        matched = provider_max >= requested if provider_max_must_be_at_least else provider_max <= requested
        status = "matched" if matched else "unmatched"
        reason = None if matched else f"Provider evidence for {field} does not satisfy the request."

    return _base_explanation(
        field=field,
        match_type=match_type,
        requested=requested,
        provided=provided,
        status=status,
        reason=reason,
        coverage=_coverage_for_status(status),
        evidence=provided,
    )


def _evaluate_quality(
    *,
    field: str,
    requested: dict,
    provided: Any,
    match_type: str,
) -> dict:
    if not isinstance(provided, dict) or _is_unknown_record(provided):
        return _base_explanation(
            field=field,
            match_type=match_type,
            requested=requested,
            provided=provided,
            status="unknown",
            reason=f"No confirmed comparable quality evidence is available for {field}.",
            coverage=0.0,
            evidence=provided if isinstance(provided, dict) else None,
        )

    if provided.get("standard") != requested.get("standard"):
        status = "unknown"
        reason = "Quality standards differ or are not comparable in H5."
    elif provided.get("best_class") is None:
        status = "unknown"
        reason = "Provider quality class is not comparable."
    elif provided.get("best_class") <= requested.get("max_class"):
        status = "matched"
        reason = None
    else:
        status = "unmatched"
        reason = "Provider quality class does not satisfy the requested class."

    return _base_explanation(
        field=field,
        match_type=match_type,
        requested=requested,
        provided=provided,
        status=status,
        reason=reason,
        coverage=_coverage_for_status(status),
        evidence=provided,
    )


def _evaluate_bounding_box(field: str, requested: dict, provided: Any, match_type: str) -> dict:
    if not isinstance(provided, dict) or _is_unknown_record(provided):
        return _base_explanation(
            field=field,
            match_type=match_type,
            requested=requested,
            provided=provided,
            status="unknown",
            reason="No confirmed bounding-box evidence is available.",
            coverage=0.0,
            evidence=provided if isinstance(provided, dict) else None,
        )

    component_results = []
    for component, request_value in requested.items():
        component_results.append(
            _evaluate_range(
                field=component,
                requested=request_value,
                provided=provided.get(component),
                match_type=match_type,
            )
        )

    matched_count = len([item for item in component_results if item["status"] == "matched"])
    unmatched_count = len([item for item in component_results if item["status"] == "unmatched"])
    unknown_count = len([item for item in component_results if item["status"] == "unknown"])

    if matched_count == len(component_results):
        status = "matched"
        reason = None
    elif matched_count and (unmatched_count or unknown_count):
        status = "partial_match"
        reason = "Some bounding-box components matched and others did not."
    elif unmatched_count:
        status = "unmatched"
        reason = "Bounding-box evidence does not satisfy the request."
    else:
        status = "unknown"
        reason = "Bounding-box evidence is incomplete."

    coverage = matched_count / len(component_results) if component_results else 0.0
    return _base_explanation(
        field=field,
        match_type=match_type,
        requested=requested,
        provided=provided,
        status=status,
        reason=reason,
        coverage=coverage,
        evidence=provided,
    ) | {"components": component_results}


def _evaluate_list_coverage(
    *,
    field: str,
    requested: list[str],
    provided_records: Any,
    record_key: str,
    match_type: str,
) -> dict:
    if not requested:
        raise ValueError("List coverage evaluator requires requested values.")

    if not isinstance(provided_records, list) or not provided_records:
        return _base_explanation(
            field=field,
            match_type=match_type,
            requested=requested,
            provided=provided_records,
            status="unknown",
            reason=f"No confirmed {field} evidence is available for this offering.",
            coverage=0.0,
        )

    provided_values = [
        item.get(record_key)
        for item in provided_records
        if isinstance(item, dict) and not _is_unknown_record(item)
    ]
    matched_values = [value for value in requested if value in provided_values]
    coverage = len(matched_values) / len(requested)

    if coverage == 1:
        status = "matched"
        reason = None
    elif coverage > 0:
        status = "partial_match"
        reason = f"Some requested {field} values are confirmed."
    else:
        status = "unmatched"
        reason = f"Requested {field} values are not confirmed."

    return _base_explanation(
        field=field,
        match_type=match_type,
        requested=requested,
        provided=provided_records,
        status=status,
        reason=reason,
        coverage=coverage,
    )


def _evaluate_certifications(requested: list[str], provider: dict, offering: dict) -> dict:
    provider_certs = provider.get("certifications", [])
    offering_certs = offering.get("generic_capabilities", {}).get("certifications", [])
    records = [*provider_certs, *offering_certs]
    return _evaluate_list_coverage(
        field="certifications",
        requested=requested,
        provided_records=records,
        record_key="code",
        match_type="generic_requirement",
    )


def _evaluate_batch_size(requested: int, provided: Any) -> dict:
    if not isinstance(provided, dict) or _is_unknown_record(provided):
        return _base_explanation(
            field="batch_size",
            match_type="generic_requirement",
            requested=requested,
            provided=provided,
            status="unknown",
            reason="No confirmed batch-size evidence is available.",
            coverage=0.0,
            evidence=provided if isinstance(provided, dict) else None,
        )
    provider_min = _number(provided, "min")
    provider_max = _number(provided, "max")
    if provider_min is None or provider_max is None:
        status = "unknown"
        reason = "Batch-size evidence is incomplete."
    elif provider_min <= requested <= provider_max:
        status = "matched"
        reason = None
    else:
        status = "unmatched"
        reason = "Requested batch size is outside provider evidence."
    return _base_explanation(
        field="batch_size",
        match_type="generic_requirement",
        requested=requested,
        provided=provided,
        status=status,
        reason=reason,
        coverage=_coverage_for_status(status),
        evidence=provided,
    )


def _evaluate_part_type(selection: dict, offering: dict) -> tuple[dict, float, str]:
    requested_type = selection["part_type"]
    records = {
        item.get("part_type"): item
        for item in offering.get("supported_part_types", [])
        if isinstance(item, dict)
    }
    record = records.get(requested_type)

    if record and record.get("support_status") == "confirmed":
        status = "matched"
        reason = None
        score = 1.0
    elif record and record.get("support_status") == "candidate_requiring_confirmation":
        status = "unknown"
        reason = "Requested part type is identified only as a candidate requiring confirmation."
        score = 0.5
    else:
        status = "unknown"
        reason = (
            "Offering confirms the part family, but confirmed support for the "
            "requested part type is not available."
        )
        score = 0.5

    explanation = _base_explanation(
        field="part_type",
        match_type="selection",
        requested=requested_type,
        provided=record,
        status=status,
        reason=reason,
        coverage=score,
        evidence=record,
    )
    return explanation, score, status


def _evaluate_family_requirements(requirements: dict, offering: dict) -> list[dict]:
    family_capabilities = offering.get("family_capabilities", {})
    evaluations = []
    for field, requested in requirements.items():
        provided = family_capabilities.get(field)
        if field in {"gear_quality", "quality"}:
            evaluations.append(
                _evaluate_quality(
                    field=field,
                    requested=requested,
                    provided=provided,
                    match_type="part_family_specification",
                )
            )
        elif field == "bounding_box_mm":
            evaluations.append(_evaluate_bounding_box(field, requested, provided, "part_family_specification"))
        else:
            evaluations.append(
                _evaluate_range(
                    field=field,
                    requested=requested,
                    provided=provided,
                    match_type="part_family_specification",
                )
            )
    return evaluations


def _evaluate_part_type_requirements(
    requirements: dict,
    offering: dict,
    requested_part_type: str,
    part_type_status: str,
) -> list[dict]:
    if not requirements:
        return []
    if part_type_status != "matched":
        return [
            _base_explanation(
                field=field,
                match_type="part_type_specification",
                requested=requested,
                provided=None,
                status="unknown",
                reason=(
                    "Part-type-specific capability cannot be confirmed because "
                    "requested part-type support is not confirmed."
                ),
                coverage=0.0,
            )
            for field, requested in requirements.items()
        ]

    capability = offering.get("part_type_capabilities", {}).get(requested_part_type, {})
    evaluations = []
    for field, requested in requirements.items():
        provided = capability.get(field)
        if field == "bounding_box_mm":
            evaluations.append(_evaluate_bounding_box(field, requested, provided, "part_type_specification"))
        else:
            evaluations.append(
                _evaluate_range(
                    field=field,
                    requested=requested,
                    provided=provided,
                    match_type="part_type_specification",
                )
            )
    return evaluations


def _evaluate_generic_requirements(requirements: dict, provider: dict, offering: dict) -> list[dict]:
    generic = offering.get("generic_capabilities", {})
    evaluations = []
    for field, requested in requirements.items():
        if field == "materials":
            evaluations.append(
                _evaluate_list_coverage(
                    field=field,
                    requested=requested,
                    provided_records=generic.get("materials"),
                    record_key="material",
                    match_type="generic_requirement",
                )
            )
        elif field == "processes":
            evaluations.append(
                _evaluate_list_coverage(
                    field=field,
                    requested=requested,
                    provided_records=generic.get("processes"),
                    record_key="process",
                    match_type="generic_requirement",
                )
            )
        elif field == "certifications":
            evaluations.append(_evaluate_certifications(requested, provider, offering))
        elif field == "batch_size":
            evaluations.append(_evaluate_batch_size(requested, generic.get("batch_size")))
        elif field == "delivery":
            evaluations.append(
                _evaluate_max_requirement(
                    field="delivery",
                    requested=requested["max_weeks"],
                    provided=generic.get("lead_time_weeks"),
                    match_type="generic_requirement",
                    provider_max_must_be_at_least=False,
                )
            )
        elif field == "surface_finish_ra_um":
            evaluations.append(
                _evaluate_max_requirement(
                    field=field,
                    requested=requested.get("max") or requested.get("exact"),
                    provided=generic.get(field),
                    match_type="generic_requirement",
                    provider_max_must_be_at_least=False,
                )
            )
        elif field == "tolerance_mm":
            evaluations.append(
                _evaluate_max_requirement(
                    field=field,
                    requested=requested.get("max") or requested.get("exact"),
                    provided=generic.get(field),
                    match_type="generic_requirement",
                    provider_max_must_be_at_least=False,
                )
            )
        elif field == "weight_kg":
            evaluations.append(
                _evaluate_max_requirement(
                    field=field,
                    requested=requested,
                    provided=generic.get("weight_kg"),
                    match_type="generic_requirement",
                    provider_max_must_be_at_least=True,
                )
            )
        elif field == "quality":
            evaluations.append(
                _evaluate_quality(
                    field=field,
                    requested=requested,
                    provided=generic.get("quality"),
                    match_type="generic_requirement",
                )
            )
    return evaluations


def _optional_policy_satisfied(policy: str, evaluations: list[dict]) -> bool:
    if not evaluations or policy == "score_only":
        return True
    if policy == "all":
        return all(item["status"] == "matched" for item in evaluations)
    return any(item["status"] in {"matched", "partial_match"} for item in evaluations)


def _calculate_score(selection_score: float, evaluations: list[dict]) -> float:
    if not evaluations:
        return selection_score
    optional_score = sum(item.get("coverage", 0.0) for item in evaluations) / len(evaluations)
    return round((0.70 * selection_score) + (0.30 * optional_score), 3)


def _result_status(part_type_status: str, evaluations: list[dict]) -> str:
    if part_type_status == "unknown":
        return "unknown_match"
    if all(item["status"] == "matched" for item in evaluations):
        return "full_match"
    return "partial_match"


def _split_explanations(evaluations: list[dict]) -> tuple[list, list, list]:
    matched, unmatched, unknown = [], [], []
    for item in evaluations:
        if item["status"] == "matched":
            matched.append(item)
        elif item["status"] == "unknown":
            unknown.append(item)
        else:
            unmatched.append(item)
    return matched, unmatched, unknown


def _relevant_evidence(provider: dict, offering: dict) -> dict:
    evidence = {
        "family_capabilities": deepcopy(offering.get("family_capabilities", {})),
        "part_type_capabilities": deepcopy(offering.get("part_type_capabilities", {})),
        "generic_capabilities": deepcopy(offering.get("generic_capabilities", {})),
        "certifications": deepcopy(provider.get("certifications", [])),
    }
    materials = offering.get("generic_capabilities", {}).get("materials")
    if materials is not None:
        evidence["materials"] = deepcopy(materials)
    return evidence


def _build_result(
    *,
    provider: dict,
    offering: dict,
    selection: dict,
    part_type_evaluation: dict,
    selection_score: float,
    part_type_status: str,
    evaluations: list[dict],
    match_policy: dict,
) -> dict:
    category_evaluation = _base_explanation(
        field="service_category",
        match_type="selection",
        requested=selection["service_category"],
        provided=offering.get("service_category"),
        status="matched",
        reason=None,
        coverage=1.0,
    )
    family_evaluation = _base_explanation(
        field="part_family",
        match_type="selection",
        requested=selection["part_family"],
        provided=offering.get("part_family"),
        status="matched",
        reason=None,
        coverage=1.0,
    )
    all_evaluations = [category_evaluation, family_evaluation, part_type_evaluation, *evaluations]
    matched_attributes, unmatched_attributes, unknown_attributes = _split_explanations(all_evaluations)

    optional_policy = match_policy.get("optional_match_mode", "any")
    optional_policy_satisfied = _optional_policy_satisfied(optional_policy, evaluations)
    score = _calculate_score(selection_score, evaluations)

    return {
        "provider": {
            "provider_id": provider["provider_id"],
            "provider_name": provider["display_name"],
        },
        "offering": {
            "offering_id": offering["offering_id"],
            "service_category": offering["service_category"],
            "offering_name": offering["name"],
            "part_family": offering["part_family"],
        },
        "match": {
            "status": _result_status(part_type_status, evaluations),
            "score": score,
            "hard_filters_passed": True,
            "optional_policy_satisfied": optional_policy_satisfied,
        },
        "matched_attributes": matched_attributes,
        "unmatched_attributes": unmatched_attributes,
        "unknown_attributes": unknown_attributes,
        "evidence": _relevant_evidence(provider, offering),
    }


def _provider_offering_pairs(provider_records: list[dict]):
    for record in provider_records:
        provider = record.get("provider", {})
        for offering in record.get("offerings", []):
            yield provider, offering


def search_service_discovery_catalog(
    canonical_request: CanonicalServiceDiscoverySearchRequest,
    *,
    provider_records: list[dict] | None = None,
) -> dict:
    provider_records = provider_records if provider_records is not None else load_service_discovery_providers()
    request = canonical_request.to_dict()
    selection = request["selection"]
    requirements = request["requirements"]
    match_policy = request["match_policy"]

    results = []
    for provider, offering in _provider_offering_pairs(provider_records):
        if offering.get("service_category") != selection["service_category"]:
            continue
        if offering.get("part_family") != selection["part_family"]:
            continue

        part_type_evaluation, selection_score, part_type_status = _evaluate_part_type(selection, offering)

        evaluations = [
            *_evaluate_family_requirements(
                requirements.get("part_family_specifications", {}),
                offering,
            ),
            *_evaluate_part_type_requirements(
                requirements.get("part_type_specifications", {}),
                offering,
                selection["part_type"],
                part_type_status,
            ),
            *_evaluate_generic_requirements(
                requirements.get("generic_requirements", {}),
                provider,
                offering,
            ),
        ]

        if match_policy.get("unknown_policy") == "reject_unknown":
            if part_type_status == "unknown" or any(item["status"] == "unknown" for item in evaluations):
                continue

        result = _build_result(
            provider=provider,
            offering=offering,
            selection=selection,
            part_type_evaluation=part_type_evaluation,
            selection_score=selection_score,
            part_type_status=part_type_status,
            evaluations=evaluations,
            match_policy=match_policy,
        )

        minimum_score = match_policy.get("minimum_score")
        if minimum_score is not None and result["match"]["score"] < minimum_score:
            continue

        results.append(result)

    results.sort(
        key=lambda result: (
            -result["match"]["score"],
            0 if result["match"]["status"] != "unknown_match" else 1,
            result["provider"]["provider_id"],
            result["offering"]["offering_id"],
        )
    )

    return {
        "request_id": canonical_request.request_id,
        "consumer_id": canonical_request.consumer_id,
        "query_interpretation": {
            "selection": deepcopy(request["selection"]),
            "requirements": deepcopy(request["requirements"]),
            "match_policy": deepcopy(request["match_policy"]),
        },
        "warnings": deepcopy(canonical_request.warnings),
        "result_count": len(results),
        "results": results,
        "status": deepcopy(MATCHER_STATUS),
    }
