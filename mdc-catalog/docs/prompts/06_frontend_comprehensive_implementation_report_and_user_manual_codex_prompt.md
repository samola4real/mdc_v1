# Codex Prompt — MDC Demo Frontend Comprehensive Implementation Report and User Manual

## Mission

Perform a deep repository-based review of the **MaaSAI MaaS Dynamic Catalogue (MDC) demonstration frontend** now preserved and maintained under this repository, and create one authoritative, comprehensive Markdown implementation report and user manual comparable in quality, depth, structure, auditability, and practical usefulness to the existing MDC backend master manual.

This is a documentation milestone. **Do not change application code, backend code, configuration behavior, dependencies, API behavior, Git remotes, or deployment infrastructure.**

The frontend is an illustrative demo used to show pilots what provider, consumer, and administrator interactions with MDC could look like before full Cloud MaaS Marketplace integration. It is **not the real Cloud MaaS Marketplace (CMM)** and must never be documented as such.

## Repository and branch gate

Work only in:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Expected branch:

```text
demo-frontend-integration
```

Expected accepted frontend cleanup baseline in ancestry:

```text
b207022363163a026a1d77e6485fd151e81aa750
fix: align MDC demo frontend with current API contract
```

Before writing:

1. Confirm the current branch is `demo-frontend-integration`.
2. Confirm the worktree is clean.
3. Confirm the branch is synchronized with `origin/demo-frontend-integration` using a normal fast-forward-only update if needed.
4. Confirm `b207022363163a026a1d77e6485fd151e81aa750` is in ancestry.
5. Confirm the normal MDC working copy has no GitLab remote.
6. Stop if there are unrelated local changes, merge conflicts, unexpected remotes, or any condition that would make a normal documentation-only commit unsafe.

Do **not** switch to `main`, merge to `main`, add a GitLab remote, touch the historical frontend repository, or push to GitLab.

## Authoritative source priority

Use repository evidence in this order when claims conflict:

1. Current frontend source on `demo-frontend-integration` under:
   `mdc-catalog/demo-frontend/`
2. Current MDC backend source in this repository.
3. Current accepted MDC master manual:
   `mdc-catalog/docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md`
4. Current frontend milestone/provenance documents under:
   `mdc-catalog/docs/Demo_Frontend/`
5. Historical frontend implementation reports under:
   `mdc-catalog/docs/Demo_Frontend/Implementation_History/`
6. Git history and commit metadata relevant to the sanitized import and cleanup.

Historical reports are evidence of project evolution, not automatically current truth. Clearly label superseded, historical, experimental, demo-only, or no-longer-used behavior.

Do not silently restore historical `/api/v1/...` routes, stale lifecycle browser helpers, old response shapes, or any other behavior that current code has intentionally replaced.

## Required review depth

Review the frontend comprehensively, including at minimum:

```text
mdc-catalog/demo-frontend/package.json
mdc-catalog/demo-frontend/package-lock.json
mdc-catalog/demo-frontend/next.config.js
mdc-catalog/demo-frontend/jsconfig.json
mdc-catalog/demo-frontend/.eslintrc.json
mdc-catalog/demo-frontend/README.md
mdc-catalog/demo-frontend/public/config.js
mdc-catalog/demo-frontend/src/config/**
mdc-catalog/demo-frontend/src/layout/**
mdc-catalog/demo-frontend/src/pages/**
mdc-catalog/demo-frontend/src/components/mdc/**
mdc-catalog/demo-frontend/src/services/mdc/**
mdc-catalog/demo-frontend/src/styles/**
```

Also inspect relevant backend/API files needed to document the frontend accurately, especially the current public contract, catalogue filters, service-discovery request/response contract, demo namespace, and trusted lifecycle security boundary.

Review all frontend provenance, release-mapping, cleanup milestone, and historical implementation reports sufficiently to reconstruct the frontend's evolution without confusing old and current behavior.

## Facts that must remain explicit

The final manual must make these boundaries unmistakable:

- Canonical project name: **MaaSAI MaaS Dynamic Catalogue (MDC)**.
- This frontend is an **MDC demonstration frontend**, not CMM itself.
- It was created to illustrate pilot interactions before Marketplace and other MaaSAI components were fully integrated.
- Current personal GitHub development location is the sanitized frontend under `mdc_v1`.
- The original GitLab history was intentionally not imported because credential-bearing objects existed in that history.
- GitLab remains the historical/official frontend release destination.
- GitHub-to-GitLab publication is controlled file synchronization through a fresh reviewed GitLab checkout/release branch, not subtree push, unrelated-history merge, history replacement, or force push.
- Browser runtime configuration is public and must not contain secrets.
- Trusted MDC provider lifecycle APIs are server-to-server/trusted integration APIs and must not receive lifecycle service tokens through browser-delivered code.
- Current browser provider/admin demo workflows use `/api/demo/...` demo endpoints rather than trusted lifecycle writes.
- Demo role guards are presentation/navigation controls; they are not a substitute for backend authorization.
- `/demo` is public; authenticated demo child routes are protected in the current route map.
- Current consumer-facing canonical MDC API routes are unversioned:
  - `GET /api/health`
  - `GET /api/catalog/filters`
  - `POST /api/service-discovery/search`
