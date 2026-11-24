# Stage 1B — Integrate the existing MaaSAI demo frontend with the accepted MDC backend

Date: 2026-11-24. Stage 1 accepted. This is a focused implementation task, not a new frontend design or production release.

## 1. Objective and non-negotiable constraints

Upgrade the existing application at `mdc-catalog/demo-frontend/` in place. Demonstrate real provider registration and editing and real consumer discovery using the accepted Stage 1 backend. Maximum reuse, minimum modification.

- Retain the existing MaaSAI branding/theme, Next.js Pages Router, React, PrimeReact, layout/navigation, forms, result components, Provider/Consumer/Admin pages, Keycloak login/logout, role selection and route guards.
- Do NOT remove Keycloak, introduce a second login system, replace the UI, create a frontend project, add UX-only components, change frameworks, redesign pages, or broadly refactor dependencies.
- Change existing API services, payload builders, response handling and necessary event handlers first. Add only essential functional controls/transport code when there is no existing suitable mechanism. Reuse existing forms, tables, dialogs, inputs and status components.
- No backend API, ontology, database schema, Django authentication, sync, Vercel project configuration or Production changes. No Stage 2 or GitLab release. Keep all actual testing isolated to the accepted validation database and disposable records. Do not simulate persistence, publication or search results.
- Frontend may run locally (localhost:3000); no new remote frontend deployment required or authorized. No production-quality UI scope.


## 1A. Mandatory MaaSAI brand alignment — supplied Brand.js reference

The operator supplied the official MaaSAI template `Brand.js` on 2026-11-24. It explicitly identifies itself as the source of truth for MaaSAI brand identity. The relevant specification is transcribed here so Codex does not need access to the ChatGPT attachment.

| Official colour | Exact hex | Intended usage |
| --- | --- | --- |
| Brand Navy | #223F61 | Headers, primary surfaces, sidebars, key UI accents |
| Brand Orange | #E78C3A | CTAs, highlights, key actions, focus rings |
| Warm Sand | #D8D1BE | Section dividers, neutral cards, supportive backgrounds |
| Off-White | #F3F2EE | Page background, large neutral areas |
| Ink | #262626 | Body copy, headings and line icons on light surfaces |

Official CSS tokens from Brand.js:

```css
:root {
  --brand-navy:   #223F61;
  --brand-orange: #E78C3A;
  --brand-sand:   #D8D1BE;
  --brand-bg:     #F3F2EE;
  --brand-ink:    #262626;
}
```

Equivalent SCSS variables use the same names prefixed with $. Typography: Outfit (Google Fonts), weights 300, 400, 500, 600, 700, 800. Brand reference samples are Display 64/80 and Body 18/28 (font size/line height). Keep existing practical form/table/component sizing rather than imposing display sizes on all elements. Ensure readable contrast, including dark text on orange and white on navy as specified by the reference's contrast intent.

First inspect current global styles, layout/theme assets, PrimeReact overrides and font loading. If already compliant, retain them; otherwise make the smallest necessary shared theme/token/font adjustments. Apply consistently to existing demo navigation, Provider/Consumer/Admin pages, forms, buttons and result/status components; retain the existing MaaSAI logo and layout. Preserve semantic warning/error/success cues and accessible keyboard focus. Reuse existing font-loading mechanism and approved existing assets; verify that Outfit actually loads (document any fallback or offline limitation).

Do not add a new Brand page, swatches, copy-to-clipboard functions, design-system showcase, Tailwind, new UI libraries, new navigation, or visual-only components. Brand.js is a design reference, not a new runtime feature or a requirement to copy its React component. Do not restyle the Keycloak-hosted login theme or change the identity server. This limited brand alignment is explicitly authorized within Stage 1B and does not relax the maximum-reuse/minimum-modification constraint.

Acceptance: record whether existing styles already matched; list any theme files changed; verify the exact palette, Outfit typography and retained layout in the running demo (screenshots or sanitized computed-style evidence where feasible). Brand alignment and Keycloak preservation are both required; do not mark unverified visual checks as passed.

