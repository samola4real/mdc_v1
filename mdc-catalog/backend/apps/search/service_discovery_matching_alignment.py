from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from typing import Any

from rdflib import Graph

from apps.api.service_discovery_search_serializers import ServiceDiscoverySearchResponseSerializer
from apps.search.service_discovery_fuseki_service import retrieve_service_discovery_candidates_from_fuseki
from apps.search.service_discovery_local_matcher import search_service_discovery_catalog
from apps.search.service_discovery_request import CanonicalServiceDiscoverySearchRequest
from apps.search.service_discovery_sparql_service import retrieve_service_discovery_candidates


class ServiceDiscoveryMatchingAlignmentError(Exception):
    pass


LOCAL_RDF_H5_STATUS = {
    "search_executed": True,
    "search_engine": "harmonized_rdf_rdflib_with_h5_policy",
    "message": (
        "Search executed using H5 matching policy over evidence retrieved from "
        "the harmonized RDFLib SPARQL layer."
    ),
}

REMOTE_FUSEKI_H5_STATUS = {
    "search_executed": True,
    "search_engine": "harmonized_fuseki_with_h5_policy",
    "message": (
        "Search executed using H5 matching policy over evidence retrieved from "
        "the dedicated harmonized Fuseki dataset."
    ),
}


def _require_dict(value: Any, *, location: str) -> dict:
    if not isinstance(value, dict):
        raise ServiceDiscoveryMatchingAlignmentError(f"{location} must be an object.")
    return value


def _require_list(value: Any, *, location: str) -> list:
    if not isinstance(value, list):
        raise ServiceDiscoveryMatchingAlignmentError(f"{location} must be a list.")
    return value


def _validate_projection(
    canonical_request: CanonicalServiceDiscoverySearchRequest,
    retrieval_projection: dict,
) -> None:
    projection = _require_dict(retrieval_projection, location="retrieval_projection")
    query_interpretation = _require_dict(
        projection.get("query_interpretation"),
        location="retrieval_projection.query_interpretation",
    )
    selection = _require_dict(
        query_interpretation.get("selection"),
        location="retrieval_projection.query_interpretation.selection",
    )
    if selection != canonical_request.selection:
        raise ServiceDiscoveryMatchingAlignmentError(
            "Retrieval projection selection does not match the canonical request selection."
        )

    status = _require_dict(projection.get("status"), location="retrieval_projection.status")
    if status.get("retrieval_executed") is not True:
        raise ServiceDiscoveryMatchingAlignmentError(
            "Retrieval projection must have status.retrieval_executed set to true."
        )
    if status.get("matching_executed") is not False:
        raise ServiceDiscoveryMatchingAlignmentError(
            "Retrieval projection must have status.matching_executed set to false."
        )

    _require_list(projection.get("candidates"), location="retrieval_projection.candidates")


def _capability_record(item: dict) -> dict:
    field = item.get("field_code")
    if not field:
        raise ServiceDiscoveryMatchingAlignmentError("Capability evidence is missing field_code.")

    record: dict[str, Any] = {}
    for source_key, target_key in [
        ("min", "min"),
        ("max", "max"),
        ("exact", "exact"),
        ("raw", "raw"),
        ("unit", "unit"),
        ("qualifier", "qualifier"),
        ("approximate", "approximate"),
        ("quality_standard", "standard"),
        ("best_class", "best_class"),
        ("comparison_rule", "comparison_rule"),
        ("normalized_order", "normalized_order"),
        ("source_type", "source_type"),
        ("confidence", "confidence"),
        ("source_note", "source_note"),
    ]:
        if source_key in item:
            record[target_key] = _provider_record_value(item[source_key])
    return record


def _provider_record_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    return value


def _material_record(item: dict) -> dict:
    material = item.get("material_code")
    if not material:
        raise ServiceDiscoveryMatchingAlignmentError("Material evidence is missing material_code.")

    record = {"material": material}
    for key in ["available_grades", "source_type", "confidence", "source_note"]:
        if key in item:
            record[key] = deepcopy(item[key])
    return record


