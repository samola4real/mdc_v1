# Codex Task 08 — M7.1 PostgreSQL / Django Persistence Foundation

## Recommended Codex configuration

- Label: `[mdc_m71_persistence]`
- Model: GPT-5.6 Sol
- Reasoning: Medium
- Increase to High only if a real migration/model/configuration blocker requires it.

Do not start M7.2 or any provider API exposure work in this task.

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

Approved M7 design baseline:

```text
mdc-catalog/docs/Phase_2/10_mdc_v1_m7_persistence_provider_lifecycle_plan.md
```

M6.1 is complete and production verified. Current external public APIs must remain unchanged:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

There is no public `/api/v1/...` URL family.

Current provider publication remains production-disabled.

---

# Current Repository Facts

Before changing code, verify these facts in the current branch rather than assuming stale history:

1. `backend/apps/providers/models.py` is effectively empty.
2. Django currently defaults to SQLite in `backend/config/settings.py`.
3. `backend/config/settings_production.py` inherits the base database configuration and does not yet require PostgreSQL.
4. `requirements/base.txt` does not yet include a PostgreSQL driver or database-URL parser.
5. The repository already contains the harmonized provider-publication serializer and normalizer:
   - `backend/apps/api/service_discovery_publication_serializers.py`
   - `backend/apps/providers/service_discovery_publication.py`
6. The existing legacy `POST /api/provider-publication` is file-backed and must NOT be converted or enabled in M7.1.
7. Existing H1-H9 service discovery must not be changed.

If the repository has evolved and any of these facts are no longer true, use the current implementation as source of truth and document the difference.

---

# M7.1 Goal

Create the durable persistence foundation only:

```text
Django persistence models
        ↓
initial migrations
        ↓
PostgreSQL / Neon-ready database configuration
        ↓
model/configuration tests
        ↓
full regression verification
```

M7.1 must NOT yet:

- migrate YAML provider data into PostgreSQL;
- switch H1-H9 runtime provider loading to PostgreSQL;
- implement the provider-validation endpoint;
- replace the legacy provider read endpoints;
- implement provider PATCH/update APIs;
- enable provider publication in production;
- create RDF/Fuseki synchronization workers;
- provision a Neon project/database;
- change Vercel environment variables;
- deploy to Vercel;
- start M7.2.

Remote Neon provisioning/connection will be reviewed as the next gate after the local schema/configuration foundation is accepted.

---

# Step 1 — Synchronize and Inspect

From repository root:

1. Run `git status`.
2. Pull `origin/main` if needed.
3. Confirm the worktree is clean before implementation.
4. Read the M7 plan and the current provider/publication/search code relevant to this task.
5. Do not discard unrelated user changes. If unexpected local changes exist, stop and report them.

---

# Step 2 — Implement Provider Persistence Models

Implement the initial persistent model set in the `providers` app. Prefer Django-native `models.JSONField`; on PostgreSQL this maps to JSONB while remaining testable with SQLite.

Use UUID primary keys for internal durable identities where specified. Use Django `TextChoices` for stable lifecycle/status enums.

## 2.1 Provider

Required baseline fields:

```text
id                         UUID primary key
provider_id                CharField, unique, stable external identifier
provider_name              CharField
country                    CharField
status                     draft | active | suspended | archived
custom_provider_fields     JSONField(default=dict, blank=True)
created_at                 auto-created timestamp
updated_at                 auto-updated timestamp
```

Requirements:

- `provider_id` is provider-supplied/stable external identity.
- Do not use business name as database identity.
- Add useful indexes only where justified; do not over-index prematurely.

## 2.2 Offering

Required baseline fields:

```text
id                         UUID primary key
offering_id                CharField, unique, MDC-owned external identifier
provider                   FK -> Provider, CASCADE
offering_name              CharField
service_category           CharField
part_family                CharField
support_status             confirmed | candidate_requiring_confirmation | unknown
supported_part_types       JSONField(default=list, blank=True)
family_capabilities        JSONField(default=dict, blank=True)
part_type_capabilities     JSONField(default=dict, blank=True)
generic_capabilities       JSONField(default=dict, blank=True)
custom_offering_fields     JSONField(default=dict, blank=True)
custom_capability_fields   JSONField(default=dict, blank=True)
is_active                  BooleanField(default=True)
created_at
updated_at
```

Important:

