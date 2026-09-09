# Codex Prompt — 04 Frontend GitHub Sanitized Snapshot Import

## Purpose

Import the already-preserved, already-sanitized MDC demonstration frontend snapshot into the personal `mdc_v1` GitHub repository in a controlled integration branch.

This is the **first write step** for the frontend integration. It must use only the sanitized staging snapshot produced by the accepted preservation step. Do not copy from the original dirty frontend working tree during this task.

The demo frontend is an illustrative MaaSAI pilot UI. It is **not** the real Cloud MaaS Marketplace (CMM). It exists to demonstrate how provider and consumer interaction with MDC could look before full Marketplace integration.

## Fixed paths

MDC repository:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Original frontend repository — READ ONLY in this task:

```text
C:\Users\Elahi\Desktop\template-frontend
```

Preservation root:

```text
C:\Users\Elahi\Desktop\mdc_frontend_preservation\2026-09-09
```

Sanitized application staging source:

```text
C:\Users\Elahi\Desktop\mdc_frontend_preservation\2026-09-09\sanitized-staging\demo-frontend
```

Sanitized historical reports source:

```text
C:\Users\Elahi\Desktop\mdc_frontend_preservation\2026-09-09\sanitized-staging\Implementation_History
```

Staging hash manifest:

```text
C:\Users\Elahi\Desktop\mdc_frontend_preservation\2026-09-09\manifest\sanitized_staging_sha256.txt
```

Source/provenance manifest:

```text
C:\Users\Elahi\Desktop\mdc_frontend_preservation\2026-09-09\manifest\frontend_source_manifest.md
```

Staging validation report:

```text
C:\Users\Elahi\Desktop\mdc_frontend_preservation\2026-09-09\reports\sanitized_staging_validation.md
```

Future path mapping:

```text
C:\Users\Elahi\Desktop\mdc_frontend_preservation\2026-09-09\reports\frontend_future_path_mapping.md
```

Target application path in `mdc_v1`:

```text
mdc-catalog/demo-frontend/
```

Target historical documentation path:

```text
mdc-catalog/docs/Demo_Frontend/Implementation_History/
```

Integration branch:

```text
demo-frontend-integration
```

## Approved source baseline

Original MaaSAI GitLab frontend source identity:

```text
repository: https://gitlab-cigip.alc.upv.es/maasai/tools/template-frontend.git
branch: main
HEAD: 832ad57265bce0889ebea58bc69c031c3b394ee7
```

Important: the original GitLab history contains credential-bearing historical objects and MUST NOT be imported into GitHub. This task is a sanitized **snapshot import**, not subtree/submodule/history migration.

The accepted sanitized staging result reported:

```text
application files: 134
historical reports: 30
forbidden staging paths: 0
likely credential findings: 0
FRONTEND SNAPSHOT PRESERVATION AND SANITIZED STAGING: PASS
READY_FOR_FRONTEND_GITHUB_IMPORT: YES
```

## Non-negotiable safety rules

Do NOT:

- modify `C:\Users\Elahi\Desktop\template-frontend`;
- change any Git remote in either repository;
- add the MaaSAI GitLab repository as a remote to `mdc_v1`;
- fetch or push to GitLab;
- import `.git` objects or frontend commit history;
- use `git subtree` or `git submodule`;
- rewrite history;
- force-push;
- merge to `main`;
- install or update npm packages;
- run `npm install`, `npm ci`, build, lint, or tests in this import step;
- rotate credentials;
- print credential values, connection strings, tokens, passwords, private keys, or secrets;
- copy `.env*`, raw realm exports, editor state, dependency/build output, caches, generated archives, or other excluded paths;
- alter MDC backend application code;
- fix frontend API behavior yet. Preserve the sanitized application snapshot as the functional baseline. API/config cleanup belongs to the next milestone.

If any safety gate fails, STOP before commit/push and report the blocker.

## Step 1 — Verify current MDC repository gate

From:

```powershell
cd C:\Users\Elahi\Desktop\mdc_v1
```

Verify:

```powershell
git status --short --branch
git branch --show-current
git rev-parse HEAD
git remote -v
git pull --ff-only
```

Requirements:

