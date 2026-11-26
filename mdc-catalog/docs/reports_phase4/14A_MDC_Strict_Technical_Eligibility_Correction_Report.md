# Task 14A — Strict technical eligibility correction

**PASS · Stage 2 closed · 2026-11-26.** The signed-in Consumer found the new gear at Module 4 when its published range was 1–5. The same request omitted it entirely when the maximum became 3. Module 3 and the search with Module omitted still returned it. A direct protected search using the old `score_only` policy and no score cutoff also excluded it at Module 4. Admin cleanup and baseline integrity checks passed. [Task 14A prompt](../prompts_phase4/14A_MDC_Strict_Technical_Eligibility_Correction_Prompt.md) · [Accepted Task 14 evidence](14_MDC_Stage2_End_to_End_Semantic_Lifecycle_Verification_Report.md)

## Root cause and effective contract

The shared matcher calculated whether the optional policy was satisfied but appended results that failed the calculation. Missing subtype support and partial requirement coverage could survive when the caller kept unknowns or requested score-only matching. The Consumer request used that policy, and its summary grouped partial matches with full matches.

The shared result gate now requires the selected category and family, confirmed evidence for the selected part type, and a matched evaluation for every supplied requirement. All requested list values and bounding-box components must match. Omitted criteria and empty selection lists impose no constraint. Numeric comparisons use inclusive boundaries, check every supplied bound, and reject contradictory or missing evidence. For generic surface finish and tolerance, the reported provider maximum is compared with the supplied bounds, with `max` and `exact` retaining their upper-limit meaning.

The RDF paths retrieve the component evidence already stored in the graph. Explicit unknown subtype support is carried through retrieval and excluded by the same matcher. Offering-level certifications already accepted by the publication contract are projected with the existing certification predicates and remain scoped to their offering. Provider-level certifications keep their existing scope. Material family filters and grade evidence retain their accepted shapes. A separate `material_grades` search filter still returns HTTP 400 under the existing contract.

