
from apps.ontology.service_discovery_registry import get_service_discovery_registry


SERVICE_TYPES = [
    {"value": "gear_manufacturing", "label": "Gear manufacturing"},
    {"value": "shaft_manufacturing", "label": "Shaft manufacturing"},
    {"value": "machining", "label": "Machining"},
    {"value": "heat_treatment", "label": "Heat treatment"},
    {"value": "inspection", "label": "Inspection"},
    {"value": "finishing", "label": "Finishing"},
]

PART_FAMILIES = [
    {"value": "gear", "label": "Gear"},
    {"value": "spur_gear", "label": "Spur gear"},
    {"value": "helical_gear", "label": "Helical gear"},
    {"value": "shaft", "label": "Shaft"},
    {"value": "transmission_component", "label": "Transmission component"},
]

PROCESSES = [
    {"value": "machining", "label": "Machining"},
    {"value": "turning", "label": "Turning"},
    {"value": "milling", "label": "Milling"},
    {"value": "hobbing", "label": "Hobbing"},
    {"value": "gear_shaping", "label": "Gear shaping"},
    {"value": "deburring", "label": "Deburring"},
    {"value": "hard_turning", "label": "Hard turning"},
    {"value": "grinding", "label": "Grinding"},
    {"value": "tooth_grinding", "label": "Tooth grinding"},
    {"value": "gear_grinding", "label": "Gear grinding / tooth grinding"},
    {"value": "gear_cutting", "label": "Gear cutting"},
    {"value": "surface_grinding", "label": "Surface grinding"},
    {"value": "heat_treatment", "label": "Heat treatment"},
    {"value": "turn_mill", "label": "Turn-mill"},
    {"value": "inspection", "label": "Inspection / quality checking"},
]

MATERIALS = [
    {"value": "steel", "label": "Steel"},
    {"value": "alloyed_carburizing_steel", "label": "Alloyed carburizing steel"},
    {"value": "stainless_steel", "label": "Stainless steel"},
    {"value": "aluminum", "label": "Aluminum"},
    {"value": "titanium", "label": "Titanium"},
    {"value": "nickel_alloy", "label": "Nickel alloy"},
]

MATERIAL_GRADES = [
    {"value": "18CrNiMo7-6", "label": "18CrNiMo7-6"},
    {"value": "16MnCr5", "label": "16MnCr5"},
    {"value": "20MnCr5", "label": "20MnCr5"},
]

CERTIFICATIONS = [
    {"value": "ISO9001_2015", "label": "ISO 9001:2015"},
    {"value": "ISO14001_2015", "label": "ISO 14001:2015"},
    {"value": "ISO_TS_16949_partial", "label": "Partial ISO/TS 16949 implementation"},
    {"value": "APQP", "label": "Advanced Product Quality Planning"},
    {"value": "aerospace_traceability", "label": "Aerospace traceability"},
    {"value": "full_traceability", "label": "Full traceability"},
]


def get_catalog_filters() -> dict:
    return {
        "service_types": SERVICE_TYPES,
        "part_families": PART_FAMILIES,
        "processes": PROCESSES,
        "materials": MATERIALS,
        "material_grades": MATERIAL_GRADES,
        "certifications": CERTIFICATIONS,
        "service_discovery": get_service_discovery_registry(),
    }

def get_vocabulary_values(vocabulary: list[dict]) -> set[str]:
    """
    Return the set of allowed 'value' entries from a vocabulary list.

    Example:
    [{"value": "machining", "label": "Machining"}]
    -> {"machining"}
    """
    return {item["value"] for item in vocabulary}