- `/api/v1/...` is not part of the current contract.
- Current public discovery rendering uses the flattened public provider/offering fields and `matched_capabilities`, `unmatched_capabilities`, and `unknown_capabilities` arrays.
- Consumer filters are loaded from the canonical filters API, with a clearly indicated static demo fallback if loading fails.
- `material_grades` is not a canonical consumer search criterion.
- Current demo search keeps `optional_match_mode: "score_only"`.
- Local browser runtime defaults may point to `http://localhost:8000`; deployed environments require deliberate HTTPS/backend origin configuration and appropriate CORS policy.
- Production MDC may have demo APIs disabled, so demo provider/admin operations require a deliberately demo-enabled backend environment.

## Required master document

Create exactly this authoritative document:

```text
mdc-catalog/docs/Demo_Frontend/MDC_Demo_Frontend_Comprehensive_Implementation_Report_and_User_Manual.md
```

Do not create a second competing master document.

The document should be written for multiple audiences at once:

- project manager / pilot stakeholder;
- developer joining the project;
- frontend developer;
- backend/API developer;
- MaaSAI/CMM integration partner;
- deployment/IT engineer;
- reviewer or future maintainer.

Use plain language where possible, but preserve exact technical details where necessary. Someone with limited frontend knowledge should be able to understand what exists, why it exists, how it works, how to run it, and what remains future work.

## Required structure and content

You may refine headings for readability, but the manual must comprehensively cover all of the following.

### 1. Executive summary

Explain:

- what the frontend is;
- why it was created;
- what it demonstrates;
- what it does not represent;
- its current accepted state;
- how it relates to the MDC backend and future CMM integration.

### 2. How to use this manual

Provide a reader-navigation table mapping common goals to sections, for example:

- understand the architecture;
- run locally;
- configure backend URL;
- understand provider demo;
- understand consumer search;
- understand admin demo;
- understand Keycloak/roles;
- understand API mappings;
- troubleshoot;
- prepare a future GitLab release;
- prepare future real CMM integration.

### 3. Project context and original motivation

Explain the MaaSAI/MDC context and why a dummy/illustrative UI was needed for pilots while Marketplace integration was unavailable.

Explain the intended conceptual chain:

```text
Provider / Consumer / Admin user
        ↓
Marketplace-like frontend demonstration
        ↓
Django MDC API
        ↓
MDC catalogue / discovery runtime
```

Make clear that real Marketplace registration, login ownership, authorization, workflow orchestration, and lifecycle integration remain outside this demo.

### 4. Evolution/history

Reconstruct the frontend's evolution from the imported historical reports and Git evidence.

Distinguish:

- base MaaSAI template frontend;
- MDC demo additions;
- provider/consumer/admin demo work;
- old/historical API assumptions;
- dirty working-tree preservation;
- sanitized snapshot creation;
- safe GitHub import;
- one-time inherited-whitespace exception;
- API/config cleanup and current accepted baseline.

Include commit/SHA evidence where useful, especially:

- historical source HEAD `832ad57265bce0889ebea58bc69c031c3b394ee7`;
- sanitized import commit `e411e7300cfbe2f9f3f9fe245027f2c0c341cd38`;
- API/config cleanup commit `b207022363163a026a1d77e6485fd151e81aa750`.

### 5. Repository strategy and security-preserving import

Explain in accessible detail:

- why the old GitLab history was not imported;
- how the dirty state was preserved;
- what was sanitized/excluded;
- why exact snapshot provenance matters;
- why GitHub is used for controlled development;
- why GitLab is retained for official historical/release continuity.

Do not expose credential values or secret material.

### 6. Technology stack

Document exact current versions/roles where supported by repository evidence, including:

- Next.js / Pages Router;
- React;
- PrimeReact / PrimeFlex / PrimeIcons;
- Axios;
- Keycloak JS;
- Sass;
- Node/npm expectations;
- Docker/standalone build behavior where applicable.

Explain what each technology contributes.

### 7. Frontend architecture

