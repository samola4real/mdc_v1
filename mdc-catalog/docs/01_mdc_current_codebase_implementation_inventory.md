# MaaSAI MDC — Current Codebase Implementation Inventory

## 1. Purpose and snapshot metadata

This document is an observed technical inventory of the current MaaSAI MaaS Dynamic Catalogue codebase. It is intended to let a later developer or assistant prepare precise Marketplace-interface implementation instructions without guessing existing file paths, module names, API behavior, or storage behavior.

- Inspection timestamp: 2026-05-22 12:24:55 +03:00.
- Git branch: `main`.
- Git commit: `766bc33f79379601ea69ee60b48fc0e4153f8b4a`.
- Documentation numbering note: existing files in `docs/` were unnumbered, so this inventory starts a numbered document convention at `01_`.
- Scope note: this is an observed implementation inventory, not a proposed architecture.
- Verification environment note: `python` resolved to `C:\Users\Elahi\AppData\Local\Programs\Python\Python311\python.exe`; Django was not installed in that active environment.

## 2. Repository structure

Focused repository tree:

```text
mdc-catalog/
  backend/
    manage.py
    config/
      settings.py
      urls.py
      asgi.py
      wsgi.py
    apps/
      api/
      catalog/
      ontology/
      providers/
      search/
    tests/
  data/
    curated/
      tasowheel_offerings.yaml
      providers/
        tasowheel.yaml
        demo_machining_provider.yaml
        demo_heat_treatment_provider.yaml
    generated/
      mdc_catalog.ttl
  ontologies/
    mdc_core.ttl
    mdc_mappings.ttl
    mdc_tasowheel_profile.ttl
    shacl/
      mdc_v1_shapes.ttl
  docs/
    api-contract-v1.md
    architecture.md
    ontology-profile-v1.md
    pilot-assumptions.md
    query-mapping-matrix.md
    seed-data-template.md
    01_mdc_current_codebase_implementation_inventory.md
  requirements/
    base.txt
    dev.txt
    locked.txt
    test.txt
  scripts/
    build_catalog.py
    load_fuseki.py
    validate_graph.py
  docker-compose.yml
  .env.example
  README.md
```

Directory purposes:

- `backend/`: Django project, apps, and tests.
- `backend/config/`: active Django settings and root URL routing.
- `backend/apps/api/`: REST API views, URL routes, response shaping, and request serializers.
- `backend/apps/providers/`: YAML-backed seed-data loading, validation, publication normalization, and repository writes.
- `backend/apps/search/`: canonical search request model, normalizer, local matcher, matcher submodules, SPARQL query builder, Fuseki client, and Fuseki candidate wrapper.
- `backend/apps/ontology/`: controlled vocabularies, ontology mappings, RDF generation, and RDF management command.
- `backend/apps/catalog/`: currently only Django skeleton files; no active catalogue matching implementation found there.
- `backend/tests/`: Django unit tests and optional Fuseki integration tests.
- `data/curated/`: current seed-data source files.
- `data/generated/`: generated RDF Turtle output.
- `ontologies/`: ontology and SHACL placeholder files; all inspected `.ttl` files are currently zero bytes.
- `requirements/`: Python dependency requirement files.
- `scripts/`: script placeholders; inspected script files are currently zero bytes.
- `docker-compose.yml`: present but zero bytes, so no current Docker/Fuseki service definition is implemented there.

## 3. Django settings and runtime configuration

Active settings file:

- `backend/config/settings.py`

Relevant settings observed:

- `BASE_DIR = Path(__file__).resolve().parent.parent`
- `PROJECT_ROOT = BASE_DIR.parent`
- `CURATED_DATA_DIR = PROJECT_ROOT / "data" / "curated"`
- `GENERATED_DATA_DIR = BASE_DIR.parent / "data" / "generated"`
- `PROVIDER_SEED_DIR = CURATED_DATA_DIR / "providers"`
- `FUSEKI_BASE_URL = os.getenv("FUSEKI_BASE_URL", "http://localhost:3030")`
- `FUSEKI_DATASET = os.getenv("FUSEKI_DATASET", "mdc")`
- `FUSEKI_QUERY_ENDPOINT = os.getenv("FUSEKI_QUERY_ENDPOINT", f"{FUSEKI_BASE_URL}/{FUSEKI_DATASET}/sparql")`
- `FUSEKI_UPDATE_ENDPOINT = os.getenv("FUSEKI_UPDATE_ENDPOINT", f"{FUSEKI_BASE_URL}/{FUSEKI_DATASET}/update")`
- `FUSEKI_TIMEOUT_SECONDS = float(os.getenv("FUSEKI_TIMEOUT_SECONDS", "10"))`
- `ROOT_URLCONF = "config.urls"`

MDC-relevant installed Django apps:

- `apps.api.apps.ApiConfig`
- `apps.catalog.apps.CatalogConfig`
- `apps.ontology.apps.OntologyConfig`
- `apps.providers.apps.ProvidersConfig`
- `apps.search.apps.SearchConfig`
- `rest_framework`
- `drf_spectacular`
- `corsheaders`

API root URL configuration:

- `backend/config/urls.py` includes `path("api/", include("apps.api.urls"))`.
- Therefore implemented API paths are rooted at `/api/`, not `/api/v1/`.

Sensitive setting note:

- `SECRET_KEY` is present in `settings.py` but is intentionally not reproduced here.

## 4. Current API endpoints and routing

Implemented routes from `backend/apps/api/urls.py`, mounted under `/api/`:

| Method | URL path | Handler | Purpose | Data/search engine | Serializer |
| --- | --- | --- | --- | --- | --- |
| GET | `/api/health` | `apps.api.views.health` | Basic service health response | Static response | None |
| GET | `/api/catalog/filters` | `apps.api.views.catalog_filters` | Return controlled vocabulary filters | Static vocabularies from `apps.ontology.vocabularies` | None |
| POST | `/api/catalog/search` | `apps.api.views.catalog_search` | Validate, normalize, and execute catalogue search | Local seed-data matcher via `find_offerings_matching_primary_filters()` | `SearchRequestSerializer` |
| POST | `/api/provider-publication` | `apps.api.views.provider_publication` | Accept provider publication payload and write provider YAML seed data | File-backed seed repository | `ProviderPublicationSerializer` |
| GET | `/api/providers/<provider_id>` | `apps.api.views.provider_detail` | Return one provider with offering summaries | Seed data via provider services | None |
| GET | `/api/offerings/<offering_id>` | `apps.api.views.offering_detail` | Return one offering with searchable capability data | Seed data via provider services | None |

No route currently uses Fuseki in the API path. Fuseki exists as a parallel candidate-retrieval service in `apps.search.fuseki_search_service`.

## 5. Provider publication implementation

Serializer file:

- `backend/apps/api/provider_publication_serializers.py`

Serializer classes:

- `FacilityPublicationSerializer`
- `CertificationPublicationSerializer`
- `ProviderPublicationInfoSerializer`
- `MaterialGradePublicationSerializer`
- `NumericRangeSerializer`
- `BatchSizeCapabilitySerializer`
- `WeightCapabilitySerializer`
- `DiametralPitchCapabilitySerializer`
- `QualityCapabilitySerializer`
- `LeadTimeCapabilitySerializer`
- `SurfaceFinishCapabilitySerializer`
- `ToleranceCapabilitySerializer`
- `TraceabilityCapabilitySerializer`
- `OfferingCapabilitiesPublicationSerializer`
- `OfferingPublicationSerializer`
- `PublicationMetadataSerializer`
- `ProviderPublicationSerializer`

Incoming field behavior:

- Top-level `provider` is required.
- Top-level `offerings` is required and cannot be empty.
- Top-level `publication_metadata` is optional.
- `provider.provider_id` is required and currently Marketplace/client supplied.
- `provider.display_name` and `provider.country` are required.
- `provider.legal_name` is optional and may be blank.
- `provider.provider_type` defaults to `MaaSProvider`.
- `provider.facilities` is optional; each supplied facility requires `facility_id`, `city`, and `country`.
- `provider.certifications` is optional; each supplied certification requires `code`, with optional `label`.
- `offerings[].offering_id` is required and currently Marketplace/client supplied.
- `offerings[].name`, `service_type`, `part_families`, `processes`, `supported_materials`, and `capabilities` are required.
- `offerings[].part_families`, `processes`, and `supported_materials` cannot be empty.
- `offerings[].supported_material_grades` is optional; publication input uses objects with `grade_id`, optional `label`, and required `material_id`.
- `publication_metadata.source_type` defaults to `provider_confirmed`.
- `publication_metadata.confidence` defaults to `declared`.
- `publication_metadata.status` defaults to `draft`.

Current ID treatment:

- `provider_id`: required from the incoming payload and used as the output YAML filename.
- `facility_id`: required only for each supplied facility; preserved in normalized provider facilities.
- `offering_id`: required from the incoming payload; must be unique within the payload and must start with `{provider_id}_`.
- `material_id`: required inside each supplied material-grade object and must already appear in the same offering's `supported_materials`.
- `supported_material_grades`: incoming grade objects are normalized into top-level `material_grades[]`, while offerings store only grade ID strings.

Forbidden route/machine/price validation:

- `FORBIDDEN_ROUTE_KEYS` is defined in `backend/apps/providers/validators.py`.
- Provider publication rejects forbidden fields at the top level, under `provider`, under each offering, and under each offering's `capabilities`.
- Rejected keys include `routes`, `route_steps`, `operation_sequence`, `machine_sequence`, `process_order`, `subcontractor_route`, `cycle_time`, `setup_time`, `machine_availability`, `pricing`, and `capacity_calendar`.

Repository and service files:

- `backend/apps/providers/normalizers.py`
  - `normalize_provider_publication()`
  - `normalize_capabilities()`
  - `normalize_materials_from_publication()`
  - `normalize_material_grades_from_publication()`
- `backend/apps/providers/repositories.py`
  - `save_provider_seed_data()`
  - `get_single_provider_id()`
  - `write_yaml_file()`
  - `load_saved_provider_seed_file()`
- Published files are stored at `data/curated/providers/{provider_id}.yaml` through `get_provider_seed_file_path()`.
- After writing, `save_provider_seed_data()` calls `clear_seed_cache()` so subsequent reads reload seed data.

Tests covering publication:

- `backend/tests/test_provider_publication_serializer.py`
- `backend/tests/test_provider_publication_normalizer.py`
- `backend/tests/test_provider_publication_repository.py`
- `backend/tests/test_provider_publication_api.py`

Likely Marketplace-interface impact:

- A future decision that Marketplace supplies only `provider_id` while MDC manages offering identifiers directly affects `OfferingPublicationSerializer.offering_id`, the prefix validation in `ProviderPublicationSerializer.validate()`, publication tests, and repository/normalizer expectations. Internal `offering_id` still must remain because provider lookups, offering lookups, search results, RDF URIs, and SPARQL projections all depend on stable offering identifiers.

## 6. Seed data and provider repository layer

Seed-data file paths:

- `data/curated/providers/tasowheel.yaml`
- `data/curated/providers/demo_machining_provider.yaml`
- `data/curated/providers/demo_heat_treatment_provider.yaml`
- `data/curated/tasowheel_offerings.yaml` exists as the backward-compatible single-file fallback.

Loader and repository files:

