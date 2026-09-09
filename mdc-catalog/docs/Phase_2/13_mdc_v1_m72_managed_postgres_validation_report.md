# M7.2 Managed PostgreSQL Validation Report

Date: 2026-09-09

## Gate status

The M7.2 managed PostgreSQL validation gate is complete. Migrations, physical schema, two imports, exact canonical/RDF/matcher parity, PostgreSQL-focused tests, and local regression gates all pass. M7.3 may start as a separate task; it has not started automatically.

## Synchronization and credential handling

The tracked worktree was clean and synchronized with `origin/main` at `fb1f0ac` after fetching. Existing untracked `mdc-catalog/env.example` and `mdc-catalog/mdc_env_standardization_files/` were preserved and excluded from staging.

The user supplied the validation connection through the ignored canonical `mdc-catalog/.env`. Its DATABASE_URL initially contained a copied psql command wrapper. The wrapper was removed locally while preserving the enclosed connection value. No connection details, credentials, hostnames, usernames, database identifiers, or URLs are included in this report. The local file remains ignored and is not part of any commit. No infrastructure was provisioned.

## Database technology and transport

| Check | Evidence |
| --- | --- |
| Django connection vendor | postgresql |
| PostgreSQL server version | 18.6 |
| Django version | 5.2.13 |
| psycopg version | 3.3.5 |
| Client TLS | Active, verified with the connected libpq client's ssl_in_use property |

The server-side pg_stat_ssl probe returned false for the backend session, while client TLS was active. This report distinguishes client transport from the backend session; it does not infer the managed service's internal network topology. No application TLS settings were weakened.

## Migrations and physical schema

The selected validation database initially had no provider tables. The following commands ran against actual PostgreSQL through Django management calls, with output captured in memory and only safe outcomes emitted:

```text
manage.py check
manage.py showmigrations providers
manage.py migrate --noinput
manage.py showmigrations providers
manage.py makemigrations --check --dry-run
```

All passed. The migration recorder confirms both `providers.0001_initial` and `providers.0002_canonical_parity_fields` are applied. No migration drift or SQLite-specific dependency was found. No migration or application code was changed.

Read-only information_schema inspection and Django constraint introspection verified:

- All five provider persistence tables exist.
- All 11 JSONField columns are physically PostgreSQL `jsonb`.
- All five primary keys are PostgreSQL `uuid` columns with primary-key constraints.
- All four foreign keys target the expected related tables and columns.
- Unique constraints exist for Provider.provider_id, Offering.offering_id, and ProviderCertification(provider_id, code).
- `sync_status_created_idx` covers `(status, created_at)`.
- Provider.publication_metadata is JSONB; both sequence_index fields are integers; source_note_present is boolean.

No PostgreSQL-only feature, extension, or index was introduced by application changes.

## Import and idempotency

Before importing, all five provider persistence tables were confirmed empty. The existing `import_service_discovery_providers` command was run twice against the selected validation database.

| Current curated provider | Offerings | Certifications |
| --- | ---: | ---: |
| demo_machining_provider | 1 | 1 |
| precipart | 1 | 0 |
| tasowheel | 2 | 4 |
| Total | 4 | 5 |

Both imports succeeded. Totals after each run were 3 providers, 4 offerings, 5 certifications, 0 publications, and 0 sync events. UUID identity sets for all five models were identical before and after the second import. No bootstrap history or outbox records were fabricated.

## Canonical, RDF, and matcher parity

After each import, direct equality of the complete ordered YAML catalogue and PostgreSQL canonical output passed. Individual canonical detail equality also passed for all three providers. This verifies the current offering/certification ordering, nested JSON evidence, grade/process/support list ordering, numerical values, explicit nested nulls, and top-level publication metadata.

The unchanged RDF generator produced identical triple sets from YAML and PostgreSQL records: **673 triples**, including **45 sequence-index triples**. Both imports passed this comparison.

The unchanged local matcher produced exactly equal responses for all **12 M7.2 scenarios**, after both imports. The scenarios reuse existing request fixtures and cover spur/crown/worm gears, hollow/splined shafts, unknown rejection, dimensional/quality criteria, process evidence, the empty metal-part/block path, and any/all/score-only policies.

## PostgreSQL focused tests