Describe major layers and data flow, including a text architecture diagram such as:

```text
Browser
  ├─ Pages / route map
  ├─ AuthContext / Keycloak
  ├─ MDC demo components
  ├─ MDC service layer
  └─ public runtime config
          ↓ HTTP
Django MDC
  ├─ canonical public APIs
  └─ demo-only APIs
```

Explain the role of:

- pages;
- reusable components;
- route configuration;
- auth context;
- demo-role selection;
- service wrappers;
- runtime configuration;
- static fallback data;
- result-formatting utilities.

### 8. Repository/file structure

Give a practical annotated tree of the important frontend directories and explain where a future developer should modify:

- pages;
- MDC components;
- services;
- runtime config;
- styles;
- layout/menu;
- documentation.

### 9. Routing and navigation

Document actual current routes and access expectations.

Include at minimum:

- `/`
- `/demo`
- `/demo/provider`
- `/demo/consumer-search`
- `/demo/admin-audit`
- `/404`

Explain the cleanup that removed accidental `/home/DashboardContent` and `/home/NotFoundPage` routes.

Explain route protection versus component-level role selection.

### 10. Authentication and demo roles

Document current Keycloak client behavior from source without exposing secrets.

Explain:

- authentication state;
- provider/consumer/admin role aliases;
- selected demo role in session storage;
- menu visibility;
- route guard behavior;
- role switching;
- what is presentation-only;
- what a real Marketplace/backend authorization layer must eventually own.

### 11. Runtime configuration

Document `window.MAASAI_CONFIG`, `public/config.js`, and runtime merging.

Explain each current field and show safe examples using placeholders only.

Explain:

- localhost development default;
- deployed HTTPS backend URL;
- shared `/api` prefix;
- demo `/api/demo` prefix;
- CORS/origin implications;
- Keycloak URL/client configuration;
- why browser configuration is public;
- why secrets must never be stored there.

### 12. API integration overview

Provide a frontend-to-backend mapping table covering every MDC endpoint the current frontend actually calls.

Separate:

**Canonical public MDC APIs**
- `GET /api/health`
- `GET /api/catalog/filters`
- `POST /api/service-discovery/search`

**Demo-only APIs**
Document the `/api/demo/...` calls actually present in the service layer for health/status/provider preview/save/admin operations.

Explain which workflows fail gracefully if demo API is disabled.

Explicitly state which trusted lifecycle APIs the browser intentionally does **not** call and why.

### 13. MDC service client

Document URL construction, prefixes, request timeout, headers, error normalization, and service modules.

Explain the current canonical error shape:

```json
{
  "contract_version": "1.0",
  "error": {
    "code": "...",
    "message": "..."
  }
}
```

Explain compatible fallback handling where implemented.

### 14. Consumer service-discovery workflow

Document the complete user journey and code flow:

```text
Open Consumer Search
→ load canonical filters
→ choose family/type/material/process/certification/specifications
→ build request payload
→ POST canonical discovery search
→ normalize public response
→ optionally combine explicitly labelled demo overlay results
→ render provider suitability/capabilities
```

Explain canonical filter transformation in detail, including:

- `service_categories`;
- `part_families`;
- family-keyed `part_types`;
- materials;
- processes;
- certifications;
- fallback behavior.

### 15. Search payload construction

Document the request contract actually produced by the demo.

Provide representative current JSON examples for at least:

- gear search;
- shaft search;
- metal-part search.

Explain selection fields, scoped requirement groups, generic requirements, and match policy.

Do not invent unsupported fields.

Explain that `material_grades` is not a canonical search criterion.

### 16. Search result rendering

Document current public result fields and how UI renders them.

Cover:

- provider identity;
- offering identity;
- service category/family;
- match status and score handling;
- matched capabilities;
- unmatched capabilities;
- unknown capabilities;
- demo-overlay labelling;
- advanced/debug JSON;
- quotation/provider/save buttons as demo-only illustrative actions.

Clearly distinguish current flattened public response from older historical/internal response shapes.

### 17. Provider demonstration workflow

Explain registration and update demo experiences separately.

Document:

- provider information;
- offering information;
- custom offering fields;
- custom capability fields;
- templates;
- gear/shaft/metal-part/general capability presentation;
- preview behavior;
- demo save/update behavior;
- demo state loading;
- Tasowheel example data where present.

Make explicit that this is demo persistence under `/api/demo/...`, not the trusted production provider lifecycle.

### 18. Flexible provider input versus controlled MDC fields

Explain the important design principle reflected by the demo and MDC:

