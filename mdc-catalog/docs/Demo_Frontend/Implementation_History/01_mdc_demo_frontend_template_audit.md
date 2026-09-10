# MaaSAI MDC Demo Frontend Template Audit

## 1. Executive summary

The active frontend template is located at `subsystem/frontend`, not at the repository root. It is a Next.js 14 JavaScript application using the Pages Router, PrimeReact, PrimeFlex, Sass, Keycloak authentication, and a MaaSAI-branded shell with sidebar/topbar/footer layout.

The template is suitable as a starting point for a temporary MDC Demo Console because it already has:

- A central layout and navigation shell.
- Route access metadata and Keycloak-backed route guards.
- PrimeReact examples for tables, forms, dialogs, dropdowns, calendars, status tags, toasts, charts, and sidebars.
- Reusable dashboard-style components such as KPI cards, status strips, filter bars, command panels, alarm feeds, and result/entity directories.
- A runtime config mechanism via `public/config.js`.

Main gaps before implementation:

- No MDC API client exists.
- No backend base URL convention exists for MDC APIs.
- Existing data is mock/static and manufacturing-template oriented.
- Forms are hand-rolled React state with no form or schema validation library.
- Route/menu additions must be kept in sync with `src/config/routes.js` and `src/layout/AppMenu.js`.
- Build succeeds only when Next.js worker spawning is permitted; the first sandboxed build failed with `spawn EPERM`.

## 2. Framework and dependency inventory

Frontend package path:

```text
subsystem/frontend
```

Framework and language:

- Next.js: `14.0.3`
- React: `^18`
- React DOM: `^18`
- Language: JavaScript
- TypeScript: not used; there is no `tsconfig.json`
- Path aliases: `@/*` maps to `./src/*` in `jsconfig.json`
- Router: Pages Router, based on `src/pages`
- Package manager: npm, based on `package-lock.json`

Primary dependencies:

- `primereact` `^10.2.1`
- `primeflex` `^3.3.1`
- `primeicons` `^6.0.1`
- `axios` `^1.5.1`
- `keycloak-js` `^23.0.1`
- `chart.js` `4.2.1`
- `reactflow` `^11.11.4`
- `sass` `^1.58.3`
- `classnames` `^2.3.2`

Dev dependencies:

- `eslint` `^8`
- `eslint-config-next` `14.0.3`

Package scripts:

```text
npm run dev    -> next dev
npm run build  -> next build
npm run start  -> next start
npm run lint   -> next lint
```

Configuration files inspected:

- `subsystem/frontend/package.json`
- `subsystem/frontend/package-lock.json`
- `subsystem/frontend/next.config.js`
- `subsystem/frontend/jsconfig.json`
- `subsystem/frontend/.eslintrc.json`
- `subsystem/frontend/public/config.js`
- No `.env*` files were present in `subsystem/frontend`.

Notable `next.config.js` settings:

- `output: 'standalone'`
- `poweredByHeader: false`
- `swcMinify: true`
- `reactStrictMode: true`
- Security headers are configured for all paths.
- `experimental.optimizePackageImports` includes PrimeReact-related packages.
- Image formats include AVIF and WebP.

## 3. Repository structure

Repository root:

```text
documentation/
orchestration/
subsystem/
README.md
```

Frontend application:

```text
subsystem/frontend/
  public/
  src/
    components/
    config/
    hooks/
    layout/
    pages/
    services/
    styles/
  package.json
  package-lock.json
  next.config.js
  jsconfig.json
  .eslintrc.json
```

Main frontend folders:

- `src/pages`: Pages Router route files. Contains public home pages, workspace pages, `_app.js`, `_document.js`, and `404.js`.
- `src/layout`: App shell components such as topbar, sidebar, menu, footer, and layout wrapper.
- `src/layout/context`: React contexts for auth, layout state, menu state, and theme.
- `src/components`: Reusable UI components for dashboard cards, filters, live monitor views, designer UI, command panels, alarms, and entity directories.
- `src/config`: Route access metadata and runtime config helper.
- `src/services`: Current service examples, including Keycloak and fake/mock data services.
- `src/hooks`: `useLiveData` mock/polling-style hook.
- `src/styles`: Sass layout and demo styles.
- `public`: Runtime config, favicon, MaaSAI assets, images, PrimeReact theme CSS, and fonts.

Folders not present:

