# F8_B Dashboard Role Landing and Sidebar Naming Cleanup Report

## 1. Purpose and scope

This frontend-only UI cleanup makes the MDC dashboard behave as a clean role landing page and updates sidebar labels to clearer MaaS Dynamic Catalogue terminology.

No backend code, provider registration logic, consumer search logic, F7 demo overlay logic, role/login logic, admin/audit backend calls, API service modules, packages, `.env`, runtime config, route config, or Keycloak files were modified.

## 2. Sidebar naming changes

The sidebar group label is now:

```text
MaaS Dynamic Catalogue
```

Sidebar item labels are now:

- `Dashboard`
- `Provider Area`
- `Service Discovery`
- `Demo Admin`

Routes remain unchanged:

- `/demo`
- `/demo/provider`
- `/demo/consumer-search`
- `/demo/admin-audit`

## 3. Provider dashboard changes

When the selected demo role is `provider`, the dashboard shows one role landing panel:

- `Welcome Provider`
- Description about registering a new provider or updating manufacturing capabilities.
- Primary action: `Open Provider Area` -> `/demo/provider`
- `Switch role`
- `Logout`

The lower duplicate Provider card is no longer shown for Provider role.

## 4. Consumer dashboard changes

When the selected demo role is `consumer`, the dashboard shows one role landing panel:

- `Welcome Consumer`
- Description about searching for suitable manufacturing providers.
- Primary action: `Open Service Discovery` -> `/demo/consumer-search`
- `Switch role`
- `Logout`

The lower duplicate Consumer card is no longer shown for Consumer role.

## 5. Admin dashboard changes

When the selected demo role is `admin`, the dashboard shows the role landing panel plus three action cards:

- `Provider Area` -> `/demo/provider`
- `Service Discovery` -> `/demo/consumer-search`
- `Demo Admin` -> `/demo/admin-audit`

The admin role panel no longer includes a separate duplicate row of action buttons.

## 6. Removed misleading Start Demo / duplicate actions

The generic `Start Demo` hero button was removed.

If no demo role is selected, the dashboard shows the role-selection view and no provider/consumer/admin action cards. This avoids dashboard navigation into pages that would only show the empty role-selection message.

Provider and Consumer selected-role views now show one clear action each, not a repeated role action plus a lower duplicate card.

## 7. MaaSAI theme preservation

The page continues to use existing PrimeReact cards, buttons, icons, theme classes, light card surfaces, existing spacing, and current primary/outlined button styles.

No new theme, design system, palette, or dependency was introduced.

## 8. Files modified

- `subsystem/frontend/src/pages/demo/index.js`
- `subsystem/frontend/src/layout/AppMenu.js`
- `docs/29_mdc_demo_dashboard_role_landing_sidebar_cleanup_report.md`

## 9. Commands run

- `Get-Content -Path C:\Users\Elahi\.codex\attachments\ecb1aa07-0f20-4c76-a196-b51a5a071359\pasted-text.txt`
- `Get-Content -Path subsystem/frontend/src/pages/demo/index.js`
- `Get-Content -Path subsystem/frontend/src/layout/AppMenu.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/DemoRoleGuard.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/demoAuth.js`
- `rg -n "Start Demo|Provider Workflow|Provider Demo|Consumer Search|Admin Tools|Admin / Audit|MDC Demo Console|MDC Demo\\b|Project|Algorithm|Dataset|Resource|Workspace|Fuseki|RDF|SPARQL|H5|payload" subsystem/frontend/src/pages/demo/index.js subsystem/frontend/src/layout/AppMenu.js`
- `rg -n "Start Demo|Provider Workflow|Provider Demo|Consumer Search|Admin Tools|Admin / Audit|MDC Demo Console|MDC Demo\\b" subsystem/frontend/src/pages/demo/index.js subsystem/frontend/src/layout/AppMenu.js`
- `git status --short subsystem/frontend/src/pages/demo/index.js subsystem/frontend/src/layout/AppMenu.js docs/29_mdc_demo_dashboard_role_landing_sidebar_cleanup_report.md`
- `npm run lint` from `subsystem/frontend`

## 10. Manual verification notes

Recommended browser checks while the user runs `npm run dev`:

1. Open `http://localhost:3000/demo`.
2. With no selected demo role, confirm only the role-selection actions are shown under the dashboard intro.
3. Select Provider and confirm `Welcome Provider`, `Open Provider Area`, `Switch role`, and `Logout` are shown with no duplicate Provider card.
4. Select Consumer and confirm `Welcome Consumer`, `Open Service Discovery`, `Switch role`, and `Logout` are shown with no duplicate Consumer card.
5. Select Admin and confirm the action cards are `Provider Area`, `Service Discovery`, and `Demo Admin`.
6. Confirm the sidebar group is `MaaS Dynamic Catalogue`.
7. Confirm sidebar items are `Dashboard`, `Provider Area`, `Service Discovery`, and `Demo Admin`.
8. Confirm the provider, consumer search, and admin routes still open.

## 11. Remaining limitations

No browser screenshot verification was run in this session. Role-selection mechanics remain the existing implementation and were not redesigned.
