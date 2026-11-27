# Task 16D — Lenient Service Discovery and Multiple Materials

**27 November 2026 · READY FOR REVIEW**

The protected Task 16D Preview and signed-in Consumer frontend support lenient discovery. Every returned offering passed the confirmed technical and certification requirements. Material alternatives and preferred processes show offering-specific evidence, including values that the published catalogue could not confirm. The same comparison appears in the downloaded PDF.

Strict search remains the default under contract `1.0`. The stable Marketplace deployment returned identical strict smoke evidence before and after Preview verification. Task 16D is published on its own branch for independent review.

## 1. Repository and release baseline

| Reference | Verified state |
| --- | --- |
| `origin/main` at fetch | `931a9c7d619edbfabee3ebfc5157af203fdb945e`, accepted Task 16B report and Consumer details |
| Task branch start | `ee91b4c05a03ffd03972b74d93f2b375b8fade91`, Task 16D prompt based on the observed main revision |
| Production backend source | `c6980293c5de9fd1e9d7449d664be8fa847d3a2e`, Task 15 |
| Archived Task 15 package | SHA-256 `354f6af20dcbdd89a26a2e582e9e75343f6154aac26ddd58e76d3bd78572f210`, verified against the recorded release digest |
| Released source comparison | The Task 15-to-16D-base comparison covered the backend, data, ontologies, Python version, build metadata and requirements. It found one change to the Marketplace handoff test. Runtime inputs matched. |
| Task 16D backend source and tests | `0d7835a30cadc4c1b534d06c960510e4650bde9f` |
| Task 16D frontend and relay | `e8d50316802cdfdb9e5a4ddc19d5a9f4d253e1f0` |
| Branch | `phase4/task16d-lenient-service-discovery`. The implementation, report and evidence are on this branch. |

Task 16D used a separate Git worktree. The permanent checkout stayed at Task 16C `e1fa1922e468f7b1465b62a1ab0860e3e64d15d1`. Its existing edits to `.gitignore`, `src/pages/demo/index.js`, and `src/pages/home/Contact.js`, the untracked `TAU Logo.JPG`, both stashes, ignored environment files and installed dependencies were preserved. Task 16D implements the required certification multi-select independently on the accepted Task 16B base. A later integration should reconcile the overlapping Consumer certification form, styles and tests with Task 16C. The Task 16C button-theme work remains on its own branch.

The deployed source and release constraints are recorded in the [Task 15 report](15_MDC_Vercel_Production_Release_and_Marketplace_API_Access_Report.md). The audited behavior is documented in the [Task 14A report](14A_MDC_Strict_Technical_Eligibility_Correction_Report.md), [Task 16A report](16A_MDC_Consumer_UI_Consolidated_Refinement_Report.md), [Task 16B report](16B_MDC_Consumer_Offering_Details_and_Actions_Report.md) and [released Partner API documentation](../Partner_API/MaaSAI_MDC_API_Documentation.md).

## 2. Previous behavior and implementation

Task 14A intentionally normalized legacy policy options to strict eligibility. H5 admitted only confirmed category, family and requested subtype, then required every submitted specification and generic requirement to match. Material and process lists required all exact codes. Successful results used `full_match` and score `1.0`. H9 gathered offering-scoped candidates and evidence with SPARQL and reused H5. The Task 16B Consumer requested strict search, sent one material and accepted only full matches with empty unresolved arrays.

Task 16D recognizes the new opt-in at the existing request serializer, preserves it through canonical normalization and evaluates preferences after the shared H5 hard gate. The H9 RDFLib and Fuseki paths continue to supply the same scoped records to the shared matcher. The change requires no new RDF predicates, inference service, search endpoint or response fields.

Backend changes are in `apps/api/service_discovery_search_serializers.py`, `apps/search/service_discovery_request.py`, `apps/search/service_discovery_local_matcher.py` and `tests/test_service_discovery_lenient.py`. Frontend changes are in the Consumer form and payload builder, result validation and accordion, comparison/detail model, PDF renderer, Consumer stylesheet, local API relay and their existing tests. The Provider and Admin components are unchanged.

