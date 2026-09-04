# MDC v1 First Vercel Deployment Report

## 1. M6 status

completed

## 2. Vercel project

| Item | Value |
| --- | --- |
| project name | `maasai-mdc-v1` |
| project ID if useful/non-secret | `prj_DekMQdOYuuH0A5yNsCkFmOC4uD9j` |
| local linked root | `C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog` |
| team/account scope | Vercel scope `mdc19`; CLI user `samola4real-6623` |

Note: Vercel project creation attempted to connect the GitHub repository but reported that the Vercel account needs a GitHub Login Connection first. This did not block CLI deployments from the local project root.

## 3. CLI/runtime

| Item | Value |
| --- | --- |
| CLI version used | `npx vercel@latest` resolved to Vercel CLI `59.11.2` |
| Vercel build CLI version | `59.3.0` |
| Django detection | Python/Django deployment through Vercel Python runtime |
| manage.py detected | Initial auto-detection was insufficient; Vercel requested explicit `pyproject.toml` entrypoint |
| WSGI entrypoint | `backend.config.wsgi:application` |
| Python version actually used by Vercel | Python `3.12` from `.python-version` |
| dependency source | `pyproject.toml` |
| function bundle | Python serverless function, `27.27MB`, region `iad1` |

## 4. Environment variables

| Variable | Preview configured | Production configured | Value disclosure |
| --- | --- | --- | --- |
| `DJANGO_SETTINGS_MODULE` | yes | yes | configured, hidden by Vercel CLI |
| `DJANGO_SECRET_KEY` | yes | yes | configured / not shown |
| `DJANGO_ALLOWED_HOSTS` | yes | yes | configured, hidden by Vercel CLI |
| `MDC_DEMO_API_ENABLED` | yes | yes | configured, hidden by Vercel CLI |
| `MDC_PROVIDER_PUBLICATION_ENABLED` | yes | yes | configured, hidden by Vercel CLI |
| `FUSEKI_TIMEOUT_SECONDS` | yes | yes | configured, hidden by Vercel CLI |
| `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` | no | no | intentionally omitted/empty |
| `CORS_ALLOWED_ORIGINS` | no | no | intentionally omitted until Marketplace frontend origin is known |
| `CSRF_TRUSTED_ORIGINS` | no | no | intentionally omitted until Marketplace frontend origin is known |

Vercel CLI stored all added values as hidden Secret-type values by default. Separate generated `DJANGO_SECRET_KEY` values were added for Preview and Production and were not printed or committed.

## 5. Preview deployment

| Item | Value |
| --- | --- |
| Preview URL | `https://maasai-mdc-v1-k16lmyz84-mdc19.vercel.app` |
| deployment ID | `dpl_GV8xfigTCfwr6SEvitad3uTm7rZF` |
| inspect URL | `https://vercel.com/mdc19/maasai-mdc-v1/GV8xfigTCfwr6SEvitad3uTm7rZF` |
| build result | ready |
| runtime result | ready |

Preview build evidence:

- `Using Python 3.12 from .python-version`
- `Installing required dependencies from pyproject.toml`
- `Compiling Python bytecode`
- `Build Completed`

Earlier Preview failures and fixes:

| Failure | Classification | Fix |
| --- | --- | --- |
| No Python entrypoint found; Vercel suggested `[tool.vercel] entrypoint` | Django/manage.py detection | Added `pyproject.toml` with `backend.config.wsgi:application`; added backend path setup to WSGI/ASGI modules. |
| `uv lock` failed because `pyproject.toml` had no `[project]` table | dependency installation | Added minimal `[project]` metadata and pinned runtime dependencies; added explicit `PyYAML` to `requirements/base.txt`. |

## 6. Preview endpoint verification

Preview was protected by Vercel Deployment Protection, so endpoint checks used authenticated `vercel curl`.

| Method | Endpoint | HTTP status | Result |
| --- | --- | --- | --- |
| GET | `/api/v1/health` | 200 | returned `{"status":"ok","service":"maasai-mdc","version":"v1"}` |
| GET | `/api/v1/catalog/filters` | 200 | returned controlled catalog filters with service-discovery registry |
| POST | `/api/v1/service-discovery/search` | 200 | `search_executed=True`, `result_count=2` |
| POST | `/api/service-discovery/search` | 200 | compatibility alias returned successful search |
| GET | `/api/demo/health` | 404 | demo API unavailable |
| POST | `/api/provider-publication` | 403 | provider publication disabled |

Preview logs after requests showed expected 200s, the intentional 404/403 safety responses, and no error-level logs.

## 7. Production deployment

| Item | Value |
| --- | --- |
| Production URL | `https://maasai-mdc-v1.vercel.app` |
| deployment URL | `https://maasai-mdc-v1-3vhy4s1wj-mdc19.vercel.app` |
| deployment ID | `dpl_GNLMfumhn4pxb9YnJq83twxzEwBM` |
| inspect URL | `https://vercel.com/mdc19/maasai-mdc-v1/GNLMfumhn4pxb9YnJq83twxzEwBM` |
| build result | ready |
| runtime result | ready |

