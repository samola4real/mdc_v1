# Codex Task 03 — MDC v1 Public API Contract Stabilization

## Recommended Codex configuration

Use:

- **Model / intelligence:** GPT-5.6 Sol
- **Reasoning:** Medium
- Increase to **High only temporarily** if there is a genuine contract/compatibility conflict.
- Do not use Ultra / Extra-High reasoning.

Keep this task tightly scoped to **Milestone M4**.

---

## Context

Repository:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

Agreed harmonization/release plan:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\01_mdc_v1_harmonization_and_release_plan.md
```

Completed reports:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\02_mdc_v1_code_test_data_harmonization_report.md

C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\03_mdc_v1_clean_git_baseline_report.md
```

Current clean baseline:

```text
commit: 3d1b37e
message: chore: establish harmonized MDC v1 baseline
branch: main
```

M1, M2, and M3 are complete.

Current verified test baseline:

```text
Full suite:
390 run
377 passed
0 failed
13 skipped

Focused service-discovery:
230 run
225 passed
0 failed
5 skipped
```

Current architectural source of truth:

```text
POST /api/service-discovery/search
```

with the harmonized H1-H9 service-discovery implementation.

Legacy paths remain intentionally isolated and test-covered:

```text
POST /api/catalog/search
POST /api/provider-publication
GET  /api/providers/<provider_id>
GET  /api/offerings/<offering_id>
```

---

# Precondition — Preserve the Baseline

Before making M4 changes, inspect:

```powershell
git status
git log -1 --oneline
git branch --show-current
git remote -v
```

Expected baseline:

```text
3d1b37e chore: establish harmonized MDC v1 baseline
```

If this commit has not yet been pushed and the working tree is clean, it is acceptable to push this existing baseline commit to:

```text
origin/main
```

before starting M4.

Do not push unrelated later M4 changes automatically unless explicitly instructed at the end of this task.

---

# Objective

Complete **Milestone M4 — Stabilize the Public MDC API Contract**.

The purpose is to establish a small, explicit, stable API surface that other MaaSAI components—especially the Cloud MaaS Marketplace—can integrate against.

This task is primarily about:

```text
API CONTRACT
ROUTES
REQUEST/RESPONSE CONSISTENCY
LEGACY ISOLATION
TESTS
```

Do not start Vercel deployment work yet.

---

# Critical Architectural Decision

The current MDC v1 integration source of truth is:

```text
POST /api/service-discovery/search
```

Treat this as the current search implementation unless repository evidence reveals a genuine issue.

Do **not** restore the older `/api/catalog/search` as the preferred public search merely because it exists.

---

# M4 Goals

Establish clear classifications for all shared API endpoints:

- `public_current`
- `public_legacy_compatibility`
- `internal_or_demo`
- `write_deferred`
- `deprecated_candidate`

The end result should make it obvious what the Marketplace should call.

---

# Step 1 — Audit the Actual API Surface

Inspect:

```text
backend/config/urls.py
backend/apps/api/urls.py
backend/apps/api/views/
backend/apps/api/serializers*
backend/apps/api/response_utils.py
backend/apps/demo/urls.py
backend/apps/demo/views/
backend/apps/providers/
backend/apps/search/
backend/tests/
```

Enumerate the actual routes, methods, serializers, response shapes, and dependencies.

Do not trust old docs over the current route table and tests.

---

# Step 2 — Decide Canonical Public v1 Paths

Preferred design:

```text
/api/v1/...
```

Evaluate whether the current public paths should gain versioned aliases while preserving compatibility.

Preferred target candidates:

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

Potential compatibility aliases:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Do not remove existing paths if doing so would break current tests or integrations unless there is explicit evidence they are safe to retire.

### Principle

Prefer:

```text
new canonical versioned path
+
temporary backwards-compatible existing alias
```

over destructive route replacement.

---

# Step 3 — Classify Legacy Endpoints

Review:

```text
POST /api/catalog/search
POST /api/provider-publication
GET  /api/providers/<provider_id>
GET  /api/offerings/<offering_id>
```

For each decide:

- should it remain callable?
- should it be described as legacy?
- should it get a versioned alias?
- should it remain out of the preferred Marketplace contract?
- does it depend on legacy seed schema?
- is it safe for future public deployment?

Do not remove these endpoints during M4 unless clearly obsolete and fully test-evidenced.

Expected likely classification:

```text
/api/catalog/search
    -> public_legacy_compatibility or deprecated_candidate

/api/provider-publication
    -> write_deferred

/api/providers/<provider_id>
    -> legacy retained / compatibility

/api/offerings/<offering_id>
    -> legacy retained / compatibility
```

Verify rather than blindly applying this expectation.

---

# Step 4 — Keep Demo APIs Out of Public Contract

Inspect:

```text
/api/demo/*
```

Classify all demo routes as:

```text
internal_or_demo
```

They should not be presented as part of the canonical MaaSAI integration API.

