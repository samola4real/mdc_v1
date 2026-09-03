SERVICE_ONTOLOGY_CONCEPTS = {
    "gear_manufacturing": "mdc:GearTransmissionService",
    "shaft_manufacturing": "mdc:GearTransmissionService",
    "machining": "mdc:MachiningService",
    "heat_treatment": "mdc:HeatTreatmentService",
    "inspection": "mdc:InspectionService",
    "finishing": "mdc:FinishingService",
}


MATERIAL_ONTOLOGY_CONCEPTS = {
    "steel": "mdc:Steel",
    "alloyed_carburizing_steel": "mdc:AlloyedCarburizingSteel",
    "stainless_steel": "mdc:StainlessSteel",
    "aluminum": "mdc:Aluminum",
    "titanium": "mdc:Titanium",
    "nickel_alloy": "mdc:NickelAlloy",
}


MATERIAL_PARENT_IDS = {
    "alloyed_carburizing_steel": "steel",
    "stainless_steel": "steel",
}


def get_service_ontology_concept(service_type: str) -> str:
    return SERVICE_ONTOLOGY_CONCEPTS[service_type]


def get_material_ontology_concept(material_id: str) -> str:
    return MATERIAL_ONTOLOGY_CONCEPTS[material_id]


def get_material_parent_id(material_id: str) -> str | None:
    return MATERIAL_PARENT_IDS.get(material_id)