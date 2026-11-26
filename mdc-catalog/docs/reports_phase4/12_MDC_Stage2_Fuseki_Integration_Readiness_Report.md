# Task 12 — Stage 2 Fuseki integration readiness

**BLOCKED · 2026-11-26.** The original industrial Fuseki dataset is verified locally. A separate local validation dataset still needs provisioning, and cloud runtime access remains unverified. Keep both synchronization flags disabled.

Reviewed `origin/main` at `f3365b3e9339598624675dc6ff3abee3ed752bc4`. The accepted Stage 1B closure is `5304d1c9ba22c230e22b580b53f7aad573867959`, including merge `30a0b10acb0ca7168d55923d3cdc29e71213a07b`. [Task 12 prompt](../prompts_phase4/12_MDC_Stage2_Fuseki_Integration_Readiness_Prompt.md) · [Task 11 closure](11_MDC_Stage1B_Closure_and_Consolidation_Report.md)

The incremental check resumed from report commit `9d3ee81` after Docker Desktop started. It was limited to local Fuseki and the repository’s AWS plan. The Neon and Stage 1B evidence below is carried forward from the initial pass.

## Readiness gates

| Gate | Result | Evidence |
| --- | --- | --- |
| Validation PostgreSQL identity and schema | Verified | An authorized read-only transaction on Neon returned `current_database() = mdc_validation`, `transaction_read_only = on`, PostgreSQL 18.7, and all 22 recorded Django migrations, including the four provider migrations through `0004_cataloguesynclease`. |
| Pinned Stage 1B and production alias | Verified | The same Preview and production deployment IDs were present before and after. All nine pinned Preview reads returned HTTP 200 in both checks. Both project Preview sync flags read `false`. |
| Local industrial Fuseki | Verified | Apache Jena Fuseki 5.1.0. The original `mdc` TDB2 dataset has 731 default-graph triples and zero triples in named graphs. SPARQL and authenticated Graph Store reads returned HTTP 200. |
| Separate local validation dataset | Pending | The running server lists only `mdc` and `mdc-service-discovery`. The former `mdc_validation` dataset, container and volume are absent. Provisioning the isolated local target requires approval. |
| Validation TLS, authorization and default-graph writes | Blocked | A validation HTTPS route, dataset-scoped credential, verified query and Graph Store pairing, and evidence of actual default-graph write permission are still required. |
| Reachability from the intended Stage 2 runtime | Blocked | The local Docker checks used loopback. The intended Vercel Python runtime in `mdc19/maasai-mdc-v1` still needs an approved network path to a durable validation target and a server-side probe. |

## Local Fuseki verification

| Check | Read-only evidence |
| --- | --- |
| Running container and volume | `mdc-fuseki`, ID `5628d636d7e3`, matches the M5-B record. Docker publishes container port 3030 as host port 3030 on `0.0.0.0` and `::`. The same local-driver volume `22e7cf0eca0b31e96a9dcf9fd9d591d4c87dcfd97bea029365525ef7fc3d5dd0` remains mounted read-write at `/fuseki`. |
| Version and service inventory | The image label and authenticated `GET /$/server` both reported 5.1.0. `GET /$/datasets` returned HTTP 200 with two active datasets. Their assemblers map `mdc` to `/fuseki/databases/mdc` and `mdc-service-discovery` to `/fuseki/databases/mdc-service-discovery`. Both are TDB2 and both directories are on the mounted volume. |
| Industrial query and Graph Store | `GET /$/ping` returned HTTP 200. Two read-only SPARQL `SELECT COUNT` requests to `http://127.0.0.1:3030/mdc/sparql` returned HTTP 200 and parsed to 731 default-graph triples and zero named-graph triples. The default count matches M5-B. `HEAD /mdc/data?default` returned HTTP 401 anonymously and HTTP 200 with the existing local credential. This verifies Graph Store read access. |
| Former validation target | The authenticated `GET /$/datasets/mdc_validation` returned HTTP 404. The mounted configuration and database directory lists contain only the two active datasets. Exact Docker lookups also found neither `mdc-fuseki-validation` nor `mdc_m5b_fuseki_validation_data`. |

