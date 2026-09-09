# MDC M7 Persistence and Provider Lifecycle Plan

**Date:** 2026-09-09  
**Project:** MaaSAI MaaS Dynamic Catalogue (MDC)  
**Milestone:** M7 — Persistence and Provider Lifecycle  
**Status:** Design baseline for review before implementation

---

## 1. Purpose

M6.1 stabilized and verified the current public discovery API. The next development step is to introduce durable operational persistence and a proper provider lifecycle without weakening or replacing the harmonized H1-H9 service-discovery implementation.

M7 will establish the foundation required for:

- registering a new MaaS provider;
- validating provider publication data before persistence;
- editing/updating an existing provider;
- adding, editing, and retrieving provider offerings;
- keeping a durable publication/version history;
- preparing controlled synchronization from PostgreSQL to RDF/Fuseki;
- eventually exposing provider lifecycle APIs safely to Marketplace.

The current external discovery APIs remain unchanged during this work:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

No `/api/v1/...` URL family is to be introduced.

---

## 2. Current State Before M7

### 2.1 Public discovery contract

M6.1 is complete and production verified. The stable public contract uses:

```text
contract_version = "1.0"
```

with stable unversioned URLs.

### 2.2 Provider persistence today

The current provider application has no operational Django database model yet; `apps/providers/models.py` is effectively empty.

The older provider publication path is file-backed. It validates a provider-publication payload, normalizes it, and writes provider seed YAML. In production it is intentionally disabled by default.

### 2.3 Harmonized publication logic already available

The repository already contains a harmonized provider-publication serializer and normalizer for the H1-H9 service-discovery schema.

Existing harmonized publication concepts include:

```text
provider_id
provider_name
country
certifications
offerings
publication_metadata
```

Offering-level harmonized fields include:

```text
service_category
offering_name
part_family
support_status
supported_part_types
family_capabilities
part_type_capabilities
generic_capabilities
```

The serializer already enforces controlled vocabulary/taxonomy constraints, rejects forbidden route fields, rejects externally owned identifiers, and validates evidence metadata.

M7 should reuse and evolve this harmonized contract rather than build a separate provider schema.

### 2.4 Legacy provider read APIs

The existing routes:

```text
GET /api/providers/{provider_id}
GET /api/offerings/{offering_id}
```

are backed by the older seed/legacy representation. They remain internal and must not become the new Marketplace contract until they are backed by the new persistent harmonized model.

---

## 3. Core M7 Architecture Decision

The operational system of record will be:

```text
PostgreSQL
```

Preferred first hosted PostgreSQL provider for the current Vercel deployment:

```text
Neon PostgreSQL
```

The semantic layer remains:

```text
RDF + Apache Jena Fuseki
```

The intended architecture is:

```text
Marketplace / Provider UI
          |
          | provider lifecycle API
          v
      Django / DRF
          |
          v
      PostgreSQL
 operational source of truth
          |
          | canonical catalogue adapter
          v
  existing H1-H9 data shape
          |
          +------------------+
          |                  |
          v                  v
    RDF generation       API retrieval
          |
          v
        Fuseki
 semantic catalogue/search
```

PostgreSQL and Fuseki are complementary. PostgreSQL owns operational provider state; RDF/Fuseki owns semantic representation/search.

---

## 4. Important Design Principle — Flexible Provider Input vs Controlled MDC Fields

Provider-entered business information must not automatically become controlled ontology/search fields.

The provider input layer may contain free-text or provider-specific terms, for example:

```text
"precision_manufacturing"
"special finishing service"
"custom prototype support"
```

If these are not official MDC controlled vocabulary values, they must not be written directly into fields such as:

```text
service_category
part_family
part_type
materials
processes
certifications
```

Instead, M7 will preserve two layers:

```text
Flexible provider/staging input
          |
          v
validation / mapping / normalization
          |
          v
Controlled harmonized MDC fields
```

