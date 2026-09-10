# MaaSAI MaaS Dynamic Catalogue Demo Frontend

## Comprehensive Implementation Report, Quick-Start Guide, and User Manual

**Document status:** Authoritative integrated frontend implementation and operating manual

**Documentation usability revision:** 11 September 2026

**Frontend application baseline:** `06df31c4b18685a174d9c3471f707d6468acc657` (`fix: finalize MDC demo frontend alignment`)

**Integrated personal-GitHub baseline:** `f5a80ec2b71dd1195de2b4718f643c6e58a80c2a` (`Merge finalized MDC demo frontend into main`)

**Public MDC contract:** `1.0`

**Application location:** `mdc-catalog/demo-frontend/`

**Repository:** personal GitHub repository `samola4real/mdc_v1`

**Audience:** first-time users, MaaSAI pilot presenters, project managers, provider representatives, consumer representatives, developers, testers, operators, and future CMM integrators

> **Purpose statement.** The MDC Demo Frontend is an illustrative user interface created for the MaaSAI pilot demonstrations. It is not the Cloud MaaS Marketplace and is not intended to replace the Marketplace frontend. Its purpose is to demonstrate how provider and consumer interactions with the MDC could work through a Marketplace-like interface before integration with the actual MaaSAI components.

> **Current-source rule.** This document describes the current frontend code first and the current MDC backend contract second. Historical reports explain how the implementation evolved; they do not override current source. When frontend assumptions and backend behavior disagree, the backend contract is authoritative and the frontend must be corrected.

> **Repository policy.** The working and maintained source for this integrated demo is the personal GitHub repository `samola4real/mdc_v1`. The original GitLab repository is historical provenance only for this scope. No GitLab synchronization, release, or push is part of the current operating workflow.

---

## Table of contents

1. Executive summary
2. How to use this manual
3. Start here — first-time quick start
4. Choose the right environment
5. Prerequisites and access requirements
6. Project context, purpose, and scope
7. Evolution, preservation, and provenance
8. Technology stack
9. Current frontend architecture
10. Repository and file structure
11. Routing and navigation
12. Authentication and demo roles
13. Runtime configuration
14. Start the MDC backend locally
15. Start the frontend locally
16. First-use verification checklist
17. Provider walkthrough — register a new demo provider
18. Provider walkthrough — update an existing provider
19. Provider form field reference
20. Provider payloads, validation, and demo persistence
21. Consumer walkthrough — search for a provider
22. Consumer form field reference
23. Search payload construction
24. Understanding search results
25. Admin walkthrough
26. API integration overview
27. Public API examples
28. Trusted provider lifecycle boundary
29. Demo data and authority boundaries
30. Validation, testing, and accepted evidence
31. Docker and container operation
32. Deployment guidance
33. Security model
34. Personal GitHub development workflow
35. Relationship to the MDC backend master manual
36. Future CMM integration
37. Known limitations and future work
38. Troubleshooting
39. Glossary
40. Appendices

---

# PART I — WHAT THE FRONTEND IS AND HOW TO START IT

## 1. Executive summary

The MaaSAI MaaS Dynamic Catalogue (MDC) Demo Frontend is a Next.js browser application that makes the MDC pilot understandable and demonstrable. It provides three role-oriented experiences:

- a **Provider** experience for illustrating provider registration and capability updates;
- a **Consumer** experience for searching the real MDC public service-discovery API;
- an **Admin** experience for inspecting demo status and reserved technical interfaces.

The frontend is deliberately separated from the production/trusted MDC lifecycle. Consumer discovery uses the current public MDC contract. Provider registration/update in this UI uses a separate demo API and demo JSON persistence. Trusted provider lifecycle APIs are intentionally not called from the browser because they require a server-side service identity, actor attribution, and ETag concurrency boundary.

The current public API used by the frontend is:

- `GET /api/health`
- `GET /api/catalog/filters`
- `POST /api/service-discovery/search`

The JSON contract uses `"contract_version": "1.0"`. There is no current `/api/v1/...` browser route.

The quickest complete demonstration is to run the Django backend locally on port `8000`, run the frontend locally on port `3000`, use the checked-in public Keycloak configuration or another valid public Keycloak client, log in with a recognized demo role, and open `/demo`.

A person reading only this document should be able to:

1. identify which environment to use;
2. install and start the backend and frontend;
3. configure browser-safe runtime values;
4. log in and select a role;
5. demonstrate provider registration/update;
6. perform consumer service discovery;
7. interpret match results correctly;
8. use the admin screen without mistaking demo metadata for live runtime verification;
9. run validation/build checks;
10. understand what is demo-only, what is public MDC behavior, and what belongs to a future CMM integration.

## 2. How to use this manual

| Your goal | Start here |
|---|---|
| Run the complete demo for the first time | Sections 3–16 |
| Decide whether to use local backend or deployed backend | Section 4 |
| Understand required software and login access | Section 5 |
| Demonstrate provider registration | Section 17 |
| Demonstrate provider updates | Section 18 |
| Understand every provider form area | Sections 19–20 |
| Demonstrate consumer search | Section 21 |
| Understand consumer fields and payload mappings | Sections 22–23 |
| Explain search results to a pilot partner | Section 24 |
| Demonstrate the admin console | Section 25 |
| Integrate another UI with MDC public APIs | Sections 26–28 |
| Run lint/build/manual acceptance | Section 30 |
| Use Docker | Section 31 |
| Prepare a deployed demo | Sections 32–33 |
| Continue development in the personal repository | Section 34 |
| Understand backend implementation details | Section 35 and the backend master manual |
| Plan future real CMM integration | Section 36 |
| Troubleshoot a failure | Section 38 |

If you are a first-time user, do not begin with the architecture sections. Follow Sections 3–16 in order, then use the Provider, Consumer, or Admin walkthrough that matches your demonstration.

## 3. Start here — first-time quick start

This is the recommended full-demo path on Windows/PowerShell. It assumes the repository is already cloned. If it is not, clone your authorized personal GitHub repository first.

### 3.1 Update the repository

From the repository root:

```powershell
cd C:\Users\Elahi\Desktop\mdc_v1
git switch main
git pull --ff-only origin main
git status
```

Expected result: `main` is current and the working tree is clean.

### 3.2 Prepare the backend

Open PowerShell terminal 1:

```powershell
cd C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python backend\manage.py migrate
python backend\manage.py runserver 8000
```

Important points:

- Python `3.12` is the project baseline.
- Leaving `DATABASE_URL` empty uses local SQLite.
- The local settings default `DEBUG=True` and permit the demo API; `.env.example` also sets `MDC_DEMO_API_ENABLED=True`.
- Do not commit `.env`.
- You do not need to place a trusted provider lifecycle token in the frontend or browser.

### 3.3 Verify the backend

Open PowerShell terminal 2 and run:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
Invoke-RestMethod http://localhost:8000/api/catalog/filters
```

Expected health result includes contract `1.0` and status `ok`.

For a full local demo, also verify the demo namespace:

```powershell
Invoke-RestMethod http://localhost:8000/api/demo/health
```

Expected result: a JSON object indicating that the MDC demo API is enabled. If this returns `404`, see Section 38.

### 3.4 Review the browser runtime configuration

Check:

```text
mdc-catalog/demo-frontend/public/config.js
```

The checked-in configuration currently points the browser at:

- a public MaaSAI Keycloak realm/client configuration;
- `http://localhost:8000` for the MDC API;
- `/api` for shared/public routes;
- `/api/demo` for demo-only routes.

Do not put passwords, bearer tokens, client secrets, database URLs, private keys, or lifecycle tokens in this file.

### 3.5 Prepare and start the frontend

Open PowerShell terminal 3:

```powershell
cd C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\demo-frontend
npm ci
npm run dev
```

Expected result: Next.js starts on `http://localhost:3000`.

### 3.6 Open the demo

Open:

```text
http://localhost:3000/demo
```

You should see **MaaS Dynamic Catalogue Demo Console**.

If you are not logged in, the page shows a login prompt. Click **Login** and authenticate through the configured Keycloak realm.

After login, choose one of the available demo roles:

- **Provider**
- **Consumer**
- **Admin**

The roles available depend on the roles contained in your Keycloak token. Admin users can select any of the three demo roles.

### 3.7 What success looks like

A successful full local setup has all of the following:

- `http://localhost:8000/api/health` returns HTTP 200;
- `http://localhost:8000/api/catalog/filters` returns contract `1.0` filters;
- `http://localhost:8000/api/demo/health` returns HTTP 200;
- `http://localhost:3000/demo` loads;
- login redirects to Keycloak and returns to the frontend;
- at least one recognized Provider, Consumer, or Admin role is available;
- Provider/Consumer/Admin child pages open according to the selected role;
- Consumer search can reach the backend;
- Provider preview/save can reach the demo namespace when local demo API is enabled.

## 4. Choose the right environment

Before running the frontend, decide what you are trying to demonstrate.

| Environment | Best use | Public search | Provider demo | Admin demo | Notes |
|---|---|---:|---:|---:|---|
| Local frontend + local Django backend | Complete pilot demonstration and development | Yes | Yes | Yes | Recommended for the full demo |
| Local/deployed frontend + accepted Vercel MDC production backend | Public API/discovery demonstration | Yes, subject to CORS/origin policy | Normally no | Normally no | Production demo API is intentionally disabled |
| Future dedicated demo backend | Controlled partner demonstration | Yes | Yes if deliberately enabled | Yes if deliberately enabled | Requires explicit deployment configuration |
| Browser only with no backend | Static page/layout inspection | No | No | No | Not a functional MDC demonstration |