## 2. Evidence and targets

Repository: samola4real/mdc_v1; original checkout C:/Users/Elahi/Desktop/mdc_v1. Frontend path mdc-catalog/demo-frontend/. Latest committed frontend change 06df31c (final alignment). Prior audit baseline 39e4570cc7839806e1db2a03bf5a7f58437f4acf.

Read the complete frontend audit and its local inspection addendum:
- Branch audit/phase4-frontend-compatibility-20261124, commit 7932f005ec5fd24971f174c57197deaa8eeeeeec
- mdc-catalog/docs/reports_phase4/00_MDC_Existing_Frontend_ReadOnly_Audit.md
- https://github.com/samola4real/mdc_v1/blob/7932f005ec5fd24971f174c57197deaa8eeeeeec/mdc-catalog/docs/reports_phase4/00_MDC_Existing_Frontend_ReadOnly_Audit.md

Read the accepted Stage 1 report:
- Branch phase4/stage1-provider-lifecycle-demo-resume, commit 3f9c8e1441f1bb581f09388b33e482eb98dcf059
- mdc-catalog/docs/reports_phase4/01_MDC_Stage1_Provider_Lifecycle_Demo_Report.md
- https://github.com/samola4real/mdc_v1/blob/3f9c8e1441f1bb581f09388b33e482eb98dcf059/mdc-catalog/docs/reports_phase4/01_MDC_Stage1_Provider_Lifecycle_Demo_Report.md

Read the M6 Marketplace Integration Guide, Joint Test Checklist and Postman collection in mdc-catalog/docs/Partner_API/. They define the frozen canonical contract.

Accepted backend:
- URL https://maasai-mdc-v1-2ps4wdme5-mdc19.vercel.app
- Vercel team/project mdc19/maasai-mdc-v1; deployment dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea; source 004fef8f0db73ef3e12c1035ec470c131dcb99a6.
- Neon mdc_validation, project mute-cell-38148661, branch br-wild-haze-aej09lb1; four migrations applied. 38 requests, 166 assertions, 0 failures. All 13 canonical methods tested; Vercel edge protected; no MDC Bearer or actor required; ETag required; live suite used X-MDC-If-Match.
- Both synchronization flags false. Normal successful writes return accepted/sync_pending/pending. No immediate semantic search visibility for new registrations is promised.
- Public Production https://maasai-mdc-v1.vercel.app remains older and must not be used for lifecycle testing. Do not promote or modify it.

## 3. Git and local baseline

Fetch latest origin/main. Create clean linked worktree and branch phase4/stage1b-frontend-integration (if it exists, inspect and safely reuse or choose unique suffix; no force-push). Compare committed frontend to the audited baseline and identify any later changes before coding.

Original checkout has unrelated uncommitted changes: root .gitignore adds tracked demo index.js ignore rule; demo-frontend/src/pages/demo/index.js replaces Provider role description with REMOVED. Neither is needed for this task. Preserve both exactly; no stash/reset/restore/clean/overwrite/commit of those original changes. Use committed index.js original description. Local and cached remote committed frontend matched (132 tracked files, no local-only/remote-only frontend commits at inspection). No need to reimport historical GitLab repo or unsanitized history. Stage 1 worktrees untouched.

Run baseline dependency/build/lint checks from frontend root in new worktree (existing lockfile, npm ci, Node compatible with documented project runtime). Inspect security/compatibility issues relevant to local demo; report and address only necessary blockers. No indiscriminate npm audit fix, major upgrades or broad reformatting. Never commit node_modules, build output, local environments, credentials or raw Keycloak tokens.

## 4. Preserve and verify Keycloak

Keep AuthContext.js, existing Keycloak client initialization, PKCE, demoAuth.js and DemoRoleGuard.js, existing role selection and login/logout flow. Preserve the current realm/client configuration unless an operator-approved adjustment is necessary to verify the existing client with the local origin.

