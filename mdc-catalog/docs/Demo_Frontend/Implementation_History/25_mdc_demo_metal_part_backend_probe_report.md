# F4_E4D Metal-Part Backend Probe Report

## 1. Purpose and scope

This report captures live backend responses for Consumer Search Metal part requests before applying more frontend fixes.

This was a diagnostic/testing task only. No payload builder, backend code, provider demo, role/login, admin/audit, API service modules, packages, `.env`, runtime config, route config, or Keycloak files were modified.

## 2. Files inspected

- `subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `subsystem/frontend/src/components/mdc/mockData.js`
- `subsystem/frontend/src/components/mdc/SearchPayloadPreview.js`
- `subsystem/frontend/src/services/mdc/search.service.js`
- `docs/22_mdc_demo_consumer_search_backend_contract_alignment_report.md`
- `docs/21_service_discovery_search_contract_backend_audit_report.md`

`docs/21_service_discovery_search_contract_backend_audit_report.md` was not present in the frontend repo, so the contract details from the F4_E4 task/report were used.

## 3. Backend probing method

Endpoint probed:

```text
POST http://localhost:8000/api/service-discovery/search
```

Requests were sent from PowerShell using .NET `System.Net.Http.HttpClient` so HTTP 400 response bodies could be captured.

Two probe sets were sent:

- Current frontend-shaped payloads from `ConsumerSearchMockup.js`.
- Backend-compatible baseline payloads from the F4_E4D task text.

An additional isolation probe removed only `surface_finish_ra_um` from the current frontend-shaped payloads to identify whether later validators would fail.

## 4. Whether backend was reachable

The backend was reachable at `http://localhost:8000`.

All current frontend-shaped Metal part probes returned HTTP 400 validation errors. All backend-compatible baseline probes returned HTTP 200 and executed search with zero results.

## 5. Payloads tested

Current frontend-shaped probes used:

- `service_category: "precision_metal_parts"`
- `part_family: "metal_part"`
- `part_type`: `block`, `plate`, `bracket`, `bushing`, `roller`, `collar`
- `materials: ["alloyed_carburizing_steel"]`
- `processes: ["hobbing", "turn_mill"]`
- `certifications: ["ISO9001_2015"]`
- `weight_kg: 2.5`
- `surface_finish_ra_um: "Customer specified"`

Backend-compatible baseline probes used the explicit payloads from the task text:

- `materials: ["steel"]`
- `processes: ["machining"]`
- no `surface_finish_ra_um`
- no `weight_kg`
- accepted Metal part family/type specification shapes.

## 6. Response matrix by part_type

Current frontend-shaped payloads:

| part_type | HTTP status | validation passed? | search executed? | result_count | errors |
|---|---:|---|---|---:|---|
| block | 400 | no | false | n/a | `requirements.generic_requirements.surface_finish_ra_um must be an object.` |
| plate | 400 | no | false | n/a | `requirements.generic_requirements.surface_finish_ra_um must be an object.` |
| bracket | 400 | no | false | n/a | `requirements.generic_requirements.surface_finish_ra_um must be an object.` |
| bushing | 400 | no | false | n/a | `requirements.generic_requirements.surface_finish_ra_um must be an object.` |
| roller | 400 | no | false | n/a | `requirements.generic_requirements.surface_finish_ra_um must be an object.` |
| collar | 400 | no | false | n/a | `requirements.generic_requirements.surface_finish_ra_um must be an object.` |

Backend-compatible baseline payloads:

| part_type | HTTP status | validation passed? | search executed? | result_count | errors |
|---|---:|---|---|---:|---|
| block | 200 | yes | true | 0 | none |
| plate | 200 | yes | true | 0 | none |
| bracket | 200 | yes | true | 0 | none |
| bushing | 200 | yes | true | 0 | none |
| roller | 200 | yes | true | 0 | none |
| collar | 200 | yes | true | 0 | none |

