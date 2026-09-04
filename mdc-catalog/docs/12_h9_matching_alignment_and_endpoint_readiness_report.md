# MaaSAI MDC — H9 Matching Alignment and Endpoint-Migration Readiness Report

## 1. Status and scope

Phase: H9.

Purpose: prove that H5 matching/scoring outcomes can be reproduced when evidence is retrieved through harmonized RDFLib and Fuseki paths.

H9 implements a request-scoped evidence-to-H5 adapter in `backend/apps/search/service_discovery_matching_alignment.py`.

H9 does not activate the active API endpoint. Endpoint migration remains a separate explicit approval decision after H9 verification.

## 2. Verified prerequisites

Focused amended H1 + H2 + H3 + H4 + H5 verification:

```text
Ran 148 tests in 0.971s

OK
```

H7-only repaired verification:

```text
Ran 19 tests in 2.937s

OK
```

Focused H1 + H2 + H3 + H4 + H5 + H6 + H7 verification:

```text
Ran 183 tests in 4.375s

OK
```

The repository owner confirmed successful focused H1-H8 unit verification and opt-in remote Fuseki integration/equivalence verification against the dedicated `mdc-service-discovery` dataset. Exact H8 test counts and elapsed times were not supplied and are therefore not recorded.

No claim is made that the full legacy project test suite passes.

## 3. H9 architecture

Direct baseline:

```text
H5 matcher <- harmonized YAML
```

Local RDF-backed alignment:

```text
H5 matcher <- H9 request-scoped adapter <- H7 RDFLib retrieval <- harmonized RDF
```

Remote Fuseki-backed alignment:

```text
H5 matcher <- H9 request-scoped adapter <- H8 Fuseki retrieval <- dedicated harmonized RDF dataset
```

The implementation uses `search_service_discovery_catalog()` for final matching/scoring in every H9 path.

## 4. Request-scoped adapter contract

The adapter validates that:

- `query_interpretation.selection` matches the supplied canonical request selection;
- `status.retrieval_executed` is `true`;
- `status.matching_executed` is `false`;
- candidate, provider, offering and evidence blocks have the expected projection shape.

It reconstructs only request-scoped H5 provider records:

- provider identity and display name;
- returned candidate offerings only;
- selected service category and part family;
- confirmed or candidate requested part-type support only when retrieved;
- family capabilities under `offering.family_capabilities`;
- part-type capabilities under `offering.part_type_capabilities[part_type]`;
- generic scalar capabilities under `offering.generic_capabilities`;
- materials and processes under generic capabilities;
- provider-scoped certifications under `provider.certifications`.

Confirmed/candidate/not-asserted handling:

- `confirmed` becomes a supported part-type record with `support_status: confirmed`;
- `candidate_requiring_confirmation` becomes a supported part-type record with `support_status: candidate_requiring_confirmation`;
- `not_asserted` becomes `supported_part_types: []` for the reconstructed offering.

Material grades remain nested under material evidence as `available_grades`. The adapter does not create material-grade search criteria and does not persist reconstructed records.

## 5. Matching-policy reuse

H5 remains the sole matching/scoring source for unknown policy, optional-match policy, minimum score, scoring, result status and ordering.

H9 does not duplicate scoring logic. It only adapts H7/H8 retrieval evidence into H5 provider-record input and replaces backend-identifying response status metadata after H5 returns.

The alignment comparison helper ignores only:

```text
status.search_engine
status.message
```

It preserves scores, match statuses, result order, matched/unmatched/unknown attributes, evidence, warnings, request identifiers and `status.search_executed`.

## 6. Tasowheel alignment outcomes

H9 local tests were added for:

- confirmed gear subtype requests;
- gear technical capability matching for `module`, `diametral_pitch`, `outside_diameter_mm` and `gear_quality`;
- `face_width_mm` remaining unknown;
- general `tolerance_mm` remaining unknown without DIN4 inference;
- material, process and provider-certification matching;
- confirmed `splined_shaft`;
- shaft family `length_mm`/`outer_diameter_mm` and subtype-scoped `spline_module`;
- unasserted subtype handling under `keep_as_unknown` and `reject_unknown`.

Strict YAML-versus-local-RDF equality is currently blocked by H7/H6 projection fidelity gaps listed in section 16.

## 7. Precipart and unknown-evidence outcomes

H9 tests cover Precipart `crown_gear` as `candidate_requiring_confirmation`. The adapter does not promote candidate evidence to confirmed evidence.

