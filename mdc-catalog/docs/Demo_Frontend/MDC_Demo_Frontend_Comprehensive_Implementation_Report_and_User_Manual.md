# MaaSAI MaaS Dynamic Catalogue Demo Frontend

## Comprehensive Implementation Report and User Manual

**Document status:** Current accepted frontend implementation baseline and operating manual

**Frontend baseline:** `b207022363163a026a1d77e6485fd151e81aa750` (`fix: align MDC demo frontend with current API contract`)

**Public MDC contract:** `1.0`

**Application location:** `mdc-catalog/demo-frontend/`

> **Scope and source rule.** This document describes the current frontend code first, then the current MDC backend contract. Historical reports explain how the implementation evolved; they do not override current source. This is an illustrative **MDC demonstration frontend**, not the Cloud MaaS Marketplace (CMM), and it does not claim that real Marketplace integration exists.

## Contents

1. Executive summary
2. How to use this manual
3. Project context and original motivation
4. Evolution and history
5. Repository strategy and security-preserving import
6. Technology stack
7. Frontend architecture
8. Repository and file structure
9. Routing and navigation
10. Authentication and demo roles
11. Runtime configuration
12. API integration overview
13. MDC service client
14. Consumer service-discovery workflow
15. Search payload construction
16. Search result rendering
17. Provider demonstration workflow
18. Flexible provider input versus controlled MDC fields
19. Admin and audit demonstration
20. Public API examples
21. Trusted provider lifecycle boundary
22. Local setup and execution
23. Validation and accepted evidence
24. Testing guidance
25. Docker and build behavior
26. Deployment guidance
27. Security model and limitations
28. Git workflow for daily development
29. GitHub-to-GitLab official release workflow
30. Relationship to the MDC backend master manual
31. Future CMM integration
32. Known limitations and future work
33. Troubleshooting
34. Glossary
35. Appendices

## 1. Executive summary

The MaaSAI MaaS Dynamic Catalogue (MDC) demo frontend is a Next.js browser application that makes the MDC pilot understandable and demonstrable to providers, consumers, administrators, developers, and reviewers. It shows how a provider might describe manufacturing offerings, how a consumer might search for capable providers, and how an administrator might inspect a demo environment.

The application was created while the real CMM user interface and integration boundaries were unavailable. It is therefore a Marketplace-like illustration around the real MDC API, not CMM itself. It does not own Marketplace registration, production identity, provider authorization, quotation, orchestration, or commercial workflows.

The accepted frontend state is the sanitized snapshot plus the API/configuration cleanup at commit `b207022363163a026a1d77e6485fd151e81aa750`. Consumer search uses the current unversioned public endpoints and contract `1.0`. Provider and administrator demonstrations use explicitly separate `/api/demo/...` endpoints. The browser intentionally does not call trusted provider lifecycle APIs because their service identity, actor attribution, and concurrency credentials belong behind a server-side Marketplace or backend-for-frontend (BFF) boundary.

The MDC backend remains authoritative for catalogue data, public contract validation, matching, persistence, RDF/Fuseki integration, and trusted lifecycle security. This frontend is authoritative only for the current browser experience and browser-to-API mapping.

## 2. How to use this manual

| Goal | Read |
|---|---|
| Understand what exists and what it is not | Sections 1, 3, 7, 32 |
| Understand the source/import history | Sections 4, 5, 28, 29 |
| Run the frontend locally | Sections 11, 22, 24 |
| Configure backend and Keycloak URLs | Sections 10, 11, 26 |
| Understand routes and navigation | Sections 8–10 |
| Demonstrate consumer search | Sections 14–16, 20 |
| Demonstrate provider registration/update | Sections 17–18 |
| Demonstrate the admin console | Section 19 |
| Integrate with MDC APIs | Sections 12, 13, 20, 21 |
| Review security boundaries | Sections 5, 21, 27 |
| Troubleshoot | Section 33 |
| Prepare a future official GitLab release | Section 29 and Appendix F |
| Plan real CMM integration | Sections 21, 30–32 |

## 3. Project context and original motivation

MDC is the MaaSAI component that describes manufacturing providers and offerings and performs evidence-based service discovery. Pilot users needed a concrete way to see those interactions before the Marketplace and the other MaaSAI components were integrated. The demo frontend fills that communication and interaction gap.

```text
Provider / Consumer / Admin user
             |
             v
Marketplace-like frontend demonstration
             |
             v
          Django MDC API
             |
             v
MDC catalogue / discovery runtime
```

The provider screens illustrate flexible data capture and a later controlled mapping process. The consumer screens exercise the real public filters and discovery contract. The admin screen exposes demo status and controlled demo actions. Real Marketplace account registration, login ownership, provider/consumer identity governance, authorization, lifecycle orchestration, quotation, and release operations remain outside this demo.

## 4. Evolution and history

The implementation history under `docs/Demo_Frontend/Implementation_History/` records incremental work. It is useful evidence, but many early assumptions are superseded.

| Stage | Evidence | Meaning today |
|---|---|---|
| MaaSAI template | Historical source `main` at `832ad57265bce0889ebea58bc69c031c3b394ee7` | Supplied Next.js layout, workspace pages, styling, Keycloak foundation, and Docker assets |
| F1–F3 | Static shell, service wrappers, status integration | Established demo pages and browser service layering |
| F4 series | Consumer forms, gear/shaft/metal-part payload fixes, result UI | Evolved toward grouped requirements and backend-compatible payloads |
| F5 series | Provider preview/save, role selection, flexible fields, saved state | Established demo-only provider and role experiences |
| F7–F8 | Demo search overlay, navigation, dashboard, admin cleanup | Produced the current role-oriented demonstration |
| Preservation | Four approved tracked modifications plus untracked MDC work were captured | Preserved the exact dirty working-tree result without modifying the original repository |
| Sanitized import | `e411e7300cfbe2f9f3f9fe245027f2c0c341cd38` | Imported a content snapshot, not GitLab history |
| API/config cleanup | `b207022363163a026a1d77e6485fd151e81aa750` | Aligned endpoints, filters, response adapters, configuration, routes, and documentation with current MDC |