### 4.1 Recommended choice

Use **local frontend + local Django backend** when you need to demonstrate all three roles. Local settings are designed for development, CORS permits `localhost:3000`, SQLite can be used when no `DATABASE_URL` is supplied, and demo routes are available.

Use the deployed Vercel backend only when you specifically want to demonstrate the canonical public health/filter/search contract and the frontend origin is permitted by backend CORS. Do not expect Provider/Admin demo endpoints to work against a production configuration where `MDC_DEMO_API_ENABLED=False`.

### 4.2 Do not confuse backend deployment with frontend deployment

The repository contains a buildable frontend and a separately deployed MDC backend. The existence of the frontend code does not prove that the frontend itself is deployed to a public production host. When demonstrating locally, the browser is served by Next.js on port 3000 and calls the configured Django backend.

## 5. Prerequisites and access requirements

### 5.1 Software

| Requirement | Recommended/current baseline | Why it is needed |
|---|---|---|
| Git | Current supported Git | Clone/update and development workflow |
| Python | 3.12 | MDC backend |
| pip / venv | Current Python 3.12 tooling | Backend dependencies |
| Node.js | 20.18.x or compatible Node 20 | Frontend build/runtime baseline |
| npm | Compatible with committed lockfile version 2 | `npm ci`, lint, build, start |
| Modern browser | Current Chrome/Edge/Firefox | Demo UI and Keycloak redirect |
| Optional Docker | Current Docker Desktop/Engine | Containerized frontend path |

### 5.2 Identity/access

To use authenticated demo pages you need a Keycloak account whose token contains a recognized role.

Recognized aliases are:

| Demo role | Accepted identity-role aliases |
|---|---|
| Provider | `provider`, `mdc_provider`, `maas_provider` |
| Consumer | `consumer`, `mdc_consumer`, `maas_consumer` |
| Admin | `admin`, `mdc_admin`, `maas_admin` |

If you can load `/demo` but cannot proceed to an authenticated role page, the most likely problem is identity/role configuration rather than the MDC API.

Do not bypass authentication by placing secrets in JavaScript or by treating session storage as authorization.

### 5.3 Network access

The browser must be able to reach:

- the configured Keycloak realm;
- the configured MDC backend origin;
- port 3000 locally for the Next.js frontend;
- port 8000 locally for the recommended Django development backend.

A corporate VPN, firewall, CORS policy, TLS problem, or unavailable Keycloak host can prevent an otherwise correct local build from working.

---

# PART II — PURPOSE, HISTORY, AND IMPLEMENTATION

## 6. Project context, purpose, and scope

MDC is the MaaSAI component that describes manufacturing providers and offerings and performs evidence-based service discovery. The frontend exists because pilot users needed a concrete way to see provider and consumer interactions before a full Marketplace user interface and integration boundary existed.

```text
Provider / Consumer / Admin user
             |
             v
MDC Demo Frontend
(Marketplace-like illustration)
             |
             v
          Django MDC API
             |
             +--> public discovery contract
             +--> demo-only provider/admin contract
             +--> trusted lifecycle contract (server-side only)
```

The frontend demonstrates:

- flexible provider information capture;
- explicit mapping of provider information to controlled MDC categories;
- consumer selection of part family, part type, material, process, certification, and technical requirements;
- evidence-aware provider discovery;
- presentation of matched, unmatched, and unknown capability evidence;
- demo status information and reserved admin interfaces.

It does **not** implement:

- the real Cloud MaaS Marketplace;
- Marketplace account registration or account recovery;
- production end-user authorization;
- provider-specific authorization against the trusted lifecycle API;
- quotation/pricing;
- commercial transactions;
- manufacturing routing/process planning;
- live machine capacity scheduling;
- CAD/2D/3D geometry analysis;
- production RDF/Fuseki administration from the browser.

## 7. Evolution, preservation, and provenance

The frontend originated from a MaaSAI Next.js template and accumulated demo work, much of which existed as untracked local files. A security-preserving snapshot process was therefore used before importing it into the personal GitHub repository.

| Stage | Evidence | Meaning today |
|---|---|---|
| Historical MaaSAI template | source commit `832ad57265bce0889ebea58bc69c031c3b394ee7` | Original layout, workspace, Keycloak foundation, styles, Docker assets |
| F1–F3 | historical reports | Demo shell, API wrappers, backend-status integration |
| F4 series | historical reports | Consumer forms and payload evolution |
| F5 series | historical reports | Provider demo, saved state, role selection |
| F7–F8 | historical reports | Demo overlay, navigation/dashboard/admin cleanup |
| Sanitized import | `e411e7300cfbe2f9f3f9fe245027f2c0c341cd38` | Content snapshot imported without unsafe Git history |
| API/config cleanup | `b207022363163a026a1d77e6485fd151e81aa750` | Public contract, filters, result adapter, routes, README aligned |
| Final application alignment | `06df31c4b18685a174d9c3471f707d6468acc657` | Vocabularies, mapping semantics, result wording, admin status corrected |
| Integrated into personal `main` | `f5a80ec2b71dd1195de2b4718f643c6e58a80c2a` | Accepted frontend and manual integrated into the personal monorepo |

The original historical Git repository contained credential-bearing objects, so its Git history was deliberately not imported. The sanitized snapshot excluded original Git metadata, environment files, credential assignments, raw realm exports, editor state, dependencies, builds, caches, logs, private-key material, and generated archives.

The original GitLab location is therefore relevant as **history/provenance only**. The current operating policy for this integrated frontend is personal GitHub only. Existing historical documents that describe a possible GitHub-to-GitLab release process are not current operating instructions.

## 8. Technology stack

| Technology | Current evidence | Role |
|---|---|---|
| Next.js | `14.0.3`, Pages Router | Page routing, build, standalone server |
| React / React DOM | `^18` | Component/state model |
| PrimeReact | `^10.2.1` | Forms, cards, panels, tables, messages, tags, toasts |
| PrimeFlex | `^3.3.1` | Responsive utility layout |
| PrimeIcons | `^6.0.1` | UI icons |
| Axios | `^1.5.1` | Browser HTTP client |
| Keycloak JS | `^23.0.1` | Browser authentication |
| Sass | `^1.58.3` | Layout and demo styling |
| Chart.js / React Flow | `4.2.1` / `^11.11.4` | Inherited workspace visualization |
| Node.js | Docker ARG `20.18.0` | Build/runtime baseline |
| npm lockfile | version 2 | Reproducible `npm ci` input |

The application is JavaScript/JSX rather than TypeScript. `jsconfig.json` maps `@/*` to `src/*`. ESLint extends `next/core-web-vitals`.

## 9. Current frontend architecture

```text
Browser
  |
  +-- Next.js Pages Router
  |     +-- /demo
  |     +-- /demo/provider
  |     +-- /demo/consumer-search
  |     +-- /demo/admin-audit
  |
  +-- AuthContext + Keycloak
  +-- session-scoped demo role
  +-- route access + DemoRoleGuard
  +-- MDC React components
  +-- payload/result adapters
  +-- Axios service wrappers
  +-- /config.js -> window.MAASAI_CONFIG
             |
             | HTTP/JSON
             v
Django MDC
  +-- /api/... public
  +-- /api/demo/... demo-only
  +-- /api/... trusted lifecycle (not called by browser)
```

`_app.js` provides application-level composition. `routes.js` defines centralized public/authenticated route access. `DemoRoleGuard` adds selected-role presentation checks on the three demo child pages. `AuthContext` initializes Keycloak and exposes login, logout, authenticated state, user name, and roles.

The MDC components are intentionally separated from endpoint wrappers. UI code builds forms and presentation models, while `src/services/mdc/` owns browser-to-API calls. Runtime URL construction is centralized so local/deployed environments can change without editing every service.

## 10. Repository and file structure

```text
mdc-catalog/
  backend/                         Django MDC backend
  data/                            curated/generated/demo data
  docs/
    MDC_Comprehensive_Implementation_Report_and_User_Manual.md
    Demo_Frontend/
      MDC_Demo_Frontend_Comprehensive_Implementation_Report_and_User_Manual.md
      Implementation_History/     historical evidence
      00_frontend_sanitized_snapshot_import_provenance.md
      01_frontend_github_to_gitlab_release_mapping.md   historical planning only
      02_frontend_api_config_cleanup_and_validation.md
  demo-frontend/
    public/
      config.js                    browser-safe runtime configuration
      layout/images/               MaaSAI assets
      themes/                      PrimeReact themes
    src/
      config/
        routes.js                  central route access
        runtimeConfig.js           runtime defaults/merge
      layout/
        AppMenu.js
        AppTopbar.js
        context/AuthContext.js
      pages/
        demo/index.js
        demo/provider.js
        demo/consumer-search.js
        demo/admin-audit.js
      components/mdc/
        ProviderDemoPanel.js
        ConsumerSearchMockup.js
        ProviderResultAccordion.js
        AdminAuditPanel.js
        DemoRoleGuard.js
        demoAuth.js
        providerPayloadBuilder.js
        searchResultFormatters.js
        mockData.js
      services/mdc/
        client.js
        health.service.js
        catalog.service.js
        search.service.js
        demoAdmin.service.js
    package.json
    package-lock.json
    next.config.js
    Dockerfile
    docker-compose.yml
    Makefile
```

Use these ownership rules when changing the frontend:

- screen/page routes -> `src/pages/`;
- reusable MDC UI -> `src/components/mdc/`;
- API calls -> `src/services/mdc/`;
- browser runtime URLs -> `public/config.js` and `runtimeConfig.js`;
- route access -> `src/config/routes.js`;
- role behavior -> `demoAuth.js`, `DemoRoleGuard.js`, and menu logic;
- API contract changes -> verify backend serializers/public-contract code first.

## 11. Routing and navigation

| Route | Central route access | Additional role behavior |
|---|---|---|
| `/` | Public | Template landing page |
| `/demo` | Public | Login/role selection/demo console |
| `/demo/provider` | Authenticated | Provider or Admin-selected role |
| `/demo/consumer-search` | Authenticated | Consumer or Admin-selected role |
| `/demo/admin-audit` | Authenticated | Admin-selected role |
| `/404` | Public | Not-found page |
| `/home/Contact`, `/home/Help`, `/home/Brand`, `/home/AccessDenied`, `/home/ErrorPage` | Public | Inherited template pages |
| `/home/EmptyPage`, `/workspace/*` | Authenticated | Inherited template workspace |

Unknown routes default to authenticated in `routes.js`. The route layer establishes authentication; role selection for demo pages is a browser presentation rule enforced by `DemoRoleGuard` and the menu.

The demo section is the part relevant to MDC pilot demonstrations. Inherited workspace pages are not required to demonstrate the MDC provider/consumer flow.

## 12. Authentication and demo roles

`AuthContext` loads `/config.js`, initializes one Keycloak instance with `check-sso`, `checkLoginIframe: false`, and PKCE S256, and resolves roles from realm and resource access claims.

After a successful login, the `/demo` page asks the user to choose an active role from the authorized options. The selected role is stored in browser session storage under `mdc_demo_selected_role`. This makes role switching convenient for a demonstration but does not create server-side authority.

Admin users can select Provider, Consumer, or Admin. A selected Admin role can open all three demo areas. Provider and Consumer selections see only their intended area.

### 12.1 If login is unavailable

If the Keycloak service is unavailable or you do not have a valid account/role:

- `/demo` can still load as a public page;
- authenticated Provider/Consumer/Admin routes will not become usable;
- disabling Keycloak does not create an authenticated local user—the current `AuthContext` treats disabled Keycloak as unauthenticated;
- obtain a valid demo identity or deliberately configure an approved local identity solution rather than bypassing the guard.

### 12.2 Logout and role switching

Use **Switch role** on the demo dashboard to choose another authorized demo role. Use **Logout** to leave the Keycloak session; the dashboard flow clears the selected demo role.

---

# PART III — CONFIGURATION AND LOCAL EXECUTION

## 13. Runtime configuration

The browser loads `public/config.js`, which defines `window.MAASAI_CONFIG`.

Current shape:

```js
window.MAASAI_CONFIG = {
  keycloak: {
    enabled: true,
    realmUrl: 'https://identity.example.org/realms/example',
    clientId: 'mdc-demo-browser',
    onLoad: 'check-sso'
  },
  mdcApi: {
    baseUrl: 'http://localhost:8000',
    sharedApiPrefix: '/api',
    demoApiPrefix: '/api/demo'
  }
};
```

The checked-in file currently contains the MaaSAI Keycloak realm/client values and the local MDC API origin. These are public browser settings, not secrets.

| Setting | Meaning |
|---|---|
| `keycloak.enabled` | Whether browser Keycloak initialization is attempted |
| `keycloak.realmUrl` | Public realm URL |
| `keycloak.clientId` | Public browser client identifier |
| `keycloak.onLoad` | Normally `check-sso` |
| `mdcApi.baseUrl` | Backend origin, e.g. `http://localhost:8000` |
| `mdcApi.sharedApiPrefix` | `/api` |
| `mdcApi.demoApiPrefix` | `/api/demo` |

### 13.1 Never place these in browser configuration

Do not put any of the following into `config.js`, `NEXT_PUBLIC_*`, source code, local storage, or session storage:

- `MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN`;
- Django secret key;
- `DATABASE_URL`;
- Fuseki password;
- private keys;
- Keycloak confidential-client secret;
- any password or bearer token.

### 13.2 Local versus deployed API URL

`http://localhost:8000` is correct when the browser and backend are running on the same workstation. For a deployed frontend, replace it with an HTTPS API origin and configure backend CORS accordingly.

If a deployed frontend still points to `localhost`, every user's browser will try to call port 8000 on that user's own machine.

## 14. Start the MDC backend locally

The frontend can only demonstrate real MDC behavior when it has a backend to call.

### 14.1 Recommended Windows procedure

From `mdc-catalog`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python backend\manage.py migrate
python backend\manage.py runserver 8000
```

The backend configuration has a safe local fallback: when `DATABASE_URL` is empty, Django uses `backend/db.sqlite3`.

The local default CORS list permits:

```text
http://localhost:3000
http://127.0.0.1:3000
```

Local demo behavior is enabled when `MDC_DEMO_API_ENABLED=True` or Django `DEBUG=True`. The example local environment enables both development mode and the demo API.

### 14.2 Minimal backend checks

```powershell
Invoke-RestMethod http://localhost:8000/api/health
Invoke-RestMethod http://localhost:8000/api/catalog/filters
Invoke-RestMethod http://localhost:8000/api/demo/health
```

If migration or startup fails, resolve the backend first; the frontend cannot compensate for a broken backend.

### 14.3 Fuseki is not required merely to open the frontend

The browser never connects directly to Fuseki. Local service-discovery behavior is controlled by the Django backend and its configured fallback/semantic path. Do not expose Fuseki credentials or a Graph Store write endpoint to the browser.

## 15. Start the frontend locally

From `mdc-catalog/demo-frontend`:

```powershell
npm ci
npm run dev
```

Open:

```text
http://localhost:3000/demo
```

Other useful commands:

```powershell
npm run lint
npm run build
npm run start
```

`npm run start` serves a previously built production-style Next.js application, normally on port 3000.

### 15.1 When to use each command

| Command | Use |
|---|---|
| `npm ci` | Clean install exactly from the committed lockfile |
| `npm run dev` | Interactive development/demo server |
| `npm run lint` | Static lint gate |
| `npm run build` | Production build validation |
| `npm run start` | Serve an already built production bundle |

Do not use `npm install` merely to start the accepted baseline if `npm ci` is available; `npm ci` preserves the committed dependency graph.

## 16. First-use verification checklist

Before presenting the demo to someone else, verify in this order:

1. `git status` is clean.
2. Backend `/api/health` returns HTTP 200.
3. Backend `/api/catalog/filters` returns contract `1.0`.
4. For full demo, `/api/demo/health` returns HTTP 200.
5. Frontend loads at `/demo`.
6. Keycloak login succeeds.
7. A recognized role is visible.
8. Provider/Consumer/Admin page opens for the selected role.
9. Consumer page shows **Loading current catalogue filters...** briefly and then normal controls; if it shows the fallback warning, investigate the filters endpoint.
10. A test search completes without a browser CORS/network error.
11. Provider Preview works if the demo API is enabled.
12. Admin backend/Fuseki labels are described as demo metadata, not live runtime proof.

---

# PART IV — USING THE PROVIDER EXPERIENCE

## 17. Provider walkthrough — register a new demo provider

This flow demonstrates **flexible provider onboarding**, not trusted production publication.

### 17.1 Open Provider mode

1. Open `http://localhost:3000/demo`.
2. Click **Login** if necessary.
3. Select **Provider**. An Admin user may also select Provider.
4. Click **Open Provider Area**.
5. Confirm the page heading is **Provider Dashboard**.
6. Click **Register New Provider** if that mode is not already selected.

### 17.2 Enter provider information

Fill **Provider information**:

| UI field | Example | Payload field |
|---|---|---|
| Provider name | `Demo Metal Works Oy` | `provider_name` |
| Provider ID | `demo_metal_works` | `provider_id` |
| Country | `Finland` | `country` |
| Short description / notes | `Precision machining and prototype manufacturing.` | `description` |

Use stable, machine-friendly IDs with no spaces when possible.

### 17.3 Enter offering information

Fill **Offering information**:

| UI field | Example | Payload field |
|---|---|---|
| Offering name | `Precision metal-part manufacturing` | `offerings[0].offering_name` |
| Offering ID | `demo_metal_works_precision_parts` | `offerings[0].offering_id` |

Registration mode deliberately does not force a controlled service-category mapping yet.

### 17.4 Add flexible offering facts

Under **Additional offering information**, click **Add field**.

Examples:

| Field name | Field value |
|---|---|
| Business capability | Precision machining |
| Typical customer | Industrial OEM |
| Prototype support | Yes |

These become `custom_offering_fields`. They are preserved as staging facts and are not silently converted into controlled MDC fields.

### 17.5 Add flexible capability facts

Under **Capability information**, click **Add capability field**.

Examples:

| Field name | Value | Unit | Notes |
|---|---:|---|---|
| Maximum diameter | 300 | mm | Depends on material |
| Batch size | 50–500 | pcs | Typical range |
| Lead time | 6 | weeks | Typical |

These become `custom_capability_fields`.

Do not enter route/operation sequencing fields; the demo backend rejects forbidden route-related terms.

### 17.6 Preview before saving

Click **Preview**.

What happens:

```text
Browser
  -> POST /api/demo/provider-publication/preview
  -> demo backend validates/normalizes the staging payload
  -> no demo state is changed
  -> frontend shows the response
```

Expected success presentation:

