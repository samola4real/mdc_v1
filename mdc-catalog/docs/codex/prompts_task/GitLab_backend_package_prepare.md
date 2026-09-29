# Prepare official MaaSAI GitLab backend package — no commit/push

## Goal

Prepare the already-cloned empty official MaaSAI GitLab backend working tree from the accepted MDC source, using the pre-reviewed transfer manifest. This is a file-transfer/packaging task, not a new architecture or refactor task.

## Source of truth

GitHub repository:

`https://github.com/samola4real/mdc_v1`

Use exact accepted source commit:

`7f72beb5d33982c63dc46b666d4ce9972fbf8662`

Read and follow:

`mdc-catalog/docs/codex/GitLab_backend_transfer_manifest.md`

Do not re-research the whole repository. The manifest already defines what to include/exclude and why.

## Destination

Existing empty MaaSAI GitLab clone:

`C:\Users\Elahi\Desktop\MaaSAI-GitLab\mdc-backend`

**Preserve the destination `.git` directory.**

Before modifying the destination:
1. verify it is the intended GitLab clone;
2. verify there are no unexpected tracked/source files already present;
3. if it is not effectively empty apart from Git metadata, stop and report instead of overwriting anything.

## Execution

1. Obtain the source files from the exact accepted GitHub commit in a clean/isolated way. Do not alter, stash, reset, or overwrite the user's original `C:\Users\Elahi\Desktop\mdc_v1` checkout or its unrelated local changes.

2. Populate the destination exactly according to `GitLab_backend_transfer_manifest.md`.

3. Important fixed decisions:
   - no `demo-frontend/`;
   - no `backend/tests/`;
   - no app-level test files;
   - no source root `scripts/`;
   - no smoke/verification/milestone scripts;
   - no Codex prompts/reports or historical milestone documentation;
   - no old `/api/v1/` contract docs;
   - copy only `data/curated/**` from source data;
   - copy all current ontology assets;
   - preserve Django migrations and verified Django management commands;
   - do not copy `data/demo`, `data/generated`, or `data/staging`;
   - do not copy the empty source `docker-compose.yml`;
   - do not copy secrets or a real `.env`.

4. Do **not** create a root `scripts/` directory unless a genuinely necessary non-test operational helper is proven missing. Prefer the existing Django management commands. For this first package, omission of `scripts/` is expected.

5. Create the clean backend-only documentation package and root README exactly as defined in the manifest. New partner/backend docs belong only in the destination `docs/`; do not copy the source development-history tree.

6. Copy only the accepted M6 generic Marketplace Postman collection/environment into `docs/postman/`, renaming them generically as specified in the manifest. Do not copy M5/M5-A evidence collections.

7. Create a backend `Dockerfile` and `.dockerignore` according to the manifest.
   - Python 3.12.
   - No secrets.
   - No Vercel-specific assumption.
   - Production-capable WSGI serving.
   - If a WSGI dependency such as Gunicorn is required, add it minimally to the appropriate Python dependency definition, document the change, and verify it.
   - Do not create `docker-compose.yml` unless a real, intentionally supported topology is needed; the expected result for this task is **no compose file**.

8. Create a backend-delivery `.gitignore` according to the manifest instead of copying the current minimal ignore file unchanged.

## Verification

Perform only package verification; do not add test code to the destination.

At minimum:

- inspect the final destination tree;
- verify forbidden folders/files are absent;
- scan for likely secrets/credentials;
- install dependencies in a temporary local environment if needed;
- run `python backend/manage.py check`;
- run `python backend/manage.py makemigrations --check --dry-run`;
- run migrations against a disposable local SQLite database;
- start the local backend and verify `GET /api/health` and `GET /api/catalog/filters`;
- build the Docker image;
- start the container with disposable/local-safe environment values and verify `GET /api/health`;
- confirm generated runtime files remain ignored/untracked.

Do not run or copy the source development test suite in this task.

## Git safety — mandatory stop

The destination is already a GitLab clone, but this task must **stop before staging or publishing**.

Do not run:
- `git add`
- `git commit`
- `git push`

Do not alter remotes.

It is fine to use read-only commands such as `git status`, `git remote -v`, and `git diff --no-index` where useful.

## Completion handoff

Return only a concise preparation summary containing:

1. exact source commit used;
2. destination path;
3. final top-level tree;
4. documentation files created;
5. Dockerfile status and any dependency change;
6. verification results;
7. secret/forbidden-file scan result;
8. `git status --short` of the destination;
9. any unresolved issue;
10. explicit confirmation: **nothing was staged, committed, or pushed to MaaSAI GitLab**.

Do not modify the personal GitHub repository as part of execution.
