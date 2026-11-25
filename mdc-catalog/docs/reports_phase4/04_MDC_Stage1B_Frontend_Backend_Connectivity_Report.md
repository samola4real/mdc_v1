# Stage 1B — Frontend-to-backend connectivity

## Operator acceptance of core connectivity · 2026-11-24

**Core connectivity — ACCEPTED.** The operator verified the frontend-to-backend request in the browser Network panel after signing in with MaaSAI Keycloak.

| Evidence | Operator observation |
| --- | --- |
| Authenticated request | `GET http://localhost:3000/api/mdc/catalog/filters` |
| Response | HTTP `200 OK` with `application/json` |
| Provider Area | Loaded successfully with the existing session. The previous red error was absent. |

This acceptance covers the signed-in catalogue-filter retrieval and Provider Area load. The earlier sections preserve the direct Preview results and the evidence available before this operator verification.

### Functional testing carry-forward

- Verify non-mutating provider validation through the signed-in Provider relay.
- Verify spur-gear discovery through an authorized Consumer or Admin browser session.
- Verify provider-write denial through an authenticated Consumer-only session.

## Earlier Provider Area follow-up · 2026-11-24

**Verdict — PARTIAL.** The operator reported that normal MaaSAI Keycloak sign-in reached Provider Area and the red error ribbon was gone. The accepted deployed MDC backend independently returned the catalogue filters, a successful non-mutating validation, and the two expected spur-gear matches. This verification window captured zero signed-in requests through the browser relay.