- `backend/apps/providers/loaders.py`
  - `load_yaml_file()`
  - `merge_seed_data()`
  - `load_provider_seed_folder()`
  - `load_catalog_seed_data()`
  - `load_tasowheel_seed_data()`
- `backend/apps/providers/services.py`
  - `get_seed_data()` cached with `lru_cache(maxsize=1)`
  - `clear_seed_cache()`
  - `list_providers()`
  - `list_offerings()`
  - `get_provider_by_id()`
  - `get_offering_by_id()`
  - `get_offerings_for_provider()`
- `backend/apps/providers/providers_utils.py`
  - path helpers and provider seed file listing.
- `backend/apps/providers/validators.py`
  - seed-data validation and route-field exclusion.

Top-level seed-data shape:

```text
metadata
providers
materials
material_grades
offerings
```

Current provider IDs and offering IDs:

| Provider ID | Offering IDs |
| --- | --- |
| `tasowheel` | `tasowheel_gears_shafts_precision` |
| `demo_machining_provider` | `demo_machining_provider_precision_machining` |
| `demo_heat_treatment_provider` | `demo_heat_treatment_provider_heat_treatment` |

Current material-grade IDs found in provider seed files:

- Tasowheel: `18CrNiMo7-6`, `16MnCr5`, `20MnCr5`.
- Demo machining provider: `42CrMo4`, `Al6082`.
- Demo heat-treatment provider: none.

Important validation behavior:

- `metadata.route_fields_included` must be `false`.
- Providers and offerings must be non-empty lists.
- Duplicate provider IDs and duplicate offering IDs are rejected.
- Offering `provider_id` must reference a declared provider.
- `service_type`, `part_families`, `processes`, `supported_materials`, certifications, and quality standard are validated against controlled vocabularies.
- Material grades must be declared in top-level `material_grades[]` before an offering may reference them.
- Material-grade `material_id` must reference a declared top-level material.
- Material-grade IDs are not validated against the static `MATERIAL_GRADES` API vocabulary; this allows current seed files to contain `42CrMo4` and `Al6082`, even though the search serializer and filters vocabulary expose only the three Tasowheel grade values.

Provenance and confidence:

- Provider, offering, supported material, material-grade, certification, and capability objects carry `source_type` and/or `confidence`.
- Publication normalization sets known capability provenance from `publication_metadata`; missing capability values are kept explicit and marked `source_type: not_confirmed`, `confidence: unknown`.

## 7. Controlled vocabularies and ontology mappings

Vocabulary file:

- `backend/apps/ontology/vocabularies.py`

Vocabulary constants:

- `SERVICE_TYPES`: `gear_manufacturing`, `shaft_manufacturing`, `machining`, `heat_treatment`, `inspection`, `finishing`.
- `PART_FAMILIES`: `gear`, `spur_gear`, `helical_gear`, `shaft`, `transmission_component`.
- `PROCESSES`: `machining`, `turning`, `milling`, `hobbing`, `gear_shaping`, `hard_turning`, `grinding`, `gear_grinding`, `heat_treatment`, `inspection`.
- `MATERIALS`: `steel`, `alloyed_carburizing_steel`, `stainless_steel`, `aluminum`, `titanium`, `nickel_alloy`.
- `MATERIAL_GRADES`: `18CrNiMo7-6`, `16MnCr5`, `20MnCr5`.
- `CERTIFICATIONS`: `ISO9001_2015`, `ISO14001_2015`, `ISO_TS_16949_partial`, `APQP`, `aerospace_traceability`, `full_traceability`.

Vocabulary functions:

- `get_catalog_filters()`: exposes `service_types`, `part_families`, `processes`, `materials`, `material_grades`, and `certifications` to `/api/catalog/filters`.
- `get_vocabulary_values()`: returns the allowed `value` set for a vocabulary list.

Ontology mapping files:

- `backend/apps/ontology/mappings.py`
  - `SERVICE_ONTOLOGY_CONCEPTS`
  - `MATERIAL_ONTOLOGY_CONCEPTS`
  - `MATERIAL_PARENT_IDS`
  - `get_service_ontology_concept()`
  - `get_material_ontology_concept()`
  - `get_material_parent_id()`
- `backend/apps/ontology/rdf_mappings.py`
  - `SERVICE_TYPE_CONCEPTS`
  - `PART_FAMILY_CONCEPTS`
  - `PROCESS_CONCEPTS`
  - `MATERIAL_CONCEPTS`
  - `CERTIFICATION_CONCEPTS`

Marketplace filter exposure:

- The filters endpoint currently exposes `material_grades`.
- Search requests currently accept `material_grades`, but only the static `MATERIAL_GRADES` values are accepted. This means `42CrMo4` and `Al6082` exist as provider seed evidence but cannot currently be requested through the public search serializer.

Material-grade role:

- Material grades are active internal evidence in seed data, local search result evidence, offering detail responses, RDF generation, and provider publication normalization.
- They are also currently exposed to the Marketplace filters endpoint and accepted in consumer search. A future materials-only M18 interface can hide or remove Marketplace input without deleting internal grade evidence.

## 8. Consumer SearchRequest pipeline

Serializer file:

- `backend/apps/api/search_serializers.py`

Serializer classes:

- `PositiveRangeOrExactSerializer`
- `PositiveRangeSerializer`
- `DiameterDimensionsSerializer`
- `WeightSerializer`
- `QualitySearchSerializer`
- `GearParametersSerializer`
- `SurfaceFinishSerializer`
- `DeliverySerializer`
- `MatchPolicySerializer`
- `SearchRequestSerializer`

Current request schema:

- `service_type`: optional controlled value.
- `part_family`: optional controlled value, but at least one of `part_family` or `part_families` is required.
- `part_families`: optional non-empty list of controlled values, default `[]`.
- `materials`: optional list of controlled values, default `[]`.
- `material_grades`: optional list of controlled values from static `MATERIAL_GRADES`, default `[]`.
- `processes`: optional list of controlled values, default `[]`.
- `dimensions.diameter_mm`: optional object with `min`, `max`, and/or `exact`; positive values required.
- `weight_kg.max`: optional positive number.
- `gear_parameters.module`: optional positive range.
- `gear_parameters.diametral_pitch`: optional positive range.
- `gear_parameters.quality.standard`: optional `DIN` or `ISO`.
- `gear_parameters.quality.max_class`: optional positive number.
- `surface_finish.ra_um`: optional positive range.
- `batch_size`: optional positive integer.
- `delivery.max_weeks`: optional positive number.
- `certifications`: optional list of controlled values, default `[]`.
- `traceability_required`: optional boolean, default `False`.
- `industry`: optional string.
- `match_policy.primary_match_mode`: optional `any` or `all`, default `any`.
- `match_policy.optional_match_mode`: optional `any`, `all`, or `score_only`, default `any`.
- `match_policy.unknown_policy`: optional `keep_as_unknown` or `reject_unknown`, default `keep_as_unknown`.
- `match_policy.minimum_score`: optional float from 0 to 1.

Unsupported/forbidden search fields:

- Consumer search does not fail immediately on forbidden route/machine/price fields.
- `validate_no_unsupported_search_fields()` collects warnings for top-level forbidden fields and the endpoint returns them in `warnings`.
- Nested forbidden search fields are not inspected by this serializer.

Current missing Marketplace IDs:

- `consumer_id` is not present in `SearchRequestSerializer`, `CanonicalSearchRequest`, normalized request output, or search responses.
- `request_id` is not present in `SearchRequestSerializer`, `CanonicalSearchRequest`, normalized request output, or search responses.

Normalizer/request files:

- `backend/apps/search/request.py`
  - `CanonicalSearchRequest` dataclass with `primary_filters`, `optional_criteria`, `match_policy`, and `warnings`.
- `backend/apps/search/normalizer.py`
  - `DEFAULT_MATCH_POLICY`
  - `has_meaningful_value()`
  - `normalize_to_list()`
  - `clean_nested_dict()`
  - `normalize_match_policy()`
  - `normalize_primary_filters()`
  - `normalize_optional_criteria()`
  - `normalize_search_request()`

Canonical request shape:

```json
{
  "primary_filters": {
    "part_families": ["shaft"]
  },
  "optional_criteria": {
    "service_type": "machining",
    "materials": ["steel"],
    "dimensions": {
      "diameter_mm": {"max": 300}
    }
  },
  "match_policy": {
    "primary_match_mode": "any",
    "optional_match_mode": "any",
    "unknown_policy": "keep_as_unknown",
    "minimum_score": null
  },
  "warnings": []
}
```

Primary filters:

- Currently only `part_families` is normalized as a primary filter.
- `part_family` and `part_families` are merged and deduplicated.

Optional criteria:

- `service_type`, `materials`, `material_grades`, `processes`, `batch_size`, `certifications`, and `industry` are copied when meaningful.
- `traceability_required` is included only when `True`.
- `dimensions`, `weight_kg`, `gear_parameters`, `surface_finish`, and `delivery` are recursively cleaned of empty nested values.

Match policy:

- Defaults are applied by the normalizer.
- `optional_match_mode`, `unknown_policy`, and `minimum_score` are preserved in the canonical request but are not currently used by the local matcher to filter or reject results.

## 9. Local matcher implementation

Main file:

- `backend/apps/search/local_matcher.py`

Current shape:

- The matcher is refactored into submodules under `backend/apps/search/matchers/`; it is not fully monolithic.
- Public entry function: `find_offerings_matching_primary_filters(canonical_request)`.

Matcher modules and responsibilities:

- `common.py`: list normalization, numeric conversion, coverage score, total score, generic scalar/list/range optional matching.
- `part_family.py`: primary part-family matching with `any`/`all` modes.
- `service_type.py`: optional service type exact matching.
- `material.py`: optional material and material-grade list matching.
- `dimensions.py`: diameter, weight, module, diametral pitch, and surface-finish optional matching.
- `production.py`: batch-size optional matching.
- `quality.py`: quality standard/class optional matching.
- `delivery.py`: delivery lead-time optional matching.
- `certification.py`: provider certification optional matching.
- `traceability.py`: traceability optional matching.
- `result_builder.py`: final local search result shape, score aggregation, matched/unmatched/unknown attributes, and evidence.

Currently matched criteria:

- Primary filter: `part_families`.
- Optional criteria evaluated for scoring/explanation: `service_type`, `materials`, `material_grades`, `processes`, `diameter_mm`, `weight_kg`, `batch_size`, `module`, `diametral_pitch`, `quality`, `surface_finish.ra_um`, `delivery.max_weeks`, `certifications`, `traceability_required`, and `industry`.

Scoring behavior:

- Primary score is list coverage over requested part families.
- Optional score is the average of non-unknown optional evaluation scores when optional evaluations exist.
- Total score equals primary score when no optional score exists.
- When optional score exists, total score is `primary_score * 0.7 + optional_score * 0.3`.
- Results are sorted by `match.score` descending.

Result structure:

- `provider`: `provider_id`, `display_name`, `country`.
- `offering`: `offering_id`, `provider_id`, `name`, `service_type`.
- `match`: status, total score, primary score, optional score, hard-filter pass flag, primary match mode, requested/matched counts.
- `matched_attributes`
- `unmatched_attributes`
- `unknown_attributes`
- `evidence`: part families, materials, material grades, processes, capabilities, certifications.

