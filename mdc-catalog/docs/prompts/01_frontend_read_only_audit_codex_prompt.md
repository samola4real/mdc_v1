# Codex Prompt — Demo Frontend Read-Only Audit

## Purpose

Perform a **strictly read-only audit** of the MaaSAI/MDC demonstration frontend located at:

```text
C:\Users\Elahi\Desktop\template-frontend
```

This frontend was created only as a **pilot/demonstration UI** to illustrate how MaaSAI pilots could interact with the MaaS Dynamic Catalogue (MDC) through a Marketplace-like interface before the real Cloud MaaS Marketplace (CMM) and other MaaSAI components were integrated.

It is **not** the real CMM/Marketplace and must not be described as such.

The immediate objective is to understand the frontend completely before any repository migration, refactor, API correction, documentation generation, or Git remote change is attempted.

A later task will create a comprehensive frontend master implementation report/manual comparable to:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\MDC_Comprehensive_Implementation_Report_and_User_Manual.md
```

A later task may also integrate the frontend into the user's personal GitHub development repository while preserving the MaaSAI GitLab repository as the controlled upstream/release destination. **Do not perform that integration in this audit.**

---

# 1. Non-negotiable safety rules

This task is **READ ONLY**.

Do NOT:

- modify any frontend source file;
- modify any file in `mdc_v1`;
- run formatters that rewrite files;
- install or update packages;
- run `npm install`, `npm update`, `yarn install`, `pnpm install`, or equivalent;
- create/delete/rename files or directories;
- change `.gitignore`;
- change Git remotes;
- add a GitHub remote;
- remove the existing GitLab remote;
- create branches/tags;
- commit;
- push;
- pull with merge/rebase;
- reset, clean, checkout, restore, stash, or otherwise modify the worktree/index;
- clone/copy/import the frontend into `mdc_v1`;
- run deployment commands;
- change GitLab configuration;
- change CI/CD configuration;
- change environment variables;
- print secrets, tokens, passwords, API keys, private URLs containing credentials, or complete `.env` contents.

If a command could mutate state, do not run it unless it is obviously read-only and required for inspection.

If the current frontend repository has uncommitted changes, report them safely and continue only with read-only inspection. Do not discard, stage, stash, or alter them.

---

# 2. Repositories and authoritative reference

Frontend to audit:

```text
C:\Users\Elahi\Desktop\template-frontend
```

Current MDC repository/reference:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Current MDC master manual:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\MDC_Comprehensive_Implementation_Report_and_User_Manual.md
```

Use the MDC master manual only as a reference for the **current MDC contract and architecture**. For frontend behavior, the frontend source code is authoritative.

Important current MDC contract facts to verify frontend usage against:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Trusted lifecycle surface:

```text
POST  /api/provider-publication/validation
POST  /api/provider-publication
GET   /api/providers/{provider_id}
PATCH /api/providers/{provider_id}
GET   /api/providers/{provider_id}/offerings
POST  /api/providers/{provider_id}/offerings
GET   /api/offerings/{offering_id}
PATCH /api/offerings/{offering_id}
```

Current canonical routes do **not** use `/api/v1`.

`POST /api/catalog/search` is legacy and must not be treated as the current consumer integration route.

Do not assume the frontend has already been updated to these contracts. Discover what it actually uses.

---

# 3. Git audit — read only

From `C:\Users\Elahi\Desktop\template-frontend`, inspect and report:

1. Is it a Git repository?
2. Repository root.
3. Current branch.
4. Current HEAD commit SHA and latest commit message/date.
5. Clean/dirty worktree state.
6. Modified, staged, untracked, deleted, or renamed paths, if any.
7. Local branches.
8. Configured remotes.
9. Which remote appears to be the MaaSAI GitLab repository.
10. Remote fetch/push URLs **redacted if credentials/tokens are embedded**.
11. Whether `origin` currently points to GitLab.
12. Tracking/upstream branch for the current local branch.
13. Ahead/behind state if it can be determined safely.
14. Recent commit history sufficient to understand the repository's development history.
15. Presence of tags/releases relevant to the frontend.
16. Presence of Git submodules, Git LFS, or nested Git repositories.
17. Any GitLab-specific files such as `.gitlab-ci.yml`.

