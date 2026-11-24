# Phase 4 — Existing MDC demo frontend: read-only compatibility audit

Date: 2026-11-24. Auditor: ChatGPT. Verdict: REUSE BASELINE; integration work and local/runtime verification required. This is not Stage 1B implementation or acceptance.

## Scope and evidence
Remote source reviewed at GitHub commit `39e4570cc7839806e1db2a03bf5a7f58437f4acf`, directory `mdc-catalog/demo-frontend/`. Compared with frozen M6 contract in `../Partner_API/MaaSAI_MDC_M6_Marketplace_Integration_Guide.md`. Source inspection only; no npm installation, lint/build/browser tests, Keycloak login, API writes, deployment, or local checkout access. No application or infrastructure changes. Report branch only. Stage 1 is independently in progress. Do not modify its worktree/branch.

## Repository provenance
VERIFIED from `../Demo_Frontend/00_frontend_sanitized_snapshot_import_provenance.md` and release mapping: historical MaaSAI GitLab `https://gitlab-cigip.alc.upv.es/maasai/tools/template-frontend.git`, source main SHA `832ad57265bce0889ebea58bc69c031c3b394ee7`, preservation 2026-09-09; 134 application files and 30 historical reports imported. Sanitized snapshot excludes original Git history, secrets, raw realm exports, dependencies/build output. Personal GitHub is controlled development source; official GitLab release via fresh checkout and reviewed synchronization only. Never reimport unsanitized history. NOT VERIFIED: current Windows worktree status, separate historic frontend clone, current GitLab tip, active local runtime and deployment status. Previously reported local edits (including demo index.js) must be preserved, not assumed still present or discarded.

## Reuse constraints (agreed)
Keep existing Next.js/React/PrimeReact application, theme, branding, navigation, routes, Keycloak integration, provider/consumer/admin roles, forms, components and layout. No new frontend project, UX redesign, new authentication system, or gratuitous component/dependency changes. Only necessary service/payload/event-handler adaptation and functional controls. Do not change accepted MDC backend API to accommodate legacy UI. Keycloak frontend login is not the separate MDC lifecycle Bearer gate.

## Verified compatibility findings
Paths below relative to demo-frontend/.

| File / area | Finding | Minimal correction |
|---|---|---|
| package.json, README.md, next.config.js | Next 14.0.3, React 18, PrimeReact 10.x, axios 1.x, keycloak-js 23.x; documented Node 20.18; standalone build and security headers | Verify lockfile, existing runtime, lint/build and applicable security issues before deployment. No broad upgrade without need. |
| public/config.js; src/config/runtimeConfig.js | Keycloak enabled, existing MAASAI realm/client; default MDC localhost:8000; shared /api and legacy /api/demo prefixes | Preserve identity config, use approved Stage 1 target via secure server-side connectivity if protected; public config contains no credentials. |
| src/layout/context/AuthContext.js; src/services/keycloak/keycloak.js; src/components/mdc/DemoRoleGuard.js; demoAuth.js | Existing login/logout, PKCE S256, token refresh on expiry, role guards and selected-role session storage; initialization promise reuse | Keep. Verify real login, logout, redirects, web origins, role mapping and denial behavior. Role guards are presentation only; for server-side writes verify token issuer/audience/expiry/roles and resource authorization as appropriate. Do not trust selected-role storage or arbitrary roles from other clients. |
| src/services/mdc/client.js | GET/POST helpers only, axios request returns response.data and discards headers. Errors normalize status/message/details. | Extend existing helpers with PATCH/DELETE and optional header/status-aware return preserving existing callers. Capture exact resource ETag, forward If-Match or documented Vercel transport alias, retain error receipt including publication_id. |
| src/services/mdc/demoAdmin.service.js | Demo state, preview, simulate-update, RDF regenerate/reload/smoke/status endpoints | Replace lifecycle calls with canonical methods; disable unsupported demo-only admin operations. No new public synchronization API. |
| src/components/mdc/providerPayloadBuilder.js | Register payload action, flat legacy capabilities/custom lists, lacks controlled category/family/support status; update payload has old combined shape and bare part-type strings | Map existing form to canonical registration and separate provider/offering PATCH. Use controlled filters, structured supported_part_types, family/part-type/generic capability maps, custom maps. Free text is not controlled vocabulary. Do not send immutable classification in PATCH. Preserve sibling fields when replacing selected maps. |
| src/components/mdc/ProviderDemoPanel.js | Static Tasowheel defaults/rows; merges demo persistence; fallback shows static rows; selection does not hydrate all real capabilities; simulated preview/save | Reuse forms and table, use explicit provider ID lookup, real offering list/detail, hydrate selected record and ETag; remove static writable fallback. Add only essential controls for add/delete if in scope; avoid blind default overwrites. Use unique disposable test records. |
| src/components/mdc/ProviderActionResult.js | Legacy success 'Saved to demo state'; 404 treated as unavailable endpoint; generic 5xx | Show actual registration/validation/update outcome and publication status. Handle 404 absent, 409 duplicate, 412 stale, 428 missing precondition, 503 possibly committed. Never replay ambiguous create. |
| src/services/mdc/catalog.service.js, search.service.js, health.service.js | Existing canonical shared GET filters, GET health, POST service-discovery/search | Reuse. Verify request and response against M6, retain real filters and backend results. |
| src/components/mdc/ConsumerSearchMockup.js | Real canonical search but merges synthetic demo results from provider demo state; fallback vocabulary | Remove demo overlay and dependency, keep existing form and actual result rendering. Fail/label unavailable controlled filters rather than invent valid values. |
| src/components/mdc/SearchResultsList.js, searchResultFormatters.js | Overlay-specific count/messages; formatter already recognizes matched/unmatched/unknown_capabilities and full_match/partial_match | Reuse accordion/renderers; remove overlay labels; verify actual result_count, distinct offering IDs, match status and score. |
| src/components/mdc/AdminAuditPanel.js | Calls demo health/status/state, regenerate RDF/reload Fuseki actions. | Keep page and role; use available health/filters and honest status; hide/disable unsupported actions. Health is liveness, not DB/Fuseki proof. |

