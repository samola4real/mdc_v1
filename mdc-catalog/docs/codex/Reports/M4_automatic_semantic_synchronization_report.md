# M4 automatic semantic synchronization report

## Baseline, branch, and worktree

- Milestone: M4 only.
- Focused branch: `phase4/automatic-semantic-sync`.
- Baseline and prompt commit: `a81c6ad82eb0677abf265f99a5974715c71b6f22`.
- Reviewed M3 merge confirmed in baseline ancestry:
  `b473422ccf80742534b25bc181c156c0f2601eab`.
- Implementation commit: `95f69f6d7faa75687d975bd1cce2bc918b6e18e9`.
- Clean linked worktree:
  `C:\Users\Elahi\Desktop\mdc_v1_m4_worktree`.
- The original checkout remained on `main`. Its pre-existing `.gitignore` and
  `mdc-catalog/demo-frontend/src/pages/demo/index.js` modifications were not
  modified, staged, stashed, discarded, reset, overwritten, or copied.
- No frontend/demo code was changed. Nothing was merged or deployed, and no
  Vercel, Neon, Fuseki, production, or real-provider write was performed.

## Inspected live implementation

The implementation was based on the current lifecycle handlers/write service,
publication/outbox and M3 tombstones, `catalogue_sync_service.py`, its management
command, the DB-backed canonical repository, RDF generator/identity mappings,
runtime search and Fuseki query client, settings, migrations, and focused
lifecycle/sync/search tests.

The actual pre-M4 discovery source order was:

1. remote harmonized Fuseki plus H5;
2. checked-in local RDFLib graph plus H5 after a recoverable remote failure;
3. harmonized YAML records plus H5 after a recoverable RDF failure;
4. redacted `503` only if all three failed.

Therefore a successful Graph Store PUT alone was not enough to guarantee that
the next canonical search read the new database-derived graph. In particular,
fallback data could still contain a deleted or outdated offering. M4 changes
this behavior only in the explicit automatic mode described below.

## Opt-in configuration

Automatic lifecycle publication requires both settings:

```text
MDC_CATALOG_SYNC_ENABLED=True
MDC_CATALOG_AUTO_SYNC_ENABLED=True
```

Both remain `False` by secure production default. `MDC_CATALOG_SYNC_ENABLED`
continues to gate every graph mutation and the existing operator command.
`MDC_CATALOG_AUTO_SYNC_ENABLED` is the single new mode flag; it enables
after-commit publication for lifecycle responses and authoritative Fuseki-only
canonical search.

Automatic mode also requires:

```text
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT=https://<host>/<dataset>/sparql
SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT=https://<host>/<dataset>/data?default
FUSEKI_TIMEOUT_SECONDS=<bounded positive duration>
FUSEKI_SYNC_TIMEOUT_SECONDS=<bounded positive duration>
```

The query and Graph Store URLs are parsed and required to use the same scheme,
host, port, and dataset path. The Graph Store URL must select the default graph.
Optional write authentication continues to use
`SERVICE_DISCOVERY_FUSEKI_USERNAME` and
`SERVICE_DISCOVERY_FUSEKI_PASSWORD`; no credential values belong in source or
this report.

Existing auth, actor, PATCH concurrency, DELETE ETag, offering identity, route,
and public search-schema behavior is unchanged. Explicit no-auth/actor pilot
mode remains supported; secure mode still requires its bearer and actor.

## Publication and search consistency guarantee

Every lifecycle write first completes its existing atomic PostgreSQL transaction
and durable publication/outbox creation. The API view calls synchronization only
after the write service returns. Automatic synchronization explicitly refuses
to start while Django is inside an open atomic block, and tests use
`TransactionTestCase` to exercise real commit boundaries rather than deferred
`on_commit` behavior.

After commit, M4:

1. acquires a database-visible global `CatalogueSyncLease` in a short
   transaction, then releases the transaction before RDF generation or HTTP;
2. builds the complete graph only from current active PostgreSQL providers and
   offerings, never publication snapshots, tombstones, YAML, or stale RDF;
