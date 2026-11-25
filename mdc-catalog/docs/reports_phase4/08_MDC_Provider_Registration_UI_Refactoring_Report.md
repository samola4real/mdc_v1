# Task 08 — Provider registration UI refactoring

**Ready for operator review · 2026-11-25.** The three-section registration form and its response flow are on `phase4/task08-provider-registration`. Reviewed `origin/main` at `09cd075853ae8938352b0210d2040e18292bcf8f`. Implementation commit `b74a1899ee9bf8aaf1d38df42a3c0e92c994a382`. The permanent development checkout is `C:/Users/Elahi/Desktop/mdc_v1`. [Locked Task 08 specification](../prompts_phase4/08_MDC_Provider_Registration_UI_Refactoring_Prompt.md)

## Compatibility gate

Before implementation, the unchanged contract accepted the proposed extension structures and a confirmed Block, Plate, and Roller offering with independent measurements. The protected Preview validation endpoint returned HTTP 200 with `valid: true` for the valid request and HTTP 400 with `valid: false` for the reversed batch-size range. Its error details named `offerings[0].generic_capabilities.batch_size.min`. An isolated Django test client with an in-memory SQLite database returned HTTP 201 with an `accepted` creation receipt, `sync_pending` publication status, and `pending` sync status. Its repeated create returned HTTP 409 `provider_already_exists`. The provider and offering GETs preserved the extension maps, independent grades, and typed dimensions exactly. [Publication serializer](../../backend/apps/api/service_discovery_publication_serializers.py#L286-L347), [Validation response](../../backend/apps/api/views/post_views.py#L388-L448), [Registration persistence](../../backend/apps/providers/provider_lifecycle_write_service.py#L367-L415)

Validation returns a normalized discovery projection. The frontend associates the explicit validation result with the serialized original payload and sends that original payload for registration. This keeps the extension maps in the write request. The existing contract defines positive finite measurements and ordered bounds. The local requiredness follows the existing name, identity, country, and taxonomy requirements. The country and offering name limits account for the persisted field sizes. [Normalization](../../backend/apps/providers/service_discovery_publication.py#L108), [Numeric validation](../../backend/apps/api/service_discovery_publication_serializers.py#L215-L263), [Persisted fields](../../backend/apps/providers/models.py), [Registration payload model](../../demo-frontend/src/components/mdc/providerRegistrationPayload.js)

| Existing extension map and key | Representation verified |
| --- | --- |
| `custom_provider_fields.description` | String |
| `custom_provider_fields.additional_certifications` | Array of free-text strings |
| `custom_offering_fields.production_mode` | Free-text string describing repetition or volume |
| `custom_offering_fields.industries_served` | Array of free-text strings. The editor accepts one industry per line. |
| `custom_offering_fields.other_service_information` and custom service keys | String for each entry |
| `custom_capability_fields.additional_materials` | Array of objects with `name` and `available_grades` as a string array |
| `custom_capability_fields.additional_processes` | Array of free-text strings |
| `custom_capability_fields.notes`, `.tolerance`, `.surface_finish` and legacy text `.quality_class` | Strings in their existing roles |
| Other technical keys in `custom_capability_fields` | Object with string `value` and optional `unit` and `notes` |

Controlled certifications, materials and their grades, processes, family bounds, and part-type measurements use the original canonical fields and declared evidence. Custom entries describe additional provider-supplied information, with storage and read-back verified. [Payload model](../../demo-frontend/src/components/mdc/providerRegistrationPayload.js)

## Registration behavior

- Provider information, Offering information, and Capability information share one form. Additional service details, Additional technical capabilities, and the advanced JSON preview start collapsed. Required fields and both disposable ID rules have inline feedback. Empty optional rows are ignored. Meaningful incomplete rows, duplicate names, reserved keys, and invalid numeric bounds require correction. [Registration controls](../../demo-frontend/src/components/mdc/ProviderRegistrationFields.js), [Validation and payload model](../../demo-frontend/src/components/mdc/providerRegistrationPayload.js)
- The live catalogue supplies the options and category mapping. Gear uses its shared dimensions and quality fields. Shaft uses its family bounds and the eligible selected spline measurement. Each selected metal box type gets its own length, width and height, and each selected round type gets its own outer diameter. Deselection excludes only that type from the payload and retains its own draft for reselection. Changing family confirms before discarding family-specific selections and specifications. Shared capabilities stay in the draft. [Family and typed measurement controls](../../demo-frontend/src/components/mdc/ProviderRegistrationFields.js), [Draft transitions and serialization](../../demo-frontend/src/components/mdc/providerRegistrationPayload.js)
- Changing confirmed support warns before omitting entered typed measurements. Ineligible controls display the explanation and disable editing. Each controlled material has a separate grade field, and additional material families have separate names and grades. Grade entries are trimmed and deduplicated while preserving the spelling of retained values. Optional service and material details start empty. [Capability controls](../../demo-frontend/src/components/mdc/ProviderRegistrationFields.js), [Support and grade mapping](../../demo-frontend/src/components/mdc/providerRegistrationPayload.js)
- Clicking the active Register New Provider button preserves the draft. Leaving registration prompts when the draft contains data. The success handoff uses the existing Update screen and attaches only the submitted provider and offering after matching read-back. The Load provider retry for an unresolved accepted receipt also uses the submitted identities. [Panel integration](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js), [Exact read-back](../../demo-frontend/src/components/mdc/providerRegistrationFlow.js)

| Response or transition | User-facing behavior |
| --- | --- |
| Catalogue loading or failure | Shows loading or error status. Retry preserves typed values. |
| `valid: true` | Shows the specified validation success. Register requires the corresponding payload to remain current. |
| Invalid result or backend field error | Shows correction feedback, maps known paths to controls, and keeps structured response details collapsed. |
| Payload edit after successful validation | Shows the stale-validation message. Reverting the edit still requires a new validation. |
| Registration submission | Locks concurrent actions and sends the validated original payload once. A verified receipt must identify the submitted provider, offering, operation, and publication. |
| Accepted with pending synchronization | Shows saved confirmation, identities, receipt, and the specified pending search guidance. Completed receipts show the reported status. |
| Definite rejection, including duplicate ID | Keeps the draft. Duplicate IDs block another attempt until the affected identity changes and the request is validated again. |
| Timeout, ambiguous response, or 503 | Keeps the draft and any receipt. Read-only lookup distinguishes matching IDs, provider-only evidence, a canonical absence, and an unresolved lookup. A retry requires a deliberate action. |
| Accepted receipt with failed read-back | Enters Update with the submitted provider ID, preserves the receipt, and shows Load provider guidance. Recovery requires the exact submitted offering. |

[Registration feedback and actions](../../demo-frontend/src/components/mdc/ProviderRegistration.js), [Response classification and reconciliation](../../demo-frontend/src/components/mdc/providerRegistrationFlow.js)

## Changed files

| File | Responsibility |
| --- | --- |
| [ProviderDemoPanel.js](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js) | Registration routing, draft protection, catalogue retry wiring, and handoff to the existing Update panel |
| [ProviderRegistration.js](../../demo-frontend/src/components/mdc/ProviderRegistration.js) | Form actions, current-validation check, and response rendering |
| [ProviderRegistrationFields.js](../../demo-frontend/src/components/mdc/ProviderRegistrationFields.js) | Three registration sections, conditional fields, optional rows, and inline feedback |
| [providerRegistrationPayload.js](../../demo-frontend/src/components/mdc/providerRegistrationPayload.js) | Isolated draft transitions, canonical payload adaptation, extension mapping, and field checks |
| [providerRegistrationFlow.js](../../demo-frontend/src/components/mdc/providerRegistrationFlow.js) | Request guard, validation decoding, receipt checks, and read-back |
| [providerRegistration.test.mjs](../../demo-frontend/tests/providerRegistration.test.mjs) | Twelve focused regression cases around draft, payload, responses, and legacy interoperability |

## Verification

| Check | Result |
| --- | --- |
| Registration and Stage 1B Node suites | 22 passed. Covered blank form, all three families, Block + Roller and Block + Plate, removal and reselection, candidate and unknown statuses, Steel + Aluminum grade independence, extension shapes, reserved and duplicate names, invalid ranges, stale validation, receipt eligibility, double submission guard, and legacy Update/Add payloads. |
| Isolated Edge with mocked services | Exercised catalogue retry and draft retention, active registration mode, cancelled discard, simultaneous Block and Roller controls, inline backend messages, revalidation, duplicate ID correction, ambiguous 503, single submission, accepted pending receipt, strict read-back recovery, and read-only baseline controls. |
| Generated payloads against the frozen contract | Gear, Shaft, mixed Metal part, and candidate Metal part each returned HTTP 200 `valid: true` from the non-mutating protected Preview validator. An in-memory registration and GET round-trip preserved all extension maps, both controlled grade lists, and the independent dimensions. |
| Existing baseline reads | Protected GETs returned HTTP 200 for Tasowheel, Precipart, both offering lists and all three offering details. The existing disposable scope gate treats both providers as read-only in the UI. |
| Lint and production build | Targeted ESLint passed. The isolated Next.js `14.0.3` production build generated all 20 routes and the standalone server using the installed lockfile dependencies. Existing hook, stylesheet and Browserslist warnings remained. |
| Permanent local route | `/demo/provider` returned HTTP 200 on port 3000 and served the signed-out shell. |

```powershell
Set-Location -LiteralPath 'C:/Users/Elahi/Desktop/mdc_v1/mdc-catalog/demo-frontend'
node --experimental-default-type=module --experimental-test-isolation=none --test tests/stage1b.test.mjs tests/providerRegistration.test.mjs
```

Authenticated operator review remains pending. Browser interaction and write-response tests used isolated fixtures. Live requests consisted of GETs and non-mutating validation. The review branch contains the registration implementation, its tests, and this report. [Provider Area on the permanent local server](http://localhost:3000/demo/provider)

## Deferred findings

The legacy Update and Add forms continue using their existing components and payload builder. The later review can address multi-type dimension editing and grades in those modes, editable-looking baseline fields, draft loss when changing an ordinary update selection, and ordinary update conflict/rebase behavior. The regression suite checks existing field and map preservation, including opaque extension data, through the legacy patch path. [Task 07 audit](07_MDC_Provider_Area_UI_Audit_Report.md), [Legacy payload builder](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js)
