from copy import deepcopy
from typing import Any

from apps.ontology.mappings import (
    get_material_ontology_concept,
    get_material_parent_id,
    get_service_ontology_concept,
)
from apps.ontology.vocabularies import MATERIALS
from apps.providers.validators import validate_seed_data


def get_vocabulary_label(vocabulary: list[dict], value: str) -> str:
    """
    Return a human-readable label for a controlled vocabulary value.
    """
    for item in vocabulary:
        if item["value"] == value:
            return item["label"]

    return value


def has_known_value(data: dict[str, Any], meaningful_keys: list[str]) -> bool:
    """
    Return True if any meaningful capability value is known.

    None and empty string are treated as unknown.
    False is treated as a known value for boolean fields.
    """
    for key in meaningful_keys:
        value = data.get(key)

        if value is False:
            return True

        if value is not None and value != "":
            return True

    return False


def add_capability_provenance(
    capability: dict[str, Any],
    *,
    meaningful_keys: list[str],
    source_type: str,
    confidence: str,
) -> dict[str, Any]:
    """
    Add source_type and confidence to one capability object.

    If the capability has no known value, mark it unknown/not_confirmed.
    """
    capability = deepcopy(capability)

    if has_known_value(capability, meaningful_keys):
        capability["source_type"] = source_type
        capability["confidence"] = confidence
    else:
        capability["source_type"] = "not_confirmed"
        capability["confidence"] = "unknown"

    return capability


def normalize_capabilities(
    capabilities: dict[str, Any],
    *,
    source_type: str,
    confidence: str,
) -> dict[str, Any]:
    """
    Normalize offering capabilities into internal seed-data format.

    Missing capability objects are kept explicit and marked unknown.
    """
    capabilities = capabilities or {}

    batch_size = capabilities.get("batch_size", {})
    batch_size.setdefault("unit", "pcs")

    return {
        "batch_size": add_capability_provenance(
            batch_size,
            meaningful_keys=["min", "max"],
            source_type=source_type,
            confidence=confidence,
        ),
        "diameter_mm": add_capability_provenance(
            capabilities.get("diameter_mm", {}),
            meaningful_keys=["min", "max"],
            source_type=source_type,
            confidence=confidence,
        ),
        "weight_kg": add_capability_provenance(
            capabilities.get("weight_kg", {}),
            meaningful_keys=["max"],
            source_type=source_type,
            confidence=confidence,
        ),
        "module": add_capability_provenance(
            capabilities.get("module", {}),
            meaningful_keys=["min", "max"],
            source_type=source_type,
            confidence=confidence,
        ),
        "diametral_pitch": add_capability_provenance(
            capabilities.get("diametral_pitch", {}),
            meaningful_keys=["min", "max", "raw"],
            source_type=source_type,
            confidence=confidence,
        ),
        "quality": add_capability_provenance(
            capabilities.get("quality", {}),
            meaningful_keys=["standard", "best_class"],
            source_type=source_type,
            confidence=confidence,
        ),
        "lead_time_weeks": add_capability_provenance(
            capabilities.get("lead_time_weeks", {}),
            meaningful_keys=["min", "max"],
            source_type=source_type,
            confidence=confidence,
        ),
        "surface_finish_ra_um": add_capability_provenance(
            capabilities.get("surface_finish_ra_um", {}),
            meaningful_keys=["max"],
            source_type=source_type,
            confidence=confidence,
        ),
        "tolerance_mm": add_capability_provenance(
            capabilities.get("tolerance_mm", {}),
            meaningful_keys=["min"],
            source_type=source_type,
            confidence=confidence,
        ),
        "traceability": add_capability_provenance(
            capabilities.get("traceability", {}),
            meaningful_keys=["aerospace_traceability", "full_traceability"],
            source_type=source_type,
            confidence=confidence,
        ),
    }


