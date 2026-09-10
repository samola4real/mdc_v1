# F4_E4 Consumer Search Backend Contract Alignment Report

## 1. Purpose and scope

This frontend-only change aligns the Consumer Search Metal part payload with the backend service-discovery search contract described in the F4_E4 task request.

No backend code, provider demo code, role/login code, admin/audit code, API service modules, packages, `.env`, runtime config, route config, or Keycloak files were modified.

## 2. Backend contract findings used

The requested backend audit report path, `docs/21_service_discovery_search_contract_backend_audit_report.md`, was not present in this workspace during inspection. The contract findings used came from the F4_E4 task text:

- Accepted service categories: `precision_gears`, `precision_shafts`, `precision_metal_parts`.
- Accepted part families: `gear`, `shaft`, `metal_part`.
- Accepted Metal part types: `block`, `plate`, `bracket`, `bushing`, `roller`, `collar`.
- Rejected Metal part types: `collar_hub`, `custom_metal_part`.
- Material, process, and certification filters must be sent in `requirements.generic_requirements` with plural keys.
- Singular `material` and `certification` must not be sent in `part_family_specifications`.

## 3. Service category derivation

Consumer Search now derives `service_category` from `part_family`:

- `gear` -> `precision_gears`
- `shaft` -> `precision_shafts`
- `metal_part` -> `precision_metal_parts`

The Service category control is rendered as a disabled read-only text field. The payload builder also derives the value independently, so stale UI state cannot submit incompatible values such as `turn_mill_services`.

## 4. Metal-part part type value changes

Metal part options now use backend-accepted values only:

```javascript
[
  { label: "Block", value: "block" },
  { label: "Plate", value: "plate" },
  { label: "Bracket", value: "bracket" },
  { label: "Bushing", value: "bushing" },
  { label: "Roller", value: "roller" },
  { label: "Collar", value: "collar" }
]
```

Unsupported active search values `collar_hub` and `custom_metal_part` were removed from the Consumer Search Metal part dropdown. The payload builder also normalizes stale unsupported Metal part values to `block` before submission.

## 5. Requirement grouping changes

For all part families, selected material, processes, and certification are now grouped only in:

```text
requirements.generic_requirements
```

using:

```text
materials
processes
certifications
```

Metal part no longer sends singular `material` or `certification`, or `processes`, inside `part_family_specifications`.

For Metal part, `weight_kg` and `surface_finish_ra_um` are also sent in `generic_requirements`. For Block, Plate, and Bracket, `tolerance_mm` is also generic because their family specs use `bounding_box_mm`.

## 6. Metal-part payload mapping by type

Block:

- `part_family_specifications.bounding_box_mm.length_mm`
- `part_family_specifications.bounding_box_mm.width_mm`
- `part_family_specifications.bounding_box_mm.height_mm`
- `part_type_specifications.number_of_holes`

Plate:

- `part_family_specifications.bounding_box_mm.length_mm`
- `part_family_specifications.bounding_box_mm.width_mm`
- `part_family_specifications.bounding_box_mm.height_mm`, mapped from the frontend thickness input
- `part_type_specifications.number_of_holes`

Bracket:

- `part_family_specifications.bounding_box_mm.length_mm`
- `part_family_specifications.bounding_box_mm.width_mm`
- `part_family_specifications.bounding_box_mm.height_mm`
- `part_type_specifications.vertical_flange_length_mm`
- `part_type_specifications.horizontal_flange_length_mm`

Bushing:

- `part_family_specifications.inner_diameter_mm`
- `part_family_specifications.outer_diameter_mm`
- `part_family_specifications.overall_length_mm`
- `part_family_specifications.tolerance_mm`
- `part_type_specifications.flange_diameter_mm`

Roller:

- `part_family_specifications.inner_diameter_mm`, mapped from the frontend shaft/bore diameter input
- `part_family_specifications.outer_diameter_mm`
- `part_family_specifications.overall_length_mm`
- `part_family_specifications.tolerance_mm`
- empty `part_type_specifications`

