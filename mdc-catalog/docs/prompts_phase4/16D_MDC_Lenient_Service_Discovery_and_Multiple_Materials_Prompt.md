# Task 16D — Lenient service discovery and multiple-material selection

**Status:** Development authorization — protected Preview only, not a production release.
**Repository:** samola4real/mdc_v1
**Task branch:** phase4/task16d-lenient-service-discovery
**Starting reference:** main, observed at 931a9c7d619edbfabee3ebfc5157af203fdb945e (Task 16B report). Verify branch ancestry and actual checkout before work.
**Report:** mdc-catalog/docs/reports_phase4/16D_MDC_Lenient_Service_Discovery_and_Multiple_Materials_Report.md

## 1. Objective and authoritative context

Make discovery less restrictive for optional material and manufacturing-process preferences, while retaining confirmed technical eligibility and offering-level evidence. Enable multiple material selections in the existing Consumer UI. Implement, test, deploy to a new protected backend Preview, validate the signed-in local frontend, and publish a comprehensive Markdown report in this single task. Do not wait after the routine audit for another implementation prompt.

Read the existing H5/H9 design and tests, the current source, and these accepted references first:
- docs/reports_phase4/14A_MDC_Strict_Technical_Eligibility_Correction_Report.md
- docs/reports_phase4/15_MDC_Vercel_Production_Release_and_Marketplace_API_Access_Report.md
- docs/reports_phase4/16A_MDC_Consumer_UI_Consolidated_Refinement_Report.md
- docs/reports_phase4/16B_MDC_Consumer_Offering_Details_and_Actions_Report.md
- docs/Partner_API/MaaSAI_MDC_API_Documentation.md and existing integration guide/Postman assets.
Paths above are relative to mdc-catalog. Locate the H5/H9 implementation reports in the repository; do not rely solely on the original Week 1 API contract.

Task 14A deliberately made every supplied criterion hard, normalized even legacy any/score_only and keep_as_unknown policies to strict, and emitted full_match / score 1.0 for eligible offerings. Task 15 released that contract to Marketplace. Do not call this intentional design a bug; this task adds a controlled lenient discovery capability, not a rollback of technical eligibility. Task 16B already implemented exact offering/provider reads, expanded capability overview with grades grouped by material, comparison, PDF export and Contact Provider toast. Preserve that work.

## 2. Baseline, worktree and release boundary

Fetch origin; read this prompt from the task branch. Record HEAD, origin/main, status, relevant diffs, and exact Task 15 deployed backend source. Verify the actual source tree against the released backend package (source c6980293c5de9fd1e9d7449d664be8fa847d3a2e per Task 15) and document any relevant later changes. Start from latest compatible accepted backend/frontend code, not a new repository, old YAML-only prototype or a production runtime edit. Use a separate worktree or task branch without disturbing existing changes, ignored configuration, stashes or Task 16C work. Task 16C has a separate existing branch phase4/task16c-consumer-certifications-button-theme; inspect its status and avoid overwriting or silently merging unfinished work. Preserve accepted certification AND semantics irrespective of that branch. Report integration dependencies.

Existing production project mdc19/maasai-mdc-v1 (prj_DekMQdOYuuH0A5yNsCkFmOC4uD9j), stable https://maasai-mdc-v1.vercel.app, deployment dpl_AdG2ZD9Lhic25LQ4E6rf7YJLgsPF as observed in Task 15 and confirmed Ready. Verify again before and after Preview testing. Keep stable aliases, current production deployment, previous Previews, production environment and Marketplace consumers unchanged. No production deploy, promotion, alias assignment, merge to main, or production configuration change. Preserve existing deployment protection and use server-only authorized Preview access. Do not publish secrets. Preview and production may share the validation PostgreSQL and Fuseki graph: use isolated local fixtures for writes; hosted tests must be read-only. Never modify published providers, delete records, manually write RDF or run sync on the shared graph for this task. Do not introduce additional infrastructure; if a necessary environment is unavailable, report the blocker.

## 3. Matching policy and contract compatibility

Use the existing canonical POST /api/service-discovery/search (contract_version 1.0), controlled vocabulary and shared matching paths. Keep existing strict mode as the default for absent policy and preserve every previously accepted legacy policy combination and strict response shape/semantics. This is necessary because the released Partner API explicitly promises strict matching even for old score_only requests.

Introduce a minimal, explicitly opted-in, additive discovery policy (preferred proposed shape match_policy.discovery_mode = "lenient", default "strict"; verify actual serializer and use one clear documented equivalent if needed). Do not silently reinterpret existing legacy policy values to enable leniency, invent a second endpoint, or change the existing contract version. Reject unsupported mode values with canonical validation. Document the new field and precise behavior in the task report and clearly marked Preview/development API examples; do not alter the released Marketplace handoff documentation to imply the feature is already live. Make the Consumer UI explicitly request the new lenient policy. The stable strict default remains until a separately approved release decision. Do not add an elaborate mode toggle to the demo UI.

