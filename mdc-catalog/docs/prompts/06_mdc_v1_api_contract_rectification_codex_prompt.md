# Codex Task 06 — M6.1 MDC API Contract Rectification

## Recommended Codex configuration

Use:

- **Model / intelligence:** GPT-5.6 Sol
- **Reasoning:** Medium
- Increase to **High only temporarily** if a real API-compatibility or deployment conflict requires deeper analysis.
- Do not use Ultra / Extra-High reasoning.

Keep the task tightly scoped. The goal is to rectify the API contract once, preserve H1-H9, and avoid repeatedly revisiting endpoint/version decisions.

---

# Context

Git repository:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

MDC project:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

Current production deployment:

```text
https://maasai-mdc-v1.vercel.app
```

Important Phase 2 decision report:

```text
mdc-catalog/docs/Phase_2/08_mdc_v1_api_persistence_rectification_decisions.md
```

Also review the previous M1-M6 reports and the current code/tests before changing anything.

**Important Git change from earlier milestones:** `mdc-catalog/docs/` is now intentionally tracked in Git. Do not remove it from tracking or re-add ignore rules that hide these reports/prompts.

---

# Objective

Complete **M6.1 — MDC API Contract Rectification**.

The milestone must establish a coherent long-term API foundation for the Marketplace and other MaaSAI components while preserving the current harmonized H1-H9 implementation.

The core decisions are already agreed. This task is implementation and verification, not another broad architecture debate.

---

# Non-Negotiable Decisions

## 1. Stable canonical routes

The long-term partner-facing routes are:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

These URLs should remain stable as MDC evolves.

Do **not** plan future progression around `/api/v2/`, `/api/v3/`, etc.

## 2. Existing `/api/v1/...` routes

Keep these working as compatibility aliases:

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

They are not the preferred long-term routes for new integrations.

Do not remove them during M6.1.

## 3. Legacy catalogue search

```text
POST /api/catalog/search
```

This is a separate legacy implementation.

Decision:

- retain it because it already exists and has been referenced in deliverables;
- do not evolve it;
- do not route the canonical service-discovery API through it;
- do not advertise it to new partners.

## 4. Preserve H1-H9

The current source of truth is the harmonized H1-H9 service-discovery implementation, including:

- harmonized registry;
- provider publication normalization support;
- harmonized provider YAML;
- search request serializer/normalizer;
- H5 matching/scoring;
- H6 RDF generation;
- H7 RDFLib retrieval;
- H8 optional remote Fuseki retrieval;
- H9 matching alignment;
- Fuseki -> RDFLib -> YAML runtime fallback.

Do not rewrite or weaken H1-H9 to simplify the external API.

External response shaping must occur at the API boundary.

---

# Step 1 — Audit the Current API Boundary

Inspect the actual repository, especially:

```text
backend/config/urls.py
backend/apps/api/urls.py
backend/apps/api/urls_v1.py
backend/apps/api/views/get_views.py
backend/apps/api/views/post_views.py
backend/apps/api/views.py
backend/apps/api/*serializers*.py
backend/apps/api/response_utils.py
backend/apps/ontology/service_discovery_registry.py
backend/apps/search/service_discovery_runtime_search.py
backend/tests/
```

Confirm which routes call the same view/service and which are genuinely separate legacy implementations.

Before modifying payloads, search the repository for consumers of current response keys so API shaping does not accidentally break internal/demo code.

---

# Step 2 — Introduce Contract Version Metadata Without URL Version Churn

Use the explicit field:

```text
contract_version
```

Baseline supported contract:

```text
1.0
```

## POST search request

For:

```text
POST /api/service-discovery/search
```

add optional request field:

```json
{
  "contract_version": "1.0"
}
```

Requirements:

- `contract_version` is optional for backward compatibility;
- when omitted, default safely to `1.0`;
- `1.0` must be accepted;
- unsupported explicit versions must return a clear `400` validation error;
- do not change existing required business fields;
- do not require Marketplace to change URL when a future contract is introduced.

The `/api/v1/service-discovery/search` alias should use the same contract handling.

## Responses

Include:

```json
"contract_version": "1.0"
```

in the external responses for the stable partner-facing APIs where appropriate.