Collar:

- `part_family_specifications.inner_diameter_mm`, mapped from the frontend bore diameter input
- `part_family_specifications.outer_diameter_mm`
- `part_family_specifications.overall_length_mm`
- `part_family_specifications.tolerance_mm`
- empty `part_type_specifications`

Unsupported Metal part keys such as `holes_or_cutouts`, `cutout_details`, `flange_length_mm`, `mounting_holes_count`, `hole_diameter_mm`, `thickness_mm`, and `surface_finish` are no longer submitted.

## 7. Gear/Shaft regression protection

Gear and Shaft still use their existing part-family and part-type technical specification branches.

Their service categories are now derived as:

- Gear: `precision_gears`
- Shaft: `precision_shafts`

Their material, process, and certification filters remain in `generic_requirements`.

## 8. Files modified

- `subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `subsystem/frontend/src/components/mdc/mockData.js`
- `docs/22_mdc_demo_consumer_search_backend_contract_alignment_report.md`

## 9. Commands run

- `Get-Content -Path C:\Users\Elahi\.codex\attachments\09c216dc-dac0-4958-9ef6-da80c00e10e8\pasted-text.txt`
- `Get-Content -Path docs/21_service_discovery_search_contract_backend_audit_report.md`
- `Get-Content -Path subsystem/frontend/src/components/mdc/mockData.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/SearchPayloadPreview.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/SearchErrorMessage.js`
- `Get-Content -Path docs/18_mdc_demo_consumer_search_metal_part_type_specific_fields_report.md`
- `Get-Content -Path docs/19_mdc_demo_consumer_search_payload_deduplication_report.md`
- `rg -n "collar_hub|custom_metal_part|surface_finish\\b|material: form.material|certification: form.certification|consumerServiceCategories|serviceCategories|exactValue|renderYesNoField" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js subsystem/frontend/src/components/mdc/mockData.js`
- `rg -n "service_category|part_family_specifications|generic_requirements|bounding_box_mm|surface_finish_ra_um|number_of_holes|overall_length_mm" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `git diff -- subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js subsystem/frontend/src/components/mdc/mockData.js docs/22_mdc_demo_consumer_search_backend_contract_alignment_report.md`
- `git status --short subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js subsystem/frontend/src/components/mdc/mockData.js docs/22_mdc_demo_consumer_search_backend_contract_alignment_report.md`
- `npm run lint` from `subsystem/frontend`
- `rg -n "serviceCategory|consumerServiceCategories|serviceCategories" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `rg -n "collar_hub|custom_metal_part|material: form.material|certification: form.certification|surface_finish\\b|holes_or_cutouts|cutout_details|mounting_holes_count|hole_diameter_mm|thickness_mm" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js subsystem/frontend/src/components/mdc/mockData.js`

## 10. Manual verification notes

Recommended browser checks while the user runs `npm run dev`:

1. Open `http://localhost:3000/demo/consumer-search`.
2. Select Gear and confirm payload has `service_category: "precision_gears"` and material/process/certification filters in `generic_requirements`.
3. Select Shaft and confirm payload has `service_category: "precision_shafts"` and material/process/certification filters in `generic_requirements`.
4. Select Metal part -> Block and confirm payload has `service_category: "precision_metal_parts"`, `part_family: "metal_part"`, `part_type: "block"`, `bounding_box_mm`, `number_of_holes`, and generic material/process/certification filters.
5. Confirm Metal part payload does not include `turn_mill_services`, singular `material`, singular `certification`, `collar_hub`, or `custom_metal_part`.
6. Submit Metal part search and confirm the previous errors about invalid service category and invalid `material` in family specs disappear.

## 11. Remaining limitations

The backend audit report file was missing locally, so this change used the contract details supplied in the task text. Browser/backend retesting was not run in this session, so any new backend validation error is unknown. If the backend returns empty results for Metal part, that is compatible with the task note that no matching Metal part provider records may exist.