Verify actual login, logout, Provider/Consumer/Admin access and denial of disallowed routes. Client-side role selection is presentation, not proof of server-side authorization. Do not fabricate tokens or silently disable login if realm/client/accounts are unavailable. Use existing authorized test accounts/operator-assisted login; never ask to paste passwords/tokens in chat or report.

## 5. Minimal protected connectivity

Inspect existing Next.js server/API facilities before implementing anything. Reuse suitable existing server-side integration if present. The browser must never receive the Vercel protection bypass secret (including via NEXT_PUBLIC_*, public/config.js, window.MAASAI_CONFIG, browser storage, debug responses or logs).

For the protected Stage 1 backend use minimal same-origin server-side transport where required; keep destination fixed to approved Preview, route/method allowlist, restrict IDs to the dedicated disposable demo/test scope for writes, check verified Keycloak access token issuer/audience/expiry/signature and intended authorized role at the server boundary, not arbitrary client-side role strings or roles from unrelated clients. Deny anonymous and Consumer writes. Retain existing Provider/Admin demo semantics without inventing a general provider ownership system. If intended audience/role configuration cannot be verified, stop live write testing and report the operator prerequisite; do not weaken checks. Use server-only approved bypass mechanism, preserve ETag and status/error bodies, avoid logging tokens, no open proxy or arbitrary forwarding. Do not send MDC lifecycle Bearer/actor headers to Django. If existing secure connectivity works, do not create extra transport components. Keep local server loopback-only for the demonstration. No new remote hosting or changes to Vercel protection. Document required local configuration names and startup commands with placeholders only.

## 6. Existing API and UI changes

Use the audit's file-by-file findings and frozen M6 contract. Make small scoped edits; inspect existing code first, avoid wholesale rewrites.

### Shared client
Extend src/services/mdc/client.js as needed: GET/POST remain compatible; PATCH/DELETE, header-aware responses and structured errors. Preserve resource-specific exact strong ETag; send current precondition for PATCH/DELETE. Use the documented X-MDC-If-Match alias on this Vercel transport where necessary; preserve standard If-Match contract. Retain receipt publication_id and sync state on errors. Do not blindly retry ambiguous mutations.

### Provider area
Reuse ProviderDemoPanel.js, existing registration/update forms, tables, ProviderActionResult.js, ProviderPayloadPreview.js, providerPayloadBuilder.js, existing services.
- Preview/validate: POST /api/provider-publication/validation. Registration: POST /api/provider-publication. Use required controlled category/family/support status, stable provider-prefixed offering ID, structured supported_part_types and canonical family/part-type/generic/custom maps. Do not send legacy action, unsupported fields or free text as controlled values. Preserve provider-entered custom fields in correct canonical custom maps. Use existing filters/controlled vocabulary.
- Existing provider: GET /api/providers/{provider_id}; GET /api/providers/{provider_id}/offerings; GET /api/offerings/{offering_id}. No canonical global provider-list endpoint; use explicit ID lookup and existing table, not a new backend endpoint. Remove static writable Tasowheel defaults and demo-state fallback. Hydrate actual provider/offering state, including capabilities and independent ETags; show 404 honestly.
- Update provider and offering separately with canonical PATCH. Send changed scalars only and complete selected maps preserving untouched siblings. Immutable identity/classification not editable in PATCH. Do not overwrite fields with stale template defaults. Preserve existing form/layout wherever possible. If one Save button edits both entities, make the separate operations and partial outcome explicit, or reuse separate existing controls. No claim of atomic cross-resource transaction.
- Support adding same-category independent offering with POST /api/providers/{provider_id}/offerings. Minimal add/delete actions using existing controls if feasible; DELETE offering and provider only for authorized disposable demo IDs, confirmation and current ETag. No elaborate multi-offering UI. Keep complete backend lifecycle accessible with Postman if optional UI affordances cannot be added without major redesign; report exact scope, do not claim unimplemented coverage.
- Show real validation/registration/update/delete receipts and pending sync state. Handle 400/404/409/412/428/503 correctly, refresh state on stale ETag, on possible committed 503 inspect resource/publication before retry. Never portray pending publication as semantic discovery.

