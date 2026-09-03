
## 1. Week 1 status: finalized

Yes — based on your confirmations, **Week 1 is finalized**.

The Week 1 exit criteria were: API contract approved, ontology profile approved, seed-data template approved, Tasowheel seed data has at least one valid offering, and matching policy approved.  Your confirmations close the remaining decisions: provider ID, primary offering ID, TSW capability ranges, unknown fields, excluded route fields, DIN quality rule, lead-time rule, and unsupported-field behavior.

We can now move into **Week 2: Build catalogue backbone**, starting with Django app creation. The baseline architecture already defines the runtime flow from marketplace JSON to Django validation, canonical `SearchRequest`, SPARQL query builder, Fuseki, result normalization, scoring, and explanation. 

---

# 2. Recommended Django app structure

Use the agreed app structure from the architecture document. The five apps are: `api`, `catalog`, `ontology`, `providers`, and `search`. Their responsibilities are already defined in the baseline architecture. 

Recommended structure:

```text
backend/
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── test.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── urls.py
│   │   │   ├── views.py
│   │   │   └── serializers.py
│   │   └── apps.py
│   ├── ontology/
│   │   ├── vocabularies.py
│   │   ├── mappings.py
│   │   ├── constants.py
│   │   └── apps.py
│   ├── providers/
│   │   ├── loaders.py
│   │   ├── services.py
│   │   └── apps.py
│   ├── search/
│   │   ├── request.py
│   │   ├── normalizer.py
│   │   ├── query_builder.py
│   │   ├── sparql_client.py
│   │   └── apps.py
│   └── catalog/
│       ├── scoring.py
│       ├── explanation.py
│       ├── result_builder.py
│       └── apps.py
└── tests/
```

## App responsibilities

| App         | Responsibility                                                               |
| ----------- | ---------------------------------------------------------------------------- |
| `api`       | REST endpoints, serializers, URL routing, OpenAPI integration                |
| `ontology`  | Controlled vocabularies, ontology URI mappings, constants                    |
| `providers` | Reading provider/offering seed data and provider detail logic                |
| `search`    | Canonical request normalization, SPARQL query builder, Fuseki client         |
| `catalog`   | Match scoring, matched/unknown/unmatched explanation, final response shaping |

Important: **do not put Tasowheel-specific business logic inside the app code**. Tasowheel should only appear in seed data, RDF instances, test fixtures, or demo examples.

---

# 3. First development tasks for creating the Django apps

## Task 1 — Create app folders

Create these apps under:

```text
backend/apps/
```

Recommended apps:

```text
api
catalog
ontology
providers
search
```

Start with empty/skeleton apps only. Do not implement search logic yet.

## Task 2 — Register apps in settings

Add the apps to `INSTALLED_APPS`.

Use stable app paths such as:

```text
apps.api
apps.catalog
apps.ontology
apps.providers
apps.search
```

Also ensure `rest_framework`, `drf_spectacular`, and `corsheaders` are registered when needed.

## Task 3 — Create initial URL structure

Start with:

```text
/api/v1/health
/api/v1/catalog/filters
```

Do **not** start with `/catalog/search` first. The health and filters endpoints are simpler and validate the project structure.

The API contract defines `/health`, `/catalog/filters`, `/catalog/search`, `/providers/{provider_id}`, and `/offerings/{offering_id}` as the v1 endpoints. 

## Task 4 — Implement controlled vocabularies

Create static controlled vocabulary definitions in the `ontology` app.

Start with:

* service types
* part families
* processes
* materials
* material grades
* certifications
* quality standards

The existing ontology profile already defines service types, part families, processes, materials, certifications, and Tasowheel offering identifiers. 

## Task 5 — Implement `/api/v1/health`

This confirms the Django API is working.

Expected response:

```json
{
  "status": "ok",
  "service": "maasai-mdc",
  "version": "v1"
}
```

The API contract says this endpoint should return HTTP `200` when Django is running and does not need Fuseki for the basic check. 

## Task 6 — Implement `/api/v1/catalog/filters`

This endpoint returns the controlled vocabulary values used by the marketplace UI. It can be implemented before Fuseki because it can come from static backend vocabulary definitions. 