- a success toast for **Preview validation**;
- a response showing `status: "valid_demo_preview"`;
- `mutates_state: false` behavior;
- normalized provider/offering information;
- warnings if flexible values cannot be treated as controlled values.

### 17.7 Save to demo state

If the preview is acceptable, click **Register for demo**.

This calls:

```text
POST /api/demo/provider-publication/simulate-update
```

Expected result:

- a **Demo save** success toast;
- provider information written to demo JSON state;
- the new provider becomes available to the demo provider-state reader;
- it may later appear as a clearly labelled **Demo registered provider** overlay in consumer search when its text/domain terms match.

### 17.8 What this registration does not do

It does **not**:

- create an authoritative PostgreSQL provider lifecycle record;
- authenticate a trusted Marketplace service;
- generate an ETag lifecycle transaction;
- synchronize the authoritative catalogue to Fuseki;
- prove that the provider is an active production supplier.

It is a demonstration of the future onboarding interaction pattern.

## 18. Provider walkthrough — update an existing provider

This mode demonstrates how a previously known provider/offering can be mapped to controlled MDC structures and edited.

### 18.1 Open Update mode

1. Open the Provider Dashboard.
2. Click **Update Existing Provider**.
3. The table shows static Tasowheel demo rows plus saved demo providers when demo state is available.
4. Select one row.

The table includes Provider, Offering, Service category, Part family, Supported part types, Materials, Processes, and Status.

### 18.2 Understand `mapping-required`

A flexible registration may not yet contain an accepted controlled category/family mapping. Such an offering is displayed as `mapping-required`.

When that happens:

1. select the row;
2. choose a **Capability template**;
3. the frontend couples the current controlled service category and part family;
4. Preview/Save remain disabled until the mapping is valid.

This is deliberate. The UI must not invent a controlled value merely because a provider used similar free text.

### 18.3 Choose a controlled template

| Capability template | Service category | Part family |
|---|---|---|
| Gear manufacturing | `precision_gears` | `gear` |
| Shaft manufacturing | `precision_shafts` | `shaft` |
| Metal-part manufacturing | `precision_metal_parts` | `metal_part` |

The **Service category / capability area** field is read-only in update mode so it cannot drift independently from the selected template.

### 18.4 Edit controlled capabilities

For gear, the page exposes supported gear types, module range, diameter range, quality standard/class, plus common capabilities.

For shaft, it exposes supported shaft types, maximum length, outer-diameter range, spline module, plus common capabilities.

For metal parts, it exposes supported metal-part types, maximum dimensions, tolerance, surface finish, plus common capabilities.

Common update fields include:

- materials;
- material grades;
- certifications;
- processes;
- batch-size minimum/maximum;
- lead-time minimum/maximum weeks;
- maximum weight;
- notes.

### 18.5 Preview the update

Click **Preview update**.

The frontend first checks that the template/category/family mapping is valid. It then sends the payload to the demo preview endpoint. No demo state is changed.

### 18.6 Save the update

Click **Save update for demo**.

The demo state stores updates separately from registrations. This is still demo persistence, not trusted lifecycle persistence.

### 18.7 Expected result

After a valid update:

- Preview/Save completes without a mapping warning;
- the exact outgoing JSON remains visible in **ProviderPayloadPreview**;
- the returned response is shown in **ProviderActionResult**;
- reloading provider state shows saved demo data when the demo endpoint remains available.

## 19. Provider form field reference

### 19.1 Registration mode

| UI area | Field | Required for a useful demo? | Meaning |
|---|---|---:|---|
| Provider information | Provider name | Yes | Human-readable organization name |
| Provider information | Provider ID | Yes | Stable provider identifier |
| Provider information | Country | Recommended | Provider location |
| Provider information | Short description / notes | Recommended | Free-text summary |
| Offering information | Offering name | Yes | Human-readable offering name |
| Offering information | Offering ID | Yes | Stable offering identifier |
| Additional offering information | Field name/value | Optional | Flexible offering staging facts |
| Capability information | Name/value/unit/notes | Optional | Flexible capability staging facts |

Registration mode intentionally demonstrates a flexible input layer. It should not be interpreted as a complete controlled publication form.

### 19.2 Gear update fields

| UI field | Payload location |
|---|---|
| Supported gear part types | `supported_part_types` |
| Module min/max | `capabilities.module.min/max` |
| Diameter min/max | `capabilities.outside_diameter_mm.min/max` |
| Quality standard/class | `capabilities.gear_quality.standard/class` |

### 19.3 Shaft update fields

| UI field | Payload location |
|---|---|
| Supported shaft part types | `supported_part_types` |
| Length max | `capabilities.length_mm.max` |
| Outer diameter min/max | `capabilities.outer_diameter_mm.min/max` |
| Spline module | `capabilities.spline_module.exact` |

### 19.4 Metal-part update fields

| UI field | Payload location |
|---|---|
| Supported metal part types | `supported_part_types` |
| Maximum length | `capabilities.maximum_dimensions_mm.length` |
| Maximum width | `capabilities.maximum_dimensions_mm.width` |
| Maximum height/thickness | `capabilities.maximum_dimensions_mm.height_or_thickness` |
| Maximum diameter | `capabilities.maximum_dimensions_mm.diameter` |
| Tolerance | `capabilities.tolerance` |
| Surface finish | `capabilities.surface_finish` |

### 19.5 Common update fields

| UI field | Payload location |
|---|---|
| Materials | `capabilities.materials` |
| Material grades | `capabilities.available_grades` |
| Processes | `capabilities.processes` |
| Certifications | top-level `certifications` and demo capability context |
| Batch size min/max | `capabilities.batch_size.min/max` |
| Lead time min/max weeks | `capabilities.lead_time_weeks.min/max` |
| Weight max | `capabilities.weight_kg.max` |
| Notes | `capabilities.notes` |

## 20. Provider payloads, validation, and demo persistence

### 20.1 Registration payload shape

Representative flexible registration:

```json
{
  "action": "register_provider",
  "provider_id": "demo_metal_works",
  "provider_name": "Demo Metal Works Oy",
  "country": "Finland",
  "description": "Precision machining and prototype manufacturing.",
  "offerings": [
    {
      "offering_id": "demo_metal_works_precision_parts",
      "offering_name": "Precision metal-part manufacturing",
      "custom_offering_fields": [
        {"name": "Business capability", "value": "Precision machining"}
      ],
      "capabilities": {
        "custom_capability_fields": [
          {"name": "Maximum diameter", "value": "300", "unit": "mm"}
        ]
      }
    }
  ]
}
```

### 20.2 Update payload shape

Controlled update payloads add:

- `publication_metadata`;
- provider certifications;
- `service_category`;
- `part_family`;
- `capability_template`;
- `supported_part_types`;
- `support_status`;
- template-specific and generic capabilities.

### 20.3 Demo backend validation behavior

The demo backend:

- requires a valid action: `register_provider` or `update_existing_provider`;
- requires provider ID/name and at least one offering;
- validates controlled values where update mode expects them;
- can retain unrecognized registration facts as custom information rather than silently promoting them;
- rejects forbidden route/operation field names;
- returns warnings for optional/unrecognized capability keys rather than pretending they are controlled.

### 20.4 Demo state file

The demo state service writes:

```text
data/demo/provider_demo_state.json
```

The file is a demonstration persistence mechanism. It contains separate provider registrations and updates plus a last-updated timestamp.

Do not use it as a substitute for the trusted PostgreSQL provider lifecycle.

---

# PART V — USING THE CONSUMER EXPERIENCE

## 21. Consumer walkthrough — search for a provider

The Consumer page is the frontend's strongest demonstration of the real public MDC contract because it loads live controlled filters and submits canonical service-discovery requests.

### 21.1 Open Consumer mode

1. Open `/demo`.
2. Log in.
3. Select **Consumer**. An Admin user may also select Consumer.
4. Click **Open Service Discovery**.
5. Confirm the card title **Consumer search request** is visible.

### 21.2 Confirm filter status

On load, the page requests:

```text
GET /api/catalog/filters
```

You may briefly see **Loading current catalogue filters...**.

If loading succeeds, the dropdowns use the current backend vocabulary.

If it fails, the page shows:

> Catalogue filters could not be loaded; explicit demo fallback vocabulary is in use.

A fallback keeps the screen usable for a demonstration, but it is not authoritative catalogue truth.

### 21.3 Run the default gear example

The accepted frontend starts with a useful gear example. Verify or enter:

| Field | Example |
|---|---|
| Consumer ID | `consumer_demo_001` |
| Request ID | automatically generated `req-demo-...` |
| Part family | Gear |
| Part type | Spur gear |
| Material | Alloyed carburizing steel |
| Processes | Hobbing, Turn mill |
| Certification | ISO 9001 |
| Technical requirements | descriptive text for the human demonstration |
| Module | 2.0 |
| Diametral pitch | 10 |
| Outside diameter | 100 mm |
| Gear quality | `DIN 6` |
| Face width | 25 mm |
| Tolerance | 0.02 mm |

Important: **Technical requirements** is currently a UI description field and is not emitted as a canonical free-text search criterion. The canonical request is built from the controlled selection and mapped structured fields.

### 21.4 Inspect the payload

Before clicking search, expand/read **SearchPayloadPreview**. This is the definitive JSON the browser intends to send.

Confirm:

- `service_category` is derived from the family;
- `part_family` and `part_type` are controlled values;
- gear fields are in `requirements.part_family_specifications` and `part_type_specifications`;
- material/process/certification are in `requirements.generic_requirements`;
- `material_grades` is not present;
- `match_policy.optional_match_mode` is `score_only`.

