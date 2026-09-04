**TOC:**


-----
# MDC v1 Resume And Vercel Deployment Audit

Audit date: 2026-09-03  
Repository root audited: `C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog`  
Audit mode: repository read-only, except for creation of this report.

## 1. Executive Summary

MDC v1 is no longer just a Django foundation. The repository contains a working Django/DRF backend with shared API routes, demo routes, controlled vocabularies, legacy provider seed-data loading, a newer harmonized service-discovery registry, publication serializers, provider YAML, RDF generation, RDFLib retrieval, optional remote Fuseki retrieval, H5 matching, and H9 alignment adapters.

Fresh verification in this audit:

| Command                                                   | Result                                 |
| --------------------------------------------------------- | -------------------------------------- |
| `..\..\.venv\Scripts\python.exe manage.py check`          | Pass: no issues                        |
| `..\..\.venv\Scripts\python.exe manage.py check --deploy` | Exit 0, but 21 deployment warnings     |
| `..\..\.venv\Scripts\python.exe manage.py test -v 2`      | Fail: 390 tests, 45 errors, 13 skipped |
| Focused service-discovery suite                           | Pass: 220 tests                        |

The practical current status is mixed:

|                Area                 | Status                                                                                                      |
| :---------------------------------: | ----------------------------------------------------------------------------------------------------------- |
|        Django app foundation        | Implemented and verified by `manage.py check`                                                               |
| Shared health and filter endpoints  | Implemented; covered by tests                                                                               |
|    Legacy `/api/catalog/search`     | Implemented but currently blocked by mixed legacy provider data                                             |
|      Provider/detail endpoints      | Implemented but currently blocked by mixed legacy provider data                                             |
| New `/api/service-discovery/search` | Implemented and verified in focused tests                                                                   |
|        Harmonized H1-H9 flow        | Implemented and focused-test verified                                                                       |
|     Public deployment readiness     | Not ready without production settings, packaging, auth/rate limiting, and external Fuseki/storage decisions |

Vercel feasibility verdict: **Suitable with moderate changes**.

>The Django API can run on Vercel Functions, but Fuseki should not run inside the same Vercel deployment. Use Vercel for the Django API and host Fuseki/RDF storage externally. Provider publication also needs redesign before public deployment because the current endpoint writes YAML files into the repository filesystem, which is not persistent on Vercel.

## 2. Current Architecture

Implemented app layout:

| Path                                                                 | Role                                                                                             |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `backend/config/settings.py`                                         | Single Django settings module; dev and pseudo-prod settings are mixed                            |
| `backend/config/settings_local.py`                                   | Imports `config.settings` and enables demo API                                                   |
| `backend/config/urls.py`                                             | Mounts admin, shared API, and demo API                                                           |
| `backend/apps/api/`                                                  | DRF views, route table, serializers, response shaping                                            |
| `backend/apps/demo/`                                                 | Temporary demo endpoints and provider-demo state APIs                                            |
| `backend/apps/ontology/`                                             | Static vocabularies, harmonized registry, RDF mappings/generators                                |
| `backend/apps/providers/`                                            | Legacy seed-data loaders, publication repository, harmonized provider loaders                    |
| `backend/apps/search/`                                               | Legacy and harmonized search normalizers, local matching, RDFLib/Fuseki retrieval, H9 alignment  |
| `backend/tests/`                                                     | Django test suite, including service-discovery, RDF, SPARQL, Fuseki, API, demo, and legacy tests |
| `data/curated/providers/`                                            | Legacy provider seed files plus at least one source-style provider file                          |
| `data/curated/service_discovery/providers/`                          | Harmonized provider records for service-discovery                                                |
| `data/generated/service_discovery/mdc_service_discovery_catalog.ttl` | Generated harmonized Turtle file used by local RDFLib fallback                                   |
| `requirements/`                                                      | Dependency files; no root `requirements.txt` exists                                              |

Current runtime flows:

```text
/api/health
  -> static DRF response

/api/catalog/filters
  -> apps.ontology.vocabularies.get_catalog_filters()
  -> static legacy vocabularies + harmonized service_discovery registry

/api/catalog/search
  -> SearchRequestSerializer
  -> normalize_search_request()
  -> legacy local seed matcher
  -> data/curated/providers/*.yaml via providers.loaders

/api/service-discovery/search
  -> ServiceDiscoverySearchRequestSerializer
  -> normalize_service_discovery_search_request()
  -> try remote Fuseki + H5
  -> fall back to local RDFLib + H5
  -> fall back to harmonized YAML + H5
```

## 3. Current Repository/Component Map

Top-level repository structure observed:

| Path                                                                 | Current state                                                                                                        |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `README.md`                                                          | Older Week 1 implementation guidance; does not represent current endpoint state                                      |
| `docs/`                                                              | Design docs, H1-H9 implementation reports, endpoint activation reports, this Phase 2 audit                           |
| `backend/`                                                           | Django project, apps, tests, SQLite db                                                                               |
| `data/curated/tasowheel_offerings.yaml`                              | Legacy single-file fallback seed data                                                                                |
| `data/curated/providers/`                                            | Legacy multi-provider seed directory; currently contains `precipart.yaml` that does not match required legacy schema |
| `data/curated/service_discovery/providers/`                          | Harmonized provider data used by the newer service-discovery path                                                    |
| `data/generated/mdc_catalog.ttl`                                     | Legacy generated Turtle                                                                                              |
| `data/generated/service_discovery/mdc_service_discovery_catalog.ttl` | Harmonized generated Turtle                                                                                          |
| `ontologies/*.ttl` and `ontologies/shacl/*.ttl`                      | Present but zero-byte placeholders                                                                                   |
| `scripts/*.py`                                                       | Present but zero-byte placeholders                                                                                   |
| `docker-compose.yml`                                                 | Present but zero-byte placeholder                                                                                    |
| `.env.example`                                                       | Present but zero-byte placeholder                                                                                    |
| `requirements/base.txt`                                              | Runtime dependencies                                                                                                 |
| `requirements/dev.txt`                                               | Dev/test dependencies                                                                                                |
| `requirements/locked.txt`                                            | Pinned dependency snapshot                                                                                           |
| `requirements/test.txt`                                              | Empty                                                                                                                |

