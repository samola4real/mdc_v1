# MaaSAI MDC Demo Frontend - F2 Runtime Config and API Client Report

## 1. Purpose and scope

F2 added the runtime configuration and service-layer foundation for future MDC Demo Console API integration.

This phase did not wire UI pages to live backend data. The F1 demo pages remain static/mock-only.

## 2. Runtime config changes

Updated:

```text
subsystem/frontend/public/config.js
subsystem/frontend/src/config/runtimeConfig.js
```

Added runtime config section:

```javascript
mdcApi: {
    baseUrl: 'http://localhost:8000',
    sharedApiPrefix: '/api',
    demoApiPrefix: '/api/demo'
}
```

Added helper exports:

```javascript
getMdcApiConfig()
getMdcApiBaseUrl()
getMdcSharedApiPrefix()
getMdcDemoApiPrefix()
```

Existing Keycloak config was preserved and still merges independently.

## 3. MDC API client design

Created:

```text
subsystem/frontend/src/services/mdc/client.js
```

The client:

- Uses existing installed `axios`.
- Reads `baseUrl` from runtime config at request time.
- Builds URLs without double slashes.
- Provides `get(path, options)` and `post(path, data, options)`.
- Uses a 10 second default timeout.
- Normalizes errors into a safe frontend object:

```javascript
{
    message,
    status,
    details
}
```

The client does not:

- Call backend at module import time.
- Add credentials or auth headers.
- Expose Fuseki directly to the browser.
- Require backend availability during build.

## 4. Shared Marketplace-like service modules

Created shared service modules:

```text
subsystem/frontend/src/services/mdc/health.service.js
subsystem/frontend/src/services/mdc/catalog.service.js
subsystem/frontend/src/services/mdc/search.service.js
subsystem/frontend/src/services/mdc/provider.service.js
```

Functions:

```javascript
getBackendHealth()
getDemoHealth()
getCatalogFilters()
searchServiceDiscovery(payload)
validateProviderPublication(payload)
publishProviderPublication(payload)
getProviders()
getProvider(providerId)
```

Shared Marketplace-like endpoints use the configured shared prefix:

```text
/api/health
/api/catalog/filters
/api/service-discovery/search
/api/provider-publication/validate
/api/provider-publication/publish
/api/providers
/api/providers/{provider_id}
```

Provider IDs are encoded with `encodeURIComponent`.

## 5. Demo-only service module

Created:

```text
subsystem/frontend/src/services/mdc/demoAdmin.service.js
```

Functions:

```javascript
getDemoBackendStatus()
runFusekiSmokeTest()
regenerateRdf()
reloadFuseki()
previewProviderPublication(payload)
simulateProviderUpdate(payload)
```

Demo-only endpoints use the configured demo prefix:

```text
/api/demo/service-discovery/backend-status
/api/demo/service-discovery/fuseki-smoke-test
/api/demo/service-discovery/regenerate-rdf
/api/demo/service-discovery/reload-fuseki
/api/demo/provider-publication/preview
/api/demo/provider-publication/simulate-update
```

## 6. Endpoint boundary rules

The endpoint boundary is explicit:

- Shared Marketplace-like endpoints are in `health.service.js`, `catalog.service.js`, `search.service.js`, and `provider.service.js`.
- Demo-only admin and provider simulation endpoints are isolated in `demoAdmin.service.js`.
- Demo admin endpoints were not added to shared search/provider modules.
- No frontend code points directly to Fuseki.

## 7. Files created and modified

Created:

```text
docs/03_mdc_demo_frontend_api_client_report.md
subsystem/frontend/src/services/mdc/client.js
subsystem/frontend/src/services/mdc/health.service.js
subsystem/frontend/src/services/mdc/catalog.service.js
subsystem/frontend/src/services/mdc/search.service.js
subsystem/frontend/src/services/mdc/provider.service.js
subsystem/frontend/src/services/mdc/demoAdmin.service.js
subsystem/frontend/src/services/mdc/index.js
```

Modified:

```text
subsystem/frontend/public/config.js
subsystem/frontend/src/config/runtimeConfig.js
```

No F1 demo pages or MDC UI components were modified in F2.

## 8. Confirmation that no UI pages were wired to backend yet

Confirmed:

- No `src/pages/demo/` file was modified.
- No `src/components/mdc/` UI component was modified.
- No F1 page imports the new service layer.
- No backend call is triggered by page render, build, or module import.

## 9. Confirmation that no .env or package changes were made

Confirmed:

- No `.env` file was added.
- `package.json` was not modified.
- `package-lock.json` was not modified.
- No packages were installed or removed.
- No backend code was changed.

## 10. Commands run and results

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

Generated demo routes remained:

```text
/demo
/demo/admin-audit
/demo/consumer-search
/demo/provider
```

Build also reported the existing lint warnings above and:

```text
Browserslist: caniuse-lite is outdated.
```

No package update was performed.

## 11. Recommended next phase: F3 Dashboard backend status integration

Recommended F3 scope:

- Connect `/demo` dashboard status cards to:
  - `GET /api/health`
  - `GET /api/demo/health`
  - `GET /api/demo/service-discovery/backend-status`
- Add loading, success, and error states.
- Keep provider, search, and admin action endpoints disconnected until their dedicated phases.
