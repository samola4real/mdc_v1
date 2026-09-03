from __future__ import annotations

from pathlib import Path
from typing import Any

from rdflib import Graph, URIRef

from apps.ontology.service_discovery_rdf_generator import default_service_discovery_turtle_path
from apps.search.service_discovery_request import CanonicalServiceDiscoverySearchRequest
from apps.search.service_discovery_sparql_query_builder import (
    ServiceDiscoverySparqlQueryBuildError,
    build_service_discovery_candidate_query,
    build_service_discovery_evidence_query,
)


class ServiceDiscoverySparqlRetrievalError(Exception):
    pass


EVIDENCE_STATUS_ORDER = {
    "confirmed": 0,
    "candidate_requiring_confirmation": 1,
    "not_asserted": 2,
}


def load_service_discovery_rdf_graph(
    ttl_path: Path | None = None,
) -> Graph:
    ttl_path = ttl_path or default_service_discovery_turtle_path()
    if not ttl_path.exists():
        raise ServiceDiscoverySparqlRetrievalError(
            f"Harmonized service-discovery Turtle file does not exist: {ttl_path}"
        )

    graph = Graph()
    try:
        graph.parse(ttl_path, format="turtle")
    except Exception as exc:
        raise ServiceDiscoverySparqlRetrievalError(
            f"Could not parse harmonized service-discovery Turtle: {ttl_path}"
        ) from exc
    return graph


def _python_value(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "toPython"):
        return value.toPython()
    return value


def _string_value(value: Any) -> str | None:
    converted = _python_value(value)
    if converted is None:
        return None
    return str(converted)


def _row_dict(row) -> dict[str, Any]:
    if isinstance(row, dict):
        return row
    return row.asdict()


def _candidate_from_row(row, selection: dict[str, Any]) -> dict:
    data = _row_dict(row)
    support_status = _string_value(data.get("partTypeSupportStatus"))
    if support_status in {"confirmed", "candidate_requiring_confirmation"}:
        evidence_status = support_status
    elif support_status is None:
        evidence_status = "not_asserted"
    else:
        raise ServiceDiscoverySparqlRetrievalError(
            f"Unexpected requested part-type support status: {support_status}"
        )

    support = {
        "part_type": selection["part_type"],
        "evidence_status": evidence_status,
        "support_status": support_status,
        "source_type": _string_value(data.get("partTypeSourceType")),
        "confidence": _string_value(data.get("partTypeConfidence")),
    }
    if support_status is not None:
        source_note = _string_value(data.get("partTypeSourceNote"))
        if source_note is not None:
            support["source_note"] = source_note

    return {
        "_offering_resource": data["offering"],
        "provider": {
            "provider_id": _string_value(data.get("providerId")),
            "provider_name": _string_value(data.get("providerName")),
        },
        "offering": {
            "offering_id": _string_value(data.get("offeringId")),
            "offering_name": _string_value(data.get("offeringName")),
            "service_category": selection["service_category"],
            "part_family": selection["part_family"],
        },
        "requested_part_type_support": support,
        "evidence": {
            "family_capabilities": [],
            "part_type_capabilities": [],
            "generic_capabilities": [],
            "materials": [],
            "processes": [],
            "certifications": [],
        },
    }


def _capability_from_row(data: dict[str, Any]) -> dict:
    item = {
        "evidence_resource": data["evidence"],
        "field_code": _string_value(data.get("fieldCode")),
        "capability_field": data.get("capabilityField"),
    }
    optional_fields = {
        "applies_to_part_type": data.get("appliesToPartType"),
        "part_type_code": _string_value(data.get("partTypeCode")),
        "min": _python_value(data.get("minValue")),
        "max": _python_value(data.get("maxValue")),
        "exact": _python_value(data.get("exactValue")),
        "raw": _string_value(data.get("rawValue")),
        "unit": _string_value(data.get("unit")),
        "qualifier": _string_value(data.get("qualifier")),
        "approximate": _python_value(data.get("approximate")),
        "quality_standard": _string_value(data.get("qualityStandard")),
        "best_class": _python_value(data.get("bestClass")),
        "comparison_rule": _string_value(data.get("comparisonRule")),
        "normalized_order": _string_value(data.get("normalizedOrder")),
        "source_type": _string_value(data.get("sourceType")),
        "confidence": _string_value(data.get("confidence")),
        "source_note": _string_value(data.get("sourceNote")),
    }
    item.update({key: value for key, value in optional_fields.items() if value is not None})
    explicit_null_field = _string_value(data.get("explicitNullField"))
    if explicit_null_field is not None:
        item[explicit_null_field] = None
    return item


