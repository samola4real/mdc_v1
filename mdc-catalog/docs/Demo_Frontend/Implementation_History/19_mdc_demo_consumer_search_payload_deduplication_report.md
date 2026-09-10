# F4_E3 Consumer Search Payload Deduplication Report

## 1. Purpose and scope

This frontend-only fix removes duplicated requirement fields from the Consumer Search payload. The change is limited to `buildSearchPayload(form)` and its local helper functions in `ConsumerSearchMockup.js`.

No backend code, provider demo code, role/login code, admin/audit code, API service modules, packages, `.env`, runtime config, route config, or Keycloak files were modified.

## 2. Original backend validation error

The backend rejected the Metal part search request with:

```json
{
  "status": {
    "search_executed": false,
    "search_engine": "not_executed",
    "message": "Invalid service-discovery search request."
  },
  "errors": {
    "non_field_errors": [
      "Requirement fields are duplicated across groups: ['processes']"
    ]
  }
}
```

## 3. Root cause

For Metal part searches, `buildSearchPayload(form)` placed `material`, `processes`, and `certification` in `requirements.part_family_specifications`.

The same selected values were also emitted again in `requirements.generic_requirements` as `materials`, `processes`, and `certifications`. The duplicate `processes` key caused backend validation to reject the request.

`custom_metal_part` also repeated `material` inside `part_type_specifications`, so that duplicate was removed from the type-specific payload.

## 4. Payload construction change

Added a local `buildGenericRequirements(form, partFamilySpecifications)` helper.

The helper emits generic requirements only when the equivalent value is not already present in `part_family_specifications`:

- Skip `materials` when `part_family_specifications.material` exists.
- Skip `processes` when `part_family_specifications.processes` exists.
- Skip `certifications` when `part_family_specifications.certification` exists.

For Metal part, this keeps material/process/certification values in `part_family_specifications` and leaves `generic_requirements` as an empty object.

For Gear and Shaft, the existing material/process/certification filters remain in `generic_requirements` because those values are not present in their part-family specifications.

## 5. Metal-part payload after fix

For the default Metal part Block search, the expected requirements shape is:

```json
{
  "requirements": {
    "part_family_specifications": {
      "material": "alloyed_carburizing_steel",
      "processes": ["hobbing", "turn_mill"],
      "certification": "ISO9001_2015"
    },
    "part_type_specifications": {
      "length_mm": { "max": 150 },
      "width_mm": { "max": 80 },
      "height_mm": { "max": 20 },
      "weight_kg": { "max": 2.5 },
      "tolerance_mm": { "max": 0.02 },
      "surface_finish": "Customer specified"
    },
    "generic_requirements": {}
  }
}
```

`generic_requirements` is intentionally preserved as an object, but no longer repeats `materials`, `processes`, or `certifications`.

## 6. Gear/Shaft regression check

Gear and Shaft payload branches still use the same technical specifications as before.

For Gear and Shaft, material/process/certification values are still emitted in `generic_requirements` because they are not duplicated in `part_family_specifications`.

The field rendering, dropdown options, result rendering, and search service call were not changed.

## 7. Files modified

- `subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `docs/19_mdc_demo_consumer_search_payload_deduplication_report.md`

## 8. Commands run

- `Get-Content -Path C:\Users\Elahi\.codex\attachments\fc826e92-bd55-4d3f-81ca-834e1e0ca240\pasted-text.txt`
- `rg -n "buildSearchPayload|generic_requirements|part_family_specifications|part_type_specifications|buildMetalPartSpecifications" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/SearchPayloadPreview.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/SearchErrorMessage.js`
- `Get-Content -Path docs/18_mdc_demo_consumer_search_metal_part_type_specific_fields_report.md`
- `Get-Content -Path subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js -TotalCount 270`
- `git diff -- subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js docs/19_mdc_demo_consumer_search_payload_deduplication_report.md`
- `git status --short subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js docs/19_mdc_demo_consumer_search_payload_deduplication_report.md`
- `npm run lint` from `subsystem/frontend`

## 9. Manual verification notes

Recommended browser verification while the user runs `npm run dev`:

1. Open `http://localhost:3000/demo/consumer-search`.
2. Select `Part family = Metal part`.
3. Select `Part type = Block`.
4. Open the request payload preview.
5. Confirm `processes` appears only in `part_family_specifications`.
6. Confirm `material`/`materials` and `certification`/`certifications` are not repeated across requirement groups.
7. Submit the search and confirm the previous duplicate-processes error disappears.
8. Recheck Gear and Shaft payload previews and submit searches if the backend is available.

## 10. Remaining backend compatibility risks

This fix addresses duplicated requirement fields only. The backend may still reject Metal part payloads for a different validation reason, such as unsupported `service_category`, `part_type`, or type-specific requirement keys. Any new backend validation error should remain visible through the existing `SearchErrorMessage` details panel.
