# Codex Prompt — MDC Master Implementation Report, Technical Manual, API Guide, and Postman Testing Manual

## Role and objective

Act as a senior software architect, technical writer, API documentation specialist, and repository auditor for the **MaaSAI MaaS Dynamic Catalogue (MDC)**.

Your task is to inspect the complete current repository and create a **single master Markdown document** that explains the MDC from its original concept and first Tasowheel pilot work through the current completed Phase 3 state.

This is **not** another milestone summary. It must become the principal MDC implementation report + architecture manual + API reference + operator/testing guide for readers ranging from non-technical project stakeholders to developers and testers.

Create exactly this file:

```text
mdc-catalog/docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md
```

The document must be readable by a person who has never seen the project before, while still being technically precise enough for someone to test or continue development.

---

# 1. Non-negotiable source-of-truth policy

The repository contains historical documents whose architecture, endpoints, schemas, and assumptions have since evolved. You MUST distinguish historical design from the current implementation.

Use this evidence priority when sources disagree:

1. **Current working implementation on `main`** — views, serializers, URL configuration, models, services, settings, management commands, runtime search code, RDF/Fuseki code.
2. **Current tests and validation scripts** that exercise the implementation.
3. **Completed Phase 3 reports**, especially P3.2–P3.6.
4. **Completed late Phase 2/M7 reports** and infrastructure portability decision.
5. Earlier Phase 2 reports.
6. Week 1 / early v1 architecture, ontology, query-mapping, seed-data and API-contract documents — these are historical design evidence only where superseded.
7. README or older API PDFs/docs if they conflict with newer code/evidence.

Critical rule:

> Latest working implementation and verified milestone evidence override stale documentation. Do not invent endpoints, fields, payloads, statuses, tests, deployment behavior, or architecture. Every current API example must be checked against the current serializers/views/tests and, where relevant, the P3.4/P3.5 validation scripts.

If historical and current behavior differ, do **not** silently rewrite history. Explain the evolution explicitly, for example:

```text
Historical Week 1 design: /api/v1/catalog/search
Current canonical contract: /api/service-discovery/search
Reason: Phase 2 API harmonization and the decision to use contract_version instead of URL versioning.
```

---

# 2. Critical current decisions that MUST be represented correctly

Verify these against the repository before writing, but use them as the expected current baseline:

## Current canonical public API policy

No `/api/v1` URL prefix is used for partners/current canonical integration.

Canonical public endpoints:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

API evolution uses response/request metadata such as:

```json
"contract_version": "1.0"
```

Do not present `/api/v1/...` as the current public API. Where useful, show that old `/api/v1` documentation was historical and that `/api/v1` should not be used.

`POST /api/catalog/search` is legacy only. Audit the exact current legacy routes before documenting them.

## Current trusted provider lifecycle API

Audit exact routes and current method support, expected to include:

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

These lifecycle APIs are trusted/internal pilot interfaces, not anonymous public Marketplace write APIs.

## Security/concurrency behavior

Audit `apps/api/lifecycle_security.py`, settings, views and tests. Explain in plain English and technically:

- Bearer service token;
- `X-MDC-Actor-Id` actor attribution for writes when required;
- strong ETags;
- canonical `If-Match` concurrency semantics;
- temporary Vercel transport workaround `X-MDC-If-Match`;
- missing precondition -> `428` when required;
- stale ETag -> `412`;
- invalid/malformed precondition -> `400`;
- missing/invalid auth -> `401`;
- auth configured as required but server token unavailable -> `503`;
- duplicate provider/offering -> `409` where implemented;
- feature-flag-disabled write/validation behavior where implemented.

Never place any real token or secret in the document.

## Persistence and semantic architecture

Current operational source of truth is PostgreSQL through Django ORM.

Explain the difference between:

```text
PostgreSQL = operational/transactional source of truth
RDF/Fuseki = semantic catalogue/search representation
```

Provider lifecycle writes create durable records such as provider/offering state plus publication/outbox evidence. Semantic synchronization is operator-controlled and uses the existing management command / Graph Store synchronization path. Do not invent a public synchronization endpoint.

## Runtime discovery order

Audit the current runtime implementation and describe the actual backend/fallback behavior accurately. Historical and current architecture may include remote Fuseki, RDFLib, and harmonized YAML fallback. Do not simplify in a way that changes runtime semantics.

## Deployment status