Active API engine:

- `/api/catalog/search` currently calls `find_offerings_matching_primary_filters()` and reports `search_engine: local_seed_catalog_matcher`.

Tests:

- No dedicated local matcher test file was found.
- No test was found for `/api/catalog/search` or for `find_offerings_matching_primary_filters()` in `backend/tests/`.

## 10. RDF generation implementation

Files:

- `backend/apps/ontology/rdf_generator.py`
- `backend/apps/ontology/rdf_mappings.py`
- `backend/apps/ontology/management/commands/generate_catalog_rdf.py`

Management command:

- Command name: `generate_catalog_rdf`
- Command path: `backend/apps/ontology/management/commands/generate_catalog_rdf.py`
- The command builds a graph for triple count and then calls `write_catalog_turtle()`, which builds the graph again before writing.

Input data source:

- `build_catalog_graph()` uses provided `seed_data` or falls back to `apps.providers.services.get_seed_data()`.

Generated Turtle path:

- Default output: `data/generated/mdc_catalog.ttl`, using `settings.GENERATED_DATA_DIR`.

RDF namespace:

- `https://maasai-project.eu/ontology/mdc#`

Generated entities and properties:

- Providers:
  - type `mdc:MaaSProvider`
  - `mdc:providerId`, `mdc:displayName`, `mdc:legalName`, `mdc:country`, `mdc:sourceType`, `mdc:dataConfidence`
  - `mdc:hasCertification`
- Certifications:
  - type `mdc:Certification`
- Materials:
  - type `mdc:Material`
  - `mdc:materialId`, `mdc:label`
- Material grades:
  - type `mdc:MaterialGrade`
  - `mdc:materialGradeCode`, `mdc:label`, `mdc:sourceType`, `mdc:dataConfidence`
  - `mdc:gradeOfMaterial`
- Offerings:
  - type `mdc:ProviderOffering`
  - provider relationship: `mdc:hasOffering`, `mdc:offeredBy`
  - `mdc:offeringId`, `mdc:providerId`, `mdc:displayName`, `mdc:sourceType`, `mdc:dataConfidence`
  - `mdc:hasServiceType`
  - `mdc:supportsPartFamily`
  - `mdc:supportsProcess`
  - `mdc:supportsMaterial`
  - `mdc:supportsMaterialGrade`
- Capabilities:
  - `mdc:batchMin`, `mdc:batchMax`
  - `mdc:diameterMinMm`, `mdc:diameterMaxMm`
  - `mdc:weightMaxKg`, `mdc:weightApproximate`
  - `mdc:moduleMin`, `mdc:moduleMax`
  - `mdc:dpMin`, `mdc:dpMax`, `mdc:dpRaw`
  - `mdc:qualityClassBest`
  - `mdc:leadTimeMinWeeks`, `mdc:leadTimeMaxWeeks`, `mdc:leadTimeQualifier`
  - `mdc:surfaceRaMinUm`
  - `mdc:toleranceMinMm`

Observed RDF limitations:

- Provider facilities are not emitted.
- Capability-level `source_type`, `confidence`, and source notes are not emitted, except offering-level and material-grade-level provenance.
- Traceability capability fields are not emitted.
- `surface_finish_ra_um.max` is emitted under property `mdc:surfaceRaMinUm`; this may be a naming/semantic mismatch in the current implementation.

Tests:

- `backend/tests/test_rdf_generator.py`

## 11. SPARQL query builder

File:

- `backend/apps/search/query_builder.py`

Public functions/classes:

- `SparqlQueryBuildError`
- `get_part_family_concepts()`
- `build_values_clause()`
- `get_primary_match_mode()`
- `build_part_family_having_clause()`
- `build_part_family_search_query()`
- `build_candidate_evidence_query()`

Supported primary filters:

- Only `primary_filters.part_families` is supported.
- Controlled API values are mapped through `PART_FAMILY_CONCEPTS`.

`build_part_family_search_query()` purpose:

- Builds deterministic SPARQL for primary part-family matching.
- Projects provider and offering identity plus matched part-family count/URIs.
- Applies `primary_match_mode` as `HAVING COUNT > 0` for `any` or `HAVING COUNT = requested_count` for `all`.

`build_candidate_evidence_query()` purpose:

- Builds deterministic SPARQL for primary part-family candidate search and evidence projection.
- Projects provider/offering identity, matched part-family count/URIs, material URIs, diameter min/max, batch min/max, and lead-time min/max.

Optional search requirements:

- Optional request criteria such as material, diameter, batch, and lead time are not applied as SPARQL filters.
- The candidate query returns some corresponding evidence values but does not perform final scoring or explanation.

Tests:

- `backend/tests/test_sparql_query_builder.py`
- Tests include deterministic query generation and RDFLib execution against the generated graph.

## 12. Fuseki integration

Settings used:

- `FUSEKI_QUERY_ENDPOINT`
- `FUSEKI_TIMEOUT_SECONDS`
- Also configured but not used by the current client: `FUSEKI_BASE_URL`, `FUSEKI_DATASET`, `FUSEKI_UPDATE_ENDPOINT`.

SPARQL client file:

- `backend/apps/search/sparql_client.py`

SPARQL client public functions/classes:

- `SparqlClientError`
- `SparqlEndpointUnavailable`
- `SparqlQueryError`
- `get_fuseki_query_endpoint()`
- `get_fuseki_timeout_seconds()`
- `execute_select_query()`
- `get_bindings()`
- `binding_value()`

Fuseki candidate service file:

- `backend/apps/search/fuseki_search_service.py`

Fuseki service public functions:

- `optional_float()`
- `optional_int()`
- `split_uri_list()`
- `uri_fragment()`
- `uri_list_fragments()`
- `normalize_candidate_binding()`
- `normalize_candidate_bindings()`
- `search_fuseki_candidates()`

Normalized candidate row shape:

```json
{
  "provider": {
    "provider_id": "tasowheel",
    "display_name": "Tasowheel Oy"
  },
  "offering": {
    "offering_id": "tasowheel_gears_shafts_precision",
    "name": "High-quality gears and shafts"
  },
  "primary_match": {
    "matched_part_family_count": 2,
    "matched_part_family_uris": [],
    "matched_part_families": []
  },
  "evidence": {
    "material_uris": [],
    "materials": [],
    "diameter_mm": {"min": 10.0, "max": 450.0},
    "batch_size": {"min": 100, "max": 2000},
    "lead_time_weeks": {"min": 8.0, "max": 12.0}
  }
}
```

Integration-test behavior:

- `backend/tests/test_fuseki_integration.py` checks the configured Fuseki host/port with a socket connection.
- If Fuseki is not reachable, tests in `FusekiIntegrationTests.setUp()` are skipped with: `Fuseki is not running. Skipping optional Fuseki integration tests.`
- Static inspection found one top-level function named `test_search_fuseki_candidates_returns_normalized_tasowheel_candidate(self)` outside the test class; under Django/unittest discovery this is not expected to run as a normal test method.

Current API usage:

- Fuseki is not currently used by `/api/catalog/search`.
- It is available as a parallel candidate-retrieval path through `search_fuseki_candidates()`.

## 13. Current response structures

Provider-publication endpoint, `POST /api/provider-publication`:

```json
{
  "status": "accepted",
  "provider_id": "api_example_provider",
  "created_or_updated": "created",
  "storage": {
    "type": "file_backed_seed_repository",
    "file_name": "api_example_provider.yaml"
  },
  "offerings": [
    {
      "offering_id": "api_example_provider_precision_machining",
      "service_type": "machining"
    }
  ],
  "next_steps": {
    "rdf_generation_required": true,
    "rdf_generation_done": false
  }
}
```

Provider detail endpoint, `GET /api/providers/<provider_id>`:

```json
{
  "provider_id": "tasowheel",
  "legal_name": "Tasowheel Oy",
  "display_name": "Tasowheel Oy",
  "provider_type": "MaaSProvider",
  "country": "Finland",
  "source_type": "provider_confirmed",
  "confidence": "declared",
  "facilities": [],
  "certifications": ["ISO9001_2015"],
  "offerings": [
    {
      "offering_id": "tasowheel_gears_shafts_precision",
      "name": "High-quality gears and shafts",
      "service_type": "gear_manufacturing"
    }
  ]
}
```

Offering detail endpoint, `GET /api/offerings/<offering_id>`:

```json
{
  "offering_id": "tasowheel_gears_shafts_precision",
  "provider_id": "tasowheel",
  "name": "High-quality gears and shafts",
  "service_type": "gear_manufacturing",
  "ontology_service_concept": "mdc:GearTransmissionService",
  "source_type": "provider_confirmed",
  "confidence": "declared",
  "part_families": [],
  "processes": [],
  "materials": [],
  "material_grades": [],
  "capabilities": {},
  "notes": []
}
```

Catalogue search endpoint, `POST /api/catalog/search`:

```json
{
  "request": {
    "primary_filters": {},
    "optional_criteria": {},
    "match_policy": {},
    "warnings": []
  },
  "warnings": [],
  "query_interpretation": {
    "primary_filters": {},
    "optional_criteria": {},
    "match_policy": {}
  },
  "result_count": 0,
  "results": [],
  "status": {
    "search_executed": true,
    "search_engine": "local_seed_catalog_matcher",
    "message": "Search executed using local seed-data matching. Primary part-family matching and local optional criteria matching are implemented. RDF/SPARQL search is not implemented yet."
  }
}
```

Each search result currently includes:

- `provider`
- `offering`
- `match`
- `matched_attributes`
- `unmatched_attributes`
- `unknown_attributes`
- `evidence`

Catalogue search currently includes:

- Request object: implemented.
- Warnings: implemented.
- Query interpretation: implemented.
- Result count: implemented.
- Provider object: implemented per result.
- Offering object: implemented per result.
- Match score/status: implemented per result.
- Matched attributes: implemented.
- Unmatched attributes: implemented.
- Unknown attributes: implemented.
- Evidence: implemented.
- Consumer ID: not implemented.
- Request ID: not implemented.

## 14. Test inventory and current status

Relevant test files:

- Seed/provider data:
  - `backend/tests/test_provider_seed_data.py`
- Provider publication:
  - `backend/tests/test_provider_publication_serializer.py`
  - `backend/tests/test_provider_publication_normalizer.py`
  - `backend/tests/test_provider_publication_repository.py`
  - `backend/tests/test_provider_publication_api.py`
- Search serializer/normalizer:
  - `backend/tests/test_search_request_serializer.py`
  - `backend/tests/test_search_request_normalizer.py`
- API endpoint:
  - `backend/tests/test_api_v1.py`
  - `backend/tests/test_provider_detail_api.py`
  - Provider-publication API tests are in `test_provider_publication_api.py`.
- Local matcher:
  - No dedicated local matcher test file found.
  - No `/api/catalog/search` endpoint test found.
- RDF generation:
  - `backend/tests/test_rdf_generator.py`
- SPARQL query builder:
  - `backend/tests/test_sparql_query_builder.py`
- Fuseki client/service/integration:
  - `backend/tests/test_fuseki_search_service.py`
  - `backend/tests/test_fuseki_integration.py`
- Local-vs-Fuseki comparison:
  - No dedicated comparison test file found.

Static test count:

