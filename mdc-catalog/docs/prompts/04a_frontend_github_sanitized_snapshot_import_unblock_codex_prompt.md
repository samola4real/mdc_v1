# Codex Prompt — 04a Frontend GitHub Sanitized Snapshot Import Unblock

## Purpose

Complete the previously blocked sanitized frontend snapshot import after the user explicitly approved a **one-time, narrowly scoped exception** for inherited whitespace findings in the preserved snapshot.

This task resumes the already-staged import on the local branch:

```text
demo-frontend-integration
```

The previous import report established that the staged set is otherwise valid and safe, but `git diff --cached --check` returned nonzero only because the preserved source snapshot already contains inherited whitespace formatting:

- six preserved files with an inherited extra blank line at EOF;
- three preserved SCSS files with inherited trailing whitespace.

The user has explicitly approved accepting those inherited findings **for this initial baseline import only** so the first GitHub frontend commit remains byte-for-byte identical to the already-accepted sanitized staging snapshot.

This exception does **not** waive any other safety, secret, path, conflict-marker, or Git review gate.

## Fixed paths

MDC repository:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Original frontend repository — READ ONLY:

```text
C:\Users\Elahi\Desktop\template-frontend
```

Preservation root — READ ONLY:

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

Expected local integration branch:

```text
demo-frontend-integration
```

Expected branch base before the import commit:

```text
98b6c4578636e2d0cc972007dde3fcbe7f982fd9
```

Target application path:

```text
mdc-catalog/demo-frontend/
```

Target historical reports path:

```text
mdc-catalog/docs/Demo_Frontend/Implementation_History/
```

## Accepted prior evidence

The immediately preceding run reported:

```text
application files imported: 134
historical reports imported: 30
staged paths: 167
unexpected paths: 0
deletions: 0
archives: 0
secret-risk scan: PASS
unrelated backend changes: NONE
unstaged changes: NONE
original frontend repository unchanged: YES
GitLab writes: NONE
```

It also reported that the only blocking gate was inherited whitespace in the hash-locked sanitized snapshot.

## Non-negotiable safety rules

Do NOT:

- modify the original `template-frontend` repository;
- modify the preserved sanitized staging snapshot;
- normalize, trim, reformat, or otherwise alter the imported frontend files in this task;
- change Git remotes;
- add the MaaSAI GitLab repository as a remote;
- fetch from or push to GitLab;
- import frontend Git history;
- use subtree or submodule;
- rewrite history;
- force-push;
- merge to `main`;
- install or update packages;
- run `npm install`, `npm ci`, build, lint, or tests;
- perform the deferred API/config cleanup;
- rotate credentials;
- print any secrets, tokens, passwords, private keys, or connection strings;
- accept any new or unrelated `git diff --check` problem beyond the already identified inherited whitespace classes.

If any gate differs materially from the accepted prior report, STOP before commit/push and return BLOCKED.

## Step 1 — Confirm the resumed local state

From:

```powershell
cd C:\Users\Elahi\Desktop\mdc_v1
```

