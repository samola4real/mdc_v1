# Codex Task 07 — Vercel Onboarding and M6.1 Deployment Verification

## Recommended Codex configuration

- Model: GPT-5.6 Sol
- Reasoning: Medium
- Increase to High only if a real Vercel/runtime blocker requires deeper investigation.

Do not redo M6.1 implementation. The code changes are already in GitHub and all focused + full local tests have passed.

---

# Context

Repository root:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Project root:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

Existing Vercel project:

```text
maasai-mdc-v1
```

Known Vercel project ID from the first deployment:

```text
prj_DekMQdOYuuH0A5yNsCkFmOC4uD9j
```

Known Vercel scope/team from the first deployment:

```text
mdc19
```

Production base URL:

```text
https://maasai-mdc-v1.vercel.app
```

Current M6.1 report:

```text
mdc-catalog/docs/Phase_2/09_mdc_v1_api_contract_rectification_report.md
```

Important: the user does not want to spend time setting up automatic GitHub -> Vercel deployment now. Manual/CLI deployment is acceptable for this milestone. Git integration can be learned/configured later.

A ChatGPT Vercel plugin is installed, but a direct plugin access check to the existing project returned 403 and no team list was visible. Therefore use the existing local Vercel CLI authentication/project link for this task. Do not spend time trying to repair ChatGPT plugin authorization unless it is trivially resolvable.

---

# Final API Decision

There is NO URL-versioned public API family.

Canonical stable routes are only:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

The following must remain unavailable:

```text
/api/v1/health
/api/v1/catalog/filters
/api/v1/service-discovery/search
```

API evolution uses:

```text
contract_version = "1.0"
```

Do not reintroduce `/api/v1/...`, `/api/v2/...`, or any other URL-versioned routes.

---

# M6.1 State Before This Task

Already completed in code and locally verified:

- stable `/api/...` canonical routes;
- `/api/v1/...` removed;
- `contract_version = "1.0"` implemented;
- public catalog-filter response shaping implemented;
- public service-discovery response shaping implemented;
- H1-H9 runtime preserved;
- provider publication remains production-disabled;
- PostgreSQL/Neon architecture documented only, not implemented;
- focused local tests passed;
- full local test suite passed.

Do not change code unless deployment reveals a genuine defect.

---

# Goal

Complete the remaining M6.1 deployment gate:

```text
verify Vercel project/auth/settings
        ↓
Preview deploy
        ↓
Preview smoke verification
        ↓
Production deploy
        ↓
Production smoke verification
        ↓
update 09 report to completed
```

---

# Step 1 — Synchronize and Inspect Local State

From:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

1. Run `git status`.
2. Pull `origin/main` if needed.
3. Confirm local HEAD matches current remote main.
4. Do not discard user changes if any exist. If unexpected local changes exist, stop and report them before deployment.

Then work from:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

---

# Step 2 — Verify Existing Vercel CLI Authentication

Use current CLI:

```powershell
npx vercel@latest whoami
```

Expected previously authenticated user from M6 was:

```text
samola4real-6623
```

If authentication is missing, use the normal Vercel CLI login flow and ask the user only when an interactive browser/login confirmation is genuinely required.

Do not create a second Vercel account/project.

---

# Step 3 — Verify Local Project Link

Inspect:

```text
.vercel/project.json
```

Confirm it points to the existing project:

```text
maasai-mdc-v1
```

and expected project ID:

```text
prj_DekMQdOYuuH0A5yNsCkFmOC4uD9j
```

If `.vercel/project.json` is missing or incorrect, relink this existing local project to the existing Vercel project using the CLI.

Do not create a new Vercel project.

Do not commit `.vercel/` metadata.

---

# Step 4 — Inspect Vercel Environment Configuration

Use Vercel CLI to inspect environment variable names/scopes without printing secret values.

Verify Preview and Production have the required runtime configuration.

Expected core variables include:

```text
DJANGO_SETTINGS_MODULE=config.settings_production
DJANGO_SECRET_KEY
DJANGO_ALLOWED_HOSTS
MDC_DEMO_API_ENABLED=False
MDC_PROVIDER_PUBLICATION_ENABLED=False
FUSEKI_TIMEOUT_SECONDS=5
```

The following may intentionally remain unset at this stage:

```text
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT
CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS
```

because external Fuseki is not configured and the Marketplace frontend origin is not yet finalized.

Do not expose secret values in console summaries or the report.

If a required variable is missing, add it only if its intended value is already known from the existing deployment/configuration. Do not invent secrets or frontend origins.

---

# Step 5 — Confirm Production Safety Before Deployment

Do not change these decisions:

```text
MDC_DEMO_API_ENABLED=False
MDC_PROVIDER_PUBLICATION_ENABLED=False
```

Do not provision or configure:

- PostgreSQL/Neon;
- external Fuseki;
- authentication;
- rate limiting;
- automatic GitHub -> Vercel deployment.

