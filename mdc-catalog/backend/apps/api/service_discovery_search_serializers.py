from copy import deepcopy
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


ALLOWED_OPTIONAL_MATCH_MODES = {
    "any",
    "all",
    "score_only",
}

ALLOWED_UNKNOWN_POLICIES = {
    "keep_as_unknown",
    "reject_unknown",
}

REQUEST_TOP_LEVEL_FIELDS = {
    "request_id",
    "consumer_id",
    "service_category",
    "part_family",
    "part_type",
    "requirements",
    "match_policy",
}

REQUIREMENT_GROUPS = {
    "part_family_specifications",
    "part_type_specifications",
    "generic_requirements",
}

GENERIC_REQUIREMENT_FIELDS = {
    "materials",
    "processes",
    "batch_size",
    "delivery",
    "certifications",
    "surface_finish_ra_um",
    "tolerance_mm",
    "quality",
    "weight_kg",
}


def _raise(message: str) -> None:
    raise serializers.ValidationError(message)


def _format_path(path: tuple[Any, ...]) -> str:
    output = "$"
    for part in path:
        if isinstance(part, int):
            output += f"[{part}]"
        else:
            output += f".{part}"
    return output


def _iter_nested(data: Any, path: tuple[Any, ...] = ()):
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = (*path, key)
            yield key, value, current_path
            yield from _iter_nested(value, current_path)
    elif isinstance(data, list):
        for index, value in enumerate(data):
            yield from _iter_nested(value, (*path, index))


def _reject_forbidden_fields(data: Any) -> None:
    for key, _value, path in _iter_nested(data):
        if key in FORBIDDEN_ROUTE_KEYS:
            _raise(f"Field '{key}' is not accepted at {_format_path(path)}.")


def _reject_unknown_keys(data: dict[str, Any], allowed: set[str], *, location: str) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        _raise(f"{location} contains unknown fields: {unknown}")


def _registry_context() -> dict[str, Any]:
    registry = get_service_discovery_registry()
    return {
        "registry": registry,
        "service_category_to_family": {
            category["value"]: category["part_family"]
            for category in registry["service_categories"]
        },
        "family_to_part_types": {
            family["value"]: set(family["part_types"])
            for family in registry["part_families"]
        },
        "part_type_profiles": registry["part_type_profiles"],
        "field_definitions": registry["field_definitions"],
    }


