# MDC v1 P3.0 — M7 Completion / Release Review

## Decision

**P3.0 PASS.** The M7 persistence/provider-lifecycle programme is accepted as the technical baseline for Phase 3 pilot deployment and Marketplace integration.

This review does not enable provider lifecycle writes or real Fuseki writes. It confirms that the codebase is ready to enter a controlled deployment baseline with fail-closed production settings.

Completion marker:

```text
READY_FOR_P31_DEPLOYMENT_BASELINE
```

## Accepted M7 sequence

```text
M7.1  PostgreSQL / Django persistence foundation       COMPLETE
M7.2  harmonized DB repository + migration            COMPLETE
       managed PostgreSQL validation                  COMPLETE
M7.3  validation + DB-backed lifecycle reads          COMPLETE
M7.4  registration / update lifecycle                 COMPLETE
M7.5  RDF / Fuseki synchronization                    COMPLETE
M7.6  external exposure readiness                     COMPLETE
```

## Architecture accepted for Phase 3

```text
Marketplace / trusted MaaSAI service
        |
        | trusted service-to-service lifecycle requests
        v
Django / DRF
        |
        v
PostgreSQL operational source of truth
        |
        +--> ProviderPublication audit/history
        |
        +--> CatalogueSyncEvent outbox
                    |
                    v
              RDF / Fuseki
```

The service-discovery runtime remains independent from the operational write path and preserves the accepted fallback order:

```text
remote Fuseki (when configured)
    -> local RDFLib
    -> harmonized YAML fallback
```

PostgreSQL is the operational source of truth for provider lifecycle state. RDF/Fuseki remains the semantic catalogue/search representation.

## Stable external API decision

Canonical public discovery remains:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Trusted provider lifecycle remains:

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

No `/api/v1/...` public strategy is restored. Contract evolution remains payload metadata based through `contract_version: "1.0"`.

## M7.6 security boundary accepted

The trusted lifecycle baseline provides:

- replaceable service-to-service Bearer authentication;
- `X-MDC-Actor-Id` attribution persisted to accepted publication history;
- strong ETag / `If-Match` optimistic concurrency for provider/offering PATCH operations;
- safe 400/401/403/404/409/412/428/503 error boundaries;
- production fail-closed defaults;
- stale outbox `processing` lease recovery;
- no anonymous lifecycle exposure merely because lifecycle code exists.

Production defaults remain:

```text
MDC_PROVIDER_PUBLICATION_ENABLED=False
MDC_PROVIDER_VALIDATION_ENABLED=False
MDC_CATALOG_SYNC_ENABLED=False
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
```

## Final M7 verification evidence

| Gate | Result |
| --- | --- |
| Focused M7.6 SQLite | 64 / 64 passed |
| Managed PostgreSQL M7.6 | 98 / 98 passed |
| Full local suite | 537 run; 528 passed; 9 existing opt-in skips |
| Maintained H1-H9 | 230 run; 225 passed; 5 existing opt-in remote skips |
| `manage.py check` | PASS |
| `makemigrations --check --dry-run` | PASS; no changes detected |
| RDF baseline | 673 triples |
| Git main after M7.6 | `3497d6e7004fc037c3085082bba1742c10df988c` |

The temporary managed PostgreSQL test database left by Django teardown was removed explicitly; the persistent validation database was preserved.

## Release-readiness findings

### Ready now

- Public health/filter/search deployment.
- Cloud-neutral Django + PostgreSQL runtime configuration.
- Trusted lifecycle code deployed in a disabled/fail-closed state.
- Managed PostgreSQL connectivity using `DATABASE_URL`.
- Future controlled enablement of provider validation/registration/update.
- Future controlled RDF/Fuseki synchronization.

### Deliberately not enabled yet

- Production provider lifecycle writes.
- Production validation endpoint.
- Production catalogue synchronization.
- Real remote Fuseki Graph Store write authentication.
- Browser-direct anonymous provider administration.
- Marketplace CORS/CSRF origin until an actual Marketplace frontend origin is known.

## Infrastructure portability decision preserved

Vercel + Neon are temporary pilot infrastructure only. Future target hosting is AWS. The application must continue to depend on standard Django/PostgreSQL/environment-variable contracts rather than Vercel-, Neon-, or AWS-specific domain logic.

## P3.0 conclusion

No further M7 code changes are required before beginning P3.1. The next action is to deploy the accepted M7 baseline to the temporary pilot infrastructure with all mutation/sync feature flags initially disabled, verify the canonical public API, verify the trusted lifecycle boundary fails closed, and only then progress to controlled lifecycle enablement.

```text
READY_FOR_P31_DEPLOYMENT_BASELINE
```
