# MaaSAI MDC — Tasowheel Provider-Confirmed Evidence and Shaft-Modelling Amendment Across H1–H5

## 1. Amendment reason and status

This amendment occurs before H5 acceptance and before H6 begins.

New Tasowheel evidence supersedes only the affected earlier conservative assumptions about Tasowheel part-type support, scoped processes, and shaft capability modelling.

Earlier H-phase reports remain historical records. Superseding amendment sections were added where needed rather than deleting prior history.

H6 has not started. No RDF, SPARQL, Fuseki, persistence, active API endpoint, or legacy matcher integration work was performed.

## 2. Supplied Tasowheel evidence

Confirmed precision-gear part types:

| Supplied/approved capability | Harmonized identifier |
| --- | --- |
| Spur gears | `spur_gear` |
| Helical gears | `helical_gear` |
| Bevel gears | `bevel_gear` |
| Worm gears | `worm_gear` |

`crown_gear` and `internal_gear` were not added.

Confirmed precision-shaft part types:

| Supplied wording | Harmonized identifier |
| --- | --- |
| Splined shafts | `splined_shaft` |
| Plain shafts | `plain_shaft` |
| Hollow shafts | `hollow_shaft` |

`stepped_shaft` and `worm_shaft` were not added.

Capability values:

| Evidence | Harmonized representation |
| --- | --- |
| Face width: no known numeric value | omitted; remains unknown |
| Batch sizes: 100-2000 pcs | `batch_size.min = 100`, `batch_size.max = 2000` |
| Module range: 0.3-10 | gear `module`; shaft `splined_shaft.spline_module` only |
| DP 85-2.5 | gear `diametral_pitch.min = 2.5`, `max = 85`, raw preserved |
| Diameter range: 10-450 mm | gear `outside_diameter_mm`; shaft `outer_diameter_mm` |
| Quality up to DIN4 | gear `gear_quality`; shaft searchable quality deferred |
| Weights up to approximately 200 kg | `weight_kg.max = 200`, approximate |
| Delivery time: 8-12 weeks | `lead_time_weeks.min = 8`, `max = 12` |
| Shafts up to 500 mm length | shaft `length_mm.max = 500`, public-web provenance |

Certifications retained:

- `ISO9001_2015`
- `ISO_TS_16949_partial`
- `APQP`
- `ISO14001_2015`

Materials retained:

- `alloyed_carburizing_steel`
- named grades `18CrNiMo7-6`, `16MnCr5`, and `20MnCr5`

The source note records that additional commonly used alloyed carburizing steels are supported, but individual additional grades are not enumerated.

Process evidence applying to Tasowheel gears and shafts:

| Supplied wording | Controlled identifier |
| --- | --- |
| Machining | `machining` |
| Hobbing | `hobbing` |
| Shaping | `gear_shaping` |
| Deburring | `deburring` |
| Hard Turning | `hard_turning` |
| Grinding | `grinding` |
| Tooth Grinding | `tooth_grinding` |
| Gear Grinding | `gear_grinding` |
| Gear Cutting | `gear_cutting` |
| Surface Grinding | `surface_grinding` |
| Milling | `milling` |
| Turn-Mill | `turn_mill` |

These are offering-level supported process capability records for both Tasowheel `precision_gears` and `precision_shafts`. They are not operation routes, mandatory sequences, machine selections, or proof that every ordered part uses every listed process.

## 3. Controlled normalization decisions

- `splined_shafts` -> `splined_shaft`.
- `Shaping` -> `gear_shaping`.
- `Turn-Mill` -> `turn_mill`.
- `DP 85-2.5` -> raw value preserved; normalized numeric gear range `2.5` to `85`.
- Diameter `10-450` -> `outside_diameter_mm` for gears; `outer_diameter_mm` for shafts.
- DIN4 -> `gear_quality` for gears only; never converted to `tolerance_mm`.
- Shaft module evidence -> `splined_shaft.spline_module` only.
- Shaft DP evidence -> deferred because no approved shaft/spline DP field exists.
- Shaft DIN4 searchable representation -> deferred because no approved shaft/spline quality field exists.
- Shaft length up to 500 mm -> represented with public-web provenance because the value was identified as public-provider-page evidence rather than inspected declared questionnaire evidence.

## 4. Files modified