- Static scan found 125 `def test_` functions under `backend/tests/`.
- Because Django could not import, `python manage.py test` did not reach test discovery and did not report an official number of discovered tests.

Command results:

`python manage.py check`:

```text
ModuleNotFoundError: No module named 'django'
ImportError: Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable? Did you forget to activate a virtual environment?
```

Status: failed before Django startup in the active Python environment.

`python manage.py test`:

```text
ModuleNotFoundError: No module named 'django'
ImportError: Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable? Did you forget to activate a virtual environment?
```

Status: failed before Django startup in the active Python environment. No skipped integration tests were reported because test discovery did not start.

## 15. Differences between existing documentation and actual implementation

Observed implementation/documentation mismatches:

- Existing docs frequently describe `/api/v1/...`; implemented routes are `/api/...`.
- Existing architecture/API docs describe search as SPARQL/Fuseki-backed; implemented `/api/catalog/search` uses the local seed-data matcher.
- Existing docs describe or imply `request_id` in search responses; implemented search responses do not include `request_id`.
- `consumer_id` is not implemented in request or response structures.
- `service_type` is documented as required in some existing API-contract text; implemented serializer makes it optional.
- Implemented search requires at least one of `part_family` or `part_families`; docs often emphasize singular `part_family`.
- `part_families` is implemented and normalized, but older docs focus on `part_family`.
- Material grades are exposed by `/api/catalog/filters` and accepted by the search serializer, but only static Tasowheel grades are accepted as search inputs. Demo provider grade evidence (`42CrMo4`, `Al6082`) exists internally but is not searchable through public `material_grades`.
- Generic dimension support is not implemented. Implemented `dimensions` supports only `diameter_mm`.
- `optional_match_mode`, `unknown_policy`, and `minimum_score` are validated/normalized but are not currently used to filter local search results.
- Provider-publication currently requires externally supplied `offering_id`; future Marketplace ID-ownership discussions may conflict with this.
- `docker-compose.yml`, `scripts/*.py`, and ontology `.ttl` source/profile files are present but zero bytes, while docs describe a fuller Fuseki/ontology operational flow.
- RDF generation emits generated Turtle into `data/generated/mdc_catalog.ttl`, but there is no implemented Docker/Fuseki load script content in the inspected script placeholders.
- RDF generation currently emits `surface_finish_ra_um.max` as `mdc:surfaceRaMinUm`, which appears inconsistent with the source field name.

## 16. Impact assessment for the new Marketplace-interface decisions

### Decision A — Add `consumer_id` and `request_id`

Likely affected existing files:

- `backend/apps/api/search_serializers.py`: add request fields and validation rules if IDs are accepted from Marketplace.
- `backend/apps/search/request.py`: extend `CanonicalSearchRequest` if IDs should be part of canonical state.
- `backend/apps/search/normalizer.py`: copy/generate/preserve IDs into canonical request.
- `backend/apps/api/views.py`: include IDs in `/api/catalog/search` response.
- `backend/apps/search/query_builder.py`: likely unaffected unless IDs are used in query metadata only.
- `backend/tests/test_search_request_serializer.py`: request validation coverage.
- `backend/tests/test_search_request_normalizer.py`: canonical ID preservation/generation coverage.
- New or existing API search tests should cover response IDs; no current search endpoint test was found.
- Existing docs to update: `docs/api-contract-v1.md`, `docs/architecture.md`, and likely `docs/query-mapping-matrix.md`.

### Decision B — Marketplace provides `provider_id`, while MDC manages other identifiers

Likely affected existing files:

- `backend/apps/api/provider_publication_serializers.py`: make `offerings[].offering_id` optional or remove it from Marketplace-facing input, and remove/replace the required prefix validation.
- `backend/apps/providers/normalizers.py`: generate stable internal offering IDs when absent.
- `backend/apps/providers/repositories.py`: still writes by provider ID; likely minimal changes unless overwrite/versioning policy changes.
- `backend/apps/api/views.py`: provider-publication response should continue returning generated internal offering IDs.
- `backend/apps/providers/validators.py`: internal seed data should still require `offering_id` because the rest of the system depends on it.
- Tests:
  - `backend/tests/test_provider_publication_serializer.py`
  - `backend/tests/test_provider_publication_normalizer.py`
  - `backend/tests/test_provider_publication_repository.py`
  - `backend/tests/test_provider_publication_api.py`
  - `backend/tests/test_provider_seed_data.py` if internal validation behavior changes.

Internal `offering_id` must remain. It is used by provider/offering lookup APIs, search result responses, RDF URI generation, SPARQL projections, tests, and generated Turtle.

### Decision C — Materials-only Marketplace input for M18

Likely affected existing files:

- `backend/apps/ontology/vocabularies.py`: decide whether `material_grades` remains exposed in `get_catalog_filters()`.
- `backend/apps/api/search_serializers.py`: remove, deprecate, or ignore Marketplace `material_grades` input.
- `backend/apps/search/normalizer.py`: stop adding `material_grades` to Marketplace optional criteria if removed externally.
- `backend/apps/search/local_matcher.py` and `backend/apps/search/matchers/material.py`: keep internal grade evidence, but avoid matching on Marketplace grade criteria if no longer accepted.
- `backend/apps/api/response_utils.py`: likely keep offering `material_grades` as evidence/detail unless Marketplace response policy says to hide them.
- `backend/apps/ontology/rdf_generator.py`: likely keep `supportsMaterialGrade` for internal/RDF evidence.
- Tests:
  - `backend/tests/test_api_v1.py`
  - `backend/tests/test_search_request_serializer.py`
  - `backend/tests/test_search_request_normalizer.py`
  - local matcher/search endpoint tests should be added or updated.

Material grades already remain useful internally as provider evidence, offering-detail data, publication normalization output, RDF nodes/links, and search-result evidence.

