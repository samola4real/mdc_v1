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

## Operator acceptance correction · 2026-11-26

Section 05, Step 3 stopped on the existing provider `mdc_stage1b_accept_20261126_a` and offering `mdc_stage1b_accept_20261126_a_metal`. The correction is commit `38a56e1a7709a6802b150bf7622437bf94972a65` on `phase4/task09-update-existing-provider`, following the initial report at `78ccad458126c067fec6dbd232cce4ec0e9e6292`. The correction prompt was reviewed at `origin/main` commit `4dd5908f0fd0eaaf673a6a8aa7144c9ec7e5dc86`. [Operator acceptance correction prompt](https://github.com/samola4real/mdc_v1/blob/4dd5908f0fd0eaaf673a6a8aa7144c9ec7e5dc86/mdc-catalog/docs/prompts_phase4/09_MDC_Update_Existing_Provider_UI_Refactoring_Prompt.md#operator-acceptance-correction--disposable-offering-unexpectedly-read-only-2026-11-26)

Preview response compression was weakening the offering ETag. Authorized read-only requests to the pinned Preview produced the following results. The initial signed-in browser check also showed HTTP 200 with a `W/` ETag on the relay offering GET. The operator reported that Provider information appeared read-only in that view as well.

| Request | Status | Response encoding | ETag |
| --- | --- | --- | --- |
| Offering detail with Node fetch defaults or explicit `br` | 200 | Brotli (`br`) | Weak, `W/` followed by the quoted 64-hex revision |
| Same offering with `Accept-Encoding: identity` | 200 | Uncompressed | Strong, the quoted 64-hex revision |
| Provider detail with defaults or `identity` | 200 | Uncompressed | Strong, a separate provider revision |
| Provider offering list with defaults or `identity` | 200 | Brotli with defaults, uncompressed with `identity` | Absent |

The decoded offering bodies matched, and the linked provider and offering IDs matched the registered record and its offering list. Both IDs passed their disposable scope checks. Registration read-back verifies the exact identities before opening the workspace. Explicit Load provider and row selection also use the exact offering detail read. The relay copies the upstream ETag and ends the successful response directly. The Axios client reads that header into `resource.etag`. The weak tag therefore reached `strongEtag` intact and made `offeringEditable` false. The provider gate uses its own detail ETag, and a newly opened workspace starts without write recovery. [Identity scope](../../demo-frontend/src/services/mdc/stage1bScope.js), [Registration read-back](../../demo-frontend/src/components/mdc/providerRegistrationFlow.js), [Management lookup and gates](../../demo-frontend/src/components/mdc/useProviderManagement.js), [Client ETag mapping](../../demo-frontend/src/services/mdc/client.js)

The local Next.js relay now requests `Accept-Encoding: identity` on provider and offering detail GETs and passes the upstream ETag through verbatim. Weak or missing ETags keep the corresponding editor read-only. Lifecycle writes continue to send the exact strong revision as `X-MDC-If-Match`, with the existing role, scope and recovery checks. [Local relay](../../demo-frontend/src/pages/api/mdc/%5B...path%5D.js), [Strong revision gate](../../demo-frontend/src/components/mdc/providerManagementFlow.js)

### Correction verification

| Evidence | Result |
| --- | --- |
| Protected Preview, live read-only | Repeated GETs returned the same saved provider and offering data before and after the relay change. Steel grades and the Roller outer diameter are present in the offering detail. |
| Focused Node regression | The added test failed before the fix on the weak ETag and passed afterward. It covers registration read-back, explicit lookup, exact row read and weak or missing revisions. All 44 tests passed across the three suites above. |
| Isolated Edge with fixture responses | The browser used the real client and relay with local fixtures. Registration handed off the exact selected offering. Reload and reselection made Steel grades and Roller diameter editable with a strong ETag. A weak offering ETag kept that section read-only while Provider name remained editable. Save offering required a valid change and sent the exact ETag. The mock save kept saved capabilities and the independent provider draft. Add worked and the baseline stayed read-only. |
| Lint, build and local route | Targeted lint passed. An isolated production build with the installed lockfile dependencies generated 20 pages and the standalone server, with the existing layout, stylesheet and Browserslist warnings. The running `localhost:3000` development relay compiled the correction and still returned HTTP 401 for an anonymous offering detail request. |

All live verification for this correction used GETs against the existing records. The browser save checks used in-memory fixtures. The corrected signed-in session and the operator’s Step 3 save are the remaining manual acceptance checks.

### Resume Section 05, Step 3

1. In the signed-in Provider Area, keep the existing provider. Preserve any unsaved draft before reloading. Open **Update Existing Provider**, enter `mdc_stage1b_accept_20261126_a`, and click **Load provider**. Confirm the selected offering is `mdc_stage1b_accept_20261126_a_metal`. [Provider Area](http://localhost:3000/demo/provider)
2. Confirm **Offering name**, **Steel grades**, and **Outer diameter max** under **Roller** are editable and show the saved values. **Provider name** has its own editor. **Save offering** starts disabled, and the IDs, part family and service category are fixed.
3. Apply the edits specified in Step 3, then click **Save offering** once it is enabled. Reload the same provider and confirm the saved values. Use **Save provider** separately for any provider edits required by the manual.
4. If the app asks for a current offering revision, pause at Step 3 and record the offering detail GET status and whether the ETag is strong, weak or absent. If a concurrent save triggers **Review current offering**, use **Check latest offering**, review the record, and choose **Edit the latest offering revision** before reapplying any edits.
