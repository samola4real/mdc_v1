# MDC API, Persistence, and Rectification Decisions

**Date:** 2026-09-04  
**Project:** MaaSAI MaaS Dynamic Catalogue (MDC)  
**Status:** Final agreed design direction before M6.1 completion

---

## 1. Purpose

This report records the API and persistence decisions agreed after the first successful Vercel deployment and before completing the API rectification milestone.

The goal is to avoid repeatedly changing partner-facing routes while MDC continues to evolve.

The governing principle is:

> Keep stable `/api/...` URLs for Marketplace and other MaaSAI components, evolve the contract behind those URLs in a backward-compatible way, and use explicit contract metadata instead of URL-versioned paths such as `/api/v1/`, `/api/v2/`, etc.

---

## 2. Current H1-H9 Service-Discovery Implementation

The current MDC source of truth is the harmonized H1-H9 service-discovery implementation.

It includes:

- harmonized service category / part family / part type registry;
- provider publication normalization support;
- harmonized provider YAML;
- structured search request validation and normalization;
- H5 matching/scoring;
- H6 RDF generation;
- H7 RDFLib retrieval;
- H8 optional remote Fuseki retrieval;
- H9 matching alignment;
- runtime fallback behavior.

The deployed search follows:

```text
External Fuseki, if configured
        ↓
RDFLib over generated harmonized RDF
        ↓
Harmonized YAML fallback
```

The first Vercel deployment successfully used:

```text
harmonized_rdf_rdflib_with_h5_policy
```

H1-H9 therefore remains the implementation that future MDC API work must preserve.

---

## 3. Final Search Route Decision

The current and future canonical search route is:

```text
POST /api/service-discovery/search
```

This route should remain stable for Marketplace and other MaaSAI components.

MDC will **not** use URL-versioned public routes such as:

```text
/api/v1/service-discovery/search
/api/v2/service-discovery/search
/api/v3/service-discovery/search
```

The previously introduced `/api/v1/...` route family was an intermediate M4 decision and is superseded by this final M6.1 architecture decision. Those routes should be removed during M6.1 rather than kept as compatibility aliases because no final partner handoff has yet established a dependency on them.

### Legacy search retained only for historical/deliverable compatibility

```text
POST /api/catalog/search
```

This is a separate older implementation using the legacy catalogue/search model and legacy provider seed schema.

Decision:

- keep it because it already exists and has been referenced in project deliverables;
- do not use it for future Marketplace integration;
- do not evolve new functionality around it;
- do not promote it as the canonical MDC search API.

---

## 4. API Contract Versioning Strategy

The final strategy is:

```text
stable URL + contract_version metadata
```

Example request:

```json
{
  "contract_version": "1.0",
  "request_id": "req_001",
  "consumer_id": "consumer_001",
  "service_category": "precision_metal_parts",
  "part_family": "metal_part",
  "part_type": "block",
  "requirements": {}
}
```

Example response metadata:

```json
{
  "contract_version": "1.0",
  "request_id": "req_001",
  "result_count": 2,
  "results": []
}
```

### Backward compatibility principle

When the contract evolves, the URL remains unchanged.

For example:

- `contract_version = 1.0` continues to receive the established contract;
- a future contract may support `2.0` without introducing `/api/v2/...`;
- if `contract_version` is omitted, MDC may default to the established baseline contract when safe and documented.

This minimizes integration changes for deployed Marketplace and MaaSAI components.

---

## 5. Final Stable Endpoint Strategy

The intended long-term external routes are:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

There is no public `/api/v1/...` route family in the final M6.1 design.

The M6.1 test suite should explicitly verify that previously introduced URL-versioned routes return `404`.

### Legacy only

```text
POST /api/catalog/search
```

Retain only for legacy/deliverable compatibility.

---

## 6. Provider APIs

The current provider-detail implementation is linked to the older legacy provider seed schema, whereas the H1-H9 service-discovery path uses the harmonized provider representation.

Current provider/detail routes may remain available internally/currently, but they should **not yet be advertised to external partners**.

Before provider browsing becomes an external partner contract, it should be backed by the harmonized provider model and later the durable database model rather than blindly exposing the legacy seed schema.

The same principle applies to offering-detail APIs.

---

## 7. Why Provider Publication Write Is Deferred

Provider publication is not deferred only because a database product has not yet been selected.

It is a state-changing production workflow and needs several capabilities that the current Vercel pilot does not yet provide.

### 7.1 Durable persistence

The current legacy publication flow writes provider YAML files. This is not suitable as a durable system of record on Vercel serverless infrastructure.

A publication accepted through the API must survive redeployment, serverless instance replacement, concurrent requests, and application restarts.

### 7.2 Transactional consistency

Publication may eventually update:

```text
Provider record
    ↓
Offering records
    ↓
Normalized capabilities
    ↓
RDF generation/update
    ↓
Fuseki catalogue
```

The operational database and RDF/Fuseki state must not silently diverge.

### 7.3 Authentication and authorization

Publishing or changing provider data must not be anonymously available on the public internet. The future workflow needs to know who submitted a change and whether that actor is authorized to modify the provider.

### 7.4 Update/version history

Provider publication should support traceability including created/updated timestamps, submitted-by identity, previous version, publication status, and approval/rejection where relevant.

### 7.5 Concurrency and validation

Two updates to the same provider/offering should not overwrite one another unpredictably.

### Conclusion

Provider publication write remains deferred until durable persistence, access control, update history, and synchronization requirements are available.

