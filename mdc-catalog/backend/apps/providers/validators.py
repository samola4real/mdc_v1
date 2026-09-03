from typing import Any

from apps.ontology.vocabularies import (
    CERTIFICATIONS,
    MATERIALS,
    PART_FAMILIES,
    PROCESSES,
    SERVICE_TYPES,
    get_vocabulary_values,
)
from apps.providers.exceptions import SeedDataError
from apps.providers.providers_utils import find_duplicate_values


FORBIDDEN_ROUTE_KEYS = {
    "routes",
    "route_steps",
    "operation_sequence",
    "machine_sequence",
    "process_order",
    "subcontractor_route",
    "cycle_time",
    "setup_time",
    "machine_availability",
    "pricing",
    "capacity_calendar",
}

ALLOWED_QUALITY_STANDARDS = {"DIN", "ISO"}


def validate_value_in_vocabulary(
    *,
    field_name: str,
    value: str,
    allowed_values: set[str],
) -> None:
    """
    Validate that one value exists in an allowed vocabulary set.
    """
    if value not in allowed_values:
        raise SeedDataError(
            f"Invalid value for {field_name}: {value}. "
            f"Allowed values: {sorted(allowed_values)}"
        )


def validate_list_values_in_vocabulary(
    *,
    field_name: str,
    values: list,
    allowed_values: set[str],
) -> None:
    """
    Validate that every item in a list exists in an allowed vocabulary set.
    """
    if not isinstance(values, list):
        raise SeedDataError(f"{field_name} must be a list.")

    for value in values:
        if not isinstance(value, str):
            raise SeedDataError(f"Each value in {field_name} must be a string.")

        validate_value_in_vocabulary(
            field_name=field_name,
            value=value,
            allowed_values=allowed_values,
        )


def get_declared_material_grade_ids(data: dict[str, Any]) -> set[str]:
    """
    Return material grade IDs declared in this seed data file/catalogue.

    Example:
    material_grades:
      - grade_id: 18CrNiMo7-6
    -> {"18CrNiMo7-6"}
    """
    grade_ids = set()

    for grade in data.get("material_grades", []):
        if not isinstance(grade, dict):
            raise SeedDataError("Each material grade must be an object.")

        grade_id = grade.get("grade_id")
        if not grade_id:
            raise SeedDataError("Each material grade must have grade_id.")

        grade_ids.add(grade_id)

    return grade_ids



def get_declared_material_ids(data: dict[str, Any]) -> set[str]:
    """
    Return material IDs declared in this seed data/catalogue.

    Example:
    materials:
      - material_id: steel
    -> {"steel"}
    """
    material_ids = set()

    for material in data.get("materials", []):
        if not isinstance(material, dict):
            raise SeedDataError("Each material must be an object.")

        material_id = material.get("material_id")
        if not material_id:
            raise SeedDataError("Each material must have material_id.")

        material_ids.add(material_id)

    return material_ids


def validate_material_grade_references(data: dict[str, Any]) -> None:
    """
    Validate material grade definitions.

    Checks:
    - every material grade has grade_id
    - every material grade has material_id
    - material_id refers to a declared material
    - grade_id values are unique
    """
    declared_material_ids = get_declared_material_ids(data)
    grade_ids = []

    for grade in data.get("material_grades", []):
        if not isinstance(grade, dict):
            raise SeedDataError("Each material grade must be an object.")

        grade_id = grade.get("grade_id")
        if not grade_id:
            raise SeedDataError("Each material grade must have grade_id.")

        material_id = grade.get("material_id")
        if not material_id:
            raise SeedDataError(f"Material grade {grade_id} must have material_id.")

        if material_id not in declared_material_ids:
            raise SeedDataError(
                f"Material grade {grade_id} references unknown material_id: "
                f"{material_id}"
            )

        grade_ids.append(grade_id)

    duplicate_grade_ids = find_duplicate_values(grade_ids)
    if duplicate_grade_ids:
        raise SeedDataError(
            f"Duplicate material grade_id values found: {duplicate_grade_ids}"
        )


