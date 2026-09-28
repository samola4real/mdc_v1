# M6-A — Marketplace integration package and plenary release readiness

## Objective

Prepare the accepted MDC v1 backend for MaaSAI Marketplace integration and plenary handoff **without redesigning the API and without pretending Production is ready before durable Fuseki hosting exists**.

This is the next step after accepted M5-A and M5-B.

M5-B proved the complete deployed flow in an isolated Preview environment:

`provider write -> PostgreSQL -> RDF rebuild -> Fuseki publication -> revision verification -> immediate canonical search`

and the reverse update/delete behavior.

M6-A is therefore primarily **contract freeze, partner integration packaging, demo/recovery runbook, and release-readiness verification**. It should not introduce a new architecture.

## Baseline

Repository: `samola4real/mdc_v1`

Start from latest `main`, which must include accepted M5-B merge commit:

`52b8d1fe26fa4acf74b8d38e67fad30ffb42b9af`

Create branch:

`phase4/marketplace-integration`

Use a clean linked worktree. Preserve the original checkout and its unrelated local modifications.

Read as authoritative current evidence:
- `docs/codex/current_refractor _plan.md`
- `docs/codex/Reports/M5A_postgresql_lifecycle_vercel_postman_report.md`
- `docs/codex/Reports/M5B_fuseki_immediate_discovery_validation_report.md`
- `docs/codex/Reports/M5_vercel_deployment_and_postman_validation_report.md`
- current API routes, serializers, lifecycle services, discovery services, settings, tests, and partner API docs on `main`

Do not use old historical assumptions where current code/tests differ.

## Hard constraints

1. **Do not redesign or version the API.** Canonical partner endpoints remain under `/api/`; do not add `/api/v1/`.
2. Do not change lifecycle semantics that passed M5-A/M5-B unless a verified documentation/contract inconsistency is found.
3. Do not modify or deploy Production.
4. Do not configure Cloudflare, AWS, DNS, or a new Fuseki host in this task.
5. Do not touch the real local `mdc-fuseki` container/dataset or existing provider records.
6. Do not start frontend/demo development.
7. Preserve the implementation of lifecycle authentication. For the plenary/pilot, document the approved environment-configurable no-auth mode; do not delete security code or make insecure defaults.
8. Preserve ETag/If-Match concurrency semantics.
9. Do not create a final release tag yet. A release tag requires successful joint Marketplace integration plus an approved durable Fuseki deployment/plenary environment.
10. Do not claim full M6 completion if the Marketplace team has not actually performed the joint test.

## M6-A Task 1 — Freeze and verify the canonical API contract

Inspect current routing, serializers, tests and deployed evidence, then produce a concise frozen partner contract covering the exact currently supported endpoints:

- `GET /api/health`
- `GET /api/catalog/filters`
- `POST /api/service-discovery/search`
- `POST /api/provider-publication`
- `POST /api/provider-publication/validation`
- `GET/PATCH/DELETE /api/providers/{provider_id}`
- `GET/POST /api/providers/{provider_id}/offerings`
- `GET/PATCH/DELETE /api/offerings/{offering_id}`

For each partner-facing endpoint document:
- purpose;
- request body/parameters;
- required vs optional fields;
- representative response;
- lifecycle/publication status semantics;
- ETag/If-Match behavior;
- expected HTTP error classes;
- whether the endpoint mutates PostgreSQL;
- whether successful automatic mode requires verified Fuseki synchronization;
- retry guidance for accepted-but-not-synchronized failures.

The contract must explicitly state:
- provider supports multiple independently addressable offerings;
- offerings may share the same service category;
- `offering_id` is identity and immutable;
- service category is classification, not identity;
- route/process sequence fields are excluded;
- whole-selected-map PATCH semantics for optional map-field attribute removal;
- DELETE is permanent for operational state while minimal audit/publication history is retained;
- a successful automatic publication is only complete after query-visible revision verification;
- Marketplace must not call a separate synchronization API;
- Marketplace must not blindly replay a non-idempotent registration after a post-commit sync failure.

Cross-check every material statement against current implementation/tests. Fix only stale documentation; do not alter runtime merely to match old prose.

## M6-A Task 2 — Create a partner handoff package

Create/update a clear partner-facing documentation package under `docs/Partner_API/` (respect existing case/path conventions already in the repo rather than creating duplicate trees).

It should include:

### A. Marketplace quick-start
A short guide showing:
1. discover supported filters;
2. validate a provider payload;
3. register provider + first offering;
4. GET provider and capture ETag;
5. add a second same-category offering;
6. PATCH provider/offering;
7. remove one optional map attribute safely;
8. search after successful publication;
9. DELETE one offering while retaining siblings;
10. DELETE provider and verify disappearance.

Use realistic but disposable/example identifiers. No secrets.

### B. Stable request/response examples
Provide JSON examples for:
- provider registration;
- second offering creation;
- provider PATCH;
- offering PATCH;
- selected-map attribute removal;
- canonical search;
- representative successful automatic-sync receipt;
- representative pending/failed synchronization receipt;
- provider/offering deletion;
- 400/404/409/412/428/503 errors.

Examples must conform to current serializers and controlled vocabulary rules. Do not invent unsupported fields.

### C. Postman partner collection
Review the existing M5 and M5-A collections. Produce one clearly named **M6 Marketplace Integration** Postman collection/environment template suitable for partner use.

