# Codex Prompt — Frontend Final Alignment and Master Manual Review

## Objective

Perform the final independent correction pass for the MaaSAI MaaS Dynamic Catalogue (MDC) demo frontend after the comprehensive frontend manual was generated.

This is a **targeted final-alignment milestone**, not a redesign. The goal is to correct the small but important implementation/documentation inconsistencies found during ChatGPT's independent review, re-run the frontend gates, and then finalize the authoritative frontend master manual.

The frontend remains an **illustrative MDC demonstration frontend**. It is **not** the Cloud MaaS Marketplace (CMM), and this task must not add real Marketplace integration.

## Repository and branch

Repository root:

`C:\Users\Elahi\Desktop\mdc_v1`

Work only on:

`demo-frontend-integration`

Expected already-accepted ancestry includes:

- sanitized import: `e411e7300cfbe2f9f3f9fe245027f2c0c341cd38`
- API/config cleanup: `b207022363163a026a1d77e6485fd151e81aa750`
- generated master manual: `0aac88a38d4fd88890af92240908edf8d008bd5d`

The current branch may be one documentation-prompt commit ahead of the master-manual commit. That is expected.

Before editing:

1. Confirm branch is `demo-frontend-integration`.
2. Confirm the worktree is clean.
3. `git pull --ff-only origin demo-frontend-integration`.
4. Confirm there is no GitLab remote in this repository.
5. Confirm the three accepted commits above remain in ancestry.
6. Stop on conflicts, unrelated tracked changes, unexpected remotes, or failed safety gates.

## Hard boundaries

Do **not**:

- modify the original `C:\Users\Elahi\Desktop\template-frontend` repository;
- add or use a GitLab remote;
- push to GitLab;
- merge to `main`;
- modify backend application code;
- modify Vercel/Neon/Fuseki configuration;
- run trusted provider lifecycle writes;
- run demo state mutation (`simulate-update`) merely for testing;
- expose or print secrets, tokens, database URLs, private keys, or credentials;
- add browser lifecycle bearer tokens, `X-MDC-Actor-Id`, `If-Match`, or service-token logic;
- introduce `/api/v1/...`;
- add new dependencies unless absolutely necessary (none are expected);
- perform broad formatting or unrelated template cleanup.

Allowed application changes are narrowly limited to the frontend correctness items below. Documentation changes are limited to the frontend README, a final review report, and the frontend master manual.

## Source-of-truth order

Use this order when facts conflict:

1. current frontend code on `demo-frontend-integration`;
2. current backend code on repository `main` / shared ancestry;
3. accepted backend master manual and Phase 3 reports;
4. accepted frontend provenance/API-cleanup reports;
5. historical frontend reports only for evolution/history.

Do not let historical demo assumptions override current code or current MDC contract.

---

# A. Controlled vocabulary and fallback correction

ChatGPT's independent review found that the active frontend still shares some stale static values in `src/components/mdc/mockData.js`.

Current backend truth is defined by:

- `backend/apps/ontology/service_discovery_registry.py`
- `backend/apps/ontology/vocabularies.py`
- `backend/apps/api/public_contract.py`
- `backend/apps/api/service_discovery_search_serializers.py`

Inspect those files directly and align **active current-v1 browser choices** with them.

## A1. Consumer fallback must remain contract-valid

The consumer normally loads `GET /api/catalog/filters`, but if that call fails it uses static demo fallback values.

That fallback must not emit values that the current canonical search serializer rejects.

In particular:

- Material grades such as `18CrNiMo7-6`, `16MnCr5`, and `20MnCr5` are **not** canonical consumer `materials` values.
- They must not appear in the consumer fallback Material selector.
- They must not be emitted as `requirements.generic_requirements.materials`.
- `material_grades` must still not be introduced as a consumer search criterion.

Align the fallback materials, processes, certifications, service categories, part families, and part types to the current backend-controlled values. Do not invent values. Derive them from current backend source.

Keep the fallback visibly labelled as demo fallback; it is not authoritative.

## A2. Provider update static choices must use current controlled values

The provider update demo intentionally uses controlled choices where possible. Ensure its active service-category, family, part-type, material, process, and certification options do not present stale invalid controlled values.

Known stale examples that must not remain as active controlled values include:

- `precision_manufacturing`
- `gear_manufacturing` when used as a `service_category`
- `shaft_manufacturing` when used as a `service_category`
- `turn_mill_services`
- `general_precision` as a current v1 controlled part family

Do not remove the concepts of gear/shaft/metal-part *templates* merely because their template labels contain “manufacturing”; distinguish UI template identifiers from controlled MDC `service_category` values.

Ensure the current complete v1 part-type choices are available from backend truth (including any currently omitted gear/shaft types).

