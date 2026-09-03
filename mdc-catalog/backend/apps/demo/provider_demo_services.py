from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from rest_framework import serializers

from apps.ontology.service_discovery_registry import get_service_discovery_registry
from apps.ontology.vocabularies import (
    CERTIFICATIONS,
    MATERIALS,
    PROCESSES,
    get_vocabulary_values,
)
from apps.providers.validators import FORBIDDEN_ROUTE_KEYS


STATE_PATH = Path(__file__).resolve().parents[3] / "data" / "demo" / "provider_demo_state.json"
ALLOWED_ACTIONS = {"register_provider", "update_existing_provider"}
FORBIDDEN_DEMO_ROUTE_TERMS = {
    *FORBIDDEN_ROUTE_KEYS,
    "route",
    "operation",
    "operations",
    "machine_route",
    "process_route",
}


def _raise(message: str) -> None:
    raise serializers.ValidationError(message)


def _iter_nested(data: Any):
    if isinstance(data, dict):
        for key, value in data.items():
            yield key
            yield from _iter_nested(value)
    elif isinstance(data, list):
        for item in data:
            yield from _iter_nested(item)


def _normalized_term(value: Any) -> str:
    return str(value).strip().lower()


def _reject_forbidden_custom_field_name(name: Any, field: str) -> None:
    normalized = _normalized_term(name)
    if normalized in FORBIDDEN_DEMO_ROUTE_TERMS:
        _raise(f"{field}.name '{name}' is not accepted in demo provider payload.")


def _reject_route_fields(payload: dict[str, Any]) -> None:
    for key in _iter_nested(payload):
        if _normalized_term(key) in FORBIDDEN_DEMO_ROUTE_TERMS:
            _raise(f"Field '{key}' is not accepted in demo provider payload.")


def _registry_context() -> dict[str, Any]:
    registry = get_service_discovery_registry()
    return {
        "service_categories": {item["value"] for item in registry["service_categories"]},
        "part_families": {item["value"] for item in registry["part_families"]},
        "family_to_part_types": {
            family["value"]: set(family["part_types"])
            for family in registry["part_families"]
        },
    }


def _validate_choice(value: str, choices: set[str], field: str) -> None:
    if value not in choices:
        _raise(f"{field} has invalid value '{value}'.")


def _validate_choice_list(values: Any, choices: set[str], field: str) -> list[str]:
    if not isinstance(values, list):
        _raise(f"{field} must be a list.")
    for index, value in enumerate(values):
        if value not in choices:
            _raise(f"{field}[{index}] has invalid value '{value}'.")
    return values


def _validate_custom_fields(values: Any, field: str) -> list[dict[str, Any]]:
    if values in (None, serializers.empty):
        return []
    if not isinstance(values, list):
        _raise(f"{field} must be a list.")

    normalized = []
    for index, item in enumerate(values):
        location = f"{field}[{index}]"
        if not isinstance(item, dict):
            _raise(f"{location} must be an object.")
        name = item.get("name")
        value = item.get("value")
        if not name:
            _raise(f"{location}.name is required.")
        if value in (None, ""):
            _raise(f"{location}.value is required.")
        _reject_forbidden_custom_field_name(name, location)

        normalized_item = {
            "name": str(name),
            "value": str(value),
        }
        if "unit" in item:
            normalized_item["unit"] = "" if item["unit"] is None else str(item["unit"])
        if "notes" in item:
            normalized_item["notes"] = "" if item["notes"] is None else str(item["notes"])
        normalized.append(normalized_item)

    return normalized


def _append_custom_field(fields: list[dict[str, Any]], name: str, value: Any) -> None:
    fields.append(
        {
            "name": name,
            "value": str(value),
        }
    )


def _validate_optional_register_choice(
    *,
    value: Any,
    choices: set[str],
    field: str,
    custom_fields: list[dict[str, Any]],
    custom_name: str,
    warnings: list[str],
) -> str | None:
    if value in (None, ""):
        return None
    if value in choices:
        return value
    _append_custom_field(custom_fields, custom_name, value)
    warnings.append(
        f"{field} value '{value}' was treated as custom offering information "
        "because it is not a controlled MDC value."
    )
    return None


def _validate_optional_register_choice_list(
    *,
    values: Any,
    choices: set[str],
    field: str,
    custom_fields: list[dict[str, Any]],
    custom_name: str,
    warnings: list[str],
) -> list[str]:
    if values in (None, serializers.empty):
        return []
    if not isinstance(values, list):
        _append_custom_field(custom_fields, custom_name, values)
        warnings.append(
            f"{field} was treated as custom offering information because it is "
            "not a controlled MDC list."
        )
        return []

    valid = []
    invalid = []
    for item in values:
        if item in choices:
            valid.append(item)
        else:
            invalid.append(item)

    if invalid:
        _append_custom_field(custom_fields, custom_name, ", ".join(str(item) for item in invalid))
        warnings.append(
            f"{field} values {invalid} were treated as custom offering "
            "information because they are not controlled MDC values."
        )
    return valid