3. adds a non-business catalogue revision marker derived from committed outbox
   state;
4. checks the outbox watermark before and after graph construction/PUT;
5. replaces the configured Fuseki default graph;
6. queries the marker through the configured canonical Fuseki query endpoint;
7. rechecks the watermark and marks the publication/events succeeded only when
   the queried revision is the committed revision.

The full rebuild naturally removes obsolete provider, offering, and capability
triples. Separate M2 same-category offering IDs remain separate RDF resources.
M3 DELETE tombstones/events remain durable, but deleted operational entities are
not read from history and cannot be resurrected by an old UPSERT retry.

An automatic-mode lifecycle response retains the established HTTP status (`201`
for creation; `200` for PATCH/DELETE) and reports completion only after those
checks:

```json
{
  "status": "completed",
  "publication_status": "synced",
  "sync_status": "succeeded"
}
```

Canonical search in automatic mode verifies the current revision both before
and after its Fuseki candidate/evidence query. If a lifecycle commit or graph
change races with the search, the request safely returns `503` rather than a
stale/mixed result. Local RDF/YAML fallback is disabled in this mode. Thus any
lifecycle response that claims completed publication has query-visible evidence,
and the next stable canonical search either reflects current state or explicitly
fails unavailable; it never masquerades stale fallback as current data.

When automatic mode is off, behavior stays backward compatible: lifecycle
responses remain `accepted` with `sync_pending`/`pending`, the operator-managed
command remains available, and the existing Fuseki -> RDFLib -> YAML search
fallback order remains active.

## Concurrency, failure, and recovery

PostgreSQL and external Fuseki are not globally atomic. M4 reports that boundary
honestly.

- The `CatalogueSyncLease` migration creates and seeds one database-visible
  catalogue-replacement lease. Competing request/worker publishers do not issue
  overlapping full-graph PUTs. An overlapping lifecycle write is still committed
  but receives a non-completed `503` with pending state.
- A catalogue change detected around a PUT triggers a bounded rebuild (maximum
  three attempts) while the publisher owns the lease. This repairs a stale PUT
  with a current full graph before success can be recorded.
- A query-visible revision marker fences Graph Store/query dataset mistakes and
  stale graph state. Endpoint identity is validated before automatic mutation.
- Transport failure, timeout, RDF/configuration failure, or query verification
  failure leaves the operational mutation committed and its events
  pending/failed and retryable. The HTTP response is `503`, includes the safe
  `publication_id`, IDs/ETag, honest publication/sync state, and
  `catalogue_publication_incomplete`; it never claims completion.
- Marketplace clients must not repeat registration or another non-idempotent
  lifecycle mutation. Recovery retries the outbox publication, rebuilding from
  current DB state, so there is no duplicate provider mutation.
- The existing processing lease recovery remains available. Expired global sync
  ownership is also replaceable after the same configured lease interval.

In automatic mode, the existing management command now performs the same query
verification. M5 should automatically schedule both recovery and retry, for
example as two trusted worker invocations:

```text
python manage.py sync_service_discovery_catalogue --recover-stale
python manage.py sync_service_discovery_catalogue --limit 100
```

No Marketplace-facing synchronization endpoint was added.

## Files changed

- `mdc-catalog/.env.example`
- `mdc-catalog/backend/apps/api/views/post_views.py`
- `mdc-catalog/backend/apps/providers/catalogue_sync_service.py`
- `mdc-catalog/backend/apps/providers/management/commands/sync_service_discovery_catalogue.py`
- `mdc-catalog/backend/apps/providers/models.py`
- `mdc-catalog/backend/apps/providers/migrations/0004_cataloguesynclease.py`
- `mdc-catalog/backend/apps/search/service_discovery_runtime_search.py`
- `mdc-catalog/backend/config/settings.py`
- `mdc-catalog/backend/config/settings_production.py`
- `mdc-catalog/backend/tests/test_catalogue_sync_concurrency.py`
- `mdc-catalog/backend/tests/test_catalogue_sync_service.py`
- `mdc-catalog/backend/tests/test_database_configuration.py`
- `mdc-catalog/backend/tests/test_m1_lifecycle_pilot_readiness.py`
- `mdc-catalog/backend/tests/test_m4_automatic_semantic_sync.py`
- `mdc-catalog/backend/tests/test_service_discovery_runtime_search.py`
- `mdc-catalog/docs/Partner_API/mdc_v1_trusted_provider_lifecycle_integration.md`
- `mdc-catalog/docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md`
- `mdc-catalog/docs/codex/Reports/M4_automatic_semantic_synchronization_report.md`

