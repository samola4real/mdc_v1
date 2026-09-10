# F4_E4C Consumer Search Service Category Cleanup Report

## 1. Purpose and scope

This frontend-only cleanup removes the internal `service_category` control from the main Consumer Search UI while preserving backend-safe payload derivation.

No backend code, provider demo code, role/login code, admin/audit code, API service modules, packages, `.env`, runtime config, route config, or Keycloak files were modified.

## 2. Why Service category was removed from main UI

`service_category` is a backend routing and ontology value, not a business field the demo user should edit or interpret.

Showing disabled values such as `precision_gears`, `precision_shafts`, or `precision_metal_parts` in the main form made the UI look more technical and potentially broken. The main form now focuses on part family, part type, technical fields, and material/process/certification filters.

## 3. How service_category is derived internally

`ConsumerSearchMockup.js` keeps a centralized mapping:

```javascript
const serviceCategoryByFamily = {
  gear: "precision_gears",
  shaft: "precision_shafts",
  metal_part: "precision_metal_parts",
};
```

`buildSearchPayload(form)` sends:

```javascript
service_category: getServiceCategoryForFamily(partFamily)
```

So the payload still includes the backend-required `service_category`.

## 4. How stale service_category state is prevented

Consumer Search does not store `serviceCategory` in React form state.

The submitted payload derives `service_category` from the current normalized `partFamily` at payload-build time. Stale values such as `turn_mill_services` or `heat_treatment_services` cannot be submitted through Consumer Search.

## 5. Payload preview behaviour

`SearchPayloadPreview.js` remains unchanged and is still collapsed by default.

The advanced payload preview still shows the derived backend request, including:

```json
"service_category": "precision_metal_parts"
```

## 6. F4_E4 behaviour preserved

The cleanup preserves the backend contract alignment:

- `service_category` remains derived from `part_family`.
- Metal part types remain `block`, `plate`, `bracket`, `bushing`, `roller`, and `collar`.
- Materials, processes, and certifications remain in `generic_requirements`.
- Block, Plate, and Bracket still use `bounding_box_mm`.
- Bushing, Roller, and Collar still use backend-accepted fields.
- Gear and Shaft payload branches remain unchanged.

## 7. Files modified

- `subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `docs/24_mdc_demo_consumer_search_service_category_cleanup_report.md`

## 8. Commands run

- `Get-Content -Path C:\Users\Elahi\.codex\attachments\1ca15064-cd54-4054-bda8-c6870c603a42\pasted-text.txt`
- `rg -n "serviceCategory|service_category|Service category|derivedServiceCategory|getServiceCategory|handlePartFamilyChange" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/SearchPayloadPreview.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/mockData.js`
- `Get-Content -Path docs/22_mdc_demo_consumer_search_backend_contract_alignment_report.md`
- `rg -n "serviceCategory|Service category|derivedServiceCategory|service_category|getServiceCategory" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `git status --short subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js docs/24_mdc_demo_consumer_search_service_category_cleanup_report.md subsystem/frontend/src/components/mdc/mockData.js subsystem/frontend/src/components/mdc/SearchPayloadPreview.js`
- `npm run lint` from `subsystem/frontend`

## 9. Manual verification notes

Recommended browser checks while the user runs `npm run dev`:

1. Open `http://localhost:3000/demo/consumer-search`.
2. Confirm Service category is not visible in the main form.
3. Select Gear and confirm payload preview has `service_category: "precision_gears"` and `part_family: "gear"`.
4. Select Shaft and confirm payload preview has `service_category: "precision_shafts"` and `part_family: "shaft"`.
5. Select Metal part and confirm payload preview has `service_category: "precision_metal_parts"` and `part_family: "metal_part"`.
6. Confirm Gear, Shaft, and Metal part field rendering still works.

## 10. Remaining limitations

The payload preview still exposes backend values by design because it is an advanced/debug view. No browser screenshot verification was run in this session.
