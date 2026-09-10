# F8_A MDC Demo Dashboard and Navigation Cleanup Report

## 1. Purpose and scope

This frontend-only UI cleanup updates the `/demo` dashboard and MDC sidebar labels so the area reads as a MaaS Dynamic Catalogue demo console instead of a generic MaaSAI template page.

No backend code, provider demo logic, consumer search logic, role/login logic, admin/audit backend calls, API service modules, packages, `.env`, runtime config, route config, or Keycloak files were modified.

## 2. Dashboard hero changes

The dashboard hero now uses:

```text
MaaS Dynamic Catalogue Demo Console
```

Description:

```text
Use this demo to show how manufacturing providers register capabilities, how existing provider information can be updated, and how consumers search for suitable MaaS providers.
```

The old temporary wording was removed, and the primary hero action is now `Start Demo`.

## 3. Quick action card changes

The dashboard now shows MDC workflow cards:

- `Provider Workflow`: register a new provider or update existing provider capabilities.
- `Consumer Search`: search for suitable manufacturing providers using part family, part type, material, process and requirement information.
- `Admin Tools`: review demo status and technical backend checks for the MDC demo.

The card routes remain:

- `/demo/provider`
- `/demo/consumer-search`
- `/demo/admin-audit`

Existing role-selection behaviour is preserved. Admin users can see all workflow cards, provider users see Provider Workflow, and consumer users see Consumer Search after selecting a role.

## 4. Sidebar label/item changes

Sidebar group label changed from:

```text
MDC Demo
```

to:

```text
MDC Demo Console
```

Sidebar item labels changed:

- `Provider Demo` -> `Provider Workflow`
- `Admin / Audit` -> `Admin Tools`

The `Dashboard` and `Consumer Search` labels remain as requested. Routes were not changed.

## 5. MaaSAI theme preservation

The page continues to use existing PrimeReact cards, buttons, icons, spacing, surfaces, and theme classes. No new design system, palette, or dependency was introduced.

The dashboard keeps light card surfaces, existing text classes, PrimeIcons, and the current primary action styling.

## 6. Files modified

- `subsystem/frontend/src/pages/demo/index.js`
- `subsystem/frontend/src/layout/AppMenu.js`
- `docs/28_mdc_demo_dashboard_navigation_cleanup_report.md`

## 7. Commands run

- `Get-Content -Path C:\Users\Elahi\.codex\attachments\392be22c-92ac-4a30-8230-874d5d83c3ca\pasted-text.txt`
- `Get-Content -Path subsystem/frontend/src/pages/demo/index.js`
- `Get-Content -Path subsystem/frontend/src/layout/AppMenu.js`
- `Get-Content -Path subsystem/frontend/src/layout/AppTopbar.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/DemoRoleGuard.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/demoAuth.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/DemoWorkflowPanel.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/DemoBackendStatusPanel.js`
- `rg -n "Welcome to the MaaSAI template|Create a Project|View your Projects|Register a Resource|Register an Algorithm|Algorithm|Dataset|Provider Demo|Admin / Audit|Temporary demo UI|MDC Demo'|MDC Demo\\b" subsystem/frontend/src/pages/demo/index.js subsystem/frontend/src/layout/AppMenu.js`
- `git status --short subsystem/frontend/src/pages/demo/index.js subsystem/frontend/src/layout/AppMenu.js docs/28_mdc_demo_dashboard_navigation_cleanup_report.md`
- `npm run lint` from `subsystem/frontend`

## 8. Manual verification notes

Recommended browser checks while the user runs `npm run dev`:

1. Open `http://localhost:3000/demo`.
2. Confirm the hero says `MaaS Dynamic Catalogue Demo Console`.
3. Confirm old template wording is gone from the demo dashboard.
4. Confirm workflow cards are `Provider Workflow`, `Consumer Search`, and `Admin Tools`.
5. Confirm card buttons navigate to `/demo/provider`, `/demo/consumer-search`, and `/demo/admin-audit`.
6. Confirm the sidebar group is `MDC Demo Console`.
7. Confirm sidebar items are `Dashboard`, `Provider Workflow`, `Consumer Search`, and `Admin Tools`.
8. Confirm provider, consumer search, and admin pages still open.

## 9. Remaining limitations

No browser screenshot verification was run in this session. Role filtering remains the existing demo role-selection behaviour and was not redesigned.
