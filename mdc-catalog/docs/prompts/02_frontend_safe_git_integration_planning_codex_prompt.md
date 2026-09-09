# Codex Prompt — Frontend Safe Git Integration Planning (Read-Only)

## Purpose

Perform a second-stage **read-only integration planning audit** for the MaaSAI MDC demo frontend at:

`C:\Users\Elahi\Desktop\template-frontend`

and the MDC repository at:

`C:\Users\Elahi\Desktop\mdc_v1`

The first frontend audit already established that:

- the frontend repository is connected to the MaaSAI GitLab repository;
- the working tree is dirty;
- most of the MDC demo implementation is currently untracked;
- tracked files contain credential-bearing Keycloak material;
- the user wants day-to-day development controlled in personal GitHub (`samola4real/mdc_v1`) and only deliberate, reviewed releases pushed to MaaSAI GitLab;
- the intended frontend location in the MDC repository is `mdc-catalog/demo-frontend/`;
- the final frontend master manual should later live at `mdc-catalog/docs/Demo_Frontend/MDC_Demo_Frontend_Comprehensive_Implementation_Report_and_User_Manual.md`.

This task must determine the **safest exact Git integration strategy before any files, remotes, branches, credentials, or histories are changed**.

## Critical safety rule

This is a **READ-ONLY planning task**.

Do NOT:

- edit frontend files;
- edit MDC files;
- stage or commit anything;
- create branches;
- fetch/pull/push any remote;
- change any Git remote;
- install packages;
- run build/lint/test commands that create output/cache files;
- copy frontend files into `mdc_v1`;
- rewrite Git history;
- rotate credentials;
- delete credentials;
- print credential values, tokens, passwords, client secrets, database passwords, or secret-bearing file contents.

You may inspect filenames, Git metadata, status, diffs, file structures, and configuration keys without revealing secret values.

## Important change from the initial subtree assumption

The first audit recommended a history-preserving subtree, but it also discovered that tracked frontend history contains credential-bearing Keycloak material.

Therefore, **do not assume an unsquashed history-preserving subtree is still safe**.

Explicitly compare these two practical strategies:

### Strategy A — sanitized snapshot inside `mdc_v1`

- Preserve the GitLab repository as the authoritative historical/upstream frontend repository.
- Prepare a sanitized current frontend baseline for import into `mdc_v1/mdc-catalog/demo-frontend/`.
- Do not import historical secret-bearing Git objects into personal GitHub.
- Develop normally in personal GitHub after import.
- For approved MaaSAI releases, synchronize the approved `demo-frontend` tree into a clean GitLab checkout/branch, review the diff, then commit/push through normal GitLab review.

### Strategy B — sanitized subtree relationship

- Use a subtree only if a safe sanitized baseline can be established without importing historical credential-bearing objects into GitHub.
- Explain whether future subtree split/push can safely and cleanly update the existing GitLab history.
- If it would create unrelated-history/non-fast-forward/reconciliation problems, state that clearly.

Also briefly reassess submodule and separate-GitHub-repo options only if they materially improve safety.

## Required analysis

### 1. Confirm current state without mutation

Report:

- frontend HEAD, branch, dirty/clean state;
- modified tracked paths;
- untracked paths relevant to the MDC demo;
- whether `.vscode/` should be excluded from the intended product baseline;
- MDC repo HEAD/branch/status;
- current frontend GitLab remote name and URL;
- no network fetch is required.

### 2. Current demo baseline inclusion plan

Classify current frontend working-tree content into:

- **MUST INCLUDE** in future `mdc-catalog/demo-frontend/`;
- **SHOULD INCLUDE**;
- **HISTORICAL/REFERENCE ONLY**;
- **MUST EXCLUDE**;
- **REQUIRES SECURITY REMEDIATION BEFORE INCLUDE**.

At minimum assess:

- `subsystem/frontend/`;
- `orchestration/`;
- `documentation/`;
- root README;
- untracked `docs/` reports;
- `.vscode/`;
- `.idea/`;
- build outputs/caches if present;
- `node_modules` if present;
- `.env*` files;
- Keycloak realm-import material.

Do not reveal secret values.

### 3. Secret/history risk analysis

Without printing secrets, determine:

- which currently tracked paths contain credential-bearing content;
- whether those paths existed in earlier commits/history;
- whether an unsquashed import of frontend history into GitHub would likely make old secret-bearing objects reachable from GitHub history;
- whether deleting/redacting only the current versions would be insufficient because old history remains;
- whether a full history rewrite would be needed to preserve history safely;
- why history rewriting is undesirable for the shared MaaSAI GitLab repository;
- whether a sanitized snapshot therefore provides a safer boundary.

Do not run destructive history-rewrite tools.

### 4. Preservation of the current dirty demo

The current demo implementation must not be lost.

Design the safest future procedure to preserve:

- all approved modified tracked files;
- all approved untracked MDC demo pages/components/services/reports;
- current source state before any cleanup;
- original GitLab HEAD reference `832ad57265bce0889ebea58bc69c031c3b394ee7` as provenance.

Explain whether the preservation should happen:

- on a new local frontend safety branch;
- through a local patch/archive/snapshot;
- or another reversible mechanism.

No preservation action should actually be executed in this task.

### 5. Recommended GitHub directory layout

Evaluate and confirm or revise:

```text
mdc_v1/
└── mdc-catalog/
    ├── backend/
    ├── data/
    ├── demo-frontend/
    ├── docs/
    │   ├── Demo_Frontend/
    │   └── MDC_Comprehensive_Implementation_Report_and_User_Manual.md
    └── scripts/
```