def _validate_register_capability_choice_list(
    *,
    capabilities: dict[str, Any],
    field_name: str,
    choices: set[str],
    field: str,
    custom_capability_fields: list[dict[str, Any]],
    custom_name: str,
    warnings: list[str],
) -> None:
    if field_name not in capabilities:
        return
    values = capabilities[field_name]
    if not isinstance(values, list):
        _append_custom_field(custom_capability_fields, custom_name, values)
        capabilities.pop(field_name)
        warnings.append(
            f"{field} was treated as custom capability information because it "
            "is not a controlled MDC list."
        )
        return

    valid = []
    invalid = []
    for item in values:
        if item in choices:
            valid.append(item)
        else:
            invalid.append(item)
    capabilities[field_name] = valid
    if invalid:
        _append_custom_field(custom_capability_fields, custom_name, ", ".join(str(item) for item in invalid))
        warnings.append(
            f"{field} values {invalid} were treated as custom capability "
            "information because they are not controlled MDC values."
        )


def validate_provider_demo_payload(payload: Any) -> tuple[dict[str, Any], list[str]]:
    if not isinstance(payload, dict):
        _raise("Request payload must be an object.")

    _reject_route_fields(payload)
    ctx = _registry_context()
    warnings = []
    action = payload.get("action")
    if action not in ALLOWED_ACTIONS:
        _raise("action must be register_provider or update_existing_provider.")

    provider_id = payload.get("provider_id")
    provider_name = payload.get("provider_name")
    if not provider_id:
        _raise("provider_id is required.")
    if not provider_name:
        _raise("provider_name is required.")

    certifications = _validate_choice_list(
        payload.get("certifications", []),
        get_vocabulary_values(CERTIFICATIONS),
        "certifications",
    )

    offerings = payload.get("offerings")
    if not isinstance(offerings, list) or not offerings:
        _raise("offerings must be a non-empty list.")

    normalized_offerings = []
    for index, offering in enumerate(offerings):
        if not isinstance(offering, dict):
            _raise(f"offerings[{index}] must be an object.")

        offering_id = offering.get("offering_id")
        offering_name = offering.get("offering_name")
        service_category = offering.get("service_category")
        part_family = offering.get("part_family")
        supported_part_types = offering.get("supported_part_types")
        if not offering_id:
            _raise(f"offerings[{index}].offering_id is required.")
        if not offering_name:
            _raise(f"offerings[{index}].offering_name is required.")

        custom_offering_fields = _validate_custom_fields(
            offering.get("custom_offering_fields"),
            f"offerings[{index}].custom_offering_fields",
        )

        if action == "register_provider":
            service_category = _validate_optional_register_choice(
                value=service_category,
                choices=ctx["service_categories"],
                field=f"offerings[{index}].service_category",
                custom_fields=custom_offering_fields,
                custom_name="Service category",
                warnings=warnings,
            )
            part_family = _validate_optional_register_choice(
                value=part_family,
                choices=ctx["part_families"],
                field=f"offerings[{index}].part_family",
                custom_fields=custom_offering_fields,
                custom_name="Part family",
                warnings=warnings,
            )
            supported_part_types = _validate_optional_register_choice_list(
                values=supported_part_types,
                choices=ctx["family_to_part_types"].get(part_family, set()) if part_family else set(),
                field=f"offerings[{index}].supported_part_types",
                custom_fields=custom_offering_fields,
                custom_name="Supported part types",
                warnings=warnings,
            )
        else:
            if not service_category:
                _raise(f"offerings[{index}].service_category is required.")
            if not part_family:
                _raise(f"offerings[{index}].part_family is required.")
            _validate_choice(service_category, ctx["service_categories"], f"offerings[{index}].service_category")
            _validate_choice(part_family, ctx["part_families"], f"offerings[{index}].part_family")
            supported_part_types = _validate_choice_list(
                supported_part_types,
                ctx["family_to_part_types"].get(part_family, set()),
                f"offerings[{index}].supported_part_types",
            )

        capabilities = deepcopy(offering.get("capabilities", {}))
        if not isinstance(capabilities, dict):
            _raise(f"offerings[{index}].capabilities must be an object.")
        custom_capability_fields = _validate_custom_fields(
            capabilities.get("custom_capability_fields"),
            f"offerings[{index}].capabilities.custom_capability_fields",
        )
        capabilities["custom_capability_fields"] = custom_capability_fields

        if action == "register_provider":
            _validate_register_capability_choice_list(
                capabilities=capabilities,
                field_name="materials",
                choices=get_vocabulary_values(MATERIALS),
                field=f"offerings[{index}].capabilities.materials",
                custom_capability_fields=custom_capability_fields,
                custom_name="Materials",
                warnings=warnings,
            )
            _validate_register_capability_choice_list(
                capabilities=capabilities,
                field_name="processes",
                choices=get_vocabulary_values(PROCESSES),
                field=f"offerings[{index}].capabilities.processes",
                custom_capability_fields=custom_capability_fields,
                custom_name="Processes",
                warnings=warnings,
            )
        elif "materials" in capabilities:
            capabilities["materials"] = _validate_choice_list(
                capabilities["materials"],
                get_vocabulary_values(MATERIALS),
                f"offerings[{index}].capabilities.materials",
            )
        if action != "register_provider" and "processes" in capabilities:
            capabilities["processes"] = _validate_choice_list(
                capabilities["processes"],
                get_vocabulary_values(PROCESSES),
                f"offerings[{index}].capabilities.processes",
            )

        known_keys = {
            "module",
            "outside_diameter_mm",
            "length_mm",
            "outer_diameter_mm",
            "spline_module",
            "gear_quality",
            "batch_size",
            "lead_time_weeks",
            "weight_kg",
            "materials",
            "available_grades",
            "processes",
            "custom_capability_fields",
        }
        unknown_keys = sorted(set(capabilities) - known_keys)
        if unknown_keys:
            warnings.append(
                f"offerings[{index}].capabilities contains optional/unrecognized fields: {unknown_keys}"
            )

        normalized_offerings.append(
            {
                "offering_id": offering_id,
                "offering_name": offering_name,
                "service_category": service_category,
                "part_family": part_family,
                "supported_part_types": supported_part_types,
                "support_status": offering.get("support_status", "confirmed"),
                "custom_offering_fields": custom_offering_fields,
                "capabilities": capabilities,
            }
        )

    return (
        {
            "action": action,
            "provider_id": provider_id,
            "provider_name": provider_name,
            "country": payload.get("country"),
            "publication_metadata": deepcopy(payload.get("publication_metadata", {})),
            "certifications": certifications,
            "offerings": normalized_offerings,
        },
        warnings,
    )