The Windows checkout reports the already-tracked partner directory with
lowercase casing in Git output; it is the same requested Partner API document.

## Verification

All tests used disposable Django databases, in-memory RDF, and mocked Fuseki
Graph Store/query behavior. No external endpoint or provider record was used.

Pre-change focused baseline:

```text
python manage.py test tests.test_m3_lifecycle_deletion tests.test_catalogue_sync_service tests.test_catalogue_sync_recovery tests.test_catalogue_sync_concurrency tests.test_service_discovery_runtime_search tests.test_service_discovery_search_endpoint --verbosity 1
54 passed; 0 failed; 0 skipped
```

Focused lifecycle/sync/discovery regression:

```text
python manage.py test tests.test_provider_lifecycle_write_api tests.test_provider_detail_api tests.test_m1_lifecycle_pilot_readiness tests.test_m2_multi_offering_management tests.test_m3_lifecycle_deletion tests.test_m4_automatic_semantic_sync tests.test_m76_external_exposure_readiness tests.test_catalogue_sync_service tests.test_catalogue_sync_recovery tests.test_catalogue_sync_concurrency tests.test_service_discovery_runtime_search tests.test_service_discovery_search_endpoint tests.test_service_discovery_fuseki_service tests.test_service_discovery_rdf_generator --verbosity 1
131 passed; 0 failed; 0 skipped
```

Final M4 automatic-path tests:

```text
python manage.py test tests.test_m4_automatic_semantic_sync --verbosity 1
5 passed; 0 failed; 0 skipped
```

Final complete local Django suite:

```text
python manage.py test --verbosity 1
579 passed; 13 skipped; 0 failed
```

The 13 skips are the repository's optional external integration tests. No live
Fuseki test was claimed.

Static and migration checks:

```text
python manage.py makemigrations --check --dry-run
No changes detected

python manage.py check
System check identified no issues (0 silenced)

git diff --check
No errors
```

Migration `0004_cataloguesynclease` was applied successfully by the disposable
test databases in focused and full runs.

## M5 deployment requirements and limitations

M4 did not configure or deploy anything. Before enabling this in M5:

1. Apply database migration `0004_cataloguesynclease`.
2. Confirm the application can reach both Fuseki endpoints and that query and
   Graph Store operate on the same default graph/dataset.
3. Configure query/write endpoints, optional write credentials, and bounded
   timeouts without logging secrets.
4. Enable `MDC_CATALOG_SYNC_ENABLED` and
   `MDC_CATALOG_AUTO_SYNC_ENABLED` only in the approved environment after those
   checks; production defaults remain off.
5. Ensure the serverless/request execution limit safely exceeds DB graph build,
   one bounded Graph Store PUT, and revision/candidate/evidence queries. If that
   latency is unsuitable for Vercel, use a durable private application/worker
   boundary before enabling automatic request publication.
6. Create an automatic scheduled trusted worker for stale-lease recovery and
   pending/failed outbox retries. M4 supplies the safe command behavior but does
   not create a scheduler.
7. Perform live Vercel + Neon + Fuseki read-after-write validation in M5. HTTP
   mocks prove application semantics, not remote proxy, credential, or Fuseki
   deployment behavior.

The branch is not merged to `main` and nothing was deployed to Vercel. Stop after
M4 and await review before any M5 work.
