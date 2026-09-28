# M5-A PostgreSQL lifecycle, Vercel, and Postman report

## Outcome

M5-A is complete on `phase4/deployment-validation`. A Vercel Preview built from
commit `e6f28fbfc604fcabfe8afd0904227a65b455a033` is connected to the isolated
Neon database `mdc_validation`. The definitive PostgreSQL-only lifecycle run
passed 35 HTTP requests and 81 assertions with no failures. All operational
rows created by the run were deleted; durable publication/outbox evidence was
retained in the required pending state.

This result does not claim semantic synchronization. Fuseki, Cloudflare, RDF,
and the Production deployment were not modified. Immediate consumer discovery
was not tested and remains M5-B scope.

## Source and preservation

| Item | Value |
| --- | --- |
| Prompt commit | `740e48889c208ba6c9e6b5799e29fd688b12b4b6` |
| Branch | `phase4/deployment-validation` |
| Required prior M5 commit | `922bad1cc40f3beee27a07e135d653b3af71c687` present |
| M4 integration | Present on the branch |
| Deployed commit | `e6f28fbfc604fcabfe8afd0904227a65b455a033` |
| Repository | `samola4real/mdc_v1` |
| Vercel project | `mdc19/maasai-mdc-v1` |

`origin/main` and `origin/phase4/deployment-validation` were fetched before
work. The prompt was read directly from its requested commit; `main` was not
merged or cherry-picked. The original checkout's `.gitignore` and
`mdc-catalog/demo-frontend/src/pages/demo/index.js` changes remained untouched.

## Deployment

| Target | Result |
| --- | --- |
| Preview | Ready: `https://maasai-mdc-v1-q9b60eu0x-mdc19.vercel.app` |
| Preview deployment | `dpl_AhY8kZ8uvjLSKcRnoCJidT7xRvNX` |
| Preview source | Exact clean commit `e6f28fbfc604fcabfe8afd0904227a65b455a033` |
| Runtime | Python 3.12, confirmed by Vercel build log |
| Production alias | `https://maasai-mdc-v1.vercel.app` remained unchanged |
| Existing Production deployment | Ready: `dpl_GmWLQStvb3qo551uYYUv4zLiW1XK` (`maasai-mdc-v1-588we5lou-mdc19.vercel.app`) |

No promotion or Production deployment was performed. The Preview remained
protected; live requests used authenticated `vercel curl`. The Vercel project
has no connected Git repository, so branch-specific Preview variables could
not be saved. The reviewed values were therefore set only in the project-wide
Preview scope used by this manual deployment.

Preview configuration, with secret values omitted:

```text
DJANGO_SETTINGS_MODULE=config.settings_production
DJANGO_ALLOWED_HOSTS=.vercel.app
DATABASE_URL=<sensitive; isolated mdc_validation database>
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=False
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=False
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
MDC_CATALOG_SYNC_ENABLED=False
MDC_CATALOG_AUTO_SYNC_ENABLED=False
MDC_DEMO_API_ENABLED=False
```

No Fuseki query, Graph Store, username, password, or dataset variable is
present in Preview. Production environment variables were not changed. The
no-auth/no-actor setting is an environment-only test choice; secured-mode code,
tests, defaults, and ETag enforcement remain intact.

## Database and migrations

Read-only preflight identified the existing Neon database `neondb` with real
provider data and left it unchanged. The already available, empty
`mdc_validation` database was selected for Preview isolation. The migration
plan was reviewed before execution and contained only the expected initial
Django schema plus provider migrations; no destructive operation was present.

All migrations through `providers.0004_cataloguesynclease` were applied to
`mdc_validation`, including required provider migrations `0003` and `0004`.
Final inspection reported:

```text
pending migrations: 0
catalogue sync leases: 1
active providers: 0
active offerings: 0
```

The provider/offering operational snapshot SHA-256 was
`a514d0dde5e78f1874af9bf4d3e29f0c9b2b0e8642313e35d5072719b40d8322`
both before and after acceptance. Because this isolated database began empty,
that also proves no unrelated operational provider or offering changed.

## M5-A Postman assets

The existing M5 collection was preserved. Separate secret-free M5-A assets
were added:

- `docs/Partner_API/MaaSAI_MDC_M5A_PostgreSQL_Lifecycle.postman_collection.json`
- `docs/Partner_API/MaaSAI_MDC_M5A_PostgreSQL_Lifecycle.postman_environment.json`