Tasowheel `not_asserted` subtype evidence is reconstructed as absent support evidence, not as unsupported.

Unknown-policy behaviour is delegated to H5.

## 8. Local-versus-remote alignment outcomes

The opt-in remote H9 test module compares:

```text
direct H5 YAML outcome
=
H9 local RDFLib-backed H5-policy outcome
=
H9 remote Fuseki-backed H5-policy outcome
```

except backend-identifying status metadata.

The remote tests cover:

- `precision_gears / gear / spur_gear`;
- `precision_gears / gear / crown_gear`;
- `precision_shafts / shaft / splined_shaft`;
- materials, processes and certifications;
- legacy Tasowheel offering exclusion;
- deferred shaft DP/quality and DIN4-derived tolerance absence;
- remote response serializer compatibility;
- `status.search_engine = harmonized_fuseki_with_h5_policy`.

Remote verification remains pending repository-owner execution against the already prepared dedicated harmonized Fuseki dataset.

## 9. Endpoint-migration readiness decision

Endpoint-migration readiness remains pending repository-owner H9 verification.

No active endpoint modification has been performed.

Current Codex local execution found evidence-fidelity blockers for strict direct-YAML versus RDF-backed H5-response equivalence. Endpoint migration is therefore not technically ready for approval until those blockers are resolved in a later phase or in an explicitly approved H6/H7/H8 amendment.

## 10. Files created and modified

Created H9 files:

- `backend/apps/search/service_discovery_matching_alignment.py`
- `backend/tests/test_service_discovery_matching_alignment.py`
- `backend/tests/test_service_discovery_fuseki_matching_alignment.py`
- `docs/12_h9_matching_alignment_and_endpoint_readiness_report.md`

No existing implementation, test, report, YAML, RDF/Turtle, API, matcher-policy, SPARQL/Fuseki, settings, Docker or persistence file was modified for H9.

The project files named in the H9 prompt were found under the actual Django project root `mdc-catalog/`.

## 11. Tests created

Created:

```text
backend/tests/test_service_discovery_matching_alignment.py
backend/tests/test_service_discovery_fuseki_matching_alignment.py
```

The local test module covers retrieval-projection validation, request-scoped provider-record reconstruction, status/evidence-scope preservation, direct H5 YAML versus H9 local RDF-backed matching comparison, key Tasowheel/Precipart/policy cases and comparison-helper safety.

The remote test module is skipped by default unless `RUN_SERVICE_DISCOVERY_FUSEKI_TESTS=1`, `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` is non-empty and `data/generated/service_discovery/mdc_service_discovery_catalog.ttl` exists.

## 12. Runtime verification responsibility

The repository owner will first run focused harmonized H1-H9 tests without remote Fuseki alignment dependency. Remote H9 Fuseki matching-alignment tests will then be run separately using the already prepared dedicated harmonized Fuseki dataset.

## 13. Focused H1-H9 local/unit verification command

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract tests.test_service_discovery_provider_loader tests.test_service_discovery_local_matcher tests.test_service_discovery_local_search_response tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_generate_service_discovery_rdf_command tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service tests.test_service_discovery_fuseki_service tests.test_service_discovery_matching_alignment -v 2
```

Do not include remote Fuseki integration/alignment tests in the first command.

## 14. Optional remote Fuseki H9 alignment verification command

The repository owner must retain:

```powershell
$env:SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="http://localhost:3030/mdc-service-discovery/query"
$env:RUN_SERVICE_DISCOVERY_FUSEKI_TESTS="1"
```

or use the exact already verified working endpoint.

Then run:

```powershell
python manage.py test tests.test_service_discovery_fuseki_matching_alignment -v 2
```

## 15. Endpoint activation decision after H9

Even if H9 equivalence tests pass, H9 does not modify the active API endpoint.
A separate explicit activation decision must specify:

- which harmonized execution backend becomes active;
- whether local H5 YAML matching or RDF/Fuseki-backed evidence retrieval is used;
- fallback behaviour if Fuseki is unavailable;
- deployment configuration for the dedicated harmonized dataset;
- endpoint contract migration and backwards-compatibility treatment;
- persistence strategy for request_id and consumer_id;
- operational monitoring and data-refresh procedure.

## 16. Issues before endpoint activation

Codex ran the H9 local test module with the repository virtual environment:

```text
..\..\.venv\Scripts\python.exe manage.py test tests.test_service_discovery_matching_alignment -v 2
```

Result:

```text
Ran 16 tests in 1.921s

