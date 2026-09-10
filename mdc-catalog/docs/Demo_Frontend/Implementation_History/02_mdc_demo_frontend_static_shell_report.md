# MaaSAI MDC Demo Frontend - F1 Static Shell Report

## 1. Purpose and scope

F1 implemented a static, navigable MDC Demo Console shell in the existing MaaSAI Next.js frontend. The work is UI-only and uses local mock data.

No backend APIs were called, no API client was added, no `.env` files were created, and no packages were installed or changed.

## 2. Pages created

Created Pages Router routes under `subsystem/frontend/src/pages/demo/`:

```text
/demo
/demo/provider
/demo/consumer-search
/demo/admin-audit
```

Files:

```text
subsystem/frontend/src/pages/demo/index.js
subsystem/frontend/src/pages/demo/provider.js
subsystem/frontend/src/pages/demo/consumer-search.js
subsystem/frontend/src/pages/demo/admin-audit.js
```

## 3. Components created

Created MDC-specific static components under:

```text
subsystem/frontend/src/components/mdc/
```

Files:

```text
AdminAuditPanel.js
ConsumerSearchMockup.js
DemoStatusCards.js
DemoWorkflowPanel.js
EvidenceList.js
ProviderDemoPanel.js
StatusTag.js
mockData.js
```

## 4. Menu/routing updates

Updated route access in:

```text
subsystem/frontend/src/config/routes.js
```

Added public demo-review routes:

```text
/demo
/demo/provider
/demo/consumer-search
/demo/admin-audit
```

Updated sidebar menu in:

```text
subsystem/frontend/src/layout/AppMenu.js
```

Added section:

```text
MDC Demo Console
- Dashboard
- Provider Demo
- Consumer Search
- Admin / Audit
```

Existing Home and Workspace menu sections were left in place.

## 5. Mock data included

Static mock data was added in:

```text
subsystem/frontend/src/components/mdc/mockData.js
```

Included:

- Provider: Tasowheel Oy
- Provider ID: `tasowheel`
- Offerings: Precision gears, Precision shafts
- Active backend: Fuseki + H5 policy
- Fallbacks: RDFLib + H5 policy, Harmonized YAML + H5 matcher
- Dataset: `mdc-service-discovery`
- Demo API namespace label: `/api/demo/`
- Service categories
- Part families
- Gear and shaft part types
- Materials and grades
- Processes
- Certifications
- Mock search result evidence
- Static audit rows

## 6. PrimeReact components used

F1 uses existing installed PrimeReact components only:

```text
Accordion
AccordionTab
Button
Card
Column
DataTable
Divider
Dropdown
InputNumber
InputText
Message
MultiSelect
Panel
Tag
Toast
```

PrimeFlex utility classes are used for layout.

## 7. Files modified

New files:

```text
docs/02_mdc_demo_frontend_static_shell_report.md
subsystem/frontend/src/pages/demo/index.js
subsystem/frontend/src/pages/demo/provider.js
subsystem/frontend/src/pages/demo/consumer-search.js
subsystem/frontend/src/pages/demo/admin-audit.js
subsystem/frontend/src/components/mdc/AdminAuditPanel.js
subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js
subsystem/frontend/src/components/mdc/DemoStatusCards.js
subsystem/frontend/src/components/mdc/DemoWorkflowPanel.js
subsystem/frontend/src/components/mdc/EvidenceList.js
subsystem/frontend/src/components/mdc/ProviderDemoPanel.js
subsystem/frontend/src/components/mdc/StatusTag.js
subsystem/frontend/src/components/mdc/mockData.js
```

Updated files:

```text
subsystem/frontend/src/config/routes.js
subsystem/frontend/src/layout/AppMenu.js
```

No Sass file was needed for F1.

## 8. Confirmation that no backend/API integration was added

Confirmed:

- No MDC API client was created.
- No fetch or axios calls were added.
- No backend URLs were hardcoded.
- Admin action buttons only show local Toast messages.
- Provider action buttons only show local Toast messages.
- Consumer search only reveals local mock result cards.

## 9. Confirmation that no .env file or package change was made

Confirmed:

- No `.env` file was added.
- `package.json` was not modified.
- `package-lock.json` was not modified.
- No packages were installed or removed.
- Existing template pages and workspace samples were not deleted.

## 10. Commands run and results

Commands were run from:

```text
C:\Users\Elahi\Desktop\template-frontend\subsystem\frontend
```

### `npm run lint`

Result: succeeded with warnings.

Warnings were the same existing warnings observed during F0:

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

First sandboxed run failed with the known worker-spawn restriction:

```text
Error: spawn EPERM
```

The command was rerun with approved escalation for `npm run build`.

Escalated result: succeeded.

Build generated 22 static pages, including:

```text
/demo
/demo/admin-audit
/demo/consumer-search
/demo/provider
```

The build retained the same lint warnings listed above and reported:

```text
Browserslist: caniuse-lite is outdated.
```

No package update was performed.

## 11. Remaining risks/questions

- F2 needs a decision on runtime configuration: extend `public/config.js` or use `NEXT_PUBLIC_MDC_API_BASE_URL`.
- Demo routes are public for review in F1; role-gating can be added later if required.
- Search/provider forms are mock-only and use local React state, not shared validation.
- Static data should be replaced by endpoint-backed data in F2/F3/F4 while keeping demo-only actions under `/api/demo/`.
- Existing unrelated lint warnings remain in layout/menu/document files.

## 12. Recommended next phase: F2 Runtime config + MDC API client

Recommended F2 scope:

- Add MDC API base URL convention.
- Add a small MDC API client layer.
- Add health/catalog status functions.
- Wire `/demo` dashboard health cards to backend status.
- Keep demo-only endpoints isolated under `/api/demo/`.
