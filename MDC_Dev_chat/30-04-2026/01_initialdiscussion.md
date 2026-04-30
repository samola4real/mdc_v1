
## TOC
- [The most important design decision](#the-most-important-design-decision)
    - [Pipeline](#pipeline)
  - [What the basic scenario should include](#what-the-basic-scenario-should-include)
  - [What to lock now](#what-to-lock-now)
- [Directory structure to lock](#directory-structure-to-lock)


---


# The most important design decision
### Pipeline
Marketplace form input → canonical SearchRequest → deterministic query builder → whitelisted SPARQL templates → provider/offering matches

## What the basic scenario should include

For the first version, I would define the basic scenario as a structured search and filtering service over a curated provider capability graph.

The user fills form fields such as:
- service type
- part family
- material
- process
- diameter / length / envelope
- weight
- tolerance / quality class
- batch size
- delivery target
- certification / traceability need

**The backend maps these to canonical ontology predicates and executes SPARQL against the catalogue.**

*The result returned to the marketplace should be:*

- matched provider
- matched offering or capability profile
- matched attributes and values
- unmatched / unknown constraints
- evidence fields used for the match

## What to lock now
**A. Scope boundary for v1**

Lock these as in scope:

- one provider pilot: Tasowheel
- structured request input only
- deterministic SPARQL generation
- manual/curated seed data
- exact + range-based filtering
- provider/offering match explanation
- JSON API for marketplace integration

Lock these as** out of scope **for the 3-week basic scenario:

- free-text/NL request parsing
- LLM-based extraction
- automatic recommendation/ranking beyond simple rule-based sorting
- dynamic operational updates from live ERP/MES
- pricing engine
- smart reasoning over disruptions
- full multi-provider supply-chain planning

---
# Directory structure to lock

mdc-catalog/
├── backend/
│   ├── manage.py
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   └── test.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── api/
│   │   │   └── v1/
│   │   ├── catalog/
│   │   ├── ontology/
│   │   ├── providers/
│   │   └── search/
│   └── tests/
│
├── ontologies/
│   ├── mdc_core.ttl
│   ├── mdc_tasowheel_profile.ttl
│   ├── mdc_mappings.ttl
│   └── shacl/
│       └── mdc_v1_shapes.ttl
│
├── data/
│   ├── raw/
│   │   └── tasowheel/
│   ├── curated/
│   │   └── tasowheel_offerings.yaml
│   └── generated/
│       └── tasowheel_catalog.ttl
│
├── scripts/
│   ├── build_catalog.py
│   ├── validate_graph.py
│   └── load_fuseki.py
│
├── docs/
│   ├── architecture.md
│   ├── ontology-profile-v1.md
│   ├── api-contract-v1.md
│   ├── seed-data-template.md
│   ├── query-mapping-matrix.md
│   └── pilot-assumptions.md
│
├── docker/
│   ├── django/
│   └── fuseki/
│
├── docker-compose.yml
├── .env.example
├── pyproject.toml
└── README.md

---
