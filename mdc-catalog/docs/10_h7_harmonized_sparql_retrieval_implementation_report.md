# MaaSAI MDC — H7 Harmonized SPARQL Candidate and Evidence Retrieval Implementation Report

## 1. Status and scope

Phase: H7.

Purpose: deterministic SPARQL candidate and evidence retrieval over the harmonized RDF graph.

Execution is local through RDFLib only. H7 does not perform scoring or final matching. H5 remains the active reference implementation for local matching logic. No Fuseki, API endpoint, persistence or runtime activation occurred.

## 2. Verified prerequisites

Focused amended H1 + H2 + H3 + H4 + H5 verification:

```text
Ran 148 tests in 0.971s

OK
```

The repository owner confirmed that focused H1-H6 tests passed and that:

```text
data/generated/service_discovery/mdc_service_discovery_catalog.ttl
```

was generated.

Exact H1-H6 test count/time was not supplied in this task. No claim is made that the full legacy project test suite passes.

## 3. H6 completion-record update

`docs/09_h6_harmonized_rdf_generation_implementation_report.md` was updated only to record repository-owner H6 completion confirmation before H7.

## 4. New H7 architecture

```text
H4 CanonicalServiceDiscoverySearchRequest selection
-> service_discovery_sparql_query_builder.py
-> RDFLib Graph.query() over H6 harmonized Turtle/Graph
-> service_discovery_sparql_service.py internal candidate/evidence projection
```

H7 does not use Fuseki. H7 does not call the H5 matcher. H7 does not produce final external search-response objects. H7 does not score/filter candidates.

## 5. Candidate-query contract

Service category and part family are hard RDF candidate scope. Selected part-type support is retrieved through an `OPTIONAL` evidence block so that category/family candidates remain visible when requested part-type evidence is absent.

The retrieval projection distinguishes:

- `confirmed`;
- `candidate_requiring_confirmation`;
- `not_asserted`.

Absence is not unsupported. `not_asserted` means no requested part-type support evidence node was retrieved.

SPARQL construction uses controlled H6 RDF mappings and fails on unmapped identifiers instead of interpolating raw user text.

## 6. Evidence-query contract

Evidence is projected by selected offering URI resources.

The evidence query preserves:

- family capability scope;
- part-type capability scope;
- generic capability scope;
- material evidence and available-grade literals;
- process evidence;
- provider-scoped certification evidence;
- provenance and confidence.

Evidence grouping is deterministic and reconstructs material grades into one material evidence record per material evidence node. Available grades remain evidence only and are not consumer-grade filtering criteria.

## 7. Tasowheel retrieval outcome

Tasowheel confirmed gear part types retrieve as confirmed:

- `spur_gear`;
- `helical_gear`;
- `bevel_gear`;
- `worm_gear`.

Tasowheel confirmed shaft part types retrieve as confirmed:

- `splined_shaft`;
- `plain_shaft`;
- `hollow_shaft`.

Unasserted gear/shaft part types such as `crown_gear`, `stepped_shaft`, and `worm_shaft` remain `not_asserted` for Tasowheel.

Tasowheel gear evidence projection retrieves:

- `module`;
- `diametral_pitch`, including raw `DP 85-2.5`;
- `outside_diameter_mm`;
- `gear_quality`.

Tasowheel shaft evidence projection retrieves:

- `length_mm.max = 500` with preserved provenance/confidence;
- `outer_diameter_mm`;
- subtype-scoped `splined_shaft.spline_module`.

Tasowheel material, process and provider certification evidence is retrievable. Deferred or unknown fields such as confirmed `face_width_mm`, general `tolerance_mm` derived from DIN4, shaft-family `module`, shaft-family `diametral_pitch`, shaft-family `gear_quality`, `spline_diametral_pitch`, `shaft_quality`, and `spline_quality` are not projected.

## 8. Precipart and other-provider handling

Precipart public/candidate evidence remains non-promoted. `crown_gear` is projected as `candidate_requiring_confirmation` with public-source/inferred provenance where present.

Demo-provider records are queried only through harmonized RDF evidence. No legacy provider data is read.

## 9. Files created and modified

Created H7 files:

- `backend/apps/search/service_discovery_sparql_query_builder.py`
- `backend/apps/search/service_discovery_sparql_service.py`
- `backend/tests/test_service_discovery_sparql_query_builder.py`
- `backend/tests/test_service_discovery_sparql_service.py`
- `docs/10_h7_harmonized_sparql_retrieval_implementation_report.md`

Modified existing file:

- `docs/09_h6_harmonized_rdf_generation_implementation_report.md`

No H6 RDF generator/mapping module was modified. No YAML was modified. No generated Turtle was overwritten by H7 implementation. No legacy RDF, API, matcher, Fuseki, SPARQL-client or settings module was modified.

## 10. Tests created

`backend/tests/test_service_discovery_sparql_query_builder.py` covers controlled candidate query construction, optional part-type evidence, shaft query construction, unmapped identifier rejection, evidence query `VALUES`, evidence `UNION` branches, provenance projection, material-grade evidence projection, and absence of legacy material-grade or bundled-offering predicates.

`backend/tests/test_service_discovery_sparql_service.py` covers graph loading, temporary Turtle parsing, missing/invalid/empty graph errors, graph-argument isolation, optional default generated Turtle smoke test, Tasowheel confirmed and not-asserted subtype retrieval, Precipart candidate preservation, non-matching/non-scoring output, evidence projection, deterministic grouping, and unmapped selection errors.

