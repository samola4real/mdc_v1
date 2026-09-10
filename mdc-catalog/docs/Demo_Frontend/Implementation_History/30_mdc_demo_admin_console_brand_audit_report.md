# F8_C Audit: Demo Admin Console and MaaSAI Theme/Brand Usage

## 1. Purpose and scope

This audit reviewed the current MDC Demo Admin page, the frontend MDC admin/service endpoint wrappers, and the MaaSAI brand/theme sources available in the template frontend.

Scope was diagnostic only. No source code changes were made. The goal is to identify which Admin UI elements are static placeholders, which backend-connected data/actions already exist in the frontend, and how the next Demo Admin implementation should align with the MaaSAI visual system.

## 2. Files inspected

- `subsystem/frontend/src/pages/demo/admin-audit.js`
- `subsystem/frontend/src/components/mdc/AdminAuditPanel.js`
- `subsystem/frontend/src/components/mdc/DemoBackendStatusPanel.js`
- `subsystem/frontend/src/components/mdc/DemoStatusCards.js`
- `subsystem/frontend/src/components/mdc/mockData.js`
- `subsystem/frontend/src/components/mdc/DemoRoleGuard.js`
- `subsystem/frontend/src/components/mdc/demoAuth.js`
- `subsystem/frontend/src/services/mdc/client.js`
- `subsystem/frontend/src/services/mdc/demoAdmin.service.js`
- `subsystem/frontend/src/services/mdc/health.service.js`
- `subsystem/frontend/src/services/mdc/catalog.service.js`
- `subsystem/frontend/src/services/mdc/provider.service.js`
- `subsystem/frontend/src/services/mdc/search.service.js`
- `subsystem/frontend/src/pages/demo/index.js`
- `subsystem/frontend/src/layout/AppMenu.js`
- `subsystem/frontend/src/layout/AppTopbar.js`
- `subsystem/frontend/src/layout/context/ThemeContext.js`
- `subsystem/frontend/src/pages/home/Brand.js`
- `subsystem/frontend/src/styles/layout/_brand.scss`
- `subsystem/frontend/src/styles/layout/_main.scss`
- `subsystem/frontend/src/styles/layout/_variables.scss`
- `subsystem/frontend/src/styles/layout/_topbar.scss`
- `subsystem/frontend/src/styles/layout/_menu.scss`
- `subsystem/frontend/public/themes/lara-light-indigo/theme.css`
- `subsystem/frontend/public/layout/images/MaaSAI_logo.png`
- `subsystem/frontend/public/layout/images/MaaSAI_colour_main_letters.png`
- `subsystem/frontend/public/layout/images/MaaSAI_colour_main_icon.png`

## 3. Current Demo Admin page structure

`subsystem/frontend/src/pages/demo/admin-audit.js` renders an admin-guarded page with:

- `DemoRoleGuard allowedRoles={["admin"]}`
- Page heading `MDC Demo Console`
- Page title `Admin / Audit`
- A description calling the page a static semantic catalogue and demo-admin view
- `AdminAuditPanel`

`AdminAuditPanel` renders:

- An info message saying endpoint activation is demo-only
- Three summary cards: `Active backend`, `Fuseki dataset`, `API status`
- A `Demo-only admin actions` panel
- Three action buttons that only display a toast
- A `Static audit log` table sourced from mock data

## 4. Static/junk fields found

| Current Admin UI item | Source | Static or real? | Keep/remove | Reason |
| --- | --- | --- | --- | --- |
| `Active backend: Fuseki + H5 policy` | `AdminAuditPanel.js` | Static | Remove or replace | Hardcoded and not connected to backend status. |
| `Fuseki dataset: mdc-service-discovery` | `AdminAuditPanel.js` | Static | Remove or replace | Hardcoded dataset value can become misleading. |
| `Demo API enabled: static placeholder` | `AdminAuditPanel.js` | Static | Remove | Explicit placeholder. |
| `Shared Marketplace API: unchanged` | `AdminAuditPanel.js` | Static | Remove or replace | Static claim with no live check. |
| `Fallbacks: RDFLib + H5 policy, YAML + H5 matcher` | `AdminAuditPanel.js` | Static | Remove or replace | Could be useful only if loaded from backend status. |
| `Run Fuseki smoke test` button | `AdminAuditPanel.js` | Static/toast-only | Replace | Button does not call `runFusekiSmokeTest`. |
| `Regenerate RDF` button | `AdminAuditPanel.js` | Static/toast-only | Replace carefully | Button does not call `regenerateRdf`; real action is potentially disruptive. |
| `Reload Fuseki` button | `AdminAuditPanel.js` | Static/toast-only | Replace carefully | Button does not call `reloadFuseki`; real action is potentially disruptive. |
| `Static audit log` | `AdminAuditPanel.js`, `mockData.js` | Static | Remove | No real event source is connected. |
| `auditRows` entries | `mockData.js` | Static | Remove from Admin UI | Fake audit entries should not appear in a real admin console. |
| `demoBackends` default cards | `mockData.js`, `DemoStatusCards.js` | Static fallback | Keep only as labelled fallback | Useful for local shell fallback only if clearly labelled. |

