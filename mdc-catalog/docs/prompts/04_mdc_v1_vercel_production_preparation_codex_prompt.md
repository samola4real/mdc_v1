# Codex Task 04 — MDC v1 Vercel Production Preparation

## Recommended Codex configuration

Use:

- **Model / intelligence:** GPT-5.6 Sol
- **Reasoning:** Medium
- Increase to **High only temporarily** for a concrete deployment-layout/runtime conflict.
- Do not use Ultra / Extra-High reasoning.

Keep this task tightly scoped to **Milestone M5** and the available Codex 5-hour window.

---

## Context

Git repository root:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

MDC project:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

Agreed plan:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\01_mdc_v1_harmonization_and_release_plan.md
```

Completed milestone reports:

```text
docs\Phase_2\02_mdc_v1_code_test_data_harmonization_report.md
docs\Phase_2\03_mdc_v1_clean_git_baseline_report.md
docs\Phase_2\04_mdc_v1_public_api_contract_stabilization_report.md
```

Current public API contract:

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

Compatibility aliases remain:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Legacy/write/detail endpoints remain only under `/api/...`.

Current M4 commit:

```text
d75dc7b feat: stabilize MDC v1 public API contract
```

Current verified baseline:

```text
Full suite:
399 run
386 passed
0 failed
13 skipped

Focused service-discovery:
230 run
225 passed
0 failed
5 skipped
```

The current service-discovery runtime supports:

```text
remote Fuseki
    -> fallback to local RDFLib
    -> fallback to harmonized YAML
