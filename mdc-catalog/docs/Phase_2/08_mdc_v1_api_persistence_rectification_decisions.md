# MDC v1 API, Persistence, and Rectification Decisions

**Date:** 2026-09-04  
**Project:** MaaSAI MaaS Dynamic Catalogue (MDC)  
**Status:** Agreed design direction before API rectification milestone

---

## 1. Purpose

This report records the API and persistence decisions agreed after the first successful Vercel deployment and before starting the API rectification milestone.

The goal is to avoid repeatedly changing partner-facing routes while MDC continues to evolve.

The important principle is:

> Keep stable API URLs for Marketplace and other MaaSAI components, evolve the contract behind those URLs in a backward-compatible way, and use explicit contract metadata rather than introducing a new `/api/vN/` path for every future API revision.

---

## 2. Reminder: Current H1-H9 Service-Discovery Implementation

The current MDC v1 source of truth is the harmonized H1-H9 service-discovery implementation.

It includes the established service-discovery flow covering:

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

The deployed search currently follows:

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

Therefore the H1-H9 service-discovery path remains the implementation that future MDC work must preserve.

---

## 3. Final Direction for the Main Search Route

### Current and future canonical search

```text
POST /api/service-discovery/search
```

This route should remain stable for Marketplace and other MaaSAI components now and in future MDC releases.

It is the current harmonized search implementation and should not be replaced with a new `/api/v2/...`, `/api/v3/...`, etc. route whenever the API evolves.

### Existing versioned route

```text
POST /api/v1/service-discovery/search
```

This route currently works and should be retained as a compatibility alias for the time being.

It should not be treated as the preferred long-term partner route.

### Legacy search

```text
POST /api/catalog/search
```

This is a different legacy implementation using the older catalogue/search model and legacy provider seed schema.

Decision:

- keep it only because it already exists and has been referenced in project deliverables;
- do not use it for future Marketplace integration;
- do not evolve new functionality around it;
- do not promote it as the canonical MDC API.

---

## 4. API Versioning Strategy

The preferred strategy is **stable URLs + contract version metadata**.

Instead of future URL changes such as:

```text
/api/v1/service-discovery/search
/api/v2/service-discovery/search
/api/v3/service-discovery/search
```

use one stable route:

```text
POST /api/service-discovery/search
```

and represent the API contract version explicitly.

Recommended field:

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

The response should also expose the applicable contract version where useful:

```json
{
  "contract_version": "1.0",
  "request_id": "req_001",
  "result_count": 2,
  "results": []
}
```

### Backward compatibility principle

When the contract evolves, the server should preserve the existing request contract wherever practical.

For example:

- `contract_version = 1.0` continues to receive v1-compatible behavior;
- a future contract may use `2.0` internally without requiring Marketplace to change URL;
- if `contract_version` is omitted, MDC may default to the established baseline contract if this is safe and documented.

This reduces coordination burden after public deployment.

---

## 5. Stable Endpoint Strategy

### Intended external / partner-facing stable routes

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

These should become the long-term stable routes given to Marketplace and other MaaSAI components.

### Compatibility aliases currently available

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

Keep for compatibility during rectification, but they do not need to be the routes advertised to new integrations.

### Legacy only

```text
POST /api/catalog/search
```

Retain only for legacy/deliverable compatibility.

---

## 6. Provider APIs

The current provider-detail implementation is linked to the older legacy provider seed schema.

This was easy to forget because the current H1-H9 harmonized service-discovery implementation uses a newer provider representation.

Current decision:

```text
GET /api/providers
GET /api/providers/{provider_id}
```

may remain available internally/for current compatibility work, but they should **not yet be advertised to external partners**.

Before they become external partner APIs, they should be backed by the harmonized provider model and later the durable database model rather than blindly exposing the legacy seed schema.

The same principle applies to offering-detail APIs.

---

## 7. Why Provider Publication Write Is Deferred

Provider publication is not deferred simply because a database product has not yet been selected.

Database selection is one important dependency, but the publication API is a **state-changing production workflow** and therefore needs several things that the current Vercel pilot does not yet provide.

### 7.1 Durable persistence

The current legacy publication flow writes provider YAML files.

That is not suitable for Vercel production persistence because serverless filesystem writes are not a durable system of record.

A publication accepted through an API must survive:

- redeployment;
- serverless instance replacement;
- concurrent requests;
- application restarts.

### 7.2 Transactional consistency

A publication may eventually update more than one representation:

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

Publishing or changing provider data must not be anonymously available on the public internet.

The future workflow needs to know:

- which provider or trusted Marketplace component submitted the change;
- whether it is authorized to modify that provider;
- whether an admin/approval step is needed.

### 7.4 Update/version history

Provider publication should support traceability such as:

- created timestamp;
- updated timestamp;
- submitted by;
- previous version;
- publication status;
- approval/rejection where relevant.

### 7.5 Concurrency and validation

Two updates to the same provider/offering should not overwrite each other unpredictably.

Therefore publication needs a durable transactional layer rather than file writes.

### Conclusion

Provider publication write is deferred until we have a suitable durable persistence architecture and the minimum access-control/update workflow around it.

---

## 8. Provider Publication Validation

A validation endpoint is less risky than publication because it does not need to persist catalogue state.

However, current decision is to keep provider-publication validation **out of external partner documentation for now**.

It may later become a trusted Marketplace/internal-component endpoint.

Important distinction:

> Hidden from documentation is not the same as technically protected.

When this route is activated for real integration, authentication/authorization should be considered even if it performs validation only.

---

## 9. Database Recommendation

The recommended operational database for MDC is:

```text
PostgreSQL
```

For the Vercel-hosted architecture, a managed/serverless PostgreSQL service such as **Neon** is the preferred first candidate.

### Why PostgreSQL fits MDC

The core MDC operational model is relational:

```text
Provider
  └── Offerings
        ├── capabilities
        ├── materials
        ├── processes
        ├── certifications
        └── publication/version state
```

MDC will also need relationships such as:

- provider → offerings;
- offering → capabilities;
- provider/offering → certifications;
- provider → publication/update history;
- ownership and authorization records;
- timestamps/status fields.

PostgreSQL handles this naturally.

### Flexible provider-entered data

PostgreSQL also provides `JSONB`, which is useful for flexible staging/custom provider fields.

This supports the previously agreed MDC principle:

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

Therefore NoSQL is not currently recommended as the primary MDC operational database.

---

## 10. Long-Term Vercel Architecture

Vercel should remain the host for the MDC Django REST API as MDC v1 and future functionality evolve.

Recommended architecture direction:

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

### Responsibilities

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

The partner API document should remain concise.

It does not need to expose every internal H1-H9 search field.

Internal search data may include items such as:

```text
query_interpretation
search_engine
fallback diagnostics
internal matching details
internal evidence/provenance fields
implementation warnings
```

External API responses should expose only information relevant to the calling component.

This must ultimately be implemented in the API response itself, not merely hidden from the documentation.

Recommended pattern:

```text
Internal H1-H9 result
        ↓
public response serializer / DTO
        ↓
Marketplace-safe response
```

The partner document can then show shorter representative payloads, while a separate technical reference can contain complete schemas if needed.

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

Do not expose internal-only implementation details merely because they exist in the backend response today.

---

## 13. Current External Exposure Decision

Before the rectification milestone is complete, do not provide the final API package to partners.

The intended final external route set is being rectified around:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Provider browsing APIs remain internal/not advertised for now.

Provider publication validation remains internal/not advertised for now.

Provider publication write remains disabled/deferred until durable persistence and access-control requirements are addressed.

---

## 14. What the Rectification Milestone Must Resolve

The next milestone should establish the coherent API foundation before partner integration.

It should address:

1. make the stable unversioned harmonized routes the canonical API;
2. preserve `/api/v1/...` only as compatibility aliases;
3. introduce `contract_version` without breaking existing callers;
4. preserve H1-H9 service-discovery behavior;
5. leave `/api/catalog/search` as legacy-only and do not evolve it;
6. define and implement external response shaping so internal fields are not unnecessarily exposed;
7. keep provider list/detail internal until their data source is harmonized;
8. keep provider-publication validation non-public for now;
9. keep provider-publication write disabled until durable persistence/access control exists;
10. define the PostgreSQL persistence architecture sufficiently to guide the next implementation phase, without implementing it during API rectification;
11. redeploy the rectified API to Vercel;
12. verify the stable routes externally;
13. update the Marketplace API document only after the deployed contract is verified.

---

## 15. Agreed Direction Summary

| Area | Decision |
|---|---|
| Main search route | `POST /api/service-discovery/search` now and future |
| H1-H9 | Preserve as current service-discovery implementation |
| `/api/v1/...` | Keep temporarily as compatibility aliases; do not make future version progression depend on URL changes |
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
| Partner handoff | Wait until rectification milestone completes |

---

## 16. Next Milestone

Proceed next with:

```text
M6.1 — MDC API Contract Rectification
```

The rectification milestone should be completed and verified on Vercel before starting the partner-integration milestone.