Allowed examples of read-only Git commands include:

```powershell
git rev-parse --show-toplevel
git status --short --branch
git branch --show-current
git branch -vv
git remote -v
git log --oneline --decorate -n 20
git tag --list
git submodule status
```

Do not reveal secrets embedded in remote URLs. Sanitize them in the report.

---

# 4. Technology-stack audit

Determine from repository files, without installing anything:

- frontend framework/library;
- framework version;
- language(s): JavaScript/TypeScript/etc.;
- package manager inferred from lockfiles;
- Node/runtime requirements if declared;
- build tool;
- router library;
- state-management approach;
- HTTP/API client approach (`fetch`, Axios, etc.);
- UI/component library;
- CSS/styling approach;
- form/validation libraries;
- authentication-related libraries;
- testing libraries;
- linting/formatting tools;
- deployment/build configuration;
- relevant package scripts from `package.json`.

Report exact evidence paths.

Do not run an install simply to identify versions; use manifests and lockfiles.

---

# 5. Repository and application structure

Produce a clear high-level map of the frontend repository, excluding generated/vendor directories such as:

```text
node_modules/
dist/
build/
coverage/
.cache/
```

Identify:

- application entry point;
- main app/root component;
- page/view directories;
- reusable component directories;
- API/service modules;
- route definitions;
- authentication/authorization helpers;
- layouts/navigation;
- forms;
- mock/demo data;
- assets;
- environment/configuration files;
- tests;
- CI/CD files;
- deployment configuration.

Explain the purpose of the important files/directories in plain language.

---

# 6. Page, route, and user-role audit

Inventory every user-facing route/page that is actually present.

For each route/page report:

- URL/route;
- component/page file;
- intended user/role;
- purpose;
- whether it is publicly reachable or protected;
- authentication/role assumptions;
- navigation entry point;
- main actions/buttons/forms;
- real API usage, mock usage, or static demonstration behavior;
- whether it appears active, incomplete, obsolete, or unused.

Pay particular attention to the intended demonstration scenarios:

1. provider registration/onboarding;
2. editing/updating an existing provider;
3. provider offering management;
4. consumer/service discovery/search;
5. login/protected routes or role-based rendering;
6. Marketplace-like navigation/illustration.

Do not infer functionality from names alone. Verify from code.

---

# 7. MDC API integration audit

Search the frontend thoroughly for:

- `/api/` strings;
- `/api/v1`;
- `/api/catalog/search`;
- `/api/service-discovery/search`;
- `/api/catalog/filters`;
- `/api/health`;
- `/api/provider-publication`;
- `/api/providers/`;
- `/api/offerings/`;
- hard-coded production URLs;
- localhost URLs;
- Vercel URLs;
- environment-based API base URLs;
- Axios/fetch clients;
- request/response type definitions;
- bearer-token handling;
- actor-header handling;
- ETag/`If-Match` handling;
- status-code/error handling.

For every API call actually implemented, provide a matrix:

| Frontend action | Page/component | Method | URL/path | Request source | Response handling | Current MDC contract status |
|---|---|---|---|---|---|---|

Classify current-contract status as one of:

```text
CURRENT
LEGACY
OUTDATED
MOCK/DEMO
UNCLEAR
```

If the frontend uses old `/api/v1/...`, `service_type`, legacy `/api/catalog/search`, or obsolete payload fields, identify them precisely but **do not fix them in this task**.

For payloads/responses, report the actual shapes used by the frontend and compare them with the current MDC master manual. Do not invent missing API integration.

---

# 8. Mock, dummy, and real behavior audit

This frontend was built for demonstration, so explicitly separate:

### A. Real behavior
Examples:
- real HTTP request to MDC;
- real dynamic filter loading;
- real service-discovery response rendering.

