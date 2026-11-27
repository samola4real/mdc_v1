# Task 16E — Comprehensive Service Discovery Validation

**27 November 2026 · PARTIALLY VERIFIED for release · ready for independent review**

## Decision summary

All **1,386 offline comparisons** and **194 sequential protected Preview cases** matched the independently derived expectations. The cases checked exact provider and offering IDs, order, contract version, hard eligibility, preference evidence, and status and score. An additional 108 local graph-path comparisons and 20 live read-only Fuseki comparisons passed. Signed-in Edge verified the consolidated selectors, expanded offering evidence, PDF download, Contact Provider feedback, and Consumer, Provider and Admin button variants.

- **Module makes the main gear result difference.** At Module 1 mm the shared catalogue returns Precipart and Tasowheel. At Modules 2, 3 and 4 mm it returns Tasowheel alone. At 12 mm it returns zero offerings in both modes.
- **Material preference changes evidence and coverage.** Strict Steel returns zero gear offers on the shared catalogue. Lenient Steel returns both eligible Spur gear offerings. Tasowheel matches through its published alloyed carburizing steel. Precipart has no comparable published material evidence.
- **Both missing certification options are selectable.** The shared Preview still returns zero results for either new code. Locally enriched AS9100 Rev D / EN 9100:2018 evidence returns exactly Precipart's gear offering. ISO 13485 stays unavailable as confirmed manufacturing evidence for that offering.
- **Production release remains gated.** The Preview is read-only and has no approved paired Graph Store configuration for automatic-sync catalogue revision checks. It retained the existing fallback behavior. The work includes positive evidence that it used the current validation graph during the test. A protected production-equivalent verification with a sanctioned paired binding remains required.

The stable Task 15 alias resolves to the original deployment. It returned identical strict smoke evidence before and after verification. This work is confined to the Task 16E branch and a new protected Preview.

## Certification findings and decision

Evidence checked on 27 November 2026. The staging Precipart YAML named Swiss ISO 9001, ISO 13485 and AS9100. The prior curated record and the shared exact provider and offering responses had empty certification evidence for Precipart. The registry supplied six choices independent of provider records. Task 16E extends that shared registry and the existing RDF mappings. Provider and Consumer use the same filter endpoint, and exact details and PDFs resolve the canonical labels. The matcher still uses AND across requested certificates and scopes offering certifications to that offering. [Staging source](../../data/staging/provider_sources/precipart.yaml) · [Curated source](../../data/curated/service_discovery/providers/precipart.yaml)

