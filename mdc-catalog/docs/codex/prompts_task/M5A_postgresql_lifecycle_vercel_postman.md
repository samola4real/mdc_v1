# M5-A — Deploy and verify PostgreSQL provider lifecycle on Vercel (Codex task prompt)

**Scope:** M5-A only; continue existing `phase4/deployment-validation` branch and existing M5 worktree. **Repository:** `samola4real/mdc_v1`; project root `mdc-catalog/`.

## Purpose / accepted temporary trade-off

The user wants to stop Cloudflare setup for now and test the **real provider lifecycle on the Vercel-hosted Django backend using Postman, with PostgreSQL (Neon) persistence only**. Do not wait for, restart, publish, modify, or expose Fuseki/Cloudflare. Keep M4 synchronization implementation intact for later M5-B when a remote Fuseki endpoint is ready.

**M5-A does not meet the previous full M5 requirement of immediate semantic search.** Lifecycle writes update PostgreSQL plus its durable publication/outbox rows; **they do not update remote/local Fuseki, RDF or the existing search index** while sync is off. Do not claim that a successful POST/PATCH/DELETE has become searchable through the canonical consumer search. DB-backed provider/offering GET/list are the acceptance oracles in this phase. Resume full immediate discovery only in M5-B, not in this task.

## Working branch / preservation

1. Fetch `origin/main` and `origin/phase4/deployment-validation`; verify the current M5 branch contains commit `922bad1cc40f3beee27a07e135d653b3af71c687`, M4 is merged, and the preexisting M5 report/Postman assets are intact. Continue in the **existing clean M5 worktree** `C:\Users\Elahi\Desktop\mdc_v1_m5_worktree` and `phase4/deployment-validation` (or safely recover the same branch in an isolated worktree if unavailable). The original checkout has unrelated local `.gitignore` and `mdc-catalog/demo-frontend/src/pages/demo/index.js` changes: never modify/stash/discard/reset/pull over/commit them. Avoid cherry-picking all of main into the M5 branch; the M5-A task prompt can be read from `origin/main` with `git show origin/main:mdc-catalog/docs/codex/prompts_task/M5A_postgresql_lifecycle_vercel_postman.md`. Do not merge to main or start M6.
2. Read the existing M5 blocked report, existing 27-request Postman collection and current API/migration/deployment configuration. Inspect only current runtime paths needed for database-only lifecycle. **No new provider CRUD implementation unless a verified deployed defect blocks acceptance.** No frontend or demo API work.

## Deployment configuration and preflight

3. Reuse the existing Vercel project `mdc19/maasai-mdc-v1` and stable base URL `https://maasai-mdc-v1.vercel.app`. Verify exact project/deployment linkage and deployment commit. Prefer a Preview deployment with an **isolated test Neon database** if already available; do not set up a new cloud infrastructure stack just for M5-A. If isolated Preview DB is unavailable, document this and use only a uniquely named disposable provider on the existing intended *test/plenary* Neon database **if the operator has authorized that environment for writes**. Never mutate Tasowheel, Framo Morat, existing demo data or real providers. Do not point two environments with auto-sync on at the same Fuseki dataset. Deploy only after read-only checks for DB identity/schema, project linkage and a safe migration procedure.
4. Verify and explicitly configure the approved test/plenary environment flags (without printing secrets):
```text
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=False
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=False
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
MDC_CATALOG_SYNC_ENABLED=False
MDC_CATALOG_AUTO_SYNC_ENABLED=False
MDC_DEMO_API_ENABLED=False
```
Temporarily disabling lifecycle auth is an environment-only pilot choice; **retain all authentication code, secured-mode tests and flags** for future re-enabling. Keep ETag/If-Match protection on PATCH/DELETE, including when auth is off. Do not change URL structure (`/api/` is canonical), public search schema, ontology, or security defaults in source.
5. Verify Neon `DATABASE_URL`, Django secret/settings/host configuration in approved scopes without revealing values; do not copy credentials into Git or chat. Confirm Python 3.12 production runtime. Apply provider migrations `0003` and `0004` safely to the intended database only after identifying that exact database and ensuring its existing data/migration history will be preserved; do not drop/reset/flush. Explicitly document whether Production or Preview schema was migrated. If a destructive/unexpected migration is detected, stop and report rather than forcing it.
6. Run local focused regression and full Django tests, `manage.py check`, `makemigrations --check --dry-run`, `git diff --check` as feasible. Preserve existing tests and report any optional integration fixture failures separately. Then deploy a Preview if available or the explicitly approved existing test/plenary production deployment and verify the actual deployed commit. No unverified promotion from Preview.

