# MaaSAI MDC - Service Discovery Search Contract Backend Audit Report

## 1. Purpose and scope

This audit documents the exact backend request contract for:

```text
POST /api/service-discovery/search
```

No backend behavior was changed. The goal is to align the Consumer Search UI
with the accepted H4/H5 service-discovery search contract.

## 2. Accepted top-level payload fields

Accepted top-level fields are exactly:

```text
request_id
consumer_id
service_category
part_family
part_type
requirements
match_policy
```

`request_id`, `consumer_id`, `service_category`, `part_family`, and `part_type`
are required. `requirements` and `match_policy` are optional and default to empty
requirement groups and default match policy.

Rejected examples:

```text
selection
part_families
primary_match_mode
unexpected
```

## 3. Accepted service_category values

Accepted:

```text
precision_gears
precision_shafts
precision_metal_parts
```

Rejected:

```text
turn_mill_services
heat_treatment_services
```

The service category also fixes the part family:

```text
precision_gears -> gear
precision_shafts -> shaft
precision_metal_parts -> metal_part
```

## 4. Accepted part_family values

Accepted:

```text
gear
shaft
metal_part
```

Rejected:

```text
general_precision
```

`metal_part` is supported by the search request serializer and registry.

## 5. Accepted part_type values by family

Gear:

```text
spur_gear
helical_gear
bevel_gear
worm_gear
crown_gear
```

Shaft:

```text
plain_shaft
stepped_shaft
splined_shaft
worm_shaft
hollow_shaft
```

Metal part:

```text
block
plate
bracket
bushing
roller
collar
```

Rejected metal-part examples:

```text
collar_hub
custom_metal_part
```

## 6. Requirement group contract

Accepted requirement groups:

```text
requirements.part_family_specifications
requirements.part_type_specifications
requirements.generic_requirements
```

`requirements` may be omitted. If present, no other groups are accepted.

Generic requirements:

```text
materials
processes
batch_size
delivery
certifications
surface_finish_ra_um
tolerance_mm
quality
weight_kg
```

`materials` must go in `generic_requirements` as a list. The singular key
`material` is not accepted.

`processes` must go in `generic_requirements` as a list. It is not accepted in
`part_family_specifications`.

`certifications` must go in `generic_requirements` as a list. The singular key
`certification` is not accepted.

`material_grades` is not accepted as a consumer search input. Material grades
may appear only as response evidence.

Fields cannot be duplicated across requirement groups.

## 7. Gear field contract

Use:

```text
service_category = precision_gears
part_family = gear
```

Gear family fields in `part_family_specifications`:

```text
module
diametral_pitch
number_of_teeth
outside_diameter_mm
gear_quality
tolerance_mm
```

Gear part-type fields in `part_type_specifications`:

```text
spur_gear:    face_width_mm
helical_gear: face_width_mm, helix_angle_deg
bevel_gear:  face_width_mm, shaft_angle_deg
worm_gear:   center_distance_mm, shaft_angle_deg
crown_gear:  face_width_mm, inner_diameter_mm
```

Rejected for spur gear:

```text
diameter_mm
outer_diameter_mm
face_width_mm in part_family_specifications
outside_diameter_mm in part_type_specifications
```

## 8. Shaft field contract

Use:

```text
service_category = precision_shafts
part_family = shaft
```

Shaft family fields in `part_family_specifications`:

```text
length_mm
outer_diameter_mm
tolerance_mm
```

Shaft part-type fields in `part_type_specifications`:

```text
plain_shaft:   principal_diameter_mm
stepped_shaft: number_of_steps
splined_shaft: spline_module, spline_length_mm
worm_shaft:    worm_module, number_of_starts
hollow_shaft:  inner_diameter_mm, wall_thickness_mm
```

Rejected shaft examples:

```text
outside_diameter_mm
shaft_quality
spline_diametral_pitch
```

## 9. Metal-part support status

`metal_part` is backend-supported by the request serializer and registry.

Use:

```text
service_category = precision_metal_parts
part_family = metal_part
```

Accepted metal-part part types:

```text
block
plate
bracket
bushing
roller
collar
```

Prismatic metal parts:

```text
block:
  part_family_specifications: bounding_box_mm
  part_type_specifications: number_of_holes

plate:
  part_family_specifications: bounding_box_mm
  part_type_specifications: number_of_holes

bracket:
  part_family_specifications: bounding_box_mm
  part_type_specifications: vertical_flange_length_mm, horizontal_flange_length_mm
```

`bounding_box_mm` is an object with components:

```text
length_mm
width_mm
height_mm
```

Rotational metal parts:

```text
bushing:
  part_family_specifications: inner_diameter_mm, outer_diameter_mm, overall_length_mm, tolerance_mm
  part_type_specifications: flange_diameter_mm

roller:
  part_family_specifications: inner_diameter_mm, outer_diameter_mm, overall_length_mm, tolerance_mm
  part_type_specifications: none

collar:
  part_family_specifications: inner_diameter_mm, outer_diameter_mm, overall_length_mm, tolerance_mm
  part_type_specifications: none
```

Frontend field mapping notes:

```text
length_mm/width_mm/height_mm -> bounding_box_mm components for block/plate/bracket
surface_finish -> surface_finish_ra_um in generic_requirements
weight_kg -> generic_requirements
holes_or_cutouts -> not accepted
thickness_mm -> not accepted
diameter_mm -> not accepted
flange_length_mm -> not accepted
mounting_holes_count -> not accepted
hole_diameter_mm -> not accepted
collar_hub -> not accepted as part_type
custom_metal_part -> not accepted as part_type
```

Search results for metal parts may still be empty unless curated service-
discovery provider data contains matching metal-part offerings. No matching
metal-part provider records were found in the inspected service-discovery YAML.

## 10. Valid example payloads

Valid gear search:

```json
{
  "request_id": "req_gear_001",
  "consumer_id": "consumer_demo",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear",
  "requirements": {
    "part_family_specifications": {
      "module": {"exact": 2.0},
      "outside_diameter_mm": {"max": 120},
      "gear_quality": {"standard": "DIN", "max_class": 5}
    },
    "part_type_specifications": {
      "face_width_mm": {"exact": 20}
    },
    "generic_requirements": {
      "materials": ["alloyed_carburizing_steel"],
      "processes": ["hobbing"],
      "certifications": ["ISO9001_2015"]
    }
  },
  "match_policy": {
    "optional_match_mode": "any",
    "unknown_policy": "keep_as_unknown",
    "minimum_score": null
  }
}
```

Valid shaft search:

```json
{
  "request_id": "req_shaft_001",
  "consumer_id": "consumer_demo",
  "service_category": "precision_shafts",
  "part_family": "shaft",
  "part_type": "hollow_shaft",
  "requirements": {
    "part_family_specifications": {
      "length_mm": {"max": 500},
      "outer_diameter_mm": {"max": 60}
    },
    "part_type_specifications": {
      "inner_diameter_mm": {"min": 10},
      "wall_thickness_mm": {"exact": 5}
    },
    "generic_requirements": {
      "processes": ["turn_mill"]
    }
  }
}
```

Valid metal-part search:

```json
{
  "request_id": "req_metal_part_001",
  "consumer_id": "consumer_demo",
  "service_category": "precision_metal_parts",
  "part_family": "metal_part",
  "part_type": "bracket",
  "requirements": {
    "part_family_specifications": {
      "bounding_box_mm": {
        "length_mm": {"max": 150},
        "width_mm": {"max": 80},
        "height_mm": {"max": 60}
      }
    },
    "part_type_specifications": {
      "vertical_flange_length_mm": {"max": 70},
      "horizontal_flange_length_mm": {"max": 120}
    },
    "generic_requirements": {
      "materials": ["steel"],
      "processes": ["machining"],
      "tolerance_mm": {"max": 0.05}
    }
  }
}
```

Valid metal-part bushing search:

```json
{
  "request_id": "req_bushing_001",
  "consumer_id": "consumer_demo",
  "service_category": "precision_metal_parts",
  "part_family": "metal_part",
  "part_type": "bushing",
  "requirements": {
    "part_family_specifications": {
      "inner_diameter_mm": {"min": 10},
      "outer_diameter_mm": {"max": 50},
      "overall_length_mm": {"max": 80},
      "tolerance_mm": {"max": 0.02}
    },
    "part_type_specifications": {
      "flange_diameter_mm": {"max": 70}
    }
  }
}
```

## 11. Current tests inspected/run

Inspected:

```text
backend/tests/test_service_discovery_search_serializer.py
backend/tests/test_service_discovery_search_normalizer.py
backend/tests/test_service_discovery_search_response_contract.py
backend/tests/test_service_discovery_local_matcher.py
backend/tests/test_service_discovery_sparql_service.py
backend/tests/test_api_v1.py
```

Focused command run:

```text
..\..\.venv\Scripts\python.exe manage.py test tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract -v 2
```

Result:

```text
Ran 45 tests in 0.083s
OK
```

## 12. Recommended frontend alignment

Use flat top-level selection fields, not nested `selection`:

```text
service_category
part_family
part_type
```

Map UI options to backend values:

```text
gear -> service_category precision_gears, part_family gear
shaft -> service_category precision_shafts, part_family shaft
metal_part -> service_category precision_metal_parts, part_family metal_part
```

Do not send:

```text
turn_mill_services
heat_treatment_services
general_precision
material
certification
processes in part_family_specifications
material in part_family_specifications
```

Put these fields only in `generic_requirements`:

```text
materials
processes
certifications
surface_finish_ra_um
weight_kg
batch_size
delivery
```

Use `bounding_box_mm` for prismatic metal-part dimensions rather than sending
top-level `length_mm`, `width_mm`, or `height_mm` in
`part_family_specifications`.

## 13. Whether backend changes are needed for live metal-part search

No backend serializer change is needed for metal-part request validation:
`metal_part` is already supported.

Backend data/search readiness may still need implementation for useful live
metal-part results. The current inspected service-discovery provider YAML did
not show metal-part offerings, so valid metal-part searches may return empty
results until curated/demo provider data includes matching
`precision_metal_parts` offerings.