Flexible information should be stored in JSONB fields such as:

```text
custom_provider_fields
custom_offering_fields
custom_capability_fields
```

Controlled/searchable fields remain ontology-compatible and validated against the existing registry/vocabularies.

---

## 5. Recommended Initial Django Data Model

M7 should begin with a pragmatic model that preserves the harmonized H1-H9 shape while avoiding premature over-normalization.

### 5.1 Provider

Recommended fields:

```text
id                         internal UUID / primary key
provider_id                stable external identifier, unique
provider_name              display/business name
country                    current provider country
status                     lifecycle status
custom_provider_fields     JSONB
created_at
updated_at
```

Potential lifecycle statuses:

```text
draft
active
suspended
archived
```

`provider_id` remains the stable external identifier. Internal database identity should not depend solely on a mutable business label.

### 5.2 Offering

Recommended fields:

```text
id                         internal UUID / primary key
offering_id                MDC-owned stable external identifier, unique
provider                   FK -> Provider
offering_name
service_category           controlled value
part_family                controlled value
support_status             controlled lifecycle/support value
supported_part_types       JSONB
family_capabilities        JSONB
part_type_capabilities     JSONB
generic_capabilities       JSONB
custom_offering_fields     JSONB
custom_capability_fields   JSONB
is_active
created_at
updated_at
```

The JSONB capability fields intentionally mirror the already accepted harmonized publication structure. This allows M7 to move from YAML to PostgreSQL without redesigning H1-H9.

A later milestone may normalize selected high-value capability fields into dedicated relational tables if query/performance requirements justify it.

### 5.3 ProviderCertification

Recommended separate relation because certifications are controlled, repeatable, and evidence-bearing:

```text
id
provider                  FK -> Provider
code                      controlled certification code
source_type
confidence
source_note               nullable/internal
created_at
updated_at
```

A uniqueness rule should prevent duplicate certification codes for one provider unless future versioning semantics explicitly require duplicates.

### 5.4 ProviderPublication

This model records each provider lifecycle submission rather than silently overwriting state.

Recommended fields:

```text
id                         UUID publication identifier
provider                   nullable FK -> Provider while new registration is pending
provider_id_snapshot       submitted external provider ID
operation                  create | update
status                     publication workflow status
contract_version
submitted_payload          JSONB
normalized_payload         JSONB
submitted_by_external_id   nullable placeholder for future Marketplace identity
validation_errors          JSONB
created_at
validated_at
persisted_at
completed_at
```

Recommended publication statuses:

```text
received
validation_failed
validated
persisted
sync_pending
synced
sync_failed
rejected
```

This provides auditability and makes retries/synchronization observable.

### 5.5 CatalogueSyncEvent / Outbox

M7 should not update PostgreSQL and Fuseki as an assumed all-or-nothing distributed transaction.

Recommended outbox/sync model:

```text
id
publication               FK -> ProviderPublication
entity_type               provider | offering
entity_id
operation                 upsert | delete
status                    pending | processing | succeeded | failed
attempt_count
last_error
created_at
processed_at
```

This creates a durable handoff between the operational database and the semantic catalogue.

---

## 6. Identifier Ownership

The existing harmonized serializer already treats some identifiers as MDC-owned.

M7 should preserve this distinction.

### Provider-owned / supplied

```text
provider_id
provider_name
business/custom information
```

### MDC-owned / generated

At minimum:

```text
offering_id
facility_id (when introduced)
material_id (where internal identifiers are required)
grade_id (where internal identifiers are required)
publication_id
```

For the first M7 implementation, offering IDs can continue to be generated deterministically from the provider and service category where compatible with existing H1-H9 assumptions. Before exposing provider update APIs externally, collision and rename behavior must be explicitly tested.

---

## 7. Provider Lifecycle API Design

The following API set is the recommended M7 target. These routes are not partner-public until M7 security, persistence, and synchronization gates pass.

