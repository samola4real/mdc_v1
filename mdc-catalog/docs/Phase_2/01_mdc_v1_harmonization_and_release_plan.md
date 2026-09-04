# MDC v1 Harmonization and Release Plan

**Project:** MaaSAI MaaS Dynamic Catalogue (MDC)  
**Phase:** Resume / Harmonization before Vercel deployment  
**Recommended Codex model:** GPT-5.6 Sol  
**Recommended reasoning:** Medium by default; High only for difficult architecture conflicts  
**Codex usage constraint:** Keep each task narrowly scoped to fit within the 5-hour usage window.

---

## 1. Objective

Before releasing or deploying MDC v1:

1. Treat the **latest code and data files as the intended source of truth**.
2. Do **not** roll back newer working code simply to satisfy stale tests.
3. Harmonize:
   - current code
   - current provider data
   - active APIs
   - tests
   - Git state
4. Keep the local `docs/` folder, but **do not track or push it to Git**.
5. Stabilize the MDC v1 baseline before starting Vercel deployment work.
6. Defer the production database redesign until after the code/test/API baseline is stable.

---

## 2. Guiding Rule

When tests disagree with the latest implementation:

> Assume the latest implementation is authoritative until repository evidence shows that the code contains a genuine defect.

Codex should classify each failing test as one of:

- current and valid
- stale / superseded
- legacy but intentionally retained
- invalid because test data is outdated
- exposing a real defect in current code

Codex must **not modify production code merely to make an old test pass** without first confirming that the test still represents the intended MDC v1 behavior.

---

# Milestone M1 — Establish the Current Source of Truth

## Goal

Clearly determine what belongs to the current MDC v1 and what is legacy or superseded.

## Main work

Audit and classify:

- current Django apps
- active API routes
- service-discovery implementation
- provider data folders and schemas
- legacy catalogue/search paths
- publication paths
- RDF/RDFLib/Fuseki components
- tests
- generated files
- obsolete placeholders
- Git-tracked vs untracked files

Pay special attention to the newer harmonized flow around:

```text
/api/service-discovery/search
```

and the H1-H9 implementation.

## Required output

Create a short classification table:

| Item | Status | Action |
|---|---|---|
| Current | keep | maintain/test |
| Legacy but needed | isolate | test separately |
| Superseded | archive/remove from active flow | do not force compatibility |
| Stale test | update/remove | align with latest implementation |
| Real defect | fix | add/update test |

## Exit condition

- Clear current MDC v1 architecture is identified.
- Legacy and superseded paths are explicitly separated.
- No code is rolled back merely to satisfy stale tests.

## Recommended Codex

**GPT-5.6 Sol — Medium reasoning**

---

# Milestone M2 — Harmonize Data and Tests

## Goal

Make the test suite represent the latest intended MDC behavior.

## Priority issue

Resolve mixed schemas under:

```text
data/curated/providers/
```

Current provider/source/staging files must not be mixed with legacy runtime seed formats if their schemas differ.

Prefer a clean data separation such as:

```text
data/
├── curated/
│   ├── providers/                    # only one clearly defined active schema
│   └── service_discovery/providers/
├── staging/                          # provider-upload/source-style files
└── generated/
```

Exact structure should be based on the current repository, not forced if another existing structure is cleaner.

## Test strategy

For each failing test:

1. Check whether the tested behavior is still part of current MDC v1.
2. If yes:
   - update the test to the latest API/data contract;
   - fix production code only when an actual defect exists.
3. If no:
   - remove, archive, or clearly mark the test as legacy.
4. Preserve tests for the harmonized service-discovery implementation.

## Verification

Run:

```powershell
python manage.py check
python manage.py test -v 2
```

Also run the focused service-discovery suite.

Record:

- total tests
- passed
- failed
- skipped
- intentionally removed/updated legacy tests
- any remaining blockers

## Exit condition

- Current MDC v1 tests reflect current behavior.
- Provider data schemas are clearly separated.
- Harmonized service-discovery tests remain green.
- Full suite is green, or any remaining failures are explicitly justified and intentionally deferred.

## Recommended Codex

**GPT-5.6 Sol — Medium reasoning**

Use **High** only if Codex encounters a real conflict between active architecture and test expectations.

---

# Milestone M3 — Create a Clean Git Baseline

## Goal

Create one trustworthy repository checkpoint before deployment work begins.

## Git principles

Keep in Git:

- backend source code
- tests
- required configuration templates
- required runtime/static provider data
- dependency files
- deployment configuration when added later

Do not push:

```text
docs/
```

The `docs/` folder should remain available locally.

## Required Git work

Codex should first inspect:

```powershell
git status
git ls-files
git diff
```

Then:

1. Preserve the latest intended code/data.
2. Add `/docs/` to `.gitignore`.
3. If `docs/` is already tracked:
   - stop tracking it without deleting the local folder.
4. Review generated/local files before committing.
5. Ensure secrets, local environment files, caches, DB artifacts, and temporary files are excluded where appropriate.
6. Create a clean baseline commit.

## Important

Do not use destructive Git commands that could remove current uncommitted improvements.

Avoid broad commands such as:

```text
git reset --hard
git clean -fd
```

unless explicitly reviewed and justified.

## Exit condition

```text
git status
```