| Dropdown code and label | Shared catalogue published evidence | Local enriched treatment and applicability |
| --- | --- | --- |
| `ISO9001_2015` · ISO 9001:2015 | Tasowheel and Demo Metal Works provider-level | Preserved. SQS 11718 covered precision components and gears in Lyss and expired 29 January 2026. No current Lyss renewal was verified. DQS 10017378 QM15 has a printed February 2027 end date for a Farmingdale, New York certificate and does not establish Lyss scope. [Swiss certificate](https://www.precipart.com/wp-content/uploads/2023/01/102353_en_9001_23.pdf) · [US certificate](https://www.precipart.com/wp-content/uploads/2024/05/ISO-9001-Industrial.pdf) |
| `ISO14001_2015` · ISO 14001:2015 | Tasowheel and Demo Metal Works provider-level | Preserved as published evidence. |
| `ISO_TS_16949_partial` · Partial ISO/TS 16949 implementation | Tasowheel provider-level | Preserved with the partial label. |
| `APQP` · Advanced Product Quality Planning | Tasowheel provider-level | Preserved with the established label. |
| `aerospace_traceability` · Aerospace traceability | Option available. None of the five offering records or three provider records asserts it. | Preserved. |
| `full_traceability` · Full traceability | Option available. None of the five offering records or three provider records asserts it. | Preserved. |
| `ISO13485_2016` · ISO 13485:2016 | New option. No shared published match. | SQS 45176 identifies Lyss and distribution of components and assemblies for medical devices, with validity shown through 13 September 2027. Retained as documented organization-level distribution evidence outside gear eligibility. [Certificate](https://www.precipart.com/wp-content/uploads/2024/08/102353_en_13485_24.pdf) · [SQS listing](https://www.sqs.ch/de/node/313182) |
| `AS9100_D` · AS9100 Rev D / EN 9100:2018 | New option. No shared published match. | SQS 42929 identifies Precipart SA at Werkstrasse 37, Lyss, one site, covering realization of precision and gearing parts, components and assemblies. Issued 30 January 2026 with validity shown through 29 January 2029. Added to the curated Swiss gear offering only, with evidence provenance. EN 9100:2018 and AS9100 D share one code. [Certificate](https://www.precipart.com/wp-content/uploads/2026/03/102353_de_EN9100_42929_25.pdf) · [SQS equivalence](https://www.sqs.ch/en/services/products) |

Precipart's gear page lists group capabilities and describes Farmingdale manufacturing. The certificate establishes coverage for the Lyss scope described above. Review site applicability on any actual quote and recheck the certificate validity before future publication. The public certifications landing page returned a verification interstitial in the research client, so the scope and dates above are based on the individual signed certificates and the accessible SQS listing. EN 9100's reference to ISO 9001 does not establish a separate ISO 9001 registration. [Precipart precision gears](https://www.precipart.com/products-capabilities/gears-motion-control/precision-gears/) · [Certification landing page](https://www.precipart.com/why-precipart/quality/certifications/)

**Gear accuracy is a separate technical requirement.** Precipart's ISO class 5 and Tasowheel's DIN class 4 are best published gear accuracy classes. Requests compare the named standard and the class independently of certification selections. No ISO-to-DIN equivalence is assumed.

## Published capability snapshot

The shared version is the five-offering catalogue on the protected Preview. Exact provider, listing and offering GETs were frozen before expected results were calculated, then re-read after the matrix. The enriched local copy differs only by the reviewed certificate on P-G. The bundled local curated gear source and regenerated RDF include the same scoped certificate. The Preview package was deliberately pinned to the vocabulary-only commit and kept its previous bundled data version.

| Key and exact offering ID | Provider and confirmed types | Published technical ranges and known gaps | Published materials, work and certifications |
| --- | --- | --- | --- |
| T-G · `tasowheel_precision_gears` | Tasowheel Oy (`tasowheel`), Spur, Helical, Bevel and Worm | Module 0.3–10 mm, DP 2.5–85, outside diameter 10–450 mm, DIN class 4. Batch 100–2,000, lead time 8–12 weeks, ≤200 kg. No confirmed face width, generic finish or tolerance in this snapshot. | Alloyed carburizing steel, 18CrNiMo7-6, 16MnCr5 and 20MnCr5. Published machining, hobbing, gear shaping, deburring, hard turning, grinding, tooth grinding, gear grinding, gear cutting, surface grinding, milling and turn-mill. Four provider certifications above. |
| T-S · `tasowheel_precision_shafts` | Tasowheel Oy, Plain, Splined and Hollow | Length ≤500 mm with no lower bound, outer diameter 10–450 mm, Splined module 0.3–10. No confirmed wall thickness, inner diameter or tolerance. Batch 100–2,000, lead 8–12 weeks, ≤200 kg. | Same grade association, twelve processes and provider certifications as T-G. |
| P-G · `precipart_precision_gears` | Precipart (`precipart`), Spur, Helical and Worm. Crown requires confirmation. | Module 0.125–1.5 mm, DP 16–200, outside diameter 6–102 mm, ISO class 5. Batch, lead time, finish, tolerance and type-specific geometry unconfirmed. | No published material, process, grade or certification in the shared record. Local-only AS9100 appears at offering scope. |
| D-M · `mdc_stage1b_accept_20261126_a_metal` | Demo Metal Works Oy (`mdc_stage1b_accept_20261126_a`), Block and Roller | Block typed maximum envelope 200 × 120 × 300 mm. Roller typed outer diameter maximum 100 mm. Other rotational dimensions and tolerance unconfirmed. Batch 10–500, lead 4–9 weeks, ≤100 kg. | Steel (42CrMo4, 16MnCr5) and Aluminum (6061-T6, 6082-T6, 7075-T6). Machining, milling, turning and grinding. ISO 9001 and ISO 14001 from provider. |
| D-S · `mdc_stage1b_accept_20261126_a_shaft` | Demo Metal Works Oy, Plain and Splined | Length ≤500 mm with no lower bound, outer diameter 10–120 mm, Splined module stored as legacy `value: 2`. Batch 100–1,000, lead 4–8 weeks, ≤75 kg. | Alloyed carburizing steel (18CrNiMo7-6, 16MnCr5), turning, milling and grinding. ISO 9001 and ISO 14001 from provider. |

[Exact frozen shared catalogue and options](assets/task16e-comprehensive-discovery-validation/catalogue-snapshot.json)

## Representative expected versus actual searches

Each entry is a manufacturing offering. Counts are in parentheses and the keys above resolve to exact provider and offering IDs. Unqualified gear criteria in the table use Spur gear. The complete matrices give the raw values and units, evidence scopes, requested quantities, exclusions, and score and status for every scenario.

### Live shared Preview

| Case | Consumer input | Mode | Expected offerings | Actual offerings | Result | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| E039 | module exact 0.125 mm | strict | P-G (1) | P-G (1) | PASS | Precipart lower bound. |
| E047 | module exact 0.3 mm | strict | P-G, T-G (2) | P-G, T-G (2) | PASS | Tasowheel lower bound. |
| E053 | module exact 1 mm | strict | P-G, T-G (2) | P-G, T-G (2) | PASS | Inside both ranges. |
| E057 | module exact 1.5 mm | strict | P-G, T-G (2) | P-G, T-G (2) | PASS | Precipart inclusive upper bound. |
| E059 | module exact 1.51 mm | strict | T-G (1) | T-G (1) | PASS | Just outside Precipart. |
| E061 | module exact 2 mm | strict | T-G (1) | T-G (1) | PASS | Tasowheel range only. |
| E063 | module exact 3 mm | strict | T-G (1) | T-G (1) | PASS | Tasowheel range only. |
| E065 | module exact 4 mm | strict | T-G (1) | T-G (1) | PASS | Tasowheel range only. |
| E071 | module exact 10 mm | strict | T-G (1) | T-G (1) | PASS | Tasowheel inclusive upper bound. |
| E076 | module exact 12 mm | lenient | None (0) | None (0) | PASS | Neither range reaches 12. |
| E089 | diametral pitch exact 2.5 | strict | T-G (1) | T-G (1) | PASS | Tasowheel lower bound. |
| E099 | diametral pitch exact 16 | strict | P-G, T-G (2) | P-G, T-G (2) | PASS | Precipart lower bound. |
| E109 | diametral pitch exact 85 | strict | P-G, T-G (2) | P-G, T-G (2) | PASS | Tasowheel upper bound. |
| E115 | diametral pitch exact 200 | strict | P-G (1) | P-G (1) | PASS | Precipart upper bound. |
| E117 | diametral pitch exact 201 | strict | None (0) | None (0) | PASS | Above both. |
| E129 | outside diameter exact 6 mm | strict | P-G (1) | P-G (1) | PASS | Precipart lower bound. |
| E145 | outside diameter exact 102 mm | strict | P-G, T-G (2) | P-G, T-G (2) | PASS | Precipart upper bound. |
| E149 | outside diameter exact 300 mm | strict | T-G (1) | T-G (1) | PASS | Tasowheel range only. |
| E158 | outside diameter exact 700 mm | lenient | None (0) | None (0) | PASS | Beyond both. |
| E169 | module 1 mm, DP 25.4, outside diameter 100 mm | strict | P-G, T-G (2) | P-G, T-G (2) | PASS | All three requirements confirmed. |
| E187 | module 4 mm, DP 6.35, outside diameter 100 mm | strict | T-G (1) | T-G (1) | PASS | Precipart fails both module and DP. |
| E191 | independent dimensions: module 1 mm plus DP 85 | strict | P-G, T-G (2) | P-G, T-G (2) | PASS | Current contract checks independent bounds. |
| E197 | ISO accuracy class 5 or better | strict | P-G (1) | P-G (1) | PASS | Only Precipart reports the ISO standard. |
| E293 | Material steel | strict | None (0) | None (0) | PASS | Exact generic Steel evidence absent. |
| E294 | Material steel | lenient | P-G, T-G (2) | P-G, T-G (2) | PASS | Tasowheel matched through its published child. Precipart unconfirmed. |
| E688 | module 4 mm and steel, titanium | lenient | T-G (1) | T-G (1) | PASS | Steel matched. Titanium unconfirmed. |
| E700 | module 12 mm and aluminum, titanium | lenient | None (0) | None (0) | PASS | Preferences cannot override the module. |
| E345 | Process turning | strict | None (0) | None (0) | PASS | Exact Turning evidence absent on both gear lines. |
| E346 | Process turning | lenient | P-G, T-G (2) | P-G, T-G (2) | PASS | Both retained with an unconfirmed preference. |
| E702 | delivery at most 6 weeks | lenient | P-G, T-G (2) | P-G, T-G (2) | PASS | Tasowheel unmatched. Precipart unconfirmed. |
| E603 | Requires ISO13485_2016 | strict | None (0) | None (0) | PASS | Option exists. No applicable shared certificate. |
| E606 | Requires AS9100_D | lenient | None (0) | None (0) | PASS | Current shared Precipart has no published certificate. |
| E862 | separate material grade search | strict | HTTP 400 | HTTP 400 | PASS | Grades are informational. |
| E001 | spur gear with no optional criteria | strict | P-G, T-G (2) | P-G, T-G (2) | PASS | Both providers confirm Spur. |
| E010 | crown gear with no optional criteria | lenient | None (0) | None (0) | PASS | Candidate mapping is unconfirmed. |
| E011 | plain shaft with no optional criteria | strict | D-S, T-S (2) | D-S, T-S (2) | PASS | Both workshops confirm Plain shaft. |
| E030 | roller with no optional criteria | lenient | D-M (1) | D-M (1) | PASS | Only the demo Roller is confirmed. |

### Enriched local and synthetic fixture cases

The equipment fixtures are fictional. E605 and E606 use the same inputs as their shared-catalogue counterparts and differ only by the local certificate evidence.

| Case | Consumer input | Mode | Expected offerings | Actual offerings | Result | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| E605 | spur gear, certifications: AS9100_D | strict | P-G (1) | P-G (1) | PASS | Lyss certificate applies to this gear offering. |
| E606 | spur gear, certifications: AS9100_D | lenient | P-G (1) | P-G (1) | PASS | Certification remains mandatory. |
| E604 | spur gear, certifications: ISO13485_2016 | lenient | None (0) | None (0) | PASS | Distribution evidence adds no manufacturing eligibility. |
| E619 | spur gear, certifications: ISO9001_2015, AS9100_D | strict | None (0) | None (0) | PASS | Separate providers cannot satisfy one AND request. |
| E797 | hollow shaft, wall thickness exact 5 mm | strict | fixture_hollow_shaft (1) | fixture_hollow_shaft (1) | PASS | Confirmed typed boundary. |
| E800 | hollow shaft, wall thickness exact 6 mm | lenient | None (0) | None (0) | PASS | Typed hard requirement fails. |
| E809 | block, number of holes exact 4 | strict | fixture_block (1) | fixture_block (1) | PASS | Block fixture confirms 4 holes. |
| E876 | collar, ISO 13485 with applicability unconfirmed | lenient | None (0) | None (0) | PASS | Unconfirmed certificate cannot pass the hard gate. |

### Why some searches return zero

- A lenient result still needs every hard dimensional, tolerance, finish, quality and certification criterion. Module 12 or an unconfirmed Crown gear leaves no candidate even if a stated material would match. ISO 9001 plus AS9100 stays conjunctive across the same offering and provider scope.
- Strict material and process selections require exact, confirmed codes. Lenient material alternatives evaluate one group and retain each selection's evidence. For Steel plus Titanium at Module 4, Tasowheel satisfies the material group through the published child. Titanium remains unconfirmed. Missing processes leave the candidate visible. A known 8–12 week lead exceeds a 6-week limit and is unmatched, while Precipart has no comparable delivery value.
- Inclusive exact values and one-sided or interval requests were exercised separately. A published upper bound alone cannot confirm an exact point under the existing range rule. Module and DP are checked against their individual ranges. The contradictory Module 1/DP 85 row returned both offerings as expected under that rule. A physical design constraint would require a separate contract decision.
- The retained demo shaft's exact detail contains legacy `{"value":2}`. Two scoped Spline module 2 requests returned Tasowheel's validated comparable range and excluded that demo offering in both modes. The current discovery path requires `exact`, `min` or `max` evidence for that input. The local fixtures exercise properly scoped exact evidence. Review normalization of this legacy record before using it as a positive acceptance fixture. [Legacy spline probe](assets/task16e-comprehensive-discovery-validation/legacy-spline-probe.json)
- The demo Block and Roller have partial type-scoped geometry. A confirmed type alone allows an unconstrained result. Additional specs still need matching evidence in the applicable group. Fictional fixture cases separately cover all controlled shaft/metal subtypes and known typed or dimensional limits.

## Coverage and reproducibility

| Dataset and path | Strict passed | Lenient passed | Failed | Total |
| --- | ---: | ---: | ---: | ---: |
| Shared snapshot evaluated in local canonical Django endpoint | 439 | 437 | 0 | 876 |
| Local certificate enrichment applied to same shared snapshots | 49 | 49 | 0 | 98 |
| Synthetic equipment and certification scopes in canonical endpoint | 206 | 206 | 0 | 412 |
| Protected shared Preview, sequential requests | 98 | 96 | 0 | 194 |
| Curated and synthetic direct, RDFLib and mocked Fuseki, repeat comparisons | 54 | 54 | 0 | 108 |
| Configured remote Fuseki, real read-only | 10 | 10 | 0 | 20 |

The 876 core vectors cover all 16 controlled types in both modes. The group counts are 134 gear single or interval checks, 26 gear cross-combinations, 30 accuracy checks, 36 batch, 24 weight, six tolerance and finish combinations, 50 material, 248 process, 82 certification, 30 material-plus-module, 12 delivery, 16 mixed certification/material/process/module, 74 shaft, 56 metal, 32 selection and 20 invalid or legacy-policy cases. Each mode includes every two-code combination for six materials, fifteen processes and eight certifications. Empty lists and duplicates have explicit cases. Hosted cases covered 150 gear, 20 shaft and 24 metal requests. The 194 cases included 87 valid empty-result responses and seven expected HTTP 400 responses.

Hosted offering appearances across all cases were **82 T-G, 43 P-G, six T-S, four D-M and four D-S**. By provider, strict yielded 37 Tasowheel, 16 Precipart and four Demo Metal Works appearances. Lenient yielded 51 Tasowheel, 27 Precipart and four Demo Metal Works appearances. Appearance counts include repeats across search cases.

The expectation function reads frozen capabilities and applies independent rules. It never calls the matcher. The actual side runs the canonical HTTP endpoint or H9 retrieval as the selected test requires. Every search receives a fresh request ID. The checks compare identities and ordering, exact requirement and provided evidence, hard exclusion, status and deterministic score. The hosted run stopped on unexpected access or server status by design. Twenty separate real H9 cases passed against 837 triples on the current validation graph. The Roller returned by both the API and the configured graph distinguishes the live dataset from the bundled fallback data, which lacks this offering. [Graph evidence](assets/task16e-comprehensive-discovery-validation/graph-connectivity.json)

| Evidence | Files |
| --- | --- |
| Shared Preview cases including actual canonical payloads and responses | [Hosted CSV](assets/task16e-comprehensive-discovery-validation/hosted.csv) · [Hosted JSON](assets/task16e-comprehensive-discovery-validation/hosted.json) |
| Shared, enriched and synthetic offline cases | [Offline CSV](assets/task16e-comprehensive-discovery-validation/offline.csv) · [Raw gzipped JSON](assets/task16e-comprehensive-discovery-validation/offline.json.gz) |
| Direct, RDFLib, mocked and actual Fuseki comparisons | [Alignment CSV](assets/task16e-comprehensive-discovery-validation/parity.csv) · [Alignment JSON](assets/task16e-comprehensive-discovery-validation/parity.json) |

From `mdc-catalog/backend` run `python scripts/validate_task16e_discovery.py offline --output ../docs/reports_phase4/assets/task16e-comprehensive-discovery-validation` with the supplied snapshot. The same runner supports `freeze` with `--origin`, `hosted`, and `parity`. Run the network modes with an approved local server-only `MDC_VERCEL_PROTECTION_BYPASS`. For live read-only parity set `TASK16E_READ_QUERY` to the existing validation SPARQL URL for that process. The runner writes result files to the specified output directory. [Deterministic runner](../../backend/scripts/validate_task16e_discovery.py)

## Regression and signed-in evidence

| Check | Result |
| --- | --- |
| Backend full suite | 597 collected, **584 passed**, 13 skipped. Django `call_command("test", "tests", interactive=False)` using in-memory SQLite, disabled live endpoints and disabled sync. The two new vocabulary and curated scope tests passed. The skipped legacy or opt-in tests target separate endpoint or seed datasets. The configured read-only equivalent is covered by the 20 live parity checks. |
| Initial backend failures | Two assertions expected a 673-triple curated graph and one required equality with the pre-enrichment normalized Precipart fixture. Updated those precise expected values for the verified 681-triple result and exact certificate record. Existing graph equality, sync behavior and canonical normalization assertions remain covered. |
| Initial matrix harness failures | The in-process Django client needed its `testserver` host enabled in the test configuration. Twelve subsequent comparisons had submitted family tolerance in the generic group. Moved those criteria to the scoped group and retained invalid-input coverage. Final matrix failures zero. |
| Frontend suite | **97 passed**, zero skips. `node --experimental-test-isolation=none --test` over six test files. Includes role and ETag guards, exact identity and stale evidence, retry/cache, material alternatives, and PDF. |
| Frontend lint/build | `next lint --file` across changed JS passed. `next build` in an isolated copy generated 20 static pages. The wider build emitted existing hook, stylesheet and Browserslist notices. |
| Signed-in Edge | Eight live cert options, both new selections sent as canonical codes, existing certification AND, material selection and keyboard clear, changes without Reset, six distinct standard search requests, published grades and comparison, 61,502-byte two-page PDF and contact toast. Strong ETags and cached detail reads were observed. |

The shared MaaSAIButton retained the Task 16C orange primary, navy light-mode outline, Dark and HMI accents and red destructive variants. Signed-in checks measured hover, active, focus, loading and disabled states. Provider lookup and Admin lookup each returned 200 with strong ETags. Provider had its red offering icon, Admin had its red Delete provider and the styled View provider and dialog close. Provider registration and update selectors each displayed the same eight live certificate choices. These operations used reads only. At 390 px the browser used 100 synthetic options in addition to the eight live codes. Keyboard filtering selected the last synthetic option, three chips wrapped within the control, and keyboard clear removed the selection. The browser made no search request with the synthetic catalogue.

| Representative visual | Evidence |
| --- | --- |
| Both new options selected | [Certification chips](assets/task16e-comprehensive-discovery-validation/new-certifications.png) |
| Partial preference and confirmed hard requirements | [Requirement comparison](assets/task16e-comprehensive-discovery-validation/03-partial-comparison.png) |
| Exact Tasowheel grades and scope | [Capability overview](assets/task16e-comprehensive-discovery-validation/04-published-capability-overview.png) |
| Provider and Admin actions | [Provider screenshot](assets/task16e-comprehensive-discovery-validation/provider-area-buttons.png) · [Admin screenshot](assets/task16e-comprehensive-discovery-validation/admin-area-buttons.png) |
| Downloaded PDF and informational flash | [Rendered PDF page](assets/task16e-comprehensive-discovery-validation/pdf-tasowheel-gears-page-1.png) · [Contact Provider](assets/task16e-comprehensive-discovery-validation/05-contact-provider-flash.png) |
| Sanitized signed-in checks | [Browser acceptance](assets/task16e-comprehensive-discovery-validation/browser-acceptance.json) · [Large certification selector](assets/task16e-comprehensive-discovery-validation/large-certification-control.json) · [Provider certificate controls](assets/task16e-comprehensive-discovery-validation/provider-certification-controls.json) · [Button variants](assets/task16e-comprehensive-discovery-validation/theme-verification.json) |

## Deployment and branch evidence

| Item | Observed state |
| --- | --- |
| Fetched `origin/main` | `931a9c7d619edbfabee3ebfc5157af203fdb945e` |
| Task start and ancestry | `90b7e8514adf7e643f9439dc57f9c2f9095f5350` on Task 16D `aa99911b73a3825d4b481faa1df050b768d2db4d` |
| Task 16C | Verified implementation `70a39d879305fe3d776423c97bf6160bcc79de90`, report head `e1fa1922e468f7b1465b62a1ab0860e3e64d15d1`. Consolidated at `1272d2a`. Retained one chip/payload implementation and one shared action theme. |
| Backend Preview source | `cb3ebee8be3ffde1114f5716c0680cc0eb0a83aa`, backend ZIP SHA-256 `240702adf5f0ec2094cd7f35b0cd37f7ef34e60e64d4481f0abf72703c8defd3`. The three changed Python file hashes and the pre-enrichment Precipart file matched the deployment manifest. |
| Protected Preview | `dpl_E9yPk9DD7qH89KawnDzJrnfgKazV`, Ready in `iad1`, anonymous health 302. Existing Preview database binding and deployment-scoped validation SPARQL. Both sync flags, publication, validation, and legacy demo features configured false. Lifecycle actor/ETag requirements retained. |
| 16E implementation | `30fab2ac2a7e20e1bbdc3a1ed0b01839987a5244` contains the local certificate, generated RDF, regression runner and unified read-only relay. The final report commit is the branch tip on publication. |
| Local browser | The permanent :3000 Task 16C checkout retained its edits, untracked logo, two stashes, installed dependencies and environment files. Task 16D :3001 was left running. Task 16E runs at :3002 from its separate worktree. All signed-in catalogue reads, exact details and search share the new pinned Preview. Existing guarded lifecycle writes retain their original route and were never used. The server-only bypass value appeared in zero of 54 built client JS files. |
| Stable production | `dpl_AdG2ZD9Lhic25LQ4E6rf7YJLgsPF` before and after. Task 15 source `c6980293c5de9fd1e9d7449d664be8fa847d3a2e`. The same smoke evidence produced SHA-256 `091b2165acf70056d1310993b66343e616c9a58c35d81c0052f40fc3b17ab2e7` before and after. |

[Protected Preview](https://maasai-mdc-v1-pi9dh538z-mdc19.vercel.app/api/health) · [Vercel deployment](https://vercel.com/mdc19/maasai-mdc-v1/E9yPk9DD7qH89KawnDzJrnfgKazV) · [Production smoke comparison input and results](assets/task16e-comprehensive-discovery-validation/production-strict-before.json)

### Review and next release gate

Open the running local Task 16E Consumer page, sign in through MaaSAI Keycloak and choose Consumer. Compare a clean Spur gear search at Module 1 and 4, then add Steel and Titanium and expand Tasowheel. Select AS9100 separately to reproduce the current shared-data result. For a restart, use the Task 16E worktree at `%TEMP%/mdc-task16e/mdc-catalog/demo-frontend`, provide the existing server-only Preview bypass through the authorized local process environment, and run `npm run dev -- --hostname 127.0.0.1 --port 3002`. [Local Consumer](http://localhost:3002/demo/consumer-search)

To close the release gate, provision an approved deployment-scoped binding for the paired validation PostgreSQL and Graph Store endpoints within the existing protected environment. Run the production-equivalent revision checks with both sync flags and the guarded runtime, using read-only requests and disabled publication paths. Confirm the current tunnel and repeat discovery for the synchronized Roller. Approve separate publication and synchronization of the scoped Precipart certificate only after site and validity review. The Partner API guide, Postman matrices and single stable production frontend routing belong to a separately approved release. The current branch and Preview are available for independent acceptance.
