# Codex Prompt — M7.3 Provider Validation and DB-Backed Read Lifecycle

**Label:** `[mdc_m73_provider_validation_read_lifecycle]`  
**Recommended model:** GPT-5.6 Sol  
**Reasoning:** Medium. Use High only for a concrete blocker.

## Objective

Implement **M7.3 only** for the MaaSAI MDC backend:

1. a **non-mutating provider-publication validation endpoint** using the existing harmonized H1-H9 publication serializer/normalizer; and
2. **PostgreSQL-backed provider/offering read lifecycle endpoints** for internal/trusted use.

Do **not** start M7.4. Do not enable provider publication writes. Do not switch service-discovery runtime from YAML/Fuseki to PostgreSQL.

The M7.2 managed PostgreSQL gate passed and is the prerequisite for this task. The accepted gate marker is:

```text
READY_FOR_M73_PROVIDER_VALIDATION_READ_LIFECYCLE
```

The starting validation report is:

```text
mdc-catalog/docs/Phase_2/13_mdc_v1_m72_managed_postgres_validation_report.md
```

The accepted M7 architecture plan is:

```text
mdc-catalog/docs/Phase_2/10_mdc_v1_m7_persistence_provider_lifecycle_plan.md
```

The infrastructure portability decision remains binding:

```text
mdc-catalog/docs/Phase_2/10a_mdc_v1_infrastructure_portability_decision.md
```

## Hard invariants

Preserve all of the following:

- Public discovery endpoints remain exactly:
  - `GET /api/health`
  - `GET /api/catalog/filters`
  - `POST /api/service-discovery/search`
- Never introduce `/api/v1/...` routes.
- API evolution uses `contract_version`, current value `"1.0"`.
- `POST /api/catalog/search` remains legacy only.
- `POST /api/provider-publication` remains disabled in production and must not be converted to a DB write in M7.3.
- H1-H9 search/matching behavior is unchanged.
- YAML remains the live service-discovery runtime source in this slice.
- RDF/Fuseki behavior remains unchanged.
- PostgreSQL is the operational persistence target, accessed through Django ORM and standard PostgreSQL configuration only.
- No Neon-specific, Vercel-specific, or AWS-specific application dependency.
- Secrets remain only in environment/secrets. Never print, log, report, stage, or commit `DATABASE_URL` or credentials.
- Preserve the project convention: **GET views in `views/get_views.py`; POST views in `views/post_views.py`.**
- Latest working implementation/code/data is authoritative over stale legacy tests/docs; update stale tests only when they conflict with the accepted current architecture, never roll back working harmonized behavior to satisfy old expectations.

## Preflight

1. Work from repo root `C:\Users\Elahi\Desktop\mdc_v1`.
2. Fetch/synchronize with `origin/main` safely.
3. Preserve all untracked local helpers and the ignored `mdc-catalog/.env`.
4. Confirm the M7.2 report exists and ends with `READY_FOR_M73_PROVIDER_VALIDATION_READ_LIFECYCLE`.
5. Confirm current migrations `providers.0001_initial` and `providers.0002_canonical_parity_fields` are present with no drift.
6. Confirm the canonical `.env` loader still uses platform/environment precedence over local `.env`.
7. Do not expose any secret value in console summaries or reports.

## Current implementation to reuse, not duplicate

Inspect and reuse the current harmonized code, especially:

```text
backend/apps/api/service_discovery_publication_serializers.py
backend/apps/providers/service_discovery_publication.py
backend/apps/providers/service_discovery_db_repository.py
backend/apps/providers/models.py
backend/apps/api/public_contract.py
backend/apps/api/views/get_views.py
backend/apps/api/views/post_views.py
backend/apps/api/views/__init__.py
backend/apps/api/urls.py
```

The validation path must reuse `ServiceDiscoveryPublicationSerializer` and `normalize_service_discovery_publication()` unless a small shared refactor is required. Do not create a second publication schema or a competing validator.

The DB read path should use a dedicated provider-lifecycle repository/service boundary rather than importing legacy seed/YAML read services into the new views.

## M7.3 endpoint scope

Implement exactly these lifecycle endpoints for this slice:

```text
POST /api/provider-publication/validation
GET  /api/providers/{provider_id}
GET  /api/providers/{provider_id}/offerings
GET  /api/offerings/{offering_id}
```

Do not add PATCH/PUT/DELETE. Do not add provider registration or offering creation. Do not change `POST /api/provider-publication` write behavior except where a small routing/refactor is required to keep it safely disabled.

### 1. POST /api/provider-publication/validation

Purpose:

