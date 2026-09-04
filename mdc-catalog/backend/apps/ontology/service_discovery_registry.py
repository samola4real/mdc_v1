from copy import deepcopy


SERVICE_CATEGORIES = [
    {
        "value": "precision_gears",
        "label": "Precision gears",
        "part_family": "gear",
    },
    {
        "value": "precision_shafts",
        "label": "Precision shafts",
        "part_family": "shaft",
    },
    {
        "value": "precision_metal_parts",
        "label": "Precision metal parts",
        "part_family": "metal_part",
    },
]

SERVICE_DISCOVERY_PART_FAMILIES = [
    {
        "value": "gear",
        "label": "Gear",
        "service_category": "precision_gears",
        "part_types": [
            "spur_gear",
            "helical_gear",
            "bevel_gear",
            "worm_gear",
            "crown_gear",
        ],
    },
    {
        "value": "shaft",
        "label": "Shaft",
        "service_category": "precision_shafts",
        "part_types": [
            "plain_shaft",
            "stepped_shaft",
            "splined_shaft",
            "worm_shaft",
            "hollow_shaft",
        ],
    },
    {
        "value": "metal_part",
        "label": "Metal part",
        "service_category": "precision_metal_parts",
        "part_types": [
            "block",
            "plate",
            "bracket",
            "bushing",
            "roller",
            "collar",
        ],
    },
]

GENERIC_REQUIREMENT_FIELDS = [
    "materials",
    "processes",
    "batch_size",
    "delivery.max_weeks",
    "certifications",
    "surface_finish_ra_um",
    "tolerance_mm",
    "quality",
    "weight_kg",
]

GEAR_FAMILY_COMMON_FIELDS = [
    "module",
    "diametral_pitch",
    "number_of_teeth",
    "outside_diameter_mm",
    "gear_quality",
    "tolerance_mm",
]

SHAFT_FAMILY_COMMON_FIELDS = [
    "length_mm",
    "outer_diameter_mm",
    "tolerance_mm",
]

ROTATIONAL_METAL_PART_COMMON_FIELDS = [
    "inner_diameter_mm",
    "outer_diameter_mm",
    "overall_length_mm",
    "tolerance_mm",
]

