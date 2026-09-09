# M7.1 PostgreSQL / Django Foundation Report

Date: 2026-09-09

## Status and synchronization

M7.1 local foundation is complete. All local acceptance gates pass, with the existing optional remote Fuseki integration skips retained. Ready for review of the separate Neon provisioning/connection gate; that gate has not started.

The initial worktree was clean on `main`. `git fetch origin` confirmed that HEAD and `origin/main` were both `7575727852b247aad85a6672b3e2fff716fab37b` (`docs: add M7.1 PostgreSQL Django foundation Codex prompt`), so no pull was needed. No unrelated changes were present or discarded.

All seven repository assumptions in Task 08 were confirmed: empty provider models, SQLite default, production settings inheriting that default, missing PostgreSQL dependencies, existing harmonized serializer/normalizer, file-backed legacy publication, and unchanged H1-H9 runtime. One organizational detail matters: public GET/POST handlers now live in `apps/api/views/get_views.py` and `post_views.py`; `views/__init__.py` loads retained legacy handlers from `views.py`. Both the current package and legacy implementation were inspected.

## Completed scope

Added five durable Django models, an initial generated migration, a testable PostgreSQL URL configuration helper, dependency declarations, an empty environment example entry, and 18 focused tests. Corrected one demonstrably stale demo test to the already-approved public filter contract. No API implementation was changed.

## Exact model definitions

All five models have `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` and useful string representations. `created_at` is `DateTimeField(auto_now_add=True)` everywhere. Provider, Offering, and ProviderCertification also have `updated_at = DateTimeField(auto_now=True)`.

`Char(N)` below means `CharField(max_length=N)`. Unless specified, fields are non-null and required, with no explicit default. All JSON defaults use callable `dict` or `list`, never shared mutable objects.

### Provider

| Field | Definition |
| --- | --- |
| provider_id | Char(255), unique; stable supplied external identity |
| provider_name | Char(255); not unique |
| country | Char(100) |
| status | Char(16), TextChoices: draft, active, suspended, archived; default draft |
| custom_provider_fields | JSONField(default=dict, blank=True) |

### Offering

| Field | Definition |
| --- | --- |
| offering_id | Char(512), unique; MDC-owned external identity |
| provider | FK Provider, CASCADE, related_name="offerings" |
| offering_name | Char(255) |
| service_category, part_family | Each Char(255), no ontology choices |
| support_status | Char(32), TextChoices: confirmed, candidate_requiring_confirmation, unknown; default unknown |
| supported_part_types | JSONField(default=list, blank=True) |
| family_capabilities, part_type_capabilities, generic_capabilities | Each JSONField(default=dict, blank=True) |
| custom_offering_fields, custom_capability_fields | Each JSONField(default=dict, blank=True) |
| is_active | BooleanField(default=True) |

There is no uniqueness constraint on `(provider, service_category)`. Multiple offerings per category are explicitly tested. External offering ID assignment remains the responsibility of a future application service; the model does not invent or accept IDs through a new API.

### ProviderCertification

| Field | Definition |
| --- | --- |
| provider | FK Provider, CASCADE, related_name="certifications" |
| code | Char(255), no ontology choices |
| source_type, confidence | Each Char(64), no duplicated evidence vocabulary choices |
| source_note | TextField(null=True, blank=True) |

Database constraint `unique_provider_certification` enforces uniqueness of `(provider, code)`.

### ProviderPublication

| Field | Definition |
| --- | --- |
| provider | FK Provider, SET_NULL, null/blank=True, related_name="publications" |
| provider_id_snapshot | Char(255) |
| operation | Char(16), TextChoices: create, update |
| status | Char(24), TextChoices: received, validation_failed, validated, persisted, sync_pending, synced, sync_failed, rejected; default received |
| contract_version | Char(32), default "1.0" |
| submitted_payload, normalized_payload, validation_errors | Each JSONField(default=dict) |
| submitted_by_external_id | Char(255), null/blank=True |
| validated_at, persisted_at, completed_at | Each DateTimeField(null=True, blank=True) |

