# Task 13 — Automatic semantic synchronization

**READY · 2026-11-26.** The protected Vercel runtime gate passed. The separate Stage 2 Preview published and served the current validation catalogue from Fuseki, reconciled the pending outbox, and synchronized one disposable create and delete automatically. The Stage 2 Preview remains protected and ready. [Stage 2 deployment](https://vercel.com/mdc19/maasai-mdc-v1/dpl_5o45jBheveXebyp49x2gVtcVBtN7)

Resumed from the authentication blocker at `e3b6d9ed999ddefcbaccb8e3061b5781548cdd69`. The prompt was reviewed at `734f8bdeda12c976f3c8e8de4122895403cf8fe2`. Both staged packages reused accepted backend source `004fef8f0db73ef3e12c1035ec470c131dcb99a6`. The diagnostic added its isolated handler only to the temporary package. The Stage 2 deployment's uploaded synchronization service, runtime search service, and Python version file digests matched the archived source. [Task 13 prompt](../prompts_phase4/13_MDC_Stage2_Automatic_Semantic_Synchronization_Prompt.md) · [Task 12 readiness report](12_MDC_Stage2_Fuseki_Integration_Readiness_Report.md)

## Protected runtime gate and activation

| Runtime | Evidence |
| --- | --- |
| Diagnostic `dpl_3omukMPvqvzan9xKRGSXMbMgzp1B` | Protected Python 3.12 Preview in `iad1`. Anonymous GET redirected with HTTP 302. Authenticated runtime metadata showed `MDC_CATALOG_SYNC_ENABLED=false` and `MDC_CATALOG_AUTO_SYNC_ENABLED=false`. |
| Outbound gate | The existing clients used the same HTTPS origin for `/mdc_validation/sparql` and `/mdc_validation/data?default`. TLS validation and parsed SPARQL passed. The default and named graphs started empty. Graph Store HEAD returned HTTP 401 anonymously and 200 with the validation credential. Authenticated default-graph PUT succeeded, SPARQL returned the exact disposable marker, and authenticated empty PUT restored both counts to zero. The runtime probe returned HTTP 200 and confirmed marker absence. |
| Diagnostic retirement | Vercel removed the exact diagnostic deployment ID after the gate. A short-lived access credential appeared in tool output during setup and was revoked before use. Its replacement was scoped to the diagnostic deployment. |
| Stage 2 `dpl_5o45jBheveXebyp49x2gVtcVBtN7` | Separate Ready Python 3.12 Preview in `iad1`, with both sync flags `True` passed as deployment-scoped variables. Anonymous health redirected with HTTP 302. The protected binding check returned the two exact accepted disposable offerings from the validation database. The automatic receipts below exercised both enabled flags. |
| Pairing | Neon project `maasai-mdc-validation` (`mute-cell-38148661`), branch `br-wild-haze-aej09lb1`, compute `ep-damp-water-aeg29kmn`, database `mdc_validation`. The existing HTTPS tunnel reached the isolated TDB2 `mdc_validation` dataset. Shared Preview and Production variables were preserved. |

## Bootstrap and authoritative discovery

The local command process verified both flags enabled, the paired validation endpoints, `current_database() = mdc_validation`, 22 migrations through provider migration `0004_cataloguesynclease`, and an unowned lease. The unpublished 836-triple projection contained only the five reviewed offerings. Its literal scan found no credential patterns or email addresses, and all 15 distinct provenance notes matched the curated baseline sources.

| Phase | Providers / offerings | Publications | Outbox | Graph |
| --- | --- | --- | --- | --- |
| Before bootstrap | 3 / 5 | 21 synced, 28 sync pending | 27 succeeded, 38 pending | Empty after runtime probe |
| Rebuild and bounded processing | 3 / 5 | 49 synced | 65 succeeded | 837 triples, including the revision marker |
| After disposable cleanup | 3 / 5 | 51 synced | 69 succeeded | 837 triples at the new revision |

The existing `sync_service_discovery_catalogue --rebuild` command published the current database catalogue. The subsequent `--limit 28` command selected 28 publications, succeeded on all 28, and completed 38 events with zero failures or no-ops. There were zero pending, failed or processing events and no owned lease afterwards. Processing rebuilt from current records. All seven historical provider IDs absent from the database remained absent from Fuseki. The visible revision after rebuild and reconciliation was `9f1ad664735bfaabc3efa12935586a218b553566fd469ebd7d0beccd990985e5`. [Existing synchronization service](../../backend/apps/providers/catalogue_sync_service.py)

Stage 2 health, filters and all three canonical searches returned HTTP 200 under contract `1.0`. The search responses reported execution in `iad1`.

| Category and part type | Exact results |
| --- | --- |
| `precision_gears` / `spur_gear` | `precipart_precision_gears`, `tasowheel_precision_gears` |
| `precision_metal_parts` / `roller` | `mdc_stage1b_accept_20261126_a_metal` |
| `precision_shafts` / `plain_shaft` | `mdc_stage1b_accept_20261126_a_shaft`, `tasowheel_precision_shafts` |

The database watermark matched the revision queried from Fuseki, and the graph contained all five exact current offering IDs. The enabled runtime verifies the current revision before and after each search. Automatic mode uses the Fuseki service, with an error path if visibility fails. The live results included the two database-created acceptance offerings. [Authoritative runtime search](../../backend/apps/search/service_discovery_runtime_search.py)

## Automatic disposable lifecycle

The only Task 13 lifecycle target was `mdc_stage1b_task13_20261126_8823907344` and its `_bracket` offering. Exact read returned HTTP 404 before registration. No management command ran between the create, delete or their verification.

| Operation | Evidence |
| --- | --- |
| Register | HTTP 201, `completed / synced / succeeded`, publication `aebac6fe-e234-4aaa-94d5-8066e362e650` and two succeeded outbox events. The exact active provider and offering were in Neon and Fuseki. Immediate bracket search returned the disposable offering. The graph had 866 triples at revision `4b88dbddd0a2f7dcf54dbba97406bd9afb2c7d90eeb9652b56fcbdb5727080c7`. |
| Delete | HTTP 200 using the current strong provider ETag through `X-MDC-If-Match`. The receipt was `completed / synced / succeeded`, publication `cc4df6a1-4848-4cc7-9926-662bfdfe5b10` with two succeeded events. Exact provider and offering GETs returned 404. Both rows and graph identities were absent, and immediate bracket search omitted the deleted offering. The graph returned to 837 triples at revision `acb9edb2b6a7fb3f35a85f4647a55db04687a321d21acfabf6d689e1aa25f7e1`. |

The database row fingerprints for all pre-existing providers and offerings matched the pre-bootstrap snapshot. The original industrial `mdc` graph still had 731 triples with sorted-binding SHA-256 `513a1f00d138dec9edaa7de0d740397fdce0d8f1c1b939d2752007601c65e2d5`. Vercel confirmed the Stage 1B Preview `dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea` and production `dpl_GmWLQStvb3qo551uYYUv4zLiW1XK` remained Ready, with the production alias on the original deployment. The Stage 2 test share was revoked. The accepted frontend pin remains on Stage 1B.

## Runtime limits, restart and rollback

Keep the existing validation container, persistent volume, route filter and Cloudflare tunnel running for this demonstration. A Quick Tunnel restart changes its HTTPS origin. Refresh both `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` and `SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT` together on a new scoped Preview, and repeat the disabled-flags runtime gate before activation. Use only the validation Basic credential for Graph Store. The HTTPS query route remains read-only and publicly reachable. [Task 12 restart instructions](12_MDC_Stage2_Fuseki_Integration_Readiness_Report.md#restart-and-rollback)

Stage 1B and Stage 2 share the validation database. Keep writes on Stage 2 while validating automatic mode. A Stage 1B write can advance the database watermark without publishing it, causing Stage 2 to reject the stale graph. If Stage 2 fails, stop writes to it and return to the pinned Stage 1B profile. Disable or retire only the separate Stage 2 runtime as appropriate. Runtime rollback leaves committed publications and the graph available for recovery.

Task 13 ends with the protected Stage 2 backend verified. The Stage 1B frontend pin, production, and the original industrial Fuseki service were preserved.