The checks used the existing Stage 1B worktree, implementation `90dcc20a715d8bd0beda30a54696df2823e02d29`, running build `ysT1CIKHxAaUnJnJZc-wu` and existing observer on PID `42432`. The Stage 1B branch matched GitHub at the starting report commit `a07d381c9a7d88e3534c187cb9a43bb4a5c7ec9f`. [Provider Area on the confirmed local origin](http://localhost:3000/demo/provider)

| Endpoint or check | Verified evidence |
| --- | --- |
| Deployed `GET /api/catalog/filters` | Direct server-side request to the fixed protected Preview with its approved credential returned HTTP 200 and contract `1.0`. The catalogue contained 3 part families, 6 materials, 15 processes and 6 certifications. |
| Deployed `POST /api/provider-publication/validation` | Direct server-side request with one disposable validation payload returned HTTP 200 and `valid: true`. The operation was validation only. |
| Deployed `POST /api/service-discovery/search` | Direct search for spur gears returned HTTP 200, contract `1.0` and two results. The IDs were `precipart` (Precipart) and `tasowheel` (Tasowheel Oy). |
| Local evidence collection | The running observer captured a fresh anonymous `GET /api/mdc/catalog/filters` with HTTP 401 and `keycloak_token_required`. This confirms the route and observer were active during the follow-up. |
| Live signed-in browser filters | Pending an observed authenticated `GET /api/mdc/catalog/filters` on the confirmed origin. The operator’s Provider Area observation is recorded above. |
| Remaining signed-in checks | Signed-in health, Provider validation and authorized Consumer or Admin discovery still require browser responses. The Consumer-only write-denial check requires an actual Consumer-only session. |

The operator was asked to reload Provider Area on the same local origin with the existing Keycloak session. A sanitized browser Network status and vocabulary summary can also establish the browser result if the local observer does not see the request. Credentials and authorization headers stay in the browser.

Zero provider records were registered, edited or deleted. The only tracked change in this follow-up is this report.

## Earlier existing MaaSAI session resume

The previous resume below documents the relay implementation and its original verification.

## Existing MaaSAI session resume · 2026-11-24

**Verdict — PARTIAL.** The updated relay is running at [http://localhost:3000/](http://localhost:3000/). The approved loopback session policy removes the mandatory audience and role-source setup for the local demo. Protected Preview transport and the anonymous browser checks passed. The live listener received zero signed-in relay requests during the verification window, so signed-in acceptance is pending.

| Reference | Current evidence |
| --- | --- |
| Updated prompt at `origin/main` | `21ea860933951a62d545044cb0451415458dc2e0` |
| Existing Stage 1B branch and starting head | `phase4/stage1b-frontend-integration` at `41b882047a6a90163da15ea29e825c4f78ad6a09`, matching GitHub |
| Scoped implementation | [`90dcc20a715d8bd0beda30a54696df2823e02d29`](https://github.com/samola4real/mdc_v1/commit/90dcc20a715d8bd0beda30a54696df2823e02d29) |
| Served build | `ysT1CIKHxAaUnJnJZc-wu` from `C:/Users/Elahi/AppData/Local/Temp/mdc-stage1b-20261124-4b9fc439/mdc-catalog/demo-frontend` |
| Local restart | The previously identified PID `41768` was restarted under the existing operator authorization. PID `42432` served the updated build on loopback port 3000. |
| Fixed Preview target | Accepted Vercel deployment `dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea` |

[Updated Task 04 prompt](https://github.com/samola4real/mdc_v1/blob/21ea860933951a62d545044cb0451415458dc2e0/mdc-catalog/docs/prompts_phase4/04_MDC_Stage1B_Frontend_Backend_Connectivity_Prompt.md)

### Local trust policy

The browser continues to send the access token from the existing `myClient` Keycloak adapter to the same-origin relay. The server verifies the pinned MAASAI issuer and JWKS, the RS256 signature, expiration, token type, subject, and `myClient` authorized party. The loopback policy confirms that Keycloak UserInfo accepts that access token and returns the same subject. The server requests that endpoint without caching or redirects. It uses only recognized demo roles in the signed realm and `myClient` claims. A failed issuer check or a mismatched UserInfo subject stops forwarding. [Keycloak UserInfo and certificate endpoints](https://www.keycloak.org/securing-apps/oidc-layers), [OpenID Connect UserInfo](https://openid.net/specs/openid-connect-core-1_0.html#UserInfo)

A configured `MDC_KEYCLOAK_AUDIENCE` retains strict audience validation and requires an approved `MDC_KEYCLOAK_ROLE_SOURCE`. A configured role source alone can restrict the loopback session policy to its chosen claim. In this local run, both settings were absent and the already saved `MDC_VERCEL_PROTECTION_BYPASS` loaded from the Git-ignored environment file. The relay still enforces loopback access, fixed Preview routing, role restrictions, disposable identities and ETag handling. The browser timeout now covers the added UserInfo request as well as signing-key and Preview requests.

The implementation touched the relay, MDC client timeout, existing scoped tests and the frontend setup README. A later hosted resource-server policy requires an explicit approved audience and role source, with deployment and access reviewed separately. The current relay applies its loopback checks in both modes.

### Verification

| Check | Observed result |
| --- | --- |
| Keycloak public discovery | HTTP 200. The advertised issuer, signing-key URL and UserInfo URL matched the pinned endpoints. |
| Offline regression, lint and build | Ten tests passed. They exercised the no-audience session path, subject matching, issuer failure, expired and wrong-client tokens, role-source restrictions, Consumer denial, strict audience enforcement, exact ETags and credential forwarding boundaries. Lint and build passed with existing warnings. These tests used offline signing fixtures. |
| Restart and protected Preview | Local Home returned HTTP 200 from the updated build. The native startup loaded the saved Preview credential. A direct health request from the restarted server to the protected Preview returned HTTP 200 with canonical liveness. |
| Anonymous browser relay | Real fresh-browser requests to health, filters, validation and provider publication returned HTTP 401 `keycloak_token_required` with `no-store`. The two POST inputs were empty JSON. |
| Existing Keycloak sign-in | The browser reached the normal MAASAI `myClient` password form with S256 PKCE and a return URL on localhost:3000. |
| Authenticated browser relay | Live health, vocabulary, Provider validation, authorized spur-gear discovery, and a Consumer-only denial are pending. The operator was asked to refresh the existing signed-in Provider tab. No signed-in role claims were observed in this run. |
| Credential isolation | An exact-value scan of 54 relevant local files and two served responses found zero occurrences. The anonymous responses exposed no bypass header. There were zero backend writes. |

## Earlier operator-approved Preview access evidence

The previous resume below established persistent Preview access before the existing-client session policy was implemented.

## Operator-approved Preview access resume · 2026-11-24

**Verdict — PARTIAL.** The Stage 1B server at [http://localhost:3000/](http://localhost:3000/) loads the saved Preview credential automatically. The restarted process reached the accepted protected Preview and received HTTP 200. Authenticated browser relay acceptance remains gated on the approved Keycloak audience and role source.

| Reference | Current evidence |
| --- | --- |
| Updated prompt at `origin/main` | `9d7ff1abcbc5e8cf70380d491a7d5a8d1d84a651` |
| Existing Stage 1B branch and starting head | `phase4/stage1b-frontend-integration` at `e3716b3cd8e11bda8a428be43099f9b186261cae`, matching GitHub |
| Existing relay implementation | `8252d2abaf8683a63e9b6c598fcd40cd50bdb7b6` |
| Served frontend | Source tree `7006724a7d9762f80c5d870fc09f63804b283612`, prepared Next.js build `ipLk0-E6GacQvxqzZH7B2` |
| Worktree and restart | `C:/Users/Elahi/AppData/Local/Temp/mdc-stage1b-20261124-4b9fc439/mdc-catalog/demo-frontend`. The identified PID `3288` was restarted with operator approval on loopback port 3000. PID `41768` served the same reviewed build after the restart. |
| Accepted protected target | Vercel Preview `dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea`. Pinned `GET /api/health` returned HTTP 200 with canonical liveness. |

[Updated Task 04 prompt](https://github.com/samola4real/mdc_v1/blob/9d7ff1abcbc5e8cf70380d491a7d5a8d1d84a651/mdc-catalog/docs/prompts_phase4/04_MDC_Stage1B_Frontend_Backend_Connectivity_Prompt.md)

### Automatic local configuration

The authorized credential was saved as exactly one `MDC_VERCEL_PROTECTION_BYPASS` assignment in the existing frontend's `.env.local`, preserving the surrounding entries. Git verified the file is ignored and untracked. Separate Next.js loader checks in production and development modes matched the persisted value, and observation after the restarted server's native configuration load confirmed presence in that process. Normal Next.js launches from this worktree load the setting from the file.

The configured value appeared zero times in a scan of 54 local files, including the served-build client assets, the public config and the restart logs, and in the live Home and `/config.js` response bodies. The browser kept the same-origin `/api/mdc` client. The existing relay builds the Preview header on the server and excludes the incoming Keycloak Bearer and actor headers from outbound requests. The updated prompt calls for rotation or revocation of previously disclosed credentials by the Vercel project owner.

### Transport and browser checks

| Check | Actual result |
| --- | --- |
| Server-side protected Preview transport | The saved server-only credential reached the fixed `/api/health` target. HTTP 200 and canonical API liveness were confirmed in the restarted process. This was a direct transport check. |
| Anonymous browser relay | `GET /api/mdc/health`, `GET /api/mdc/catalog/filters`, `POST /api/mdc/provider-publication/validation` and `POST /api/mdc/provider-publication` returned HTTP 401 `keycloak_token_required`. The POST probes used empty JSON. |
| Browser credential isolation | The four responses had `Cache-Control: no-store` and exposed no Preview bypass header. The public environment scan showed zero credential exposure. |
| Existing login | The real MAASAI Keycloak form opened for `myClient` with S256 PKCE and a return origin of `http://localhost:3000`. |
| Signed-in connectivity | Pending an approved audience and role source, followed by test sessions. Positive health and filters, provider validation, spur-gear discovery and Consumer-only write denial still need authenticated browser evidence. No backend writes occurred. |

The restarted server reported `MDC_KEYCLOAK_AUDIENCE` and `MDC_KEYCLOAK_ROLE_SOURCE` absent. The operator was asked for the two non-secret administrator confirmations for `myClient`: the exact intended MDC access-token audience and the approved role source (`resource_access.myClient.roles` or explicitly approved `realm_access.roles`). Once those are confirmed, Codex can set the two entries and restart the identified local process. The operator can then sign in through Keycloak on port 3000 with the available authorized Provider, Consumer-only or Admin test sessions.

The frontend code and accepted Preview were reused for the checks. The only tracked change in this resume is the Task 04 report.

## Earlier port 3000 resume evidence

The following records the previous resume before the operator-authorized Preview credential was applied.

## Resumed verification on port 3000 · 2026-11-24

**Verdict — BLOCKED.** The Stage 1B frontend is running at [http://localhost:3000/](http://localhost:3000/). The new origin reaches the real Keycloak sign-in form and passes the anonymous relay tests. The local Preview credential and the administrator-approved Keycloak audience and role source are still unavailable to this worktree. Actual signed-in relay acceptance is pending.

| Reference | Resumed result |
| --- | --- |
| Fetched `origin/main` | `a17801f897774a116b58394053b9683f7c2bd4bb` |
| Existing task branch and resume base | `phase4/stage1b-frontend-integration` at `d1e9686b7765f20a0fdbc2c598f6bf4430a7dc3d`, matching the fetched remote head |
| Served frontend source and build | Frontend tree from `7006724a7d9762f80c5d870fc09f63804b283612` with existing relay `8252d2abaf8683a63e9b6c598fcd40cd50bdb7b6`. Served Next.js build `ipLk0-E6GacQvxqzZH7B2`, with CSS bytes matching that prepared build. |
| Worktree and listener | `C:/Users/Elahi/AppData/Local/Temp/mdc-stage1b-20261124-4b9fc439/mdc-catalog/demo-frontend`. Port 3000 had no listener at preflight. The verified Stage 1B process is PID `3288` on `127.0.0.1:3000`. |
| Change on this resume | This report is the only committed file. The running server uses the already prepared isolated production build. |

Preflight also observed a separate listener on port 3001. The resumed test used port 3000 for Home, browser API requests and the Keycloak return URL.

### Local configuration evidence

The operator reported entering the existing protection bypass. The absolute Git-ignored file used by this worktree is `C:/Users/Elahi/AppData/Local/Temp/mdc-stage1b-20261124-4b9fc439/mdc-catalog/demo-frontend/.env.local`. It contained one `MDC_VERCEL_PROTECTION_BYPASS` assignment, which was empty on disk at the last check. Next.js parsed the file successfully and reported all three required settings absent. The other scoped worktree `.env.local` locations and Windows environment scopes yielded no alternate value. The protected Preview health check was gated on a nonempty local credential and did not send a request. The operator can save the approved value directly to the frontend file or identify the file they edited by path.

### Keycloak configuration investigation

The tracked runtime config and existing adapter identify the MAASAI issuer and `myClient`. Public discovery and JWKS each returned HTTP 200, with the expected endpoints and an RS256 signing key. The reviewed worktree references contained setup instructions and verification code without an approved client or realm mapper export. The UI merges realm and client role lists for presentation. The server requires an explicit approved authorization claim source. [Keycloak Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)

A MAASAI realm administrator needs to confirm these two items in **Clients → myClient → Client scopes**, including the dedicated scope and any effective linked scopes.

1. **Intended audience.** Identify the exact MDC API audience configured by the effective protocol mapper and emitted in `aud` on access tokens issued to `myClient`. An existing Audience or Audience Resolve mapper and Client scopes → Evaluate for a permitted test user can provide supporting evidence. Enter the approved identifier in `MDC_KEYCLOAK_AUDIENCE`.
2. **Role source.** Confirm the effective mapper and the authorized demo role assignments. Enter `client` in `MDC_KEYCLOAK_ROLE_SOURCE` if the permitted roles are carried in `resource_access.myClient.roles`, or `realm` if `realm_access.roles` is explicitly approved for MDC. Confirm which test users have Provider, Consumer-only and Admin access so each operation can be verified with the intended role.

### Actual browser results on port 3000

| Check | Observation |
| --- | --- |
| Frontend and runtime config | Home returned HTTP 200. The browser selected the relative `/api/mdc` relay. |
| Keycloak sign-in challenge | The real MAASAI password form opened for `myClient` with S256 PKCE and a return origin of `http://localhost:3000`. A test session did not complete in this run. |
| Anonymous health and filters | `GET /api/mdc/health` and `GET /api/mdc/catalog/filters` each returned HTTP 401 `keycloak_token_required`. |
| Anonymous validation and write denial | `POST /api/mdc/provider-publication/validation` and `POST /api/mdc/provider-publication` each returned HTTP 401 `keycloak_token_required` with empty JSON probes. |
| Credential exposure check | The served public config and static build had no Preview credential variable or header markers. All four anonymous responses used `Cache-Control: no-store` and exposed no bypass header. |
| Authenticated acceptance | Pending actual signed-in browser results for health, canonical filters, non-mutating validation, spur-gear discovery and Consumer-only write denial. There were zero backend writes. |

After the approved entries are saved, the identified Stage 1B listener needs an approved reload to consume them. Coordinate personal Keycloak sign-in and run the remaining tests on the same port 3000 origin. Keep the values in the local server environment file. [Vercel Protection Bypass for Automation](https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/protection-bypass-automation)

## Original Task 04 run · earlier port 3001 evidence

The following records the first connectivity attempt and its startup context.

**Verdict — BLOCKED on operator configuration.** The existing relay is present on the running frontend and rejected all four anonymous browser requests. The approved Keycloak audience, role source and Preview credential are still unavailable in the local server configuration. Actual signed-in frontend-to-Preview requests remain pending.

| Reference | Verified or recorded value |
| --- | --- |
| Date | 2026-11-24 |
| Fetched `origin/main` | `a17801f897774a116b58394053b9683f7c2bd4bb` |
| Task branch | `phase4/stage1b-frontend-integration` |
| Clean starting branch tip | `394aaaf7904d5b1102dc0e3322dced2e32513554`, matching the fetched task branch |
| Existing relay implementation | [`8252d2abaf8683a63e9b6c598fcd40cd50bdb7b6`](https://github.com/samola4real/mdc_v1/commit/8252d2abaf8683a63e9b6c598fcd40cd50bdb7b6) |
| Confirmed local origin | [MaaSAI Home](http://localhost:3001/), listener `127.0.0.1:3001`, PID `38508`, frontend build `l_V5qaqm9olxY4KqIkH8c` |
| Worktree | `C:/Users/Elahi/AppData/Local/Temp/mdc-stage1b-20261124-4b9fc439/mdc-catalog/demo-frontend` |
| Fixed Preview target | `maasai-mdc-v1-2ps4wdme5-mdc19.vercel.app`, deployment `dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea`, `READY` in Vercel metadata |
| Accepted backend baseline | Source `004fef8f0db73ef3e12c1035ec470c131dcb99a6`, Neon `mdc_validation` and both semantic sync flags off in the Stage 1 acceptance record |

The operator accepted Task 03 Home, sidebar and Contact visuals and demonstrated Keycloak login/logout and Provider navigation, as recorded in the controlling prompt. This establishes the reviewed UI starting point. Backend relay and lifecycle acceptance have separate evidence. [Connectivity prompt](https://github.com/samola4real/mdc_v1/blob/a17801f897774a116b58394053b9683f7c2bd4bb/mdc-catalog/docs/prompts_phase4/04_MDC_Stage1B_Frontend_Backend_Connectivity_Prompt.md), [accepted Stage 1 backend report](https://github.com/samola4real/mdc_v1/blob/3f9c8e1441f1bb581f09388b33e482eb98dcf059/mdc-catalog/docs/reports_phase4/01_MDC_Stage1_Provider_Lifecycle_Demo_Report.md)

## Diagnosis and sanitized configuration

The current browser config selects the same-origin `/api/mdc` client. The existing relay verifies the access token against the MAASAI issuer and signing keys, approved audience and role source, authorized party `myClient`, expiry and required token claims. The exact error reported by the operator is emitted at the local identity configuration check as HTTP 503 with code `identity_configuration_required`. That check precedes token verification and the outbound request. This mapping was confirmed in source. The signed-in error itself was reported by the operator.

The public Keycloak discovery and JWKS requests both returned HTTP 200. The issuer and signing-key endpoint matched the configuration, and an RS256 signing key was present. The intended MDC audience and approved role source require confirmation from the realm configuration.

| Local server setting | Sanitized verification and action needed |
| --- | --- |
| `MDC_KEYCLOAK_AUDIENCE` | Missing. Use the single MDC API audience approved for access tokens issued to `myClient`. |
| `MDC_KEYCLOAK_ROLE_SOURCE` | Missing. Use `client` for the approved `resource_access.myClient.roles` claim, or `realm` only for explicitly approved `realm_access.roles`. |
| `MDC_VERCEL_PROTECTION_BYPASS` | Missing. Use the existing approved Protection Bypass for Automation credential for `mdc19/maasai-mdc-v1`. |

A Git-ignored `.env.local` was initialized in the existing frontend directory with the three empty entries. Next.js environment parsing succeeded and confirmed the entries were still empty at the last check. The code attaches the Preview credential from the server environment. The outbound header construction excludes the incoming Keycloak Bearer and actor headers. The running build's client assets and its served `/config.js` had no Preview credential variable name or header marker, and the anonymous responses exposed no bypass header. A live signed-in check with the configured credential is still required. The only committed path from this attempt is this report.

## Actual browser evidence

A fresh Edge profile made same-origin requests on `localhost:3001`. Each anonymous rejection returned contract `1.0`, code `keycloak_token_required` and `Cache-Control: no-store`. The two anonymous POST probes used empty JSON. The relay rejected them at its token gate.

| Route | Anonymous browser | Authenticated browser |
| --- | --- | --- |
| `GET /api/mdc/health` | 401 | Pending approved configuration and session. Expected HTTP 200 with API liveness. |
| `GET /api/mdc/catalog/filters` | 401 | Pending approved configuration and session. Must return canonical vocabulary and load Provider filters. |
| `POST /api/mdc/provider-publication/validation` | 401 | Pending an authorized Provider or Admin session and disposable validation input. This is a non-mutating endpoint. |
| `POST /api/mdc/service-discovery/search` | — | Pending an authorized Consumer or Admin session. Verify the canonical spur-gear query through the UI with Tasowheel and Precipart. |
| `POST /api/mdc/provider-publication` | 401 | Consumer write denial is pending an actual Consumer-only token. Use an empty body and verify HTTP 403 `mdc_role_forbidden`. |

Vercel's `READY` metadata is a deployment status check. The prior direct authenticated Preview CLI smoke is recorded in report 02. This attempt made zero authenticated requests through the browser relay and zero backend writes. [Earlier integration report](https://github.com/samola4real/mdc_v1/blob/4843ebf19ca047894c96f4cf1901397851a25bd2/mdc-catalog/docs/reports_phase4/02_MDC_Stage1B_Existing_Frontend_Integration_Report.md)

## Operator steps and local restart

1. Confirm the approved audience and authorization claim with the MAASAI realm owner for `myClient`. Inspect the effective client scopes and protocol mappers. Use the existing Client scopes → Evaluate view with an authorized test user as a cross-check. Place the two confirmed values directly in the frontend's `.env.local`. [Keycloak Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)
2. Obtain the existing approved automation bypass through the Vercel project owner or the authorized project settings. Enter it directly into the server-only `MDC_VERCEL_PROTECTION_BYPASS` entry. [Vercel Protection Bypass for Automation](https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/protection-bypass-automation)
3. Confirm that the file is saved and the identified Stage 1B process can be restarted to load the settings. Coordinate a personal Keycloak sign-in on the confirmed origin for the available Provider, Consumer and Admin test roles. A separate Consumer-only role is needed for the role-denial check. Keep credentials in the local file or approved server environment and enter login credentials directly in Keycloak.

Once restart is approved and the identified listener has released the port, the existing build can be started from the same worktree.

```powershell
Set-Location -LiteralPath 'C:/Users/Elahi/AppData/Local/Temp/mdc-stage1b-20261124-4b9fc439/mdc-catalog/demo-frontend'
npm run start -- --hostname 127.0.0.1 --port 3001
```

The report commit and permalink are recorded in the delivery message. [Report history](https://github.com/samola4real/mdc_v1/commits/phase4/stage1b-frontend-integration/mdc-catalog/docs/reports_phase4/04_MDC_Stage1B_Frontend_Backend_Connectivity_Report.md)
