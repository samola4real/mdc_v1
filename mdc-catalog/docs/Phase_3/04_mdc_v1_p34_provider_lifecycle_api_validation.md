# MDC v1 P3.4 — Provider Lifecycle API Validation

## Status

**COMPLETE.** The deployed trusted provider lifecycle API passed the controlled P3.4 validation. No Marketplace integration or frontend/demo UI was introduced.

## Scope decision

P3.4 was intentionally API-first:

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

P3.4 did **not** build or integrate a Marketplace UI, standalone MDC frontend, Marketplace login, public synchronization endpoint, or Vercel-side automatic Fuseki synchronization.

## Starting database baseline

Before the P3.4 run, read-only verification against `neondb` showed:

```text
providers=4
offerings=6
publications=5
sync_events=6
p34_providers=0
p34_offerings=0
```

## Controlled P3.4 provider

```text
provider_id = p34_api_validation_provider
```

Offerings:

```text
p34_api_validation_provider_precision_metal_parts
p34_api_validation_provider_precision_gears
```

The provider is deliberately retained for P3.5.

## Validation script

Primary entry point:

```text
scripts/p34_provider_lifecycle_validation.py
```

The lifecycle bearer token is read from `MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN` and is never printed.

During the run, the previous Production lifecycle token could not be retrieved from Vercel because it was returned as `[SENSITIVE]`. A new strong token was generated once and the same undisclosed value was configured in local `.env` and Vercel Production. Production was redeployed successfully. No token value was committed or printed.

## P3.4 API validation result — PASSED

Confirmed result:

```text
P3.4 PROVIDER LIFECYCLE API VALIDATION: PASS
tests_passed=45
tests_failed=0
```

Validated successfully:

- `GET /api/health` -> `200`, `contract_version=1.0`;
- `GET /api/catalog/filters` -> `200`, `contract_version=1.0`;
- anonymous provider validation -> `401`;
- invalid validation -> `400`, `valid=false`;
- valid validation -> `200`, `valid=true`;
- write without actor attribution -> `400`;
- anonymous provider read -> `401`;
- first provider registration -> `201`;
- duplicate provider registration -> `409`;
- trusted provider GET -> `200` + ETag;
- provider PATCH without precondition -> `428`;
- provider PATCH with current ETag -> `200`;
- provider ETag changed after update;
- stale provider ETag -> `412`;
- initial offering listed;
- second offering creation -> `201`;
- duplicate offering -> `409`;
- trusted offering GET -> `200` + ETag;
- offering PATCH without precondition -> `428`;
- offering PATCH with current ETag -> `200`;
- offering ETag changed after update;
- stale offering ETag -> `412`;
- final provider offering list contains both controlled offerings.

`If-Match` remains the canonical concurrency contract. `X-MDC-If-Match` remains the temporary Vercel transport workaround established in P3.2.

## PostgreSQL persistence evidence — PASSED

Independent read-only verification after the successful run showed:

```text
providers=5
offerings=8
publications=9
sync_events=11
p34_providers=1
p34_offerings=2
```

Controlled provider state:

```text
provider_id=p34_api_validation_provider
status=active
offerings=2
```

P3.4 publications:

```text
sync_pending create=1
sync_pending update=3
```

P3.4 outbox events:

```text
status=pending
events=5
min_attempts=0
max_attempts=0
```

This confirms that the P3.4 lifecycle writes were durably persisted and produced exactly the pending semantic synchronization work expected while `MDC_CATALOG_SYNC_ENABLED=False` in Vercel Production.

## P3.4 acceptance

- reusable deployed API validation script passes — **PASS**;
- provider validation/authentication/actor boundary works — **PASS**;
- provider registration/duplicate protection works — **PASS**;
- provider GET/PATCH/ETag concurrency works — **PASS**;
- offering list/create/GET/PATCH/ETag concurrency works — **PASS**;
- PostgreSQL evidence confirms the controlled provider and two offerings — **PASS**;
- P3.4 publications/outbox remain pending for P3.5 — **PASS**;
- no Marketplace/frontend integration introduced — **PASS**;
- no semantic synchronization executed in P3.4 — **PASS**;
- no secrets committed or printed — **PASS**.

Completion marker:

```text
READY_FOR_P35_PROVIDER_TO_DISCOVERY_END_TO_END_VALIDATION
```
