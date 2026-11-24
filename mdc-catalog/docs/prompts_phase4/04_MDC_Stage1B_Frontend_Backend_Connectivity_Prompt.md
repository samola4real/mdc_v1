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


## Resume — operator-provided Preview access and automatic startup configuration

The operator is frustrated by repeated manual configuration. Do not ask them to edit .env.local again. Continue from the latest existing Stage 1B branch (last report e3716b3cd8e11bda8a428be43099f9b186261cae), using the correct worktree and localhost:3000. Prior port 3001 instructions are superseded. The operator has authorized Codex to configure the local server and restart the identified Stage 1B process. Use the replacement approved Vercel bypass supplied through private operator input, never a Git-tracked prompt/report. A previously disclosed credential should be rotated/revoked; do not reproduce it.

- Accept the approved replacement secret via secure local operator input or existing authorized server-only credential mechanism. Write/update exactly one MDC_VERCEL_PROTECTION_BYPASS assignment in the correct worktree's ignored .env.local, preserving other entries. Verify Git ignore and actual Next.js environment loading without displaying the value. Configure persistent server-side startup loading: the pilot must not type a bypass key on every launch. Never place it in NEXT_PUBLIC_*, public/config.js, client bundles, committed files or startup output. If subsequently hosted, configure its server environment separately; pilots only use normal Keycloak login.
- Restart the identified Stage 1B listener on localhost:3000 with the correct build; verify actual server-side protected Preview health with the configured credential and report status only. Separate this transport check from authenticated browser acceptance. Do not stop unrelated processes.
- Resolve approved Keycloak audience and role source using existing authorized configuration. If administrator confirmation is unavailable, provide one precise request for both values and do not repeat the same investigation; record Preview transport separately from Keycloak relay acceptance. Do not disable verification or guess authorization settings.
- Finish the remaining authenticated checks in the original task once configuration is approved. Keep the report updated, preserve UI and infrastructure. No new implementation task, no new deployment, no merge or Stage 2.


## Latest operator decision — reuse central MaaSAI authentication, unblock local demo

This section supersedes the earlier requirement to obtain separate MDC audience/role-source confirmation from a Keycloak administrator for the local demonstration. Operator explicitly approves reuse of existing central MaaSAI authentication and existing authorized demo roles. No second login, new realm/client, administrator request, or pilot-entered configuration.

Resume existing Stage 1B branch at latest reviewed report 41b882047a6a90163da15ea29e825c4f78ad6a09 or its verified descendant. Correct worktree and localhost:3000 unchanged. Server-only Vercel bypass is already configured, loads automatically and passed direct HTTP 200; do not repeat setup or expose it.

Make the smallest necessary change to existing local relay authentication:
- Reuse the real MAASAI Keycloak session/access token from existing myClient adapter. Establish session validity server-side using trusted issuer/JWKS, signature, expiry, token type, subject and authorized party myClient; where necessary validate the token against the issuer's UserInfo endpoint and match subject. Do not trust browser authentication booleans, unsigned claims or user-selected role alone.
- Inspect only relevant sanitized claims from operator's actual signed-in session and existing demo role mapping. Use existing recognized roles from the verified realm and/or myClient claims; exclude unrelated client role claims and never elevate privileges based on selected UI role. Confirm role mapping behavior in actual session. No raw tokens or secrets in output.
- If existing token has suitable audience, validate it against the intended existing application policy. If central login does not issue a dedicated MDC API audience, do not invent one or require a new mapper for this loopback demo: implement an explicitly scoped existing-client session verification policy (including issuer, myClient authorized party, signature/expiry and issuer UserInfo validation) rather than treating arbitrary bearer tokens as MDC resource-server tokens. Retain strict audience-based mode where configured for future deployment. Document this local-only trust decision and limits. If real token/session validation cannot be established, fail closed and report exact blocker; no blanket auth bypass.
- Remove the mandatory manual MDC_KEYCLOAK_AUDIENCE / MDC_KEYCLOAK_ROLE_SOURCE setup dependency for this local existing-client session mode. No second user interaction beyond normal Keycloak login. Preserve loopback-only relay, fixed Preview destination, role restrictions, disposable writes, strong ETags and server-only bypass. This does not authorize exposing relay remotely or modifying production.
- Restart existing Stage 1B frontend on port 3000 with operator approval. Verify actual signed-in health, filters, Provider non-mutating validation, authorized consumer discovery, anonymous and Consumer-only write denial where available. If actual test roles unavailable, report precise missing test. Do not fake claims or results. No live writes, UI redesign, backend/deployment changes or Stage 2.
- Update same Task 04 report, record exact minimal implementation and local session policy, test evidence and remaining production requirements. Push scoped code/report to existing branch without merge.

