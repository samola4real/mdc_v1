# MaaSAI MDC Demo Frontend - F3 Dashboard Backend Status Integration Report

## 1. Purpose and scope

F3 connected the MDC Demo Console dashboard route `/demo` to the safe read-only backend status endpoints prepared in F2.

The integration is limited to dashboard status display. Provider publication, consumer search, RDF regeneration, Fuseki reload, and admin mutation actions remain disconnected.

## 2. Endpoints connected

Connected only these read-only endpoints:

```text
GET /api/health
GET /api/demo/health
GET /api/demo/service-discovery/backend-status
```

Used existing F2 service functions:

```javascript
getBackendHealth()
getDemoHealth()
getDemoBackendStatus()
```

No mutation, search, provider publication, catalog, smoke test, RDF regeneration, or Fuseki reload endpoint was connected.

## 3. Components/pages modified

Modified:

```text
subsystem/frontend/src/pages/demo/index.js
subsystem/frontend/src/components/mdc/DemoStatusCards.js
subsystem/frontend/src/components/mdc/StatusTag.js
```

Created:

```text
subsystem/frontend/src/components/mdc/DemoBackendStatusPanel.js
```

The dashboard now renders `DemoBackendStatusPanel`, which owns the read-only status loading and refresh behavior.

## 4. Status-card mapping

Backend-status values are mapped to display labels:

```text
fuseki_with_h5_policy -> Fuseki + H5 policy
local_rdflib_with_h5_policy -> RDFLib + H5 policy
harmonized_yaml_h5_matcher -> Harmonized YAML + H5 matcher
demo_only_not_marketplace_contract -> Demo only - not Marketplace contract
```

If the backend returns unknown values, the UI renders the raw value safely.

Dashboard cards include:

- Backend API health
- Demo API health
- Active backend
- Fallback backends
- Fuseki dataset
- Marketplace/shared API unchanged
- Endpoint activation status
- Demo API namespace

## 5. Loading/error/partial-success behaviour

On page load, the dashboard:

- Shows a loading state.
- Calls the three F3 endpoints with `Promise.allSettled`.
- Renders any successful endpoint data.
- Shows endpoint-specific errors for failed endpoints.
- Keeps available cards visible during partial failure.
- Provides a manual `Refresh status` button.
- Does not require backend availability during `npm run build`.

Error messages include:

```text
Backend API unavailable. Check that Django is running at http://localhost:8000.
Demo API is disabled or not available. Enable MDC_DEMO_API_ENABLED=true in the backend for demo endpoints.
```

Fallback explanatory values are shown for active backend, fallbacks, and dataset if backend-status is unavailable.

## 6. Safety boundary confirmation

Confirmed:

- No mutation endpoints were connected.
- No consumer search endpoint was connected.
- No provider publication endpoint was connected.
- No catalog filters endpoint was connected.
- No Fuseki smoke test endpoint was connected.
- No RDF regenerate endpoint was connected.
- No Fuseki reload endpoint was connected.
- No browser code calls Fuseki directly.
- No API client or runtime config files were modified in F3.
- No route/menu files were modified in F3.
- No `.env`, package, or backend changes were made.

## 7. Files modified

Created:

```text
docs/04_mdc_demo_frontend_dashboard_status_report.md
subsystem/frontend/src/components/mdc/DemoBackendStatusPanel.js
```

Modified:

```text
subsystem/frontend/src/pages/demo/index.js
subsystem/frontend/src/components/mdc/DemoStatusCards.js
subsystem/frontend/src/components/mdc/StatusTag.js
```

## 8. Commands run and results

Commands were run from:

```text
C:\Users\Elahi\Desktop\template-frontend\subsystem\frontend
```

### `npm run lint`

Result: succeeded with existing unrelated warnings.

Warnings:

```text
./src/layout/AppMenuitem.js
34:8  Warning: React Hook useEffect has missing dependencies: 'item.to', 'key', 'router.events', 'router.pathname', and 'setActiveMenu'.  react-hooks/exhaustive-deps

./src/layout/layout.js
74:8  Warning: React Hook useEffect has a missing dependency: 'bindMenuOutsideClickListener'.  react-hooks/exhaustive-deps
80:8  Warning: React Hook useEffect has a missing dependency: 'bindProfileMenuOutsideClickListener'.  react-hooks/exhaustive-deps
93:8  Warning: React Hook useEffect has missing dependencies: 'hideMenu', 'hideProfileMenu', and 'router.events'.  react-hooks/exhaustive-deps

./src/pages/_document.js
27:21  Warning: Do not include stylesheets manually.  @next/next/no-css-tags
```

### `npm run build`

First sandboxed run failed with the known worker-process restriction:

```text
Error: spawn EPERM
```

The command was rerun with approved escalation for `npm run build`.

Escalated result: succeeded.

Build output:

```text
Compiled successfully
Generated static pages: 22/22
```

The `/demo` dashboard route built successfully.

Build also reported the existing lint warnings above and:

```text
Browserslist: caniuse-lite is outdated.
```

No package update was performed.

## 9. Browser/manual verification result

Browser verification was not performed in this run.

Backend endpoint checks from PowerShell:

```text
GET http://localhost:8000/api/health -> 200
Response: {"status":"ok","service":"maasai-mdc","version":"v1"}

GET http://localhost:8000/api/demo/health -> 404
GET http://localhost:8000/api/demo/service-discovery/backend-status -> 404
```

The 404 responses mean the dashboard should show the F3 demo API unavailable guidance until the backend demo API is enabled with:

```powershell
$env:MDC_DEMO_API_ENABLED="true"
```

## 10. Remaining risks/questions

- Demo endpoints currently return 404 in this environment, so runtime browser verification with full success state still needs a backend run with `MDC_DEMO_API_ENABLED=true`.
- Backend response shapes should be confirmed before adding richer status details.
- Existing unrelated lint warnings remain in layout/menu/document files.

## 11. Recommended next phase: F4 Consumer search integration

Recommended F4 scope:

- Connect `/demo/consumer-search` to `POST /api/service-discovery/search`.
- Keep score hidden by default unless explicitly requested.
- Add loading, empty, success, and error states for search.
- Continue keeping demo admin mutation endpoints disconnected until their dedicated phase.