- Do not hard-code ontology vocabulary values as Django `choices` for `service_category` or `part_family`; those are controlled by the existing registry/serializer layer and may evolve without schema migrations.
- Do not create a database uniqueness constraint on `(provider, service_category)` in M7.1. The current harmonized serializer can continue enforcing current publication assumptions while leaving room for future multiple offerings per category if the business model evolves.

## 2.3 ProviderCertification

Required baseline fields:

```text
id                         UUID primary key
provider                   FK -> Provider, CASCADE
code                       CharField
source_type                CharField
confidence                 CharField
source_note                TextField(null/blank)
created_at
updated_at
```

Add a database uniqueness constraint preventing duplicate `(provider, code)` certification rows.

Do not duplicate the full controlled certification vocabulary in model choices; application-level harmonized validation remains authoritative.

## 2.4 ProviderPublication

Required baseline fields:

```text
id                         UUID primary key
provider                   nullable FK -> Provider, SET_NULL
provider_id_snapshot       CharField
operation                  create | update
status                     received | validation_failed | validated | persisted | sync_pending | synced | sync_failed | rejected
contract_version           CharField(default="1.0")
submitted_payload          JSONField(default=dict)
normalized_payload         JSONField(default=dict)
submitted_by_external_id   nullable/blank CharField
validation_errors          JSONField(default=dict)
created_at                 auto-created
validated_at               nullable DateTimeField
persisted_at               nullable DateTimeField
completed_at               nullable DateTimeField
```

Preserve publication history if the current provider row is later removed; therefore use `SET_NULL` for the provider FK.

## 2.5 CatalogueSyncEvent

Required baseline fields:

```text
id                         UUID primary key
publication                FK -> ProviderPublication, CASCADE
entity_type                provider | offering
entity_id                  CharField
operation                  upsert | delete
status                     pending | processing | succeeded | failed
attempt_count              PositiveIntegerField(default=0)
last_error                 TextField(blank=True)
created_at                 auto-created
processed_at               nullable DateTimeField
```

Add sensible indexes for future outbox processing, especially status/creation ordering, but keep the model minimal.

## Model-quality requirements

- Add useful `__str__` methods where appropriate.
- Use explicit `related_name` values so future repository/service code is readable.
- Do not introduce authentication/ownership FK models yet; `submitted_by_external_id` remains a placeholder.
- Do not put H1-H9 business validation logic into model `save()` methods.
- Do not rewrite the existing harmonized publication serializer in M7.1.

---

# Step 3 — Create Initial Migration

Create the first real migration for `apps.providers` using Django migrations.

Expected path pattern:

```text
backend/apps/providers/migrations/0001_initial.py
```

Requirements:

- migration must be generated from the actual models;
- no hand-written SQL unless Django genuinely cannot represent the needed schema;
- run `makemigrations --check --dry-run` after generation to prove the model state is fully represented;
- do not delete existing migration package files.

---

# Step 4 — PostgreSQL / Neon-Ready Database Configuration

The current public production deployment must not break merely because Neon has not yet been provisioned.

Implement environment-based database configuration with these semantics:

```text
DATABASE_URL absent
    -> retain current SQLite fallback

DATABASE_URL present
    -> configure Django PostgreSQL from DATABASE_URL
```

Recommended dependencies:

```text
psycopg[binary]
dj-database-url
```

Add them to the appropriate tracked requirements file used by both local and Vercel installs.

Prefer a small testable helper module, for example:

```text
backend/config/database.py
```

rather than embedding difficult-to-test parsing logic directly in settings.

Recommended behavior:

- SQLite fallback remains `BASE_DIR / "db.sqlite3"`.
- `DATABASE_URL` is parsed through `dj-database-url` or an equally standard minimal mechanism.
- Do not hard-code Neon credentials or hostnames.
- Do not invent a connection string.
- Preserve query parameters supplied by the hosted PostgreSQL URL, including SSL mode when present.
- Use serverless-safe connection behavior; do not add long-lived connection assumptions prematurely. A conservative `CONN_MAX_AGE=0` baseline is acceptable.
- Do not make `DATABASE_URL` mandatory in `settings_production.py` during M7.1, because current Vercel production has not yet been connected to Neon and no production provider persistence route is being enabled.

Update `.env.example` (or the repository’s canonical environment example) to document `DATABASE_URL` without any real credential value.

Do not commit `.env` or database credentials.

---

# Step 5 — Tests

Add focused tests for the new foundation.

Recommended test files:

```text
backend/tests/test_provider_persistence_models.py
backend/tests/test_database_configuration.py
```

