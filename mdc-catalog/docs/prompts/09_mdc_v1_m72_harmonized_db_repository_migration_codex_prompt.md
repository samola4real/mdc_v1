# Codex Task 09 — M7.2 Harmonized DB Repository + Curated YAML Migration

## Recommended Codex configuration

- Label: `[mdc_m72_repository_migration]`
- Model: GPT-5.6 Sol
- Reasoning: Medium
- Increase to High only if a real parity/transaction/migration blocker requires it.

Do not start M7.3 or expose provider lifecycle APIs in this task.

---

# Context

Repository root:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Project root:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

Backend root:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\backend
```

Approved design baseline:

```text
mdc-catalog/docs/Phase_2/10_mdc_v1_m7_persistence_provider_lifecycle_plan.md
mdc-catalog/docs/Phase_2/10a_mdc_v1_infrastructure_portability_decision.md
```

M7.1 report:

```text
mdc-catalog/docs/Phase_2/11_mdc_v1_m71_postgresql_django_foundation_report.md
```

M7.1 is accepted. Verified evidence from its report:

```text
focused M7.1 tests: 18/18 passed
full suite:          410 passed, 13 existing skips
focused H1-H9:       225 passed, 5 existing skips
migration 0001:      generated, applied in tests, no drift
public APIs:          unchanged
publication prod:    disabled by default
```

The application persistence design is cloud-neutral. PostgreSQL is the durable target technology; Neon/Vercel are only possible temporary pilot infrastructure. AWS is the long-term MaaSAI deployment target. Do not introduce provider-specific SDKs or persistence assumptions.

Current canonical external discovery APIs remain exactly:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

No `/api/v1/...` family.

---

# M7.2 Goal

Implement the database repository/adapter and deterministic migration of the existing harmonized curated provider catalogue into Django persistence while proving semantic parity with the existing YAML-backed H1-H9 data.

Conceptually:

```text
curated harmonized YAML
        ↓
existing YAML loader
        ↓
transactional DB import
        ↓
Provider / Offering / Certification rows
        ↓
DB canonical adapter
        ↓
same harmonized provider dictionaries
        ↓
RDF + local matcher parity verification
```

M7.2 must NOT switch the production/runtime service-discovery loader to PostgreSQL yet. YAML remains the live runtime source until parity and the later managed-PostgreSQL gate are accepted.

---

# Important M7.1 Review Finding — Evidence/Order Fidelity

Before implementing the repository, account for a parity gap in the M7.1 schema.

The current harmonized YAML/RDF pipeline preserves publication order. In particular:

- provider certifications are emitted with sequence indexes;
- offering lists are ordered in the canonical provider record;
- nested material/process/grade/support lists already preserve order because they are stored as JSON lists;
- top-level `publication_metadata` is part of the harmonized provider record.

The M7.1 relational models do not yet explicitly preserve certification order, offering order, or current top-level publication metadata.

M7.2 is authorized to make the smallest schema correction needed for exact canonical parity.

Preferred minimal correction:

```text
Provider.publication_metadata    JSONField(default=dict, blank=True)
Offering.sequence_index          PositiveIntegerField(default=0)
ProviderCertification.sequence_index PositiveIntegerField(default=0)
```

Generate a normal Django migration, expected as `0002_...py`.

Do not add large new schema abstractions. Do not normalize nested capability JSON fields into relational tables.

Ordering must be explicit in repository queries; do not rely on database insertion order.

Do not add uniqueness constraints on sequence indexes in this task unless current data and migration behavior make that clearly safe and justified. Deterministic explicit ordering plus tests is required.

---

# Step 1 — Synchronize and Inspect

1. Run `git status` from repository root.
2. Pull/fetch `origin/main` as needed.
3. Confirm the worktree is clean.
4. Read the M7.0 plan, portability decision, M7.1 report, current models, migration, YAML loader, RDF generator, and local matcher before editing.
5. Inspect the current curated harmonized provider directory:

```text
mdc-catalog/data/curated/service_discovery/providers/
```

Current expected files include:

```text
demo_machining_provider.yaml
precipart.yaml
tasowheel.yaml
```

Use current repository contents as source of truth if the set has evolved.

Do not discard unrelated user work.

---

# Step 2 — Add Minimal Parity Fields + Migration

Implement the minimal evidence/order-fidelity fields described above unless current code provides an equally clean existing solution.

Requirements:

- `Provider.publication_metadata` stores the current canonical top-level publication metadata only.
- `Offering.sequence_index` preserves the offering list order within the provider canonical record.
- `ProviderCertification.sequence_index` preserves certification publication order.
- Keep current UUID identities, constraints, relationships, JSON capability fields, and lifecycle status choices unchanged unless a genuine defect is demonstrated.
- Create a generated Django migration.
- Run `makemigrations --check --dry-run` after generation.

No provider/publication API changes.

---

# Step 3 — Implement a Harmonized DB Repository / Canonical Adapter

Create a clearly named DB-backed repository/adapter under `apps/providers`, for example:

```text
backend/apps/providers/service_discovery_db_repository.py
```

The exact name may follow a stronger current convention if present.

Provide a small explicit API, conceptually including:

```python
import_service_discovery_provider_records(records)
load_service_discovery_providers_from_db()
get_service_discovery_provider_from_db(provider_id)
```

Names may differ, but responsibilities must remain separated and testable.

## DB -> canonical record shape

The DB adapter must reconstruct the existing internal harmonized shape, not invent a new schema:

```yaml
provider:
  provider_id: ...
  display_name: ...
  country: ...
  certifications: [...]