FAILED (failures=8)
```

After repairing the selection-mismatch test, syntax checks passed:

```text
..\..\.venv\Scripts\python.exe -m py_compile apps\search\service_discovery_matching_alignment.py tests\test_service_discovery_matching_alignment.py tests\test_service_discovery_fuseki_matching_alignment.py
```

Identified blockers for strict H9 equivalence:

- H7/H8 retrieval projection does not expose `normalized_order` from Tasowheel `diametral_pitch`, while direct H5 YAML evidence includes it.
- H6/H7 projection omits explicit `null` evidence values such as `surface_finish_ra_um.max: null`, while direct H5 YAML evidence includes them.
- H7 material-grade grouping sorts `available_grades`, while direct H5 YAML preserves publication order.
- H7 evidence grouping sorts process and provider-certification evidence, while direct H5 YAML preserves publication order.
- These differences are visible in matched attributes and evidence blocks. The H9 comparison helper must not suppress them.

No response serializer incompatibility was identified for the new H9 engine strings during syntax/import-level implementation.

Remote equivalence remains pending and is expected to hit the same projection-fidelity blockers unless H7/H8 projection fidelity is amended first.

The endpoint backend/fallback decision remains unresolved. Request persistence remains outside the current activation.

## 17. Completion checklist

- [x] H9 request-scoped retrieval-to-H5 adapter exists.
- [x] H9 local RDF-backed H5-policy search wrapper exists.
- [x] H9 remote Fuseki-backed H5-policy search wrapper exists.
- [x] H5 scoring/matching policy is reused without reimplementation.
- [x] Confirmed/candidate/not-asserted subtype scope is preserved.
- [x] Materials/grades/processes/certifications remain correctly scoped.
- [x] Tasowheel key alignment cases are tested.
- [x] Precipart candidate/unknown alignment cases are tested.
- [x] Local RDF-backed matching equivalence tests exist.
- [x] Opt-in remote Fuseki-backed matching equivalence tests exist.
- [x] Active API endpoint remains unchanged.
- [x] No existing implementation/data/configuration file was modified.
- [ ] Repository owner ran focused H1-H9 local/unit verification.
- [ ] Repository owner ran opt-in remote H9 Fuseki alignment verification.
- [x] Endpoint-migration readiness recommendation recorded.

## Step 4 strict alignment rerun after H6-H8 evidence-fidelity repair

### 1. Repair prerequisites completed

Step 1 repaired H6 RDF representation for normalized_order, explicit null members and declared evidence ordering.

Step 2 repaired H7 local RDFLib reconstruction for normalized_order, explicit null values and declared grade/process/certification ordering.

Step 3 verified H8 remote Fuseki retrieval fidelity after regeneration and dedicated dataset reload.

Repository-owner Step 3 remote H8 verification result:

```text
Ran 4 tests in 1.409s

OK
```

### 2. Codex local H9 rerun result

Codex first reran the existing H9 local alignment tests:

```powershell
..\..\.venv\Scripts\python.exe manage.py test tests.test_service_discovery_matching_alignment -v 2
```

Initial Step 4 result before H9-specific repair:

```text
Ran 16 tests in 2.347s

FAILED (failures=8)
```

The remaining failures were H9 adapter reconstruction defects, not H6/H7/H8 retrieval gaps:

- the H9 adapter did not copy `normalized_order` from retrieved capability evidence into reconstructed H5 provider records;
- the H9 adapter sorted provider certifications by code, losing the repaired provider-certification publication order.

H9 was minimally repaired to preserve these retrieved values without changing H5 scoring/matching policy or weakening comparison.

Codex reran:

```powershell
..\..\.venv\Scripts\python.exe manage.py test tests.test_service_discovery_matching_alignment -v 2
```

Final Codex local H9 result:

```text
Ran 16 tests in 2.930s

