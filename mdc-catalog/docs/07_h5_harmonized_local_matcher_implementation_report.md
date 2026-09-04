# MaaSAI MDC - H5 Harmonized Local Matcher Implementation Report

## 1. Status and scope

Phase: H5.

Purpose: inactive harmonized local matcher and explainable result construction.

The matcher reads only the parallel harmonized H3 YAML directory. Active `/api/catalog/search` remains unchanged. No RDF, SPARQL, Fuseki, or persistence activation occurred.

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

H1 + H2 + H3 + H4 focused tests:

```text
Ran 111 tests
OK
```

No claim is made that the full legacy project test suite passes.

## 3. Files created and modified

Created H5 files:

- `backend/apps/providers/service_discovery_loaders.py`
- `backend/apps/search/service_discovery_local_matcher.py`
- `backend/tests/test_service_discovery_provider_loader.py`
- `backend/tests/test_service_discovery_local_matcher.py`
- `backend/tests/test_service_discovery_local_search_response.py`
- `docs/07_h5_harmonized_local_matcher_implementation_report.md`

Updated existing file:

- `docs/06_h4_service_discovery_search_contract_implementation_report.md`

No out-of-scope implementation file was modified.

## 4. Harmonized provider loader

The loader defaults to:

```text
data/curated/service_discovery/providers/
```

It loads only `.yaml` and `.yml` files directly in that directory, in deterministic file-name order. It does not call or fall back to the legacy provider loader or `data/curated/providers/`.

It raises clear loader errors for a missing directory, invalid YAML, and a malformed non-dictionary root.

## 5. Matcher input and response output

Input is the H4 `CanonicalServiceDiscoverySearchRequest`.

Output is shaped for the H4 response contract, with external `provider_name` and `offering_name` mapped from internal harmonized `display_name` and `name`.

The matcher remains inactive at runtime. It is not connected to API views or routes.

Implementation note: the H4 response serializer currently accepts `status.search_executed` and `status.message` but not `status.search_engine`. H5 therefore emits an H4-compatible status object and records this as a contract limitation before endpoint activation.

## 6. Evidence-scope policy

Family-level confirmation is not subtype confirmation.

Candidate subtype evidence remains non-confirmed and is represented as unknown in matching.

Absent subtype evidence does not mean explicit unsupported; absence is treated as unknown unless a future negative-evidence model is added.

Tasowheel process evidence is not inferred and is not read from legacy YAML. Since H3 removed unscoped process claims from the narrower Tasowheel offerings, process requests for Tasowheel are unknown.

Material grades remain evidence only. Matching uses material-family identifiers and may return nested `available_grades` as evidence.

## 7. Capability matching semantics

Ranges and exact values use provider-envelope coverage:

- requested exact must fall inside provider min/max;
- requested min/max must be fully covered by provider min/max;
- missing comparable provider evidence is unknown.

`gear_quality` and generic `quality` use exact standard matching and class comparison. No conversion between standards is attempted.

`bounding_box_mm` evaluates supplied components and reports matched, partial, unmatched, or unknown based on component coverage.

Materials and processes use list coverage. Processes are evaluated only from harmonized offering `generic_capabilities.processes`.

Batch size matches when provider range covers the requested quantity.

Delivery matches when provider maximum lead time is less than or equal to consumer maximum weeks.

Certifications match provider-level and offering-level certification evidence by code.

Surface finish and tolerance compare maximum values where known.

Weight matches when provider maximum supported weight covers the requested weight.

## 8. Unknown policy, optional-match policy, score and ranking

`keep_as_unknown` retains candidates with unknown part-type or requirement evidence and explains unknowns.

`reject_unknown` excludes candidates with unknown requested part-type evidence or any unknown requested criterion.

`optional_match_mode` behaviour:

- `any`: satisfied when no criteria exist or at least one criterion matched or partially matched;
- `all`: satisfied only when all submitted criteria matched, or when no criteria exist;
- `score_only`: always satisfied for candidate-return purposes.

Optional policy alone does not remove comparison candidates. `unknown_policy` and `minimum_score` can remove candidates.

Scoring:

- confirmed requested part type: `selection_score = 1.0`;
- unknown or candidate requested part type: `selection_score = 0.5`;
- if no criteria are submitted, score equals selection score;
- otherwise score is `round((0.70 * selection_score) + (0.30 * optional_score), 3)`.

Statuses:

- `full_match`: confirmed requested part type and every submitted criterion matched;
- `unknown_match`: requested part type is unknown or candidate requiring confirmation;
- `partial_match`: confirmed requested part type with at least one partial, unmatched, or unknown criterion.

Results are sorted by score descending, confirmed subtype before unknown subtype on ties, then provider ID and offering ID.

`minimum_score` excludes results below the threshold.

## 9. Tests created

`backend/tests/test_service_discovery_provider_loader.py` covers default harmonized loading, deterministic order, internal shape, missing directory, invalid YAML, and non-dictionary root errors.

`backend/tests/test_service_discovery_local_matcher.py` covers:

- Precipart confirmed `spur_gear` full match;
- Tasowheel family-level `spur_gear` unknown match;
- `reject_unknown` exclusion;
- Precipart candidate `crown_gear`;
- family-level shaft subtype unknown behaviour;
- Tasowheel process request unknown behaviour;
- Tasowheel family technical evidence matching without promoting subtype support;
- tolerance not being satisfied by gear quality;
- material-grade evidence retention;
- minimum-score filtering;
- optional-match modes;
- confirmed synthetic subtype full match.

