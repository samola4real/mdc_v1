# MDC v1 P3.2 — Trusted Lifecycle Pilot Enablement

## Status

**COMPLETE / ACCEPTED.**

Official marker:

```text
READY_FOR_P33_REAL_FUSEKI_SYNCHRONIZATION_VALIDATION
```

## Goal

Enable the trusted provider-lifecycle surface on the temporary pilot deployment in controlled stages, without changing the public discovery contract and without enabling real Fuseki writes.

P3.2 uses the production alias:

```text
https://maasai-mdc-v1.vercel.app
```

The public discovery routes remain unchanged and unauthenticated:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

The trusted lifecycle boundary requires the service bearer token. Write requests require actor attribution. PATCH requests use optimistic concurrency with strong opaque lifecycle ETags.

## Why staged enablement

P3.2 did not reduce the intended functionality. It enabled the trusted lifecycle in a short sequence so each risk boundary could be verified before the next one was opened:

1. validation only — no database mutation;
2. authentication + validation + non-mutation verification;
3. provider publication/write lifecycle enablement;
4. controlled provider/offering registration and update verification;
5. catalogue synchronization kept disabled for the later real-Fuseki gate.

This kept rollback simple while completing the full trusted lifecycle pilot.

## Stage A — validation-only enablement

**STATUS: PASS**

Production configuration during Stage A:

```text
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_PUBLICATION_ENABLED=False
MDC_CATALOG_SYNC_ENABLED=False

MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
```

Observed deployment smoke results:

```text
PASS public health unchanged: 200
PASS anonymous validation rejected: 401
PASS authenticated valid validation: 200
PASS authenticated invalid validation: 400
PASS provider writes still disabled: 403
PASS trusted DB read still works: 200
P3.2 Stage A validation smoke PASS
```

Database baseline before Stage A:

```text
providers=3
offerings=4
certifications=5
publications=0
sync_events=0
```

Database verification after Stage A:

```text
providers=3
offerings=4
certifications=5
publications=0
sync_events=0
```

Therefore the deployed validation flow is confirmed non-mutating.

## Stage B — controlled write enablement

**STATUS: PASS**

Production configuration:

```text
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_CATALOG_SYNC_ENABLED=False

MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
```

The controlled write smoke used the dedicated provider ID:

```text
p32_pilot_provider
```

Existing Tasowheel, Precipart, and seeded provider records were not edited.

### Temporary Vercel concurrency transport compatibility

The first Stage B run exposed a deployment-boundary issue: the standard `If-Match` request reached the API and the provider update was committed, but the temporary Vercel path returned 412 to the client. PostgreSQL evidence confirmed the update, publication, and outbox event had already been persisted.

The lifecycle API therefore retains canonical `If-Match` support and additionally accepts this temporary compatibility header:

```text
X-MDC-If-Match
```

It carries exactly the same strong opaque ETag value and feeds the same optimistic-concurrency comparison. The compatibility header does not change the provider model, persistence semantics, ETag algorithm, actor attribution, public API contract, or future AWS architecture. Conflicting canonical and compatibility revision headers are rejected.

Focused verification after the compatibility change:

```text
Found 16 test(s).
................
Ran 16 tests in 45.928s
OK
```

Django then failed only while attempting to delete the temporary `test_neondb` database because one external session still held that test database. This teardown issue occurred after all 16 tests passed and did not affect the deployed pilot database or Stage B API smoke.

### Stage B deployed smoke results

```text
PASS public health unchanged: 200
PASS anonymous provider registration rejected: 401
PASS authenticated provider registration: existing pilot provider reused (409)
PASS trusted provider read: 200
PASS provider update with current revision: 200
PASS stale provider revision rejected: 412
PASS authenticated offering creation: 201
PASS trusted offering read: 200
PASS offering update with current revision: 200
PASS stale offering revision rejected: 412
PASS public filters unchanged: 200
P3.2 Stage B trusted write smoke PASS
```

The 409 on registration is expected: the first Stage B attempt had already created the fixed pilot provider before the concurrency transport issue was discovered. Reusing the same fixed pilot identity avoided duplicate pilot data.

## PostgreSQL evidence after Stage B

Final managed PostgreSQL counts:

```text
providers=4
offerings=6
certifications=5
publications=5
sync_events=6
```

All five publications for `p32_pilot_provider` are persisted with:

```text
submitted_by_external_id = p32:trusted-write-smoke
status = sync_pending
```

The history consists of one create publication and four update publications. The extra early update is retained as valid audit evidence from the first Stage B attempt, where the database commit succeeded even though the temporary Vercel boundary returned 412.

All six corresponding catalogue sync events remain:

```text
status = pending
attempt_count = 0
last_error = ""
```

The pending event set covers provider and offering upserts for:

```text
p32_pilot_provider
p32_pilot_provider_precision_metal_parts
p32_pilot_provider_precision_gears
```

Therefore no semantic event was processed remotely while `MDC_CATALOG_SYNC_ENABLED=False`, and no real Fuseki write occurred during P3.2.

## Acceptance

P3.2 acceptance is satisfied:

- validation-only trusted flow passed and was proved non-mutating;
- controlled provider registration/update passed;
- controlled offering creation/update passed;
- anonymous lifecycle access remained rejected;
- actor attribution was persisted for all accepted writes;
- current revision updates succeeded;
- stale revisions returned 412 and did not overwrite newer state;
- public discovery remained available;
- `/api/v1/...` remained outside the canonical API strategy;
- all accepted lifecycle writes remained durable in PostgreSQL with pending outbox evidence;
- real semantic synchronization remained disabled;
- no secret or bearer credential was committed or written into this report;
- the implementation remains PostgreSQL/Django based and cloud-provider neutral apart from the explicitly temporary Vercel transport compatibility header.

Official marker:

```text
READY_FOR_P33_REAL_FUSEKI_SYNCHRONIZATION_VALIDATION
```
