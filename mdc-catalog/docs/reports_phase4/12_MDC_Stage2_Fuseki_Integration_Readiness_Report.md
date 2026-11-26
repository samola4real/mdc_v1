# Task 12 — Stage 2 Fuseki integration readiness

**BLOCKED · 2026-11-26.** The existing Neon validation database and Stage 1B Preview passed the read-only checks. No approved, durable, isolated Fuseki target was available to verify. Keep both synchronization flags disabled.

Reviewed `origin/main` at `f3365b3e9339598624675dc6ff3abee3ed752bc4`. The accepted Stage 1B closure is `5304d1c9ba22c230e22b580b53f7aad573867959`, including merge `30a0b10acb0ca7168d55923d3cdc29e71213a07b`. [Task 12 prompt](../prompts_phase4/12_MDC_Stage2_Fuseki_Integration_Readiness_Prompt.md) · [Task 11 closure](11_MDC_Stage1B_Closure_and_Consolidation_Report.md)

## Readiness gates

| Gate | Result | Evidence |
| --- | --- | --- |
| Validation PostgreSQL identity and schema | Verified | An authorized read-only transaction on Neon returned `current_database() = mdc_validation`, `transaction_read_only = on`, PostgreSQL 18.7, and all 22 recorded Django migrations, including the four provider migrations through `0004_cataloguesynclease`. |
| Pinned Stage 1B and production alias | Verified | The same Preview and production deployment IDs were present before and after. All nine pinned Preview reads returned HTTP 200 in both checks. Both project Preview sync flags read `false`. |
| Fuseki dataset, storage and industrial isolation | Blocked | The former dedicated M5-B target was torn down. The documented local Docker engine pipe was unavailable. No approved host, active service configuration, persistent mount or independent route-to-dataset mapping for a validation target was available. |
| SPARQL query and Graph Store | Blocked | Read-only checks against both documented loopback endpoints at ports 3030 and 3031 returned `ECONNREFUSED`. There was no candidate HTTP response, parsed SPARQL result, current industrial triple count, Fuseki version, or evidence of query and write pairing. |
| TLS, authorization and actual default-graph write capability | Blocked | No approved validation HTTPS route or dataset-scoped credential was available. No marker was written, so there was no read-back or cleanup. |
| Reachability from the intended Stage 2 runtime | Blocked | The intended backend runtime is Vercel Python in `mdc19/maasai-mdc-v1`. There is no verified Fuseki target or existing approved diagnostic path to it from that runtime. Preview liveness and the public discovery response cannot identify the Fuseki backend used. |

## Evidence from the existing infrastructure

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

The ignored local configuration points to the industrial `mdc` dataset at `http://localhost:3030/mdc/sparql` and `http://localhost:3030/mdc/data?default`. Local credential entries are present for that setup. Its database URL selects `neondb`, so it is unsuitable as validation runtime configuration. Historical M5-B evidence records `mdc-fuseki` with a volume mounted at `/fuseki` and 731 industrial triples before and after the test. The separate `mdc-fuseki-validation` on port 3031, its dedicated volume and its quick tunnel were removed after M5-B. Both local ports refused the query and Graph Store read probes today. [M5-B validation and teardown](../codex/Reports/M5B_fuseki_immediate_discovery_validation_report.md)

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

Have the Fuseki owner nominate an **existing managed Fuseki host** and authorize one dedicated TDB2 `mdc_validation` dataset with its own persistent volume or directory. Supply read-only access to the dataset assembler, route mapping, storage mount and ownership, and access policy for comparison with the industrial `mdc` dataset. Provide the canonical HTTPS endpoint pair and the approved Vercel network path. Deliver a Graph Store service credential scoped to validation through the existing secret store. This establishes the evidence needed to prove the routes reach one persistent dataset separate from `mdc`. [Apache Jena TDB2 service configuration](https://jena.apache.org/documentation/tdb2/tdb2_fuseki.html) · [Fuseki access control](https://jena.apache.org/documentation/fuseki2/fuseki-data-access-control.html)

Once those facts are verified, authorize a unique named-graph write, exact SPARQL read-back, and removal of only that test graph if the validation Graph Store supports it. Confirm its absence afterwards. Obtain separate evidence that the runtime identity can write the actual `?default` target. If the route is default-only, leave write verification pending until it can be tested safely. Confirm TLS, query and Graph Store reachability from an approved server-side diagnostic on the intended network with both flags still off. If that requires a separate Task 13 diagnostic deployment, treat it as a pre-enable gate.

Preserve the pinned Stage 1B deployment and production alias. If a later authorized activation fails, stop synchronization, set both flags back to `false`, and restore the prior runtime routing and settings before resuming validation. Task 12 made no endpoint, secret, database, graph, backend, frontend, or deployment changes.
