# M4 — Automatic lifecycle-to-semantic synchronization (Codex task prompt)

**Scope:** M4 only. **Repository:** `samola4real/mdc_v1`; working project `mdc-catalog/`.
**Prerequisite:** Reviewed M3 merge `b473422ccf80742534b25bc181c156c0f2601eab` is included in fresh `origin/main`. `docs/codex/current_refractor _plan.md` is context, not a substitute for current code and tests.

## User-facing acceptance requirement

The MaaSAI Marketplace uses the existing canonical `/api/` APIs (not the demo frontend) to register a provider, add an offering, PATCH a provider/offering or remove an optional capability, DELETE an offering, or DELETE a provider. **For any lifecycle response claiming completed successful publication, the very next `POST /api/service-discovery/search` must reflect the changed active offering set and capability evidence**, without a Marketplace-issued synchronization request, manual CLI operation, or frontend action. PostgreSQL is authoritative; RDF/Fuseki must reflect that authoritative state. Preserve accepted independent same-category offering IDs from M2 and durable delete tombstones from M3. Route/operation sequences remain excluded.

Do not tell the Marketplace that `sync_pending` is a completed publication. Keep the client workflow simple: lifecycle request -> truthful completed-success response -> next search sees the change. An external Fuseki and PostgreSQL do **not** share an atomic transaction: if sync fails after DB commit, return an explicit **non-completed** response with durable publication ID/pending or failed status, and ensure recovery is possible without re-registering a duplicate provider.

## Safe development setup and scope

1. Fetch `origin/main`, verify M3 merge, branch/head and worktree. Original checkout has uncommitted `.gitignore` and `mdc-catalog/demo-frontend/src/pages/demo/index.js` changes: **do not alter, stash, discard, reset, overwrite, or commit them**. Use a separate clean linked Git worktree from current origin/main on `phase4/automatic-semantic-sync` (or a clearly named M4 follow-up). Stop with an accurate blocker if unable to isolate.
2. Inspect **only** current live code relevant to M4: lifecycle handlers/writes and transaction boundaries, publication/outbox models (including M3 DELETE), `apps/providers/catalogue_sync_service.py`, current sync management command, `service_discovery_db_repository.py`, ontology RDF generator and RDF identity mappings, `apps/search/service_discovery_runtime_search.py`, Fuseki query client, in-process RDF and checked-in YAML fallbacks, current settings/environment flags and relevant sync/discovery/lifecycle tests. Record the **actual** active discovery source selection; do not assume a successful Graph Store PUT means canonical search reads that same dataset.
3. No frontend/demo modifications, no M5 deployment or external Vercel/Neon/Fuseki writes, no new `/api/v1/` paths, no changed public search payload/response fields, no permanent removal of authentication code, no change to required DELETE ETag or M2 offering IDs. Do not introduce provider-specific branching or recreate a separate source-of-truth store.

## Implementation tasks

