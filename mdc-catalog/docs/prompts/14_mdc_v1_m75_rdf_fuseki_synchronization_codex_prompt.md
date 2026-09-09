# Codex Prompt — M7.5 RDF/Fuseki Synchronization

**Label:** `[mdc_m75_rdf_fuseki_sync]`  
**Recommended model:** GPT-5.6 Sol  
**Reasoning:** Medium; use High only for a real blocker.  
**Scope:** M7.5 only. Do not start M7.6 automatically.

## Context

Repository: `samola4real/mdc_v1`  
Local project root: `C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog`  
Development branch prepared for this slice: `m75-rdf-fuseki-sync`.

M7.4 is complete and on `origin/main`. PostgreSQL is the durable operational provider source of truth. Successful provider/offering writes create `ProviderPublication(status=sync_pending)` and durable `CatalogueSyncEvent` rows. M7.5 must consume that outbox and synchronize the semantic catalogue without changing the public discovery contract or prematurely starting M7.6.

A ChatGPT implementation may already exist on `m75-rdf-fuseki-sync`. **Do not rewrite it from scratch.** First inspect the branch diff against `origin/main`, then test, review, and minimally fix only what is required for the gates below. This is intentionally a verification/fix task to conserve Codex usage.

## Standing Git authorization

The user authorizes normal fast-forward pushes of completed, passing MDC milestone commits to `origin/main` at `https://github.com/samola4real/mdc_v1` without asking again. Ask only for unusual/destructive operations such as force-push/history rewrite, branch/tag deletion, a different repository/branch destination, unresolved merge conflicts, unexpected unrelated changes, or secret exposure.

## Non-negotiable architecture

- PostgreSQL remains the operational source of truth.
- RDF/Fuseki remains the semantic representation/search layer.
- Existing H1–H9 semantics are not redesigned.
- Service discovery runtime remains unchanged in M7.5; do **not** switch canonical search to PostgreSQL yet.
- Stable API URLs remain unversioned; do not introduce `/api/v1/...`.
- Provider writes remain production-disabled by default.
- No authentication/UI/Marketplace login work in this slice.
- No Vercel/AWS deployment change in this slice.
- No partner API documentation expansion in this slice.
- Cloud-provider-neutral application code only.

## Required M7.5 behavior

### 1. DB-backed RDF rebuild

Use the existing canonical DB repository and existing harmonized RDF generator. Do not build a second RDF mapping.

The synchronized graph must be generated from:

`load_service_discovery_providers_from_db()` → `build_service_discovery_graph(provider_records=...)`

This intentionally includes active providers and active offerings only, preserving the existing canonical ordering/evidence/null behavior.

Provide one reusable service function that rebuilds the complete semantic graph from current PostgreSQL state and sends it to Fuseki.

### 2. Safe Fuseki write mechanism

Use the Fuseki Graph Store Protocol to replace the configured default graph in one HTTP PUT with Turtle (`text/turtle`).

Configuration should be explicit and environment-based, for example:

- `SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT`
- `FUSEKI_SYNC_TIMEOUT_SECONDS`
- `MDC_CATALOG_SYNC_ENABLED`

The graph-store endpoint should normally look like `.../<dataset>/data?default` but must come from environment/configuration, not a hard-coded vendor URL.

Do not print endpoints, credentials, response bodies, SQL, stack traces, or secrets in normal command/report output. Validate that the configured endpoint is HTTP/HTTPS. Production sync must default to disabled.

### 3. Outbox processing

Process `CatalogueSyncEvent` rows with status `pending` or `failed` by publication. One publication attempt should synchronize the complete current DB-backed graph once, then settle all events for that publication.

Required status semantics:

- claim eligible events under a DB transaction/row lock;
- set claimed events `processing`;
- increment `attempt_count` exactly once per attempt;
- on successful Fuseki replacement: mark publication events `succeeded`, clear safe error state, set `processed_at`, set publication `synced`, and set `completed_at`;
- on failed generation/transport/database attempt: mark claimed events `failed`, keep a safe non-sensitive error code/message only, set publication `sync_failed`, leave `completed_at` null;
- a later run must retry failed events and increment attempts again;
- succeeded events must not be reprocessed;
- do not roll back already committed provider/offering operational data merely because semantic synchronization fails.

The whole-graph replacement strategy is deliberate for the pilot: it makes provider suspension, offering deactivation, and future delete semantics converge safely without fragile per-triple delete logic. Document this as a correctness-first pilot baseline, not a claim of final large-scale optimization.

### 4. Concurrency/idempotency

Use `transaction.atomic()` and `select_for_update()` around outbox claim/finalization. Avoid long network calls while holding DB locks: claim/commit first, perform RDF/Fuseki I/O outside the lock, then finalize in a short transaction.

Batch selection must process each publication at most once per command run, even when a failed publication remains retry-eligible after that attempt.

Repeated successful processing must be a no-op for already succeeded publications/events.

### 5. Management command

Add an internal management command, preferably:

`python manage.py sync_service_discovery_catalogue`

