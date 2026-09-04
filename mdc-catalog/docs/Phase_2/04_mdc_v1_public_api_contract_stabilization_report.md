# MDC v1 Public API Contract Stabilization Report

Report date: 2026-09-03

## 1. M4 status

completed

## 2. Canonical public API

| Method | Canonical path | Compatibility path | Classification | Intended consumer |
|---|---|---|---|---|
| GET | `/api/v1/health` | `/api/health` | public_current | Marketplace, ops, smoke tests |
| GET | `/api/v1/catalog/filters` | `/api/catalog/filters` | public_current | Marketplace dynamic form/filter clients |
| POST | `/api/v1/service-discovery/search` | `/api/service-discovery/search` | public_current | Marketplace service-discovery search |

## 3. Compatibility/legacy API

| Method | Path | Classification | Why it remains |
|---|---|---|---|
| POST | `/api/catalog/search` | public_legacy_compatibility | Legacy seed-data search remains test-covered but is not the preferred Marketplace integration endpoint. |
| POST | `/api/provider-publication` | write_deferred | File-backed provider publication remains test-covered but is not deployment-safe public persistence. |
| GET | `/api/providers/<provider_id>` | public_legacy_compatibility | Legacy provider detail remains test-covered against isolated legacy seed data. |
| GET | `/api/offerings/<offering_id>` | public_legacy_compatibility | Legacy offering detail remains test-covered against isolated legacy seed data. |
| `/api/demo/*` | `/api/demo/*` | internal_or_demo | Demo-only routes remain outside the canonical public v1 contract. |

Legacy/write/detail endpoints were intentionally not added under `/api/v1/`.

## 4. Files changed

| Path | Change | Reason |
|---|---|---|
| `backend/config/urls.py` | Added `api/v1/` include before compatibility `api/` include. | Establish canonical versioned public API base path. |
| `backend/apps/api/urls_v1.py` | Added canonical v1 route table for health, filters, and service-discovery search. | Keep public current routes explicit and separate from legacy compatibility endpoints. |
| `backend/apps/ontology/service_discovery_registry.py` | Changed `search_contract_active` to `True` and updated note with canonical and compatibility search paths. | Align registry metadata with active shared service-discovery endpoint. |
| `backend/tests/test_api_v1.py` | Updated filter endpoint expectation for active service-discovery contract. | Keep existing foundation test aligned with current contract status. |
| `backend/tests/test_service_discovery_registry.py` | Updated registry metadata expectations. | Verify active contract flag and route note. |
| `backend/tests/test_public_api_contract.py` | Added public API contract tests. | Prove canonical v1 endpoints, compatibility alias, legacy isolation, and demo exclusion. |

## 5. Contract decisions

| Decision | Result |
|---|---|
| Canonical base path | `/api/v1/` |
| Canonical search endpoint | `POST /api/v1/service-discovery/search` |
| Compatibility approach | Existing `/api/health`, `/api/catalog/filters`, and `/api/service-discovery/search` remain callable. |
| Legacy search | `/api/catalog/search` remains callable only as legacy compatibility. |
| Provider publication | `/api/provider-publication` remains callable but classified `write_deferred`; production hardening belongs to M5/later persistence work. |
| Provider/offering detail | `/api/providers/<provider_id>` and `/api/offerings/<offering_id>` remain legacy compatibility endpoints. |
| Demo API | `/api/demo/*` remains internal/demo and outside canonical public v1. |

## 6. Search request contract

Authoritative canonical service-discovery request fields:

```text
request_id
consumer_id
service_category
part_family
part_type
requirements
match_policy
```

`requirements` contains:

```text
part_family_specifications
part_type_specifications
generic_requirements
```

`match_policy` contains:

```text
optional_match_mode
unknown_policy
minimum_score
```

The harmonized contract rejects unknown top-level fields, forbidden route/machine/price fields, invalid controlled values, invalid scoped requirement fields, duplicated requirement fields across groups, and `primary_match_mode`.

## 7. Search response contract

Authoritative response fields:

```text
request_id
consumer_id
query_interpretation
warnings
result_count
results
status
```

Each result contains:

```text
provider
offering
match
matched_attributes
unmatched_attributes
unknown_attributes
evidence
```

`status` contains:

```text
search_executed
search_engine
message
```

H1-H9 behavior remains unchanged: Fuseki is tried first, then RDFLib, then harmonized YAML fallback.

## 8. Tests

| Command | Tests run | Passed | Failed | Skipped | Result |
|---|---:|---:|---:|---:|---|
| `..\..\.venv\Scripts\python.exe manage.py check` | 0 | 0 | 0 | 0 | Pass: no system-check issues. |
| `..\..\.venv\Scripts\python.exe manage.py test tests.test_public_api_contract tests.test_api_v1 tests.test_service_discovery_registry -v 2` | 21 | 21 | 0 | 0 | Pass. |
| `..\..\.venv\Scripts\python.exe manage.py test -v 2` | 399 | 386 | 0 | 13 | Pass. |
| `..\..\.venv\Scripts\python.exe manage.py test tests.test_service_discovery_registry tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_provider_loader tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_local_matcher tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service tests.test_service_discovery_fuseki_service tests.test_service_discovery_matching_alignment tests.test_service_discovery_runtime_search tests.test_service_discovery_search_endpoint tests.test_service_discovery_local_search_response tests.test_service_discovery_fuseki_matching_alignment tests.test_service_discovery_search_response_contract -v 2` | 230 | 225 | 0 | 5 | Pass. |

Skipped tests are optional Fuseki/integration checks guarded by missing local/remote Fuseki environment.

## 9. Git commit

| Item | Result |
|---|---|
| Hash | `d75dc7b` |
| Message | `feat: stabilize MDC v1 public API contract` |
| Branch | `main` |

## 10. M5 readiness

READY_FOR_M5
