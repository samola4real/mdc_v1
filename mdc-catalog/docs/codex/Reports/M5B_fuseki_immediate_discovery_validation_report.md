# M5-B Fuseki immediate discovery validation report

## Outcome

M5-B is complete. A Vercel Preview connected the isolated Neon
`mdc_validation` database to a separate disposable Fuseki
`mdc_validation` dataset through a temporary Cloudflare Quick Tunnel. The
definitive live run passed **39 requests / 88 assertions / 0 failures** and
proved:

```text
register -> PostgreSQL commit -> RDF rebuild -> Fuseki revision verification
-> immediate canonical search -> update -> immediate search -> delete
-> immediate absence
```

The temporary tunnel, disposable Fuseki container, disposable volume, and
temporary Preview environment variables were removed after evidence was
collected. Production was not changed or promoted. The real `mdc-fuseki`
container, persistent volume, and `mdc` dataset were never used or mutated.
M6 was not started.

## Source and branch

| Item | Value |
| --- | --- |
| Prompt/baseline commit | `a55bbb8242e2da43c01c147a641d50a3dfb1b441` |
| Accepted M5-A merge in ancestry | `e62f332bd97f4e76d3d32f2f322547ae8adde138` |
| Branch | `phase4/m5b-semantic-validation` |
| Clean linked worktree | `C:\Users\Elahi\Desktop\mdc_v1_m5b_worktree` |
| Preview-deployed commit | `e8cbdb1676daf80cf8724603f5ec6f8f329293ca` |
| Final branch commit | Recorded in the review handoff because Git assigns it when this report is committed |

The worktree was created from the fetched `origin/main` at the prompt commit.
The original checkout's existing `.gitignore` and
`mdc-catalog/demo-frontend/src/pages/demo/index.js` changes were not modified,
staged, stashed, discarded, or committed.

## Scoped repository change

The only runtime-adjacent repository issue required by the prompt was stale
partner-guide prose. The automatic synchronization DELETE example now reports
the actual M4 verified-success contract:

```json
{"status": "completed", "publication_status": "synced", "sync_status": "succeeded"}
```

No backend runtime, migration, provider fixture, frontend, or deployment
configuration file was changed for M5-B.

## Isolated Fuseki and safety proof

### Real service, read-only baseline and final state

| Evidence | Before M5-B | After disposable teardown |
| --- | --- | --- |
| Container | `mdc-fuseki` | `mdc-fuseki` |
| Container ID | `5628d636d7e37754e6e7bb2967ad8417a5f3db4a29802c7dca5d5f85de078652` | Same |
| Persistent volume | `22e7cf0eca0b31e96a9dcf9fd9d591d4c87dcfd97bea029365525ef7fc3d5dd0:/fuseki` | Same |
| Host port | `3030` | `3030` |
| State | Running | Running |
| Read-only `mdc` triple count | `731` | `731` |

No M5-B endpoint, rebuild, Graph Store request, tunnel, or Vercel variable
targeted host port `3030` or dataset `mdc`.

### Disposable validation service

| Item | Value |
| --- | --- |
| Container | `mdc-fuseki-validation` |
| Container ID | `37e9cfce15aca7247d500a8ca11cd23d24874935b2f35a00ce64ce28da171430` |
| Host binding | `127.0.0.1:3031 -> 3030` |
| Dedicated volume | `mdc_m5b_fuseki_validation_data:/fuseki` |
| Dataset | `mdc_validation` |
| Local query shape | `http://127.0.0.1:3031/mdc_validation/sparql` |
| Local Graph Store shape | `http://127.0.0.1:3031/mdc_validation/data?default` |

The dataset was created through the disposable container's authenticated admin
API. Local checks proved that query and Graph Store addressed the same dataset.
Anonymous Graph Store access returned `401`; authenticated read/write/clear
probes succeeded. The current application query client has no Basic-auth
setting, so the read-only SPARQL endpoint remained anonymously readable for the
short validation window. Graph Store mutations required a generated credential
held only in environment/runtime state. No secret was committed or printed.