`POST /api/service-discovery/search` and contract version `1.0` keep their request and response structures. Earlier policy values still validate. Normalization and internal interpretation now report `all / reject_unknown` for required evidence. The valid legacy `minimum_score` field remains an additional restriction after eligibility. Eligible offerings retain the compatible `full_match` status and score 1.0 and are returned in deterministic provider and offering ID order. The response is HTTP 200 with `result_count: 0` and `results: []` when nothing qualifies. The MaaS Recommendation System compares and ranks eligible offerings. The Consumer page sends the strict policy without a cutoff and labels the result list **Eligible offerings**. [Partner API discovery guide](../Partner_API/MaaSAI_MDC_API_Documentation.md#6-service-discovery-search) · [Postman flow](../Partner_API/MaaSAI_MDC_M6_Marketplace_Integration.postman_collection.json)

## Protected Preview and local integration

Started from GitHub `origin/main` at `82cd70da6d227b5714521c3fa7d10cd45b821983`. Vercel CLI 48.9.2 uploaded the backend package archived from `c6980293c5de9fd1e9d7449d664be8fa847d3a2e`. The one new deployment is `dpl_FTCmjoE7jo7QtP1ayEe5JER7UCtC`, Ready in `iad1` on Python 3.12, at `https://maasai-mdc-v1-y1vib2sq7-mdc19.vercel.app`. It has no assigned alias. The prior Task 13 Preview, Stage 1B Preview and production deployment were still Ready, and the production aliases still pointed to `dpl_GmWLQStvb3qo551uYYUv4zLiW1XK`. [New protected Preview](https://vercel.com/mdc19/maasai-mdc-v1/dpl_FTCmjoE7jo7QtP1ayEe5JER7UCtC) · [Task 13 runtime gate](13_MDC_Stage2_Automatic_Semantic_Synchronization_Report.md) · [Vercel CLI deploy options](https://vercel.com/docs/cli/deploy)

Deployment-scoped settings reused Neon `mdc_validation`, the current Cloudflare HTTPS endpoint pair for the isolated Fuseki `mdc_validation` default graph, and its existing Graph Store authentication. `MDC_CATALOG_SYNC_ENABLED` and `MDC_CATALOG_AUTO_SYNC_ENABLED` were both true for this deployment. The tunnel origin was the one used at the accepted Task 13 runtime gate. The validation graph was already current before the test. The new runtime proved its binding through the exact baseline offering list, revision-gated discovery, and the three automatic write receipts below. No shared variables, infrastructure or previous deployments were changed.

Anonymous Preview health returned HTTP 302. Protected health, filters, exact baseline offering reads and strict search all returned HTTP 200 before the relay was retargeted. The exact server-only pin is in `demo-frontend/src/pages/api/mdc/[...path].js` at integration commit `14a6ddfced0bb724cf292d9e62b6e5f95333d8cc`. Provider, Consumer and Admin routes returned HTTP 200. The HTML and ten checked browser bundles excluded the pin and credential. Anonymous relay health returned HTTP 401 `keycloak_token_required` with `Cache-Control: no-store`. The relay continues to enforce signed roles, Admin-only provider deletion, disposable IDs, loopback access and strong ETag forwarding.

## Focused signed-in acceptance

The one new fictional provider was `mdc_stage1b_task14a_20261126_3e7d42b1` (**MDC Task 14A Workshop**, Finland). Its sole offering was `mdc_stage1b_task14a_20261126_3e7d42b1_gear` (**Task 14A Spur Gear**), confirmed Spur gear with Steel, Machining and an outside diameter of 20–200 mm. The signed-in steps ran through the actual MaaSAI Keycloak session and the existing browser controls.

| Step | Actual evidence |
| --- | --- |
| Before creation | Signed-in **Gear / Spur gear / Module 4** returned HTTP 200 with only `tasowheel_precision_gears`. Protected detail reads for the reserved IDs both returned 404. |
| Register with Module 1–5 | **Validate publication** returned HTTP 200 with `valid: true`. **Register provider** returned HTTP 201 in 1.98 s. Registration handed off the exact provider and offering with strong ETags. PostgreSQL and RDF read back 1–5. The first signed-in Module 4 search returned the disposable gear and Tasowheel, both full matches. |
| Change only Module max to 3 | **Save offering** carried the current strong precondition and returned HTTP 200 in 2.01 s. A fresh strong-ETag detail read confirmed 1–3, and the other family, typed and generic capability data and supported part types matched their prior values. PostgreSQL and RDF read back 1–3. |
| Repeat Module 4 | The same signed-in request returned HTTP 200 in 1.85 s with only Tasowheel. Both requests used `all / reject_unknown` and omitted `minimum_score`. The rendered list changed from two eligible offerings to one. |
| Check inclusion controls | Signed-in searches at Module 3 and with Module omitted each returned HTTP 200 and included the exact disposable gear. Supplemental protected API requests with legacy `score_only / keep_as_unknown` and no cutoff returned HTTP 200, excluded that gear at Module 4, and included it at Module 3. |
| Admin cleanup | The Admin Area loaded the exact provider with a fresh strong ETag and confirmed the cascade. **Delete provider** carried that precondition and returned HTTP 200 in 2.41 s. The browser's provider read-back and the protected provider and offering detail reads returned 404. The signed-in Module 3 search again returned only Tasowheel. Both identities were absent from PostgreSQL and RDF. |

All three writes returned `completed / synced / succeeded`. All five Task 14A outbox events succeeded on their first attempt. Each revision below matched the database watermark and the visible Fuseki marker. No synchronization command or manual Graph Store write was used. The six-operation Task 14 lifecycle remains accepted under its original evidence.

| Action | Publication receipt | Visible current Fuseki revision |
| --- | --- | --- |
| Register | `a19a13e1-406f-4ebc-86ee-1c4f2fa027ec` | `3e10825b2bd3d2517f0f377d592f2392a912aebe34d9bc8086582b7a048d336f` |
| Save max 3 | `6a2c8159-e6cb-4630-8d1e-9e8c67b9dfd7` | `ec0ea4eb6158cd016b3ce3da690562c6b6591448ceb7842b2a5afc0275dfc411` |
| Admin cascade | `ceef2369-f82f-4ede-a520-a140e37cfd19` | `491ec9c45a754e8eae57a62df18b84ea835fe3bf58c2012e88a33749e9132e51` |

- [Signed-in Module 4 results with published range 1–5](assets/task14a-strict-eligibility/01-module-four-before.png)
- [The same signed-in search with published range 1–3](assets/task14a-strict-eligibility/02-module-four-after.png)

## Regression and integrity evidence

| Verification | Result |
| --- | --- |
| Full isolated backend suite | 587 collected with 574 passed and 13 skipped. The in-memory SQLite run isolated production services. Skips covered four legacy Fuseki tests and nine opt-in harmonized retrieval or matching tests. |
| Opt-in Fuseki matching alignment | Five passed in a separate read-only run against the authorized isolated validation query endpoint. The legacy and curated retrieval fixtures were outside that run. |
| Eligibility regressions | Synthetic Gear, Shaft and Metal Part cases agreed across the shared evaluator, RDFLib and the Fuseki alignment path driven by SPARQL bindings. They cover inclusive boundaries, multiple eligible results, partial lists and boxes, missing and unknown evidence, unconfirmed type, one failure despite several successes, omitted input, both certification scopes, legacy policies, and HTTP 200 with zero results. Validation, lifecycle and concurrency tests remained covered. |
| Frontend | 63 focused tests passed. Targeted lint passed. The isolated production build generated 20 pages and the standalone server using the existing dependencies. Existing lint and Browserslist warnings remained in the full build. |
| Pre-existing business records | All three provider and five offering full-row fingerprints matched both the Task 14A preflight and accepted Task 13 snapshot. The validation default graph returned to 837 triples and the same five baseline offering IDs, with zero disposable identities. |
| Sync and original graph | History moved from 57 to 60 synced publications and from 77 to 82 succeeded events. Zero pending, processing or failed events and zero owned leases. The original industrial `mdc` graph retained 731 triples and sorted-binding SHA-256 `513a1f00d138dec9edaa7de0d740397fdce0d8f1c1b939d2752007601c65e2d5`. |

The following exact protected search results matched before and after the disposable test. The criteria were checked against stored capabilities.

| Search criteria | Exact offering IDs |
| --- | --- |
| Spur gear, Module 4 | `tasowheel_precision_gears` |
| Spur gear, Module 1 | `precipart_precision_gears`, `tasowheel_precision_gears` |
| Roller, Steel and Aluminum, Turning | `mdc_stage1b_accept_20261126_a_metal` |
| Plain shaft, length max 500 mm and outer diameter 80 mm | `mdc_stage1b_accept_20261126_a_shaft`, `tasowheel_precision_shafts` |
| Crown gear, no technical constraints | HTTP 200, zero eligible offerings |

The validation container, volume, filter and tunnel stayed running. The permanent checkout retained its unrelated edits, stashes, local assets, dependencies and ignored configuration. One local Next.js server remains on `127.0.0.1:3000`. Open [MDC Demo Console](http://localhost:3000/demo) using MaaSAI Keycloak. Keep writes confined to the corrected Preview because the retained deployment profiles share the validation database. Stage 2 approval applies to the verified strict Preview.
