# M6-A Marketplace integration and release-readiness report

## Outcome

M6-A is complete on `phase4/marketplace-integration`. The accepted MDC v1 API
was frozen and packaged for Marketplace integration without changing runtime
semantics or adding versioned routes. The package includes a current contract,
validated request/response examples, a 29-request Postman flow, a plenary and
recovery runbook, a Production-readiness checklist, and a joint-test checklist.

The package is ready for a joint Marketplace test, but that test was not
performed during M6-A. Production/plenary enablement and a release tag remain
gated by durable protected Fuseki hosting, owned retry operations, approved
deployment configuration/migrations, and actual Marketplace-originated test
evidence.

## Source and branch

| Item | Value |
| --- | --- |
| Requested prompt commit | `4b14038cba79e0dfca2c270200d300d33157e906` |
| Latest `origin/main` baseline | `3388d3dfeaaecf2d2f57f4d9d9e1720198846c1d` |
| Accepted M5-B merge in ancestry | `52b8d1fe26fa4acf74b8d38e67fad30ffb42b9af` |
| Branch | `phase4/marketplace-integration` |
| Clean linked worktree | `C:\Users\Elahi\Desktop\mdc_v1_m6a_worktree` |
| Final branch commit | Recorded in the review handoff because Git assigns it when this report is committed |

The original checkout's pre-existing `.gitignore` and
`mdc-catalog/demo-frontend/src/pages/demo/index.js` changes remained untouched.

## Frozen endpoint list

The following existing `contract_version: 1.0` routes are frozen for partner
integration:

```text
GET                 /api/health
GET                 /api/catalog/filters
POST                /api/service-discovery/search
POST                /api/provider-publication
POST                /api/provider-publication/validation
GET/PATCH/DELETE    /api/providers/{provider_id}
GET/POST            /api/providers/{provider_id}/offerings
GET/PATCH/DELETE    /api/offerings/{offering_id}
```

The route-table contract test proves the canonical prefix is `/api/` and no
partner `/api/v1/` route was introduced.

The integration guide cross-checks purpose, request fields, representative
responses, ETag/If-Match rules, HTTP error classes, PostgreSQL mutation,
automatic synchronization, and post-commit failure recovery for every route.
It explicitly freezes these material rules:

- provider aggregates support multiple independent same-category offerings;
- `offering_id` is immutable identity and category is classification;
- process/route sequence fields are excluded;
- optional maps use whole-selected-map PATCH replacement;
- operational DELETE is permanent while minimal redacted audit/outbox history
  remains;
- automatic success requires query-visible revision verification;
- Marketplace has no synchronization API and must not blindly replay an
  accepted non-idempotent write after synchronization failure.

## Partner handoff package

New assets under `docs/Partner_API/`:

- `MaaSAI_MDC_M6_Marketplace_Integration_Guide.md`
- `MaaSAI_MDC_M6_Marketplace_Integration.postman_collection.json`
- `MaaSAI_MDC_M6_Marketplace_Integration.postman_environment.json`
- `MaaSAI_MDC_M6_Plenary_Runbook.md`
- `MaaSAI_MDC_M6_Production_Readiness_Checklist.md`
- `MaaSAI_MDC_M6_Marketplace_Joint_Test_Checklist.md`

The one lifecycle guide formerly tracked under the lower-case path was safely
case-normalized to `docs/Partner_API/`, preserving its content and history. It
now links the M6 handoff package and labels the M5/M5-A collections as retained
historical evidence. Only the canonical partner-documentation directory remains.

### Postman package

| Item | Result |
| --- | --- |
| Collection | `MaaSAI_MDC_M6_Marketplace_Integration.postman_collection.json` |
| Environment | `MaaSAI_MDC_M6_Marketplace_Integration.postman_environment.json` |
| Ordered requests | `29` |
| Folders | Preconditions `3`; lifecycle `16`; destructive cleanup `10` |
| Base URL | Configurable placeholder; no baked Preview/Production URL |
| Identity | Unique generated `marketplace_m6_*` provider and two explicit offerings |
| Security profile | No bearer or actor header; explicitly scoped to an approved no-auth/no-actor pilot |
| Concurrency | Captures and reuses provider/offering strong ETags; checks `428` and stale `412` |
| Semantic checks | Automatically skipped unless `automatic_sync_enabled=true` |
| Cleanup | Clearly separated destructive folder; verifies offering sibling and final absence |

The collection validates `completed/synced/succeeded` in automatic mode and
`accepted/sync_pending/pending` when automatic mode is deliberately disabled.
M5 and M5-A evidence collections were preserved.

## Documentation and asset validation