Adapt names if the repository has a stronger existing convention.

## Model tests must cover at least

- Provider creation/default status/custom fields.
- Provider `provider_id` uniqueness.
- Offering relationship to Provider and JSON capability fields.
- Offering external ID uniqueness.
- ProviderCertification `(provider, code)` uniqueness.
- ProviderPublication can exist before a Provider FK is resolved.
- ProviderPublication history survives provider deletion through `SET_NULL`.
- CatalogueSyncEvent relationship/status/default attempt count.
- Representative JSON structures round-trip without mutation/loss.

Do not test ontology semantics in model tests; serializer/H1-H9 tests already own that responsibility.

## Database configuration tests must cover at least

- no `DATABASE_URL` -> SQLite configuration;
- PostgreSQL `DATABASE_URL` -> PostgreSQL engine/configuration;
- URL query parameters are preserved appropriately;
- no credentials are printed/logged by helper code.

Make tests isolated from the developer’s real environment values.

---

# Step 6 — Regression Verification

From backend root, run at minimum:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
```

Then run the new focused M7.1 tests.

Then run the full local Django test suite:

```powershell
python manage.py test -v 2
```

Also identify and run the repository’s current focused H1-H9/service-discovery verification set if it is separately maintained/documented.

Acceptance requirement:

```text
new M7.1 tests PASS
full existing suite PASS
focused H1-H9 verification PASS (where separately available)
```

Do not weaken, skip, or delete current tests merely to make M7.1 pass.

If an old test is genuinely stale because of an already-approved architecture decision, explain it before changing it and preserve newer working behavior.

---

# Step 7 — Confirm API Non-Regression

M7.1 must not change endpoint routing or public response contracts.

Confirm the current canonical endpoints are untouched:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Confirm M7.1 does NOT make provider lifecycle APIs newly public or enabled.

In particular:

```text
MDC_PROVIDER_PUBLICATION_ENABLED=False
```

must remain the production default.

Do not add `/api/v1/...` routes.

---

# Step 8 — M7.1 Report

Create:

```text
mdc-catalog/docs/Phase_2/11_mdc_v1_m71_postgresql_django_foundation_report.md
```

Include:

1. M7.1 status;
2. scope completed;
3. exact model definitions and relationships;
4. migration generated;
5. database configuration behavior;
6. dependencies added;
7. environment example changes;
8. tests added;
9. exact local test counts/results;
10. H1-H9 regression status;
11. files changed;
12. known limitations/non-goals;
13. whether the code is ready for the Neon provisioning/connection gate;
14. Git commit hash/message.

If all local gates pass, end with exactly:

```text
READY_FOR_M71_NEON_CONNECTION_GATE
```

Otherwise end with:

```text
NOT_READY_FOR_M71_NEON_CONNECTION_GATE
```

and state the blocker.

---

# Step 9 — Git Handling

After verification:

1. inspect `git status` and diff;
2. commit only M7.1 implementation/tests/docs;
3. push to `origin/main`;
4. do not force-push;
5. do not commit secrets, `.env`, `.vercel/`, SQLite DB files, or generated local runtime artifacts.

Suggested implementation commit message:

```text
feat: add M7.1 provider persistence foundation
```

If the report is committed separately, suggested report commit:

```text
docs: report M7.1 persistence foundation verification
```

---

# Scope Restrictions

Do NOT in this task:

- provision Neon;
- change Vercel configuration;
- deploy Preview or Production;
- migrate current YAML providers into the database;
- change H1-H9 loaders/runtime to use PostgreSQL;
- change RDF generation;
- change Fuseki behavior;
- implement sync processing;
- implement/provider-enable publication validation;
- enable provider publication;
- implement provider PATCH/update APIs;
- expose provider/offering APIs to Marketplace;
- update partner API documentation;
- start M7.2.

---

# Final Console Response

Return only:

1. git synchronization/worktree status
2. models implemented
3. migration file/status
4. database configuration implementation/status
5. dependencies added
6. environment example update status
7. focused M7.1 test result/count
8. full local test result/count
9. focused H1-H9 verification result/count
10. canonical public API non-regression status
11. provider-publication production-default status
12. report path/status
13. Git commit hash/message(s)
14. `READY_FOR_M71_NEON_CONNECTION_GATE` or `NOT_READY_FOR_M71_NEON_CONNECTION_GATE`

Do not start the Neon connection gate or M7.2 automatically.