## Temporary Cloudflare transport

`cloudflared 2026.9.3` ran a Quick Tunnel that targeted only
`http://127.0.0.1:3031`. Its temporary safe hostname was:

```text
https://belongs-fotos-background-colleges.trycloudflare.com
```

The temporary endpoint shapes were:

```text
https://belongs-fotos-background-colleges.trycloudflare.com/mdc_validation/sparql
https://belongs-fotos-background-colleges.trycloudflare.com/mdc_validation/data?default
```

Remote checks returned `200` for SPARQL, `401` for anonymous Graph Store, and
`200` for authenticated Graph Store. The tunnel was stopped after validation;
the final matching-process count was zero. No named tunnel, managed hostname,
token, permanent route, or real Fuseki port was used.

## Preview deployment and configuration

| Item | Value |
| --- | --- |
| Vercel scope/project | `mdc19/maasai-mdc-v1` |
| Target | Preview only |
| URL | `https://maasai-mdc-v1-ffw4ztyxm-mdc19.vercel.app` |
| Deployment ID | `dpl_31NH8mVVxYGEqh5Ub19mNbDuH4ni` |
| Deployment status | Ready |
| Exact deployed commit | `e8cbdb1676daf80cf8724603f5ec6f8f329293ca` |
| Database | Neon `mdc_validation` |
| Runtime | Python 3.12 |

The validation deployment used these non-secret Preview values:

| Variable | Validation value |
| --- | --- |
| `MDC_PROVIDER_PUBLICATION_ENABLED` | `True` |
| `MDC_PROVIDER_VALIDATION_ENABLED` | `True` |
| `MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED` | `False` |
| `MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED` | `False` |
| `MDC_PROVIDER_CONCURRENCY_REQUIRED` | `True` |
| `MDC_CATALOG_SYNC_ENABLED` | `True` |
| `MDC_CATALOG_AUTO_SYNC_ENABLED` | `True` |
| `MDC_DEMO_API_ENABLED` | `False` |
| `FUSEKI_SYNC_TIMEOUT_SECONDS` | `10` |

The query and Graph Store variables used the safe shapes above. Fuseki username
and password variables were present without exposing their values. The existing
Preview `DATABASE_URL` continued to target `mdc_validation`.

After testing, future project Preview configuration was restored to the M5-A
baseline: both catalogue sync flags are `False`, and the temporary query,
Graph Store, username, password, and sync-timeout variables are absent. The
already-built validation deployment retains its immutable deployment snapshot,
but its tunnel and disposable target no longer exist.

Production remained Ready on deployment
`dpl_GmWLQStvb3qo551uYYUv4zLiW1XK` at
`https://maasai-mdc-v1.vercel.app`. It was neither redeployed nor promoted, and
no Production environment variable was changed.

## Live semantic acceptance

The definitive disposable provider was
`postman_m5b_20260928170916`. The equivalent Postman HTTP runner used Vercel's
authenticated Preview request path and the public documented lifecycle
contract. Every successful mutation was required to return
`completed/synced/succeeded`; the runner would stop immediately otherwise.

| Flow evidence | Result |
| --- | --- |
| Health, filters, empty canonical baseline | Passed |
| Demo route disabled and versioned route absent | Passed (`404`) |
| Payload validation | Passed (`200`) |
| Register provider with first offering | `201`, verified synchronization completed |
| Very next canonical search | Found first offering through Fuseki |
| PATCH provider name | `200`; very next search showed new name |
| Add second same-category offering | `201`; very next search found both distinct IDs |
| PATCH offering name/capabilities | `200`; very next search showed updated values |
| Whole-selected-map removal | PostgreSQL omitted vertical flange capability while retaining its horizontal sibling; immediate semantic search matched the retained field and reported the removed field unknown |
| Duplicate provider/offering | Passed (`409`) |
| Invalid controlled value | Passed (`400`) |
| Stale PATCH/DELETE ETags | Passed (`412`) |
| Missing DELETE ETag | Passed (`428`) |
| DELETE second offering | `200`; next search omitted it and retained the sibling |
| DELETE provider | `200`; next search omitted provider and both offerings |
| Final lifecycle reads | Provider and both offerings returned `404` |