Lenient mode:
- Required service category, part family, part type and confirmed subtype support retain the Task 14A candidate gate. Preserve existing form inputs and derive category only as already implemented; do not add new required fields.
- Hard: every supplied module, diametral pitch, relevant diameter, dimensions/bounding-box components, weight, batch size, quality, tolerance, surface finish and mandatory certification. Preserve exact/range/upper-limit interpretation, units, inclusive bounds, offering-level scope, and all existing Task 14A evidence requirements. Unknown or contradictory hard evidence cannot qualify as confirmed eligible. Omitted/empty values have no effect. Multiple certifications remain AND. Do not classify an unknown hard capability as eligible.
- Soft: material families, manufacturing processes, lead time and supported industry preferences. No soft mismatch or missing information may eliminate a candidate that passed the hard gate in lenient mode. Keep actual evidence for each submitted preference, distinguish matched from unmatched and unknown, and preserve public capability scope. Where explicit negative evidence exists, show unmatched; absence of confirmation is unknown, not proof of impossibility. No hidden default cutoff; do not allow legacy score thresholds or all/reject_unknown to silently defeat lenient discovery. Define and test the treatment of explicit minimum_score in lenient mode (prefer clear rejection of conflicting policy or no cutoff rather than silently misinterpreting it); preserve strict behavior. Document mode precedence and validation.
- Multiple materials in lenient mode are acceptable alternatives (OR). Any semantically supported selected family satisfies the material preference group; evaluate and display each selected value independently. If none matches, retain candidate and report unmatched/unknown preferences; do not claim actual material eligibility. If consumers must satisfy every material, strict mode remains available to API callers. Multiple processes are preferences, with evidence for each, not a mandatory intersection. No advanced ranking or Recommendation System functionality.
- Return accurate full_match/partial_match and bounded, deterministic score using existing response structures. Full match only when applicable hard criteria and preference groups are satisfied; retain per-value unresolved evidence even when an OR group matches, with a clear comparison label. Explicitly document how mixed OR alternatives affect status and score. Do not double-penalize redundant parent/child alternatives, count omitted criteria, rank providers by advanced scoring, or claim an unconfirmed material capability. Preserve deterministic offering ordering. Make clear that lenient results pass hard checks but may require confirmation of preferences; do not forward them as strict RS eligibility without that distinction.

## 4. Semantic material matching and multi-select

Inspect service_discovery_request.py, service_discovery_local_matcher.py, RDFLib and Fuseki query/retrieval paths, controlled material vocabulary and ontology mappings, canonical normalization and current tests. Verify that a request for steel can match the narrower alloyed_carburizing_steel where the existing ontology provides a supported relationship; preserve the direction and provenance of inference and do not infer arbitrary grades from generic steel. Apply this improvement in the new lenient mode; preserve strict release behavior unless the task proves an existing documented semantic relationship is already expected and changing it cannot broaden the released strict contract. Do not hardcode Tasowheel or any provider. Check whether the live published Tasowheel offering and synchronized graph actually declare steel, alloyed_carburizing_steel, and their grades. Compare to approved pilot assumptions; do not overwrite production data. Do not label unsupported grades as published. Keep material_grades informational only; separate material_grades search input remains rejected (HTTP 400) as specified by current contract.

Replace the single-select Material dropdown with the existing multi-select pattern (as used for Manufacturing processes and Certifications), consistent styling, controlled options from GET /api/catalog/filters, keyboard/accessibility behavior, individual deselection and clear all, optional blank selection, and reset behavior. Send all chosen canonical material values as the existing requirements.materials array after confirming actual schema; no string concatenation, duplicate entries, or new API shape for material lists. Empty list/omitted field must not constrain results. Verify selection state across repeated searches, resets and clear actions. Do not add a material-grade input. Keep existing multiple process/certification selectors and current form design. Avoid changes to other UI features.

Update Task 16B result rendering minimally so partial matches and missing/unmatched soft preferences are visible and not rejected as inconsistent detail evidence. Display requested versus supported materials/processes and truthful per-value status; no blanket Matched or Eligible label that misrepresents full material suitability. Preserve exact provider/offerings reads, identity checks, stale-record checks, safe published material-grade grouping, result-detail caching/reset, PDF export (reflect actual comparison/status), Contact Provider toast and existing signed-role/relay protection. Do not expose arbitrary custom fields, private notes or server credentials. Preserve all other frontend routes and behavior.

## 5. Required acceptance tests

First reproduce the existing restrictive behavior against the strict baseline with exact payloads, then test the new opt-in path. Use real Tasowheel/Precipart records read-only for Preview observations; derive assertions about actual published materials from exact reads, not assumed seed data. For cases needing specific data, use explicit synthetic fixtures separately.