## 3. Policy and evidence

| Criteria | Strict | Lenient opt-in |
| --- | --- | --- |
| Service category, part family and part type | Confirmed offering and exact subtype required | Same |
| Module, diametral pitch, relevant diameters, dimensions and bounding-box components, weight, batch size, quality, tolerance and surface finish | Every submitted value must be confirmed and satisfy the existing comparison | Same |
| Certifications | Every selected certification must be confirmed in its applicable offering or provider scope | Same |
| Materials | All supplied codes must be confirmed exactly | Alternatives. Any confirmed selected family satisfies the material group. Each value has separate evidence. |
| Processes | All supplied codes must be confirmed | Each unique process contributes its own preference evidence. Missing or incompatible evidence leaves the candidate in the result. |
| Delivery | Published upper bound must meet `delivery.max_weeks` | Same comparison. The outcome is a preference. |
| Industry | Existing request vocabulary has no industry criterion | Published `industries_served` remains descriptive in offering details |

Omitted criteria add no checks. Empty lists add no constraints. Missing or contradictory hard evidence excludes an offering. Inclusive ranges, units and comparison direction still follow Task 14A. Only `materials`, `processes` and `delivery` are soft in lenient mode.

For compatibility with Partner API callers, omitted `discovery_mode` and explicit `strict` use the released strict implementation. Legacy `optional_match_mode` accepts `any`, `all` and `score_only`. Legacy `unknown_policy` accepts `keep_as_unknown` and `reject_unknown`. Valid legacy values can accompany the explicit lenient opt-in and leave its preference rules in effect. Invalid modes and invalid legacy values return canonical HTTP 400. The numeric strict `minimum_score` keeps its existing range and behavior. Lenient accepts its omission or `null` and rejects every non-null value, including zero. `material_grades` remains an invalid search input in both modes.

Each preference row goes into the existing matched, unmatched or unknown capability array. A confirmed delivery maximum above the submitted limit is unmatched. An absent comparable maximum or missing categorical evidence is unknown. The current categorical publication records supply positive material and process evidence, so an absent code appears as unconfirmed. Published grades stay attached to their actual material records.

| Lenient score component | Contribution |
| --- | --- |
| Material alternatives | `1` for any confirmed alternative, otherwise `0`. Repeated and related alternatives do not increase the group weight. |
| Preferred processes | Confirmed unique process count divided by the number of unique requested processes |
| Delivery | `1` for a confirmed maximum within the limit, otherwise `0` |

The compatibility score is the arithmetic mean of applicable preference groups, rounded to six decimal places. With no preferences the score is `1.0`. When all applicable groups are satisfied the result is `full_match`. Otherwise the hard-eligible result is `partial_match`. Steel plus Titanium can be full if Steel is supported even when Titanium is unconfirmed. The comparison still shows both rows. Scores never filter lenient results or determine sort order. Provider and offering ID ordering is preserved. Consumers and Recommendation System integrators should treat lenient results as hard-eligible offerings that may need further confirmation of preferences.

## 4. Preview-only request examples

These examples describe the protected Task 16D development API. Use the existing `POST /api/service-discovery/search` with the applicable Preview access.

```json
{
  "contract_version": "1.0",
  "request_id": "task16d-example",
  "consumer_id": "consumer_example",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear",
  "requirements": {
    "part_family_specifications": {"module": {"exact": 4}},
    "generic_requirements": {
      "materials": ["steel", "titanium"],
      "certifications": ["ISO9001_2015", "ISO14001_2015"]
    }
  },
  "match_policy": {"discovery_mode": "lenient"}
}
```

The example requires Module 4 and both certifications, with either material serving as a preference alternative. On this Preview, choose `{"discovery_mode":"strict"}` or omit `match_policy` for strict matching across both materials and both certifications. On the stable Task 15 API, omit the Preview-only field and use the released strict request format. The Partner API integration guide and Postman assets still describe the stable release.

## 5. Published material and synchronization evidence

