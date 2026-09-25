# M5 — Vercel deployment and live Postman/API validation (Codex task prompt)

**Scope:** M5 only. **Repository:** `samola4real/mdc_v1`; project root `mdc-catalog/`.
**Prerequisite:** reviewed M4 merge `d6c7f5e3879b04489c2fe64575a2abb7e4127706` must be present in fresh `origin/main`.

## Goal

Deploy the accepted M1–M4 backend to the existing MaaSAI MDC Vercel project and prove the hosted lifecycle works end to end against the intended Neon PostgreSQL and external Fuseki catalogue:

**register / add offering / PATCH / attribute removal / DELETE -> automatic semantic publication -> very next canonical search reflects the change.**

The demo frontend is not part of this milestone. Use command-line HTTP/Postman-equivalent requests with disposable test IDs. Do not modify Tasowheel, Framo Morat, FACTOR or any real provider.

The plenary pilot has an explicit temporary no-auth lifecycle configuration. Do not remove authentication code; configure the approved deployment environment with lifecycle auth and actor requirements disabled, while keeping ETag concurrency enabled. Keep canonical unversioned `/api/` routes.

## Safe Git and deployment preparation

1. Fetch latest `origin/main`, confirm M4 merge, and create a separate clean linked worktree on `phase4/deployment-validation` (or clearly named follow-up). Preserve the original checkout's unrelated `.gitignore` and `mdc-catalog/demo-frontend/src/pages/demo/index.js` changes exactly: do not modify/stash/discard/reset/copy/commit them. Do not merge to main during this task.
2. Inspect the existing Vercel project linkage/configuration and currently deployed commit before changing anything. Reuse the existing `maasai-mdc-v1` project; do not create a second production project. Prefer a Preview deployment first, then Production only after live acceptance passes.
3. Never print, commit, report, or echo secret values. Report only whether required variables are present/missing and in which Vercel environment.
4. Confirm deployed Python is >=3.12, Django production settings are selected, the intended Neon `DATABASE_URL` is configured, and migrations 0003 and 0004 are applied. Do not reset/drop data.

## Required plenary configuration

Verify/apply these non-secret switches in the approved plenary environment:

```text
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=False
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=False
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
MDC_CATALOG_SYNC_ENABLED=True
MDC_CATALOG_AUTO_SYNC_ENABLED=True
MDC_DEMO_API_ENABLED=False
```

Verify without exposing values that these dependencies are configured: `DATABASE_URL`, `DJANGO_SECRET_KEY`, `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT`, `SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT`, optional Fuseki username/password, bounded Fuseki timeouts, allowed hosts/CORS as already required. Query and Graph Store endpoints must target the same Fuseki dataset/default graph; do not weaken M4 validation.

## Live readiness checks before mutation

5. On Preview if practical, verify `GET /api/health`, `GET /api/catalog/filters`, canonical `POST /api/service-discovery/search`, provider validation POST without bearer/actor headers, and that demo endpoints are disabled. Confirm auto-sync mode uses authoritative Fuseki rather than local RDF/YAML fallback.
6. Verify through the application path that Fuseki Graph Store write plus query-visible revision round-trip works on the intended dataset. If Vercel request duration/size/runtime cannot safely complete graph rebuild + PUT + verification, stop and report the platform blocker rather than disabling M4 guarantees.

## Live acceptance sequence — disposable provider only

Use a clearly disposable unique provider ID such as `postman_m5_<safe_suffix>` and record it in the report. Before creation, confirm it does not already exist.

7. Execute and capture status/body/ETag evidence:
   1. `POST /api/provider-publication/validation` -> valid.
   2. `POST /api/provider-publication` with one offering -> 201 and `completed/synced`.
   3. Immediate canonical search -> first offering present.
   4. `POST /api/providers/{provider_id}/offerings` with a second offering in the same service category -> 201 completed/synced.
   5. Immediate search -> both distinct offering IDs present.
   6. GET offering, capture ETag; PATCH name/capability with `If-Match` -> 200 completed/synced; immediate search reflects update.
   7. GET/capture current ETag; remove one optional capability key using the M3 selected-map replacement rule -> 200 completed/synced; immediate search reflects removal while retained fields remain.
   8. DELETE second offering with current ETag -> 200 completed/synced; immediate search no longer returns it and still returns sibling.
   9. DELETE disposable provider with current ETag -> 200 completed/synced; immediate search returns neither deleted offering.

8. Negative checks: missing DELETE ETag -> 428; stale PATCH/DELETE ETag -> 412; duplicate provider/offering ID -> conflict; invalid controlled field -> 400; no lifecycle auth header required in approved pilot mode; `/api/v1/...` remains absent/not the partner contract.

If any write returns M4 `503 catalogue_publication_incomplete`, do not blindly repeat non-idempotent registration. Inspect safe publication/outbox state and recover using existing sync behavior, then verify search convergence. Record the real failure and recovery.

## Recovery automation — keep it simple

9. Inspect whether the existing Vercel setup can automatically retry pending/failed outbox work using the existing commands:

```text
python manage.py sync_service_discovery_catalogue --recover-stale
python manage.py sync_service_discovery_catalogue --limit 100
```

Prefer an existing supported scheduler/worker mechanism. Do not add a Marketplace-facing sync endpoint or a second provider-management API. If current Vercel cannot safely schedule these without substantial new architecture, do not over-engineer M5: document it as an M6/release operational requirement and retain truthful 503 behavior.

## Production deployment gate

10. Only after Preview/live dependency checks and disposable acceptance pass, deploy/promote the same reviewed commit/configuration to the intended plenary Production project. Repeat compact Production smoke tests with a new disposable ID: health/filters; canonical POST search; register -> completed/synced -> immediate search; delete provider -> completed/synced -> immediate absence. Do not alter real pilot providers.

## Postman and documentation

11. Update/create a concise Postman collection/environment template under the existing docs/API area if the current one is not adequate. Use variables such as `base_url`, `provider_id`, `offering_id`, captured ETags; no bearer token is needed for the temporary plenary no-auth environment. Do not commit secrets.
12. Update only current partner/backend documentation necessary to reflect actual deployed behavior. Leave historical reports untouched.

## Testing and report

Run focused local M1–M4 regression and full suite if feasible, `manage.py check`, migration consistency, and `git diff --check`. Record local results separately from live Preview/Production evidence.

Write `docs/codex/Reports/M5_vercel_deployment_and_postman_validation_report.md` including: source branch/commit and exact deployed commit(s); Vercel project/environment and non-secret deployment URLs; configuration presence matrix; Python/Django runtime and migration status; Fuseki same-dataset verification; each live lifecycle/search request with endpoint/status/evidence and disposable IDs; latency/timeouts; recovery/scheduler status; files changed; local/live tests; final Production base URL; remaining blockers.

Commit report/docs/config changes to `phase4/deployment-validation` and push. Do not merge this branch; stop for review before M6. If deployment is blocked, push the accurate blocker report and stop.

Return a short completion summary: branch, final commit SHA, report path/URL, Preview/Production URLs/status, live acceptance summary, local test counts, blockers, and `awaiting review before M6`.