def _validate_positive_number(value: Any, *, location: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _raise(f"{location} must be a positive number.")
    if value <= 0:
        _raise(f"{location} must be positive.")
    return float(value)


def _validate_positive_integer(value: Any, *, location: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _raise(f"{location} must be a positive integer.")
    if value <= 0:
        _raise(f"{location} must be positive.")
    return value


def _validate_range_or_exact(data: Any, *, location: str, integer: bool = False) -> dict:
    if not isinstance(data, dict):
        _raise(f"{location} must be an object.")

    allowed = {"min", "max", "exact"}
    _reject_unknown_keys(data, allowed, location=location)

    if not set(data) & allowed:
        _raise(f"{location} must include at least one of min, max, or exact.")

    normalized = {}
    for key in ["min", "max", "exact"]:
        if key not in data:
            continue
        child_location = f"{location}.{key}"
        if integer:
            normalized[key] = _validate_positive_integer(data[key], location=child_location)
        else:
            normalized[key] = _validate_positive_number(data[key], location=child_location)

    min_value = normalized.get("min")
    max_value = normalized.get("max")
    exact_value = normalized.get("exact")

    if min_value is not None and max_value is not None and min_value > max_value:
        _raise(f"{location}.min must be less than or equal to max.")
    if exact_value is not None and min_value is not None and exact_value < min_value:
        _raise(f"{location}.exact must be greater than or equal to min.")
    if exact_value is not None and max_value is not None and exact_value > max_value:
        _raise(f"{location}.exact must be less than or equal to max.")

    return normalized


def _validate_quality(data: Any, *, location: str) -> dict:
    if not isinstance(data, dict):
        _raise(f"{location} must be an object.")

    allowed = {"standard", "max_class"}
    _reject_unknown_keys(data, allowed, location=location)

    standard = data.get("standard")
    if not isinstance(standard, str) or not standard.strip():
        _raise(f"{location}.standard is required.")

    max_class = data.get("max_class")
    if max_class is None:
        _raise(f"{location}.max_class is required.")

    return {
        "standard": standard,
        "max_class": _validate_positive_number(max_class, location=f"{location}.max_class"),
    }


def _validate_bounding_box(data: Any, *, location: str) -> dict:
    if not isinstance(data, dict):
        _raise(f"{location} must be an object.")

    allowed = {"length_mm", "width_mm", "height_mm"}
    _reject_unknown_keys(data, allowed, location=location)

    if not set(data) & allowed:
        _raise(f"{location} must include at least one bounding-box component.")

    return {
        key: _validate_range_or_exact(value, location=f"{location}.{key}")
        for key, value in data.items()
    }


def _validate_field_value(
    field_name: str,
    value: Any,
    *,
    location: str,
    field_definitions: dict[str, dict],
) -> Any:
    definition = field_definitions[field_name]
    input_shape = definition["input_shape"]

    if input_shape == "range_or_exact":
        return _validate_range_or_exact(value, location=location)
    if input_shape == "positive_integer_range_or_exact":
        return _validate_range_or_exact(value, location=location, integer=True)
    if input_shape == "quality_standard_and_class":
        return _validate_quality(value, location=location)
    if input_shape == "composite_dimensions":
        return _validate_bounding_box(value, location=location)
    if input_shape == "positive_number":
        return _validate_positive_number(value, location=location)
    if input_shape == "positive_integer":
        return _validate_positive_integer(value, location=location)

    _raise(f"{location} uses unsupported input shape '{input_shape}'.")


def _validate_selection(data: dict[str, Any], context: dict[str, Any]) -> None:
    service_category = data["service_category"]
    part_family = data["part_family"]
    part_type = data["part_type"]

    category_to_family = context["service_category_to_family"]
    if service_category not in category_to_family:
        _raise(f"service_category has invalid value '{service_category}'.")

    expected_family = category_to_family[service_category]
    if part_family != expected_family:
        _raise(
            f"part_family must be '{expected_family}' for service_category "
            f"'{service_category}'."
        )

    allowed_part_types = context["family_to_part_types"][part_family]
    if part_type not in allowed_part_types:
        _raise(f"part_type '{part_type}' does not belong to part_family '{part_family}'.")


def _default_requirements() -> dict:
    return {
        "part_family_specifications": {},
        "part_type_specifications": {},
        "generic_requirements": {},
    }


def _validate_requirements(
    requirements: Any,
    *,
    part_type: str,
    context: dict[str, Any],
) -> dict:
    if requirements in (None, serializers.empty):
        requirements = {}

    if not isinstance(requirements, dict):
        _raise("requirements must be an object.")

    _reject_unknown_keys(requirements, REQUIREMENT_GROUPS, location="requirements")

    normalized = _default_requirements()
    for group_name in REQUIREMENT_GROUPS:
        value = requirements.get(group_name, {})
        if not isinstance(value, dict):
            _raise(f"requirements.{group_name} must be an object.")
        normalized[group_name] = deepcopy(value)

    family_specs = normalized["part_family_specifications"]
    part_type_specs = normalized["part_type_specifications"]
    generic_requirements = normalized["generic_requirements"]

    profile = context["part_type_profiles"][part_type]
    family_fields = set(profile["family_common_fields"])
    part_type_fields = set(profile["part_type_specific_fields"])
    scoped_fields = family_fields | part_type_fields
    field_definitions = context["field_definitions"]

    duplicate_fields = (
        (set(family_specs) & set(part_type_specs))
        | (set(family_specs) & set(generic_requirements))
        | (set(part_type_specs) & set(generic_requirements))
    )
    if duplicate_fields:
        _raise(f"Requirement fields are duplicated across groups: {sorted(duplicate_fields)}")

    for field_name, value in list(family_specs.items()):
        if field_name not in family_fields:
            _raise(f"{field_name} is not valid in part_family_specifications.")
        family_specs[field_name] = _validate_field_value(
            field_name,
            value,
            location=f"requirements.part_family_specifications.{field_name}",
            field_definitions=field_definitions,
        )

    for field_name, value in list(part_type_specs.items()):
        if field_name not in part_type_fields:
            _raise(f"{field_name} is not valid in part_type_specifications.")
        part_type_specs[field_name] = _validate_field_value(
            field_name,
            value,
            location=f"requirements.part_type_specifications.{field_name}",
            field_definitions=field_definitions,
        )

    for field_name, value in list(generic_requirements.items()):
        if field_name == "material_grades":
            _raise("material_grades is not accepted as a harmonized search criterion.")
        if field_name not in GENERIC_REQUIREMENT_FIELDS:
            _raise(f"{field_name} is not valid in generic_requirements.")
        if field_name in scoped_fields:
            _raise(
                f"{field_name} must be supplied in its scoped specification group "
                "for the selected part type."
            )
        generic_requirements[field_name] = _validate_generic_requirement(
            field_name,
            value,
            location=f"requirements.generic_requirements.{field_name}",
            field_definitions=field_definitions,
        )

    return normalized


def _validate_string_choice_list(
    value: Any,
    *,
    choices: set[str],
    location: str,
) -> list[str]:
    if not isinstance(value, list):
        _raise(f"{location} must be a list.")

    normalized = []
    for index, item in enumerate(value):
        if item not in choices:
            _raise(f"{location}[{index}] has invalid value '{item}'.")
        normalized.append(item)
    return normalized


def _validate_delivery(value: Any, *, location: str) -> dict:
    if not isinstance(value, dict):
        _raise(f"{location} must be an object.")
    _reject_unknown_keys(value, {"max_weeks"}, location=location)
    if "max_weeks" not in value:
        _raise(f"{location}.max_weeks is required.")
    return {
        "max_weeks": _validate_positive_number(value["max_weeks"], location=f"{location}.max_weeks")
    }


def _validate_generic_requirement(
    field_name: str,
    value: Any,
    *,
    location: str,
    field_definitions: dict[str, dict],
) -> Any:
    if field_name == "materials":
        return _validate_string_choice_list(
            value,
            choices=get_vocabulary_values(MATERIALS),
            location=location,
        )
    if field_name == "processes":
        return _validate_string_choice_list(
            value,
            choices=get_vocabulary_values(PROCESSES),
            location=location,
        )
    if field_name == "certifications":
        return _validate_string_choice_list(
            value,
            choices=get_vocabulary_values(CERTIFICATIONS),
            location=location,
        )
    if field_name == "batch_size":
        return _validate_positive_integer(value, location=location)
    if field_name == "delivery":
        return _validate_delivery(value, location=location)
    if field_name == "surface_finish_ra_um":
        return _validate_field_value(
            "surface_finish_ra_um",
            value,
            location=location,
            field_definitions=field_definitions,
        )
    if field_name == "tolerance_mm":
        return _validate_field_value(
            "tolerance_mm",
            value,
            location=location,
            field_definitions=field_definitions,
        )
    if field_name == "weight_kg":
        return _validate_positive_number(value, location=location)
    if field_name == "quality":
        return _validate_quality(value, location=location)

    _raise(f"{field_name} is not supported in generic_requirements.")


def _default_match_policy() -> dict:
    return {
        "optional_match_mode": "any",
        "unknown_policy": "keep_as_unknown",
        "minimum_score": None,
    }


def _validate_match_policy(value: Any) -> dict:
    if value in (None, serializers.empty):
        value = {}

    if not isinstance(value, dict):
        _raise("match_policy must be an object.")

    allowed = {"optional_match_mode", "unknown_policy", "minimum_score"}
    if "primary_match_mode" in value:
        _raise("primary_match_mode is not accepted in the harmonized request contract.")
    _reject_unknown_keys(value, allowed, location="match_policy")

    normalized = _default_match_policy()

    optional_match_mode = value.get("optional_match_mode", normalized["optional_match_mode"])
    if optional_match_mode not in ALLOWED_OPTIONAL_MATCH_MODES:
        _raise("match_policy.optional_match_mode has an invalid value.")
    normalized["optional_match_mode"] = optional_match_mode

    unknown_policy = value.get("unknown_policy", normalized["unknown_policy"])
    if unknown_policy not in ALLOWED_UNKNOWN_POLICIES:
        _raise("match_policy.unknown_policy has an invalid value.")
    normalized["unknown_policy"] = unknown_policy

    if "minimum_score" in value:
        minimum_score = value["minimum_score"]
        if minimum_score is None:
            normalized["minimum_score"] = None
        elif isinstance(minimum_score, bool) or not isinstance(minimum_score, (int, float)):
            _raise("match_policy.minimum_score must be a number or null.")
        elif minimum_score < 0 or minimum_score > 1:
            _raise("match_policy.minimum_score must be between 0 and 1.")
        else:
            normalized["minimum_score"] = float(minimum_score)

    return normalized


class ServiceDiscoverySearchRequestSerializer(serializers.Serializer):
    request_id = serializers.CharField(required=True, allow_blank=False)
    consumer_id = serializers.CharField(required=True, allow_blank=False)
    service_category = serializers.CharField(required=True, allow_blank=False)
    part_family = serializers.CharField(required=True, allow_blank=False)
    part_type = serializers.CharField(required=True, allow_blank=False)
    requirements = serializers.DictField(required=False, default=dict)
    match_policy = serializers.DictField(required=False, default=dict)

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            _raise("Request payload must be an object.")
        _reject_forbidden_fields(data)
        _reject_unknown_keys(data, REQUEST_TOP_LEVEL_FIELDS, location="request")
        return super().to_internal_value(data)

    def validate(self, attrs):
        context = _registry_context()
        _validate_selection(attrs, context)
        attrs["requirements"] = _validate_requirements(
            attrs.get("requirements", {}),
            part_type=attrs["part_type"],
            context=context,
        )
        attrs["match_policy"] = _validate_match_policy(attrs.get("match_policy", {}))
        return attrs


RESPONSE_TOP_LEVEL_FIELDS = {
    "request_id",
    "consumer_id",
    "query_interpretation",
    "warnings",
    "result_count",
    "results",
    "status",
}

RESULT_FIELDS = {
    "provider",
    "offering",
    "match",
    "matched_attributes",
    "unmatched_attributes",
    "unknown_attributes",
    "evidence",
}


def _validate_query_interpretation(data: Any) -> dict:
    if not isinstance(data, dict):
        _raise("query_interpretation must be an object.")
    _reject_unknown_keys(data, {"selection", "requirements", "match_policy"}, location="query_interpretation")

    selection = data.get("selection")
    if not isinstance(selection, dict):
        _raise("query_interpretation.selection is required.")
    _reject_unknown_keys(
        selection,
        {"service_category", "part_family", "part_type"},
        location="query_interpretation.selection",
    )
    for field in ["service_category", "part_family", "part_type"]:
        if field not in selection:
            _raise(f"query_interpretation.selection.{field} is required.")

    context = _registry_context()
    _validate_selection(selection, context)

    requirements = _validate_requirements(
        data.get("requirements", {}),
        part_type=selection["part_type"],
        context=context,
    )
    match_policy = _validate_match_policy(data.get("match_policy", {}))

    return {
        "selection": deepcopy(selection),
        "requirements": requirements,
        "match_policy": match_policy,
    }


def _validate_material_evidence(data: Any, *, location: str) -> dict:
    if not isinstance(data, dict):
        _raise(f"{location} must be an object.")
    allowed = {"material", "available_grades", "source_type", "confidence", "source_note"}
    _reject_unknown_keys(data, allowed, location=location)

    material = data.get("material")
    if material not in get_vocabulary_values(MATERIALS):
        _raise(f"{location}.material has invalid value '{material}'.")

    grades = data.get("available_grades", [])
    if not isinstance(grades, list):
        _raise(f"{location}.available_grades must be a list.")
    for index, grade in enumerate(grades):
        if not isinstance(grade, str) or not grade.strip():
            _raise(f"{location}.available_grades[{index}] must be a non-empty string.")

    return deepcopy(data)


def _validate_evidence(data: Any, *, location: str) -> dict:
    if not isinstance(data, dict):
        _raise(f"{location} must be an object.")
    if "material_grades" in data:
        _raise(f"{location}.material_grades is not accepted; use materials[].available_grades.")

    evidence = deepcopy(data)
    if "materials" in evidence:
        if not isinstance(evidence["materials"], list):
            _raise(f"{location}.materials must be a list.")
        evidence["materials"] = [
            _validate_material_evidence(item, location=f"{location}.materials[{index}]")
            for index, item in enumerate(evidence["materials"])
        ]
    return evidence


def _validate_result(data: Any, *, location: str) -> dict:
    if not isinstance(data, dict):
        _raise(f"{location} must be an object.")
    _reject_unknown_keys(data, RESULT_FIELDS, location=location)

    for field in RESULT_FIELDS:
        if field not in data:
            _raise(f"{location}.{field} is required.")

    provider = data["provider"]
    if not isinstance(provider, dict):
        _raise(f"{location}.provider must be an object.")
    _reject_unknown_keys(provider, {"provider_id", "provider_name"}, location=f"{location}.provider")
    if "provider_name" not in provider:
        _raise(f"{location}.provider.provider_name is required.")
    if "provider_id" not in provider:
        _raise(f"{location}.provider.provider_id is required.")

    offering = data["offering"]
    if not isinstance(offering, dict):
        _raise(f"{location}.offering must be an object.")
    _reject_unknown_keys(
        offering,
        {"offering_id", "service_category", "offering_name", "part_family"},
        location=f"{location}.offering",
    )
    for field in ["offering_id", "service_category", "offering_name", "part_family"]:
        if field not in offering:
            _raise(f"{location}.offering.{field} is required.")

    match = data["match"]
    if not isinstance(match, dict):
        _raise(f"{location}.match must be an object.")
    if "score" in match:
        score = match["score"]
        if isinstance(score, bool) or not isinstance(score, (int, float)) or score < 0 or score > 1:
            _raise(f"{location}.match.score must be between 0 and 1.")
    if "hard_filters_passed" in match and not isinstance(match["hard_filters_passed"], bool):
        _raise(f"{location}.match.hard_filters_passed must be boolean.")
    if "optional_policy_satisfied" in match and not isinstance(
        match["optional_policy_satisfied"],
        bool,
    ):
        _raise(f"{location}.match.optional_policy_satisfied must be boolean.")

    for field in ["matched_attributes", "unmatched_attributes", "unknown_attributes"]:
        if not isinstance(data[field], list):
            _raise(f"{location}.{field} must be a list.")

    normalized = deepcopy(data)
    normalized["evidence"] = _validate_evidence(data["evidence"], location=f"{location}.evidence")
    return normalized


class ServiceDiscoverySearchResponseSerializer(serializers.Serializer):
    request_id = serializers.CharField(required=True, allow_blank=False)
    consumer_id = serializers.CharField(required=True, allow_blank=False)
    query_interpretation = serializers.DictField(required=True)
    warnings = serializers.ListField(required=True)
    result_count = serializers.IntegerField(required=True, min_value=0)
    results = serializers.ListField(child=serializers.DictField(), required=True)
    status = serializers.DictField(required=True)

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            _raise("Response payload must be an object.")
        _reject_forbidden_fields(data)
        _reject_unknown_keys(data, RESPONSE_TOP_LEVEL_FIELDS, location="response")
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs["query_interpretation"] = _validate_query_interpretation(
            attrs["query_interpretation"]
        )

        if not isinstance(attrs["status"], dict):
            _raise("status must be an object.")
        _reject_unknown_keys(
            attrs["status"],
            {"search_executed", "search_engine", "message"},
            location="status",
        )
        if "search_executed" not in attrs["status"]:
            _raise("status.search_executed is required.")
        if not isinstance(attrs["status"]["search_executed"], bool):
            _raise("status.search_executed must be boolean.")
        if attrs["status"]["search_executed"] and "search_engine" not in attrs["status"]:
            _raise("status.search_engine is required when search_executed is true.")
        if "search_engine" in attrs["status"]:
            search_engine = attrs["status"]["search_engine"]
            if not isinstance(search_engine, str) or not search_engine.strip():
                _raise("status.search_engine must be a non-empty string.")
        if "message" not in attrs["status"]:
            _raise("status.message is required.")

        attrs["results"] = [
            _validate_result(result, location=f"results[{index}]")
            for index, result in enumerate(attrs["results"])
        ]

        return attrs
