# MaaSAI MDC - H3 Harmonized Provider YAML Migration Report

## 1. Status and scope

Phase: H3.

Purpose: create parallel harmonized normalized provider YAML records.

Legacy provider YAML remains active and unchanged. The new harmonized YAML is not yet loaded by current API, matcher, RDF, SPARQL, or Fuseki paths.

No full legacy test-suite claim is made.

## 2. Verified H1 and H2 prerequisite tests

H1 focused tests passed: 12.

H1 + H2 focused command:

```text
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer -v 2
```

Result:

```text
Ran 56 tests in 0.051s
OK
```

Repository-owner focused H1 + H2 + H3 verification completed in the activated Django-enabled `.venv`.

Command executed:

```text
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration -v 2
```

Result:

```text
Ran 71 tests in 0.154s
OK
```

No claim is made that the full legacy project test suite passes at this checkpoint.

## 3. Source files inspected

- `docs/01_mdc_current_codebase_implementation_inventory.md`: current implementation baseline.
- `docs/02_mdc_harmonized_service_discovery_decisions.md`: H0/H1 taxonomy and migration decisions.
- `docs/03_h1_service_discovery_registry_implementation_report.md`: H1 registry status.
- `docs/04_h2_service_discovery_publication_contract_implementation_report.md`: H2 publication contract status.
- `backend/apps/ontology/service_discovery_registry.py`: approved taxonomy and field profiles.
- `backend/apps/api/service_discovery_publication_serializers.py`: H2 validation contract.
- `backend/apps/providers/service_discovery_publication.py`: H2 internal normalization and offering-ID generation.
- `backend/tests/test_service_discovery_publication_serializer.py`: H2 serializer fixture patterns.
- `backend/tests/test_service_discovery_publication_normalizer.py`: H2 normalizer fixture patterns.
- `data/curated/providers/tasowheel.yaml`: source for confirmed Tasowheel family-level gear and shaft evidence.
- `data/curated/providers/demo_machining_provider.yaml`: source for demo machining provider assessment.
- `data/curated/providers/demo_heat_treatment_provider.yaml`: source for heat-treatment-only assessment.
- `data/curated/providers/precipart.yaml`: local Precipart source was present and inspected.

## 4. Files created and modified

New harmonized provider YAML files:

- `data/curated/service_discovery/providers/tasowheel.yaml`
- `data/curated/service_discovery/providers/demo_machining_provider.yaml`
- `data/curated/service_discovery/providers/precipart.yaml`

New H3 test file:

- `backend/tests/test_service_discovery_provider_yaml_migration.py`

New report file:

- `docs/05_h3_harmonized_provider_yaml_migration_report.md`

Updated existing report:

- `docs/04_h2_service_discovery_publication_contract_implementation_report.md`

No legacy provider YAML was modified. No implementation Python module was modified. No RDF, SPARQL, or Fuseki file was modified.

## 5. Harmonized data-location decision

H3 creates a new parallel inactive harmonized-data directory:

```text
data/curated/service_discovery/providers/
```

Current legacy runtime continues to read `data/curated/providers/`. Later phases will decide activation and migration into API, matcher, RDF, and Fuseki paths.

## 6. Tasowheel migration

Legacy offering observed:

```text
tasowheel_gears_shafts_precision
```

New harmonized offerings created:

- `tasowheel_precision_gears`
- `tasowheel_precision_shafts`

`tasowheel_precision_metal_parts` was not created because the inspected source confirms broad gear and shaft capability, not the approved `precision_metal_parts` category.

No Tasowheel part subtype was asserted. Both harmonized Tasowheel offerings keep:

```text
supported_part_types: []
part_type_capabilities: {}
```

Capabilities migrated to gears:

- `module`: `0.3-10`
- `diametral_pitch`: `2.5-85`, preserving raw `DP 85-2.5`
- `outside_diameter_mm`: `10-450`, mapped from legacy `diameter_mm`
- `gear_quality`: DIN best class `4`

Capabilities migrated to shafts:

- `outer_diameter_mm`: `10-450`, mapped from legacy `diameter_mm`