Current pilot infrastructure is temporary:

```text
Django/DRF API -> Vercel
PostgreSQL -> Neon PostgreSQL
RDF/Fuseki -> pilot/local/external validation arrangement
```

Future deployment target is AWS. Vercel and Neon are not permanent architectural dependencies.

AWS migration must remain operational/configuration-oriented where possible, preserving Django models/domain logic, standard PostgreSQL, API contracts, H1-H9 matching, RDF generation, and publication/outbox semantics.

Read and use:

```text
docs/Phase_2/10a_mdc_v1_infrastructure_portability_decision.md
docs/Phase_3/06_mdc_v1_p36_aws_migration_readiness_plan.md
```

---

# 3. Original pilot context and historical source handling

The project began with a Tasowheel/TSW structured-search pilot.

The original provider-confirmed capability basis included the following approved/curated values:

- provider ID: `tasowheel`;
- batch size: `100–2000` pieces;
- gear module: `0.3–10`;
- raw diametral pitch notation preserved as `DP 85-2.5`;
- diameter: `10–450 mm`;
- approximate maximum weight: `200 kg`;
- quality capability: up to `DIN4`;
- normal lead time: `8–12 weeks`, case-dependent;
- material grades: `18CrNiMo7-6`, `16MnCr5`, `20MnCr5`;
- certifications including ISO 9001:2015, ISO 14001:2015, partial ISO/TS 16949 and APQP;
- surface finish/general tolerance were not confirmed and must not be invented.

A provider questionnaire also contained a typical manufacturing routing description, but the project explicitly decided that **route/operation sequence fields were excluded from the v1 public/queryable catalogue**. Do not reproduce confidential/raw route details as if they became current searchable API fields.

Historical Week 1 principles included:

- structured JSON input first;
- ProviderOffering as central search result concept;
- ontology/RDF-backed search;
- deterministic/template-driven semantic query logic;
- explainable matching;
- unknown does not automatically mean failure;
- provider-confirmed values should take precedence over inference;
- no pricing, real-time scheduling/capacity, or route sequencing in v1.

Explain how the implementation evolved beyond the initial one-provider YAML prototype into the harmonized registry, H1–H9 evidence fidelity, database-backed lifecycle, outbox, and real Fuseki synchronization.

---

# 4. Verified Phase 3 evidence that MUST appear

Audit the Phase 3 documents and scripts and include the verified evidence in the appropriate sections.

## P3.4 — Provider Lifecycle API Validation

Final real deployed validation result:

```text
45 passed
0 failed
```

The validation covered at minimum:

- health and filters;
- anonymous lifecycle rejection;
- invalid and valid provider validation;
- missing actor rejection;
- provider registration;
- duplicate provider protection;
- trusted provider GET;
- provider ETag;
- missing concurrency precondition;
- current ETag PATCH;
- changed ETag;
- stale provider ETag rejection;
- offering listing;
- offering creation;
- duplicate offering protection;
- offering GET + ETag;
- offering PATCH concurrency;
- stale offering ETag rejection;
- final offering state.

Controlled P3.4 provider:

```text
p34_api_validation_provider
```

P3.4 deliberately left semantic synchronization unexecuted so P3.5 could prove the full pipeline.

Starting/ending PostgreSQL evidence around this milestone is recorded in the P3.4/P3.5 reports; use those exact verified values rather than guessing.

## P3.5 — Provider to Discovery End-to-End Validation

Final verified synchronization command evidence:

```text
selected=4; succeeded=4; failed=0; noop=0; events=5
```

Before synchronization:

- P3.4 provider absent from Fuseki;
- P3.4 controlled offering absent from Fuseki;
- P3.4 provider absent from deployed canonical discovery.

After synchronization:

```text
Fuseki triple count = 731
```

and:

- P3.4 provider present in Fuseki;
- P3.4 offering present in Fuseki;
- deployed `POST /api/service-discovery/search` returned `p34_api_validation_provider`;
- `contract_version = 1.0`;
- Vercel-side semantic synchronization remained disabled;
- no tracked code changes were needed for the validation.

PostgreSQL verification after P3.5 showed the relevant P3.4 publications synchronized and its five sync events succeeded with one attempt each. Use the exact Phase 3 report wording where possible.

## P3.6

Phase 3 ends with the AWS migration/readiness plan. Clearly state:

```text
P3.0 COMPLETE
P3.1 COMPLETE
P3.2 COMPLETE
P3.3 COMPLETE
P3.4 COMPLETE
P3.5 COMPLETE
P3.6 COMPLETE
PHASE 3 COMPLETE
```

Do not imply that AWS migration has already been executed. P3.6 is the readiness/migration plan.

---

# 5. Repository audit requirements before drafting

Before writing the report, perform a systematic read-only audit.

At minimum inspect:

```text
README.md
.env.example
requirements/
backend/config/
backend/apps/api/
backend/apps/providers/
backend/apps/search/
backend/apps/ontology/
backend/tests/
data/curated/
data/generated/
ontologies/
scripts/
docs/Phase_2/
docs/Phase_3/
docs/prompts/ where useful
```

Specifically locate and inspect current:

- URL routing;
- GET and POST views;
- public contract response shaping;
- lifecycle serializers;
- search serializers;
- provider lifecycle repository/write service;
- lifecycle ETag code;
- provider/publication/outbox models;
- catalogue synchronization service;
- `sync_service_discovery_catalogue` command;
- RDF generation/retrieval/runtime backend selection;
- current controlled vocabularies;
- P3.3/P3.4/P3.5 scripts;
- P3.6 plan;
- migration files where useful for the data model.

Use `git log --oneline` and milestone reports to reconstruct evolution, but do not turn the manual into a raw commit dump.

Run only non-destructive/read-only checks needed to validate the document. Do **not**:

- publish another provider;
- modify production data;
- run semantic synchronization;
- rotate credentials;
- alter Vercel/Neon/Fuseki configuration;
- run destructive database commands;
- expose secret values.

You may use syntax/static inspection and existing test evidence. A full production write test is not needed because P3.4/P3.5 already provide accepted evidence.

---

# 6. Required document structure

Use a professional title page/header and a linked Markdown table of contents. Include a clear **Document Status / As-of Snapshot** near the beginning with the current date and audited Git commit (`git rev-parse HEAD`).

Use the following major structure. You may add subsections where useful, but do not omit major topics.

## 1. Executive Summary

Explain MDC in plain language in approximately one page:

- what it is;
- why MaaSAI needs it;
- who a MaaS Provider is;
- who a MaaS Consumer is;
- what the Marketplace does;
- what MDC does and does not do;
- current status after Phase 3.

Include a simple mental model such as:

```text
Provider describes what it can manufacture
        -> MDC normalizes and stores the capability
        -> semantic catalogue represents searchable capability
        -> Consumer submits requirements
        -> MDC returns suitable provider offerings with matched values
```

## 2. MaaSAI/MDC Context and Terminology

Explain, for a lay reader:

- MaaS in this project context;
- MaaS Provider;
- MaaS Consumer;
- Provider Offering;
- capability;
- ontology;
- RDF;
- SPARQL;
- Fuseki;
- PostgreSQL;
- API;
- REST;
- JSON;
- ETag;
- outbox/publication;
- contract version.

Use examples rather than dictionary-only definitions.

## 3. Problem Statement and Original Requirements

Explain why a normal static directory/list of companies is insufficient and why structured capability matching was needed.

Describe the original Tasowheel pilot and source-confidence principle.

## 4. Scope and Design Principles

Separate current v1 scope from future possibilities.

Explicitly document important exclusions such as route sequencing, pricing, real-time scheduling/capacity and CAD interpretation where they are still not implemented.

## 5. Architecture Evolution — From Week 1 to Current State

Make this chronological and understandable.

At minimum cover:

1. provider questionnaire / machine list / curated assumptions;
2. YAML seed data;
3. initial Django/DRF foundation;
4. ontology profile and RDF generation;
5. RDFLib/Fuseki retrieval;
6. harmonization and H1–H9 evidence fidelity;
7. public API contract stabilization;
8. Vercel deployment;
9. PostgreSQL persistence;
10. trusted provider lifecycle;
11. publication/outbox pattern;
12. real Fuseki synchronization;
13. deployed end-to-end proof;
14. AWS readiness.

Include a table with columns such as:

```text
Stage | Problem being solved | What was added | Why it mattered | Result
```

## 6. Current Architecture

Provide at least two diagrams using Markdown fenced text/Mermaid only if the repo/docs conventions support it; plain ASCII is acceptable and safer.

One **layman flow**:

```text
Provider -> MDC -> Catalogue -> Consumer Search
```

One **technical flow** approximately:

```text
Trusted Provider Client
    |
    v
Django/DRF lifecycle API
    |
    v
PostgreSQL
  Provider / Offering
  ProviderPublication
  CatalogueSyncEvent
    |
    | trusted operator synchronization
    v
RDF generation
    |
    v
Fuseki Graph Store
    |
    | SPARQL
    v
Service discovery runtime
    |
    v
POST /api/service-discovery/search
    |
    v
Consumer / Marketplace
```

Explain remote Fuseki/RDFLib/YAML fallback behavior accurately after auditing code.

## 7. Repository Structure and Main Components

Explain important directories/modules, not every file.

For each major Django app describe responsibility and key files.

Note the convention:

```text
GET views -> views/get_views.py
POST/PATCH logic -> views/post_views.py
```

if current code confirms it.

## 8. Data Model and Persistence

Explain at both business and technical levels:

- Provider;
- Offering;
- ProviderCertification;
- ProviderPublication;
- CatalogueSyncEvent;
- status/revision/audit concepts;
- JSON/custom staging fields;
- why PostgreSQL is source of truth;
- why Fuseki is not the transaction database.

Include a simple entity relationship explanation/table derived from current models.

## 9. Provider Data, Controlled Vocabulary, and Flexible Custom Fields

Explain the important design rule:

> provider-entered business information may be flexible staging/custom data, while searchable controlled fields must use ontology-compatible vocabulary values.

Explain why arbitrary text such as an unrecognized service category cannot simply be inserted into a controlled field.

Use actual current vocabulary values/examples from repository code, not stale Week 1 values if they changed.

## 10. Tasowheel Pilot

Explain the approved provider-confirmed values without exposing raw confidential material unnecessarily.

Discuss known vs unknown data and why unknown fields are preserved rather than guessed.

Explain the v1 route-exclusion decision.

## 11. H1–H9 Harmonization and Evidence Fidelity

For each H phase, explain:

- what problem it addressed;
- what changed conceptually;
- why it mattered for trustworthy matching;
- the accepted verification state.

A lay reader should understand why H1–H9 was necessary even without reading code.

Do not fabricate phase meanings; derive them from tests/reports/code.

## 12. Development History and Milestones

Summarize:

- early Phase A–D;
- H1–H9;
- Phase 2 M1–M7;
- Phase 3 P3.0–P3.6.

For each milestone include purpose, major outcome and final status. Keep detailed command/test dumps in appendices rather than cluttering the main story.

## 13. Current API Strategy

Explain:

- `/api/` canonical paths;
- no URL `/v1` for current partner integration;
- `contract_version: "1.0"`;
- public read/search vs trusted lifecycle;
- legacy routes and why they remain/not recommended.

Add a concise endpoint summary table.

## 14. Complete Current API Reference

This is a critical section.

For **every current endpoint**, document:

```text
Method
Path
Audience (public/trusted/legacy)
Purpose
Feature flag requirements if relevant
Authentication requirements
Required headers
Path parameters
Request fields
Example request
Example success response
Relevant error responses
HTTP status codes
Operational notes
Source implementation files
```

Do not use invented schemas. Verify response shapes against current code/tests.

At minimum cover the canonical public endpoints and all trusted lifecycle endpoints listed earlier.

Clearly identify legacy endpoints separately.

## 15. End-to-End Provider Registration Walkthrough

Use a realistic, current-compatible example provider payload.

Show:

```text
validate -> publish -> GET provider -> GET offerings -> publication/outbox pending
```

Explain what happens inside the system at each step.

## 16. Updating an Existing Provider Safely

Explain:

```text
GET provider
    -> receive ETag
PATCH provider + concurrency header
    -> new ETag
stale old ETag
    -> 412
```

Include both canonical `If-Match` and current Vercel `X-MDC-If-Match` compatibility guidance without confusing them.

## 17. Offering Creation and Updating

Provide current-compatible examples for:

- list offerings;
- create offering;
- GET offering;
- capture ETag;
- PATCH offering;
- duplicate creation;
- stale ETag.

## 18. Consumer Service Discovery

Explain the current canonical search request fields and result structure in plain English.

Provide several repository-valid examples:

- gear search;
- shaft/metal-part search where supported;
- a known matching capability;
- an unknown or unmatched criterion if supported by current contract;
- the P3.5 controlled provider search example.