- No `app/`
- No top-level `pages/`
- No `lib/`
- No `utils/`
- No `docs/` existed before this audit report.

## 4. Routing and layout analysis

The project uses the Pages Router under `src/pages`.

Existing route files:

```text
/
/404
/home/AccessDenied
/home/Brand
/home/Contact
/home/DashboardContent
/home/EmptyPage
/home/ErrorPage
/home/Help
/home/NotFoundPage
/workspace/agents
/workspace/analytics
/workspace/charts
/workspace/crud
/workspace/designer
/workspace/monitor
/workspace/scheduler
```

Important route/layout files:

- `src/pages/_app.js`: wraps all pages with `ThemeProvider`, `AuthProvider`, `LayoutProvider`, route protection, and default `Layout`.
- `src/pages/_document.js`: adds theme CSS link, Google font links, and an inline script for theme initialization.
- `src/layout/layout.js`: defines topbar, sidebar, main content area, footer, menu overlay behavior, and page metadata.
- `src/layout/AppMenu.js`: sidebar menu model and auth-based menu filtering.
- `src/config/routes.js`: central route access control map.

Navigation:

- Sidebar sections: `Home` and `Workspace`.
- Topbar includes MaaSAI logo, menu toggle, theme cycle button, and login/profile action.
- Footer exists through `AppFooter`.

Protected routes:

- Public routes are listed in `ROUTE_ACCESS`, including `/`, contact/help/brand, access denied, error, and 404 pages.
- Workspace routes are currently authenticated.
- Unknown routes default to authenticated via `DEFAULT_ACCESS = 'authenticated'`.
- Role arrays are supported by `canAccessRoute`, although current routes do not use role-specific arrays.

Dynamic routes:

- No dynamic route files were found.

Recommended location for future MDC Demo Console pages:

- Add Pages Router pages under `subsystem/frontend/src/pages/demo/`, for example:
  - `src/pages/demo/index.js`
  - `src/pages/demo/provider.js`
  - `src/pages/demo/consumer-search.js`
  - `src/pages/demo/admin-audit.js`
- Add route access entries in `src/config/routes.js`.
- Add a new sidebar section in `src/layout/AppMenu.js`.
- Reuse the existing default `Layout` through `_app.js`.

## 5. Styling and UI component analysis

Styling system:

- PrimeReact component CSS.
- PrimeFlex utility classes.
- PrimeIcons icon font.
- Sass styles under `src/styles`.
- PrimeReact theme CSS files under `public/themes`.
- Runtime theme switching through `ThemeContext`.

Global style imports are in `src/pages/_app.js`:

```text
primereact/resources/primereact.css
primeflex/primeflex.css
primeicons/primeicons.css
reactflow/dist/style.css
@/styles/layout/layout.scss
@/styles/demo/Demos.scss
```

Theme files:

```text
public/themes/lara-light-indigo/theme.css
public/themes/lara-dark-indigo/theme.css
public/themes/lara-dark-amber/theme.css
```

Reusable UI patterns already present:

- Dashboard cards: `KpiCard`, `MachineCard`, dashboard action card styles.
- Forms: PrimeReact `InputText`, `Dropdown`, `Calendar`, `InputNumber`, `SelectButton`, and custom `ConfigureDialog`.
- Dropdown/filter controls: `FilterBar`, PrimeReact `Dropdown`, `Calendar`.
- Tables: PrimeReact `DataTable` and `Column` in `workspace/crud.js` and `workspace/analytics.js`.
- Status badges: PrimeReact `Tag`, custom status strip and status tone classes.
- Result/detail panels: `Sidebar`, cards, `EntityDirectory`, `AlarmFeed`.
- Dialogs/modals: PrimeReact `Dialog` in CRUD and `ConfigureDialog`.
- Toasts: PrimeReact `Toast`.
- Charts: PrimeReact `Chart` with Chart.js.
- Flow/canvas UI: `reactflow` and designer components.

Suitability for MDC:

- Dashboard cards: suitable for service counts, backend health, Fuseki status, RDF status, and policy checks.
- Forms: suitable for provider preview and search forms, but validation should be made explicit.
- Dropdowns: suitable for catalog filters and part/service options.
- Tables: suitable for audit rows, provider lists, and search result details.
- Tags/status strips: suitable for H5 policy match status, Fuseki smoke status, RDF reload status, and API health.
- Drawers/dialogs: suitable for JSON previews, provider publication preview, and detailed match explanations.

