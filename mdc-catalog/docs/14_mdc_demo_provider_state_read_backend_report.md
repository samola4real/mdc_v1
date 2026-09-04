# MaaSAI MDC - Demo Provider State Read Backend Report

## 1. Purpose and scope

F5_C4 adds a backend-only demo read endpoint so the temporary demo frontend can
load providers saved by the Register New Provider flow.

## 2. Endpoint added

```text
GET /api/demo/provider-publication/state
```

The endpoint is mounted only under the demo API namespace and follows the
existing demo API enablement guard.

## 3. State file read behaviour

The endpoint reads:

```text
data/demo/provider_demo_state.json
```

When the file exists, it returns:

```text
status = demo_provider_state_loaded
providers
updates
last_updated
state_path = data/demo/provider_demo_state.json
```

## 4. Empty-state behaviour

If the state file does not exist, the endpoint returns `200 OK` with:

```text
status = demo_provider_state_empty
providers = {}
updates = {}
last_updated = null
```

Reading does not create or modify the state file.

## 5. Files modified

```text
backend/apps/demo/provider_demo_services.py
backend/apps/demo/views/get_views.py
backend/apps/demo/urls.py
backend/tests/test_demo_provider_publication.py
docs/14_mdc_demo_provider_state_read_backend_report.md
```

## 6. Tests and results

Focused verification command:

```text
..\..\.venv\Scripts\python.exe manage.py test tests.test_demo_provider_publication tests.test_demo_api_foundation -v 2
```

Result:

```text
Ran 28 tests in 0.204s
OK
```

## 7. Safety confirmation

This change did not modify frontend files, shared API endpoints, consumer
search, curated YAML, generated RDF/Turtle, Fuseki, Docker, requirements,
models, or migrations.

The endpoint does not regenerate RDF, reload Fuseki, or write to demo state
while reading.

## 8. Remaining limitations

This endpoint exposes only temporary demo state. It is not a Marketplace API
contract and does not read curated provider YAML.