Earlier reports may mention static filters, older nested/internal search results, stale lifecycle browser helpers, or experimental route assumptions. The current code supersedes them. In particular, current code does not use `/api/v1/...`, does not expose `material_grades` as a search criterion, and does not call trusted lifecycle writes from the browser.

The sanitized import preserved inherited source formatting. The subsequent cleanup used a one-time, explicitly scoped exception to normalize nine inherited whitespace files so `git diff --check` could become a reliable gate. That exception is historical, not permission for broad formatting rewrites.

## 5. Repository strategy and security-preserving import

The original GitLab working tree was preserved outside this repository, including its approved dirty state. A separate staging tree was built, screened, and hashed. The import copied only that sanitized staging content into `mdc-catalog/demo-frontend/` and copied 30 sanitized historical reports into the documentation tree. Provenance records 134 application files and the original source commit.

Original Git history was deliberately excluded because credential-bearing objects existed in it. Deleting a secret from the latest tree would not remove it from older reachable objects; importing unsquashed GitLab history would therefore have exposed avoidable risk in personal GitHub.

The snapshot excluded original `.git` objects, environment files, credential assignments, raw identity-realm exports, editor state, dependencies, build output, caches, logs, and generated archives. Exact provenance and hashes matter because they show what source was used, what was omitted, and that the historical repository was not silently altered.

Personal GitHub is the controlled development location for this sanitized snapshot. GitLab retains historical continuity and remains the official frontend release destination. Publication back to GitLab is a separately approved file synchronization through a fresh GitLab checkout and release branch. It is never a subtree push, unrelated-history merge, history replacement, or force push.

## 6. Technology stack

| Technology | Current repository evidence | Role |
|---|---|---|
| Next.js | `14.0.3`, Pages Router | Routing, SSR-capable shell, build and standalone server |
| React / React DOM | `^18` | Component and state model |
| PrimeReact | `^10.2.1` | Cards, panels, forms, tables, accordions, messages, toasts |
| PrimeFlex | `^3.3.1` | Responsive utility layout |
| PrimeIcons | `^6.0.1` | Interface icons |
| Axios | `^1.5.1` | Browser HTTP client |
| Keycloak JS | `^23.0.1` | Browser authentication client |
| Sass | `^1.58.3` | Layout and demo styling |
| Chart.js / React Flow | `4.2.1` / `^11.11.4` | Inherited workspace visualization features |
| Node.js | Docker build ARG `20.18.0` | Build/runtime baseline; use a compatible Node 20 locally |
| npm lockfile | committed lockfile version 2 | Reproducible `npm ci` input |

The app uses JavaScript rather than TypeScript. `jsconfig.json` maps `@/*` to `src/*`. ESLint extends `next/core-web-vitals`, with selected warnings retained. No package installation or dependency change is part of this documentation milestone.

## 7. Frontend architecture

```text
Browser
  +-- Next.js pages and ROUTE_ACCESS
  +-- Layout, menu, theme and Keycloak AuthContext
  +-- Session-scoped demo-role selection and component guards
  +-- MDC provider, consumer and admin components
  +-- Result/payload adapters and static fallback vocabulary
  +-- Axios MDC service wrappers
  +-- /config.js -> window.MAASAI_CONFIG
            |
            | HTTP/JSON
            v
Django MDC
  +-- canonical public APIs under /api
  +-- demo-only APIs under /api/demo
  +-- trusted lifecycle APIs under /api (not called by browser)
```

Pages compose screen-level content. `_app.js` wraps all pages with theme, authentication, layout, and centralized route protection. `routes.js` is the route-access source. `AppMenu.js` applies route visibility and the selected demo role. `DemoRoleGuard` performs page-content presentation checks.

`AuthContext` loads `/config.js`, initializes one Keycloak instance with PKCE S256, exposes login/logout/user/role state, and refreshes expiring tokens. Demo-role utilities normalize identity roles and store the user's active demonstration role in session storage.

MDC components build forms, payload previews, result panels, and status dashboards. Service wrappers isolate URL construction and HTTP behavior. `mockData.js` is a visible fallback only when canonical filters cannot be loaded. `searchResultFormatters.js` adapts the current flattened public response while retaining compatibility with historical/demo shapes.

## 8. Repository and file structure

```text
mdc-catalog/
  demo-frontend/
    public/
      config.js                    public runtime settings
      layout/images/               MaaSAI assets
      themes/                      PrimeReact light/dark/HMI themes
    src/
      config/                      runtime config and route access map
      layout/                      shell, top bar, menu, contexts
      pages/                       Pages Router entries
        demo/                      dashboard, provider, consumer, admin
        home/ and workspace/       inherited template pages
      components/mdc/              MDC forms, guards, status and results
      services/mdc/                API client and endpoint wrappers
      services/keycloak/           single-init Keycloak adapter
      styles/                      layout, demo and responsive Sass
    package.json / package-lock.json
    next.config.js
    Dockerfile / docker-compose.yml / Makefile
  docs/Demo_Frontend/              provenance, release mapping and this manual
```

Add or modify screen routes in `src/pages/`; MDC reusable UI in `src/components/mdc/`; endpoint calls in `src/services/mdc/`; route access in `src/config/routes.js`; runtime fields in `runtimeConfig.js` and `public/config.js`; navigation in `src/layout/AppMenu.js`; and visual rules in `src/styles/`. API contract changes must begin with backend/source review rather than copying historical examples.

## 9. Routing and navigation

The current Pages Router entries include:

| Route | Route-map access | Additional behavior |
|---|---|---|
| `/` | Public | Template landing page |
| `/demo` | Public | Demo console; prompts login, role selection, or role actions |
| `/demo/provider` | Authenticated | `DemoRoleGuard`: provider or admin-selected role |
| `/demo/consumer-search` | Authenticated | `DemoRoleGuard`: consumer or admin-selected role |
| `/demo/admin-audit` | Authenticated | `DemoRoleGuard`: admin-selected role |
| `/404` | Public | Explicit not-found page |
| `/home/Contact`, `/home/Help`, `/home/Brand`, `/home/AccessDenied`, `/home/ErrorPage` | Public | Template information/support pages |
| `/home/EmptyPage`, `/workspace/*` | Authenticated | Inherited template workspace |

