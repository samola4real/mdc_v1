# MaaSAI MaaS Dynamic Catalogue (MDC)

Current implementation repository for the **MaaSAI MaaS Dynamic Catalogue (MDC)** backend and its **MDC Demo Frontend**.

The repository now contains the integrated Phase 3 backend, the sanitized and aligned demonstration frontend, current implementation reports, API/testing evidence, and operating manuals.

> **Current-source rule:** use the code on `main` and the current master manuals as the source of truth. Older Week 1, Phase 1, or milestone reports are historical evidence only and may describe superseded routes, schemas, or deployment assumptions.

> **Frontend scope:** the MDC Demo Frontend is an illustrative interface for MaaSAI pilot demonstrations. It is **not** the Cloud MaaS Marketplace (CMM) and does not replace the Marketplace frontend. It demonstrates how provider and consumer interactions with MDC could work before integration with the real MaaSAI Marketplace components.

---

## 1. Current status

The current integrated baseline includes:

- Django/DRF MDC backend;
- PostgreSQL-backed provider/offering lifecycle;
- transactional catalogue synchronization outbox;
- RDF generation and Apache Jena Fuseki semantic retrieval;
- deterministic public service discovery;
- trusted provider lifecycle APIs with bearer authentication, actor attribution, and ETag concurrency controls;
- Vercel-hosted backend pilot;
- managed PostgreSQL pilot database;
- Next.js 14 MDC Demo Frontend;
- Keycloak-based browser login and demo-role selection;
- Provider, Consumer, and Admin demonstration flows;
- comprehensive backend and frontend operating manuals.

The maintained development repository for this integrated version is the personal GitHub repository:

```text
samola4real/mdc_v1
```

The normal working branch is:

```text
main
```

No MaaSAI GitLab synchronization is part of the current workflow.

---

## 2. Repository structure

```text
mdc-catalog/
├── backend/                  Django/DRF MDC backend
│   ├── apps/
│   │   ├── api/
│   │   ├── catalog/
│   │   ├── demo/
│   │   ├── ontology/
│   │   ├── providers/
│   │   └── search/
│   ├── config/
│   ├── tests/
│   └── manage.py
│
├── demo-frontend/            Next.js MDC Demo Frontend
│   ├── public/
│   ├── src/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── package.json
│   └── README.md
│
├── data/                     Curated/generated/demo data
├── ontologies/               Ontology assets
├── scripts/                  Validation and operational scripts
├── docs/                     Implementation reports and manuals
├── requirements/             Python dependency definitions
├── requirements.txt
├── pyproject.toml
└── .env.example
```

For normal development, backend code lives under `backend/` and frontend code lives under `demo-frontend/`.

---

## 3. Architecture overview

```text
Provider / Consumer / Demo Admin
             |
             v
      MDC Demo Frontend
         Next.js 14
             |
             | HTTP / JSON
             v
        Django MDC API
             |
     +-------+---------+
     |                 |
     v                 v
PostgreSQL        RDF / Fuseki
source of truth   semantic layer
     |
     v
Transactional catalogue-sync outbox
```

### Backend authority

PostgreSQL is the operational source of truth for current provider and offering lifecycle state. RDF/Fuseki is a derived semantic representation used for discovery. Catalogue synchronization is performed through trusted operator workflows rather than a public synchronization endpoint.

### Frontend authority

The browser frontend owns only presentation, browser-side form handling, demo-role navigation, and calls to permitted MDC interfaces. It does not own trusted provider lifecycle credentials or backend authorization.

---

## 4. Canonical public API

The current public contract is **`1.0`** and uses unversioned `/api/` routes.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | MDC service health |
| `GET` | `/api/catalog/filters` | Controlled search vocabulary |
| `POST` | `/api/service-discovery/search` | Provider/offering discovery |

There is **no current `/api/v1/...` public route**.

A current discovery request uses controlled selection fields such as:

```json
{
  "request_id": "req-demo-001",
  "consumer_id": "consumer-demo",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear",
  "requirements": {
    "part_family_specifications": {
      "module": { "exact": 2 },
      "outside_diameter_mm": { "max": 100 }
    },
    "part_type_specifications": {
      "face_width_mm": { "exact": 25 }
    },
    "generic_requirements": {
      "materials": ["alloyed_carburizing_steel"],
      "processes": ["hobbing"],
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

For complete payload and response examples, use the backend and frontend master manuals listed below.

---

## 5. Trusted provider lifecycle API

Provider lifecycle operations are a separate trusted server-side integration surface.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/provider-publication/validation` | Validate provider publication |
| `POST` | `/api/provider-publication` | Register/publish provider |
| `GET`, `PATCH` | `/api/providers/{provider_id}` | Read/update provider |
| `GET`, `POST` | `/api/providers/{provider_id}/offerings` | List/create offerings |
| `GET`, `PATCH` | `/api/offerings/{offering_id}` | Read/update offering |

The trusted lifecycle can require:

- `Authorization: Bearer <service token>`;
- `X-MDC-Actor-Id` for mutating operations;
- strong `ETag` values on reads;
- `If-Match` for safe updates.

**Never place the trusted lifecycle service token in browser code, `public/config.js`, `NEXT_PUBLIC_*`, local storage, session storage, or committed files.** A future CMM integration should hold trusted credentials behind a Marketplace backend or BFF.

---

## 6. Demo-only API

The frontend Provider and Admin demonstrations use a separate `/api/demo/...` namespace.

Examples include:

```text
GET  /api/demo/health
GET  /api/demo/provider-publication/state
POST /api/demo/provider-publication/preview
POST /api/demo/provider-publication/simulate-update
GET  /api/demo/service-discovery/backend-status
GET  /api/demo/service-discovery/fuseki-smoke-test
POST /api/demo/service-discovery/regenerate-rdf
POST /api/demo/service-discovery/reload-fuseki
```

These endpoints are demonstration interfaces, not the trusted production lifecycle.

The current backend intentionally treats several technical demo actions as reserved/not implemented. Production deployments normally keep the demo API disabled unless a specific demo environment is deliberately configured.

---

## 7. Quick start — backend

### Prerequisites

- Python 3.12
- Git
- PowerShell, Command Prompt, Bash, or equivalent shell

From `mdc-catalog/`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python backend\manage.py migrate
python backend\manage.py runserver 8000
```

With `DATABASE_URL` empty, local development uses SQLite. Never commit `.env`.

Verify the backend:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
Invoke-RestMethod http://localhost:8000/api/catalog/filters
```

Expected base URL:

```text
http://localhost:8000
```

For full backend setup, lifecycle testing, PostgreSQL, RDF/Fuseki, synchronization, and deployment procedures, use the backend master manual.

---

## 8. Quick start — demo frontend

### Prerequisites

- Node.js 20
- npm
- running MDC backend or an approved deployed MDC API
- valid Keycloak access for authenticated demo routes

From `mdc-catalog/demo-frontend/`:

```powershell
npm ci
npm run dev
```

Open:

```text
http://localhost:3000/demo
```

The browser runtime configuration is in:

```text
demo-frontend/public/config.js
```

Its local MDC API default is:

```text
http://localhost:8000
```

`config.js` is delivered to the browser and therefore must contain **public configuration only**.

Useful validation commands:

```powershell
npm run lint
npm run build
npm run start
```

The full frontend quick-start, Provider walkthrough, Consumer walkthrough, Admin walkthrough, field mappings, Docker procedure, and troubleshooting guide are in the frontend master manual.

---

## 9. Demo frontend roles and routes

The main demo routes are:

| Route | Purpose | Access |
|---|---|---|
| `/demo` | Demo console and role selection | Public shell |
| `/demo/provider` | Provider demonstration | Authenticated Provider/Admin role |
| `/demo/consumer-search` | Consumer discovery demonstration | Authenticated Consumer/Admin role |
| `/demo/admin-audit` | Demo administration/audit | Authenticated Admin role |

Recognized role aliases include:

```text
Provider: provider, mdc_provider, maas_provider
Consumer: consumer, mdc_consumer, maas_consumer
Admin:    admin, mdc_admin, maas_admin
```

Browser route and role guards are presentation controls only. Backend authorization remains authoritative.

---

## 10. Main demo workflows

### Provider

The Provider experience demonstrates two flows:

1. **Register New Provider** — capture provider/offering facts in a flexible staging structure, preview them, and save them to demo persistence.
2. **Update Existing Provider** — select an existing demo offering, explicitly map it to a controlled Gear/Shaft/Metal Part template when required, edit controlled capabilities, preview, and save the demo update.

Provider demo save does **not** publish directly to the trusted PostgreSQL lifecycle and does not automatically synchronize Fuseki.

### Consumer

The Consumer experience:

1. loads controlled values from `GET /api/catalog/filters`;
2. builds a canonical discovery payload;
3. submits `POST /api/service-discovery/search`;
4. displays provider candidates and matched, unmatched, and unknown capabilities;
5. may append clearly labelled demo-provider overlay entries when demo state is available.

### Admin

The Admin experience shows health, filters, demo provider state, and demo-reported backend information. Static demo metadata must not be interpreted as proof that a specific Fuseki runtime is live. Reserved technical actions currently return not-implemented responses and are labelled accordingly.

---

## 11. Controlled manufacturing scope

The current public search registry includes three main service-category/part-family pairs:

```text
precision_gears       -> gear
precision_shafts      -> shaft
precision_metal_parts -> metal_part
```

Current part types include:

**Gear:** spur, helical, bevel, worm, crown.

**Shaft:** plain, stepped, splined, worm, hollow.

**Metal part:** block, plate, bracket, bushing, roller, collar.

Current public filters also advertise controlled materials, processes, and certifications. Consumer search should load these dynamically from `/api/catalog/filters` rather than assuming a permanently fixed list.

`material_grades` are provider evidence and are not a current canonical consumer search criterion.

---

## 12. Testing

