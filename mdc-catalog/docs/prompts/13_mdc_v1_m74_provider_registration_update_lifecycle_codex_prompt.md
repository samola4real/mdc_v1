# Codex Prompt — M7.4 Provider Registration and Update Lifecycle

**Project:** MaaSAI MaaS Dynamic Catalogue (MDC)  
**Milestone:** M7.4 — Provider registration/update lifecycle  
**Executor:** Codex on the user's local repository  
**Recommended model:** GPT-5.6 Sol  
**Recommended reasoning:** Medium; use High only for a real transactional/PostgreSQL blocker

## Mission

Implement **M7.4 only**. M7.3 is accepted and the repository is ready for provider registration and update writes.

M7.4 must replace the legacy file-backed provider publication write path with a PostgreSQL-backed, transactional provider lifecycle and add provider/offering update routes. Every successful write must create durable publication history and pending catalogue sync/outbox evidence. **Do not process RDF/Fuseki sync in this milestone.**

Do not start M7.5 automatically.

## Repository and baseline

Repository:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Project root:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

Backend:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\backend
```

Remote:

```text
https://github.com/samola4real/mdc_v1
```

Accepted M7.3 implementation/report commits:

```text
9b0feec  feat: add M7.3 provider validation and DB-backed reads
ea6bf17  docs: report M7.3 provider validation and read lifecycle
```

At the M7.3 gate:

```text
Full local suite: 466 passed, 13 existing skips
H1-H9 focused:   225 passed, 5 existing skips
PostgreSQL M7.3 focused: 35 passed
Migration drift: none
```

M7.3 report:

```text
mdc-catalog/docs/Phase_2/14_mdc_v1_m73_provider_validation_read_lifecycle_report.md
```

Expected pre-M7.4 marker:

```text
READY_FOR_M74_PROVIDER_REGISTRATION_UPDATE_LIFECYCLE
```

## Important worktree rule

The user has a **pre-existing unrelated `.gitignore` modification**. Preserve it exactly. Do not stage, commit, revert, overwrite, or discard it unless the user explicitly asks.

Preserve all unrelated untracked helper files as well.

Before implementation:

1. fetch/synchronize safely with `origin/main`;
2. verify the M7.3 commits/report are present;
3. record the pre-existing worktree state;
4. exclude unrelated local modifications from every M7.4 commit.

## Architecture rules that remain fixed

1. PostgreSQL is the operational source of truth for provider lifecycle state.
2. Neon is only the current temporary managed PostgreSQL host. Application code must remain standard PostgreSQL/cloud-provider-neutral and future-AWS-portable.
3. RDF/Fuseki remains the semantic catalogue/search layer.
4. H1-H9 matching/search semantics must not be redesigned.
5. Live service-discovery runtime remains unchanged in M7.4. Do **not** switch discovery from YAML/Fuseki/runtime fallback to PostgreSQL in this milestone.
6. Stable API URLs use `contract_version = "1.0"`; do not add `/api/v1/...` routes.
7. GET view functions belong in `backend/apps/api/views/get_views.py`.
8. POST/PATCH write view functions belong in `backend/apps/api/views/post_views.py`.
9. Production write routes remain disabled by default. M7.4 does not add authentication/authorization and therefore must not make anonymous production writes available.
10. No committed secrets, `.env`, connection strings, database hosts/users/passwords, or credential-bearing logs/reports.

## M7.4 target routes

Implement/replace these lifecycle writes:

```text
POST  /api/provider-publication
PATCH /api/providers/{provider_id}
POST  /api/providers/{provider_id}/offerings
PATCH /api/offerings/{offering_id}
```

Keep the M7.3 read/validation routes unchanged:

```text
POST /api/provider-publication/validation
GET  /api/providers/{provider_id}
GET  /api/providers/{provider_id}/offerings
GET  /api/offerings/{offering_id}
```

Keep the canonical public discovery endpoints unchanged:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

`POST /api/catalog/search` remains legacy/internal. No `/api/v1/...` route may appear.

---

# Task 1 — Retire file-backed behavior from canonical provider publication

The existing `POST /api/provider-publication` route currently resolves to legacy file-backed behavior when enabled. Replace the route implementation with the new M7.4 PostgreSQL lifecycle implementation.

After M7.4, a successful canonical provider publication must **not**:

- create or overwrite YAML provider files;
- call the legacy seed repository writer;
- directly generate RDF;
- directly update Fuseki.

Do not delete legacy seed/YAML infrastructure if it is still required by legacy search/tests/runtime fixtures. Merely stop using it for the canonical provider lifecycle write.

Prove with tests that M7.4 provider publication has no file-write side effect.

---

# Task 2 — Reuse the harmonized publication contract

For full provider registration, reuse:

```text
ServiceDiscoveryPublicationSerializer
normalize_service_discovery_publication()
```

Do not create a second competing vocabulary/taxonomy contract.

The current harmonized rules remain authoritative, including:

- controlled service categories/part families/part types;
- certifications/material/process vocabularies;
- evidence metadata;
- provider ID format;
- MDC-owned identifier rejection;
- route/operation field rejection;
- duplicate service-category rejection;
- capability validation.

Refactor shared validation helpers only when necessary to support offering-level create/update. Avoid copying controlled vocabulary rules into new serializers/services.

## Flexible/staging fields

Preserve the established MDC design principle:

```text
Flexible provider/staging input
          ↓