4. Implement a narrowly scoped, **explicit opt-in** automatic publication mode (reusing existing `MDC_CATALOG_SYNC_ENABLED` plus any single necessary additional mode flag if required) with safe existing production defaults untouched. Existing operator-managed sync and non-pilot settings must continue working. Enabled pilot mode should synchronize **after the lifecycle transaction commits**, never do HTTP calls to Fuseki while holding a database transaction/row lock. Do not depend on Vercel continuing work after sending its HTTP response. Do not use `transaction.on_commit` side effects inside Django `TestCase` without testing the real commit semantics.
5. Reuse the existing durable publication/outbox and DB -> RDF graph generation. Handle CREATE, second same-category OFFERING CREATE, PROVIDER/OFFERING PATCH, optional attribute removal, M3 OFFERING DELETE and PROVIDER DELETE. The graph must be derived from **current active DB-backed state**, remove obsolete provider/offering/capability triples (including for deleted rows), and preserve separate same-category identities, provenance and evidence. Keep retained tombstones/outbox events safe when rows no longer exist; do not resurrect deleted entities from historical publications or checked-in seed files.
6. Resolve **read-after-write visibility**: prove the query endpoint and Graph Store endpoint target the same dataset/graph. In the opt-in mode, canonical discovery must not silently fall back to stale checked-in RDF/YAML and return outdated offerings after a committed mutation or deletion. Choose an explicit, documented policy (for example, require authoritative synchronized Fuseki for this mode and return a safe `503` if it is unavailable). Preserve non-pilot fallback behavior unless there is a demonstrated correctness defect. Treat successful sync as confirmed **query visibility of the committed revision**, not merely RDF serialization or an HTTP PUT response.
7. Concurrency/idempotency: inspect the current watermark/claim/lease implementation for overlapping writes and simultaneous rebuilds. Prevent stale graph PUTs from overwriting a newer graph and old event retries from restoring deleted offerings. Use bounded retries/timeouts safe for serverless requests and retain failed/pending events for automated recovery. Do not claim a globally atomic Postgres+Fuseki transaction. Document exactly when a lifecycle write is persisted but not yet searchable, and how a duplicate retry is avoided; prefer no additional Marketplace-facing synchronization endpoint.
8. Keep the HTTP lifecycle contract backward-compatible where possible: already-successful `201` (create), `200` (PATCH/DELETE) and IDs/ETags stay stable. In auto mode, return completed publication status **only when verified searchable**; if DB commit succeeded but semantic sync failed, use a clearly non-completed HTTP/error response containing safe `publication_id` and pending/failed status, not a misleading 2xx-completed receipt. Define a practical recovery strategy for failed events (e.g. the existing command used by an **automatic scheduled operator/worker**, with a safe M5 deployment hook); the Marketplace must not need to request manual synchronization. Preserve current responses when auto mode is off, including `sync_pending`.
9. Identify the minimum Vercel/Fuseki/Neon requirements to deploy this safely in M5: environment variable names (never secret values), same-dataset query and Graph Store URLs, reachable write credentials for Fuseki if required, appropriate timeouts, DB migrations and automated retry mechanism if necessary. Do not apply any deployed configuration or create an external scheduler in M4. Do not claim M4 has passed a live Vercel test.

## Acceptance tests and regression evidence

Use disposable Django test DBs, in-memory RDF, mocked HTTP Fuseki where necessary; use transaction-aware tests for post-commit hooks and concurrent-event ordering, and realistic query-side visibility checks. Verify:
- provider registration -> success -> next canonical search contains its offering;
- adding a second same-category offering -> both distinct offerings with correct evidence;
- provider/offering PATCH -> next search uses updated values, no stale evidence;
- removing exactly one capability -> next search no longer matches the removed declared value, retained fields unaffected;
- DELETE offering -> only that offering absent, sibling still present;
- DELETE provider -> all related offerings absent, unrelated provider intact;
- graph-store failure/timeout/query failure -> **no false completed-success response**, committed state/outbox preserved and retryable; recovery eventually converges without duplicate mutation;
- concurrent writes/retries -> no stale overwrite or deleted-offering resurrection;
- authoritative Fuseki unavailable in auto mode -> no stale YAML/local-RDF fallback masquerading as current data; non-pilot fallback remains tested;
- secured and explicitly opted-in no-auth pilot modes, existing ETags/DELETE preconditions and canonical public contract remain intact.

Run targeted sync/lifecycle/discovery tests, full Django suite when feasible, `manage.py check`, migration consistency, and `git diff --check`. If HTTP mocks are insufficient to prove real remote query visibility, label that limitation **for M5** rather than claiming a live end-to-end pass. Avoid tests against real provider records or production data.

## Reporting and stop gate

Write `docs/codex/Reports/M4_automatic_semantic_synchronization_report.md` with current commit/worktree and preserved-original-checkout evidence; inspected paths; exact opt-in settings; implementation changed files; actual publication/search consistency guarantee and failure/recovery semantics; tests with commands/counts/skips; comparison of normal/non-pilot and pilot behavior; outstanding M5 deployment steps (especially whether any scheduler is required); **not merged/not deployed** state and final pushed commit SHA in completion summary.

Commit scoped M4 code/tests/docs/report on the focused branch, push to personal GitHub repository only, **do not merge or deploy**, and stop awaiting review before M5.