A focused test was added at
`backend/tests/test_m6a_marketplace_handoff.py`. It:

- asserts every frozen route and selected reverse-resolved URL;
- asserts the API route table has no `v1/` partner prefix;
- extracts the literal registration, second-offering, provider PATCH, offering
  PATCH, selected-map removal, and canonical search JSON examples from the guide
  and validates them through current serializers;
- parses both Postman JSON files;
- verifies collection name and 29-request count;
- verifies no Authorization/actor header, Production URL, `/api/v1/`, or secret
  environment key;
- verifies semantic requests are conditional and destructive cleanup is
  separated.

Additional Node validation parsed all Postman JSON and compiled the collection's
71 script blocks/lines without syntax errors.

## Regression results

| Check | Result |
| --- | --- |
| M6-A contract/asset test | `3 passed` |
| Focused lifecycle/sync/search plus M6-A | `136 passed` |
| Full isolated Django suite | `582 passed, 13 skipped` |
| `manage.py check` | Passed; 0 issues |
| `makemigrations --check --dry-run` | Passed; no changes detected |
| Postman JSON parse | Both assets valid |
| Postman request/script validation | 29 requests; 71 script blocks/lines parsed |
| Route table / no `/api/v1/` | Passed in automated contract test |
| `git diff --check` | Passed before reporting; repeated before commit |

The 13 skips are the repository's designed optional external-integration tests.
All regression runs used disposable Django test databases and
`FUSEKI_BASE_URL=http://127.0.0.1:1`, so M6-A did not query or modify the real
local Fuseki service.

## Reused accepted evidence, not repeated live

M6-A did not redeploy or repeat M5's live infrastructure exercise. It reuses
the accepted evidence already merged to `main`:

- M5-A: Vercel Preview + isolated Neon PostgreSQL lifecycle, **35 requests / 81
  assertions / 0 failures**;
- M5-B: isolated Preview + disposable Fuseki flow, **39 requests / 88
  assertions / 0 failures**, including revision verification, authoritative
  immediate discovery, update visibility, and delete absence.

No claim is made that a durable Production Fuseki environment or a Marketplace
client has been validated.

## Joint Marketplace test status

**Prepared, not executed.** No Marketplace-originated call set, Marketplace
client environment, or joint evidence was available in this task. The checklist
defines the exact URL placeholder, endpoint order, retained IDs/ETags,
success/error semantics, semantic-visibility proof, cleanup, and evidence to
capture. Its status must not change until the Marketplace team performs the
test.

## Remaining Production/plenary gates

1. Durable remotely hosted and protected Fuseki query + default Graph Store
   endpoints; temporary tunnels are not acceptable.
2. Same-origin/same-dataset endpoint verification and scoped credential review.
3. Production/plenary PostgreSQL backup, connectivity, and migration
   verification through `providers.0004_cataloguesynclease`.
4. Explicit approval of every Production/plenary environment flag and secret
   delivery through the approved channel.
5. Owned, monitored worker/scheduler for pending/failed outbox retries and stale
   processing recovery.
6. Explicit approval for any deployment-specific no-auth/no-actor pilot mode.
7. Final disposable smoke test and complete cleanup on the intended environment.
8. Actual joint Marketplace integration test with retained redacted evidence.
9. Named incident, rollback, database, and Fuseki owners.
10. Release approval; only then may a release tag be created.

## Files changed

- `backend/tests/test_m6a_marketplace_handoff.py`
- `docs/Partner_API/MaaSAI_MDC_M6_Marketplace_Integration.postman_collection.json`
- `docs/Partner_API/MaaSAI_MDC_M6_Marketplace_Integration.postman_environment.json`
- `docs/Partner_API/MaaSAI_MDC_M6_Marketplace_Integration_Guide.md`
- `docs/Partner_API/MaaSAI_MDC_M6_Marketplace_Joint_Test_Checklist.md`
- `docs/Partner_API/MaaSAI_MDC_M6_Plenary_Runbook.md`
- `docs/Partner_API/MaaSAI_MDC_M6_Production_Readiness_Checklist.md`
- `docs/Partner_API/mdc_v1_trusted_provider_lifecycle_integration.md`
- `docs/codex/current_refractor _plan.md`
- `docs/codex/Reports/M6A_marketplace_integration_release_readiness_report.md`

## Safety confirmation

- Production was not inspected, configured, deployed, or promoted.
- No AWS, Cloudflare, DNS, tunnel, or durable Fuseki configuration was created.
- The real `mdc-fuseki` container/dataset and provider records were not accessed
  or modified.
- The original checkout and its unrelated local modifications were untouched.
- No release tag was created.
- The branch was not merged to `main`.
