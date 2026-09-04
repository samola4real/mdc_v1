# Codex Task 05 — MDC v1 First Vercel Deployment and Public API Verification

## Recommended Codex configuration

Use:

- **Model / intelligence:** GPT-5.6 Sol
- **Reasoning:** Medium
- Increase to **High only temporarily** for an actual Vercel build/runtime failure that requires non-trivial diagnosis.
- Do not use Ultra / Extra-High reasoning.

Keep this task tightly scoped to **Milestone M6** and the available Codex 5-hour window.

---

# Context

Git repository root:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Vercel project root:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

Agreed milestone plan:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\01_mdc_v1_harmonization_and_release_plan.md
```

Completed reports:

```text
docs\Phase_2\02_mdc_v1_code_test_data_harmonization_report.md
docs\Phase_2\03_mdc_v1_clean_git_baseline_report.md
docs\Phase_2\04_mdc_v1_public_api_contract_stabilization_report.md
docs\Phase_2\05_mdc_v1_vercel_production_preparation_report.md
```

Current M5 baseline:

```text
commit: 200a951
message: chore: prepare MDC v1 for Vercel
branch: main
```

Current canonical public API contract:

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

Compatibility aliases intentionally remain:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Not part of the canonical partner API:

```text
POST /api/catalog/search
POST /api/provider-publication
GET  /api/providers/<provider_id>
GET  /api/offerings/<offering_id>
/api/demo/*
```

M5 production safety behavior:

```text
/api/demo/*                 -> unavailable by default in production
/api/provider-publication   -> disabled by default in production
```

Current service-discovery backend order:

```text
external Fuseki, if configured
        ↓
local RDFLib over bundled generated Turtle
        ↓
harmonized YAML fallback
```

External Fuseki is intentionally not required for this first deployment.

---

# Current Vercel Facts to Follow

Use current official Vercel behavior rather than old tutorials.

Current verified assumptions:

1. Django has current zero-configuration support on Vercel.
2. Vercel detects Django from `manage.py` and derives the WSGI application.
3. Do not add `api/index.py` or old redirect-based `vercel.json` unless an actual platform failure demonstrates a need.
4. The selected project Python runtime is `3.12` via `.python-version`.
5. Runtime dependencies are declared through root `requirements.txt`.
6. Environment-variable changes require redeployment before they affect a deployment.
7. Vercel environment variables can be scoped separately to Preview and Production.
8. Use a current Vercel CLI for current Django/project behavior.

Official references:

```text
https://vercel.com/changelog/zero-configuration-django-support
https://vercel.com/docs/frameworks/full-stack/django
https://vercel.com/docs/functions/runtimes/python
https://vercel.com/docs/projects/environment-variables
https://vercel.com/docs/functions/limitations
```

Do not modify application architecture merely to match an outdated Vercel tutorial.

---

# Objective

Complete **Milestone M6 — First Vercel Pilot Deployment**.

The goal is to:

1. safely preserve/push the M5 code baseline;
2. authenticate/link the local `mdc-catalog/` directory to Vercel;
3. create or select the appropriate Vercel project;
4. configure Preview and Production environment variables;
5. perform a **Preview deployment first**;
6. inspect build/runtime behavior under Python 3.12;
7. smoke-test the canonical API;
8. only after Preview succeeds, perform the **Production deployment**;
9. repeat API smoke tests against Production;
10. record the exact public base URL partners will use;
11. leave provider publication and demo functionality disabled;
12. make no unrelated feature changes.

---

# Deployment Safety Rules

## Preview first

Do not deploy directly to Production as the first platform test.

Use:

```text
Preview deployment
        ↓
build succeeds
        ↓
runtime smoke tests pass
        ↓
Production deployment
```

If Preview fails, diagnose it there first.

## Minimal-change rule

If Vercel build/runtime fails:

1. identify the actual error from Vercel logs;
2. make the smallest justified repository/configuration fix;
3. add/update a local test when appropriate;
4. rerun local verification;
5. commit that specific deployment fix;
6. redeploy Preview.

Do not broadly restructure Django, APIs, data, or H1-H9.

## No database work

Do not add Postgres, SQLite persistence, Redis, object storage, or another database in M6.

## No Fuseki provisioning

Do not provision an external Fuseki service in M6.

The first deployed search should prove the current bundled RDFLib/YAML fallback works.

---

# Step 1 — Verify and Preserve the M5 Baseline

From Git root:

```powershell
git status
git branch --show-current
git log -3 --oneline
git remote -v
```

Expected latest commit:

```text
200a951 chore: prepare MDC v1 for Vercel
```

Expected branch:

```text
main
```

If the working tree is clean and `200a951` has not yet been pushed to `origin/main`, push the existing baseline before deployment:

```powershell
git push origin main
```

Do not force-push.

If remote differs unexpectedly, inspect before proceeding.

---

# Step 2 — Use a Current Vercel CLI

The locally installed global CLI may be outdated.

Prefer:

```powershell
npx vercel@latest --version
```

rather than relying on the global `vercel` binary.

Then check authentication:

```powershell
npx vercel@latest whoami
```

## If authenticated

Continue.

## If not authenticated

Run the normal Vercel login flow:

```powershell
npx vercel@latest login
```

If login requires a browser/device approval that Codex cannot complete autonomously:

- stop at the authentication boundary;
- clearly tell the user the exact one-time action required;
- do not make speculative code changes;
- after authentication is available, continue the same M6 task.

Authentication alone is not an application blocker.

---

# Step 3 — Inspect Existing Vercel Link/Project State

From:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

inspect whether the directory is already linked:

```text
.vercel/
```

and use current CLI project/link commands as appropriate.

Determine whether an MDC project already exists in the user's Vercel account.

Preferred project name if a new project must be created:

```text
maasai-mdc-v1
```

If a clearly matching existing MDC project exists, use it instead of creating a duplicate.

Do not create multiple trial projects.

The Vercel project root must correspond to:

```text
mdc-catalog/
```

not the parent `mdc_v1/` Git root.

---

# Step 4 — Link/Create the Vercel Project

Use current Vercel CLI behavior.

Link the local:

```text
mdc-catalog/
```

directory to the selected/new project.

Verify the resulting project configuration.

Do not commit:

```text
.vercel/
```

It should remain local/ignored.

If `.vercel/` is not already ignored, safely add the appropriate ignore rule.

---

# Step 5 — Configure Environment Variables

Configure at least **Preview and Production**.

## Required

```text
DJANGO_SETTINGS_MODULE=config.settings_production
DJANGO_SECRET_KEY=<strong generated secret>
DJANGO_ALLOWED_HOSTS=.vercel.app
MDC_DEMO_API_ENABLED=False
MDC_PROVIDER_PUBLICATION_ENABLED=False
```

## Optional/currently empty

```text
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT=
FUSEKI_TIMEOUT_SECONDS=5
```

## Browser CORS

The final MaaSAI Marketplace production origin is not yet known.

Therefore for this first backend deployment:

```text
CORS_ALLOWED_ORIGINS=
CSRF_TRUSTED_ORIGINS=
```

or omit them if production settings safely default to empty.

Do **not** use:

```text
CORS_ALLOW_ALL_ORIGINS=True
```

merely to make testing easier.

Server-to-server and curl smoke tests do not require browser CORS.

When the actual Marketplace frontend origin is known, it can be added explicitly later.

---

# Step 6 — Secret Handling

Generate a strong Django secret locally using Django/Python or an equivalent cryptographically secure method.

Do not:

- commit it;
- save it in the report;
- print the full value in the final console summary.

Store it only as Vercel environment configuration.

If separate Preview and Production secrets are easy to create, prefer separate secrets.

---

# Step 7 — First Preview Deployment

From `mdc-catalog/`, create a Preview deployment using the current CLI.

Do not use `--prod` yet.

Capture:

```text
deployment URL
build status
detected framework
detected manage.py
Python runtime/version
dependency installation
function build/bundle information if shown
```

Confirm Vercel is using the intended Django zero-config path and Python 3.12.

If the platform unexpectedly uses another Python version, capture the build evidence before making changes.

Do not assume success because the build command exits zero; test the deployed API.

---

# Step 8 — Diagnose Preview Failures Pragmatically

If the Preview build or runtime fails, inspect Vercel logs.

Classify failure as one of:

```text
project-root detection
Django/manage.py detection
Python runtime
dependency installation
module import/path
environment variable
runtime-data packaging
Django allowed-host/security setting
serverless bundle/size
application defect
Vercel platform/account issue
```

Only make code/configuration changes that correspond directly to observed evidence.

### Examples

If `manage.py` is not detected:

- verify current Vercel Django docs;
- first try supported project/root configuration;
- add a root shim or `vercel.json` only if truly necessary.

If runtime data is missing:

- verify the bundle contains required `data/` paths;
- fix packaging/path inclusion minimally.

If Python 3.12 exposes an actual dependency incompatibility:

- identify the exact dependency;
- make the smallest compatible dependency change;
- rerun tests.

Do not replace RDFLib/Fuseki architecture because of deployment configuration errors.

---

# Step 9 — Preview API Smoke Tests

Once Preview is deployed, test externally using the deployment URL.

## Health

```http
GET /api/v1/health
```

Expected:

```text
HTTP 200
```

and valid MDC health JSON.

## Filters

```http
GET /api/v1/catalog/filters
```

Expected:

```text
HTTP 200
```

with controlled catalogue values.

## Service discovery

Build one **valid request from the current repository tests/registry**, not from memory.

Test:

```http
POST /api/v1/service-discovery/search
Content-Type: application/json
```

Expected:

```text
HTTP 200
search_executed = true
result_count/results according to current seed data
```

Confirm `status.search_engine`.

For the first deployment without external Fuseki, it should legitimately use a bundled fallback such as RDFLib or harmonized YAML.

## Compatibility search alias

Also verify:

```http
POST /api/service-discovery/search
```

with the same valid payload.

Expected:

```text
HTTP 200
```

## Production-safety routes on Preview production settings

Verify:

```text
/api/demo/...
```

is unavailable.

Verify a safe non-mutating request against:

```text
POST /api/provider-publication
```

does not result in successful file-backed publication when the flag is disabled.

Do not send a payload intended to mutate persistent provider data.

Expected disabled behavior should match current M5 tests, e.g. `403`.

---

# Step 10 — Inspect Preview Logs After Requests

After smoke tests inspect runtime/function logs for:

- import errors;
- missing data;
- warnings caused by filesystem assumptions;
- Django host errors;
- server exceptions;
- search fallback warnings;
- timeout issues.

Distinguish expected fallback warnings from actual failures.

Do not treat absence of Fuseki as an error for this pilot.

---

# Step 11 — Production Deployment Gate

Proceed to Production only if Preview satisfies all:

```text
[ ] build successful
[ ] Django zero-config detection successful
[ ] intended Python runtime verified or acceptable evidence recorded
[ ] /api/v1/health -> 200
[ ] /api/v1/catalog/filters -> 200
[ ] /api/v1/service-discovery/search -> 200
[ ] search uses valid RDFLib/YAML fallback without external Fuseki
[ ] compatibility search alias works
[ ] demo API disabled
[ ] provider publication disabled
[ ] no unexplained runtime 500 errors
```

If any critical item fails:

```text
NOT_READY_FOR_PRODUCTION
```

Do not force a Production deployment.

---

# Step 12 — Production Deployment

If Preview gate passes, deploy Production using the current Vercel CLI.

Capture the final production deployment URL.

Do not add a custom domain yet unless one is already configured automatically.

The default Vercel production domain is sufficient for M6.

---

# Step 13 — Production Smoke Tests

Repeat against the Production URL:

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
POST /api/service-discovery/search       # compatibility verification
```

Also verify:

```text
/api/demo/*                  disabled
/api/provider-publication    disabled
```

Record HTTP status and concise result for each.

---

# Step 14 — Partner-Facing API Information

At completion, clearly identify:

```text
MDC public base URL:
https://<actual-vercel-production-domain>
```

Official partner endpoints:

```text
GET  https://<actual-domain>/api/v1/health

GET  https://<actual-domain>/api/v1/catalog/filters

POST https://<actual-domain>/api/v1/service-discovery/search
```

Do **not** present legacy/detail/demo/write endpoints as the official partner contract.

State that browser-based Marketplace integration will additionally require the actual Marketplace origin to be added to:

```text
CORS_ALLOWED_ORIGINS
```

once that frontend URL is known.

---

# Step 15 — Git Handling for Any M6 Fixes

If no source-code changes were needed for deployment:

- do not create an empty application commit merely for deployment.

If M6 required a justified repository fix:

1. rerun local tests;
2. commit only that fix;
3. use an appropriate message such as:

```text
fix: support Vercel runtime deployment
```

4. push the fix to `origin/main` if required for the final production deployment.

Never force-push.

Do not commit `.vercel/` or secrets.

---

# Step 16 — Local Regression Verification If Code Changed

If any application/config/dependency code changed during M6, rerun:

```powershell
python manage.py check
python manage.py test -v 2
```

and the focused service-discovery suite before Production.

If no code changed, the M5 green baseline may be referenced, but external deployment smoke tests are still mandatory.

---

# Out of Scope

Do not:

- add a production database;
- enable provider publication;
- enable demo APIs;
- add authentication/API keys;
- add rate limiting;
- provision Fuseki;
- configure Marketplace CORS without knowing its actual URL;
- add a custom production domain unless already available;
- remove compatibility API routes;
- redesign the API contract;
- redesign H1-H9;
- add unrelated features;
- modernize OpenAPI warnings merely because they exist.

---

# Required Deliverable

Create:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\06_mdc_v1_first_vercel_deployment_report.md
```

This report remains local because `docs/` is ignored.

Include:

## 1. M6 status

Use one:

```text
completed
partially completed
blocked
```

## 2. Vercel project

```text
project name
project ID if useful/non-secret
local linked root
team/account scope
```

Do not expose tokens.

## 3. CLI/runtime

```text
CLI version used
Django detection
manage.py detected
Python version actually used by Vercel
dependency source
```

## 4. Environment variables

Table:

```text
Variable | Preview configured | Production configured | Value disclosure
```

For secrets write only:

```text
configured / not shown
```

Never include secret values.

## 5. Preview deployment

```text
Preview URL
build result
runtime result
```

## 6. Preview endpoint verification

Table:

```text
Method | Endpoint | HTTP status | Result
```

## 7. Production deployment

```text
Production URL
build result
runtime result
```

## 8. Production endpoint verification

Table:

```text
Method | Endpoint | HTTP status | Result
```

## 9. Search backend used

State actual observed:

```text
Fuseki
RDFLib
YAML fallback
```

and any warnings.

## 10. Production safety

Confirm:

```text
demo disabled
provider publication disabled
no secrets committed
docs remain untracked
```

## 11. Partner integration information

Provide exactly:

```text
Base URL
GET /api/v1/health
GET /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

## 12. Changes required during M6

List any repository changes and commit(s).

If none:

```text
No source-code changes required during deployment.
```

## 13. Remaining pilot limitations

Examples only if actually applicable:

```text
no external Fuseki
no production DB
no auth
Marketplace CORS origin not yet configured
```

## 14. Next-step recommendation

Do not automatically start another phase.

End with exactly one:

```text
MDC_V1_VERCEL_PILOT_DEPLOYED
```

or:

```text
MDC_V1_VERCEL_PILOT_BLOCKED
```

If blocked, state the exact blocker.

---

# Final Console Response

Return only:

1. M6 status
2. Vercel project name
3. Preview URL/result
4. Production URL/result
5. actual Python runtime
6. canonical health result
7. canonical filters result
8. canonical service-discovery result
9. observed search backend
10. demo/publication safety result
11. any code fix commit
12. partner base URL
13. `MDC_V1_VERCEL_PILOT_DEPLOYED` or `MDC_V1_VERCEL_PILOT_BLOCKED`
14. report path

Do not start database/Fuseki/auth work automatically.