Git status at audit time shows a dirty worktree with many modified/deleted/untracked files. Most of the backend apps, tests, provider folders, generated data, demo data, and `settings_local.py` are untracked from Git's perspective. Treat the current working tree, not the last commit, as the actual state of work.

Recent Git history:

```text
766bc33 installed
192eef2 dependencies
11e7eb5 Backend initial settings
73e6e55 testing
143bccf discard
c2aed93 first commit
```

## 4. What Has Been Completed

| Capability                                             | Evidence                                                                                                                                  | Verification status                                               |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Django project foundation                              | `backend/manage.py`, `backend/config/settings.py`, `backend/config/urls.py`                                                               | Implemented and verified by `manage.py check`                     |
| Project apps registered                                | `apps.api`, `apps.catalog`, `apps.ontology`, `apps.providers`, `apps.search`, `apps.demo` in `settings.py`                                | Implemented                                                       |
| Health endpoint                                        | `backend/apps/api/urls.py`, `backend/apps/api/views.py`                                                                                   | Implemented and test-covered                                      |
| Catalogue filters endpoint                             | `backend/apps/ontology/vocabularies.py`, `backend/apps/api/views.py`                                                                      | Implemented and test-covered                                      |
| Legacy provider/offering detail                        | `backend/apps/providers/services.py`, `backend/apps/api/response_utils.py`, `backend/apps/api/views.py`                                   | Implemented but current data causes failing tests                 |
| Legacy provider publication                            | `backend/apps/api/provider_publication_serializers.py`, `backend/apps/providers/normalizers.py`, `backend/apps/providers/repositories.py` | Implemented and tested, but not Vercel-safe                       |
| Legacy local catalogue search                          | `backend/apps/search/local_matcher.py` and matcher submodules                                                                             | Implemented but current data causes legacy test failures          |
| H1 registry                                            | `backend/apps/ontology/service_discovery_registry.py`                                                                                     | Focused service-discovery tests pass                              |
| H2 service-discovery publication serializer/normalizer | `service_discovery_publication_serializers.py`, `providers/service_discovery_publication.py`                                              | Focused tests pass                                                |
| H3 harmonized provider YAML migration                  | `data/curated/service_discovery/providers/*.yaml`                                                                                         | Focused tests pass                                                |
| H4 service-discovery search contract                   | `service_discovery_search_serializers.py`, `service_discovery_normalizer.py`                                                              | Focused tests pass                                                |
| H5 harmonized local matcher                            | `service_discovery_local_matcher.py`                                                                                                      | Focused tests pass                                                |
| H6 harmonized RDF generation                           | `service_discovery_rdf_generator.py`, generated Turtle                                                                                    | Focused tests pass                                                |
| H7 RDFLib SPARQL retrieval                             | `service_discovery_sparql_service.py`                                                                                                     | Focused tests pass                                                |
| H8 optional remote Fuseki retrieval                    | `service_discovery_fuseki_service.py`                                                                                                     | Unit tests pass; real Fuseki skipped/unverified in fresh full run |
| H9 alignment                                           | `service_discovery_matching_alignment.py`                                                                                                 | Focused tests pass                                                |
| Shared service-discovery endpoint                      | `POST /api/service-discovery/search`                                                                                                      | Focused tests pass                                                |
| Demo API foundation                                    | `backend/apps/demo/urls.py`, `views/get_views.py`, `views/post_views.py`                                                                  | Implemented and test-covered                                      |

## 5. Current API Inventory

Routes are implemented in `backend/config/urls.py`, `backend/apps/api/urls.py`, and `backend/apps/demo/urls.py`.

Important: implemented paths have no trailing slash.

Shared API mounted under `/api/`:

| Method | Implemented path                | View                                                                               | Current backend dependency                               |
| ------ | ------------------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------- |
| GET    | `/api/health`                   | `apps.api.views.health`                                                            | None                                                     |
| GET    | `/api/catalog/filters`          | `apps.api.views.catalog_filters`                                                   | Static Python vocabularies/registry                      |
| POST   | `/api/catalog/search`           | `apps.api.views.catalog_search`                                                    | Legacy `data/curated/providers/*.yaml`                   |
| POST   | `/api/service-discovery/search` | `apps.api.views.post_views.service_discovery_search` via `apps.api.views.__init__` | Remote Fuseki, local RDFLib, or harmonized YAML fallback |
| POST   | `/api/provider-publication`     | `apps.api.views.provider_publication`                                              | Writes YAML under `data/curated/providers/`              |
| GET    | `/api/providers/<provider_id>`  | `apps.api.views.provider_detail`                                                   | Legacy seed-data loader                                  |
| GET    | `/api/offerings/<offering_id>`  | `apps.api.views.offering_detail`                                                   | Legacy seed-data loader                                  |

Demo API mounted under `/api/demo/`:

| Method | Implemented path                                 | Purpose                                         |
| ------ | ------------------------------------------------ | ----------------------------------------------- |
| GET    | `/api/demo/health`                               | Demo API status                                 |
| GET    | `/api/demo/service-discovery/backend-status`     | Demo-selected backend status                    |
| GET    | `/api/demo/service-discovery/fuseki-smoke-test`  | Placeholder, returns not implemented            |
| POST   | `/api/demo/service-discovery/regenerate-rdf`     | Placeholder, returns 501                        |
| POST   | `/api/demo/service-discovery/reload-fuseki`      | Placeholder, returns 501                        |
| POST   | `/api/demo/provider-publication/preview`         | Validate/preview flexible demo provider payload |
| GET    | `/api/demo/provider-publication/state`           | Read demo provider state JSON                   |
| POST   | `/api/demo/provider-publication/simulate-update` | Write demo provider state JSON                  |

OpenAPI/schema: `drf_spectacular` is installed and configured, but no schema or Swagger route is mounted in `config/urls.py`. `check --deploy` also reports drf-spectacular cannot infer serializers for the function-based views.

## 6. Current Data/Ontology/RDF/Fuseki Flow

Legacy flow:

```text
data/curated/providers/*.yaml
  -> apps.providers.loaders.load_catalog_seed_data()
  -> apps.providers.validators.validate_seed_data()
  -> legacy local matcher and legacy RDF generator
  -> data/generated/mdc_catalog.ttl
```