OK
```

The previously identified local H9 fidelity blockers are resolved under the repaired H6-H8 evidence pipeline, subject to repository-owner focused local and remote acceptance verification.

### 3. Files modified in Step 4

H9 production code required a minimal adapter repair in:

- `backend/apps/search/service_discovery_matching_alignment.py`

The repair preserved `normalized_order` and stopped re-sorting provider certifications. H5 remains the sole matching/scoring policy implementation.

H9 tests were updated only to add explicit repaired-fidelity assertions in:

- `backend/tests/test_service_discovery_matching_alignment.py`
- `backend/tests/test_service_discovery_fuseki_matching_alignment.py`

The strict comparison helper still ignores only:

```text
status.search_engine
status.message
```

It continues to compare normalized order, explicit `None` values, material-grade order, process order, certification order, scores, match statuses, evidence and explanations.

H5, H6, H7 and H8 implementation/data files were not modified in Step 4.

### 4. Endpoint-readiness status pending repository-owner tests

Endpoint-migration readiness remains pending repository-owner Step 4 verification. No active API endpoint modification has been performed.

If repository-owner Gate A and Gate B pass, the strict matching-alignment prerequisite will be satisfied for focused harmonized scope. H9 still does not activate the API endpoint; a separate explicitly approved endpoint-activation phase remains required.

### 5. Repository-owner Step 4 verification gates

Gate A - focused H1-H9 local/unit verification:

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract tests.test_service_discovery_provider_loader tests.test_service_discovery_local_matcher tests.test_service_discovery_local_search_response tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_generate_service_discovery_rdf_command tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service tests.test_service_discovery_fuseki_service tests.test_service_discovery_matching_alignment -v 2
```

Gate B - opt-in remote H9 Fuseki matching-alignment verification:

```powershell
$env:SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="http://localhost:3030/mdc-service-discovery/query"
$env:RUN_SERVICE_DISCOVERY_FUSEKI_TESTS="1"
python manage.py test tests.test_service_discovery_fuseki_matching_alignment -v 2
```

### 6. Step 4 checklist

- [x] H9 local strict-equivalence tests pass after H6-H8 fidelity repair.
- [x] Repository owner ran focused H1-H9 local/unit verification.
- [x] Repository owner ran opt-in remote H9 Fuseki matching-alignment verification.
- [x] Strict direct-YAML/local-RDF/remote-Fuseki H5-policy alignment is accepted.
- [x] Endpoint-migration readiness recommendation finalised.

### Repository-owner remote Gate B failure after Codex local H9 pass

Repository-owner remote H9 Fuseki matching-alignment command:

```powershell
$env:SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="http://localhost:3030/mdc-service-discovery/query"
$env:RUN_SERVICE_DISCOVERY_FUSEKI_TESTS="1"
python manage.py test tests.test_service_discovery_fuseki_matching_alignment -v 2
```

Result:

```text
Ran 5 tests in 1.398s

FAILED (failures=5)
```

Failing tests:

- `test_crown_gear_not_asserted_and_candidate_evidence_are_equivalent`
- `test_material_process_and_certification_matching_are_equivalent`
- `test_remote_matching_excludes_legacy_and_fabricated_deferred_evidence`
- `test_splined_shaft_scope_direct_local_and_remote_matching_are_equivalent`
- `test_spur_gear_direct_local_and_remote_matching_are_equivalent`

Codex local H9 strict alignment had passed, but repository-owner remote H9 strict alignment failed. Therefore strict direct-YAML/local-RDF/remote-Fuseki alignment is not accepted and endpoint migration remains blocked until the remote failure is repaired and reverified.

Step 4A diagnosis compared direct H5 YAML-backed responses, H9 local RDFLib-backed responses and H9 remote Fuseki-backed responses for the failing request classes. It also directly compared raw H7 and H8 retrieval projections while ignoring only `status.retrieval_engine` and `status.message`.

Raw H7 local and H8 remote retrieval projections remained equivalent for:

- `precision_gears / gear / spur_gear`
- `precision_gears / gear / crown_gear`
- `precision_shafts / shaft / splined_shaft`
- the material/process/certification `spur_gear` request

The H9 local and remote normalized responses also remained equivalent for these requests. The first divergent paths were between direct YAML-backed H5 responses and RDF/Fuseki-backed H9 responses:

- `spur_gear`: `results[0].evidence.family_capabilities.module.max`, direct `1.5` as `float`, RDF-backed `Decimal('1.5')`
- `crown_gear`: `results[0].evidence.family_capabilities.module.max`, direct `1.5` as `float`, RDF-backed `Decimal('1.5')`
- `splined_shaft`: `results[0].evidence.part_type_capabilities.splined_shaft.spline_module.min`, direct `0.3` as `float`, RDF-backed `Decimal('0.3')`
- material/process/certification `spur_gear`: `results[0].evidence.family_capabilities.diametral_pitch.min`, direct `2.5` as `float`, RDF-backed `Decimal('2.5')`