- provider-entered business information may be flexible/staging input;
- controlled/searchable MDC fields remain ontology/vocabulary-aligned;
- arbitrary free text should not be silently written into controlled fields;
- custom fields allow demonstration of provider flexibility while mapping to controlled semantics can happen later.

Use current repository evidence and avoid overstating automation that is not implemented.

### 19. Admin/audit demonstration

Document the admin page and status cards/actions.

Explain which calls are read-only and which demo-admin actions may mutate demo state or trigger demo-only backend operations.

Explain how disabled/unavailable demo endpoints are represented.

Do not describe client admin role checks as backend security.

### 20. Public API examples

Include current, compact, realistic examples for:

- health response;
- catalogue filters response shape;
- discovery request;
- discovery response;
- error envelope.

Use current backend code/master manual as source of truth.

### 21. Trusted provider lifecycle boundary

Include a dedicated section explaining why the real trusted lifecycle APIs are separate from this browser demo.

Summarize conceptually:

```text
Browser / Marketplace UI
        ↓
Marketplace backend or BFF
        ↓ trusted auth + actor + concurrency
MDC trusted lifecycle API
```

Explain service-token, actor attribution, ETag/If-Match concepts at a high level, but do not expose token values and do not imply the current browser implements them.

### 22. Local setup and execution

Provide step-by-step instructions from a clean checkout for:

- locating the frontend;
- Node prerequisites;
- `npm ci`;
- runtime config;
- `npm run dev`;
- browser route;
- optional local Django endpoint assumption;
- lint/build/start commands.

Use repository-relative paths where possible.

### 23. Validation and accepted evidence

Record the accepted frontend validation milestone, including:

- secret scan pass;
- `git diff --check` pass after cleanup;
- `npm ci` pass;
- zero vulnerabilities reported by that run;
- lint pass with five pre-existing warnings;
- build pass;
- route sanity results;
- public deployed backend smoke results;
- no lockfile changes;
- no generated files tracked.

Phrase these as evidence from the accepted milestone, not perpetual guarantees.

### 24. Testing guidance

Provide practical manual test checklists for:

- unauthenticated landing/demo dashboard;
- provider role;
- consumer role;
- admin role;
- canonical filters unavailable fallback;
- demo API disabled;
- backend unavailable;
- canonical search success and no-result cases.

Also describe missing automated test/CI coverage as future work.

### 25. Docker/build behavior

Document Dockerfile, standalone Next.js output, compose/Makefile behavior if current files support it.

Separate existing repository capability from deployment recommendations.

### 26. Deployment guidance

Explain what is required to deploy this demo frontend safely:

- frontend HTTPS origin;
- runtime MDC backend URL;
- backend CORS policy;
- Keycloak ownership/configuration;
- demo API enablement decision;
- no browser secrets;
- backend environment separation.

Do not claim a frontend production deployment currently exists unless repository evidence proves it.

### 27. Security model and limitations

Include a concise threat/boundary section covering:

- public browser config;
- no lifecycle secrets in browser;
- client-side role guards are not backend authorization;
- demo APIs require deliberate server-side deployment policy;
- original credential-bearing Git history remains outside personal GitHub;
- secret scanning limitations;
- dependency/update considerations.

### 28. Git workflow for daily development

Explain the intended controlled workflow in `mdc_v1` after the integration branch is accepted.

Document normal branch/commit/review practices and that GitHub is the working development source for this sanitized snapshot.

### 29. GitHub-to-GitLab official release workflow

Base this section on:

`mdc-catalog/docs/Demo_Frontend/01_frontend_github_to_gitlab_release_mapping.md`

Provide a detailed but safe step-by-step process.

Make clear that a release requires separate review/approval and must not be performed during this documentation task.

### 30. Relationship to the MDC backend master manual

Explain which manual is authoritative for which layer:

- backend/API/catalogue/security/AWS architecture → MDC backend master manual;
- browser demo/front-end operation/integration → this frontend manual.

Explain that the two documents should be read together for end-to-end understanding.

### 31. Future CMM integration

Describe a future architecture without pretending it exists today.

Cover likely ownership boundaries for:

- user registration/login;
- provider identity;
- consumer identity;
- Marketplace forms;
- dynamic filters;
- trusted lifecycle server-side calls;
- quotation workflow;
- authorization;
- routing/navigation;
- removal or retirement of demo-only APIs.

### 32. Known limitations and future work

At minimum include:

- real CMM integration not implemented;
- trusted lifecycle browser integration intentionally absent;
- deployment-specific HTTPS/CORS/Keycloak ownership unresolved;
- stronger automated frontend tests absent;
- scoped CI absent;
- GitLab release synchronization not yet performed;
- demo-only overlay/persistence must not be confused with authoritative catalogue data;
- any other significant limitations supported by current code.

