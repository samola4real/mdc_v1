# MDC v1 P3.3 — Real Fuseki Synchronization Validation

## Status

**COMPLETE.** P3.3 has validated the real PostgreSQL -> RDF -> Fuseki synchronization path and proved that deployed canonical service discovery can consume the synchronized semantic catalogue.

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

Verified against the pilot database `neondb` before synchronization:

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

This provider did not exist in the original curated YAML baseline. Its appearance through deployed service discovery after synchronization therefore provides positive evidence that the synchronized Fuseki graph is being consumed.

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

## Confirmed Fuseki pilot

The existing Docker container is:

```text
mdc-fuseki
image: stain/jena-fuseki
host port: 3030
dataset: mdc
```

Verified local evidence:

```text
GET http://localhost:3030/$/ping -> 200
POST http://localhost:3030/mdc/sparql with ASK -> boolean true
HEAD http://localhost:3030/mdc/data?default without credentials -> 401
HEAD http://localhost:3030/mdc/data?default with credentials -> 200
```

Therefore the `mdc` dataset is alive, SPARQL query access works, and Graph Store writes are protected by HTTP authentication.

## P3.3 Fuseki write authentication

P3.3 added optional secret-backed HTTP Basic authentication for protected Graph Store writes:

```text
SERVICE_DISCOVERY_FUSEKI_USERNAME
SERVICE_DISCOVERY_FUSEKI_PASSWORD
```

Rules:

- credentials are optional for Fuseki deployments that permit anonymous Graph Store writes;
- when credentials are used, username and password must be configured together;
- credentials are sent only in the Graph Store HTTP `Authorization` header;
- credentials are not embedded in endpoint URLs;
- credentials are not committed or printed by P3.3 tooling.

The local `.env` remains ignored by Git (`.env*`, except `.env.example`).

## Deployment policy

During P3.3, Vercel Production remained:

```text
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_CATALOG_SYNC_ENABLED=False
```

Semantic writes were performed only from the trusted local operator environment against `neondb` and the local Fuseki dataset.

For the local management-command invocation only:

```text
MDC_CATALOG_SYNC_ENABLED=True
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT=http://localhost:3030/mdc/sparql
SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT=http://localhost:3030/mdc/data?default
SERVICE_DISCOVERY_FUSEKI_USERNAME=<local secret-backed username>
SERVICE_DISCOVERY_FUSEKI_PASSWORD=<local secret-backed password>
```

For the final deployed-consumption gate, only the Fuseki SPARQL query endpoint was made temporarily remotely reachable through a Cloudflare Quick Tunnel. Vercel was not given the Graph Store endpoint or Fuseki write credentials.

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

Focused P3.3 Fuseki write-authentication tests also passed.

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

Therefore all six P3.2 sync events succeeded exactly once, no error remained, and all five P3.2 publication records completed as `synced`.

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

## Stage E — deployed discovery consumes synchronized Fuseki — PASSED

A temporary Cloudflare Quick Tunnel exposed the local Fuseki query endpoint for the final Vercel-consumption gate. The tunnel was left running during validation.

Confirmed remote evidence:

```text
remote SPARQL endpoint reachable: PASS
p33_fuseki_preflight.py --require-remote: PASS
Fuseki triple count: 702
p32_pilot_provider present: PASS
p32_pilot_provider_precision_metal_parts present: PASS
```

Vercel Production verification:

```text
project/scope: mdc19/maasai-mdc-v1
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT configured: PASS
MDC_CATALOG_SYNC_ENABLED=False: PASS
Fuseki Graph Store endpoint not configured in Vercel: PASS
Fuseki write credentials not configured in Vercel: PASS
production deployment: PASS
stable alias: https://maasai-mdc-v1.vercel.app
```

Canonical deployed discovery verification:

```text
GET /api/health -> 200
contract_version -> 1.0
POST /api/service-discovery/search -> p32_pilot_provider returned
python scripts/p33_fuseki_verify.py -> PASS
```

Because `p32_pilot_provider` was created in PostgreSQL during P3.2 and was not part of the original curated YAML baseline, its appearance in deployed canonical service discovery proves that the deployed runtime consumed the synchronized Fuseki graph.

No application code changes, Git commits, or Git pushes were required for the final remote gate. The final gate involved only environment/configuration changes and production redeployment.

Public contract rules remain unchanged:

```text
POST /api/service-discovery/search
contract_version = 1.0
no /api/v1 route
```

## P3.3 acceptance

All P3.3 acceptance gates are satisfied:

- real Fuseki `mdc` dataset used — **PASS**;
- non-mutating local query + authenticated Graph Store preflight — **PASS**;
- real PostgreSQL outbox processed through Graph Store Protocol — **PASS**;
- outbox/publication durable synchronization state — **PASS**;
- direct SPARQL contains `p32_pilot_provider` — **PASS**;
- remotely reachable temporary query path available for Vercel — **PASS**;
- Vercel Production configured with the Fuseki query endpoint — **PASS**;
- canonical deployed discovery returns `p32_pilot_provider` — **PASS**;
- PostgreSQL remains the operational source of truth — **PASS**;
- Fuseki write credentials are not committed or configured in Vercel — **PASS**;
- no public synchronization endpoint introduced — **PASS**;
- no application-code change required for the final remote gate — **PASS**.

## Completion marker

```text
P3.3 COMPLETE
READY_FOR_P34_PROVIDER_LIFECYCLE_API_VALIDATION
```

P3.4 is intentionally an API-validation milestone, not Marketplace integration and not frontend development. The planned gate is a controlled reusable test script that exercises provider registration, reads, updates, offering lifecycle, authentication, actor requirements, ETags/concurrency, validation failures, and publication/outbox behavior. Application code should change only if that validation exposes a genuine backend defect.
