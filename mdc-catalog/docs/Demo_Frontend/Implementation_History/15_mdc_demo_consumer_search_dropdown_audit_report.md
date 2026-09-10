# F4_D Consumer Search Dropdown and Dynamic Field Audit Report

## 1. Purpose and scope

This audit covers the Consumer Search form at `/demo/consumer-search`, with focus on dropdown sources, part family normalization, part type dependency, dynamic technical fields, and submitted search payload values.

No source files were changed for this audit.

## 2. Files inspected

- `subsystem/frontend/src/pages/demo/consumer-search.js`
- `subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `subsystem/frontend/src/components/mdc/mockData.js`
- `subsystem/frontend/src/components/mdc/SearchPayloadPreview.js`
- `subsystem/frontend/src/components/mdc/SearchResultsList.js`
- `subsystem/frontend/src/components/mdc/SearchResultCard.js`
- `subsystem/frontend/src/components/mdc/ProviderResultAccordion.js`
- `subsystem/frontend/src/components/mdc/SearchErrorMessage.js`
- `subsystem/frontend/src/components/mdc/searchResultFormatters.js`
- `subsystem/frontend/src/services/mdc/search.service.js`
- `subsystem/frontend/src/services/mdc/catalog.service.js`
- `docs/05_mdc_demo_frontend_consumer_search_report.md`

## 3. Current dropdown value sources

The Consumer Search form imports option arrays from `src/components/mdc/mockData.js`:

- `partFamilies`
- `partTypes`
- `serviceCategories`
- `materials`
- `processes`
- `certifications`

`ConsumerSearchMockup.js` does not call `getCatalogFilters()` and does not load backend `/api/catalog/filters`. `catalog.service.js` exports `getCatalogFilters()`, but the search form does not use it.

The search request is submitted through `searchServiceDiscovery(payload)` in `src/services/mdc/search.service.js`, which posts to:

```text
POST /api/service-discovery/search
```

## 4. Current Part family options

`mockData.js` currently exports:

```javascript
export const partFamilies = ['gear', 'shaft', 'metal_part', 'general_precision', 'gears', 'shafts'];
```

PrimeReact `Dropdown` receives this raw string array directly:

```javascript
<Dropdown value={form.partFamily} options={partFamilies} ... />
```

Because no `label`/`value` option objects are used, each string is both the displayed option and the submitted UI value.

## 5. Duplicate/redundant value findings

`gear` and `gears` are both actual selectable values. `shaft` and `shafts` are also both actual selectable values.

They are not separate label/value pairs. The dropdown displays both because `mockData.js` includes both singular and plural strings in the same array.

`ConsumerSearchMockup.js` then normalizes only these pairs:

```javascript
if (family === "gear" || family === "gears") return "gear";
if (family === "shaft" || family === "shafts") return "shaft";
```

This makes the UI redundant while hiding some of the inconsistency at payload time.

## 6. Current Part type dependency behaviour

Part type options are selected with a binary gear/shaft branch:

```javascript
const availablePartTypes =
  normalizeFamily(form.partFamily) === "shaft"
    ? partTypes.shafts
    : partTypes.gears;
```

Current `partTypes` in `mockData.js` include:

```javascript
gears: ['spur_gear', 'helical_gear', 'bevel_gear', 'worm_gear']
shafts: ['splined_shaft', 'plain_shaft', 'hollow_shaft']
metalParts: ['block', 'bracket', 'plate', 'bushing', 'roller', 'collar_hub', 'custom_metal_part']
```

However, Consumer Search never selects `partTypes.metalParts`. Any family that is not normalized to `shaft` falls through to `partTypes.gears`.

## 7. Current dynamic field rendering behaviour

Dynamic technical fields are also rendered with a binary shaft-vs-gear branch:

```javascript
normalizeFamily(form.partFamily) === "shaft"
  ? "Shaft technical fields"
  : "Gear technical fields"