- validate provider publication payloads;
- validate controlled vocabularies/taxonomy and evidence metadata;
- reject forbidden route fields;
- reject externally owned identifiers;
- normalize with the existing harmonized normalizer;
- return validation errors/warnings/normalized preview;
- **never persist provider, offering, certification, publication, or sync-event state**.

Contract handling:

- accept optional `contract_version`;
- omitted version defaults safely to current `1.0`;
- explicit unsupported version returns HTTP 400 with the existing public contract-version error style;
- response includes `contract_version: "1.0"`.

Safety/exposure:

- introduce a separate feature flag such as `MDC_PROVIDER_VALIDATION_ENABLED`;
- default it to **False** for safe environments/production;
- document it in `.env.example` without any secret;
- tests may override it explicitly;
- when disabled, return a safe 403 error such as `provider_validation_disabled`;
- this feature flag is only an interim exposure control and must not be described as authentication/authorization.

Successful response should be deterministic and API-friendly. Prefer an already established validation response shape if one exists in current tests/docs. Otherwise use a small lifecycle DTO containing at least:

```text
contract_version
valid
message
warnings
normalized_payload
```

Do not return internal UUIDs, database metadata, stack traces, filesystem paths, backend names, raw SQL, or secrets.

Invalid payloads should return HTTP 400 with structured, JSON-safe validation details and no persistence.

### 2. GET /api/providers/{provider_id}

Replace the legacy seed-backed implementation at this route with a PostgreSQL/Django-ORM-backed provider-lifecycle read.

Requirements:

- stable lookup by external `provider_id`;
- return `contract_version: "1.0"`;
- return lifecycle/provider fields needed for future provider-management UI;
- preserve harmonized certification ordering/evidence fidelity;
- include offering summaries in deterministic publication/sequence order;
- include lifecycle `status` if useful for management;
- preserve provider-owned custom fields if they are part of the persisted model and safe for trusted lifecycle retrieval;
- never expose internal UUID primary keys;
- never expose `ProviderPublication` snapshots, sync/outbox internals, raw database metadata, or credentials;
- provider not found -> safe HTTP 404 with stable error code.

Do not make this endpoint part of partner documentation yet.

### 3. GET /api/providers/{provider_id}/offerings

Add a PostgreSQL-backed list endpoint for the selected provider.

Requirements:

- stable provider lookup;
- deterministic offering order using persisted `sequence_index` and stable tie-break behavior;
- lifecycle representation should preserve current controlled capability structures and provider-owned custom offering/capability fields when safe;
- include `contract_version: "1.0"`;
- no internal UUIDs/audit/outbox fields;
- unknown provider -> safe 404;
- a known provider with zero offerings -> HTTP 200 with an empty list, not 404.

### 4. GET /api/offerings/{offering_id}

Replace the legacy seed-backed implementation with PostgreSQL-backed lookup.

Requirements:

- stable lookup by MDC-owned `offering_id`;
- include provider external ID and harmonized lifecycle fields;
- preserve nested JSON capability fidelity and ordering;
- include `is_active`/lifecycle state if useful for trusted edit UI;
- include provider-owned custom offering/capability fields when safe;
- no internal UUIDs;
- unknown offering -> safe 404.

## Repository/service design

Create a focused provider-lifecycle read repository/service if needed. It should:

- use Django ORM only;
- avoid N+1 reads where practical (`select_related`/`prefetch_related`);
- preserve sequence/order fields introduced in M7.2;
- not reuse the service-discovery repository's active-only assumptions if doing so would hide legitimate lifecycle states such as draft/inactive records;
- keep provider-management reads conceptually separate from service-discovery runtime reads;
- contain no cloud-provider-specific logic.

Do not over-normalize the schema in M7.3. A new migration should not be necessary unless a concrete requirement cannot be met with the accepted M7.1/M7.2 schema. If a migration appears necessary, stop and justify it before proceeding rather than silently expanding scope.

## View/routing cleanup

Follow the accepted view convention:

- all new/updated GET lifecycle views in `backend/apps/api/views/get_views.py`;
- validation POST in `backend/apps/api/views/post_views.py`;
- update `views/__init__.py` exports deliberately;
- keep only genuinely legacy views dynamically sourced from `backend/apps/api/views.py`;
- route the M7.3 endpoints from `backend/apps/api/urls.py`.

Do not rewrite unrelated legacy `catalog_search` in this slice.

## Validation endpoint non-mutation proof

Tests must explicitly prove that `POST /api/provider-publication/validation` does not mutate any of:

```text
Provider
Offering
ProviderCertification
ProviderPublication
CatalogueSyncEvent
```

For both valid and invalid requests, compare row counts/identity sets before and after where useful.