Expected modes:

- default: process pending/failed outbox publications;
- `--limit N`: bounded number of publications;
- `--publication-id <uuid>`: retry/process one publication safely;
- `--rebuild`: explicit full DB → Fuseki graph replacement without fabricating publication/outbox history, useful for initial bootstrap after curated import.

Reject incompatible options. Keep output aggregate/safe only. Return a non-zero command result when selected outbox processing contains failures so a scheduler/operator can detect it.

Do not add an HTTP sync/admin endpoint in M7.5.

### 6. Initial/bootstrap catalogue

M7.2 bootstrap import intentionally created no `ProviderPublication` or outbox rows. Therefore `--rebuild` must allow an explicit initial semantic rebuild from the already imported DB catalogue without fabricating audit history.

For the current curated catalogue, DB-backed RDF must still equal the accepted YAML graph: **673 triples**, including the established sequence-index evidence.

### 7. Tests

Add focused tests covering at minimum:

- feature flag disabled: no HTTP call and no outbox mutation;
- missing/invalid graph-store endpoint: safe failure/no secret leakage;
- successful Graph Store PUT uses Turtle and the DB-backed graph;
- baseline imported catalogue graph equals YAML graph and is 673 triples;
- successful pending publication: `pending → processing → succeeded`, publication `sync_pending → synced`, attempt count = 1, completed timestamp set;
- Fuseki HTTP/network failure: event `failed`, publication `sync_failed`, attempt count = 1, no operational provider/offering rollback;
- retry after failure succeeds, attempt count = 2;
- succeeded event is not processed again;
- publication with multiple provider/offering events performs one full-graph HTTP replacement and settles all events;
- provider suspension and/or offering deactivation disappears from the rebuilt semantic graph because the canonical DB repository is active-only;
- batch `--limit` and single `--publication-id` behavior;
- `--rebuild` does not create publication or outbox rows;
- no credential/endpoint/HTTP response body leakage in safe errors/command output;
- current M7.3/M7.4 provider APIs remain unchanged.

Use mocked/local HTTP transport for mandatory tests. Do not require or mutate a shared remote Fuseki dataset unless an explicit opt-in endpoint dedicated to testing is already configured.

### 8. Regression gates

After focused fixes, run:

1. `python manage.py check`
2. `python manage.py makemigrations --check --dry-run`
3. focused M7.5 tests on SQLite/local baseline;
4. focused persistence/sync tests on the managed PostgreSQL validation database using the existing safe temporary-test-database pattern where practical;
5. full local test suite;
6. separately maintained H1–H9 suite.

Baseline before M7.5:

- Full local suite: **486 passed, 13 existing skips**.
- H1–H9: **225 passed, 5 existing skips**.
- M7.4 managed PostgreSQL focused set: **71 passed**.

M7.5 must add no unexplained skip/regression.

For H1–H9 alignment after DB changes, prove that the synchronized DB-backed RDF remains equivalent to the existing harmonized mapping and that existing retrieval/matching tests remain passing. Remote Fuseki tests may remain under their established opt-in guards.

### 9. Runtime/API safety

Verify all of the following remain true:

- `GET /api/health` unchanged.
- `GET /api/catalog/filters` unchanged.
- `POST /api/service-discovery/search` unchanged.
- `/api/v1/...` remains absent.
- provider validation/read/write routes from M7.3/M7.4 remain unchanged.
- provider publication is still production-disabled by default.
- catalogue sync is production-disabled by default.
- YAML/Fuseki discovery runtime selection is not switched in this milestone.
- no sync HTTP route is exposed.

### 10. Report

Create:

`mdc-catalog/docs/Phase_2/16_mdc_v1_m75_rdf_fuseki_synchronization_report.md`

The report must include:

- architecture and why whole-graph GSP replacement is used for this pilot;
- configuration/safety flags;
- DB canonical → RDF → Fuseki flow;
- outbox claim/retry/state semantics;
- transaction boundaries and failure behavior;
- bootstrap `--rebuild` behavior;
- exact focused/PostgreSQL/full/H1–H9 results;
- whether any real remote Fuseki was used (do not include endpoint/credentials);
- files/commits changed;
- known limitations and M7.6 boundary.

Never include credentials, DATABASE_URL, Fuseki endpoint values, hostnames, auth tokens, or response bodies in the report.

## Git completion

If the branch implementation passes all gates:

1. commit any necessary minimal fixes and the report;
2. merge/fast-forward the verified M7.5 work to `main` without rewriting history;
3. push normal fast-forward `main` to `origin/main` under the standing authorization;
4. verify `HEAD == origin/main`, divergence `0 ahead / 0 behind`, and no unexpected tracked changes;
5. preserve unrelated/untracked local user files;
6. do not start M7.6 automatically.

Expected final marker only if all technical and remote-verification gates pass:

`READY_FOR_M76_EXTERNAL_EXPOSURE_READINESS`

Otherwise finish with:

`NOT_READY_FOR_M76_EXTERNAL_EXPOSURE_READINESS`