- Gear/spur gear with no optional criteria: same relevant candidates as strict baseline.
- Steel alone: Tasowheel retained; mark matched if direct or supported semantic evidence, otherwise appropriately unknown/unmatched. Report actual evidence.
- Alloyed carburizing steel alone: same principle.
- Steel + alloyed carburizing steel: one offering result, correct OR grouping and per-value evidence.
- Steel + titanium: retain offering with supported steel and truthful other status.
- Aluminum + titanium: retain hard-eligible offerings with transparent unresolved material preferences, never claim these materials are supported.
- Multiple materials selected, then one removed, then all cleared, then Reset; verify requests and UI.
- Module 4: Tasowheel only on accepted live gear baseline; Module 1: Tasowheel and Precipart; Module 12: Tasowheel excluded; unsupported Crown gear: no results. Test exact inclusive boundary and missing hard evidence in fixtures.
- Steel + module 4: Tasowheel retained; any material preferences + module 12 cannot rescue it.
- Diameter 300 and 700 mm, batch 500 and 5000, and other hard range tests with appropriate fixtures; confirmed out-of-range excluded. Unknown hard surface finish/tolerance excluded from confirmed eligibility when requested.
- Multiple preferred processes including a missing or incompatible process: retained, explained.
- Multiple mandatory certifications: AND, and scope correct (offering and provider).
- No preference selected: no artificial score penalties.
- Strict mode (absent, explicit strict, legacy any/all/score_only and unknown values per existing accepted contract): preserve Task 14A/15 baseline, strict multiple materials/processes AND, full_match/1.0 and stable order; unsupported material_grades still 400.
- Unknown/invalid policy values, score threshold rules, mixed matched and unknown OR alternatives, semantic parent-child direction, no inference of all grades, deterministic results.
- Task 16B expansion, actual provider grade overview, accurate partial comparison, PDF and toast, no regressions to exact reads, role checks or stale-data handling.

Run focused H1–H9 and service-discovery tests, local YAML/RDFLib parity for both policies, configured remote Fuseki alignment tests using read-only checks or truly isolated fixtures only, provider lifecycle/sync local regressions, Partner API contract checks, frontend relevant tests/build and signed-in local browser acceptance if access is available. Do not modify old tests simply to conceal regressions. Record commands, totals, failures and skipped checks.

## 6. Vercel Preview and end-to-end verification

After local checks pass, deploy ONLY the updated backend package to a new protected Preview in the existing Vercel project. Confirm CLI auth, linked project, package source SHA and correct Preview binding before deploy. Reuse existing environment/protection safely; do not change project-wide env, production aliases or previous deployment. Verify anonymous generated Preview remains protected and authorized read-only health, filters, canonical search, provider/offerings GETs and deprecated route absence. Compare strict responses to Task 15 baseline and demonstrate lenient requests with the real published records. Verify current production alias still points to its original deployment; run safe read-only production smoke and confirm existing strict behavior unchanged.

Point only the task's local Consumer frontend/relay to the new protected Preview using existing safe server-only configuration; no browser-visible bypass secrets. Do not deploy the frontend to production. Test signed-in Consumer flow and multiple selections, partial status, expanded capability details, PDF and contact. Capture suitable non-secret screenshots and sanitized request/response evidence under reports_phase4/assets/task16d-lenient-service-discovery. If deployment/Keycloak/Fuseki access is blocked, finish what can be safely tested and report exact limitations; no workaround that bypasses access controls or uses live data writes.

## 7. Deliverables and Git protocol

Commit and push only task-relevant changes to phase4/task16d-lenient-service-discovery. Do not merge to main or promote production. Publish the comprehensive Markdown report at:
mdc-catalog/docs/reports_phase4/16D_MDC_Lenient_Service_Discovery_and_Multiple_Materials_Report.md

Include:
1. Executive summary and recommendation (READY FOR REVIEW / PARTIALLY VERIFIED / NOT READY).
2. Git baseline, current production source, task implementation commit, changed paths, final branch/status, Task 16C dependency handling.
3. Verified root cause; actual current serializer/matcher/query/renderer behavior; how Task 14A differs from new opt-in policy.
4. Final field classification, policy shape and precedence; examples for strict and lenient, multi-material OR and certification AND; scores/status/unknown handling.
5. Tasowheel exact published material/grade and graph evidence, any discrepancies, provenance; no unauthorized changes.
6. Implementation and minimal frontend changes; compatibility assessment and draft API examples for Preview, not a production handoff.
7. All acceptance cases with actual outcomes, sanitized payloads/evidence; separate fixture vs live cases.
8. Executed tests and counts, backend parity, build, security checks, any skips.
9. New protected Preview URL and deployment ID, code/package SHA, effective runtime/data binding (no secrets); proof production unchanged.
10. Signed-in frontend evidence/screenshots and PDF validation; local relay configuration method without secrets.
11. Risks, blockers, limitations, rollout/rollback plan and separately required approval for production.
12. Exact report URL and implementation/report commit IDs available at completion (report commit can be provided in final Codex message).

Do not mark the task ACCEPTED on behalf of the project owner/ChatGPT reviewer. Acceptance will follow independent review of the pushed report and evidence. Stop only for a genuine breaking-contract, security, environment, or unauthorized-data-change blocker; continue safe independent work. No production release or changes without separate approval.