is clean except for intentionally ignored local files.

## Recommended Codex

**Luna or GPT-5.6 Sol — Medium reasoning**

Luna is sufficient if this becomes mostly mechanical Git cleanup.

---

# Milestone M4 — Stabilize the Public MDC API Contract

## Goal

Decide the API that the MaaSAI Marketplace and other components should use.

## Preferred current candidate

Use the harmonized endpoint as the main integration candidate:

```text
POST /api/service-discovery/search
```

Before public deployment, decide whether the canonical versioned path should become:

```text
POST /api/v1/service-discovery/search
```

Possible transition:

```text
/api/service-discovery/search
    -> temporarily retained for compatibility

/api/v1/service-discovery/search
    -> documented public v1 contract
```

## Also review

- `/api/health`
- `/api/catalog/filters`
- provider detail endpoints
- offering detail endpoints
- provider-publication endpoint
- demo endpoints

## Exit condition

A small, explicit list of:

- supported public APIs
- internal/demo APIs
- deprecated APIs
- write APIs deferred until durable persistence is available

## Recommended Codex

**GPT-5.6 Sol — Medium reasoning**

---

# Milestone M5 — Vercel Production Preparation

## Goal

Make the Django backend deployment-safe.

Do this only after M1-M4 are stable.

## Required areas

- production settings
- `DEBUG=False`
- environment-based `SECRET_KEY`
- `ALLOWED_HOSTS`
- CORS
- CSRF trusted origins where required
- secure deployment settings
- dependency packaging
- Python version
- Vercel entrypoint/configuration
- disable demo APIs in production
- disable or protect file-backed mutation endpoints
- ensure required RDF/YAML fallback files are included

## Database

Do **not** redesign the database during the harmonization milestones.

For the first deployment:

- keep search/read functionality as the focus;
- defer durable provider publication/request persistence.

A proper production database can be introduced as a separate later milestone.

## Exit condition

```powershell
python manage.py check
python manage.py check --deploy
```

shows an acceptable production configuration, with any remaining warnings documented.

## Recommended Codex

**GPT-5.6 Sol — Medium reasoning**

---

# Milestone M6 — First Vercel Pilot Deployment

## Goal

Deploy the read-oriented MDC backend and verify external access.

Initial public scope should preferably be limited to:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Provider publication should remain disabled or protected until durable storage is implemented.

## Search backend

Initial deployment can use:

```text
External Fuseki
      ↓ failure
RDFLib fallback
      ↓ failure
harmonized YAML fallback
```

External Fuseki can be added/configured after the Vercel Django deployment is stable.

## Exit condition

Marketplace or another MaaSAI component can successfully call:

- health
- filters
- service discovery search

over HTTPS.

## Recommended Codex

**GPT-5.6 Sol — Medium reasoning**

---

# Later Milestone — Production Persistence and External Fuseki

This should be handled separately after the Vercel pilot is stable.

## Work

- select and configure production DB
- provider publication persistence
- request/history persistence if required
- authentication
- authorization
- throttling/rate limiting
- external Fuseki hosting
- RDF update pipeline
- monitoring/logging
- backup/recovery

---

# Recommended Execution Order

```text
M1  Current source of truth
 ↓
M2  Harmonize data + tests
 ↓
M3  Clean Git baseline
 ↓
M4  Stabilize public API contract
 ↓
M5  Vercel production preparation
 ↓
M6  First Vercel pilot
 ↓
Later: production DB + provider persistence + external Fuseki hardening
```

---

# Recommended Use of the Codex 5-Hour Limit

Do not combine the entire roadmap into one Codex task.

## Next Codex session

Focus only on:

```text
M1 + M2
```

If M1 and M2 finish cleanly and there is enough capacity, continue with:

```text
M3
```

Do **not** begin Vercel configuration in the same session unless M1-M3 are fully completed and verified.

## Desired result after the next Codex session

```text
Latest MDC code preserved
        ↓
Current vs legacy clearly classified
        ↓
Provider data schemas harmonized
        ↓
Tests aligned to the current implementation
        ↓
Relevant test suite green
        ↓
Ready for clean Git baseline
```

---

# Model / Intelligence Recommendation

| Task | Recommended configuration |
|---|---|
| Architecture/source-of-truth audit | GPT-5.6 Sol — Medium |
| Test/data harmonization | GPT-5.6 Sol — Medium |
| Difficult architecture conflict | GPT-5.6 Sol — High temporarily |
| Git cleanup | Luna or Sol — Medium |
| API stabilization | GPT-5.6 Sol — Medium |
| Vercel preparation | GPT-5.6 Sol — Medium |
| Routine mechanical changes | Luna where available |

Avoid:

- Ultra
- Extra High
- unnecessarily expensive reasoning modes

unless a specific blocking issue clearly requires deeper reasoning.

---

# Immediate Next Task

Create the next Codex task as:

```text
01_mdc_v1_code_test_data_harmonization
```

Its scope should be limited to:

1. establish latest/current code as source of truth;
2. classify legacy vs current behavior;
3. harmonize provider data schemas;
4. update/remove stale tests;
5. preserve H1-H9/service-discovery behavior;
6. rerun verification;
7. prepare the repository for the subsequent clean Git baseline.

Do not start Vercel deployment work in this task.