Current issue: `data/curated/providers/precipart.yaml` is source/provider-publication-style data with top-level keys such as `provider_id`, `provider_name`, and `offerings`. It is not the legacy schema required by `validate_seed_data()`, which expects top-level `metadata`, `providers`, `materials`, `material_grades`, and `offerings`. This caused the full test-suite failures.

Harmonized service-discovery flow:

```text
data/curated/service_discovery/providers/*.yaml
  -> apps.providers.service_discovery_loaders.load_service_discovery_providers()
  -> apps.ontology.service_discovery_rdf_generator.generate_service_discovery_turtle()
  -> data/generated/service_discovery/mdc_service_discovery_catalog.ttl
  -> apps.search.service_discovery_sparql_service.load_service_discovery_rdf_graph()
  -> RDFLib SPARQL retrieval
  -> H9 request-scoped adapter
  -> H5 matcher/scorer
```

Optional remote Fuseki flow:

```text
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT
  -> apps.search.service_discovery_fuseki_service.execute_fuseki_sparql_query()
  -> H8 remote retrieval projection
  -> H9 request-scoped adapter
  -> H5 matcher/scorer
```

`SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` defaults to an empty string. When it is empty or unreachable, `/api/service-discovery/search` falls back to local RDFLib and then YAML matching.

The ontology source/profile files under `ontologies/` are zero bytes. The working RDF behavior is currently driven by Python mappings and generated Turtle, not by populated ontology source files or SHACL files.

## 7. Current Provider-Publication Flow

Legacy public provider publication:

```text
POST /api/provider-publication
  -> ProviderPublicationSerializer
  -> normalize_provider_publication()
  -> save_provider_seed_data()
  -> writes data/curated/providers/{provider_id}.yaml
```

Implemented behavior:

| Topic                      | Current behavior                                                                    |
| -------------------------- | ----------------------------------------------------------------------------------- |
| External provider field    | Uses `provider.display_name`                                                        |
| Offering IDs               | External payload must supply `offering_id`, and it must begin with `{provider_id}_` |
| Storage                    | File-backed seed repository                                                         |
| RDF/Fuseki update          | Response says RDF generation required but not done                                  |
| Route/machine/price fields | Rejected                                                                            |
| Vercel readiness           | Not production-safe because repository filesystem writes are not persistent         |

Harmonized provider publication code exists separately:

| Path                                                            | Role                                                                                                                               |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `backend/apps/api/service_discovery_publication_serializers.py` | Validates newer `provider_id`, `provider_name`, `service_category`, `part_family`, `supported_part_types`, and scoped capabilities |
| `backend/apps/providers/service_discovery_publication.py`       | Generates internal offering IDs like `{provider_id}_{service_category}`                                                            |

That harmonized publication path is not currently exposed as a shared API route.

## 8. Current Search/Matching Flow

Legacy catalogue search:

```text
POST /api/catalog/search
  -> older broad request schema
  -> local seed-data matcher
  -> returns provider/offering matches with explanations
```

This path is implemented but currently not reliable because it loads `data/curated/providers/*.yaml`, and the current folder contains mixed schema files.

Harmonized service-discovery search:

```text
POST /api/service-discovery/search
  -> required request_id, consumer_id, service_category, part_family, part_type
  -> requirements grouped into part_family_specifications, part_type_specifications, generic_requirements
  -> H5 matching/scoring
  -> result_count, results, matched/unmatched/unknown attributes, evidence
```

Backend order in `service_discovery_runtime_search.py`:

1. Remote Fuseki + H5 policy.
2. Local RDFLib + H5 policy.
3. Harmonized YAML + H5 matcher.

The current H5 matcher supports:

| Capability                         | Current status                                                      |
| ---------------------------------- | ------------------------------------------------------------------- |
| Service category/family filtering  | Implemented                                                         |
| Part-type support status           | Implemented with confirmed/candidate/not-asserted distinctions      |
| Gear family ranges                 | Implemented                                                         |
| Shaft family ranges                | Implemented                                                         |
| Bounding box comparison            | Implemented in matcher; provider data availability varies           |
| Materials/processes/certifications | Implemented                                                         |
| Batch size, delivery, weight       | Implemented                                                         |
| Gear quality and generic quality   | Implemented with lower-or-equal-is-better comparison where relevant |
| Unknown handling                   | Implemented; `reject_unknown` can filter                            |
| Minimum score                      | Implemented                                                         |
| Request persistence                | Missing                                                             |
| API authentication                 | Missing                                                             |

## 9. Testing Status

Fresh commands run from `backend/`:

```powershell
..\..\.venv\Scripts\python.exe manage.py check
```

Result:

```text
System check identified no issues (0 silenced).
```

```powershell
..\..\.venv\Scripts\python.exe manage.py check --deploy
```

Result: exit code 0, but 21 warnings, including:

| Warning area                            | Meaning                                                                 |
| --------------------------------------- | ----------------------------------------------------------------------- |
| `security.W018`                         | `DEBUG` is true under current settings                                  |
| `security.W009`                         | `SECRET_KEY` is an insecure generated development key                   |
| `security.W004`, `W008`, `W012`, `W016` | HSTS/SSL redirect/secure cookie production settings are missing         |
| `drf_spectacular.W002`                  | Function-based API views lack serializer metadata for schema generation |

```powershell
..\..\.venv\Scripts\python.exe manage.py test -v 2
```

Result:

```text
Ran 390 tests in 15.209s
FAILED (errors=45, skipped=13)
```

Primary failure class:

```text
apps.providers.exceptions.SeedDataError:
Seed data is missing required top-level keys:
['material_grades', 'materials', 'metadata', 'providers']
```

The failing tests are concentrated around legacy provider seed loading, provider detail APIs, legacy RDF generation, and legacy SPARQL query tests that depend on the legacy seed loader. Optional Fuseki integration tests were skipped because Fuseki was not running.

Focused harmonized service-discovery command:

```powershell
..\..\.venv\Scripts\python.exe manage.py test tests.test_service_discovery_registry tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_provider_loader tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract tests.test_service_discovery_local_matcher tests.test_service_discovery_rdf_generator tests.test_service_discovery_rdf_mappings tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service tests.test_service_discovery_matching_alignment tests.test_service_discovery_fuseki_service tests.test_service_discovery_runtime_search tests.test_service_discovery_search_endpoint -v 2
```

Result:

```text
Ran 220 tests in 8.318s
OK
```

Interpretation:

| Claim                                                        | Status                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------------- |
| The Django app imports and passes system checks              | Implemented and verified                                            |
| The harmonized service-discovery path works in focused tests | Implemented and verified                                            |
| The full current repository test suite passes                | False                                                               |
| Live remote Fuseki integration passes in this audit          | Not verified; optional tests skipped because Fuseki was not running |

## 10. Important Design Decisions Already Established

| Decision                                                                                              | Evidence                                                                                                       |
| ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Structured JSON first; NLP/LLM extraction out of scope for v1                                         | `docs/architecture.md`, `docs/api-contract-v1.md`                                                              |
| ProviderOffering is the search result entity                                                          | `docs/architecture.md`, matcher result builders                                                                |
| Route steps, machine sequence, pricing, live availability are excluded                                | `providers/validators.py`, service-discovery serializers, docs                                                 |
| Unknown evidence is explicit, not automatically failure                                               | matchers and service-discovery tests                                                                           |
| Tasowheel should remain data, not hardcoded logic                                                     | docs and provider-neutral matchers                                                                             |
| H1-H9 introduced a harmonized service category/family/type model                                      | `service_discovery_registry.py`                                                                                |
| Consumer search in the harmonized contract is single service category + single part type              | `service_discovery_search_serializers.py`                                                                      |
| Consumers search by material families, not material grades, in the newer contract                     | `service_discovery_search_serializers.py`, `docs/21_service_discovery_search_contract_backend_audit_report.md` |
| Material grades remain evidence in provider data/responses                                            | harmonized provider YAML and RDF generator                                                                     |
| Fuseki is optional at runtime for `/api/service-discovery/search` because RDFLib/YAML fallbacks exist | `service_discovery_runtime_search.py`                                                                          |

## 11. Documentation/Code Drift Or Inconsistencies

### API base path

```text
Documented:
docs/api-contract-v1.md and docs/architecture.md use /api/v1/...

Implemented:
backend/config/urls.py mounts apps.api.urls at /api/.
Implemented paths are /api/health, /api/catalog/filters, /api/catalog/search,
/api/service-discovery/search, /api/provider-publication, /api/providers/<id>,
and /api/offerings/<id>.

Recommended source of truth:
backend/config/urls.py and backend/apps/api/urls.py.

Action required:
Choose whether public MDC v1 should stay at /api/... or add explicit /api/v1/ aliases.
Update docs and Marketplace configuration accordingly.
```

### Search backend

```text
Documented:
Older architecture says /api/v1/catalog/search validates, builds SPARQL, calls Fuseki,
then normalizes/scares/explains results.

Implemented:
/api/catalog/search uses legacy local seed-data matching.
/api/service-discovery/search tries Fuseki, then local RDFLib, then YAML, all through H5 scoring.

Recommended source of truth:
For new MaaSAI Marketplace integration, treat /api/service-discovery/search as the current
integration candidate.

Action required:
Update API docs and Marketplace frontend contract around the harmonized endpoint, or deliberately
restore /api/catalog/search as the public v1 endpoint after fixing legacy data.
```

### Provider publication

```text
Documented:
Harmonized docs say Marketplace/provider supplies provider_id and provider_name; MDC generates
offering_id.

Implemented:
Legacy /api/provider-publication requires provider.display_name and externally supplied offering_id.
Harmonized serializer/normalizer exists but is not exposed as an API route.

Recommended source of truth:
Existing public route source is backend/apps/api/views.py.
Harmonized target contract source is backend/apps/api/service_discovery_publication_serializers.py.

Action required:
Expose a harmonized provider-publication endpoint or explicitly keep legacy publication out of
public deployment.
```

### Registry active flag

```text
Documented:
H1 registry originally marked harmonized search as inactive.

Implemented:
/api/service-discovery/search is now registered and tested, but get_service_discovery_registry()
still returns search_contract_active: False.

Recommended source of truth:
Route table plus tests prove the endpoint exists; registry metadata is stale.

Action required:
Update registry metadata or split "frontend form registry active" from "search endpoint active".
```

### Ontology files

```text
Documented:
Architecture and ontology profile describe populated Turtle/SHACL source files.

Implemented:
ontologies/mdc_core.ttl, mdc_mappings.ttl, mdc_tasowheel_profile.ttl, and shacl/mdc_v1_shapes.ttl
are zero bytes. Generated Turtle files exist under data/generated/.

Recommended source of truth:
Python RDF mapping/generator modules and generated Turtle.

Action required:
Populate ontology/SHACL source files or document that Python mappings are the current ontology
source of truth.
```

### Deployment and ops files

```text
Documented:
Architecture describes Docker/Fuseki load workflow.

Implemented:
docker-compose.yml and scripts/build_catalog.py, scripts/load_fuseki.py, scripts/validate_graph.py
are zero-byte placeholders.

Recommended source of truth:
Python management command generate_service_discovery_rdf and current settings.

Action required:
Either implement Docker/Fuseki ops scripts or remove stale operational references from docs.
```

## 12. Known Gaps And Technical Debt

| Gap                                                                  | Impact                                                                                          | Priority |
| -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | -------- |
| Mixed schemas in `data/curated/providers/` break legacy seed loading | Full test suite fails; legacy detail/search endpoints are unreliable                            | P0       |
| Production settings do not exist                                     | Public deployment would run with `DEBUG=True`, insecure hardcoded dev key, localhost-only hosts | P0       |
| No root Vercel packaging files                                       | Vercel cannot install dependencies reliably from current root without configuration             | P0       |
| Provider publication writes repository YAML                          | Not persistent or concurrency-safe on Vercel                                                    | P0       |
| No authentication/authorization                                      | Public write/search endpoints are open                                                          | P0/P1    |
| No rate limiting or abuse controls                                   | Public API can be spammed                                                                       | P1       |
| OpenAPI not exposed and schema inference warnings exist              | MaaSAI consumers lack generated API contract                                                    | P1       |
| External Fuseki not provisioned/configured                           | Primary RDF search backend unavailable; fallback works but depends on bundled files             | P1       |
| Demo API enabled by default in `settings.py`                         | Demo routes may be exposed unintentionally                                                      | P0       |
| SQLite db is committed and default                                   | Not suitable for request persistence/public production                                          | P1       |
| Empty `.env.example`                                                 | Deployment variables are undocumented for operators                                             | P0       |
| Empty Docker/scripts/ontology source files                           | Ops/reproducibility gap                                                                         | P1/P2    |
| No public API versioning route                                       | Marketplace integration may bind to unstable `/api/...` paths                                   | P1       |
| CORS only allows localhost                                           | Browser-based Marketplace cannot call Vercel deployment until configured                        | P0       |