PART_TYPE_PROFILES = {
    "spur_gear": {
        "value": "spur_gear",
        "label": "Spur gear",
        "service_category": "precision_gears",
        "part_family": "gear",
        "geometry_class": "rotational",
        "family_common_fields": GEAR_FAMILY_COMMON_FIELDS,
        "part_type_specific_fields": [
            "face_width_mm",
        ],
    },
    "helical_gear": {
        "value": "helical_gear",
        "label": "Helical gear",
        "service_category": "precision_gears",
        "part_family": "gear",
        "geometry_class": "rotational",
        "family_common_fields": GEAR_FAMILY_COMMON_FIELDS,
        "part_type_specific_fields": [
            "face_width_mm",
            "helix_angle_deg",
        ],
    },
    "bevel_gear": {
        "value": "bevel_gear",
        "label": "Bevel gear",
        "service_category": "precision_gears",
        "part_family": "gear",
        "geometry_class": "rotational",
        "family_common_fields": GEAR_FAMILY_COMMON_FIELDS,
        "part_type_specific_fields": [
            "face_width_mm",
            "shaft_angle_deg",
        ],
    },
    "worm_gear": {
        "value": "worm_gear",
        "label": "Worm gear",
        "service_category": "precision_gears",
        "part_family": "gear",
        "geometry_class": "rotational",
        "family_common_fields": GEAR_FAMILY_COMMON_FIELDS,
        "part_type_specific_fields": [
            "center_distance_mm",
            "shaft_angle_deg",
        ],
    },
    "crown_gear": {
        "value": "crown_gear",
        "label": "Crown gear",
        "service_category": "precision_gears",
        "part_family": "gear",
        "geometry_class": "rotational",
        "family_common_fields": GEAR_FAMILY_COMMON_FIELDS,
        "part_type_specific_fields": [
            "face_width_mm",
            "inner_diameter_mm",
        ],
    },
    "plain_shaft": {
        "value": "plain_shaft",
        "label": "Plain shaft",
        "service_category": "precision_shafts",
        "part_family": "shaft",
        "geometry_class": "rotational",
        "family_common_fields": SHAFT_FAMILY_COMMON_FIELDS,
        "part_type_specific_fields": [
            "principal_diameter_mm",
        ],
    },
    "stepped_shaft": {
        "value": "stepped_shaft",
        "label": "Stepped shaft",
        "service_category": "precision_shafts",
        "part_family": "shaft",
        "geometry_class": "rotational",
        "family_common_fields": SHAFT_FAMILY_COMMON_FIELDS,
        "part_type_specific_fields": [
            "number_of_steps",
        ],
    },
    "splined_shaft": {
        "value": "splined_shaft",
        "label": "Splined shaft",
        "service_category": "precision_shafts",
        "part_family": "shaft",
        "geometry_class": "rotational",
        "family_common_fields": SHAFT_FAMILY_COMMON_FIELDS,
        "part_type_specific_fields": [
            "spline_module",
            "spline_length_mm",
        ],
    },
    "worm_shaft": {
        "value": "worm_shaft",
        "label": "Worm shaft",
        "service_category": "precision_shafts",
        "part_family": "shaft",
        "geometry_class": "rotational",
        "family_common_fields": SHAFT_FAMILY_COMMON_FIELDS,
        "part_type_specific_fields": [
            "worm_module",
            "number_of_starts",
        ],
    },
    "hollow_shaft": {
        "value": "hollow_shaft",
        "label": "Hollow shaft",
        "service_category": "precision_shafts",
        "part_family": "shaft",
        "geometry_class": "rotational",
        "family_common_fields": SHAFT_FAMILY_COMMON_FIELDS,
        "part_type_specific_fields": [
            "inner_diameter_mm",
            "wall_thickness_mm",
        ],
    },
    "block": {
        "value": "block",
        "label": "Block",
        "service_category": "precision_metal_parts",
        "part_family": "metal_part",
        "geometry_class": "prismatic",
        "family_common_fields": [
            "bounding_box_mm",
        ],
        "part_type_specific_fields": [
            "number_of_holes",
        ],
    },
    "plate": {
        "value": "plate",
        "label": "Plate",
        "service_category": "precision_metal_parts",
        "part_family": "metal_part",
        "geometry_class": "prismatic",
        "family_common_fields": [
            "bounding_box_mm",
        ],
        "part_type_specific_fields": [
            "number_of_holes",
        ],
    },
    "bracket": {
        "value": "bracket",
        "label": "Bracket",
        "service_category": "precision_metal_parts",
        "part_family": "metal_part",
        "geometry_class": "prismatic",
        "family_common_fields": [
            "bounding_box_mm",
        ],
        "part_type_specific_fields": [
            "vertical_flange_length_mm",
            "horizontal_flange_length_mm",
        ],
    },
    "bushing": {
        "value": "bushing",
        "label": "Bushing",
        "service_category": "precision_metal_parts",
        "part_family": "metal_part",
        "geometry_class": "rotational",
        "family_common_fields": ROTATIONAL_METAL_PART_COMMON_FIELDS,
        "part_type_specific_fields": [
            "flange_diameter_mm",
        ],
    },
    "roller": {
        "value": "roller",
        "label": "Roller",
        "service_category": "precision_metal_parts",
        "part_family": "metal_part",
        "geometry_class": "rotational",
        "family_common_fields": ROTATIONAL_METAL_PART_COMMON_FIELDS,
        "part_type_specific_fields": [],
    },
    "collar": {
        "value": "collar",
        "label": "Collar",
        "service_category": "precision_metal_parts",
        "part_family": "metal_part",
        "geometry_class": "rotational",
        "family_common_fields": ROTATIONAL_METAL_PART_COMMON_FIELDS,
        "part_type_specific_fields": [],
    },
}

