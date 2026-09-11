# Codex Prompt — Vercel stale preview-branch cleanup

## Objective

Clean up the stale Vercel preview branch/deployment entry associated with the already-deleted GitHub branch `p3-p30-p31-release-deployment`, while preserving the current `main` production deployment and all production configuration.

This is a housekeeping task only. Do not change MDC application code, frontend code, backend code, repository history, database state, environment-variable values, domains, or production feature flags.

## Repository and platform context

- Personal GitHub repository: `https://github.com/samola4real/mdc_v1`
- Repository branch to keep: `main`
- Current repository policy: personal GitHub only; no GitLab work
- Vercel project: `maasai-mdc-v1`
- Production hostname to preserve: `https://maasai-mdc-v1.vercel.app`
- Stale Vercel branch shown in the dashboard: `p3-p30-p31-release-deployment`
- The GitHub branch `p3-p30-p31-release-deployment` has already been deleted.
- The current production/main deployment must remain untouched.

## Safety rules

1. Start read-only. Inspect first; mutate only after the target is unambiguous.
2. Verify the local repository is on `main`, clean, and synchronized with `origin/main`.
3. Verify `origin` is the personal GitHub repository above.
4. Verify GitHub no longer has branch `p3-p30-p31-release-deployment`.
5. Confirm the Vercel project identity from the local `.vercel/project.json`, Vercel CLI project inspection, or equivalent safe command.
6. Before deleting anything, enumerate the Vercel deployments/aliases associated with:
   - `main`
   - `p3-p30-p31-release-deployment`
7. Treat `main`, the production deployment, `maasai-mdc-v1.vercel.app`, production aliases, project settings, environment variables, Neon/PostgreSQL configuration, Fuseki configuration, and trusted lifecycle secrets as protected.
8. Never print secret values. Do not run commands that dump all environment-variable values.
9. Do not redeploy production merely to clean the stale branch entry unless Vercel explicitly requires it and you stop for approval first.
10. Do not remove the Vercel project.
11. Do not remove the `main` deployment or any production deployment.
12. Do not change GitHub branches, tags, history, or remotes.
13. No GitLab interaction.

## Required procedure

### A. Repository gate

Run safe checks similar to:

```powershell
git status
git branch --show-current
git remote -v
git fetch --prune origin
git branch -a
```

Expected repository state:

- branch `main`
- clean worktree
- `origin/main` synchronized
- stale GitHub feature branches already removed

If this is not true, stop and report the discrepancy.

### B. Inspect the Vercel project

Use the installed Vercel CLI and/or connected Vercel tooling to identify the linked project and current deployment state. It is acceptable to inspect help text first so that command semantics are confirmed.

Gather, without revealing secrets:

- project name / project ID
- account/team scope
- current production deployment URL and deployment ID
- current `main` deployment/branch metadata
- stale preview deployment(s), branch alias(es), or branch environment record(s) tied specifically to `p3-p30-p31-release-deployment`
- whether the stale dashboard row is backed by one current preview deployment, a branch alias, or another Vercel branch-level object

Do not infer the deletion target from display text alone. Confirm it from Vercel metadata.

### C. Clean only the stale preview branch

Once the target is confirmed, remove only the Vercel object(s) needed to clear the stale `p3-p30-p31-release-deployment` active-branch entry.

Preferred behavior:

- If the row is caused by a stale branch alias, remove only that branch alias.
- If it is caused by the latest preview deployment for that deleted branch and Vercel requires deployment deletion to clear the row, remove only the preview deployment(s) belonging to `p3-p30-p31-release-deployment`.
- Preserve historical production deployments.
- Do not delete unrelated previews from other branches.

If Vercel presents multiple objects and it is unclear which one can be safely removed, stop before mutation and report what needs approval.

### D. Post-cleanup verification

After cleanup, verify:

1. `main` remains the active production branch/deployment.
2. `https://maasai-mdc-v1.vercel.app/api/health` still returns HTTP 200 and contract `1.0`.
3. `GET /api/catalog/filters` still returns HTTP 200.
4. A read-only canonical `POST /api/service-discovery/search` smoke request still returns HTTP 200.
5. The stale Vercel branch/deployment/alias for `p3-p30-p31-release-deployment` is absent from Vercel branch/deployment listings or otherwise no longer active.
6. Production domain/alias is unchanged.
7. No environment-variable, database, Fuseki, or project-setting mutation occurred.
8. Git repository remains clean and unchanged.

Do not run trusted lifecycle writes, demo mutation endpoints, database writes, RDF regeneration, Fuseki reload, or any destructive application operation as part of this validation.

## Documentation / Git rule

This is an infrastructure cleanup only. Do **not** create application-code changes. Do not make a Git commit unless an explicit cleanup report file is requested later. The current prompt itself is already stored in Git.

## Required final report

Return exactly a concise report headed:

```text
# VERCEL STALE PREVIEW BRANCH CLEANUP REPORT
```

Include:

### 1. Repository gate
- branch
- current SHA
- worktree state
- origin verification

### 2. Vercel target identified
- project
- production deployment/alias preserved
- stale branch name
- exact stale deployment/alias/object identified

### 3. Cleanup action
- what was removed
- what was deliberately not touched

### 4. Verification
- stale branch absent/inactive
- production health result
- filters result
- search result
- production alias unchanged
- Git unchanged

### 5. Final gate

If everything is correct, end with:

```text
VERCEL STALE PREVIEW BRANCH CLEANUP: PASS
VERCEL ACTIVE BRANCH STATE: MAIN ONLY
PRODUCTION DEPLOYMENT: PRESERVED
```

If any safety condition is uncertain, do not delete anything and end with:

```text
VERCEL STALE PREVIEW BRANCH CLEANUP: BLOCKED
```

with the exact reason.
