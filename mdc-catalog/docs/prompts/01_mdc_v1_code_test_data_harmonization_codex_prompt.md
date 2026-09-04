# Codex Task 01 — MDC v1 Code, Data, and Test Harmonization

## Recommended Codex configuration

Use:

- **Model / intelligence:** GPT-5.6 Sol
- **Reasoning:** Medium
- Increase to **High only temporarily** if there is a genuine architecture/test conflict that cannot be resolved confidently at Medium.
- Do **not** use Ultra / Extra-High reasoning for this task.

Keep the task tightly scoped so it fits within the available Codex 5-hour usage window.

---

## Context

I am resuming development of the **MaaSAI MaaS Dynamic Catalogue (MDC v1)** after a break.

Repository:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

The agreed harmonization/release plan is:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\01_mdc_v1_harmonization_and_release_plan.md
```

The previous repository audit is:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\00_mdc_v1_resume_and_vercel_deployment_audit.md
```

Read both documents first for context, but verify all conclusions against the **actual current repository**.

---

# Objective

Complete **Milestone M1 and Milestone M2 only**:

1. establish the current/latest MDC v1 implementation as the source of truth;
2. clearly separate current, legacy, superseded, and staging/source artifacts;
3. harmonize provider data/schema locations;
4. update/remove/archive stale tests so tests represent the current intended implementation;
5. fix production code only where there is evidence of a real current defect;
6. preserve the newer harmonized H1-H9/service-discovery implementation;
7. rerun verification and leave the repository ready for the later clean-Git milestone.

Do **not** start Vercel, database, deployment, authentication, Fuseki hosting, or API-versioning work in this task.

---

# Critical Rule — Latest Implementation Takes Priority

Before modifying code because a test fails, determine whether the test still represents the current intended MDC v1 behavior.

Use this principle:

> **The latest implementation/code/data is presumed authoritative unless repository evidence shows that it contains a genuine defect. Do not roll back or weaken newer working code merely to satisfy stale legacy tests.**

Classify every relevant conflict as one of:

- `current_and_valid`
- `stale_or_superseded_test`
- `legacy_but_intentionally_retained`
- `outdated_test_data`
- `real_current_code_defect`
- `unclear_requires_evidence`

Only modify current production code for `real_current_code_defect` or when necessary to establish a clean, intentional data boundary.

---

# M1 — Establish Current MDC v1 Source of Truth

Inspect the actual repository.

Review at minimum:

```text
backend/
backend/config/
backend/apps/api/
backend/apps/providers/
backend/apps/search/
backend/apps/ontology/
backend/apps/demo/
backend/tests/

data/curated/
data/curated/providers/
data/curated/service_discovery/
data/generated/

requirements/
.gitignore
git status
git diff
git ls-files
```

Also inspect relevant implementation/history reports under `docs/` only as supporting evidence.

## Determine the active architecture

Pay particular attention to:

```text
POST /api/service-discovery/search
```

and the harmonized H1-H9 implementation, including:

- service-discovery registry
- publication serializer/normalizer
- harmonized provider YAML
- search serializer/normalizer
- H5 matcher
- H6 RDF generation
- H7 RDFLib retrieval
- H8 optional Fuseki retrieval
- H9 matching alignment
- runtime fallback behavior

Also classify the older paths, including where applicable:

```text
/api/catalog/search
/api/provider-publication
/api/providers/<provider_id>
/api/offerings/<offering_id>
```

Do not assume these must remain active just because old tests exist.

## Required classification

Create an internal working classification similar to:

| Component/file/path | Classification | Evidence | Required action |
|---|---|---|---|
| ... | current | ... | keep |
| ... | legacy retained | ... | isolate |
| ... | superseded | ... | stop treating as active |
| ... | staging/source | ... | move/isolate from runtime data |
| ... | stale test | ... | update/remove |
| ... | real defect | ... | fix |

Use this classification to guide all changes.

---

# M2 — Harmonize Provider Data and Tests

## Priority problem

The previous audit found mixed schemas under:

```text
data/curated/providers/
```

with newer/source-style provider files being interpreted by an older legacy loader/schema.

Resolve this cleanly.

### Preferred architectural principle

A runtime loader should consume a clearly defined schema from a clearly defined location.

Do **not** make a legacy loader silently accept arbitrary unrelated provider schemas merely to make tests pass.

If a provider file represents staging/source/publication input rather than the active runtime schema, move or classify it accordingly.

Possible separation might resemble:

```text
data/
├── curated/
│   ├── providers/
│   └── service_discovery/providers/
├── staging/
└── generated/
```

This is only an example. Use the cleanest structure consistent with the existing latest implementation.