Unknown routes default to authenticated in `routes.js`. `_app.js` redirects unauthenticated denied navigation to `/` and authenticated denied navigation to `/home/AccessDenied`. The demo child routes are only marked `authenticated` centrally; role selection is enforced inside their components and reflected in the menu.

The cleanup moved reusable `DashboardContent` and `NotFoundPage` files out of the pages tree into `src/components/home/`. This removed accidental `/home/DashboardContent` and `/home/NotFoundPage` URL generation while preserving their use as components.

## 10. Authentication and demo roles

At startup, `AuthContext` loads runtime settings and, when Keycloak is enabled, initializes `keycloak-js` with `check-sso`, `checkLoginIframe: false`, and PKCE S256. Display name resolution uses token name, preferred username, or given/family name. Roles are collected from realm roles and all resource-access roles.

Demo roles accept these aliases:

| Normalized role | Recognized identity-role names |
|---|---|
| Provider | `provider`, `mdc_provider`, `maas_provider` |
| Consumer | `consumer`, `mdc_consumer`, `maas_consumer` |
| Admin | `admin`, `mdc_admin`, `maas_admin` |

The primary-role priority is admin, provider, then consumer. After login, the user selects an active demo role. It is stored only for the browser tab/session under `mdc_demo_selected_role`; a custom event updates components immediately. Admin users may select any of the three demo roles. Logout clears the selected role from the dashboard flow.

The sidebar shows only the MDC section to recognized demo users and filters child items by the selected role. Users without a recognized role see an explanatory warning. Role switching returns to the dashboard choice.

These checks are presentation and navigation controls. Session storage is not a trust store, hidden menu items are not authorization, and client JavaScript can be modified by its user. Every sensitive backend action must independently authenticate and authorize the request.

## 11. Runtime configuration

`public/config.js` defines `window.MAASAI_CONFIG`. `AuthContext` dynamically loads `/config.js` if it is not already present. `getRuntimeConfig()` deeply merges the `keycloak` and `mdcApi` groups over built-in defaults.

| Field | Purpose |
|---|---|
| `keycloak.enabled` | Enables browser Keycloak initialization |
| `keycloak.realmUrl` | Public realm URL; the adapter splits base URL and realm |
| `keycloak.clientId` | Public browser client identifier |
| `keycloak.onLoad` | Initialization mode, currently normally `check-sso` |
| `mdcApi.baseUrl` | Backend origin; local default is `http://localhost:8000` |
| `mdcApi.sharedApiPrefix` | Canonical prefix, `/api` |
| `mdcApi.demoApiPrefix` | Demo prefix, `/api/demo` |

Safe deployed example:

```js
window.MAASAI_CONFIG = {
  keycloak: {
    enabled: true,
    realmUrl: 'https://identity.example.org/realms/example',
    clientId: 'mdc-demo-browser',
    onLoad: 'check-sso'
  },
  mdcApi: {
    baseUrl: 'https://mdc-api.example.org',
    sharedApiPrefix: '/api',
    demoApiPrefix: '/api/demo'
  }
};
```

Everything delivered to a browser is public, including `config.js`, JavaScript bundles, network requests, and storage. Never put lifecycle service tokens, database credentials, private keys, Django secrets, Fuseki credentials, or other secrets in this configuration, `NEXT_PUBLIC_*`, source code, local storage, or session storage.

The localhost backend is a development convention only. Deployment requires an HTTPS backend origin and matching backend CORS/origin policy. A deployed frontend left on `http://localhost:8000` would ask each user's own machine for the API and may also be blocked as mixed content.

## 12. API integration overview

### 12.1 Canonical public MDC APIs called by the browser

| Method and path | Frontend service | Use |
|---|---|---|
| `GET /api/health` | `health.service.js` | Shared backend health |
| `GET /api/catalog/filters` | `catalog.service.js` | Current form vocabulary and family relationships |
| `POST /api/service-discovery/search` | `search.service.js` | Canonical service discovery |

These routes are unversioned. Contract versioning is represented in JSON as `contract_version: "1.0"`. `/api/v1/...` is not a current route.

### 12.2 Demo-only APIs present in the current service layer

| Method and path | Current use |
|---|---|
| `GET /api/demo/health` | Dashboard/admin demo availability |
| `GET /api/demo/service-discovery/backend-status` | Runtime labels/status |
| `GET /api/demo/service-discovery/fuseki-smoke-test` | Admin read-only smoke action |
| `POST /api/demo/service-discovery/regenerate-rdf` | Confirmed admin action; current backend returns `501`, `mutates_state: false` |
| `POST /api/demo/service-discovery/reload-fuseki` | Confirmed admin action; current backend returns `501`, `mutates_state: false` |
| `GET /api/demo/provider-publication/state` | Provider list, admin summary, optional consumer overlay |
| `POST /api/demo/provider-publication/preview` | Non-mutating provider payload validation/normalization preview |
| `POST /api/demo/provider-publication/simulate-update` | Saves registration/update into demo JSON state |

The backend guards the entire demo namespace. Production settings default `MDC_DEMO_API_ENABLED` to false, so these routes normally return 404 unless a demo environment deliberately enables them. Status panels, provider state, and overlay loading show warnings or fallbacks. Provider preview/save and admin actions show normalized error states.

The browser intentionally has no helpers for trusted provider validation, publication, provider/offering reads, POST offering creation, or PATCH updates. Those endpoints require a trusted server-side boundary described in Section 21.

## 13. MDC service client

`src/services/mdc/client.js` trims leading/trailing slashes, joins the configured origin and prefix, and supports an empty base URL for same-origin deployment. `sharedPath()` and `demoPath()` keep the namespaces explicit.

Requests use Axios, a 10,000 ms default timeout, JSON content type, optional headers/query parameters, and return `response.data`. Failures are normalized to `{message, status, details}`. The message preference is current nested `response.data.error.message`, then legacy top-level `response.data.message`, then the Axios message. Details prefer `error.details`, then `error`, then the raw response body.

The current backend error envelope is:

```json
{
  "contract_version": "1.0",
  "error": {
    "code": "invalid_service_discovery_request",
    "message": "The service-discovery request is invalid.",
    "details": {}
  }
}
```

Compatibility handling is presentation-only; it does not redefine the canonical backend contract. The service barrel exports health, catalogue, search, and demo-admin modules.

