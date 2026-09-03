import re
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


PROVIDER_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")

OWNED_IDENTIFIER_FIELDS = {
    "offering_id",
    "facility_id",
    "material_id",
    "grade_id",
}

ALLOWED_SOURCE_TYPES = {
    "provider_confirmed",
    "public_web",
    "curated",
    "not_confirmed",
}

ALLOWED_CONFIDENCE_VALUES = {
    "declared",
    "publicly_confirmed",
    "curated",
    "inferred",
    "unknown",
}

ALLOWED_SUPPORT_STATUSES = {
    "confirmed",
    "candidate_requiring_confirmation",
    "unknown",
}

ALLOWED_DELIVERY_MODES = {
    "in_house",
    "subcontracted",
    "unspecified",
}

ALLOWED_GENERIC_CAPABILITY_FIELDS = {
    "materials",
    "processes",
    "batch_size",
    "lead_time_weeks",
    "certifications",
    "surface_finish_ra_um",
    "tolerance_mm",
    "quality",
    "weight_kg",
}

ALLOWED_QUALITY_STANDARDS = {
    "AGMA",
    "DIN",
    "ISO",
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
            _raise(
                f"Field '{key}' is not accepted in the harmonized "
                f"provider-publication contract at {_format_path(path)}."
            )


def _reject_externally_owned_identifiers(data: Any) -> None:
    for key, _value, path in _iter_nested(data):
        if key in OWNED_IDENTIFIER_FIELDS:
            _raise(
                f"Field '{key}' is not accepted in the harmonized "
                f"provider-publication contract at {_format_path(path)}."
            )

        if key == "display_name":
            _raise(
                "Field 'display_name' is not accepted in the harmonized "
                "provider-publication contract; use 'provider_name'."
            )


def _validate_evidence_metadata(
    data: dict[str, Any],
    *,
    location: str,
    required: bool = False,
) -> None:
    if required:
        for field in ["source_type", "confidence"]:
            if field not in data:
                _raise(f"{location}.{field} is required.")

    source_type = data.get("source_type")
    confidence = data.get("confidence")

    if source_type is not None and source_type not in ALLOWED_SOURCE_TYPES:
        _raise(
            f"{location}.source_type has invalid value '{source_type}'. "
            f"Allowed values: {sorted(ALLOWED_SOURCE_TYPES)}."
        )

    if confidence is not None and confidence not in ALLOWED_CONFIDENCE_VALUES:
        _raise(
            f"{location}.confidence has invalid value '{confidence}'. "
            f"Allowed values: {sorted(ALLOWED_CONFIDENCE_VALUES)}."
        )

    if source_type == "not_confirmed" and confidence != "unknown":
        _raise(f"{location} uses source_type not_confirmed and must use confidence unknown.")

    if confidence == "unknown" and source_type != "not_confirmed":
        _raise(f"{location} uses confidence unknown and must use source_type not_confirmed.")


def _validate_positive_numeric_values(data: Any, *, location: str) -> None:
    if isinstance(data, dict):
        min_value = data.get("min")
        max_value = data.get("max")

        if min_value is not None and max_value is not None and min_value > max_value:
            _raise(f"{location}.min must be less than or equal to max.")

        for key, value in data.items():
            child_location = f"{location}.{key}"
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                if value <= 0:
                    _raise(f"{child_location} must be positive.")
            else:
                _validate_positive_numeric_values(value, location=child_location)
    elif isinstance(data, list):
        for index, value in enumerate(data):
            _validate_positive_numeric_values(value, location=f"{location}[{index}]")


def _validate_capability_record(data: Any, *, location: str) -> None:
    if not isinstance(data, dict):
        _raise(f"{location} must be an object.")

    _validate_evidence_metadata(data, location=location)
    _validate_positive_numeric_values(data, location=location)


def _validate_part_type_profile_capabilities(
    capabilities: dict[str, Any],
    *,
    location: str,
) -> None:
    for field, value in capabilities.items():
        if field == "bounding_box_mm":
            if not isinstance(value, dict):
                _raise(f"{location}.bounding_box_mm must be an object.")
            _validate_capability_record(value, location=f"{location}.bounding_box_mm")
            for component in ["length_mm", "width_mm", "height_mm"]:
                if component in value:
                    _validate_capability_record(
                        value[component],
                        location=f"{location}.bounding_box_mm.{component}",
                    )
            continue

        _validate_capability_record(value, location=f"{location}.{field}")


def _get_registry_context() -> dict[str, Any]:
    registry = get_service_discovery_registry()

    service_category_to_family = {
        category["value"]: category["part_family"]
        for category in registry["service_categories"]
    }
    family_to_part_types = {
        family["value"]: set(family["part_types"])
        for family in registry["part_families"]
    }

    return {
        "registry": registry,
        "service_category_to_family": service_category_to_family,
        "family_to_part_types": family_to_part_types,
        "part_type_profiles": registry["part_type_profiles"],
    }


class ServiceDiscoveryPublicationSerializer(serializers.Serializer):
    provider_id = serializers.CharField(required=True)
    provider_name = serializers.CharField(required=True, max_length=255)
    country = serializers.CharField(required=True, max_length=120)
    certifications = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )
    offerings = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        allow_empty=False,
    )
    publication_metadata = serializers.DictField(required=False, default=dict)

    def to_internal_value(self, data):
        _reject_forbidden_fields(data)
        _reject_externally_owned_identifiers(data)
        return super().to_internal_value(data)

    def validate_provider_id(self, value):
        if not PROVIDER_ID_PATTERN.match(value):
            raise serializers.ValidationError(
                "provider_id must be lower snake_case and identifier-safe."
            )
        return value

    def validate(self, attrs):
        raw_payload = getattr(self, "initial_data", {})
        _reject_forbidden_fields(raw_payload)
        _reject_externally_owned_identifiers(raw_payload)

        publication_metadata = attrs.get("publication_metadata") or {}
        publication_metadata.setdefault("source_type", "provider_confirmed")
        publication_metadata.setdefault("confidence", "declared")
        attrs["publication_metadata"] = publication_metadata

        self._validate_publication_metadata(publication_metadata)
        self._validate_provider_certifications(attrs.get("certifications", []))
        self._validate_offerings(attrs["offerings"])

        return attrs

    def _validate_publication_metadata(self, metadata: dict[str, Any]) -> None:
        if not isinstance(metadata, dict):
            _raise("publication_metadata must be an object.")

        _validate_evidence_metadata(metadata, location="publication_metadata")

    def _validate_provider_certifications(self, certifications: list[dict[str, Any]]) -> None:
        allowed_certifications = get_vocabulary_values(CERTIFICATIONS)

        for index, certification in enumerate(certifications):
            location = f"certifications[{index}]"
            if not isinstance(certification, dict):
                _raise(f"{location} must be an object.")

            code = certification.get("code")
            if not code:
                _raise(f"{location}.code is required.")

            if code not in allowed_certifications:
                _raise(f"{location}.code has invalid value '{code}'.")

            _validate_evidence_metadata(certification, location=location)

    def _validate_offerings(self, offerings: list[dict[str, Any]]) -> None:
        registry_context = _get_registry_context()
        service_categories = []

        for index, offering in enumerate(offerings):
            location = f"offerings[{index}]"
            if not isinstance(offering, dict):
                _raise(f"{location} must be an object.")

            self._validate_offering_required_fields(offering, location=location)

            service_category = offering["service_category"]
            service_categories.append(service_category)

            self._validate_offering_taxonomy(
                offering,
                location=location,
                registry_context=registry_context,
            )
            self._validate_family_capabilities(
                offering,
                location=location,
                registry_context=registry_context,
            )
            self._validate_part_type_capabilities(
                offering,
                location=location,
                registry_context=registry_context,
            )
            self._validate_generic_capabilities(
                offering.get("generic_capabilities", {}),
                location=f"{location}.generic_capabilities",
            )

        duplicate_categories = sorted(
            {
                service_category
                for service_category in service_categories
                if service_categories.count(service_category) > 1
            }
        )
        if duplicate_categories:
            _raise(f"Duplicate service_category values: {duplicate_categories}")

    def _validate_offering_required_fields(
        self,
        offering: dict[str, Any],
        *,
        location: str,
    ) -> None:
        required_fields = [
            "service_category",
            "offering_name",
            "part_family",
            "support_status",
        ]
        for field in required_fields:
            if field not in offering or offering[field] in ("", None):
                _raise(f"{location}.{field} is required.")

        support_status = offering["support_status"]
        if support_status not in ALLOWED_SUPPORT_STATUSES:
            _raise(f"{location}.support_status has invalid value '{support_status}'.")

        offering.setdefault("supported_part_types", [])
        offering.setdefault("family_capabilities", {})
        offering.setdefault("part_type_capabilities", {})
        offering.setdefault("generic_capabilities", {})

        if not isinstance(offering["supported_part_types"], list):
            _raise(f"{location}.supported_part_types must be a list.")
        if not isinstance(offering["family_capabilities"], dict):
            _raise(f"{location}.family_capabilities must be an object.")
        if not isinstance(offering["part_type_capabilities"], dict):
            _raise(f"{location}.part_type_capabilities must be an object.")
        if not isinstance(offering["generic_capabilities"], dict):
            _raise(f"{location}.generic_capabilities must be an object.")

    def _validate_offering_taxonomy(
        self,
        offering: dict[str, Any],
        *,
        location: str,
        registry_context: dict[str, Any],
    ) -> None:
        service_category = offering["service_category"]
        part_family = offering["part_family"]

        category_to_family = registry_context["service_category_to_family"]
        if service_category not in category_to_family:
            _raise(f"{location}.service_category has invalid value '{service_category}'.")

        expected_family = category_to_family[service_category]
        if part_family != expected_family:
            _raise(
                f"{location}.part_family must be '{expected_family}' for "
                f"service_category '{service_category}'."
            )

        allowed_part_types = registry_context["family_to_part_types"][part_family]
        submitted_part_types = []

        for index, part_type_data in enumerate(offering["supported_part_types"]):
            item_location = f"{location}.supported_part_types[{index}]"
            if not isinstance(part_type_data, dict):
                _raise(f"{item_location} must be an object.")

            for field in ["part_type", "support_status", "source_type", "confidence"]:
                if field not in part_type_data:
                    _raise(f"{item_location}.{field} is required.")

            part_type = part_type_data["part_type"]
            if part_type not in allowed_part_types:
                _raise(
                    f"{item_location}.part_type '{part_type}' does not belong to "
                    f"part_family '{part_family}'."
                )

            support_status = part_type_data["support_status"]
            if support_status not in ALLOWED_SUPPORT_STATUSES:
                _raise(f"{item_location}.support_status has invalid value '{support_status}'.")

            _validate_evidence_metadata(part_type_data, location=item_location, required=True)
            submitted_part_types.append(part_type)

        duplicate_part_types = sorted(
            {
                part_type
                for part_type in submitted_part_types
                if submitted_part_types.count(part_type) > 1
            }
        )
        if duplicate_part_types:
            _raise(f"{location}.supported_part_types has duplicates: {duplicate_part_types}")

    def _validate_family_capabilities(
        self,
        offering: dict[str, Any],
        *,
        location: str,
        registry_context: dict[str, Any],
    ) -> None:
        part_family = offering["part_family"]
        family_capabilities = offering.get("family_capabilities", {})

        if part_family == "metal_part":
            if family_capabilities:
                _raise(
                    f"{location}.family_capabilities must be empty for "
                    "precision_metal_parts in H2."
                )
            return

        if part_family == "gear":
            allowed_fields = set(registry_context["part_type_profiles"]["spur_gear"]["family_common_fields"])
            forbidden_gear_fields = {"diameter_mm", "outer_diameter_mm"}
            for field in forbidden_gear_fields & set(family_capabilities):
                _raise(f"{location}.family_capabilities.{field} is not valid for gear.")
        elif part_family == "shaft":
            allowed_fields = set(registry_context["part_type_profiles"]["plain_shaft"]["family_common_fields"])
            if "outside_diameter_mm" in family_capabilities:
                _raise(
                    f"{location}.family_capabilities.outside_diameter_mm is not valid "
                    "for shaft."
                )
        else:
            allowed_fields = set()

        for field, value in family_capabilities.items():
            if field not in allowed_fields:
                _raise(f"{location}.family_capabilities.{field} is not allowed.")
            _validate_capability_record(
                value,
                location=f"{location}.family_capabilities.{field}",
            )

    def _validate_part_type_capabilities(
        self,
        offering: dict[str, Any],
        *,
        location: str,
        registry_context: dict[str, Any],
    ) -> None:
        part_type_capabilities = offering.get("part_type_capabilities", {})
        supported_part_types = {
            item["part_type"]: item
            for item in offering.get("supported_part_types", [])
        }
        profiles = registry_context["part_type_profiles"]

        for part_type, capabilities in part_type_capabilities.items():
            part_type_location = f"{location}.part_type_capabilities.{part_type}"

            if part_type not in supported_part_types:
                _raise(
                    f"{part_type_location} is not listed in supported_part_types."
                )

            if supported_part_types[part_type]["support_status"] != "confirmed":
                _raise(
                    f"{part_type_location} can only be published for a confirmed "
                    "part type."
                )

            allowed_fields = set(profiles[part_type]["family_common_fields"])
            allowed_fields.update(profiles[part_type]["part_type_specific_fields"])

            if not isinstance(capabilities, dict):
                _raise(f"{part_type_location} must be an object.")

            for field in capabilities:
                if field not in allowed_fields:
                    _raise(f"{part_type_location}.{field} is not allowed.")

            _validate_part_type_profile_capabilities(
                capabilities,
                location=part_type_location,
            )

    def _validate_generic_capabilities(
        self,
        capabilities: dict[str, Any],
        *,
        location: str,
    ) -> None:
        if not isinstance(capabilities, dict):
            _raise(f"{location} must be an object.")

        for field in capabilities:
            if field not in ALLOWED_GENERIC_CAPABILITY_FIELDS:
                _raise(f"{location}.{field} is not allowed.")

        if "materials" in capabilities:
            self._validate_materials(capabilities["materials"], location=f"{location}.materials")

        if "processes" in capabilities:
            self._validate_processes(capabilities["processes"], location=f"{location}.processes")

        if "certifications" in capabilities:
            self._validate_provider_certifications(capabilities["certifications"])

        for field in [
            "batch_size",
            "lead_time_weeks",
            "surface_finish_ra_um",
            "tolerance_mm",
            "quality",
            "weight_kg",
        ]:
            if field in capabilities:
                record = capabilities[field]
                if field == "quality":
                    self._validate_quality(record, location=f"{location}.{field}")
                else:
                    _validate_capability_record(record, location=f"{location}.{field}")

    def _validate_materials(self, materials: list[dict[str, Any]], *, location: str) -> None:
        if not isinstance(materials, list):
            _raise(f"{location} must be a list.")

        allowed_materials = get_vocabulary_values(MATERIALS)
        for index, material_data in enumerate(materials):
            item_location = f"{location}[{index}]"
            if not isinstance(material_data, dict):
                _raise(f"{item_location} must be an object.")

            material = material_data.get("material")
            if material not in allowed_materials:
                _raise(f"{item_location}.material has invalid value '{material}'.")

            available_grades = material_data.get("available_grades", [])
            if not isinstance(available_grades, list):
                _raise(f"{item_location}.available_grades must be a list.")

            for grade_index, grade in enumerate(available_grades):
                if not isinstance(grade, str) or not grade.strip():
                    _raise(
                        f"{item_location}.available_grades[{grade_index}] must be "
                        "a non-empty string."
                    )

            _validate_evidence_metadata(material_data, location=item_location)

    def _validate_processes(self, processes: list[dict[str, Any]], *, location: str) -> None:
        if not isinstance(processes, list):
            _raise(f"{location} must be a list.")

        allowed_processes = get_vocabulary_values(PROCESSES)
        for index, process_data in enumerate(processes):
            item_location = f"{location}[{index}]"
            if not isinstance(process_data, dict):
                _raise(f"{item_location} must be an object.")

            process = process_data.get("process")
            if process not in allowed_processes:
                _raise(f"{item_location}.process has invalid value '{process}'.")

            delivery_mode = process_data.get("delivery_mode", "unspecified")
            if delivery_mode not in ALLOWED_DELIVERY_MODES:
                _raise(
                    f"{item_location}.delivery_mode has invalid value '{delivery_mode}'."
                )

            _validate_evidence_metadata(process_data, location=item_location)

    def _validate_quality(self, quality: dict[str, Any], *, location: str) -> None:
        if not isinstance(quality, dict):
            _raise(f"{location} must be an object.")

        standard = quality.get("standard")
        if standard is not None and standard not in ALLOWED_QUALITY_STANDARDS:
            _raise(f"{location}.standard has invalid value '{standard}'.")

        _validate_capability_record(quality, location=location)
