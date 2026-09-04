# MDC M6.1 API Contract Rectification Report

**Date:** 2026-09-04  
**Project:** MaaSAI MaaS Dynamic Catalogue (MDC)  
**Milestone:** M6.1 — API Contract Rectification  
**Status:** Completed - implementation, local verification, Vercel Preview verification, and Vercel Production verification passed

---

## 1. M6.1 Status

M6.1 implementation is complete in the GitHub repository and the requested local verification has been run successfully by the user.

The remaining Vercel deployment gate was completed on 2026-09-04.

M6.1 status: completed

Current state:

```text
Implementation            PASS
Focused local API tests   PASS
Full local test suite     PASS
Vercel Preview verify     PASS
Vercel Production verify  PASS
```

The exact numeric local test counts were not captured in this report at the time of writing; the user confirmed that all requested local tests passed.

---

## 2. Final Route Matrix

| Method | Route | Classification | External? | Implementation backing |
|---|---|---|---|---|
| GET | `/api/health` | Stable canonical | Yes | Public GET view + public contract adapter |
| GET | `/api/catalog/filters` | Stable canonical | Yes | Harmonized service-discovery registry + public contract adapter |
| POST | `/api/service-discovery/search` | Stable canonical | Yes | H1-H9 runtime service discovery + public response adapter |
| POST | `/api/catalog/search` | Legacy retained | No | Legacy catalogue/search implementation |
| GET | `/api/providers/{provider_id}` | Legacy/internal | No | Legacy provider seed schema |
| GET | `/api/offerings/{offering_id}` | Legacy/internal | No | Legacy offering/provider seed schema |
| POST | `/api/provider-publication` | Legacy/deferred write | No | Existing file-backed publication flow; disabled in production |
| `/api/demo/*` | Demo/internal | No | Demo app; disabled in production by default |
| `/api/v1/*` | Removed | No | No URL-versioned public route family |

Important clarification:

```text
GET /api/providers
```

is not currently registered as a list endpoint. The existing legacy route is the provider-detail route:

```text
GET /api/providers/{provider_id}
```

The project will not introduce `/api/v1/`, `/api/v2/`, etc. as the future public versioning strategy.

---

## 3. Contract-Version Behavior

The public API contract version is:

```text
1.0
```

The API uses stable URLs plus explicit contract metadata.

### Search request behavior

For:

```text
POST /api/service-discovery/search
```

`contract_version` is optional.

If omitted:

```text
default -> 1.0
```

If explicitly supplied as:

```json
{
  "contract_version": "1.0"
}
```

it is accepted.

If an unsupported explicit value is supplied, for example:

```json
{
  "contract_version": "2.0"
}
```

MDC returns HTTP `400` with public error code:

```text
unsupported_contract_version
```

The URL itself does not change when the contract evolves.

### Response behavior

The public health, catalogue-filter, service-discovery success, and public error responses expose:

```json
"contract_version": "1.0"
```

---

## 4. Final External Catalogue Filter Contract

Canonical endpoint:

```text
GET /api/catalog/filters
```

The external response exposes only the harmonized Marketplace-facing keys:

```text
contract_version
service_categories
part_families
part_types
materials
processes
certifications
```

`service_categories` preserve their `part_family` relationship and `part_families` preserve their `service_category` relationship.

`part_types` are grouped by part family so Marketplace can render dependent filters/forms coherently.

Short representative shape:

```json
{
  "contract_version": "1.0",
  "service_categories": [
    {
      "value": "precision_gears",
      "label": "Precision gears",
      "part_family": "gear"
    }
  ],
  "part_families": [
    {
      "value": "gear",
      "label": "Gear",
      "service_category": "precision_gears"
    }
  ],
  "part_types": {
    "gear": [
      {
        "value": "spur_gear",
        "label": "Spur gear"
      }
    ]
  },
  "materials": [],
  "processes": [],
  "certifications": []
}
```

The actual controlled values are populated from the current registry/vocabularies rather than hard-coded in the public response.

---

## 5. Final External Service-Discovery Contract

Canonical endpoint:

```text
POST /api/service-discovery/search
```

### Request contract

Required top-level business fields remain:

```text
request_id
consumer_id
service_category
part_family
part_type
```

Optional fields remain:

```text
requirements
match_policy
contract_version
```

`contract_version` is handled at the API boundary and removed before the existing H1-H9 request serializer/normalizer receives the business payload.

Short representative request:

```json
{
  "contract_version": "1.0",
  "request_id": "req_001",
  "consumer_id": "consumer_001",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear",
  "requirements": {},
  "match_policy": {
    "optional_match_mode": "any",
    "unknown_policy": "keep_as_unknown",
    "minimum_score": null
  }
}
```

### Public success response — exact top-level keys

```text
contract_version
request_id
service_category
part_family
part_type
result_count
results
```