## 13. What Remains To Complete MDC v1

Required before treating MDC v1 as complete:

| Work item                                                                                | Current status                 |
| ---------------------------------------------------------------------------------------- | ------------------------------ |
| Decide public endpoint contract: `/api/...`, `/api/v1/...`, or both                      | Missing decision               |
| Fix legacy/harmonized data split so full tests pass                                      | Missing                        |
| Make harmonized service-discovery endpoint the documented public contract                | Partly implemented; docs stale |
| Add production settings and deployment env handling                                      | Missing                        |
| Configure external Fuseki or explicitly run first public release on RDFLib/YAML fallback | Missing deployment decision    |
| Persist generated RDF and provider updates outside Vercel filesystem                     | Missing                        |
| Add authentication for write endpoints and likely API-key auth for consumer integration  | Missing                        |
| Add CORS configuration for actual Marketplace origins                                    | Missing                        |
| Add OpenAPI route and annotate serializers/views                                         | Missing                        |
| Add deployment verification scripts/curl docs                                            | Missing                        |
| Add request persistence if MaaSAI needs request audit/history                            | Missing                        |

## 14. Recommended Phase 2 Backlog

| Priority | Backlog item                                                                       | Files/modules                                                                                     |
| -------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| P0       | Fix legacy provider loader/data split so full tests pass                           | `data/curated/providers/`, `providers/loaders.py`, tests                                          |
| P0       | Add production settings loaded from environment                                    | `backend/config/settings.py` or `backend/config/settings/production.py`                           |
| P0       | Add deploy packaging                                                               | `requirements.txt`, `.python-version`, `vercel.json` or `pyproject.toml`, possible `api/index.py` |
| P0       | Disable demo API by default outside local development                              | `settings.py`, `settings_local.py`, tests                                                         |
| P0       | Decide whether `/api/service-discovery/search` is public v1 and update docs/routes | `api/urls.py`, docs                                                                               |
| P1       | Configure external Fuseki deployment and Vercel env vars                           | settings, infra docs                                                                              |
| P1       | Add API authentication and rate limiting                                           | DRF settings, permissions/throttles, middleware                                                   |
| P1       | Add OpenAPI route and schema annotations                                           | `config/urls.py`, API views/serializers                                                           |
| P1       | Move provider publication persistence out of filesystem                            | database/object store/Fuseki update pipeline                                                      |
| P1       | Add health/readiness detail that reports Fuseki and fallback availability          | API health/readiness views                                                                        |
| P2       | Populate ontology and SHACL source files                                           | `ontologies/`                                                                                     |
| P2       | Implement Docker/Fuseki helper scripts for non-Vercel deployment                   | `docker-compose.yml`, `scripts/`                                                                  |
| P2       | Add request-history database models and endpoints                                  | `apps/catalog` or new app                                                                         |

## 15. Prioritized Next Actions

### P0 - Required Before Public Deployment