## Database-only Postman acceptance

7. Existing M5 27-request collection expects `completed/synced` and immediate Fuseki search and **must not be run unchanged** with sync disabled. Create a separate `M5A` Postman collection/environment template in `docs/Partner_API/` by reusing its safe example payloads, ETag capture and disposable identifiers. Use `base_url`, unique `postman_m5a_<suffix>` provider ID, offering IDs and ETags, no token/actor header; no real secrets. Acceptance for lifecycle responses in DB-only mode is the actual documented `accepted/sync_pending` or equivalent non-synced response, **not** `completed/synced`. Do not assert immediate canonical discovery.
8. Run collection with Postman or equivalent real HTTP requests against approved deployed environment and record status/body/ETag:
   - health GET, filters GET, canonical POST search as a **read-only baseline only** (its results may reflect old RDF/YAML and MUST NOT be used as evidence of new DB writes);
   - provider validation POST, register disposable provider with one offering POST, GET provider and offerings and verify persisted values;
   - POST second **same-category** offering, GET list and each detail; verify distinct IDs and independent data;
   - PATCH provider name and selected offering capabilities with current If-Match, GET and verify persistence; PATCH a complete selected map minus one optional attribute and GET again to confirm sibling fields intact;
   - negative cases: duplicate ID, invalid controlled field, missing/stale DELETE ETag and stale PATCH;
   - DELETE only the disposable second offering, GET 404 for deleted offering and GET/list confirms sibling remains;
   - DELETE the disposable provider with its current ETag, GET provider/offering 404 afterward, GET/list of unrelated providers unchanged.
   - Check provider publication/outbox status through permitted non-mutating operator inspection to confirm events remain pending rather than claiming Fuseki was updated. If a request fails after DB mutation, do not blindly repeat non-idempotent POST; inspect GET first and recover according to actual state.
9. Verify no modifications to local Fuseki, RDF files, Cloudflare, or remote dataset were made. A `200` canonical search in this temporary mode does not imply that it reflects newly created/deleted provider data. Report this limitation prominently.

## Report and stopping rule

10. Append accurate M5-A findings to the **existing** `docs/codex/Reports/M5_vercel_deployment_and_postman_validation_report.md`, preserving its original blocker history, and write a concise standalone `docs/codex/Reports/M5A_postgresql_lifecycle_vercel_postman_report.md`. Include exact deployed commit, Preview/Production URL and target DB identity (non-secret), applied migrations, flags without secret values, real HTTP statuses and disposable IDs, PostgreSQL persisted/deleted evidence, outbox pending evidence, tests/limitations, cleanup status, and what remains for M5-B. Distinguish any scope/environment/permission blocker from code failures; never fabricate a successful deployment or Postman run.
11. Commit/push only scoped M5-A docs/Postman and any narrowly required defect fix to `phase4/deployment-validation`. Do not merge to main or deploy further unreviewed changes. Stop for review and return a short summary with branch, final SHA, deployed URL/commit, report path, status of Postman DB-only lifecycle tests, blockers, and explicit **'Fuseki / immediate consumer discovery not tested; M5-B pending.'**

**No requirement to configure Cloudflare or AWS in M5-A.** The user may return to Cloudflare or another remote Fuseki solution after M5-A is accepted.