- current branch is `main` before integration branch creation;
- worktree is clean;
- pull is fast-forward only;
- `origin` remains the personal GitHub repository;
- no unexpected remotes;
- no unrelated changes.

Do not proceed if these conditions fail.

## Step 2 — Verify sanitized staging gate before copying

Read the accepted preservation manifests/reports.

Confirm:

- sanitized staging application path exists;
- historical reports staging path exists;
- staging contains the required Next.js application files;
- no `.git`, `.idea`, `.vscode`, `node_modules`, `.next`, build output, `.env*`, known raw Keycloak credential files, private-key material, or archives are present;
- active application contains no `/api/v1` usage;
- canonical public MDC paths are identifiable:
  - `/api/health`
  - `/api/catalog/filters`
  - `/api/service-discovery/search`;
- the staging hash manifest is internally consistent.

Use a local safe secret-risk scan comparable to the preservation step. Output only paths, identifiers/key names, and risk categories. Never print values.

If the staging tree now differs unexpectedly from the preserved manifest, STOP.

## Step 3 — Create integration branch

Create the branch only after the above gates pass:

```powershell
git switch -c demo-frontend-integration
```

Do not create or modify any GitLab branch.

## Step 4 — Import the sanitized application snapshot

Copy the sanitized staging application contents into:

```text
mdc-catalog/demo-frontend/
```

Rules:

- use the sanitized staging tree as the source, not `template-frontend`;
- preserve application file contents exactly unless a path must be adjusted purely because of the import location;
- do not perform API cleanup in this task;
- do not add credential-bearing orchestration material;
- do not add dependency/build output;
- do not import original frontend `.git` history;
- retain the staging-only provenance/readme material for this first import if it is present.

After copying, compare imported application files against the sanitized staging hashes. Explain any deliberate difference. There should normally be none.

## Step 5 — Import approved historical frontend reports

Copy the 30 sanitized historical reports into:

```text
mdc-catalog/docs/Demo_Frontend/Implementation_History/
```

These reports are historical evidence. Do not rewrite them to make old statements look current. Their historical API assumptions and earlier implementation states must remain traceable.

Do not place them inside the runtime frontend source tree.

## Step 6 — Add import provenance and release-boundary documentation

Create:

```text
mdc-catalog/docs/Demo_Frontend/00_frontend_sanitized_snapshot_import_provenance.md
```

It must record, without secrets:

- purpose of the demo frontend;
- explicit statement that it is not the real CMM;
- original GitLab repository URL;
- source branch and source HEAD `832ad57265bce0889ebea58bc69c031c3b394ee7`;
- why old Git history was not imported;
- preservation date `2026-09-09`;
- preservation root path for the local operator only;
- target GitHub path;
- count of imported application files and historical reports;
- major exclusions;
- security boundary: credential-bearing GitLab history remains outside GitHub;
- GitHub becomes controlled development source after approval/merge;
- GitLab remains historical/official release repository;
- future GitLab releases must use clean temporary checkout + reviewed file synchronization, not subtree push and not permanent GitLab remote in the normal `mdc_v1` worktree.

Also create:

```text
mdc-catalog/docs/Demo_Frontend/01_frontend_github_to_gitlab_release_mapping.md
```

It should document the intended mapping at minimum:

```text
GitHub: mdc-catalog/demo-frontend/**
    -> GitLab: subsystem/frontend/**

GitHub: selected/sanitized integration files only if explicitly approved
    -> GitLab: their documented original locations

GitHub-only master/provenance documentation
    -> NOT synchronized to GitLab product tree by default
```

Include a clear release procedure that requires a fresh GitLab checkout, release branch, secret scan, build/lint/test gate, diff review, explicit approval, and normal GitLab merge review. Never force-push GitLab.

## Step 7 — Ignore-rule review

Inspect the existing `mdc_v1` ignore rules.

Only if necessary, make the smallest safe update to ensure the imported frontend cannot accidentally track:

```text
node_modules/
.next/
out/
dist/
build/
coverage/
.env
.env.*
.vscode/
.idea/
.DS_Store
*.log
```

Preserve tracked safe example files where appropriate (for example `*.example` if already used). Do not broadly ignore legitimate repository documentation or source files.

Any ignore-file modification must be explicitly listed in the final report.