Those are outside this deployment gate.

---

# Step 6 — Preview Deployment

From the project root run:

```powershell
npx vercel@latest
```

Use the already-linked `maasai-mdc-v1` project.

Record:

- Preview deployment URL;
- deployment status;
- build/runtime errors if any.

If build fails, inspect Vercel build logs and fix only the genuine deployment defect. Do not refactor unrelated code.

---

# Step 7 — Preview API Verification

Test the actual Preview URL externally.

## Stable endpoints

Verify:

```text
GET /api/health
```

Expected:

- HTTP 200
- `contract_version = "1.0"`
- `status = "ok"`

Verify:

```text
GET /api/catalog/filters
```

Expected:

- HTTP 200
- `contract_version = "1.0"`
- harmonized external keys including:
  - `service_categories`
  - `part_families`
  - `part_types`
  - `materials`
  - `processes`
  - `certifications`

Verify:

```text
POST /api/service-discovery/search
```

Use a valid existing service-discovery request from the test suite or existing examples.

Expected:

- HTTP 200
- `contract_version = "1.0"`
- actual result(s) returned
- public response shape only
- H1-H9 runtime still operational

Do not require external Fuseki. RDFLib fallback is acceptable/expected while Fuseki is not configured.

## Removed URL-versioned routes

Confirm all return 404:

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

## Production-safety behavior on Preview

Confirm:

```text
/api/demo/* -> unavailable
POST /api/provider-publication -> 403
```

If any Preview gate fails, stop before Production and report/fix the exact issue.

---

# Step 8 — Production Deployment

Only after Preview passes, deploy Production:

```powershell
npx vercel@latest --prod
```

Do not create a new project/domain.

The canonical production base must remain:

```text
https://maasai-mdc-v1.vercel.app
```

---

# Step 9 — Production API Verification

Repeat the same verification against:

```text
https://maasai-mdc-v1.vercel.app
```

Verify:

```text
GET  /api/health                         -> 200
GET  /api/catalog/filters                -> 200
POST /api/service-discovery/search       -> 200
```

Confirm:

```text
contract_version = "1.0"
```

Confirm URL-versioned routes are gone:

```text
GET  /api/v1/health                      -> 404
GET  /api/v1/catalog/filters             -> 404
POST /api/v1/service-discovery/search    -> 404
```

Confirm safety:

```text
/api/demo/*                              -> unavailable
POST /api/provider-publication           -> 403
```

Inspect Vercel runtime logs after smoke tests and confirm there are no new error-level runtime failures caused by M6.1.

---

# Step 10 — Update M6.1 Report

Update the existing file:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\09_mdc_v1_api_contract_rectification_report.md
```

Do not create a second M6.1 report.

Add actual values for:

- local verification status;
- Preview deployment URL/status;
- Preview endpoint verification;
- Production deployment URL/status;
- Production endpoint verification;
- removed `/api/v1/...` verification;
- production safety verification;
- observed search backend/fallback behavior if available from runtime evidence;
- final Git/deployment commit(s).

If all gates pass, set:

```text
M6.1 status: completed
```

and end the report with exactly:

```text
READY_TO_UPDATE_PARTNER_API_DOCUMENT
```

If anything remains blocked, retain `partially completed` and end with:

```text
NOT_READY_TO_UPDATE_PARTNER_API_DOCUMENT
```

with the exact blocker.

---

# Step 11 — Git Handling

After successful Production verification:

1. review `git status` and diff;
2. commit the updated M6.1 report and only any genuine deployment fixes made during this task;
3. push to `origin/main`;
4. do not force-push;
5. do not commit secrets or `.vercel/` files.

Suggested report-only commit message:

```text
docs: complete M6.1 Vercel verification
```

If code fixes were genuinely required, use an appropriate implementation commit before the final report commit.

---

# Scope Restrictions

Do not:

- reintroduce `/api/v1/...`;
- add `/api/v2/...`;
- redesign H1-H9;
- evolve `/api/catalog/search`;
- enable provider publication;
- provision PostgreSQL/Neon;
- provision external Fuseki;
- add auth/rate limiting;
- configure automatic GitHub deployments;
- update the Marketplace PDF;
- start M7;
- create a new Vercel project.

---

# Final Console Response

Return only:

1. CLI authentication status
2. existing Vercel project-link status
3. Preview environment configuration status
4. Production environment configuration status
5. Preview deployment URL/status
6. Preview stable endpoint results
7. Preview `/api/v1/...` 404 results
8. Preview safety results
9. Production deployment status
10. production base URL
11. Production stable endpoint results
12. Production `/api/v1/...` 404 results
13. Production safety results
14. runtime error/log summary
15. report update status/path
16. Git commit hash/message
17. `READY_TO_UPDATE_PARTNER_API_DOCUMENT` or `NOT_READY_TO_UPDATE_PARTNER_API_DOCUMENT`

Do not start any next milestone automatically.