The endpoint must not write YAML files, generate RDF files, call Fuseki update endpoints, or create outbox events.

## Required tests

Add focused M7.3 tests covering at minimum:

### Validation contract

- valid harmonized provider payload -> 200;
- normalized result is deterministic;
- omitted contract version -> current 1.0;
- explicit `1.0` -> accepted;
- unsupported explicit version -> 400;
- feature disabled -> 403;
- invalid controlled vocabulary -> 400;
- invalid service-category/part-family/part-type relation -> 400;
- forbidden route/operation field -> 400;
- externally owned identifier such as `offering_id` -> 400;
- provider ID format rejection -> 400;
- evidence metadata validation preserved;
- valid/invalid requests are non-mutating across all five persistence models;
- safe error body contains no stack trace/path/credentials.

### Provider read

- existing DB provider detail -> 200;
- unknown provider -> 404;
- certification ordering/evidence fidelity preserved;
- offering summaries deterministic;
- no internal UUID fields;
- custom provider fields round-trip if included by lifecycle contract.

### Provider offering list

- existing provider -> deterministic ordered list;
- zero-offering provider -> 200 empty list;
- unknown provider -> 404;
- custom offering/capability fields round-trip if included.

### Offering detail

- existing offering -> 200;
- unknown offering -> 404;
- provider external ID and harmonized nested capabilities preserved;
- no internal UUID fields.

### Routing/non-regression

- no `/api/v1/...` route introduced;
- canonical discovery endpoints unchanged;
- `POST /api/provider-publication` remains production-disabled;
- M7.3 adds no write/update endpoint.

## PostgreSQL verification

The canonical ignored `mdc-catalog/.env` contains the managed validation `DATABASE_URL`. Use it without printing it.

1. Run focused M7.3 tests against PostgreSQL using an isolated temporary test database where feasible.
2. Do not use the populated `mdc_validation` catalogue database as a destructive test database.
3. If you smoke-test the populated validation catalogue, use read-only lifecycle requests plus the non-mutating validation endpoint and prove counts remain unchanged.
4. Clean up only task-owned temporary databases. Never drop or reset the configured validation database.
5. Never print host/user/password/URL.

## Regression gates

After PostgreSQL-focused verification, return the local process to the normal SQLite/default regression mode without editing or removing the user's `.env` secret.

Run at minimum:

```text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test -v 2
```

Then run the same separately maintained H1-H9 focused set used in the M7.2 reports.

M7.2 baselines before M7.3 additions were:

```text
Full local suite: 443 passed, 13 existing skips
Focused H1-H9:    225 passed, 5 existing skips
```

The total test count may increase because of new M7.3 tests, but there must be no new unexplained failures, errors, or skips. Do not weaken, delete, or bypass existing H1-H9 tests.

## Public/runtime non-regression checks

Prove and report that:

- `GET /api/health` unchanged;
- `GET /api/catalog/filters` unchanged;
- `POST /api/service-discovery/search` unchanged;
- `/api/v1/...` still 404;
- YAML remains live discovery runtime source;
- existing RDF generation/matcher semantics unchanged;
- provider publication write remains disabled by default in production;
- no provider PATCH/POST-offering write endpoint exists yet;
- no Fuseki synchronization/outbox processor was started;
- no Vercel deployment was performed;
- no partner API documentation was expanded to lifecycle endpoints.

## Documentation

Create:

```text
mdc-catalog/docs/Phase_2/14_mdc_v1_m73_provider_validation_read_lifecycle_report.md
```

The report must record:

- exact endpoint behavior implemented;
- feature-flag behavior;
- files changed;
- whether any migration was needed (expected: no);
- PostgreSQL-focused test totals;
- validation non-mutation proof;
- DB-backed read parity/order evidence;
- full local regression totals;
- H1-H9 totals;
- API/runtime non-regression;
- known limitations;
- Git commit(s);
- no secrets or connection identifiers.

## Git

Keep changes focused. Commit implementation/tests and report with clear messages. Push normally after successful gates. Do not commit `.env`, `.env.local`, temporary helper files, database artifacts, or credential-bearing output.

Suggested implementation commit message:

```text
feat: add M7.3 provider validation and DB-backed reads
```

Suggested report commit message:

```text
docs: report M7.3 provider validation and read lifecycle
```

## Stop condition

If all M7.3 gates pass, end with exactly:

```text
READY_FOR_M74_PROVIDER_REGISTRATION_UPDATE_LIFECYCLE
```

If any required gate fails, end with:

```text
NOT_READY_FOR_M74_PROVIDER_REGISTRATION_UPDATE_LIFECYCLE
```

and explain the blocker safely.

**Do not start M7.4 automatically.**