offerings:
  - offering_id: ...
    provider_id: ...
    service_category: ...
    name: ...
    part_family: ...
    support_status: ...
    supported_part_types: [...]
    family_capabilities: {...}
    part_type_capabilities: {...}
    generic_capabilities: {...}
publication_metadata: {...}
```

Mapping rules:

```text
Provider.provider_name      -> provider.display_name
Offering.offering_name      -> offering.name
Offering.provider FK        -> offering.provider_id using external Provider.provider_id
```

The canonical adapter must NOT leak:

```text
internal UUIDs
custom_provider_fields
custom_offering_fields
custom_capability_fields
created_at / updated_at
DB lifecycle internals
publication/outbox internals
```

unless those are explicitly part of the existing harmonized canonical schema (currently they are not).

Use `select_related`/`prefetch_related` where sensible so the adapter is not designed around obvious N+1 query behavior.

Default catalogue loading should include active providers/current active offerings only. The exact handling of draft/suspended/archived providers must be explicit and tested. Imported current curated catalogue providers should become active.

---

# Step 4 — Implement Deterministic Curated YAML Import

Reuse the existing YAML loader:

```text
apps.providers.service_discovery_loaders.load_service_discovery_providers
```

Do not duplicate YAML parsing.

Implement a transactional import service and a management command, recommended name:

```text
python manage.py import_service_discovery_providers
```

Expected command path:

```text
backend/apps/providers/management/commands/import_service_discovery_providers.py
```

Create the Django management package files if needed.

## Import semantics

Treat each harmonized YAML record as a complete current snapshot for that provider.

For each provider record:

- upsert Provider using external `provider_id`;
- map YAML `display_name` -> `provider_name`;
- map `country`;
- set imported current curated providers to `active`;
- preserve `publication_metadata` exactly;
- replace/synchronize current ProviderCertification rows for that provider and assign `sequence_index` from YAML order;
- upsert Offering rows by external `offering_id`;
- validate each offering's YAML `provider_id` matches the enclosing provider external ID;
- map YAML `name` -> `offering_name`;
- preserve service_category, part_family, support_status, supported_part_types, family_capabilities, part_type_capabilities, and generic_capabilities without semantic mutation;
- assign `sequence_index` from YAML offering order;
- set imported offerings `is_active=True`;
- remove stale Offering rows for that imported provider that are absent from the current full snapshot;
- do not delete providers that are absent from the input batch/directory;
- do not silently copy unknown YAML keys into controlled DB fields.

For M7.2 bootstrap migration, do NOT fabricate `ProviderPublication` or `CatalogueSyncEvent` rows. Existing curated YAML is a migration/bootstrap source, not a new external provider submission. Publication/version records will be created by the actual provider lifecycle write flow in M7.4.

## Transaction behavior

Prefer all-or-nothing transaction behavior for an import batch. If any provider record is invalid or cannot be persisted, no partial batch should remain.

At minimum validate structural assumptions before mutation:

- root record is a mapping;
- provider block exists and contains provider_id/display_name/country;
- offerings is a list;
- offering_id is present;
- offering provider_id matches enclosing provider_id;
- certifications is a list when present;
- duplicate provider IDs/offering IDs in one import batch are rejected clearly.

Do not duplicate the full harmonized ontology validation layer. The current curated YAML is already covered by existing H1-H9 serializer/migration tests. Repository import validation should focus on persistence safety and canonical shape integrity.

## Idempotency

Running the same import twice must:

- not create duplicate Providers;
- not create duplicate Offerings;
- not create duplicate certifications;
- reconstruct the same canonical output;
- leave stable row counts/current state.

---

# Step 5 — Exact YAML ↔ DB Canonical Parity Tests

Add focused tests, recommended files:

```text
backend/tests/test_service_discovery_db_repository.py
backend/tests/test_import_service_discovery_providers_command.py
```

Adapt names only if the repository has a stronger convention.

Tests must cover at least:

1. Import all current harmonized curated provider files.
2. DB canonical records exactly equal the YAML loader records after import, including ordering, explicit nulls, nested evidence fields, available-grade order, and `publication_metadata`.
3. Provider record ordering from DB is deterministic and matches the existing loader's provider-id/file-name behavior for current data.
4. Certification order is preserved.
5. Offering order is preserved.
6. Nested list order inside JSON capabilities is preserved.
7. Import is idempotent.
8. Reimport of a changed full provider snapshot removes stale offerings/certifications for that provider only.
9. Import failure rolls back the whole batch.
10. Cross-provider/offering identifier mismatch is rejected.
11. Duplicate IDs in one input batch are rejected.
12. Draft/suspended/archived providers are not returned by the default active catalogue loader.
13. Inactive offerings are not returned by the default active catalogue loader.
14. Internal/custom DB fields do not leak into canonical H1-H9 records.

Use real current curated YAML in parity tests where appropriate rather than constructing only toy fixtures.

---

# Step 6 — RDF and Matching Parity

The existing architecture already supports dependency injection of provider records:

```text
build_service_discovery_graph(provider_records=...)
search_service_discovery_catalog(..., provider_records=...)
```

Use this to prove DB-backed canonical records are semantically interchangeable with YAML records without changing runtime source selection.

Add tests that:

## RDF parity

- build one graph from current YAML loader records;
- build one graph from DB canonical records after import;
- assert RDF graph isomorphism / triple equivalence;
- preserve sequence-index-sensitive evidence behavior.

## Local matcher parity

For representative existing H1-H9 requests covering current providers/part families:

- run local matcher with YAML records;
- run local matcher with DB records;
- assert exact result equality.

Reuse current serializer/normalizer request fixtures where practical. Do not create a second matching engine.

This is the key M7.2 acceptance proof.

---

# Step 7 — Management Command Safety

The import command should provide a concise non-secret summary, for example:

```text
providers imported/updated
offerings synchronized
certifications synchronized
```

Do not print entire provider payloads, evidence blobs, credentials, or database URLs.

If a useful `--dry-run` can be implemented cleanly without broad scope expansion, it is welcome but not mandatory. Idempotency and transactional safety are mandatory.

---

# Step 8 — Do NOT Switch Runtime Source Yet

M7.2 must not change the default runtime service-discovery loader.

These should remain untouched in behavior:

```text
apps.providers.service_discovery_loaders.load_service_discovery_providers
H1-H9 runtime fallback order
RDF/Fuseki production search behavior
public response adapters
```

DB-backed records are verified through explicit repository/adapter calls and injected test paths only.

Do not add a runtime flag that silently changes production source selection in M7.2.

---

# Step 9 — Managed PostgreSQL Gate Sequencing

The M7.1 report correctly notes that actual hosted PostgreSQL connectivity/migration remains unverified.

For this task, do NOT provision Neon/AWS, change Vercel, or require a remote database. M7.2 is intentionally completing the local/provider-neutral repository + semantic parity layer first.

After M7.2 passes, the next operational gate will run the actual migrations/import/parity smoke checks against a managed PostgreSQL instance before M7.3 provider read/validation APIs are implemented.

This keeps vendor-specific infrastructure out of application code and avoids making a remote pilot database a prerequisite for repository design.

---

# Step 10 — Verification

From backend root run at minimum:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
```