Exact protected reads for Tasowheel and Precipart returned HTTP 200 with strong provider and offering ETags. The provider, listing and exact offering JSON matched production for both and for the retained Stage 1B demo provider. Tasowheel's `tasowheel_precision_gears` publishes `alloyed_carburizing_steel` with **18CrNiMo7-6, 16MnCr5 and 20MnCr5**, `provider_confirmed` source and `declared` confidence. The synchronized offering record returned the same material, grades and provenance. The offering has no separate `steel` material row. Precipart's exact gears offering has no published material record. It has confirmed Spur gear support and Crown gear as requiring confirmation.

The existing controlled ontology mapping resolves `alloyed_carburizing_steel` to its parent `steel`. The lenient matcher follows published child-to-requested parent links and returns the scoped child record. Generic Steel alone cannot confirm the alloyed subtype. The grades shown for a Steel request are the grades of the published child. Broad Steel grade support is never generated.

Read-only SPARQL confirmed **837 default-graph triples and zero named-graph triples** in `mdc_validation`. The existing Neon validation connection reported `current_database() = mdc_validation` in a transaction with `transaction_read_only = on`, with 3 active providers and 5 active offerings. No hosted lifecycle mutation, Graph Store write, sync or catalogue edit was run. [Validation evidence](assets/task16d-lenient-service-discovery/validation-readonly.json)

## 6. Acceptance results

Each live case used the actual protected Preview and the existing published records. Tasowheel and Precipart below refer to their exact gear offerings.

| Live canonical search | Observed outcome |
| --- | --- |
| Spur gear without preferences | Precipart then Tasowheel, both `full_match` / `1.0`, same as strict |
| Steel alone | Both returned. Tasowheel matched through its published alloyed child. Precipart was unconfirmed. Strict returned zero. |
| Alloyed carburizing steel alone | Both returned, with Tasowheel directly confirmed. Strict returned Tasowheel only. |
| Steel + Alloyed carburizing steel | Tasowheel returned once, both alternatives confirmed with their scoped evidence and material group score `1.0`. Strict returned zero. |
| Steel + Titanium | Tasowheel returned once, Steel matched and Titanium unconfirmed, `full_match` / `1.0` for the OR group. Strict returned zero. |
| Aluminum + Titanium | Both hard-eligible offerings retained as `partial_match` / `0.0` with both material alternatives unconfirmed |
| Module 4 / Module 1 / Module 12 | Tasowheel only / both in ID order / zero results |
| Crown gear | HTTP 200 with zero results |
| Steel + Module 4 / Steel and Titanium + Module 12 | Tasowheel only / zero results |
| Hobbing + Turning, Module 4 | Tasowheel retained as `partial_match` / `0.5`. Hobbing confirmed and Turning unconfirmed. All three strict legacy variants returned zero. |
| Required certifications | ISO 9001:2015 and ISO 14001:2015 retained Tasowheel only. ISO 9001:2015 with unconfirmed full traceability at Module 4 returned zero. |
| Preview request validation | HTTP 400 for an invalid discovery mode, invalid legacy value, non-null lenient cutoff including zero, and `material_grades` |
| Strict parity and precedence | 14 strict and validation cases returned matching production and Preview bodies. Explicit strict excluded generic Steel. Lenient with legacy `all`, `reject_unknown` and null cutoff retained the unconfirmed Titanium case. |
| Stable production | The original unauthenticated stable endpoint still rejects the Preview-only opt-in with HTTP 400. |

The local fixture with diameter range 10–450 mm and batch range 100–2000 retained 300 mm and 500 pieces. It excluded 700 mm and 5000 pieces. Fixtures covered Module boundaries, malformed and unknown hard evidence, missing tolerance and surface finish, hard quality, weight and diametral pitch, and both certification scopes. Existing cross-family fixtures exercised bounding-box and typed dimensions. Additional local tests checked explicit negative and unknown delivery evidence, OR scoring, child-to-parent direction, stable ordering, duplicate preferences and published grade scoping. [Live payloads and responses](assets/task16d-lenient-service-discovery/preview-api.json)

## 7. Regression and security verification

