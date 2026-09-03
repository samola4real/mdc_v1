from __future__ import annotations

from rdflib import Namespace, URIRef


MDC = Namespace("https://maasai-project.eu/ontology/mdc#")


class ServiceDiscoveryRdfMappingError(Exception):
    pass


SERVICE_CATEGORY_CONCEPTS = {
    "precision_gears": MDC.PrecisionGears,
    "precision_shafts": MDC.PrecisionShafts,
    "precision_metal_parts": MDC.PrecisionMetalParts,
}

PART_FAMILY_CONCEPTS = {
    "gear": MDC.Gear,
    "shaft": MDC.Shaft,
    "metal_part": MDC.MetalPart,
}

PART_TYPE_CONCEPTS = {
    "spur_gear": MDC.SpurGear,
    "helical_gear": MDC.HelicalGear,
    "bevel_gear": MDC.BevelGear,
    "worm_gear": MDC.WormGear,
    "crown_gear": MDC.CrownGear,
    "plain_shaft": MDC.PlainShaft,
    "stepped_shaft": MDC.SteppedShaft,
    "splined_shaft": MDC.SplinedShaft,
    "worm_shaft": MDC.WormShaft,
    "hollow_shaft": MDC.HollowShaft,
    "block": MDC.Block,
    "plate": MDC.Plate,
    "bracket": MDC.Bracket,
    "bushing": MDC.Bushing,
    "roller": MDC.Roller,
    "collar": MDC.Collar,
}

CAPABILITY_FIELD_CONCEPTS = {
    "module": MDC.Module,
    "diametral_pitch": MDC.DiametralPitch,
    "outside_diameter_mm": MDC.OutsideDiameterMm,
    "gear_quality": MDC.GearQuality,
    "length_mm": MDC.LengthMm,
    "outer_diameter_mm": MDC.OuterDiameterMm,
    "spline_module": MDC.SplineModule,
    "batch_size": MDC.BatchSize,
    "lead_time_weeks": MDC.LeadTimeWeeks,
    "weight_kg": MDC.WeightKg,
    "surface_finish_ra_um": MDC.SurfaceFinishRaUm,
    "tolerance_mm": MDC.ToleranceMm,
    "quality": MDC.Quality,
    "bounding_box_mm": MDC.BoundingBoxMm,
    "inner_diameter_mm": MDC.InnerDiameterMm,
    "wall_thickness_mm": MDC.WallThicknessMm,
    "face_width_mm": MDC.FaceWidthMm,
    "helix_angle_deg": MDC.HelixAngleDeg,
    "shaft_angle_deg": MDC.ShaftAngleDeg,
    "center_distance_mm": MDC.CenterDistanceMm,
    "principal_diameter_mm": MDC.PrincipalDiameterMm,
    "number_of_steps": MDC.NumberOfSteps,
    "spline_length_mm": MDC.SplineLengthMm,
    "worm_module": MDC.WormModule,
    "number_of_starts": MDC.NumberOfStarts,
    "overall_length_mm": MDC.OverallLengthMm,
    "number_of_holes": MDC.NumberOfHoles,
    "vertical_flange_length_mm": MDC.VerticalFlangeLengthMm,
    "horizontal_flange_length_mm": MDC.HorizontalFlangeLengthMm,
    "flange_diameter_mm": MDC.FlangeDiameterMm,
    "width_mm": MDC.WidthMm,
    "height_mm": MDC.HeightMm,
}

MATERIAL_CONCEPTS = {
    "alloyed_carburizing_steel": MDC.AlloyedCarburizingSteel,
    "steel": MDC.Steel,
    "aluminum": MDC.Aluminum,
    "stainless_steel": MDC.StainlessSteel,
    "titanium": MDC.Titanium,
    "nickel_alloy": MDC.NickelAlloy,
}

PROCESS_CONCEPTS = {
    "machining": MDC.Machining,
    "turning": MDC.Turning,
    "hobbing": MDC.Hobbing,
    "gear_shaping": MDC.GearShaping,
    "deburring": MDC.Deburring,
    "hard_turning": MDC.HardTurning,
    "grinding": MDC.Grinding,
    "tooth_grinding": MDC.ToothGrinding,
    "gear_grinding": MDC.GearGrinding,
    "gear_cutting": MDC.GearCutting,
    "surface_grinding": MDC.SurfaceGrinding,
    "milling": MDC.Milling,
    "turn_mill": MDC.TurnMill,
}

