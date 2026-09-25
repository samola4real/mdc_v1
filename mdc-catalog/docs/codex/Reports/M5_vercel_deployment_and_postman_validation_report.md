# M5 Vercel deployment and Postman validation report

## Outcome

**M5 deployment is blocked and was not claimed complete.** The repository,
existing Vercel project, intended Neon database, and existing local Fuseki were
audited. Local regression passed, and reusable no-auth Postman assets were
added. No M5 Preview or Production deployment was created because the only
available remote Fuseki path was an expired temporary Cloudflare Quick Tunnel,
and the execution environment did not authorize exposing the local authenticated
Fuseki service through a new public tunnel. M4's same-dataset write/query and
query-visible-revision guarantees were therefore not weakened or bypassed.

The intended Neon database also has provider migrations `0003` and `0004`
unapplied. Once the remote Fuseki dependency was blocked, those Production
migrations were deliberately not applied as an isolated partial rollout.

## Source, branch, and isolation

| Item | Value |
| --- | --- |
| Repository | `https://github.com/samola4real/mdc_v1.git` |
| Prompt/baseline commit | `3a69b2830a19700d9abe5ed81df0797b509418c6` |
| Required M4 merge | `d6c7f5e3879b04489c2fe64575a2abb7e4127706` (confirmed in baseline ancestry) |
| M5 branch | `phase4/deployment-validation` |
| Clean linked worktree | `C:\Users\Elahi\Desktop\mdc_v1_m5_worktree` |
| M5 deployed commit | None |

The original checkout remained on `main`. Its pre-existing `.gitignore` and
`mdc-catalog/demo-frontend/src/pages/demo/index.js` edits were not modified,
staged, stashed, discarded, reset, copied, or committed. No branch was merged.

## Existing Vercel project inspection

The clean worktree was linked to the existing project only:

| Item | Evidence |
| --- | --- |
| Scope/project | `mdc19/maasai-mdc-v1` |
| Project ID | `prj_DekMQdOYuuH0A5yNsCkFmOC4uD9j` |
| Existing Production deployment | `https://maasai-mdc-v1-588we5lou-mdc19.vercel.app` |
| Existing stable alias | `https://maasai-mdc-v1.vercel.app` |
| Existing deployment ID/status | `dpl_GmWLQStvb3qo551uYYUv4zLiW1XK`, Ready |
| Existing deployment creation | 2026-09-09 19:26 EEST |
| Existing runtime | Build log: `Using Python 3.12 from .python-version` |
| M5 Preview | Not created |
| M5 Production | Not created; existing Production remained unchanged |

The installed Vercel CLI did not expose source-commit metadata for the older
Production deployment. No M5 commit was deployed, so there is no M5 deployed
commit to report.

## Configuration presence audit

Only variable names/scopes and safe non-secret state were inspected. Stored
secret values were not printed or copied into this report.

| Requirement | Production before M5 | Preview before M5 | M5 result |
| --- | --- | --- | --- |
| `DATABASE_URL` | Present/encrypted; existing live app works | Missing | Unchanged |
| `DJANGO_SECRET_KEY` | Present/encrypted | Present/encrypted | Unchanged |
| `DJANGO_SETTINGS_MODULE` | Present/encrypted | Present/encrypted | Unchanged |
| `DJANGO_ALLOWED_HOSTS` | Present/encrypted | Present/encrypted | Unchanged |
| CORS/CSRF explicit variables | Not listed | Not listed | No change required for the blocked CLI-only gate |
| `MDC_PROVIDER_PUBLICATION_ENABLED` | Present/encrypted | Present/encrypted | Required M5 value not applied |
| `MDC_PROVIDER_VALIDATION_ENABLED` | Present/encrypted | Missing | Required M5 value not applied |
| `MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED` | Present/encrypted | Missing | Existing Production behavior proved it remained enabled |
| `MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED` | Present/encrypted | Missing | Required M5 value not applied |
| `MDC_PROVIDER_CONCURRENCY_REQUIRED` | Present/encrypted | Missing | Required M5 value not applied |
| `MDC_CATALOG_SYNC_ENABLED` | Present/encrypted | Missing | Required M5 value not applied |
| `MDC_CATALOG_AUTO_SYNC_ENABLED` | Missing | Missing | Blocked |
| `MDC_DEMO_API_ENABLED` | Present/encrypted | Present/encrypted | Existing Production demo route remained 404 |
| Fuseki query endpoint | Present; old Quick Tunnel was unreachable | Missing | Blocked |
| Fuseki Graph Store endpoint | Missing | Missing | Blocked |
| Fuseki username/password | Missing | Missing | Blocked |
| `FUSEKI_TIMEOUT_SECONDS` | Present/encrypted | Present/encrypted | Unchanged |
| `FUSEKI_SYNC_TIMEOUT_SECONDS` | Missing | Missing | No separate override applied |

The ignored local operator configuration was inspected without printing values.
It points to PostgreSQL on a Neon host and contains same-dataset local Fuseki
query and default-graph Graph Store URLs plus paired write credentials. The
configured query and Graph Store origin, port, and dataset path matched. The
existing `mdc-fuseki` container was restarted without recreation or data reset,
and the repository's non-mutating preflight passed:

```text
SPARQL ASK reachable: PASS (graph has triples)
authenticated Graph Store HEAD: 200
same local dataset: PASS
graph write attempted: NO
```

The container was restored to its original stopped state after this check.

## Database and migration audit

Read-only production-settings inspection selected `postgresql`, and the host
matched the intended Neon service. Migration status was:

```text
[X] providers.0001_initial
[X] providers.0002_canonical_parity_fields
[ ] providers.0003_alter_providerpublication_operation
[ ] providers.0004_cataloguesynclease
```

No database was reset or dropped. Migrations `0003` and `0004` were not applied
after the external dependency gate failed, avoiding a partial Production
rollout with no deployable authoritative Fuseki path.

## Existing Production baseline (non-mutating)

These checks describe the pre-M5 deployment, not an M5 acceptance run:

| Request | Status | Evidence / latency |
| --- | ---: | --- |
| `GET /api/health` | 200 | contract `1.0`; 3234 ms cold request |
| `GET /api/catalog/filters` | 200 | contract `1.0`; 159 ms |
| canonical `POST /api/service-discovery/search` | 200 | contract `1.0`; zero results for the disposable bracket probe; 415 ms |
| `POST /api/provider-publication/validation` without auth | 401 | `trusted_lifecycle_auth_required`; 183 ms |
| `GET /api/demo/health` | 404 | demo API disabled; 150 ms |
| `POST /api/v1/service-discovery/search` | 404 | versioned route absent; 184 ms |

The validation payload used the non-mutating identifier
`postman_m5_validation_only`. No provider/offering lifecycle mutation was made,
so no disposable live acceptance provider ID exists for this blocked run.

## Blocking dependency and deployment decision

The old Production Fuseki query endpoint targets a temporary Cloudflare host
and is no longer reachable. The only available working Fuseki is the local
authenticated `mdc` dataset. Starting a dedicated public Quick Tunnel to that
service was rejected by the execution environment's security approval gate
because it would expose a locally authenticated data service to an external
destination without separate explicit authorization for that tunnel scope.

Without a remotely reachable same-dataset query and Graph Store pair, Vercel
cannot safely perform M4's graph replacement and query-visible revision
round-trip. Therefore this run did not:

- add or update Vercel environment variables;
- create a Preview deployment;
- run lifecycle writes against Preview or Production;
- apply Neon migrations;
- promote or create a Production deployment;
- disable authentication or actor requirements on the existing Production
  deployment;
- weaken authoritative search, revision verification, or truthful M4 `503`
  behavior.

Request duration/size suitability could not be measured because the remote
write/query gate was unavailable.

## Recovery automation

The current Vercel project is a request-driven Python deployment. Vercel's
scheduler invokes HTTP routes; it cannot directly execute the two existing
Django management commands as a durable private worker:

```text
python manage.py sync_service_discovery_catalogue --recover-stale
python manage.py sync_service_discovery_catalogue --limit 100
```

Adding a scheduler-only HTTP sync endpoint would conflict with the prompt's
instruction not to add another Marketplace-facing management API. A durable
private scheduler/worker remains an M6/release operational requirement. The
existing truthful `503 catalogue_publication_incomplete` and outbox retry
semantics remain unchanged.

## Postman assets

Added a secret-free Postman collection and environment template under the
partner API documentation:

- `docs/Partner_API/MaaSAI_MDC_M5_Lifecycle.postman_collection.json`
- `docs/Partner_API/MaaSAI_MDC_M5_Lifecycle.postman_environment.json`

The 27-request ordered collection generates a unique `postman_m5_*` provider,
uses no bearer/actor headers, captures ETags, covers registration, a second
same-category offering, PATCH, selected-map attribute removal, DELETE, immediate
canonical-search assertions, and the required 400/409/412/428/404 negative
checks. Its default `base_url` is a non-routable replacement placeholder so it
cannot accidentally mutate the old Production deployment. Both JSON files
parsed successfully, and the environment contains no token/password/secret
field.

## Local verification

| Check | Result |
| --- | --- |
| Focused M1-M4 lifecycle/sync/search regression | 133 passed, 0 failed, 0 skipped |
| Complete isolated Django suite | 579 passed, 13 skipped, 0 failed |
| `manage.py check` | Passed; 0 issues |
| `makemigrations --check --dry-run` | Passed; no changes detected |
| Postman JSON parsing | Passed; 27 requests, no secret fields |
| `git diff --check` | Passed |

The local virtual environment uses Python 3.11.9 although the project requires
Python 3.12+. The existing Vercel build log independently confirms its deployed
runtime is Python 3.12. No new M5 deployment was available to reconfirm runtime
parity.

One diagnostic full-suite run while the real Fuseki container was active ran
579 tests with 3 failures and 9 skips. The failures were read-only optional
integration fixtures expecting the older curated Tasowheel offering ID, while
the live pilot graph contains newer DB-backed offering IDs. After restoring
Fuseki to its original unavailable state, the intended isolated suite passed
with 13 optional external-integration skips. No assertion or test was changed.

## Files changed

- `docs/Partner_API/MaaSAI_MDC_M5_Lifecycle.postman_collection.json`
- `docs/Partner_API/MaaSAI_MDC_M5_Lifecycle.postman_environment.json`
- `docs/Partner_API/mdc_v1_trusted_provider_lifecycle_integration.md`
- `docs/codex/Reports/M5_vercel_deployment_and_postman_validation_report.md`

No backend runtime, frontend/demo, provider data, migration, route, or Vercel
configuration file was changed.

## Required next action

Provide an approved, remotely reachable, protected Fuseki query + default-graph
Graph Store pair for the same dataset (or explicitly authorize the temporary
local-service tunnel after reviewing its exposure risk). Then rerun M5 from
this branch: configure Preview secrets/switches, apply migrations `0003` and
`0004`, deploy Preview, run the collection, and promote the same reviewed commit
only after Preview acceptance passes.

M5 stops here awaiting review. M6 was not started.