def _material_key(data: dict[str, Any]) -> tuple[URIRef, str]:
    return data["evidence"], _string_value(data.get("materialCode")) or ""


def _sequence_index(data: dict[str, Any]) -> Any:
    value = _python_value(data.get("sequenceIndex"))
    if isinstance(value, bool):
        return None
    return value if isinstance(value, int) else None


def _grade_sequence_index(data: dict[str, Any]) -> Any:
    value = _python_value(data.get("gradeSequenceIndex"))
    if isinstance(value, bool):
        return None
    return value if isinstance(value, int) else None


def _evidence_item_from_row(data: dict[str, Any]) -> dict:
    kind = _string_value(data.get("evidenceKind"))
    if kind in {"family_capability", "part_type_capability", "generic_capability"}:
        return _capability_from_row(data)
    if kind == "process":
        return {
            "evidence_resource": data["evidence"],
            "process": data.get("process"),
            "process_code": _string_value(data.get("processCode")),
            "delivery_mode": _string_value(data.get("deliveryMode")),
            "source_type": _string_value(data.get("sourceType")),
            "confidence": _string_value(data.get("confidence")),
            "_sequence_index": _sequence_index(data),
            **({"source_note": _string_value(data.get("sourceNote"))} if data.get("sourceNote") else {}),
        }
    if kind == "certification":
        return {
            "evidence_resource": data["evidence"],
            "certification": data.get("certification"),
            "certification_code": _string_value(data.get("certificationCode")),
            "evidence_scope": _string_value(data.get("evidenceScope")),
            "source_type": _string_value(data.get("sourceType")),
            "confidence": _string_value(data.get("confidence")),
            "_sequence_index": _sequence_index(data),
            **({"source_note": _string_value(data.get("sourceNote"))} if data.get("sourceNote") else {}),
        }
    raise ServiceDiscoverySparqlRetrievalError(f"Unknown evidence kind in SPARQL result: {kind}")


def _merge_capability_item(existing: dict, incoming: dict) -> None:
    for key, value in incoming.items():
        if key not in existing:
            existing[key] = value


def _sequence_sort_key(item: dict) -> tuple[int, int, str, str]:
    sequence = item.get("_sequence_index")
    if isinstance(sequence, int):
        return (0, sequence, "", str(item.get("evidence_resource")))
    return (
        1,
        0,
        str(item.get("field_code") or item.get("material_code") or item.get("process_code") or item.get("certification_code") or ""),
        str(item.get("evidence_resource")),
    )


def _strip_internal_ordering(item: dict) -> None:
    item.pop("_sequence_index", None)
    item.pop("_ordered_grades", None)
    item.pop("_flat_grades", None)


def _attach_evidence(candidates: list[dict], rows) -> None:
    by_resource = {
        candidate["_offering_resource"]: candidate
        for candidate in candidates
    }
    material_groups: dict[tuple[URIRef, str], dict] = {}

    for row in rows:
        data = _row_dict(row)
        candidate = by_resource.get(data.get("offering"))
        if candidate is None:
            continue
        evidence = candidate["evidence"]
        kind = _string_value(data.get("evidenceKind"))

        if kind == "material":
            key = _material_key(data)
            item = material_groups.get(key)
            if item is None:
                item = {
                    "evidence_resource": data["evidence"],
                    "material": data.get("material"),
                    "material_code": _string_value(data.get("materialCode")),
                    "available_grades": [],
                    "source_type": _string_value(data.get("sourceType")),
                    "confidence": _string_value(data.get("confidence")),
                    "_sequence_index": _sequence_index(data),
                    "_ordered_grades": {},
                    "_flat_grades": [],
                }
                source_note = _string_value(data.get("sourceNote"))
                if source_note is not None:
                    item["source_note"] = source_note
                material_groups[key] = item
                evidence["materials"].append(item)
            grade = _string_value(data.get("orderedAvailableGrade"))
            grade_index = _grade_sequence_index(data)
            if grade is not None and grade_index is not None:
                item["_ordered_grades"][grade_index] = grade
            flat_grade = _string_value(data.get("availableGrade"))
            if flat_grade is not None and flat_grade not in item["_flat_grades"]:
                item["_flat_grades"].append(flat_grade)
            continue

        item = _evidence_item_from_row(data)
        bucket = {
            "family_capability": "family_capabilities",
            "part_type_capability": "part_type_capabilities",
            "generic_capability": "generic_capabilities",
            "process": "processes",
            "certification": "certifications",
        }[kind]

        existing = next(
            (
                existing_item
                for existing_item in evidence[bucket]
                if existing_item["evidence_resource"] == item["evidence_resource"]
            ),
            None,
        )
        if existing is None:
            evidence[bucket].append(item)
        elif kind in {"family_capability", "part_type_capability", "generic_capability"}:
            _merge_capability_item(existing, item)

    for candidate in candidates:
        for material in candidate["evidence"]["materials"]:
            ordered_grades = material.get("_ordered_grades", {})
            if ordered_grades:
                material["available_grades"] = [
                    ordered_grades[index]
                    for index in sorted(ordered_grades)
                ]
            else:
                material["available_grades"] = sorted(material.get("_flat_grades", []))
        for bucket in candidate["evidence"].values():
            bucket.sort(key=_sequence_sort_key)
            for item in bucket:
                _strip_internal_ordering(item)