Inspect without modifying the staged import:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short --branch
git remote -v
git diff --cached --stat
git diff --cached --name-status
```

Requirements:

- current branch is `demo-frontend-integration`;
- local HEAD is still `98b6c4578636e2d0cc972007dde3fcbe7f982fd9` unless there is a clearly understood, safe prompt-only change that does not alter the staged import;
- the import remains staged and uncommitted;
- no unstaged application changes have appeared;
- no unexpected paths or deletions have appeared;
- `origin` is the personal GitHub repository;
- no GitLab remote was added.

Do not run `git reset`, `git restore`, `git checkout` on staged files, or any command that would disturb the accepted staged snapshot.

## Step 2 — Re-verify snapshot integrity and security

Re-run the same staging-to-import hash verification used in the previous task.

Confirm:

- all 134 imported application files that are governed by the sanitized staging manifest still match the preserved staging bytes;
- all 30 historical reports remain present in the intended documentation location;
- no `.git`, `.idea`, `.vscode`, `node_modules`, `.next`, build output, `.env*`, raw credential-bearing realm export, private-key material, or archive has entered the staged set;
- no original frontend Git objects/history were imported;
- no known trusted MDC lifecycle service-token value is present in browser code;
- active frontend application code contains no `/api/v1` path;
- canonical public MDC paths remain identifiable;
- safe secret-risk scan returns zero likely credential findings.

The scan must print only paths/identifiers/categories, never values.

If any of these checks fails, STOP.

## Step 3 — Validate the one-time whitespace exception precisely

Run:

```powershell
git diff --cached --check
```

The command is expected to return nonzero.

Inspect the output carefully. The exception is acceptable **only** when all findings are inherited whitespace corresponding to the already reported snapshot condition:

- six preserved files affected by an extra blank line at EOF; and
- three preserved SCSS files affected by trailing whitespace.

The exact number of output lines may be greater than nine if one SCSS file has more than one trailing-whitespace line. Evaluate by affected files and finding class, not merely by command exit code.

Confirm all of the following:

1. every finding is under the intended imported frontend snapshot/documentation set;
2. no conflict marker exists;
3. no malformed patch or other non-whitespace error exists;
4. there is no new whitespace issue outside the known inherited set;
5. fixing these findings would alter the byte-for-byte hash-locked initial snapshot.

Do **not** edit the files to make `git diff --cached --check` return zero in this task.

Record the affected paths and finding classes in the final report, but do not print file contents unless needed and never print secrets.

If the findings differ from the approved scope, STOP and return BLOCKED.

## Step 4 — Final staged-set review

Inspect:

```powershell
git diff --cached --stat
git diff --cached --name-status
git status --short
```

Confirm the expected staged set remains:

- 134 application files;
- 30 historical reports;
- 2 provenance/release-boundary documents;
- 1 root `.gitignore` update;
- 167 staged paths total;
- no deletions;
- no unrelated backend changes;
- no unstaged changes;
- no preservation artifacts accidentally staged.

If counts changed only because Git reports rename/copy metadata differently, explain and validate the exact paths before proceeding. Otherwise STOP on unexplained differences.

## Step 5 — Commit the exact sanitized baseline

Because the user explicitly approved this one-time inherited-whitespace exception, commit the staged set unchanged.

Use:

```text
feat: import sanitized MDC demo frontend snapshot
```

Do not amend or combine it with other work.

Immediately inspect:

```powershell
git show --stat --oneline --summary HEAD
git status --short --branch
```

The worktree should be clean after the commit.

## Step 6 — Push only the integration branch to personal GitHub

Push only:

```powershell
git push -u origin demo-frontend-integration
```

Do not push `main` and do not push anywhere except the personal GitHub `origin`.

After push verify:

```powershell
git rev-parse HEAD
git rev-parse origin/demo-frontend-integration
git status --short --branch
```

Local HEAD and `origin/demo-frontend-integration` must match.

Do not merge to `main` in this task.

## Step 7 — Source integrity recheck

Reconfirm the original frontend repository still has:

```text
branch: main
HEAD: 832ad57265bce0889ebea58bc69c031c3b394ee7
```

and retains the same dirty-path inventory/remotes as before.

Do not modify it.

Confirm GitLab writes remain `NONE`.

## Step 8 — Preserve cleanup boundary

Do not yet fix:

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

These remain for the next `05_frontend_...` milestone.

## Required final report

Return exactly:

```text
# FRONTEND GITHUB SANITIZED SNAPSHOT IMPORT UNBLOCK REPORT
```

Include:

### 1. Resume gate
- branch
- pre-commit HEAD
- staged path count
- unstaged changes
- GitHub origin verification
- GitLab remote present: NO

### 2. Integrity/security recheck
- application hash comparison
- historical report count
- forbidden path findings
- secret-risk scan
- original frontend Git history imported: NO

### 3. Approved whitespace exception
- `git diff --cached --check` exit status
- affected file count by category
- extra-EOF-blank-line file count
- SCSS trailing-whitespace file count
- conflict markers: NONE
- new/unapproved findings: NONE
- files normalized/edited to suppress warnings: NO
- exception scope: INITIAL SANITIZED BASELINE ONLY

### 4. Commit
- commit SHA
- commit message
- staged import committed unchanged: YES
- worktree clean after commit

### 5. Push
- pushed branch
- destination: personal GitHub origin
- local/remote SHA synchronized
- `main` merged: NO
- GitLab push: NO

### 6. Source repository integrity
- original frontend HEAD unchanged
- dirty-path inventory unchanged
- frontend remotes unchanged
- GitLab writes: NONE

### 7. Deferred cleanup
List the known `05_frontend_...` items.

### 8. Final gate

End with exactly:

```text
FRONTEND GITHUB SANITIZED SNAPSHOT IMPORT: PASS
READY_FOR_FRONTEND_API_CONFIG_CLEANUP: YES
```

or a clear BLOCKED result if any finding falls outside the explicitly approved exception.
