# Codex Task 02 — MDC v1 Clean Git Baseline

## Recommended Codex configuration

Use:

- **Model / intelligence:** GPT-5.6 Sol
- **Reasoning:** Medium
- Luna is acceptable only if the task remains purely mechanical after inspection.
- Do not use Ultra / Extra-High reasoning.

Keep this task narrowly scoped to Milestone M3.

---

## Context

Repository:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

Agreed plan:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\01_mdc_v1_harmonization_and_release_plan.md
```

Completed harmonization report:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\02_mdc_v1_code_test_data_harmonization_report.md
```

M1 and M2 are complete.

Current verified baseline from the harmonization report:

- full suite: 390 run, 377 passed, 0 failed, 13 skipped;
- focused service-discovery suite: 230 run, 225 passed, 0 failed, 5 skipped;
- `manage.py check`: pass;
- `POST /api/service-discovery/search` and H1-H9 remain the current MDC v1 source of truth;
- legacy `/api/catalog/search`, provider detail, offering detail, and legacy provider publication remain intentionally isolated;
- source-style Precipart data was moved to:

```text
data/staging/provider_sources/precipart.yaml
```

Do not revisit M1/M2 architecture unless Git inspection reveals a concrete inconsistency.

---

# Objective

Complete **Milestone M3 — Clean Git Baseline**.

The goal is to make Git accurately represent the latest intended MDC v1 code/data/test state while:

1. preserving all current/latest implementation files;
2. keeping `docs/` locally;
3. ensuring `docs/` is not tracked or pushed to Git;
4. excluding local/generated/cache/secret artifacts that should not be versioned;
5. avoiding destructive Git operations;
6. creating a clean local baseline commit;
7. leaving the repository ready for M4.

Do not start M4 API work, Vercel work, database work, auth, or deployment work.

---

# Critical Git Safety Rules

The working tree contains important work that was previously untracked or modified.

Therefore:

## Never use destructive commands such as

```text
git reset --hard
git clean -fd
git checkout -- .
git restore .
```

or equivalent broad destructive operations.

Do not delete files merely because Git does not currently track them.

Treat the **current working tree as the source of truth** unless evidence clearly proves a file is disposable.

---

# Step 1 — Inspect Git State First

Before changing anything, inspect:

```powershell
git status --short
git status
git branch --show-current
git remote -v
git log --oneline --decorate -10
git ls-files
git diff
git diff --cached
```

Also inspect:

```text
.gitignore
```

Classify current files into:

- source code that must be tracked;
- tests that must be tracked;
- required runtime data that must be tracked;
- configuration/dependency templates that must be tracked;
- generated artifacts intentionally tracked;
- local-only files;
- cache/build artifacts;
- secrets/environment files;
- documentation to remain local but untracked;
- obsolete/unnecessary files.

Do not assume generated files should be ignored if the current runtime relies on them. Verify first.

---

# Step 2 — Preserve the Current MDC v1 Baseline

The following categories should normally remain tracked if required by the repository:

```text
backend/
backend/tests/
requirements/
data/curated/
data/staging/
```

Also retain required generated runtime assets if the application/tests currently depend on them.

Pay special attention to:

```text
data/generated/service_discovery/mdc_service_discovery_catalog.ttl
```

Do not remove it from version control merely because it is generated if the current deployment/runtime fallback expects the file to exist.

Use repository evidence and tests to decide.

---

# Step 3 — Keep docs/ Local but Remove It From Git Tracking

User requirement:

> The `docs/` folder must remain on the local machine but must not be pushed to Git.

Ensure `.gitignore` includes:

```gitignore
/docs/
```

If `docs/` is already tracked, stop tracking it **without deleting local files**.

Use the safe Git approach appropriate to the current repository, e.g. equivalent to:

```powershell
git rm -r --cached docs
```

only after confirming the folder is tracked and the operation will leave local files intact.

Verify afterward that:

- local `docs/` still exists;
- Git no longer tracks files under `docs/`;
- `/docs/` is ignored.

Do not delete the local reports.

---

# Step 4 — Improve .gitignore Conservatively

Inspect existing ignore rules before modifying.

At minimum consider whether the repository should ignore:

```text
.env
.env.*
!.env.example
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/
.venv/
venv/
*.log
.DS_Store
Thumbs.db
```

For Django/local development, inspect whether these should be ignored:

```text
db.sqlite3
*.sqlite3
staticfiles/
media/
```

