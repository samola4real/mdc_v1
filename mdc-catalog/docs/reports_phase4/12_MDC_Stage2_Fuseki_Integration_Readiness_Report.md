# Task 12 — Stage 2 Fuseki integration readiness

**PARTIAL · 2026-11-26.** The isolated validation dataset is running and persistent. The existing MDC clients verified query and authenticated default-graph writes over Cloudflare HTTPS. A probe from the intended Vercel runtime remains the Task 13 pre-enable gate. Both synchronization flags remain disabled.

Reviewed `origin/main` at `f3365b3e9339598624675dc6ff3abee3ed752bc4`. The accepted Stage 1B closure is `5304d1c9ba22c230e22b580b53f7aad573867959`, including merge `30a0b10acb0ca7168d55923d3cdc29e71213a07b`. [Task 12 prompt](../prompts_phase4/12_MDC_Stage2_Fuseki_Integration_Readiness_Prompt.md) · [Task 11 closure](11_MDC_Stage1B_Closure_and_Consolidation_Report.md)

Option A provisioning resumed from report commit `827b220`. Vercel, Neon, Docker Desktop and Cloudflare remain the development and demonstration environment. AWS hosting is deferred until MaaSAI infrastructure is available. The Neon and Stage 1B evidence below is carried forward from the initial pass.

## Readiness gates

| Gate | Result | Evidence |
| --- | --- | --- |
| Validation PostgreSQL identity and schema | Verified | An authorized read-only transaction on Neon returned `current_database() = mdc_validation`, `transaction_read_only = on`, PostgreSQL 18.7, and all 22 recorded Django migrations, including the four provider migrations through `0004_cataloguesynclease`. |
| Pinned Stage 1B and production alias | Verified | The same Preview and production deployment IDs were present before and after. All nine pinned Preview reads returned HTTP 200 in both checks. Both project Preview sync flags read `false`. |
| Local industrial Fuseki | Verified | The original `mdc-fuseki` container, start time and volume match the pre-provision checks. Sorted RDF bindings match before and after, with 731 default-graph triples. |
| Local validation and persistence | Verified | The new container serves only `mdc_validation` on loopback. A disposable default-graph triple survived a restart on its own volume. Cleanup restored zero default and named graph triples. |
| Cloudflare HTTPS and MDC clients | Verified | Trusted TLS 1.3. The existing SPARQL client queried the validation graph. The Graph Store client received HTTP 401 anonymously and HTTP 200 with validation Basic authentication. Admin, industrial, and update paths returned HTTP 404. |
| Connectivity from the intended Stage 2 runtime | Pending | The HTTPS checks ran from the local workstation. A protected diagnostic in the intended Vercel Python runtime still needs to verify outbound query and Graph Store access. |

## Local Fuseki verification

| Check | Read-only evidence |
| --- | --- |
| Running container and volume | `mdc-fuseki`, ID `5628d636d7e3`, matches the M5-B record. Docker publishes container port 3030 as host port 3030 on `0.0.0.0` and `::`. The same local-driver volume `22e7cf0eca0b31e96a9dcf9fd9d591d4c87dcfd97bea029365525ef7fc3d5dd0` remains mounted read-write at `/fuseki`. |
| Version and service inventory | The image label and authenticated `GET /$/server` both reported 5.1.0. `GET /$/datasets` returned HTTP 200 with two active datasets. Their assemblers map `mdc` to `/fuseki/databases/mdc` and `mdc-service-discovery` to `/fuseki/databases/mdc-service-discovery`. Both are TDB2 and both directories are on the mounted volume. |
| Industrial query and Graph Store | `GET /$/ping` returned HTTP 200. Two read-only SPARQL `SELECT COUNT` requests to `http://127.0.0.1:3030/mdc/sparql` returned HTTP 200 and parsed to 731 default-graph triples and zero named-graph triples. The default count matches M5-B. `HEAD /mdc/data?default` returned HTTP 401 anonymously and HTTP 200 with the existing local credential. This verifies Graph Store read access. |
| Isolation baseline | Before provisioning, the original container's authenticated `GET /$/datasets/mdc_validation` returned HTTP 404. Its mounted configuration and database directory lists contained only `mdc` and `mdc-service-discovery`. The retired M5-B container and volume were absent. |