**44 tests passed, zero failures, zero errors, zero skips.** The existing suites ran in a separate randomly named temporary PostgreSQL test database:

```text
tests.test_provider_persistence_models
tests.test_service_discovery_db_repository
tests.test_import_service_discovery_providers_command
```

The selected validation database and imported catalogue are separate from the test database. No test is redirected into the catalogue database. Existing tests exercise JSONB fidelity including Unicode and certification note omission/null distinctions, uniqueness, foreign-key deletion behavior, active-state filtering, idempotency, ownership protection, mid-batch rollback, and select_for_update paths under real PostgreSQL transactions.

The first test-run attempt reached database teardown, where PostgreSQL rejected the normal temporary-database drop with SQLSTATE 55006 because another connection remained attached. The temporary harness was adjusted to emit safe aggregate results before teardown and retain its uniquely named test database for explicit cleanup. The focused suites were rerun without weakening or changing repository tests; all 44 passed. Both task-owned temporary test databases were then removed using explicitly scoped PostgreSQL DROP DATABASE WITH (FORCE), with identifier validation and checks excluding the configured catalogue database. Their absence was verified. No pre-existing user or production database was dropped. The selected validation catalogue was subsequently rechecked: canonical, RDF, and 12-scenario matcher parity still passed.

The passing PostgreSQL tests include simulated mid-batch database failure with full rollback, ownership conflicts and delete-then-reassign rejection, successful select_for_update paths, uniqueness constraints, Unicode/nested JSONB values, certification note omission versus explicit null, UUID idempotency, publication-history preservation, and command error redaction. No test database creation permission limitation was encountered.

## Local regression

Local regression used a process-local empty DATABASE_URL to select SQLite without modifying or persisting credentials. Local demo/publication flags were explicitly set to the normal test baseline; production settings and production-default safety assertions remain unchanged.

| Verification | Total | Passed | Failed/errors | Existing skips | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| PostgreSQL M7.1/M7.2 focused tests | 44 | 44 | 0 | 0 | PASS |
| Local manage.py check | — | — | 0 | — | PASS |
| Local makemigrations --check --dry-run | — | — | 0 | — | No drift |
| Local manage.py test -v 2 | 456 | 443 | 0 | 13 | PASS |
| Local separately maintained H1-H9 set | 230 | 225 | 0 | 5 | PASS |

The focused H1-H9 module list is exactly the command recorded in the M7.2 report. Existing optional remote Fuseki guards account for the skips: four legacy integration tests, four harmonized integration tests, and five remote alignment tests in the full suite; the latter five in the focused suite. No tests were modified, weakened, removed, or newly skipped.

## Runtime and API non-regression

No application, migration, route, serializer, response adapter, YAML loader, RDF mapping, or matching code was changed for this gate. YAML remains the live runtime source, Fuseki fallback behavior remains intact, and no runtime database-selection switch was introduced.

The canonical endpoints remain `GET /api/health`, `GET /api/catalog/filters`, and `POST /api/service-discovery/search`. No `/api/v1/...` routes or provider lifecycle endpoints were added. Provider publication remains disabled by default in production. No deployment, provider SDK, cloud-specific domain dependency, or partner API documentation change was made.

## Files and Git

The only intended tracked change is this report:

`mdc-catalog/docs/Phase_2/13_mdc_v1_m72_managed_postgres_validation_report.md`.

The validation helper was temporary local tooling outside the repository and contained no connection value. No credential-bearing files, database artifacts, helper-folder copies, or runtime outputs are staged.

Report-only commit message: `docs: verify M7.2 on managed PostgreSQL`. The final commit hash and normal push/synchronization are reported in the console response after commit, avoiding a self-referential commit hash in this file. No application-code or test changes were required.

## Limitations and next step

This gate establishes compatibility of the current schema, curated data import, and repository behavior with the selected PostgreSQL validation target. It does not establish production load capacity or general concurrent writer correctness. Real remote Fuseki integration remains outside this database gate. The validation catalogue remains populated for subsequent reviewed work; it has not become the runtime catalogue source.

All required gates passed. M7.3 may begin through a separate explicit task. M7.3 has not started.

READY_FOR_M73_PROVIDER_VALIDATION_READ_LIFECYCLE