Publications can precede provider resolution. Removing a provider preserves its publication payloads, external ID snapshot, and attached outbox events.

### CatalogueSyncEvent

| Field | Definition |
| --- | --- |
| publication | FK ProviderPublication, CASCADE, related_name="sync_events" |
| entity_type | Char(16), TextChoices: provider, offering |
| entity_id | Char(512) |
| operation | Char(16), TextChoices: upsert, delete |
| status | Char(16), TextChoices: pending, processing, succeeded, failed; default pending |
| attempt_count | PositiveIntegerField(default=0) |
| last_error | TextField(blank=True) |
| processed_at | DateTimeField(null=True, blank=True) |

Composite index `sync_status_created_idx` covers `(status, created_at)` for future status-filtered chronological processing. Beyond this, only Django's primary-key, unique-field/constraint, and FK indexes are introduced. No worker, lifecycle transition logic, ownership FK, or custom `save()` behavior is added.

## Migration

`backend/apps/providers/migrations/0001_initial.py` was generated by Django 5.2.13 using `manage.py makemigrations providers`. It creates all five models, relationships, uniqueness constraints, and the outbox index. Existing migration package files remain intact. No handwritten SQL or data migration was used.

The migration applied successfully to the temporary SQLite test database. `manage.py makemigrations --check --dry-run` reported `No changes detected`. No hosted database migration was attempted.

## Database configuration, dependencies, and environment example

`backend/config/database.py` exposes `database_config(base_dir, database_url=None)`. Base settings explicitly pass `os.getenv("DATABASE_URL")` to it; the helper itself does not read ambient environment values or open a connection.

- Missing, empty, or whitespace-only URL retains SQLite at `BASE_DIR / "db.sqlite3"`.
- PostgreSQL URLs are parsed using `dj-database-url`, with `CONN_MAX_AGE=0`.
- Hosted URL query options, including `sslmode`, are retained. No SSL mode or hostname is invented.
- Non-PostgreSQL and parser-invalid URLs raise a credential-free `ImproperlyConfigured` message with parser exception chaining suppressed.
- Production settings inherit the result and do not require a database URL.
- The helper does not print or log URLs or credentials; successful and failing parsing paths are tested.

Added `psycopg[binary]` and `dj-database-url` to `requirements/base.txt`, following the repository's existing unpinned dependency convention. Project-root `requirements.txt` includes this file, covering local and Vercel installs. Local verification used psycopg/psycopg-binary 3.3.5 and dj-database-url 3.1.2, with Django 5.2.13 and Python 3.11.