### Consumer area
Keep ConsumerSearchMockup, search form, filters, result list, accordion and formatters. Preserve GET /api/catalog/filters and POST /api/service-discovery/search. Remove demo overlay generation, demo provider-state calls and simulated match messages. Render actual canonical result_count, offering identities, match status/score, matched/unmatched/unknown capabilities. No synthetic fallback results. Do not silently substitute stale vocabulary as authoritative. Verify Tasowheel and Precipart baseline query. Newly registered provider may not be discoverable until Stage 2; display truthful state, not manufactured match.

### Admin area
Keep existing route, Keycloak role and layout. Retain compatible shared health/filter/status checks; remove/hide unsupported demo-only actions (regenerate RDF, reload Fuseki, simulated provider state and obsolete demo status). Do not invent a public sync endpoint, show fake DB/Fuseki health, or build new dashboard. Health is liveness only.

## 7. Acceptance and verification

Run scoped unit/service/payload tests where existing tooling permits; verify canonical payloads, map preservation, ETag routing, errors and protected transport authorization. Run npm lint/build and start actual existing application. Verify UI theme/layout preserved, login/logout and each intended role's access (incl unauthenticated/Consumer denied provider writes). Use real browser/manual smoke if available; if operator credentials or browser unavailable report PARTIAL/BLOCKED, do not mark unexecuted steps passed.

Use unique disposable IDs with dedicated scope; never mutate Tasowheel, Precipart, existing providers or Production. From existing UI prove:
1. Consumer: canonical filters and spur-gear results, no overlays.
2. Provider: validate and register a disposable provider/first offering, show pending publication, retrieve by ID and verify actual state; update provider and offering with ETags and confirm persisted changes. Core registration and editing are mandatory for PASS.
3. Where UI add/delete controls implemented, exercise independent second same-category offering, sibling preservation and confirmed deletion. Otherwise demonstrate remaining lifecycle via approved disposable API tests and clearly distinguish UI versus API coverage.
4. ETag stale handling, rejection of unauthorized calls, no browser-visible bypass secret. No new provider search match requirement while sync disabled.
5. Cleanup all disposable operational provider/offering records with fresh ETags; verify final 404s and if available sanitized read-only Neon counts. Retained audit/outbox history expected. If ambiguous write inspect state before retry. Preserve original Production alias, Stage 1 deployment, sync flags, real providers and unrelated local edits.

## 8. Commit/report workflow

Commit only reviewed frontend implementation, necessary scoped tests/documentation and report; separate code commit(s) from report commit. Do not modify backend or other unrelated paths. Push the dedicated task branch to GitHub, not main or GitLab. Do not merge.

Mandatory report (publish even PARTIAL/BLOCKED):
`mdc-catalog/docs/reports_phase4/02_MDC_Stage1B_Existing_Frontend_Integration_Report.md`.

Include verdict, baseline/implementation SHA, exact changed files and rationale, reused components, MaaSAI Brand.js palette and typography compliance evidence, Keycloak and role evidence, protected transport design and secret-handling verification, endpoint/payload/ETag matrix, actual UI vs API tests and counts, lint/build/browser evidence, cleanup, Stage 1/Production preservation, screenshots or sanitized evidence if available without sensitive material, startup instructions and operator prerequisites, known limits/Stage 2 dependency, report link. Distinguish verified from inferred/not verified. Do not include credentials, tokens, sensitive exports or unnecessary generated artifacts.

Final response: verdict, branch, implementation SHA, report SHA/link, minimal changed files, startup commands, confirmed Keycloak/browser evidence, core provider registration/update and real discovery results, optional lifecycle UI coverage, cleanup and blockers. Stop after Stage 1B. No Stage 2, remote frontend deployment, or Production promotion.