| Check | Result |
| --- | --- |
| Offline Django suite | **582 passed, 13 skipped** out of 595. The run used in-memory SQLite, disabled sync, and isolated Fuseki configuration. |
| H1–H9, lifecycle, synchronization and Partner API | The full offline suite includes request/response serializers, normalization, YAML, RDF generation, query/retrieval, matching alignment, lifecycle ETags and authorization, sync concurrency and recovery, and Marketplace handoff. |
| New backend regression | Eight tests cover strict and lenient settings. Synthetic and local YAML cases agree across direct evaluation, RDFLib and the H9 Fuseki retrieval path supplied with SPARQL bindings. |
| Configured remote alignment | Five existing H9 alignment tests passed read-only. Four additional direct remote comparisons matched live Preview output. The Roller result present only in the synchronized validation graph distinguished the Preview's retrieval path from bundled fallback data. |
| Frontend regression | **97 passed** via `node --experimental-test-isolation=none --test` over the six frontend test files. Includes Consumer exact identity and stale-record checks, comparison, PDF, role gating, disposable scope, ETags and routing to the pinned Preview. |
| Frontend lint and build | Targeted lint passed. The production build compiled the relay and generated 20 static pages. Existing hook/style lint warnings and Browserslist notice remain in the wider codebase. |
| Access control | Protected Preview health returned 302 from a plain anonymous GET and 401 with JSON negotiation. Authorized health and filters returned 200, legacy demo health returned 404, and signed Consumer received 200 on exact offering and provider reads. The local relay returned 401 anonymously. |

The offline skips were four legacy industrial Fuseki integration tests and nine opt-in harmonized remote tests. Five of the latter were run in the separate read-only alignment pass. The four legacy and four curated retrieval checks that depend on different fixture datasets stayed outside the remote run. The first offline invocation reached the running local legacy endpoint and reported three legacy fixture mismatches. The final isolation checks used an explicitly unreachable loopback URL for that legacy client. The initial Node test runner could not create sandboxed workers, so the successful test run disabled Node test-process isolation.

The isolated runner invoked Django `call_command("test", "tests", interactive=False)` after configuring SQLite in memory. The remote run used `python manage.py test tests.test_service_discovery_fuseki_matching_alignment --noinput` with the existing validation SPARQL URL and `RUN_SERVICE_DISCOVERY_FUSEKI_TESTS=1`. Frontend verification ran `node --experimental-test-isolation=none --test` with the six explicit test paths, `next lint --file` for each changed source file, and `next build` in an isolated copy using the existing installed packages.

## 8. Protected Preview and production checks

| Item | Evidence |
| --- | --- |
| Project and deployment | `mdc19/maasai-mdc-v1`, Preview `dpl_856Vn86BbFAgPG21r3fsL1dLMMXz`, Ready in `iad1` |
| Package | Clean backend archive of `0d7835a30cadc4c1b534d06c960510e4650bde9f`, SHA-256 `6642bbf889e0747f099ddc9069b687f245bd1b3bfd9ccd3eef2911aa6ad120e3`. Seven uploaded file IDs matched local SHA-1 digests, including all three changed runtime files. |
| Effective binding | Existing project Preview `DATABASE_URL`, matched to the validation catalogue by exact API records and separate read-only Neon identification. Deployment-scoped read-only HTTPS `/mdc_validation/sparql`. Both synchronization flags, publication, validation and legacy demo endpoints were disabled. Exact GETs use the existing protected Preview profile with Vercel gating. Server config keeps the lifecycle actor and concurrency requirements enabled. |
| Isolation from production | Deployment used Preview target and skipped custom-domain assignment. Previous protected Preview health remained 200 via the authorized local access route. |
| Stable production | `https://maasai-mdc-v1.vercel.app` pointed to Ready production `dpl_AdG2ZD9Lhic25LQ4E6rf7YJLgsPF` before and after. The same 15 read-only search payloads, health, filters and exact offering probe produced byte-identical sanitized evidence, SHA-256 `091b2165acf70056d1310993b66343e616c9a58c35d81c0052f40fc3b17ab2e7`. |

The first deployment command was rejected by automatic approval review before execution because it proposed enabled sync flags and database and Graph Store credential overrides. The executed deployment inherited the existing project database entry, used only the public read-only query endpoint and disabled both sync flags. Graph Store stayed outside this Preview configuration.