### Public result-level keys

Each public result exposes:

```text
provider_id
provider_name
offering_id
offering_name
service_category
part_family
match
matched_capabilities
unmatched_capabilities
unknown_capabilities
```

`match` exposes only:

```text
status
score
```

### Selection metadata vs capability matching

H1-H9 continues to evaluate:

```text
service_category
part_family
part_type
```

internally as selection checks.

These are not repeated inside the external `matched_capabilities`, `unmatched_capabilities`, or `unknown_capabilities` arrays because they classify the selected service/part rather than manufacturing capability requirements.

Capability arrays are reserved for requirement/capability comparisons such as dimensions, materials, processes, quality, batch size, delivery, etc.

### Internal fields deliberately excluded from the public response

Examples include:

```text
consumer_id
query_interpretation
warnings
status.search_engine
status.message
hard_filters_passed
optional_policy_satisfied
raw evidence
source_type
confidence
source_note
runtime backend/fallback diagnostics
```

These remain available in the internal H1-H9 result where required, but are not exposed to Marketplace through the public response adapter.

Short representative response:

```json
{
  "contract_version": "1.0",
  "request_id": "req_001",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear",
  "result_count": 1,
  "results": [
    {
      "provider_id": "tasowheel",
      "provider_name": "Tasowheel Oy",
      "offering_id": "tasowheel_gears_shafts_precision",
      "offering_name": "Precision gears",
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

The sample above illustrates the public shape only; exact result values depend on the submitted request and runtime catalogue data.

---

## 6. H1-H9 Preservation

M6.1 did not replace the harmonized service-discovery architecture.

The canonical endpoint still flows through the existing request normalization and runtime search stack.

The preserved architecture remains:

```text
POST /api/service-discovery/search
        ↓
public request boundary
        ↓
existing harmonized request serializer/normalizer
        ↓
H1-H9 service-discovery runtime
        ↓
Fuseki, if configured
        ↓
RDFLib over generated RDF
        ↓
Harmonized YAML fallback
        ↓
rich internal H1-H9 result
        ↓
public response adapter
        ↓
