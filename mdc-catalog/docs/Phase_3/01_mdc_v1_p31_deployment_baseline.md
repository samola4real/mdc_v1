# MDC v1 P3.1 — Temporary Pilot Deployment Baseline

## Status

**COMPLETE.** The current Phase 3 baseline has been deployed successfully to the temporary Vercel pilot, connected to managed PostgreSQL, and verified with the automated production smoke gate.

Successful marker:

```text
READY_FOR_P32_TRUSTED_LIFECYCLE_PILOT_ENABLEMENT
```

## Target

Temporary pilot only:

```text
Vercel Django runtime
        |
        v
MDC API
        |
        v
managed PostgreSQL (temporary Neon pilot)
```

Future target remains AWS. P3.1 does not introduce Vercel- or Neon-specific domain logic.

## Deployment baseline

```text
project: maasai-mdc-v1
production alias: https://maasai-mdc-v1.vercel.app
project root: mdc-catalog/
Python: 3.12
entrypoint: backend.config.wsgi:application
settings: config.settings_production
```

The canonical public API remains unversioned under `/api/...`; `/api/v1/...` is intentionally absent.

## Managed PostgreSQL state

The local canonical `.env` used for the P3.1 deployment baseline was confirmed to point to the temporary Neon database named:

```text
neondb
```

The database was migrated and seeded successfully with the accepted harmonized baseline:

```text
backend= postgresql
providers= 3
offerings= 4
certifications= 5
```

Direct read-only Neon verification also confirmed the same 3/4/5 counts.

The separate `mdc_validation` database remains unused for this deployment baseline and was not modified as part of final P3.1 deployment.

## Production feature policy

Mutation and semantic-write switches remain disabled:

```text
MDC_PROVIDER_PUBLICATION_ENABLED=False
MDC_PROVIDER_VALIDATION_ENABLED=False
MDC_CATALOG_SYNC_ENABLED=False
```

Trusted lifecycle security remains enabled:

```text
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
```

The lifecycle service token is stored only in Vercel secret/environment configuration and was not committed or written into reports.

## Runtime dependency correction

The first P3.1 production deployment built successfully but returned HTTP 500 on `/api/health` after `DATABASE_URL` was introduced.

Root cause: Vercel installs Python dependencies from `pyproject.toml`, while PostgreSQL runtime dependencies had only been present in `requirements/base.txt`.

The following dependencies were added to `pyproject.toml`:

```text
psycopg[binary]==3.2.12
dj-database-url==3.0.1
```

Fix commit:

```text
d27ee8a9e7f561e01b46ef74606844593e6c0f98
fix: include PostgreSQL runtime dependencies for Vercel
```

After redeployment, the full P3.1 smoke gate passed.

## Production smoke verification

Target:

```text
https://maasai-mdc-v1.vercel.app
```

Observed results:

| Request | Result |
| --- | --- |
| `GET /api/health` | 200 |
| `GET /api/catalog/filters` | 200 |
| `POST /api/service-discovery/search` | 200 |
| `GET /api/v1/health` | 404 |
| `GET /api/v1/catalog/filters` | 404 |
| `POST /api/v1/service-discovery/search` | 404 |
| `GET /api/demo/health` | 404 |
| anonymous `GET /api/providers/tasowheel` | 401 |
| anonymous `POST /api/provider-publication` | 401 |
| authenticated `GET /api/providers/tasowheel` | 200 |
| authenticated provider write while publication disabled | 403 |

Final smoke result:

```text
P3.1 deployment smoke PASS
```

This confirms all of the following at once:

- canonical public discovery remains available without lifecycle authentication;
- `/api/v1/...` remains absent;
- demo routes remain disabled;
- Vercel can connect successfully to the managed PostgreSQL catalogue;
- the deployed database can return the Tasowheel lifecycle record;
- anonymous lifecycle access is rejected;
- valid lifecycle authentication does not bypass the publication feature flag;
- provider writes remain disabled in production;
- no real remote Fuseki write was enabled or exercised.

## P3.1 acceptance

All P3.1 gates are satisfied:

- current Phase 3 baseline deployed on Vercel — **PASS**;
- production runtime uses `config.settings_production` — **PASS**;
- managed PostgreSQL connectivity — **PASS**;
- catalogue baseline 3 providers / 4 offerings / 5 certifications — **PASS**;
- public canonical discovery — **PASS**;
- `/api/v1/...` absent — **PASS**;
- demo disabled — **PASS**;
- trusted lifecycle authentication boundary — **PASS**;
- authenticated DB-backed lifecycle read — **PASS**;
- lifecycle writes feature-disabled — **PASS**;
- no remote Fuseki mutation — **PASS**;
- no secret committed to Git/report — **PASS**.

## Next step

Proceed to P3.2: trusted lifecycle pilot enablement. Enable capabilities progressively rather than all at once, beginning with validation and trusted reads before provider registration/update writes.

```text
READY_FOR_P32_TRUSTED_LIFECYCLE_PILOT_ENABLEMENT
```