```

If normalized family is `shaft`, the page renders shaft fields:

- `length_mm`
- `outer_diameter_mm`
- `spline_module`
- `inner_diameter_mm`
- `wall_thickness_mm`
- `tolerance_mm`

For every other value, it renders gear fields:

- `module`
- `diametral_pitch`
- `outside_diameter_mm`
- `gear_quality`
- `face_width_mm`
- `tolerance_mm`

There is no metal-part-specific dynamic field group in Consumer Search.

## 8. Metal-part behaviour diagnosis

Selecting `metal_part` does not switch to metal-part fields because:

1. `normalizeFamily("metal_part")` returns `"metal_part"` unchanged.
2. `availablePartTypes` only checks whether normalized family is `"shaft"`.
3. Since `"metal_part" !== "shaft"`, the form uses gear part types.
4. The dynamic panel also only checks for `"shaft"` and otherwise renders gear fields.
5. `handlePartFamilyChange()` sets `serviceCategory` to `precision_gears` and `partType` to `spur_gear` for every non-shaft family, including `metal_part` and `general_precision`.

Current result: selecting `metal_part` submits `part_family: "metal_part"` but shows gear-like part types and gear technical fields.

## 9. Current search payload values submitted

`buildSearchPayload(form)` currently submits the backend-facing shape:

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

`part_family` is normalized by `toBackendFamily(form.partFamily)`, which calls `normalizeFamily()`.

Current payload mapping:

- UI `gear` -> payload `part_family: "gear"`
- UI `gears` -> payload `part_family: "gear"`
- UI `shaft` -> payload `part_family: "shaft"`
- UI `shafts` -> payload `part_family: "shaft"`
- UI `metal_part` -> payload `part_family: "metal_part"`
- UI `general_precision` -> payload `part_family: "general_precision"`

For `metal_part`, the payload still includes gear-oriented defaults unless the user changes them:

- `service_category: "precision_gears"`
- `part_type: "spur_gear"`
- gear `part_family_specifications`
- `face_width_mm` under `part_type_specifications`

The request payload preview renders the same `payload` object passed to `searchServiceDiscovery(payload)`, so it accurately shows the submitted values.

Docs from the previous F4_B payload alignment identify the backend-accepted top-level search fields and show `part_family: gear` in the validated default payload. They do not establish plural values as accepted. Based on current frontend normalization and the previous validated example, the safer normalized payload values are singular controlled values:

- `gear`
- `shaft`
- `metal_part`

The audit did not inspect backend source in this task.

## 10. Risks if fixed incorrectly

- Removing options without updating default `form.partFamily`, `form.partType`, and `serviceCategory` could leave invalid/stale selections.
- Adding metal-part part types without updating payload construction would still send gear-oriented specifications.
- Changing display labels without explicit `label`/`value` objects could accidentally change backend payload values.
- Switching to backend catalog filters without a fallback could break the demo when `/api/catalog/filters` is unavailable.
- Changing payload values from current normalized singular values could reintroduce backend validation errors.
- Adding metal-part fields without backend contract confirmation could send unsupported requirement keys.

## 11. Recommended correction plan

1. Replace raw string part-family options with explicit `{ label, value }` objects.
2. Use one canonical payload value per family:
   - `gear`
   - `shaft`
   - `metal_part`
3. Remove plural selectable values from Consumer Search UI, or keep plural text only as display labels.
4. Update part type dependency logic to branch on `gear`, `shaft`, and `metal_part`.
5. Add a dedicated metal-part dynamic field renderer before enabling `metal_part` as a complete user path.
6. Update `handlePartFamilyChange()` so each family sets a matching service category and default part type.
7. Update `buildSearchPayload()` so each family sends family-appropriate `part_family_specifications` and `part_type_specifications`.
8. Keep payload preview collapsed and use it to verify the exact submitted shape.
9. Run focused lint and manual browser checks against `/demo/consumer-search`.
10. Confirm backend support for metal-part requirement keys before sending them to the live search endpoint.

## 12. Proposed next implementation phases

- `F4_E1 - Normalize Consumer Search dropdown options and labels`
  Replace raw string options with explicit labels/values, remove duplicate singular/plural selectable values, and keep payload values normalized.

- `F4_E2 - Add metal-part dynamic field rendering`
  Add metal-part part type filtering and metal-part technical fields without affecting gear/shaft behavior.

- `F4_E3 - Verify search payload compatibility and result behaviour`
  Confirm gear, shaft, and metal-part payloads against the backend search endpoint, then adjust field keys only where backend accepts them.