## 5. Real API-connected fields found

The current `AdminAuditPanel` is not API-connected, but the frontend already has real service wrappers and one real status component.

`DemoBackendStatusPanel.js` already calls:

- `getBackendHealth()`
- `getDemoHealth()`
- `getDemoBackendStatus()`

It displays backend API health, demo API health, active backend, fallback backend details, Fuseki dataset, shared API status, endpoint activation status, and demo API namespace. It falls back to static data if the backend status endpoint is unavailable, so a future admin console should label fallback values clearly.

## 6. Existing admin/service endpoints available in frontend

| Endpoint/action | Method | Current frontend usage | Safety | Recommended Admin placement |
| --- | --- | --- | --- | --- |
| `/health` | GET | `getBackendHealth` in `health.service.js`; used by `DemoBackendStatusPanel` | Safe read-only | System status |
| `/demo/health` | GET | `getDemoHealth` in `health.service.js`; used by `DemoBackendStatusPanel` | Safe read-only | System status |
| `/demo/service-discovery/backend-status` | GET | `getDemoBackendStatus` in `demoAdmin.service.js`; used by `DemoBackendStatusPanel` | Safe read-only | Service discovery backend status |
| `/demo/service-discovery/fuseki-smoke-test` | GET | `runFusekiSmokeTest` exists; not used by current Admin page | Safe read-only or low risk | Technical actions |
| `/demo/service-discovery/regenerate-rdf` | POST | `regenerateRdf` exists; not used by current Admin page | Potentially disruptive demo mutation | Technical actions with confirmation |
| `/demo/service-discovery/reload-fuseki` | POST | `reloadFuseki` exists; not used by current Admin page | Potentially disruptive demo mutation | Technical actions with confirmation |
| `/demo/provider-publication/state` | GET | `getProviderDemoState` exists; used in consumer search overlay, not Admin | Safe read-only | Demo provider state |
| `/demo/provider-publication/preview` | POST | `previewProviderPublication` exists; provider workflow usage | Demo preview action | Provider Area, not Admin |
| `/demo/provider-publication/simulate-update` | POST | `simulateProviderUpdate` exists; provider workflow usage | Demo state mutation | Provider Area, not Admin |
| `/catalog/filters` | GET | `getCatalogFilters` exists | Safe read-only | Catalogue/search readiness |
| `/providers` | GET | `getProviders` exists | Safe read-only | Provider catalogue summary, if needed |
| `/providers/{providerId}` | GET | `getProvider` exists | Safe read-only | Provider detail drill-in, if needed |
| `/provider-publication/validate` | POST | `validateProviderPublication` exists | Validation action | Provider Area, not Admin |
| `/provider-publication/publish` | POST | `publishProviderPublication` exists | Real publication mutation | Keep out of Demo Admin unless explicitly required |
| `/service-discovery/search` | POST | `searchServiceDiscovery` exists | Search action | Service Discovery page, not Admin |

## 7. Existing admin actions and safety classification

The Admin UI currently shows three admin action buttons, but all three are toast-only placeholders.

Real wrappers already exist:

- `runFusekiSmokeTest`: low-risk read/check action.
- `regenerateRdf`: potentially disruptive demo write/regeneration action.
- `reloadFuseki`: potentially disruptive demo reload action.

`regenerateRdf` and `reloadFuseki` should require explicit confirmation, visible pending/error states, and a clear demo-only label before execution.

## 8. Recommended Demo Admin Console structure

Recommended F8_D structure:

1. Page title: `Demo Admin Console`
2. System status
   - Backend API health
   - Demo API health
   - Active service-discovery backend
   - Fuseki dataset/status
3. Demo provider state
   - Provider count
   - Update/saved-state count if returned by backend
   - Last updated timestamp if returned by backend
   - Link or action to inspect provider demo state
4. Catalogue/search readiness
   - Catalog filter availability
   - Search endpoint readiness if a lightweight check is available