Requirements:
- secret-free;
- configurable `base_url`;
- no baked Production URL;
- disposable unique provider ID generation;
- no bearer/actor header in the approved plenary no-auth profile;
- captures and reuses ETags;
- demonstrates multiple same-category offerings;
- validates lifecycle responses accurately;
- includes canonical discovery checks only when automatic sync is enabled;
- clearly separates destructive cleanup operations;
- does not depend on the demonstration frontend.

Do not remove the evidence collections from M5-A/M5-B.

## M6-A Task 3 — Plenary demo runbook

Create a practical plenary runbook that another team member can follow without knowing the internal Django implementation.

The runbook must include:

### Preconditions
- deployed backend URL;
- PostgreSQL reachable and migrated;
- durable remote Fuseki query + Graph Store URLs target the same dataset;
- synchronization flags enabled;
- provider publication and validation flags enabled;
- approved pilot lifecycle auth/actor flags;
- concurrency enabled;
- demo API disabled;
- health/search preflight;
- no secret values printed.

### Demonstration sequence
Use one disposable demonstration provider:
1. health;
2. filters;
3. baseline search;
4. validation;
5. registration;
6. immediate consumer search;
7. add same-category offering;
8. immediate search;
9. PATCH;
10. immediate search;
11. remove one attribute;
12. verify search;
13. DELETE one offering;
14. verify sibling remains;
15. DELETE provider;
16. verify all offerings disappear.

For each step include expected status class and what the presenter should verify, not merely “request succeeds”.

### Recovery/failure procedure
Cover:
- 503 after DB commit but before verified Fuseki visibility;
- pending/failed outbox work;
- stale ETag;
- Fuseki temporarily unavailable;
- query-visible revision mismatch;
- safe retry of the existing synchronization management command;
- instruction not to blindly replay provider registration;
- how to confirm operational PostgreSQL state before retry/recovery.

Do not expose internal management commands as Marketplace APIs.

## M6-A Task 4 — Production/plenary readiness checklist

Create a release-readiness checklist separating **already proven** from **still required**.

Already proven should include only evidence supported by M1-M5:
- lifecycle CRUD;
- multi-offering;
- ETag protection;
- outbox;
- automatic RDF/Fuseki synchronization;
- revision verification;
- authoritative immediate discovery;
- Vercel Preview + isolated Neon validation;
- M5-A and M5-B acceptance totals.

Still required before Production/plenary enablement must include at least:
- durable remotely hosted/protected Fuseki query + Graph Store pair;
- same-dataset endpoint verification;
- Production/plenary database migration verification;
- approved Production environment-variable values;
- reliable retry/worker/scheduler arrangement for pending/failed outbox events;
- final smoke test using disposable data;
- joint Marketplace test;
- confirmation that temporary no-auth pilot mode is explicitly approved for that deployment;
- final rollback/recovery ownership.

Do not solve durable infrastructure in this task; document the exact gate.

## M6-A Task 5 — Marketplace compatibility / joint-test script

Create a concise joint-test checklist for the Marketplace team.

It must state:
- exact base URL placeholder;
- exact endpoints called by Marketplace;
- expected request order;
- values Marketplace must retain between calls (provider_id, offering_id, ETag);
- expected success/error semantics;
- which result proves semantic visibility;
- cleanup steps;
- evidence to capture (status, response, IDs, ETag, search match).

Do not claim this joint test was performed unless actual Marketplace-originated calls are available during this task. If no Marketplace client/environment is available, mark it **prepared, not executed**.

## M6-A Task 6 — Regression and contract verification

Run:
- focused lifecycle/sync/search regression;
- full Django suite;
- `manage.py check`;
- `makemigrations --check --dry-run`;
- `git diff --check`;
- parse/validate new Postman JSON assets;
- inspect route table / URL configuration to prove no accidental `/api/v1/` partner route was introduced.

If documentation examples can be automatically validated against serializers without mutating real data, do so.

Do not require live Fuseki/Cloudflare/AWS for M6-A. External-integration tests may remain skipped where designed, but document them accurately.

## M6-A Task 7 — Update roadmap/status truthfully

Update `docs/codex/current_refractor _plan.md` only enough to reflect:
- M1-M5 accepted;
- M6-A partner integration/release-readiness package completed if this task succeeds;
- final M6 joint integration + Production/plenary release remains gated by durable Fuseki hosting and actual Marketplace test.

Do not rewrite historical milestone detail unnecessarily.

## Required report

Write:

`mdc-catalog/docs/codex/Reports/M6A_marketplace_integration_release_readiness_report.md`

Report:
- branch and final commit;
- files changed;
- frozen endpoint list;
- Postman asset names and request count;
- regression results;
- documentation validation results;
- what was proven by M5 and reused rather than re-tested live;
- joint Marketplace test status: executed or prepared-only;
- explicit remaining gates for Production/plenary;
- confirmation Production, real Fuseki, provider data and original checkout were untouched;
- confirmation no release tag was created.

## Completion / Git

Commit and push scoped work to:

`phase4/marketplace-integration`

Do not merge to `main`.

Do not deploy Production.

Do not create a release tag.

Do not start a speculative AWS/Cloudflare infrastructure implementation.

Return a short review handoff with:
- branch;
- final commit SHA;
- report path;
- Postman collection/environment paths;
- test results;
- Marketplace joint-test status;
- remaining Production/plenary gates.

## Acceptance criterion

M6-A is accepted when the current proven API is frozen and packaged so the Marketplace team can integrate without another API redesign, with a reproducible plenary workflow and a truthful list of the remaining infrastructure/joint-test gates.