def _process_record(item: dict) -> dict:
    process = item.get("process_code")
    if not process:
        raise ServiceDiscoveryMatchingAlignmentError("Process evidence is missing process_code.")

    record = {"process": process}
    for source_key, target_key in [
        ("delivery_mode", "delivery_mode"),
        ("source_type", "source_type"),
        ("confidence", "confidence"),
        ("source_note", "source_note"),
    ]:
        if source_key in item:
            record[target_key] = item[source_key]
    return record


def _certification_record(item: dict) -> dict | None:
    if item.get("evidence_scope") not in {None, "provider"}:
        return None
    code = item.get("certification_code")
    if not code:
        raise ServiceDiscoveryMatchingAlignmentError("Certification evidence is missing certification_code.")

    record = {"code": code}
    for key in ["source_type", "confidence", "source_note"]:
        if key in item:
            record[key] = item[key]
    return record


def _reconstruct_offering(candidate: dict, requested_part_type: str) -> dict:
    offering_projection = _require_dict(candidate.get("offering"), location="candidate.offering")
    evidence = _require_dict(candidate.get("evidence"), location="candidate.evidence")

    offering = {
        "offering_id": offering_projection.get("offering_id"),
        "provider_id": candidate["provider"]["provider_id"],
        "service_category": offering_projection.get("service_category"),
        "name": offering_projection.get("offering_name"),
        "part_family": offering_projection.get("part_family"),
        "supported_part_types": [],
        "family_capabilities": {},
        "part_type_capabilities": {},
        "generic_capabilities": {},
    }
    if "support_status" in offering_projection:
        offering["support_status"] = offering_projection["support_status"]

    support = _require_dict(
        candidate.get("requested_part_type_support"),
        location="candidate.requested_part_type_support",
    )
    evidence_status = support.get("evidence_status")
    if evidence_status in {"confirmed", "candidate_requiring_confirmation"}:
        if support.get("support_status") != evidence_status:
            raise ServiceDiscoveryMatchingAlignmentError(
                "Requested part-type evidence status and support_status differ."
            )
        support_record = {
            "part_type": requested_part_type,
            "support_status": evidence_status,
        }
        for key in ["source_type", "confidence", "source_note"]:
            if support.get(key) is not None:
                support_record[key] = support[key]
        offering["supported_part_types"].append(support_record)
    elif evidence_status != "not_asserted":
        raise ServiceDiscoveryMatchingAlignmentError(
            f"Unexpected requested part-type evidence status: {evidence_status}"
        )

    for item in _require_list(evidence.get("family_capabilities"), location="candidate.evidence.family_capabilities"):
        item = _require_dict(item, location="family capability evidence")
        offering["family_capabilities"][item["field_code"]] = _capability_record(item)

    for item in _require_list(
        evidence.get("part_type_capabilities"),
        location="candidate.evidence.part_type_capabilities",
    ):
        item = _require_dict(item, location="part-type capability evidence")
        part_type = item.get("part_type_code")
        if not part_type:
            raise ServiceDiscoveryMatchingAlignmentError(
                "Part-type capability evidence is missing part_type_code."
            )
        offering["part_type_capabilities"].setdefault(part_type, {})[item["field_code"]] = _capability_record(item)

    for item in _require_list(
        evidence.get("generic_capabilities"),
        location="candidate.evidence.generic_capabilities",
    ):
        item = _require_dict(item, location="generic capability evidence")
        offering["generic_capabilities"][item["field_code"]] = _capability_record(item)

    materials = [
        _material_record(_require_dict(item, location="material evidence"))
        for item in _require_list(evidence.get("materials"), location="candidate.evidence.materials")
    ]
    if materials:
        offering["generic_capabilities"]["materials"] = materials

    processes = [
        _process_record(_require_dict(item, location="process evidence"))
        for item in _require_list(evidence.get("processes"), location="candidate.evidence.processes")
    ]
    if processes:
        offering["generic_capabilities"]["processes"] = processes

    for key in ["offering_id", "provider_id", "service_category", "name", "part_family"]:
        if not offering.get(key):
            raise ServiceDiscoveryMatchingAlignmentError(f"Reconstructed offering is missing {key}.")

    return offering