[Protected Preview health](https://maasai-mdc-v1-ei6ijogqi-mdc19.vercel.app/api/health) · [Preview deployment record](https://vercel.com/mdc19/maasai-mdc-v1/856Vn86BbFAgPG21r3fsL1dLMMXz) · [Production smoke payloads](assets/task16d-lenient-service-discovery/production-strict-before.json)

## 9. Signed-in frontend and PDF

The isolated Next.js task worktree ran on loopback port 3001. Its local relay used the existing server-only `MDC_VERCEL_PROTECTION_BYPASS` setting, verified the Keycloak session and roles, and forwarded only explicit lenient canonical search to the new pinned Preview origin. Filters, exact provider and offering reads and all lifecycle routing keep the accepted protected Preview. Both Preview search and the exact detail service were checked against the same validation catalogue. No browser request went directly to Vercel, and a scan of 54 built client JavaScript chunks found zero copies of the bypass value. Provider/Admin routes, disposable ID enforcement, strong ETag handling and write permissions retain the accepted behavior.

In the signed-in Edge session the Consumer used keyboard search and selection for Steel, added Titanium, removed its chip, cleared all materials by keyboard, and searched again without Reset. The Clear button restored focus to the material control. Reset restored the Gear/Spur gear defaults and cleared materials, processes, certifications and Module. Six searches used distinct request IDs. The mixed result kept both material statuses, and the partial result showed Module 4 and both certifications matched, Hobbing matched, and Aluminum, Titanium and Turning unconfirmed. Exact details were fetched once per offering within a search and reused when reopened. Contact Provider showed the future-release notification without a network request.

The downloaded Tasowheel PDF contained 61,502 bytes across two rendered pages. It used the same requirement statuses and actual published overview, including grade associations, process evidence and provider certification scope. Images were cropped to the application content and toast. The evidence omits Keycloak subjects, tokens, bypass values, ETag values and private provenance notes.

| Evidence | Capture |
| --- | --- |
| Material alternatives and retained requirements layout | [Selected materials](assets/task16d-lenient-service-discovery/01-material-alternatives.png) |
| Steel matched by the published child with Titanium unconfirmed | [Mixed OR evidence](assets/task16d-lenient-service-discovery/02-mixed-or-evidence.png) |
| Technical requirements matched and soft criteria explained | [Partial comparison](assets/task16d-lenient-service-discovery/03-partial-comparison.png) |
| Exact Tasowheel published capabilities and scoped grades | [Manufacturing capability overview](assets/task16d-lenient-service-discovery/04-published-capability-overview.png) |
| Informational contact feedback | [Contact Provider flash](assets/task16d-lenient-service-discovery/05-contact-provider-flash.png) |
| Actual PDF rendered for review | [Comparison page](assets/task16d-lenient-service-discovery/pdf-tasowheel-gears-page-1.png) · [Published evidence page](assets/task16d-lenient-service-discovery/pdf-tasowheel-gears-page-2.png) |
| Browser observations and sanitized requests | [Signed-in acceptance log](assets/task16d-lenient-service-discovery/browser-acceptance.json) |

## 10. Review and rollout

Review the exact material and grade provenance, mixed OR rows and partial comparison against the recorded API and browser evidence. The read-only Preview retains the existing RDFLib and YAML fallbacks. Use the synchronized Roller probe to confirm live Fuseki retrieval if the validation Quick Tunnel changes. A new tunnel origin calls for a newly scoped protected Preview with a verified query binding and a corresponding local relay pin. A future production release requires separate approval and a fresh check of authoritative graph visibility, strict Partner API compatibility and the adopted Task 16C certification and theme changes. To return to the accepted strict local Consumer flow, restore its payload, comparison and relay together from the Task 16B baseline. The existing stable production deployment remains available.

[Task 16D branch report](https://github.com/samola4real/mdc_v1/blob/phase4/task16d-lenient-service-discovery/mdc-catalog/docs/reports_phase4/16D_MDC_Lenient_Service_Discovery_and_Multiple_Materials_Report.md)