Shared generic evidence migrated conservatively:

- alloyed carburizing steel material evidence;
- material grades `18CrNiMo7-6`, `16MnCr5`, and `20MnCr5` nested only under `materials[].available_grades`;
- provider-level certifications `ISO9001_2015`, `ISO14001_2015`, `ISO_TS_16949_partial`, and `APQP`;
- batch size `100-2000 pcs`;
- normal lead time `8-12 weeks`, case dependent;
- approximate weight up to `200 kg`;
- surface finish represented as explicit unknown evidence.

Process and heat-treatment handling:

- The inspected legacy source attaches processes only to the bundled `tasowheel_gears_shafts_precision` offering.
- H3 does not retain those process claims on the narrower `tasowheel_precision_gears` or `tasowheel_precision_shafts` offerings because the source does not explicitly scope individual processes to the new narrower offerings.
- Heat treatment is therefore not published in the H3 Tasowheel harmonized YAML. The source note that heat treatment is subcontracting-related remains a future migration consideration, but it is not turned into a confirmed narrower-offering process claim in H3.
- Routes and process sequence are not published.

Unknown or omitted data:

- No confirmed general dimensional `tolerance_mm` value was added.
- DIN4 remains `gear_quality`, not a general tolerance.
- Traceability values beyond certification evidence were omitted.

Future H6 material concept observation:

- The inspected legacy Tasowheel source maps `alloyed_carburizing_steel` to `mdc:Steel`. This should be reviewed in H6 before RDF extension, because a future more specific concept such as `mdc:AlloyedCarburizingSteel` may be appropriate. No RDF or ontology code was changed in H3.

## 7. Demo-provider migration assessment

Demo machining provider:

- Harmonized YAML was created for `precision_shafts`.
- The source explicitly lists `shaft` in the legacy `part_families`, so broad shaft support can be mapped without asserting subtypes.
- No `plain_shaft`, `stepped_shaft`, `block`, `bracket`, or other subtype was inferred.
- Legacy `diameter_mm` was mapped to shaft `outer_diameter_mm`.

Demo heat-treatment provider:

- No harmonized YAML was created.
- The source is a heat-treatment service. A heat-treatment-only offering is not automatically one of the three approved manufacturing categories: `precision_gears`, `precision_shafts`, or `precision_metal_parts`.
- It requires a future taxonomy decision for process-only or post-processing services.

## 8. Precipart migration assessment

Local Precipart source YAML was found at:

```text
data/curated/providers/precipart.yaml
```

Migrated offering:

- `precipart_precision_gears`

Evidence discipline retained:

- `spur_gear`, `helical_gear`, and `worm_gear` were mapped as confirmed because the source lists those exact approved part types.
- `crown_gear` was kept as `candidate_requiring_confirmation` because the source records it through `candidate_mapping_requiring_confirmation` from `face_gear`.
- `internal_gear`, rack, sector, planetary, and specific bevel variants were not mapped because they are outside or more specific than the approved H1 part-type identifiers.
- No material-offering association was invented from provider-level supported material families.
- Certification strings were not migrated because the source values do not directly match the current controlled certification-code vocabulary.

Deferred Precipart data:

- The custom turned and milled metal-part offerings were not migrated because the source describes process envelopes and candidate part types, not confirmed approved H1 metal-part subtype support with capability claims.

## 9. Validation method

Each created harmonized YAML is tested by:

```text
external fixture
-> ServiceDiscoveryPublicationSerializer
-> normalize_service_discovery_publication()
-> equality with loaded harmonized YAML
```

This proves the YAML records correspond to the H2 contract and normalizer rather than manually drifting from them.

## 10. Tests created

`backend/tests/test_service_discovery_provider_yaml_migration.py` verifies:

- harmonized Tasowheel YAML exists;
- Tasowheel external fixture validates through the H2 serializer;
- Tasowheel loaded YAML exactly equals H2-normalized fixture output;
- Tasowheel offering IDs are `tasowheel_precision_gears` and `tasowheel_precision_shafts`;
- Tasowheel legacy bundled and unsupported metal-part offering IDs are absent;
- Tasowheel gear offering uses `outside_diameter_mm` and avoids `diameter_mm` and `outer_diameter_mm`;
- Tasowheel shaft offering uses `outer_diameter_mm` and avoids gear capability fields;
- Tasowheel does not promote unconfirmed subtypes;
- Tasowheel contains no route, machine, or price fields;
- material grades are nested only under material evidence;
- Tasowheel bundled process claims are deferred from the narrower gear and shaft offerings;
- demo machining provider YAML equals H2-normalized fixture output;
- demo machining maps only to broad `precision_shafts`;
- Precipart YAML equals H2-normalized fixture output;
- Precipart keeps `crown_gear` as candidate requiring confirmation;
- H3 data directory is separate from the legacy provider directory.

## Evidence-integrity audit before H3 runtime verification

Tasowheel process-scoping outcome:

- The legacy Tasowheel source lists processes only on the old bundled `tasowheel_gears_shafts_precision` offering.
- The source does not explicitly scope `machining`, `turning`, `milling`, `hobbing`, `gear_shaping`, `hard_turning`, `grinding`, `gear_grinding`, `heat_treatment`, or `inspection` separately to `tasowheel_precision_gears` or `tasowheel_precision_shafts`.
- H3 therefore removed `generic_capabilities.processes` from both narrower harmonized Tasowheel offerings.
- No Tasowheel process claims were retained in H3 harmonized YAML.
- Heat treatment is not published in H3. It is not marked `in_house`, and no route sequence is published.

Precipart evidence metadata outcome:

- The migrated `precipart_precision_gears` offering remains `support_status: confirmed` based on public source data, not provider-confirmed questionnaire evidence.
- `spur_gear`, `helical_gear`, and `worm_gear` use `support_status: confirmed`, `source_type: public_web`, and `confidence: publicly_confirmed`.
- `crown_gear` remains `support_status: candidate_requiring_confirmation`, `source_type: public_web`, and `confidence: inferred`, with a note that the source maps it from `face_gear` as requiring confirmation.
- No Precipart migrated part type uses `source_type: provider_confirmed` or `confidence: declared`.

Tasowheel certification-retention outcome:

- The inspected source contains `ISO9001_2015`, `ISO14001_2015`, `ISO_TS_16949_partial`, and `APQP` as provider-confirmed declared certifications.
- All four certification codes are accepted by the current H2 schema and controlled vocabulary.
- All four are retained in `data/curated/service_discovery/providers/tasowheel.yaml` under `provider.certifications` with `source_type: provider_confirmed` and `confidence: declared`.
- No Tasowheel certification was omitted or converted.

Files changed during this audit:

- `data/curated/service_discovery/providers/tasowheel.yaml`
- `backend/tests/test_service_discovery_provider_yaml_migration.py`
- `docs/05_h3_harmonized_provider_yaml_migration_report.md`

`data/curated/service_discovery/providers/precipart.yaml` was inspected and did not require changes.

Focused H1 + H2 + H3 runtime verification was pending immediately after this audit and was later completed by the repository owner with the result recorded above.

Evidence-integrity audit outcome after repository-owner focused verification:

- Tasowheel unscoped process claims were removed from both narrower harmonized offerings.
- Precipart evidence remains public-source evidence and was not promoted to provider-confirmed evidence.
- Tasowheel certification evidence was retained.

## Tasowheel provider-confirmed evidence amendment after initial H3 migration

The earlier removal of Tasowheel process evidence was correct under the earlier local source baseline, where processes existed only on the legacy bundled `tasowheel_gears_shafts_precision` offering and were not explicitly scoped to the narrower harmonized gear and shaft offerings.

That H3 baseline is superseded by a later repository-owner Tasowheel update confirming that specific part types, shared generic capabilities, and the listed process capabilities apply to the gears and shafts Tasowheel produces.

Updated `tasowheel_precision_gears` now confirms exactly these part types:

- `spur_gear`
- `helical_gear`
- `bevel_gear`
- `worm_gear`

No `crown_gear` or `internal_gear` support is added.

Updated `tasowheel_precision_shafts` now confirms exactly these part types:

- `splined_shaft`
- `plain_shaft`
- `hollow_shaft`

No `stepped_shaft` or `worm_shaft` support is added.

Gear capability mapping:

- `module`: `0.3` to `10`, provider-confirmed declared evidence.
- `diametral_pitch`: `2.5` to `85`, with raw value `DP 85-2.5` preserved.
- `outside_diameter_mm`: `10` to `450`, using gear outside-diameter terminology.
- `gear_quality`: DIN best class `4`, with lower-or-equal-is-better comparison.
- No confirmed `tolerance_mm` is published; DIN4 remains gear-quality evidence only.
- No numeric `face_width_mm` or other gear part-type-specific dimensions are published.

Corrected shaft modelling:

- `length_mm.max = 500` is represented on the shaft family capability with `source_type: public_web` and `confidence: publicly_confirmed`, because the length value is from public provider-page evidence rather than the inspected declared questionnaire source.
- `outer_diameter_mm` is represented as `10` to `450` with provider-confirmed declared evidence.
- `splined_shaft.spline_module` is represented at splined-shaft subtype scope only, with range `0.3` to `10`.
- `module`, `diametral_pitch`, and `gear_quality` are not published as shaft-family capabilities.
- Shaft DP evidence is deferred because the current registry has no approved shaft/spline diametral-pitch field.
- Shaft DIN4 searchable quality representation is deferred because the current registry has no approved `shaft_quality` or `spline_quality` field.
- General dimensional `tolerance_mm` remains unknown and is not inferred from DIN4.

Shared generic capabilities now represented on both Tasowheel harmonized offerings:

- `materials` with material family `alloyed_carburizing_steel` and named grades `18CrNiMo7-6`, `16MnCr5`, and `20MnCr5`.
- `processes` with `machining`, `hobbing`, `gear_shaping`, `deburring`, `hard_turning`, `grinding`, `tooth_grinding`, `gear_grinding`, `gear_cutting`, `surface_grinding`, `milling`, and `turn_mill`, all with `delivery_mode: unspecified`.
- `batch_size`: `100` to `2000` pcs.
- `lead_time_weeks`: `8` to `12`, normal/case-dependent.
- `weight_kg.max = 200`, approximate.

The process records are offering-level capability evidence. They are not routes, mandatory operation sequences, machine selections, or proof that every ordered part uses every listed process.

No `tasowheel_precision_metal_parts` offering was created.

## 11. Runtime verification responsibility

The repository owner will run focused H1 + H2 + H3 tests in the activated Django-enabled `.venv`.

## 12. Focused verification command for repository owner

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration -v 2
```

Do not run the full legacy test suite for this H3 checkpoint.

## 13. Issues before H4

- Demo heat-treatment provider was deferred pending a future process-only or post-processing taxonomy decision.
- Precipart metal-part offerings were deferred because the local source contains candidate/process-envelope evidence rather than confirmed approved H1 metal-part subtype claims.
- Precipart certification strings need future controlled-code mapping before publication as H2 certification evidence.
- Tasowheel `alloyed_carburizing_steel` currently maps to generic `mdc:Steel` in the legacy source; review in H6 RDF/mapping work.
- Repository-owner focused H1 + H2 + H3 runtime verification passed after the evidence-integrity correction.

No out-of-scope modification was made during H3.

## 14. Completion checklist

- [x] Parallel harmonized provider directory exists.
- [x] Tasowheel harmonized YAML exists.
- [x] Tasowheel legacy bundled offering is mapped in the report only.
- [x] Tasowheel precision-gears offering exists.
- [x] Tasowheel precision-shafts offering exists.
- [x] No unsupported Tasowheel precision-metal-parts offering was invented.
- [x] No unconfirmed part subtype was promoted to confirmed capability.
- [x] Conditional provider migrations are evidence-grounded or deferred.
- [x] Legacy provider YAML remains unchanged.
- [x] No runtime loader/API/matcher/RDF/SPARQL/Fuseki activation occurred.
- [x] H3 focused tests exist.
- [x] Repository owner ran focused H1 + H2 + H3 verification.
- [x] Ready for H4 review.