CERTIFICATION_CONCEPTS = {
    "ISO9001_2015": MDC.ISO90012015,
    "ISO_TS_16949_partial": MDC.ISO_TS_16949_partial,
    "APQP": MDC.APQP,
    "ISO14001_2015": MDC.ISO140012015,
    "aerospace_traceability": MDC.AerospaceTraceability,
    "full_traceability": MDC.FullTraceability,
}


def safe_identifier(value: str) -> str:
    return (
        value.replace("-", "_")
        .replace("/", "_")
        .replace(" ", "_")
        .replace(".", "_")
        .replace(":", "_")
    )


def _concept(mapping: dict[str, URIRef], value: str, label: str) -> URIRef:
    try:
        return mapping[value]
    except KeyError as exc:
        raise ServiceDiscoveryRdfMappingError(
            f"Unsupported {label} identifier: {value}"
        ) from exc


def get_service_category_concept(value: str) -> URIRef:
    return _concept(SERVICE_CATEGORY_CONCEPTS, value, "service_category")


def get_part_family_concept(value: str) -> URIRef:
    return _concept(PART_FAMILY_CONCEPTS, value, "part_family")


def get_part_type_concept(value: str) -> URIRef:
    return _concept(PART_TYPE_CONCEPTS, value, "part_type")


def get_capability_field_concept(value: str) -> URIRef:
    return _concept(CAPABILITY_FIELD_CONCEPTS, value, "capability field")


def get_material_concept(value: str) -> URIRef:
    return _concept(MATERIAL_CONCEPTS, value, "material")


def get_process_concept(value: str) -> URIRef:
    return _concept(PROCESS_CONCEPTS, value, "process")


def get_certification_concept(value: str) -> URIRef:
    return _concept(CERTIFICATION_CONCEPTS, value, "certification")


def provider_resource(provider_id: str) -> URIRef:
    return MDC[f"provider_{safe_identifier(provider_id)}"]


def offering_resource(offering_id: str) -> URIRef:
    return MDC[f"offering_{safe_identifier(offering_id)}"]


def part_type_support_resource(offering_id: str, part_type: str) -> URIRef:
    return MDC[f"part_type_support_{safe_identifier(offering_id)}_{safe_identifier(part_type)}"]


def family_capability_resource(offering_id: str, field_code: str) -> URIRef:
    return MDC[f"family_capability_{safe_identifier(offering_id)}_{safe_identifier(field_code)}"]


def part_type_capability_resource(offering_id: str, part_type: str, field_code: str) -> URIRef:
    return MDC[
        f"part_type_capability_{safe_identifier(offering_id)}_"
        f"{safe_identifier(part_type)}_{safe_identifier(field_code)}"
    ]


def generic_capability_resource(offering_id: str, field_code: str) -> URIRef:
    return MDC[f"generic_capability_{safe_identifier(offering_id)}_{safe_identifier(field_code)}"]


def material_evidence_resource(offering_id: str, material_code: str) -> URIRef:
    return MDC[f"material_evidence_{safe_identifier(offering_id)}_{safe_identifier(material_code)}"]


def available_grade_evidence_resource(offering_id: str, material_code: str, sequence_index: int) -> URIRef:
    return MDC[
        f"available_grade_evidence_{safe_identifier(offering_id)}_"
        f"{safe_identifier(material_code)}_{sequence_index}"
    ]


def process_evidence_resource(offering_id: str, process_code: str) -> URIRef:
    return MDC[f"process_evidence_{safe_identifier(offering_id)}_{safe_identifier(process_code)}"]


def certification_evidence_resource(provider_id: str, certification_code: str) -> URIRef:
    return MDC[
        f"certification_evidence_{safe_identifier(provider_id)}_"
        f"{safe_identifier(certification_code)}"
    ]


def component_evidence_resource(parent_resource: URIRef, component_field: str) -> URIRef:
    return MDC[
        f"component_{safe_identifier(str(parent_resource).split('#')[-1])}_"
        f"{safe_identifier(component_field)}"
    ]
