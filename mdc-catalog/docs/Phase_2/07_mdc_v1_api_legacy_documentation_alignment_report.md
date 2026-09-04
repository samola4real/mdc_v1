# MDC API Alignment Report — Deployed v1 vs Legacy vs Marketplace Documentation

**Date:** 2026-09-04  
**MDC production base URL:** `https://maasai-mdc-v1.vercel.app`  
**Purpose:** Reconcile the deployed MDC API with the current MaaSAI Marketplace API documentation before partner handoff.

---

## 1. Executive Summary

The deployed MDC currently has **three canonical v1 partner APIs**:

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

These are the only endpoints intentionally promoted to the `/api/v1/` public contract during API stabilization.

The older `/api/...` routes were **not automatically converted to v1**. Some remain as compatibility aliases to the current implementation, while others remain isolated legacy APIs.

The Marketplace API PDF currently documents additional v1 endpoints that are **not present in the deployed v1 route table**, including:

```text
GET  /api/v1/providers
GET  /api/v1/providers/{provider_id}
POST /api/v1/provider-publication/validation
POST /api/v1/provider-publication/publish
```

Therefore, the current PDF should **not yet be given to partners as the final deployed API specification**.

---

# 2. Why `/api/v1/` Exists

`v1` is an **API version**, not a separate MDC backend.

Its purpose is to provide partners with a stable external contract.

Example:

```text
Today:
POST /api/v1/service-discovery/search

Future breaking redesign:
POST /api/v2/service-discovery/search
```

A Marketplace integrated with `/api/v1/...` can continue operating even if MDC later develops a different v2 request/response contract.

Versioning provides:

1. **Stable partner integration**
2. **Controlled future breaking changes**
3. **Clear separation between current and legacy APIs**
4. **Reduced risk of partners depending on internal/demo endpoints**
5. **Ability to deprecate old APIs gradually**
6. **A clear externally supported API surface**

The `/api/v1/` prefix does not automatically change the business logic. A v1 URL can route to the same current Django view/service as an older compatibility URL.

---

# 3. How v1 and Legacy APIs Relate

The MDC is one Django backend.

The URLs are different entry points into backend functionality.

```text
                         MDC Django backend
                                |
              +-----------------+-----------------+
              |                                   |
       Canonical v1 API                    Older /api routes
       for new partners                     / compatibility
              |                                   |
              |                                   |
 /api/v1/service-discovery/search     /api/service-discovery/search
              |                                   |
              +---------------+-------------------+
                              |
                    Same current H1-H9
                  service-discovery flow
                              |
                   Fuseki -> RDFLib -> YAML
```

This is different from the old catalogue search:

```text
/api/catalog/search
        |
        v
Legacy catalogue request/matcher
        |
        v
Legacy provider seed schema
```

Therefore:

- `/api/v1/service-discovery/search` = **current harmonized search**
- `/api/service-discovery/search` = **compatibility alias to current harmonized search**
- `/api/catalog/search` = **different legacy search implementation**

There is no automatic "communication" from every legacy endpoint into v1. Each route must be deliberately mapped.

---

# 4. Current Deployed API Classification

## 4.1 Canonical v1 APIs — Official Partner Candidates

| Method | Endpoint | Status | Purpose |
|---|---|---|---|
| GET | `/api/v1/health` | **WORKING** | MDC availability/health |
| GET | `/api/v1/catalog/filters` | **WORKING** | Marketplace catalogue/filter metadata |
| POST | `/api/v1/service-discovery/search` | **WORKING** | Main harmonized provider/offering discovery |

Production base:

```text
https://maasai-mdc-v1.vercel.app
```

Official current partner URLs:

```text
GET  https://maasai-mdc-v1.vercel.app/api/v1/health

GET  https://maasai-mdc-v1.vercel.app/api/v1/catalog/filters

POST https://maasai-mdc-v1.vercel.app/api/v1/service-discovery/search
```

---

## 4.2 Compatibility Routes — Current Logic Without `/v1`

These remain available so existing callers are not broken.