## 6. API integration pattern

Current API-related files:

- `src/services/fake.service.js`
- `src/services/keycloak/keycloak.js`
- `src/config/runtimeConfig.js`
- `public/config.js`
- `src/hooks/useLiveData.js`

Findings:

- `axios` is installed.
- `fake.service.js` imports axios and also demonstrates `fetch`, but it uses an empty `API_URL` and is explicitly a placeholder.
- No shared API client, fetch wrapper, axios instance, MDC service module, React Query, SWR, or server actions were found.
- No environment variable convention exists for backend base URLs.
- Runtime config currently supports Keycloak only.
- Loading/error state patterns exist locally in components and in `useLiveData`, but there is no global API error handling convention.

Recommended future MDC API location:

```text
subsystem/frontend/src/services/mdc/
  client.js
  health.service.js
  catalog.service.js
  search.service.js
  provider.service.js
  admin.service.js
```

Recommended future config convention:

- If using build-time public env vars:

```text
NEXT_PUBLIC_MDC_API_BASE_URL=http://localhost:8000
```

- If following the current runtime config pattern, extend `public/config.js` and `src/config/runtimeConfig.js` with an `mdcApi` section instead of relying only on `.env`.

Suggested future endpoint separation:

- Marketplace/shared calls should stay pointed at shared paths such as `/api/health`, `/api/catalog/filters`, and `/api/service-discovery/search`.
- Demo-only actions should be isolated under `/api/demo/`, matching the backend constraint.

## 7. State/form handling

State management:

- React local state with `useState`, `useEffect`, `useMemo`, `useRef`, and `useCallback`.
- React Context for auth, layout, menu, and theme.
- No Redux, Zustand, MobX, Jotai, Recoil, React Query, or SWR found.

Forms:

- No React Hook Form or Formik.
- No Zod or Yup validation library.
- Existing forms are controlled manually with React state.
- Validation is implemented inline, such as required fields and date ordering in `workspace/crud.js`.
- `ConfigureDialog` supports declarative field schemas for dropdowns, numbers, ranges, select buttons, and groups.

Suitability for MDC forms:

- Provider publication preview form: feasible with PrimeReact controls and manual state for the demo; add structured validation for confidence.
- Consumer search form: feasible with `FilterBar`, `Dropdown`, calendars, and controlled state.
- Dynamic fields based on part type: feasible using a schema-driven pattern similar to `ConfigureDialog`, but it currently needs MDC-specific field kinds and validation.
- Admin/audit status panel: feasible with local state, cards, tables, tags, and toasts.

Risk:

- Manual validation may become hard to maintain if provider publication and search schemas grow. A future implementation should keep validation logic centralized even if no new library is added.

## 8. Authentication/role support

Authentication:

- Keycloak is integrated through `keycloak-js`.
- `AuthContext` initializes Keycloak from runtime config.
- `public/config.js` currently enables Keycloak and defines:
  - `realmUrl`
  - `clientId`
  - `onLoad: 'check-sso'`
- Login/logout helpers are exposed through `useAuth`.
- User display name and roles are resolved from Keycloak token claims.

Authorization:

- `src/config/routes.js` supports:
  - public routes
  - authenticated routes
  - role-specific route arrays
- `src/pages/_app.js` enforces route access.
- `src/layout/AppMenu.js` hides inaccessible menu items.

Role simulation for demo:

- The current code can support Provider, Consumer, and Admin/Audit roles if role names are added to `ROUTE_ACCESS` and menu items.
- For a temporary demo without real role enforcement, route entries can remain authenticated or public depending on the intended demo flow.
- No mock user switcher exists.

## 9. Branding/assets

Brand assets found:

```text
public/layout/images/MaaSAI_logo.png
public/layout/images/MaaSAI_colour_main_icon.png
public/layout/images/MaaSAI_colour_main_letters.png
public/layout/images/01_CERTH.png
public/layout/images/02_UPV.png
public/favicon.ico
```

Other public images:

```text
public/images/product.png
public/images/user_vector.png
public/images/user_vector1.png
public/images/asset-access.svg
public/images/asset-error.svg
```

Brand/style references:

- `documentation/PALETTE.md`
- Sass partials under `src/styles/layout`, including `_brand.scss`
- MaaSAI logo is used in `AppTopbar`.
- Page title is currently `MaaSAI template` in `src/layout/layout.js`.

