# Task 14 — End-to-end semantic lifecycle verification

**PARTIAL · 2026-11-26.** All six signed-in lifecycle writes synchronized automatically, and cleanup restored the validation catalogue to 3 providers, 5 offerings and 837 triples. The same Module 4 search changed from matched to **Not matched** in the Consumer comparison. The existing score-only policy kept the gear in the raw results as a partial match. Strict result-list exclusion was verified through the protected API's existing score cutoff. The prompt's strict exclusion criterion remains open in the signed-in UI. [Task 14 prompt](../prompts_phase4/14_MDC_Stage2_End_to_End_Semantic_Lifecycle_Verification_Prompt.md)

## Integration and regression checks

Fetched `origin/main` at `e1f32a56ef1a48f8494c1e22a588853467cda7f2`. Implementation commit `027d6198ab10d9e322480da99f5ee01a978dc169` updates the fixed server-only origin, the corresponding relay tests and the frontend setup instructions. The existing local frontend serves the accepted protected Stage 2 Preview, deployment `dpl_5o45jBheveXebyp49x2gVtcVBtN7`, Python 3.12 in `iad1`, at `https://maasai-mdc-v1-3eufbyaio-mdc19.vercel.app`. The relay retains the existing Keycloak role checks, loopback restriction, fixed routing, disposable prefix, redirect rejection, no-store responses, strong ETags and conditional header forwarding. [Task 13 acceptance](13_MDC_Stage2_Automatic_Semantic_Synchronization_Report.md) · [Stage 2 deployment](https://vercel.com/mdc19/maasai-mdc-v1/dpl_5o45jBheveXebyp49x2gVtcVBtN7)

| Check | Observed evidence |
| --- | --- |
| Preview protection | Exact deployment Ready. Anonymous health HTTP 302. The approved server-only credential reached health, filters, gear discovery and the three baseline providers' offering lists with HTTP 200. Anonymous loopback health and search returned HTTP 401 `keycloak_token_required` with `Cache-Control: no-store`. The checked frontend bundles contained neither the fixed upstream origin nor the Preview credential. |
| Local pages | Provider Area, Service Discovery and Admin Dashboard compiled and served HTTP 200 with their JS bundles. The lifecycle below used the actual Keycloak sign-in and browser controls on the single server at `127.0.0.1:3000`. |
| Focused tests | 62 frontend tests passed across `stage1b`, `providerRegistration`, `providerManagement` and `adminDashboard`. 39 Consumer endpoint, runtime and matching tests passed with an isolated in-memory Django database. Targeted ESLint passed on the changed relay and its test. |
| Production build | Next.js 14.0.3 generated 20 pages in an isolated production build and produced the standalone server. Existing layout-hook, stylesheet and Browserslist warnings were present. |
| Timings | Direct protected health and filters took about 1.94 s each. The preflight gear query took 5.61 s. Signed-in Consumer searches took 1.17–2.15 s and the six writes took 1.49–3.41 s to response headers. The existing 12 s upstream and 25 s client limits were sufficient. |

## Signed-in lifecycle

The fictional provider ID was `mdc_stage1b_task14_20261126_c5bc7615`, in Finland. The full offering IDs were `mdc_stage1b_task14_20261126_c5bc7615_gear` and `mdc_stage1b_task14_20261126_c5bc7615_shaft`. All mutations came from the existing signed-in Provider and Admin interfaces. For each receipt, a read-only PostgreSQL query confirmed the publication and its outbox events, and Fuseki exposed the revision calculated from the current database watermark. No synchronization command or manual Graph Store write ran during the lifecycle.

| Operation | Signed-in HTTP and concurrency evidence | Immediate signed-in Consumer and persisted results |
| --- | --- | --- |
| Before registration | Consumer search HTTP 200 in 2,153 ms. | **Gear / Spur gear**, exact Module **4**. The new gear ID was absent. Baseline Tasowheel and Precipart results were present. |
| Provider registration | **Validate publication** returned HTTP 200, `valid=true`. **Register provider** returned HTTP 201 in 3,409 ms. The handoff loaded the exact provider and gear via two HTTP 200 detail reads with strong ETags and editable fields. | **MDC Task 14 Workshop** and **Task 14 Spur Gear** appeared in the Module 4 search as `full_match`. PostgreSQL and RDF held Spur gear support with Module **1–5** and outside diameter **20–200 mm**. The submitted offering used Steel and Machining. |
| Provider information update | **Save provider** returned HTTP 200 in 2,231 ms with a strong browser precondition and strong response ETag. | The Module 4 search still returned the exact gear as a full match and displayed **MDC Task 14 Workshop Updated**. PostgreSQL and the RDF provider display name matched. |
| Technical capability update | **Save offering** returned HTTP 200 in 1,799 ms with a strong precondition and strong response ETag. A fresh exact detail read returned HTTP 200 with a strong ETag. | Module max changed from **5** to **3** in PostgreSQL and RDF. Module min remained **1**, outside diameter remained **20–200 mm**, and Steel and Machining were still present. The same Module 4 request returned the exact gear as `partial_match`, with a rendered **Not matched** Module row showing requested **4** and provided **1–3**. Clearing Module returned the gear as `full_match`. |
| Additional offering | **Create offering** returned HTTP 201 in 1,490 ms. The Provider table showed both offering rows. | **Task 14 Plain Shaft** used **Shaft / Plain shaft** and Steel. Its exact ID was absent before creation and present immediately after in the Plain shaft search. Spur gear with Module blank still returned the exact gear. Both offering IDs and part types were visible in PostgreSQL and RDF. |
| Individual offering deletion | The row-level shaft action loaded that exact offering with a strong ETag, confirmed its exact ID, and returned HTTP 200 in 1,670 ms with a strong precondition. The browser read-back returned HTTP 404. | The shaft was absent from the Plain shaft search and from PostgreSQL and RDF. The gear remained in the Provider table and in Spur gear discovery. A supplemental protected API read confirmed shaft 404 and gear 200 with a strong ETag. |
| Admin cascade deletion | **Load provider** returned the exact ID with a strong ETag. **View provider** opened the shared read-only fields and surviving gear. **Delete provider** confirmed the exact ID and cascade. It returned HTTP 200 in 1,601 ms with a strong precondition. The browser read-back returned HTTP 404. | Immediate Spur gear and Plain shaft searches omitted the disposable IDs. PostgreSQL and RDF contained no disposable provider or offering identities. Supplemental exact protected API reads for the provider and both offerings returned HTTP 404. |

The Consumer form sends `optional_match_mode: score_only` with no minimum score. Its comparison correctly marked Module 4 **Not matched** and removed the offering from the full-match set. Its result list kept the partial match, and the current summary badge groups full and partial matches under **Suitable**. Supplemental protected API searches reused the exact Module 4 criteria and added `minimum_score: 0.99`. Both returned HTTP 200. The gear was included at score 1 before the edit and excluded after it. The existing form has no score cutoff or hard numeric filter. Repeating the same manual input leaves the same partial result visible.

The live account offered all three role controls. The Provider and Consumer pages showed no provider deletion action. In the Admin Area, loading `tasowheel` showed its protected card without a delete action. Changing the lookup cleared the previous loaded card. The scoped, strong-ETag cascade succeeded from Admin. Provider-only and Consumer-only server denial, stale ETag rejection and strong conditional-header forwarding are covered by the passing fixtures. The browser session carried Admin authority, so no separate live role-only denial was attempted.

### Receipts and visible revisions

Each browser write returned `completed / synced / succeeded`. The eight scoped outbox events each succeeded on their first attempt. Revision values came from the existing visibility check and read-only SPARQL, and were distinct after all six writes.

| Action | Publication receipt | Current Fuseki revision | Events |
| --- | --- | --- | --- |
| Register provider and gear | `2e58ef49-4ad3-4a42-89d9-521941b1db70` | `48417ca919a563704944af9dbf73b32051961f678483bfc0e2b824ee0ba0cd67` | 2 upserts |
| Update provider name | `e9a701c3-768e-4069-ab09-bc4ac4fc0ecc` | `11501fe759983a61927f18f61ab9ca6237260618750ba5ff2f58f9f63c7bd498` | 1 upsert |
| Update gear Module max | `741623c4-bf01-4b70-8505-225f6854cff0` | `0f2065c9420ac298b421c83489231f956c87e3cbe1e7ef54fdefd6075156581c` | 1 upsert |
| Add shaft | `af11fc00-f92f-4ac8-afcd-117894deaa73` | `cfb4e3a2d6c2571ea3458bc05516603f7f170118388b5447c366186e1ef1caf9` | 1 upsert |
| Delete shaft | `0ae35ba9-b65e-4739-b8e2-c434e615e460` | `074ecb00b7db41eb771bbb79547c185be31e7729a4c1bd9b80890dfb59c3130b` | 1 delete |
| Delete provider and gear | `d5643cc0-742c-4ffc-8d19-6f8a0251f5ed` | `fafdb4687513121f83b8f38e4765980ec73671209462c1b317b7ef3faebd85a3` | 2 deletes |

### Rendered evidence

- [Registration success toast](assets/task14-semantic-lifecycle/01-registration.png)
- [Saved technical specification fields](assets/task14-semantic-lifecycle/02-updated-capability.png)
- [Two offerings in the Provider Area](assets/task14-semantic-lifecycle/03-two-offerings.png)
- [Surviving gear after shaft removal](assets/task14-semantic-lifecycle/04-offering-removal.png)
- [Admin cascade deletion receipt](assets/task14-semantic-lifecycle/05-admin-deletion.png)
- [Consumer gear results after the cascade](assets/task14-semantic-lifecycle/06-consumer-after-cascade.png)

The screenshots are regions of the rendered signed-in pages. The Module comparison row is recorded as live text in the lifecycle table.

## Final integrity checks

| Check | Before | After |
| --- | --- | --- |
| `mdc_validation` business records | 3 providers, 5 offerings | 3 providers, 5 offerings. Ordered full-row hashes matched the accepted Task 13 snapshot for every provider and offering, including the prior acceptance provider. |
| Validation synchronization | 51 synced publications, 69 succeeded events | 57 synced publications, 77 succeeded events. Zero pending, processing or failed events and zero owned leases. The six Task 14 receipts remain as history. |
| Validation Fuseki default graph | 837 triples, revision `acb9edb2b6a7fb3f35a85f4647a55db04687a321d21acfabf6d689e1aa25f7e1` | 837 triples, current revision `fafdb4687513121f83b8f38e4765980ec73671209462c1b317b7ef3faebd85a3`. Same five baseline offering IDs and zero Task 14 business identities. |
| Original industrial `mdc` default graph | 731 triples | 731 triples, same SHA-256 of sorted RDF bindings, `513a1f00d138dec9edaa7de0d740397fdce0d8f1c1b939d2752007601c65e2d5`. |

Final protected Stage 2 discovery returned the same approved results. The signed-in Consumer also verified the Gear and Shaft results after cleanup.

| Search | Exact baseline offering IDs |
| --- | --- |
| Gear / Spur gear | `precipart_precision_gears`, `tasowheel_precision_gears` |
| Metal part / Roller | `mdc_stage1b_accept_20261126_a_metal` |
| Shaft / Plain shaft | `mdc_stage1b_accept_20261126_a_shaft`, `tasowheel_precision_shafts` |

The accepted Stage 2 runtime in automatic mode checks the Fuseki revision against PostgreSQL before and after retrieval. Successful Consumer responses tracked the six actual committed changes and their independently verified RDF revisions. The validation container, persistent volume, route filter and Cloudflare tunnel stayed running. Original industrial datasets, Stage 1B Preview, production deployment, application dependencies, ignored configuration, unrelated local edits and stashes were preserved. [Authoritative runtime search](../../backend/apps/search/service_discovery_runtime_search.py)

## Operator review and startup

The authorized disposable test is already cleaned up. For a read-only operator review, open the Demo Console through MaaSAI Keycloak, run the three baseline searches above, then use **Load provider** and **View provider** for `tasowheel` in Admin. Check that its card offers only **View provider**. Use the receipt and screenshots for the completed disposable lifecycle. A strict numeric result-list check in the current Consumer UI remains unavailable under the score-only policy. No further live mutations are needed to review the recorded run.

The local frontend was left running at `127.0.0.1:3000`. To restart it, use the existing dependencies and ignored server configuration from `mdc-catalog/demo-frontend`, and open the browser at `http://localhost:3000/demo` for the existing Keycloak origin.

```powershell
npm.cmd run dev -- --hostname 127.0.0.1 --port 3000
```

Keep Stage 1B writes paused during any subsequent Stage 2 test since the Previews share the validation database. If a rollback is needed, stop Stage 2 writes, restore the prior fixed server pin and restart the local frontend. Stage 1B writes can make the Stage 2 graph stale. Keep the receipts and current data available for recovery. If the validation tunnel hostname changes, the accepted Stage 2 Preview needs coordinated endpoint re-verification. [Task 12 restart instructions](12_MDC_Stage2_Fuseki_Integration_Readiness_Report.md#restart-and-rollback)


## Task 14A closure

Task 14A closed the strict result-list acceptance gap. With the same signed-in Module 4 search, the disposable gear was included at range 1–5 and omitted at range 1–3. The protected API enforced the same rule under the legacy policy. Automatic synchronization, cleanup and baseline integrity passed on the corrected Stage 2 Preview. [Task 14A correction and Stage 2 closure](14A_MDC_Strict_Technical_Eligibility_Correction_Report.md)