Run all new M7.2 focused tests.

Then run the full suite:

```powershell
python manage.py test -v 2
```

Then run the same separately maintained focused H1-H9 set recorded in the M7.1 report.

Acceptance:

```text
M7.2 focused tests PASS
full suite PASS
focused H1-H9 PASS
no new skips introduced
```

Existing optional remote Fuseki skips may remain.

Do not weaken or remove newer working tests to satisfy stale assumptions.

---

# Step 11 — Public API / Safety Non-Regression

Confirm:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

remain unchanged.

Confirm:

```text
MDC_PROVIDER_PUBLICATION_ENABLED=False
```

remains production default.

Do not add provider lifecycle routes in M7.2.

Do not add `/api/v1/...`.

---

# Step 12 — M7.2 Report

Create:

```text
mdc-catalog/docs/Phase_2/12_mdc_v1_m72_harmonized_db_repository_migration_report.md
```

Include:

1. status;
2. M7.1 review/parity schema adjustment;
3. migration generated;
4. DB repository/adapter API;
5. exact YAML->model mapping;
6. ordering/evidence fidelity behavior;
7. import transaction/idempotency semantics;
8. management command usage;
9. current curated providers imported in tests;
10. exact YAML↔DB parity result;
11. RDF graph parity result;
12. local matcher parity result;
13. focused M7.2 test count/result;
14. full suite count/result;
15. focused H1-H9 count/result;
16. public API/safety non-regression;
17. files changed;
18. known limitations/non-goals;
19. Git commit hash/message(s);
20. readiness for managed PostgreSQL validation gate.

