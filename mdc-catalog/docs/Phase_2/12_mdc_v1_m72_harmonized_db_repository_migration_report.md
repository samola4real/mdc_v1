# M7.2 Harmonized DB Repository and Curated YAML Migration Report

Date: 2026-09-09

## Status and baseline

M7.2 local implementation and semantic parity verification are complete. The repository, transactional import command, generated schema correction, and all local regression gates pass. Managed PostgreSQL validation and M7.3 have not started.

The worktree was clean on `main` at `5b3ee3abe632e3437bcab06b58c934b7b0a9e256` (`docs: add M7.2 harmonized DB repository migration prompt`). Fetching `origin` confirmed synchronization; no pull or conflict resolution was necessary. The M7 plan, infrastructure portability decision, M7.1 report/models/migration, current YAML loader, RDF generator, and local matcher were inspected before implementation. No unrelated work was changed.

## Parity schema correction

Generated `backend/apps/providers/migrations/0002_canonical_parity_fields.py` with Django 5.2.13 using:

```powershell
../../.venv/Scripts/python.exe manage.py makemigrations providers --name canonical_parity_fields
```

It depends on `providers.0001_initial` and adds:

| Field | Definition | Purpose |
| --- | --- | --- |
| Provider.publication_metadata | JSONField(default=dict, blank=True) | Current canonical top-level metadata |
| Offering.sequence_index | PositiveIntegerField(default=0) | Offering list order within a provider |
| ProviderCertification.sequence_index | PositiveIntegerField(default=0) | Certification evidence publication order |
| ProviderCertification.source_note_present | BooleanField(default=False) | Distinguish an omitted source note from an explicit null |

The fourth field is a small fidelity correction beyond the three preferred fields: the M7.1 nullable text field alone cannot distinguish omission from explicit null. Tests preserve all four cases: omitted, null, empty string, and populated string. Non-null notes on preexisting rows are still emitted even when the presence flag defaults to false. This adds no payload duplication or schema abstraction.

Existing UUIDs, relationships, uniqueness constraints, lifecycle choices, and nested JSON fields remain unchanged. No sequence uniqueness constraints or extra indexes were added. The generated migration applied successfully to the temporary test database; `makemigrations --check --dry-run` reports no drift. No actual hosted database was migrated.

## Repository API and exact mapping

Implementation: `backend/apps/providers/service_discovery_db_repository.py`.

| Function | Behavior |
| --- | --- |
| import_service_discovery_provider_records(records) | Validate and synchronize a list/tuple of complete current snapshots in one transaction; return provider/offering/certification counts |
| load_service_discovery_providers_from_db() | Return canonical records for active providers and active offerings |
| get_service_discovery_provider_from_db(provider_id) | Return one active canonical record, or None when missing/inactive |

The adapter emits only the harmonized `provider`, `offerings`, and `publication_metadata` shape. It does not emit UUIDs, custom fields, timestamps, lifecycle flags, sequence fields, publication history, or outbox state.

| YAML path | Persistent mapping |
| --- | --- |
| provider.provider_id | Provider.provider_id, external upsert identity |
| provider.display_name | Provider.provider_name |
| provider.country | Provider.country |
| provider.certifications[].code/source_type/confidence/source_note | ProviderCertification fields attached to Provider; source_note presence recorded separately |
| provider.certifications[] position | ProviderCertification.sequence_index |
| publication_metadata | Provider.publication_metadata |
| offerings[].offering_id | Offering.offering_id, stable external upsert identity |
| offerings[].provider_id | Must equal the enclosing provider_id; stored as Offering.provider FK |
| offerings[].name | Offering.offering_name |
| offerings[].service_category/part_family/support_status | Same-named Offering fields |
| offerings[].supported_part_types | Offering.supported_part_types JSON list |
| offerings[].family_capabilities/part_type_capabilities/generic_capabilities | Same-named JSON objects |
| offerings[] position | Offering.sequence_index |

Import sets current providers to `active` and imported offerings to `is_active=True`. Canonical reads reverse the name mappings and derive offering `provider_id` from the parent's external identity. Existing custom DB fields are preserved on reimport but excluded from canonical output.

## Ordering and evidence fidelity

Providers are explicitly ordered by `provider_id`. This matches the existing filename-sorted YAML loader for all current files; arbitrary renamed files are not treated as a separate persisted provider order. Offering reads use `(sequence_index, offering_id)` and certification reads use `(sequence_index, code)`. Stable external-ID tie breakers make preexisting default-zero sequences deterministic.