Definitive total: **39 requests / 88 assertions / 0 failures**.

Two earlier fully cleaned diagnostic providers were
`postman_m5b_20260928165844` and `postman_m5b_20260928170436`. Their lifecycle
mutations and cleanup succeeded; the temporary runner initially asserted a
composite field at the wrong matching scope, then sent it in a serializer-invalid
scope. The final runner instead compared retained and removed bracket-specific
fields in the same selected map. This was test-harness correction, not a server
or synchronization fix. All three providers ended absent from PostgreSQL and
Fuseki.

## Authoritative search and revision evidence

Before lifecycle acceptance, only the disposable graph's revision marker was
cleared. The next canonical Preview search returned `503` with
`service_discovery_search_unavailable`; it did not fall back to YAML or local
RDF. The isolated rebuild command then restored the empty catalogue and revision
marker before live mutations began.

After the definitive cleanup:

```text
PostgreSQL expected revision:
f38c26608396a12e54bdf779290f85e279f7ebb58370931c8a0ff832e4f54624

Fuseki-visible revision:
f38c26608396a12e54bdf779290f85e279f7ebb58370931c8a0ff832e4f54624

revision match: true
disposable default-graph triples: 1 (the catalogue revision marker only)
postman_m5b identifiers present: false
```

This verifies Graph Store publication plus query-visible revision round-trip,
not merely an HTTP success from the write endpoint.

## PostgreSQL and outbox audit

The final read-only Neon audit returned:

```text
database=mdc_validation
active providers=0
active offerings=0
M5-B publications=21, all synced
M5-B sync events=27, all succeeded
attempt_count=1 for all 27 M5-B events
sync lease owner/expires_at cleared
catalogue watermark event count=47
```

The 21 publications and 27 events are the complete lifecycle history for the
three documented `postman_m5b_*` diagnostic/definitive providers. Previously
accepted M5-A publication/outbox history remained intact and distinguishable;
no unrelated active provider or offering existed. Operational cleanup used only
the public lifecycle API, never direct SQL.

## Local verification

| Check | Result |
| --- | --- |
| Focused lifecycle/sync/search regression | `133 passed` |
| Full isolated Django suite | `579 passed, 13 skipped` |
| `manage.py check` | Passed; 0 issues |
| `migrate --check` against Neon `mdc_validation` | Passed; zero pending migrations |
| `makemigrations --check --dry-run` against Neon `mdc_validation` | Passed; no changes detected |
| Temporary PowerShell runner parse | 0 errors; runner removed and not committed |
| `git diff --check` | Passed before final commit |

The 13 skips are the repository's optional external integration tests. Test
runs set `FUSEKI_BASE_URL=http://127.0.0.1:1` so regression discovery tests
could not accidentally query the real local Fuseki service.

## Teardown and remaining blockers

- Quick Tunnel: stopped; no M5-B tunnel process remains.
- Disposable container `mdc-fuseki-validation`: removed.
- Disposable volume `mdc_m5b_fuseki_validation_data`: removed.
- Future Preview sync flags: restored to `False`.
- Temporary Preview Fuseki endpoint/credential/timeout variables: removed.
- Neon operational rows: removed through the public API; audit history retained.
- Preview deployment: not promoted.
- Production: unchanged.
- Real `mdc-fuseki` / `mdc`: unchanged and still running with 731 triples.

There is no blocker to accepting M5-B's temporary semantic validation evidence.
A durable protected remotely hosted Fuseki service remains an infrastructure
prerequisite before enabling automatic semantic synchronization in Production;
the disposable Quick Tunnel demonstrated the flow but is intentionally not a
Production architecture. M6 was not started.

## Files changed

- `docs/partner_api/mdc_v1_trusted_provider_lifecycle_integration.md`
- `docs/codex/Reports/M5B_fuseki_immediate_discovery_validation_report.md`
- `docs/codex/Reports/M5_vercel_deployment_and_postman_validation_report.md`
