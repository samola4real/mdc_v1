# MaaSAI MDC — H1 Service Discovery Registry Diagnostic and Repair Report

## 1. Status and purpose

Phase: H1.

Status: diagnostic/repair review after repository-owner test failures.

Purpose: record actual H1 changes, failure classification, controlled repairs, and pending final verification.

Codex does not own final Django test execution unless a Django-enabled environment is explicitly available. The repository owner owns the final `python manage.py check` and `python manage.py test` rerun in the activated project `.venv`.

## 2. User-supplied test outcome before repair

The prompt reported:

- 134 tests discovered.
- Some tests skipped.
- Multiple tests failed.
- The result was observed by the repository owner from the Django-enabled `.venv`.

The exact terminal output was not supplied; the prompt still contained the placeholder:

```text
<PASTE THE EXACT OUTPUT FROM python manage.py test HERE, INCLUDING ALL FAILURES, ERRORS AND SKIPS>
```

Because the exact failure output was not supplied, specific affected tests, tracebacks, failure counts, and skip counts cannot be classified with confidence. This diagnostic is therefore blocked from claiming that specific repository-owner failures were repaired.

## 3. Files changed before repair

Read-only inspection commands were run before the controlled repair:

- `git status --short`
- `git diff --name-only`
- `git diff`
- direct reads of the H1 files

Detected status from the repository root included many pre-existing changed/untracked paths:

| Path | Classification |
| --- | --- |
| `mdc-catalog/docs/02_mdc_harmonized_service_discovery_decisions.md` | permitted H1 change, but ignored by git status because `docs/` is ignored |
| `mdc-catalog/backend/apps/ontology/service_discovery_registry.py` | permitted H1 change |
| `mdc-catalog/backend/apps/ontology/vocabularies.py` | permitted H1 change |
| `mdc-catalog/backend/tests/test_service_discovery_registry.py` | permitted H1 change |
| `mdc-catalog/backend/tests/test_api_v1.py` | permitted H1 change |
| `mdc-catalog/backend/apps/` | unclear from git because the whole directory is untracked in this worktree |
| `mdc-catalog/backend/tests/` | unclear from git because the whole directory is untracked in this worktree |
| `mdc-catalog/backend/config/settings.py` | out-of-scope for H1; pre-existing/unrelated change requiring owner review |
| `mdc-catalog/backend/config/urls.py` | out-of-scope for H1; pre-existing/unrelated change requiring owner review |
| `mdc-catalog/backend/config/__init__.py` | out-of-scope for H1; deleted in worktree before this repair |
| `mdc-catalog/backend/db.sqlite3` | out-of-scope for H1; pre-existing/unrelated change requiring owner review |
| `mdc-catalog/data/curated/tasowheel_offerings.yaml` | out-of-scope for H1; pre-existing/unrelated change requiring owner review |
| `mdc-catalog/data/curated/providers/` | out-of-scope for H1; untracked directory requiring owner review |
| `mdc-catalog/data/generated/tasowheel_catalog.ttl` | out-of-scope for H1; deleted in worktree before this repair |
| `mdc-catalog/data/generated/mdc_catalog.ttl` | out-of-scope for H1; untracked generated data requiring owner review |
| `mdc-catalog/README.md` | out-of-scope for H1; pre-existing/unrelated change requiring owner review |
| `mdc-catalog/docs/api-contract-v1.md` | out-of-scope for H1; pre-existing/unrelated change requiring owner review |
| `mdc-catalog/docs/architecture.md` | out-of-scope for H1; pre-existing/unrelated change requiring owner review |
| `mdc-catalog/docs/ontology-profile-v1.md` | out-of-scope for H1; pre-existing/unrelated change requiring owner review |
| `mdc-catalog/docs/query-mapping-matrix.md` | out-of-scope for H1; pre-existing/unrelated change requiring owner review |
| `mdc-catalog/docs/seed-data-template.md` | out-of-scope for H1; pre-existing/unrelated change requiring owner review |
| `MDC_Dev_chat/...` | out-of-scope for H1; pre-existing/unrelated deletions requiring owner review |
| `new_Phases.md` | out-of-scope for H1; untracked file requiring owner review |

The normal `git diff` did not show the H1 file content because the relevant backend paths are inside untracked directories and `docs/` is ignored. The H1 files were inspected directly from disk.

## 4. Failure classification

Exact failure classification is blocked pending the repository-owner test output.

| Classification | Affected test | Probable cause | Repair performed | Final rerun required |
| --- | --- | --- | --- | --- |
| Unclassified pending output | Unknown | Exact failure output was not supplied | None claimed against a specific failure | Yes |
| Potential Category A hardening | H1 registry tests or stricter hidden/owner checks | `bounding_box_mm` declared `width_mm` and `height_mm` components, while those component fields did not have explicit field definitions | Added `width_mm` and `height_mm` field definitions and asserted component definitions exist | Yes |
| Potential Category E if present in owner output | Optional Fuseki integration tests | Fuseki may be unavailable, which the inventory identifies as an expected skip path | No repair; expected skip should remain | Yes |