```

External Fuseki hosting and production database work are deliberately deferred.

---

# Current Vercel Guidance to Respect

Before implementing, verify current official Vercel documentation if internet access is available.

Important current assumptions to verify:

1. Vercel added **zero-configuration Django support in April 2026**.
2. Vercel can detect Django via `manage.py` and the configured WSGI/ASGI application.
3. Do **not** add an old-style `/api/index.py` launcher or complex redirects merely because older Vercel tutorials used them.
4. The current Vercel Python runtime supports Python **3.12, 3.13, and 3.14**, with 3.12 currently documented as the default.
5. Python version can be selected via `.python-version` or `pyproject.toml`.
6. Python dependencies can be supplied with `requirements.txt` or `pyproject.toml`.
7. Python function bundles have size limits; exclude unnecessary development files only when needed.
8. Vercel is serverless/ephemeral. Do not rely on repository-file writes for durable provider publication.

Official references:

```text
https://vercel.com/changelog/zero-configuration-django-support
https://vercel.com/docs/functions/runtimes/python
https://vercel.com/templates/backend/django-hello-world
https://vercel.com/docs/functions/limitations
https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
```

Prefer the **simplest currently supported Django deployment pattern**.

---

# Precondition — Preserve M4 Baseline

Before changes run:

```powershell
git status
git log -2 --oneline
git branch --show-current
git remote -v
```

Expected current branch:

```text
main
```

Expected latest commit:

```text
d75dc7b feat: stabilize MDC v1 public API contract
```

If `d75dc7b` has not yet been pushed and the working tree is clean, it is acceptable to push the existing M4 baseline commit to:

```text
origin/main
```

before making M5 changes.

Do not automatically push the new M5 commit.

---

# Objective

Complete **Milestone M5 — Vercel Production Preparation**.

Prepare the current Django/DRF backend so it can be deployed safely to Vercel in M6.

M5 must address:

```text
production settings
environment variables
Vercel-compatible project layout
runtime/dependencies
CORS/hosts/HTTPS settings
demo/write endpoint safety
runtime data availability
deployment checks
tests
```

M5 must **not actually create/deploy a Vercel project**.

---

# Critical Scope Decisions

## Do now

- make Django production-configurable;
- prepare repository packaging for Vercel;
- make the canonical read/search API safe to expose in a pilot;
- disable demo and file-backed provider-publication mutation in production;
- preserve RDFLib/YAML search fallback;
- verify production settings with `check --deploy`.

## Defer

Do not implement:

- production database;
- durable provider-publication persistence;
- authentication/API keys;
- rate limiting;
- external Fuseki hosting;
- request-history persistence;
- OpenAPI modernization unless absolutely required for deployment;
- major architecture refactoring.

These belong to later milestones.

---

# Step 1 — Inspect Current Deployment-Relevant Structure

Inspect:

```text
mdc-catalog/
mdc-catalog/backend/manage.py
mdc-catalog/backend/config/settings.py
mdc-catalog/backend/config/settings_local.py
mdc-catalog/backend/config/wsgi.py
mdc-catalog/backend/config/asgi.py
mdc-catalog/backend/config/urls.py
mdc-catalog/requirements/
mdc-catalog/.env.example
mdc-catalog/data/
mdc-catalog/.gitignore
```

Also inspect any existing:

```text
requirements.txt
pyproject.toml
.python-version
vercel.json
manage.py
```

at `mdc-catalog/` root.

Do not assume they are absent.

---

# Step 2 — Resolve the Vercel Project Root / manage.py Layout Pragmatically

The intended Vercel project root should preferably be:

```text
mdc-catalog/
```

because required runtime data lives under:

```text
mdc-catalog/data/
```

while Django currently has:

```text
mdc-catalog/backend/manage.py
```

Determine the **minimum safe change** that allows current Vercel Django detection to work.

Preferred order:

1. Use current zero-config Django support if it can detect this layout.
2. If Vercel requires `manage.py` at the project root, add a **small root-level Django launcher/shim** that delegates to the existing backend configuration without moving the Django project.
3. Add custom `vercel.json` routing/entrypoints only if current Vercel behavior genuinely requires it.
4. Do not move `data/` or perform a broad repository restructure just for deployment.

If a root-level `manage.py` is added, preserve:

```text
backend/manage.py
```

for the existing local workflow unless there is strong evidence it is redundant.

Document the final Vercel root clearly.

---

# Step 3 — Production Settings

Prefer a clean production settings layer that does **not break local/test defaults**.

A minimal approach may be:

```text
backend/config/settings.py              # existing local/base behavior
backend/config/settings_local.py        # local/demo overrides
backend/config/settings_production.py   # production/Vercel overrides
```

Use the existing repository structure if another minimal design is cleaner.

Production settings must address at minimum:

```text
SECRET_KEY
DEBUG
ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS
SECURE_PROXY_SSL_HEADER
SESSION_COOKIE_SECURE
CSRF_COOKIE_SECURE
SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS
```

Requirements:

- `DEBUG=False` in production;
- real `SECRET_KEY` must come from environment;
- never commit a production secret;
- fail clearly or safely if required production secret is absent;
- allow Vercel hostnames and configured custom hosts;
- CORS origins must be environment-driven;
- preserve localhost/local development behavior in non-production settings.

Do not hardcode the future Marketplace production URL if it is not yet known.

---

# Step 4 — Environment Variable Parsing

Use small, testable parsing helpers where appropriate rather than duplicated ad-hoc parsing.

Recommended variables to evaluate:

```text
DJANGO_SETTINGS_MODULE
DJANGO_SECRET_KEY
DJANGO_ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS

MDC_DEMO_API_ENABLED
MDC_PROVIDER_PUBLICATION_ENABLED

SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT
FUSEKI_TIMEOUT_SECONDS
```

Add only variables genuinely used by the current code.

For list settings, use a clear comma-separated convention.

Examples in `.env.example` must be placeholders only.

Do not include real secrets.

---

# Step 5 — Protect Non-Public/Mutation Endpoints in Production

Canonical public v1 endpoints should remain available:

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

Compatibility read/search aliases may remain.

Production must not expose mutable demo/file-backed APIs by default.

At minimum:

```text
/api/demo/*
/api/provider-publication
```

should be disabled or not routed when production flags are false.

Preferred environment flags:

```text
MDC_DEMO_API_ENABLED=False
MDC_PROVIDER_PUBLICATION_ENABLED=False
```

Preserve local/test behavior through explicit local defaults.

Add focused tests proving:

- production mode does not expose demo routes;
- production mode does not expose file-backed provider publication;
- canonical public v1 search/read routes remain available.

Do not redesign provider publication persistence.

---

# Step 6 — Dependencies for Vercel

Inspect:

```text
requirements/base.txt
requirements/locked.txt
requirements/dev.txt
```

Create the minimum Vercel-recognized runtime dependency declaration at the chosen Vercel project root.

Preferred simple approach if compatible:

```text
requirements.txt
```

that delegates to the existing runtime dependency file, e.g.:

```text
-r requirements/base.txt
```

or uses the appropriate pinned runtime file if that is demonstrably safer.

Do not deploy dev/test-only dependencies unnecessarily.

Do not duplicate dependency lists without reason.

---

# Step 7 — Python Runtime

Current Vercel Python documentation should be treated as authoritative.

If current supported versions are:

```text
3.12
3.13
3.14
```

prefer **Python 3.12** for this first pilot unless dependency evidence supports another choice better.

Add at project root:

```text
.python-version
```

only if appropriate.

Before finalizing:

1. inspect the project's current Python/dependency compatibility;
2. check whether Python 3.12 is installed locally, e.g. using Windows Python launcher;
3. if available, run at least a smoke/check under Python 3.12;
4. if unavailable, do not pretend local 3.12 verification occurred—record this as a deployment-time compatibility risk.

Do not upgrade Django or unrelated packages during M5 unless required for Python 3.12 compatibility.

---

# Step 8 — Runtime Data and File Paths

The deployed search must still be able to read:

```text
data/curated/service_discovery/providers/
data/generated/service_discovery/mdc_service_discovery_catalog.ttl
```

Inspect all relevant path calculations.

Confirm they work when the Vercel project root is:

```text
mdc-catalog/
```

and the Django code is under:

```text
backend/
```

Do not rely on current working directory assumptions when robust absolute paths based on Django settings/module paths are already available.

Do not introduce runtime writes to these files.

---

# Step 9 — Fuseki Behavior for M5

Do not provision Fuseki.

Preserve current behavior:

```text
external Fuseki configured
    -> try Fuseki
else/failure
    -> RDFLib
    -> YAML fallback
```

Production settings should allow:

```text
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT
```

to remain empty during the first pilot.

If it is empty, canonical search must still function through current fallback behavior.

Add no new RDF-store technology.

---

# Step 10 — .env.example

Populate:

```text
mdc-catalog/.env.example
```

with concise placeholder documentation.

Include only relevant variables.

Example format:

```dotenv
# Django
DJANGO_SETTINGS_MODULE=config.settings_production
DJANGO_SECRET_KEY=replace-me
DJANGO_ALLOWED_HOSTS=.vercel.app
CORS_ALLOWED_ORIGINS=https://marketplace.example.org
CSRF_TRUSTED_ORIGINS=https://marketplace.example.org

# MDC production safety
MDC_DEMO_API_ENABLED=False
MDC_PROVIDER_PUBLICATION_ENABLED=False

# Optional Fuseki
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT=
FUSEKI_TIMEOUT_SECONDS=5
```

Adjust names to final code.

Do not commit actual `.env`.

---

# Step 11 — Vercel-Specific Configuration: Keep It Minimal

Because Vercel now supports zero-configuration Django, do not create `vercel.json` merely out of habit.

Only add it when it solves a demonstrated need, such as:

- project layout not detected;
- required function include/exclude behavior;
- bundle-size control.

If `vercel.json` is unnecessary, explicitly report:

```text
No vercel.json required for current zero-config Django deployment.
```

Likewise do not create `api/index.py` if Django zero-config detection is sufficient.

---

# Step 12 — Local Production Smoke Verification

Run normal verification:

```powershell
python manage.py check
python manage.py test -v 2
```

Use the repository's established local command/venv.

Also run focused service-discovery tests.

Then run Django deployment checks against the production settings.

Example concept:

```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings_production"
$env:DJANGO_SECRET_KEY="<temporary-local-test-secret>"
$env:DJANGO_ALLOWED_HOSTS=".vercel.app,localhost"
$env:MDC_DEMO_API_ENABLED="False"
$env:MDC_PROVIDER_PUBLICATION_ENABLED="False"

python manage.py check --deploy
```

Use a temporary test secret only in the local process/environment.

Do not store it.

Record every remaining warning.

Classify each warning:

```text
fixed
acceptable_for_preview
must_fix_before_M6
```

M5 should not be marked ready if critical deployment-security warnings remain unexplained.

---

# Step 13 — Production Route Safety Tests

Add focused tests for production settings/routing.

At minimum prove:

```text
/api/v1/health                         available
/api/v1/catalog/filters                available
/api/v1/service-discovery/search       available

/api/demo/*                            unavailable by default in production
/api/provider-publication              unavailable by default in production
```

Preserve local development/test access where intentionally required.

---

# Step 14 — Optional Vercel Build Detection Check

If Vercel CLI is already installed and can perform a local build/detection check without requiring destructive setup or deployment, use it.

Do not:

- install large unrelated tooling solely for this;
- log into Vercel;
- create a Vercel project;
- deploy.

If no local Vercel build check is possible, record:

```text
Vercel platform detection not locally verified; M6 will perform first platform build.
```

This alone does not necessarily block M6 if the repository matches current official Django requirements.

---

# Step 15 — Git Commit

After all M5 tests pass:

```powershell
git status
git diff
git diff --cached
```

Create one local commit.

Recommended:

```text
chore: prepare MDC v1 for Vercel
```

Do not automatically push this M5 commit.

---

# Out of Scope

Do not:

- create/import a Vercel project;
- deploy to Vercel;
- configure a custom domain;
- add production DB;
- modify database architecture;
- implement durable provider publication;
- add API keys/authentication;
- add throttling/rate limiting;
- provision external Fuseki;
- change the canonical M4 API contract;
- remove legacy APIs;
- redesign H1-H9 matching;
- rewrite unrelated documentation.

---

# Required Deliverable

Create:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\05_mdc_v1_vercel_production_preparation_report.md
```

The report remains local/ignored.

Include:

## 1. M5 status

Use:

```text
completed
partially completed
blocked
```

## 2. Final deployment architecture for M6

State:

```text
Vercel project root
Django manage.py used by Vercel
settings module
WSGI/ASGI entrypoint
Python version
dependency file
vercel.json required? yes/no
api/index.py required? yes/no
```

## 3. Files changed

```text
Path | Change | Reason
```

## 4. Production settings

Summarize environment-driven settings and security behavior.

## 5. Environment variables

Table:

```text
Variable | Required | Secret | Purpose | Example placeholder
```

## 6. Production endpoint exposure

Table:

```text
Endpoint | Production status | Reason
```

## 7. Runtime data/fallback

Confirm:

- harmonized provider YAML availability;
- generated RDF availability;
- Fuseki optional;
- RDFLib/YAML fallback works.

## 8. Vercel/Python compatibility

State:

- current official Vercel Python versions verified;
- selected version;
- whether local verification under that version was possible;
- any bundle/layout risk.

## 9. Verification

Include exact commands and counts:

```text
manage.py check
full suite
focused service-discovery
production check --deploy
production route safety tests
```

## 10. Remaining M6 prerequisites

Only concrete tasks requiring actual Vercel account/platform access.

## 11. Git commit

```text
hash
message
branch
```

## 12. M6 readiness

End with exactly one:

```text
READY_FOR_M6
```

or:

```text
NOT_READY_FOR_M6
```

If not ready, state exact blockers.

---

# Final Console Response

Return only:

1. M5 status
2. Vercel project root
3. selected Python version
4. whether zero-config Django is used
5. production route safety status
6. `check --deploy` result
7. full test result
8. focused service-discovery result
9. local commit hash/message
10. `READY_FOR_M6` or `NOT_READY_FOR_M6`
11. report path

Do not deploy and do not start M6 automatically.
