# MDC v1 P3.3 — Real Fuseki Synchronization Validation

## Status

**IN PROGRESS.** P3.2 is complete. P3.3 validates the real PostgreSQL -> RDF -> Fuseki synchronization path and proves that deployed public discovery can consume the synchronized graph.

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

Verified against the temporary pilot database `neondb`:

```text
providers=4
offerings=6
certifications=5
publications=5
sync_events=6
```

All six sync events are currently:

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

M7.5 already provides the required durable implementation:

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

Therefore the `mdc` dataset is alive, SPARQL query access works, and Graph Store writes are correctly protected by HTTP authentication.

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

The Vercel deployment keeps serverless semantic writes disabled. The controlled synchronization run is executed from the trusted local operator environment against the same `neondb` PostgreSQL database and the existing local Fuseki dataset.

For that local management-command invocation only:

```text
MDC_CATALOG_SYNC_ENABLED=True
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT=http://localhost:3030/mdc/sparql
SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT=http://localhost:3030/mdc/data?default
SERVICE_DISCOVERY_FUSEKI_USERNAME=<local secret-backed username>
SERVICE_DISCOVERY_FUSEKI_PASSWORD=<local secret-backed password>
```

The deployed application later needs a remotely reachable Fuseki SPARQL query endpoint. The local dataset can be exposed temporarily through a controlled tunnel for the final Vercel-consumption gate; permanent cloud Fuseki hosting is not required for this pilot.

## Stage A — non-mutating local Fuseki preflight

Run:

```text
python scripts/p33_fuseki_preflight.py
```

The preflight:

- checks that `DATABASE_URL` is configured without printing it;
- checks both Fuseki endpoint variables;
- validates HTTP(S) endpoint syntax;
- verifies the SPARQL query endpoint with a harmless `ASK`;
- verifies protected Graph Store access using authenticated `HEAD` only;
- accepts localhost for the local synchronization gate;
- `--require-remote` is reserved for the later deployed/Vercel gate.

No graph write occurs during this preflight.

## Stage B — controlled real synchronization

After Stage A and the focused authentication tests pass, execute the management command from `mdc-catalog` with local sync enabled:

```powershell
$env:MDC_CATALOG_SYNC_ENABLED = "True"
& '..\.venv\Scripts\python.exe' backend\manage.py sync_service_discovery_catalogue
```

The command will process the pending publication outbox. Because the M7.5 implementation rebuilds/replaces the whole current graph for each selected publication, the small P3.3 pilot may perform several equivalent full-graph PUTs while advancing each publication/event to its durable success state. This is acceptable for the small validation dataset; optimization is not required for the P3.3 gate.

After the command, remove the local override:

```powershell
Remove-Item Env:MDC_CATALOG_SYNC_ENABLED -ErrorAction SilentlyContinue
```

## Stage C — PostgreSQL success evidence

After synchronization, verify:

- all six current P3.2 sync events are `succeeded`;
- each has `attempt_count >= 1`;
- `last_error` is empty;
- the five P3.2 publication records are `synced`;
- completion timestamps are populated;
- no provider/offering business data was changed by synchronization.

## Stage D — Fuseki graph evidence

Run:

```text
python scripts/p33_fuseki_verify.py --direct-only
```

Required evidence:

- SPARQL endpoint responds;
- graph contains triples;
- graph contains `mdc:providerId "p32_pilot_provider"`;
- graph contains the controlled P3.2 offering data.

## Stage E — deployed discovery consumes synchronized Fuseki

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

- the existing real Fuseki `mdc` dataset is used;
- non-mutating local query + authenticated Graph Store preflight passes;
- the pending PostgreSQL outbox is processed by the real Graph Store Protocol path;
- outbox/publication statuses prove durable synchronization success;
- direct SPARQL proves the synchronized graph contains `p32_pilot_provider`;
- a temporary remotely reachable query path is available for the Vercel gate;
- Vercel production is configured with that Fuseki query endpoint;
- canonical deployed service discovery returns `p32_pilot_provider` from the synchronized graph;
- PostgreSQL remains the operational source of truth;
- no Fuseki credentials are committed or printed;
- no public synchronization endpoint is introduced.

Target marker:

```text
READY_FOR_P34_MARKETPLACE_PROVIDER_UI_INTEGRATION
```