Do not reintroduce stale Week 1 `service_type` schema if current code uses `service_category`, etc. Audit current serializers first.

## 19. POSTMAN TESTING MANUAL — STEP BY STEP

This is one of the most important sections and must be suitable for a tester who is not a backend developer.

### 19.1 Explain why Postman is suitable

Explain installation/use conceptually without relying on screenshots.

### 19.2 Create a Postman environment

Recommended variables:

```text
base_url
lifecycle_token
actor_id
provider_id
provider_etag
offering_id
offering_etag
```

Use:

```text
base_url = https://maasai-mdc-v1.vercel.app
```

for the current pilot example, but clearly state that future AWS deployment will use a different base URL.

Never insert a real lifecycle token in the document. Use:

```text
<YOUR_TRUSTED_LIFECYCLE_TOKEN>
```

### 19.3 Build a Postman collection in an exact test order

At minimum:

```text
01 Health
02 Catalogue filters
03 Anonymous lifecycle validation -> expect 401
04 Valid provider validation
05 Invalid provider validation
06 Register provider
07 Duplicate provider -> expect 409
08 GET provider + capture ETag
09 PATCH provider without precondition -> expect 428
10 PATCH provider with ETag -> expect 200
11 PATCH provider with stale ETag -> expect 412
12 List offerings
13 Create offering
14 Duplicate offering -> expect 409
15 GET offering + capture ETag
16 PATCH offering without precondition -> expect 428
17 PATCH offering with ETag -> expect 200
18 PATCH offering with stale ETag -> expect 412
19 Canonical service discovery search
20 Optional legacy/version-path negative checks where useful
```

### 19.4 Show exact headers

Examples:

```http
Authorization: Bearer {{lifecycle_token}}
X-MDC-Actor-Id: {{actor_id}}
Content-Type: application/json
Accept: application/json
```

For current Vercel PATCH testing, explain the compatibility header:

```http
X-MDC-If-Match: {{provider_etag}}
```

and explain that canonical HTTP semantics remain `If-Match`.

### 19.5 Postman scripts

Provide copy/paste Postman test scripts for:

- checking status code;
- checking `contract_version`;
- storing provider ETag;
- storing offering ETag;
- storing returned provider/offering IDs when useful;
- asserting known errors (`401`, `409`, `428`, `412`);
- verifying search results include an expected provider.

Example concept:

```javascript
pm.test("HTTP 200", function () {
    pm.response.to.have.status(200);
});

const etag = pm.response.headers.get("ETag");
pm.expect(etag).to.exist;
pm.environment.set("provider_etag", etag);
```

Validate syntax and adapt to current Postman scripting conventions.

### 19.6 Explain rerun/idempotency behavior

A tester may already have created the example provider. Explain how `409` duplicate behavior changes a repeated run and recommend unique test provider IDs when a clean `201` is required.

### 19.7 Explain what Postman cannot do

Postman must **not** be presented as a public semantic-sync trigger because there is no public synchronization endpoint.

Explain that the P3.5 semantic sync was performed through the trusted Django management command/operator environment, not through a public REST call.

## 20. Reproducing the P3.4 Validation

Explain what `scripts/p34_provider_lifecycle_validation.py` does.

Include:

```text
45 passed
0 failed
```

Describe the categories of proof and how a tester can either run the script or perform equivalent Postman calls.

Do not print secrets in commands/examples.

## 21. Reproducing the P3.5 End-to-End Validation

Explain the full sequence:

```text
provider exists in PostgreSQL
provider absent from old Fuseki graph/search
        -> trusted sync management command
        -> updated Fuseki graph
        -> direct SPARQL proof
        -> deployed canonical search proof
```

Include accepted evidence:

```text
selected=4; succeeded=4; failed=0; noop=0; events=5
Fuseki triples=731
p34 provider returned by deployed canonical search
```

Explain that Vercel semantic sync remained disabled and why this is a safety decision.

## 22. RDF and Fuseki Explained for Non-Semantic-Web Readers

Explain:

- why RDF exists in addition to PostgreSQL;
- triples using simple examples;
- ontology namespace;
- SPARQL;
- Graph Store whole-graph replacement;
- how provider IDs/offering IDs appear in RDF;
- what the fallback runtime means.

## 23. Security and Safety Model

Cover:

- feature flags;
- bearer token;
- actor attribution;
- ETag concurrency;
- database transactions;
- outbox;
- operator-controlled sync;
- secret handling;
- why `.env` is not committed;
- HTTPS/production settings;
- limitations of the current pilot security boundary;
- what should change under AWS/Marketplace identity integration.

Do not include any real token, DB password, secret key, or full credential-bearing database URL.

## 24. Current Deployment and Operations

Explain current Vercel + Neon pilot and the Fuseki validation arrangement.

Clearly distinguish:

- current stable pilot components;
- temporary validation mechanisms such as a Cloudflare Quick Tunnel if documented;
- local operator requirements;
- what should not be treated as permanent production architecture.

Include important environment variable names, but not values/secrets.

## 25. Troubleshooting Guide

Use actual issues encountered in Phase 2/3 as examples, without exposing secrets:

- missing lifecycle token locally;
- sensitive Vercel env value not retrievable;
- authentication 401;
- missing actor 400;
- missing ETag 428;
- stale ETag 412;
- duplicate provider/offering 409;
- Fuseki query endpoint unreachable;
- Graph Store authentication issues;
- sync disabled;
- pending/failed outbox;
- temporary test database teardown/session issue if appropriate;
- dead temporary tunnel / deployed query endpoint implications;
- stale `/api/v1` examples.

For each, provide symptom -> likely cause -> safe resolution.

## 26. Current Limitations

Be explicit and non-marketing. Examples to verify/include:

- no real Marketplace frontend/integration was built in Phase 3;
- lifecycle service token is a replaceable pilot boundary, not final Marketplace OAuth/JWT identity;
- no public automatic sync endpoint;
- route sequencing/manufacturing planning not queryable in v1;
- no pricing/quotation engine;
- no real-time capacity/scheduling;
- no CAD/2D/3D geometry analysis implemented;
- current Vercel/Neon/temporary Fuseki arrangement is pilot infrastructure;
- permanent AWS deployment not yet executed.

## 27. Future Development

Separate **planned/credible next steps** from **ideas/not yet implemented**.

Include:

- actual AWS migration according to P3.6;
- Marketplace identity/integration when needed;
- durable AWS-hosted PostgreSQL;
- AWS-hosted/private Fuseki;
- CI/CD/monitoring/backups;
- stronger auth/identity;
- provider onboarding improvements;
- optional CAD/2D/3D feature extraction and manufacturability/routing support as a future extension, clearly marked not implemented;
- route-aware planning, capacity and quotation only as future work.

## 28. AWS Migration/Readiness Plan

Summarize P3.6 at enough detail for a future team to act on it.

Include:

- target components;
- migration sequence;
- database migration strategy;
- semantic graph rebuild/sync strategy;
- secrets/networking;
- deployment/CI-CD;
- monitoring;
- cutover;
- rollback;
- retirement of temporary Vercel/Neon/tunnel dependencies;
- what must remain unchanged in application/domain/API behavior.

Do not claim an AWS service choice that P3.6 intentionally leaves open unless the current plan explicitly names it as a recommendation rather than a decision.

## 29. Glossary

Provide a practical glossary for project managers/non-developers.

## 30. Appendices

At minimum include:

### Appendix A — Current Endpoint Matrix

One compact table of method/path/audience/auth/status.

### Appendix B — Environment Variables

Group by:

- Django;
- database;
- lifecycle;
- Fuseki;
- deployment.

Mark which are secrets and which are safe configuration.

### Appendix C — Example Payload Catalogue

Collect reusable current-compatible JSON examples for:

- provider validation/publication;
- provider patch;
- offering creation;
- offering patch;
- service discovery.

### Appendix D — Important Scripts and Commands

Include safe commands for:

- syntax/check;
- P3.3 verify;
- P3.4 lifecycle validation;
- P3.5 verification;
- management sync command;
- relevant Django tests.

Label commands that mutate state.

### Appendix E — Milestone Status Matrix

Show major phases and completion status.

### Appendix F — Source/Traceability Map

List the key repository files used for each chapter, so future maintainers know where the documentation came from.

---

# 7. API example quality requirements

Every API example must be **current and internally consistent**.

For each example:

1. Verify the request field names in the serializer.
2. Verify controlled values in current vocabularies/tests.
3. Verify response fields in the view/response builder/repository.
4. Verify HTTP status codes in implementation/tests.
5. Never show a field that the endpoint does not actually accept/return.
6. Use placeholder secrets only.
7. Use `contract_version: "1.0"` exactly where the current contract uses it.
8. Avoid stale `/api/v1` URLs except inside clearly labelled historical examples.
9. Avoid stale Week 1 `service_type` examples if current search uses `service_category`.
10. Do not expose internal diagnostics/evidence/provenance fields if the current external response deliberately hides them.

Where a response includes dynamic values (UUID publication IDs, ETags, timestamps), show clear placeholders such as:

```text
<publication-uuid>
<etag-value>
```

rather than pretending a fabricated value is real.

---

# 8. Writing style requirements

The document must be comprehensive but readable.

Use:

- plain English before technical detail;
- short introductory paragraphs for every major concept;
- diagrams and flowcharts;
- tables where comparison is easier than prose;
- numbered step-by-step procedures for testing/operations;
- callouts such as **Current**, **Historical**, **Important**, **Security**, **Future** where useful;
- concrete examples;
- cross-references between API, Postman, security, and architecture sections.

Avoid:

- unexplained jargon;
- marketing language;
- long raw code dumps;
- repeating the same milestone evidence in many sections;
- presenting assumptions as verified implementation;
- treating future ideas as current capability.

The document may be long. Do not optimize for brevity at the cost of missing necessary detail. A comprehensive technical manual in the approximate range of 15,000–30,000 words is acceptable if needed, but correctness and organization are more important than hitting a word count.

---

# 9. Self-audit before completion

Before finishing, perform a consistency audit of your draft.

Search the generated report for:

```text
/api/v1
service_type
catalog/search
If-Match
X-MDC-If-Match
contract_version
MDC_CATALOG_SYNC_ENABLED
MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN
DATABASE_URL
Cloudflare
Vercel
Neon
AWS
route
CAD
```

For every occurrence verify that it is correctly labelled as current/historical/future.

Also check:

- no real secrets are present;
- no full credential-bearing URLs are present;
- all canonical current endpoints match current `urls.py`;
- no phantom endpoint exists;
- Postman calls can be followed in sequence;
- request/response JSON is syntactically valid;
- Phase 3 is shown complete;
- P3.4 and P3.5 accepted evidence is correct;
- AWS is future/readiness, not already migrated;
- Postgres remains source of truth;
- Fuseki is semantic layer;
- route sequencing is not current v1 search capability;
- no Marketplace UI/integration is falsely claimed as implemented.

---

# 10. Git/output rules

1. Start from repository root and run:

```text
git pull --ff-only
git status --short --branch
```

2. Do not modify application code, tests, data, configuration, existing milestone reports or prompts.
3. Create/update only:

```text
mdc-catalog/docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md
```

4. Do not add temporary audit files to Git.
5. After writing, run `git diff --check` and inspect the report diff/stat.
6. If and only if the worktree contains **only this report file** as a tracked change, commit it with:

```text
docs: add comprehensive MDC implementation and user manual
```

7. Push normally to `origin/main` (no force push, no history rewrite).
8. If any unrelated tracked change appears, STOP before commit/push and report the blocker.

---

# 11. Final response format

Return a concise execution report only; do not paste the whole manual into the terminal response.

Use:

```text
# MDC MASTER REPORT GENERATION REPORT

## Repository audit
- audited commit: <sha>
- current API implementation checked: PASS/FAIL
- Phase 2/3 evidence checked: PASS/FAIL
- stale/historical API docs distinguished: PASS/FAIL

## Master document
- path: mdc-catalog/docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md
- major sections: <count>
- Postman manual included: PASS/FAIL
- current API payload/response examples included: PASS/FAIL
- P3.4 evidence included: PASS/FAIL
- P3.5 evidence included: PASS/FAIL
- P3.6/AWS future plan included: PASS/FAIL
- secrets scan: PASS/FAIL
- /api/v1 current-contract misuse scan: PASS/FAIL

## Git
- unrelated tracked changes: YES/NO
- commit: <sha or NONE>
- push: PASS/FAIL/NOT RUN

## Review notes
- list any unresolved ambiguity that ChatGPT must review

FINAL: READY_FOR_CHATGPT_MASTER_REPORT_REVIEW
```

Do not modify code to make the documentation easier to write. If the repository has genuine ambiguity, document it in `Review notes` and let ChatGPT resolve it during final review.