For GET endpoints there is no request-body negotiation in M6.1. Return the current external contract version in the response.

Do not invent complex Accept-header/media-type negotiation in this milestone.

---

# Step 3 — Rectify Catalogue Filters for the Harmonized Marketplace Contract

Current deployed filter output contains a mixture of older catalogue fields and nested harmonized service-discovery metadata.

The stable external endpoint:

```text
GET /api/catalog/filters
```

should return a concise harmonized Marketplace-facing representation based on the current service-discovery registry/data.

Target external keys should include, where supported by the actual registry:

```text
contract_version
service_categories
part_families
part_types
materials
processes
certifications
```

The exact values must come from current controlled vocabularies/registry; do not invent values.

Important:

- preserve the internal vocabulary/registry services if legacy or internal code still needs them;
- shape the public API response at the API boundary rather than deleting useful internal structures;
- `/api/v1/catalog/filters` should remain a compatibility alias to the same rectified external contract;
- do not expose unnecessary legacy-only filter keys merely because internal Python structures contain them;
- if a field cannot be safely produced from current harmonized data, document it rather than fabricate it.

Add/update tests for the exact external filter response contract.

---

# Step 4 — Create an Explicit External Service-Discovery Response Shape

The H1-H9 runtime currently returns rich internal matching/retrieval information.

Do not expose every internal implementation detail to Marketplace/partners.

Implement a deliberate external response adapter/serializer/DTO at the API boundary.

## Preserve internally

Internal runtime objects may continue to contain fields such as:

```text
query_interpretation
search_engine
fallback diagnostics
internal matching details
internal provenance/evidence details
implementation warnings
```

## External response

The public response should be concise but useful to the Marketplace.

At minimum retain information required to understand the result, such as:

```text
contract_version
request_id
result_count
results
```

Each external result should expose only partner-relevant fields supported by the actual H1-H9 result, for example:

```text
provider_id
provider_name
offering_id
offering_name
match_status
match_score or equivalent, if part of the agreed external need
capabilities / matched values relevant to the request
```

Do not blindly use this example as a schema. Inspect the actual result object and choose the smallest coherent external representation.

### Important information-hiding rule

Do not merely hide fields in documentation while still returning them over the public API.

The API response itself must be shaped.

### Compatibility rule

Preserve H1-H9 internal tests at the service/matcher layer.

Update API endpoint tests to assert the external shape.

If another internal component genuinely relies on the rich API response, identify it before changing the endpoint and preserve a clean internal service-level access path rather than exposing implementation details publicly.

Do not create a new public debug endpoint unless there is strong evidence it is required.

---

# Step 5 — Provider APIs Stay Internal / Legacy for Now

Do not promote or advertise provider browsing APIs during M6.1.

Current/legacy provider/detail routes may remain working as currently implemented, but do not add new canonical external endpoints merely to match the draft Marketplace PDF.

In particular, do not implement a new public contract for:

```text
GET /api/v1/providers
GET /api/v1/providers/{provider_id}
```

unless the repository already contains an intentionally harmonized implementation that can be exposed without using the legacy seed schema. If not, leave them internal/planned and document this clearly.

Offering-detail APIs follow the same rule.

Do not remove working legacy routes that are still test-covered.

---

# Step 6 — Provider Publication Validation Remains Non-Public

Do not expose or advertise:

```text
/api/provider-publication/validation
/api/v1/provider-publication/validation
```

as an external partner API during M6.1.

If validation code already exists internally, preserve it and test it at its existing layer.

Do not add an anonymous public validation route merely because it appears in the draft Marketplace document.

---

# Step 7 — Provider Publication Write Remains Disabled in Production

Keep the current file-backed publication write disabled on Vercel production.

Do not implement DB persistence in M6.1.

The current publication write is deferred because a production state-changing workflow requires more than choosing a database:

- durable persistence;
- transactional consistency;
- concurrency handling;
- authentication/authorization;
- update/version history;
- reliable PostgreSQL -> RDF -> Fuseki synchronization.

Keep production safety behavior intact, including the current publication feature gate.

---

# Step 8 — Define the PostgreSQL Persistence Architecture, But Do Not Implement It