H1 amendment:

- `backend/apps/ontology/vocabularies.py`: added missing controlled process identifiers.
- `backend/tests/test_api_v1.py`: verified additive process exposure while preserving existing filter keys.

H2 amendment:

- `backend/tests/test_service_discovery_publication_serializer.py`: added updated Tasowheel publication validation coverage.
- `backend/tests/test_service_discovery_publication_normalizer.py`: added preservation coverage for shaft length, splined-shaft module, and process evidence.

H3 amendment:

- `data/curated/service_discovery/providers/tasowheel.yaml`: updated harmonized inactive Tasowheel evidence.
- `backend/tests/test_service_discovery_provider_yaml_migration.py`: updated external fixture -> serializer -> normalizer -> YAML equality path and evidence assertions.
- `docs/05_h3_harmonized_provider_yaml_migration_report.md`: added superseding Tasowheel evidence amendment section.

H4 amendment:

- `backend/apps/api/service_discovery_search_serializers.py`: extended inactive response contract for `status.search_engine` and boolean `match.optional_policy_satisfied`.
- `backend/tests/test_service_discovery_search_serializer.py`: added shaft-field and updated-process request validation coverage.
- `backend/tests/test_service_discovery_search_response_contract.py`: added response metadata and optional-policy explanation validation.
- `docs/06_h4_service_discovery_search_contract_implementation_report.md`: added amendment note.

H5 amendment:

- `backend/apps/search/service_discovery_local_matcher.py`: added `status.search_engine` to harmonized matcher output.
- `backend/tests/test_service_discovery_local_matcher.py`: updated Tasowheel matcher expectations for confirmed part types, shaft modelling, process matching, material evidence, certifications, unknowns, score, and optional policy.
- `backend/tests/test_service_discovery_local_search_response.py`: updated response assertions for `search_engine` and `optional_policy_satisfied`.
- `docs/07_h5_harmonized_local_matcher_implementation_report.md`: added superseding Tasowheel evidence and shaft-modelling amendment section.

New amendment report:

- `docs/08_tasowheel_evidence_amendment_h1_h5_report.md`

## 5. H3 data amendment outcome

The updated harmonized Tasowheel YAML keeps exactly two offerings:

- `tasowheel_precision_gears`
- `tasowheel_precision_shafts`

No `tasowheel_precision_metal_parts` offering was created.

`tasowheel_precision_gears` confirms exactly `spur_gear`, `helical_gear`, `bevel_gear`, and `worm_gear`.

`tasowheel_precision_shafts` confirms exactly `splined_shaft`, `plain_shaft`, and `hollow_shaft`.

Gear capability evidence remains scoped to gear family fields. Shaft capability evidence remains scoped to approved shaft family fields and splined-shaft subtype fields.

Processes are represented as offering capability records with `delivery_mode: unspecified`, not routes or sequences.

Materials, named grades, and provider-level certifications were retained.

## 6. H4 contract compatibility amendments

The controlled process vocabulary was extended with:

- `deburring`
- `tooth_grinding`
- `gear_cutting`
- `surface_grinding`
- `turn_mill`

Already-present approved values were retained:

- `machining`
- `hobbing`
- `gear_shaping`
- `hard_turning`
- `grinding`
- `gear_grinding`
- `milling`

H4 request tests now exercise `length_mm`, `outer_diameter_mm`, and `splined_shaft.spline_module`.

No shaft DP or shaft-quality field was added.

The response contract was extended additively so H5 can return `status.search_engine` and per-result `match.optional_policy_satisfied`.

## 7. H5 matcher-expectation amendments

Tasowheel confirmed gear subtype requests may now produce `full_match` with score `1.0` when no requested criteria are unknown or unmatched.

Tasowheel confirmed shaft subtype requests may now produce `full_match` with score `1.0` when no requested criteria are unknown or unmatched.

Unconfirmed `crown_gear`, `internal_gear`, `stepped_shaft`, and `worm_shaft` remain unconfirmed. Absence remains unknown rather than explicit unsupported evidence.

Shaft `length_mm` and `outer_diameter_mm` can match from shaft family capability evidence. `splined_shaft.spline_module` can match from subtype-scoped evidence.

Face width remains unknown. General dimensional tolerance remains unknown and is not satisfied by DIN4.

