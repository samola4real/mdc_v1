# MaaSAI MDC — H8 Fuseki Retrieval Fidelity Amendment Report

## 1. Amendment purpose and status

This is Step 3 of the controlled H6-H9 fidelity repair.

Step 1 amended H6 RDF representation. Step 2 amended H7 local RDFLib retrieval reconstruction. Step 3 verifies/amends H8 remote Fuseki retrieval fidelity.

H9 strict matching alignment remains pending Step 4.

Endpoint migration remains blocked.

## 2. Accepted prior-step prerequisites

The repository owner confirmed that focused H1-H6 verification passed after Step 1.

The repository owner confirmed that focused H1-H7 verification passed after Step 2.

Exact repository-owner test counts and elapsed times for these confirmations were not supplied and are therefore not recorded.

H8 is expected to preserve these fidelity metadata terms:

```text
mdc:normalizedOrder
mdc:explicitNullField
mdc:sequenceIndex
mdc:hasAvailableGradeEvidence
mdc:AvailableGradeEvidence
mdc:availableGrade
```

## 3. H8 production-code impact assessment

`service_discovery_fuseki_service.py` did not require modification.

Inspection confirmed H8 already:

- reuses the amended H7 evidence query builder;
- converts all SPARQL JSON variables into RDFLib values without a variable whitelist;
- passes remote rows into the amended shared H7 projection helpers.

Therefore H8 inherits the repaired shared reconstruction logic when queried against regenerated RDF containing the Step 1 metadata.

H7 query semantics were not changed in Step 3.

## 4. Remote fidelity behaviour

H8 mocked tests now cover remote reconstruction of:

- `normalized_order`;
- explicit-null members as `None`;
- ordered available grades without duplication from flat and ordered grade evidence;
- ordered process evidence as evidence publication order only;
- ordered provider-certification evidence;
- confirmed, candidate and not-asserted part-type evidence states.

H8 remains retrieval-only. It does not score, match, call H5/H9, construct an external API response, or mutate Fuseki.

## 5. Files modified and created

Modified files:

- `backend/tests/test_service_discovery_fuseki_service.py`
- `backend/tests/test_service_discovery_fuseki_integration.py`
- `docs/14_h7_retrieval_fidelity_amendment_report.md`

Created file:

- `docs/15_h8_fuseki_retrieval_fidelity_amendment_report.md`

No H6 or H7 code/test was modified.

No H9 code/test was modified.

No YAML was modified.

No API, matching policy, settings, Docker or persistence file was modified.

Generated Turtle generation and Fuseki reload are repository-owner runtime steps only.

## 6. Tests added or updated

Updated:

```text
backend/tests/test_service_discovery_fuseki_service.py
backend/tests/test_service_discovery_fuseki_integration.py
```

Mocked unit coverage verifies:

- H8 uses the amended evidence query projection;
- remote rows reconstruct `normalized_order`;
- explicit nulls reconstruct as `None`;
- ordered grades are preserved without duplication;
- process and certification sequence ordering is applied;
- sequence metadata is not exposed as route/order/matching evidence;
- retrieval-only status and confirmed/candidate/not-asserted semantics remain unchanged.

Opt-in remote integration coverage verifies, after repository-owner RDF regeneration and Fuseki reload:

- local H7 and remote H8 projections match for key gear and shaft selections;
- Tasowheel `diametral_pitch.normalized_order = "ascending"`;
- Tasowheel explicit `surface_finish_ra_um.max = None`;
- available-grade, process and provider-certification ordering;
- absence of legacy bundled Tasowheel offerings and fabricated deferred fields;
- retrieval-only behaviour.

Codex local mocked H8 unit verification passed:

```text
Ran 11 tests in 0.008s

OK
```

Codex did not run remote Fuseki integration verification.

## 7. Repository-owner Step 3 verification sequence