Explain whether the existing frontend top-level structure should be imported wholesale under `demo-frontend/`, e.g.:

```text
mdc-catalog/demo-frontend/
├── orchestration/
├── subsystem/
├── documentation/
├── README.md
└── ...
```

or whether a narrower structure is safer/cleaner.

### 6. GitLab release workflow design

The user explicitly wants:

```text
personal GitHub / mdc_v1
    -> normal frontend development and review
    -> approved release only
    -> MaaSAI GitLab frontend repository
```

Design a future release workflow that minimizes accidental GitLab pushes.

Prefer a process like:

1. keep normal `origin` of `mdc_v1` pointing only to personal GitHub;
2. do not add a permanently pushable GitLab remote to the daily MDC working copy unless necessary;
3. when a release is approved, use a temporary clean checkout/worktree of the MaaSAI GitLab frontend repository;
4. copy/synchronize only approved frontend product files from `mdc-catalog/demo-frontend/`;
5. explicitly exclude GitHub-only master docs, secrets, local editor files, caches, and generated outputs;
6. review `git status` and `git diff` in the GitLab checkout;
7. create a GitLab release branch;
8. commit/push only after explicit approval;
9. use the normal GitLab review/merge process;
10. never force-push or replace GitLab history.

Assess whether this is safer than direct `git subtree push` for the present repository history.

### 7. Future integration branch in `mdc_v1`

Recommend a temporary integration branch name, preferably:

`demo-frontend-integration`

Explain the exact future sequence:

- create branch from current `main`;
- import sanitized frontend baseline;
- add/update ignore rules;
- add provenance/readme documentation;
- run secret scan;
- install/use existing dependencies only as appropriate;
- lint/build;
- verify frontend routes and current MDC search API behavior;
- review diff;
- merge to `main` only after passing gates.

Do not create the branch in this task.

### 8. Master document timing

Decide whether the comprehensive frontend manual should be drafted:

- before Git integration;
- immediately after sanitized import;
- or after a minimal API/config cleanup pass.

The intended document is:

`mdc-catalog/docs/Demo_Frontend/MDC_Demo_Frontend_Comprehensive_Implementation_Report_and_User_Manual.md`

The recommended answer should favor the point at which the repository provides the most trustworthy and stable evidence without delaying documentation unnecessarily.

### 9. Frontend/API cleanup sequencing

Based on the first audit, classify these as:

- fix before import;
- fix immediately after import;
- document-only for now;
- future CMM work.

Items:

- stale `/api/provider-publication/validate` helper;
- stale `/api/provider-publication/publish` helper;
- nonexistent `GET /api/providers` helper;
- lack of bearer/actor/ETag support in browser lifecycle client;
- static consumer filter vocabularies;
- browser-generated demo result overlay;
- public/demo role guard boundary;
- outdated Axios error normalization;
- lack of response-header access for ETags;
- localhost API default;
- missing tests/CI;
- accidental routable page components.

Do not implement fixes.

## Required decision output

End with one clear recommendation among:

- `SANITIZED_SNAPSHOT_IMPORT_RECOMMENDED`
- `SANITIZED_SUBTREE_RECOMMENDED`
- `SUBMODULE_RECOMMENDED`
- `SEPARATE_GITHUB_REPO_RECOMMENDED`
- `BLOCKED_PENDING_SECURITY_DECISION`

If recommending a sanitized snapshot, explicitly state that the GitLab repository remains the historical/release source and that the GitHub monorepo becomes the controlled development source after import.

## Required report format

Return exactly this structure:

```text
# FRONTEND SAFE GIT INTEGRATION PLANNING REPORT

## 1. Safety gate
- frontend modified: NO
- mdc_v1 modified: NO
- remotes changed: NO
- commits/pushes: NONE
- secrets printed: NO

## 2. Confirmed current state
- frontend HEAD/branch: ...
- frontend worktree: ...
- MDC HEAD/branch: ...
- GitLab remote: ...

## 3. Baseline inclusion matrix
- MUST INCLUDE: ...
- SHOULD INCLUDE: ...
- HISTORICAL/REFERENCE ONLY: ...
- MUST EXCLUDE: ...
- SECURITY REMEDIATION REQUIRED: ...

## 4. Secret/history assessment
- current tracked credential-bearing paths: <paths only>
- historical exposure risk: LOW/MEDIUM/HIGH
- unsquashed history import safe: YES/NO
- history rewrite required to preserve history safely: YES/NO
- conclusion: ...

## 5. Integration strategy comparison
- sanitized snapshot: ...
- sanitized subtree: ...
- submodule: ...
- separate GitHub repo: ...

## 6. Recommended architecture
- GitHub development source: ...
- GitLab historical/release source: ...
- target frontend path: ...
- integration branch: ...

## 7. Exact future preservation/import sequence
1. ...
2. ...

## 8. Exact future GitLab release sequence
1. ...
2. ...

## 9. Frontend cleanup sequencing
- before import: ...
- immediately after import: ...
- document-only: ...
- future CMM work: ...

## 10. Master-document timing
- recommendation: ...
- rationale: ...

## 11. User approvals required before execution
- ...

## 12. Final decision
<ONE_REQUIRED_DECISION_TOKEN>

FRONTEND SAFE GIT INTEGRATION PLANNING: PASS/FAIL
```

## Final reminder

This task is planning only. Do not mutate either repository or any infrastructure. Do not reveal credentials.