JSON list order, nested objects, evidence fields, grade order, support order, explicit nulls, numeric/boolean values, and Unicode survive unchanged. Optional missing containers are explicitly normalized to empty containers: certifications/supported_part_types become `[]`, capability objects/publication_metadata become `{}`. All current curated files already provide these containers, so their complete records round-trip exactly. Null in place of a required container is rejected, while nested null evidence and explicit null certification notes are retained.

The active catalogue query prefetches the ordered child relations. Tests verify three queries for the complete nonempty catalogue and three for an existing provider detail. Draft, suspended, and archived providers are excluded; inactive offerings are excluded. Active providers with no active offerings remain visible as records with empty offering lists. Neither query path changes the runtime source selection.

## Import transaction and idempotency semantics

The existing `load_service_discovery_providers` remains the sole YAML parser. The repository validates all batch structure before writes, including required bounded string fields, mapping/list types, duplicate provider/offering IDs, duplicate per-provider certification codes, offering parent identity, support lifecycle values, and JSON representability. Unknown top-level/provider/offering/certification keys are rejected with structural paths and no supplied values in the error. Nested capability vocabulary semantics remain owned by existing harmonized validation; no second ontology validator was added.

The entire persistence batch runs within `transaction.atomic()`. Existing offering ownership is checked before stale-row deletion, preventing a batch from deleting an ID under one provider and reassigning it to another. Existing rows are locked using standard Django ORM operations where applicable; conflicting identities fail the batch. Provider, offering, and certification upserts retain existing UUIDs. Absent children of each imported provider are deleted; providers absent from the batch and their children are left alone. Empty batches are no-ops, and empty child snapshots clear that provider's children only.

No ProviderPublication or CatalogueSyncEvent rows are created for bootstrap import. Existing history/outbox rows are not rewritten. Reimporting identical snapshots preserves canonical output, row counts, and UUID sets. Auto-updated timestamps may advance; byte-for-byte database immutability is not the idempotency contract.

Tests demonstrate both structural rejection before any database queries and rollback after a simulated database failure following earlier successful writes. They also verify that an offering cannot move to a different provider, including through delete-then-reassign ordering within one batch.

## Management command

Implementation: `backend/apps/providers/management/commands/import_service_discovery_providers.py`.

From the backend directory, after applying migrations to the explicitly selected local database:

```powershell
../../.venv/Scripts/python.exe manage.py migrate
../../.venv/Scripts/python.exe manage.py import_service_discovery_providers
../../.venv/Scripts/python.exe manage.py import_service_discovery_providers --directory <provider-directory>
```

The default directory is `data/curated/service_discovery/providers` beneath the project root. `--directory` uses the same loader and its `.yaml`/`.yml` support. No dry-run mode was added. The command operates on the database selected by the existing Django configuration; no cloud SDK or provider-specific behavior is introduced.

Successful current-catalogue output is exactly:

```text
Providers imported/updated: 3; offerings synchronized: 4; certifications synchronized: 5.
```

Only aggregate counts are printed. YAML/parser and database errors are converted to safe CommandError messages so source lines, evidence blobs, rejected rows, and connection details are not echoed. Command tests cover defaults, alternate directory, repeated import, malformed/invalid YAML, missing directory, empty-directory no-op, and database-error redaction.

All imports during this task ran against temporary test databases. The commands above document usage; no developer or hosted database was populated as an unreported side effect.

## Current curated data and parity results

| File / provider_id | Offerings | Certifications |
| --- | ---: | ---: |
| demo_machining_provider.yaml / demo_machining_provider | 1 | 1 |
| precipart.yaml / precipart | 1 | 0 |
| tasowheel.yaml / tasowheel | 2 | 4 |
| Total | 4 | 5 |

Exact YAML-to-DB canonical equality passes for all three records in loader order. Tests additionally reverse import order, certification order, offering order, grade/process/support list order, and exercise nested null/Unicode evidence and publication metadata.

RDF parity passes both graph isomorphism and exact triple-set equality: **673 triples**, including **45 sequence-index triples**. A separate reordered certification/offering test preserves graph parity after reimport. The existing RDF generator is used unchanged with injected provider records.

Local matcher parity passes exact result equality for **12 request scenarios** using existing serializer/normalizer fixtures: spur/crown/worm gears, hollow/splined shafts, reject-unknown policy, dimensional/quality requirements, process evidence, a metal-part/block empty-result path, and any/all/score-only optional policies. Together they exercise all three current providers; the metal-part family intentionally has no current offering. No matching engine or semantics were changed.

## Verification evidence