Keep material grades separate as provider capability/evidence information where the demo uses them; do not mix grades into the material-family selector.

Inspect unused/stale `mockData.js` exports. If an export has no current caller and only preserves obsolete controlled values, either remove it safely or label/structure it so it cannot be mistaken for current canonical data. Do not change historical reports.

---

# B. Provider update mapping semantics

The flexible registration flow is intentionally permissive staging. The controlled update flow must not silently invent ontology values.

Current issues to correct:

1. The metal-part template currently uses the stale service category `precision_manufacturing`; current backend truth is different.
2. The `general_precision_manufacturing` update template currently implies unsupported current-v1 controlled values (`precision_manufacturing` / `general_precision`).
3. Saved flexible registrations lacking controlled `service_category` / `part_family` can currently be assigned stale fallback values when mapped into the update table.
4. Service category and capability template can currently drift into an invalid family/category combination.

Implement the **smallest safe correction** consistent with the existing demo design:

- Gear, shaft, and metal-part controlled update templates must map to the current valid service category + part family.
- Do not present `general_precision_manufacturing` as a valid current-v1 controlled update template unless current backend source actually supports that category/family (it presently does not). Flexible/general facts belong in registration/custom staging until governed mapping exists.
- When a saved flexible registration lacks a valid controlled mapping, do **not** silently map it to an invented category/family.
- Represent that row as requiring controlled mapping, and require the user to choose a valid controlled template before preview/save of an update.
- A valid template selection should set the correct coupled `serviceCategory`, `partFamily`, and sensible supported-part-type defaults.
- Do not allow an editable service-category control to create a category/family mismatch. Prefer deriving/read-only display from the selected controlled template, or otherwise enforce the relationship in the browser before action.
- Show a concise visible message when a saved flexible provider requires mapping.
- Disable or block update Preview/Save until a valid controlled mapping is present.
- Preserve the existing static Tasowheel gear and shaft update examples.
- Preserve flexible registration custom fields and demo-only state behavior.

Do not turn this into automatic semantic mapping. The user must make the mapping choice explicitly.

Inspect `providerPayloadBuilder.js` and ensure obvious current controlled field names do not use an already-known stale alias where the demo backend/current vocabulary has a clear existing field. For example, check the gear-quality key against current demo/backend truth. Make only low-risk corrections supported by source; do not redesign the provider publication schema.

---

# C. Search result wording and status semantics

The canonical public discovery response intentionally removes selection checks such as `part_type` from the capability arrays. `part_type` is available at response level, and result `match.status` carries the result state.

Correct presentation so the frontend never overclaims confirmed support:

1. A result header must not unconditionally say `<Part Type> supported`.
   - Prefer wording such as `Requested part type: <Part Type>`.
2. The list heading must not imply every returned result is already fully “suitable”.
   - Use neutral evidence-safe wording such as `Provider candidates found` or equivalent.
3. Derive the part-type support label safely from current result semantics:
   - `unknown_match` => not confirmed / evidence incomplete;
   - `full_match` or `partial_match` => part-type support is confirmed under current matcher semantics;
   - preserve compatibility for historical/demo result shapes when they carry an explicit part-type attribute.
4. Do not label an unmatched material/process/certification row simply `Supported` or `Available`.
   - If `provided` evidence exists, display it.
   - Otherwise use a status-appropriate fallback.
5. Keep unmatched/unknown reasons visible.
6. Keep `match.score` out of the primary provider-quality presentation. It may remain in advanced/debug JSON.
7. Keep demo-overlay entries visibly labelled as demo-generated, non-canonical results.

Do not alter backend matching semantics.

---

# D. Demo admin/status truthfulness

Current backend source shows important demo-only behavior:

- `/api/demo/service-discovery/backend-status` returns **hard-coded demo-reported metadata/labels**. It is not a live verification that remote Fuseki is currently active.
- `/api/demo/service-discovery/fuseki-smoke-test` currently returns HTTP 200 with `status: "not_implemented"` and `mutates_state: false`.
- `/api/demo/service-discovery/regenerate-rdf` and `/reload-fuseki` currently return HTTP 501 with `status: "not_implemented"` and `mutates_state: false`.

Correct frontend presentation accordingly:

1. Do not describe the demo backend-status values as verified live/online Fuseki runtime state.
   - Wording should say they are demo-reported/illustrative backend direction or configured demo labels.
2. Do not present the HTTP-200 `fuseki-smoke-test` `not_implemented` response as “completed successfully”.
   - Detect the returned status and show a warning/info message that the smoke test is reserved/not implemented.
