# MaaS Dynamic Catalogue — Architecture v1

**Status:** Week 1 finalized baseline  
**Project:** MaaSAI MaaS Dynamic Catalogue  
**Scenario:** Basic structured-search scenario  
**Pilot:** Tasowheel / TSW gear and shaft manufacturing  
**Source of truth:** `MaaS_Dynamic_Catalogue_Basic_Scenario_Technical_Specification_v1_0.md`

---

## 1. Purpose

This document describes the v1 architecture for the **MaaS Dynamic Catalogue (MDC)** basic scenario.

The goal of v1 is to build a first operational catalogue service that allows the **Cloud MaaS Marketplace** to send a structured manufacturing request and receive suitable **MaaS Provider Offering** results.

For v1, the system focuses on the **Tasowheel / TSW pilot**, especially gear and shaft manufacturing. The catalogue will use curated seed data and an ontology-backed RDF graph to search for suitable offerings.

---

## 2. Architectural principles

1. **Structured input first**  
   v1 accepts marketplace form input as structured JSON. Natural-language request parsing is reserved for the advanced scenario.

2. **Canonical request object**  
   All input must be normalized into one internal `SearchRequest` structure before query generation.

3. **Ontology-backed search**  
   Search is performed against an RDF/OWL knowledge graph through SPARQL.

4. **Template-based SPARQL only**  
   The backend must not generate free-form SPARQL from raw user text. SPARQL must be assembled from validated fields and predefined templates.

5. **ProviderOffering as the search result**  
   Search returns provider offerings, not only provider records.

6. **Explainable matching**  
   Results must include matched, unknown, and unmatched attributes, with evidence where available.

7. **Unknown is not automatically failure**  
   If a capability is not confirmed in v1 data, the result may still be returned as `partial_match` with the field listed under `unknown_attributes`.

8. **Routes excluded from v1**  
   Manufacturing route steps, operation sequences, and machine-to-route assignments are not modelled or queried in this version.

---

## 3. Scope

### 3.1 In scope for v1

| Area | Decision |
|---|---|
| Pilot | Tasowheel / TSW only |
| Scenario | Basic structured-search scenario |
| Input mode | Marketplace form fields, checkboxes, dropdowns |
| Search target | `ProviderOffering` |
| Knowledge source | Provider-confirmed seed data + ontology profile |
| Query mechanism | Deterministic SPARQL templates |
| Backend | Python + Django + Django REST Framework |
| Ontology store | RDF/OWL in Turtle + Apache Jena Fuseki |
| Result type | Matched offerings with evidence and unknowns |
| Matching style | Hard filters + soft filters + simple score + explanation |
| Data update mode | Manual/curated seed data |
| Material detail | Generic material + material grades |
| Lead time | Normal provider-confirmed 8–12 week range, case-dependent |

### 3.2 Out of scope for v1

| Area | Reason |
|---|---|
| Route fields / route steps | User decision: not needed in this version |
| Natural-language request parsing | Reserved for advanced scenario |
| LLM-based extraction | Reserved for advanced scenario |
| Live ERP/MES integration | Too large for v1 |
| Real-time capacity planning | Requires provider system integration |
| Pricing engine | Insufficient pricing data |
| Smart contract negotiation | Later MaaSAI phase |
| Full disruption recommendation | Later reasoning/recommendation phase |
| Multi-provider process-chain planning | Later Consumer Planner integration |
| Machine-level public search | Machine data is supporting context only for v1 |

---

## 4. High-level system architecture

```text
Cloud MaaS Marketplace UI
        |
        | Structured SearchRequest JSON
        v
Django REST API
        |
        | Request validation
        v
Canonical SearchRequest
        |
        | Field-to-ontology mapping
        v
SPARQL Query Builder
        |
        | Deterministic SPARQL templates
        v
Apache Jena Fuseki
        |
        | RDF/OWL catalogue graph
        v
Raw SPARQL Results
        |
        | Result normalization + scoring + explanation
        v
Marketplace Response JSON
```

---

## 5. Main runtime flow

1. User enters manufacturing requirements in the Cloud MaaS Marketplace UI.
2. Marketplace sends a structured request to `POST /api/v1/catalog/search`.
3. Django REST Framework validates the request payload.
4. The API layer normalizes the request into a canonical `SearchRequest`.
5. The search layer maps request fields to ontology concepts and query templates.
6. The SPARQL query builder assembles deterministic SPARQL from predefined templates.
7. The Fuseki query service executes the query against the RDF graph.
8. Raw SPARQL results are normalized into provider/offering objects.
9. The catalogue layer applies matching status, scoring, and explanation logic.
10. API returns JSON with matched offerings, evidence, unknown fields, and unmatched fields.

---

## 6. Repository structure

