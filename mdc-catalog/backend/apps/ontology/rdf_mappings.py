
SERVICE_TYPE_CONCEPTS = {
    "gear_manufacturing": "GearTransmissionService",
    "shaft_manufacturing": "GearTransmissionService",
    "machining": "MachiningService",
    "heat_treatment": "HeatTreatmentService",
    "inspection": "InspectionService",
    "finishing": "FinishingService",
}


PART_FAMILY_CONCEPTS = {
    "gear": "Gear",
    "spur_gear": "SpurGear",
    "helical_gear": "HelicalGear",
    "shaft": "Shaft",
    "transmission_component": "TransmissionComponent",
}


PROCESS_CONCEPTS = {
    "machining": "Machining",
    "turning": "Turning",
    "milling": "Milling",
    "hobbing": "Hobbing",
    "gear_shaping": "GearShaping",
    "hard_turning": "HardTurning",
    "grinding": "Grinding",
    "gear_grinding": "GearGrinding",
    "heat_treatment": "HeatTreatment",
    "inspection": "InspectionProcess",
}


MATERIAL_CONCEPTS = {
    "steel": "Steel",
    "alloyed_carburizing_steel": "AlloyedCarburizingSteel",
    "stainless_steel": "StainlessSteel",
    "aluminum": "Aluminum",
    "titanium": "Titanium",
    "nickel_alloy": "NickelAlloy",
}


CERTIFICATION_CONCEPTS = {
    "ISO9001_2015": "ISO9001_2015",
    "ISO14001_2015": "ISO14001_2015",
    "ISO_TS_16949_partial": "ISO_TS_16949_partial",
    "APQP": "APQP",
    "aerospace_traceability": "AerospaceTraceability",
    "full_traceability": "FullTraceability",
}