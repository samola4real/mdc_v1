# MDC v1 M7.5 RDF/Fuseki Synchronization Report

## Outcome

M7.5 is complete. PostgreSQL remains the durable operational source of truth, while the existing harmonized RDF model remains the semantic representation used by service discovery. The implementation consumes the M7.4 publication outbox through an internal management command and replaces the Fuseki default graph with one Turtle document through the Graph Store Protocol.

The public service-discovery runtime and API routes were not changed. Provider publication and catalogue synchronization both remain disabled by default in production. No HTTP synchronization route, versioned `/api/v1/...` route, authentication flow, deployment change, or M7.6 work was introduced.

## Architecture

The synchronization path reuses the two existing canonical components:

```text
PostgreSQL provider catalogue
    -> load_service_discovery_providers_from_db()
    -> build_service_discovery_graph(provider_records=...)
    -> Turtle serialization
    -> one Graph Store Protocol PUT
    -> configured Fuseki default graph
```

The DB repository returns active providers and active offerings in the established canonical shape. The existing RDF generator therefore preserves H1–H9 ordering, evidence, null handling, identifiers, and mappings without a second semantic model. The current curated DB projection remains equivalent to the accepted YAML projection at exactly 673 triples, including sequence-index evidence.

M7.5 replaces the complete graph for each attempt. This correctness-first pilot baseline makes provider suspension and offering deactivation converge naturally because inactive records disappear from the next canonical projection. It also avoids fragile per-triple delete bookkeeping. Whole-graph replacement is suitable for the current catalogue size; it is not presented as the final large-scale synchronization strategy.

## Configuration and safety

The implementation uses environment-based settings:

- `MDC_CATALOG_SYNC_ENABLED` gates every rebuild and outbox attempt.
- `SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT` names the Graph Store endpoint explicitly.
- `FUSEKI_SYNC_TIMEOUT_SECONDS` bounds the HTTP operation.

The endpoint must be an HTTP or HTTPS URL. The timeout must be positive and finite. Production settings default catalogue synchronization to disabled, independently of the local setting. The endpoint is not inferred from a query endpoint.

Synchronization performs one HTTP `PUT` with a `text/turtle` body. Normal results and command failures contain aggregate counts or fixed safe messages. Endpoint values, credentials, response bodies, SQL, and stack traces are excluded. Serialization, configuration, transport, database, and concurrent-change failures are converted to safe error categories.

## Outbox processing and state transitions

The default command selects distinct publications with `pending` or `failed` events and processes each selected publication at most once per invocation. `--limit N` bounds the number of publications, `--publication-id <uuid>` selects one publication, and `--rebuild` performs an explicit bootstrap replacement. Mutually incompatible selections are rejected.

For an outbox attempt:

1. A short `transaction.atomic()` block locks the publication and eligible event rows with `select_for_update()`.
2. Every claimed event becomes `processing`, its `attempt_count` increments exactly once, and its previous safe error state is cleared.
3. The transaction commits before DB projection, RDF generation, and Fuseki network I/O begin.
4. A second short locked transaction finalizes the claimed rows.

On success, claimed events become `succeeded`, `last_error` is cleared, `processed_at` is set, and a publication whose events are all successful becomes `synced` with `completed_at` set. On generation, configuration, transport, database-read, or concurrency failure, claimed events become `failed` with a fixed non-sensitive failure code; the publication becomes `sync_failed` and keeps `completed_at` null. Operational provider and offering writes remain committed regardless of semantic synchronization failure. A later command retries failed events and increments their attempts again. Already succeeded events produce no work.

A catalogue event count/latest-created watermark is checked before and after graph construction and after the PUT. If a lifecycle write commits during an attempt, that attempt remains retryable so the next run reconverges Fuseki to the latest PostgreSQL state. Network I/O is outside row-lock transactions.

## Bootstrap rebuild