### 33. Troubleshooting

Provide symptom → likely cause → corrective action guidance for common issues such as:

- frontend cannot reach backend;
- CORS failure;
- Keycloak/login issue;
- no demo role available;
- demo API disabled/404;
- filters fall back to static vocabulary;
- search returns 400;
- search returns no providers;
- build/lint problems;
- accidental use of localhost in deployed config.

### 34. Glossary

Include relevant terms such as MDC, MaaS, MaaSAI, CMM, provider, consumer, offering, service discovery, controlled vocabulary, demo overlay, Keycloak, ETag, CORS, Fuseki, RDFLib, GitHub, GitLab, sanitized snapshot.

### 35. Appendices

Include compact reference material where useful:

- endpoint table;
- route table;
- role/access table;
- important file map;
- milestone/commit timeline;
- safe deployment checklist;
- future GitLab release checklist.

## Style requirements

The manual must be:

- comprehensive but organized;
- readable by non-specialists;
- precise enough for developers;
- explicit about historical versus current behavior;
- explicit about demo-only versus canonical/production concepts;
- rich in practical examples;
- free of secrets;
- free of unsupported claims;
- internally consistent with the current backend master manual.

Prefer explanatory prose, compact tables, diagrams in Markdown text, and realistic JSON/code examples. Avoid repetitive filler.

Use repository-relative paths throughout the final manual unless an absolute path is necessary to explain historical local preservation; do not make operator-local Windows paths the normal user instructions.

## Secret and privacy guard

Never print or copy credential values from any file, Git object, environment variable, report, local preservation directory, Keycloak export, or shell history.

Do not include:

- lifecycle service-token values;
- database URLs/passwords;
- Django secret keys;
- Fuseki passwords;
- private keys;
- credential-bearing historical content.

If a historical report references a credential incident, document only the existence/risk category and mitigation.

## Verification gates after writing

After creating the master manual:

1. Review it against current frontend source and current backend API source.
2. Confirm there are no current-contract claims using `/api/v1/...`.
3. Confirm it does not document stale browser helpers as active.
4. Confirm it does not claim real CMM integration exists.
5. Confirm it does not claim client-side role guards secure backend APIs.
6. Confirm it does not instruct placing trusted lifecycle tokens in browser code/config.
7. Confirm it correctly distinguishes canonical public APIs, demo APIs, and trusted lifecycle APIs.
8. Confirm the filters and public discovery response shapes reflect current code.
9. Confirm `git diff --check` passes.
10. Run a safe text secret-risk scan over the new document and report only paths/categories, never values.
11. Confirm no frontend/backend application files changed.
12. Confirm the only intended change is the master manual itself.

If a gate fails, correct the documentation and re-run the checks. Stop rather than committing if a safety or scope issue cannot be resolved cleanly.

## Git result

If all gates pass:

```text
git add mdc-catalog/docs/Demo_Frontend/MDC_Demo_Frontend_Comprehensive_Implementation_Report_and_User_Manual.md
git commit -m "docs: add comprehensive MDC demo frontend manual"
git push origin demo-frontend-integration
```

Do not merge to `main`.
Do not push to GitLab.
Do not change Git remotes.

## Required final response

Return exactly one report headed:

```text
# FRONTEND MASTER IMPLEMENTATION REPORT AND USER MANUAL GENERATION REPORT
```

Include:

### 1. Repository gate
- branch
- starting commit
- accepted cleanup baseline in ancestry
- clean/synchronized state
- remote safety

### 2. Review coverage
- major frontend areas reviewed
- backend/API references reviewed
- historical/provenance documentation reviewed

### 3. Master document
- exact path
- scope/major sections
- current-vs-historical distinction confirmed
- CMM/demo boundary confirmed

### 4. Contract/security verification
- canonical API routes
- `/api/v1` current-contract findings
- public/demo/trusted lifecycle boundary
- browser secret rule
- role-guard security wording

### 5. Documentation verification
- `git diff --check`
- secret-risk scan
- application code changed YES/NO
- unrelated files changed YES/NO

### 6. Git result
- commit SHA
- commit message
- push result
- local/remote synchronized
- `main` merged YES/NO
- GitLab push YES/NO

### 7. Final gate

End with exactly:

```text
FRONTEND MASTER IMPLEMENTATION REPORT AND USER MANUAL: PASS
READY_FOR_CHATGPT_FRONTEND_MASTER_REVIEW: YES
```

If the milestone cannot be completed safely, use `BLOCKED` instead and explain the exact reason without making unrelated changes.