```text
mdc-catalog/
├── backend/
│   ├── manage.py
│   ├── config/
│   ├── apps/
│   │   ├── api/
│   │   ├── catalog/
│   │   ├── ontology/
│   │   ├── providers/
│   │   └── search/
│   └── tests/
├── ontologies/
│   ├── mdc_core.ttl
│   ├── mdc_tasowheel_profile.ttl
│   ├── mdc_mappings.ttl
│   └── shacl/
│       └── mdc_v1_shapes.ttl
├── data/
│   ├── raw/
│   │   └── tasowheel/
│   ├── curated/
│   │   └── tasowheel_offerings.yaml
│   └── generated/
│       └── tasowheel_catalog.ttl
├── scripts/
├── docs/
├── docker/
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 7. Django apps and responsibilities

| App | Responsibility |
|---|---|
| `api` | Versioned REST API routes, serializers, views, OpenAPI schema integration |
| `catalog` | Main catalogue orchestration, result shaping, scoring, match explanation |
| `ontology` | Ontology constants, URI mappings, controlled vocabularies, SHACL hooks |
| `providers` | Provider/offering seed data handling and provider detail responses |
| `search` | Canonical request normalization, SPARQL template assembly, Fuseki query service |

---

## 8. Data architecture

### 8.1 Data sources

| Source | Purpose |
|---|---|
| TSW provider questionnaire | Main provider-confirmed offering-level data |
| TSW machine list | Supporting process/machine context; not direct offering search limits |
| Curated YAML seed data | Normalized provider/offering records |
| Ontology profile | Shared semantic classes, properties, and vocabulary |
| Generated RDF | Machine-readable catalogue graph loaded into Fuseki |

### 8.2 Data priority

Use this priority when values differ:

1. provider-confirmed questionnaire value
2. provider-confirmed machine/context value
3. curated project value
4. public-web value
5. inferred value

### 8.3 Data lifecycle

```text
Curated YAML seed data
→ RDF generation script
→ Generated Turtle graph
→ SHACL validation
→ Fuseki load
→ SPARQL search
→ API response
```

### 8.4 Provenance and confidence

Every important capability value should include:

| Field | Purpose |
|---|---|
| `source_type` | Indicates whether the value comes from provider confirmation, machine list, public web, curated data, etc. |
| `confidence` | Indicates whether the value is declared, curated, estimated, inferred, unknown, or not confirmed |
| `source_note` | Optional explanation or evidence note |

---

## 9. Matching architecture

### 9.1 Hard filters

Hard filters can reject a result when known data proves incompatibility.

Examples:

- requested service type must match
- requested diameter must not exceed 450 mm for TSW v1
- requested module range must overlap 0.3–10
- requested batch size should be within 100–2000 pcs
- requested weight should not exceed approx. 200 kg when weight is supplied
- requested known certification must be present if configured as hard

### 9.2 Soft / conditional filters

Soft filters improve score or produce conditional explanations.

Examples:

- process match
- industry match
- lead-time match, because TSW lead time is normal/case-dependent
- material family match when exact material grade is not supplied

### 9.3 Unknown fields

Unknown fields are returned explicitly when v1 does not have confirmed data.

Examples:

- surface finish Ra
- general ± tolerance in mm
- aerospace traceability

---

## 10. API architecture

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/health` | Health check |
| `GET /api/v1/catalog/filters` | Returns controlled vocabulary values for marketplace UI |
| `POST /api/v1/catalog/search` | Main structured catalogue search |
| `GET /api/v1/providers/{provider_id}` | Provider detail |
| `GET /api/v1/offerings/{offering_id}` | Offering detail |

The full request and response structure is documented in `docs/api-contract-v1.md`.

---

## 11. Security and privacy assumptions for v1

v1 is a local development and demo-oriented system. It does not yet implement full production security.

Still, the following principles apply:

- Do not expose confidential provider data.
- Do not expose route or internal operation sequence data in v1.
- Only use public, curated, or explicitly confirmed capability fields.
- Do not expose raw internal comments in API responses unless marked safe.
- Keep provenance metadata available for traceability.
- Avoid direct user-controlled SPARQL injection by using template-based query assembly.

---

## 12. Testing strategy

### 12.1 Unit tests

- API serializer validation
- controlled vocabulary mapping
- canonical `SearchRequest` normalization
- SPARQL template assembly
- scoring calculation

### 12.2 Integration tests

- Django search service calls Fuseki
- RDF graph loads correctly
- SPARQL templates return expected TSW results

### 12.3 Acceptance tests

The v1 acceptance scenarios are:

1. Positive gear search within known capability.
2. Negative search where requested diameter exceeds known maximum.
3. Surface finish requested but unknown in v1 data.
4. ISO9001 certification match.
5. Lead-time request within/outside normal 8–12 week range.
6. Material-grade search for `18CrNiMo7-6`, `16MnCr5`, or `20MnCr5`.

---

## 13. Definition of done for v1

The v1 basic scenario is complete when this end-to-end flow works:

```text
User selects gear manufacturing requirements in marketplace form
→ Marketplace sends SearchRequest JSON
→ MDC validates and normalizes request
→ MDC queries ontology-backed TSW catalogue
→ MDC returns matching provider offering
→ Response explains matched, unmatched, and unknown fields
```

The response must include:

- provider information
- offering information
- match status
- match score
- matched attributes
- unknown attributes
- unmatched attributes if any
- evidence values

---

## 14. Review checklist

Before implementation continues, review and confirm:

- [x] `ProviderOffering` is the correct result entity.
- [x] TSW starts with one primary offering.
- [x] Route fields are excluded from v1.
- [x] Unknown fields should be kept and reported.
- [x] Delivery and material grades should use provider-confirmed questionnaire data.
- [x] Surface finish should be supported in schema but unknown unless confirmed.
- [x] Query generation should remain template-based only.
- [x] Data provenance should be required for all capability values.
- [x] Natural-language parsing remains out of scope for v1.