### Backend

The repository contains focused and full backend tests under:

```text
backend/tests/
```

Use the backend master manual for the accepted milestone test matrix and current commands.

### Frontend

The accepted frontend baseline has been validated with:

```text
npm ci
npm run lint
npm run build
```

The frontend currently does not have a full automated unit/integration/browser test suite. Manual role and API checks are documented in the frontend master manual.

---

## 13. Deployment

### Backend

The accepted pilot backend is hosted on Vercel:

```text
https://maasai-mdc-v1.vercel.app
```

The canonical public endpoints are available below that origin. Deployment-specific feature flags and secrets remain server-side.

The current repository also contains AWS-readiness planning, but AWS migration has not been completed.

### Frontend

The repository contains a production-capable Next.js build plus Docker assets, but the repository itself does not prove that a public production frontend deployment is currently active.

A deployed frontend requires:

- HTTPS frontend origin;
- HTTPS MDC backend origin;
- correct CORS/CSRF policy;
- valid public Keycloak client and redirect URIs;
- deliberate demo-API policy;
- no browser-delivered secrets.

---

## 14. Docker frontend

From `mdc-catalog/demo-frontend/`:

```powershell
docker compose up --build
```

Then open:

```text
http://localhost:3000
```

Useful commands:

```powershell
docker compose logs -f frontend
docker compose down
```

The compose configuration mounts `public/config.js` read-only so public runtime URLs can be changed without rebuilding the image.

---

## 15. Security rules

Do not commit or expose:

- `MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN`;
- `DJANGO_SECRET_KEY`;
- `DATABASE_URL` credentials;
- Fuseki passwords;
- private keys;
- real bearer tokens;
- secret-bearing identity exports;
- credentials in browser runtime configuration.

Do not:

- reintroduce `/api/v1/...` unless the backend contract genuinely changes;
- expose catalogue synchronization as a public browser action;
- place trusted lifecycle credentials in the frontend;
- treat demo role selection as backend authorization;
- treat demo JSON state as authoritative provider lifecycle data.

---

## 16. Authoritative documentation

### Backend master manual

```text
docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md
```

Use it for:

- backend architecture;
- PostgreSQL persistence;
- provider lifecycle;
- API contract details;
- ETags and concurrency;
- matching semantics;
- RDF/Fuseki;
- catalogue synchronization;
- Postman testing;
- Vercel/Neon deployment;
- Phase 3 validation;
- AWS readiness.

### Frontend master manual

```text
docs/Demo_Frontend/MDC_Demo_Frontend_Comprehensive_Implementation_Report_and_User_Manual.md
```

Use it for:

- first-time setup;
- frontend architecture;
- Keycloak/browser configuration;
- Provider walkthrough;
- Consumer walkthrough;
- Admin walkthrough;
- UI-field/API mappings;
- local and Docker execution;
- frontend validation;
- security boundaries;
- troubleshooting;
- future CMM integration.

Historical reports under `docs/Phase_2/`, `docs/Phase_3/`, and `docs/Demo_Frontend/Implementation_History/` provide traceability but do not override the current manuals or code.

---

## 17. Development workflow

For normal work in the personal repository:

```powershell
git switch main
git pull --ff-only origin main
git status
```

Create a focused branch for substantive changes, make scoped edits, run relevant tests/builds, inspect the diff, and merge back through normal review.

The maintained remote is:

```text
origin -> https://github.com/samola4real/mdc_v1.git
```

Avoid adding unrelated remotes or reviving completed milestone branches unless there is a specific recovery need.

---

## 18. Known limitations

The current pilot does not provide:

- the real Cloud MaaS Marketplace frontend;
- end-user Marketplace identity/authorization integration;
- browser-based trusted lifecycle publication;
- automatic mapping of arbitrary provider text into controlled MDC semantics;
- production quotation/pricing workflows;
- live capacity scheduling;
- manufacturing routing generation;
- CAD/2D/3D geometry analysis;
- fully automated frontend test coverage;
- permanent production Fuseki/AWS infrastructure.

These are future-development areas rather than current capabilities.

---

## 19. Project principle

MDC should remain provider-neutral and evidence-driven:

```text
Provider facts
    -> validate and normalize
    -> persist authoritative lifecycle state
    -> derive semantic representation
    -> retrieve candidate offerings
    -> apply one deterministic matcher
    -> return explained public results
```

Tasowheel is the primary pilot example, but provider-specific facts belong in data/evidence rather than hard-coded provider branches in application logic.

---

## 20. Where to begin

If you are new to the project:

1. Read this README.
2. For backend/API work, open `docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md`.
3. For frontend/demo work, open `docs/Demo_Frontend/MDC_Demo_Frontend_Comprehensive_Implementation_Report_and_User_Manual.md`.
4. Run the local backend and verify `/api/health`.
5. Run the frontend and open `/demo`.
6. Use the relevant Provider, Consumer, or Admin walkthrough before making changes.

That gives the shortest path from a fresh checkout to understanding and operating the current MDC pilot.