Marketplace-safe response
```

The M6.1 changes were intentionally concentrated in the API boundary, routing metadata, and API tests.

The user confirmed that the local focused and full test runs passed after rectification.

---

## 7. Legacy / Internal Handling

### Legacy catalogue search

```text
POST /api/catalog/search
```

Retained only because it exists in earlier implementation/deliverable history.

It is not the current harmonized search and must not be used for new Marketplace integration.

### Provider detail

```text
GET /api/providers/{provider_id}
```

Remains a legacy/internal route backed by the legacy provider seed schema.

Do not advertise externally yet.

### Offering detail

```text
GET /api/offerings/{offering_id}
```

Remains legacy/internal for the same reason.

### Provider publication validation

No new public validation route was added in M6.1.

Publication validation remains internal/non-public for now.

### Provider publication write

```text
POST /api/provider-publication
```

remains available only as the existing legacy workflow and remains disabled by default in production.

Expected production behavior remains:

```text
403 provider_publication_disabled
```

### Demo API

```text
/api/demo/*
```

remains separate from the public contract and disabled by default in production.

### URL-versioned routes

The previously introduced:

```text
/api/v1/health
/api/v1/catalog/filters
/api/v1/service-discovery/search
```

have been removed and are expected to return `404`.

`backend/apps/api/urls_v1.py` has been removed.

---

## 8. PostgreSQL Persistence Architecture Proposal

No database implementation was performed in M6.1.

Recommended operational database:

```text
PostgreSQL
```

Preferred first Vercel-friendly candidate:

```text
Neon PostgreSQL
```

### Why PostgreSQL

The future MDC operational model is relational and needs durable provider/offering state, publication history, ownership, status, timestamps, and controlled relationships.

PostgreSQL also provides `JSONB`, which is suitable for provider-entered staging/custom fields before they are normalized into controlled MDC values.

### Minimum conceptual model

A later persistence milestone should consider at least:

```text
Provider
Offering
ProviderPublication / PublicationVersion
PublicationStatus / history
created_at
updated_at
submitted_by / owner placeholders
flexible staging/custom provider fields (JSONB)
normalized controlled capability relationships
```

### Intended publication flow

```text
Marketplace/provider input
        ↓
validation + normalization
        ↓
PostgreSQL transaction / system of record
        ↓
RDF generation/update
        ↓
Fuseki semantic catalogue
```

### Synchronization principle

PostgreSQL should become the durable operational source of truth.

RDF/Fuseki updates should be explicit and observable rather than silently assumed successful. A future implementation should consider an update/publication job status or outbox-style synchronization mechanism so PostgreSQL and Fuseki cannot silently diverge.

---

## 9. Files Changed

| Path | Change | Reason |
|---|---|---|
| `backend/apps/api/public_contract.py` | Added | Stable public contract versioning, filter shaping, response shaping, error shaping |
| `backend/apps/api/views/get_views.py` | Added | Preserve GET-view organization convention and route public health/filter responses through public adapter |
| `backend/apps/api/views/post_views.py` | Updated | Add contract-version handling and public service-discovery response/error shaping |
| `backend/apps/api/views/__init__.py` | Updated | Route current public GET/POST functions to the organized view modules while retaining legacy imports |
| `backend/config/urls.py` | Updated | Remove `/api/v1/` URL include |
| `backend/apps/api/urls_v1.py` | Removed | URL-versioned public API strategy was superseded |
| `backend/apps/ontology/service_discovery_registry.py` | Updated | Registry note now identifies `/api/service-discovery/search` as the active harmonized route |
| `backend/tests/test_api_foundation.py` | Added/renamed | Test stable unversioned API foundation |
| `backend/tests/test_api_v1.py` | Removed | Obsolete v1-named foundation tests |
| `backend/tests/test_public_api_contract.py` | Updated | Enforce stable external contract and `/api/v1/* -> 404` |
| `backend/tests/test_service_discovery_search_endpoint.py` | Updated | Align endpoint tests with public response shaping |
| `backend/tests/test_service_discovery_registry.py` | Updated | Align registry metadata test with stable route |
| `backend/tests/test_production_route_safety.py` | Updated | Verify stable production routes, v1 removal, demo/publication safety |
| `docs/Phase_2/08_mdc_v1_api_persistence_rectification_decisions.md` | Updated | Finalize no-URL-versioning decision |
| `docs/prompts/06_mdc_v1_api_contract_rectification_codex_prompt.md` | Updated | Correct stored milestone instructions to match final decision |

---

## 10. Local Verification

The requested local verification sequence was:

```powershell
python manage.py check

python manage.py test `
  tests.test_api_foundation `
  tests.test_public_api_contract `
  tests.test_service_discovery_search_endpoint `
  tests.test_service_discovery_registry `
  tests.test_production_route_safety -v 2

python manage.py test -v 2
```

The user confirmed that all requested local tests passed.

Result:

```text
Focused M6.1/API verification: PASS
Full local suite:              PASS
```

Exact numeric test counts were not supplied in the conversation and are therefore not invented in this report.

Production configuration safety tests in the repository explicitly verify:

```text
/api/health                       available
/api/catalog/filters              available
/api/service-discovery/search     available
/api/v1/health                    404
/api/v1/catalog/filters           404
/api/v1/service-discovery/search  404
/api/demo/*                       unavailable by default
/api/provider-publication         403 when publication disabled
```

---

## 11. Vercel Project And Environment Verification

CLI authentication:

```text
npx vercel@latest whoami -> samola4real-6623
```

Local project link:

```text
Project name: maasai-mdc-v1
Project ID:   prj_DekMQdOYuuH0A5yNsCkFmOC4uD9j
Scope/team:   mdc19
```

Environment variable name/scope inspection was performed with:

```text
npx vercel@latest env ls
```

Required variables were present without printing secret values:

| Variable | Preview | Production |
|---|---:|---:|
| `DJANGO_SETTINGS_MODULE` | Present | Present |
| `DJANGO_SECRET_KEY` | Present | Present |
| `DJANGO_ALLOWED_HOSTS` | Present | Present |
| `MDC_DEMO_API_ENABLED` | Present | Present |
| `MDC_PROVIDER_PUBLICATION_ENABLED` | Present | Present |
| `FUSEKI_TIMEOUT_SECONDS` | Present | Present |

Optional variables intentionally remained unset/not required for this gate:

```text
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT
CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS
```

Production safety flags remained configured as deployment-time environment variables and were verified by endpoint behavior:

```text
MDC_DEMO_API_ENABLED=False
MDC_PROVIDER_PUBLICATION_ENABLED=False
```

---

## 12. Vercel Preview Verification

Preview deployment:

```text
URL:        https://maasai-mdc-v1-8stkezur1-mdc19.vercel.app
Deployment: dpl_EECkvSApRDViBisrNfbj1PFvRhiv
Inspector:  https://vercel.com/mdc19/maasai-mdc-v1/EECkvSApRDViBisrNfbj1PFvRhiv
Status:     READY
```

The Preview deployment is protected by Vercel authentication, so direct unauthenticated HTTP smoke requests returned `401`. API behavior was verified with authenticated `vercel curl`, the verification method recommended by the Vercel CLI for protected deployments.

Preview checks:

| Method | Endpoint | Result |
|---|---|---|
| GET | `/api/health` | PASS - HTTP 200, `contract_version=1.0`, `status=ok` |
| GET | `/api/catalog/filters` | PASS - HTTP 200, `contract_version=1.0`, exposed `service_categories`, `part_families`, `part_types`, `materials`, `processes`, `certifications` |
| POST | `/api/service-discovery/search` | PASS - HTTP 200, `contract_version=1.0`, `result_count=2`, first result `tasowheel/tasowheel_precision_gears`; public response shape only |
| GET | `/api/v1/health` | PASS - HTTP 404 |
| GET | `/api/v1/catalog/filters` | PASS - HTTP 404 |
| POST | `/api/v1/service-discovery/search` | PASS - HTTP 404 |
| GET | `/api/demo/health` | PASS - HTTP 404 |
| POST | `/api/provider-publication` | PASS - HTTP 403, `provider_publication_disabled` |

---

## 13. Vercel Production Verification

Production base URL remains:

```text
https://maasai-mdc-v1.vercel.app
```

Production deployment:

```text
URL:        https://maasai-mdc-v1-5tdtm4sek-mdc19.vercel.app
Alias:      https://maasai-mdc-v1.vercel.app
Deployment: dpl_EgaqDzXXfddZ92gaRAr9E9rZGwyN
Inspector:  https://vercel.com/mdc19/maasai-mdc-v1/EgaqDzXXfddZ92gaRAr9E9rZGwyN
Status:     READY
Target:     production
```

Production smoke checks against the canonical base URL:

| Method | Endpoint | Result |
|---|---|---|
| GET | `/api/health` | PASS - HTTP 200, `contract_version=1.0`, `status=ok` |
| GET | `/api/catalog/filters` | PASS - HTTP 200, `contract_version=1.0`, exposed `service_categories`, `part_families`, `part_types`, `materials`, `processes`, `certifications` |
| POST | `/api/service-discovery/search` | PASS - HTTP 200, `contract_version=1.0`, `result_count=2`, first result `tasowheel/tasowheel_precision_gears` |
| GET | `/api/v1/health` | PASS - HTTP 404 |
| GET | `/api/v1/catalog/filters` | PASS - HTTP 404 |
| POST | `/api/v1/service-discovery/search` | PASS - HTTP 404 |
| GET | `/api/demo/health` | PASS - HTTP 404 |
| POST | `/api/provider-publication` | PASS - HTTP 403, `provider_publication_disabled` |

Runtime log inspection:

```text
npx vercel@latest logs https://maasai-mdc-v1.vercel.app
```

The log inspection returned eight recent smoke-test entries at info level only. No error-level runtime failures were observed. The expected safety checks logged `404` for removed/demo routes and `403` for disabled provider publication.

Search backend/fallback behavior:

```text
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT was not configured for this gate.
The runtime first attempts Fuseki, then falls back to local RDFLib plus H5 matching, then YAML if needed.
The verified 200 search response returned two public-shaped results while omitting internal backend/fallback diagnostics by design.
```

---

## 14. Git / Implementation And Deployment Commits

M6.1 was implemented directly through GitHub file operations, therefore the work appears as several small commits rather than one monolithic commit.

Significant M6.1 commits include:

```text
b5976d9  feat: add MDC stable public API contract adapter
ef4f369  feat: add stable public GET views
b4d2abb  refactor: route public GET APIs through stable views
172eba6  feat: rectify stable service-discovery contract
68bf639  fix: remove URL-versioned API routes
ecf8971  fix: remove obsolete v1 URLconf
b25759b  test: enforce stable unversioned public routes
091ded6  test: verify unversioned production API routes
0be73ec  docs: finalize unversioned MDC API decision
09576a5  docs: correct M6.1 prompt to unversioned API strategy
51f836d  fix: align service-discovery registry with stable API route
6b082f9  test: align registry metadata with stable API route
103b1a8  fix: preserve harmonized filter relationships in public contract
34acd47  fix: avoid exposing runtime backend details in public errors
44c2a86  test: tighten public filter and route contract
df321ff  fix: keep selection metadata out of capability lists
```

Current synchronized source head used for Preview and Production deployment:

```text
5e5e1e8cf54d433c5a7b26283a2c09e859373c23
```

Additional synchronization/deployment-preparation commits now included:

```text
05a6f82 chore: track MDC documentation in git
5e5e1e8 docs: authorize Codex to reconcile known gitignore blocker
```

Deployment IDs:

```text
Preview:    dpl_EECkvSApRDViBisrNfbj1PFvRhiv
Production: dpl_EgaqDzXXfddZ92gaRAr9E9rZGwyN
```

This report completion is committed separately after deployment verification.

---

## 15. Partner-Document Readiness

The API design, local implementation, Preview deployment, and Production deployment are now coherent and externally verified.

Current status:

```text
READY_TO_UPDATE_PARTNER_API_DOCUMENT
```

Do not start M7 partner integration yet.

READY_TO_UPDATE_PARTNER_API_DOCUMENT
