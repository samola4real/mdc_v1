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

## P3.3 deployment policy

During the first real synchronization gate:

```text
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_CATALOG_SYNC_ENABLED=False   # Vercel production
```

The Vercel deployment keeps serverless semantic writes disabled. The one controlled synchronization run is executed from the trusted local operator environment against the same `neondb` PostgreSQL database.

For that local management-command invocation only:

```text
MDC_CATALOG_SYNC_ENABLED=True
SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT=<real dedicated Fuseki graph-store endpoint>
```

The deployed application only needs the real Fuseki SPARQL query endpoint:

```text
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT=<real Fuseki SPARQL endpoint>
```

This separation prevents accidental Graph Store writes from the Vercel runtime while still allowing deployed discovery to query the synchronized semantic catalogue.

## Required real Fuseki endpoints

P3.3 requires a dedicated reachable Fuseki dataset with two endpoint roles:

```text
SPARQL query endpoint
Graph Store Protocol default-graph endpoint
```

The graph-store endpoint must be explicit. MDC deliberately does not infer a writable endpoint from the query URL.

The current sync implementation does not send Fuseki credentials. If the real pilot Fuseki requires HTTP authentication, P3.3 must first add and test a secret-backed authentication mechanism rather than embedding credentials in a URL or source code.

## Stage A — non-mutating Fuseki preflight

Run:

```text
python scripts/p33_fuseki_preflight.py
```

The preflight:

- checks that `DATABASE_URL` is configured without printing it;
- checks that both Fuseki endpoint variables are configured without printing credentials;
- validates that both URLs are HTTP(S);
- verifies that the query endpoint responds to a harmless SPARQL `ASK` request;
- rejects a localhost-only query endpoint for the full deployed P3.3 gate because Vercel cannot reach the user's laptop.

No graph write occurs during this preflight.

## Stage B — controlled real synchronization

After Stage A passes, execute the management command from `mdc-catalog` with local sync enabled:

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

Set `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` in Vercel Production, redeploy, then run:

```text
python scripts/p33_fuseki_verify.py
```

The final verification searches for `precision_gears` and requires the deployed canonical response to include:

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

- a real reachable Fuseki dataset is configured;
- non-mutating query preflight passes;
- the pending PostgreSQL outbox is processed by the real Graph Store Protocol path;
- outbox/publication statuses prove durable synchronization success;
- direct SPARQL proves the synchronized graph contains `p32_pilot_provider`;
- Vercel production is configured with the real Fuseki query endpoint;
- canonical deployed service discovery returns `p32_pilot_provider` from the synchronized graph;
- PostgreSQL remains the operational source of truth;
- no Fuseki credentials are committed or printed;
- no public synchronization endpoint is introduced.

Target marker:

```text
READY_FOR_P34_MARKETPLACE_PROVIDER_UI_INTEGRATION
```