### 21.5 Search

Click **Search MDC**.

While waiting, the button/message shows **Searching MDC...**.

The browser calls:

```text
POST /api/service-discovery/search
```

On success, it then optionally reads demo provider state and appends separately labelled demo-overlay candidates.

### 21.6 What success looks like

Expected successful presentation:

- success toast **Search completed**;
- results heading **Provider candidates found** when results exist;
- one accordion/panel per provider/offering candidate;
- Provider, Offering, Requested part type, Suitability/result state, and Support status;
- matched/unmatched/unknown capability evidence;
- materials/processes/certifications where returned;
- an explicit **Demo registered provider** tag only for browser-generated demo overlays.

### 21.7 Try a shaft search

Choose:

```text
Part family: Shaft
Part type: Splined shaft
```

Typical structured fields are:

- Length mm
- Outer diameter mm
- Spline module
- Tolerance mm

For `hollow_shaft`, the relevant type-specific fields become internal diameter and wall thickness. A plain shaft does not use spline/hollow-specific fields.

### 21.8 Try a metal-part search

Choose:

```text
Part family: Metal part
Part type: Bracket
```

Typical fields are:

- Length
- Width
- Height
- Vertical flange length
- Horizontal flange length
- Weight
- Tolerance
- Surface finish

The service category is derived as `precision_metal_parts`.

## 22. Consumer form field reference

### 22.1 Common fields

| UI field | Canonical payload mapping | Notes |
|---|---|---|
| Consumer ID | `consumer_id` | Requesting consumer identifier |
| Request ID | `request_id` | Request trace identifier |
| Part family | `part_family` | `gear`, `shaft`, or `metal_part` |
| Part type | `part_type` | Loaded by family from filters |
| Material | `requirements.generic_requirements.materials[]` | Controlled material family/value |
| Processes | `requirements.generic_requirements.processes[]` | Multi-select |
| Certification | `requirements.generic_requirements.certifications[]` | Single UI selection -> list in JSON |
| Technical requirements | Not currently emitted | Human-facing descriptive field only |

`service_category` is derived from the family relationship supplied by the filters endpoint, with the explicit demo mapping as a fallback.

### 22.2 Gear fields

| UI field | Payload mapping | Interpretation |
|---|---|---|
| Module | `part_family_specifications.module.exact` | Requested exact module |
| Diametral pitch | `diametral_pitch.min/max` with same value | Exact-like bounded request |
| Outside diameter mm | `outside_diameter_mm.max` | Provider capacity must cover request |
| Gear quality | parsed to `gear_quality.standard/max_class` | Use format such as `DIN 6` |
| Face width mm | `part_type_specifications.face_width_mm.exact` | Type-specific requirement |
| Tolerance mm | `part_family_specifications.tolerance_mm.max` | Maximum acceptable tolerance |

If Gear quality cannot be parsed as `<standard> <positive number>`, it is omitted rather than inventing a quality requirement.

### 22.3 Shaft fields

| UI field | Payload mapping | When used |
|---|---|---|
| Length mm | `part_family_specifications.length_mm.max` | Shaft family |
| Outer diameter mm | `outer_diameter_mm.max` | Shaft family |
| Tolerance mm | `tolerance_mm.max` | Shaft family |
| Spline module | `part_type_specifications.spline_module.exact` | `splined_shaft` |
| Internal diameter mm | `part_type_specifications.inner_diameter_mm.max` | `hollow_shaft` |
| Wall thickness mm | `part_type_specifications.wall_thickness_mm.exact` | `hollow_shaft` |

### 22.4 Metal-part fields by type

| Type | Main UI fields | Main structured mapping |
|---|---|---|
| Block | length, width, height, holes, weight, tolerance, surface finish | bounding box + hole count + generic limits |
| Bracket | length, width, height, vertical/horizontal flange lengths, weight, tolerance, surface finish | bounding box + flange dimensions + generic limits |
| Plate | length, width, thickness, holes, weight, tolerance, surface finish | bounding box + hole count + generic limits |
| Bushing | inner diameter, outer diameter, length, flange diameter, tolerance, surface finish | family diameters/length/tolerance + flange diameter + generic requirements |
| Roller | outer diameter, length, inner diameter, weight, tolerance, surface finish | family dimensions/tolerance + generic requirements |
| Collar | inner diameter, outer diameter, length, weight, tolerance, surface finish | family dimensions/tolerance + generic requirements |

### 22.5 Surface finish input caveat

The UI field is text-capable, but the canonical consumer payload only includes `surface_finish_ra_um` when the value can be interpreted as a positive number. Enter a numeric Ra value such as `3.2` when you want it sent as a structured criterion. Text such as `Customer specified` is not emitted as a numeric search criterion.

### 22.6 Material grades

The consumer form does not send material grades as a canonical search criterion. Provider-side `available_grades` is evidence; consumer discovery currently uses the controlled material requirement supported by the backend contract.

## 23. Search payload construction

Every canonical request contains:

- `request_id`;
- `consumer_id`;
- `service_category`;
- `part_family`;
- `part_type`;
- grouped `requirements`;
- `match_policy`.

Empty/unused values are omitted.

### 23.1 Representative gear request

```json
{
  "request_id": "req-demo-gear-001",
  "consumer_id": "consumer_demo_001",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear",
  "requirements": {
    "part_family_specifications": {
      "module": {"exact": 2},
      "diametral_pitch": {"min": 10, "max": 10},
      "outside_diameter_mm": {"max": 100},
      "gear_quality": {"standard": "DIN", "max_class": 6},
      "tolerance_mm": {"max": 0.02}
    },
    "part_type_specifications": {
      "face_width_mm": {"exact": 25}
    },
    "generic_requirements": {
      "materials": ["alloyed_carburizing_steel"],
      "processes": ["hobbing", "turn_mill"],
      "certifications": ["ISO9001_2015"]
    }
  },
  "match_policy": {
    "unknown_policy": "keep_as_unknown",
    "optional_match_mode": "score_only",
    "minimum_score": null
  }
}
```

### 23.2 Representative shaft request

```json
{
  "request_id": "req-demo-shaft-001",
  "consumer_id": "consumer_demo_001",
  "service_category": "precision_shafts",
  "part_family": "shaft",
  "part_type": "splined_shaft",
  "requirements": {
    "part_family_specifications": {
      "length_mm": {"max": 220},
      "outer_diameter_mm": {"max": 35},
      "tolerance_mm": {"max": 0.02}
    },
    "part_type_specifications": {
      "spline_module": {"exact": 1.5}
    },
    "generic_requirements": {
      "materials": ["alloyed_carburizing_steel"],
      "processes": ["turn_mill"],
      "certifications": ["ISO9001_2015"]
    }
  },
  "match_policy": {
    "unknown_policy": "keep_as_unknown",
    "optional_match_mode": "score_only",
    "minimum_score": null
  }
}
```

### 23.3 Representative metal-part request

```json
{
  "request_id": "req-demo-metal-001",
  "consumer_id": "consumer_demo_001",
  "service_category": "precision_metal_parts",
  "part_family": "metal_part",
  "part_type": "bracket",
  "requirements": {
    "part_family_specifications": {
      "bounding_box_mm": {
        "length_mm": {"max": 150},
        "width_mm": {"max": 80},
        "height_mm": {"max": 20}
      }
    },
    "part_type_specifications": {
      "vertical_flange_length_mm": {"max": 40},
      "horizontal_flange_length_mm": {"max": 40}
    },
    "generic_requirements": {
      "materials": ["alloyed_carburizing_steel"],
      "processes": ["turn_mill"],
      "certifications": ["ISO9001_2015"],
      "weight_kg": 2.5,
      "tolerance_mm": {"max": 0.02},
      "surface_finish_ra_um": {"max": 3.2}
    }
  },
  "match_policy": {
    "unknown_policy": "keep_as_unknown",
    "optional_match_mode": "score_only",
    "minimum_score": null
  }
}
```

## 24. Understanding search results

The current public response is flattened. Each result can contain:

- `provider_id` / `provider_name`;
- `offering_id` / `offering_name`;
- `service_category`;
- `part_family`;
- response/request `part_type` context;
- `match`;
- `matched_capabilities`;
- `unmatched_capabilities`;
- `unknown_capabilities`.

### 24.1 Result status

| Result status | Meaning |
|---|---|
| `full_match` | Confirmed part-type support and evaluated requirements matched |
| `partial_match` | Part-type support is confirmed, but not all evaluated requirements fully matched |
| `unknown_match` | Important support/evidence remains unconfirmed/unknown |

The UI uses **Provider candidates found**, not “suitable providers,” because a candidate can include partial or unknown evidence.

### 24.2 Capability evidence

| Capability status | Interpret as |
|---|---|
| matched | Provider evidence satisfies the request |
| unmatched | Provider evidence does not satisfy the request |
| unknown | There is insufficient confirmed comparable evidence |
| partial match where present | Some requested list/components matched and others did not |

Unknown is not the same as false. It means the catalogue cannot confirm the requirement from current evidence.

### 24.3 Match score

`match.score` is a deterministic matching score used by the backend. Do not describe it as:

- product quality;
- commercial ranking;
- supplier reliability;
- probability of success;
- quotation competitiveness.

The main UI emphasizes capability evidence instead of using the score as a business rating.

### 24.4 Demo overlay results

After canonical search, the frontend may read demo provider state and append browser-generated candidates. These are marked **Demo registered provider**.

They are not backend-canonical catalogue results. They exist to make the provider-registration demonstration visible to a consumer during a pilot session.