### B. Mock/demo behavior
Examples:
- hard-coded provider records;
- simulated login;
- fake role selection;
- mock search results;
- static status badges;
- dummy Marketplace components.

### C. Placeholder/incomplete behavior
Examples:
- button with no handler;
- TODO component;
- route not reachable;
- unused form;
- hard-coded response waiting for integration.

Create a concise matrix of these categories.

Do not criticize demo/mock behavior merely for being mocked; explain whether it was reasonable for the pilot illustration and what would need replacement for real CMM integration.

---

# 9. Authentication, authorization, and route protection audit

Determine what is actually implemented for:

- login;
- logout;
- session persistence;
- token storage;
- provider/consumer role selection;
- route guards;
- protected components;
- role-based navigation;
- trusted MDC lifecycle token usage;
- frontend exposure of sensitive credentials.

Flag any design where a trusted MDC lifecycle service token is embedded or expected in browser-side code/config. Do not print its value.

Clearly distinguish:

```text
DEMO AUTHENTICATION
REAL APPLICATION AUTHENTICATION
NOT IMPLEMENTED
```

Do not claim the frontend implements CMM identity unless code proves it.

---

# 10. Environment and secrets audit

Inventory environment/configuration mechanisms by **variable name only**.

Inspect filenames and references such as:

```text
.env
.env.local
.env.development
.env.production
.env.example
vite.config.*
next.config.*
webpack.config.*
```

Never print secret values.

Report:

- env/config filenames present;
- whether any are tracked by Git;
- variable names referenced by application code;
- which appear public/browser-safe;
- which appear sensitive and should not be browser-exposed;
- whether `.gitignore` covers local secret files;
- whether any likely secret is committed, without reproducing its value.

If you discover a real exposed secret, stop short of displaying it and report only the affected path/key name and recommended remediation.

---

# 11. Build, run, test, CI/CD, and deployment audit

From package manifests/configuration, determine:

- local development command;
- production build command;
- preview/start command;
- lint command;
- test command;
- test coverage present;
- CI/CD pipeline behavior;
- current GitLab deployment flow, if defined;
- Docker/configuration if present;
- hosting assumptions;
- base/public path assumptions;
- environment selection.

Do not execute deployment.

Do not install dependencies.

You may run a command such as `node --version` or a package-manager `--version` only if it is read-only and useful, but distinguish the locally installed tool version from the project's declared version.

Do **not** run the application/build/tests during this first audit if doing so could create or rewrite files. The purpose is structural understanding first.

---

# 12. Documentation audit

Inventory existing frontend documentation:

- README;
- architecture notes;
- setup instructions;
- API notes;
- screenshots/demo instructions;
- GitLab documentation;
- TODOs;
- comments describing pilot intent.

Identify stale or misleading documentation, especially claims that the frontend is the actual Marketplace/CMM or API examples that conflict with the current MDC contract.

Do not edit anything.

---

# 13. Suitability for import into `mdc_v1`

The user intends to use personal GitHub repository:

```text
samola4real/mdc_v1
```

as the controlled development location, while retaining the existing MaaSAI GitLab frontend repository as an official/release destination to update only when frontend work is approved.

Evaluate, but do not execute, the safest integration strategy.

Compare at least:

1. **Git subtree into `mdc_v1`**;
2. **submodule**;
3. **copy/squash import without history**;
4. **separate personal GitHub frontend repository with GitLab as second remote**.

The currently preferred option is a history-preserving subtree under approximately:

```text
mdc_v1/mdc-catalog/demo-frontend/
```

but this preference must be validated against the actual repository state.

For each option briefly report:

- advantages;
- disadvantages;
- history preservation;
- ease of daily development;
- ease of controlled push back to GitLab;
- risk of accidental GitLab push;
- fit with the current `mdc_v1` repository.

Then give **one recommendation**.

If subtree remains recommended, provide a proposed safe future sequence at a conceptual/command level, but **do not run any command** that changes either repository.