## 14. Consumer service-discovery workflow

```text
Open Consumer Search
  -> load GET /api/catalog/filters
  -> choose family/type/material/process/certification/specifications
  -> derive service category and build grouped requirements
  -> POST /api/service-discovery/search
  -> adapt flattened public results
  -> optionally load and merge labelled demo-state matches
  -> render suitability and capability evidence
```

The page starts with a known demonstration form and requests filter contract `1.0`. `service_categories` and `part_families` are transformed to PrimeReact `{value,label}` options. Relationships on either list build family-to-service-category lookup. `part_types` remains keyed by part family. Materials, processes, and certifications are transformed without silently filtering newly returned values.

Changing family selects the first part type returned for that family. Service category is not an editable user field; it is derived from the API relationship, with the explicit demo mapping (`gear` to `precision_gears`, `shaft` to `precision_shafts`, `metal_part` to `precision_metal_parts`) as fallback.

If the filters response is unavailable or not contract `1.0`, the UI displays a warning and uses explicit static demo vocabulary. This keeps a presentation usable but does not turn fallback values into authoritative catalogue truth.

After canonical search, the browser optionally reads demo provider state. It compares normalized family/type/domain/search terms, avoids provider-ID duplicates already returned by the backend, and appends matching entries marked `Demo registered provider`. Failure to read demo state never invalidates successful canonical results.

## 15. Search payload construction

Every payload has consumer/request identity, a controlled selection, three requirement scopes, and a match policy. Empty values are removed. `unknown_policy` is `keep_as_unknown`, `optional_match_mode` is `score_only`, and `minimum_score` is null. `material_grades` is not emitted because it is not a canonical consumer criterion.

### 15.1 Representative gear request

```json
{
  "request_id": "req-demo-gear-001",
  "consumer_id": "consumer_demo_001",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear",
  "requirements": {
    "part_family_specifications": {
      "module": { "exact": 2 },
      "diametral_pitch": { "min": 10, "max": 10 },
      "outside_diameter_mm": { "max": 100 },
      "gear_quality": { "standard": "DIN", "max_class": 6 },
      "tolerance_mm": { "max": 0.02 }
    },
    "part_type_specifications": {
      "face_width_mm": { "exact": 25 }
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

### 15.2 Representative shaft request

```json
{
  "request_id": "req-demo-shaft-001",
  "consumer_id": "consumer_demo_001",
  "service_category": "precision_shafts",
  "part_family": "shaft",
  "part_type": "splined_shaft",
  "requirements": {
    "part_family_specifications": {
      "length_mm": { "max": 220 },
      "outer_diameter_mm": { "max": 35 },
      "tolerance_mm": { "max": 0.02 }
    },
    "part_type_specifications": {
      "spline_module": { "exact": 1.5 }
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

For `hollow_shaft`, the type scope uses `inner_diameter_mm` as a maximum and `wall_thickness_mm` as an exact value instead of spline module.

### 15.3 Representative metal-part request

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
        "length_mm": { "max": 150 },
        "width_mm": { "max": 80 },
        "height_mm": { "max": 20 }
      }
    },
    "part_type_specifications": {
      "vertical_flange_length_mm": { "max": 40 },
      "horizontal_flange_length_mm": { "max": 40 }
    },
    "generic_requirements": {
      "materials": ["alloyed_carburizing_steel"],
      "processes": ["turn_mill"],
      "certifications": ["ISO9001_2015"],
      "weight_kg": 2.5,
      "tolerance_mm": { "max": 0.02 },
      "surface_finish_ra_um": { "max": 3.2 }
    }
  },
  "match_policy": {
    "unknown_policy": "keep_as_unknown",
    "optional_match_mode": "score_only",
    "minimum_score": null
  }
}
```

Current metal types are block, bracket, plate, bushing, roller, and collar. Their fields map to bounding boxes, diameters, length, tolerance, flange dimensions, or hole count as supported by the backend schema. Positive-number guards omit invalid weight/surface-finish values. Some legacy form state names remain in source but are not sent unless mapped by `buildSearchPayload`; payload preview is the definitive browser request.

## 16. Search result rendering

The canonical public response provides top-level request context and flattened results. Each result supplies `provider_id`, `provider_name`, `offering_id`, `offering_name`, `service_category`, `part_family`, `match`, and `matched_capabilities`, `unmatched_capabilities`, and `unknown_capabilities` arrays.

The adapter maps those capability arrays to the established presentation names while preserving fields, requested/provided values, reasons, and implied status. Response-level `part_type` is passed into result presentation. It also accepts older nested/internal and demo-overlay shapes solely for compatibility.

Provider accordions show provider/offering identity, requested part type, suitability, support status, materials, processes, certifications, capability ranges, unknown reasons, and optional advanced/debug data. `match.score` remains available in advanced details; the main UI emphasizes evidence and does not present the score as provider quality, commercial ranking, or probability.

Demo overlay results carry a visible label and summary/custom-field tables. They do not claim backend-canonical evidence. Quote, contact/provider, save, or similar result actions are illustrative toast actions for a future Marketplace workflow, not completed transactions.

Older reports show nested `provider`, `offering`, `evidence`, and `matched_attributes` structures. Those are historical/internal compatibility shapes, not the current public contract.

## 17. Provider demonstration workflow

The provider page has two modes.

**Register New Provider** collects provider ID/name/country/description and one offering. Registration intentionally uses flexible staging: offering name/ID, arbitrary custom offering name/value pairs, and arbitrary custom capability name/value/unit/notes rows. Preview calls the demo preview endpoint; demo save calls `simulate-update` with action `register_provider` and then refreshes saved demo state.

**Update Existing Provider** starts with static Tasowheel example rows and merges saved demo providers from the state endpoint by stable provider/offering identity. The table is sortable and paginated. Selecting a row fills provider/offering and controlled capability fields. Update payloads include publication metadata, certifications, service category, family, template, supported types, support status, and template-specific capabilities.

Templates are:

| Template | Main controlled presentation |
|---|---|
| Gear manufacturing | module, outside diameter, quality |
| Shaft manufacturing | length, outer diameter, spline module |
| Metal-part manufacturing | maximum dimensions, tolerance, surface finish |
| General precision manufacturing | description, keyword list, maximum-size description |

Common update capabilities include materials, available grades, processes, certifications, batch size, lead time, maximum weight, and notes. Template selection applies defaults. Payload panels expose the exact JSON for review.

Preview is non-mutating. Demo save writes `data/demo/provider_demo_state.json` through the demo backend when enabled; registrations and updates are maintained in separate state maps. This is not PostgreSQL lifecycle registration, not authoritative publication, and not automatic RDF/Fuseki synchronization.

## 18. Flexible provider input versus controlled MDC fields

Provider business descriptions often arrive as spreadsheets or free text. MDC discovery, however, depends on stable categories, families, types, units, and evidence semantics. The demo reflects a safe two-layer principle:

- flexible/staging fields can preserve provider-supplied facts;
- controlled fields remain aligned with the MDC registry and ontology;
- arbitrary text is not silently promoted into searchable controlled properties;
- custom fields retain facts until a person or future governed mapping process can classify them.

Registration mode therefore demonstrates broad custom input. Update mode demonstrates richer controlled structures. The current code does not implement automatic semantic mapping, approval, or authoritative publication of custom fields. A future workflow must validate mappings explicitly.

## 19. Admin and audit demonstration

The admin page loads shared health, demo health, backend status, demo provider state, and canonical catalogue filters in parallel. Status cards summarize API availability, demo enablement, active/fallback discovery labels, Fuseki dataset label, provider/update counts, last update, and filter counts. Raw responses are available in collapsed advanced panels.

Read-only calls are health, backend status, provider state, catalogue filters, and Fuseki smoke test. Provider preview is also non-mutating but belongs to the provider page. `simulate-update` mutates demo JSON state. Admin RDF regeneration and Fuseki reload require browser confirmation; current backend implementations return HTTP 501 and explicitly report `mutates_state: false`. They are reserved interfaces, not working production operations.

Missing/disabled demo endpoints appear as unavailable/warning states. A 404 is explained as likely demo API disablement. Partial success remains visible rather than collapsing every card into one failure.

The selected admin role only controls browser presentation. Backend deployment policy and backend authorization remain decisive.

## 20. Public API examples

### Health

```json
{
  "contract_version": "1.0",
  "status": "ok",
  "service": "maasai-mdc"
}
```

### Catalogue filters (shortened)

```json
{
  "contract_version": "1.0",
  "service_categories": [
    { "value": "precision_gears", "label": "Precision gears", "part_family": "gear" }
  ],
  "part_families": [
    { "value": "gear", "label": "Gear", "service_category": "precision_gears" }
  ],
  "part_types": {
    "gear": [{ "value": "spur_gear", "label": "Spur gear" }]
  },
  "materials": [{ "value": "alloyed_carburizing_steel", "label": "Alloyed carburizing steel" }],
  "processes": [{ "value": "hobbing", "label": "Hobbing" }],
  "certifications": [{ "value": "ISO9001_2015", "label": "ISO 9001:2015" }]
}
```

Clients must load the complete current lists rather than treat this shortened example as the registry.

### Discovery request

Use one of the payloads in Section 15 with `POST /api/service-discovery/search` and `Content-Type: application/json`.

### Discovery response (shortened)

```json
{
  "contract_version": "1.0",
  "request_id": "req-demo-gear-001",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear",
  "result_count": 1,
  "results": [{
    "provider_id": "example_provider",
    "provider_name": "Example Provider",
    "offering_id": "example_precision_gears",
    "offering_name": "Precision gear manufacturing",
    "service_category": "precision_gears",
    "part_family": "gear",
    "match": { "status": "full_match", "score": 1.0 },
    "matched_capabilities": [
      { "field": "module", "requested": { "exact": 2 }, "provided": { "min": 1, "max": 4 } }
    ],
    "unmatched_capabilities": [],
    "unknown_capabilities": []
  }]
}
```

### Error envelope

```json
{
  "contract_version": "1.0",
  "error": {
    "code": "unsupported_contract_version",
    "message": "The requested contract version is not supported."
  }
}
```

## 21. Trusted provider lifecycle boundary

The current backend separately exposes trusted provider validation, registration, reads, offering creation, and PATCH updates. These are not consumer/public browser APIs.

```text
Browser / Marketplace UI
          |
          v
