# Codex Task 10 — M7.2 Managed PostgreSQL Validation Gate

## Recommended Codex configuration

- Label: `[mdc_m72_managed_postgres_gate]`
- Model: GPT-5.6 Sol
- Reasoning: Medium
- Increase to High only if a real PostgreSQL migration/transaction blocker requires it.

Do not start M7.3 in this task.

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

Relevant completed reports:

```text
mdc-catalog/docs/Phase_2/11_mdc_v1_m71_postgresql_django_foundation_report.md
mdc-catalog/docs/Phase_2/12_mdc_v1_m72_harmonized_db_repository_migration_report.md
```

M7.2 is locally complete. Current verified local evidence includes:

```text
M7.2 focused tests: 33 passed
Full suite: 443 passed, 13 existing skips
Focused H1-H9: 225 passed, 5 existing skips
YAML <-> DB canonical parity: PASS
RDF parity: 673 identical triples
Matcher parity: 12 scenarios PASS
```

The next gate is to prove the same persistence/repository/import behavior against a real managed PostgreSQL database before M7.3.

The persistence layer is intentionally cloud-neutral. The managed database may currently be Neon for the pilot, while AWS is the long-term deployment target. Do not introduce Neon-, Vercel-, AWS-, or other provider-specific application code.

---

# Security prerequisite

This task requires a dedicated managed PostgreSQL `DATABASE_URL` supplied through the local process environment or an untracked local `.env` mechanism.

Important:

- NEVER put the actual `DATABASE_URL` in this prompt, Git, report, console summary, test fixture, command history committed to the repository, screenshot, or error message.
- NEVER print the connection string.
- If no usable managed PostgreSQL `DATABASE_URL` is available in the local environment, stop and report exactly:

```text
BLOCKED_MANAGED_POSTGRES_DATABASE_URL_REQUIRED
```

Do not invent credentials and do not provision cloud infrastructure from Codex.

Prefer a dedicated validation database/branch rather than a production catalogue database.

---

# Current public/API safety baseline

These public APIs must remain unchanged:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

No `/api/v1/...` routes.

Provider publication remains production-disabled:

```text
MDC_PROVIDER_PUBLICATION_ENABLED=False
```

YAML remains the live runtime provider source during this validation gate. Do not switch runtime discovery to the DB.

---

# Goal

Validate the M7.1/M7.2 database schema, migrations, import, canonical adapter, JSONB behavior, transactional guarantees, RDF parity, and matcher parity against actual PostgreSQL.

Conceptually:

```text
managed PostgreSQL
      ↓
0001 + 0002 migrations
      ↓
curated YAML import
      ↓
3 providers / 4 offerings / 5 certifications
      ↓
DB canonical adapter
      ↓
exact YAML parity
      ↓
RDF 673-triple parity
      ↓
12 matcher scenarios parity
```

No new product feature is being implemented in this gate.

---

# Step 1 — Synchronize and inspect

1. Run `git status` from repository root.
2. Pull/fetch `origin/main` if required.
3. Confirm the worktree is clean.
4. Read the M7.1 and M7.2 reports and current implementation before executing database operations.
5. Do not discard unrelated local work.

---

# Step 2 — Confirm the selected database is real PostgreSQL

With `DATABASE_URL` supplied securely outside Git:

Run Django against the selected environment and prove:

```text
connection.vendor == "postgresql"
```

Also safely record, without credentials:

- PostgreSQL server version;
- database name if safe to state;
- whether SSL is active if it can be queried without revealing connection details;
- Django version and psycopg version.

Do not report host, username, password, URL query secrets, or full connection metadata.

If the configured engine is not PostgreSQL, stop.

---

# Step 3 — Apply actual Django migrations

From backend root, with the managed PostgreSQL environment selected:

```powershell
python manage.py check
python manage.py showmigrations providers
python manage.py migrate --noinput
python manage.py showmigrations providers
python manage.py makemigrations --check --dry-run
```

Required:

- `providers.0001_initial` applies successfully;
- `providers.0002_canonical_parity_fields` applies successfully;
- no migration drift;
- no SQLite-specific migration dependency is exposed.

Do not edit migrations merely because PostgreSQL reports a genuine schema error; first identify the exact mismatch and only fix code/migration if it is an application defect.

---

# Step 4 — Verify actual PostgreSQL physical schema

Using Django's connection cursor or a safe read-only SQL inspection, verify the provider tables created by migrations.

At minimum verify:

- Provider/Offering/ProviderCertification/ProviderPublication/CatalogueSyncEvent tables exist;
- Django `JSONField` columns are physically PostgreSQL `jsonb` columns where expected;
- UUID primary keys are PostgreSQL UUID-compatible;
- FK relationships exist;
- unique constraints exist for `provider_id`, `offering_id`, and `(provider, code)`;
- `sync_status_created_idx` exists;
- M7.2 parity fields exist:
  - `Provider.publication_metadata`
  - `Offering.sequence_index`
  - `ProviderCertification.sequence_index`
  - `ProviderCertification.source_note_present`

Do not add PostgreSQL-only indexes/extensions/features merely for this validation.

---

# Step 5 — Import the current curated catalogue

Run:

```powershell
python manage.py import_service_discovery_providers
```

Expected successful aggregate result:

```text
Providers imported/updated: 3; offerings synchronized: 4; certifications synchronized: 5.
```

Then run the same command a second time.

Requirements after both runs:

```text
Provider rows: 3 current imported providers
Offering rows: 4 current imported offerings
ProviderCertification rows: 5 current imported certifications
```

The second import must be idempotent for canonical state and UUID identities.

Do not create bootstrap ProviderPublication or CatalogueSyncEvent rows unless the existing M7.2 implementation already does so; current approved behavior is that bootstrap import creates neither.

---

# Step 6 — Exact YAML <-> PostgreSQL canonical parity

Using the existing functions:

```python
load_service_discovery_providers()
load_service_discovery_providers_from_db()
```

prove exact equality for the complete current curated provider set.

Also verify provider-detail parity for:

```text
tasowheel
precipart
demo_machining_provider
```

Fidelity must include:

- provider ordering;
- offering ordering;
- certification ordering;
- nested JSON list order;
- available-grade order;
- process/support order;
- numeric and boolean values;
- Unicode;
- explicit nested null values;
- certification `source_note` omission vs explicit null behavior;
- top-level `publication_metadata`.

Do not weaken exact parity to set equality.

---

# Step 7 — PostgreSQL transaction / rollback verification

Run focused existing M7.1/M7.2 tests against PostgreSQL where feasible, especially:

```text
tests.test_provider_persistence_models
tests.test_service_discovery_db_repository
tests.test_import_service_discovery_providers_command
```

The PostgreSQL-backed verification must demonstrate:

- `transaction.atomic()` rollback works after a simulated mid-batch failure;
- offering ownership conflicts cannot partially mutate the batch;
- `select_for_update()` paths execute successfully under PostgreSQL transaction semantics;
- uniqueness constraints behave as expected;
- JSON values round-trip through real JSONB without semantic loss.

If Django's test runner cannot create a temporary test database due managed-service permissions, do not weaken tests silently. Report the permission limitation and perform equivalent isolated checks against a dedicated validation database only if they can be done safely and reversibly.

Do not run destructive checks against any production database.

---

# Step 8 — RDF parity on PostgreSQL-backed canonical data

Load the canonical records from PostgreSQL and compare them against the current YAML records through the unchanged existing RDF generator.

Required result:

```text
exact RDF triple-set equality
expected current catalogue triple count: 673
```

Confirm sequence/evidence fidelity remains represented.

Do not change the RDF generator or mappings unless a genuine existing defect is proven.

---

# Step 9 — Matcher parity on PostgreSQL-backed canonical data

Run the same existing M7.2 matcher-parity scenario set with:

```text
A = YAML canonical records
B = PostgreSQL canonical records
```

Required:

```text
12 scenarios
A == B for every result
```

Do not change H1-H9 matching semantics.

---

