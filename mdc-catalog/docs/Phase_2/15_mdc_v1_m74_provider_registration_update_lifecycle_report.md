# M7.4 Provider Registration and Update Lifecycle Report

**Date:** 2026-09-09

**Scope:** M7.4 only

**Result:** PASS

## Outcome

M7.4 replaces the canonical file-backed provider publication write with a transactional Django ORM lifecycle and enables controlled provider/offering updates. Every successful write creates durable publication history and pending catalogue sync evidence in the same database transaction.

The implemented write routes are:

```text
POST  /api/provider-publication
PATCH /api/providers/{provider_id}
POST  /api/providers/{provider_id}/offerings
PATCH /api/offerings/{offering_id}
```

The M7.3 validation and read contracts remain on their existing URLs. No `/api/v1/...` route was added.

## Exposure and contract behavior

All four lifecycle writes use `MDC_PROVIDER_PUBLICATION_ENABLED`. Base/local configuration can opt in deliberately; production continues to default to `False`. A disabled request returns HTTP 403 with `provider_publication_disabled` before validation or database access and creates no catalogue row, publication record, or sync event. This flag is an exposure control and is not authentication or authorization.

Omitted `contract_version` defaults to `1.0`, explicit `1.0` is accepted, and unsupported versions return the existing safe HTTP 400 contract-version error. Successful responses contain the contract version, accepted status, create/update operation, external provider ID, MDC-owned publication ID, `sync_pending` publication state, pending sync state, and affected offering IDs. Offering-specific responses also identify the affected offering.

Errors use stable HTTP semantics: 400 for invalid input, 403 for disabled writes, 404 for an unknown provider/offering, 409 for confirmed duplicate identities, and a redacted 503 for other persistence failures. Responses do not expose SQL, stack traces, filesystem paths, connection data, or internal provider/offering/event UUIDs.

## Registration semantics

`POST /api/provider-publication` now accepts the harmonized `ServiceDiscoveryPublicationSerializer` contract and calls `normalize_service_discovery_publication()`. The legacy seed serializer/writer is no longer on the canonical route.

A registration creates a new active Provider. It is not an upsert: an existing or concurrently inserted provider ID returns HTTP 409 `provider_already_exists` without overwriting data. Offering IDs remain MDC-owned and deterministic as `{provider_id}_{service_category}`.

One `transaction.atomic()` boundary creates:

1. the Provider;
2. ProviderCertification rows with submitted `sequence_index` order;
3. Offering rows with submitted `sequence_index` order;
4. one `ProviderPublication` with operation `create` and status `sync_pending`;
5. one pending provider upsert event and one pending offering upsert event per offering.

The publication records the safe submitted payload, complete post-write provider snapshot, contract version, validation/persistence timestamps, and a null completion timestamp. An injected failure during event creation rolls back the provider, certifications, offerings, publication, and events together.

## Provider PATCH semantics

`PATCH /api/providers/{provider_id}` permits only:

```text
provider_name
country
status
certifications
publication_metadata
custom_provider_fields
```

Omitted values remain unchanged. Supplied scalars and JSON objects replace their fields. A supplied certification list replaces the full certification set and receives new deterministic sequence indexes; omitted certifications remain unchanged. `provider_id`, embedded offerings, and unsupported fields are rejected rather than ignored.

The transaction locks the Provider with `select_for_update()`, applies only validated fields, creates one update publication containing the submitted patch and complete resulting provider/offering state, and creates one pending provider upsert event. Unknown providers return `provider_not_found` without mutation. Injected publication/event failures roll the entity update back.

## Offering create and PATCH semantics

`POST /api/providers/{provider_id}/offerings` takes provider identity only from the path. Body-supplied provider/offering IDs are rejected. It validates the complete offering with the existing harmonized taxonomy, capability, and evidence rules, locks the Provider, generates the deterministic offering ID, and assigns `sequence_index` after the current maximum (or zero for the first offering). Duplicate generated identity returns HTTP 409 `offering_already_exists` without overwrite.

The offering-create transaction creates one update publication with the complete post-write provider state and one pending offering upsert event. It does not create a provider event because no provider row or provider certification representation changes; the offering event carries the durable external offering identity and the persisted offering retains its provider identity.

`PATCH /api/offerings/{offering_id}` permits:

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

Each supplied JSON/list field replaces that field as a whole. The service locks the Offering and Provider, combines the patch with persisted values, revalidates the complete resulting offering through the harmonized rules, and preserves `offering_id`, `provider_id`, `service_category`, `part_family`, and `sequence_index`. A successful patch creates one update publication and one pending offering upsert event. Unknown offerings return `offering_not_found` without mutation.

## Flexible staging data and safety

The full publication contract now deliberately accepts `custom_provider_fields`; offering contracts accept `custom_offering_fields` and `custom_capability_fields`. These fields must be JSON objects, round-trip through PostgreSQL JSONB, and remain separate from controlled search capability fields. They are not promoted into controlled vocabularies.

Recursive checks reject route/operation keys even inside custom structures. JSON checks reject NaN, Infinity, NUL-containing strings/keys, non-string object keys, non-JSON types, and credential-bearing keys before persistence. Full registration also rejects unsupported top-level/offering keys and duplicate certification codes rather than silently ignoring them.