3. Technical-action warnings must not say the current regenerate/reload handlers can mutate runtime state when current source explicitly reports `mutates_state: false` and returns 501.
   - Explain that the interfaces are reserved and may become mutating only in a future controlled implementation.
4. Retain confirmation prompts if desired for future-safe behavior, but do not claim a current mutation occurred.
5. Do not modify backend demo endpoints in this task.

Scan any other currently rendered frontend text that claims demo status is live when source only provides static labels, and correct only those misleading claims.

---

# E. README correction

The current frontend README says the committed npm lockfile is v3, but `package-lock.json` is currently lockfile version 2.

Correct the README to match the actual lockfile.

Keep the README concise and consistent with the finalized master manual.

---

# F. Master manual final-review corrections

File:

`mdc-catalog/docs/Demo_Frontend/MDC_Demo_Frontend_Comprehensive_Implementation_Report_and_User_Manual.md`

Preserve its strong 35-section structure and depth. Do not rewrite it from scratch.

After application corrections and their commit exist, update the manual so it describes the corrected code baseline precisely.

At minimum verify/correct all of the following:

## F1. Baseline/status

- Change the frontend baseline SHA to the new application-correction commit created in this task.
- Final document status should state that it is the accepted/final frontend implementation baseline **only after all gates below pass**.
- Keep public contract `1.0` and the demo/CMM boundary.

## F2. Whitespace-import chronology

Correct the chronology:

- the initial sanitized import was allowed by a one-time scoped exception for the nine inherited whitespace warnings **without editing those bytes**;
- the later API/config cleanup intentionally normalized those nine files;
- `git diff --check` then passed normally.

Do not say the cleanup “used the exception to normalize” the files.

## F3. `mockData.js` role

Do not say `mockData.js` is only the consumer filter fallback. It also contains provider/demo template/static presentation data. Explain which parts are current controlled fallback/choices and which are illustrative demo data.

## F4. Provider controlled mapping

Update Sections 17–18 and related appendices to reflect the corrected current-v1 provider update behavior:

- valid controlled gear/shaft/metal-part templates;
- explicit mapping required for flexible registrations that lack controlled category/family values;
- no automatic promotion of arbitrary free text;
- no unsupported `general_precision` current-v1 controlled category/family claim.

## F5. Search-result semantics

Update Section 16 and any manual checklist wording to reflect neutral provider-candidate wording and the distinction between confirmed part-type support and `unknown_match`.

Do not imply that every returned candidate is a confirmed suitable provider.

## F6. Demo backend status and smoke-test semantics

Explicitly state:

- demo backend-status is static/demo-reported metadata, not direct runtime/Fuseki verification;
- Fuseki smoke-test endpoint is currently reserved/not implemented even though it returns HTTP 200;
- regenerate/reload are currently HTTP 501 and `mutates_state: false`.

Ensure Sections 12, 19, 24, 33, and Appendix A are mutually consistent.

## F7. Exact public error examples

Where an example is presented as the current backend response, use wording actually supported by current backend source.

For an invalid search request, current code uses:

- code: `invalid_service_discovery_request`
- message: `Invalid service-discovery search request.`

For unsupported contract version, derive the exact message behavior from `validate_contract_version()` rather than inventing a generic message. If an exact value-specific message would distract, label the JSON explicitly as illustrative rather than exact.

## F8. Production defaults versus accepted deployed policy

Keep the useful distinction between:

- **code defaults in `config/settings_production.py`**, and
- **the accepted current deployed Vercel Phase-3 policy snapshot**, if the latter is supported by the tracked backend master/Phase-3 evidence.

Do not imply that production-setting defaults necessarily equal the currently configured deployment.

The accepted Phase-3 evidence should reflect, where documented:

- provider validation enabled;
- provider publication enabled;
- lifecycle auth required;
- actor required;
- concurrency required;
- catalogue sync disabled on Vercel;
- demo API disabled.

If tracked authoritative evidence differs, use that evidence and explain the distinction.

## F9. Admin-role table

Re-check Appendix B against current `DemoRoleGuard`, `demoAuth.js`, `AppMenu.js`, and `/demo` dashboard behavior.

In the current design, when an admin user selects the **Admin** demo role, Provider and Consumer pages also accept `admin` in their allowed roles. The table must not incorrectly say those pages are unavailable.

## F10. Trusted lifecycle quick reference

Expand the trusted reference enough to list the exact current server-side routes/methods, while emphasizing the browser does not call them:

- provider validation;
- provider publication/registration;
- provider GET/PATCH;
- provider offerings GET/POST;
- offering GET/PATCH.

Use current `backend/apps/api/urls.py` as truth. Do not introduce a collection `GET /api/providers` route.

## F11. Local demo enablement nuance

