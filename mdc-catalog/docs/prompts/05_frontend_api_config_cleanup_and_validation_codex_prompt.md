# Codex Prompt — 05 Frontend API/Config Cleanup and Validation

## Purpose

Perform a **narrow, evidence-driven cleanup and validation** of the imported MaaSAI MDC demonstration frontend on the `demo-frontend-integration` branch.

The imported frontend is an illustrative pilot UI. It is **not the real Cloud MaaS Marketplace (CMM)**. Its purpose is to demonstrate provider and consumer interaction with the MaaS Dynamic Catalogue before full CMM integration.

This milestone must align the demo frontend with the **current MDC public API contract**, remove stale browser-side lifecycle assumptions, make configuration/documentation truthful, eliminate accidental Next.js routes, and produce a clean lint/build validation baseline.

Do **not** turn this into a real CMM integration and do **not** implement trusted provider lifecycle credentials in the browser.

## Fixed paths

Repository:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Frontend:

```text
mdc-catalog/demo-frontend/
```

Frontend documentation:

```text
mdc-catalog/docs/Demo_Frontend/
```

Current working branch:

```text
demo-frontend-integration
```

Accepted sanitized frontend baseline commit:

```text
e411e7300cfbe2f9f3f9fe245027f2c0c341cd38
```

Original MaaSAI GitLab repository remains historical/official release source:

```text
https://gitlab-cigip.alc.upv.es/maasai/tools/template-frontend.git
```

Do not add that GitLab repository as a remote and do not push to it.

## Source-of-truth policy

For current behavior, use this priority:

1. current backend implementation under `mdc-catalog/backend/`;
2. accepted current MDC master manual;
3. current frontend implementation;
4. historical frontend reports only as traceability evidence.

Do not revive historical `/api/v1/...` contracts or obsolete lifecycle routes.

Current canonical public API routes are:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Trusted lifecycle routes exist separately:

```text
POST  /api/provider-publication/validation
POST  /api/provider-publication
GET/PATCH  /api/providers/{provider_id}
GET/POST   /api/providers/{provider_id}/offerings
GET/PATCH  /api/offerings/{offering_id}
```

Those lifecycle routes are **trusted/server-to-server** and currently rely on a replaceable service-token/actor/ETag boundary. A trusted lifecycle service token must never be embedded in browser code, `public/config.js`, `NEXT_PUBLIC_*`, local storage, session storage, source code, or any client-delivered asset.

## Current public response facts to verify from backend

Before editing, inspect at least:

```text
backend/apps/api/urls.py
backend/config/urls.py
backend/apps/api/public_contract.py
backend/apps/api/service_discovery_search_serializers.py
backend/apps/ontology/service_discovery_registry.py
backend/apps/ontology/vocabularies.py
backend/apps/api/lifecycle_security.py
backend/apps/api/views/get_views.py
backend/apps/api/views/post_views.py
```

In particular, confirm that the current public service-discovery response is shaped approximately as:

```json
{
  "contract_version": "1.0",
  "request_id": "...",
  "service_category": "...",
  "part_family": "...",
  "part_type": "...",
  "result_count": 1,
  "results": [
    {
      "provider_id": "...",
      "provider_name": "...",
      "offering_id": "...",
      "offering_name": "...",
      "service_category": "...",
      "part_family": "...",
      "match": {"status": "...", "score": 0.0},
      "matched_capabilities": [],
      "unmatched_capabilities": [],
      "unknown_capabilities": []
    }
  ]
}
```

Do not assume the older/internal `matched_attributes`, `unmatched_attributes`, `unknown_attributes`, or `evidence` structures are the current public contract. The frontend may keep compatibility with those historical/demo shapes, but canonical public rendering must work with the current flattened public result.

Also verify the current catalogue-filter response, including:

- `contract_version`;
- `service_categories`;
- `part_families`;
- `part_types` keyed by part family;
- `materials`;
- `processes`;
- `certifications`.

## Non-negotiable safety rules

Do NOT:

- modify `C:\Users\Elahi\Desktop\template-frontend`;
- touch or push to MaaSAI GitLab;
- add/change Git remotes;
- merge to `main`;
- modify backend application code;
- add `/api/v1` routes;
- implement Marketplace/CMM login integration;
- implement a browser-held trusted lifecycle service token;
- put bearer tokens, passwords, secrets, database URLs, private keys, or confidential credentials in tracked files;
- call trusted lifecycle write APIs during validation;
- call destructive demo admin actions against deployed environments;
- rewrite Git history;
- force-push;
- upgrade package versions or intentionally modify `package-lock.json`;
- introduce a large new test framework or redesign the frontend.

If an unexpected security issue, unrelated change, merge conflict, secret, or major architectural dependency appears, STOP and report it.

## Step 1 — Repository gate

From:

```powershell
cd C:\Users\Elahi\Desktop\mdc_v1
```

Verify:

```powershell
git status --short --branch
git branch --show-current
git rev-parse HEAD
git remote -v
```

Requirements:

- branch = `demo-frontend-integration`;
- working tree clean before edits;
- branch synchronized with `origin/demo-frontend-integration` after an explicit fast-forward-only pull;
- only personal GitHub remotes are present;
- no GitLab remote;
- accepted sanitized baseline is in branch ancestry.

Use:

```powershell
git pull --ff-only origin demo-frontend-integration
```

Do not switch to `main` for this milestone.

## Step 2 — Confirm stale lifecycle service has no callers

Inspect:

```text
mdc-catalog/demo-frontend/src/services/mdc/provider.service.js
mdc-catalog/demo-frontend/src/services/mdc/index.js
```

Search the complete frontend for imports/references to:

- `validateProviderPublication`
- `publishProviderPublication`
- `getProviders`
- `getProvider`
- `provider.service`

The known stale module currently contains obsolete paths such as:

```text
/api/provider-publication/validate
/api/provider-publication/publish
GET /api/providers
```

If there are no active UI/runtime callers, **delete `provider.service.js` and remove its barrel export** rather than updating it into a browser-side trusted lifecycle client.

If active callers do exist, STOP and report the exact callers before changing behavior.

Reason: trusted lifecycle integration belongs behind a future CMM/backend-for-frontend/server-side boundary.

## Step 3 — Fix MDC client error/response handling narrowly

Inspect `src/services/mdc/client.js`.

Update error normalization so current public errors are presented correctly. Prefer the canonical nested envelope:

```text
response.data.error.message
```

while retaining reasonable fallback compatibility with older/simple `response.data.message` and Axios `error.message`.

Do not expose sensitive headers or log secrets.

The current client returns only `response.data`. For the present public/demo frontend this is acceptable for most calls. If you add a response-metadata option, keep it opt-in and secret-safe; **do not add lifecycle bearer/actor/If-Match logic to the browser** merely to expose ETags.

The goal of this milestone is current public/demo API correctness, not production lifecycle implementation.

## Step 4 — Align canonical search result rendering

Inspect at minimum:

```text
src/components/mdc/ConsumerSearchMockup.js
src/components/mdc/SearchResultsList.js
src/components/mdc/ProviderResultAccordion.js
src/components/mdc/searchResultFormatters.js
```

The frontend currently supports older/internal/demo result fields such as:

```text
matched_attributes
unmatched_attributes
unknown_attributes
evidence
```

The current public API returns:

```text
matched_capabilities
unmatched_capabilities
unknown_capabilities
```

Implement a **small normalization layer** so the UI correctly renders the current public response while preserving compatibility with browser-generated demo-overlay results and historical/internal response shapes where useful.

Requirements:

- canonical `provider_id`, `provider_name`, `offering_id`, `offering_name`, `service_category`, `part_family`, and `match` render correctly;
- canonical `matched_capabilities`, `unmatched_capabilities`, and `unknown_capabilities` are visible in the suitability/explanation UI;
- materials/processes/certifications present as capability entries remain visible in appropriate sections or explanation tables;
- unknown reasons remain visible;
- the top-level canonical `part_type` may be propagated to individual result display context when the result itself does not repeat it;
- browser-generated demo-overlay results remain visibly labelled as demo registrations and must not be presented as canonical semantic-search results;
- do not invent provider evidence that is not present in the response;
- scores may remain in advanced/debug information if that is the existing presentation policy.

Do not alter backend response contracts.

## Step 5 — Load consumer filters from canonical API with demo fallback