## Deployment boundary
Preferred first use: existing frontend running locally, connected to accepted protected Stage 1 Preview through a minimal same-origin server-side adapter if needed. Reuse any existing suitable server component first; no open generic proxy. Approved server-only Vercel bypass secret never goes to browser or public config; enforce Keycloak authorization before protected calls and allowlist canonical paths/methods, forward ETags. Use controlled demo test data; for remotely accessible UI enforce trusted server-side role/resource checks. No separate MDC login/Bearer in accepted demo profile; no changes to public Production or official GitLab. Verify CORS/preflight and exposed ETag if direct browser connection is approved. Avoid broad infrastructure work.

## Local verification gate (NOT VERIFIED)
After Codex Stage 1 completes, use read-only git commands in original checkout (and any known separate legacy checkout separately):
```bash
cd ~/Desktop/mdc_v1
git rev-parse --show-toplevel
git status --short --branch
git branch -vv
git remote -v
git worktree list
git log -1 --oneline
git log -1 --oneline -- mdc-catalog/demo-frontend
git status --short -- mdc-catalog/demo-frontend
git diff --stat -- mdc-catalog/demo-frontend
git diff --cached --stat -- mdc-catalog/demo-frontend
git ls-files mdc-catalog/demo-frontend | head
```
Inspect any remote URL locally; redact credentials before sharing. A later fetch of origin/main is safe for working files but should be coordinated with current Codex task. Compare frontend paths with remote after fetch. Never reset, stash, clean, overwrite or force-push. Use clean linked worktree only after reviewing and preserving local edits. No local build claim until npm ci/lint/build and real Keycloak/browser tests pass.

## Minimal Stage 1B acceptance proposal
1. Stage 1 PASS and exact protected deployment/binding confirmed; local Git review completed.
2. Confirm existing frontend builds and current Keycloak login/roles; verify demo theme/routes unchanged.
3. Adapt existing service layer and payload builders; provider register/validate, retrieve by ID, update provider/offering using ETag. Preserve complete maps and immutable identities. Add second offering/deletion only through minimal existing controls, with confirmation and disposable records.
4. Verify real canonical consumer search, no synthetic overlay, accurate pending publication state while semantic sync disabled; admin page honest and unsupported controls unavailable.
5. Verify protected connectivity, no browser bypass secret, no unauthorized writes, error/ETag handling and disposable cleanup. Record lint/build/browser/API evidence.
6. Stage 2 later verifies immediate semantic visibility using same UI, no simulated results. Report only verified behavior. No production promotion.

## Estimate and disposition
Approx. one focused engineering day (5–9 hours indicative, not measured) if build, Keycloak and safe connectivity are operational; more if dependency fixes or identity/proxy work is needed. Biggest risks are legacy payload shape and static update defaults, missing ETag headers, and protected transport; not visual layout. No implementation now. After Stage 1 acceptance create the numbered 02 Stage 1B prompt in prompts_phase4/ and report in reports_phase4/. Preserve all existing UI and Keycloak. This report is a remote source audit, not a local repo or deployment readiness certificate.