### 24.5 Illustrative action buttons

Any quote/contact/save-style action presented in result UI is illustrative. It does not create an order, quotation, transaction, or Marketplace message.

---

# PART VI — USING THE ADMIN EXPERIENCE

## 25. Admin walkthrough

### 25.1 Open Admin

1. Open `/demo`.
2. Log in with an Admin role.
3. Select **Admin**.
4. Click **Open Demo Admin**.
5. Confirm the page loads system status, demo provider state, catalogue/search readiness, and technical actions.

### 25.2 System status

The Admin screen reads:

- shared backend health;
- demo API health;
- demo backend-status metadata;
- demo provider state;
- catalogue filters.

Interpret the cards carefully:

- **Backend API** can show whether shared health responded;
- **Demo API** can show whether the demo health endpoint responded;
- backend direction/fallback/Fuseki dataset labels are **illustrative demo-reported metadata**, not live verification of which matcher or Fuseki instance is currently executing discovery.

### 25.3 Demo provider state

The provider-state panel reports:

- registered demo provider count;
- demo update count;
- last-updated time;
- provider summary rows when available;
- the raw response in an advanced JSON panel.

This describes the demo JSON state, not authoritative PostgreSQL provider lifecycle state.

### 25.4 Catalogue/search readiness

The admin panel reads the public filters endpoint and shows counts for materials, processes, certifications, and part families. This verifies that the public filter contract is reachable; it is not a substitute for a complete service-discovery test.

### 25.5 Technical actions

Current technical interfaces are reserved:

| Action | Current backend behavior | Correct UI interpretation |
|---|---|---|
| Run Fuseki Smoke Test | HTTP 200 with `status: "not_implemented"`, non-mutating | Warning/not implemented |
| Regenerate RDF | HTTP 501, `status: "not_implemented"`, `mutates_state: false` | Reserved/not implemented |
| Reload Fuseki | HTTP 501, `status: "not_implemented"`, `mutates_state: false` | Reserved/not implemented |

The frontend intentionally avoids presenting `not_implemented` as successful execution.

Do not tell a pilot user that these buttons actually rebuilt RDF or reloaded Fuseki; they currently do not.

---

# PART VII — API INTEGRATION AND BACKEND BOUNDARIES

## 26. API integration overview

### 26.1 Canonical public browser calls

| Method | Path | Frontend use |
|---|---|---|
| GET | `/api/health` | Shared backend health |
| GET | `/api/catalog/filters` | Controlled search filters |
| POST | `/api/service-discovery/search` | Consumer provider discovery |

These routes are unversioned. The contract version is in JSON.

### 26.2 Demo-only browser calls

| Method | Path | Use |
|---|---|---|
| GET | `/api/demo/health` | Demo availability |
| GET | `/api/demo/service-discovery/backend-status` | Demo metadata labels |
| GET | `/api/demo/service-discovery/fuseki-smoke-test` | Reserved smoke interface |
| POST | `/api/demo/service-discovery/regenerate-rdf` | Reserved action |
| POST | `/api/demo/service-discovery/reload-fuseki` | Reserved action |
| GET | `/api/demo/provider-publication/state` | Demo provider state/overlay |
| POST | `/api/demo/provider-publication/preview` | Non-mutating provider preview |
| POST | `/api/demo/provider-publication/simulate-update` | Save demo registration/update |

Demo routes are temporary demonstration interfaces, not the Marketplace contract.

### 26.3 HTTP client behavior

`src/services/mdc/client.js`:

- constructs shared/demo URLs from runtime configuration;
- uses Axios;
- uses a default 10-second timeout;
- returns `response.data` to callers;
- normalizes current nested backend error messages with backward-compatible fallbacks.

The browser does not need response ETags because it does not call trusted lifecycle update endpoints.

## 27. Public API examples

### 27.1 Health

```json
{
  "contract_version": "1.0",
  "status": "ok",
  "service": "maasai-mdc"
}
```

### 27.2 Catalogue filters — shortened example

```json
{
  "contract_version": "1.0",
  "service_categories": [
    {"value": "precision_gears", "label": "Precision gears", "part_family": "gear"}
  ],
  "part_families": [
    {"value": "gear", "label": "Gear", "service_category": "precision_gears"}
  ],
  "part_types": {
    "gear": [
      {"value": "spur_gear", "label": "Spur gear"}
    ]
  },
  "materials": [],
  "processes": [],
  "certifications": []
}
```

### 27.3 Search result — shortened example

```json
{
  "contract_version": "1.0",
  "results": [
    {
      "provider_id": "example_provider",
      "provider_name": "Example Provider",
      "offering_id": "example_precision_gears",
      "offering_name": "Precision gear manufacturing",
      "service_category": "precision_gears",
      "part_family": "gear",
      "match": {
        "status": "full_match",
        "score": 1.0
      },
      "matched_capabilities": [],
      "unmatched_capabilities": [],
      "unknown_capabilities": []
    }
  ]
}
```

### 27.4 Error envelope

```json
{
  "contract_version": "1.0",
  "error": {
    "code": "invalid_service_discovery_request",
    "message": "Invalid service-discovery search request.",
    "details": {}
  }
}
```

An unsupported contract example can return a message such as:

```text
Unsupported contract_version '2.0'. Supported versions: ['1.0']
```

## 28. Trusted provider lifecycle boundary

The backend also exposes trusted provider lifecycle APIs, but the current frontend deliberately does not call them.

| Method | Trusted route | Purpose |
|---|---|---|
| POST | `/api/provider-publication/validation` | Validate publication |
| POST | `/api/provider-publication` | Register/publish provider |
| GET, PATCH | `/api/providers/<provider_id>` | Read/update provider |
| GET, POST | `/api/providers/<provider_id>/offerings` | List/add offering |
| GET, PATCH | `/api/offerings/<offering_id>` | Read/update offering |

There is no current collection `GET /api/providers` browser route.

Trusted lifecycle can require:

- `Authorization: Bearer <service token>`;
- `X-MDC-Actor-Id` on writes;
- strong ETags on reads;
- `If-Match` on updates;
- a temporary Vercel compatibility `X-MDC-If-Match` header where documented by the backend manual.

### 28.1 Why the browser must not hold the lifecycle token

A browser token embedded in JavaScript or runtime configuration is visible to every user. It would allow a user to impersonate the trusted integration service.

The future safe pattern is:

```text
Browser / real CMM UI
        |
        v
CMM backend / BFF
        |  server-side service token
        |  end-user/provider authorization
        |  actor attribution
        |  ETag management
        v
MDC trusted lifecycle API
```

## 29. Demo data and authority boundaries

Keep these three data classes separate when presenting the system.

| Data/interface | Authority | Intended use |
|---|---|---|
| Public discovery results | MDC backend public contract | Real provider discovery response for current catalogue/runtime |
| Demo provider JSON state | Demo backend only | Pilot illustration of registration/update and overlay |
| Trusted lifecycle/PostgreSQL | MDC backend trusted boundary | Authoritative provider/offering lifecycle |

The frontend can show both canonical search results and a demo overlay on one screen, but the overlay is explicitly labelled so users can distinguish them.

---

# PART VIII — VALIDATION, DOCKER, DEPLOYMENT, AND SECURITY

## 30. Validation, testing, and accepted evidence

The accepted final-alignment run validated the application with:

| Gate | Accepted result |
|---|---|
| `npm ci` | PASS, committed dependency graph |
| npm audit output from that run | 0 vulnerabilities reported at that point in time |
| `npm run lint` | PASS with five pre-existing warnings |
| `npm run build` | PASS |
| Route sanity | PASS |
| Public health/filters/search smoke | PASS |
| Secret-risk scans | PASS |
| `git diff --check` | PASS |
| Backend application modifications during final frontend alignment | NONE |

These are point-in-time acceptance results. Future changes require new validation.

### 30.1 Manual acceptance suite

**Unauthenticated**

- open `/` and `/demo`;
- confirm public rendering;
- confirm authenticated child routes do not behave as anonymous access.

**Provider**

- login with Provider role;
- register a flexible provider;
- preview before save;
- save only against a disposable/demo environment;
- open Update Existing Provider;
- verify saved flexible entries require controlled mapping;
- choose template and verify category/family coupling;
- preview and save a demo update.

**Consumer**

- load canonical filters;
- test Gear, Shaft, and all metal-part type groups;
- inspect payload preview;
- submit search;
- verify matched/unmatched/unknown presentation;
- verify `unknown_match` is not described as confirmed support;
- verify demo overlays are labelled.

**Admin**

- verify backend/demo health cards;
- verify provider state and filter counts;
- confirm backend/Fuseki labels are demo metadata;
- confirm smoke test is shown as not implemented;
- confirm regenerate/reload show reserved 501 behavior.

**Failure cases**

- filters unavailable -> fallback warning;
- demo API disabled -> canonical search continues while demo calls warn/unavailable;
- backend unavailable -> timeout/network error;
- invalid search -> backend error details displayed;
- canonical search succeeds but demo state read fails -> canonical results remain valid.

### 30.2 Missing automated test coverage

The frontend currently has no comprehensive unit/integration/browser test suite and no scoped frontend CI workflow. Future work should add:

- payload-builder tests;
- runtime/path-builder tests;
- role utility tests;
- filter/result adapter tests;
- component tests with mocked APIs;
- end-to-end role journeys;
- accessibility checks;
- a repository-approved CI workflow.

## 31. Docker and container operation