Do not blindly ignore them if this project intentionally relies on a committed pilot artifact.

Never commit real secrets.

Keep `.env.example` trackable when it is later populated.

---

# Step 5 — Review Untracked and Modified Files

For every significant untracked/modified file, determine whether it belongs to the latest MDC implementation.

Especially review:

```text
backend/apps/
backend/tests/
data/curated/
data/staging/
data/generated/
requirements/
backend/config/settings_local.py
```

The previous audit reported that many important current files appeared untracked.

The purpose of M3 is to make sure the actual current implementation is now captured in Git.

Do not omit current code simply because it was never committed before.

---

# Step 6 — Stage Intentionally

Stage only the intended MDC v1 baseline.

Before committing, run:

```powershell
git status
git diff --cached --stat
git diff --cached
```

Review for:

- accidental deletion of current code;
- accidental inclusion of docs;
- accidental secrets;
- local machine paths;
- cache files;
- SQLite/local runtime state unless intentionally retained;
- unintended generated noise.

If a suspicious secret or credential is found:

- do not commit it;
- report it;
- do not print the secret value in the report.

---

# Step 7 — Re-run Verification Before Commit

Because Git cleanup can accidentally alter paths/files, rerun at minimum:

```powershell
python manage.py check
python manage.py test -v 2
```

Use the repository's existing virtual environment/Python executable if required.

Also rerun the focused service-discovery suite if practical within the remaining Codex window.

Expected baseline from M2:

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

If counts change, explain why.

Do not create the baseline commit if active tests unexpectedly fail.

---

# Step 8 — Create Local Baseline Commit

Once:

- current source is staged;
- docs are untracked/ignored;
- secrets/local artifacts are excluded;
- tests are green;

create one local Git commit.

Recommended commit message:

```text
chore: establish harmonized MDC v1 baseline
```

If repository conventions clearly use another style, follow the existing convention.

## Important

**Do not push to the remote repository in this task.**

The purpose of M3 is to create and verify a clean local baseline first.

Remote push can be done after the M3 report is reviewed.

---

# Step 9 — Confirm Final Git State

After commit run:

```powershell
git status
git status --short
git log -1 --oneline
git ls-files docs
```

Required result:

- working tree clean, except intentionally ignored local files;
- latest MDC code/data/tests captured in Git;
- `git ls-files docs` returns no tracked documentation files;
- local `docs/` directory still exists.

---

# Required Deliverable

Create a concise Markdown report:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\03_mdc_v1_clean_git_baseline_report.md
```

Because `docs/` is ignored, this report should remain local and should not become part of the Git commit.

Include:

## 1. M3 status

Use:

```text
completed
partially completed
blocked
```

## 2. Git state before cleanup

Summarize:

- branch;
- remote(s);
- tracked/untracked situation;
- important risks found.

## 3. .gitignore decisions

Table:

```text
Pattern | Added/retained | Reason
```

## 4. docs/ handling

State explicitly:

- local docs preserved: yes/no;
- Git docs tracking removed: yes/no;
- `/docs/` ignored: yes/no.

## 5. Files newly tracked

Summarize important current code/data/test directories captured by the baseline.

Do not list every file if hundreds exist; group logically.

## 6. Files intentionally excluded

Examples:

- docs
- caches
- virtual environments
- secrets
- local DB/runtime files

Only report what actually applies.

## 7. Verification

Include exact commands and:

```text
tests run
passed
failed
skipped
```

## 8. Baseline commit

Report:

```text
commit hash
commit message
branch
```

## 9. Final Git state

State whether the working tree is clean.

## 10. Readiness

End with exactly one:

```text
READY_FOR_M4
```

or

```text
NOT_READY_FOR_M4
```

If not ready, give concrete blockers.

---

# Scope Restrictions

Do not:

- push to GitHub/GitLab/remote;
- start M4;
- change API paths/contracts;
- start Vercel;
- add DB;
- add authentication;
- configure external Fuseki;
- rewrite docs;
- refactor working H1-H9 code;
- remove legacy APIs;
- change current provider-data architecture without a concrete Git-related reason.

This task is Git baseline work only.

---

# Final Console Response

Return only a concise summary containing:

1. M3 status
2. current branch
3. docs Git status
4. tests result
5. baseline commit hash/message
6. final `git status`
7. `READY_FOR_M4` or `NOT_READY_FOR_M4`
8. report path

Do not push and do not start M4 automatically.