def build_request_scoped_provider_records_from_retrieval(
    canonical_request: CanonicalServiceDiscoverySearchRequest,
    retrieval_projection: dict,
) -> list[dict]:
    _validate_projection(canonical_request, retrieval_projection)

    requested_part_type = canonical_request.selection["part_type"]
    providers: dict[str, dict] = {}

    for candidate in retrieval_projection["candidates"]:
        candidate = _require_dict(candidate, location="retrieval_projection.candidates[]")
        provider_projection = _require_dict(candidate.get("provider"), location="candidate.provider")
        provider_id = provider_projection.get("provider_id")
        provider_name = provider_projection.get("provider_name")
        if not provider_id or not provider_name:
            raise ServiceDiscoveryMatchingAlignmentError("Candidate provider identity is incomplete.")

        provider_record = providers.setdefault(
            provider_id,
            {
                "provider": {
                    "provider_id": provider_id,
                    "display_name": provider_name,
                    "certifications": [],
                },
                "offerings": [],
            },
        )

        offering = _reconstruct_offering(candidate, requested_part_type)
        provider_record["offerings"].append(offering)

        certifications = candidate["evidence"].get("certifications", [])
        for item in _require_list(certifications, location="candidate.evidence.certifications"):
            certification = _certification_record(_require_dict(item, location="certification evidence"))
            if certification is None:
                continue
            if certification not in provider_record["provider"]["certifications"]:
                provider_record["provider"]["certifications"].append(certification)

    for provider_record in providers.values():
        provider_record["offerings"].sort(key=lambda item: item["offering_id"])

    return [providers[key] for key in sorted(providers)]


def _validate_search_response(response: dict) -> None:
    serializer = ServiceDiscoverySearchResponseSerializer(data=response)
    if not serializer.is_valid():
        raise ServiceDiscoveryMatchingAlignmentError(
            f"H9 matching response is not compatible with the H4/H5 response serializer: {serializer.errors}"
        )


def _with_status(response: dict, status: dict) -> dict:
    aligned = deepcopy(response)
    aligned["status"] = deepcopy(status)
    _validate_search_response(aligned)
    return aligned


def search_service_discovery_catalog_via_local_rdf(
    canonical_request: CanonicalServiceDiscoverySearchRequest,
    *,
    graph: Graph | None = None,
    ttl_path: Path | None = None,
) -> dict:
    retrieval_projection = retrieve_service_discovery_candidates(
        canonical_request,
        graph=graph,
        ttl_path=ttl_path,
    )
    provider_records = build_request_scoped_provider_records_from_retrieval(
        canonical_request,
        retrieval_projection,
    )
    response = search_service_discovery_catalog(
        canonical_request,
        provider_records=provider_records,
    )
    return _with_status(response, LOCAL_RDF_H5_STATUS)


def search_service_discovery_catalog_via_fuseki(
    canonical_request: CanonicalServiceDiscoverySearchRequest,
    *,
    endpoint: str | None = None,
    timeout_seconds: float = 10.0,
) -> dict:
    retrieval_projection = retrieve_service_discovery_candidates_from_fuseki(
        canonical_request,
        endpoint=endpoint,
        timeout_seconds=timeout_seconds,
    )
    provider_records = build_request_scoped_provider_records_from_retrieval(
        canonical_request,
        retrieval_projection,
    )
    response = search_service_discovery_catalog(
        canonical_request,
        provider_records=provider_records,
    )
    return _with_status(response, REMOTE_FUSEKI_H5_STATUS)


def normalize_search_response_for_alignment_comparison(
    response: dict,
) -> dict:
    normalized = deepcopy(response)
    status = normalized.get("status")
    if isinstance(status, dict):
        status.pop("search_engine", None)
        status.pop("message", None)
    return normalized
