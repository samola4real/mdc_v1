# F4_E1 Consumer Search Dropdown Normalization Report

## 1. Purpose and scope

This frontend-only change normalizes the Consumer Search Part family dropdown options and labels. It preserves the existing active gear and shaft search paths and defers metal-part dynamic fields to F4_E2.

## 2. Original duplicate/dropdown problem

The previous Consumer Search Part family options came from raw strings:

```javascript
['gear', 'shaft', 'metal_part', 'general_precision', 'gears', 'shafts']
```

Because the dropdown rendered the strings directly, users saw duplicate/redundant selectable values such as `gear/gears` and `shaft/shafts`.

## 3. Part family options after normalization

The Consumer Search part family options are now:

```javascript
[
  { label: 'Gear', value: 'gear' },
  { label: 'Shaft', value: 'shaft' },
  { label: 'Metal part', value: 'metal_part' }
]
```

`general_precision`, `gears`, and `shafts` are no longer selectable in the Consumer Search Part family dropdown.

## 4. Label/value mapping

The dropdown displays readable labels:

- `Gear`
- `Shaft`
- `Metal part`

The selected values remain backend-facing controlled values:

- `gear`
- `shaft`
- `metal_part`

The dropdown uses explicit `optionLabel="label"` and `optionValue="value"`.

## 5. Part type behaviour after normalization

Gear selection shows gear part types:

- `spur_gear`
- `helical_gear`
- `bevel_gear`
- `worm_gear`

Shaft selection shows shaft part types:

- `splined_shaft`
- `plain_shaft`
- `hollow_shaft`

Metal part does not show gear part types. The part type dropdown is disabled with a temporary placeholder.

## 6. Metal-part temporary behaviour

Metal part is visible as a Part family option, but it is not active for search in F4_E1.

When selected:

- The form sets `service_category` to `precision_manufacturing`.
- The form clears `partType`.
- The part type dropdown is disabled.
- Gear technical fields are not shown.
- A warning explains that metal-part technical fields will be added in the next step.
- The Search button is disabled.

## 7. Payload value behaviour

Gear and shaft payload values remain singular normalized values:

- `part_family: "gear"`
- `part_family: "shaft"`

Plural payload values are not sent:

- `gears`
- `shafts`

For the temporary metal-part state, the payload preview no longer combines `part_family: "metal_part"` with gear defaults such as `part_type: "spur_gear"` and gear technical specifications. Active metal-part submission remains disabled until F4_E2.

## 8. Files modified

- `subsystem/frontend/src/components/mdc/mockData.js`
- `subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`

## 9. Commands run

- `Get-Content` to inspect requested files.
- `rg` to verify part-family and duplicate-value references.
- `npm run lint` from `subsystem/frontend`.

## 10. Manual verification notes

Manual browser verification was not run in this session. Recommended checks:

1. Open `/demo/consumer-search`.
2. Confirm the Part family dropdown shows `Gear`, `Shaft`, and `Metal part`.
3. Confirm `gear/gears` and `shaft/shafts` duplicate raw options are gone.
4. Confirm Gear shows gear part types and gear technical fields.
5. Confirm Shaft shows shaft part types and shaft technical fields.
6. Confirm Metal part shows no gear part types, no gear fields, and a clear temporary warning.
7. Confirm Search is disabled for Metal part.
8. Confirm payload preview for Gear/Shaft uses `gear` and `shaft`.

## 11. Remaining work for F4_E2

F4_E2 should add metal-part-specific part type filtering, dynamic fields, and backend-compatible metal-part payload construction. It should confirm the accepted backend requirement keys before enabling metal-part submission.