def normalize_materials_from_publication(
    offerings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build top-level materials[] from all offering supported_materials.
    """
    material_ids = set()

    for offering in offerings:
        material_ids.update(offering.get("supported_materials", []))

        for grade in offering.get("supported_material_grades", []):
            material_ids.add(grade["material_id"])

    materials = []

    for material_id in sorted(material_ids):
        material = {
            "material_id": material_id,
            "label": get_vocabulary_label(MATERIALS, material_id),
            "ontology_concept": get_material_ontology_concept(material_id),
        }

        parent_material_id = get_material_parent_id(material_id)
        if parent_material_id:
            material["parent_material_id"] = parent_material_id

        materials.append(material)

    return materials


def normalize_material_grades_from_publication(
    offerings: list[dict[str, Any]],
    *,
    source_type: str,
    confidence: str,
) -> list[dict[str, Any]]:
    """
    Build top-level material_grades[] from all offering grade declarations.

    Duplicate grade IDs are collapsed if they have the same material_id.
    Conflicting duplicate grade definitions are rejected.
    """
    grades_by_id: dict[str, dict[str, Any]] = {}

    for offering in offerings:
        for grade in offering.get("supported_material_grades", []):
            grade_id = grade["grade_id"]
            material_id = grade["material_id"]

            existing = grades_by_id.get(grade_id)
            if existing and existing["material_id"] != material_id:
                raise ValueError(
                    f"Material grade {grade_id} has conflicting material_id values: "
                    f"{existing['material_id']} and {material_id}"
                )

            grades_by_id[grade_id] = {
                "grade_id": grade_id,
                "label": grade.get("label") or grade_id,
                "material_id": material_id,
                "source_type": source_type,
                "confidence": confidence,
            }

    return [grades_by_id[grade_id] for grade_id in sorted(grades_by_id)]


def normalize_provider_publication(
    validated_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert validated provider-publication serializer data into internal seed-data format.

    This function does not write files.
    It only returns a normalized catalogue seed dictionary.
    """
    provider_data = validated_data["provider"]
    offerings_data = validated_data["offerings"]

    publication_metadata = validated_data.get("publication_metadata") or {}
    source_type = publication_metadata.get("source_type", "provider_confirmed")
    confidence = publication_metadata.get("confidence", "declared")
    publication_status = publication_metadata.get("status", "draft")

    provider_id = provider_data["provider_id"]

    provider = {
        "provider_id": provider_id,
        "legal_name": provider_data.get("legal_name", ""),
        "display_name": provider_data["display_name"],
        "provider_type": provider_data.get("provider_type", "MaaSProvider"),
        "country": provider_data["country"],
        "source_type": source_type,
        "confidence": confidence,
        "facilities": [],
        "certifications": [],
    }

    for facility in provider_data.get("facilities", []):
        normalized_facility = {
            **facility,
            "confidence": confidence,
        }
        provider["facilities"].append(normalized_facility)

    for certification in provider_data.get("certifications", []):
        provider["certifications"].append(
            {
                "code": certification["code"],
                "label": certification.get("label") or certification["code"],
                "source_type": source_type,
                "confidence": confidence,
            }
        )

    normalized_offerings = []

    for offering in offerings_data:
        normalized_offerings.append(
            {
                "offering_id": offering["offering_id"],
                "provider_id": provider_id,
                "name": offering["name"],
                "service_type": offering["service_type"],
                "ontology_service_concept": get_service_ontology_concept(
                    offering["service_type"]
                ),
                "source_type": source_type,
                "confidence": confidence,
                "part_families": offering["part_families"],
                "processes": offering["processes"],
                "supported_materials": [
                    {
                        "material": material_id,
                        "source_type": source_type,
                        "confidence": confidence,
                    }
                    for material_id in offering["supported_materials"]
                ],
                "supported_material_grades": [
                    grade["grade_id"]
                    for grade in offering.get("supported_material_grades", [])
                ],
                "capabilities": normalize_capabilities(
                    offering.get("capabilities", {}),
                    source_type=source_type,
                    confidence=confidence,
                ),
                "notes": offering.get("notes", []),
            }
        )

    normalized_seed_data = {
        "metadata": {
            "dataset_id": f"{provider_id}_publication_seed_v1",
            "version": "1.0",
            "status": f"provider_publication_{publication_status}",
            "route_fields_included": False,
            "notes": [
                "Generated from provider-publication payload.",
                "Route/operation sequence fields are excluded from v1.",
            ],
        },
        "providers": [provider],
        "materials": normalize_materials_from_publication(offerings_data),
        "material_grades": normalize_material_grades_from_publication(
            offerings_data,
            source_type=source_type,
            confidence=confidence,
        ),
        "offerings": normalized_offerings,
    }

    return validate_seed_data(normalized_seed_data)