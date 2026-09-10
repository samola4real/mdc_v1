# F4_E2B Consumer Search Metal-Part Type-Specific Fields Report

## 1. Purpose and scope

This frontend-only change makes the `/demo/consumer-search` Metal part flow render different technical fields for each selected metal-part type. The change is limited to Consumer Search UI state, rendering, and payload construction.

No backend code, provider demo code, role/login code, admin/audit code, service modules, packages, runtime config, or `.env` files were modified.

## 2. Current issue

The earlier Metal part flow exposed one generic technical field group for all metal-part types. That made Block, Bracket, Plate, Bushing, Roller, Collar / hub, and Custom metal part look identical even though each type needs different dimensions and requirements.

## 3. Type-specific field groups implemented

The Metal part technical panel now changes based on `form.partType`:

- `block`: length, width, height, weight, holes / bores, pockets / slots, tolerance, surface finish.
- `bracket`: length, width, height / thickness, flange length, mounting holes count, hole diameter, weight, tolerance, surface finish.
- `plate`: length, width, thickness, holes / cut-outs, cut-out details, weight, tolerance, surface finish.
- `bushing`: inner diameter, outer diameter, length, wall thickness, material grade, tolerance, surface finish.
- `roller`: outer diameter, length, shaft/bore diameter, surface finish, material grade, weight, tolerance.
- `collar_hub`: bore diameter, outer diameter, length, keyway required, thread required, set screw required, tolerance, surface finish.
- `custom_metal_part`: part description, main dimensions, material, process, drawing available, tolerance, surface finish, additional requirements.

The panel header also changes by selected metal-part type.

## 4. Field reset and stale field prevention

The implementation does not clear every stored form value when the selected metal-part type changes. Instead, stale hidden values are prevented from leaking into the request by `buildMetalPartSpecifications(form)`, which emits only the keys relevant to the currently selected `partType`.

This means switching from one metal-part type to another can preserve previously entered values in browser state, but hidden fields are not included in the generated payload for the new type.

## 5. Payload construction changes

For Metal part, `requirements.part_type_specifications` is now built through `buildMetalPartSpecifications(form)`.

The emitted payload shapes are:

- `block`: `length_mm`, `width_mm`, `height_mm`, `weight_kg`, `holes_or_bores`, `pockets_or_slots`, `tolerance_mm`, `surface_finish`.
- `bracket`: `length_mm`, `width_mm`, `height_or_thickness_mm`, `flange_length_mm`, `mounting_holes_count`, `hole_diameter_mm`, `weight_kg`, `tolerance_mm`, `surface_finish`.
- `plate`: `length_mm`, `width_mm`, `thickness_mm`, `holes_or_cutouts`, `cutout_details`, `weight_kg`, `tolerance_mm`, `surface_finish`.
- `bushing`: `inner_diameter_mm`, `outer_diameter_mm`, `length_mm`, `wall_thickness_mm`, `material_grade`, `tolerance_mm`, `surface_finish`.
- `roller`: `outer_diameter_mm`, `length_mm`, `shaft_or_bore_diameter_mm`, `surface_finish`, `material_grade`, `weight_kg`, `tolerance_mm`.
- `collar_hub`: `bore_diameter_mm`, `outer_diameter_mm`, `length_mm`, `keyway_required`, `thread_required`, `set_screw_required`, `tolerance_mm`, `surface_finish`.
- `custom_metal_part`: `part_description`, `main_dimensions`, `material`, `process`, `drawing_available`, `tolerance_mm`, `surface_finish`, `additional_requirements`.

Gear-specific and shaft-specific technical keys remain excluded from Metal part payloads.

## 6. Gear/Shaft regression protection

The Gear and Shaft branches are still selected from `normalizedPartFamily` and retain their existing field rendering and payload branches.

Gear still uses gear part types and gear specifications. Shaft still uses shaft part types and shaft specifications. The Metal part changes are isolated behind `isMetalPart`.

## 7. Files modified

- `subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `subsystem/frontend/src/components/mdc/mockData.js`
- `docs/18_mdc_demo_consumer_search_metal_part_type_specific_fields_report.md`

## 8. Commands run

- `rg -n "renderMetalPartFields|Metal-part technical fields|isMetalPart \\? \\(" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js -TotalCount 520`
- `Get-Content -Path subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js -Tail 360`
- `git diff -- subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js subsystem/frontend/src/components/mdc/mockData.js`
- `Get-Content -Path docs/17_mdc_demo_consumer_search_metal_part_fields_report.md`
- `git status --short`
- `npm run lint` from `subsystem/frontend`

## 9. Manual verification notes

Recommended browser checks with `npm run dev` already running:

1. Open `/demo/consumer-search`.
2. Select `Metal part`.
3. Select each metal-part type and confirm the field group changes.
4. Confirm Search stays enabled for Metal part.
5. Confirm the payload preview includes only the currently selected metal-part type fields.
6. Recheck Gear and Shaft field groups and payload previews.

## 10. Remaining backend compatibility risks

The frontend now sends type-specific Metal part keys, but backend acceptance of each key still needs endpoint-level verification. If the backend rejects a Metal part search request, the next step should adjust only the field names or controlled values expected by the backend search contract.

## 11. Recommended next phase F4_E3

Run browser/API verification against the backend search endpoint and align Metal part payload keys with the backend contract if validation errors appear.