| Method | Endpoint | Classification |
|---|---|---|
| GET | `/api/health` | compatibility alias |
| GET | `/api/catalog/filters` | compatibility alias |
| POST | `/api/service-discovery/search` | compatibility alias |

For new MaaSAI partner integrations, use `/api/v1/...`, not these aliases.

---

## 4.3 Legacy APIs

These use older contracts and/or older seed-data paths.

| Method | Endpoint | Classification | Recommendation |
|---|---|---|---|
| POST | `/api/catalog/search` | legacy search | Do not give to new partners |
| GET | `/api/providers/{provider_id}` | legacy provider detail | Do not advertise as v1 |
| GET | `/api/offerings/{offering_id}` | legacy offering detail | Do not advertise as v1 |
| POST | `/api/provider-publication` | legacy file-backed publication | Disabled in production; do not give to partners |

Important:

```text
POST /api/provider-publication
```

is deliberately disabled on Vercel because the current implementation writes provider YAML to the local filesystem. Vercel serverless storage is not suitable for durable provider publication.

---

# 5. API Endpoints in the Marketplace PDF vs Actual Deployment

The attached API document currently describes six functional API groups.

| PDF API | Documented endpoint | Actual deployed status | Action |
|---|---|---|---|
| Catalogue Filter | `GET /api/v1/catalog/filters` | **Exists and works** | Keep, but update response example |
| List Providers | `GET /api/v1/providers` | **Not currently implemented as v1** | Remove/mark planned, or implement later |
| Specific Provider | `GET /api/v1/providers/{provider_id}` | **Not currently implemented as v1** | Remove/mark planned, or implement later |
| Service Discovery | `POST /api/v1/service-discovery/search` | **Exists and works** | Keep; align response example |
| Publication Validation | `POST /api/v1/provider-publication/validation` | **Not currently implemented as v1** | Mark planned/deferred |
| Service Publication | `POST /api/v1/provider-publication/publish` | **Not currently implemented as v1** | Mark planned/deferred until durable persistence/auth |

The PDF is therefore currently **ahead of the deployed implementation**.

---

# 6. Important Payload Mismatches in the PDF

## 6.1 Catalogue Filters

The PDF shows a simplified response with top-level fields such as:

```text
service_categories
part_families
part_types
materials
processes
certifications
```

The deployed endpoint currently returns existing catalogue fields such as:

```text
service_types
part_families
processes
materials
material_grades
certifications
service_discovery
```

The harmonized values such as:

```text
service_categories
part-family relationships
part types
part-type profiles
```

are currently represented inside the:

```text
service_discovery
```

section of the deployed response.

### Decision needed before partner handoff

Choose one of:

**A. Short-term:** update the PDF to show the actual deployed response.

**B. Later API improvement:** change `/api/v1/catalog/filters` to expose a cleaner v1-only harmonized response while retaining `/api/catalog/filters` as the compatibility response.

Option B is architecturally cleaner, but it requires intentional code/test work.

---

## 6.2 Service-Discovery Response

The PDF shows relatively flat result objects:

```text
provider_id
provider_name
country
offering_name
capabilities
```

The current harmonized v1 implementation uses a richer explainable search contract. Its response includes top-level information such as:

```text
request_id
consumer_id
query_interpretation
warnings
result_count
results
status
```

and each result contains structures such as:

```text
provider
offering
match
matched_attributes
unmatched_attributes
unknown_attributes
evidence
```

The PDF service-discovery response example therefore needs to be aligned with the actual H1-H9 contract before partner distribution.

---

# 7. Provider APIs — Why They Are Not v1 Yet

The older provider-detail implementation was retained for compatibility and is tied to the **legacy provider seed schema**.

During M4 it was deliberately not promoted to `/api/v1/`.

This avoided giving partners a new versioned contract that was actually backed by old data architecture.

If Marketplace needs provider browsing, the better future implementation is:

```text
GET /api/v1/providers
GET /api/v1/providers/{provider_id}
```

