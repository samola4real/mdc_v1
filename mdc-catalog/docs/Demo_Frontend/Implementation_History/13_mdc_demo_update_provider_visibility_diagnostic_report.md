# MDC Demo Update Provider Visibility Diagnostic Report

## 1. Where the Update Existing Provider list comes from

`Update Existing Provider` is rendered in `subsystem/frontend/src/components/mdc/ProviderDemoPanel.js`.

The table data comes from the module-level `offeringRows` constant in that same file. It currently contains two hardcoded Tasowheel offerings:

- `tasowheel_precision_gears`
- `tasowheel_precision_shafts`

The table uses:

```javascript
<DataTable value={offeringRows} ...>
```

## 2. Static mock data or live/demo state

The Update Existing Provider list is static frontend data. It does not read live backend demo state, and it does not read `provider_demo_state.json`.

`src/components/mdc/mockData.js` also contains static provider/offering demo data, including `Tasowheel Oy`, but the current update table is not even driven from those exported arrays. It is driven by the local `offeringRows` constant inside `ProviderDemoPanel.js`.

## 3. Whether registration success updates frontend local state

Registration success does not update the Update Existing Provider list.

`runAction()` calls `simulateProviderUpdate(payload)` for Save/Register and stores the backend response in `actionResult`, but it does not append the newly registered provider/offering to any local list state.

The list is also not held in React state; it is a constant. Because of that, successful registration cannot affect the Update Existing Provider table in the current implementation.

## 4. Whether a backend read endpoint is missing

The inspected demo service layer, `subsystem/frontend/src/services/mdc/demoAdmin.service.js`, exposes these demo provider-publication functions:

- `previewProviderPublication(payload, options)`
- `simulateProviderUpdate(payload, options)`

Both are POST actions. There is no frontend demo service function for reading saved provider demo state or loading `provider_demo_state.json`.

There is a separate shared `getProviders()` function in `src/services/mdc/provider.service.js`, but `ProviderDemoPanel.js` does not use it, and it is not a demo-state read endpoint for the saved demo registration file.

## 5. Recommended minimal fix

Two fixes are possible:

- Frontend session-only append: after a successful `register_provider` save, keep `offeringRows` in React state and append a summary row based on the submitted payload. This would make the new provider visible immediately in the current browser session. It would not survive page refresh unless the backend is queried.
- Durable backend-state load: add a backend demo read endpoint that returns saved provider demo state, then add a frontend service function and load it when the provider page opens or when the user switches to Update Existing Provider.

Recommended path:

1. Add the small frontend session-only append if immediate same-session visibility is needed for the demo.
2. Add a backend read endpoint plus frontend load for durable behaviour across refreshes and separate browser sessions.

## 6. Files inspected

- `subsystem/frontend/src/components/mdc/ProviderDemoPanel.js`
- `subsystem/frontend/src/components/mdc/providerPayloadBuilder.js`
- `subsystem/frontend/src/components/mdc/ProviderActionResult.js`
- `subsystem/frontend/src/components/mdc/mockData.js`
- `subsystem/frontend/src/services/mdc/demoAdmin.service.js`
- `subsystem/frontend/src/services/mdc/provider.service.js` by search reference only, to confirm the existing shared provider read helper is not used by the demo page.

## 7. Files modified

- `docs/13_mdc_demo_update_provider_visibility_diagnostic_report.md`

No frontend source files, backend files, consumer search files, role/login files, admin/audit files, API service modules, packages, runtime config, or `.env` files were modified for this diagnostic.

## 8. Commands run

- `Get-Content` for the inspected files.
- `rg` to find provider state, demo publication, provider list, and offering list references.
- `git status --short` to view the working tree.