def _candidate_sort_key(candidate: dict) -> tuple[int, str, str]:
    return (
        EVIDENCE_STATUS_ORDER[candidate["requested_part_type_support"]["evidence_status"]],
        candidate["provider"]["provider_id"],
        candidate["offering"]["offering_id"],
    )


def _strip_internal(candidate: dict) -> dict:
    clean = dict(candidate)
    clean.pop("_offering_resource", None)
    return clean


def service_discovery_candidate_offering_resources(candidate_rows) -> list[URIRef]:
    resources: list[URIRef] = []
    for row in candidate_rows:
        data = _row_dict(row)
        offering = data.get("offering")
        if not isinstance(offering, URIRef):
            raise ServiceDiscoverySparqlRetrievalError(
                "Candidate SPARQL result did not include an offering URI resource."
            )
        resources.append(offering)
    return resources


def assemble_service_discovery_retrieval_projection(
    canonical_request: CanonicalServiceDiscoverySearchRequest,
    *,
    candidate_rows,
    evidence_rows,
    retrieval_engine: str,
    message: str,
) -> dict:
    request = canonical_request.to_dict()
    candidates = [
        _candidate_from_row(row, request["selection"])
        for row in candidate_rows
    ]

    if candidates:
        _attach_evidence(candidates, evidence_rows)

    candidates.sort(key=_candidate_sort_key)

    return {
        "query_interpretation": {
            "selection": request["selection"],
            "requirements": request["requirements"],
            "match_policy": request["match_policy"],
        },
        "candidates": [_strip_internal(candidate) for candidate in candidates],
        "status": {
            "retrieval_executed": True,
            "retrieval_engine": retrieval_engine,
            "matching_executed": False,
            "message": message,
        },
    }


def retrieve_service_discovery_candidates(
    canonical_request: CanonicalServiceDiscoverySearchRequest,
    *,
    graph: Graph | None = None,
    ttl_path: Path | None = None,
) -> dict:
    if graph is None:
        graph = load_service_discovery_rdf_graph(ttl_path)
    if len(graph) == 0:
        raise ServiceDiscoverySparqlRetrievalError(
            "Cannot retrieve harmonized candidates from an empty RDF graph."
        )

    try:
        candidate_query = build_service_discovery_candidate_query(canonical_request)
        candidate_rows = list(graph.query(candidate_query))
    except ServiceDiscoverySparqlQueryBuildError:
        raise
    except Exception as exc:
        raise ServiceDiscoverySparqlRetrievalError("Candidate SPARQL retrieval failed.") from exc

    evidence_rows = []
    offering_resources = service_discovery_candidate_offering_resources(candidate_rows)
    if offering_resources:
        try:
            evidence_query = build_service_discovery_evidence_query(
                offering_resources
            )
            evidence_rows = list(graph.query(evidence_query))
        except ServiceDiscoverySparqlQueryBuildError:
            raise
        except Exception as exc:
            raise ServiceDiscoverySparqlRetrievalError("Evidence SPARQL retrieval failed.") from exc

    return assemble_service_discovery_retrieval_projection(
        canonical_request,
        candidate_rows=candidate_rows,
        evidence_rows=evidence_rows,
        retrieval_engine="local_harmonized_sparql_rdflib",
        message=(
            "Candidate and evidence retrieval executed over harmonized RDF. "
            "Matching and scoring are not performed in H7."
        ),
    )
