# MaaSAI GitLab backend transfer manifest

## Purpose

Prepare a clean backend-only MaaSAI MDC repository from the accepted personal GitHub source without transferring frontend code, development history, Codex material, historical milestone evidence, smoke/verification scripts, tests, generated runtime artifacts, or secrets.

This manifest is an operator/developer transfer aid only. **Do not copy this manifest into the official MaaSAI GitLab repository.**

## Source baseline

Repository: `https://github.com/samola4real/mdc_v1`

Accepted source branch: `main`

Accepted source commit at manifest preparation:

`2e49d7c8f7f70f440ae4e873b05cc259884586aa`

This commit includes accepted M6-A Marketplace integration/readiness work.

## Destination working tree

Local clone of the empty official MaaSAI GitLab repository:

`C:\Users\Elahi\Desktop\MaaSAI-GitLab\mdc-backend`

The first preparation pass must stop before `git add`, commit, or push.

## Destination repository intent

The official repository is a **backend delivery repository**, not a mirror of the personal development workspace.

Target structure:

```text
mdc-backend/
├── backend/
├── data/
│   └── curated/
├── ontologies/
├── requirements/
├── docs/
├── .dockerignore
├── .env.example
├── .gitignore
├── .python-version
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

A root `scripts/` directory is intentionally omitted in the initial transfer. The current useful operational actions already exist as verified Django management commands under `backend/apps/*/management/commands/`.

A root `docker-compose.yml` is also omitted initially unless a specific, verified local topology is intentionally implemented. The existing source `mdc-catalog/docker-compose.yml` is empty and must not be copied.

## Include exactly

### 1. Backend application source

Copy `mdc-catalog/backend/` with the following exclusions:

- exclude `backend/tests/`;
- exclude app-level test placeholders such as `backend/apps/*/tests.py`;
- exclude `__pycache__/`, `.pytest_cache/`, `*.pyc`, local SQLite databases, coverage files and other generated caches;
- preserve all Django migrations and management commands;
- preserve the optional `apps/demo` backend package because it is part of the current verified application source and is feature-flagged off in production by default.

Verified operational Django commands that remain inside the backend source include:

- `python backend/manage.py generate_catalog_rdf`
- `python backend/manage.py generate_service_discovery_rdf`
- `python backend/manage.py import_service_discovery_providers`
- `python backend/manage.py sync_service_discovery_catalogue`

These are preferred over transferring milestone-specific root scripts.

### 2. Runtime seed/reference data

Copy only:

`mdc-catalog/data/curated/**`

This is required by the current seed/fallback provider loaders and harmonized service-discovery YAML fallback.

Do **not** copy:

- `data/demo/`
- `data/generated/`
- `data/staging/`

Rationale:

- demo data is not part of the backend delivery baseline;
- generated Turtle/RDF is derived output and can be regenerated;
- staging provider-source files are development/import inputs rather than required current runtime baseline.

### 3. Ontology assets

Copy all of:

`mdc-catalog/ontologies/**`

This includes current ontology Turtle and SHACL assets.

### 4. Python/dependency configuration

Copy:

- `mdc-catalog/.env.example`
- `mdc-catalog/.python-version`
- `mdc-catalog/pyproject.toml`
- `mdc-catalog/requirements.txt`
- `mdc-catalog/requirements/**`

Do not copy a real `.env` or any secret-bearing environment file.

### 5. Git ignore policy

Do not blindly reuse the minimal current source `.gitignore`. Create a backend-delivery `.gitignore` covering at minimum:

```text
.env
.env.*
!.env.example
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/
*.sqlite3
db.sqlite3
data/generated/
data/demo/
.vercel/
.idea/
.vscode/
.DS_Store
Thumbs.db
```

Adjust only if a listed path must deliberately remain tracked.

## Do not copy root scripts

Do not copy `mdc-catalog/scripts/`.

Current contents are historical milestone/deployment validation utilities (`p31_*` through `p35_*`) plus currently empty legacy files such as `build_catalog.py`, `load_fuseki.py`, and `validate_graph.py`.

The official repository must not contain smoke, verification, milestone, or test scripts merely for historical evidence.

If a future operational helper is genuinely needed, add it later with a purpose-based name and documentation after review. Prefer Django management commands where appropriate.

## Docker requirement

Create a new backend `Dockerfile` and `.dockerignore`; do not copy the frontend Dockerfile or the empty root compose file.

Requirements for the Dockerfile:

- Python 3.12 base;
- build from the official backend repository root;
- install dependencies from the repository's Python requirements;
- copy only repository content needed by the backend;
- set a non-secret production-capable default settings selection through runtime environment, not hard-coded secrets;
- run the Django application through an appropriate WSGI server rather than Django `runserver` for production use;
- expose port 8000;
- no embedded database/Fuseki credentials;
- no Vercel-specific assumption.

Because the current Python requirements do not include a production WSGI server such as Gunicorn, do not silently add one without updating the dependency definition and verifying the resulting container. A minimal dependency addition is acceptable only if documented and validated.

Do not create a multi-service `docker-compose.yml` unless a deliberate local development topology is implemented and validated. Future AWS may use managed PostgreSQL and remotely hosted Fuseki, so Compose must not dictate the future cloud topology.

## Documentation package

Do not copy the full current `docs/` tree. Do not copy Codex prompts/reports, Phase 2/3 history, H1-H9 implementation reports, obsolete `/api/v1/` contracts, or frontend manuals.

Create a concise backend-only documentation set:

```text
docs/
├── overview.md
├── architecture.md
├── getting-started.md
├── configuration.md
├── api-reference.md
├── semantic-catalogue-and-sync.md
├── operations-and-recovery.md
└── marketplace-integration.md
```

Use the **current accepted code and current M6-A partner package** as the source of truth.

### Required documentation content

#### `overview.md`
- what the MaaSAI MaaS Dynamic Catalogue is;
- what problems it solves;
- provider publication/lifecycle;
- consumer service discovery;
- PostgreSQL as operational source of truth;
- RDF/Fuseki as derived semantic discovery layer;
- current manufacturing scope;
- explicit exclusions such as route/operation sequences.

#### `architecture.md`
- component diagram/description;
- Django/DRF;
- PostgreSQL/Neon-compatible persistence;
- publication/outbox;
- RDF generation;
- Fuseki;
- Marketplace interaction;
- immediate publication semantics;
- no separate Marketplace sync API.

#### `getting-started.md`
- Python 3.12 prerequisites;
- virtual environment;
- dependency installation;
- copy `.env.example` to `.env`;
- migrations;
- local server startup;
- health/filter checks;
- local SQLite development behavior;
- links to Docker usage once verified.

#### `configuration.md`
Document current environment variables by category without real values:
- Django;
- database;
- lifecycle feature flags;
- lifecycle auth/actor/concurrency;
- Fuseki query/Graph Store;
- synchronization;
- timeouts.
Clearly distinguish local defaults, secure production defaults, and explicitly approved pilot overrides.

#### `api-reference.md`
Freeze current canonical unversioned API only:

- `GET /api/health`
- `GET /api/catalog/filters`
- `POST /api/service-discovery/search`
- `POST /api/provider-publication`
- `POST /api/provider-publication/validation`
- `GET/PATCH/DELETE /api/providers/{provider_id}`
- `GET/POST /api/providers/{provider_id}/offerings`
- `GET/PATCH/DELETE /api/offerings/{offering_id}`

Include representative current request/response examples, ETag/If-Match behavior, error classes, multi-offering semantics, same-category offerings, attribute removal semantics, and publication status semantics.

Do not document `/api/v1/` as a current route.

#### `semantic-catalogue-and-sync.md`
- DB -> RDF -> Fuseki flow;
- full graph rebuild behavior;
- query-visible revision marker verification;
- authoritative search when automatic sync enabled;
- fallback behavior when automatic mode is disabled;
- generated RDF is derived output;
- same-dataset requirement for query/Graph Store endpoints.

#### `operations-and-recovery.md`
- migrations;
- relevant verified Django management commands;
- outbox state/recovery;
- stale processing recovery;
- handling post-commit synchronization failure;
- never blindly repeat non-idempotent registration after ambiguous 503;
- deployment health checks;
- current durable Fuseki requirement before production auto-sync enablement.

#### `marketplace-integration.md`
Derive from the accepted M6-A Marketplace package:
- integration sequence;
- values Marketplace retains between calls;
- ETags;
- multiple same-category offerings;
- search after completed/synced/succeeded;
- cleanup sequence;
- current pilot no-auth option as deployment configuration only;
- no frontend-specific implementation details.

### Optional partner assets

The official repository may include the accepted generic M6 Marketplace Postman pair under:

`docs/postman/`

Rename generically if useful:

- `MaaSAI_MDC_Marketplace_Integration.postman_collection.json`
- `MaaSAI_MDC_Marketplace_Integration.postman_environment.json`

Source from the accepted M6-A assets only. Do not copy M5/M5-A historical Postman collections.

## README requirement

Create a new backend-only root `README.md`.

Do not copy the current combined backend+demo-frontend README unchanged.

README should contain:

1. Project title and short purpose.
2. Current capabilities.
3. Architecture summary.
4. Repository structure.
5. Prerequisites.
6. Quick local start.
7. Docker quick start once verified.
8. Canonical API endpoint summary.
9. PostgreSQL/Fuseki relationship.
10. Configuration and security note.
11. Testing/verification note without shipping test code.
12. Documentation index.
13. Current deployment/infrastructure note phrased generically, not tied to the personal GitHub workflow.
14. Known current limitations/future infrastructure items.

Do not mention Codex workflow, personal GitHub working practices, or historical milestone branches.

## Explicitly exclude

Do not copy:

- `demo-frontend/`
- `backend/tests/`
- app-level test files;
- `scripts/` from the source repo;
- `docs/codex/`
- `docs/prompts/`
- `docs/Phase_2/`
- `docs/Phase_3/`
- historical H-phase/M-phase implementation reports;
- old `api-contract-v1.md` or any documentation presenting `/api/v1/` as current;
- frontend documentation;
- `data/demo/`
- `data/generated/`
- `data/staging/`
- the empty source `docker-compose.yml`;
- `.vercel/`;
- `.env` or any other secrets;
- Cloudflare/Vercel credentials;
- local virtual environments/caches;
- local worktree metadata;
- personal-repository Git history.

## Verification before commit/push

The preparation pass should verify the destination package itself without adding test files:

1. inspect complete destination tree;
2. scan for forbidden paths/files and likely secrets;
3. create a temporary local environment if needed without committing it;
4. install dependencies;
5. run `python backend/manage.py check`;
6. run `python backend/manage.py makemigrations --check --dry-run`;
7. run `python backend/manage.py migrate` against a disposable/local database;
8. start the backend locally and verify at least `/api/health` and `/api/catalog/filters`;
9. if Dockerfile is created, build the image and verify the container can start and serve health;
10. ensure generated runtime output remains ignored/untracked.

The source repository's accepted automated test evidence remains the verification source for the copied runtime code; the official delivery repository intentionally does not ship the development test suite.

## Stop rule

After preparing and verifying the local GitLab working tree:

- do not run `git add`;
- do not commit;
- do not push;
- return the destination tree, created/changed files, verification results, Docker status, any dependency changes, and any unresolved issue for human review.