FIELD_DEFINITIONS = {
    "module": {
        "label": "Module",
        "input_shape": "range_or_exact",
        "scope": "gear_family",
        "unit": "mm",
    },
    "diametral_pitch": {
        "label": "Diametral pitch",
        "input_shape": "range_or_exact",
        "scope": "gear_family",
    },
    "number_of_teeth": {
        "label": "Number of teeth",
        "input_shape": "positive_integer_range_or_exact",
        "scope": "gear_family",
    },
    "outside_diameter_mm": {
        "label": "Outside diameter",
        "input_shape": "range_or_exact",
        "scope": "gear_family",
        "unit": "mm",
        "note": (
            "Tooth-tip/addendum boundary diameter for external gears. "
            "For bevel gears this refers to the outside diameter at the crown/outer end. "
            "Future internal gears must use inside_diameter_mm rather than this field."
        ),
    },
    "gear_quality": {
        "label": "Gear quality",
        "input_shape": "quality_standard_and_class",
        "scope": "gear_family",
        "note": (
            "Gear accuracy class under a named standard such as DIN or ISO. "
            "This is distinct from general dimensional tolerance_mm and must not be "
            "converted into a ± tolerance value."
        ),
    },
    "tolerance_mm": {
        "label": "Tolerance",
        "input_shape": "range_or_exact",
        "scope": "generic_or_family_specific",
        "unit": "mm",
    },
    "face_width_mm": {
        "label": "Face width",
        "input_shape": "range_or_exact",
        "scope": "gear_part_type",
        "unit": "mm",
    },
    "helix_angle_deg": {
        "label": "Helix angle",
        "input_shape": "range_or_exact",
        "scope": "helical_gear",
        "unit": "deg",
    },
    "shaft_angle_deg": {
        "label": "Shaft angle",
        "input_shape": "range_or_exact",
        "scope": "gear_part_type",
        "unit": "deg",
    },
    "center_distance_mm": {
        "label": "Center distance",
        "input_shape": "range_or_exact",
        "scope": "worm_gear",
        "unit": "mm",
        "note": (
            "Mating/interface requirement for a worm-gear pair; not automatically "
            "a standalone manufactured-part dimension."
        ),
    },
    "inner_diameter_mm": {
        "label": "Inner diameter",
        "input_shape": "range_or_exact",
        "scope": "crown_gear_or_rotational_metal_part_or_hollow_shaft",
        "unit": "mm",
    },
    "length_mm": {
        "label": "Length",
        "input_shape": "range_or_exact",
        "scope": "shaft_or_bounding_box_component",
        "unit": "mm",
    },
    "width_mm": {
        "label": "Width",
        "input_shape": "range_or_exact",
        "scope": "bounding_box_component",
        "unit": "mm",
    },
    "height_mm": {
        "label": "Height",
        "input_shape": "range_or_exact",
        "scope": "bounding_box_component",
        "unit": "mm",
    },
    "outer_diameter_mm": {
        "label": "Outer diameter",
        "input_shape": "range_or_exact",
        "scope": "shaft_or_rotational_metal_part",
        "unit": "mm",
        "note": (
            "Outer diameter for shafts and rotational metal parts. "
            "This is distinct from gear outside_diameter_mm."
        ),
    },
    "principal_diameter_mm": {
        "label": "Principal diameter",
        "input_shape": "range_or_exact",
        "scope": "plain_shaft",
        "unit": "mm",
    },
    "number_of_steps": {
        "label": "Number of steps",
        "input_shape": "positive_integer_range_or_exact",
        "scope": "stepped_shaft",
    },
    "spline_module": {
        "label": "Spline module",
        "input_shape": "range_or_exact",
        "scope": "splined_shaft",
    },
    "spline_length_mm": {
        "label": "Spline length",
        "input_shape": "range_or_exact",
        "scope": "splined_shaft",
        "unit": "mm",
    },
    "worm_module": {
        "label": "Worm module",
        "input_shape": "range_or_exact",
        "scope": "worm_shaft",
    },
    "number_of_starts": {
        "label": "Number of starts",
        "input_shape": "positive_integer_range_or_exact",
        "scope": "worm_shaft",
    },
    "wall_thickness_mm": {
        "label": "Wall thickness",
        "input_shape": "range_or_exact",
        "scope": "hollow_shaft",
        "unit": "mm",
    },
    "bounding_box_mm": {
        "label": "Bounding box",
        "input_shape": "composite_dimensions",
        "scope": "prismatic_metal_part",
        "unit": "mm",
        "components": [
            "length_mm",
            "width_mm",
            "height_mm",
        ],
        "note": (
            "Applies to prismatic/complex metal parts such as blocks, plates, "
            "and brackets; not as a generic replacement for rotational gear "
            "or shaft dimensions."
        ),
    },
    "overall_length_mm": {
        "label": "Overall length",
        "input_shape": "range_or_exact",
        "scope": "rotational_metal_part",
        "unit": "mm",
    },
    "number_of_holes": {
        "label": "Number of holes",
        "input_shape": "positive_integer_range_or_exact",
        "scope": "prismatic_metal_part",
    },
    "vertical_flange_length_mm": {
        "label": "Vertical flange length",
        "input_shape": "range_or_exact",
        "scope": "bracket",
        "unit": "mm",
    },
    "horizontal_flange_length_mm": {
        "label": "Horizontal flange length",
        "input_shape": "range_or_exact",
        "scope": "bracket",
        "unit": "mm",
    },
    "flange_diameter_mm": {
        "label": "Flange diameter",
        "input_shape": "range_or_exact",
        "scope": "bushing",
        "unit": "mm",
    },
    "materials": {
        "label": "Materials",
        "input_shape": "multi_select",
        "scope": "generic_requirement",
        "note": (
            "Consumer-selectable material-family criterion. Material grades are "
            "not consumer-selectable search input in the harmonized "
            "service-discovery contract."
        ),
    },
    "processes": {
        "label": "Processes",
        "input_shape": "multi_select",
        "scope": "generic_requirement",
    },
    "batch_size": {
        "label": "Batch size",
        "input_shape": "positive_integer",
        "scope": "generic_requirement",
        "unit": "pcs",
    },
    "delivery.max_weeks": {
        "label": "Maximum delivery time",
        "input_shape": "positive_number",
        "scope": "generic_requirement",
        "unit": "weeks",
    },
    "certifications": {
        "label": "Certifications",
        "input_shape": "multi_select",
        "scope": "generic_requirement",
    },
    "surface_finish_ra_um": {
        "label": "Surface finish Ra",
        "input_shape": "range_or_exact",
        "scope": "generic_requirement",
        "unit": "um",
    },
    "quality": {
        "label": "Quality",
        "input_shape": "quality_standard_and_class",
        "scope": "generic_requirement",
        "note": (
            "Generic quality-reference field. It must not silently replace the "
            "specialised gear_quality field."
        ),
    },
    "weight_kg": {
        "label": "Weight",
        "input_shape": "positive_number",
        "scope": "generic_requirement",
        "unit": "kg",
    },
}


def get_service_discovery_registry() -> dict:
    assembled_profiles = deepcopy(PART_TYPE_PROFILES)

    for profile in assembled_profiles.values():
        profile["generic_requirement_fields"] = deepcopy(GENERIC_REQUIREMENT_FIELDS)

    return {
        "registry_version": "m18_harmonized_v1",
        "search_contract_active": True,
        "note": (
            "This registry supports Marketplace dynamic form rendering. "
            "The harmonized service-discovery search request contract is active "
            "through POST /api/service-discovery/search. API contract evolution "
            "uses contract_version metadata rather than URL-versioned routes."
        ),
        "service_categories": deepcopy(SERVICE_CATEGORIES),
        "part_families": deepcopy(SERVICE_DISCOVERY_PART_FAMILIES),
        "part_type_profiles": assembled_profiles,
        "field_definitions": deepcopy(FIELD_DEFINITIONS),
        "generic_requirement_fields": deepcopy(GENERIC_REQUIREMENT_FIELDS),
    }