Marketplace backend or BFF
          |
          | trusted bearer identity
          | actor attribution
          | ETag / If-Match concurrency
          v
MDC trusted provider lifecycle API
```

The pilot backend can require a bearer service token. Writes can require `X-MDC-Actor-Id`. Reads return strong ETags; updates send the current value in `If-Match` (with a temporary pilot compatibility header documented in the backend manual). Missing, malformed, or stale preconditions have distinct errors. These controls prevent anonymous writes and lost updates at a service boundary.

Putting a service token in browser code would disclose it to every user and allow impersonation of the trusted integration. The real CMM or a BFF must hold the credential server-side, authenticate the end user, authorize that user against the provider, attribute the action, manage ETags, and return only safe results to the browser. The current frontend implements none of those trusted calls.

## 22. Local setup and execution

From a clean checkout:

1. Enter `mdc-catalog/demo-frontend/`.
2. Install a compatible Node 20 release; the Docker baseline is Node `20.18.0`.
3. Review `public/config.js` without adding secrets. For the standard local topology, keep the API origin at `http://localhost:8000`.
4. Install exactly the committed dependency graph:

   ```bash
   npm ci
   ```

5. Start development:

   ```bash
   npm run dev
   ```

6. Open `http://localhost:3000/demo`.

The local API assumption is a Django MDC server on port 8000 with CORS permitting the frontend origin. Demo provider/admin functionality also requires the backend demo API to be enabled.

Validation and production-style execution:

```bash
npm run lint
npm run build
npm run start
```

`npm run start` serves the previously built application, normally on port 3000. Do not edit `.env` for browser runtime configuration and do not put secrets into public assets.

## 23. Validation and accepted evidence

The accepted API/config cleanup milestone recorded the following evidence. These are results of that run, not perpetual guarantees about future commits or registries.

