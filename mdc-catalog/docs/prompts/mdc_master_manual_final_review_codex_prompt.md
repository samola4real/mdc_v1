# Codex Prompt — Final Review and Correction of the MDC Master Manual

## Objective

Perform a **targeted final correction pass** on:

`mdc-catalog/docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md`

The document is already comprehensive and should **not** be rewritten from scratch. Preserve its structure, depth, diagrams, historical narrative, API examples, Postman guide, P3.4/P3.5 evidence, limitations, and AWS section. Correct the specific issues below and strengthen a few missing integration/reader-guide points.

This is a documentation-only task.

## Hard constraints

- Modify **only** `mdc-catalog/docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md`.
- Do not modify application code, tests, data, configuration, other reports, or prompts.
- Do not expose, print, or copy any secret values.
- Current code and accepted Phase 3 evidence override stale Week-1 documentation.
- Do not reintroduce `/api/v1` as a current route.
- Keep PostgreSQL as operational source of truth and RDF/Fuseki as a derived semantic layer.
- Keep Phase 3 complete and P3.6 explicitly a completed **plan/readiness milestone**, not an executed AWS migration.
- Run `git diff --check` before committing.
- If the worktree contains unexpected tracked changes before editing, stop and report them.

## Repository gate

From the repository root:

1. `git status --short`
2. `git pull --ff-only`
3. Confirm the current master manual exists.
4. Confirm there are no unrelated tracked changes.

## Required corrections

### 1. Correct the project name everywhere

The canonical project/component name is:

**MaaSAI MaaS Dynamic Catalogue (MDC)**

The document currently says **MaaSAI Manufacturing Data Catalogue** in the title/executive summary. Correct those occurrences. Do not rename MDC to Manufacturing Data Catalogue anywhere.

### 2. Correct Fuseki graph terminology

The synchronization implementation replaces the configured Fuseki **default graph** through Graph Store PUT. It does not target a named graph in the current implementation.

Replace the executive-summary wording `remote named graph` with wording such as:

`configured Fuseki default graph`

Verify against:

- `backend/apps/providers/catalogue_sync_service.py`

### 3. Correct the Postman `/api/catalog/filters` assertion

The current public filter response is not a set of flat string arrays. Verify against:

- `backend/apps/api/public_contract.py::build_public_catalog_filters`

Current shape:

- `service_categories`: array of objects with `value`, `label`, `part_family`
- `part_families`: array of objects with `value`, `label`, `service_category`
- `part_types`: object keyed by part family, each value an array of `{value, label}`
- `materials`: array of objects
- `processes`: array of objects
- `certifications`: array of objects

Replace the broken Postman assertion with a working version equivalent to:

```javascript
pm.test("Required controlled values are advertised", function () {
  const body = pm.response.json();
  const serviceCategories = body.service_categories.map(item => item.value);
  const partFamilies = body.part_families.map(item => item.value);
  const metalPartTypes = (body.part_types.metal_part || []).map(item => item.value);

  pm.expect(serviceCategories).to.include("precision_metal_parts");
  pm.expect(partFamilies).to.include("metal_part");
  pm.expect(metalPartTypes).to.include("bracket");
});
```

Also fix wording such as `six controlled arrays`. Use `six controlled structures` or state precisely that there are five arrays plus the family-keyed `part_types` mapping.

For lay readers, add a compact example of the actual current filter response structure in the API reference if it is not already shown.

### 4. Correct offering-create ETag semantics

The master manual currently says that:

`POST /api/providers/{provider_id}/offerings`

returns a **provider ETag**.

This is incorrect. The write service attaches an ETag for the **newly created offering**.

Verify against:

- `backend/apps/providers/provider_lifecycle_write_service.py::add_provider_offering`
- `_entity_etag("offering", offering)`

Correct every occurrence, including the endpoint detail and endpoint matrix.

It is valid to tell clients either:

- use the returned offering ETag, or
- GET `/api/offerings/{offering_id}` immediately before PATCH to capture the current offering ETag.

The existing Postman flow may still use GET-before-PATCH; that is safe.

### 5. Complete current H5 optional-match semantics

The current request contract accepts:

- `optional_match_mode: any`
- `optional_match_mode: all`
- `optional_match_mode: score_only`

The manual discusses `any` and `all` but should explicitly document `score_only`.

More importantly, in current H5 behavior `optional_match_mode` by itself does **not** remove candidates. It computes internal `optional_policy_satisfied`; public response shaping does not expose that internal field. Candidate removal can occur through `unknown_policy: reject_unknown` and/or `minimum_score`.

Verify against:

- `backend/apps/api/service_discovery_search_serializers.py`
- `backend/apps/search/service_discovery_local_matcher.py`
- `docs/07_h5_harmonized_local_matcher_implementation_report.md`

Clarify this in Section 11 and/or Section 18 so an integrator does not misunderstand `all` as an automatic filter.

### 6. Normalize trusted endpoint error/status documentation

Review the endpoint matrix and detailed API reference against current views/security behavior. Ensure the documented possible statuses include the current feature-flag/auth-unavailable behavior.

Use this safe summary unless current code proves otherwise:

- `POST /api/provider-publication/validation`: `200`, `400`, `401`, `403`, `503`
- `POST /api/provider-publication`: `201`, `400`, `401`, `403`, `409`, `503`
- `GET /api/providers/{provider_id}`: `200`, `401`, `404`, `503`
- `PATCH /api/providers/{provider_id}`: `200`, `400`, `401`, `403`, `404`, `412`, `428`, `503`
- `GET /api/providers/{provider_id}/offerings`: `200`, `401`, `404`, `503`
- `POST /api/providers/{provider_id}/offerings`: `201`, `400`, `401`, `403`, `404`, `409`, `503`
- `GET /api/offerings/{offering_id}`: `200`, `401`, `404`, `503`
- `PATCH /api/offerings/{offering_id}`: `200`, `400`, `401`, `403`, `404`, `412`, `428`, `503`

Verify against:

- `backend/apps/api/views/get_views.py`
- `backend/apps/api/views/post_views.py`
- `backend/apps/api/lifecycle_security.py`

Do not invent new error codes.

### 7. Fix P3.6 future wording

The document says wording similar to:

`The next deployment program should implement P3.6 rather than reopening Phase 3.`

P3.6 itself is already complete as an AWS migration/readiness **plan**. Change this to:

`The next deployment program should implement the accepted P3.6 AWS migration/readiness plan rather than reopening Phase 3.`

Keep the distinction:

- P3.6 planning/readiness = COMPLETE
- actual AWS infrastructure/migration/cutover = FUTURE

### 8. Add a clear “How to use this manual” quick-start

Near the beginning, after the Executive Summary or terminology section, add a short reader navigation block for:

- Lay reader / project manager
- Marketplace/consumer integrator
- Trusted provider integrator
- Tester/Postman user
- MDC developer/operator
- AWS/platform engineer

State clearly that a **new Marketplace consumer integration** should start with only these canonical public endpoints unless a separate trusted lifecycle integration is explicitly agreed:

- `GET /api/health`
- `GET /api/catalog/filters`
- `POST /api/service-discovery/search`

The trusted provider lifecycle APIs are a separate authenticated integration surface.

### 9. Add Cloud MaaS Marketplace (CMM) relationship in plain language

The master manual should define the relationship to the **Cloud MaaS Marketplace (CMM)** because a new project reader may not know it.

Add concise wording explaining:

- CMM/Marketplace is the intended external user/integration context for provider onboarding and consumer discovery.
- MDC is API-first and does not implement the Marketplace UI/login itself in the current pilot.
- Marketplace consumer side can obtain filter values and call canonical discovery.
- Trusted provider onboarding/update can later be integrated with Marketplace identity/authorization, but current pilot lifecycle uses the trusted bearer-token boundary.

Do not claim a Marketplace integration has already been completed.

### 10. Add the accepted Phase-3 production policy snapshot

In Current Deployment/Operations, add a clearly labelled **accepted Phase-3 pilot configuration snapshot** (not a permanent guarantee):

```text
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
MDC_CATALOG_SYNC_ENABLED=False
MDC_DEMO_API_ENABLED=False
```

Explain that deployment settings must be rechecked if the environment changes.

### 11. Clarify temporary post-pilot infrastructure cleanup

