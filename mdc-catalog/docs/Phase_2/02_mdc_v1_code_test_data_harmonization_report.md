# MDC v1 Code, Data, and Test Harmonization Report

Report date: 2026-09-03

## 1. Executive result

M1: completed.

M2: completed.

The current working tree implementation is coherent after separating source-style provider staging data from the legacy runtime seed directory. The full Django test suite and focused harmonized service-discovery suite are green, with only optional Fuseki/integration tests skipped by environment guards.

## 2. Source-of-truth decisions

| Area | Current source of truth | Legacy/superseded | Decision |
|---|---|---|---|
| Shared current search API | `POST /api/service-discovery/search` via `backend/apps/api/views/post_views.py` | Older `/api/catalog/search` contract | Keep service-discovery path as current MDC v1 integration candidate. |
| H1-H9 service discovery | `backend/apps/ontology/service_discovery_registry.py`, `backend/apps/api/service_discovery_*`, `backend/apps/search/service_discovery_*`, `backend/apps/ontology/service_discovery_rdf_*` | Legacy catalogue search/RDF components | Preserve current implementation; no production changes required. |
| Harmonized provider runtime data | `data/curated/service_discovery/providers/*.yaml` | Legacy seed files under `data/curated/providers/` | Keep as active H1-H9 YAML fallback and RDF source. |
| Legacy catalogue runtime data | `data/curated/providers/*.yaml` with `metadata`, `providers`, `materials`, `material_grades`, and `offerings` | Source-style provider records in same directory | Keep only legacy seed-schema YAML in this directory. |
| Source/staging provider data | `data/staging/provider_sources/*.yaml` | Previously mixed into `data/curated/providers/` | Isolate source/public-web style records from runtime loaders. |
| Generated harmonized RDF | `data/generated/service_discovery/mdc_service_discovery_catalog.ttl` | Legacy `data/generated/mdc_catalog.ttl` for old RDF flow | Keep both for their respective test-covered flows. |
| Demo API | `backend/apps/demo/` mounted under `/api/demo/` | Not public production scope | Retain as guarded demo functionality. |
| Provider publication | `/api/provider-publication` legacy seed writer | Not Vercel-safe production persistence | Retain for current tests; defer production persistence hardening. |

## 3. Files changed/moved

| Path | Change | Reason |
|---|---|---|
| `data/curated/providers/precipart.yaml` | Moved out of legacy runtime seed directory. | File used source-style top-level keys (`provider_id`, `provider_name`, `offerings`) and was invalid for the legacy seed loader. |
| `data/staging/provider_sources/precipart.yaml` | Added by move, preserving original contents. | Keeps source/public-web Precipart data available without contaminating runtime seed loading. |

## 4. Test harmonization

| Category | Result |
|---|---|
| Stale tests updated | None required. The failures represented mixed runtime/staging data, not stale assertions. |
| Stale tests removed/retired | None. |
| Fixtures/data updated | Provider data boundary changed by moving source-style Precipart YAML to staging. |
| Genuine production defects fixed | None. No current-code defect was found after data separation. |
| Important tests deliberately retained | Legacy catalogue/provider-detail/RDF tests retained because the legacy seed path remains intentionally supported and green once isolated. H1-H9 service-discovery tests retained and green. |

## 5. Provider-data architecture after harmonization

```text
data/
  curated/
    providers/
      demo_heat_treatment_provider.yaml     # legacy seed schema
      demo_machining_provider.yaml          # legacy seed schema
      tasowheel.yaml                        # legacy seed schema
    service_discovery/
      providers/
        demo_machining_provider.yaml        # harmonized H1-H9 provider schema
        precipart.yaml                      # harmonized H1-H9 provider schema
        tasowheel.yaml                      # harmonized H1-H9 provider schema
    tasowheel_offerings.yaml                # backward-compatible legacy fallback
  staging/
    provider_sources/
      precipart.yaml                        # source/public-web style staging record
  generated/
    mdc_catalog.ttl                         # legacy catalogue RDF
    service_discovery/
      mdc_service_discovery_catalog.ttl     # harmonized service-discovery RDF
```

Runtime rule: `data/curated/providers/` is for legacy seed-schema YAML only. `data/curated/service_discovery/providers/` is for harmonized service-discovery runtime YAML. Source/provider-upload/public-web style input belongs outside runtime loader directories until explicitly normalized.

## 6. API/component status after harmonization

| API/component | Status | Evidence/decision |
|---|---|---|
| `/api/service-discovery/search` | current | Implemented, tested, and backed by Fuseki -> RDFLib -> YAML fallback behavior. |
| `/api/catalog/search` | legacy retained | Still implemented and full-suite green after legacy provider seed isolation. Not the preferred current integration endpoint. |
| `/api/provider-publication` | legacy retained | Test-covered file-backed seed writer. Production persistence/deployment hardening deferred. |
| Provider detail `/api/providers/<provider_id>` | legacy retained | Test-covered against isolated legacy seed data. |
| Offering detail `/api/offerings/<offering_id>` | legacy retained | Test-covered against isolated legacy seed data. |
| H7 RDFLib retrieval | current | Focused service-discovery tests pass. |
| H8 Fuseki retrieval | current optional | Unit-tested; real Fuseki integration skipped when no Fuseki endpoint is available. |
| H9 matching alignment | current | Focused local alignment tests pass; remote Fuseki alignment tests skipped by explicit env guard. |

## 7. Verification results

| Command | Tests run | Passed | Failed | Skipped | Result |
|---|---:|---:|---:|---:|---|
| `..\..\.venv\Scripts\python.exe manage.py check` | 0 | 0 | 0 | 0 | Pass: no system-check issues. |
| `..\..\.venv\Scripts\python.exe manage.py test -v 2` | 390 | 377 | 0 | 13 | Pass. |
| `..\..\.venv\Scripts\python.exe manage.py test tests.test_service_discovery_registry tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_provider_loader tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_local_matcher tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service tests.test_service_discovery_fuseki_service tests.test_service_discovery_matching_alignment tests.test_service_discovery_runtime_search tests.test_service_discovery_search_endpoint tests.test_service_discovery_local_search_response tests.test_service_discovery_fuseki_matching_alignment tests.test_service_discovery_search_response_contract -v 2` | 230 | 225 | 0 | 5 | Pass. |

Skipped tests are optional Fuseki/integration checks guarded by missing local/remote Fuseki environment.

## 8. Remaining issues

- The repository remains dirty and many current backend/data/test files are untracked. This is intentionally deferred to M3.
- Existing deployment hardening, Vercel packaging, auth/rate limiting, production persistence, and API versioning remain deferred by Task 01 scope.
- `docs/` contains known drift and Git-tracking decisions are deferred to M3.

## 9. Readiness for M3

M1 and M2 are complete. The active code/data/test baseline is coherent and verified. The remaining work is clean-Git baseline preparation.

READY_FOR_M3