The splined-shaft failures produced `full_match` score `1.0` for direct YAML-backed H5 matching and `partial_match` score `0.9` for RDF/Fuseki-backed H9 matching because H5 treated the RDF-derived `Decimal('0.3')` range boundary as incomplete comparison evidence. This was an H9 adapter defect: the request-scoped adapter did not normalize RDF numeric literal Python values into the same provider-record scalar shape consumed by H5 from YAML.

Step 4A minimally repaired `backend/apps/search/service_discovery_matching_alignment.py` so `Decimal` values in reconstructed provider records are converted to YAML-equivalent numeric scalars before invoking H5: integral decimals become `int`, non-integral decimals become `float`. H5 remains the sole matching/scoring policy implementation.

Step 4A added one focused H9 local adapter regression test in `backend/tests/test_service_discovery_matching_alignment.py` proving RDF decimal literals are normalized before H5 provider-record reconstruction. The strict comparison helper was not weakened; it still ignores only:

```text
status.search_engine
status.message
```

and continues to compare normalized order, explicit `None` values, material-grade order, process order, certification order, scores, match statuses and evidence.

Codex reran local H9 after the Step 4A repair:

```powershell
..\..\.venv\Scripts\python.exe manage.py test tests.test_service_discovery_matching_alignment -v 2
```

Result:

```text
Ran 17 tests in 3.480s

OK
```

Codex also reran the opt-in remote H9 Fuseki matching-alignment module against the configured dedicated endpoint available in this environment:

```powershell
$env:SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="http://localhost:3030/mdc-service-discovery/query"
$env:RUN_SERVICE_DISCOVERY_FUSEKI_TESTS="1"
..\..\.venv\Scripts\python.exe manage.py test tests.test_service_discovery_fuseki_matching_alignment -v 2
```

Result:

```text
Ran 5 tests in 1.368s

OK
```

Files modified in Step 4A:

- `backend/apps/search/service_discovery_matching_alignment.py`
- `backend/tests/test_service_discovery_matching_alignment.py`
- `docs/12_h9_matching_alignment_and_endpoint_readiness_report.md`

H5, H6, H7 and H8 implementation/data files were not modified. YAML, generated Turtle, Fuseki dataset content, API, settings, Docker and persistence files were not modified.

Repository-owner rerun remains required for formal acceptance:

```powershell
$env:SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="http://localhost:3030/mdc-service-discovery/query"
$env:RUN_SERVICE_DISCOVERY_FUSEKI_TESTS="1"
python manage.py test tests.test_service_discovery_fuseki_matching_alignment -v 2
```

Endpoint-migration readiness remains blocked until the repository owner reruns the remote Gate B after this Step 4A repair and then completes the focused H1-H9 local/unit verification gate for final closure.

## Final repository-owner H9 verification and acceptance

The repository owner completed the final H9 verification gates successfully.

### Gate A — Focused H1–H9 local/unit verification

The repository owner confirmed that the focused H1–H9 local/unit verification passed with 212 tests passing.

Exact elapsed time was not supplied and is therefore not recorded.

### Gate B — Opt-in remote Fuseki H9 matching-alignment verification

The repository owner ran the opt-in remote matching-alignment tests against the dedicated harmonized Fuseki dataset:

- Dataset: `mdc-service-discovery`
- Harmonized Turtle source: `data/generated/service_discovery/mdc_service_discovery_catalog.ttl`
- Legacy Turtle excluded: `data/generated/mdc_catalog.ttl`

Result:

```text
Ran 5 tests in 1.309s

OK
```

The remote verification covered:

- `spur_gear` direct/local/remote matching alignment;
- `crown_gear` not-asserted and candidate-evidence alignment;
- `splined_shaft` scoped capability alignment;
- materials, processes and provider certifications;
- exclusion of legacy offerings and fabricated deferred evidence.

Following the completed H6–H9 evidence-fidelity repair, strict matching alignment is accepted for focused harmonized scope:

```text
direct harmonized YAML-backed H5 outcome
=
local RDFLib-retrieved evidence passed through H5 policy
=
dedicated Fuseki-retrieved evidence passed through H5 policy
```

excluding only intentionally backend-identifying status metadata.

H9 is accepted for focused scope.

This acceptance does not activate the live API endpoint. Endpoint activation remains a separate explicitly approved phase requiring a backend-selection decision, fallback policy, deployment configuration, persistence treatment, monitoring and data-refresh procedure.

No claim is made that the full legacy project test suite passes at this checkpoint.