Shaft DP and shaft DIN4 searchable-quality representation are deferred.

Process requests can now match Tasowheel offerings from harmonized H3 YAML process capability evidence. The matcher must not read legacy bundled process lists.

Material matching uses `alloyed_carburizing_steel`; named grades remain nested evidence only.

Provider-level certification matching can satisfy requests such as `ISO9001_2015`.

Successful matcher output includes `status.search_executed: true`, `status.search_engine: local_harmonized_service_discovery_matcher`, and `match.optional_policy_satisfied`.

## 8. Test files amended

- `backend/tests/test_api_v1.py`: additive process vocabulary exposure.
- `backend/tests/test_service_discovery_publication_serializer.py`: updated Tasowheel publication validation.
- `backend/tests/test_service_discovery_publication_normalizer.py`: updated evidence normalization preservation.
- `backend/tests/test_service_discovery_provider_yaml_migration.py`: updated Tasowheel YAML equality and evidence assertions.
- `backend/tests/test_service_discovery_search_serializer.py`: shaft field and new process request validation.
- `backend/tests/test_service_discovery_search_response_contract.py`: response `search_engine` and `optional_policy_satisfied` validation.
- `backend/tests/test_service_discovery_local_matcher.py`: updated H5 Tasowheel matching expectations.
- `backend/tests/test_service_discovery_local_search_response.py`: H5 execution metadata and optional-policy response assertions.

## 9. Runtime verification responsibility

The repository owner will run focused amended H1 + H2 + H3 + H4 + H5 tests in the activated Django-enabled `.venv`. The full legacy test suite is not required at this H-phase checkpoint.

## 10. Focused verification command

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract tests.test_service_discovery_provider_loader tests.test_service_discovery_local_matcher tests.test_service_discovery_local_search_response -v 2
```

## 11. Issues before H6

- Shaft DP evidence is known from the supplied update but is deferred because no approved shaft/spline DP field exists.
- Shaft DIN4-capable evidence is known but searchable shaft/spline quality representation is deferred because no approved `shaft_quality` or `spline_quality` field exists.
- `deburring`, `tooth_grinding`, `gear_cutting`, `surface_grinding`, and `turn_mill` required additive controlled vocabulary extension.
- The H4 response contract was extended for H5 execution metadata and optional-policy explanation.
- Repository-owner focused amended H1-H5 tests passed with the result recorded below.

## Final acceptance and focused verification result

The repository owner accepted the following harmonized Tasowheel shaft capability for the amended evidence baseline:

- `tasowheel_precision_shafts.family_capabilities.length_mm.max = 500`

This acceptance confirms that the amended shaft offering may represent a maximum supported shaft length of 500 mm in the harmonized Tasowheel evidence baseline.

The repository owner then executed the focused amended H1 + H2 + H3 + H4 + H5 verification in the activated Django-enabled `.venv`.

Result:

```text
Ran 148 tests in 0.971s

OK
```

No claim is made that the full legacy project test suite passes at this checkpoint.

Following this focused verification, the Tasowheel H1-H5 amendment is accepted and H6 may begin.

## 12. Completion checklist

- [x] New Tasowheel evidence recorded.
- [x] Confirmed Tasowheel gear part types represented.
- [x] Confirmed Tasowheel shaft part types represented.
- [x] No unsupported Tasowheel metal-parts offering created.
- [x] No unsupported `crown_gear`, `internal_gear`, `stepped_shaft` or `worm_shaft` confirmation added.
- [x] Gear/shaft diameter terminology preserved.
- [x] Shaft length evidence represented with correct provenance.
- [x] Shaft length capability accepted for the harmonized Tasowheel baseline.
- [x] Splined-shaft module evidence represented only at subtype scope.
- [x] Shaft DP deferral documented.
- [x] Shaft DIN4 searchable-quality deferral documented.
- [x] DIN4 not converted into dimensional tolerance.
- [x] Face-width unknown preserved.
- [x] Processes represented as offering capabilities, not routes.
- [x] Materials and named grades preserved as evidence.
- [x] Certifications retained.
- [x] Affected H1-H5 tests amended.
- [x] H5 execution metadata and optional-policy explanation verified.
- [x] Repository owner ran focused amended H1 + H2 + H3 + H4 + H5 tests.
- [x] Ready for H6 review.