MDC Demo Console consistency recommendation:

- Keep the existing MaaSAI topbar/sidebar shell.
- Add an MDC Demo Console sidebar section rather than replacing the whole template.
- Reuse the existing brand palette, PrimeReact themes, `KpiCard`, `StatusStrip`, `FilterBar`, `DataTable`, `Tag`, `Dialog`, and `Toast`.
- Rename visible page titles and section labels only during the implementation phase, not during this audit.

## 10. Build/lint command results

Commands were run only because dependencies were already installed in `subsystem/frontend/node_modules` and scripts existed.

### `npm run lint`

Result: succeeded with warnings.

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

First run result: failed inside sandbox.

Failure:

```text
Error: spawn EPERM
```

The command was rerun with approval/escalation because the failure was consistent with sandbox worker-process restrictions.

Second run result: succeeded with the same lint warnings listed above.

Build summary:

```text
Next.js 14.0.3
Compiled successfully
Generated static pages: 18/18
```

Generated routes included:

```text
/
/404
/home/AccessDenied
/home/Brand
/home/Contact
/home/DashboardContent
/home/EmptyPage
/home/ErrorPage
/home/Help
/home/NotFoundPage
/workspace/agents
/workspace/analytics
/workspace/charts
/workspace/crud
/workspace/designer
/workspace/monitor
/workspace/scheduler
```

Additional build note:

```text
Browserslist: caniuse-lite is outdated.
```

No package update was performed.

## 11. Suitability for MDC Demo Console

Overall suitability: good for a temporary demo console.

Strong matches:

- Existing dashboard shell can host the demo.
- Existing sidebar/topbar can provide Provider, Consumer, and Admin/Audit areas.
- PrimeReact gives most required controls without adding packages.
- Existing table/card/status/dialog/toast patterns map well to health checks, catalog filters, search results, provider previews, and admin actions.
- Route access model can support demo roles later.
- Runtime config pattern can be extended for backend base URLs.

Limitations:

- No production-grade API layer exists yet.
- Current workspace pages are sample/manufacturing dashboard pages, not marketplace/demo-specific pages.
- No centralized loading/error UX exists for REST calls.
- No schema validation library exists.
- Keycloak is enabled by default, which may complicate a standalone temporary demo unless the runtime config is adjusted later.

## 12. Recommended implementation phases

### F0 - Frontend audit and inventory

Status: completed by this report.

Files created:

```text
docs/01_mdc_demo_frontend_template_audit.md
```

### F1 - Static MDC Demo Console shell

Likely files:

```text
subsystem/frontend/src/pages/demo/index.js
subsystem/frontend/src/pages/demo/provider.js
subsystem/frontend/src/pages/demo/consumer-search.js
subsystem/frontend/src/pages/demo/admin-audit.js
subsystem/frontend/src/layout/AppMenu.js
subsystem/frontend/src/config/routes.js
subsystem/frontend/src/styles/layout/_mdc-demo.scss
subsystem/frontend/src/styles/layout/layout.scss
```

Work:

- Add demo routes.
- Add sidebar section for MDC Demo Console.
- Add static dashboard cards and page shells.
- Reuse existing layout and PrimeReact components.

### F2 - Backend health/catalog filters integration

Likely files:

```text
subsystem/frontend/src/config/runtimeConfig.js
subsystem/frontend/public/config.js
subsystem/frontend/src/services/mdc/client.js
subsystem/frontend/src/services/mdc/health.service.js
subsystem/frontend/src/services/mdc/catalog.service.js
subsystem/frontend/src/pages/demo/index.js
```

Work:

- Add MDC API base URL convention.
- Add health and backend status calls.
- Add catalog filter loading.
- Add loading/error/status UI.

### F3 - Consumer search UI and result display

Likely files:

```text
subsystem/frontend/src/pages/demo/consumer-search.js
subsystem/frontend/src/services/mdc/search.service.js
subsystem/frontend/src/components/mdc/SearchForm.js
subsystem/frontend/src/components/mdc/SearchResults.js
subsystem/frontend/src/components/mdc/PolicyMatchBadge.js
```

Work:

- Add search form using catalog filters.
- Call `/api/service-discovery/search` or demo-equivalent endpoint as agreed.
- Show ranked results, provider metadata, H5 policy status, and explanations.

### F4 - Provider publication preview UI

