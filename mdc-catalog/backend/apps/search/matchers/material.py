from typing import Any

from apps.search.matchers.common import (
    evaluate_list_optional_match,
    normalize_string_list,
)


def extract_supported_materials(offering: dict[str, Any]) -> list[str]:
    """
    Extract material IDs from offering.supported_materials.
    """
    materials = []

    for material_entry in offering.get("supported_materials", []):
        if not isinstance(material_entry, dict):
            continue

        material = material_entry.get("material")
        if isinstance(material, str):
            materials.append(material)

    return sorted(set(materials))


def extract_supported_material_grades(offering: dict[str, Any]) -> list[str]:
    """
    Extract supported material grade IDs from an offering.
    """
    return sorted(set(normalize_string_list(offering.get("supported_material_grades"))))


def evaluate_material_optional_match(
    *,
    requested_materials: list[str],
    offering: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Evaluate requested materials against offering supported materials.
    """
    return evaluate_list_optional_match(
        field="materials",
        requested_values=requested_materials,
        provided_values=extract_supported_materials(offering),
        unknown_reason="No confirmed supported material data is available for this offering.",
    )


def evaluate_material_grade_optional_match(
    *,
    requested_material_grades: list[str],
    offering: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Evaluate requested material grades against offering supported grades.
    """
    return evaluate_list_optional_match(
        field="material_grades",
        requested_values=requested_material_grades,
        provided_values=extract_supported_material_grades(offering),
        unknown_reason="No confirmed material-grade data is available for this offering.",
    )
