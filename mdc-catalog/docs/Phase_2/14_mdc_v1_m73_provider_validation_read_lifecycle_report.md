# M7.3 Provider Validation and DB-Backed Read Lifecycle Report

**Date:** 2026-09-09

**Scope:** M7.3 only

**Result:** PASS

## Outcome

M7.3 adds a non-mutating provider-publication validation preview and Django ORM-backed provider lifecycle reads. It does not add provider or offering writes, change the live service-discovery source, start an outbox processor, or begin M7.4.

The implemented routes are:

```text
POST /api/provider-publication/validation
GET  /api/providers/{provider_id}
GET  /api/providers/{provider_id}/offerings
GET  /api/offerings/{offering_id}
```

No `/api/v1/...` route was introduced.

## Validation endpoint

`POST /api/provider-publication/validation` reuses `ServiceDiscoveryPublicationSerializer` and `normalize_service_discovery_publication()`. It does not define a competing publication schema.

- A valid harmonized payload returns HTTP 200 with `contract_version: "1.0"`, `valid: true`, a deterministic normalized preview, and an empty warnings list.
- An omitted contract version defaults to `1.0`; explicit `1.0` is accepted.
- An unsupported version returns HTTP 400 through the existing public contract-version error style.
- Invalid vocabulary, taxonomy relationships, evidence metadata, provider identifiers, externally owned offering identifiers, and forbidden route fields return HTTP 400 with JSON-safe structured details.
- `MDC_PROVIDER_VALIDATION_ENABLED` controls exposure. It defaults to `False` in base and production settings and is documented in `.env.example` as an interim exposure control rather than authentication or authorization. Disabled requests return a safe HTTP 403 `provider_validation_disabled` error.

The response omits internal UUIDs, database metadata, stack traces, filesystem paths, backend identifiers, SQL, and secrets.

## Non-mutation proof

Focused tests compare complete primary-key identity sets before and after both valid and invalid validation requests for:

- `Provider`
- `Offering`
- `ProviderCertification`
- `ProviderPublication`
- `CatalogueSyncEvent`

All five sets remain identical. Separate side-effect guards prove that validation does not call the YAML writer, RDF generator, or Fuseki retrieval/update path. It creates no files, publications, or sync events.

The populated managed PostgreSQL catalogue was also smoke-tested with read-only lifecycle requests and a validation preview. Counts remained exactly 3 providers, 4 offerings, 5 certifications, 0 publications, and 0 sync events.

## DB-backed lifecycle reads

A dedicated `provider_lifecycle_repository.py` boundary uses Django ORM only and stays separate from the active-only service-discovery repository.

`GET /api/providers/{provider_id}` resolves the stable external provider ID across all lifecycle states. It returns provider identity/name/country/status, safe provider custom fields and publication metadata, ordered certification evidence, and deterministic offering summaries. Certifications use `(sequence_index, code)` ordering; offerings use `(sequence_index, offering_id)` ordering.

`GET /api/providers/{provider_id}/offerings` returns all persisted offerings, including inactive records, in the same deterministic offering order. Nested part-type, family, generic, custom-offering, and custom-capability JSON structures round-trip without flattening. A known provider with no offerings returns HTTP 200 and an empty list.

`GET /api/offerings/{offering_id}` resolves the stable MDC-owned offering ID and returns the external provider ID, harmonized lifecycle fields, active/support state, nested capabilities, and safe custom fields.

Unknown providers and offerings return safe HTTP 404 responses with stable `provider_not_found` and `offering_not_found` codes. Lifecycle responses do not expose internal UUIDs, timestamps, sequence fields, publication snapshots, or sync/outbox state. Query-count tests bound provider detail, provider offering list, and offering detail to three, two, and one query respectively.

Read-only managed PostgreSQL smoke requests passed for a populated provider, its ordered offering list, and an offering detail. The same focused lifecycle suite passed against an isolated, randomly named temporary PostgreSQL test database, including ordering, JSON fidelity, inactive lifecycle visibility, safe errors, and non-mutation. The task-owned test database was removed after verification; the configured validation catalogue was neither reset nor dropped.

## Database and migrations

