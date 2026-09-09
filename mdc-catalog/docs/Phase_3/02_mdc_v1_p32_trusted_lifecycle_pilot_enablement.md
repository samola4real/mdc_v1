# MDC v1 P3.2 — Trusted Lifecycle Pilot Enablement

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

The trusted lifecycle boundary continues to require the service bearer token. Write requests also require actor attribution, and PATCH requests require `If-Match` when concurrency protection is enabled.

## Why staged enablement

P3.2 does not reduce the intended functionality. It enables it in a short sequence so that each risk boundary is verified before the next one is opened:

1. enable validation only — no database mutation;
2. verify authentication + validation + non-mutation;
3. enable provider publication/write lifecycle;
4. register one controlled pilot provider and verify provider/offering read-update concurrency behavior;
5. keep catalogue synchronization disabled until the later real-Fuseki gate.

This keeps rollback simple while still completing the full trusted lifecycle pilot.

## Stage A — validation-only enablement

**STATUS: PASS**

Production configuration:

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

**STATUS: READY TO RUN**

Production configuration:

```text
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_CATALOG_SYNC_ENABLED=False
```

The controlled write smoke uses the dedicated provider ID:

```text
p32_pilot_provider
```

Existing Tasowheel, Precipart, and seeded provider records are not edited.

The Stage B smoke verifies:

- anonymous provider registration remains rejected;
- authenticated provider registration succeeds (or safely reuses the same fixed pilot identity on rerun);
- provider GET returns an opaque ETag;
- provider PATCH with current `If-Match` succeeds;
- stale provider `If-Match` returns 412;
- a second controlled offering can be created;
- offering GET returns an opaque ETag;
- offering PATCH with current `If-Match` succeeds;
- stale offering `If-Match` returns 412;
- accepted writes remain `sync_pending` because catalogue synchronization is disabled;
- public catalogue filters remain available;
- no real Fuseki write occurs.

After the smoke run, PostgreSQL evidence must confirm:

- the pilot provider and offerings exist;
- `ProviderPublication.submitted_by_external_id` records `p32:trusted-write-smoke`;
- publication history exists for accepted writes;
- corresponding sync events remain pending;
- no event was processed remotely while `MDC_CATALOG_SYNC_ENABLED=False`.

## P3.2 acceptance

P3.2 is complete when:

- validation-only trusted flow passes and is proved non-mutating;
- controlled provider registration/update and offering create/update pass;
- authentication, actor attribution, and ETag/If-Match are verified on the deployed pilot;
- public discovery remains unchanged;
- `/api/v1/...` remains absent;
- real semantic synchronization is still disabled;
- no secrets are committed or written to reports.

Target marker:

```text
READY_FOR_P33_REAL_FUSEKI_SYNCHRONIZATION_VALIDATION
```