### Preserve current data

Do not discard or overwrite newer provider data.

If a file must move:

- preserve its contents;
- update only references that genuinely need the new location;
- avoid duplicate competing sources of truth.

---

# Test Harmonization Rules

For each failing/relevant test:

### 1. Determine intent

Ask:

- Does this test describe the latest/current MDC v1 behavior?
- Does it test a superseded API/schema?
- Is its fixture/data shape obsolete?
- Is the failure caused by mixed runtime/staging data?
- Does it expose a genuine defect in current code?

### 2. Apply the appropriate action

If the behavior is current:

- update the test/fixture to the latest contract where necessary;
- fix production code only for genuine current defects.

If the behavior is superseded:

- remove, archive, rename, or otherwise clearly separate the stale test from the active suite;
- do not distort new implementation to preserve obsolete behavior.

If legacy functionality is intentionally retained:

- isolate its test data and expectations so it cannot contaminate the harmonized service-discovery path.

### 3. Protect H1-H9

The newer service-discovery flow previously passed a focused suite of approximately 220 tests.

Do not regress it.

After changes, rerun the focused service-discovery tests.

---

# Scope Control

## Allowed

- move/reorganize provider data where justified;
- update loaders/references to enforce clean schema boundaries;
- update current tests and fixtures;
- retire/archive stale tests where clearly superseded;
- small current-code fixes supported by evidence;
- remove obsolete duplicate runtime assumptions;
- update `.gitignore` only if needed to prevent test/generated/local artifacts from interfering with this task.

## Not allowed in Task 01

Do not:

- start Vercel configuration;
- add production DB;
- redesign provider persistence;
- add authentication/rate limiting;
- configure external Fuseki hosting;
- change public API versioning;
- perform broad architecture refactors;
- rewrite working H1-H9 logic without evidence;
- populate unrelated empty ontology/scripts/Docker placeholders;
- perform destructive Git cleanup;
- commit/push unless explicitly requested later.

Do not use:

```text
git reset --hard
git clean -fd
```

or other destructive commands.

The `docs/` Git cleanup belongs mainly to **Milestone M3**, not this task.

---

# Verification

Run from the appropriate environment/repository location.

At minimum:

```powershell
python manage.py check
python manage.py test -v 2
```

Use the repository's existing virtual environment/Python executable if required.

Also rerun the focused harmonized service-discovery suite.

If the full suite remains non-green, do not hide it.

For every remaining failure classify it as:

```text
current defect
intentional legacy/deferred behavior
environment/integration dependency
unresolved
```

The task is successful when the active/current MDC v1 baseline is coherent even if an intentionally retired legacy suite is no longer part of the active test baseline.

---

# Required Deliverable

Create a Markdown implementation report here:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2
```

Filename:

```text
02_mdc_v1_code_test_data_harmonization_report.md
```

The report must be concise and evidence-based.

Include:

## 1. Executive result

State whether M1 and M2 are:

- completed
- partially completed
- blocked

## 2. Source-of-truth decisions

Table:

```text
Area | Current source of truth | Legacy/superseded | Decision
```

## 3. Files changed/moved

For each:

```text
Path | Change | Reason
```

## 4. Test harmonization

State:

- stale tests updated
- stale tests removed/retired
- fixtures/data updated
- genuine production defects fixed
- important tests deliberately retained

Do not claim old tests were wrong without evidence.

## 5. Provider-data architecture after harmonization

Show the relevant directory/schema structure.

## 6. API/component status after harmonization

Especially:

```text
/api/service-discovery/search
/api/catalog/search
/api/provider-publication
provider detail
offering detail
```

Classify each as:

- current
- legacy retained
- superseded/deferred
- broken/blocking

## 7. Verification results

Provide exact commands and:

```text
tests run
passed
failed
skipped
```

Include focused H1-H9/service-discovery result.

## 8. Remaining issues

Only concrete unresolved issues.

## 9. Readiness for M3

End with exactly one verdict:

```text
READY_FOR_M3
```

or:

```text
NOT_READY_FOR_M3
```

Explain blockers if not ready.

---

# Important Documentation Rule

Do not spend time rewriting old documentation in this task.

The report should record documentation drift for later cleanup, but Task 01 is about:

```text
CODE
DATA
TESTS
```

not documentation modernization.

---

# Final Console Response

After implementation and report creation, respond concisely with:

1. M1 status
2. M2 status
3. main harmonization decisions
4. files/data moved or structurally changed
5. full test result
6. focused service-discovery test result
7. `READY_FOR_M3` or `NOT_READY_FOR_M3`
8. report path

Do not start Milestone M3 automatically.
