# Task 09 — Update Existing Provider UI refactoring

**Ready for operator acceptance · 2026-11-25.** Branch `phase4/task09-update-existing-provider` in the permanent checkout at `C:/Users/Elahi/Desktop/mdc_v1`. Implementation `a6b36f5778255d0cd9620032febbf4a25553a9df`. Accepted Task 08 base `1e58ff5fc28f092aec4a83134d631129ec408853`. Reviewed `origin/main` at `0f7e2af59a329aa49da5515097ad16bc46f9fc88`. [Task 09 prompt](https://github.com/samola4real/mdc_v1/blob/0f7e2af59a329aa49da5515097ad16bc46f9fc88/mdc-catalog/docs/prompts_phase4/09_MDC_Update_Existing_Provider_UI_Refactoring_Prompt.md), [Accepted Task 08 report](08_MDC_Provider_Registration_UI_Refactoring_Report.md), [Task 07 audit](07_MDC_Provider_Area_UI_Audit_Report.md)

## Provider Area behavior

- The lookup uses the provider ID. The offering table retains its columns and displays catalogue names for categories, families, part types, materials and processes, plus readable support statuses. Loaded provider and selected offering are shown explicitly. [Provider management view](../../demo-frontend/src/components/mdc/ProviderManagement.js)
- Register, Update and Add render the same Provider information, Offering information and Capability information sections where applicable. They share the Task 08 controls, heading styles and validation helpers. Additional service details stays optional and initially collapsed. The legacy Additional offering information and developer response panels were removed from the Provider Area. Validation messages, publication receipts and synchronization status remain visible. [Shared information sections](../../demo-frontend/src/components/mdc/ProviderRegistrationFields.js), [Registration responses](../../demo-frontend/src/components/mdc/ProviderRegistration.js), [Management feedback](../../demo-frontend/src/components/mdc/ProviderActionResult.js), [Scoped styles](../../demo-frontend/src/styles/demo/Demos.scss)
- The provider and offering identities, family and category are locked after creation. Save provider sits inside Provider information. Save offering follows Capability information. A separate deletion section requires the target name and ID to be confirmed, with a cascade warning for provider deletion. Protected baselines render saved values as text and expose lookup and selection controls. [Provider management view](../../demo-frontend/src/components/mdc/ProviderManagement.js), [Write and confirmation handling](../../demo-frontend/src/components/mdc/useProviderManagement.js)
- Offering support and individual part-type statuses have separate controls. Changing offering status leaves saved type status and evidence in place. The editor asks before removing selected types or materials and before demoting a confirmed type with specifications. Reselection restores that type’s dimensions or material’s grades before save. Add offering opens a fresh draft under the loaded provider and uses the Task 08 creation mapping, with confirmed status for the offering and selected types. [Shared controls](../../demo-frontend/src/components/mdc/ProviderRegistrationFields.js), [Draft and payload model](../../demo-frontend/src/components/mdc/providerManagementDraft.js)

## Payload and revision handling

| Area | Handling |
| --- | --- |
| Provider | Provider name, country, recognized certifications, company description and additional certifications hydrate from the saved provider. PATCH contains changed fields only. A changed extension map retains its other entries, and saved certification records keep their evidence. |
| Offering | The draft hydrates service details, family measurements, optional tolerance and finish, Shaft and Metal part quality or fit text, separate per-type measurements and per-material grades, and offering-level ranges. Gear quality uses its existing canonical representation. Edits to complete maps keep untouched leaves, evidence, delivery modes and opaque entries. |
| Legacy data | Grade editing uses one line per grade in Update so a saved comma stays part of its value. Multiple records for the same material keep their separate grades and evidence. Ambiguous or unsupported saved values are protected from replacement. Recognized numeric specifications outside the editable Task 08 controls can appear as saved values. |
| Independent revisions | Provider and offering drafts are separate. Each save or deletion uses the exact target’s strong ETag through the existing transport. An offering write can advance the parent revision. The editor adopts that revision alongside a provider draft only when the provider’s saved fields match. |
| Draft navigation | Lookup, refresh, mode or row switches, Add and deletion ask before discarding the affected draft. A failed lookup retains the open draft. A browser refresh with unsaved changes triggers the browser’s confirmation. Exact IDs determine read-back and offering selection. |
| Stale revision | A 412 preserves the attempted draft and blocks that target’s write. The operator checks the latest exact record and can explicitly open it for editing. The attempted values remain available for comparison and manual reapplication. |
| Ambiguous response | A timeout or 503 triggers read-only reconciliation of the exact target. A matching value or verified absence is reported as a read-back result. A pending receipt is distinguished from discovery availability. The editor requires review when the result is unresolved. |

[Draft hydration and PATCH composition](../../demo-frontend/src/components/mdc/providerManagementDraft.js), [Exact target and result checks](../../demo-frontend/src/components/mdc/providerManagementFlow.js), [Workspace transitions](../../demo-frontend/src/components/mdc/useProviderManagement.js), [Existing lifecycle endpoints](../../demo-frontend/src/services/mdc/provider.service.js)

## Changed files

| Files | Responsibility |
| --- | --- |
| [ProviderDemoPanel.js](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js), [ProviderManagement.js](../../demo-frontend/src/components/mdc/ProviderManagement.js), [ProviderActionResult.js](../../demo-frontend/src/components/mdc/ProviderActionResult.js) | Mode navigation, offering lookup and table, editable and read-only presentation, revision review and human-readable results |
| [ProviderRegistrationFields.js](../../demo-frontend/src/components/mdc/ProviderRegistrationFields.js), [ProviderRegistration.js](../../demo-frontend/src/components/mdc/ProviderRegistration.js), [providerRegistrationPayload.js](../../demo-frontend/src/components/mdc/providerRegistrationPayload.js), [providerRegistrationFlow.js](../../demo-frontend/src/components/mdc/providerRegistrationFlow.js) | Shared controls and validation, accepted registration response flow and removal of raw JSON panels |
| [providerManagementDraft.js](../../demo-frontend/src/components/mdc/providerManagementDraft.js), [providerManagementFlow.js](../../demo-frontend/src/components/mdc/providerManagementFlow.js), [useProviderManagement.js](../../demo-frontend/src/components/mdc/useProviderManagement.js) | Lossless hydration, scoped PATCH values, exact reads and writes, separate drafts and recovery |
| [catalog.service.js](../../demo-frontend/src/services/mdc/catalog.service.js), [Demos.scss](../../demo-frontend/src/styles/demo/Demos.scss) | Category labels and shared read-only presentation |
| [providerManagement.test.mjs](../../demo-frontend/tests/providerManagement.test.mjs) | Sixteen focused Task 09 tests |

## Verification

| Evidence | Result |
| --- | --- |
| Focused Node tests | 43 passed across Stage 1B transport, Task 08 registration and Task 09 management. Covered no-op hydration, mixed types and grades, retained metadata, unsupported formats, ID and ETag gates, 412, 503, Add and exact deletion read-back. |
| Isolated Edge with mocked services | Rendered human labels, immutable identifiers, saved values and read-only baseline controls. Verified independent saves, cancelled navigation, failed lookup, 412 review with the retained draft, a reconciled 503, reselection, Add and both named deletion confirmations. The Task 08 browser regression covered the three families, heading styles, validation, pending receipt and exact handoff. |
| Existing Django API with in-memory SQLite | Frontend-generated provider and offering PATCH returned 200 and matched exact read-back. A stale PATCH and stale DELETE returned 412. Add returned 201 with the expected confirmed capability maps, and duplicate Add returned 409. Offering deletion preserved the other offering, and provider deletion cascaded in the isolated data. Synchronization was disabled for this run. |
| Protected Preview read-only | Tasowheel, Precipart, their two offering lists and all three offering details returned 200. Record detail responses carried strong ETags. |
| Lint, build and permanent route | Targeted ESLint passed. Next.js 14.0.3 generated 20 routes and the standalone server using the installed lockfile dependencies. Existing layout hook, stylesheet and Browserslist warnings appeared. The permanent route returned HTTP 200 on port 3000. |

Run the focused suites from `mdc-catalog/demo-frontend`.

```powershell
node --experimental-default-type=module --experimental-test-isolation=none --test tests/stage1b.test.mjs tests/providerRegistration.test.mjs tests/providerManagement.test.mjs
```

Signed-in operator acceptance remains pending. The permanent route check reached the signed-out shell. Browser write scenarios used mock services and the contract checks used a local in-memory database. Live Preview verification consisted of baseline reads. [Provider Area](http://localhost:3000/demo/provider)