### Gate A — Focused H1-H8 local/unit verification before RDF regeneration

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract tests.test_service_discovery_provider_loader tests.test_service_discovery_local_matcher tests.test_service_discovery_local_search_response tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_generate_service_discovery_rdf_command tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service tests.test_service_discovery_fuseki_service -v 2
```

Do not include H9 tests in Gate A.

### Gate B — Regenerate the harmonized Turtle after Gate A passes

```powershell
python manage.py generate_service_discovery_rdf
```

Expected regenerated file:

```text
data/generated/service_discovery/mdc_service_discovery_catalog.ttl
```

### Gate C — Replace/reload the dedicated harmonized Fuseki dataset

```text
1. Use only the dedicated dataset: mdc-service-discovery.
2. Clear/delete and recreate its existing data, or otherwise ensure the
   previously loaded pre-amendment harmonized graph is replaced.
3. Load only the newly regenerated file:
   data/generated/service_discovery/mdc_service_discovery_catalog.ttl
4. Do not load:
   data/generated/mdc_catalog.ttl
```

### Gate D — Run opt-in remote H8 retrieval-fidelity verification

Set or retain the already verified working endpoint:

```powershell
$env:SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="http://localhost:3030/mdc-service-discovery/query"
$env:RUN_SERVICE_DISCOVERY_FUSEKI_TESTS="1"
```

Use the exact endpoint previously verified if it differs.

Then run:

```powershell
python manage.py test tests.test_service_discovery_fuseki_integration -v 2
```

## 8. Deferred Step 4

```text
Step 4: After H8 remote retrieval fidelity passes, rerun H9 strict matching
alignment through direct YAML, local RDFLib and remote Fuseki paths, then
produce the endpoint-migration readiness decision.
```

## Repository-owner Step 3 verification and acceptance

The repository owner completed the Step 3 gate sequence successfully.

### Gate A — Focused H1–H8 local/unit verification

The repository owner confirmed that the focused H1–H8 local/unit verification passed successfully.

Exact repository-owner test count and elapsed time were not supplied and are therefore not recorded.

### Gate B — Harmonized Turtle regeneration

The repository owner confirmed regeneration of:

- `data/generated/service_discovery/mdc_service_discovery_catalog.ttl`

### Gate C — Dedicated Fuseki dataset replacement/reload

The repository owner confirmed that the dedicated harmonized Fuseki dataset was replaced/reloaded using only the regenerated harmonized Turtle:

- Dataset: `mdc-service-discovery`
- Loaded: `data/generated/service_discovery/mdc_service_discovery_catalog.ttl`
- Legacy Turtle excluded: `data/generated/mdc_catalog.ttl`

### Gate D — Opt-in remote H8 retrieval-fidelity verification

Command:

```powershell
$env:SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="http://localhost:3030/mdc-service-discovery/query"
$env:RUN_SERVICE_DISCOVERY_FUSEKI_TESTS="1"
python manage.py test tests.test_service_discovery_fuseki_integration -v 2
```

Result:

```text
Ran 4 tests in 1.409s

OK
```

The passing remote verification confirms that H8 Fuseki retrieval now preserves the repaired harmonized evidence fidelity required for later H9 strict alignment, including local-versus-remote equivalence for key selections, part-type status preservation, Tasowheel evidence fidelity and deferred-field safeguards.

Step 3 is accepted for focused scope.

H9 strict matching alignment remains pending Step 4. Endpoint migration remains blocked until Step 4 verification is complete.

## 9. Completion checklist

- [x] Step 2 focused verification closure recorded.
- [x] H8 production-code impact assessed.
- [x] H8 mocked tests cover normalized_order fidelity.
- [x] H8 mocked tests cover explicit-null reconstruction.
- [x] H8 mocked tests cover ordered grades without duplication.
- [x] H8 mocked tests cover process/certification evidence order.
- [x] H8 preserves confirmed/candidate/not_asserted retrieval semantics.
- [x] H8 remains retrieval-only.
- [x] No H6/H7/H9/YAML/API/settings/Docker/persistence code changed.
- [x] Repository owner ran focused H1-H8 local/unit verification.
- [x] Repository owner regenerated harmonized Turtle.
- [x] Repository owner replaced/reloaded dedicated harmonized Fuseki dataset.
- [x] Repository owner ran opt-in H8 remote retrieval-fidelity verification.
- [x] Ready for Step 4 H9 strict alignment rerun.
