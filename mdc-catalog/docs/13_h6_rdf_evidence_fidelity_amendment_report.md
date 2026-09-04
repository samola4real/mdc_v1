# MaaSAI MDC — H6 RDF Evidence-Fidelity Amendment Report

## 1. Amendment purpose and status

This is Step 1 of a controlled H6-H9 fidelity repair.

H9 correctly exposed RDF-backed strict-equivalence blockers. This step modifies only the H6 RDF representation and H6 tests so later retrieval/reconstruction steps can preserve direct YAML evidence shape more exactly.

H7, H8 and H9 remain unchanged and are not expected to pass strict equivalence until later steps.

Endpoint migration remains blocked.

## 2. H9 blocker baseline

H9 local alignment test result reported by Codex:

```text
Ran 16 tests in 1.921s

FAILED (failures=8)
```

Blocker categories from the H9 report:

```text
- missing normalized_order projection;
- missing explicit null evidence values;
- altered available_grades order;
- altered process and provider-certification evidence order.
```

## 3. Actual YAML evidence inspected

Actual `diametral_pitch.normalized_order` evidence:

- Path: `tasowheel.yaml` -> `offerings[0].family_capabilities.diametral_pitch.normalized_order`
- Value: `ascending`
- Python/YAML type: `str`

Explicit null-valued evidence fields found:

- `tasowheel.yaml` -> `offerings[0].generic_capabilities.surface_finish_ra_um.max: null`
- `tasowheel.yaml` -> `offerings[1].generic_capabilities.surface_finish_ra_um.max: null`

Tasowheel available-grade list order in both gear and shaft offerings:

```text
18CrNiMo7-6
16MnCr5
20MnCr5
```

Tasowheel process list order in both gear and shaft offerings:

```text
machining
hobbing
gear_shaping
deburring
hard_turning
grinding
tooth_grinding
gear_grinding
gear_cutting
surface_grinding
milling
turn_mill
```

Tasowheel provider-certification list order:

```text
ISO9001_2015
ISO14001_2015
ISO_TS_16949_partial
APQP
```

No equivalent RDF properties for normalized order, explicit null markers, declared sequence index, or ordered available-grade evidence existed before this amendment.

## 4. RDF representation amendment

`normalized_order` is represented with:

```text
mdc:normalizedOrder
```

Explicit null-valued capability members are represented with:

```text
mdc:explicitNullField
```

Declared sequence order is represented with zero-based:

```text
mdc:sequenceIndex
```

Sequence indexes are emitted for material evidence records, process evidence records and provider-level certification evidence records.

Available grades retain the existing backward-compatible flat literal representation:

```text
mdc:availableGrade
```

Additionally, every available grade now has a deterministic ordered child evidence node:

```text
mdc:hasAvailableGradeEvidence
mdc:AvailableGradeEvidence
mdc:availableGrade
mdc:sequenceIndex
```

The new ordered process evidence metadata records YAML publication-list order only. It is not a route, route step, manufacturing operation sequence, machine sequence, or process-order model.

## 5. Files modified and created

Modified files:

- `backend/apps/ontology/service_discovery_rdf_mappings.py`
- `backend/apps/ontology/service_discovery_rdf_generator.py`
- `backend/tests/test_service_discovery_rdf_mappings.py`
- `backend/tests/test_service_discovery_rdf_generator.py`
- `backend/tests/test_generate_service_discovery_rdf_command.py`

Created file:

- `docs/13_h6_rdf_evidence_fidelity_amendment_report.md`

No YAML was modified.

No generated Turtle file was modified by Codex.

No H7/H8/H9 code or test file was modified.

No API, matcher-policy, Fuseki, settings, Docker or persistence file was modified.

## 6. H6 tests added or updated

Updated H6 tests prove:

- `normalized_order` is represented as `mdc:normalizedOrder`;
- explicit null differs from absent numeric evidence through `mdc:explicitNullField`;
- material evidence has recoverable `mdc:sequenceIndex`;
- available-grade order can be recovered through ordered `mdc:AvailableGradeEvidence` nodes;
- flat `mdc:availableGrade` triples remain present;
- process evidence order can be recovered from `mdc:sequenceIndex`;
- provider-certification order can be recovered from `mdc:sequenceIndex`;
- route/process-sequence properties are not introduced;
- earlier Tasowheel evidence-scope protections remain satisfied.

## 7. Runtime verification responsibility

The repository owner will run focused H1-H6 verification only after this Step 1 H6 RDF amendment. H7/H8/H9 tests are intentionally not part of the Step 1 acceptance gate because their retrieval/reconstruction updates are scheduled for later amendment steps.

Codex local focused Step 1 verification passed:

```text
Ran 164 tests in 1.338s

OK
```

The repository owner confirmed that focused H1-H6 verification passed
successfully after the Step 1 RDF representation amendment.

Exact repository-owner test count and elapsed time were not supplied and
are therefore not recorded.

No full legacy test-suite claim is made.

## 8. Focused Step 1 verification command

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract tests.test_service_discovery_provider_loader tests.test_service_discovery_local_matcher tests.test_service_discovery_local_search_response tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_generate_service_discovery_rdf_command -v 2
```

Do not run the full legacy suite for this Step 1 checkpoint.

## 9. Deferred work after Step 1

```text
Step 2: Amend H7 RDFLib retrieval projection to retrieve/reconstruct
        normalized_order, explicit null values and declared evidence ordering.

Step 3: Amend H8 remote Fuseki retrieval/equivalence, regenerate harmonized
        Turtle, reload the dedicated harmonized Fuseki dataset and verify
        local-versus-remote retrieval fidelity.

Step 4: Rerun H9 strict matching alignment and produce endpoint-migration
        readiness decision.
```

## 10. Completion checklist

- [x] H9 fidelity blockers recorded.
- [x] Actual YAML evidence shapes inspected and documented.
- [x] normalized_order RDF representation implemented.
- [x] Explicit null RDF representation implemented.
- [x] Material-evidence sequence representation implemented.
- [x] Ordered available-grade RDF evidence representation implemented.
- [x] Process-evidence sequence representation implemented.
- [x] Certification-evidence sequence representation implemented.
- [x] Existing evidence-scope protections preserved.
- [x] No YAML/H7/H8/H9/API/Fuseki/settings changes made.
- [x] H6 amendment focused tests exist.
- [x] Repository owner ran focused H1-H6 verification.
- [x] Ready for Step 2 H7 retrieval-projection amendment.