`ConsumerSearchMockup.js` currently uses static lists from `mockData.js`.

Use the existing `getCatalogFilters()` service to load the current canonical filter contract and drive, where applicable:

- service categories;
- part families;
- family-keyed part types;
- materials;
- processes;
- certifications.

Requirements:

- convert `{value,label}` entries to PrimeReact options correctly;
- respect canonical `service_category` ↔ `part_family` relationships;
- continue deriving the correct service category for the selected family;
- keep specialized gear/shaft/metal-part input sections and current nested request construction;
- keep `match_policy.optional_match_mode = "score_only"` unless current backend evidence proves otherwise;
- static mock vocabulary may remain only as an explicit **demo fallback** if catalogue filters cannot be loaded;
- show a modest UI notice if fallback vocabulary is being used;
- do not make material grades a canonical consumer search criterion, because the current harmonized search contract does not accept `material_grades`;
- do not make the form unusable when demo API endpoints are disabled; canonical consumer search must remain independent of demo state where possible.

Ensure newly available canonical part types such as crown gear / stepped shaft / worm shaft are not silently omitted when the filter endpoint provides them.

## Step 6 — Preserve demo provider flow as demo-only

The active provider UI currently uses:

```text
/api/demo/provider-publication/state
/api/demo/provider-publication/preview
/api/demo/provider-publication/simulate-update
```

Keep this behavior for the pilot illustration unless current code proves it is broken.

Do not replace these calls with direct browser calls to trusted production lifecycle APIs.

Make wording in UI/README explicit:

- registration/update here is **demo persistence**;
- it illustrates what future Marketplace/CMM-mediated provider lifecycle interaction could look like;
- it is not the production trusted provider lifecycle;
- demo endpoints may be disabled in normal production environments.

## Step 7 — Route cleanup

The central route map currently marks all `/demo/*` paths public while child pages also use `DemoRoleGuard`.

Apply this minimal access policy:

```text
/demo                  -> public
/demo/provider         -> authenticated
/demo/consumer-search  -> authenticated
/demo/admin-audit      -> authenticated
```

Rationale:

- `/demo` can remain public so unauthenticated users see the login/role-selection entry point;
- child demo pages require an authenticated Keycloak session at the central route layer;
- `DemoRoleGuard` remains responsible for the selected provider/consumer/admin demo-role presentation;
- client-side route guards are UX controls only and **not a backend authorization boundary**.

Do not claim this makes the backend endpoints secure.

## Step 8 — Eliminate accidental Next.js routes

The Pages Router currently turns reusable component files under `src/pages/home/` into routes, notably:

```text
/home/DashboardContent
/home/NotFoundPage
```

Move reusable components to an appropriate non-pages directory, for example:

```text
src/components/home/DashboardContent.js
src/components/home/NotFoundPage.js
```

Update imports in:

```text
src/pages/index.js
src/pages/404.js
```

and any other callers.

Delete the old component copies from `src/pages/home/` so those accidental routes no longer exist.

Do not remove intended `/home/...` pages such as Contact, Help, Brand, AccessDenied, ErrorPage, or EmptyPage.

## Step 9 — Runtime configuration truthfulness

Review:

```text
src/config/runtimeConfig.js
public/config.js
SearchErrorMessage.js
DemoBackendStatusPanel.js
README.md
```

The local default `http://localhost:8000` may remain as a **local-development default**, but remove wording that treats it as universally correct.

Document clearly:

- browser runtime config comes from `window.MAASAI_CONFIG`;
- `mdcApi.baseUrl` must be overridden for deployed environments;
- deployed browser/backend traffic should use an appropriate HTTPS endpoint;
- CORS/origin policy must permit the deployed frontend origin;
- `sharedApiPrefix` defaults to `/api`;
- `demoApiPrefix` defaults to `/api/demo`;
- browser config must contain no trusted lifecycle service token or other secret;
- the accepted current MDC production deployment normally has the demo API disabled, so provider/admin demo actions require a deliberately demo-enabled backend environment.

Update no-response/error messages to refer to the **configured MDC API URL** or generic configuration rather than always instructing the user to check `localhost:8000`.

Do not hard-code the current Vercel production hostname as the only supported architecture.

## Step 10 — Replace stale frontend README

