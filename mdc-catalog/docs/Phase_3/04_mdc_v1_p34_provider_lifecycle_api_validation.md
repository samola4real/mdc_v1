# MDC v1 P3.4 — Provider Lifecycle API Validation

## Status

**IN PROGRESS.** P3.3 is complete. P3.4 validates the trusted provider lifecycle API directly. No Marketplace integration and no frontend/demo UI are required for this milestone.

## Scope decision

P3.4 is intentionally API-first:

```text
validation script
      |
      v
trusted MDC lifecycle REST API
      |
      v
Django
      |
      v
PostgreSQL source of truth
      |
      v
publication/outbox records
```

P3.4 does **not** build or integrate:

- a Marketplace UI;
- a standalone MDC frontend;
- Marketplace authentication/login;
- a new public synchronization endpoint;
- automatic Fuseki synchronization from Vercel.

The purpose is to prove that the already implemented lifecycle contract is sufficient for a future Marketplace or other trusted client.

## Starting P3.4 database baseline

Read-only verification against the pilot `neondb` before the P3.4 validation run confirmed:

```text
providers=4
offerings=6
publications=5
sync_events=6
p34_providers=0
p34_offerings=0
```

Therefore the controlled P3.4 provider does not exist before the first P3.4 run, and any later P3.4 provider/offering/publication/outbox records can be attributed to this milestone.

## Production policy during P3.4

The trusted pilot remains:

```text
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
MDC_CATALOG_SYNC_ENABLED=False
```

P3.4 writes are therefore persisted to PostgreSQL and create publication/outbox work, but semantic synchronization is intentionally left pending for P3.5.

## Controlled P3.4 provider

The validation script uses a clearly scoped pilot identity:

```text
provider_id = p34_api_validation_provider
```

Initial offering:

```text
p34_api_validation_provider_precision_metal_parts
```

Second offering:

```text
p34_api_validation_provider_precision_gears
```

The P3.4 provider is deliberately retained after validation. P3.5 will use it to prove the complete provider -> PostgreSQL -> Fuseki -> canonical search path.

## Validation script

Primary entry point:

```text
scripts/p34_provider_lifecycle_validation.py
```

The script uses only Python standard-library HTTP tooling. It reads the lifecycle bearer token from:

```text
MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN
```

The token is never printed.

Default deployed target:

```text
https://maasai-mdc-v1.vercel.app
```

Optional override:

```text
MDC_P34_BASE_URL
```

## Test matrix

### A. Public API baseline

Validate:

- `GET /api/health` -> `200`;
- `contract_version = 1.0`;
- `GET /api/catalog/filters` -> `200`;
- public contract remains unchanged.

### B. Trusted security boundary

Validate:

- anonymous provider validation -> `401`;
- lifecycle bearer token is required;
- authenticated write without `X-MDC-Actor-Id` -> `400`;
- anonymous provider detail read -> `401`.

### C. Provider payload validation

Validate:

- incomplete/invalid provider payload -> `400`, `valid=false`;
- controlled P3.4 provider payload -> `200`, `valid=true`;
- `contract_version = 1.0` is preserved.

### D. Provider registration and duplicate protection

Validate:

- authenticated/attributed registration -> `201` on first run;
- rerun may safely reuse the controlled provider after `409`;
- duplicate provider registration -> `409` with `provider_already_exists`;
- successful write reports `publication_status=sync_pending` while sync remains disabled.

### E. Provider read/update concurrency

Validate:

- trusted `GET /api/providers/{provider_id}` -> `200`;
- strong ETag is returned;
- PATCH without concurrency precondition -> `428`;
- PATCH with current ETag through the temporary Vercel-safe `X-MDC-If-Match` transport header -> `200`;
- provider ETag changes after update;
- stale ETag -> `412`;
- update creates `sync_pending` publication work.

`If-Match` remains the canonical HTTP contract; `X-MDC-If-Match` remains only the temporary Vercel transport workaround established in P3.2.

### F. Offering lifecycle

Validate:

- provider offering list returns the initial offering;
- authenticated second-offering creation -> `201` on first run or safe `409` reuse on rerun;
- duplicate offering -> `409` with `offering_already_exists`;
- trusted offering GET -> `200` + ETag;
- offering PATCH without precondition -> `428`;
- offering PATCH with current ETag -> `200`;
- offering ETag changes;
- stale offering ETag -> `412`;
- final provider offering list contains both controlled offerings.

## P3.4 persistence evidence

After a successful first run, PostgreSQL should contain the controlled provider and its two offerings plus new publication/outbox audit records. Exact audit/outbox counts should be read from the database after the run rather than hard-coded because reruns legitimately create additional update publications.

Required post-run evidence:

- `p34_api_validation_provider` exists and is active;
- both controlled offerings exist and are active;
- P3.4 write publications are recorded;
- corresponding catalogue sync events are pending while `MDC_CATALOG_SYNC_ENABLED=False`;
- no P3.4 synchronization is executed yet;
- no existing provider/offering is deleted or rewritten as part of the validation.

## Run command

From `mdc-catalog` with the lifecycle token already available in the local environment:

```powershell
& '..\.venv\Scripts\python.exe' scripts\p34_provider_lifecycle_validation.py
```

Do not paste or print the lifecycle token.

## Expected final console marker

```text
P3.4 PROVIDER LIFECYCLE API VALIDATION: PASS
```

The script also prints:

```text
tests_passed=<count>
tests_failed=0
```

## P3.4 acceptance

P3.4 is complete when:

- the reusable P3.4 validation script passes against the deployed canonical API;
- provider validation/authentication/actor requirements behave correctly;
- provider registration and duplicate protection behave correctly;
- provider GET/PATCH + ETag concurrency behave correctly;
- offering list/create/GET/PATCH + ETag concurrency behave correctly;
- PostgreSQL evidence confirms the controlled provider/offering state and pending publication/outbox work;
- no Marketplace/frontend integration is introduced;
- no semantic synchronization is executed as part of P3.4;
- no lifecycle token or database secret is committed or printed.

Target marker:

```text
READY_FOR_P35_PROVIDER_TO_DISCOVERY_END_TO_END_VALIDATION
```
