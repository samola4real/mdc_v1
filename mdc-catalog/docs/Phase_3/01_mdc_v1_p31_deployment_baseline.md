# MDC v1 P3.1 — Temporary Pilot Deployment Baseline

## Status

**IN PROGRESS.** Code/configuration review is complete and the deployment procedure is fixed. One environment preparation step and one Vercel production deployment/smoke run remain.

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

## Existing Vercel baseline

Existing pilot project:

```text
project: maasai-mdc-v1
production alias: https://maasai-mdc-v1.vercel.app
project root: mdc-catalog/
Python: 3.12
entrypoint: backend.config.wsgi:application
settings: config.settings_production
```

The repository already contains the Vercel-compatible `pyproject.toml`, `.python-version`, production settings, backend import-path support, and runtime dependencies established during M5/M6. No `vercel.json` is required for this baseline.

The prior Vercel deployment predates M7 persistence/security work and therefore must be redeployed from the current Phase 3 baseline.

## Current managed PostgreSQL state

The temporary Neon validation project/database exists, but inspection at the start of P3.1 found:

```text
mdc_validation tables: 0
```

Therefore `mdc_validation` must receive the existing Django migrations and harmonized provider import before it can serve as the deployed lifecycle database. This is an environment preparation operation, not a new schema design.

Do not run tests against `mdc_validation`; Django tests must continue using isolated test databases.

## Deployment feature policy

The first P3.1 deployment must keep all mutation/semantic-write switches disabled:

```text
MDC_PROVIDER_PUBLICATION_ENABLED=False
MDC_PROVIDER_VALIDATION_ENABLED=False
MDC_CATALOG_SYNC_ENABLED=False
```

Trusted lifecycle security stays enabled even while lifecycle features are disabled:

```text
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
```

A real lifecycle service token should be stored only in Vercel secret/environment configuration. It must not be committed or pasted into project reports.

## Required production environment variables

Minimum P3.1 production set:

```text
DJANGO_SETTINGS_MODULE=config.settings_production
DJANGO_SECRET_KEY=<secret>
DJANGO_ALLOWED_HOSTS=.vercel.app
DATABASE_URL=<mdc_validation PostgreSQL URL>
MDC_DEMO_API_ENABLED=False
MDC_PROVIDER_PUBLICATION_ENABLED=False
MDC_PROVIDER_VALIDATION_ENABLED=False
MDC_CATALOG_SYNC_ENABLED=False
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True
MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN=<secret>
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT=
SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT=
FUSEKI_TIMEOUT_SECONDS=5
FUSEKI_SYNC_TIMEOUT_SECONDS=10
```

`CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` remain empty until the Marketplace frontend origin is known.

## Database preparation

From `mdc-catalog/backend`, with the local `.env` pointing to the temporary `mdc_validation` database:

```powershell
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
& '..\..\.venv\Scripts\python.exe' manage.py migrate
& '..\..\.venv\Scripts\python.exe' manage.py import_service_discovery_providers
```

Expected curated import baseline:

```text
3 providers
4 offerings
5 certifications
```

Then verify without exposing credentials:

```powershell
& '..\..\.venv\Scripts\python.exe' manage.py shell -c "from django.db import connection; from apps.providers.models import Provider,Offering,ProviderCertification; connection.ensure_connection(); print('backend=',connection.vendor); print('providers=',Provider.objects.count(),'offerings=',Offering.objects.count(),'certifications=',ProviderCertification.objects.count())"
```

Expected:

```text
backend= postgresql
providers= 3 offerings= 4 certifications= 5
```

## Vercel deployment

The connected ChatGPT Vercel integration is not currently exposing the project/team in this session, so P3.1 uses the already-established local Vercel CLI path rather than blocking on plugin access.

From `C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog`:

```powershell
npx vercel@latest --prod
```

If production environment variables are not yet updated, configure them in Vercel before this command. Secrets must be entered interactively or through the Vercel dashboard, never placed in shell history or Git.

## Mandatory smoke gate

After deployment, verify the production alias:

```text
https://maasai-mdc-v1.vercel.app
```

Required outcomes:

| Request | Expected |
| --- | --- |
| `GET /api/health` | 200, `contract_version: 1.0` |
| `GET /api/catalog/filters` | 200 |
| `POST /api/service-discovery/search` | 200 with normal discovery result |
| `GET /api/v1/health` | 404 |
| `GET /api/v1/catalog/filters` | 404 |
| `POST /api/v1/service-discovery/search` | 404 |
| `GET /api/demo/health` | 404 |
| anonymous `GET /api/providers/tasowheel` | 401 when lifecycle token is configured |
| anonymous `POST /api/provider-publication` | 401 when lifecycle token is configured |
| authenticated lifecycle write while publication flag is False | 403 |

Public discovery must remain independent of the lifecycle bearer credential.

## P3.1 acceptance

P3.1 is complete when all of the following are true:

- current Phase 3 baseline deployed on Vercel;
- production runtime uses `config.settings_production`;
- deployed `DATABASE_URL` points to prepared managed PostgreSQL;
- public canonical discovery smoke tests pass;
- `/api/v1/...` remains absent;
- demo remains disabled;
- trusted lifecycle boundary rejects anonymous requests;
- lifecycle writes remain feature-disabled;
- no real remote Fuseki write occurs;
- no secrets are committed or printed in reports.

Successful marker:

```text
READY_FOR_P32_TRUSTED_LIFECYCLE_PILOT_ENABLEMENT
```
