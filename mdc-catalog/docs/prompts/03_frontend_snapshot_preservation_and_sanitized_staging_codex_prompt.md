# Codex Prompt — Frontend Snapshot Preservation and Sanitized Staging

## Role

Act as a careful repository migration and security engineer. Your task is to preserve the current MaaSAI demo frontend working state without changing the source repository, construct a sanitized staging snapshot outside both repositories, and produce evidence that the snapshot is safe and complete enough for the next GitHub import milestone.

This is **not yet the GitHub import milestone**. Do not modify `mdc_v1`, do not modify the frontend repository, do not change Git remotes, do not commit, do not push, and do not touch GitLab.

## Source repositories

Frontend source repository:

`C:\Users\Elahi\Desktop\template-frontend`

MDC repository:

`C:\Users\Elahi\Desktop\mdc_v1`

Expected frontend source baseline from the accepted read-only audit:

- branch: `main`
- HEAD: `832ad57265bce0889ebea58bc69c031c3b394ee7`
- dirty working tree containing the MDC demo implementation

Expected MDC baseline before this milestone:

- clean `main`
- personal GitHub `origin`
- latest prompt commit available after `git pull --ff-only`

If either baseline materially differs, stop and report instead of guessing.

## Accepted strategy

The accepted planning decision is:

`SANITIZED_SNAPSHOT_IMPORT_RECOMMENDED`

The MaaSAI GitLab repository remains the historical/official release repository. The personal GitHub `samola4real/mdc_v1` repository will become the controlled daily development source only after a sanitized snapshot is reviewed and imported in a later milestone.

Do **not** use `git subtree`, `git submodule`, history rewrite, force push, or unrelated-history merge.

## Hard safety constraints

You MUST obey all of the following:

1. Do not edit any file under `C:\Users\Elahi\Desktop\template-frontend`.
2. Do not edit any file under `C:\Users\Elahi\Desktop\mdc_v1`.
3. Do not run `git add`, `git commit`, `git push`, `git reset`, `git checkout`, `git switch`, `git clean`, `git restore`, `git stash`, or remote-changing commands in the frontend repository.
4. Do not change Git remotes in either repository.
5. Do not fetch from or push to GitLab.
6. Do not install npm packages or global tools.
7. Do not run a command that prints credential values.
8. Do not copy credential-bearing files into the sanitized staging tree.
9. Do not rotate credentials in this milestone.
10. Do not delete anything from either repository.
11. Do not create a frontend Git safety branch; the preservation artifacts below are the safety mechanism for this milestone.
12. Never display the contents of `.env.keycloak`, Keycloak client secrets, user passwords, database passwords, tokens, or any suspected secret.

## Preservation/staging location

Use a new local directory outside both repositories:

`C:\Users\Elahi\Desktop\mdc_frontend_preservation\2026-09-09`

If this directory already exists, do not overwrite existing evidence. Create a timestamped subdirectory under it and report the exact path.

Inside the selected preservation root create:

```text
manifest/
patches/
untracked-source/
sanitized-staging/
reports/
```

The preservation directory must never be added to either Git repository.

## Step 1 — Reconfirm source state

Read-only checks only.

Record:

- frontend repository root
- current branch
- current HEAD
- `git status --short`
- tracked modified paths
- untracked paths relevant to the MDC demo
- frontend remote names and URLs
- MDC branch/HEAD/status

Do not print credential file contents.

Expected important current frontend dirty paths include:

Tracked modifications:

- `subsystem/frontend/public/config.js`
- `subsystem/frontend/src/config/routes.js`
- `subsystem/frontend/src/config/runtimeConfig.js`
- `subsystem/frontend/src/layout/AppMenu.js`

Relevant untracked content:

- `docs/`
- `subsystem/frontend/src/components/mdc/`
- `subsystem/frontend/src/pages/demo/`
- `subsystem/frontend/src/services/mdc/`

Exclude `.vscode/`.

If major expected MDC demo directories are missing, stop.

## Step 2 — Create preservation manifest

Create a manifest under `manifest/` containing only non-secret metadata:

- source repository path
- source GitLab repository URL
- source branch
- source HEAD
- timestamp
- complete dirty-path inventory
- intended import scope
- excluded scope
- SHA-256 hashes for preservation artifacts created later

Do not include secret values.

Use a clear filename such as:

`frontend_source_manifest.md`