---

# 4. Suggested order of implementation

Use this order:

## Phase A — Django foundation

1. Create `apps/` package.
2. Create the five Django apps.
3. Register apps in settings.
4. Confirm `python manage.py check` passes.
5. Confirm development server still runs.

## Phase B — API skeleton

6. Create `/api/v1/` URL routing.
7. Implement `/api/v1/health`.
8. Add basic API test for `/health`.

## Phase C — Controlled vocabularies

9. Add controlled vocabularies in `ontology`.
10. Add material grades from TSW: `18CrNiMo7-6`, `16MnCr5`, `20MnCr5`.
11. Add certification values: `ISO9001_2015`, `ISO14001_2015`, partial ISO/TS 16949, APQP.
12. Implement `/api/v1/catalog/filters`.

The TSW questionnaire confirms batch size, module/DP range, diameter range, quality up to DIN4, weight up to about 200 kg, material grades, lead time, and certifications. 

## Phase D — Provider seed data access

13. Add YAML loading service in `providers`.
14. Load `data/curated/tasowheel_offerings.yaml`.
15. Implement internal provider/offering lookup by ID.
16. Later expose `/providers/{provider_id}` and `/offerings/{offering_id}`.

## Phase E — Search foundation

17. Create canonical `SearchRequest` structure.
18. Add request normalization.
19. Add validation using DRF serializers.
20. Only after this, begin SPARQL/RDF/Fuseki work.

---

# 5. Database preparation

For now: **do not create provider/offering database models**.

Reason: for v1, the catalogue source of truth is:

```text
curated YAML → RDF/Turtle → Fuseki → SPARQL
```

The architecture already defines this lifecycle. 

Use Django’s default SQLite database only for framework-level needs. Later, we may add database models for:

| Future model        | Purpose                               |
| ------------------- | ------------------------------------- |
| `SearchLog`         | Store search request/response history |
| `ImportJob`         | Track RDF/YAML import runs            |
| `ProviderSnapshot`  | Cache provider summaries              |
| `VocabularyVersion` | Track vocabulary changes              |

But for the first implementation slice, avoid database complexity.

---

# 6. Risks and design decisions for future provider extensibility

## Keep Tasowheel as data, not logic

Bad pattern:

```text
if provider_id == "tasowheel":
    apply special search logic
```

Good pattern:

```text
for each offering in catalogue:
    apply the same matching rules
```

TSW should be the first provider record, not a hardcoded branch.

## Keep provider capabilities generic

Your seed-data format should support:

```text
providers:
  - provider_id: tasowheel
  - provider_id: future_provider_1
  - provider_id: future_provider_2
```

Each provider should have one or more offerings. Search should operate over all offerings, not over one known provider.

## Keep vocabularies extensible

For future providers, you will need new:

* materials
* material grades
* processes
* service types
* certifications
* part families
* industry sectors

Put these in the `ontology` app as controlled vocabulary data, not scattered across serializers or views.

## Separate offering-level and machine-level capability

Even though TSW has machine data, do not let machine-level maximums automatically override provider-confirmed offering-level values. Offering-level values should drive v1 search. Machine-level data can support future detail views or advanced matching.

## Preserve unknown fields

Surface finish and general tolerance remain unknown for TSW. The system must continue to return `unknown_attributes` instead of pretending those fields are supported. The API contract already expects unknown attributes in the response. 

## Keep search pipeline provider-neutral

The future search flow should be:

```text
SearchRequest
→ validate
→ normalize to ontology concepts
→ query all provider offerings
→ score all results
→ return ranked/explained results
```

Not:

```text
SearchRequest
→ check Tasowheel
→ return Tasowheel
```

---

# 7. Clear next step

Start coding with this sequence:

1. Create the five Django apps: `api`, `catalog`, `ontology`, `providers`, `search`.
2. Register them in Django settings.
3. Create API v1 routing.
4. Implement `/api/v1/health`.
5. Add controlled vocabularies in `ontology`.
6. Implement `/api/v1/catalog/filters`.
7. Add a simple test for both endpoints.

That gives you the first clean backend slice and keeps the project ready for RDF/Fuseki integration next.