Replace the generic create-next-app boilerplate `mdc-catalog/demo-frontend/README.md` with a project-specific README covering:

- what the MDC demo frontend is;
- explicit statement that it is not the real CMM;
- provider/consumer/admin demo roles;
- which parts use canonical public MDC APIs;
- which parts use `/api/demo/...` and may be disabled;
- why trusted lifecycle writes are not performed directly from browser code;
- local requirements and Node/npm version expectations based on current repo/Docker evidence;
- `npm ci`, `npm run dev`, `npm run lint`, `npm run build`, `npm run start`;
- runtime `window.MAASAI_CONFIG` example using placeholders/safe URLs only;
- local `http://localhost:8000` development convention;
- deployed HTTPS/CORS requirement;
- GitHub development → GitLab release boundary, linking to the existing provenance/release docs;
- where the comprehensive manual will later live.

The staging-only file:

```text
README_SANITIZED_SNAPSHOT_DRAFT.md
```

is now stale because the snapshot has actually been imported. Incorporate any still-useful provenance into the real README/provenance docs and delete the staging-only draft.

## Step 11 — Normalize inherited whitespace baseline

The initial sanitized import intentionally preserved nine inherited whitespace warnings for byte-for-byte provenance.

Now normalize those exact files as part of the first cleanup commit so future `git diff --check` is clean:

Extra EOF blank-line files:

```text
src/components/mdc/DemoBackendStatusPanel.js
src/components/mdc/DemoWorkflowPanel.js
src/components/mdc/SearchErrorMessage.js
src/components/mdc/SearchPayloadPreview.js
src/components/mdc/searchResultFormatters.js
src/services/mdc/index.js
```

Trailing-whitespace SCSS files:

```text
src/styles/demo/code.scss
src/styles/layout/_config.scss
src/styles/layout/_variables.scss
```

Do not mass-reformat unrelated source files.

## Step 12 — Testing/CI scope

Do not add a large testing framework in this milestone.

Inspect existing GitHub workflows first. If there is no conflicting workflow and a small scoped workflow is straightforward, you MAY add a GitHub Actions workflow that runs only for relevant frontend changes and performs:

```text
npm ci
npm run lint
npm run build
```

with a supported Node version consistent with the frontend Dockerfile.

If adding CI would materially broaden the milestone or conflict with existing repository policy, leave it as documented future work. Report the decision.

No `npm test` claim may be made because there is currently no test script unless you explicitly and minimally create one—which is not required here.

## Step 13 — Create milestone report

Create:

```text
mdc-catalog/docs/Demo_Frontend/02_frontend_api_config_cleanup_and_validation.md
```

It must document:

- purpose/scope;
- exact starting commit;
- changed files by category;
- current canonical API mapping;
- demo-only API mapping;
- lifecycle browser-boundary decision;
- filter-loading behavior and fallback;
- result normalization behavior;
- route/access changes;
- accidental-route cleanup;
- runtime configuration model;
- README/documentation updates;
- whitespace normalization;
- validation commands/results;
- limitations/future CMM work;
- no GitLab changes;
- final commit/push information after completion.

Do not claim that client-side roles secure backend APIs.

## Step 14 — Validation gates

### A. Static/security checks

Verify all of the following:

- active frontend contains no `/api/v1` route usage;
- stale lifecycle route strings `/provider-publication/validate` and `/provider-publication/publish` are absent from active frontend code;
- nonexistent browser helper `GET /api/providers` is absent;
- no `MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN` value or browser storage of any trusted lifecycle secret exists;
- no `.env*`, private keys, passwords, database URLs, or raw credential-bearing realm exports are introduced;
- no GitLab remote is added;
- backend application code is unchanged;
- original `template-frontend` is unchanged;
- `git diff --check` passes with **no exception**.

A safe secret scan must print only path/key/risk categories, never values.

### B. Dependency/build validation

Package installation for validation is authorized for this milestone.

From:

```powershell
cd C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\demo-frontend
```

Run:

```powershell
npm ci
npm run lint
npm run build
```

Requirements:

- `npm ci` must use the existing lockfile;
- `package.json` / `package-lock.json` must not be modified by the install;
- generated `node_modules` / `.next` output must remain ignored/untracked;
- lint passes (warnings may be reported if the command exits 0; do not hide them);
- production build passes.