## 11. Runtime verification responsibility

The repository owner will run focused amended H1 + H2 + H3 + H4 + H5 + H6 + H7 tests in the activated Django-enabled `.venv`. The full legacy test suite is not required at this H-phase checkpoint.

## 12. Focused H1-H7 verification command

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract tests.test_service_discovery_provider_loader tests.test_service_discovery_local_matcher tests.test_service_discovery_local_search_response tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_generate_service_discovery_rdf_command tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service -v 2
```

## 13. Required H8/H9 considerations

1. H8 may add optional Fuseki-backed execution using the same controlled H7 SPARQL query templates, but it must use only the harmonized RDF dataset.

2. Fuseki loading must not mix `data/generated/mdc_catalog.ttl` with `data/generated/service_discovery/mdc_service_discovery_catalog.ttl`.

3. H8/H9 must preserve confirmed, candidate and not-asserted subtype distinctions when moving from local RDFLib query execution to remote SPARQL.

4. Final RDF-backed matching/scoring must remain consistent with H5 policy, especially for unknown evidence, optional-policy handling and no material-grade search criteria.

5. Shaft DP and shaft quality remain deferred until a separately approved schema decision exists.

6. Active API endpoint migration must occur only after local H5 and RDF/SPARQL retrieval outputs have been compared and accepted.

## 14. Issues before H8

No RDFLib SPARQL limitation was identified during implementation.

The H6 graph contract was sufficient for H7 candidate and evidence retrieval.

## Focused runtime verification defect and H7 repair

The repository owner ran focused H1-H7 verification.

Initial run failed:

```text
Ran 183 tests in 4.438s

FAILED (failures=1, errors=2)
```

Reported failures/errors:

- `test_unasserted_tasowheel_gear_and_shaft_subtypes_are_not_unsupported` errored because the Tasowheel candidate for requested `crown_gear` was absent from the retrieval output.
- `test_candidate_ordering_and_evidence_deduplication` errored because the same missing Tasowheel candidate led to evidence access on `None`.
- `test_retrieval_does_not_perform_matching_or_scoring` failed because the test searched the full response string for `"score"`, while the H7 contract permits `query_interpretation.match_policy.minimum_score` to be echoed for traceability.

Root cause after inspection:

- The candidate SPARQL query used the requested part-type variable directly inside the `OPTIONAL` support pattern. Although intended to be optional, RDFLib runtime behaviour in the focused test run lost category/family candidates that had other part-type support nodes but no support node for the requested type.
- Candidate reconstruction did not explicitly include `support_status`, `source_type`, and `confidence` keys with `None` values for absent support evidence.
- The retrieval-only test contained an implementation-independent assertion bug by rejecting the substring `"score"` anywhere in the response, including the allowed trace copy of `minimum_score` inside `query_interpretation`.

Repair performed:

- `backend/apps/search/service_discovery_sparql_query_builder.py` now binds support node part type as `?supportPartType` and applies `FILTER(?supportPartType = ?requestedPartType)` inside the `OPTIONAL` block. The only mandatory candidate constraints remain service category, part family, provider identity and offering identity.
- `backend/apps/search/service_discovery_sparql_service.py` now reconstructs absent requested subtype evidence as `evidence_status: not_asserted` and includes `support_status: None`, `source_type: None`, and `confidence: None`.
- `backend/tests/test_service_discovery_sparql_query_builder.py` was updated to assert the safer optional support filter pattern.
- `backend/tests/test_service_discovery_sparql_service.py` now explicitly asserts not-asserted Tasowheel candidates are present and verifies retrieval-only output by checking candidate structures rather than rejecting `minimum_score` inside query interpretation.

Focused H1-H7 verification remains pending repository-owner rerun after this repair.

No H6 RDF generator/mapping module, YAML, generated Turtle, legacy RDF, API, matcher, Fuseki, legacy SPARQL-client or settings file was modified.

## Final focused verification after H7 repair

Repository-owner H7-only verification after repair:

Command:

```text
python manage.py test tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service -v 2
```

Result:

```text
Ran 19 tests in 2.937s

OK
```

Repository-owner focused H1-H7 verification after repair:

Command:

```text
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract tests.test_service_discovery_provider_loader tests.test_service_discovery_local_matcher tests.test_service_discovery_local_search_response tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_generate_service_discovery_rdf_command tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service -v 2
```

Result:

```text
Ran 183 tests in 4.375s

OK
```

No claim is made that the full legacy project test suite passes at this checkpoint.

## 15. Completion checklist

- [x] H6 completion confirmation recorded.
- [x] Harmonized SPARQL query-builder module exists.
- [x] Harmonized RDFLib SPARQL retrieval-service module exists.
- [x] H7 reads only harmonized RDF graph/Turtle.
- [x] No Fuseki or active API integration occurred.
- [x] Candidate service-category/family scope is enforced.
- [x] Confirmed/candidate/not-asserted part-type evidence is distinguished.
- [x] Evidence scope and provenance are preserved.
- [x] Tasowheel amended evidence is retrievable correctly.
- [x] Precipart candidate/public evidence is not promoted.
- [x] Material grades remain evidence only.
- [x] H7 does not calculate final matches or scores.
- [x] H7 focused tests exist.
- [x] Repository owner ran focused H1-H7 verification successfully after repair.
- [x] Ready for H8 review.
