# Task 11 — Stage 1B closure and consolidation

**Stage 1B closed · 2026-11-26.** The operator authorized consolidation and deferred remaining minor cosmetic adjustments. GitHub merged the accepted Task 08–10 ancestry into `main` at `30a0b10acb0ca7168d55923d3cdc29e71213a07b`. The permanent checkout at `C:/Users/Elahi/Desktop/mdc_v1` was fast-forwarded to that merge. [Task 11 prompt](https://github.com/samola4real/mdc_v1/blob/f6a1bb332ca45c9b7bfa9f6fb5f005b592975a04/mdc-catalog/docs/prompts_phase4/11_MDC_Stage1B_Closure_and_Consolidation_Prompt.md), [Merged PR #10](https://github.com/samola4real/mdc_v1/pull/10)

## Consolidated baseline

| Task | Verified implementation and remote tip |
| --- | --- |
| 08 · Provider registration | Registration refactor `b74a189` and operator correction `3150464`, with report tip `1e58ff5fc28f092aec4a83134d631129ec408853`. [Task 08 report](08_MDC_Provider_Registration_UI_Refactoring_Report.md) |
| 09 · Update Existing Provider | Provider management refactor `a6b36f5`, ETag correction `38a56e1` and notification, role and row deletion refinements `7656654`, with report tip `e3327a6d32a58c319dc6998fbfaca48eedc195f8`. [Task 09 report](09_MDC_Update_Existing_Provider_UI_Refactoring_Report.md) |
| 10 · Admin Dashboard | Dashboard implementation `9300b6c` and visual correction `43e6cfa`, with report and six screenshots at tip `812ff912191037d37df2eadbd40e209e724796b3`. [Task 10 report](10_MDC_Admin_Dashboard_UI_Refinement_Report.md) |

The fetched GitHub tips contained the implementations, reports and regression files. Task 08 is an ancestor of Task 09, and Task 09 is an ancestor of Task 10. PR #10 merged that chain with `main` at `f6a1bb332ca45c9b7bfa9f6fb5f005b592975a04`. The merged frontend tree matches the published Task 10 tree, and the prompt tree matches pre-merge `main`. The change from that `main` is limited to 33 frontend, test, report and screenshot paths. The unrelated edits, untracked logo, stash list and ignored frontend environment file matched their pre-merge fingerprints.

## Accepted behavior

- Provider registration, offering and capability inputs reuse the accepted Task 08 sections and mappings. Provider and offering edits retain separate drafts and revisions, with explicit conflict review and read-back for ambiguous results.
- **Update Existing Provider** uses exact lookup and the strong lifecycle ETag returned by the uncompressed detail read. **Delete offering** is an eligible row action under **Actions**. Offering and part-type status remain in the details. Action results use top-right Toast with compact receipts and synchronization guidance.
- **Admin Dashboard** provides availability cards, provider lookup, catalogue metrics and **View provider** using the shared read-only details. **Delete provider** belongs in Admin. The local relay requires a verified signed Admin role and disposable scope, and forwards the conditional revision. The Admin UI requires a strong ETag and confirmation that names the provider and warns about its offerings. This location and the row-level offering action supersede earlier manual references to a Provider Area deletion panel.

## Verification on merged main

| Check | Result |
| --- | --- |
| Focused regression suites | All 62 passed. The signed-role fixture matrix denied Provider-only and Consumer-only provider DELETE before Preview forwarding, including a forged client role header. Admin deletion stayed within disposable scope. Provider and Admin could still delete eligible offerings in the fixtures. |
| Targeted lint and production build | Lint passed for all 22 changed JS and test files. Next.js 14.0.3 built 20 pages and the standalone server from a clean archive of the merged frontend using the existing installed dependencies. The build emitted the existing layout hook, stylesheet and Browserslist warnings. |
| Permanent local app | Home, Demo, Provider, Service Discovery and Admin returned HTTP 200 at `127.0.0.1:3000`. The served bundles contained Update Existing Provider, Admin Dashboard and View provider. Anonymous relay health and provider reads each returned HTTP 401 with `keycloak_token_required` and `Cache-Control: no-store`. The existing listener served the checks. The IPv6 loopback request timed out. |
| Server-only access | The approved Preview credential was available through the ignored frontend environment file. Its exact value had zero matches across the checked HTML, API responses, response headers and 40 served script responses. |
| Pinned Preview | Health and filters returned HTTP 200 under contract `1.0`. Health reported `ok` for `maasai-mdc`. Filters contained 3 part families, 6 materials, 15 processes and 6 certifications. Both Preview project synchronization settings were verified disabled. The same CLI-created Preview remains pinned to the accepted disabled runtime profile. The recent Vercel deployment IDs matched before and after the merge. |
| Protected baseline providers | All seven exact GETs returned HTTP 200. Tasowheel listed `tasowheel_precision_gears` and `tasowheel_precision_shafts`. Precipart listed `precipart_precision_gears`. Each offering detail matched its parent and exact ID. Both provider details and all three offering details returned strong ETags. |

Run from `mdc-catalog/demo-frontend`.

```powershell
node --experimental-default-type=module --experimental-test-isolation=none --test tests/stage1b.test.mjs tests/providerRegistration.test.mjs tests/providerManagement.test.mjs tests/adminDashboard.test.mjs
```

The standard local launch uses the existing ignored configuration and IPv4 loopback. Keep the existing Keycloak origin for signed-in work.

```powershell
npm.cmd run dev -- --hostname 127.0.0.1 --port 3000
```

## Manual evidence and outstanding limits

- The operator reported successful registration, an editable offering save after the ETag fix, multiple offerings displayed, and successful signed-in Admin deletion. The operator accepted the current Task 08–10 implementation for closure and deferred unspecified minor cosmetic adjustments. Pending synchronization receipts are expected in this Stage 1B profile.
- Closure read-back found `mdc_stage1b_accept_20261126_a` and its two offerings, `mdc_stage1b_accept_20261126_a_metal` and `mdc_stage1b_accept_20261126_a_shaft`, at their exact Preview endpoints. Provider detail, offering list and both offering details returned HTTP 200. Presence is the verified result for these records. The earlier reported deletion remains separate operator evidence. Every live request for this closure was a GET.
- The live signed-in Provider-only denial and the full manual checklist remain unverified. The role fixture and loopback checks above are automated evidence. The recorded visual comparisons and earlier write simulations are fixture evidence in the implementation reports.

## Stage 2 gate

Stage 1B supplies the accepted code baseline on `main`. Stage 2 requires a durable isolated Fuseki query endpoint and Graph Store dataset paired with the validation PostgreSQL database. Verify the pairing and isolation before enabling semantic synchronization. Keep sparse validation data isolated from the existing production graph.