If all M7.2 local gates pass, end exactly with:

```text
READY_FOR_M72_MANAGED_POSTGRES_VALIDATION_GATE
```

Otherwise:

```text
NOT_READY_FOR_M72_MANAGED_POSTGRES_VALIDATION_GATE
```

and state the blocker.

---

# Step 13 — Git Handling

After successful verification:

1. inspect `git status` and diff;
2. commit implementation/tests/migrations;
3. commit report (same or separate clean commit is acceptable);
4. push to `origin/main`;
5. no force push;
6. never commit credentials, `.env`, database files, `.vercel/`, or generated runtime artefacts.

Suggested implementation commit:

```text
feat: add M7.2 harmonized DB repository and import
```

Suggested report commit:

```text
docs: report M7.2 repository parity verification
```

---

# Scope Restrictions

Do NOT in M7.2:

- provision Neon;
- provision AWS database infrastructure;
- change Vercel configuration;
- deploy Preview/Production;
- change the default runtime provider loader to DB;
- change H1-H9 matching semantics;
- redesign RDF mappings;
- implement provider validation API;
- implement provider registration/write API;
- implement provider PATCH/update API;
- expose PostgreSQL-backed provider/offering read APIs;
- create provider publication/outbox events for bootstrap import;
- implement Fuseki synchronization processing;
- enable provider publication;
- update partner API documentation;
- start M7.3.

---

# Final Console Response

Return only:

1. git/worktree synchronization status
2. parity schema adjustment + migration status
3. DB repository/adapter implementation status
4. YAML import service/command status
5. current curated provider import summary
6. exact YAML↔DB canonical parity result
7. ordering/evidence fidelity result
8. idempotency/rollback result
9. RDF graph parity result
10. local matcher parity result
11. focused M7.2 test result/count
12. full suite result/count
13. focused H1-H9 result/count
14. canonical public API non-regression status
15. provider-publication production-default status
16. report path/status
17. Git commit hash/message(s)
18. `READY_FOR_M72_MANAGED_POSTGRES_VALIDATION_GATE` or `NOT_READY_FOR_M72_MANAGED_POSTGRES_VALIDATION_GATE`

Do not start managed PostgreSQL provisioning/validation or M7.3 automatically.
