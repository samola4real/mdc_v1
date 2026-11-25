# Stage 1B — Existing MaaSAI frontend integration

**Stage 1B verdict — PARTIAL.** The existing application now routes the Provider, Consumer and Admin workflows to the accepted Stage 1 MDC Preview through a local server route. The build, MaaSAI theme, anonymous guards and real Keycloak login challenge were verified. Authenticated browser discovery, provider registration and editing, and logout still require the approved Keycloak and Preview access described below.

| Item | Reference |
| --- | --- |
| Date | 2026-11-24 |
| Fetched `origin/main` and implementation base | `423e8c2eae9113b122fcc731ef4507b95bcfcbd4` |
| Committed frontend on that base | `06df31c4b18685a174d9c3471f707d6468acc657` |
| Audited frontend baseline | `39e4570cc7839806e1db2a03bf5a7f58437f4acf`. The committed frontend diff from this baseline to the fetched main was empty. |
| GitHub task branch | `phase4/stage1b-frontend-integration` |
| Frontend implementation | [`8252d2abaf8683a63e9b6c598fcd40cd50bdb7b6`](https://github.com/samola4real/mdc_v1/commit/8252d2abaf8683a63e9b6c598fcd40cd50bdb7b6) |
| Accepted Stage 1 Preview | [maasai-mdc-v1-2ps4wdme5-mdc19.vercel.app](https://maasai-mdc-v1-2ps4wdme5-mdc19.vercel.app), `dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea`, source `004fef8f0db73ef3e12c1035ec470c131dcb99a6` |
| Report | [Stage 1B integration report](https://github.com/samola4real/mdc_v1/blob/phase4/stage1b-frontend-integration/mdc-catalog/docs/reports_phase4/02_MDC_Stage1B_Existing_Frontend_Integration_Report.md) |

The implementation used a clean linked worktree. The original checkout still has its two unrelated working-tree edits in `.gitignore` and `mdc-catalog/demo-frontend/src/pages/demo/index.js`. The audit, its local inspection addendum and the accepted Stage 1 report supplied the baseline. [Frontend audit and addendum](https://github.com/samola4real/mdc_v1/blob/7932f005ec5fd24971f174c57197deaa8eeeeeec/mdc-catalog/docs/reports_phase4/00_MDC_Existing_Frontend_ReadOnly_Audit.md), [accepted Stage 1 report](https://github.com/samola4real/mdc_v1/blob/3f9c8e1441f1bb581f09388b33e482eb98dcf059/mdc-catalog/docs/reports_phase4/01_MDC_Stage1_Provider_Lifecycle_Demo_Report.md)

## MaaSAI brand and existing application

The starting light theme used the older shared colours and a Source Sans body stack. It already loaded Outfit alongside Source Sans. The four theme files below apply the official tokens through the existing stylesheet and Google Fonts links. Existing layouts, navigation, MaaSAI logo, theme selector, component sizing, semantic status styles and Keycloak-hosted login were retained. [Brand.js reference](../../demo-frontend/src/pages/home/Brand.js), [updated prompt](../prompts_phase4/02_MDC_Stage1B_Existing_Frontend_Integration_Prompt.md)

| Computed token at `/demo` | Exact value | Use |
| --- | --- | --- |
| `--brand-navy` | `#223F61` | Top bar, sidebar, panel headers and primary accents |
| `--brand-orange` | `#E78C3A` | Primary actions and keyboard focus |
| `--brand-sand` | `#D8D1BE` | Supporting surfaces, borders and navigation section labels |
| `--brand-bg` | `#F3F2EE` | Page background and readable sidebar link text |
| `--brand-ink` | `#262626` | Body copy and text on orange actions |

In Edge on `http://localhost:3000/demo`, the page background and body text computed to `#F3F2EE` and `#262626`. The header and sidebar rendered `#223F61`. The sidebar link and Login action rendered Off-White on Navy and Ink on Orange respectively. Keyboard Tab reached Login and showed a 2 px Navy and 4 px Orange ring. The body and Login action computed to Outfit, and the browser reported loaded Outfit faces for weights 300, 400, 500, 600, 700 and 800. The existing logo loaded and the layout and sidebar were present. This browser evidence covers the public demo shell. The role pages use the same shared styles and still need authenticated visual smoke tests.

## Keycloak and Preview transport

The existing Keycloak initialization, `AuthContext`, role selection, `DemoRoleGuard`, login and logout controls remain the app's authentication flow. The browser reached the real MaaSAI realm password form from the existing Login control with `myClient`, S256 PKCE and a localhost redirect. Discovery returned the expected issuer and signing-key endpoint. Anonymous navigation to `/demo/provider`, `/demo/consumer-search` and `/demo/admin-audit` redirected to `/` with the protected controls absent. The login challenge establishes reachability and the first leg of the redirect. Session completion, logout and the authorized role views remain unverified.

The browser sends its current Keycloak access token to the same-origin `/api/mdc` route. The route checks loopback and same-origin access, then verifies the RS256 signature against the configured realm's JWKS, exact issuer, approved audience, expiry, subject, access-token type and authorized party `myClient`. Role authorization uses `resource_access.myClient.roles` or an explicitly approved realm role mapping. Route selection in the UI is independent of server authorization. Provider and Admin can use the provider lifecycle, Consumer and Admin can use discovery, and all three demo roles can use health and filters. Provider write requests also need the `mdc_stage1b_` disposable scope and provider-prefixed offering IDs. [Keycloak JavaScript adapter](https://www.keycloak.org/securing-apps/javascript-adapter), [Keycloak server administration guide](https://www.keycloak.org/docs/26.7.0/server_admin/)

The server pins the destination and allowlists the 13 canonical method/route pairs. It attaches the approved Vercel bypass from a server-only environment variable and forwards JSON plus the documented ETag precondition. Incoming Keycloak Bearer and actor headers are excluded from requests to Django. The browser build scan found neither bypass variable name nor bypass header in `.next/static` or `public/config.js`. Offline transport tests confirmed response ETag and publication receipt preservation. Real browser network verification of an authorized relay still needs the operator setup.

## Canonical workflow coverage

Provider reuses the existing panels, inputs, payload preview, `DataTable`, status tags and receipt area. The form uses current vocabulary, separate provider and offering saves, and real state loaded by ID. The offering form also supports a second offering in the same category and confirmed disposable deletes. The Consumer page reuses its search form, filters, result list, accordion and evidence formatters. It renders the canonical result count, offering identity, match status and score, and matched, unmatched and unknown evidence. Admin reuses the existing route, cards and panels for API liveness and current catalogue vocabulary. Demo overlays, simulated provider state and obsolete admin actions were removed.

| Canonical Preview endpoint | Existing frontend use and payload | Concurrency and result |
| --- | --- | --- |
| `GET /api/health` | Admin API liveness | Displays the API status |
| `GET /api/catalog/filters` | Provider, Consumer and Admin vocabulary | Uses controlled families, categories, part types, materials, processes and certifications |
| `POST /api/service-discovery/search` | Consumer selections and optional requirements | Renders the canonical response |
| `POST /api/provider-publication/validation` | Validate the registration envelope | Returns validation details without a write |
| `POST /api/provider-publication` | Register with provider identity, country and first offering, typed evidence and custom maps | Shows the receipt and reads back the live provider and offering |
| `GET /api/providers/{provider_id}` | Look up a provider by explicit ID | Captures the strong provider ETag |
| `GET /api/providers/{provider_id}/offerings` | Fill the existing offerings table | Selects independent offering IDs |
| `GET /api/offerings/{offering_id}` | Hydrate actual offering fields and capabilities | Captures the strong offering ETag |
| `PATCH /api/providers/{provider_id}` | Save changed provider scalars and selected maps | Sends current provider ETag and reads back the record |
| `POST /api/providers/{provider_id}/offerings` | Create an independent offering with controlled classification and a distinct ID | Shows the receipt and reloads the offerings |
| `PATCH /api/offerings/{offering_id}` | Save changed offering scalars and complete selected maps, retaining unedited entries | Sends current offering ETag and reads back the record |
| `DELETE /api/offerings/{offering_id}` | Confirm removal of a disposable offering | Sends current offering ETag and reloads surviving offerings |
| `DELETE /api/providers/{provider_id}` | Confirm removal of a disposable provider | Sends current provider ETag and clears the removed provider from the form |

PATCH and DELETE send the exact strong `If-Match` from the relevant read. The server uses `X-MDC-If-Match` for this Preview. Writes are separate resource operations. HTTP 400 and 404 surface the rejection or missing resource. HTTP 409, 412 and 428 trigger a readback when applicable. A 503 or ambiguous transport failure retains any available publication ID and status, prompts inspection and triggers a readback before another attempted write. The UI has no automatic write retry. With both Stage 1 sync flags off, a normal write may return `accepted / sync_pending / pending` without semantic visibility. [M6 integration guide](../Partner_API/MaaSAI_MDC_M6_Marketplace_Integration_Guide.md), [M6 joint test checklist](../Partner_API/MaaSAI_MDC_M6_Marketplace_Joint_Test_Checklist.md), [M6 Postman collection](../Partner_API/MaaSAI_MDC_M6_Marketplace_Integration.postman_collection.json)

## Verification results

| Check | Result |
| --- | --- |
| Baseline in the clean worktree | `npm ci`, `npm run lint` and `npm run build` passed on Windows with Node 22.15.0 and npm 10.9.2. The documented Docker runtime is Node 20.18.0. |
| Final local lint and build | Both passed. Scoped JavaScript `no-undef` passed. Next.js built all 20 static pages and the dynamic `/api/mdc/[...path]` route. Existing hook dependency, stylesheet and Browserslist warnings were observed. |
| Offline regression tests | 8 passed, 0 failed. Covered canonical registration, independent PATCH bodies, mutable leaf and sibling preservation, disposable scope, JWT checks, exact ETag and structured 503 handling, and Consumer write denial. The tests used isolated signed fixtures and stubbed upstream responses. |
| Running local HTTP API | 4 of 4 checks passed. Anonymous health and registration each returned 401, the obsolete demo route returned 404, and a cross-origin request returned 403. Each used `Cache-Control: no-store`. |
| Edge browser | Official theme and keyboard focus verified on the demo shell. Three anonymous role-page redirects and the real Keycloak login challenge verified. Signed-in role access, logout, browser discovery and lifecycle calls are pending. |
| Direct protected Preview API | 3 read-only calls using existing Vercel CLI access returned HTTP 200 and contract `1.0`. Health reported `ok`, filters returned 3 part families, and the spur-gear search returned `result_count: 2` with Tasowheel and Precipart. This search was issued directly to the accepted Preview. |
| Provider registration and editing | 0 live registrations, 0 live edits. Validation, persisted readback, stale ETag recovery and publication receipts still need an authenticated browser run. |
| Optional offering lifecycle and cleanup | The same-category add and confirmed delete controls are implemented. 0 live adds and 0 live deletes were executed. No records were created for Stage 1B, so there were no cleanup deletions, final 404s or Neon row counts to report. |

The dependency audit reported 11 findings in the inherited runtime dependency tree (2 critical, 7 high, 2 moderate). The existing versions were retained for this loopback demo. The only runtime dependency added was `jose` for server-side token verification.

The accepted Preview deployment returned `READY`. Its accepted database binding is Neon `mdc_validation`, project `mute-cell-38148661`, branch `br-wild-haze-aej09lb1`, as recorded in Stage 1. Vercel resolved the public Production alias to its existing deployment `dpl_GmWLQStvb3qo551uYYUv4zLiW1XK`, source `b9275258bf4a2455814ad9b2af9621e0a5d01327`. Stage 1B used the accepted Preview for its direct read-only checks and made no backend writes. Its commits are scoped to the existing frontend and this report. [Accepted Stage 1 deployment and isolation evidence](https://github.com/samola4real/mdc_v1/blob/3f9c8e1441f1bb581f09388b33e482eb98dcf059/mdc-catalog/docs/reports_phase4/01_MDC_Stage1_Provider_Lifecycle_Demo_Report.md)

## Local startup and remaining acceptance gate

Run the local frontend from the Stage 1B branch.

```bash
cd mdc-catalog/demo-frontend
npm ci
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Open `http://localhost:3000/demo`. Supply the following through the approved local server environment or a Git-ignored `.env.local` from the frontend directory.

```dotenv
MDC_KEYCLOAK_AUDIENCE=<approved-audience-of-myClient-access-tokens>
MDC_KEYCLOAK_ROLE_SOURCE=<client-or-explicitly-approved-realm>
MDC_VERCEL_PROTECTION_BYPASS=<approved-protected-Preview-bypass>
```

The approved audience and exact role claim source were unconfirmed, and the approved bypass was unavailable in the local server environment. Use authorized Provider, Consumer and Admin test sessions with the existing Keycloak client. Confirm the localhost redirect and web origin as part of completing login. Keep the bypass on the server and use the existing login form for credentials. After these checks, run the baseline Consumer query, complete the disposable Provider lifecycle through the UI, verify stale ETag recovery and role denial, and confirm operational cleanup by re-reading the removed IDs. Accepted Stage 1 records state that semantic sync is disabled. Discovery of a newly registered provider depends on publication and synchronization beyond this stage.

## Exact implementation files

Paths below are relative to `mdc-catalog/demo-frontend/`.

| Files | Change |
| --- | --- |
| `src/pages/_document.js`, `src/styles/layout/_main.scss`, `src/styles/layout/_menu.scss`, `src/styles/layout/_topbar.scss` | Shared Outfit loading, official colours, readable navigation and keyboard focus |
| `public/config.js`, `src/config/runtimeConfig.js`, `src/services/keycloak/keycloak.js`, `src/pages/api/mdc/[...path].js` | Same-origin configuration, existing session token refresh, and fixed-target verified relay |
| `src/services/mdc/client.js`, `src/services/mdc/provider.service.js`, `src/services/mdc/stage1bScope.js`, `src/services/mdc/catalog.service.js`, `src/services/mdc/health.service.js`, `src/services/mdc/index.js` | Header-aware requests, canonical lifecycle services, disposable IDs, current vocabulary and liveness |
| `src/components/mdc/ProviderDemoPanel.js`, `src/components/mdc/ProviderActionResult.js`, `src/components/mdc/providerPayloadBuilder.js`, `src/pages/demo/provider.js` | Reused Provider form and table with live lookup, canonical payloads, conditional saves and receipts |
| `src/components/mdc/ConsumerSearchMockup.js`, `src/components/mdc/ProviderResultAccordion.js`, `src/components/mdc/SearchResultsList.js`, `src/pages/demo/index.js` | Live discovery filters, canonical results and accurate workflow wording |
| `src/components/mdc/AdminAuditPanel.js`, `src/pages/demo/admin-audit.js`, `src/components/mdc/DemoBackendStatusPanel.js` (removed), `src/services/mdc/demoAdmin.service.js` (removed) | Reused Admin route and status panels with current liveness/vocabulary and removal of legacy actions |
| `README.md`, `package.json`, `package-lock.json`, `tests/stage1b.test.mjs` | Local configuration and verification, scoped JWT dependency and regression tests |
