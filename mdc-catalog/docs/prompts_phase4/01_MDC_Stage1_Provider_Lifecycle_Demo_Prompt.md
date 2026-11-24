# Stage 1 — Restore complete MDC provider lifecycle demo

Date: 2026-11-24. Scope: implementation and live acceptance on protected Vercel Preview only.

## Objective
Deploy the accepted MDC backend in the existing Vercel project and verify the complete PostgreSQL-backed lifecycle without MDC Bearer authentication or mandatory actor attribution. Keep ETag concurrency. Do not build a frontend, create infrastructure, redesign the API, or repeat the completed deployment audit.

## Targets and references
- Local checkout: `C:\Users\Elahi\Desktop\mdc_v1`; application root: `mdc-catalog/`.
- GitHub: `samola4real/mdc_v1`; accepted application baseline: `004fef8f0db73ef3e12c1035ec470c131dcb99a6`; M6-A merge: `2e49d7c8f7f70f440ae4e873b05cc259884586aa`.
- Existing Vercel team/project: `mdc19/maasai-mdc-v1`, project ID `prj_DekMQdOYuuH0A5yNsCkFmOC4uD9j`.
- Preserve public Production `https://maasai-mdc-v1.vercel.app`, deployment `dpl_GmWLQStvb3qo551uYYUv4zLiW1XK`, SHA `b9275258bf4a2455814ad9b2af9621e0a5d01327`. Reverify current mapping before proceeding.
- Accepted audit: branch `audit/vercel-demo-deployment-20261123`, SHA `6ebf685021c5c093d64e0185a1e742fe3731c163`, file `mdc-catalog/docs/phase4/MDC_Vercel_Demo_Deployment_Audit_2026-11-23.md`.
- Read the M6 integration guide, joint-test checklist, production readiness checklist, Postman collection/environment in `mdc-catalog/docs/Partner_API/` and M5-A/M5-B reports in `mdc-catalog/docs/codex/Reports/`.

## Verified Neon evidence
ChatGPT read-only inspection identified project `maasai-mdc-validation` (`mute-cell-38148661`), branch `main` (`br-wild-haze-aej09lb1`). Database `mdc_validation` has provider migrations 0001_initial, 0002_canonical_parity_fields, 0003_alter_providerpublication_operation, 0004_cataloguesynclease and provider, outbox, lease tables. Database `neondb` has only 0001–0002 and no lease table. These are database-level findings, NOT proof of current Vercel DATABASE_URL binding.

## Step 1 — Preflight and isolation
1. Fetch origin/main. Use a clean linked worktree, never stash/reset/discard/overwrite the original checkout's changes. Deploy the pinned accepted application baseline; later documentation-only commits are not needed in the deployed artifact.
2. Verify Vercel authorization for the exact project/team; if CLI access is blocked, ask for only the necessary operator login. Never expose tokens.
3. Verify Preview DATABASE_URL resolves to the existing Neon project/branch and database mdc_validation using authorized operator-side sanitized checks. Confirm that it is not the Production database and that the required migrations and tables are present. Prior Neon evidence can supplement but not replace binding verification. Review restore capability. Stop before enabling writes if identity/isolation cannot be established. No new database; no migrations against neondb; do not run unnecessary migrations.
4. Record Production deployment/aliases and health, filters, known spur-gear canonical search baseline. Do not change Production.

## Step 2 — Configure only the controlled Preview
Apply or confirm these flags, scoped to the intended Preview deployment (avoid affecting other environments; record any Preview-scope changes and prior nonsecret values):
```dotenv
DJANGO_SETTINGS_MODULE=config.settings_production
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=False
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=False
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
MDC_CATALOG_SYNC_ENABLED=False
MDC_CATALOG_AUTO_SYNC_ENABLED=False
MDC_DEMO_API_ENABLED=False
```
Preserve valid secret, database, host and runtime settings. Keep the configurable security implementation intact. Retain Vercel Deployment Protection; approved fresh bypass credential may be used via x-vercel-protection-bypass, never as an MDC Bearer token. Never print/export/commit credentials. Verify anonymous requests are denied at Vercel and approved clients can reach Django without MDC Authorization or actor header. Do not enable unprotected lifecycle writes.

