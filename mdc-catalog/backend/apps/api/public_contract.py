from copy import deepcopy
from typing import Any

from apps.ontology.service_discovery_registry import get_service_discovery_registry
from apps.ontology.vocabularies import CERTIFICATIONS, MATERIALS, PROCESSES


PUBLIC_CONTRACT_VERSION = "1.0"
SUPPORTED_CONTRACT_VERSIONS = {PUBLIC_CONTRACT_VERSION}

INTERNAL_VALUE_KEYS = {
    "source_type",
    "confidence",
    "source_note",
}


def validate_contract_version(value: Any) -> str:
    """Validate the optional public contract version and return the active version."""
    if value in (None, ""):
        return PUBLIC_CONTRACT_VERSION
    if not isinstance(value, str) or value not in SUPPORTED_CONTRACT_VERSIONS:
        raise ValueError(
            f"Unsupported contract_version '{value}'. Supported versions: "
            f"{sorted(SUPPORTED_CONTRACT_VERSIONS)}"
        )
    return value


def build_public_health_response() -> dict:
    return {
        "contract_version": PUBLIC_CONTRACT_VERSION,
        "status": "ok",
        "service": "maasai-mdc",
    }


def _public_choice(item: dict) -> dict:
    return {
        "value": item["value"],
        "label": item["label"],
    }


def build_public_catalog_filters() -> dict:
    """Return the harmonized Marketplace-facing filter contract."""
    registry = get_service_discovery_registry()
    profiles = registry["part_type_profiles"]

    part_families = [
        _public_choice(item)
        for item in registry["part_families"]
    ]
    part_types = {
        family["value"]: [
            {
                "value": part_type,
                "label": profiles[part_type]["label"],
            }
            for part_type in family["part_types"]
        ]
        for family in registry["part_families"]
    }

    return {
        "contract_version": PUBLIC_CONTRACT_VERSION,
        "service_categories": [
            _public_choice(item)
            for item in registry["service_categories"]
        ],
        "part_families": part_families,
        "part_types": part_types,
        "materials": deepcopy(MATERIALS),
        "processes": deepcopy(PROCESSES),
        "certifications": deepcopy(CERTIFICATIONS),
    }


def _public_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _public_value(item)
            for key, item in value.items()
            if key not in INTERNAL_VALUE_KEYS
        }
    if isinstance(value, list):
        return [_public_value(item) for item in value]
    return deepcopy(value)


def _public_capability(item: dict, *, include_reason: bool) -> dict:
    public = {
        "field": item.get("field"),
        "requested": _public_value(item.get("requested")),
    }
    if item.get("provided") is not None:
        public["provided"] = _public_value(item.get("provided"))
    if include_reason and item.get("reason"):
        public["reason"] = item["reason"]
    return public


def _public_result(result: dict) -> dict:
    provider = result.get("provider", {})
    offering = result.get("offering", {})
    match = result.get("match", {})

    return {
        "provider_id": provider.get("provider_id"),
        "provider_name": provider.get("provider_name"),
        "offering_id": offering.get("offering_id"),
        "offering_name": offering.get("offering_name"),
        "service_category": offering.get("service_category"),
        "part_family": offering.get("part_family"),
        "match": {
            "status": match.get("status"),
            "score": match.get("score"),
        },
        "matched_capabilities": [
            _public_capability(item, include_reason=False)
            for item in result.get("matched_attributes", [])
        ],
        "unmatched_capabilities": [
            _public_capability(item, include_reason=True)
            for item in result.get("unmatched_attributes", [])
        ],
        "unknown_capabilities": [
            _public_capability(item, include_reason=True)
            for item in result.get("unknown_attributes", [])
        ],
    }


def build_public_service_discovery_response(
    internal_response: dict,
    *,
    canonical_request: Any,
) -> dict:
    """Shape the rich H1-H9 runtime result into the stable partner response."""
    request_data = canonical_request.to_dict()
    selection = request_data["selection"]
    results = [
        _public_result(result)
        for result in internal_response.get("results", [])
    ]

    return {
        "contract_version": PUBLIC_CONTRACT_VERSION,
        "request_id": canonical_request.request_id,
        "service_category": selection["service_category"],
        "part_family": selection["part_family"],
        "part_type": selection["part_type"],
        "result_count": len(results),
        "results": results,
    }


def build_public_error(
    *,
    code: str,
    message: str,
    details: Any | None = None,
) -> dict:
    error = {
        "code": code,
        "message": message,
    }
    if details is not None:
        error["details"] = _public_value(details)
    return {
        "contract_version": PUBLIC_CONTRACT_VERSION,
        "error": error,
    }