Configuration was checked against the [dj-database-url documentation](https://pypi.org/project/dj-database-url/) and [Psycopg installation documentation](https://www.psycopg.org/psycopg3/docs/basic/install.html).

`.env.example` now documents optional `DATABASE_URL=` with an empty value and comments about SQLite fallback, hosted query options, and connection lifetime. No real credentials or hosted connection string were used or committed.

## Tests and regression evidence

Commands ran from `mdc-catalog/backend` using `../../.venv/Scripts/python.exe`, with process-local `DATABASE_URL` empty and `DJANGO_SETTINGS_MODULE=config.settings`. Configuration tests use explicit synthetic, non-routable URLs; settings integration runs in isolated subprocess environments.

| Verification | Total | Passed | Failed | Skipped | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| `manage.py check` | — | — | 0 | — | No issues |
| `manage.py makemigrations --check --dry-run` | — | — | 0 | — | No changes detected |
| `manage.py test tests.test_provider_persistence_models tests.test_database_configuration -v 2` | 18 | 18 | 0 | 0 | PASS |
| `manage.py test -v 2` (final run) | 423 | 410 | 0 | 13 | PASS |
| Separately maintained focused H1-H9 set below | 230 | 225 | 0 | 5 | PASS |
| `git diff --check` / staged diff check | — | — | 0 | — | PASS |

The 11 model tests cover creation/defaults, UUID identities, provider/external offering uniqueness, same-category offerings, certification uniqueness per provider, unresolved publications, deletion cascades and retained history/outbox, sync defaults, independent mutable defaults, and nested Unicode/boolean/null/numeric JSON round-trips across all capability and publication fields.

The seven configuration tests cover fallback without ambient environment dependence, empty values, both PostgreSQL URL schemes and decoded credentials, query parameters, unsupported engines, credential-safe output/errors, and base/production settings wiring including disabled publication by default.

The first full run had 409 passed, one failed, and 13 skipped out of 423. `test_demo_api_foundation.test_shared_catalog_filters_endpoint_still_works` still expected the legacy `service_types` key. The approved [API contract rectification report](09_mdc_v1_api_contract_rectification_report.md) and existing `test_public_api_contract.test_stable_filters_contract` require `service_categories`. This mismatch was explained before editing the stale test. The replacement asserts contract version 1.0, `service_categories`, `part_families`, `part_types`, and absence of `service_types`. No production behavior was reverted and no test was removed or newly skipped. The full suite then passed.

The H1-H9 command is the separately documented set from the production preparation report:

```powershell
../../.venv/Scripts/python.exe manage.py test tests.test_service_discovery_registry tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_provider_loader tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_local_matcher tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service tests.test_service_discovery_fuseki_service tests.test_service_discovery_matching_alignment tests.test_service_discovery_runtime_search tests.test_service_discovery_search_endpoint tests.test_service_discovery_local_search_response tests.test_service_discovery_fuseki_matching_alignment tests.test_service_discovery_search_response_contract -v 2
```

All 13 full-suite skips are existing optional remote integration guards: four legacy Fuseki integration tests, four harmonized Fuseki integration tests, and five H9 remote matching alignment tests. The focused suite includes the latter five. Live Fuseki integration was not verified; local matching, RDF, SPARQL, runtime, and contract tests passed. No skip conditions were changed.

## API and production safety

Diff inspection confirms no route, API implementation, public response adapter, harmonized serializer/normalizer, H1-H9 loader/matcher, RDF generator, or Fuseki implementation changes. Existing public contract and production safety tests passed within the full suite.

The canonical public endpoints remain `GET /api/health`, `GET /api/catalog/filters`, and `POST /api/service-discovery/search`. No `/api/v1/...` routes or provider lifecycle APIs were added. Legacy provider publication remains file-backed, with `MDC_PROVIDER_PUBLICATION_ENABLED=False` still the production default. The new configuration tests independently verify that default with and without a PostgreSQL URL.

## Changed files

- `mdc-catalog/backend/apps/providers/models.py`
- `mdc-catalog/backend/apps/providers/migrations/0001_initial.py`
- `mdc-catalog/backend/config/database.py`
- `mdc-catalog/backend/config/settings.py`
- `mdc-catalog/backend/tests/test_provider_persistence_models.py`
- `mdc-catalog/backend/tests/test_database_configuration.py`
- `mdc-catalog/backend/tests/test_demo_api_foundation.py`
- `mdc-catalog/requirements/base.txt`
- `mdc-catalog/.env.example`
- This report.

## Git and next gate

Implementation commit: `325874b` — `feat: add M7.1 provider persistence foundation`.

This report is committed separately as `docs: report M7.1 persistence foundation verification`, allowing it to reference the already-created implementation commit. Both commits are intended for the requested normal push to `origin/main`; final remote synchronization is verified after that push and reported in the console response. No secrets, actual `.env`, `.vercel/`, SQLite databases, or generated runtime artifacts are included.

PostgreSQL URL configuration and driver installation were verified locally; actual PostgreSQL/Neon connectivity, PostgreSQL migration execution, and hosted JSONB behavior remain for the next gate. This task did not provision Neon, change Vercel configuration/environment, deploy, import YAML, switch runtime data sources, add provider lifecycle endpoints, enable publication, implement sync processing, or update partner API documentation. M7.2 has not started.

READY_FOR_M71_NEON_CONNECTION_GATE