Production build evidence:

- `Using Python 3.12 from .python-version`
- `Installing required dependencies from pyproject.toml`
- `Compiling Python bytecode`
- `Build Completed`
- Aliased to `https://maasai-mdc-v1.vercel.app`

## 8. Production endpoint verification

Production endpoint checks were run directly against the public alias.

| Method | Endpoint | HTTP status | Result |
| --- | --- | --- | --- |
| GET | `/api/v1/health` | 200 | returned MDC health JSON |
| GET | `/api/v1/catalog/filters` | 200 | returned controlled catalog filters |
| POST | `/api/v1/service-discovery/search` | 200 | `search_executed=True`, `result_count=2` |
| POST | `/api/service-discovery/search` | 200 | compatibility alias returned successful search |
| GET | `/api/demo/health` | 404 | demo API unavailable |
| POST | `/api/provider-publication` | 403 | provider publication disabled |

Production logs after requests showed expected 200s, the intentional 404/403 safety responses, and no error-level logs.

## 9. Search backend used

Observed deployed search backend:

```text
harmonized_rdf_rdflib_with_h5_policy
```

Observed warning:

```text
Primary Fuseki backend unavailable; used local RDFLib fallback.
```

This is expected for M6 because no external Fuseki endpoint was configured. The deployed search successfully used the bundled generated Turtle through RDFLib.

## 10. Production safety

| Item | Status |
| --- | --- |
| demo disabled | confirmed, `/api/demo/health` returned 404 |
| provider publication disabled | confirmed, `/api/provider-publication` returned 403 |
| no secrets committed | confirmed; generated secrets were piped only into Vercel env configuration |
| docs remain untracked | yes, `docs/` remains ignored |
| `.vercel/` metadata ignored | yes |
| `.env.local` ignored | yes |

## 11. Partner integration information

Base URL: `https://maasai-mdc-v1.vercel.app`

GET `https://maasai-mdc-v1.vercel.app/api/v1/health`

GET `https://maasai-mdc-v1.vercel.app/api/v1/catalog/filters`

POST `https://maasai-mdc-v1.vercel.app/api/v1/service-discovery/search`

Browser-based Marketplace integration will additionally require the actual Marketplace frontend origin to be added to `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` when that frontend URL is known.

## 12. Changes required during M6

| Commit | Message | Reason |
| --- | --- | --- |
| `6fe157a` | `chore: ignore Vercel project metadata` | Added root `.vercel/` ignore rule before project linking. |
| `0c3a5fc` | `chore: ignore Vercel local files` | Added project-level ignore rules for `.vercel/` and local env files while preserving `.env.example`. |
| `4a70ea2` | `fix: support Vercel runtime deployment` | Added Vercel entrypoint configuration and robust backend import path setup for WSGI/ASGI. |
| `e4bc09c` | `fix: declare Vercel Python dependencies` | Completed `pyproject.toml` for Vercel's uv-based Python build and explicitly declared `PyYAML`. |

`origin/main` was pushed to `e4bc09c` after the Production deployment so the remote baseline matches the deployed source.

Local verification after M6 fixes:

| Command | Result |
| --- | --- |
| `..\.venv\Scripts\python.exe backend/manage.py check` from `mdc-catalog/` | Exit 0; no issues. |
| Production `check --deploy` with process-only env values | Exit 0; 15 known `drf_spectacular.W002` schema warnings; no Django security warnings. |
| `..\.venv\Scripts\python.exe backend/manage.py test tests.test_production_route_safety tests.test_public_api_contract -v 2` from `mdc-catalog/` | 14 run; 14 passed. |
| Focused service-discovery suite | 230 run; 225 passed; 0 failed; 5 skipped. |
| `..\..\.venv\Scripts\python.exe manage.py test -v 2` from `backend/` | 405 run; 392 passed; 0 failed; 13 skipped. |

## 13. Remaining pilot limitations

- No external Fuseki is configured.
- No production database is configured.
- No authentication/API key layer is configured.
- No rate limiting is configured.
- Provider publication remains disabled because durable persistence and auth are deferred.
- Demo APIs remain disabled in production.
- Marketplace CORS/CSRF origin is not configured because the frontend URL is not yet known.
- Vercel GitHub repository connection requires adding a GitHub Login Connection to the Vercel account.

## 14. Next-step recommendation

Use `https://maasai-mdc-v1.vercel.app` as the pilot partner API base URL and proceed with frontend/partner integration checks against the canonical v1 endpoints. Configure the Marketplace frontend origin in Vercel once the frontend URL is known.

MDC_V1_VERCEL_PILOT_DEPLOYED