Current frontend-shaped payloads with only `surface_finish_ra_um` omitted:

| part_type | HTTP status | validation passed? | search executed? | result_count | errors |
|---|---:|---|---|---:|---|
| block | 200 | yes | true | 0 | none |
| plate | 200 | yes | true | 0 | none |
| bracket | 200 | yes | true | 0 | none |
| bushing | 200 | yes | true | 0 | none |
| roller | 200 | yes | true | 0 | none |
| collar | 200 | yes | true | 0 | none |

## 7. Validation errors collected

Unique validation error from current frontend-shaped payloads:

```text
requirements.generic_requirements.surface_finish_ra_um must be an object.
```

The earlier `weight_kg must be a positive number` error did not reproduce in this probe. Current frontend-shaped payloads send `weight_kg` as scalar `2.5`.

## 8. Which part types validated successfully

With backend-compatible baseline payloads, all six supported Metal part types validated successfully:

- `block`
- `plate`
- `bracket`
- `bushing`
- `roller`
- `collar`

With current frontend-shaped payloads after omitting only `surface_finish_ra_um`, all six also validated successfully.

## 9. Which part types executed but returned zero results

All six supported Metal part types executed and returned zero results when validation passed:

- `block`
- `plate`
- `bracket`
- `bushing`
- `roller`
- `collar`

The backend response included:

```text
Primary Fuseki backend unavailable; used local RDFLib fallback.
```

## 10. Which part types failed validation

All six current frontend-shaped payloads failed validation because of `surface_finish_ra_um`:

- `block`
- `plate`
- `bracket`
- `bushing`
- `roller`
- `collar`

## 11. Current frontend payload mismatches

Confirmed mismatch:

- `surface_finish_ra_um` is currently sent as the string `"Customer specified"`.
- Backend validation requires `requirements.generic_requirements.surface_finish_ra_um` to be an object.

Not reproduced as current issues:

- `weight_kg` is currently scalar and positive in the probed payloads.
- `service_category` is `precision_metal_parts`.
- `part_family` is `metal_part`.
- Metal part type values are accepted.
- Material/process/certification values in the current frontend-shaped payload did not fail validation after `surface_finish_ra_um` was removed.

## 12. Recommended frontend fix list

Recommended next frontend fix:

1. Stop sending free-text `"Customer specified"` as `surface_finish_ra_um`.
2. Either omit `surface_finish_ra_um` when no numeric Ra value is available, or add a numeric Ra input and send the backend-accepted object shape.
3. Preserve the current scalar positive `weight_kg` behavior.
4. Preserve service category derivation and accepted Metal part type values from F4_E4.

Do not change the backend for the validation issue found here.

## 13. Whether backend changes are needed

No backend change is needed for the validation error collected in this probe. The backend accepted all six Metal part types when the payload matched the contract.

Data/RDF catalogue changes may be needed later if the demo requires provider results for Metal part searches, because all successful probes returned zero results.

## 14. Remaining risks before demo

- The frontend still sends an invalid `surface_finish_ra_um` string until a follow-up fix is implemented.
- Successful Metal part searches currently return zero results in the probed backend state.
- Fuseki was unavailable during probing and the backend used RDFLib fallback, so demo behavior may differ if Fuseki data is later refreshed.

## Commands run

- `Get-Content -Path C:\Users\Elahi\.codex\attachments\1e02f79b-22d2-4859-9264-c2ceb1bbe262\pasted-text.txt`
- `Get-Content -Path subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/mockData.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/SearchPayloadPreview.js`
- `Get-Content -Path subsystem/frontend/src/services/mdc/search.service.js`
- `Get-Content -Path docs/22_mdc_demo_consumer_search_backend_contract_alignment_report.md`
- `Get-Content -Path docs/21_service_discovery_search_contract_backend_audit_report.md`
- PowerShell/.NET `HttpClient` POST probes to `http://localhost:8000/api/service-discovery/search`
