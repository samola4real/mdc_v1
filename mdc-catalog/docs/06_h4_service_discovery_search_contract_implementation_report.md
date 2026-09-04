# MaaSAI MDC - H4 Service Discovery Search Contract Implementation Report

## 1. Status and scope

Phase: H4.

Purpose: additive harmonized consumer request/response contract and canonical normalization.

The new contract is not wired into the active `/api/catalog/search` endpoint. Matching, persistence, RDF, SPARQL, and Fuseki remain unchanged.

## 2. Verified prerequisite tests

H1 focused tests passed: 12.

H1 + H2 focused tests:

```text
Ran 56 tests in 0.051s
OK
```

H1 + H2 + H3 focused tests:

```text
Ran 71 tests in 0.154s
OK
```

No claim is made that the full legacy project test suite passes.

## 3. Files created and modified

Created H4 files:

- `backend/apps/api/service_discovery_search_serializers.py`
- `backend/apps/search/service_discovery_request.py`
- `backend/apps/search/service_discovery_normalizer.py`
- `backend/tests/test_service_discovery_search_serializer.py`
- `backend/tests/test_service_discovery_search_normalizer.py`
- `backend/tests/test_service_discovery_search_response_contract.py`
- `docs/06_h4_service_discovery_search_contract_implementation_report.md`

Updated existing file:

- `docs/05_h3_harmonized_provider_yaml_migration_report.md`

No implementation file outside the new H4 modules was modified.

## 4. Harmonized request contract

Required request metadata:

- `request_id`
- `consumer_id`

The harmonized request selects exactly one:

- `service_category`
- `part_family`
- `part_type`

The request rejects `part_families`, multi-part request structures, unknown service categories, category/family mismatches, and part types outside the selected family.

Requirement groups:

- `requirements.part_family_specifications`
- `requirements.part_type_specifications`
- `requirements.generic_requirements`

All six approved gear-family specification fields are supported:

- `module`
- `diametral_pitch`
- `number_of_teeth`
- `outside_diameter_mm`
- `gear_quality`
- `tolerance_mm`

Field validation is registry based. Family-common fields must appear in `part_family_specifications`; part-type-specific fields must appear in `part_type_specifications`; generic fields must appear in `generic_requirements` only when not displaced by a scoped profile field.

Consumer `material_grades` are rejected. Material grades remain provider/result evidence only.

Match policy contains:

- `optional_match_mode`
- `unknown_policy`
- `minimum_score`

`primary_match_mode` is rejected because the harmonized request selects exactly one service category, one family, and one part type.

Unknown fields and forbidden route/machine/price fields are rejected recursively.

Scope-precedence rule:

When a field is applicable through the selected part profile, such as `tolerance_mm` for gears, shafts, or rotational metal parts, its scoped placement takes precedence over `generic_requirements`. Duplicate fields across requirement groups are rejected.

## 5. Canonical normalized request

The normalizer returns:

- `request_id`
- `consumer_id`
- `selection`
- `requirements`
- `match_policy`
- `warnings`

Empty requirement groups remain present as empty dictionaries. Numeric values are normalized through serializer validation before canonical construction.

The normalizer does not load provider YAML, call matching, build result responses, persist requests, generate RDF, build SPARQL, or query Fuseki.

## 6. Harmonized response contract

The response serializer validates a future response envelope only. It does not build results or activate an endpoint.

Provider result objects use external `provider_name`; internal `display_name` without `provider_name` is rejected.

Offering result objects use external `offering_name`; internal `name` without `offering_name` is rejected.

The response preserves:

- `match`
- `matched_attributes`
- `unmatched_attributes`
- `unknown_attributes`
- `evidence`

Material grades may appear only as nested result evidence under `materials[].available_grades`, not as consumer request criteria.

## 7. Tests created

`backend/tests/test_service_discovery_search_serializer.py` covers:

- valid complete `spur_gear` requests;
- valid `hollow_shaft`, `bracket`, and `bushing` scoping;
- metadata and taxonomy rejection;
- gear-family field acceptance;
- wrong-group and duplicate-field rejection;
- generic materials, processes, delivery, certifications, surface finish, weight, and quality validation;
- material-grade rejection;
- range/exact, integer, bounding-box, unknown-field, and forbidden-field validation.