The future workflow should aim for:

```text
Personal GitHub / mdc_v1
        -> daily development and documentation
        -> test/review/approval
        -> deliberate publication of frontend changes to MaaSAI GitLab
```

Do not delete or overwrite GitLab history.

---

# 14. Master-document readiness assessment

The next major task will create:

```text
mdc-catalog/docs/Demo_Frontend/MDC_Demo_Frontend_Comprehensive_Implementation_Report_and_User_Manual.md
```

Based on this audit, identify the chapters the master frontend document should contain and which repository files will be the principal evidence for each chapter.

At minimum assess readiness for sections covering:

- executive summary;
- why the demo frontend exists;
- relationship to CMM/Marketplace and MDC;
- scope/non-scope;
- technology stack;
- architecture;
- repository structure;
- routes/pages;
- provider workflow;
- consumer workflow;
- login/role demonstration;
- API integration;
- actual payloads/responses;
- environment configuration;
- local setup/run/build;
- browser/manual testing;
- API/Postman testing relationship;
- dummy/mock versus real behavior;
- Git workflow;
- GitHub-development-to-GitLab-release process;
- limitations;
- future real CMM integration;
- troubleshooting;
- glossary;
- source/traceability appendix.

Do not create this master document yet.

---

# 15. Required final report

Return exactly one structured report titled:

```text
# FRONTEND READ-ONLY AUDIT REPORT
```

Use this structure:

```text
# FRONTEND READ-ONLY AUDIT REPORT

## 1. Safety gate
- frontend modified: NO
- mdc_v1 modified: NO
- packages installed/updated: NO
- Git remotes changed: NO
- commits created: NO
- pushes performed: NO
- secrets printed: NO

## 2. Git state
- repo root:
- current branch:
- HEAD:
- worktree clean/dirty:
- upstream/ahead-behind:
- remotes:
- GitLab remote:
- recent-history summary:
- submodule/LFS/nested-repo findings:

## 3. Technology stack
- framework/version:
- language:
- package manager:
- build tool:
- routing:
- state management:
- HTTP client:
- UI/styling:
- testing:
- important package scripts:

## 4. Repository structure
- high-level tree:
- important files/directories and purpose:

## 5. Pages/routes/roles
<table or structured inventory>

## 6. Provider demonstration workflow
- registration:
- existing-provider update:
- offering management:
- protected/role behavior:

## 7. Consumer demonstration workflow
- filters:
- search:
- result rendering:

## 8. MDC API integration
<table of actual API calls>
- current-contract integrations:
- legacy/outdated integrations:
- missing integrations:
- payload/response mismatches:
- ETag/auth/actor handling:

## 9. Real vs mock vs placeholder
<table>

## 10. Authentication/security/environment
- auth type:
- route protection:
- token handling:
- environment variable names:
- secret-risk findings:

## 11. Build/test/deployment
- dev command:
- build command:
- test/lint commands:
- GitLab CI/CD:
- deployment assumptions:

## 12. Existing documentation
- documents found:
- stale/misleading areas:

## 13. GitHub/GitLab integration assessment
- subtree:
- submodule:
- historyless copy:
- separate GitHub repo + second remote:
- RECOMMENDATION:
- proposed future safe sequence:

## 14. Frontend master-document readiness
- recommended document path:
- recommended chapter structure:
- principal evidence files:
- gaps requiring clarification before drafting:

## 15. Main findings and risks
<numbered, prioritized findings>

## 16. Final gate
FRONTEND READ-ONLY AUDIT: PASS / BLOCKED
READY_FOR_FRONTEND_GIT_INTEGRATION_PLANNING: YES / NO
READY_FOR_FRONTEND_MASTER_DOCUMENT_DRAFT: YES / NO
```

A PASS means the audit completed without modifying either repository and the evidence is sufficient to plan the next step.

If blocked by an unreadable repository, unsafe credential exposure, inaccessible Git metadata, or another material issue, stop and report the blocker instead of changing anything.