def preview_provider_demo_payload(payload: Any) -> dict[str, Any]:
    normalized, warnings = validate_provider_demo_payload(payload)
    return {
        "status": "valid_demo_preview",
        "mutates_state": False,
        "provider": {
            "provider_id": normalized["provider_id"],
            "provider_name": normalized["provider_name"],
        },
        "action": normalized["action"],
        "offerings": [
            {
                "offering_id": item["offering_id"],
                "offering_name": item["offering_name"],
                "service_category": item.get("service_category"),
                "part_family": item.get("part_family"),
            }
            for item in normalized["offerings"]
        ],
        "normalized_payload": normalized,
        "warnings": warnings,
    }


def _load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"providers": {}, "updates": {}, "last_updated": None}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def read_provider_demo_state() -> dict[str, Any]:
    exists = STATE_PATH.exists()
    state = _load_state()
    return {
        "status": (
            "demo_provider_state_loaded"
            if exists
            else "demo_provider_state_empty"
        ),
        "state_path": "data/demo/provider_demo_state.json",
        "providers": deepcopy(state.get("providers", {})),
        "updates": deepcopy(state.get("updates", {})),
        "last_updated": state.get("last_updated"),
    }


def _save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def simulate_provider_demo_update(payload: Any) -> dict[str, Any]:
    normalized, warnings = validate_provider_demo_payload(payload)
    state = _load_state()
    now = datetime.now(timezone.utc).isoformat()
    provider_id = normalized["provider_id"]

    if normalized["action"] == "register_provider":
        state.setdefault("providers", {})[provider_id] = normalized
        result_status = "registered_provider_saved_for_demo"
    else:
        state.setdefault("updates", {})[provider_id] = normalized
        result_status = "existing_provider_update_saved_for_demo"

    state["last_updated"] = now
    _save_state(state)

    return {
        "status": result_status,
        "mutates_state": True,
        "state_path": str(STATE_PATH),
        "provider": {
            "provider_id": provider_id,
            "provider_name": normalized["provider_name"],
        },
        "action": normalized["action"],
        "offerings": [
            {
                "offering_id": item["offering_id"],
                "offering_name": item["offering_name"],
            }
            for item in normalized["offerings"]
        ],
        "warnings": warnings,
        "last_updated": now,
    }