`python manage.py sync_service_discovery_catalogue --rebuild` generates and replaces the current complete DB-backed graph without creating a `ProviderPublication` or `CatalogueSyncEvent`. This supports the M7.2 curated import, which intentionally created no publication history. Rebuild uses the same feature flag, endpoint validation, safe failures, timeout, RDF path, and catalogue-change guard as outbox processing.

## Verification

The prepared branch was reviewed against `origin/main` before changes. Its initial 14 focused synchronization tests passed. Review then produced only narrow fixes: finite timeout validation, mutually exclusive publication/limit selection, safe rebuild transport and RDF errors, serialization error wrapping, and rebuild concurrency watermark checks.

| Gate | Result |
| --- | --- |
| Final focused M7.5 SQLite set | 20 run; 20 passed; 0 failed; 0 skipped |
| Managed PostgreSQL focused persistence/sync set | 57 run; 57 passed; 0 failed; 0 skipped |
| `manage.py check` | PASS; no issues |
| `makemigrations --check --dry-run` | PASS; no changes detected |
| Full local suite | 519 run; 510 passed; 0 failed; 9 skipped |
| Separately maintained H1–H9 suite | 230 run; 225 passed; 0 failed; 5 skipped |
| DB-backed/YAML RDF parity | PASS; both graphs contain 673 triples and are equal |
| Git whitespace check | PASS |

Managed PostgreSQL validation used a fresh randomly named task-owned test database. The harness confirmed the PostgreSQL backend, ran the final focused set, and removed only that temporary database. The configured managed catalogue was not reset, migrated, populated, or dropped.

The full-suite skip count changed from the M7.4 baseline of 13 to 9 because four established read-only legacy integration tests detected the available local Fuseki service and ran successfully. The remaining nine skips are the existing opt-in remote harmonized Fuseki suites: four retrieval-integration tests and five matching-alignment tests. The separately maintained H1–H9 suite retains those five remote-alignment skips. M7.5 adds no skip.

All mandatory M7.5 Graph Store writes used mocked HTTP transport. No real remote Fuseki endpoint was used or mutated. The full suite used the available local Fuseki only for the four existing read-only legacy query tests; it did not perform an M7.5 catalogue replacement.

The full suite also verifies the unchanged health, filter, service-discovery, provider validation, provider read, registration, and update contracts. Source/diff inspection confirms that no URL configuration or discovery-runtime selection changed. The stable routes remain unversioned, `/api/v1/...` remains absent, and no sync HTTP route is exposed.

## Files and commits

M7.5 changes are limited to:

- `.env.example`
- `backend/apps/providers/catalogue_sync_service.py`
- `backend/apps/providers/management/commands/sync_service_discovery_catalogue.py`
- `backend/config/settings.py`
- `backend/config/settings_production.py`
- `backend/tests/test_catalogue_sync_service.py`
- `backend/tests/test_catalogue_sync_concurrency.py`
- `backend/tests/test_database_configuration.py`
- `docs/prompts/14_mdc_v1_m75_rdf_fuseki_synchronization_codex_prompt.md`
- this report

The prepared implementation is recorded in commits `ec9c259` through `d87f2aa`. Review fixes and added edge-case tests are in `57b1dce` (`fix: harden M7.5 catalogue synchronization`). This report is committed separately as `docs: report M7.5 RDF Fuseki synchronization`.

## Known limitations and M7.6 boundary

- Synchronization is an operator/scheduler-invoked Django command; M7.5 does not add a durable worker scheduler, monitoring, alerting, or deployment wiring.
- A process terminated after claiming rows can leave events in `processing`; lease/timeout recovery belongs in later operational hardening.
- A concurrent write detected after a completed PUT can leave Fuseki briefly behind PostgreSQL until the failed publication is retried. The safe state makes the need for retry visible.
- Whole-graph replacement trades throughput for simple convergence and should be reevaluated when catalogue size or write rate requires it.
- Real remote Graph Store authentication, network policy, deployment credentials, and production execution are outside this milestone and were not exercised.
- The existing YAML/Fuseki discovery runtime selection remains unchanged. M7.6 may assess external exposure readiness; it has not been started here.