Current `demo_api_required` permits demo endpoints when the demo flag is enabled **or** Django `DEBUG` is true. Production settings use `DEBUG=False` and demo disabled by default.

Describe this accurately where local setup/demo enablement is discussed.

## F12. Lockfile

Keep the manual's correct lockfile version 2 and make README/manual consistent.

---

# G. Validation

After code corrections, run from `mdc-catalog/demo-frontend/`:

```text
npm ci
npm run lint
npm run build
```

Requirements:

- `npm ci` must pass using the existing lockfile.
- No package/lockfile version change unless npm itself proves the lockfile was unexpectedly rewritten; if it changes, stop and report rather than committing it.
- Lint must exit 0. Existing accepted warnings may remain only if they are the same known warnings; new warnings require review.
- Build must pass.
- Generated `node_modules`, `.next`, logs, caches, and other generated files must remain untracked.

Also run:

- `git diff --check`
- staged `git diff --cached --check` before each commit
- a secret-risk scan over changed/staged files that prints only paths/categories, never secret values
- route sanity for `/`, `/404`, `/demo`, `/demo/provider`, `/demo/consumer-search`, `/demo/admin-audit`
- source checks showing no `/api/v1` active frontend usage
- source checks showing no browser trusted lifecycle token/header implementation
- source checks showing no material grade is used as a consumer `materials` fallback choice
- source checks showing active controlled provider `service_category` choices are current backend values
- source checks showing no active current-v1 `general_precision` controlled family/category is sent by update flow
- source checks showing admin `not_implemented` action responses are not rendered as success

Perform public **read-only/non-mutating** MDC smoke checks if network access is available:

- `GET /api/health`
- `GET /api/catalog/filters`
- one safe `POST /api/service-discovery/search`

Do not run trusted lifecycle writes or demo `simulate-update` as a test.

For provider controlled choices, compare frontend constants/mappings directly with current backend registry/vocabulary source. You may use non-mutating demo preview validation if a suitable local demo backend is already available, but do not create or persist demo state merely for this milestone.

---

# H. Git/commit sequence

Use **two focused commits** so the finalized manual can point at an exact application baseline.

## Commit 1 — application alignment

Include only the targeted frontend application/README corrections and, if useful, a short final alignment evidence report:

`mdc-catalog/docs/Demo_Frontend/03_frontend_final_alignment_review.md`

Suggested message:

`fix: finalize MDC demo frontend alignment`

Record the resulting full SHA. This SHA becomes the frontend baseline referenced by the master manual.

Run all application gates before this commit.

## Commit 2 — master manual finalization

Update only the master manual (plus the final alignment report only if a SHA field must be completed) with the corrections above.

Suggested message:

`docs: finalize MDC demo frontend master manual`

Run documentation scope, secret, and whitespace gates before commit.

Push only:

`origin/demo-frontend-integration`

A normal fast-forward push is allowed if all gates pass.

Do not merge to `main` and do not touch GitLab.

---

# I. Final report

Return exactly a report headed:

`# FRONTEND FINAL ALIGNMENT AND MASTER MANUAL REVIEW REPORT`

Include:

### 1. Repository gate
- branch
- starting SHA
- accepted ancestry checks
- clean/synchronized status
- remote safety

### 2. Independent corrections implemented
- controlled fallback/provider vocab alignment
- flexible-registration mapping behavior
- result wording/status changes
- admin/status truthfulness changes
- README lockfile correction

### 3. Contract/security evidence
- canonical public endpoints
- `/api/v1` findings
- material-grade consumer criterion findings
- provider controlled values comparison
- trusted lifecycle browser implementation: NO
- secrets introduced: NO
- backend changed: NO
- GitLab writes: NONE

### 4. Validation
- `npm ci`
- npm audit result as reported by npm (do not overclaim beyond the run)
- lint result/warning count
- build result
- route sanity
- public smoke result
- `git diff --check`
- secret-risk scan
- generated/untracked artifacts

### 5. Application baseline commit
- SHA
- message
- files/scope summary

### 6. Master manual finalization
- document path
- baseline SHA recorded in document
- corrections verified (F1–F12)
- documentation-only final commit SHA
- message

### 7. Push/synchronization
- integration branch push result
- local/remote SHA match
- main merged: NO
- GitLab push: NO

### 8. Remaining future work
Only genuinely remaining items; do not re-list fixed issues.

### 9. Final gate

If every requirement passes, finish with exactly:

`FRONTEND FINAL ALIGNMENT AND MASTER MANUAL REVIEW: PASS`

`READY_FOR_CHATGPT_FINAL_FRONTEND_ACCEPTANCE: YES`

If anything fails, stop before unsafe commit/push and report the blocker accurately.
