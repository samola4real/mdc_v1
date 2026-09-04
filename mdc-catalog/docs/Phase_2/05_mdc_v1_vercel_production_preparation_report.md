# MDC v1 Vercel Production Preparation Report

## 1. M5 status

completed

## 2. Final deployment architecture for M6

| Item | Decision |
| --- | --- |
| Vercel project root | `mdc-catalog/` |
| Django manage.py used by Vercel | `backend/manage.py` |
| settings module | `config.settings_production` for Vercel; `config.settings` and `config.settings_local` preserved for local/test workflows |
| WSGI/ASGI entrypoint | `config.wsgi.application` via `backend/config/wsgi.py` |
| Python version | `3.12` selected in `.python-version` |
| dependency file | `requirements.txt`, delegating to `requirements/base.txt` |
| vercel.json required? | no |
| api/index.py required? | no |

Current official Vercel documentation was checked during M5:

- https://vercel.com/changelog/zero-configuration-django-support
- https://vercel.com/docs/frameworks/full-stack/django
- https://vercel.com/docs/functions/runtimes/python
- https://vercel.com/docs/functions/limitations
- https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

No `vercel.json` required for current zero-config Django deployment.

## 3. Files changed

| Path | Change | Reason |
| --- | --- | --- |
| `.env.example` | Populated placeholder environment variables. | Document production-safe configuration without committing secrets. |
| `.python-version` | Added `3.12`. | Select Vercel's documented default Python runtime for the first pilot. |
| `requirements.txt` | Added `-r requirements/base.txt`. | Provide Vercel-recognized runtime dependency declaration at the project root. |
| `backend/config/env.py` | Added small env parsing helpers. | Avoid repeated ad-hoc parsing for booleans, numbers, and comma-separated lists. |
| `backend/config/settings.py` | Made local/base settings environment-aware while preserving local defaults. | Support configurable hosts, CORS, debug, secret, Fuseki timeout, demo, and publication flags. |
| `backend/config/settings_local.py` | Explicitly enabled provider publication locally. | Preserve existing local/demo behavior. |
| `backend/config/settings_production.py` | Added production settings layer. | Set `DEBUG=False`, require env secret, configure hosts/CORS/CSRF/HTTPS/HSTS, and disable demo/write APIs by default. |
| `backend/apps/api/views.py` | Added provider-publication feature gate. | Prevent file-backed provider publication in production by default. |
| `backend/tests/test_provider_publication_api.py` | Added disabled-flag test. | Prove provider publication does not write files when disabled. |
| `backend/tests/test_production_route_safety.py` | Added production route safety tests. | Prove canonical v1 endpoints stay available and demo/write endpoints are unavailable with production flags. |

## 4. Production settings

`config.settings_production` imports the base settings and overrides production-sensitive values.

| Setting | Production behavior |
| --- | --- |
| `DEBUG` | Always `False`. |
| `SECRET_KEY` | Required from `DJANGO_SECRET_KEY`; raises `ImproperlyConfigured` if absent. |
| `ALLOWED_HOSTS` | Comma-separated `DJANGO_ALLOWED_HOSTS`; defaults to `.vercel.app`. |
| `CORS_ALLOWED_ORIGINS` | Comma-separated `CORS_ALLOWED_ORIGINS`; defaults to empty. |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated `CSRF_TRUSTED_ORIGINS`; defaults to CORS origins. |
| `SECURE_PROXY_SSL_HEADER` | `("HTTP_X_FORWARDED_PROTO", "https")`. |
| `SESSION_COOKIE_SECURE` | Enabled by default; env override available. |
| `CSRF_COOKIE_SECURE` | Enabled by default; env override available. |
| `SECURE_SSL_REDIRECT` | Enabled by default; env override available. |
| `SECURE_HSTS_SECONDS` | Defaults to `31536000`; env override available. |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | Enabled by default; env override available. |
| `SECURE_HSTS_PRELOAD` | Enabled by default; env override available. |
| `MDC_DEMO_API_ENABLED` | Disabled by default. |
| `MDC_PROVIDER_PUBLICATION_ENABLED` | Disabled by default. |

## 5. Environment variables

| Variable | Required | Secret | Purpose | Example placeholder |
| --- | --- | --- | --- | --- |
| `DJANGO_SETTINGS_MODULE` | Yes for Vercel | No | Select production settings. | `config.settings_production` |
| `DJANGO_SECRET_KEY` | Yes for production | Yes | Django cryptographic signing secret. | `replace-me-with-a-generated-secret` |
| `DJANGO_ALLOWED_HOSTS` | Recommended | No | Comma-separated allowed hostnames. | `.vercel.app` |
| `CORS_ALLOWED_ORIGINS` | No | No | Comma-separated browser frontend origins. | `https://marketplace.example.org` |
| `CSRF_TRUSTED_ORIGINS` | No | No | Comma-separated CSRF trusted origins. | `https://marketplace.example.org` |
| `MDC_DEMO_API_ENABLED` | No | No | Enables or disables `/api/demo/*`. | `False` |
| `MDC_PROVIDER_PUBLICATION_ENABLED` | No | No | Enables or disables file-backed `/api/provider-publication`. | `False` |
| `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` | No | No | Optional external Fuseki SPARQL query endpoint. | empty |
| `FUSEKI_TIMEOUT_SECONDS` | No | No | Fuseki request timeout. | `5` |

## 6. Production endpoint exposure

