# Codex prompt — P3.4 Provider Lifecycle API Validation

Work on the existing local checkout only. This milestone is **API validation**, not UI development and not Marketplace integration.

## Repository

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Project root:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

## Objective

Run the committed P3.4 validation script against the deployed MDC API and return a concise evidence report.

Primary script:

```text
mdc-catalog/scripts/p34_provider_lifecycle_validation.py
```

Phase report:

```text
mdc-catalog/docs/Phase_3/04_mdc_v1_p34_provider_lifecycle_api_validation.md
```

## Important constraints

1. Do **not** build any UI or frontend.
2. Do **not** integrate with the Marketplace.
3. Do **not** change the API contract.
4. Do **not** run Fuseki synchronization in P3.4.
5. Do **not** run `sync_service_discovery_catalogue`.
6. Keep Vercel `MDC_CATALOG_SYNC_ENABLED=False`.
7. Do **not** expose, echo, print, commit, or paste:
   - `MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN`;
   - `DATABASE_URL`;
   - Fuseki credentials;
   - Django secrets.
8. Do **not** modify `.env` unless absolutely required to use an already-known local value, and never print its secret contents.
9. Do **not** create Git commits or push anything.
10. Do **not** edit application code. If the validation exposes a reproducible backend/script defect, stop and report the exact failing step and safe response metadata so ChatGPT can review/fix it in GitHub.
11. Do not delete any provider, offering, publication, sync event, Neon database, or Fuseki data.
12. The P3.4 controlled provider is intentional pilot data and must remain after the run for P3.5.

## Current accepted baseline

P3.3 is complete. Production alias:

```text
https://maasai-mdc-v1.vercel.app
```

Canonical API:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Trusted lifecycle API:

```text
POST  /api/provider-publication/validation
POST  /api/provider-publication
GET   /api/providers/{provider_id}
PATCH /api/providers/{provider_id}
GET   /api/providers/{provider_id}/offerings
POST  /api/providers/{provider_id}/offerings
GET   /api/offerings/{offering_id}
PATCH /api/offerings/{offering_id}
```

No `/api/v1` partner contract.

P3.4 controlled identities:

```text
provider_id = p34_api_validation_provider
initial offering = p34_api_validation_provider_precision_metal_parts
second offering  = p34_api_validation_provider_precision_gears
```

P3.4 intentionally leaves new publication/outbox work in `sync_pending`/`pending` for P3.5.

## Procedure

### 1. Synchronize local Git checkout

From repository root:

```powershell
cd C:\Users\Elahi\Desktop\mdc_v1
git status --short
git pull --ff-only
```

If there are unexpected local modifications, do not discard them. Report them and continue only if they do not affect the P3.4 files.

Then:

```powershell
cd mdc-catalog
```

### 2. Confirm the lifecycle token exists without printing it

Use a boolean-only check, for example:

```powershell
if ($env:MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN) { "PASS lifecycle token present" } else { "FAIL lifecycle token missing" }
```

If missing, stop and report `P3.4 BLOCKED: lifecycle token not present locally`. Do not retrieve or print the production token by unsafe means.

### 3. Syntax-check the validation script

```powershell
& '..\.venv\Scripts\python.exe' -m py_compile scripts\p34_provider_lifecycle_validation.py
```

This must complete successfully.

### 4. Run the real deployed P3.4 validation

```powershell
& '..\.venv\Scripts\python.exe' scripts\p34_provider_lifecycle_validation.py
```

Do not suppress output. Capture the complete non-secret PASS/FAIL output.

The script intentionally performs controlled writes against the deployed lifecycle API. It must not trigger semantic synchronization.

### 5. Check Git state

```powershell
git status --short
```

The script should not modify tracked files. Report whether the worktree is clean.

## Expected successful areas

The run should prove:

- health and catalog filters return `200`, contract `1.0`;
- anonymous lifecycle validation is rejected `401`;
- invalid provider validation returns `400`, `valid=false`;
- valid provider validation returns `200`, `valid=true`;
- write without actor is rejected `400`;
- anonymous provider read is rejected `401`;
- controlled provider registration succeeds `201` or safely reuses an existing controlled provider after `409`;
- duplicate provider is rejected `409`;
- provider GET returns ETag;
- provider PATCH without precondition is rejected `428`;
- provider PATCH with current ETag succeeds `200`;
- stale provider ETag is rejected `412`;
- initial offering is listed;
- second offering creation succeeds `201` or safely reuses it after `409`;
- duplicate offering is rejected `409`;
- offering GET returns ETag;
- offering PATCH without precondition is rejected `428`;
- offering PATCH with current ETag succeeds `200`;
- stale offering ETag is rejected `412`;
- final offering list contains both controlled offerings;
- final script marker is `P3.4 PROVIDER LIFECYCLE API VALIDATION: PASS`.

## Failure handling

If any step fails:

- do not retry destructive operations;
- do not delete the controlled provider;
- do not run synchronization;
- do not modify code;
- report the failing HTTP status, safe error code/message, and step name;
- never include bearer tokens, DB URLs/passwords, or Fuseki credentials.

## Required final response

Return exactly this structured report, populated from the real run:

```text
# P3.4 PROVIDER LIFECYCLE API VALIDATION REPORT

## 1. Local gate
- git pull/status: PASS/FAIL
- lifecycle token present: PASS/FAIL
- script syntax check: PASS/FAIL

## 2. Public/trusted boundary
- health 200 + contract 1.0: PASS/FAIL
- catalog filters 200 + contract 1.0: PASS/FAIL
- anonymous validation 401: PASS/FAIL
- invalid validation 400 / valid=false: PASS/FAIL
- valid validation 200 / valid=true: PASS/FAIL
- missing actor write 400: PASS/FAIL
- anonymous provider read 401: PASS/FAIL

## 3. Provider lifecycle
- registration/reuse: PASS/FAIL + status
- duplicate provider 409: PASS/FAIL
- trusted GET + ETag: PASS/FAIL
- missing precondition 428: PASS/FAIL
- current ETag PATCH 200: PASS/FAIL
- ETag changed: PASS/FAIL
- stale ETag 412: PASS/FAIL

## 4. Offering lifecycle
- initial offering listed: PASS/FAIL
- second offering creation/reuse: PASS/FAIL + status
- duplicate offering 409: PASS/FAIL
- offering GET + ETag: PASS/FAIL
- missing precondition 428: PASS/FAIL
- current ETag PATCH 200: PASS/FAIL
- ETag changed: PASS/FAIL
- stale ETag 412: PASS/FAIL
- final list contains both offerings: PASS/FAIL

## 5. Final script result
- tests_passed: <count if available>
- tests_failed: <count if available>
- final marker: PASS/FAIL
- semantic sync executed: NO
- tracked worktree changes from validation: NONE / describe

## 6. Final gate
P3.4 PROVIDER LIFECYCLE API VALIDATION: PASS/FAIL
```