### 7.1 Validate provider submission

```text
POST /api/provider-publication/validation
```

Purpose:

- validate payload structure;
- validate controlled vocabularies/taxonomy;
- normalize provider/offering data;
- identify staging/custom fields;
- return warnings/errors;
- do not persist catalogue state.

This endpoint should reuse the harmonized publication serializer/normalizer.

### 7.2 Register/publish a provider

```text
POST /api/provider-publication
```

Purpose:

- create a new provider publication;
- validate and normalize;
- persist provider/offering state transactionally;
- create publication history;
- enqueue RDF/Fuseki synchronization;
- return publication/sync status.

The current file-backed implementation must not be promoted as the final endpoint behavior. The route may remain the same, but its implementation must become PostgreSQL-backed before enabling it in production.

### 7.3 Retrieve provider

```text
GET /api/providers/{provider_id}
```

Purpose:

- retrieve the harmonized persisted provider;
- include stable provider metadata and offering summaries;
- support provider edit screens and trusted Marketplace integration.

The current legacy implementation should be replaced/redirected internally to the new persistent service layer only after parity tests pass.

### 7.4 Update provider

Recommended:

```text
PATCH /api/providers/{provider_id}
```

Purpose:

- update only supplied provider fields;
- validate controlled fields where applicable;
- preserve existing unspecified state;
- write publication/version history;
- enqueue semantic synchronization.

`PUT` should not be the first choice because provider edit forms often change only selected fields. If full-replacement semantics are later required, `PUT` can be added deliberately.

### 7.5 List provider offerings

Recommended:

```text
GET /api/providers/{provider_id}/offerings
```

Purpose:

- retrieve all current offerings for the selected provider;
- populate provider-management UI.

### 7.6 Create a new offering for an existing provider

Recommended:

```text
POST /api/providers/{provider_id}/offerings
```

The provider supplies the offering business/capability content; MDC owns the generated `offering_id`.

### 7.7 Retrieve offering

```text
GET /api/offerings/{offering_id}
```

The existing legacy route can eventually be retained at the same path but backed by PostgreSQL/harmonized data.

### 7.8 Update offering

Recommended:

```text
PATCH /api/offerings/{offering_id}
```

Changes should create publication/version history and a semantic sync event.

---

## 8. Contract Versioning for Provider APIs

Provider lifecycle APIs must follow the same strategy established in M6.1:

```text
stable /api/... URLs + contract_version metadata
```

Do not introduce:

```text
/api/v1/provider-publication
/api/v2/providers/...
```

The initial provider lifecycle contract should use:

```text
contract_version = "1.0"
```

The provider/publication contract version may evolve independently in implementation detail, but the public versioning principle remains consistent.

---

## 9. Transaction Boundaries

A successful publication should treat PostgreSQL changes atomically.

Conceptual flow:

```text
receive request
     |
validate/normalize
     |
BEGIN DB TRANSACTION
     |
upsert Provider
upsert Offering(s)
record ProviderPublication
create CatalogueSyncEvent(s)
     |
COMMIT
     |
async / retryable semantic synchronization
```

If validation fails, provider catalogue state must not change.

If PostgreSQL persistence succeeds but Fuseki synchronization fails, the provider state remains durable and the publication is marked `sync_failed`/`sync_pending` for retry rather than silently rolling back already committed operational data.

---

## 10. H1-H9 Preservation Strategy

M7 must not rewrite the matching engine merely because the operational persistence layer changes.

The safest migration path is:

```text
PostgreSQL models
      |
      v
canonical catalogue repository/adapter
      |
      v
same harmonized provider/offering dictionary shape
      |
      +------------------------+
      |                        |
      v                        v
existing RDF generation    YAML-parity tests
      |
      v
existing H1-H9 runtime
```

The new database repository should be capable of reconstructing the same canonical structure currently loaded from harmonized YAML.