| Gate | Accepted evidence |
|---|---|
| Snapshot/current-tree secret-risk scans | Passed; no credential values were published |
| `git diff --check` | Passed after the approved inherited-whitespace cleanup |
| `npm ci` | Passed; 358 packages installed |
| Audit output from that install | 0 vulnerabilities reported |
| `npm run lint` | Exit 0 with five pre-existing warnings: one `AppMenuitem` hook warning, three layout hook warnings, one `_document.js` CSS warning |
| `npm run build` | Passed; an initial sandbox `EPERM` was environmental and the authorized rerun succeeded |
| Route sanity | Expected `/`, `/404`, `/demo`, three demo children, home/workspace routes built; accidental component routes absent |
| Public deployed backend smoke | Health, filters, and search returned HTTP 200 and contract `1.0`; filters had expected groups; search had flattened result/capability arrays |
| Dependency artifacts | `package.json` and lockfile unchanged; generated build/dependency files untracked/ignored |

No frontend test suite or compatible GitHub Actions workflow was added. The public backend smoke target proves API compatibility at a point in time, not that this frontend is deployed there.

## 24. Testing guidance

### Manual acceptance checklist

**Unauthenticated:** open `/` and `/demo`; confirm public rendering, login prompt, and redirection from authenticated child routes.

**Provider:** log in with a recognized provider alias, select Provider, verify only appropriate MDC navigation, preview a valid registration, and—only in a disposable demo environment—save and confirm it appears in Update Existing Provider.

**Consumer:** select Consumer, verify canonical filter values, family-dependent types, gear/shaft/each metal-part field group, payload preview, loading, success, no-result, capability arrays, and clearly labelled overlay entries.

**Admin:** select Admin, verify role switching, status cards, partial errors, advanced responses, provider state, filter counts, smoke test, and confirmation prompts. Expect current regenerate/reload endpoints to return not implemented.

**Filter outage:** make only the filters call unavailable; verify a visible fallback warning and usable static choices.

**Demo disabled:** target a production-like backend with demo API off; verify public search still works and demo panels show 404/unavailable warnings without claiming public API failure.

**Backend unavailable/CORS:** verify timeout/network messages and that no sensitive request data is logged or displayed.

**Search cases:** test valid response, 400 validation error, no providers, matched/unmatched/unknown capabilities, and demo-state read failure after canonical success.

Future work should add focused unit tests for config/path builders, payload builders, filter/result normalization, role utilities, and components; integration tests with mocked APIs; browser tests for role journeys; accessibility checks; and a scoped CI policy approved for this repository.

## 25. Docker and build behavior

`next.config.js` enables standalone output, React strict mode, SWC minification, optimized Prime package imports, local/approved remote image configuration, removes `X-Powered-By`, and applies HSTS, frame, content-type, referrer, DNS-prefetch, and permissions headers.

The Dockerfile has dependency, builder, and runner stages on Node 20.18/Alpine 3.20. It runs `npm ci`, builds Next.js, copies only standalone server/static/public assets, runs as a non-root `nextjs` user, exposes port 3000, and uses `wget` for health checking.

Compose maps a configurable host port, mounts `public/config.js` read-only for runtime overrides, drops capabilities, prevents privilege escalation, limits logs, and supplies `/tmp` tmpfs. The image filesystem remains writable because Next.js may use cache.

The Makefile offers local build/run/log targets, multi-architecture buildx publication, semver release tags, image size, and optional Trivy scan. Registry publication and cleanup targets are operational capabilities, not automatically authorized steps. Review registry names, credentials, provenance labels, and release policy before use.

## 26. Deployment guidance

A safe deployment needs:

1. an HTTPS frontend origin;
2. a deliberate HTTPS `mdcApi.baseUrl` in public runtime configuration;
3. backend CORS and CSRF-origin settings that permit only intended origins;
4. a correctly registered public Keycloak client, redirect URIs, realm URL, and ownership;
5. a policy decision whether this environment is allowed to expose demo APIs;
6. no secrets in browser-delivered configuration or bundles;
7. separate backend secret management for Django, database, lifecycle, and semantic services;
8. lint/build/manual smoke validation against the intended environment.

Production MDC settings default demo, provider publication, validation, and catalogue synchronization flags off, while trusted lifecycle authentication/actor/concurrency requirements default on. A demonstration environment may deliberately differ, but it must not be mistaken for the production policy.

The repository proves the app can be built and packaged; it does not by itself prove an active production deployment of this frontend. Deployment ownership for the frontend host, Keycloak, backend origin, and demo enablement must be assigned before release.

## 27. Security model and limitations

| Boundary/risk | Current control | Limitation/next control |
|---|---|---|
| Browser configuration | Explicitly public; no secrets intended | Review built assets and runtime config on every release |
| Trusted lifecycle | No browser client/helpers | Implement only behind CMM/BFF with real identity and authorization |
| Demo roles | Route/menu/component presentation checks | Backend must enforce every sensitive operation |
| Demo endpoints | Separate namespace and server feature gate | Add appropriate backend auth if exposed beyond a controlled demo |
| Source history | Sanitized snapshot; credential-bearing GitLab objects excluded | Keep GitLab checkout isolated and scan every release sync |
| Secret scanning | Pattern/risk scans at milestones | Scans cannot prove absence of every secret; use prevention and review |
| Dependencies | Committed lockfile and accepted clean audit | Re-audit and patch under controlled dependency-update work |
| Network | Deployment guidance requires HTTPS/CORS | Current local defaults are intentionally HTTP/localhost |

Security headers reduce common browser risks but do not replace a content security policy, authorization, secure identity configuration, dependency maintenance, or infrastructure monitoring.

## 28. Git workflow for daily development

After integration acceptance, use personal GitHub as the working source for this sanitized frontend:

1. update the intended base with fast-forward-only Git operations;
2. create a focused development branch;
3. keep secrets and generated outputs outside Git;
4. make scoped application/documentation changes;
5. run relevant tests, lint, build, diff checks, and secret-risk checks;
6. inspect every changed path and the complete diff;
7. commit with a focused message and push only the intended GitHub branch;
8. obtain normal review before merging;
9. update provenance/manuals when behavior or contracts change.

Do not add the historical GitLab repository as a convenience remote to the normal `mdc_v1` working copy. Do not mix an official GitLab release with ordinary feature development.