The Dockerfile uses a multi-stage Node 20.18/Alpine 3.20 build and Next.js standalone output. The runtime runs as a non-root user and exposes port 3000.

### 31.1 Start the frontend with Docker Compose

From `mdc-catalog/demo-frontend`:

```powershell
docker compose up --build -d
docker compose ps
docker compose logs -f frontend
```

Open:

```text
http://localhost:3000/demo
```

Stop it with:

```powershell
docker compose down
```

The Compose file mounts `./public/config.js` read-only into the container, so runtime URLs can be changed without rebuilding the image.

### 31.2 Important Docker limitation

The frontend Compose file starts the frontend service only. It does not start Django, Keycloak, PostgreSQL, or Fuseki. The configured backend and identity services must already be reachable from the user's browser.

Because API requests are made by the browser, `http://localhost:8000` refers to the user's host machine, not to the frontend container itself.

### 31.3 Makefile operations

The Makefile includes buildx, registry push/release, scan, size, run, logs, and cleanup helpers. Registry publication is an operational action and is not automatically authorized by this manual. Review the target registry and credentials before any push/release target.

## 32. Deployment guidance

A safe deployed demo requires:

1. an HTTPS frontend origin;
2. an HTTPS MDC API origin in `public/config.js` or equivalent runtime mount;
3. backend CORS/CSRF origins matching the frontend host;
4. a correctly registered Keycloak public client and redirect/origin rules;
5. an explicit decision whether demo APIs are allowed in that environment;
6. no browser-delivered secrets;
7. backend secrets managed server-side;
8. lint/build and manual role-journey validation;
9. a rollback path.

### 32.1 Production backend defaults versus local demo defaults

Production Django settings use `DEBUG=False` and default these feature flags off:

- `MDC_DEMO_API_ENABLED`;
- provider publication/validation/sync flags unless explicitly enabled by controlled deployment configuration.

Trusted lifecycle authentication, actor, and concurrency requirements default on in production settings.

The accepted Phase-3 Vercel backend is suitable for the public contract. Its demo namespace is intentionally not the default place for provider/admin browser demonstrations.

### 32.2 Keycloak deployment ownership

A deployment owner must confirm:

- realm URL;
- public client ID;
- valid redirect URIs;
- web origins;
- role assignment process;
- logout redirect behavior;
- availability from the target network.

Do not configure a confidential-client secret in the browser.

## 33. Security model

| Boundary/risk | Current frontend control | Important limitation |
|---|---|---|
| Browser configuration | Explicitly public | Must never contain trusted secrets |
| Authentication | Keycloak browser login | Identity config must be correctly owned/deployed |
| Demo roles | Route/menu/component presentation checks | Not backend authorization |
| Public search | Uses public canonical API | Backend remains contract authority |
| Demo endpoints | Separate `/api/demo` namespace + backend feature gate | Should be exposed only in controlled demo environments |
| Trusted lifecycle | No browser helpers/token | Must be behind CMM/BFF/server-side boundary |
| Demo state | Clearly demo-only JSON persistence | Not authoritative catalogue state |
| Historical source | Sanitized snapshot, unsafe history excluded | Do not re-import credential-bearing history |
| Dependencies | Lockfile + point-in-time clean audit | Requires maintenance over time |
| Network | HTTPS/CORS guidance | Local development intentionally uses HTTP localhost |

### 33.1 Security rules for users and developers

Never:

- paste the lifecycle service token into the frontend;
- commit `.env`;
- print database/Fuseki credentials into logs or docs;
- treat a client-side role as authorization for a backend write;
- expose a Graph Store write endpoint to browser JavaScript;
- enable demo APIs casually on a production environment;
- revive `/api/v1` without an actual backend contract change;
- import historical credential-bearing Git objects into the personal repository.

---

# PART IX — MAINTENANCE, DEVELOPMENT, AND FUTURE INTEGRATION

## 34. Personal GitHub development workflow

The current working policy is **personal GitHub only**.

Repository:

```text
https://github.com/samola4real/mdc_v1
```

Current accepted integration entered `main` at:

```text
f5a80ec2b71dd1195de2b4718f643c6e58a80c2a
```

For normal future frontend work:

```powershell
git switch main
git pull --ff-only origin main
git switch -c <focused-branch-name>
```

Then:

1. make scoped changes;
2. keep secrets/generated files out of Git;
3. run `npm ci` when dependency installation is needed;
4. run relevant tests/lint/build;
5. run `git diff --check`;
6. inspect the full diff and changed paths;
7. commit with a focused message;
8. push only the intended personal-GitHub branch;
9. review/merge into personal `main` through a normal non-force workflow;
10. update this manual when behavior, configuration, routes, or API mapping changes.

### 34.1 GitLab policy for this scope

Do not push, synchronize, release, or add a convenience GitLab remote as part of current frontend development. The historical GitLab repository is mentioned only because it explains where the original template came from and why a sanitized snapshot was necessary.

Historical release-planning documents under `docs/Demo_Frontend/` remain evidence of earlier planning, not a current instruction to publish there.

## 35. Relationship to the MDC backend master manual

Read this document together with:

```text
mdc-catalog/docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md
```

| Question | Authoritative source |
|---|---|
| How to use frontend pages/roles/forms | This frontend manual |
| Browser runtime configuration | This frontend manual/current frontend source |
| Browser-to-API service mapping | This frontend manual/current frontend source |
| Public API request/response semantics | Backend source + backend master manual |
| Provider lifecycle security/ETags | Backend source + backend master manual |
| PostgreSQL models/outbox | Backend master manual |
| RDF/Fuseki generation/synchronization | Backend master manual |
| Vercel/Neon/backend operations | Backend master manual |
| Future CMM integration boundaries | Both manuals, with backend contract authoritative |

When a browser behavior and backend contract disagree, do not rewrite the backend contract to match the UI. Correct the frontend.

## 36. Future CMM integration

A real CMM integration should preserve the current MDC contract while replacing demo ownership boundaries.

Target architecture:

```text
CMM browser UI
     |
     +--> public filters/discovery as deployment policy allows
     |
     v
CMM backend / BFF
     |
     +--> authenticates end user and organization
     +--> authorizes provider-specific operations
     +--> holds MDC lifecycle service credential
     +--> sends actor identity
     +--> reads/stores ETags
     +--> retries/rejects stale updates safely
     v
MDC trusted lifecycle API
     |
     v
PostgreSQL + outbox -> controlled semantic synchronization
```

Future CMM ownership should include:

- user registration/login/account recovery;
- organization/provider membership;
- authorization policy;
- provider drafts and approval;
- saved searches;
- quotations/contact/transactions;
- user-facing lifecycle history;
- server-side trusted MDC integration.

Demo JSON state and demo-overlay matching should not become hidden production behavior.

## 37. Known limitations and future work

Current limitations include:

- no real CMM integration;
- no browser-side trusted provider lifecycle by design;
- no production-grade provider/admin demo deployment defined here;
- client role guards are not backend authorization;
- demo persistence is a JSON file;
- demo overlay results are non-authoritative;
- demo RDF/Fuseki technical actions are reserved/not implemented;
- no quotation/contact/order workflow;
- no manufacturing routing engine;
- no live production-capacity scheduling;
- no CAD/2D/3D drawing analysis;
- no strong automated frontend unit/integration/browser/accessibility suite;
- no scoped frontend CI workflow;
- inherited template workspace pages remain in the application;
- result adapters retain some historical compatibility code;
- automatic semantic mapping from flexible provider fields to controlled MDC values is not implemented;
- frontend public-host deployment ownership is not proven by the repository alone.

---

# PART X — TROUBLESHOOTING AND REFERENCE

## 38. Troubleshooting

| Symptom | Likely cause | Corrective action |
|---|---|---|
| `npm ci` fails | Wrong Node/npm, damaged cache/lock mismatch, network | Use compatible Node 20, keep committed lockfile, retry clean install |
| `npm run dev` starts but `/demo` does not load | Wrong port/process/build problem | Check terminal, `http://localhost:3000`, browser console |
| Backend health fails | Django not running or wrong API URL | Start backend and verify port 8000/config.js |
| Browser CORS error | Frontend origin not allowed | Add exact frontend origin to backend CORS through controlled config |
| Browser calls localhost from a deployed site | `baseUrl` not overridden | Set deployed HTTPS MDC origin in public runtime config |
| Login button does nothing | Keycloak unavailable/misconfigured or initialization failed | Check realm/client/network/browser console |
| Login works but no MDC role appears | Token lacks recognized alias | Ask identity administrator to assign approved role; re-login |
| Child page redirects/denies | Not authenticated or selected role is wrong | Return to `/demo`, login/switch role |
| `/api/demo/...` returns 404 | Demo API disabled | Use local/dedicated demo environment; do not casually enable production demo API |
| Provider Preview fails | Demo API unavailable or invalid payload | Check demo health and response details |
| Saved provider shows `mapping-required` | Flexible registration lacks current controlled mapping | Select one of the three capability templates |
| Filters show fallback warning | `/api/catalog/filters` unavailable or wrong contract | Verify endpoint and backend contract 1.0 |
| Search returns 400 | Invalid family/type/field/range/contract | Inspect SearchPayloadPreview and backend error details |
| Search returns no providers | No compatible active offering or requirements too restrictive | Remove optional requirements or verify catalogue/runtime |
| Search returns `unknown_match` | Evidence/support is incomplete | Treat as not confirmed; do not claim support |
| Canonical search succeeds but overlay warning appears | Demo state endpoint unavailable | Canonical results remain valid; ignore overlay for authoritative truth |
| Admin backend/Fuseki card looks static | It is demo-reported metadata | Do not use it as live runtime proof |
| Admin smoke test returns HTTP 200 but warning | Endpoint body says `not_implemented` | Expected current behavior |
| Regenerate/Reload returns 501 | Interface is reserved | Expected current behavior; no state mutation occurred |
| Request times out | Backend/network/semantic processing >10 s | Check API/backend status and network; browser client timeout is 10 s |
| Lint shows five known warnings | Accepted baseline warnings | Ensure no additional warning was introduced |
| Build worker fails with environment permission error | Local sandbox/child-process restriction | Re-run in an environment that permits Next build workers; do not mask real build errors |