No schema change or migration was needed. `providers.0001_initial` and `providers.0002_canonical_parity_fields` remain the complete provider migration set. `makemigrations --check --dry-run` reports no changes.

The canonical environment loader remains unchanged and continues to give process/platform environment values precedence over the ignored local `.env`. No cloud-provider-specific application dependency was added.

## Verification

Local regression ran with a process-local SQLite override without editing the user's canonical `.env`.

| Gate | Total | Passed | Failed/errors | Existing skips | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Managed PostgreSQL focused M7.3 suite | 35 | 35 | 0 | 0 | PASS |
| Managed PostgreSQL populated-catalogue smoke | 4 requests | 4 | 0 | 0 | PASS |
| `manage.py check` | — | — | 0 | — | PASS |
| `makemigrations --check --dry-run` | — | — | 0 | — | No drift |
| Full local `manage.py test -v 2` | 479 | 466 | 0 | 13 | PASS |
| Separately maintained H1-H9 suite | 230 | 225 | 0 | 5 | PASS |
| Git whitespace checks | — | — | 0 | — | PASS |

The 13 full-suite skips remain the existing optional Fuseki integration guards. The H1-H9 set retains its five existing remote-alignment skips. M7.3 introduces no skip.

The focused M7.3 suites are:

```text
tests.test_provider_detail_api
tests.test_provider_publication_validation_api
tests.test_production_route_safety
```

## API and runtime non-regression

The canonical public discovery endpoints and their contract remain unchanged:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

YAML remains the live discovery runtime source. Existing RDF generation, local matching, Fuseki retrieval/fallback, and public response semantics are unchanged, as confirmed by the separately maintained H1-H9 suite. PostgreSQL lifecycle reads do not feed discovery in this slice.

`POST /api/catalog/search` remains legacy. `POST /api/provider-publication` retains its file-backed behavior and remains disabled by default in production. PATCH/PUT/DELETE lifecycle endpoints and provider-offering creation routes were not added. No Fuseki synchronization or outbox processor was started, no Vercel deployment was performed, and partner API documentation was not expanded with lifecycle endpoints.

## Files changed

Paths are relative to `mdc-catalog/`:

- `.env.example`
- `backend/apps/api/urls.py`
- `backend/apps/api/views/__init__.py`
- `backend/apps/api/views/get_views.py`
- `backend/apps/api/views/post_views.py`
- `backend/apps/providers/provider_lifecycle_repository.py`
- `backend/config/settings.py`
- `backend/config/settings_production.py`
- `backend/tests/test_database_configuration.py`
- `backend/tests/test_production_route_safety.py`
- `backend/tests/test_provider_detail_api.py`
- `backend/tests/test_provider_publication_api.py`
- `backend/tests/test_provider_publication_validation_api.py`
- `backend/tests/test_public_api_contract.py`
- `docs/Phase_2/14_mdc_v1_m73_provider_validation_read_lifecycle_report.md`

The legacy publication tests now enable their own publication flag explicitly, so their file-write contract is isolated from the canonical local environment. The stale seed-backed provider-detail test was replaced by database-backed lifecycle contract coverage, and route-presence checks now resolve database-backed routes without querying from a `SimpleTestCase`.

No `.env`, `.env.local`, database artifact, temporary helper, generated RDF, or credential-bearing output is included.

## Git

Implementation commit: `9b0feec` — `feat: add M7.3 provider validation and DB-backed reads`.

This report is committed separately as `docs: report M7.3 provider validation and read lifecycle`. Its final hash and normal push synchronization are reported after the commit, avoiding a self-referential hash in this document.

## Known limitations

The lifecycle routes are intended for internal/trusted use, but M7.3 does not introduce authentication or authorization. The validation feature flag is only an exposure switch. Deployment must therefore keep these routes within the intended trusted boundary until a separate security lifecycle is implemented.

This slice provides validation and reads only. It does not create or update providers or offerings, persist publication previews, process outbox events, synchronize Fuseki, switch discovery to PostgreSQL, add pagination, or establish production load/concurrency guarantees. Remote Fuseki integration remains guarded by the existing optional test configuration.

All M7.3 gates passed. M7.4 has not started.

READY_FOR_M74_PROVIDER_REGISTRATION_UPDATE_LIFECYCLE