M6.1 must produce a concise architecture section to guide the next persistence milestone.

Recommended operational DB:

```text
PostgreSQL
```

Preferred Vercel-friendly candidate:

```text
Neon PostgreSQL
```

Do not provision Neon and do not create Django migrations/models in this milestone unless a tiny model change is strictly required for API rectification (unlikely and should be justified).

Document a proposed minimum operational model covering concepts such as:

```text
Provider
Offering
ProviderPublication / PublicationVersion
publication status/history
created_at / updated_at
ownership/submitted_by placeholders for future auth
flexible staging/custom provider fields using JSONB
normalized/controlled capability relationships
```

Also define the intended synchronization direction:

```text
Marketplace/provider input
        ↓
validation + normalization
        ↓
PostgreSQL transaction / system of record
        ↓
RDF generation/update
        ↓
Fuseki semantic catalogue
```

Recommend how to avoid silent PostgreSQL/Fuseki divergence, e.g. an explicit publication/update job/status or outbox-style synchronization concept. Keep this conceptual only in M6.1.

---

# Step 9 — Route Classification Must Be Explicit in Code/Tests/Report

At the end, classify routes into these categories:

## Stable external

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

## Compatibility aliases

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

## Legacy retained

```text
POST /api/catalog/search
```

plus existing legacy provider/offering detail routes where applicable.

## Trusted/internal/deferred

Provider publication validation and write workflows.

## Demo/internal

```text
/api/demo/*
```

Do not make route classification dependent only on documentation; tests should enforce the key public/production behavior.

---

# Step 10 — Preserve View Organization Convention

Maintain the established MDC convention:

```text
GET endpoint views  -> views/get_views.py
POST endpoint views -> views/post_views.py
```

If response-adapter/helper modules are needed, place them in a clear API-layer module rather than mixing them into search/matcher internals.

---

# Step 11 — Tests

Add/update only the tests necessary to prove the rectified contract.

At minimum test:

## Search contract

- unversioned canonical search accepts omitted `contract_version` and defaults to `1.0`;
- explicit `contract_version: "1.0"` succeeds;
- unsupported explicit version returns `400`;
- `/api/v1/service-discovery/search` alias behaves consistently;
- external response contains `contract_version`;
- external response excludes fields deliberately classified internal-only;
- H1-H9 internal service/matcher tests remain green.

## Filters

- `/api/catalog/filters` returns the harmonized external keys;
- `/api/v1/catalog/filters` compatibility alias returns the same external contract;
- values come from current controlled registry/vocabularies.

## Health

- `/api/health` remains available;
- `/api/v1/health` remains available;
- include `contract_version` if that is the agreed final response shape.

## Safety

- `/api/catalog/search` still exists as legacy if current tests require it;
- demo routes remain unavailable in production;
- provider publication write remains disabled in production.

Do not duplicate the full H1-H9 test suite logic in API tests.

---

# Step 12 — Local Verification

Run at minimum:

```powershell
python manage.py check
python manage.py test -v 2
```

Also rerun the focused H1-H9/service-discovery suite.

Run production safety/deployment checks where applicable:

```powershell
python manage.py check --deploy
```

with the required process-only production environment values.

Record exact counts.

No active test failures are acceptable for M6.1 completion.

---

# Step 13 — Git Handling

The docs folder is now intentionally tracked.

Do not remove:

```text
mdc-catalog/docs/
```

from Git.

After local verification:

1. review `git status` and diff;
2. commit only M6.1 changes;
3. include the M6.1 implementation report under `docs/Phase_2/` in the commit;
4. push the verified commit to `origin/main` before final Vercel deployment.

Recommended implementation commit message:

```text
feat: rectify MDC stable API contract
```

Do not force-push.

---

# Step 14 — Vercel Preview Then Production Redeployment

The current Vercel project is:

```text
maasai-mdc-v1
```

Use the existing linked project.

Do not create a new Vercel project.

Use current Vercel CLI, preferably:

```powershell
npx vercel@latest
```

Follow:

```text
Preview deploy
    ↓
external smoke verification
    ↓
Production deploy
    ↓
external verification
```

Do not configure database or external Fuseki during this redeployment.

---

# Step 15 — External Vercel Verification