The ordered collection has 35 requests. It generates a unique
`postman_m5a_*` provider, sends no token or actor header, captures ETags, expects
`accepted/sync_pending/pending`, and uses provider/offering GET/list responses
as the post-write oracle. It makes one canonical search request before mutation
as a readiness baseline only and contains no immediate-discovery assertion.

## Definitive live acceptance

The equivalent live run used disposable provider
`postman_m5a_20260928161236`. Vercel's protected transport used the documented
`X-MDC-If-Match` compatibility header while preserving the same strong ETag
values and concurrency semantics represented by `If-Match` in the Postman
collection.

| Check | HTTP/result |
| --- | --- |
| Health and filters | `200`, contract `1.0` |
| Canonical search readiness baseline | `200`; not used as lifecycle evidence |
| Demo endpoint and `/api/v1` route | `404`, `404` |
| Disposable provider initially absent | `404` |
| Validation without bearer/actor | `200`, `valid=true` |
| Provider plus first offering registration | `201`, `accepted/sync_pending/pending` |
| Provider GET and offering list persistence | `200`; expected IDs and strong ETags |
| Provider-name PATCH and confirming GET | `200`, then `200`; name persisted |
| Duplicate provider | `409` |
| Second same-category offering | `201`, `accepted/sync_pending/pending` |
| Both offering IDs/list/detail | `200`; distinct independent rows |
| Duplicate offering and invalid controlled field | `409`, `400` |
| Offering name/capability PATCH | `200`, `accepted/sync_pending/pending` |
| Stale offering PATCH | `412` |
| Selected-map removal and confirming GET | `200`, then `200`; selected keys absent and siblings retained |
| Offering DELETE without/stale ETag | `428`, `412` |
| Second-offering DELETE | `200`, `accepted/sync_pending/pending` |
| Deleted offering / retained sibling | `404`; sibling still listed with `200` |
| Provider DELETE | `200`, `accepted/sync_pending/pending` |
| Final provider and both offering GETs | `404`, `404`, `404` |

Definitive result: **35 requests, 81 assertions, 0 failures**.

Two pre-acceptance client-harness diagnostics also used disposable IDs
`postman_m5a_20260928160220` and `postman_m5a_20260928160841`. The first exposed
quote loss in an inline Windows wrapper header and produced expected safe
`400`/`428` rejections; the second stopped after registration because of an
inline PowerShell function-call typo. Accepted POSTs were not blindly repeated.
State was inspected first, and each diagnostic provider was deleted with its
current strong ETag and verified `404`. These were client-runner issues, not
deployed API defects.

## Publication and outbox evidence

Final operator inspection found no active `postman_m5a_*` provider. Historical
evidence for the definitive and diagnostic cleanup flows is retained by design:

```text
provider publications: 13, all sync_pending
publication operations: create=3, update=6, delete=4
catalogue sync events: 20, all pending
total sync attempts: 0
non-disposable publication history: 0
```

This confirms PostgreSQL durability and that no semantic worker or Fuseki write
was run. The additional history reflects the two accurately documented,
fully-cleaned transport diagnostics.

## Local verification

| Check | Result |
| --- | --- |
| Focused lifecycle/sync/search regression | 133 passed |
| Full isolated Django suite | 579 passed, 13 skipped |
| `manage.py check` | Passed; 0 issues |
| `makemigrations --check --dry-run` | Passed; no changes detected |
| M5-A collection/environment JSON | Parsed successfully; no credential fields |
| PowerShell equivalent-run script syntax | 0 parse errors; temporary script removed after use |
| `git diff --check` | Passed before reporting; repeated before final commit |

The local reusable environment runs Python 3.11.9. This does not represent the
deployed runtime; the Preview build independently confirms Python 3.12.

## Changed files

- `docs/Partner_API/MaaSAI_MDC_M5A_PostgreSQL_Lifecycle.postman_collection.json`
- `docs/Partner_API/MaaSAI_MDC_M5A_PostgreSQL_Lifecycle.postman_environment.json`
- `docs/Partner_API/mdc_v1_trusted_provider_lifecycle_integration.md`
- `docs/codex/Reports/M5_vercel_deployment_and_postman_validation_report.md`
- `docs/codex/Reports/M5A_postgresql_lifecycle_vercel_postman_report.md`

No backend runtime, migration, frontend, demo API, ontology, RDF, or Cloudflare
file was changed.

## Remaining work and blockers

There is no M5-A blocker. M5-B still requires an approved protected remote
Fuseki query/Graph Store pair, semantic synchronization/retry execution, and
immediate canonical consumer-discovery validation. No such work was attempted
or claimed here. M6 was not started.
