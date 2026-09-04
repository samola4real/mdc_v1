# MaaSAI MDC — H2 Service Discovery Publication Contract Implementation Report

## 1. Status and scope

Phase: H2.

Purpose: additive harmonized provider-publication contract and deterministic internal offering-ID generation.

The new contract is not wired to an API endpoint in H2. The active legacy `POST /api/provider-publication` endpoint remains unchanged.

No provider YAML migration occurs in H2.

No RDF, SPARQL, or Fuseki changes occur in H2.

## 2. H1 verified prerequisite

Repository-owner supplied H1 focused verification:

```text
python manage.py test tests.test_service_discovery_registry -v 2
Found 8 tests. Ran 8 tests. OK.

python manage.py test tests.test_api_v1 -v 2
Found 4 tests. Ran 4 tests. OK.

Total H1-focused tests passed: 12.
```

This report does not state that the full legacy test suite passed.

## 3. Files created and modified

Files created:

- `backend/apps/api/service_discovery_publication_serializers.py`
- `backend/apps/providers/service_discovery_publication.py`
- `backend/tests/test_service_discovery_publication_serializer.py`
- `backend/tests/test_service_discovery_publication_normalizer.py`
- `docs/04_h2_service_discovery_publication_contract_implementation_report.md`

Existing files modified: none.

Any existing-file modification during H2 would be an issue. No existing implementation file, legacy test file, provider YAML, generated data, route, view, serializer, normalizer, repository, RDF, SPARQL, Fuseki, settings, requirement, or Docker file was modified.

## 4. Implemented external contract

Required external provider fields:

- `provider_id`
- `provider_name`
- `country`
- `offerings`

Optional external provider fields:

- `certifications`
- `publication_metadata`

Offering structure:

- `service_category`
- `offering_name`
- `part_family`
- `support_status`
- `supported_part_types`
- `family_capabilities`
- `part_type_capabilities`
- `generic_capabilities`

Supported `support_status` values:

- `confirmed`
- `candidate_requiring_confirmation`
- `unknown`

Allowed evidence values:

- `source_type`: `provider_confirmed`, `public_web`, `curated`, `not_confirmed`
- `confidence`: `declared`, `publicly_confirmed`, `curated`, `inferred`, `unknown`
- optional `source_note`

Identifier fields intentionally not accepted externally:

- `offering_id`
- `facility_id`
- `material_id`
- `grade_id`

The external field `display_name` is not accepted; the harmonized contract uses `provider_name`.

Controlled validation uses the H1 `service_discovery` registry:

- `precision_gears` requires `gear`
- `precision_shafts` requires `shaft`
- `precision_metal_parts` requires `metal_part`

Submitted part types must belong to the selected part family, duplicate service categories are rejected, and duplicate supported part types within an offering are rejected.

## 5. Internal offering-ID generation and normalization

ID generation formula:

```python
f"{provider_id}_{service_category}"
```

Examples:

- `tasowheel` + `precision_gears` -> `tasowheel_precision_gears`
- `tasowheel` + `precision_shafts` -> `tasowheel_precision_shafts`
- `precipart` + `precision_metal_parts` -> `precipart_precision_metal_parts`

Normalization is in memory only.

External `provider_name` maps to internal `provider.display_name`.

External `offering_name` maps to internal offering `name`.

Each normalized offering includes generated `offering_id`, `provider_id`, `service_category`, `name`, `part_family`, support/evidence blocks, and capability blocks.

The H2 normalizer does not write YAML and does not insert legacy `service_type`.

## 6. Capability scoping rules

Gear family capability fields:

- `module`
- `diametral_pitch`
- `number_of_teeth`
- `outside_diameter_mm`
- `gear_quality`
- `tolerance_mm`

Gear family capabilities reject `diameter_mm` and `outer_diameter_mm`.

Shaft family capability fields:

- `length_mm`
- `outer_diameter_mm`
- `tolerance_mm`

Shaft family capabilities reject gear `outside_diameter_mm`.

Metal-part rule for H2:

- `precision_metal_parts` family capabilities must be empty.
- Metal-part dimensional evidence is scoped under `part_type_capabilities` for confirmed part types.

Part-type capabilities:

- Keys must correspond to a submitted supported part type.
- The part type must be `confirmed`.
- Allowed fields are inherited `family_common_fields` plus `part_type_specific_fields` from the H1 registry.

Material-grade evidence treatment:

- Material grade strings are allowed only under `materials[].available_grades`.
- Grade strings are not constrained to the legacy public `MATERIAL_GRADES` filter vocabulary.
- `material_id` and `grade_id` are rejected.

Route, machine, price, and availability fields are rejected recursively using the existing `FORBIDDEN_ROUTE_KEYS` policy.

## 7. Tests created

`backend/tests/test_service_discovery_publication_serializer.py` covers:

- valid family-level `precision_gears`;
- valid `precision_gears` plus `precision_shafts`;
- valid confirmed `bracket`;
- `provider_id` lower_snake_case / identifier-safe validation;
- `provider_name` acceptance and `display_name` rejection;
- `publication_metadata` acceptance, defaulting, and invalid-value rejection;
- external ID ownership rejections;
- duplicate category/type rejection;
- category/family/type taxonomy validation;
- gear, shaft, and metal-part capability scope;
- candidate part-type capability rejection;
- material grade evidence strings including `42CrMo4`;
- material/process/delivery-mode validation;
- numeric positivity and range validation;
- recursive forbidden route/machine/price rejection.

`backend/tests/test_service_discovery_publication_normalizer.py` covers:

- deterministic `generate_offering_id()`;
- `provider_name` to `display_name`;
- two generated offering IDs;
- normalized offering `provider_id`;
- `offering_name` to `name`;
- preservation of service category, part family, support status, evidence, and capabilities;
- preservation of material grade evidence;
- preservation of supplied `publication_metadata`;
- preservation of defaulted `publication_metadata`;
- no YAML output shape;
- no automatic legacy `service_type`.

## 8. Runtime verification responsibility

Codex did not run Django tests. The repository owner ran focused H1 + H2 tests in the activated Django-enabled `.venv`.

A syntax-only `python -m py_compile` check was run for the newly created H2 Python/test files and passed. This is not a substitute for Django runtime verification.

Repository-owner focused H1 + H2 verification completed in the activated Django-enabled `.venv`.

Command executed:

```text
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer -v 2
```

Result:

```text
Ran 56 tests in 0.051s
OK
```

No claim is made that the full legacy project test suite passes at this checkpoint.

## 9. Focused verification commands for repository owner

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer -v 2
```

## 10. Issues before H3

No implementation issue was found that required modifying legacy files.

Repository-owner focused H1 + H2 verification has passed. H3 may proceed without claiming full legacy suite success.

## 11. Completion checklist

- [x] New harmonized publication serializer exists.
- [x] Internal offering-ID generator exists.
- [x] In-memory publication normalizer exists.
- [x] Existing active provider-publication endpoint remains unchanged.
- [x] Existing provider YAML remains unchanged.
- [x] H2 tests exist.
- [x] H1 focused tests were previously confirmed by repository owner.
- [x] Repository owner has run focused H1 + H2 verification after H2.
- [x] Ready for H3 review.