Likely files:

```text
subsystem/frontend/src/pages/demo/provider.js
subsystem/frontend/src/services/mdc/provider.service.js
subsystem/frontend/src/components/mdc/ProviderPreviewForm.js
subsystem/frontend/src/components/mdc/PublicationPreviewPanel.js
```

Work:

- Add provider publication preview form.
- Call demo-only preview endpoint under `/api/demo/provider-publication/preview`.
- Display validation, RDF/policy output summaries, and mock publication result.

### F5 - Admin/audit panel for Fuseki/RDF/demo status

Likely files:

```text
subsystem/frontend/src/pages/demo/admin-audit.js
subsystem/frontend/src/services/mdc/admin.service.js
subsystem/frontend/src/components/mdc/AdminStatusPanel.js
subsystem/frontend/src/components/mdc/AuditTable.js
```

Work:

- Add Fuseki backend status.
- Add smoke test action.
- Add regenerate RDF and reload Fuseki actions.
- Add audit/status rows with PrimeReact DataTable and Tag.

### F6 - Dynamic update demo flow

Likely files:

```text
subsystem/frontend/src/pages/demo/provider.js
subsystem/frontend/src/pages/demo/admin-audit.js
subsystem/frontend/src/services/mdc/provider.service.js
subsystem/frontend/src/services/mdc/admin.service.js
subsystem/frontend/src/components/mdc/DynamicUpdatePanel.js
```

Work:

- Add simulate update action.
- Show before/after status.
- Refresh relevant dashboard/search/admin panels.
- Keep all demo-only calls under `/api/demo/`.

## 13. Files/folders likely to be used later

High-likelihood existing files to modify later:

```text
subsystem/frontend/src/layout/AppMenu.js
subsystem/frontend/src/config/routes.js
subsystem/frontend/src/config/runtimeConfig.js
subsystem/frontend/public/config.js
subsystem/frontend/src/styles/layout/layout.scss
```

High-likelihood new files/folders:

```text
subsystem/frontend/src/pages/demo/
subsystem/frontend/src/components/mdc/
subsystem/frontend/src/services/mdc/
subsystem/frontend/src/styles/layout/_mdc-demo.scss
```

Reusable existing components:

```text
subsystem/frontend/src/components/KpiCard.js
subsystem/frontend/src/components/StatusStrip.js
subsystem/frontend/src/components/FilterBar.js
subsystem/frontend/src/components/ConfigureDialog.js
subsystem/frontend/src/components/EntityDirectory.js
subsystem/frontend/src/components/CommandPanel.js
subsystem/frontend/src/components/AlarmFeed.js
```

Reference pages for implementation patterns:

```text
subsystem/frontend/src/pages/workspace/crud.js
subsystem/frontend/src/pages/workspace/analytics.js
subsystem/frontend/src/pages/workspace/monitor.js
subsystem/frontend/src/pages/workspace/agents.js
subsystem/frontend/src/pages/home/DashboardContent.js
```

## 14. Risks/questions before implementation

Risks:

- No MDC API client pattern exists; adding one will require a new convention.
- Backend base URL is not configured; choose `.env` or runtime config before integration.
- Keycloak is currently enabled by default in `public/config.js`; demo access requirements should be decided before pages are added.
- Current routes default to authenticated, so new demo routes will be protected unless explicitly marked public.
- Existing lint warnings should be understood before major layout changes.
- Existing `_document.js` manually includes theme CSS and external fonts, which triggers a Next lint warning.
- Existing sample pages contain hardcoded domain data; implementation should avoid mixing MDC demo behavior with old manufacturing placeholder data.
- Manual form validation may become fragile as provider/search schemas grow.
- The sandboxed build can fail with `spawn EPERM`; local unrestricted build succeeded.

Questions before implementation:

- Should the MDC Demo Console be public for live demos, authenticated only, or role-gated by Provider/Consumer/Admin roles?
- Should MDC API base URL come from `NEXT_PUBLIC_MDC_API_BASE_URL` or from `window.MAASAI_CONFIG` in `public/config.js`?
- Should demo pages live under `/demo/*` or replace current workspace/demo template routes?
- Which endpoints are guaranteed in the first backend demo app milestone?
- Should shared marketplace endpoints and `/api/demo/` endpoints be shown in the same UI, or visually separated?
- Should the frontend display raw RDF/policy payloads, summarized validation results, or both?