## 29. GitHub-to-GitLab official release workflow

This procedure derives from `docs/Demo_Frontend/01_frontend_github_to_gitlab_release_mapping.md`. It requires separate approval and was not performed for this manual.

1. Select a reviewed GitHub source commit and record its full SHA.
2. Define the exact application paths intended for release. Exclude GitHub-only docs by default.
3. Obtain approval to prepare a GitLab release candidate.
4. Create a fresh temporary checkout of the official GitLab frontend repository; do not alter the normal `mdc_v1` remotes.
5. Verify expected GitLab base commit, clean status, branch, and official remote.
6. Create a release branch; never work directly on GitLab `main`.
7. Synchronize reviewed files by explicit path from the sanitized GitHub tree, preserving unrelated GitLab files.
8. Exclude `.env*`, local/editor files, dependencies, builds, caches, raw exports, and GitHub-only documentation unless explicitly approved.
9. Run a secret scan that reports categories/paths without printing values.
10. Install from the committed lockfile in the release checkout and run approved lint/build/test/browser gates.
11. Review status, changed-path inventory, full diff, whitespace, generated files, and configuration boundary.
12. Record GitHub source SHA, GitLab base, proposed release commit, validation, and mapping.
13. Obtain explicit approval for that concrete commit and push.
14. Push only the GitLab release branch and use normal GitLab merge review.
15. After approval/merge, record the merged GitLab SHA in GitHub release documentation.

Never force-push, rewrite or replace GitLab history, merge unrelated histories, or publish with subtree push.

## 30. Relationship to the MDC backend master manual

Read this document together with `docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md`.

| Question | Authoritative manual |
|---|---|
| Browser pages, role presentation, runtime browser config, frontend services and UI workflows | This frontend manual |
| Public/trusted API validation, database model, matching, RDF/Fuseki, outbox, backend deployment/security and AWS planning | Backend master manual |

When browser behavior and an old frontend report disagree, current frontend source wins. When API semantics and browser assumptions disagree, current backend source and backend manual win; the frontend should be corrected rather than redefining the API.

## 31. Future CMM integration

A future CMM integration should preserve MDC's controlled API while replacing demo ownership boundaries:

- CMM owns user registration, login journey, account recovery, and navigation.
- Marketplace identity maps authenticated people and organizations to provider and consumer principals.
- CMM forms load current filters dynamically from MDC.
- Consumer discovery can call the public search contract according to deployment policy.
- A CMM backend/BFF holds trusted lifecycle credentials, authorizes provider actions, supplies actor attribution, and manages ETags.
- Provider drafts/custom fields pass through governed validation and mapping before controlled publication.
- CMM owns quotation, saved searches, contact/transaction workflow, and commercial authorization.
- Backend/API authorization remains independent of browser visibility.
- Demo state, overlay matching, and demo admin mutation interfaces are retired or confined to non-production demonstrations.

This is a target architecture, not current functionality.

## 32. Known limitations and future work

- Real CMM integration is not implemented.
- Trusted lifecycle calls are intentionally absent from browser code.
- Production ownership of frontend hosting, HTTPS origin, CORS, and Keycloak configuration is unresolved in this repository.
- Client role guards do not secure backend endpoints.
- Demo persistence is a JSON file and demo overlay entries are not authoritative catalogue data.
- Production MDC commonly disables demo APIs, so provider/admin demonstrations need a dedicated environment.
- RDF regeneration and Fuseki reload demo actions are reserved and currently return 501.
- Result buttons do not implement quotation, contact, saving, or transactions.
- Strong automated frontend unit/integration/browser/accessibility tests are absent.
- Scoped frontend CI is absent.
- The accepted dependency audit is point-in-time evidence and requires periodic renewal.
- No GitLab release synchronization has been performed for this integrated snapshot.
- Legacy template workspace pages and styling remain and may need product-scope review.
- Browser result adapters retain historical compatibility, increasing maintenance surface.
- Automated mapping from flexible provider fields to controlled MDC semantics is not implemented.

## 33. Troubleshooting

| Symptom | Likely cause | Corrective action |
|---|---|---|
| Frontend cannot reach backend | Wrong origin, backend down, DNS/TLS, or mixed content | Check the public non-secret `baseUrl`, health route, HTTPS, and backend logs |
| Browser reports CORS error | Frontend origin not allowed | Add the exact HTTPS frontend origin to backend CORS policy through deployment change control |
| Login does nothing/fails | Keycloak disabled, invalid realm/client/redirect URI, or identity service unavailable | Check public Keycloak fields and client redirect/origin registration; never add a client secret |
| Logged in but no demo role | Token lacks recognized alias | Assign an approved realm/client role and log in again |
| Role page shows selection warning | No role selected or stale unavailable selection | Return to `/demo`, switch/clear the selected role, and retry |
| Demo call returns 404 | Demo API disabled by server policy | Use a deliberately demo-enabled environment; do not enable it casually in production |
| Filters show fallback warning | Filters unavailable or response not contract `1.0` | Inspect `GET /api/catalog/filters`; treat fallback as demo-only |
| Search returns 400 | Invalid family/type relationship, field scope/type, range, or contract | Compare payload preview with Section 15 and backend error details; do not send `material_grades` |
| Search returns no providers | No compatible active offering or restrictive requirements | Try fewer optional requirements and verify current catalogue/semantic runtime |
| Canonical results work but overlay warning appears | Demo state endpoint disabled/unavailable | Ignore for canonical truth or use a demo-enabled backend |
| Admin regenerate/reload reports failure | Current handlers are reserved | HTTP 501 is expected; do not claim the operation ran |
| Lint shows five known warnings | Accepted baseline warnings | Confirm count/files have not changed; new warnings still require review |
| Build fails after install | Wrong Node/npm, stale output, or environment restriction | Use compatible Node 20, clean ignored build output safely, run `npm ci`, then rebuild |
| Deployed browser calls localhost | Runtime config was not overridden | Deploy a public `config.js` with the intended HTTPS backend origin |
| Request times out after 10 seconds | API/network/semantic backend slow or unavailable | Check API and discovery backend health; client timeout is 10,000 ms |

Troubleshooting must not print authorization headers, full environments, database URLs, tokens, or secret-bearing configuration.