Do not yet implement production disablement; that belongs mainly to M5.

---

# Step 5 — Stabilize Search Request/Response Contract

Review the current serializer and tests for:

```text
POST /api/service-discovery/search
```

Confirm the authoritative request fields, including where applicable:

```text
request_id
consumer_id
service_category
part_family
part_type
requirements
match_policy
```

Confirm the authoritative response fields, including:

```text
request_id
result_count
results
status
warnings
matched_attributes
unmatched_attributes
unknown_attributes
evidence
```

Use the actual implementation/tests as source of truth.

Do not redesign the harmonized schema unless a genuine inconsistency is found.

---

# Step 6 — Resolve Small Contract Inconsistencies Only

Allowed examples:

- stale registry activation flag;
- route alias inconsistencies;
- mismatched response/status naming;
- endpoint path inconsistency;
- missing route test for a versioned alias;
- serializer/view import organization that causes contract ambiguity.

Avoid broad refactors.

One known candidate from the prior audit is:

```text
search_contract_active
```

in the service-discovery registry, which may be stale relative to the active shared endpoint.

Verify and correct it if needed.

---

# Step 7 — Preserve GET/POST View Convention

For any new or adjusted API views, preserve the established MDC convention:

```text
GET views  -> views/get_views.py
POST views -> views/post_views.py
```

Do not collapse these back into a monolithic `views.py` if the current implementation has already adopted the split.

---

# Step 8 — Tests

Add/update tests only as needed to prove the stabilized contract.

At minimum verify:

### Canonical public v1 endpoints

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

if versioned aliases are implemented.

### Existing compatibility endpoints

Confirm existing equivalent routes still work if retained.

### Search contract

Test:

- valid request;
- invalid controlled vocabulary;
- required-field validation;
- response contract;
- legacy alias compatibility if applicable.

Do not create duplicate exhaustive tests where existing H1-H9 tests already cover the behavior.

---

# Step 9 — Explicit Public API Matrix

At the end of implementation, produce a clear API matrix such as:

| Method | Canonical path | Compatibility path | Classification | Intended consumer |
|---|---|---|---|---|
| GET | `/api/v1/health` | `/api/health` | public_current | Marketplace/ops |
| GET | `/api/v1/catalog/filters` | `/api/catalog/filters` | public_current | Marketplace |
| POST | `/api/v1/service-discovery/search` | `/api/service-discovery/search` | public_current | Marketplace |
| POST | ... | ... | legacy/write_deferred | ... |

Populate it from the actual final code.

---

# Step 10 — Verification

Run:

```powershell
python manage.py check
python manage.py test -v 2
```

Also rerun the focused service-discovery suite.

Record exact counts.

Expected pre-M4 baseline:

```text
Full:
390 run
377 passed
0 failed
13 skipped

Focused:
230 run
225 passed
0 failed
5 skipped
```

Counts may increase because of new route/contract tests.

All active tests must pass.

---

# Git Handling

M3 established a clean baseline.

For M4:

- make only M4-related changes;
- do not touch ignored local docs except creating the required report;
- do not commit unrelated files;
- do not alter the data architecture;
- do not rewrite deployment files.

After verification, create a local commit.

Recommended message:

```text
feat: stabilize MDC v1 public API contract
```

Do not push the M4 commit automatically unless explicitly instructed.

---

# Out of Scope

Do not:

- configure Vercel;
- add `vercel.json`;
- add production deployment settings;
- add database persistence;
- redesign provider publication;
- add authentication;
- add rate limiting;
- host/configure external Fuseki;
- populate empty Docker/ontology placeholder files;
- perform documentation modernization;
- remove legacy APIs without strong evidence;
- redesign H1-H9 matching.

---

# Required Deliverable

Create:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\04_mdc_v1_public_api_contract_stabilization_report.md
```

The report remains local because `docs/` is ignored.

Include:

## 1. M4 status

```text
completed
partially completed
blocked
```

## 2. Canonical public API

Provide the final endpoint matrix.

## 3. Compatibility/legacy API

State exactly what remains and why.

## 4. Files changed

```text
Path | Change | Reason
```

## 5. Contract decisions

State:

- canonical base path;
- search endpoint;
- compatibility approach;
- provider publication status;
- demo API status.

## 6. Search request contract

Summarize authoritative request fields.

## 7. Search response contract

Summarize authoritative response fields.

## 8. Tests

Provide exact commands and counts.

## 9. Git commit

Report:

```text
hash
message
branch
```

## 10. M5 readiness

End with exactly one:

```text
READY_FOR_M5
```

or:

```text
NOT_READY_FOR_M5
```

Explain concrete blockers if not ready.

---

# Final Console Response

Return only:

1. M4 status
2. canonical public search endpoint
3. compatibility endpoint status
4. files changed
5. full test result
6. focused service-discovery result
7. local commit hash/message
8. `READY_FOR_M5` or `NOT_READY_FOR_M5`
9. report path

Do not start M5 automatically.