validation/mapping/normalization
          ↓
controlled harmonized searchable fields
```

M7.4 should support the existing JSONB staging fields deliberately:

```text
Provider.custom_provider_fields
Offering.custom_offering_fields
Offering.custom_capability_fields
```

Provider-specific/free-text values must stay in these custom JSONB fields unless they are valid controlled ontology/vocabulary values. Do not silently promote custom values into controlled fields.

If the current full-publication serializer does not explicitly accept `custom_provider_fields`, add it as an optional JSON object without altering the canonical H1-H9 normalized shape. For offering dictionaries, explicitly validate optional `custom_offering_fields` and `custom_capability_fields` as JSON objects and preserve them in persistence while keeping them outside controlled canonical matching fields.

Forbidden route/operation keys must remain rejected recursively, including when nested inside custom structures.

Use existing finite/JSON-safety checks where available; do not persist NaN/Infinity or non-JSON-safe structures.

---

# Task 3 — Registration semantics for POST /api/provider-publication

Treat this route as **new provider registration/publication**, not silent upsert of an existing provider.

### Contract version

- omitted `contract_version` defaults to `1.0` where safe;
- explicit `1.0` accepted;
- unsupported explicit version -> safe HTTP 400 using existing contract-version error style.

### Feature flag

Use the existing provider publication/write safety flag rather than inventing unnecessary flags:

```text
MDC_PROVIDER_PUBLICATION_ENABLED
```

Production default must remain `False`.

When disabled:

- return safe HTTP 403;
- do not validate into a write path;
- do not mutate any database model;
- do not create publication history or sync events.

### Duplicate provider

If `provider_id` already exists, do not overwrite it through POST registration.

Return a stable safe conflict response, preferably:

```text
HTTP 409
error.code = provider_already_exists
```

A concurrent duplicate-registration race must also resolve safely to conflict rather than a raw database exception.

### Successful registration

Within one `transaction.atomic()` boundary:

1. create Provider;
2. create ordered ProviderCertification rows;
3. create ordered Offering rows;
4. create ProviderPublication history;
5. create CatalogueSyncEvent/outbox rows;
6. commit.

A successful registration represents an accepted publication and should create the Provider in `active` lifecycle state unless a stronger existing project invariant requires otherwise. If you find a conflicting accepted rule in current implementation/tests/docs, preserve the newer working invariant and explain it in the report.

Preserve submission ordering:

- certification `sequence_index = 0..n-1` in submitted order;
- offering `sequence_index = 0..n-1` in submitted order.

Generated offering IDs remain MDC-owned and deterministic using the existing generator unless a demonstrated collision bug requires a narrowly scoped fix:

```text
{provider_id}_{service_category}
```

### Publication history

For a successful registration, create one `ProviderPublication` with at least:

```text
operation = create
provider = created provider
provider_id_snapshot = submitted provider_id
contract_version = 1.0
submitted_payload = safe submitted provider payload
normalized_payload = complete normalized/canonical post-write representation
validated_at = set
persisted_at = set
status = sync_pending
completed_at = null
```

Do not put secrets/system metadata into publication payloads.

### Outbox/sync evidence

Create pending events in the same DB transaction:

- one provider `upsert` event;
- one offering `upsert` event for each created offering.

Do not create separate certification event types; provider synchronization owns provider certification representation.

M7.4 creates durable pending events only. **Do not process them and do not contact Fuseki.**

---

# Task 4 — Close the current outbox identity gap if necessary

Inspect `CatalogueSyncEvent` against the accepted M7 design. M7.5 must be able to identify the exact provider/offering to synchronize.

If the current model still lacks an external entity identifier, add:

```text
entity_id
```

with an appropriate string length capable of storing provider/offering external IDs, plus a normal Django migration (expected next migration: `0003...`).

Use:

```text
provider event entity_id = provider.provider_id
offering event entity_id = offering.offering_id
```

Do not add Neon-specific types/extensions.

If current `origin/main` already contains an equivalent durable entity identifier by the time this prompt runs, reuse it and do not create redundant schema.

Run `makemigrations --check --dry-run` after committed migrations to prove no drift.

---

# Task 5 — Provider PATCH

Implement:

```text
PATCH /api/providers/{provider_id}
```

This is a partial top-level update. `provider_id` is immutable.

Recommended M7.4 editable fields:

```text
provider_name
country
status
certifications
publication_metadata
custom_provider_fields
```

Do not allow offerings to be edited inside Provider PATCH; use offering routes.

If the payload contains immutable/unsupported controlled identity fields, reject safely rather than ignoring them.

### Partial semantics

- omitted fields remain unchanged;
- a supplied scalar replaces the scalar;
- a supplied JSON object replaces that top-level object as a whole for M7.4 (do not invent undocumented deep-merge/delete semantics);
- a supplied certifications list replaces the provider certification set as a whole and reassigns deterministic sequence indexes in submitted order;
- omitted certifications remain unchanged.

Validate any supplied controlled certification/evidence values using the same harmonized rules as full publication.

Use `select_for_update()` on the target Provider during the transaction to protect the write path.

Unknown provider -> safe HTTP 404 `provider_not_found` with no mutation.

A successful PATCH must:

- update only supplied fields;
- create one ProviderPublication with `operation = update`;
- set its final M7.4 status to `sync_pending` with validation/persistence timestamps;
- store the submitted patch in `submitted_payload`;
- store the complete resulting canonical provider state in `normalized_payload` (not merely the patch), including current offerings as needed for deterministic audit/reconstruction;
- create one pending provider `upsert` CatalogueSyncEvent;
- not contact Fuseki.

---

# Task 6 — Add an offering to an existing provider

Implement:

```text
POST /api/providers/{provider_id}/offerings
```

The path supplies provider identity. Reject body-supplied `provider_id` or `offering_id` rather than allowing identity override.

Required controlled offering inputs should match the existing harmonized offering contract:

```text
service_category
offering_name
part_family
support_status
```

Optional harmonized fields:

```text
supported_part_types
family_capabilities
part_type_capabilities
generic_capabilities
custom_offering_fields
custom_capability_fields
```

Validate with the same taxonomy/capability/evidence rules as full provider publication. Do not duplicate the vocabulary implementation.

Generate the MDC-owned offering ID using the existing deterministic generator.

Unknown provider -> 404 `provider_not_found`.

If the generated offering already exists or the same provider already has that deterministic service-category offering, return safe HTTP 409 (for example `offering_already_exists`).

Within one transaction:

- lock the Provider;
- create the Offering;
- assign `sequence_index` after the provider's current maximum (deterministically; use 0 when it is the first offering);
- create one ProviderPublication with `operation = update` and full post-write normalized provider state;
- create one pending offering `upsert` CatalogueSyncEvent;
- commit.

Do not create a provider outbox event unless the provider-level semantic representation actually changes as part of the offering relationship and current RDF mapping requires it. If both provider and offering events are required by the existing RDF structure, prove why in tests/report and create both transactionally. Prefer the minimum sufficient durable event set.

---

# Task 7 — Offering PATCH

Implement:

```text
PATCH /api/offerings/{offering_id}
```

Stable identity fields are immutable in M7.4:

```text
offering_id
provider_id
service_category
part_family
```

Rationale: current deterministic offering IDs include service category and part family is constrained by service category. Changing either under a stable offering ID would create identity/taxonomy ambiguity. A provider needing a different service category should create a new offering and deactivate the old one.

Recommended editable fields:

```text
offering_name
support_status
supported_part_types
family_capabilities
part_type_capabilities
generic_capabilities
custom_offering_fields
custom_capability_fields
is_active
```

Omitted fields remain unchanged. Supplied JSON/list fields replace that field as a whole; do not invent deep patch semantics in M7.4.

Revalidate the **complete resulting offering state** against the existing harmonized taxonomy/capability rules before persistence. This is important because a partial patch may make sense only when combined with existing fields.

Unknown offering -> 404 `offering_not_found`.

Within one transaction:

- lock the Offering and relevant Provider;
- apply only supplied mutable fields;
- preserve sequence index and stable IDs;
- create one ProviderPublication with `operation = update` and complete post-write normalized provider state;
- create one pending offering `upsert` CatalogueSyncEvent;
- commit.

Do not contact Fuseki.

---

# Task 8 — Failed write behavior and audit safety

The M7.3 validation-only endpoint must remain strictly non-mutating.

For actual enabled M7.4 write routes:

- validation failure must never change Provider/Offering/Certification state;
- no sync/outbox event may be created for a failed write;
- if practical with the existing ProviderPublication model, record a `validation_failed` ProviderPublication audit record containing safe submitted payload + structured validation errors, but only after the write feature flag has passed and without altering catalogue entities;
- if implementing failed-attempt audit would materially complicate or weaken transaction/error behavior, successful-write history is mandatory and failed-attempt audit may be deferred explicitly to M7.6 with a documented reason.

Never create audit records for feature-flag-disabled requests.

All exception responses must be safe and must not include:

- SQL;
- stack traces;
- filesystem paths;
- database host/user/password/URL;
- internal UUIDs unless deliberately exposed as the external `publication_id` contract;
- backend/provider-specific diagnostics.

---

# Task 9 — Response contract

Follow the stable unversioned API pattern and existing public error style.

A successful write response should be compact and suitable for future Marketplace use. Include only deliberate lifecycle information, for example:

```json
{
  "contract_version": "1.0",
  "status": "accepted",
  "operation": "create|update",
  "provider_id": "...",
  "publication_id": "...",
  "publication_status": "sync_pending",
  "sync_status": "pending",
  "offering_ids": ["..."]
}
```

For offering-specific routes, include the affected `offering_id`.

Use HTTP status semantics consistently:

```text
201 new provider registration / new offering
200 successful PATCH
400 invalid payload/contract
403 write feature disabled
404 unknown provider/offering
409 duplicate identity/conflict
```

Do not expose model timestamps, sequence indexes, database UUIDs for Provider/Offering/Certification/SyncEvent, raw SQL, filesystem paths, or internal backend diagnostics.

`ProviderPublication.id` is an MDC-owned publication identifier and may be exposed as `publication_id` if this remains consistent with accepted design.

---

# Task 10 — Transaction and concurrency verification

Add focused tests proving at least:

1. successful provider registration is atomic;
2. provider + certifications + offerings + publication + outbox all commit together;
3. injected mid-write failure rolls the entire successful-write transaction back;
4. provider PATCH locks/updates correctly;
5. offering create locks provider and calculates deterministic sequence index;
6. offering PATCH preserves immutable identity/sequence;
7. duplicate provider registration returns conflict and does not overwrite;
8. duplicate offering creation returns conflict and does not overwrite;
9. database uniqueness/IntegrityError races are translated to safe contract responses;
10. disabled write flag creates no mutations/audit/events;
11. validation failures create no catalogue/outbox mutation;
12. no YAML writer, RDF generator, Fuseki query/update, or runtime switch is called by M7.4 writes;
13. every successful write creates exactly one traceable publication history record and the expected pending event set;
14. ordering fidelity remains deterministic;
15. custom JSONB fields round-trip without becoming controlled fields.

Use existing tests as the current source of truth where they reflect newer implementation behavior. Do not weaken or delete valid regression tests merely to satisfy this milestone.

---

# Task 11 — Managed PostgreSQL verification

The canonical ignored local:

```text
mdc-catalog/.env
```

should already provide the validation `DATABASE_URL`. Never print it.

Run M7.4 focused persistence/API tests against real PostgreSQL, preferably using a separate randomly named temporary Django test database as established in M7.2/M7.3.

Requirements:

- prove `connection.vendor == "postgresql"` safely;
- apply migrations including any M7.4 migration;
- verify `CatalogueSyncEvent.entity_id` physically exists if added;
- verify JSONB/UUID/constraints still behave correctly;
- run all M7.4 write tests under PostgreSQL transactions;
- clean up only task-created temporary test databases;
- never drop/reset the configured `mdc_validation` catalogue database;
- never reveal connection details.

If managed PostgreSQL is temporarily unavailable, do not pretend the gate passed. Report the blocker clearly.

Do not alter the populated validation catalogue unless a smoke test is explicitly transaction-rolled-back and leaves proven zero net changes. Prefer isolated test databases.

---

# Task 12 — Regression gates

After M7.4 implementation, run at minimum:

```text
python manage.py check
python manage.py makemigrations --check --dry-run
```

Run the full local test suite using the established local/SQLite regression method without editing or deleting the user's canonical `.env`.

Baseline before M7.4:

```text
466 passed, 13 existing skips
```

New M7.4 tests may increase the total. There must be zero new failures/errors and no unjustified new skips.

Run the separately maintained H1-H9 suite. Baseline:

```text
225 passed, 5 existing remote-alignment skips
```

H1-H9 behavior must remain unchanged.

Also verify route safety:

```text
/api/v1/health                       -> 404
/api/v1/catalog/filters              -> 404
/api/v1/service-discovery/search     -> 404
```

Production settings must keep provider lifecycle writes disabled by default.

---

# Task 13 — Explicit M7.4 non-goals

Do **not** do any of the following in M7.4:

- process CatalogueSyncEvent rows;
- regenerate/update Fuseki from write routes;
- implement retry workers/jobs;
- switch service discovery to DB runtime;
- redesign H1-H9;
- add Marketplace login/auth UI;
- claim feature flags are authentication;
- expose lifecycle write APIs publicly in production;
- add `/api/v1/...` URLs;
- deploy Vercel;
- configure AWS production infrastructure;
- update partner-facing API documentation to advertise these write routes;
- start M7.5.

---

# Task 14 — Documentation/report

Create:

```text
mdc-catalog/docs/Phase_2/15_mdc_v1_m74_provider_registration_update_lifecycle_report.md
```

Report at least:

- files changed;
- route contract and feature-flag behavior;
- exact registration/PATCH semantics;
- immutable fields;
- custom staging-field behavior;
- transaction boundaries;
- publication-history behavior;
- outbox event behavior/counts;
- any M7.4 migration and physical PostgreSQL verification;
- duplicate/conflict behavior;
- rollback/concurrency evidence;
- proof canonical publication no longer writes YAML;
- PostgreSQL-focused test counts;
- full local suite counts;
- H1-H9 counts;
- production route safety;
- confirmation that no Fuseki sync/runtime switch was started;
- known limitations, especially lack of auth/authorization and unprocessed sync events.

Do not include any credentials, database URL, hostname, username, password, or sensitive `.env` value.

Expected successful end marker:

```text
READY_FOR_M75_RDF_FUSEKI_SYNCHRONIZATION
```

If any required gate fails, finish instead with:

```text
NOT_READY_FOR_M75_RDF_FUSEKI_SYNCHRONIZATION
```

and state the exact blocker.

---

# Task 15 — Git discipline

Keep implementation and report commits reviewable. Suggested commits:

```text
feat: add M7.4 provider registration and update lifecycle
docs: report M7.4 provider registration and update lifecycle
```

Do not include the user's unrelated `.gitignore` modification, local `.env`, temporary DB artifacts, generated files, or helper folders.

Before any push, inspect the exact staged diff and verify no secrets or unrelated changes are present.

If external-action policy requires explicit user authorization to push to:

```text
origin/main
https://github.com/samola4real/mdc_v1
```

stop after local commits and ask for that approval. Do not mark M7.4 technically failed merely because a push authorization is pending; distinguish `technical gate PASS, push pending approval` from an implementation/test failure.

Do not start M7.5 automatically after completion.
