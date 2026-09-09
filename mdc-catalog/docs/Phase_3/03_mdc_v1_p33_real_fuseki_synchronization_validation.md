# MDC v1 P3.3 — Real Fuseki Synchronization Validation

## Status

**IN PROGRESS — LOCAL GATES PASSED.** P3.2 is complete. P3.3 has now validated the real PostgreSQL -> RDF -> local Fuseki synchronization path. Only the final remotely reachable/Vercel-consumption gate remains.

## Goal

Validate this real pilot path end-to-end:

```text
trusted lifecycle write
        |
        v
PostgreSQL source of truth
        |
        v
ProviderPublication + CatalogueSyncEvent outbox
        |
        v
DB-backed RDF graph generation
        |
        v
Fuseki Graph Store Protocol PUT
        |
        v
Fuseki SPARQL query endpoint
        |
        v
POST /api/service-discovery/search
```

PostgreSQL remains the operational source of truth. Fuseki remains the semantic/search layer.

## Starting P3.3 database state

Verified against the temporary pilot database `neondb` before synchronization:

```text
providers=4
offerings=6
certifications=5
publications=5
sync_events=6
```

All six sync events initially were:

```text
status=pending
attempt_count=0
```

The controlled provider created in P3.2 is:

```text
p32_pilot_provider
```

This identity is important for P3.3 because it does not exist in the original curated YAML baseline. Finding it through deployed service discovery after synchronization is therefore positive evidence that the synchronized Fuseki graph is being queried.

## Existing synchronization implementation

M7.5 provides the durable implementation:

- `apps.providers.catalogue_sync_service` builds the RDF graph from the current active DB-backed catalogue;
- the configured Fuseki default graph is replaced through Graph Store Protocol `PUT`;
- outbox events move through `pending/failed -> processing -> succeeded`;
- the related publication becomes `synced` only when its events succeed;
- failures remain visible/retryable and record only safe failure codes;
- graph generation and graph replacement are guarded by a catalogue write watermark so concurrent lifecycle writes cannot silently publish a stale graph.

The management entry point is:

```text
python backend/manage.py sync_service_discovery_catalogue
```

P3.3 does not add a public synchronization endpoint.

## Confirmed local Fuseki pilot

The existing Docker container is:

```text
mdc-fuseki
image: stain/jena-fuseki
host port: 3030
```

Verified evidence:

```text
GET http://localhost:3030/$/ping -> 200
POST http://localhost:3030/mdc/sparql with ASK -> boolean true
HEAD http://localhost:3030/mdc/data?default without credentials -> 401
HEAD http://localhost:3030/mdc/data?default with admin credentials -> 200
```

Therefore the `mdc` dataset is alive, SPARQL query access works, and Graph Store writes are protected by HTTP authentication.

## P3.3 Fuseki write authentication

P3.3 adds optional secret-backed HTTP Basic authentication for protected Graph Store writes:

```text
SERVICE_DISCOVERY_FUSEKI_USERNAME
SERVICE_DISCOVERY_FUSEKI_PASSWORD
```

Rules:

- credentials are optional for Fuseki deployments that permit anonymous Graph Store writes;
- when credentials are used, username and password must be configured together;
- credentials are sent only in the Graph Store HTTP `Authorization` header;
- credentials are not embedded in endpoint URLs;
- credentials are never committed or printed by P3.3 tooling.

The local `.env` remains ignored by Git (`.env*`, except `.env.example`).

## P3.3 deployment policy

During the first real synchronization gate:

```text
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_CATALOG_SYNC_ENABLED=False   # Vercel production
```

The Vercel deployment keeps serverless semantic writes disabled. The controlled synchronization run was executed from the trusted local operator environment against the same `neondb` PostgreSQL database and the existing local Fuseki dataset.

For that local management-command invocation only:

```text
MDC_CATALOG_SYNC_ENABLED=True
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT=http://localhost:3030/mdc/sparql
SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT=http://localhost:3030/mdc/data?default
SERVICE_DISCOVERY_FUSEKI_USERNAME=<local secret-backed username>
SERVICE_DISCOVERY_FUSEKI_PASSWORD=<local secret-backed password>
```

