# F4_E4B Consumer Search Weight Payload Fix Report

## 1. Purpose and scope

This frontend-only fix aligns `requirements.generic_requirements.weight_kg` with the backend search contract. The change is limited to Consumer Search payload construction.

No backend code, provider demo code, role/login code, admin/audit code, API service modules, packages, `.env`, runtime config, route config, or Keycloak files were modified.

## 2. Original backend validation error

The backend rejected Metal part search with:

```json
{
  "status": {
    "search_executed": false,
    "search_engine": "not_executed",
    "message": "Invalid service-discovery search request."
  },
  "errors": {
    "non_field_errors": [
      "requirements.generic_requirements.weight_kg must be a positive number."
    ]
  }
}
```

## 3. Root cause

The frontend sent generic `weight_kg` as a range object:

```json
"weight_kg": {
  "max": 2.5
}
```

The backend expects `requirements.generic_requirements.weight_kg` to be a scalar positive number.

## 4. Payload change

Added a local `positiveNumber(value)` helper in `ConsumerSearchMockup.js`.

Metal part generic requirements now emit:

```json
"weight_kg": 2.5
```

instead of:

```json
"weight_kg": {
  "max": 2.5
}
```

Dimension and tolerance fields still use the existing accepted range object shapes where required by the F4_E4 mapping.

## 5. Positive-number guard

`weight_kg` is included only when the form value converts to a finite number greater than zero.

If the value is missing, empty, zero, negative, or invalid, `weight_kg` is omitted from `generic_requirements`.

## 6. Gear/Shaft/Metal part consistency

The current Consumer Search form only emits `weight_kg` for Metal part generic requirements. The fix ensures every Metal part branch emits scalar `weight_kg` consistently.

Gear and Shaft payload branches are unchanged and do not currently emit `weight_kg`.

## 7. Files modified

- `subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `docs/23_mdc_demo_consumer_search_weight_payload_fix_report.md`

## 8. Commands run

- `Get-Content -Path C:\Users\Elahi\.codex\attachments\99ef47bc-2e5a-4da3-ae2e-f8a82af93006\pasted-text.txt`
- `rg -n "weight_kg|buildGenericRequirements|buildSearchPayload|buildMetalPart" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `Get-Content -Path docs/22_mdc_demo_consumer_search_backend_contract_alignment_report.md`
- `Get-Content -Path docs/21_service_discovery_search_contract_backend_audit_report.md`
- `Get-Content -Path subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js -TotalCount 230`
- `rg -n "weight_kg" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `git status --short subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js docs/23_mdc_demo_consumer_search_weight_payload_fix_report.md`
- `npm run lint` from `subsystem/frontend`

## 9. Manual verification notes

Recommended browser checks while the user runs `npm run dev`:

1. Open `http://localhost:3000/demo/consumer-search`.
2. Select `Part family = Metal part`.
3. Select `Part type = Block`.
4. Set `Weight kg = 2.5`.
5. Open request payload preview.
6. Confirm `requirements.generic_requirements.weight_kg` is `2.5`, not `{ "max": 2.5 }`.
7. Submit Metal part search and confirm the previous positive-number validation error disappears.
8. If a new backend validation error appears, keep it visible in the existing backend error details panel.

## 10. Remaining backend compatibility risks

This fix addresses only the `weight_kg` scalar shape. Browser/backend retesting was not run in this session, so any remaining backend validation error is unknown. The referenced backend audit report file was not present locally.
