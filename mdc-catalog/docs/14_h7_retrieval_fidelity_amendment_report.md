# MaaSAI MDC — H7 RDFLib Retrieval Fidelity Amendment Report

## 1. Amendment purpose and status

This is Step 2 of the controlled H6-H9 fidelity repair.

Step 1 amended the H6 RDF representation. Step 2 amends H7 local RDFLib query/projection reconstruction only.

H8 remote Fuseki retrieval and H9 strict matching equivalence remain pending later steps.

Endpoint migration remains blocked.

## 2. Accepted Step 1 prerequisite

The repository owner confirmed that focused H1-H6 verification passed after the H6 RDF evidence-fidelity amendment. Exact repository-owner test count/time was not supplied.

H7 now consumes these H6 predicates/structures:

```text
mdc:normalizedOrder
mdc:explicitNullField
mdc:sequenceIndex
mdc:hasAvailableGradeEvidence
mdc:AvailableGradeEvidence
mdc:availableGrade
```

## 3. H7 query amendment

Candidate-query semantics are unchanged:

- service category and part family remain mandatory candidate scope;
- requested part-type support remains optional;
- unasserted requested subtype candidates remain retrievable.

The evidence query now projects:

- normalized order for capability evidence;
- explicit-null member markers for capability evidence;
- material, process and certification sequence indexes;
- ordered available-grade child evidence;
- existing flat `mdc:availableGrade` literals for backward compatibility;
- existing provenance/confidence/source-note values.

No H5 matching, scoring, result filtering or external search response construction was added.

## 4. H7 reconstruction amendment

Reconstruction now:

- maps `mdc:normalizedOrder` to `normalized_order`;
- maps `mdc:explicitNullField "max"` to an actual `"max": None` member;
- orders material evidence by `mdc:sequenceIndex` where present;
- prefers ordered grade evidence children for `available_grades`;
- falls back to flat `mdc:availableGrade` literals when ordered grade evidence is absent;
- avoids grade duplication when both flat and ordered grade evidence exist;
- orders process evidence by `mdc:sequenceIndex`;
- orders provider-certification evidence by `mdc:sequenceIndex`;
- strips internal sequence metadata from returned evidence dictionaries.

Ordering metadata is not exposed as a process route, operation sequence or search criterion.

## 5. Shared H7/H8 helper impact

`service_discovery_sparql_service.py` contains projection helpers shared by H8. Step 2 modified those helpers to reconstruct the new fidelity metadata when rows contain it.

Public helper/function signatures were preserved.

`service_discovery_fuseki_service.py` was not modified. H8 has not been verified in Step 2. Step 3 must regenerate/load the amended harmonized RDF into the dedicated Fuseki dataset and explicitly verify remote Fuseki retrieval fidelity.

## 6. Files modified and created

Modified files:

- `backend/apps/search/service_discovery_sparql_query_builder.py`
- `backend/apps/search/service_discovery_sparql_service.py`
- `backend/tests/test_service_discovery_sparql_query_builder.py`
- `backend/tests/test_service_discovery_sparql_service.py`
- `docs/13_h6_rdf_evidence_fidelity_amendment_report.md`

Created file:

- `docs/14_h7_retrieval_fidelity_amendment_report.md`

No H8 or H9 code/test was modified.

No YAML was modified.

No generated Turtle was regenerated or modified.

No Fuseki reload occurred.

No API, matcher-policy, settings, Docker or persistence file was modified.

## 7. Tests added or updated

Updated H7 query-builder tests prove projection of:

- `normalized_order`;
- explicit-null markers;
- sequence indexes;
- ordered available-grade evidence nodes;
- retained provenance/confidence;
- material grades as evidence only.

Updated H7 retrieval-service tests prove:

- Tasowheel gear `diametral_pitch.normalized_order = "ascending"`;
- Tasowheel gear and shaft `surface_finish_ra_um.max = None`;
- absent fields such as `tolerance_mm` are not reconstructed as explicit null evidence;
- available-grade order is `18CrNiMo7-6`, `16MnCr5`, `20MnCr5`;
- ordered grades are not duplicated by flat literals;
- Tasowheel process evidence preserves publication order;
- Tasowheel provider certifications preserve provider-level publication order;
- confirmed/candidate/not-asserted semantics remain intact;
- H7 remains retrieval-only.

## 8. Runtime verification responsibility

The repository owner will run focused H1-H7 verification after this Step 2 H7 retrieval-fidelity amendment. H8 and H9 tests are intentionally deferred until later controlled steps.

Codex local focused H1-H7 verification passed:

```text
Ran 184 tests in 4.495s

OK
```

The repository owner confirmed that focused H1-H7 verification passed
successfully after the Step 2 H7 retrieval-fidelity amendment.

Exact repository-owner test count and elapsed time were not supplied and
are therefore not recorded.

No full legacy test-suite claim is made.

## 9. Focused Step 2 verification command

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract tests.test_service_discovery_provider_loader tests.test_service_discovery_local_matcher tests.test_service_discovery_local_search_response tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_generate_service_discovery_rdf_command tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service -v 2
```

Do not run the full legacy suite.

## 10. Deferred steps

```text
Step 3: Amend/verify H8 remote Fuseki retrieval fidelity, regenerate the
        harmonized Turtle, reload only the dedicated harmonized Fuseki dataset,
        and verify local-versus-remote retrieval equivalence.

Step 4: Rerun H9 strict H5 matching alignment through direct YAML, local RDFLib
        and remote Fuseki paths, then issue the endpoint-migration readiness
        decision.
```

## 11. Completion checklist

- [x] Step 1 focused verification closure recorded.
- [x] H7 candidate-query semantics remain unchanged.
- [x] H7 evidence query projects normalized_order.
- [x] H7 evidence query projects explicit-null markers.
- [x] H7 retrieves sequence-index ordering metadata.
- [x] H7 retrieves ordered available-grade evidence nodes.
- [x] normalized_order is reconstructed.
- [x] Explicit nulls are reconstructed as None values.
- [x] Material-grade order is preserved without duplication.
- [x] Process order is preserved as evidence order only.
- [x] Provider-certification order is preserved.
- [x] Confirmed/candidate/not-asserted semantics remain intact.
- [x] H7 remains retrieval-only.
- [x] No H8/H9/YAML/Turtle/Fuseki/API/settings changes made.
- [x] Repository owner ran focused H1-H7 verification.
- [x] Ready for Step 3 H8 retrieval-fidelity amendment.