If dependency installation or build fails because of an environmental/toolchain problem, diagnose narrowly. Do not upgrade packages automatically. Stop and report before broad dependency changes.

### C. Route/build sanity

Using the build output and, if practical, a temporary local start, verify intended route behavior at least for:

```text
/
/demo
/demo/provider
/demo/consumer-search
/demo/admin-audit
/404
```

Confirm `/home/DashboardContent` and `/home/NotFoundPage` are no longer generated as intended application routes.

Do not weaken authentication merely to make route smoke tests easier.

### D. Public backend read/search smoke

If network access is available, use only safe/read-only public MDC calls against:

```text
https://maasai-mdc-v1.vercel.app
```

Check:

```text
GET /api/health
GET /api/catalog/filters
POST /api/service-discovery/search
```

Use a valid non-destructive search payload based on current registry values.

Confirm:

- health HTTP 200 and `contract_version=1.0`;
- filters HTTP 200 and expected current structural keys;
- search HTTP 200 and current flattened public response shape;
- frontend normalization can consume a representative current result shape.

Do NOT call:

- trusted provider lifecycle writes;
- demo mutation endpoints;
- Fuseki graph-store/write endpoints;
- destructive actions.

If the deployed backend has a stale temporary remote Fuseki query endpoint and search falls back internally, record the observed public response only; do not mutate Vercel configuration in this milestone.

## Step 15 — Git review and commit

Before staging:

```powershell
git status --short
git diff --stat
git diff --check
```

Review the complete diff. Stage only frontend cleanup, its report, and an optional scoped CI workflow if explicitly justified by the implementation.

After staging:

```powershell
git diff --cached --stat
git diff --cached --name-status
git diff --cached --check
```

Require:

- no unexpected files;
- no backend code changes;
- no credentials;
- no generated build/dependency output;
- no preservation artifacts;
- no unrelated deletions;
- `git diff --cached --check` PASS.

If all gates pass, commit with:

```text
fix: align MDC demo frontend with current API contract
```

Push only:

```powershell
git push origin demo-frontend-integration
```

Verify local branch and `origin/demo-frontend-integration` point to the same commit.

Do not merge to `main` yet. Do not push to GitLab.

## Required final report

Return exactly a report titled:

```text
# FRONTEND API CONFIG CLEANUP AND VALIDATION REPORT
```

Include:

### 1. Repository gate
- starting branch/commit
- clean/synchronized state
- personal GitHub remote verification
- GitLab remote present: NO

### 2. Cleanup implemented
- stale lifecycle helper decision
- client error handling
- canonical result normalization
- catalogue-filter loading + fallback
- demo-provider boundary
- route changes
- accidental route cleanup
- runtime config/documentation
- README replacement
- whitespace normalization
- CI decision

### 3. API alignment evidence
- canonical public endpoints
- demo-only endpoints retained
- `/api/v1` findings
- stale lifecycle paths findings
- current filter shape handling
- current public search response handling

### 4. Security boundary
- trusted lifecycle token in browser: NO
- lifecycle bearer/actor/If-Match browser implementation: NO
- secrets introduced: NO
- demo role guard described as backend security: NO
- backend code changed: NO
- original frontend repo changed: NO
- GitLab writes: NONE

### 5. Validation
- secret-risk scan
- `git diff --check`
- `npm ci`
- `npm run lint`
- `npm run build`
- lockfile changed: NO
- generated files tracked: NO
- route sanity results
- public backend smoke results

### 6. Documentation
- milestone report path
- frontend README status
- provenance/release docs retained

### 7. Git result
- commit SHA
- push result
- local/remote synchronized
- `main` merged: NO
- GitLab push: NO

### 8. Remaining future work
Keep this limited to genuine future CMM/server-side lifecycle integration, deployment-specific HTTPS/CORS/Keycloak ownership, optional stronger automated tests, and approved GitLab release work.

### 9. Final gate

End with exactly one of:

```text
FRONTEND API CONFIG CLEANUP AND VALIDATION: PASS
READY_FOR_FRONTEND_MASTER_DOCUMENT: YES
```

or a clear FAIL/BLOCKED result with no unsafe push.