backed by the **harmonized service-discovery provider data**, not simply a blind alias to the legacy provider loader.

This should be a deliberate API task.

---

# 8. Provider Publication — Why It Is Deferred

The PDF describes:

```text
POST /api/v1/provider-publication/validation
POST /api/v1/provider-publication/publish
```

These are reasonable target APIs, but they are not currently deployed.

The present legacy publication flow is file-backed.

On Vercel:

```text
provider publication
       |
       v
write YAML file
       |
       X
not durable production persistence
```

For this reason the existing production route is intentionally disabled.

A future publication architecture should be closer to:

```text
Marketplace
    |
POST /api/v1/provider-publication/validation
    |
validate + normalize
    |
POST /api/v1/provider-publication/publish
    |
durable database / catalogue persistence
    |
RDF update
    |
Fuseki/catalogue refresh
```

Publication also needs appropriate authentication/authorization before being exposed publicly.

---

# 9. What Partners Should Receive Today

Until the API alignment work is completed, provide partners only:

## Base URL

```text
https://maasai-mdc-v1.vercel.app
```

## Health

```text
GET /api/v1/health
```

## Catalogue/filter metadata

```text
GET /api/v1/catalog/filters
```

## Service discovery

```text
POST /api/v1/service-discovery/search
```

Do not yet advertise:

```text
/api/v1/providers
/api/v1/providers/{provider_id}
/api/v1/provider-publication/validation
/api/v1/provider-publication/publish
```

because these are not currently part of the deployed v1 route table.

---

# 10. Recommended Status Labels for the Marketplace API Document

Use explicit status labels while the specification is being completed.

| Endpoint | Suggested documentation label |
|---|---|
| `/api/v1/health` | AVAILABLE |
| `/api/v1/catalog/filters` | AVAILABLE — response alignment required |
| `/api/v1/service-discovery/search` | AVAILABLE — response example alignment required |
| `/api/v1/providers` | PLANNED |
| `/api/v1/providers/{provider_id}` | PLANNED |
| `/api/v1/provider-publication/validation` | PLANNED / DEFERRED |
| `/api/v1/provider-publication/publish` | DEFERRED — durable persistence required |

---

# 11. Recommended Next Step Before M7 Partner Integration

Do **not** begin full M7 yet.

First perform a small API alignment milestone:

```text
M6.1 — MDC v1 API and Documentation Alignment
```

Scope:

1. decide whether Marketplace really needs provider list/detail in the first integration;
2. if yes, implement those v1 read APIs against harmonized provider data;
3. decide whether publication validation should be exposed before persistent publication;
4. keep actual publication disabled until durable DB/persistence is available;
5. align `/api/v1/catalog/filters` response with the intended Marketplace contract;
6. update the service-discovery response example to match the actual H1-H9 response;
7. retest all canonical APIs on Vercel;
8. only then finalize the partner API document.

---

# 12. Recommended API Direction

## Current stable partner contract

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

## Recommended next read APIs

If Marketplace requires provider browsing:

```text
GET /api/v1/providers
GET /api/v1/providers/{provider_id}
```

These should use harmonized provider data.

## Deferred write APIs

```text
POST /api/v1/provider-publication/validation
POST /api/v1/provider-publication/publish
```

Validation may be introduced earlier if useful.

Actual publishing should remain deferred until durable persistence and access control are implemented.

---

# 13. Final Conclusion

The current Vercel deployment is not generally broken.

The issue is primarily **API specification alignment**:

```text
Deployed canonical v1 API
        !=
all endpoints currently written in the Marketplace PDF
```

M4 intentionally created a small stable v1 surface instead of automatically versioning all legacy APIs.

The correct approach is not to expose every legacy API under `/api/v1/`.

Instead:

```text
Current harmonized functionality
        -> canonical /api/v1/

Old implementation still needed
        -> /api/ compatibility/legacy

New functionality not production-ready
        -> planned/deferred
```

This preserves a clean, stable API contract for MaaSAI partners and gives MDC room to introduce future `/api/v2/` changes without breaking Marketplace integrations.