Before and after provisioning, the original `mdc` returned 731 default-graph triples and the same SHA-256 over sorted RDF result bindings, `513a1f00d138dec9edaa7de0d740397fdce0d8f1c1b939d2752007601c65e2d5`. The container retained its existing volume, port binding and start time. All requests to the industrial container were read-only. [M5-B baseline and teardown](../codex/Reports/M5B_fuseki_immediate_discovery_validation_report.md) · [Fuseki administration protocol](https://jena.apache.org/documentation/fuseki2/fuseki-server-protocol.html)

## Provisioned validation dataset

| Item | Verified configuration |
| --- | --- |
| Container and image | `mdc-fuseki-validation` (`0c0377423cb1`), cached Fuseki 5.1.0 from `stain/jena-fuseki@sha256:b1d0c96f19adddef417520184471ac816cf36c6e72936a88ea02b29f4305929a` |
| Host binding | `127.0.0.1:3031:3030` |
| Volume and dataset | `mdc_stage2_fuseki_validation_data` mounted at `/fuseki`. The authenticated inventory listed only `mdc_validation`. Its persisted assembler and TDB2 store are under `/fuseki/configuration` and `/fuseki/databases/mdc_validation`. |
| SPARQL | `http://127.0.0.1:3031/mdc_validation/sparql`, read-only query. Fuseki returned HTTP 422 with an explicit denial of federated `SERVICE` execution. |
| Graph Store | `http://127.0.0.1:3031/mdc_validation/data?default`, using the image's existing HTTP Basic mechanism and a generated validation-only credential. |

Local SPARQL counted zero triples before the probe. Anonymous Turtle `PUT` returned HTTP 401. Authenticated `PUT` returned HTTP 200, and SPARQL found the exact probe triple. Docker recorded a restart of `mdc-fuseki-validation` at `2026-11-26T13:52:07Z` with the same container ID and volume. The original probe connection dropped during restart. After reconnecting, the default graph contained only the probe triple. Authenticated local Graph Store cleanup returned HTTP 204, and SPARQL confirmed the marker absent with zero default and named graph triples. [Apache Jena TDB2 service configuration](https://jena.apache.org/documentation/tdb2/tdb2_fuseki.html) · [ARQ federation control](https://jena.apache.org/documentation/query/service.html#controlling-service-requests)

## Cloudflare HTTPS verification

The existing `cloudflared` 2026.9.3 installation is running one dedicated Quick Tunnel. Its origin is a loopback route filter on `127.0.0.1:3032`, which forwards only to validation Fuseki on `127.0.0.1:3031`. The filter permits form-encoded SPARQL POST and default-graph Graph Store GET, HEAD and Turtle PUT. It forwards Fuseki's Basic challenge and credentials on the Graph Store route. This keeps admin, UI, update, named-graph and both industrial dataset paths outside the tunnel. The filter and tunnel were still running at the end of the checks. [Cloudflare Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)

| Check | Result |
| --- | --- |
| Trusted public TLS and query | TLS 1.3 certificate validation passed. The HTTPS SPARQL POST returned HTTP 200 with a parsed count of zero. Federated `SERVICE` returned HTTP 422. |
| Excluded routes | HTTP 404 for `/`, `/$/server`, `/$/datasets`, `/mdc/sparql`, `/mdc-service-discovery/sparql`, `/mdc_validation/update` and a named-graph selector. |
| Existing MDC clients | Executed `execute_fuseki_sparql_query` and `replace_service_discovery_graph_in_fuseki` in an isolated Python process with Django's dummy database driver and both sync flags `false`. The existing paired-endpoint validator passed. The HTTPS Graph Store rejected anonymous HEAD and PUT with HTTP 401. Authenticated PUT and HEAD returned HTTP 200, and the SPARQL client read the exact marker back. |
| Probe cleanup | The verified isolated one-triple graph was cleared through local authenticated Graph Store, HTTP 204. Both local and HTTPS default-graph counts returned zero. Local named-graph count was zero, and HTTPS read-back confirmed the marker absent. |

The temporary HTTPS origin is saved locally in `%LOCALAPPDATA%\MaaSAI\mdc-stage2-fuseki\tunnel-url.txt`. The Quick Tunnel depends on the Windows host and gets a new hostname when restarted.

## AWS hosting plan

P3.6 documents one containerized Fuseki service with persistent RDF/TDB storage on a private VPC path. Django uses the internal SPARQL endpoint. A trusted AWS task uses the private Graph Store endpoint with credentials from Secrets Manager or Parameter Store. Public HTTPS ingress is for the MDC API. The planned bootstrap builds RDF from the authoritative PostgreSQL catalogue using the existing synchronization implementation.

The plan specifies an architecture and acceptance gates. It leaves the Fuseki compute and storage products, resource definition, and actual endpoint addresses open. Its ECS/Fargate example is for Django. The repository plan provides no deployed Fuseki host or approved network path from the current Vercel runtime. [AWS target architecture](../Phase_3/06_mdc_v1_p36_aws_migration_readiness_plan.md#4-recommended-aws-target-architecture) · [Fuseki migration strategy](../Phase_3/06_mdc_v1_p36_aws_migration_readiness_plan.md#6-fuseki-migration-strategy) · [Network and security model](../Phase_3/06_mdc_v1_p36_aws_migration_readiness_plan.md#8-networksecurity-model)

## Initial Neon and Stage 1B evidence

- **Stage 1B runtime.** Vercel resolved the pinned hostname and ID to the same Ready CLI Preview `dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea` in `iad1`. The deployment listed no Git SHA. Eight uploaded file digests, including both settings modules, WSGI entry point, sync service, SPARQL client and Python version file, matched the clean accepted source at `004fef8f0db73ef3e12c1035ec470c131dcb99a6`. The accepted build used Python 3.12. The backend tree at the reviewed `main` matches that source. The production alias still resolved to Ready `dpl_GmWLQStvb3qo551uYYUv4zLiW1XK`, and the six most recent deployment IDs matched in both reads. [Pinned Preview deployment](https://vercel.com/mdc19/maasai-mdc-v1/dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea) · [Accepted runtime and database evidence](https://github.com/samola4real/mdc_v1/blob/phase4/stage1-provider-lifecycle-demo-resume/mdc-catalog/docs/reports_phase4/01_MDC_Stage1_Provider_Lifecycle_Demo_Report.md)
- **Protected reads.** Anonymous Preview health redirected to Vercel SSO with HTTP 302. With the previously approved pinned-host credential, `/api/health` returned `maasai-mdc` / `ok` and `/api/catalog/filters` returned 3 part families, 6 materials, 15 processes and 6 certifications. The two exact provider reads, two offering lists and three offering detail reads returned HTTP 200 under contract `1.0`. Both provider and all three offering details had strong ETags. No credential or ETag value was recorded.
- **Deployment configuration.** The two current project Preview flag values were read individually and were both `false`. The original acceptance record verifies the disabled settings and database binding of this exact deployment ID. Current Vercel deployment metadata and health do not expose injected environment values. Project Preview metadata shows a sensitive `DATABASE_URL`, and no service-discovery Fuseki query, Graph Store or credential entries. The Production-scoped query entry was left outside the validation configuration.
- **Neon pairing.** Project `maasai-mdc-validation` (`mute-cell-38148661`), branch `main` (`br-wild-haze-aej09lb1`), compute `ep-damp-water-aeg29kmn`, database `mdc_validation`. The migration ledger matches the accepted provider schema. The prior protected Vercel database probe and application receipts tie the pinned deployment to this database. The current exact Preview reads agree with the independently queried Neon records. [Accepted database binding](https://github.com/samola4real/mdc_v1/blob/phase4/stage1-provider-lifecycle-demo-resume/mdc-catalog/docs/reports_phase4/01_MDC_Stage1_Provider_Lifecycle_Demo_Report.md#3-actual-preview-database-binding)

| Neon snapshot | Observed |
| --- | --- |
| Providers and offerings | 3 active providers and 5 active offerings. Tasowheel has `tasowheel_precision_gears` and `tasowheel_precision_shafts`. Precipart has `precipart_precision_gears`. The disposable `mdc_stage1b_accept_20261126_a` still has `mdc_stage1b_accept_20261126_a_metal` and `mdc_stage1b_accept_20261126_a_shaft`. |
| Publications | 49 total, with 28 `sync_pending` and 21 `synced`. |
| Outbox | 65 total, with 38 `pending` and 27 `succeeded`. All 38 pending events have zero attempts. Nine reference the current disposable provider and 29 reference providers absent from the current tables. |
| Lease and recheck | One lease row with no owner or expiry. Counts and pending totals matched on the second read-only snapshot. Account for the disposable provider and pending history before any later activation. |

## Fuseki target and Task 13 settings

The ignored local configuration is for the industrial `mdc` dataset at `localhost:3030` and uses `neondb`. Any validation runtime needs its own Fuseki routes paired with the previously verified `mdc_validation` database.

Reuse the existing synchronization implementation. It validates the same scheme, host and dataset for `/sparql` and `/data?default`. The Graph Store client uses HTTP Basic when both credentials are supplied and replaces the entire **default graph** via Turtle `PUT`. Its visibility check queries the catalogue revision in that graph. The SPARQL client sends a form-encoded query POST without a Basic header. Protect query access at the network or ingress boundary so the existing client can reach it from the approved runtime. [Synchronization service](../../backend/apps/providers/catalogue_sync_service.py) · [SPARQL client](../../backend/apps/search/service_discovery_fuseki_service.py)

| Setting | Intended use and verification |
| --- | --- |
| `DATABASE_URL` | Existing server-only validation connection to `mdc_validation` on the verified Neon compute. Sensitive entry present. |
| `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` | Current validation HTTPS origin from `tunnel-url.txt` plus `/mdc_validation/sparql`. Verified from the workstation. |
| `SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT` | Same origin plus `/mdc_validation/data?default`. Verified from the workstation with the existing client. |
| `SERVICE_DISCOVERY_FUSEKI_USERNAME`, `SERVICE_DISCOVERY_FUSEKI_PASSWORD` | Provisioned locally in the restricted runtime directory's `validation.env`. Use its `SERVICE_DISCOVERY_FUSEKI_USERNAME` and `ADMIN_PASSWORD` values as the two deployment-scoped server-side secrets. |
| `FUSEKI_TIMEOUT_SECONDS`, `FUSEKI_SYNC_TIMEOUT_SECONDS` | Existing query and Graph Store timeout settings. Source defaults to 10 seconds, with sync inheriting the query timeout when unset. Current project metadata has a query-timeout entry. Validate both against the actual runtime path. |
| `MDC_CATALOG_SYNC_ENABLED`, `MDC_CATALOG_AUTO_SYNC_ENABLED` | Keep both `false` through the readiness checks. Both current Preview project values verified. |
| `FUSEKI_BASE_URL`, `FUSEKI_DATASET`, `FUSEKI_QUERY_ENDPOINT`, `FUSEKI_UPDATE_ENDPOINT` | Legacy settings. Leave existing routing alone. The explicit service-discovery endpoints select the validation sync target. |

## Task 13 pre-enable gate

The existing private Vercel diagnostic checks the PostgreSQL binding. The pinned application's health route is liveness-only. A query to its service-discovery API cannot establish which endpoint handled retrieval. There was no configured diagnostic that could verify the new Fuseki origin from that runtime.

Authorize a separate protected diagnostic Preview in `mdc19/maasai-mdc-v1`, matching the intended Python 3.12 Preview execution network and `iad1` region. Give that deployment only the current HTTPS endpoint pair and its validation-only Basic secrets. With both sync flags `false`, verify TLS and parse an outbound SPARQL count, then confirm anonymous Graph Store HEAD returns 401 and authenticated HEAD returns 200. Record the diagnostic deployment ID, execution region and statuses without publishing the credential. Preserve the accepted Stage 1B deployment, its variables and production alias. This probe is the remaining runtime condition before any authorized activation.

## Restart and rollback

Start Docker Desktop and use `docker start mdc-fuseki-validation` if the container is stopped. Use `docker restart mdc-fuseki-validation` to restart it with the same volume. A Fuseki-only restart leaves the running Quick Tunnel hostname in place.

If the route filter has stopped, start it in a PowerShell terminal.

```powershell
$runtime = Join-Path $env:LOCALAPPDATA 'MaaSAI\mdc-stage2-fuseki'
node.exe (Join-Path $runtime 'validation-routes.cjs')
```

To restart the Quick Tunnel, stop its existing process first. The initial background launch recorded its PID in `cloudflared.pid`. Verify that PID still belongs to `cloudflared.exe` with origin `http://127.0.0.1:3032` before stopping it. Start the tunnel in a second terminal.

```powershell
cloudflared.exe tunnel --no-autoupdate --protocol http2 --metrics 127.0.0.1:0 --url http://127.0.0.1:3032
```

Save the URL printed by Cloudflare in `tunnel-url.txt`. Use the new origin for both endpoint settings and repeat the HTTPS checks before the next demonstration or runtime probe. The assembler, dataset and validation-only credential persist independently of the tunnel.

If a later authorized activation fails, stop synchronization, restore both flags to `false`, and restore the prior runtime routing and settings. The industrial container and graphs, Neon records and outbox, Stage 1B configuration, and application source were preserved. All Task 12 changes were limited to the separate validation infrastructure and this report.