## Step 3 — Preserve tracked modifications

From the frontend repository, create a binary-capable patch of current tracked working-tree modifications without altering the repository.

Preferred command semantics:

`git diff --binary HEAD -- <approved tracked paths>`

Write it to:

`patches/frontend_tracked_worktree.patch`

Do not include unchanged credential-bearing files merely because they are tracked.

Record a SHA-256 hash for the patch.

## Step 4 — Preserve approved untracked MDC work

Copy only the approved untracked MDC implementation/report material into `untracked-source/`, preserving relative paths:

- `docs/`
- `subsystem/frontend/src/components/mdc/`
- `subsystem/frontend/src/pages/demo/`
- `subsystem/frontend/src/services/mdc/`

Do not copy:

- `.vscode/`
- `.idea/`
- dependency/build/cache output
- `.env*`
- credential exports
- logs
- archives
- secret-scan output containing values

Calculate SHA-256 hashes for the preserved files or for a deterministic archive if you create one. If archiving is used, do not delete the copied source preservation tree.

## Step 5 — Secret-risk path scan

Perform a non-destructive scan over:

- the intended frontend product source
- approved untracked reports
- tracked modifications

Use an already-installed secret scanner if available. Do not install one.

If no dedicated scanner is installed, use cautious filename/key-name/pattern scanning. Output only:

- path
- line number where safe
- suspected key/variable name or category

Never print the suspected value.

Known high-risk source paths that MUST NOT enter the sanitized staging tree:

- `orchestration/.env.keycloak`
- `orchestration/keycloak/realm-import/maasai-realm.json`

If additional credential-bearing files are found, exclude them and record them in the report.

## Step 6 — Construct sanitized staging tree

Create:

`sanitized-staging/demo-frontend/`

The staging tree is a clean snapshot for the future `mdc-catalog/demo-frontend/` path.

### Required application scope

Promote the **contents** of:

`template-frontend/subsystem/frontend/`

directly into:

`sanitized-staging/demo-frontend/`

so the future application root contains items such as:

```text
package.json
package-lock.json
next.config.js
jsconfig.json
.eslintrc.json
Dockerfile
docker-compose.yml
Makefile
public/
src/
```

The staging snapshot must reflect the current working state, including the four tracked modifications and the untracked MDC components/pages/services.

Because the source repository is dirty, construct the staging tree from the current filesystem state, not only from `HEAD`.

### Required exclusions

Do not stage:

- `.git/`
- `.idea/`
- `.vscode/`
- `.DS_Store`
- `node_modules/`
- `.next/`
- `dist/`
- `build/`
- `out/`
- coverage/cache/log files
- `.env`
- `.env.*`
- credential-bearing orchestration files
- raw realm credential exports
- generated theme ZIPs unless proven required by the application build
- temporary preservation files

### Browser runtime configuration

The audit found `public/config.js` and `src/config/runtimeConfig.js` to contain browser runtime configuration and no lifecycle service token. Preserve them only if the secret scan confirms they are browser-safe.

Never add a trusted lifecycle service token to browser code.

## Step 7 — Historical frontend reports staging

Create:

`sanitized-staging/Implementation_History/`

Copy the approved frontend `docs/` reports there as historical/reference evidence.

These are intended later for:

`mdc-catalog/docs/Demo_Frontend/Implementation_History/`

Do not mix them into the application source tree.

## Step 8 — Create safe integration metadata

Inside `sanitized-staging/demo-frontend/` create a **staging-only** draft README named:

`README_SANITIZED_SNAPSHOT_DRAFT.md`

It must state:

- this is a MaaSAI MDC demonstration frontend, not the real Cloud MaaS Marketplace
- source GitLab repository URL
- source HEAD `832ad57265bce0889ebea58bc69c031c3b394ee7`
- snapshot date
- historical GitLab history is intentionally not imported because credential-bearing objects exist in history
- GitHub will become the controlled development source only after a later approved import
- GitLab remains the historical/official release repository
- no trusted lifecycle service token may be placed in browser code

Do not claim this staging snapshot has already been imported into GitHub.

Also create a staging-only mapping document:

`reports/frontend_future_path_mapping.md`

At minimum map:

- staging `demo-frontend/*` → future GitHub `mdc-catalog/demo-frontend/*`
- staging `Implementation_History/*` → future GitHub `mdc-catalog/docs/Demo_Frontend/Implementation_History/*`
- future approved GitHub application files → GitLab `subsystem/frontend/*` during reviewed release synchronization

## Step 9 — Sanitized staging validation

Run checks that do not install dependencies and do not mutate the source repositories.

Validate:

- `package.json` exists at the staging app root
- lockfile exists
- `src/pages/demo/` exists with the expected four demo files
- `src/components/mdc/` exists
- `src/services/mdc/` exists
- the four tracked source modifications are represented in staging
- no `.git`, editor directories, dependency/build directories, `.env*`, or known credential-bearing realm files exist in staging
- no `/api/v1` strings exist in active application code unless clearly historical/comment-only
- current canonical consumer endpoints are identifiable:
  - `/api/health`
  - `/api/catalog/filters`
  - `/api/service-discovery/search`
- stale unused lifecycle helpers are preserved as current source evidence, but clearly listed for the next cleanup milestone; do not edit them here

Run a second secret-risk scan over the final sanitized staging tree.

If a likely credential remains, stop with FAIL and do not mark the staging snapshot ready.

## Step 10 — File inventory and hashes

Produce:

- total staged application file count
- total historical report file count
- excluded sensitive path list
- top-level staging tree
- SHA-256 manifest for all staged files, or a deterministic equivalent

Do not hash-print secret source files because they must not be staged; simply record their excluded paths.

Update `manifest/frontend_source_manifest.md` with the preservation artifact hashes and sanitized staging summary.

## Step 11 — Verify no source repository mutation

At the end, reconfirm:

Frontend:

- same branch
- same HEAD
- exactly the same tracked/untracked status as before this milestone
- same remotes

MDC:

- same branch
- same HEAD
- clean worktree
- same remotes

No commits or pushes must have occurred.

## Security note

The audit established that the frontend Git history contains credential-bearing objects. This milestone does not fix or rewrite that history and does not rotate secrets. It only ensures those objects and current credential-bearing files are excluded from the future GitHub snapshot.

Any still-active historical credentials must be rotated separately through the appropriate owners before or as part of operational cleanup. Do not attempt rotation in this task.

## Required final report

Return exactly one structured Markdown report titled:

`# FRONTEND SNAPSHOT PRESERVATION AND SANITIZED STAGING REPORT`

Include:

### 1. Safety gate

- frontend modified: YES/NO
- mdc_v1 modified: YES/NO
- remotes changed: YES/NO
- commits/pushes: NONE or details
- secrets printed: NO

### 2. Source baseline

- frontend branch/HEAD
- source status summary
- MDC branch/HEAD/status

### 3. Preservation artifacts

- preservation root
- patch path and hash
- untracked preservation summary
- manifest path

### 4. Secret-risk findings

- scanner/method used
- excluded known sensitive paths
- additional excluded sensitive paths
- values exposed: NO

### 5. Sanitized application snapshot

- staging path
- application file count
- key required directories/files present
- tracked modifications represented: PASS/FAIL
- untracked MDC demo represented: PASS/FAIL

### 6. Historical reports snapshot

- staging path
- report count

### 7. API/config observations retained for next cleanup

List, without fixing:

- stale lifecycle helper paths
- Axios error-envelope issue
- ETag/header limitation
- static consumer filter issue
- localhost/runtime-config issue
- accidental routes
- public/demo security boundary findings

### 8. Exclusion verification

Confirm staging contains none of:

- `.git`
- `.idea`
- `.vscode`
- dependency/build output
- `.env*`
- known credential-bearing realm import
- trusted lifecycle service token

### 9. Final staging secret scan

- PASS/FAIL
- suspected credential values printed: NO

### 10. Source repositories unchanged

- frontend HEAD/status/remotes unchanged: PASS/FAIL
- MDC HEAD/status/remotes unchanged: PASS/FAIL

### 11. Next-step readiness

State whether the snapshot is ready for the next milestone:

`READY_FOR_FRONTEND_GITHUB_IMPORT: YES/NO`

### 12. Final gate

If and only if all safety and staging checks pass, end with:

`FRONTEND SNAPSHOT PRESERVATION AND SANITIZED STAGING: PASS`

Otherwise end with:

`FRONTEND SNAPSHOT PRESERVATION AND SANITIZED STAGING: BLOCKED`

and explain the blocker without exposing secrets.
