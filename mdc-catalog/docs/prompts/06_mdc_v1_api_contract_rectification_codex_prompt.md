# Codex Task 06 — M6.1 MDC API Contract Rectification

> Historical note: this prompt was originally written with `/api/v1/...` compatibility aliases. That decision was superseded on 2026-09-04. The final M6.1 architecture uses stable `/api/...` routes only and explicit `contract_version` metadata.

## Objective

Complete **M6.1 — MDC API Contract Rectification** while preserving the harmonized H1-H9 service-discovery implementation.

Repository:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Project:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

Production deployment:

```text
https://maasai-mdc-v1.vercel.app
```

Read first:

```text
mdc-catalog/docs/Phase_2/08_mdc_v1_api_persistence_rectification_decisions.md
```

## Final non-negotiable route decision

The only long-term canonical external routes are:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Do not keep or introduce URL-versioned public routes such as:

```text
/api/v1/...
/api/v2/...
```

The previously introduced `/api/v1/...` route family must be removed during M6.1 because partner handoff has not yet established a compatibility dependency on it.

Future API evolution must use explicit contract metadata such as:

```json
"contract_version": "1.0"
```

while keeping the URL stable.

## Preserve H1-H9

Do not replace or weaken the harmonized H1-H9 service-discovery implementation:

```text
H5 matching/scoring
H6 RDF generation
H7 RDFLib retrieval
H8 optional Fuseki retrieval
H9 alignment
Fuseki -> RDFLib -> YAML fallback
```

External response shaping belongs at the API boundary.

## Legacy search

Keep:

```text
POST /api/catalog/search
```

only because it already exists and has been referenced in deliverables.

Do not evolve it, advertise it, or route canonical service discovery through it.

## Contract version behavior

For:

```text
POST /api/service-discovery/search
```

support optional:

```json
"contract_version": "1.0"
```

Requirements:

- omitted -> default `1.0`;
- explicit `1.0` -> accepted;
- unsupported explicit value -> clear `400`;
- response includes `contract_version`;
- no URL version negotiation.

GET public responses should also expose the active contract version.

## Public catalogue filters

`GET /api/catalog/filters` should return a concise harmonized Marketplace-facing contract based on current controlled registry/vocabularies, including where supported:

```text
contract_version
service_categories
part_families
part_types
materials
processes
certifications
```

Do not expose the old mixed legacy + nested registry payload as the public contract.

## Public service-discovery response shaping

Keep the rich H1-H9 runtime response internally, but shape the external API response deliberately.

The external response should include partner-relevant information only, such as:

```text
contract_version
request_id
service_category
part_family
part_type
result_count
results
```

Each result should expose provider/offering identity, match status/score, and relevant matched/unmatched/unknown capabilities.

Do not expose unnecessary internal fields such as raw backend selection, internal evidence/provenance, fallback diagnostics, or internal matching control flags.

## Provider/detail APIs

Existing provider/offering detail routes may remain for internal/legacy use, but do not advertise them to external partners until their backing model is harmonized.

Do not add new `/api/v1/providers...` routes.

## Provider publication

Provider-publication validation remains non-public.

Provider-publication write remains disabled in production because production publication requires:

- durable persistence;
- transactions/concurrency handling;
- authentication/authorization;
- update/version history;
- reliable PostgreSQL -> RDF -> Fuseki synchronization.

Do not implement the database in M6.1.

## Persistence direction

Document, but do not implement:

```text
PostgreSQL
```

with **Neon PostgreSQL** as the preferred Vercel-friendly candidate.

Conceptual direction:

```text
Marketplace/provider input
        ↓
validation + normalization
        ↓
PostgreSQL system of record
        ↓
RDF generation/update
        ↓
Fuseki semantic catalogue
```

Use PostgreSQL `JSONB` for flexible staging/custom provider fields where appropriate.

## View organization

Maintain:

```text
GET endpoint views  -> views/get_views.py
POST endpoint views -> views/post_views.py
```

## Required tests

Verify at minimum:

```text
/api/health                       -> 200
/api/catalog/filters              -> 200
/api/service-discovery/search     -> 200 for valid request

/api/v1/health                    -> 404
/api/v1/catalog/filters           -> 404
/api/v1/service-discovery/search  -> 404
```

Also verify:

- omitted `contract_version` defaults to `1.0`;
- explicit `1.0` succeeds;
- unsupported version returns `400`;
- public search response excludes deliberately internal fields;
- `/api/catalog/search` remains available as legacy;
- demo routes remain unavailable in production;
- provider publication remains `403` in production;
- focused H1-H9 tests stay green;
- full test suite has zero active failures.

## Vercel verification

Use existing project:

```text
maasai-mdc-v1
```

Follow:

```text
Preview deploy -> verify -> Production deploy -> verify
```

Do not create another Vercel project.

Verify the three stable `/api/...` routes externally and confirm `/api/v1/...` returns `404` after deployment.

## Required report

Create:

```text
mdc-catalog/docs/Phase_2/09_mdc_v1_api_contract_rectification_report.md
```

Include:

1. M6.1 status;
2. final route matrix;
3. `contract_version` behavior;
4. final filter contract;
5. final external search request/response contract;
6. H1-H9 preservation evidence;
7. legacy/internal route handling;
8. PostgreSQL/Neon design-only architecture;
9. files changed;
10. local test counts;
11. Preview verification;
12. Production verification;
13. commits;
14. final readiness marker.

Finish with exactly one:

```text
READY_TO_UPDATE_PARTNER_API_DOCUMENT
```

or:

```text
NOT_READY_TO_UPDATE_PARTNER_API_DOCUMENT
```

Do not start the database or partner-integration milestone automatically.