Add a concise operations note that:

- the Cloudflare Quick Tunnel/query endpoint is temporary validation infrastructure;
- after it is no longer required, remove or replace the temporary Vercel `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` and redeploy so a dead endpoint does not add avoidable remote-query timeout/fallback delay;
- never expose Graph Store/write credentials through Vercel/public clients;
- rotate pilot database/Fuseki credentials before long-term production/AWS use where appropriate.

Do not perform any infrastructure changes in this task.

### 12. Avoid overstating DB provenance for fallback candidates

Review wording that implies **all runtime candidates** necessarily come from current PostgreSQL. The operational source of truth is PostgreSQL, and the synchronized Fuseki graph is built from it. However, current runtime fallback order includes local generated RDF and harmonized YAML fallback paths.

Use precise wording:

- PostgreSQL is authoritative operational state.
- operator synchronization builds the remote Fuseki graph from active DB records.
- runtime continuity still includes RDFLib and harmonized-YAML fallbacks, which may reflect generated/curated fallback artifacts rather than a fresh database read.

Verify against:

- `backend/apps/search/service_discovery_runtime_search.py`
- `backend/apps/search/service_discovery_matching_alignment.py`
- `backend/apps/search/service_discovery_sparql_service.py`

Do not imply that fallback makes YAML authoritative.

## Quality enhancement — API examples

Without making the document unnecessarily repetitive, ensure the API reference remains useful to a lay tester. At minimum it should contain:

- exact health response;
- representative current filter response structure;
- minimal discovery request and representative public response;
- provider-publication validation behavior;
- provider registration request/response cross-reference;
- provider GET/PATCH + ETag workflow;
- offering create/GET/PATCH + ETag workflow;
- one representative current JSON error envelope;
- status-code matrix.

Cross-reference later detailed walkthroughs instead of duplicating giant payloads unnecessarily.

## Static verification after editing

Run checks equivalent to:

```powershell
git diff --check
rg -n "Manufacturing Data Catalogue|remote named graph|six controlled arrays|provider ETag|optional_match_mode|score_only|P3\.6" mdc-catalog/docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md
```

Manually verify that:

- project name is `MaaS Dynamic Catalogue`;
- no current `/api/v1` route is presented as valid;
- offering create is documented with offering ETag;
- Postman filter assertion matches the object structure;
- `score_only` is documented;
- P3.4 remains `45 passed / 0 failed`;
- P3.5 remains `selected=4, succeeded=4, failed=0, noop=0, events=5`, `731` triples;
- P3.6 remains completed as a plan, not as an AWS deployment;
- no secrets are present.

## Git completion

If all checks pass and only the master manual changed:

1. Commit the correction on `main` with a concise message such as:
   `docs: finalize comprehensive MDC master manual`
2. Push fast-forward to `origin/main`.
3. Verify local HEAD equals `origin/main`.

Do not force-push or rewrite history.

## Return report

Return exactly this structure:

```text
# MDC MASTER MANUAL FINAL REVIEW REPORT

## Repository gate
- pull/status: PASS/FAIL
- unrelated tracked changes: NONE / describe

## Corrections
- canonical project name: PASS/FAIL
- Fuseki default-graph terminology: PASS/FAIL
- Postman filter structure/assertion: PASS/FAIL
- offering-create ETag semantics: PASS/FAIL
- H5 any/all/score_only semantics: PASS/FAIL
- trusted endpoint status matrices: PASS/FAIL
- P3.6 plan-vs-implementation wording: PASS/FAIL
- How-to-use reader guide: PASS/FAIL
- CMM/Marketplace relationship: PASS/FAIL
- Phase-3 production flag snapshot: PASS/FAIL
- temporary infrastructure cleanup note: PASS/FAIL
- fallback/DB provenance wording: PASS/FAIL

## Verification
- git diff --check: PASS/FAIL
- secrets introduced: NO/YES
- application code changed: NO/YES
- master manual only changed: YES/NO

## Git
- commit: <sha or NONE>
- push origin/main: PASS/FAIL
- local/remote synchronized: PASS/FAIL

## Final gate
MDC MASTER MANUAL FINAL REVIEW: PASS/FAIL
```
