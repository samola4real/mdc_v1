# MDC v1 Clean Git Baseline Report

Report date: 2026-09-03

## 1. M3 status

completed

## 2. Git state before cleanup

| Item | Result |
|---|---|
| Git root | `C:\Users\Elahi\Desktop\mdc_v1` |
| Working project | `mdc-catalog/` |
| Branch | `main` |
| Remotes | `origin` and `upstream` both point to `https://github.com/samola4real/mdc_v1.git` |
| Initial tracking state | Important backend apps, tests, curated/generated/staging data, and local `.gitignore` were not captured in Git. |
| Tracked docs state | `mdc-catalog/docs/*` and `MDC_Dev_chat/*` were tracked or staged, contrary to the M3 local-docs rule. |
| Important risks found | `backend/db.sqlite3`, provider demo state JSON, Python caches, duplicate data zip archives, and local docs should not be versioned. The generated service-discovery Turtle file is runtime-relevant and was retained. |

## 3. .gitignore decisions

| Pattern | Added/retained | Reason |
|---|---|---|
| `.venv/`, `venv/` | Added/retained | Exclude local virtual environments. |
| `.vscode/` | Retained | Exclude editor-local settings. |
| `docs/`, `mdc-catalog/docs/` | Added/retained | Keep documentation local and out of Git. |
| `Chat_MDC_Dev/`, `MDC_Dev_chat/`, `new_Phases.md` | Added/retained | Exclude local development notes and phase-planning docs. |
| `__pycache__/`, `*.py[cod]`, `*$py.class`, `.pytest_cache/`, `.coverage`, `htmlcov/` | Added/retained | Exclude Python/test cache artifacts. |
| `.env`, `.env.*`, `!.env.example`, `!mdc-catalog/.env.example` | Added | Exclude secrets/local env files while keeping env templates trackable. |
| `db.sqlite3`, `*.sqlite3` | Added/retained | Exclude local SQLite runtime state. |
| `staticfiles/`, `media/`, `*.log` | Added | Exclude Django/static/runtime output. |
| `mdc-catalog/data/demo/provider_demo_state*.json` | Added | Exclude mutable demo endpoint state. |
| `.DS_Store`, `Thumbs.db`, `~$*.xlsx` | Added | Exclude OS and Office temp files. |
| `mdc-catalog/data/curated/*.zip` | Added | Exclude duplicate local data archives; YAML files are the runtime sources. |

## 4. docs/ handling

| Check | Result |
|---|---|
| Local docs preserved | yes: `mdc-catalog/docs/` remains on disk. |
| Git docs tracking removed | yes: `git ls-files mdc-catalog/docs` returns no files. |
| `/docs/` ignored | yes for actual repo paths: top-level `docs/` and `mdc-catalog/docs/` are ignored. |

## 5. Files newly tracked

| Group | Included |
|---|---|
| Backend implementation | `mdc-catalog/backend/apps/api`, `catalog`, `demo`, `ontology`, `providers`, `search`; updated config and `manage.py`. |
| Tests | `mdc-catalog/backend/tests/`, including legacy retained tests and focused H1-H9 service-discovery tests. |
| Runtime data | `data/curated/providers/`, `data/curated/service_discovery/providers/`, `data/staging/provider_sources/precipart.yaml`. |
| Generated runtime assets | `data/generated/mdc_catalog.ttl` and `data/generated/service_discovery/mdc_service_discovery_catalog.ttl`. |
| Demo asset | `data/demo/mdc_demo_metal_provider_registration_copy_paste.xlsx`. |
| Ignore rules | Root `.gitignore`. |

## 6. Files intentionally excluded

| Group | Excluded |
|---|---|
| Local docs | `mdc-catalog/docs/`, top-level `docs/`, `new_Phases.md`, and development chat notes. |
| Runtime/local state | `backend/db.sqlite3`, `data/demo/provider_demo_state*.json`. |
| Caches | Python `__pycache__/`, `.pytest_cache/`, coverage output. |
| Virtual environments | `.venv/`, `venv/`. |
| Secrets/env | `.env`, `.env.*`; env examples remain trackable. |
| Duplicate archives/temp files | `data/curated/*.zip`, OS temp files, Office lock files. |

## 7. Verification

| Command | Tests run | Passed | Failed | Skipped | Result |
|---|---:|---:|---:|---:|---|
| `..\..\.venv\Scripts\python.exe manage.py check` | 0 | 0 | 0 | 0 | Pass: no system-check issues. |
| `..\..\.venv\Scripts\python.exe manage.py test -v 2` | 390 | 377 | 0 | 13 | Pass. |
| `..\..\.venv\Scripts\python.exe manage.py test tests.test_service_discovery_registry tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_provider_loader tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_local_matcher tests.test_service_discovery_sparql_query_builder tests.test_service_discovery_sparql_service tests.test_service_discovery_fuseki_service tests.test_service_discovery_matching_alignment tests.test_service_discovery_runtime_search tests.test_service_discovery_search_endpoint tests.test_service_discovery_local_search_response tests.test_service_discovery_fuseki_matching_alignment tests.test_service_discovery_search_response_contract -v 2` | 230 | 225 | 0 | 5 | Pass. |

Skipped tests are optional Fuseki/integration checks guarded by missing local/remote Fuseki environment.

## 8. Baseline commit

| Item | Result |
|---|---|
| Commit hash | `3d1b37e` |
| Commit message | `chore: establish harmonized MDC v1 baseline` |
| Branch | `main` |

## 9. Final Git state

`git status` reports:

```text
On branch main
Your branch is ahead of 'origin/main' by 1 commit.
nothing to commit, working tree clean
```

No remote push was performed.

## 10. Readiness

READY_FOR_M4