Only after parity is demonstrated should PostgreSQL become the default operational source for provider data.

The runtime fallback design can then evolve deliberately without changing the external service-discovery contract.

---

## 11. Existing YAML Migration Strategy

Current harmonized provider YAML is valuable curated pilot data and must not be discarded.

Recommended migration sequence:

1. create PostgreSQL schema;
2. implement deterministic import command/service for harmonized YAML;
3. import current pilot providers and offerings;
4. reconstruct canonical provider dictionaries from PostgreSQL;
5. compare reconstructed data against YAML source;
6. regenerate RDF from DB-backed canonical data;
7. rerun H1-H9 parity tests;
8. only then designate PostgreSQL as operational source of truth.

The YAML files can remain as fixtures/reference evidence during transition but should stop being the mutable production system of record.

---

## 12. Neon / Vercel Deployment Plan

Neon PostgreSQL is the preferred first hosted database candidate because it fits the existing Vercel-hosted Django deployment.

M7 implementation should introduce environment-based database configuration, for example through a database URL, without committing credentials.

Expected environments:

```text
Local development/test
Vercel Preview
Vercel Production
```

Requirements:

- database credentials only in environment/secrets;
- SSL enabled where required by hosted PostgreSQL;
- Django migrations executed in a controlled deployment step;
- connection behavior suitable for serverless deployment;
- no database credentials in Git, reports, screenshots, or API responses.

Automatic GitHub-to-Vercel deployment is not required to begin M7.

---

## 13. Security and Exposure Gates

Provider write APIs must remain non-public/disabled until the minimum safety boundary is available.

Before external Marketplace exposure, require at least:

```text
durable PostgreSQL persistence
validated provider ownership/authorization model or trusted service-to-service boundary
publication history/audit trail
transactional writes
input validation/normalization
safe error responses
RDF/Fuseki sync observability/retry
concurrency protection
```

The current flag:

```text
MDC_PROVIDER_PUBLICATION_ENABLED=False
```

should remain the production default during early M7 implementation.

M7 may implement and test the APIs behind feature flags before enabling them.

Authentication itself may be integrated with Marketplace later, but MDC must not expose anonymous write operations merely because Marketplace is expected to authenticate users upstream.

---

## 14. Concurrency and Update Safety

Provider edits must avoid lost updates.

Recommended baseline:

- use database transactions;
- lock/update the relevant provider/publication rows when necessary;
- record `updated_at` and publication versions;
- consider optimistic concurrency using an entity version/revision or `If-Match`/ETag in a later API hardening step.

For the first M7 implementation, versioned publication records plus transactional updates are mandatory; public optimistic-concurrency headers may be added before broad external exposure.

---

## 15. M7 Implementation Slices

M7 should be implemented incrementally rather than as one large change.

### M7.0 — Design baseline

Deliverables:

- this persistence/provider-lifecycle plan;
- reviewed model boundaries;
- reviewed endpoint semantics;
- explicit non-goals and acceptance criteria.

No database provisioning required in M7.0.

### M7.1 — PostgreSQL/Django foundation

Deliverables:

- Django provider persistence models;
- initial migrations;
- PostgreSQL/Neon-ready settings;
- local migration/model tests;
- no public provider write exposure yet.

### M7.2 — Harmonized data repository + migration

Deliverables:

- DB repository/service layer;
- import of existing harmonized YAML;
- DB -> canonical H1-H9 data adapter;
- parity tests against current curated data;
- no H1-H9 semantic regression.

### M7.3 — Provider validation and read lifecycle

Deliverables:

- validation-only provider publication endpoint;
- PostgreSQL-backed provider detail;
- provider offerings list;
- PostgreSQL-backed offering detail;
- public contract shaping for provider-management responses;
- routes still internal/trusted until security gate.

### M7.4 — Provider registration and update lifecycle

Deliverables:

- PostgreSQL-backed provider publication/register flow;
- provider PATCH;
- add offering;
- offering PATCH;
- transaction + publication history;
- feature-flag protection retained until ready.

### M7.5 — RDF/Fuseki synchronization

Deliverables:

- durable sync/outbox event;
- RDF regeneration/update from DB-backed canonical data;
- Fuseki update/retry/status behavior;
- failure-state tests;
- H1-H9 search alignment verified after updates.

### M7.6 — External exposure readiness

Deliverables:

- authorization/trusted integration gate;
- concurrency/error-contract review;
- Preview/Production verification;
- provider API partner documentation;
- explicit enablement decision.

---

## 16. Acceptance Criteria for M7 Overall

M7 is complete only when all of the following are demonstrated:

1. PostgreSQL is the durable operational source of truth for providers and offerings.
2. Existing curated harmonized provider data can be imported without semantic loss.
3. DB-backed canonical data preserves H1-H9 service-discovery behavior.
4. New provider registration is persisted transactionally.
5. Existing provider data can be retrieved and updated without file-backed writes.
6. Provider offerings can be created, retrieved, and updated.
7. Provider publication validation can run without changing catalogue state.
8. Every write produces traceable publication/version history.
9. RDF/Fuseki synchronization is observable and retryable.
10. Failed semantic synchronization cannot silently corrupt the operational source of truth.
11. Write routes are protected/disabled until authorization and deployment gates pass.
12. Existing three public discovery endpoints remain backward-compatible.
13. No `/api/v1/...` URL versioning is introduced.
14. Production verification passes before provider APIs are advertised to Marketplace.

---

## 17. M7 Non-Goals

The following should not be bundled into the first persistence implementation unless a direct blocker emerges:

- redesigning H1-H9 matching;
- CAD/2D/3D drawing analysis;
- quotation generation;
- manufacturing routing generation;
- Marketplace user registration/login UI;
- full workflow/approval portal;
- automatic GitHub-to-Vercel deployment;
- replacing Fuseki with PostgreSQL;
- large-scale capability schema normalization before evidence shows it is needed;
- URL API versioning.

---

## 18. Recommended Immediate Next Action

After review/approval of this M7 design baseline, begin:

```text
M7.1 — PostgreSQL/Django foundation
```

The first implementation task should be deliberately narrow:

```text
Django models + migrations
        ↓
PostgreSQL/Neon-ready settings
        ↓
model/repository tests
        ↓
no public write enablement yet
```

Only after M7.1 is verified should the existing harmonized YAML be migrated into PostgreSQL and the provider lifecycle APIs be activated incrementally.

---

## 19. Decision Summary

| Area | M7 decision |
|---|---|
| Operational source of truth | PostgreSQL |
| Preferred hosted DB | Neon PostgreSQL |
| Semantic catalogue | RDF/Fuseki retained |
| H1-H9 | Preserve; DB adapter reconstructs current canonical shape |
| Flexible provider input | JSONB staging/custom fields |
| Controlled searchable fields | Existing ontology registry/vocabularies remain authoritative |
| New provider validation | `POST /api/provider-publication/validation` target |
| New provider registration | `POST /api/provider-publication` target, PostgreSQL-backed |
| Provider retrieval | `GET /api/providers/{provider_id}` target, harmonized DB-backed |
| Provider update | `PATCH /api/providers/{provider_id}` target |
| Offering list | `GET /api/providers/{provider_id}/offerings` target |
| Add offering | `POST /api/providers/{provider_id}/offerings` target |
| Offering retrieval | `GET /api/offerings/{offering_id}` target |
| Offering update | `PATCH /api/offerings/{offering_id}` target |
| Write safety | Feature-flagged/internal until persistence + authorization + sync gates pass |
| Versioning | Stable URLs + `contract_version`; no `/api/v1/...` |
| DB/Fuseki consistency | Durable publication history + outbox/sync status |
| Immediate implementation next | M7.1 PostgreSQL/Django foundation |
