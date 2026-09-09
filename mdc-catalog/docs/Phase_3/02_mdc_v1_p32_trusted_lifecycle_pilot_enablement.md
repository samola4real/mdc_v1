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
4. register one controlled pilot provider and verify read/update concurrency behavior;
5. keep catalogue synchronization disabled until the later real-Fuseki gate.

This keeps rollback simple while still completing the full trusted lifecycle pilot.

## Stage A — validation-only enablement

Production configuration:

```text
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_PUBLICATION_ENABLED=False
MDC_CATALOG_SYNC_ENABLED=False

MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
```

Expected behavior:

| Check | Expected |
| --- | --- |
| public discovery | unchanged, 200 |
| anonymous validation | 401 |
| authenticated valid validation | 200, `valid=true` |
| authenticated invalid validation | 400 |
| authenticated provider write | 403 |
| provider/publication/sync-event DB counts | unchanged |

Baseline before Stage A:

```text
providers=3
offerings=4
certifications=5
publications=0
sync_events=0
```

## Stage B — controlled write enablement

Only after Stage A passes:

```text
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_CATALOG_SYNC_ENABLED=False
```

The pilot write will use a dedicated/demo provider identity so existing Tasowheel, Precipart, and seeded provider records are not edited.

Planned write checks:

- authenticated provider registration succeeds;
- actor attribution is persisted in `ProviderPublication.submitted_by_external_id`;
- provider GET succeeds and returns an opaque ETag;
- provider PATCH with current `If-Match` succeeds;
- stale `If-Match` returns 412 and does not overwrite the newer state;
- accepted writes create publication/outbox history;
- catalogue sync remains pending because `MDC_CATALOG_SYNC_ENABLED=False`;
- no real Fuseki write occurs.

## P3.2 acceptance

P3.2 is complete when:

- validation-only trusted flow passes and is proved non-mutating;
- controlled provider registration/update passes;
- authentication, actor attribution, and ETag/If-Match are verified on the deployed pilot;
- public discovery remains unchanged;
- `/api/v1/...` remains absent;
- real semantic synchronization is still disabled;
- no secrets are committed or written to reports.

Target marker:

```text
READY_FOR_P33_REAL_FUSEKI_SYNCHRONIZATION_VALIDATION
```
