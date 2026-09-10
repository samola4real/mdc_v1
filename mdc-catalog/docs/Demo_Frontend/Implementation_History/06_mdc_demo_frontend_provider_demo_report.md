# MaaSAI MDC Demo Frontend - F5 Provider Demo Integration Report

## 1. Purpose and scope

F5 connected only the Provider Demo page at `/demo/provider` to demo-only provider publication endpoints under `/api/demo/`.

The implementation mimics a provider editing capability information, building a preview payload, and invoking demo preview/simulate actions. It does not persist provider YAML, regenerate RDF, reload Fuseki, or call shared Marketplace provider-publication endpoints.

## 2. Endpoints connected

Connected only:

```text
POST /api/demo/provider-publication/preview
POST /api/demo/provider-publication/simulate-update
```

Used existing F2 service functions:

```javascript
previewProviderPublication(payload)
simulateProviderUpdate(payload)
```

No shared provider-publication endpoints were used.

## 3. Provider form fields

Provider-level fields:

- provider ID
- provider name
- certifications

Offering-level fields:

- offering ID
- offering name
- service category
- part family
- supported part types
- support status

Gear capability fields:

- module min/max
- diameter min/max mm
- gear quality standard
- gear quality max class
- batch size min/max
- lead time min/max weeks
- weight max kg
- materials
- available grades
- processes

Shaft capability fields:

- length max mm
- outer diameter min/max mm
- spline module
- batch size min/max
- lead time min/max weeks
- weight max kg
- materials
- available grades
- processes

## 4. Provider preview payload shape

Payload construction is isolated in:

```text
subsystem/frontend/src/components/mdc/providerPayloadBuilder.js
```

Implemented shape:

```javascript
{
    provider_id,
    provider_name,
    publication_metadata: {
        source_type: 'provider_confirmed',
        confidence: 'declared'
    },
    certifications: [...],
    offerings: [
        {
            offering_id,
            offering_name,
            service_category,
            part_family,
            supported_part_types: [...],
            support_status,
            capabilities: {
                module: { min, max },
                outside_diameter_mm: { min, max },
                gear_quality: { standard, max_class },
                batch_size: { min, max },
                lead_time_weeks: { min, max },
                weight_kg: { max },
                materials: [...],
                available_grades: [...],
                processes: [...]
            }
        }
    ]
}
```

For shaft offerings, `capabilities` uses shaft-specific fields such as `length_mm`, `outer_diameter_mm`, and `spline_module`.

The payload is shown in a collapsed `Payload preview` panel.

## 5. Preview/simulate action behaviour

`Preview validation`:

- Builds the current provider preview payload.
- Calls `previewProviderPublication(payload)`.
- Shows loading state on the button.
- Shows success, validation error, not-implemented, unavailable, or server-error result panels.

`Simulate update`:

- Builds the same current provider preview payload.
- Calls `simulateProviderUpdate(payload)`.
- Shows loading state on the button.
- Uses the same result handling.

Neither button triggers RDF generation, Fuseki reload, or provider YAML mutation.

## 6. Error and 501 handling

The result panel handles:

- `200`: success summary with provider, offering, and status.
- `400`: provider payload rejected with validation details in advanced/debug.
- `404` or network error: demo provider endpoint unavailable.
- `501`: friendly not-implemented message:

```text
Backend demo action not implemented yet.
This UI is ready, but the backend demo provider action is reserved for a later phase.
```

Raw response/error JSON is hidden under a collapsed `Advanced/debug response JSON` panel.

## 7. Files modified/created

Created:

```text
docs/06_mdc_demo_frontend_provider_demo_report.md
subsystem/frontend/src/components/mdc/providerPayloadBuilder.js
subsystem/frontend/src/components/mdc/ProviderPayloadPreview.js
subsystem/frontend/src/components/mdc/ProviderActionResult.js
```

Modified:

```text
subsystem/frontend/src/pages/demo/provider.js
subsystem/frontend/src/components/mdc/ProviderDemoPanel.js
```

## 8. Safety boundary confirmation

Confirmed:

- No shared provider-publication endpoints were used.
- No consumer search endpoint was called from the provider page.
- No RDF regeneration endpoint was connected.
- No Fuseki reload endpoint was connected.
- No Fuseki direct browser call was added.
- No provider YAML mutation or persistence was added.
- No route/menu/auth/runtime config/package/`.env` file was modified.
- No service module was modified.
- No backend code was modified.

## 9. Commands run and results

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

The `/demo/provider` route built successfully.

## 10. Browser/manual verification result

Browser verification was not performed in this run.

Direct backend endpoint checks from PowerShell:

```text
POST /api/demo/provider-publication/preview -> 501
POST /api/demo/provider-publication/simulate-update -> 501
```

This is acceptable for F5. The UI handles 501 as a friendly reserved-for-later backend demo phase.

## 11. Remaining risks/questions

- Backend provider preview/simulate contracts are not implemented yet and currently return 501.
- Once backend returns 200/400 payloads, the response panel should be reviewed against the actual response shape.
- Browser layout should be reviewed manually for dense form sections on smaller screens.

## 12. Recommended next phase: F6 Admin/audit demo actions

Recommended F6 scope:

- Connect admin/audit demo-only actions for Fuseki smoke test, RDF regeneration, and Fuseki reload.
- Keep all admin actions under `/api/demo/`.
- Add loading, success, error, and not-implemented states.
- Avoid any Marketplace/shared endpoint mutation.