# Step 10 — Local regression after managed PostgreSQL validation

After the managed PostgreSQL-specific checks, restore the normal local test environment so credentials are not accidentally persisted.

Then run the regular local verification with the repository's normal SQLite/default test setup:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test -v 2
```

Also run the separately maintained H1-H9 focused set used in the M7.2 report.

Expected baseline before any genuine fix:

```text
Full suite: 443 passed, 13 existing skips
Focused H1-H9: 225 passed, 5 existing skips
```

Counts may increase if this gate legitimately adds tests, but existing tests must not regress, be removed, weakened, or newly skipped.

---

# Step 11 — Confirm runtime/API non-regression

Confirm this gate does NOT:

- switch runtime provider discovery from YAML to DB;
- alter Fuseki fallback behavior;
- change RDF mappings;
- expose provider lifecycle endpoints;
- enable provider publication;
- add `/api/v1/...` routes;
- change the three canonical public API contracts;
- introduce managed-provider-specific code.

The managed PostgreSQL database is a validation target only at this stage.

---

# Step 12 — Create managed PostgreSQL validation report

Create:

```text
mdc-catalog/docs/Phase_2/13_mdc_v1_m72_managed_postgres_validation_report.md
```

Include:

1. gate status;
2. safe database technology/version evidence;
3. migration execution result;
4. PostgreSQL physical-schema/JSONB verification;
5. import result and exact counts;
6. second-import idempotency evidence;
7. YAML <-> DB exact parity result;
8. transaction/rollback/locking result;
9. RDF parity result and triple count;
10. matcher parity result/scenario count;
11. PostgreSQL-backed focused test result/count;
12. regular local full-suite result/count;
13. regular focused H1-H9 result/count;
14. public/runtime non-regression confirmation;
15. files changed, if any;
16. Git commit(s);
17. known limitations;
18. whether M7.3 can start.

Do not include credentials, hostnames, usernames, URLs, tokens, or sensitive connection metadata.

If all gates pass, end exactly with:

```text
READY_FOR_M73_PROVIDER_VALIDATION_READ_LIFECYCLE
```

Otherwise end exactly with:

```text
NOT_READY_FOR_M73_PROVIDER_VALIDATION_READ_LIFECYCLE
```

and state the exact blocker.

---

# Step 13 — Git handling

If this task requires no code change, commit only the validation report.

Suggested report-only commit:

```text
docs: verify M7.2 on managed PostgreSQL
```

If a genuine PostgreSQL portability defect requires a code/test fix:

1. make the smallest cloud-neutral fix;
2. add/adjust tests proving it;
3. rerun all gates;
4. commit implementation separately before the report.

Then push normally to `origin/main`.

Never commit `.env`, `DATABASE_URL`, passwords, local DB artifacts, cloud metadata, or secrets.

---

# Scope restrictions

Do NOT in this task:

- start M7.3;
- switch production/runtime provider source to PostgreSQL;
- change Vercel deployment;
- enable provider publication;
- implement provider validation/read/update APIs;
- implement RDF/Fuseki outbox processing;
- update partner API documentation;
- redesign H1-H9;
- add cloud-vendor SDK dependencies;
- make a managed cloud provider part of the domain/application architecture.

---

# Final console response

Return only:

1. git/worktree synchronization status
2. managed PostgreSQL engine/version validation
3. migration status
4. physical PostgreSQL schema/JSONB status
5. first import counts
6. second import/idempotency status
7. exact YAML <-> DB parity status
8. PostgreSQL transaction/rollback/locking status
9. RDF parity/triple count
10. matcher parity/scenario count
11. PostgreSQL-backed focused test result/count
12. regular local full-suite result/count
13. regular focused H1-H9 result/count
14. public/runtime non-regression status
15. report path/status
16. Git commit hash/message(s)
17. `READY_FOR_M73_PROVIDER_VALIDATION_READ_LIFECYCLE` or `NOT_READY_FOR_M73_PROVIDER_VALIDATION_READ_LIFECYCLE`

Do not start M7.3 automatically.
