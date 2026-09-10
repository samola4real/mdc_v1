# F4_E2 Consumer Search Metal-Part Fields Report

## 1. Purpose and scope

This frontend-only change completes the active Metal part path in Consumer Search. It adds metal-part part type options, metal-part dynamic technical fields, and metal-part-specific payload construction while preserving the existing Gear and Shaft flows.

## 2. Metal-part part type options added

Consumer Search now uses label/value metal-part part type options:

```javascript
[
  { label: 'Block', value: 'block' },
  { label: 'Bracket', value: 'bracket' },
  { label: 'Plate', value: 'plate' },
  { label: 'Bushing', value: 'bushing' },
  { label: 'Roller', value: 'roller' },
  { label: 'Collar / hub', value: 'collar_hub' },
  { label: 'Custom metal part', value: 'custom_metal_part' }
]
```

The shared raw `partTypes.metalParts` array remains available for other demo components. Consumer Search uses the new `metalPartTypeOptions` export.

## 3. Metal-part dynamic fields added

Selecting `Metal part` now shows a `Metal-part technical fields` group with:

- Length mm
- Width mm
- Height mm
- Thickness mm
- Diameter mm
- Weight kg
- Tolerance mm
- Surface finish
- Holes / cut-outs

The temporary F4_E1 “coming next” warning is removed from the active metal-part path.

## 4. Payload construction for metal_part

Metal part now submits the same top-level search payload shape as gear and shaft:

```javascript
{
  request_id,
  consumer_id,
  service_category,
  part_family,
  part_type,
  requirements: {
    part_family_specifications,
    part_type_specifications,
    generic_requirements
  },
  match_policy
}
```

For `part_family: "metal_part"`, the form sends:

```javascript
service_category: "precision_metal_parts"
part_type: "block" // or selected metal-part type
requirements: {
  part_family_specifications: {
    material,
    processes,
    certification
  },
  part_type_specifications: {
    length_mm,
    width_mm,
    height_mm,
    thickness_mm,
    diameter_mm,
    weight_kg,
    tolerance_mm,
    surface_finish,
    holes_or_cutouts
  },
  generic_requirements: {
    materials,
    processes,
    certifications
  }
}
```

Metal part does not send gear-specific fields such as `module`, `diametral_pitch`, `gear_quality`, `face_width_mm`, or `outside_diameter_mm`. It also does not send shaft-specific fields such as `spline_module`, `inner_diameter_mm`, or `wall_thickness_mm`.

## 5. Gear/Shaft behaviour preserved

Gear still defaults to:

- `service_category: "precision_gears"`
- `part_family: "gear"`
- `part_type: "spur_gear"`

Shaft still defaults to:

- `service_category: "precision_shafts"`
- `part_family: "shaft"`
- `part_type: "splined_shaft"`

Gear and Shaft dynamic field groups are unchanged.

## 6. Files modified

- `subsystem/frontend/src/components/mdc/mockData.js`
- `subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`

## 7. Commands run

- `Get-Content` to inspect requested files.
- `rg` to verify metal-part references and removed temporary-blocking behavior.
- `npm run lint` from `subsystem/frontend`.

## 8. Manual verification notes

Manual browser verification was not run in this session. Recommended checks:

1. Open `/demo/consumer-search`.
2. Select Gear and confirm gear fields, gear part types, and enabled Search.
3. Select Shaft and confirm shaft fields, shaft part types, and enabled Search.
4. Select Metal part and confirm metal-part part types, metal-part fields, and enabled Search.
5. Confirm metal-part payload preview shows `part_family: "metal_part"` and `part_type: "block"` by default.
6. Confirm metal-part payload does not include gear or shaft technical fields.
7. Submit Metal part search and confirm the UI shows either provider results or a clean backend validation/error message.

## 9. Remaining backend compatibility risks

`precision_metal_parts` and the metal-part requirement keys must still be verified against the backend search contract. If the backend rejects the payload, F4_E3 should adjust only the field keys and controlled values accepted by the backend.

## 10. Recommended next phase F4_E3

`F4_E3 - Verify metal-part payload compatibility with backend search endpoint and adjust only accepted field keys.`