def validate_offering_material_references(data: dict[str, Any]) -> None:
    """
    Validate material references used by offerings.

    Checks:
    - supported_materials[].material refers to a declared material
    - supported_material_grades[] refers to a declared material grade
    """
    declared_material_ids = get_declared_material_ids(data)
    declared_material_grade_ids = get_declared_material_grade_ids(data)

    for offering in data.get("offerings", []):
        offering_id = offering.get("offering_id", "<unknown offering>")

        for material_entry in offering.get("supported_materials", []):
            if not isinstance(material_entry, dict):
                raise SeedDataError(
                    f"Each supported material in offering {offering_id} "
                    "must be an object."
                )

            material_id = material_entry.get("material")
            if not material_id:
                raise SeedDataError(
                    f"Each supported material in offering {offering_id} "
                    "must have material."
                )

            if material_id not in declared_material_ids:
                raise SeedDataError(
                    f"Offering {offering_id} references unknown material: "
                    f"{material_id}"
                )

        for grade_id in offering.get("supported_material_grades", []):
            if grade_id not in declared_material_grade_ids:
                raise SeedDataError(
                    f"Offering {offering_id} references unsupported material grade: "
                    f"{grade_id}. The grade must be declared in material_grades first."
                )





def validate_controlled_vocabulary_values(data: dict[str, Any]) -> None:
    """
    Validate controlled vocabulary values used by provider seed data.

    This protects future RDF generation because each controlled value must map
    cleanly to an ontology concept.
    """
    allowed_service_types = get_vocabulary_values(SERVICE_TYPES)
    allowed_part_families = get_vocabulary_values(PART_FAMILIES)
    allowed_processes = get_vocabulary_values(PROCESSES)
    allowed_materials = get_vocabulary_values(MATERIALS)
    allowed_certifications = get_vocabulary_values(CERTIFICATIONS)

    declared_material_grade_ids = get_declared_material_grade_ids(data)

    for provider in data.get("providers", []):
        certifications = provider.get("certifications", [])

        if not isinstance(certifications, list):
            raise SeedDataError("providers[].certifications must be a list.")

        for certification in certifications:
            if not isinstance(certification, dict):
                raise SeedDataError("Each certification must be an object.")

            code = certification.get("code")
            if not code:
                raise SeedDataError("Each certification must have code.")

            validate_value_in_vocabulary(
                field_name="providers[].certifications[].code",
                value=code,
                allowed_values=allowed_certifications,
            )

    for offering in data.get("offerings", []):
        offering_id = offering.get("offering_id", "<unknown offering>")

        service_type = offering.get("service_type")
        if not service_type:
            raise SeedDataError(f"Offering {offering_id} must have service_type.")

        validate_value_in_vocabulary(
            field_name=f"offerings[{offering_id}].service_type",
            value=service_type,
            allowed_values=allowed_service_types,
        )

        validate_list_values_in_vocabulary(
            field_name=f"offerings[{offering_id}].part_families",
            values=offering.get("part_families", []),
            allowed_values=allowed_part_families,
        )

        validate_list_values_in_vocabulary(
            field_name=f"offerings[{offering_id}].processes",
            values=offering.get("processes", []),
            allowed_values=allowed_processes,
        )

        supported_materials = offering.get("supported_materials", [])
        if not isinstance(supported_materials, list):
            raise SeedDataError(
                f"offerings[{offering_id}].supported_materials must be a list."
            )

        for material_entry in supported_materials:
            if not isinstance(material_entry, dict):
                raise SeedDataError(
                    f"Each supported material in offering {offering_id} must be an object."
                )

            material = material_entry.get("material")
            if not material:
                raise SeedDataError(
                    f"Each supported material in offering {offering_id} must have material."
                )

            validate_value_in_vocabulary(
                field_name=f"offerings[{offering_id}].supported_materials[].material",
                value=material,
                allowed_values=allowed_materials,
            )

        supported_material_grades = offering.get("supported_material_grades", [])
        if not isinstance(supported_material_grades, list):
            raise SeedDataError(
                f"offerings[{offering_id}].supported_material_grades must be a list."
            )

        for grade_id in supported_material_grades:
            if not isinstance(grade_id, str):
                raise SeedDataError(
                    f"Each supported material grade in offering {offering_id} must be a string."
                )

            if grade_id not in declared_material_grade_ids:
                raise SeedDataError(
                    f"Offering {offering_id} references unsupported material grade: "
                    f"{grade_id}. The grade must be declared in material_grades first."
                )

        quality = offering.get("capabilities", {}).get("quality", {})
        quality_standard = quality.get("standard")

        if quality_standard is not None:
            validate_value_in_vocabulary(
                field_name=f"offerings[{offering_id}].capabilities.quality.standard",
                value=quality_standard,
                allowed_values=ALLOWED_QUALITY_STANDARDS,
            )


