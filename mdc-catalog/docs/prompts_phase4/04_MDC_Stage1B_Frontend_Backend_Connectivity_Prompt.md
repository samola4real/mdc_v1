# Stage 1B — Establish live frontend-to-backend connectivity

## Objective
Resolve the current Provider Area error: "The local server needs the approved Keycloak audience and role source." The operator has already accepted Home/sidebar/Contact and demonstrated real Keycloak login/logout and Provider role navigation. Do not repeat UI refinement or redesign.

Use the existing Stage 1B worktree:
`C:/Users/Elahi/AppData/Local/Temp/mdc-stage1b-20261124-4b9fc439/mdc-catalog/demo-frontend`
Branch `phase4/stage1b-frontend-integration`; last reviewed report head `394aaaf7904d5b1102dc0e3322dced2e32513554`, implementation `7006724a7d9762f80c5d870fc09f63804b283612`. Fetch latest refs and verify current head/status, preserve subsequent work. Continue the correct server on http://localhost:3001/; do not use port 3000 or original checkout.

Target: existing protected Stage 1 Preview https://maasai-mdc-v1-2ps4wdme5-mdc19.vercel.app (deployment dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea, accepted source 004fef8f0db73ef3e12c1035ec470c131dcb99a6, Neon mdc_validation). Both semantic sync flags remain off. No new deployment, database, Keycloak client, or backend changes.

## Execute
1. Inspect only frontend README, existing `src/pages/api/mdc/[...path].js`, relevant runtime config and Keycloak token access as needed. Confirm current relay configuration and missing prerequisites. Keep existing authentication and server-side authorization.
2. With operator assistance, confirm intended access-token audience and authorized role claim source for existing MAASAI realm/client myClient from approved Keycloak configuration. Inspect relevant sanitized claims locally only if necessary. Do not infer approved audience from client name or mere token contents. No raw tokens, passwords, cookies or secrets in chat/logs/reports. No unauthorized realm/client changes or weakening token verification.
3. Configure existing server-only environment variables:
   - MDC_KEYCLOAK_AUDIENCE (approved audience)
   - MDC_KEYCLOAK_ROLE_SOURCE (client or explicitly approved realm)
   - MDC_VERCEL_PROTECTION_BYPASS (approved existing Preview protection credential).
   Reuse secure operator-managed values where available; otherwise guide operator to enter them directly into Git-ignored frontend .env.local or secure local server environment. Verify ignore status and presence without revealing values. No browser-visible bypass, no MDC Bearer/actor forwarded to backend. Restart only identified Stage 1B server with operator approval on port 3001.
4. Verify real signed-in browser calls through existing same-origin /api/mdc relay: GET health and catalog/filters (200 and actual canonical vocabulary), Provider page loads without the current configuration/filter error. Validate a disposable provider registration payload via POST provider-publication/validation (no publication write); verify actual response. With authorized Consumer/Admin role, perform canonical spur-gear discovery through UI (expect Tasowheel and Precipart baseline). Verify anonymous and Consumer provider-write denial without making real writes, and no credential leakage. Distinguish direct Preview CLI tests from actual browser relay evidence; only the latter proves frontend connectivity. If a role/account is unavailable, report the precise remaining test.
5. Fix only actual connection defects if necessary, preserve current UI/roles/ETag behavior. Rerun affected checks if source changes. Do not alter wording, layout, forms, disposable ID constraints or sync flags. No live registration/edit/delete tests in this task; those follow separately.

## Acceptance and delivery
PASS for connectivity requires real authorized browser relay success for health/filters, non-mutating provider validation and consumer discovery, plus verified role denial. If operator configuration or role access is missing, report PARTIAL/BLOCKED and exact action needed; do not use mocked results or bypass identity checks. Keep one working local URL and give concise startup/restart instructions. No broad audits.

Update/publish `mdc-catalog/docs/reports_phase4/04_MDC_Stage1B_Frontend_Backend_Connectivity_Report.md` on existing task branch. Include sanitized configuration confirmation, actual route/status results, remaining blockers, local URL and implementation/report SHA; no secret values. Record operator's accepted Task 03 visual checks in the report (Home/sidebar/Contact, login/logout); do not imply Stage 1B lifecycle acceptance. Push only necessary scoped changes/report; no merge, Production changes or Stage 2. Stop after connectivity verification.