| Endpoint | Production status | Reason |
| --- | --- | --- |
| `GET /api/v1/health` | available | Canonical public M4 contract. |
| `GET /api/v1/catalog/filters` | available | Canonical public M4 contract. |
| `POST /api/v1/service-discovery/search` | available | Canonical public M4 contract. |
| `GET /api/health` | available | Compatibility read alias. |
| `GET /api/catalog/filters` | available | Compatibility read alias. |
| `POST /api/service-discovery/search` | available | Compatibility search alias. |
| `/api/demo/*` | unavailable by default | Demo guard returns 404 when `DEBUG=False` and `MDC_DEMO_API_ENABLED=False`. |
| `POST /api/provider-publication` | unavailable by default | File-backed mutation returns 403 when `MDC_PROVIDER_PUBLICATION_ENABLED=False`. |
| Legacy detail endpoints under `/api/...` | unchanged | Compatibility surface deferred from M5. |

## 7. Runtime data/fallback

Confirmed existing runtime data availability:

- `data/curated/service_discovery/providers/` exists.
- `data/generated/service_discovery/mdc_service_discovery_catalog.ttl` exists.
- Path calculations use `Path(__file__).resolve()` via Django settings, not current working directory.
- Fuseki remains optional through `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT`.
- Search fallback remains: external Fuseki if configured, then local RDFLib, then harmonized YAML.

## 8. Vercel/Python compatibility

Current official Vercel Python documentation was verified during M5:

- Django zero-config support exists and detects `manage.py`, including in an immediate subdirectory.
- Supported Python versions are `3.12`, `3.13`, and `3.14`.
- `3.12` is documented as the default and was selected for the pilot.
- Dependencies can be provided with `requirements.txt`.
- The standard Python function bundle limit is 500 MB uncompressed.

Local Python 3.12 verification was not possible. The Windows launcher reported no suitable Python 3.12 runtime. The existing project venv uses Python 3.11.9 and passed all M5 checks. M6 must verify the first Vercel platform build under Python 3.12.

Vercel CLI is installed locally as `48.9.2`, below the documented `50.38.0` minimum for the current Django workflow. Vercel platform detection was not locally verified; M6 will perform the first platform build.

## 9. Verification

| Command | Result |
| --- | --- |
| `..\..\.venv\Scripts\python.exe manage.py check` from `backend/` | Exit 0; no issues. |
| `..\.venv\Scripts\python.exe backend/manage.py check` from `mdc-catalog/` | Exit 0; no issues. |
| Production data-path smoke command | Confirmed harmonized YAML provider directory and generated Turtle file exist. |
| `..\..\.venv\Scripts\python.exe manage.py test tests.test_production_route_safety tests.test_provider_publication_api -v 2` | 10 run; 10 passed; 0 failed; 0 skipped. |
| `..\..\.venv\Scripts\python.exe manage.py test tests.test_service_discovery_registry tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_provider_loader tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_local_matcher tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service tests.test_service_discovery_fuseki_service tests.test_service_discovery_matching_alignment tests.test_service_discovery_runtime_search tests.test_service_discovery_search_endpoint tests.test_service_discovery_local_search_response tests.test_service_discovery_fuseki_matching_alignment tests.test_service_discovery_search_response_contract -v 2` | 230 run; 225 passed; 0 failed; 5 skipped. |
| `..\..\.venv\Scripts\python.exe manage.py test -v 2` | 405 run; 392 passed; 0 failed; 13 skipped. |
| Production `check --deploy` from `backend/` using process-only env values | Exit 0; 15 drf-spectacular schema warnings; no Django security warnings. |
| Production `check --deploy` from `mdc-catalog/` using process-only env values | Exit 0; 15 drf-spectacular schema warnings; no Django security warnings. |

Remaining `check --deploy` warnings:

| Warning class | Count | Classification | Notes |
| --- | --- | --- | --- |
| `drf_spectacular.W002` unable to guess serializer for function API views | 15 | acceptable_for_preview | Existing OpenAPI/schema modernization issue; not a Django deployment-security warning and explicitly deferred unless required for deployment. |

Security warning classification:

| Warning area | Classification | Notes |
| --- | --- | --- |
| Hardcoded production secret | fixed | Production settings require `DJANGO_SECRET_KEY`. |
| `DEBUG=True` in production | fixed | Production settings force `DEBUG=False`. |
| Host/CORS/CSRF environment control | fixed | Production values are env-driven. |
| HTTPS proxy, secure cookies, SSL redirect, HSTS | fixed | Production settings define these values with safe defaults and env overrides. |
| drf-spectacular schema warnings | acceptable_for_preview | Non-security warnings; defer OpenAPI modernization. |

## 10. Remaining M6 prerequisites

- Create/import the Vercel project with project root set to `mdc-catalog/`.
- Configure Vercel environment variables, especially `DJANGO_SETTINGS_MODULE=config.settings_production`, `DJANGO_SECRET_KEY`, and `DJANGO_ALLOWED_HOSTS`.
- Run the first Vercel platform build on Python 3.12.
- Confirm bundle size on the platform; add `vercel.json` `excludeFiles` only if the bundle approaches the documented limit.
- Exercise public endpoints on the Vercel preview URL.
- Decide custom production frontend origin and update CORS/CSRF values.
- Leave `MDC_DEMO_API_ENABLED=False` and `MDC_PROVIDER_PUBLICATION_ENABLED=False` unless a later milestone adds durable persistence and auth.

## 11. Git commit

| Item | Value |
| --- | --- |
| hash | `200a951` |
| message | `chore: prepare MDC v1 for Vercel` |
| branch | `main` |

## 12. M6 readiness

READY_FOR_M6