---

## 8. Provider Publication Validation

Validation is less risky than publication because it does not persist catalogue state. However, provider-publication validation remains out of external partner documentation for now.

It may later become a trusted Marketplace/internal-component API.

Important distinction:

> Hidden from documentation is not the same as technically protected.

When activated for real integration, authentication/authorization should be considered even if the operation is validation-only.

---

## 9. Database Recommendation

The recommended operational database is:

```text
PostgreSQL
```

For the Vercel-hosted architecture, **Neon PostgreSQL** is the preferred first candidate.

### Why PostgreSQL fits MDC

The core operational model is relational:

```text
Provider
  └── Offerings
        ├── capabilities
        ├── materials
        ├── processes
        ├── certifications
        └── publication/version state
```

MDC will also need provider/offering relationships, publication history, ownership/authorization records, timestamps, and status fields.

PostgreSQL also provides `JSONB`, which is suitable for flexible staging/custom provider input before normalization into controlled MDC fields.

Recommended direction:

```text
Flexible provider input / staging
        ↓
PostgreSQL relational + JSONB storage
        ↓
validation / normalization / vocabulary mapping
        ↓
controlled MDC provider/offering fields
        ↓
RDF generation / semantic catalogue
```

NoSQL is therefore not recommended as the primary MDC operational database at this stage.

---

## 10. Long-Term Vercel Architecture

Vercel should remain the host for the MDC Django REST API as MDC evolves.

```text
Marketplace / MaaSAI components
             |
             | stable REST API
             v
        Django on Vercel
             |
       +-----+------+
       |            |
 PostgreSQL       Fuseki
 operational     semantic RDF
 system of       catalogue /
 record          search layer
```

Responsibilities:

**Vercel / Django**
- external API;
- request validation;
- orchestration;
- response shaping;
- provider/publication workflows.

**PostgreSQL**
- durable operational provider/offering state;
- provider updates;
- publication status/history;
- flexible staging/custom fields;
- future user/ownership records.

**Fuseki / RDF**
- ontology-backed semantic representation;
- semantic search/retrieval;
- reasoning/alignment where applicable.

PostgreSQL and Fuseki are complementary rather than replacements for one another.

---

## 11. External Response Shaping

The partner API document should remain concise and does not need to expose every internal H1-H9 field.

Internal search data may include:

```text
query_interpretation
search_engine
fallback diagnostics
internal matching details
internal evidence/provenance fields
implementation warnings
```

External API responses should expose only information relevant to the calling component.

This must be implemented in the API response itself, not merely hidden from documentation.

Recommended pattern:

```text
Internal H1-H9 result
        ↓
public response adapter / serializer / DTO
        ↓
Marketplace-safe response
```

---

## 12. Documentation Strategy

The Marketplace API document should remain short and practical.

For each external API it should contain primarily:

- purpose;
- method/path;
- required input fields;
- shortened representative request;
- key response fields;
- shortened representative response;
- relevant status codes.

Do not expose internal-only implementation details merely because they exist in backend runtime objects.

---

## 13. Current External Exposure Decision

Do not provide the final API package to partners until M6.1 has been locally tested and redeployed to Vercel.

The intended external route set is:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Provider browsing APIs remain internal/not advertised for now.

Provider publication validation remains internal/not advertised for now.

Provider publication write remains disabled/deferred until durable persistence and access-control requirements are addressed.

---

## 14. M6.1 Rectification Requirements

M6.1 must:

1. make the stable unversioned harmonized routes the canonical API;
2. remove the `/api/v1/...` route family;
3. introduce `contract_version` without breaking the baseline request contract;
4. preserve H1-H9 service-discovery behavior;
5. leave `/api/catalog/search` as legacy-only and do not evolve it;
6. implement external response shaping so internal fields are not unnecessarily exposed;
7. keep provider list/detail internal until their data source is harmonized;
8. keep provider-publication validation non-public for now;
9. keep provider-publication write disabled until durable persistence/access control exists;
10. define the PostgreSQL persistence architecture sufficiently to guide the next implementation phase without implementing it in M6.1;
11. redeploy the rectified API to Vercel;
12. verify the stable routes externally;
13. update the Marketplace API document only after the deployed contract is verified.

---

## 15. Agreed Direction Summary

| Area | Decision |
|---|---|
| Main search route | `POST /api/service-discovery/search` now and future |
| H1-H9 | Preserve as current service-discovery implementation |
| `/api/v1/...` | Remove; URL versioning is not part of final MDC API strategy |
| API versioning | Use explicit `contract_version` and backward-compatible handling |
| `/api/catalog/search` | Legacy only; retain because already referenced in deliverables |
| Provider list/detail | Keep internal/not advertised until harmonized persistence/model is ready |
| Publication validation | Keep non-public for now |
| Publication write | Deferred until durable persistence + access control + update consistency are available |
| Operational DB | PostgreSQL recommended |
| Vercel-friendly DB candidate | Neon PostgreSQL preferred first candidate |
| RDF/Fuseki | Remains semantic catalogue/search layer |
| Vercel | Continue as MDC Django/API host |
| External responses | Deliberately shape/shorten; do not expose unnecessary internal H1-H9 details |
| Partner handoff | Wait until M6.1 completes and is verified on Vercel |

---

## 16. Next Milestone

Complete:

```text
M6.1 — MDC API Contract Rectification
```

Only after M6.1 is tested and verified on Vercel should the Marketplace API document be finalized and partner integration begin.