The incremental checks used only Docker inspection, configuration reads, and read-only HTTP operations against the existing loopback service. No credentials or stored graph data changed. [M5-B baseline and teardown](../codex/Reports/M5B_fuseki_immediate_discovery_validation_report.md) · [Fuseki administration protocol](https://jena.apache.org/documentation/fuseki2/fuseki-server-protocol.html)

## Minimum local validation configuration

Reuse the cached Fuseki 5.1.0 image for one separate container bound to `127.0.0.1:3031`, forwarding to its port 3030. There was no host listener on port 3031 during this check. The available image digest is `stain/jena-fuseki@sha256:b1d0c96f19adddef417520184471ac816cf36c6e72936a88ea02b29f4305929a`. Give the container its own named volume mounted at `/fuseki`. Persist the assembler in that volume and point `tdb2:location` at `/fuseki/databases/mdc_validation`.

Configure a single `mdc_validation` service with `fuseki:query` at `/mdc_validation/sparql` and `fuseki:gsp-rw` at `/mdc_validation/data`. Use `?default` for the existing synchronization client and require its Basic authentication with validation-scoped access. Keep the default graph separate from any named graph, and restrict access to the loopback service. This layout preserves both existing datasets and their shared industrial volume. The container, volume and dataset are proposed only. [Apache Jena TDB2 service configuration](https://jena.apache.org/documentation/tdb2/tdb2_fuseki.html) · [Fuseki access control](https://jena.apache.org/documentation/fuseki2/fuseki-data-access-control.html)

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
| `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` | Stable approved HTTPS origin with `/mdc_validation/sparql`. Unassigned and unverified. |
| `SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT` | Same approved origin with `/mdc_validation/data?default`. Unassigned and unverified. |
| `SERVICE_DISCOVERY_FUSEKI_USERNAME`, `SERVICE_DISCOVERY_FUSEKI_PASSWORD` | Dataset-scoped Basic credentials delivered through the server-side secret store. No validation credential entries found in Preview. |
| `FUSEKI_TIMEOUT_SECONDS`, `FUSEKI_SYNC_TIMEOUT_SECONDS` | Existing query and Graph Store timeout settings. Source defaults to 10 seconds, with sync inheriting the query timeout when unset. Current project metadata has a query-timeout entry. Validate both against the actual runtime path. |
| `MDC_CATALOG_SYNC_ENABLED`, `MDC_CATALOG_AUTO_SYNC_ENABLED` | Keep both `false` through the readiness checks. Both current Preview project values verified. |
| `FUSEKI_BASE_URL`, `FUSEKI_DATASET`, `FUSEKI_QUERY_ENDPOINT`, `FUSEKI_UPDATE_ENDPOINT` | Legacy settings. Leave existing routing alone. The explicit service-discovery endpoints select the validation sync target. |

## Required owner action and rollback

1. **Local validation.** Authorize the one loopback-only container, named volume and TDB2 dataset described above. Verify the isolated storage mapping and query and Graph Store routes with both sync flags off.
2. **Cloud runtime.** Have the Fuseki owner nominate a managed host for the isolated dataset and supply the persistent mount, assembler, route mapping and access-policy evidence. Provide the protected HTTPS endpoint pair, a validation-scoped Graph Store credential through the server-side secret store, and an approved path from the intended Vercel runtime. Use an approved server-side diagnostic to verify TLS, query and Graph Store connectivity. If the diagnostic needs a Task 13 deployment, treat it as a pre-enable gate.

After isolation and access are verified, use an explicitly authorized unique marker in a disposable named graph, if supported, to verify query and Graph Store pairing. Confirm initial absence, exact SPARQL read-back and absence after removing only that graph. Obtain separate evidence of write permission for the actual `?default` target. Keep that gate pending until it can be verified safely.

Preserve the pinned Stage 1B deployment and production alias. If a later authorized activation fails, stop synchronization, set both flags back to `false`, and restore the prior runtime routing and settings before resuming validation. Task 12 made no container, volume, dataset, endpoint, secret, database, backend, frontend, or deployment changes.