### Decision D — Generic future part dimensions

Likely affected files if/when implemented:

- `backend/apps/api/search_serializers.py`: replace diameter-only `dimensions` schema with generic part-dimension schema.
- `backend/apps/search/request.py`: canonical request may need explicit generic dimensions structure.
- `backend/apps/search/normalizer.py`: normalize generic dimension inputs.
- `backend/apps/search/matchers/dimensions.py`: evaluate generic dimensions instead of hardcoded diameter/module/surface fields.
- `backend/apps/search/local_matcher.py`: collect new dimension evaluations.
- `backend/apps/ontology/rdf_generator.py`: emit generic dimension triples if represented in RDF.
- `backend/apps/search/query_builder.py`: add deterministic SPARQL templates for generic dimensions if Fuseki matching is expanded.
- `backend/apps/search/fuseki_search_service.py`: normalize projected generic dimension evidence.
- Tests:
  - `backend/tests/test_search_request_serializer.py`
  - `backend/tests/test_search_request_normalizer.py`
  - `backend/tests/test_rdf_generator.py`
  - `backend/tests/test_sparql_query_builder.py`
  - new local matcher/search endpoint tests.

Current status: future/deferred. Only `dimensions.diameter_mm` is implemented under the generic-looking `dimensions` key.

## 17. Recommended safe implementation order

1. Update the interface/documentation decision record so `/api/...` versus `/api/v1/...`, local matcher versus Fuseki, and ID ownership are explicit.
2. Add `consumer_id` and `request_id` to the consumer search interface and tests.
3. Decide and implement provider-publication ID ownership, keeping internal `offering_id` stable.
4. Simplify Marketplace material-grade exposure/input while preserving internal grade evidence in seed data, RDF, provider details, and possibly result evidence.
5. Add search endpoint/local matcher tests before changing matching behavior.
6. Resume local-vs-Fuseki candidate/result comparison after the Marketplace-facing response shape is stable.
7. Consider generic dimensions later as a separate schema and matching change.

## 18. Appendix: important actual file paths

Settings/configuration:

- `backend/config/settings.py`
- `backend/config/urls.py`
- `backend/manage.py`
- `requirements/base.txt`
- `requirements/dev.txt`
- `requirements/test.txt`
- `requirements/locked.txt`
- `.env.example`
- `docker-compose.yml`

API:

- `backend/apps/api/urls.py`
- `backend/apps/api/views.py`
- `backend/apps/api/search_serializers.py`
- `backend/apps/api/provider_publication_serializers.py`
- `backend/apps/api/response_utils.py`
- `backend/apps/api/serializers.py` currently empty.

Providers/publication:

- `backend/apps/providers/loaders.py`
- `backend/apps/providers/services.py`
- `backend/apps/providers/repositories.py`
- `backend/apps/providers/normalizers.py`
- `backend/apps/providers/providers_utils.py`
- `backend/apps/providers/validators.py`
- `backend/apps/providers/exceptions.py`

Search:

- `backend/apps/search/request.py`
- `backend/apps/search/normalizer.py`
- `backend/apps/search/local_matcher.py`
- `backend/apps/search/query_builder.py`
- `backend/apps/search/sparql_client.py`
- `backend/apps/search/fuseki_search_service.py`
- `backend/apps/search/matchers/common.py`
- `backend/apps/search/matchers/part_family.py`
- `backend/apps/search/matchers/service_type.py`
- `backend/apps/search/matchers/material.py`
- `backend/apps/search/matchers/dimensions.py`
- `backend/apps/search/matchers/production.py`
- `backend/apps/search/matchers/quality.py`
- `backend/apps/search/matchers/delivery.py`
- `backend/apps/search/matchers/certification.py`
- `backend/apps/search/matchers/traceability.py`
- `backend/apps/search/matchers/result_builder.py`

Ontology/RDF:

- `backend/apps/ontology/vocabularies.py`
- `backend/apps/ontology/mappings.py`
- `backend/apps/ontology/rdf_mappings.py`
- `backend/apps/ontology/rdf_generator.py`
- `backend/apps/ontology/management/commands/generate_catalog_rdf.py`

Data:

- `data/curated/providers/tasowheel.yaml`
- `data/curated/providers/demo_machining_provider.yaml`
- `data/curated/providers/demo_heat_treatment_provider.yaml`
- `data/curated/tasowheel_offerings.yaml`
- `data/generated/mdc_catalog.ttl`
- `ontologies/mdc_core.ttl`
- `ontologies/mdc_mappings.ttl`
- `ontologies/mdc_tasowheel_profile.ttl`
- `ontologies/shacl/mdc_v1_shapes.ttl`

Tests:

- `backend/tests/test_api_v1.py`
- `backend/tests/test_provider_detail_api.py`
- `backend/tests/test_provider_seed_data.py`
- `backend/tests/test_provider_publication_serializer.py`
- `backend/tests/test_provider_publication_normalizer.py`
- `backend/tests/test_provider_publication_repository.py`
- `backend/tests/test_provider_publication_api.py`
- `backend/tests/test_search_request_serializer.py`
- `backend/tests/test_search_request_normalizer.py`
- `backend/tests/test_rdf_generator.py`
- `backend/tests/test_sparql_query_builder.py`
- `backend/tests/test_fuseki_search_service.py`
- `backend/tests/test_fuseki_integration.py`

Existing docs:

- `docs/api-contract-v1.md`
- `docs/architecture.md`
- `docs/ontology-profile-v1.md`
- `docs/pilot-assumptions.md`
- `docs/query-mapping-matrix.md`
- `docs/seed-data-template.md`
- `docs/01_mdc_current_codebase_implementation_inventory.md`