`backend/tests/test_service_discovery_local_search_response.py` covers H4 response-contract validation, external response names, H4-compatible inactive status, and selection explanations.

## Tasowheel provider-confirmed evidence and shaft-modelling amendment before H5 acceptance

The original H5 implementation report used the earlier family-only Tasowheel baseline. Before H5 runtime acceptance, that baseline was superseded by later Tasowheel confirmation of four gear part types, three shaft part types, shared generic capabilities, process capability evidence, material-grade evidence, and certifications.

Updated expected Tasowheel gear matching:

- `spur_gear`, `helical_gear`, `bevel_gear`, and `worm_gear` are confirmed subtype matches.
- With no additional criteria, those requests may return `full_match` with score `1.0`.
- `crown_gear` and `internal_gear` remain unconfirmed and must not be promoted.
- Gear family capabilities can match `module`, `diametral_pitch`, `outside_diameter_mm`, and `gear_quality`.
- `face_width_mm` remains unknown because no numeric value was supplied.
- General dimensional `tolerance_mm` remains unknown and is never satisfied from DIN4 gear-quality evidence.

Corrected Tasowheel shaft matching:

- `splined_shaft`, `plain_shaft`, and `hollow_shaft` are confirmed subtype matches.
- With no additional criteria, those requests may return `full_match` with score `1.0`.
- `stepped_shaft` and `worm_shaft` remain unconfirmed and are handled as unknown under `keep_as_unknown`.
- `length_mm.max = 500` is available with public-web provenance.
- `outer_diameter_mm = 10-450` is available with provider-confirmed provenance.
- `splined_shaft.spline_module = 0.3-10` is available only at `splined_shaft` subtype scope.
- Shaft DP evidence is deferred because there is no approved shaft/spline DP field.
- Shaft DIN4 searchable quality representation is deferred because there is no approved shaft/spline quality field.
- Shaft general dimensional tolerance remains unknown.

Process matching is now supported from amended harmonized offering evidence for both Tasowheel gear and shaft offerings. The matcher must read this only from `data/curated/service_discovery/providers/tasowheel.yaml`; it must not use legacy bundled process lists. Process evidence remains capability evidence, not route or sequence evidence.

Material matching uses the `alloyed_carburizing_steel` material-family identifier. Named grades `18CrNiMo7-6`, `16MnCr5`, and `20MnCr5` remain nested evidence only.

Provider-level certification matching can satisfy requests such as `ISO9001_2015`.

Successful H5 matcher responses now include:

- `status.search_executed: true`;
- `status.search_engine: local_harmonized_service_discovery_matcher`;
- per-result `match.optional_policy_satisfied`.

H5 runtime tests were later accepted after repository-owner focused verification; the final result is recorded below.

## Final focused verification and Tasowheel amendment acceptance

The repository owner accepted the amended Tasowheel shaft capability baseline:

- `tasowheel_precision_shafts.family_capabilities.length_mm.max = 500`

The repository owner completed focused amended H1 + H2 + H3 + H4 + H5 runtime verification in the activated Django-enabled `.venv`.

Result:

```text
Ran 148 tests in 0.971s

OK
```

This verification covers the harmonized H1-H5 scope, including the Tasowheel evidence and shaft-modelling amendment.

No claim is made that the full legacy project test suite passes at this checkpoint.

## 10. Required H6/H7 considerations

1. RDF generation must preserve the same evidence scopes established by H3 and H5; family-level data must not be emitted as confirmed subtype evidence.

2. RDF/SPARQL candidate retrieval must preserve unknown subtype candidates separately from confirmed subtype matches.

3. Tasowheel process evidence must appear in future RDF/SPARQL only from the amended scoped harmonized offering evidence, not from legacy bundled process lists.

4. Material grades may be projected as evidence but must not become consumer search criteria in the harmonized contract.

## 11. Runtime verification responsibility

The repository owner ran focused H1 + H2 + H3 + H4 + H5 tests in the activated Django-enabled `.venv`.

## 12. Focused verification command

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract tests.test_service_discovery_provider_loader tests.test_service_discovery_local_matcher tests.test_service_discovery_local_search_response -v 2
```

Do not run the full legacy test suite for this H5 checkpoint.

## 13. Issues before H6

The H4 response serializer was amended before H5 acceptance to accept `status.search_engine`, and H5 now emits `local_harmonized_service_discovery_matcher`.

No unclear YAML evidence structure blocked H5.

No out-of-scope file modification was made.

Focused runtime verification passed with the repository-owner result recorded above.

## 14. Completion checklist

- [x] H4 focused verification result recorded.
- [x] Harmonized provider loader exists.
- [x] Harmonized local matcher exists.
- [x] Matcher reads only parallel H3 YAML.
- [x] Family-level evidence is not promoted to confirmed subtype matching.
- [x] Candidate subtype evidence remains non-confirmed.
- [x] Tasowheel processes are matched only from amended scoped harmonized offering evidence; no legacy bundled process fallback is used.
- [x] Material grades remain evidence only.
- [x] Range/quality/material/batch/delivery/tolerance matching is implemented.
- [x] Unknown and optional policy behaviour is implemented.
- [x] Explainable response construction is implemented.
- [x] Active legacy endpoint remains unchanged.
- [x] No persistence/RDF/SPARQL/Fuseki activation occurred.
- [x] H5 tests exist.
- [x] Repository owner ran focused H1 + H2 + H3 + H4 + H5 verification.
- [x] Ready for H6 review.