## Step 8 — Post-import safety verification

Before staging anything, verify:

- original `template-frontend` status/HEAD/remotes are unchanged;
- no GitLab remote was added to `mdc_v1`;
- imported runtime application is under `mdc-catalog/demo-frontend/`;
- 30 reports exist under `mdc-catalog/docs/Demo_Frontend/Implementation_History/`;
- no `.git` directories exist inside imported frontend;
- no forbidden editor/build/dependency/environment/credential files are present;
- no known trusted MDC lifecycle service token identifier/value is present in browser code;
- no raw Keycloak credential-bearing realm export is present;
- no `/api/v1` is present in active imported frontend application code;
- canonical public MDC endpoints remain represented as expected;
- staging-to-import hash comparison passes for imported source files.

Run the same safe secret-risk pattern scan again over all files proposed for commit. Print only path, key/identifier, and risk category. If any likely secret value is detected, STOP before staging.

## Step 9 — Review the complete Git change set

Run and inspect:

```powershell
git status --short
git diff --stat
git diff --check
```

Then stage only approved frontend import/documentation/ignore paths.

After staging inspect:

```powershell
git diff --cached --stat
git diff --cached --name-status
git diff --cached --check
```

Review the staged set for:

- unexpected files;
- secrets;
- local preservation artifacts;
- generated output;
- unrelated backend changes;
- accidental deletions;
- unexpected binary archives.

Do not stage anything from:

```text
C:\Users\Elahi\Desktop\mdc_frontend_preservation\2026-09-09
```

except the intentionally recreated non-sensitive provenance facts in repository documentation.

## Step 10 — Commit and push integration branch only

If and only if all gates pass, commit with a concise message such as:

```text
feat: import sanitized MDC demo frontend snapshot
```

Push only the integration branch to the personal GitHub origin:

```powershell
git push -u origin demo-frontend-integration
```

Do NOT:

- merge to `main`;
- force-push;
- push to GitLab;
- create GitLab commits;
- modify the original frontend repository.

After push, verify local branch and `origin/demo-frontend-integration` point to the same commit.

## Step 11 — Do not perform cleanup yet

Do not fix the following in this task; only confirm they remain known next-step items:

- stale lifecycle helper paths;
- nonexistent provider collection helper;
- Axios `error.message` normalization;
- response headers/ETag access;
- lifecycle bearer/actor/If-Match handling;
- static consumer filters;
- localhost runtime default;
- accidental page routes;
- demo security boundary;
- missing tests/CI.

These will be handled in a separate `05_frontend_...` cleanup/validation milestone.

## Required final report

Return exactly a report titled:

```text
# FRONTEND GITHUB SANITIZED SNAPSHOT IMPORT REPORT
```

Include:

### 1. Repository gate
- pull/status result
- starting `main` commit
- integration branch
- GitHub origin verification
- GitLab remote added: NO

### 2. Sanitized source verification
- staging source used
- staging hash verification
- application file count
- historical report count
- forbidden files found
- secret-risk scan result

### 3. Import result
- target application path
- target historical reports path
- imported application count
- imported reports count
- hash comparison result
- provenance docs created
- ignore rules changed or unchanged

### 4. Security boundary
- original Git history imported: NO
- credential-bearing files imported: NO
- `.env*` imported: NO
- raw realm credential export imported: NO
- secrets printed: NO
- source credentials rotated: NO

### 5. Source repository integrity
- frontend HEAD unchanged
- frontend worktree unchanged
- frontend remotes unchanged
- GitLab writes: NONE

### 6. Git review gates
- `git diff --check`
- staged-path review
- secret-risk scan over staged set
- unrelated backend changes: NONE

### 7. Git result
- integration commit SHA
- push to `origin/demo-frontend-integration`
- local/remote synchronized
- `main` merged: NO
- GitLab push: NO

### 8. Deferred cleanup items
List the known API/config/security/test items preserved for `05_frontend_...`.

### 9. Final gate

End with exactly one of:

```text
FRONTEND GITHUB SANITIZED SNAPSHOT IMPORT: PASS
READY_FOR_FRONTEND_API_CONFIG_CLEANUP: YES
```

or a clear FAIL/BLOCKED result with no unsafe partial push.