Do not troubleshoot by printing full `.env` files or authorization headers.

## 39. Glossary

| Term | Meaning |
|---|---|
| MaaSAI | Project context for Manufacturing-as-a-Service capabilities |
| MaaS | Manufacturing as a Service |
| MDC | MaaS Dynamic Catalogue |
| CMM | Cloud MaaS Marketplace; future external integration context, not this demo frontend |
| Provider | Organization offering manufacturing capability |
| Consumer | User/system searching for suitable offerings |
| Offering | A provider's manufacturing service description |
| Service discovery | Structured matching of a consumer request to offerings |
| Controlled vocabulary | Approved category/family/type/material/process/certification values |
| Custom field | Flexible staging fact not automatically promoted to a controlled semantic field |
| Demo API | `/api/demo/...` temporary demonstration namespace |
| Demo state | JSON-backed provider registration/update state for pilot use |
| Demo overlay | Browser-generated, explicitly labelled candidate from demo state |
| Keycloak | Identity provider/client technology used for browser login |
| PKCE | Browser-safe OAuth/OIDC authorization-code protection mechanism |
| CORS | Browser cross-origin request policy |
| ETag | Strong resource revision identifier used for trusted update concurrency |
| BFF | Backend for Frontend; server-side boundary for safe browser integrations |
| RDF | Graph representation generated by the MDC backend |
| Fuseki | Apache Jena RDF/SPARQL service used by the MDC semantic layer |
| RDFLib | Python RDF library used by MDC local semantic paths |
| Personal GitHub | Current maintained repository source `samola4real/mdc_v1` |
| Sanitized snapshot | Reviewed frontend content imported without unsafe historical Git objects |

## 40. Appendices

### Appendix A — Endpoint quick reference

| Class | Method | Path | Browser use |
|---|---|---|---|
| Public | GET | `/api/health` | Health |
| Public | GET | `/api/catalog/filters` | Search controls |
| Public | POST | `/api/service-discovery/search` | Consumer discovery |
| Demo | GET | `/api/demo/health` | Demo availability |
| Demo | GET | `/api/demo/service-discovery/backend-status` | Static/demo metadata |
| Demo | GET | `/api/demo/service-discovery/fuseki-smoke-test` | Reserved; current 200/not implemented |
| Demo | POST | `/api/demo/service-discovery/regenerate-rdf` | Reserved; current 501/not implemented |
| Demo | POST | `/api/demo/service-discovery/reload-fuseki` | Reserved; current 501/not implemented |
| Demo | GET | `/api/demo/provider-publication/state` | Demo provider state |
| Demo | POST | `/api/demo/provider-publication/preview` | Provider preview |
| Demo | POST | `/api/demo/provider-publication/simulate-update` | Demo save |
| Trusted | POST | `/api/provider-publication/validation` | Server-side only |
| Trusted | POST | `/api/provider-publication` | Server-side only |
| Trusted | GET, PATCH | `/api/providers/<provider_id>` | Server-side only |
| Trusted | GET, POST | `/api/providers/<provider_id>/offerings` | Server-side only |
| Trusted | GET, PATCH | `/api/offerings/<offering_id>` | Server-side only |

### Appendix B — Route/role quick reference

| Selected demo role | Dashboard | Provider | Consumer | Admin |
|---|---:|---:|---:|---:|
| Not authenticated | Public/login prompt | No | No | No |
| Provider | Yes | Yes | No | No |
| Consumer | Yes | No | Yes | No |
| Admin selecting Provider | Yes | Yes | No | No |
| Admin selecting Consumer | Yes | No | Yes | No |
| Admin selecting Admin | Yes | Yes | Yes | Yes |

### Appendix C — Important file map

| Concern | File(s) |
|---|---|
| Global route/auth composition | `src/pages/_app.js`, `src/config/routes.js` |
| Authentication | `src/layout/context/AuthContext.js`, `src/services/keycloak/keycloak.js` |
| Demo roles/menu | `src/components/mdc/demoAuth.js`, `DemoRoleGuard.js`, `src/layout/AppMenu.js` |
| Runtime API configuration | `public/config.js`, `src/config/runtimeConfig.js` |
| HTTP services | `src/services/mdc/*.js` |
| Consumer form/payload | `ConsumerSearchMockup.js` |
| Result adaptation/presentation | `searchResultFormatters.js`, `ProviderResultAccordion.js`, `SearchResultsList.js` |
| Provider form/payload | `ProviderDemoPanel.js`, `providerPayloadBuilder.js` |
| Admin | `AdminAuditPanel.js`, `DemoBackendStatusPanel.js` |
| Public backend contract | `backend/apps/api/public_contract.py`, service-discovery serializers/views |
| Demo backend | `backend/apps/demo/` |
| Trusted lifecycle security | `backend/apps/api/lifecycle_security.py` |

### Appendix D — First-time presenter checklist

- [ ] Personal GitHub `main` updated
- [ ] Clean working tree
- [ ] Python 3.12 environment available
- [ ] Backend dependencies installed
- [ ] Local `.env` present but uncommitted
- [ ] `python backend/manage.py migrate` completed
- [ ] Django running on port 8000
- [ ] `/api/health` HTTP 200
- [ ] `/api/catalog/filters` contract 1.0
- [ ] `/api/demo/health` HTTP 200 for full demo
- [ ] Node 20 available
- [ ] `npm ci` completed
- [ ] `npm run dev` running on port 3000
- [ ] Keycloak login works
- [ ] Recognized demo role available
- [ ] Provider Preview tested
- [ ] Consumer Search tested
- [ ] Admin not-implemented interfaces interpreted correctly

### Appendix E — Safe deployment checklist

- [ ] Reviewed source commit and clean build
- [ ] HTTPS frontend origin
- [ ] HTTPS backend origin
- [ ] Correct public runtime config
- [ ] No secrets in `config.js` or bundle
- [ ] Exact backend CORS/CSRF origins
- [ ] Keycloak public client redirect/web origins confirmed
- [ ] Demo API policy explicitly decided
- [ ] Backend secrets stay server-side
- [ ] Lint/build/manual smoke passed
- [ ] Built assets/changed paths secret-risk reviewed
- [ ] Rollback owner and prior deployment identified

### Appendix F — Personal GitHub maintenance checklist

- [ ] Start from current personal `main`
- [ ] Create focused branch
- [ ] Make only intended changes
- [ ] No `.env`, tokens, credentials, build output, or dependency directories tracked
- [ ] Run relevant frontend/backend tests
- [ ] `npm run lint` and `npm run build` for material frontend changes
- [ ] `git diff --check` passes
- [ ] Review changed-file list and full diff
- [ ] Commit with focused message
- [ ] Push only to intended personal-GitHub branch
- [ ] Use normal review/merge; never force-push `main`
- [ ] Update this manual when behavior changes
- [ ] No GitLab push/synchronization for the current scope

### Appendix G — Maintenance rules

1. Verify current source before changing behavioral claims.
2. Keep public, demo, and trusted lifecycle interfaces visibly separate.
3. Do not introduce `/api/v1` examples unless the backend really adds that route.
4. Never instruct a browser to hold trusted credentials.
5. Treat demo provider state and overlays as non-authoritative.
6. Keep flexible provider facts separate from controlled MDC values until explicitly mapped.
7. Re-run lint/build/manual role journeys after material UI changes.
8. Re-run secret-risk and whitespace checks before committing.
9. Keep the personal GitHub repository as the maintained source for this scope.
10. Update this manual together with accepted frontend contract, configuration, workflow, or deployment changes.

### Appendix H — Five-minute demonstration script

If time is limited, use this sequence:

1. Show `/demo` and explain that it is a Marketplace-like demonstration, not the real CMM.
2. Select **Provider** and show **Register New Provider**. Add one flexible offering/capability fact and click **Preview**. Explain flexible staging versus controlled MDC fields.
3. Switch to **Consumer**. Use the default Spur Gear request. Expand the payload preview, click **Search MDC**, and open one provider result. Explain matched/unmatched/unknown evidence.
4. If a demo provider was saved and matches the request text/domain, point out the **Demo registered provider** label and explain that it is not canonical catalogue truth.
5. Switch to **Admin**. Show backend/demo health and explain that backend/Fuseki direction cards are demo metadata, while the reserved technical actions are currently not implemented.
6. Finish with the target architecture: real CMM would own login/provider authorization and call trusted lifecycle APIs through a server-side BFF while MDC remains the catalogue/discovery service.

---

## Final operating statement

For the current MaaSAI MDC pilot demonstration, use this document as the primary frontend operating manual and `docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md` as the backend authority. The integrated frontend is maintained in personal GitHub. Run the complete provider/consumer/admin demonstration against a deliberately demo-enabled local or dedicated backend, keep trusted lifecycle credentials server-side, and treat all demo-state overlays and reserved admin actions exactly as labelled.