## Step 3 — Deploy
Use existing project, Preview only, mdc-catalog/ upload root, Python 3.12, existing WSGI entry point. Record exact source SHA, URL, deployment ID, build and runtime status. No --prod, alias changes, promotion, new project, broad code fixes, or GitLab push. On failure inspect actual error; report necessary code fixes separately.

## Step 4 — Live acceptance
Use existing M6 Postman package or equivalent automated requests. Set base_url to exact protected Preview, automatic_sync_enabled=false, concurrency_required=true. No MDC Bearer or actor header; approved Vercel bypass separately. Use unique disposable provider and offering IDs only; never modify real providers.

- Verify health, filters, and a standalone canonical spur-gear search (automatic-mode-only collection assertions skip when false); record actual baseline results, expected known catalogue matches. Search must not be presented as authoritative synchronized discovery.
- Confirm disposable provider absent; validate publication (valid and invalid payloads); register first offering; GET provider and capture strong ETag; list offerings; PATCH provider and verify updated state.
- Add second offering in same category with distinct ID; GET both; PATCH one; verify sibling unchanged; test whole-map replacement and optional attribute removal.
- Verify duplicate ID conflict (409), invalid input (400), missing ETag (428), stale ETag (412), successful current ETag updates. Use X-MDC-If-Match only if necessary for known Vercel intermediary behavior; canonical If-Match remains supported.
- DELETE second offering with current ETag; confirm 404 and sibling remains; DELETE provider with latest ETag; verify provider, offering list, and both offerings absent. Cleanup mandatory; inspect committed state before retrying ambiguous mutations. Do not blindly replay registration.
- Expected successful statuses: GET/validation/PATCH/DELETE 200, creates 201, absent resources 404. With sync off expect accepted/sync_pending/pending receipts; retained redacted audit/outbox history is expected, not a failure. Verify database/operational cleanup using safe read-only evidence. No Fuseki writes, sync or recovery commands.

## Step 5 — Final verification and rollback
Confirm complete lifecycle, no MDC Bearer/actor requirement, ETag enforcement, disposable cleanup, no real provider changes, no Fuseki changes, original Production alias/deployment and discovery still working. Leave successful protected Preview available for Postman/Marketplace tests. Stage 1 does not establish immediate semantic visibility; that is Stage 2. If blocked, stop unsafe actions, preserve evidence, identify minimal operator action; do not modify Production. Record how to retire failed Preview and restore any changed Preview settings without altering Production; no blind database restoration.

## Step 6 — Mandatory report and Git workflow
All new Phase 4 task prompts live in `mdc-catalog/docs/prompts_phase4/`; all new reports live in `mdc-catalog/docs/reports_phase4/`. Do not use the older docs/phase4 location for this report.

Write `mdc-catalog/docs/reports_phase4/01_MDC_Stage1_Provider_Lifecycle_Demo_Report.md` on branch `phase4/stage1-provider-lifecycle-demo`. Base the report branch on current origin/main including the prompt; use a clean worktree and preserve unrelated local changes. If branch exists, inspect it and safely reuse or choose a distinct branch. Stage ONLY the report, commit `docs: record Stage 1 MDC provider lifecycle demo validation`, push to GitHub, no force push or merge. Publish even if BLOCKED/PARTIAL. Do not commit secrets or test exports.

Report: verdict PASS/PARTIAL/BLOCKED; exact deployed source and Preview URL/ID; verified database identity and migrations; nonsecret flags; protection and no-Bearer/no-actor evidence; full endpoint matrix with redacted status/response and request/assertion/failure totals; publication and cleanup evidence; Production preservation; remaining Stage 2 prerequisites; Postman instructions; rollback; VERIFIED/INFERRED/NOT VERIFIED distinction.

Final Codex response: verdict, source SHA, Preview URL and ID, confirmed Neon database/migrations, auth status, endpoint results and totals, cleanup, Production unchanged confirmation, report path, branch, commit SHA and direct GitHub report link, blockers. Stop after Stage 1. No Stage 2 or Production promotion.
