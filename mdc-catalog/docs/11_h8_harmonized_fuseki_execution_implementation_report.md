# MaaSAI MDC — H8 Harmonized Fuseki Execution Implementation Report

## 1. Status and scope

Phase: H8.

Purpose: optional remote Fuseki-backed SPARQL execution over the dedicated harmonized RDF dataset.

H8 reuses H7 controlled SPARQL semantics. H8 performs retrieval only, not matching or scoring. H5 remains the matching policy reference. The active API endpoint remains unchanged.

Fuseki dataset loading is performed manually by the repository owner, not by H8 code.

## 2. Verified prerequisite tests

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

The repository owner confirmed H6 harmonized Turtle generation. No claim is made that the full legacy project test suite passes.

## 3. H7 closure update

`docs/10_h7_harmonized_sparql_retrieval_implementation_report.md` was updated only to close H7 with the final passing verification result.

## 4. Dedicated Fuseki dataset decision

```text
Dataset name: mdc-service-discovery
Dataset purpose: harmonized RDF only
Expected loaded Turtle:
data/generated/service_discovery/mdc_service_discovery_catalog.ttl
Legacy Turtle explicitly excluded:
data/generated/mdc_catalog.ttl
```

Optional endpoint setting:

```text
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT
```

Recommended endpoint:

```text
http://localhost:3030/mdc-service-discovery/query
```

Opt-in integration-test flag:

```text
RUN_SERVICE_DISCOVERY_FUSEKI_TESTS=1
```

An empty endpoint setting means remote Fuseki retrieval is not configured.

## 5. New H8 architecture

```text
CanonicalServiceDiscoverySearchRequest selection
-> H7 controlled SPARQL templates
-> HTTP query to dedicated harmonized Fuseki dataset
-> shared H7/H8 internal retrieval projection semantics
```

No API activation, matching, scoring or Fuseki mutation occurs.

## 6. Remote retrieval contract

`service_discovery_fuseki_service.py` resolves the endpoint from an explicit function argument first, then from `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT`.

Remote execution sends read-only SPARQL query requests and requests SPARQL results JSON. HTTP errors, connection failures, timeouts, invalid JSON and malformed SPARQL result bindings raise `ServiceDiscoveryFusekiRetrievalError`.

Empty valid candidate results return a successful retrieval projection with an empty `candidates` list and do not issue the evidence query.

Remote status metadata:

```text
retrieval_executed: true
retrieval_engine: remote_harmonized_sparql_fuseki
matching_executed: false
```

H8 does not return scores, selection scores, optional scores, match statuses, matched/unmatched/unknown attributes, or external result-count output.

## 7. Evidence-scope preservation

The shared H7/H8 projection preserves:

- confirmed, candidate and not-asserted subtype distinctions;
- absence as `not_asserted`, never `unsupported`;
- provider-scoped certifications;
- family, part-type and generic capability scope;
- material grades as evidence literals only;
- process evidence from harmonized RDF only.

Tasowheel confirmed gear and shaft subtypes remain confirmed. Tasowheel `crown_gear`, `stepped_shaft`, and `worm_shaft` remain not asserted where the dedicated harmonized dataset contains no support node. Precipart `crown_gear` remains `candidate_requiring_confirmation` with public-source/non-provider-confirmed provenance where present.

Deferred shaft DP and shaft searchable DIN4 quality remain absent. General tolerance is not inferred from DIN4.

## 8. Local-versus-remote equivalence

The opt-in integration tests compare H7 RDFLib local retrieval with H8 remote Fuseki retrieval while ignoring only backend-specific `status.retrieval_engine` and `status.message` values.

Candidate order, requested part-type support, evidence grouping, provenance and deduplication must otherwise match. The dedicated dataset requirement prevents legacy/harmonized graph mixing.

## 9. Files created and modified

Created H8 files:

- `backend/apps/search/service_discovery_fuseki_service.py`
- `backend/tests/test_service_discovery_fuseki_service.py`
- `backend/tests/test_service_discovery_fuseki_integration.py`
- `docs/11_h8_harmonized_fuseki_execution_implementation_report.md`

Modified existing files:

- `backend/config/settings.py`
- `backend/apps/search/service_discovery_sparql_service.py`
- `docs/10_h7_harmonized_sparql_retrieval_implementation_report.md`

`backend/config/settings.py` was modified only to add the dedicated opt-in harmonized Fuseki query endpoint setting.

`backend/apps/search/service_discovery_sparql_service.py` was minimally refactored to expose pure shared candidate/evidence projection helpers for H7 and H8. H7 query templates were not modified.

No YAML, RDF generator, generated Turtle, ontology, API, H5 matcher, legacy Fuseki, Docker, requirements or persistence file was modified.

## 10. Tests created

`backend/tests/test_service_discovery_fuseki_service.py` contains mocked unit tests for:

- endpoint configuration and explicit override;
- read-only SPARQL HTTP request shape;
- SPARQL JSON response handling;
- timeout, connection, HTTP, JSON and malformed-binding errors;
- H7 query-builder reuse;
- empty candidate handling;
- remote retrieval-only status;
- confirmed, candidate and not-asserted support reconstruction;
- evidence reconstruction and deterministic deduplication.

`backend/tests/test_service_discovery_fuseki_integration.py` contains opt-in tests for:

- dedicated dataset sanity and legacy-offering exclusion;
- H7 local versus H8 remote projection equivalence;
- Tasowheel confirmed, not-asserted and evidence retrieval;
- Precipart candidate preservation where present;
- material/process/certification evidence retrieval;
- deferred shaft DP/quality and fabricated-field absence.

## 11. Runtime verification responsibility

The repository owner will first run focused amended H1-H8 unit tests in the activated Django-enabled `.venv`. Remote Fuseki integration tests are opt-in and will be run only after the owner creates and loads the dedicated harmonized Fuseki dataset.

## 12. Focused H1-H8 unit verification command

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract tests.test_service_discovery_provider_loader tests.test_service_discovery_local_matcher tests.test_service_discovery_local_search_response tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_generate_service_discovery_rdf_command tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service tests.test_service_discovery_fuseki_service -v 2
```

Remote integration tests are not included in this first command because they require repository-owner Fuseki dataset preparation.

## 13. Repository-owner Fuseki preparation steps

1. Start local Fuseki using the already chosen repository-owner installation/runtime method.
2. Create a new dataset named: `mdc-service-discovery`.
3. Load only: `data/generated/service_discovery/mdc_service_discovery_catalog.ttl`.
4. Do not load: `data/generated/mdc_catalog.ttl`.
5. Set the harmonized Fuseki query endpoint environment variable.
6. Enable opt-in integration tests.
7. Run the remote H8 integration tests.

Example PowerShell environment setup:

```powershell
$env:SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="http://localhost:3030/mdc-service-discovery/query"
$env:RUN_SERVICE_DISCOVERY_FUSEKI_TESTS="1"
```

## 14. Opt-in Fuseki integration verification command

```powershell
python manage.py test tests.test_service_discovery_fuseki_integration -v 2
```

## 15. Required H9 considerations

1. H9 must compare H5 local-matcher outcomes with harmonized RDF/SPARQL-backed candidate/evidence retrieval and define how retrieved evidence is passed into the accepted matching/scoring policy.

2. H9 must not activate the live API endpoint until local matcher and harmonized RDF/Fuseki-backed outputs are demonstrably aligned.

3. API activation, if approved later, must preserve provider_name/offering_name response naming, request_id/consumer_id, evidence explanations and material grades as evidence only.

4. The active endpoint must never query a Fuseki dataset containing mixed legacy and harmonized RDF.

5. Shaft DP and shaft-quality fields remain deferred unless a separately approved schema amendment is introduced.

## 16. Issues before H9

The dedicated Fuseki endpoint is not expected to be configured by default.

Remote integration verification was completed by the repository owner after creation/loading of the dedicated harmonized Fuseki dataset.

A shared H7/H8 projection refactor was necessary to avoid duplicating candidate/evidence reconstruction logic. H7 public retrieval behaviour is intended to remain unchanged.

No HTTP or Fuseki query compatibility issue was reported from repository-owner verification.

No out-of-scope modification was made.

## Repository-owner H8 verification and acceptance

The repository owner confirmed successful completion of the required H8 verification stages:

1. Focused H1-H8 unit verification, including regression coverage for the shared H7/H8 retrieval projection behaviour.
2. Opt-in remote Fuseki integration/equivalence verification against the dedicated harmonized Fuseki dataset.

The dedicated harmonized dataset used for H8 verification was:

- Dataset name: `mdc-service-discovery`
- Harmonized Turtle loaded: `data/generated/service_discovery/mdc_service_discovery_catalog.ttl`
- Legacy Turtle explicitly excluded: `data/generated/mdc_catalog.ttl`

The repository owner confirmed that all required tests passed. Exact test counts, elapsed times and terminal output were not supplied and are therefore not recorded here.

The successful H8 verification establishes that the optional remote Fuseki-backed retrieval layer can execute the accepted H7 harmonized SPARQL retrieval semantics against the dedicated harmonized RDF dataset while preserving local-versus-remote candidate/evidence equivalence.

H8 remains retrieval-only:

- No active API endpoint was changed or activated.
- No final matching or scoring was implemented through Fuseki.
- H5 remains the accepted matching/scoring policy reference.
- No legacy/harmonized RDF mixing is permitted.

No claim is made that the full legacy project test suite passes at this checkpoint.

Following repository-owner verification, H8 is accepted for focused scope and the project is ready for H9 review.

## 17. Completion checklist

- [x] H7 focused verification closure recorded.
- [x] Harmonized Fuseki service exists.
- [x] Dedicated harmonized Fuseki endpoint setting exists or is already available.
- [x] H8 reuses H7 controlled SPARQL templates.
- [x] H8 returns retrieval-only internal projections.
- [x] H8 preserves confirmed/candidate/not-asserted distinctions.
- [x] H8 never queries or mixes legacy RDF by design and integration checks.
- [x] H8 mocked unit tests exist.
- [x] H8 opt-in Fuseki integration/equivalence tests exist.
- [x] Active API endpoint remains unchanged.
- [x] No matcher/scoring/RDF/YAML/persistence activation occurred.
- [x] Repository owner ran focused H1-H8 unit verification.
- [x] Repository owner loaded dedicated harmonized Fuseki dataset.
- [x] Repository owner ran H8 remote integration verification.
- [x] Ready for H9 review.