All commands used the workspace Python 3.11 virtual environment from `mdc-catalog/backend`, with process-local `DATABASE_URL` empty and `DJANGO_SETTINGS_MODULE=config.settings`. Migrations 0001 and 0002 applied in the SQLite test database. No new skips were introduced.

| Gate | Total | Passed | Failed | Existing skips | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| manage.py check | — | — | 0 | — | No issues |
| manage.py makemigrations --check --dry-run | — | — | 0 | — | No changes detected |
| Focused M7.2 repository + command tests | 33 | 33 | 0 | 0 | PASS |
| Full Django suite | 456 | 443 | 0 | 13 | PASS |
| Separately maintained H1-H9 suite | 230 | 225 | 0 | 5 | PASS |
| Git diff/staged whitespace checks | — | — | 0 | — | PASS |

Focused and full commands:

```powershell
../../.venv/Scripts/python.exe manage.py check
../../.venv/Scripts/python.exe manage.py makemigrations --check --dry-run
../../.venv/Scripts/python.exe manage.py test tests.test_service_discovery_db_repository tests.test_import_service_discovery_providers_command -v 2
../../.venv/Scripts/python.exe manage.py test -v 2
```

The focused H1-H9 command is unchanged from the M7.1 report:

```powershell
../../.venv/Scripts/python.exe manage.py test tests.test_service_discovery_registry tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_provider_loader tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_local_matcher tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service tests.test_service_discovery_fuseki_service tests.test_service_discovery_matching_alignment tests.test_service_discovery_runtime_search tests.test_service_discovery_search_endpoint tests.test_service_discovery_local_search_response tests.test_service_discovery_fuseki_matching_alignment tests.test_service_discovery_search_response_contract -v 2
```

The 13 existing skips cover four legacy Fuseki integration tests, four harmonized Fuseki integration tests, and five H9 remote alignment tests. The focused set includes the latter five. Actual remote Fuseki behavior was not exercised. Existing tests were neither edited, removed, weakened, nor newly skipped.

## Public API and runtime safety

Diff inspection and existing public-contract/production-route tests confirm the canonical endpoints are unchanged: `GET /api/health`, `GET /api/catalog/filters`, and `POST /api/service-discovery/search`. No routes or public response adapters were modified, no `/api/v1/...` routes were added, and no provider lifecycle APIs were exposed.

`MDC_PROVIDER_PUBLICATION_ENABLED=False` remains the production default. Legacy provider publication remains file-backed. YAML remains the live provider loader; runtime fallback order, RDF mappings, and Fuseki search behavior are unchanged. The only application integration with the new repository is the explicit management command; tests inject DB records directly for parity verification. No runtime source-selection flag was added.

## Changed files and Git

- `backend/apps/providers/models.py`
- `backend/apps/providers/migrations/0002_canonical_parity_fields.py`
- `backend/apps/providers/service_discovery_db_repository.py`
- `backend/apps/providers/management/__init__.py`
- `backend/apps/providers/management/commands/__init__.py`
- `backend/apps/providers/management/commands/import_service_discovery_providers.py`
- `backend/tests/test_service_discovery_db_repository.py`
- `backend/tests/test_import_service_discovery_providers_command.py`
- `docs/Phase_2/12_mdc_v1_m72_harmonized_db_repository_migration_report.md`

Paths above are relative to `mdc-catalog/`. No dependency, actual environment, database, curated YAML, generated runtime artifact, deployment configuration, or partner API documentation changes are included.

Implementation commit: `2e62c16` — `feat: add M7.2 harmonized DB repository and import`.

This report is committed separately as `docs: report M7.2 repository parity verification`, so it can reference the completed implementation commit. The requested normal push to `origin/main` and final worktree synchronization are checked after committing the report and reported in the console response.

## Limitations and next gate

The foundation uses standard Django ORM and PostgreSQL-compatible data types; it contains no Neon/AWS SDKs or Vercel persistence logic. Actual PostgreSQL connectivity, migration/import execution, JSONB behavior, and lock/concurrency behavior remain for the managed PostgreSQL validation gate. Bootstrap imports should be run as a controlled operation; this task does not establish a concurrent public write protocol or large-catalogue streaming/bulk performance contract. Reads use three statements, without claiming a cross-statement snapshot during simultaneous writes.

Before M7.3, validate actual migrations/import and parity smoke checks against the explicitly selected managed PostgreSQL instance. This task did not provision infrastructure, connect a hosted database, change Vercel configuration, deploy, switch runtime data sources, implement lifecycle APIs, enable publication, create bootstrap publication/outbox events, implement synchronization, or start M7.3.

READY_FOR_M72_MANAGED_POSTGRES_VALIDATION_GATE