No Category B, C, or D classification can be assigned without the actual failed test names and tracebacks.

## 5. Controlled repairs made

Files modified during this repair task:

- `backend/apps/ontology/service_discovery_registry.py`
- `backend/tests/test_service_discovery_registry.py`
- `docs/03_h1_service_discovery_registry_implementation_report.md`

Repair details:

- Added field definitions for `width_mm` and `height_mm`, because `bounding_box_mm.components` references them.
- Extended the registry unit test to assert every `bounding_box_mm` component has a field definition.
- Created this diagnostic-and-repair report.

Why this is within H1 scope:

- The registry is the H1 implementation surface.
- The H1 test file is the intended place to prove registry completeness.
- No active search, matching, RDF, SPARQL, Fuseki, provider-publication, provider YAML, route, settings, model, or migration behaviour was changed.

No legacy test file was deleted, no regression assertion was removed merely to obtain passing results, and no H2-or-later functionality was activated.

No assertion was weakened. No unconditional skip was added. No out-of-scope production file was modified during this repair task.

## 6. Registry and terminology verification

Verified by inspection:

- Response key is `service_discovery`.
- No new `m18_` or `M18_` API/Python naming identifiers were introduced except version string `"m18_harmonized_v1"`.
- Public getter is `get_service_discovery_registry()`.
- Part-family constant is `SERVICE_DISCOVERY_PART_FAMILIES`.
- Registry activation key is `search_contract_active`.
- `search_contract_active` is `False`.
- Gear profiles use `outside_diameter_mm`.
- Gear profiles do not use `diameter_mm` or `outer_diameter_mm` in gear family-common or gear part-type-specific fields.
- Shaft profiles use `outer_diameter_mm`.
- Rotational metal-part profiles use `outer_diameter_mm`.
- Material grades are excluded from new `generic_requirement_fields`.

## 7. Legacy preservation verification

Verified by inspection:

- Legacy filter keys remain: `service_types`, `part_families`, `processes`, `materials`, `material_grades`, `certifications`.
- The existing legacy top-level `part_families` vocabulary was not expanded in H1.
- Active `SearchRequestSerializer` remains unchanged.
- Local matcher remains unchanged.
- Provider publication remains unchanged.
- Provider YAML remains unchanged during this repair task.
- RDF generation remains unchanged.
- SPARQL query builder remains unchanged.
- Fuseki client/search service remains unchanged.

## 8. Tests created or changed

H1 test files:

- `backend/tests/test_service_discovery_registry.py`
  - Tests registry metadata and inactive search contract.
  - Tests neutral naming.
  - Tests three service categories.
  - Tests sixteen part types.
  - Tests corrected gear `outside_diameter_mm`.
  - Tests shaft and rotational metal-part `outer_diameter_mm`.
  - Tests material-grade exclusion from generic requirements.
  - Tests field-definition completeness and copy safety.
  - During this repair, it was extended to verify `bounding_box_mm` component definitions.

Existing endpoint/filter test:

- `backend/tests/test_api_v1.py`
  - Retains legacy filter assertions.
  - Adds additive `service_discovery` filter assertions.
  - Adds protective non-activation tests for the legacy search serializer.

No other test was touched during this repair.

## 9. Runtime verification status after repair

Final runtime verification must be run by the repository owner in the activated Django-enabled `.venv` after these repairs.

Codex did not run Django verification because the available default interpreter still does not have Django installed. A syntax-only `python -m py_compile` pass was run for the touched Python/test files and completed successfully, but that is not a substitute for Django runtime verification.

Required owner commands:

```powershell
python manage.py check
python manage.py test
```

## 10. Issues blocking H2

H2 is currently blocked.

Reasons:

- Exact repository-owner failure output was not supplied, so failures are not fully classified.
- Final repository-owner rerun has not yet passed after this repair.
- The worktree contains many out-of-scope modified/untracked paths that should be reviewed before treating H1 as cleanly accepted.

## 11. Completion checklist

- [ ] Exact pre-repair failure output recorded.
- [ ] All failures classified.
- [x] No legacy tests deleted to hide failures.
- [x] No regression assertions improperly removed.
- [x] H0 gear terminology correction confirmed.
- [x] `service_discovery` registry verified.
- [x] Neutral naming verified.
- [x] Gear/shaft diameter distinction verified.
- [x] Legacy filter keys preserved.
- [x] Active search contract remains unchanged.
- [x] Out-of-scope files unchanged or issue documented.
- [ ] Final repository-owner `python manage.py check` passed.
- [ ] Final repository-owner `python manage.py test` passed.
- [ ] Ready for H2 review.