5. Technical actions
   - Run Fuseki smoke test
   - Regenerate RDF
   - Reload Fuseki
   - Use confirmations for POST actions
6. Optional debug payload/result panel
   - Show last action response in a compact read-only panel

## 9. Sections to remove

- Static `Active backend`, `Fuseki dataset`, and `API status` cards from `AdminAuditPanel`
- Static/fake `Static audit log`
- Toast-only admin action behavior
- Placeholder copy such as `Static F1 shell only`
- Any fake audit row sourced from `mockData.auditRows`

## 10. Sections to keep

- `DemoRoleGuard` admin-only protection
- The `Admin / Audit` route can remain as the Admin page route, though the visible title should become `Demo Admin Console`
- `DemoBackendStatusPanel` logic is useful, but should be integrated into the Admin page with clear fallback labeling
- `DemoStatusCards` can be reused as a card renderer if values are supplied from real status calls
- Existing `demoAdmin.service.js` wrappers should be reused before adding new service code

## 11. MaaSAI brand/theme sources inspected

| Brand element | Current source/file | Observed value/style | Recommendation |
| --- | --- | --- | --- |
| Brand source of truth | `pages/home/Brand.js` | Comment explicitly says this is the source of truth for MaaSAI brand identity | Use this as the primary reference for MDC demo page styling. |
| Brand Navy | `pages/home/Brand.js` | `#223F61` | Use for primary headings, key accents, and major admin surfaces sparingly. |
| Brand Orange | `pages/home/Brand.js` | `#E78C3A` | Use for primary actions, highlights, and focus states. |
| Warm Sand | `pages/home/Brand.js` | `#D8D1BE` | Use for subtle section backgrounds/dividers, not dominant panels. |
| Off-White | `pages/home/Brand.js` | `#F3F2EE` | Use as page/background tone where compatible with existing layout variables. |
| Ink | `pages/home/Brand.js` | `#262626` | Use for main text and icons on light surfaces. |
| Brand typography | `pages/home/Brand.js`, `_brand.scss` | Outfit for brand page; app uses Source Sans 3 runtime variables | Keep app typography consistent with the layout unless the MDC pages intentionally adopt the brand-page treatment. |
| Runtime theme variables | `_main.scss` | `--orange:#E8903E`, `--blue:#4A8FD9`, `--bg-card`, `--border`, `--text-dark` | Prefer existing CSS variables in MDC pages to avoid hardcoded drift. |
| PrimeReact light theme | `public/themes/lara-light-indigo/theme.css` | `--primary-color:#334b6f`, `--maasai-orange-color:#e7a048`, `--surface-ground:#f3f2ee` | Align custom MDC styles with these variables where possible. |
| Topbar logo | `AppTopbar.js` | `/layout/images/MaaSAI_colour_main_letters.png` | Reuse existing topbar branding; do not add competing logos inside MDC pages. |
| Topbar/menu interaction colour | `_topbar.scss`, `_menu.scss` | Orange hover/focus, blue active route | Follow this interaction pattern in Admin controls. |

## 12. MaaSAI colour/style findings

The repository has two related colour systems:

- The explicit MaaSAI brand palette in `pages/home/Brand.js`.
- Runtime app/theme variables in SCSS and PrimeReact theme files.

The MDC demo pages should not introduce a third palette. The safest implementation path is to use CSS variables such as `var(--bg-card)`, `var(--border)`, `var(--text-dark)`, `var(--text-medium)`, `var(--orange)`, and `var(--blue)`, while keeping the brand source-of-truth values in mind.

The current layout already uses a light operational style: white cards, soft borders, muted text, orange hover/focus accents, and blue active navigation. That fits the Demo Admin Console better than a marketing-style hero or decorative visual treatment.

## 13. Recommended colour/style usage for MDC demo pages

- Use white or `var(--bg-card)` cards with `var(--border)` borders.
- Use `var(--orange)` or the brand orange as the primary action accent.
- Use `var(--blue)` or the brand navy for status headings, active states, and restrained emphasis.
- Use `var(--text-dark)` and `var(--text-medium)` for readable operational UI text.
- Avoid new hardcoded gradients and one-off colour scales.
- Keep Admin controls compact and status-focused.
- Use PrimeReact components already present in the app: `Button`, `Card`, `Panel`, `Tag`, `Message`, and loading states.
- Use clear warning/confirmation states for RDF regeneration and Fuseki reload.

## 14. Proposed F8_D implementation plan