## Publication history and failed writes

Every successful M7.4 write creates exactly one `ProviderPublication` with operation `create` or `update`, status `sync_pending`, the safe submitted request body, a complete deterministic post-write snapshot, and validation/persistence timestamps. `completed_at` remains null until a later synchronization milestone.

Feature-disabled and validation-failed requests create no audit/history rows or events. Recording rejected payloads is deferred to M7.6: without authentication and a defined retention/redaction policy, persisting arbitrary invalid submissions would expand sensitive-data and abuse exposure. This choice keeps failed validation strictly non-mutating while preserving mandatory history for every accepted write.

## Outbox behavior and schema

`CatalogueSyncEvent.entity_id` already existed in `providers.0001_initial` with sufficient length for both provider and offering external IDs, so no M7.4 migration was needed. Managed PostgreSQL inspection confirmed the column physically exists. All new events use `upsert`, start as `pending`, have zero attempts, and remain unprocessed.

Event counts are:

| Successful operation | Provider events | Offering events |
| --- | ---: | ---: |
| Provider registration with N offerings | 1 | N |
| Provider PATCH | 1 | 0 |
| Offering create | 0 | 1 |
| Offering PATCH | 0 | 1 |

No certification event type was added; provider events own certification representation.

## Verification

Managed PostgreSQL verification used a fresh randomly named task-owned test database. The configured catalogue database was not modified or reset. The harness confirmed `connection.vendor == "postgresql"`, verified the physical `entity_id` column, applied the existing migrations, ran the focused persistence/API suites, and force-removed only the task database afterward.

| Gate | Total | Passed | Failed/errors | Existing skips | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Managed PostgreSQL M7.4 persistence/API set | 71 | 71 | 0 | 0 | PASS |
| `manage.py check` | — | — | 0 | — | PASS |
| `makemigrations --check --dry-run` | — | — | 0 | — | No drift |
| Full local suite | 499 | 486 | 0 | 13 | PASS |
| Separately maintained H1-H9 suite | 230 | 225 | 0 | 5 | PASS |
| Git whitespace/secret-scope checks | — | — | 0 | — | PASS |

The 13 full-suite skips and five focused H1-H9 skips remain the existing optional remote Fuseki guards. M7.4 adds no skip.

Tests cover atomic commit and rollback, real PostgreSQL constraints/JSONB/UUID behavior, explicit row-lock calls, deterministic ordering, immutable fields, duplicate prechecks and database-race translation, feature-disabled non-mutation, validation-failed non-mutation, complete publication snapshots, exact pending event counts, custom-field isolation, safe error responses, and unchanged read/validation routes.

## Canonical publication and runtime non-regression

Tests patch the legacy YAML writer, RDF generator, Fuseki access, and discovery-runtime entry point and prove no M7.4 write calls them. The canonical publication route creates no provider file and performs no RDF/Fuseki synchronization.

YAML remains the live discovery runtime source. RDF generation, Fuseki retrieval/fallback, and H1-H9 matching semantics remain unchanged. The canonical public discovery endpoints remain:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

`POST /api/catalog/search` remains legacy/internal. `/api/v1/health`, `/api/v1/catalog/filters`, `/api/v1/service-discovery/search`, and versioned lifecycle-write variants remain 404. PUT/DELETE lifecycle routes were not added. No sync worker, retry job, runtime source switch, Vercel deployment, AWS configuration, authentication UI, or partner API documentation expansion was performed.

## Files changed

Paths are relative to `mdc-catalog/`:

- `backend/apps/api/provider_lifecycle_serializers.py`
- `backend/apps/api/service_discovery_publication_serializers.py`
- `backend/apps/api/views/__init__.py`
- `backend/apps/api/views/get_views.py`
- `backend/apps/api/views/post_views.py`
- `backend/apps/providers/provider_lifecycle_write_service.py`
- `backend/tests/test_production_route_safety.py`
- `backend/tests/test_provider_detail_api.py`
- `backend/tests/test_provider_lifecycle_write_api.py`
- `backend/tests/test_provider_publication_api.py`
- `backend/tests/test_provider_publication_validation_api.py`
- `backend/tests/test_public_api_contract.py`
- `docs/Phase_2/15_mdc_v1_m74_provider_registration_update_lifecycle_report.md`

No model, migration, dependency, runtime data, generated RDF, environment file, credential, database artifact, temporary helper, deployment configuration, or partner-facing API documentation changed.

## Git

Implementation commit: `6099c7d` — `feat: add M7.4 provider registration and update lifecycle`.

This report is committed separately as `docs: report M7.4 provider registration and update lifecycle`. Its final hash and push status are reported after commit to avoid a self-referential hash.

## Known limitations

M7.4 does not add authentication or authorization. Production writes therefore remain disabled by default, and enabling them is safe only behind an independently enforced trusted boundary.

Pending sync events are durable but unprocessed. M7.4 does not contact Fuseki, implement retries/workers, regenerate RDF, or switch discovery reads to PostgreSQL. Failed-attempt audit retention is deferred as described above. Load, rate-limit, actor-attribution, and broad concurrent-writer testing remain outside this milestone.

All M7.4 technical gates passed. M7.5 has not started.

READY_FOR_M75_RDF_FUSEKI_SYNCHRONIZATION