Verify the stable canonical routes on Preview, then Production:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Verify:

- HTTP status;
- `contract_version` behavior;
- concise external response shape;
- actual search returns results using the existing H1-H9 runtime;
- actual observed backend remains RDFLib/YAML fallback when Fuseki is not configured.

Also verify compatibility aliases:

```text
GET  /api/v1/health
GET  /api/v1/catalog/filters
POST /api/v1/service-discovery/search
```

Verify production safety:

```text
/api/demo/*                 -> unavailable
/api/provider-publication   -> disabled
```

Do not advertise legacy/internal routes.

---

# Step 16 — Do Not Update the Marketplace PDF Yet

The draft Marketplace PDF is evidence for desired external information, but M6.1 should first make the deployed API coherent.

Do not attempt to edit the PDF during this Codex task.

The M6.1 report must provide the exact final deployed request/response contract so the partner document can be updated afterward.

Keep payload examples in the report short.

---

# Required Deliverable

Create:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2\09_mdc_v1_api_contract_rectification_report.md
```

This report is intentionally tracked in Git.

Include:

## 1. M6.1 status

Use:

```text
completed
partially completed
blocked
```

## 2. Final route matrix

```text
Method | Route | Classification | External? | Implementation backing
```

## 3. Contract-version behavior

State:

- supported value;
- omitted-value behavior;
- unsupported-version behavior;
- response behavior.

## 4. Final external filter contract

List the exact external keys and one short sample.

## 5. Final external service-discovery contract

List:

- required request fields;
- optional `contract_version`;
- exact top-level response keys;
- exact result-level external keys;
- internal fields deliberately excluded.

Include one short request and response example from the verified implementation.

## 6. H1-H9 preservation

Confirm internal H1-H9 architecture was not replaced and give focused test result.

## 7. Legacy/internal handling

State status of:

```text
/api/catalog/search
provider list/detail
offering detail
publication validation
publication write
/api/demo/*
```

## 8. PostgreSQL persistence architecture proposal

Concise only:

- why PostgreSQL;
- Neon recommendation;
- minimum conceptual entities;
- JSONB staging/custom fields;
- PostgreSQL -> RDF -> Fuseki synchronization concept;
- explicitly state that DB was **not implemented** in M6.1.

## 9. Files changed

```text
Path | Change | Reason
```

## 10. Local verification

Exact commands and test counts.

## 11. Vercel Preview verification

```text
Method | Stable endpoint | HTTP status | Key result
```

## 12. Vercel Production verification

Use production base:

```text
https://maasai-mdc-v1.vercel.app
```

Report exact external results.

## 13. Git/deployment commits

List commit hashes/messages created during M6.1.

## 14. Partner-document readiness

End with one:

```text
READY_TO_UPDATE_PARTNER_API_DOCUMENT
```

or:

```text
NOT_READY_TO_UPDATE_PARTNER_API_DOCUMENT
```

If not ready, state exact blockers.

---

# Scope Restrictions

Do not:

- add `/api/v2/` routes;
- remove `/api/v1/` compatibility aliases;
- replace H1-H9;
- evolve `/api/catalog/search`;
- implement provider list/detail as a new external contract unless already harmonized and justified by repository evidence;
- expose publication validation publicly;
- enable publication write in production;
- provision PostgreSQL/Neon;
- create Django DB migrations for the future persistence architecture;
- provision external Fuseki;
- add authentication/rate limiting in this milestone;
- rewrite the Marketplace PDF;
- create a new Vercel project;
- perform unrelated refactors.

---

# Final Console Response

Return only:

1. M6.1 status
2. canonical stable routes
3. `/api/v1/...` compatibility status
4. `contract_version` behavior
5. external filter contract status
6. external search-response shaping status
7. H1-H9 focused test result
8. full test result
9. Preview deployment result
10. Production deployment result
11. production base URL
12. publication-write safety status
13. PostgreSQL architecture status (design only / not implemented)
14. implementation commit hash/message
15. `READY_TO_UPDATE_PARTNER_API_DOCUMENT` or `NOT_READY_TO_UPDATE_PARTNER_API_DOCUMENT`
16. report path

Do not start the next persistence or partner-integration milestone automatically.