def validate_seed_data(data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate curated provider seed data.

    This validates:
    - required top-level keys
    - route-field exclusion
    - provider/offering structure
    - duplicate provider IDs
    - duplicate offering IDs
    - offering provider references
    - controlled vocabulary values
    """
    required_top_level_keys = {
        "metadata",
        "providers",
        "materials",
        "material_grades",
        "offerings",
    }

    missing_keys = required_top_level_keys - set(data.keys())
    if missing_keys:
        raise SeedDataError(
            f"Seed data is missing required top-level keys: {sorted(missing_keys)}"
        )

    metadata = data.get("metadata", {})
    if metadata.get("route_fields_included") is not False:
        raise SeedDataError("metadata.route_fields_included must be false for v1.")

    for forbidden_key in FORBIDDEN_ROUTE_KEYS:
        if forbidden_key in data:
            raise SeedDataError(
                f"Forbidden route-related top-level key found: {forbidden_key}"
            )

    providers = data.get("providers")
    if not isinstance(providers, list) or not providers:
        raise SeedDataError("providers must be a non-empty list.")

    offerings = data.get("offerings")
    if not isinstance(offerings, list) or not offerings:
        raise SeedDataError("offerings must be a non-empty list.")

    provider_ids = []

    for provider in providers:
        if not isinstance(provider, dict):
            raise SeedDataError("Each provider must be an object.")

        provider_id = provider.get("provider_id")
        if not provider_id:
            raise SeedDataError("Each provider must have provider_id.")

        provider_ids.append(provider_id)

    duplicate_provider_ids = find_duplicate_values(provider_ids)
    if duplicate_provider_ids:
        raise SeedDataError(
            f"Duplicate provider_id values found: {duplicate_provider_ids}"
        )

    provider_id_set = set(provider_ids)

    offering_ids = []

    for offering in offerings:
        if not isinstance(offering, dict):
            raise SeedDataError("Each offering must be an object.")

        for forbidden_key in FORBIDDEN_ROUTE_KEYS:
            if forbidden_key in offering:
                raise SeedDataError(
                    f"Forbidden route-related offering key found: {forbidden_key}"
                )

        offering_id = offering.get("offering_id")
        if not offering_id:
            raise SeedDataError("Each offering must have offering_id.")

        offering_ids.append(offering_id)

        provider_id = offering.get("provider_id")
        if not provider_id:
            raise SeedDataError(f"Offering {offering_id} must have provider_id.")

        if provider_id not in provider_id_set:
            raise SeedDataError(
                f"Offering {offering_id} references unknown provider_id: {provider_id}"
            )

    duplicate_offering_ids = find_duplicate_values(offering_ids)
    if duplicate_offering_ids:
        raise SeedDataError(
            f"Duplicate offering_id values found: {duplicate_offering_ids}"
        )

    validate_material_grade_references(data)
    validate_offering_material_references(data)
    validate_controlled_vocabulary_values(data)

    return data
