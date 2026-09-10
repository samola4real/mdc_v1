# F4_E4E Consumer Search Surface Finish Payload Fix Report

## 1. Purpose and scope

This frontend-only fix corrects the Metal part `requirements.generic_requirements.surface_finish_ra_um` payload shape in Consumer Search.

No backend code, provider demo code, role/login code, admin/audit code, API service modules, packages, `.env`, runtime config, route config, or Keycloak files were modified.

## 2. Backend probe error addressed

The F4_E4D backend probe found that all current frontend-shaped Metal part payloads failed with:

```text
requirements.generic_requirements.surface_finish_ra_um must be an object.
```

The same payloads passed backend validation when only `surface_finish_ra_um` was omitted.

## 3. Root cause

Consumer Search sent the free-text Surface finish field directly as:

```json
"surface_finish_ra_um": "Customer specified"
```

The backend expects `surface_finish_ra_um` to be an object when present, not a string.

## 4. Payload change

Added a local `positiveMaxNumber(value)` helper in `ConsumerSearchMockup.js`.

Metal part generic requirements now build `surface_finish_ra_um` as:

```json
"surface_finish_ra_um": {
  "max": 1.6
}
```

only when the visible field contains a positive numeric value.

## 5. Numeric-object rule for surface_finish_ra_um

The rule is:

- Positive numeric value, such as `1.6`: send `{ "max": 1.6 }`.
- Free text, such as `Customer specified`, `N/A`, or `Ra depends on drawing`: omit `surface_finish_ra_um`.
- Missing, empty, zero, negative, or invalid values: omit `surface_finish_ra_um`.

## 6. Gear/Shaft/Metal part consistency

The current Consumer Search form emits `surface_finish_ra_um` only for Metal part generic requirements. Gear and Shaft do not emit this field.

The existing F4_E4 alignment was preserved:

- `service_category` remains derived from `part_family`.
- Metal part types remain `block`, `plate`, `bracket`, `bushing`, `roller`, and `collar`.
- Materials, processes, and certifications remain in `generic_requirements`.
- Block, Plate, and Bracket still use `bounding_box_mm`.
- Bushing, Roller, and Collar still use backend-accepted family fields.
- `weight_kg` remains a scalar positive number.

## 7. Files modified

- `subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `docs/26_mdc_demo_consumer_search_surface_finish_payload_fix_report.md`

## 8. Commands run

- `Get-Content -Path C:\Users\Elahi\.codex\attachments\488731e0-5534-4518-b097-7b2f64a27593\pasted-text.txt`
- `rg -n "surfaceFinish|surface_finish_ra_um|genericRequirements|buildMetalPartRequirements|buildSearchPayload" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/mockData.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/SearchPayloadPreview.js`
- `Get-Content -Path docs/25_mdc_demo_metal_part_backend_probe_report.md`
- `rg -n "surface_finish_ra_um|positiveMaxNumber|surfaceFinish" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `npm run lint` from `subsystem/frontend`
- PowerShell/.NET `HttpClient` POST retest to `http://localhost:8000/api/service-discovery/search` for `block`, `plate`, `bracket`, `bushing`, `roller`, and `collar`

## 9. Manual verification notes

Recommended browser checks while the user runs `npm run dev`:

1. Open `http://localhost:3000/demo/consumer-search`.
2. Select `Part family = Metal part`.
3. Select `Part type = Block`.
4. Leave Surface finish as `Customer specified` and confirm payload preview omits `surface_finish_ra_um`.
5. Enter `1.6` and confirm payload preview sends `"surface_finish_ra_um": { "max": 1.6 }`.
6. Submit searches for `block`, `plate`, `bracket`, `bushing`, `roller`, and `collar`.
7. Confirm the previous string-shape validation error no longer appears.
8. Recheck Gear and Shaft payload previews.

## 10. Remaining backend/data risks

This fix addresses only the `surface_finish_ra_um` string-shape validation error. The backend may still return zero Metal part results if no matching provider/RDF data exists. The F4_E4D probe also showed the backend using RDFLib fallback because primary Fuseki was unavailable.

Backend retest after the fix returned HTTP 200 for all six supported Metal part types with `search_executed: true` and `result_count: 0`. No `surface_finish_ra_um` validation error remained.