## 34. Glossary

| Term | Meaning |
|---|---|
| MaaSAI | Project context for Manufacturing-as-a-Service capabilities |
| MaaS | Manufacturing as a Service |
| MDC | MaaS Dynamic Catalogue |
| CMM | Cloud MaaS Marketplace; future external product context, not this frontend |
| Provider | Organization offering manufacturing capability |
| Consumer | User/system searching for suitable offerings |
| Offering | A provider's manufacturing service description |
| Service discovery | Matching a structured request against offerings |
| Controlled vocabulary | Approved category/family/type/material/process/certification values |
| Custom field | Flexible staging data not automatically promoted to controlled semantics |
| Demo overlay | Browser-generated, explicitly labelled matches from demo provider state |
| Keycloak | Identity provider/client technology used for browser login |
| ETag | Strong revision identifier used for safe updates |
| CORS | Browser cross-origin request policy enforced by server/browser |
| BFF | Backend for frontend; safe server-side integration layer |
| Fuseki | Apache Jena SPARQL/RDF service used by MDC's semantic layer |
| RDFLib | Local Python RDF implementation/fallback used by MDC |
| GitHub | Controlled development source for the sanitized snapshot |
| GitLab | Historical repository and official release destination |
| Sanitized snapshot | Reviewed content copy excluding unsafe history and sensitive/local artifacts |

## 35. Appendices

### Appendix A — Endpoint quick reference

| Class | Method | Path | Browser use |
|---|---|---|---|
| Public | GET | `/api/health` | Health/status |
| Public | GET | `/api/catalog/filters` | Search controls |
| Public | POST | `/api/service-discovery/search` | Consumer discovery |
| Demo | GET | `/api/demo/health` | Demo availability |
| Demo | GET | `/api/demo/service-discovery/backend-status` | Status |
| Demo | GET | `/api/demo/service-discovery/fuseki-smoke-test` | Admin smoke |
| Demo | POST | `/api/demo/service-discovery/regenerate-rdf` | Reserved; current 501 |
| Demo | POST | `/api/demo/service-discovery/reload-fuseki` | Reserved; current 501 |
| Demo | GET | `/api/demo/provider-publication/state` | Demo state/overlay |
| Demo | POST | `/api/demo/provider-publication/preview` | Provider preview |
| Demo | POST | `/api/demo/provider-publication/simulate-update` | Demo state save |
| Trusted | Multiple | `/api/provider-publication...`, `/api/providers/...`, `/api/offerings/...` | Intentionally not called by browser |

### Appendix B — Route/role quick reference

| Selected demo role | Dashboard | Provider | Consumer | Admin |
|---|---:|---:|---:|---:|
| Not authenticated | Public/login prompt | No | No | No |
| Provider | Yes | Yes | No | No |
| Consumer | Yes | No | Yes | No |
| Admin selecting Provider | Yes | Yes | No | No |
| Admin selecting Consumer | Yes | No | Yes | No |
| Admin selecting Admin | Yes | No | No | Yes |

### Appendix C — Important file map

| Concern | File(s) |
|---|---|
| Global composition/route guard | `src/pages/_app.js`, `src/config/routes.js` |
| Authentication | `src/layout/context/AuthContext.js`, `src/services/keycloak/keycloak.js` |
| Demo roles/menu | `src/components/mdc/demoAuth.js`, `DemoRoleGuard.js`, `src/layout/AppMenu.js` |
| Runtime API configuration | `public/config.js`, `src/config/runtimeConfig.js` |
| HTTP services | `src/services/mdc/*.js` |
| Consumer payload/results | `ConsumerSearchMockup.js`, `searchResultFormatters.js`, `ProviderResultAccordion.js` |
| Provider flow | `ProviderDemoPanel.js`, `providerPayloadBuilder.js` |
| Admin flow | `AdminAuditPanel.js` |
| Backend contract | `backend/apps/api/public_contract.py`, `service_discovery_search_serializers.py` |
| Demo backend | `backend/apps/demo/` |
| Trusted security | `backend/apps/api/lifecycle_security.py` |

### Appendix D — Milestone timeline

| Evidence | Identifier |
|---|---|
| Historical template source | `832ad57265bce0889ebea58bc69c031c3b394ee7` |
| Preservation/sanitized staging | 2026-09-09; 134 app files and 30 reports |
| Sanitized GitHub import | `e411e7300cfbe2f9f3f9fe245027f2c0c341cd38` |
| Current API/config cleanup baseline | `b207022363163a026a1d77e6485fd151e81aa750` |

### Appendix E — Safe deployment checklist

- [ ] Reviewed source commit and clean build
- [ ] HTTPS frontend and API origins
- [ ] Correct public runtime config with no secrets
- [ ] Exact backend CORS/CSRF origins
- [ ] Keycloak public client and redirect ownership confirmed
- [ ] Demo API policy explicitly decided
- [ ] Backend secrets remain server-side
- [ ] Lint, build, manual role journeys, public API smoke passed
- [ ] Built assets and changed files secret-risk scanned
- [ ] Rollback owner and previous deploy identified

### Appendix F — Future GitLab release checklist

- [ ] Separate approval obtained
- [ ] GitHub source SHA and exact file scope recorded
- [ ] Fresh isolated GitLab checkout verified
- [ ] GitLab release branch created from approved base
- [ ] Reviewed file synchronization only; unrelated files preserved
- [ ] Sensitive/local/generated/GitHub-only paths excluded
- [ ] Secret-risk, diff, lockfile, lint/build/test gates passed
- [ ] Proposed GitLab commit reviewed and explicitly approved
- [ ] Release branch pushed without force; normal merge review used
- [ ] Final GitLab SHA recorded back in release documentation

### Appendix G — Maintenance rules

1. Verify current source before updating behavioral claims.
2. Keep public, demo, and trusted lifecycle interfaces visibly separate.
3. Do not introduce `/api/v1` examples unless the backend truly adds that route.
4. Never instruct a browser to hold trusted credentials.
5. Label historical/internal shapes and demo data explicitly.
6. Re-run documentation link, whitespace, secret-risk, lint/build, and scope gates after material changes.
7. Update this manual alongside accepted frontend contract or workflow changes.
