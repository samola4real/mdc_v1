# MaaSAI MDC â€” Demo API App Foundation Report

## 1. Purpose

This creates a separate demo-only Django app for the temporary MDC Demo Console.
The app exists to support temporary provider, consumer, and admin/audit demo UI
flows without changing the Marketplace/shared MDC API contract.

## 2. Boundary

```text
/api/...       = Marketplace/shared MDC API
/api/demo/...  = temporary demo console API
```

Demo endpoints are isolated under `/api/demo/` and are not mounted under shared
service-discovery or provider-publication routes.

## 3. View Organisation

```text
GET endpoints  -> views/get_views.py
POST endpoints -> views/post_views.py
```

## 4. Feature Flag

```text
MDC_DEMO_API_ENABLED
```

The flag is read from the `MDC_DEMO_API_ENABLED=true` environment variable.
It is disabled by default. When disabled, demo endpoints return `404`.

## 5. Initial Endpoints

```text
GET  /api/demo/health
GET  /api/demo/service-discovery/backend-status
GET  /api/demo/service-discovery/fuseki-smoke-test
POST /api/demo/service-discovery/regenerate-rdf
POST /api/demo/service-discovery/reload-fuseki
POST /api/demo/provider-publication/preview
POST /api/demo/provider-publication/simulate-update
```

`/api/demo/health` and `/api/demo/service-discovery/backend-status` return
safe read-only status payloads when enabled. The Fuseki smoke-test endpoint
returns a safe non-mutating placeholder. POST endpoints return `501 Not
Implemented` and do not mutate state.

## 6. Safety Constraints

- No shared endpoint behaviour changed.
- No provider YAML modified.
- No RDF regenerated.
- No Fuseki reload implemented.
- No API endpoint activation performed.
- No persistence added.

## 7. Tests

Focused test module:

```text
backend/tests/test_demo_api_foundation.py
```

It covers the default-disabled flag state, `404` hidden demo endpoints while
disabled, enabled demo health/status/smoke-test responses, `501` POST
placeholders, existing shared `/api/health` and `/api/catalog/filters`
availability, and the absence of demo routes under shared service-discovery
paths.

## 8. Next Frontend Step

The next step is to audit the Next.js MaaSAI template and map
pages/components/API clients for the temporary MDC Demo Console.

## Local demo settings amendment

Demo API availability is now controlled by Django settings, not by a frontend
request or endpoint toggle. Local `DEBUG=True` enables the demo API
automatically, so no manual PowerShell environment variable is needed for local
demo work.

Base/default settings keep the explicit demo flag disabled:

```text
config.settings -> MDC_DEMO_API_ENABLED = False
```

Local development settings enable the demo API for MVD/demo work:

```text
config.settings_local -> MDC_DEMO_API_ENABLED = True
```

Production-like `DEBUG=False` remains disabled unless
`MDC_DEMO_API_ENABLED=True` is explicitly set in Django settings. Test and
non-runserver management commands continue to default to `config.settings`, and
tests explicitly cover the `DEBUG` and flag combinations with
`override_settings`.

The frontend cannot enable or disable the demo API by request.

Focused verification command:

```text
..\..\.venv\Scripts\python.exe manage.py test tests.test_demo_api_foundation tests.test_api_v1 -v 2
```

Result:

```text
Ran 13 tests in 0.031s
OK
```