`backend/tests/test_service_discovery_search_normalizer.py` covers:

- canonical `spur_gear` normalization;
- preservation of request IDs, consumer IDs, selection, requirements, match policy, and warnings;
- default match policy;
- empty requirement group preservation;
- absence of result, response, matching, persistence, or YAML-loading behaviour.

`backend/tests/test_service_discovery_search_response_contract.py` covers:

- valid empty and non-empty response envelopes;
- `provider_name` and `offering_name` contract;
- required metadata;
- non-negative result count;
- nested material-grade evidence;
- rejection of material grades as consumer criteria in query interpretation.

## 8. Required H5 policy decisions

1. A provider with confirmed family-level support but no confirmed requested part-type evidence must not automatically become a confirmed full part-type match. H5 must implement explicit unknown, partial-match or exclusion behaviour.

2. Tasowheel process criteria must not be inferred as matching from the legacy bundled process list, because H3 intentionally removed unscoped process evidence from the narrower harmonized offerings.

3. When a field is applicable through the selected part profile, such as `tolerance_mm` for gear or shaft, its scoped placement takes precedence over `generic_requirements`, preventing ambiguous matching input.

4. Generic quality request handling is implemented using the H1 registry's `quality_standard_and_class` input shape, while remaining distinct from the specialised `gear_quality` field.

## 9. Runtime verification responsibility

The repository owner ran focused H1 + H2 + H3 + H4 tests in the activated Django-enabled `.venv`.

Repository-owner focused H1 + H2 + H3 + H4 verification completed in the activated Django-enabled `.venv`.

Command executed:

```text
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract -v 2
```

Result:

```text
Ran 111 tests
OK
```

No claim is made that the full legacy project test suite passes at this checkpoint.

## Tasowheel amendment before H5 acceptance

The Tasowheel provider-confirmed evidence amendment does not change the general H4 taxonomy or canonical request shape.

The amended focused tests now exercise approved shaft fields already present in the H1 registry:

- `length_mm` and `outer_diameter_mm` in shaft family specifications;
- `spline_module` in `splined_shaft` part-type specifications.

No shaft-family `module`, `diametral_pitch`, `gear_quality`, `shaft_quality`, `spline_quality`, or shaft/spline diametral-pitch request field was added.

The controlled process vocabulary was extended additively for the newly confirmed Tasowheel process capability values, and H4 request tests verify those values can be submitted as consumer process requirements.

The inactive H4 response contract was extended to accept:

- `status.search_engine` for executed harmonized matcher responses;
- `match.optional_policy_satisfied` as a boolean result explanation field.

This extension supports transparent H5 local-matcher output only. The active legacy `/api/catalog/search` endpoint remains unchanged.

## 10. Focused verification command

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract -v 2
```

Do not run the full legacy test suite for this H4 checkpoint.

## 11. Issues before H5

No unclear registry input shape blocked H4.

Generic `quality` was implemented because H1 defines `quality` with `input_shape: quality_standard_and_class` and a note distinguishing it from `gear_quality`.

Repository-owner focused H1 + H2 + H3 + H4 runtime verification passed.

No out-of-scope file modification was made during H4.

## 12. Completion checklist

- [x] H3 focused verification result recorded.
- [x] New harmonized request serializer exists.
- [x] New canonical request object exists.
- [x] New normalizer exists.
- [x] New response contract serializer exists.
- [x] Single selected part type enforced.
- [x] All approved gear-family inputs are supported.
- [x] Registry-based field scoping enforced.
- [x] Scoped-versus-generic duplicate ambiguity rejected.
- [x] Consumer material grades rejected.
- [x] Strict unknown/forbidden field rejection enforced.
- [x] Active legacy search endpoint remains unchanged.
- [x] No matching/storage/RDF/SPARQL/Fuseki activation occurred.
- [x] H4 tests exist.
- [x] Repository owner ran focused H1 + H2 + H3 + H4 verification.
- [x] Ready for H5 review.