1. Replace `AdminAuditPanel` static cards with real status sections using `getBackendHealth`, `getDemoHealth`, and `getDemoBackendStatus`.
2. Add a demo provider state summary using `getProviderDemoState`.
3. Add optional catalogue readiness using `getCatalogFilters`.
4. Wire `runFusekiSmokeTest` to the smoke-test button.
5. Wire `regenerateRdf` and `reloadFuseki` only behind confirmation prompts and pending/error states.
6. Remove the static audit log unless a real audit/event endpoint is provided.
7. Style the page with existing layout variables and MaaSAI brand colours.

Suggested next implementation prompt:

```text
Implement F8_D Demo Admin Console in the MaaSAI template frontend. Replace the static AdminAuditPanel content with real frontend service calls for backend health, demo health, service-discovery backend status, provider demo state, and catalogue readiness. Wire Fuseki smoke test, RDF regenerate, and Fuseki reload using existing demoAdmin.service.js functions, with confirmations for POST actions. Do not modify backend, consumer search, role/login, or admin routing. Do not add packages. Do not run npm run build. Preserve MaaSAI theme variables and brand styling.
```

## 15. Risks and safeguards

- `regenerateRdf` and `reloadFuseki` are POST actions and may change demo backend state. They should be admin-only, confirmation-gated, and visibly marked as demo-only.
- Fallback status data can mislead users if it looks live. Any fallback values should be labelled as unavailable/fallback.
- The provider demo state response shape may vary. The UI should parse conservatively and show raw response details only in a debug/details area.
- A fake audit log should not remain in an Admin Console unless it is clearly labelled as sample data.
- Shared API publication endpoints should not be added to Demo Admin unless the product decision explicitly requires real provider publication control there.

## 16. Files modified

- `docs/30_mdc_demo_admin_console_brand_audit_report.md`

No source files were modified.

## 17. Commands run

- `Get-Content -Path C:\Users\Elahi\.codex\attachments\534672c5-0767-43bb-9834-44d1f5c7cdcb\pasted-text.txt`
- `Get-Content -Path subsystem/frontend/src/pages/demo/admin-audit.js`
- `Get-ChildItem -Path subsystem/frontend/src/services/mdc -File | Select-Object -ExpandProperty FullName`
- `Get-ChildItem -Path subsystem/frontend/src/components/mdc -File | Select-Object -ExpandProperty FullName`
- `Get-ChildItem -Path subsystem/frontend/src -Directory | Select-Object -ExpandProperty FullName`
- `Get-Content -Path subsystem/frontend/src/components/mdc/AdminAuditPanel.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/DemoBackendStatusPanel.js`
- `Get-Content -Path subsystem/frontend/src/services/mdc/catalog.service.js`
- `Get-Content -Path subsystem/frontend/src/services/mdc/provider.service.js`
- `Get-Content -Path subsystem/frontend/src/services/mdc/health.service.js`
- `Get-Content -Path subsystem/frontend/src/services/mdc/demoAdmin.service.js`
- `Get-Content -Path subsystem/frontend/src/services/mdc/search.service.js`
- `Get-Content -Path subsystem/frontend/src/services/mdc/client.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/mockData.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/DemoStatusCards.js`
- `rg --files subsystem/frontend/src/pages subsystem/frontend/src/layout subsystem/frontend/src/styles subsystem/frontend/public | rg -i "brand|theme|style|uikit|documentation|logo|scss|css|layout|theme"`
- `rg -n "MaaSAI|brand|theme|primary|orange|#|logo|palette|colour|color" subsystem/frontend/src subsystem/frontend/public`
- `Get-ChildItem -Path subsystem/frontend/src/styles -Recurse -File | Select-Object -ExpandProperty FullName`
- `Get-ChildItem -Path subsystem/frontend/public -Recurse -File | Select-Object -ExpandProperty FullName`
- `Get-Content -Path subsystem/frontend/src/pages/home/Brand.js`
- `Get-Content -Path subsystem/frontend/src/styles/layout/_variables.scss`
- `Get-Content -Path subsystem/frontend/src/styles/layout/_brand.scss`
- `Get-Content -Path subsystem/frontend/src/styles/layout/_main.scss`
- `Get-Content -Path subsystem/frontend/src/layout/context/ThemeContext.js`
- `Get-Content -Path subsystem/frontend/src/layout/AppTopbar.js`
- `Get-Content -Path subsystem/frontend/src/styles/layout/_topbar.scss`
- `Get-Content -Path subsystem/frontend/src/styles/layout/_menu.scss`
- `Test-Path docs/30_mdc_demo_admin_console_brand_audit_report.md`

No build command was run.