The deployed application later needs a remotely reachable Fuseki SPARQL query endpoint. The local dataset can be exposed temporarily through a controlled tunnel for the final Vercel-consumption gate; permanent cloud Fuseki hosting is not required for this pilot.

## Stage A — non-mutating local Fuseki preflight — PASSED

Command:

```text
python scripts/p33_fuseki_preflight.py
```

Confirmed output:

```text
PASS DATABASE_URL configured (value hidden)
PASS Fuseki query endpoint configured: http://localhost:3030/mdc/sparql
PASS Fuseki graph-store endpoint configured: http://localhost:3030/mdc/data?default
PASS Fuseki write credentials configured (values hidden)
INFO Fuseki is local-only; local synchronization gate can proceed, remote/Vercel gate remains pending
PASS Fuseki SPARQL ASK reachable (graph_has_triples=true)
PASS Fuseki graph-store authenticated HEAD: 200
PASS no graph write attempted
P3.3 Fuseki preflight PASS
```

## Stage B — controlled real synchronization — PASSED

Executed from `mdc-catalog` with local sync enabled:

```powershell
$env:MDC_CATALOG_SYNC_ENABLED = "True"
& '..\.venv\Scripts\python.exe' backend\manage.py sync_service_discovery_catalogue
Remove-Item Env:MDC_CATALOG_SYNC_ENABLED -ErrorAction SilentlyContinue
```

Confirmed result:

```text
Catalogue synchronization: selected=5; succeeded=5; failed=0; noop=0; events=6.
Catalogue synchronization completed successfully.
```

The real authenticated Graph Store path therefore processed all five pending publications and all six outbox events successfully.

## Stage C — PostgreSQL success evidence — PASSED

Read-only post-sync verification against `neondb` confirmed:

```text
CatalogueSyncEvent:
status=succeeded
events=6
min_attempts=1
max_attempts=1
with_errors=0

ProviderPublication for p32_pilot_provider:
status=synced
publications=5
completed=5
```

Therefore all six P3.2 sync events succeeded exactly once, no error code remained, and all five P3.2 publication records completed as `synced`.

## Stage D — Fuseki graph evidence — PASSED

Command:

```text
python scripts/p33_fuseki_verify.py --direct-only
```

Confirmed output:

```text
PASS Fuseki graph contains triples: 702
PASS Fuseki contains provider: p32_pilot_provider
PASS Fuseki contains offering: p32_pilot_provider_precision_metal_parts
P3.3 direct Fuseki verification PASS
```

This proves the DB-created P3.2 provider and offering are present in the synchronized semantic graph.

## Stage E — deployed discovery consumes synchronized Fuseki — PENDING

Expose the local Fuseki query endpoint through a temporary controlled public tunnel, set the resulting `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` in Vercel Production, redeploy, and run:

```text
python scripts/p33_fuseki_preflight.py --require-remote
python scripts/p33_fuseki_verify.py
```

The final verification requires the deployed canonical response to include:

```text
provider_id = p32_pilot_provider
```

Because that provider was created in PostgreSQL during P3.2 and was not part of the original curated YAML baseline, its appearance in deployed service discovery is the key proof that the synchronized semantic catalogue is being consumed.

Public contract rules remain unchanged:

```text
POST /api/service-discovery/search
contract_version = 1.0
no /api/v1 route
```

## P3.3 acceptance

P3.3 is complete when all of the following are true:

- the existing real Fuseki `mdc` dataset is used — **PASS**;
- non-mutating local query + authenticated Graph Store preflight passes — **PASS**;
- the pending PostgreSQL outbox is processed by the real Graph Store Protocol path — **PASS**;
- outbox/publication statuses prove durable synchronization success — **PASS**;
- direct SPARQL proves the synchronized graph contains `p32_pilot_provider` — **PASS**;
- a temporary remotely reachable query path is available for the Vercel gate — **PENDING**;
- Vercel production is configured with that Fuseki query endpoint — **PENDING**;
- canonical deployed service discovery returns `p32_pilot_provider` from the synchronized graph — **PENDING**;
- PostgreSQL remains the operational source of truth — **PASS**;
- no Fuseki credentials are committed or printed — **PASS**;
- no public synchronization endpoint is introduced — **PASS**.

Target marker after Stage E:

```text
READY_FOR_P34_MARKETPLACE_PROVIDER_UI_INTEGRATION
```