1. Fix `data/curated/providers/` schema mixing or change legacy loader to ignore source-style files, then rerun the full test suite.
2. Add production settings: environment-driven `SECRET_KEY`, `DEBUG=False`, Vercel/domain `ALLOWED_HOSTS`, real `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, secure cookies, SSL settings.
3. Add Vercel packaging/configuration: root dependency file, Python version pin, Vercel entrypoint/root setup, and function include/exclude rules.
4. Disable or protect demo and mutation endpoints in production, especially `/api/demo/*` and `/api/provider-publication`.
5. Decide public API paths and update the Marketplace contract to match implementation.

### P1 - Required For Reliable MaaSAI Integration

1. Provision external Fuseki and set `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` in Vercel.
2. Add authentication/authorization for public APIs; at minimum API-key auth for trusted MaaSAI components and protected provider publication.
3. Add rate limiting/throttling and request-size controls.
4. Publish OpenAPI/schema docs and add serializer annotations to remove drf-spectacular warnings.
5. Add readiness checks and deployment curl smoke tests for health, filters, service-discovery search, and Fuseki fallback behavior.

### P2 - Later Improvements

1. Populate ontology and SHACL source files.
2. Implement Docker/Fuseki local ops scripts.
3. Add request persistence/audit history.
4. Replace file-backed provider updates with database/object-store backed workflow.
5. Add observability, structured logging, and dashboards.

## 16. Where I Should Restart Coding

Restart at the legacy data/schema break:

```text
backend/apps/providers/loaders.py
data/curated/providers/
backend/tests/test_provider_seed_data.py
backend/tests/test_provider_detail_api.py
```

The immediate goal should be: full test suite passes again while preserving the harmonized service-discovery path. Concretely, decide whether `data/curated/providers/precipart.yaml` belongs in the legacy provider seed folder. If it is source-style input, move it to a source/staging folder or make the legacy loader ignore non-legacy schemas. After that, rerun `manage.py test -v 2`.

For deployment work, restart at:

```text
backend/config/settings.py
backend/config/settings_local.py
requirements/
.env.example
```

The goal should be a production settings split plus Vercel packaging, not endpoint feature work.

# Part 2 - Vercel Deployment And Public API Readiness

## A. Feasibility Verdict

Verdict: **Suitable with moderate changes**.

Why:

| Factor                     | Assessment                                                                                                              |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Django on Vercel           | Feasible. Vercel's 2026 Django support detects `manage.py` and WSGI/ASGI entrypoints.                                   |
| Current Django entrypoints | `backend/config/wsgi.py` and `backend/config/asgi.py` exist and expose `application`.                                   |
| Project layout             | Needs configuration because `manage.py` is under `backend/` while data and requirements live one level above/elsewhere. |
| Dependencies               | Runtime dependencies exist, but there is no root `requirements.txt` or `pyproject.toml` for Vercel.                     |
| Production settings        | Not ready. Current settings are local/dev-oriented.                                                                     |
| Data persistence           | Not ready. File-backed provider publication is unsuitable on Vercel.                                                    |
| Fuseki                     | Should be external. Vercel Functions are not the right place for a long-running JVM RDF store.                          |
| Search                     | `/api/service-discovery/search` can work without Fuseki via RDFLib/YAML fallback if generated data is bundled.          |

Official Vercel facts checked:

- Vercel's Python runtime supports WSGI/ASGI applications and detects Python framework dependencies/entrypoints.
- Vercel's Django guide says Django deployments are loaded from `manage.py` plus WSGI/ASGI settings.
- Django on Vercel becomes a Vercel Function.
- Vercel Functions have a read-only filesystem with writable `/tmp` scratch space.
- Python function bundle size matters; standard uncompressed bundle limit is 500 MB.

Sources:

- Vercel Python runtime: https://vercel.com/docs/functions/runtimes/python
- Vercel Django guide: https://vercel.com/docs/frameworks/full-stack/django
- Vercel runtimes/filesystem: https://vercel.com/docs/functions/runtimes
- Vercel function limits: https://vercel.com/docs/functions/limitations
- Vercel project configuration: https://vercel.com/docs/project-configuration/vercel-json
- Django deployment checklist: https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

## B. Recommended Target Architecture

Recommended production shape:

```text
Marketplace / MaaSAI components
        |
      HTTPS
        v
Vercel-hosted Django API
        |
        | SPARQL over HTTPS
        v
Externally hosted Fuseki
        |
        v
MDC harmonized RDF catalogue
```

Fallback-capable runtime:

```text
/api/service-discovery/search
        |
        v
Try external Fuseki
        |
        | failure
        v
Local generated Turtle via RDFLib
        |
        | failure
        v
Bundled harmonized YAML matcher
```

Do not run Fuseki inside Vercel. Fuseki is a Java server and RDF store, while Vercel Functions are request-scoped serverless functions with read-only deployment filesystem and `/tmp` scratch space. The sensible architecture is Vercel for the Django HTTP API and a separate persistent Fuseki service.

Suitable external Fuseki hosting patterns:

| Option                                                                                                        | Fit                                                |
| ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| Small VM/container service running Fuseki behind HTTPS                                                        | Best match for current architecture                |
| Managed container platform such as Azure Container Apps, AWS ECS/Fargate, Fly.io, Render, Railway, or similar | Good if persistent volume/networking is available  |
| Non-Vercel Django + Fuseki on one VM                                                                          | Simpler early pilot ops, weaker serverless scaling |

## C. Exact Repository Changes Needed

| File/path                                                            |    Exists? | Purpose                                                                             | Precise change required                                                                                                                                                               | Priority |
| -------------------------------------------------------------------- | ---------: | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `requirements.txt` at repo root                                      |         No | Let Vercel install dependencies                                                     | Add runtime dependencies, likely `-r requirements/base.txt`; consider pinning from `requirements/locked.txt` for production                                                           | P0       |
| `.python-version` or `pyproject.toml`                                |         No | Pin supported Python version                                                        | Pin Python to a Vercel-supported version compatible with deps, e.g. 3.12/3.13 after testing                                                                                           | P0       |
| `vercel.json`                                                        |         No | Configure function, include/exclude files, rewrites if needed                       | Add configuration for Django entrypoint and bundle excludes. If using a custom launcher, route all requests to it.                                                                    | P0       |
| `api/index.py`                                                       |         No | Deterministic Vercel WSGI launcher if zero-config does not handle `backend/` layout | Add launcher that inserts `backend/` into `sys.path`, sets `DJANGO_SETTINGS_MODULE`, and exposes `app`/`application` from Django WSGI                                                 | P0       |
| `backend/config/settings.py`                                         |        Yes | Environment-driven production behavior                                              | Stop hardcoding production secret/debug/hosts. Read `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, Fuseki endpoint vars | P0       |
| `backend/config/settings_local.py`                                   |        Yes | Local-only overrides                                                                | Keep local-only demo/debug settings here; ensure Vercel does not use this module                                                                                                      | P0       |
| `.env.example`                                                       | Yes, empty | Operator docs                                                                       | Add placeholders for all required env vars without real secrets                                                                                                                       | P0       |
| `backend/apps/demo/services.py` / settings                           |        Yes | Demo endpoint safety                                                                | Ensure demo API is disabled by default when `DEBUG=False`, or protect it with auth                                                                                                    | P0       |
| `backend/apps/api/urls.py`                                           |        Yes | Public versioning                                                                   | Decide and optionally add `/api/v1/` aliases in `config/urls.py`, or document `/api/` as final                                                                                        | P0/P1    |
| `backend/apps/api/views.py`                                          |        Yes | Provider publication write safety                                                   | Disable public file-backed writes in production or move to durable storage                                                                                                            | P0       |
| `backend/apps/search/service_discovery_runtime_search.py`            |        Yes | External Fuseki runtime                                                             | Make primary backend selection explicit with env toggles; preserve fallback warnings                                                                                                  | P1       |
| `backend/apps/api/views/*`                                           |        Yes | API docs                                                                            | Add schema annotations or class-based views so drf-spectacular can generate OpenAPI                                                                                                   | P1       |
| `backend/config/urls.py`                                             |        Yes | OpenAPI route                                                                       | Add schema and Swagger/Redoc routes if public contract docs are needed                                                                                                                | P1       |
| `docker-compose.yml` / `scripts/load_fuseki.py`                      | Yes, empty | Non-Vercel Fuseki ops                                                               | Implement external/local Fuseki loading workflow                                                                                                                                      | P1       |
| `data/generated/service_discovery/mdc_service_discovery_catalog.ttl` |        Yes | RDFLib fallback                                                                     | Ensure it is generated before deploy and included in Vercel bundle                                                                                                                    | P0/P1    |
| `data/curated/service_discovery/providers/`                          |        Yes | YAML fallback                                                                       | Ensure provider YAML is included in bundle and does not contain confidential fields                                                                                                   | P0       |

Minimum viable Vercel deployment approach:

1. Keep Vercel project root at `mdc-catalog`.
2. Add root `requirements.txt`.
3. Add `.python-version`.
4. Add a deterministic Vercel entrypoint or `pyproject.toml` entrypoint for `backend/config/wsgi.py`.
5. Configure production settings through environment variables.
6. Disable provider-publication writes and demo API in production.
7. Deploy the API with local RDFLib/YAML fallback first.
8. Add external Fuseki after deployment and set `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT`.

## D. Step-By-Step Vercel Guide For A First-Time User

1. Prerequisites:
   - A GitHub account.
   - A Vercel account.
   - The repo pushed to GitHub.
   - Local test command working with `C:\Users\Elahi\Desktop\mdc_v1\.venv`.

2. Prepare Git:
   - Review the dirty worktree.
   - Commit the current backend/apps/tests/data that are meant to deploy.
   - Do not commit real secrets.
   - Decide whether `db.sqlite3` and generated Turtle should be committed for the pilot.

3. Fix P0 tests:
   - Resolve the mixed schema file under `data/curated/providers/`.
   - Run `..\..\.venv\Scripts\python.exe manage.py test -v 2`.
   - Do not deploy while the full suite has unexplained failures.

4. Add Vercel packaging:
   - Add `requirements.txt` at `mdc-catalog/`.
   - Add `.python-version` or `pyproject.toml`.
   - Add `vercel.json` or a Vercel-recognized Django entrypoint setup.

5. Configure production settings:
   - Use environment variables for secrets and hosts.
   - Set `DEBUG=False`.
   - Add Vercel host and custom API domain to `ALLOWED_HOSTS`.
   - Add Marketplace origin(s) to CORS.

6. Create/import project in Vercel:
   - Go to Vercel dashboard.
   - Import the GitHub repository.
   - Set project root to `mdc-catalog` unless you have moved data/requirements under `backend`.
   - Confirm Vercel detects Python/Django or uses the configured entrypoint.

7. Add environment variables in Vercel:
   - Production scope: required production values.
   - Preview scope: separate preview values.
   - Development/local: use `.env.local` locally, not committed.

8. Deploy:
   - Trigger deploy from Vercel dashboard or by pushing to the configured branch.
   - Watch build logs for dependency installation, Django detection, import errors, and bundle-size warnings.

9. Read deployment logs:
   - Check whether `Django` was detected.
   - Check whether dependencies installed from the intended file.
   - Check whether the resolved WSGI/ASGI entrypoint is correct.
   - Check runtime errors after first request.

10. Test health:

```powershell
curl https://<your-vercel-domain>/api/health
```

Expected:

```json
{"status":"ok","service":"maasai-mdc","version":"v1"}
```

11. Test filters:

```powershell
curl https://<your-vercel-domain>/api/catalog/filters
```

12. Test service-discovery search:

```powershell
curl -X POST https://<your-vercel-domain>/api/service-discovery/search `
  -H "Content-Type: application/json" `
  -d "{\"request_id\":\"req_001\",\"consumer_id\":\"marketplace_demo\",\"service_category\":\"precision_gears\",\"part_family\":\"gear\",\"part_type\":\"spur_gear\"}"
```

Expected: `200` with `result_count`, `results`, and `status.search_engine`. If external Fuseki is absent, expect fallback warnings or local RDF/YAML engine status.

13. Configure Marketplace:
   - Set MDC base URL to `https://<your-vercel-domain>`.
   - Use exact implemented path `/api/service-discovery/search` unless version aliases are added.
   - Send `Content-Type: application/json`.
   - Include any API key header once authentication is added.

14. Configure CORS:
   - Add Marketplace origin, e.g. `https://<marketplace-domain>`, to `CORS_ALLOWED_ORIGINS`.
   - Add CSRF trusted origins only where browser unsafe requests require it and auth/session behavior warrants it.

15. Redeploy workflow:
   - Push changes to GitHub.
   - Vercel builds Preview deployments for branches/PRs.
   - Merge to production branch to deploy production.
   - Use Vercel deployment logs and health/search curl checks after each deploy.

16. Rollback/basic recovery:
   - Use Vercel's previous deployments list to promote/rollback.
   - Keep external Fuseki dataset versioned separately.
   - If Fuseki fails, `/api/service-discovery/search` should fall back to local RDFLib/YAML. Monitor status/warnings to detect degraded mode.

## E. Environment-Variable Table

Do not expose real secrets. The repository currently hardcodes a development Django secret in `settings.py`; rotate it for any production use.

| Variable                                  | Required?                      | Example/placeholder                                       | Where used                                               |                         Secret? | Vercel scope        |
| ----------------------------------------- | ------------------------------ | --------------------------------------------------------- | -------------------------------------------------------- | ------------------------------: | ------------------- |
| `DJANGO_SECRET_KEY`                       | Yes                            | `set-in-vercel-secret-value`                              | Production Django `SECRET_KEY`                           |                             Yes | Production, Preview |
| `DJANGO_DEBUG`                            | Yes                            | `False`                                                   | Production debug toggle                                  |                              No | Production, Preview |
| `DJANGO_ALLOWED_HOSTS`                    | Yes                            | `.vercel.app,api.example.org`                             | `ALLOWED_HOSTS`                                          |                              No | Production, Preview |
| `CORS_ALLOWED_ORIGINS`                    | Yes for browser clients        | `https://marketplace.example.org`                         | `django-cors-headers`                                    |                              No | Production, Preview |
| `CSRF_TRUSTED_ORIGINS`                    | Maybe                          | `https://marketplace.example.org`                         | Django CSRF checks                                       |                              No | Production, Preview |
| `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` | P1                             | `https://fuseki.example.org/mdc-service-discovery/sparql` | Harmonized remote Fuseki retrieval                       | Maybe, if private URL/tokenized | Production, Preview |
| `FUSEKI_BASE_URL`                         | Optional/legacy                | `https://fuseki.example.org`                              | Legacy Fuseki settings                                   |                           Maybe | Production, Preview |
| `FUSEKI_DATASET`                          | Optional/legacy                | `mdc`                                                     | Legacy Fuseki settings                                   |                              No | Production, Preview |
| `FUSEKI_QUERY_ENDPOINT`                   | Optional/legacy                | `https://fuseki.example.org/mdc/sparql`                   | Legacy SPARQL client                                     |                           Maybe | Production, Preview |
| `FUSEKI_UPDATE_ENDPOINT`                  | Optional, avoid public API use | `https://fuseki.example.org/mdc/update`                   | Legacy update setting; not currently used in public flow |           Yes if credentialized | Production only     |
| `FUSEKI_TIMEOUT_SECONDS`                  | Optional                       | `5`                                                       | Remote SPARQL timeout                                    |                              No | Production, Preview |
| `MDC_DEMO_API_ENABLED`                    | Yes                            | `False`                                                   | Demo endpoint guard                                      |                              No | Production, Preview |
| `MDC_PROVIDER_PUBLICATION_ENABLED`        | Recommended new var            | `False`                                                   | Gate file-backed/mutation endpoint in production         |                              No | Production, Preview |
| `MDC_API_KEY`                             | Recommended new var            | `set-in-vercel`                                           | Future MaaSAI component auth                             |                             Yes | Production, Preview |
| `DATABASE_URL`                            | Future/P1 if persistence added | `postgres://...`                                          | Django database                                          |                             Yes | Production, Preview |

## F. Public API Integration Contract

Base URL:

```text
https://<mdc-vercel-domain>
```

Recommended current integration endpoint:

| Method | Path                            | Content type       | Auth today | Recommended auth                             |
| ------ | ------------------------------- | ------------------ | ---------- | -------------------------------------------- |
| GET    | `/api/health`                   | N/A                | None       | None or internal allowlist                   |
| GET    | `/api/catalog/filters`          | N/A                | None       | Optional                                     |
| POST   | `/api/service-discovery/search` | `application/json` | None       | API key or service token                     |
| GET    | `/api/providers/<provider_id>`  | N/A                | None       | API key if public provider data is sensitive |
| GET    | `/api/offerings/<offering_id>`  | N/A                | None       | API key if public provider data is sensitive |

Do not expose as reliable production APIs yet:

| Method        | Path                           | Reason                                                           |
| ------------- | ------------------------------ | ---------------------------------------------------------------- |
| POST          | `/api/provider-publication`    | File-backed writes are not persistent/concurrency-safe on Vercel |
| `/api/demo/*` | Explicitly temporary/demo-only |                                                                  |
| POST          | `/api/catalog/search`          | Current legacy data break causes failures                        |

Search request shape for `/api/service-discovery/search`:

```json
{
  "request_id": "req_001",
  "consumer_id": "marketplace_demo",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear",
  "requirements": {
    "part_family_specifications": {
      "module": {"exact": 2.0}
    },
    "part_type_specifications": {},
    "generic_requirements": {
      "materials": ["alloyed_carburizing_steel"],
      "certifications": ["ISO9001_2015"]
    }
  },
  "match_policy": {
    "optional_match_mode": "any",
    "unknown_policy": "keep_as_unknown",
    "minimum_score": null
  }
}
```

Expected status codes:

| Status | Meaning                                                                        |
| -----: | ------------------------------------------------------------------------------ |
|    200 | Search executed through Fuseki, RDFLib fallback, or YAML fallback              |
|    400 | Invalid request contract or uncontrolled value                                 |
|    404 | Provider/offering not found for detail endpoints                               |
|    503 | All service-discovery search backends failed                                   |
|    413 | Vercel function payload too large                                              |
|    500 | Unhandled backend error; should be eliminated before public reliability claims |

Timeout/retry:

- Marketplace should use a client timeout such as 10-15 seconds for search.
- Retry idempotent GETs once or twice.
- For POST search, retry only if `request_id` is stable and the Marketplace can tolerate duplicate searches. There is no request persistence today.
- Treat fallback status/warnings as degraded mode, not a hard failure.

Example curl calls:

```powershell
curl https://<mdc-base-url>/api/health
```

```powershell
curl https://<mdc-base-url>/api/catalog/filters
```

```powershell
curl -X POST https://<mdc-base-url>/api/service-discovery/search `
  -H "Content-Type: application/json" `
  -H "X-MDC-API-Key: <future-api-key>" `
  -d "{\"request_id\":\"req_001\",\"consumer_id\":\"marketplace_demo\",\"service_category\":\"precision_gears\",\"part_family\":\"gear\",\"part_type\":\"spur_gear\"}"
```

## G. Deployment Blockers Checklist

Must fix before first Vercel deployment:

```text
[ ] Add root deploy dependency file or pyproject recognized by Vercel.
[ ] Add a supported Python version pin.
[ ] Configure Vercel/Django entrypoint for the backend subdirectory layout.
[ ] Add production settings from environment variables.
[ ] Set DEBUG=False in production.
[ ] Replace committed development SECRET_KEY with environment-provided secret for production.
[ ] Configure ALLOWED_HOSTS for .vercel.app and/or custom domain.
[ ] Configure CORS_ALLOWED_ORIGINS for the Marketplace domain.
[ ] Disable demo API in production.
[ ] Disable or protect file-backed provider publication in production.
[ ] Ensure data/generated/service_discovery/mdc_service_discovery_catalog.ttl and service_discovery provider YAML are included in the deployment bundle.
```

Must fix before other MaaSAI components rely on the API:

```text
[ ] Fix mixed legacy provider data so full test suite passes, or remove legacy endpoints from the public contract.
[ ] Decide and document canonical API base path/versioning.
[ ] Add authentication/authorization for public integration.
[ ] Add rate limiting/throttling.
[ ] Add OpenAPI/schema route and remove schema inference warnings.
[ ] Provision external Fuseki or explicitly document RDFLib/YAML fallback as temporary pilot mode.
[ ] Add health/readiness behavior that reports Fuseki/fallback state.
[ ] Add deployment smoke-test commands to docs or CI.
```

Optional production hardening:

```text
[ ] Add HSTS/SSL redirect/secure cookie settings after domain/HTTPS behavior is confirmed.
[ ] Add structured logging and error monitoring.
[ ] Add request persistence in a real database.
[ ] Move provider-publication persistence to durable storage and/or an ingestion workflow.
[ ] Populate ontology and SHACL source files.
[ ] Implement Docker/Fuseki local development and load scripts.
```

## Final Recommendation

Use `/api/service-discovery/search` as the next integration target, not the older `/api/catalog/search`, unless you intentionally roll back to the legacy contract. The fastest safe path is:

1. Repair the mixed legacy provider data so the full suite is green.
2. Add production/Vercel packaging and settings.
3. Deploy read-only search first with local RDFLib/YAML fallback.
4. Add external Fuseki and set `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT`.
5. Only then expose provider publication or request persistence.
