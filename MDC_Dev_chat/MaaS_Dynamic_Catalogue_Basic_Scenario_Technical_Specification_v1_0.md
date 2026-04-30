# MaaS Dynamic Catalogue — Basic Scenario Technical Specification v1.0

## 1. Purpose
- [MaaS Dynamic Catalogue — Basic Scenario Technical Specification v1.0](#maas-dynamic-catalogue--basic-scenario-technical-specification-v10)
  - [1. Purpose](#1-purpose)
  - [2. Frozen v1 scope](#2-frozen-v1-scope)
    - [2.1 In scope](#21-in-scope)
    - [2.2 Out of scope for v1](#22-out-of-scope-for-v1)
  - [3. Core v1 architecture](#3-core-v1-architecture)
  - [4. Frozen repository structure](#4-frozen-repository-structure)
  - [5. Frozen technology stack](#5-frozen-technology-stack)
  - [6. Frozen v1 ontology profile](#6-frozen-v1-ontology-profile)
    - [6.1 Namespace decision](#61-namespace-decision)
    - [6.2 Naming corrections to apply before implementation](#62-naming-corrections-to-apply-before-implementation)
    - [6.3 Core classes for v1](#63-core-classes-for-v1)
      - [Actor classes](#actor-classes)
      - [Offering classes](#offering-classes)
      - [Capability classes](#capability-classes)
      - [Process classes](#process-classes)
      - [Material classes](#material-classes)
      - [Request / requirement classes](#request--requirement-classes)
      - [Business and quality classes](#business-and-quality-classes)
  - [7. Frozen object properties](#7-frozen-object-properties)
  - [8. Frozen data properties](#8-frozen-data-properties)
  - [9. Frozen controlled vocabularies](#9-frozen-controlled-vocabularies)
    - [9.1 Service type vocabulary](#91-service-type-vocabulary)
    - [9.2 Part family vocabulary](#92-part-family-vocabulary)
    - [9.3 Process vocabulary](#93-process-vocabulary)
    - [9.4 Certification vocabulary](#94-certification-vocabulary)
  - [10. Frozen Tasowheel v1 provider/offering model](#10-frozen-tasowheel-v1-provideroffering-model)
    - [10.1 Provider record](#101-provider-record)
    - [10.2 Offering records](#102-offering-records)
  - [11. Frozen seed-data template](#11-frozen-seed-data-template)
  - [12. Frozen API contract v1](#12-frozen-api-contract-v1)
    - [12.1 Endpoint list](#121-endpoint-list)
    - [12.2 `POST /api/v1/catalog/search`](#122-post-apiv1catalogsearch)
      - [Request schema](#request-schema)
    - [12.3 Required request fields](#123-required-request-fields)
    - [12.4 Search response schema](#124-search-response-schema)
  - [13. Frozen matching policy](#13-frozen-matching-policy)
    - [13.1 Result statuses](#131-result-statuses)
    - [13.2 Hard filters for v1](#132-hard-filters-for-v1)
    - [13.3 Soft filters for v1](#133-soft-filters-for-v1)
    - [13.4 Unknown policy](#134-unknown-policy)
  - [14. Frozen scoring model v1](#14-frozen-scoring-model-v1)
  - [15. Frozen field-to-ontology mapping matrix](#15-frozen-field-to-ontology-mapping-matrix)
  - [16. Frozen SPARQL strategy](#16-frozen-sparql-strategy)
  - [17. Frozen validation rules](#17-frozen-validation-rules)
    - [17.1 API validation](#171-api-validation)
    - [17.2 Ontology data validation](#172-ontology-data-validation)
  - [18. Frozen acceptance tests](#18-frozen-acceptance-tests)
    - [18.1 Positive test: gear within known capability](#181-positive-test-gear-within-known-capability)
    - [18.2 Negative test: diameter too large](#182-negative-test-diameter-too-large)
    - [18.3 Unknown test: surface finish requested](#183-unknown-test-surface-finish-requested)
    - [18.4 Certification test](#184-certification-test)
    - [18.5 Unsupported certification test](#185-unsupported-certification-test)
  - [19. Week-by-week development backlog](#19-week-by-week-development-backlog)
    - [Week 1 — Freeze model, data, and contracts](#week-1--freeze-model-data-and-contracts)
      - [Goal](#goal)
      - [Tasks](#tasks)
      - [Week 1 exit criteria](#week-1-exit-criteria)
    - [Week 2 — Build catalogue backbone](#week-2--build-catalogue-backbone)
      - [Goal](#goal-1)
      - [Tasks](#tasks-1)
      - [Week 2 exit criteria](#week-2-exit-criteria)
    - [Week 3 — Integrate API and demo scenario](#week-3--integrate-api-and-demo-scenario)
      - [Goal](#goal-2)
      - [Tasks](#tasks-2)
      - [Week 3 exit criteria](#week-3-exit-criteria)
  - [20. Definition of done for v1](#20-definition-of-done-for-v1)
  - [21. Open decisions to confirm before coding](#21-open-decisions-to-confirm-before-coding)
  - [22. Recommended immediate next step](#22-recommended-immediate-next-step)

The purpose of this v1 implementation is to build a first operational version of the **MaaS Dynamic Catalogue (MDC)** that allows the **Cloud MaaS Marketplace** to send a structured manufacturing request and receive a list of suitable MaaS Provider offerings.

For v1, the catalogue will focus on the **Tasowheel pilot**, specifically gear and shaft manufacturing. Tasowheel publicly describes expertise in ground external and internal spur and helical gears and shafts, small and medium volumes, gears typically between module 0.3–10 or DP 85–2.5, gears up to 450 mm in diameter, shafts up to 500 mm in length, and quality demands up to DIN4.  
Source: <https://www.tasowheel.fi/products-and-services/gears-and-transmission-solutions/gears-and-shafts/>

The uploaded MDC ontology already contains the necessary high-level conceptual areas: actors/stakeholders, manufacturing services, capabilities, assets, processes, materials, product requirements, business terms, quality descriptors, operational states, compliance artefacts, locations, time entities, and semantic mapping artefacts.

---

## 2. Frozen v1 scope

### 2.1 In scope

| Area | v1 decision |
|---|---|
| Pilot | Tasowheel only |
| Scenario | Basic structured-search scenario |
| Input mode | Marketplace form fields, checkboxes, dropdowns |
| Search target | Provider offerings, not only provider records |
| Knowledge source | Curated seed data + ontology profile |
| Query mechanism | Deterministic SPARQL templates |
| Backend | Python + Django + Django REST Framework |
| Ontology store | RDF/OWL in Turtle + Apache Jena Fuseki |
| Result type | Matched provider offerings with evidence and unknowns |
| Matching style | Hard filters + simple score + explanation |
| Data update mode | Manual/curated seed data for v1 |

### 2.2 Out of scope for v1

| Out of scope item | Reason |
|---|---|
| Natural-language request parsing | Reserved for advanced scenario |
| LLM-based extraction | Reserved for advanced scenario |
| Live ERP/MES integration | Too large for 3-week v1 |
| Real-time capacity planning | Requires provider system integration |
| Pricing engine | Insufficient data |
| Contract negotiation | Handled later by agents/smart contracts |
| Full disruption recommendation | Later reasoning/recommendation phase |
| Multi-provider process-chain planning | Later Consumer Planner integration |

---

## 3. Core v1 architecture

The basic scenario shall follow this fixed pipeline:

```text
Marketplace UI
→ Structured SearchRequest JSON
→ Django REST API
→ Request validation and normalization
→ Field-to-ontology mapping
→ Deterministic SPARQL template generation
→ Fuseki SPARQL query
→ Result normalization
→ Match scoring and explanation
→ Marketplace response JSON
```

The important architectural rule is:

**Both the basic scenario and the future advanced natural-language scenario must produce the same canonical SearchRequest object.**

The advanced scenario may later add:

```text
Natural language request
→ NLP/LLM extraction
→ Canonical SearchRequest
→ Same v1 search pipeline
```

So the search engine must not depend on the UI. It depends only on the canonical SearchRequest.

---

## 4. Frozen repository structure

```text
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
```

---

## 5. Frozen technology stack

| Layer | Decision |
|---|---|
| Language | Python 3.11 |
| Backend framework | Django 5.x |
| API framework | Django REST Framework |
| API documentation | drf-spectacular / OpenAPI |
| RDF processing | rdflib |
| SPARQL client | SPARQLWrapper or HTTP client |
| Triple store | Apache Jena Fuseki |
| Ontology format | Turtle `.ttl` |
| Ontology editing | Protégé |
| Validation | pySHACL |
| Test framework | pytest + pytest-django |
| Formatting/linting | black + ruff |
| Local deployment | Docker Compose |
| Configuration | `.env` + python-dotenv |

---

## 6. Frozen v1 ontology profile

The uploaded ontology is broader than needed for v1. The implementation shall use a smaller **MDC Tasowheel Application Profile v1** derived from it.

### 6.1 Namespace decision

Use one base namespace for the prototype:

```text
https://maasai-project.eu/ontology/mdc#
```

Recommended prefix:

```text
mdc:
```

### 6.2 Naming corrections to apply before implementation

| Current issue | Frozen v1 correction |
|---|---|
| `ManufacturingSevice` | `ManufacturingService` |
| `SubstractiveProcess` | `SubtractiveProcess` or preferably `MaterialRemovalProcess` |
| Duplicate `ProcessCapability` | Keep one `ProcessCapability` |
| `Gear&TransmissionService` | Use URI-safe `GearTransmissionService`; keep label “Gear & Transmission Service” |
| Mixing “Stakeholder” and “Actor” | Use `Actor` as canonical class, allow `Stakeholder` as label/comment if needed |
| Broad ontology vs implementation | Use application profile for v1, not full ontology |

### 6.3 Core classes for v1

#### Actor classes

| Class | Purpose |
|---|---|
| `mdc:Actor` | Generic participant |
| `mdc:MaaSProvider` | Provider offering manufacturing capability |
| `mdc:MaaSConsumer` | Consumer requesting manufacturing service |

#### Offering classes

| Class | Purpose |
|---|---|
| `mdc:ProviderOffering` | Searchable commercial/technical offering |
| `mdc:ManufacturingService` | Generic manufacturing service |
| `mdc:MachiningService` | Machining-related service |
| `mdc:GearTransmissionService` | Gear/transmission-specific service |
| `mdc:HeatTreatmentService` | Heat treatment / hardening-related service |
| `mdc:FinishingService` | Finishing-related service |
| `mdc:InspectionService` | Inspection/metrology-related service |

#### Capability classes

| Class | Purpose |
|---|---|
| `mdc:ManufacturingCapability` | Generic capability |
| `mdc:ProcessCapability` | Supported manufacturing process |
| `mdc:MaterialCapability` | Supported material/material family |
| `mdc:PrecisionCapability` | Tolerance / quality capability |
| `mdc:DimensionalCapability` | Size envelope / diameter / length |
| `mdc:BatchCapability` | Supported production volume |
| `mdc:SurfaceFinishCapability` | Surface quality / Ra support |
| `mdc:InspectionCapability` | Metrology / quality inspection support |
| `mdc:CertificationBackedCapability` | Capability backed by certification |

#### Process classes

| Class | Purpose |
|---|---|
| `mdc:Process` | Generic process |
| `mdc:MaterialRemovalProcess` | Parent for subtractive operations |
| `mdc:Turning` | Turning |
| `mdc:Milling` | Milling |
| `mdc:Drilling` | Drilling |
| `mdc:Grinding` | Grinding |
| `mdc:GearGrinding` | Gear grinding |
| `mdc:Hobbing` | Gear hobbing |
| `mdc:GearShaping` | Gear shaping |
| `mdc:HardTurning` | Hard turning |
| `mdc:HeatTreatment` | Heat treatment / hardening |
| `mdc:InspectionProcess` | Inspection/metrology process |

Tasowheel publicly mentions gear grinding expertise and use of Reishauer and Liebherr machines, including a Liebherr LGG 280 investment.  
Source: <https://www.tasowheel.fi/products-and-services/gears-and-transmission-solutions/gears-and-shafts/>

#### Material classes

| Class | Purpose |
|---|---|
| `mdc:Material` | Generic material |
| `mdc:Metal` | Parent for metals |
| `mdc:Steel` | Steel |
| `mdc:StainlessSteel` | Stainless steel |
| `mdc:Aluminum` | Aluminum |
| `mdc:Titanium` | Titanium |
| `mdc:NickelAlloy` | Nickel alloy |

For v1, material support should be treated as **curated catalogue data** unless directly confirmed from Tasowheel data.

#### Request / requirement classes

| Class | Purpose |
|---|---|
| `mdc:ConsumerRequest` | Marketplace user request |
| `mdc:MaterialRequirement` | Required material/material family |
| `mdc:ProcessRequirement` | Required process |
| `mdc:DimensionRequirement` | Required size/envelope |
| `mdc:ToleranceRequirement` | Required tolerance / quality |
| `mdc:SurfaceRequirement` | Required surface finish |
| `mdc:WeightRequirement` | Required part weight |
| `mdc:BatchSizeRequirement` | Required batch size |
| `mdc:DeliveryRequirement` | Required delivery time |
| `mdc:CertificationRequirement` | Required certification |
| `mdc:TraceabilityRequirement` | Required traceability |

#### Business and quality classes

| Class | Purpose |
|---|---|
| `mdc:LeadTimeDescriptor` | Lead-time information |
| `mdc:AvailabilityDescriptor` | Availability status |
| `mdc:QualityDescriptor` | Generic quality descriptor |
| `mdc:PrecisionLevel` | Precision/quality class |
| `mdc:SurfaceFinishDescriptor` | Surface finish descriptor |
| `mdc:Certification` | Certification artefact |
| `mdc:TraceabilityRecord` | Traceability information |
| `mdc:FacilityLocation` | Provider/facility location |

Tasowheel states that its processes are operated according to ISO 9001:2015 and ISO 14001:2015.  
Source: <https://www.tasowheel.fi/company/our-quality/>

---

## 7. Frozen object properties

| Property | Domain | Range | Purpose |
|---|---|---|---|
| `mdc:hasOffering` | `MaaSProvider` | `ProviderOffering` | Provider owns/offers offering |
| `mdc:offeredBy` | `ProviderOffering` | `MaaSProvider` | Reverse relation |
| `mdc:hasServiceType` | `ProviderOffering` | `ManufacturingService` | Classifies offering |
| `mdc:hasCapability` | `ProviderOffering` | `ManufacturingCapability` | Links offering to capability |
| `mdc:supportsProcess` | `ProviderOffering` | `Process` | Process supported by offering |
| `mdc:supportsMaterial` | `ProviderOffering` | `Material` | Material supported by offering |
| `mdc:hasCertification` | `MaaSProvider` or `ProviderOffering` | `Certification` | Certification evidence |
| `mdc:hasLocation` | `MaaSProvider` | `FacilityLocation` | Provider/facility location |
| `mdc:supportsIndustry` | `ProviderOffering` | `IndustrySector` | Supported industry |
| `mdc:hasQualityStandard` | `ProviderOffering` | `QualityStandard` | DIN/ISO/etc. quality standard |
| `mdc:hasAvailabilityStatus` | `ProviderOffering` | `AvailabilityDescriptor` | Availability status |

---

## 8. Frozen data properties

| Property | Type | Unit / format | Purpose |
|---|---|---|---|
| `mdc:providerId` | string | stable slug | Provider ID |
| `mdc:offeringId` | string | stable slug | Offering ID |
| `mdc:legalName` | string | text | Provider legal name |
| `mdc:displayName` | string | text | UI name |
| `mdc:description` | string | text | Human-readable description |
| `mdc:diameterMinMm` | decimal | mm | Minimum diameter |
| `mdc:diameterMaxMm` | decimal | mm | Maximum diameter |
| `mdc:lengthMaxMm` | decimal | mm | Maximum shaft/part length |
| `mdc:weightMaxKg` | decimal | kg | Maximum part weight |
| `mdc:moduleMin` | decimal | module | Minimum gear module |
| `mdc:moduleMax` | decimal | module | Maximum gear module |
| `mdc:dpMin` | decimal | diametral pitch | Optional DP lower bound |
| `mdc:dpMax` | decimal | diametral pitch | Optional DP upper bound |
| `mdc:qualityClassMax` | decimal/string | standard-specific | Best achievable quality class |
| `mdc:toleranceMinMm` | decimal | mm | Best/lowest tolerance if known |
| `mdc:surfaceRaMinUm` | decimal | µm | Best surface finish if known |
| `mdc:batchMin` | integer | pieces | Minimum batch |
| `mdc:batchMax` | integer | pieces | Maximum batch |
| `mdc:leadTimeMinWeeks` | decimal | weeks | Minimum lead-time |
| `mdc:leadTimeMaxWeeks` | decimal | weeks | Maximum lead-time |
| `mdc:dataConfidence` | string | enum | declared / inferred / estimated / unknown |
| `mdc:sourceType` | string | enum | public_web / proposal / curated / provider_confirmed |
| `mdc:sourceNote` | string | text | Evidence note |

---

## 9. Frozen controlled vocabularies

### 9.1 Service type vocabulary

| UI value | Ontology concept |
|---|---|
| `gear_manufacturing` | `mdc:GearTransmissionService` |
| `shaft_manufacturing` | `mdc:GearTransmissionService` |
| `machining` | `mdc:MachiningService` |
| `heat_treatment` | `mdc:HeatTreatmentService` |
| `inspection` | `mdc:InspectionService` |
| `finishing` | `mdc:FinishingService` |

### 9.2 Part family vocabulary

| UI value | Ontology concept / tag |
|---|---|
| `spur_gear` | `mdc:SpurGear` |
| `helical_gear` | `mdc:HelicalGear` |
| `internal_gear` | `mdc:InternalGear` |
| `external_gear` | `mdc:ExternalGear` |
| `shaft` | `mdc:Shaft` |
| `gear_shaft` | `mdc:GearShaft` |
| `transmission_component` | `mdc:TransmissionComponent` |

Tasowheel explicitly describes external and internal spur and helical gears and shafts.  
Source: <https://www.tasowheel.fi/products-and-services/gears-and-transmission-solutions/gears-and-shafts/>

### 9.3 Process vocabulary

| UI value | Ontology concept |
|---|---|
| `turning` | `mdc:Turning` |
| `milling` | `mdc:Milling` |
| `hobbing` | `mdc:Hobbing` |
| `gear_shaping` | `mdc:GearShaping` |
| `hard_turning` | `mdc:HardTurning` |
| `grinding` | `mdc:Grinding` |
| `gear_grinding` | `mdc:GearGrinding` |
| `heat_treatment` | `mdc:HeatTreatment` |
| `inspection` | `mdc:InspectionProcess` |

### 9.4 Certification vocabulary

| UI value | Ontology concept |
|---|---|
| `ISO9001_2015` | `mdc:ISO9001_2015` |
| `ISO14001_2015` | `mdc:ISO14001_2015` |
| `aerospace_traceability` | `mdc:AerospaceTraceability` |
| `full_traceability` | `mdc:FullTraceability` |

For v1, `ISO9001_2015` and `ISO14001_2015` can be populated from public Tasowheel information. Other traceability concepts should be allowed in the request model but treated as `unknown` unless confirmed.  
Source: <https://www.tasowheel.fi/company/our-quality/>

---

## 10. Frozen Tasowheel v1 provider/offering model

### 10.1 Provider record

| Field | Value |
|---|---|
| `provider_id` | `tasowheel` |
| `display_name` | `Tasowheel Oy` |
| `provider_type` | `MaaSProvider` |
| `country` | Finland |
| `known_certifications` | ISO 9001:2015, ISO 14001:2015 |
| `source_type` | public_web + proposal_context + curated |
| `data_status` | seed_v1 |

Tasowheel’s public site identifies its Tampere factories, Tikkakoski factory, and Espoo R&D center, and describes products/services across gears and transmission solutions, machining, motion solutions, R&D, and assembly.  
Source: <https://www.tasowheel.fi/video/tasowheel-our-core-values/>

### 10.2 Offering records

For v1, Tasowheel should be decomposed into several offerings.

| Offering ID | Offering name | Purpose |
|---|---|---|
| `tasowheel_gears_shafts_precision` | High-quality gears and shafts | Main gear/shaft offering |
| `tasowheel_gear_grinding` | Gear grinding capability | Precision finishing/quality capability |
| `tasowheel_transmission_components` | Transmission components | Broader gear/transmission component offering |
| `tasowheel_machining_complex_components` | Complex machined components | Optional broader machining offering |
| `tasowheel_heat_treatment_supported` | Heat treatment supported workflow | External/partner-supported treatment stage, if retained from proposal context |

Only the first three should be used in the first demo unless you have confirmed data for the others.

---

## 11. Frozen seed-data template

This is the **data shape**, not implementation code.

```yaml
providers:
  - provider_id: tasowheel
    legal_name: Tasowheel Oy
    display_name: Tasowheel
    provider_type: MaaSProvider
    country: Finland
    facilities:
      - facility_id: tasowheel_tampere
        city: Tampere
        role: gears_manufacturing
      - facility_id: tasowheel_tikkakoski
        city: Tikkakoski
        role: other_components
    certifications:
      - code: ISO9001_2015
        source_type: public_web
        confidence: declared
      - code: ISO14001_2015
        source_type: public_web
        confidence: declared

offerings:
  - offering_id: tasowheel_gears_shafts_precision
    provider_id: tasowheel
    service_type: gear_manufacturing
    part_families:
      - external_gear
      - internal_gear
      - spur_gear
      - helical_gear
      - shaft
    processes:
      - turning
      - milling
      - hobbing
      - gear_shaping
      - grinding
      - gear_grinding
    capabilities:
      diameter_mm:
        min: null
        max: 450
        confidence: declared
        source_type: public_web
      shaft_length_mm:
        max: 500
        confidence: declared
        source_type: public_web
      module:
        min: 0.3
        max: 10
        confidence: declared
        source_type: public_web
      quality:
        standard: DIN
        max_class: 4
        confidence: declared
        source_type: public_web
      batch:
        category: small_medium
        min: null
        max: null
        confidence: declared
        source_type: public_web
      lead_time_weeks:
        min: null
        max: null
        confidence: unknown
        source_type: not_confirmed
      surface_finish_ra_um:
        min: null
        confidence: unknown
        source_type: not_confirmed
    supported_materials:
      - material: steel
        confidence: curated
      - material: stainless_steel
        confidence: curated
    industries:
      - powertrain
      - engines_combustion_systems
      - machine_building
    notes:
      - Public source confirms high-quality gears and shafts up to 450 mm diameter, shafts up to 500 mm, module 0.3-10, and quality up to DIN4.
```

Important: values such as titanium, aerospace-grade traceability, exact Ra 1.6, and four-week delivery should be supported in the **request schema**, but not marked as Tasowheel-supported unless confirmed.

---

## 12. Frozen API contract v1

### 12.1 Endpoint list

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/catalog/search` | Main structured catalogue search |
| `GET` | `/api/v1/catalog/filters` | Returns available UI filter values |
| `GET` | `/api/v1/providers/{provider_id}` | Provider detail |
| `GET` | `/api/v1/offerings/{offering_id}` | Offering detail |
| `GET` | `/api/v1/health` | Service health check |

---

### 12.2 `POST /api/v1/catalog/search`

#### Request schema

```json
{
  "service_type": "gear_manufacturing",
  "part_family": "spur_gear",
  "materials": ["steel"],
  "processes": ["gear_grinding"],
  "dimensions": {
    "diameter_mm": {
      "max": 300
    },
    "length_mm": {
      "max": 80
    },
    "width_mm": {
      "max": null
    },
    "height_mm": {
      "max": null
    }
  },
  "weight_kg": {
    "max": 20
  },
  "gear_parameters": {
    "module": {
      "min": 0.5,
      "max": 6
    },
    "quality": {
      "standard": "DIN",
      "max_class": 4
    }
  },
  "surface_finish": {
    "ra_um": {
      "max": 1.6
    }
  },
  "batch_size": 100,
  "delivery": {
    "max_weeks": 4
  },
  "certifications": ["ISO9001_2015"],
  "traceability_required": false,
  "industry": "powertrain",
  "match_policy": {
    "unknown_policy": "keep_as_unknown",
    "minimum_score": 0.5
  }
}
```

### 12.3 Required request fields

| Field | Required? | v1 rule |
|---|---|---|
| `service_type` | Yes | Must map to controlled vocabulary |
| `part_family` | No | Optional but recommended |
| `materials` | No | If absent, do not filter by material |
| `processes` | No | If absent, do not filter by process |
| `dimensions` | No | Range filters if present |
| `gear_parameters` | No | Range/quality filters if present |
| `batch_size` | No | Used as soft criterion unless numeric ranges exist |
| `delivery` | No | Keep unknown unless confirmed |
| `certifications` | No | Hard or soft depending on request |
| `traceability_required` | No | Unknown in v1 unless confirmed |
| `industry` | No | Soft matching field |

---

### 12.4 Search response schema

```json
{
  "request_id": "generated-request-id",
  "query_interpretation": {
    "service_type": {
      "input": "gear_manufacturing",
      "mapped_concept": "mdc:GearTransmissionService"
    },
    "materials": [
      {
        "input": "steel",
        "mapped_concept": "mdc:Steel"
      }
    ],
    "processes": [
      {
        "input": "gear_grinding",
        "mapped_concept": "mdc:GearGrinding"
      }
    ]
  },
  "result_count": 1,
  "results": [
    {
      "provider": {
        "provider_id": "tasowheel",
        "display_name": "Tasowheel Oy",
        "country": "Finland"
      },
      "offering": {
        "offering_id": "tasowheel_gears_shafts_precision",
        "name": "High-quality gears and shafts",
        "service_type": "gear_manufacturing"
      },
      "match": {
        "status": "partial_match",
        "score": 0.78,
        "hard_filters_passed": true
      },
      "matched_attributes": [
        {
          "field": "service_type",
          "requested": "gear_manufacturing",
          "provided": "GearTransmissionService",
          "status": "matched",
          "confidence": "declared"
        },
        {
          "field": "diameter_mm.max",
          "requested": 300,
          "provided_max": 450,
          "status": "matched",
          "confidence": "declared"
        },
        {
          "field": "quality.max_class",
          "requested": "DIN4",
          "provided": "DIN4",
          "status": "matched",
          "confidence": "declared"
        }
      ],
      "unknown_attributes": [
        {
          "field": "surface_finish.ra_um",
          "requested": 1.6,
          "reason": "No confirmed surface roughness value in v1 seed data"
        },
        {
          "field": "delivery.max_weeks",
          "requested": 4,
          "reason": "No confirmed lead-time value in v1 seed data"
        }
      ],
      "unmatched_attributes": [],
      "evidence": [
        {
          "field": "diameter_mm.max",
          "value": 450,
          "source_type": "public_web",
          "confidence": "declared"
        },
        {
          "field": "quality",
          "value": "DIN4",
          "source_type": "public_web",
          "confidence": "declared"
        }
      ]
    }
  ]
}
```

---

## 13. Frozen matching policy

### 13.1 Result statuses

| Status | Meaning |
|---|---|
| `full_match` | All requested supported fields matched |
| `partial_match` | Hard filters passed, but some optional/unknown fields unresolved |
| `no_match` | One or more hard filters failed |
| `unknown` | Insufficient data to determine suitability |

### 13.2 Hard filters for v1

| Field | Rule |
|---|---|
| `service_type` | Must match |
| `part_family` | Must match if supplied and known |
| `diameter_mm.max` | Requested max must be ≤ provider max |
| `length_mm.max` | Requested max must be ≤ provider max, if known |
| `module.min/max` | Requested range must overlap provider range |
| `quality.max_class` | Requested class must be achievable if standard is known |
| `certifications` | Hard only for ISO9001/ISO14001; otherwise unknown |

### 13.3 Soft filters for v1

| Field | Rule |
|---|---|
| `materials` | Match if supported; unknown if not confirmed |
| `processes` | Match if declared/curated |
| `industry` | Improves score |
| `batch_size` | Soft unless numeric min/max exists |
| `delivery.max_weeks` | Unknown unless confirmed |
| `surface_finish.ra_um` | Unknown unless confirmed |
| `traceability_required` | Unknown unless confirmed |

### 13.4 Unknown policy

Default v1 policy:

```text
unknown_policy = keep_as_unknown
```

This means the catalogue should **not reject** Tasowheel only because a field is not yet known. Instead, the response must explicitly show that the attribute is unresolved.

---

## 14. Frozen scoring model v1

Use a simple transparent score.

| Criterion | Weight |
|---|---:|
| Service type match | 20 |
| Part family match | 15 |
| Dimension match | 15 |
| Gear module / gear parameter match | 10 |
| Quality class match | 10 |
| Process match | 10 |
| Material match | 8 |
| Certification match | 5 |
| Industry match | 4 |
| Batch match | 3 |

Total possible score: `100`.

Unknown fields receive `0` for that criterion, but do not automatically reject the result unless the field is configured as hard.

Final score:

```text
score = achieved_points / applicable_points
```

This avoids unfairly penalizing a provider when the user did not supply some fields.

---

## 15. Frozen field-to-ontology mapping matrix

| SearchRequest field | Ontology path | Filter type |
|---|---|---|
| `service_type` | `ProviderOffering → hasServiceType → ManufacturingService` | Hard |
| `part_family` | `ProviderOffering → supportsPartFamily → PartFamily` | Hard if supplied |
| `materials[]` | `ProviderOffering → supportsMaterial → Material` | Soft/unknown |
| `processes[]` | `ProviderOffering → supportsProcess → Process` | Soft |
| `dimensions.diameter_mm.max` | `ProviderOffering → diameterMaxMm` | Hard |
| `dimensions.length_mm.max` | `ProviderOffering → lengthMaxMm` | Hard if known |
| `gear_parameters.module.min/max` | `ProviderOffering → moduleMin/moduleMax` | Hard |
| `gear_parameters.quality` | `ProviderOffering → hasQualityStandard + qualityClassMax` | Hard if supplied |
| `surface_finish.ra_um.max` | `ProviderOffering → surfaceRaMinUm` | Soft/unknown |
| `batch_size` | `ProviderOffering → batchMin/batchMax` | Soft |
| `delivery.max_weeks` | `ProviderOffering → leadTimeMaxWeeks` | Soft/unknown |
| `certifications[]` | `Provider/MaaSProvider → hasCertification` | Hard for known standards |
| `traceability_required` | `ProviderOffering → supportsTraceability` | Soft/unknown |
| `industry` | `ProviderOffering → supportsIndustry` | Soft |

---

## 16. Frozen SPARQL strategy

No free-form SPARQL generation in v1.

Use named template groups:

| Template | Purpose |
|---|---|
| `service_type_filter` | Match offering by service type |
| `part_family_filter` | Match part family |
| `process_filter` | Match one or more supported processes |
| `material_filter` | Match one or more materials |
| `diameter_range_filter` | Requested diameter ≤ provider max |
| `length_range_filter` | Requested length ≤ provider max |
| `module_range_filter` | Requested module range overlaps provider range |
| `quality_filter` | Requested DIN class compatible with provider capability |
| `certification_filter` | Provider has requested certification |
| `industry_filter` | Offering supports requested industry |
| `evidence_projection` | Return provider/offering capability values |

The Django search layer should assemble templates only from validated request fields.

---

## 17. Frozen validation rules

### 17.1 API validation

| Rule |
|---|
| `service_type` must be in controlled vocabulary |
| all numeric values must be positive |
| `module.min <= module.max` |
| `diameter_mm.max > 0` if supplied |
| `batch_size` must be integer > 0 |
| `quality.standard` must be from allowed standards |
| unknown controlled vocabulary values return `400 Bad Request` |
| unsupported but syntactically valid fields return a warning, not failure, if configured |

### 17.2 Ontology data validation

Use SHACL to validate:

| Shape | Purpose |
|---|---|
| `ProviderShape` | provider has ID, name, type |
| `OfferingShape` | offering has ID, provider, service type |
| `CapabilityShape` | capability values use valid units |
| `DimensionShape` | max values are positive |
| `QualityShape` | quality standard/class is present together |
| `SourceShape` | each important value has source/confidence metadata |

---

## 18. Frozen acceptance tests

### 18.1 Positive test: gear within known capability

Request:
- service type: gear manufacturing
- part family: spur gear
- diameter max: 300 mm
- module: 1–5
- quality: DIN4

Expected:
- Tasowheel gear/shaft offering returned
- status: `full_match` or `partial_match`
- evidence includes diameter max 450 mm and DIN4

### 18.2 Negative test: diameter too large

Request:
- service type: gear manufacturing
- diameter max: 700 mm

Expected:
- no Tasowheel offering returned, or returned as `no_match`
- reason: requested diameter exceeds provider maximum of 450 mm

### 18.3 Unknown test: surface finish requested

Request:
- service type: gear manufacturing
- surface finish Ra 1.6

Expected:
- Tasowheel may still be returned
- surface finish appears under `unknown_attributes`
- result status: `partial_match`

### 18.4 Certification test

Request:
- service type: gear manufacturing
- certification: ISO9001_2015

Expected:
- Tasowheel returned
- certification matched

### 18.5 Unsupported certification test

Request:
- service type: gear manufacturing
- certification: aerospace_traceability

Expected:
- result not automatically rejected in default policy
- traceability/certification marked unknown unless confirmed

---

## 19. Week-by-week development backlog

### Week 1 — Freeze model, data, and contracts

#### Goal

Prepare everything needed for implementation before coding the core functionality.

#### Tasks

| ID | Task | Output |
|---|---|---|
| W1.1 | Confirm v1 scope and non-goals | `docs/architecture.md` |
| W1.2 | Clean ontology naming decisions | `docs/ontology-profile-v1.md` |
| W1.3 | Freeze v1 ontology profile | `ontologies/mdc_core.ttl` draft |
| W1.4 | Freeze Tasowheel offering decomposition | `docs/pilot-assumptions.md` |
| W1.5 | Freeze API request/response schema | `docs/api-contract-v1.md` |
| W1.6 | Freeze seed-data template | `docs/seed-data-template.md` |
| W1.7 | Freeze field-to-ontology mapping matrix | `docs/query-mapping-matrix.md` |
| W1.8 | Decide hard/soft/unknown matching policy | documented in API contract |
| W1.9 | Prepare initial curated Tasowheel seed file | `data/curated/tasowheel_offerings.yaml` |
| W1.10 | Define acceptance test cases | `backend/tests/specs/` or docs |

#### Week 1 exit criteria

- API contract approved
- ontology application profile approved
- seed-data template approved
- Tasowheel seed data has at least one valid offering
- matching policy approved

---

### Week 2 — Build catalogue backbone

#### Goal

Prepare ontology store, data transformation, validation, and SPARQL query structure.

#### Tasks

| ID | Task | Output |
|---|---|---|
| W2.1 | Set up Django project structure | backend skeleton |
| W2.2 | Set up Fuseki in Docker Compose | local SPARQL endpoint |
| W2.3 | Create initial Turtle ontology profile | `mdc_core.ttl` |
| W2.4 | Create Tasowheel profile graph | `mdc_tasowheel_profile.ttl` |
| W2.5 | Convert curated seed data to RDF | generated graph |
| W2.6 | Load RDF graph into Fuseki | working dataset |
| W2.7 | Create SHACL validation shapes | `mdc_v1_shapes.ttl` |
| W2.8 | Define SPARQL template registry | query templates documented |
| W2.9 | Test SPARQL templates manually | query result examples |
| W2.10 | Finalize filter vocabulary endpoint data | filter definitions |

#### Week 2 exit criteria

- Fuseki running locally
- ontology graph loaded
- Tasowheel offering queryable
- validation can catch incomplete seed data
- manual SPARQL search returns expected Tasowheel offering

---

### Week 3 — Integrate API and demo scenario

#### Goal

Complete basic end-to-end flow from structured request to catalogue response.

#### Tasks

| ID | Task | Output |
|---|---|---|
| W3.1 | Implement search API endpoint | `/api/v1/catalog/search` |
| W3.2 | Implement request validation | DRF serializer/schema |
| W3.3 | Implement canonical request normalization | internal SearchRequest |
| W3.4 | Implement SPARQL template assembly | deterministic query builder |
| W3.5 | Implement Fuseki query execution | search service |
| W3.6 | Implement result shaping | response schema |
| W3.7 | Implement match explanation | matched/unknown/unmatched attributes |
| W3.8 | Implement filters endpoint | `/api/v1/catalog/filters` |
| W3.9 | Add acceptance tests | test scenarios |
| W3.10 | Prepare demo documentation | demo script + known limitations |

#### Week 3 exit criteria

- Marketplace-style request accepted
- SPARQL query executed against Fuseki
- Tasowheel offering returned with evidence
- unknown fields clearly reported
- acceptance tests pass
- OpenAPI documentation generated
- known limitations documented

---

## 20. Definition of done for v1

The v1 basic scenario is complete when the following demo works:

```text
User selects gear manufacturing requirements in marketplace form
→ Marketplace sends SearchRequest JSON
→ MDC validates and normalizes request
→ MDC queries ontology-backed Tasowheel catalogue
→ MDC returns matching provider offering
→ Response explains matched, unmatched, and unknown fields
```

Minimum demo request:

```json
{
  "service_type": "gear_manufacturing",
  "part_family": "spur_gear",
  "materials": ["steel"],
  "processes": ["gear_grinding"],
  "dimensions": {
    "diameter_mm": {
      "max": 300
    }
  },
  "gear_parameters": {
    "module": {
      "min": 1,
      "max": 5
    },
    "quality": {
      "standard": "DIN",
      "max_class": 4
    }
  },
  "certifications": ["ISO9001_2015"],
  "industry": "powertrain"
}
```

Expected result:

```text
Tasowheel gear/shaft offering returned as match or partial_match,
with evidence for diameter, module, quality, and certification.
```

---

## 21. Open decisions to confirm before coding

These should be locked before starting the implementation chat:

| Decision | Recommended answer |
|---|---|
| Result entity | `ProviderOffering` |
| Number of Tasowheel offerings | Start with 1–3 |
| Unknown-field policy | Keep result and report unknown |
| Delivery field in v1 | Supported in schema, unknown unless curated/confirmed |
| Surface finish in v1 | Supported in schema, unknown unless confirmed |
| Titanium/aerospace example | Supported in schema, not asserted for Tasowheel unless confirmed |
| Ranking in v1 | Simple transparent score only |
| Query generation | Template-based only |
| Ontology scope | Application profile, not full ontology |
| Data provenance | Required for all capability values |

---

## 22. Recommended immediate next step

Before coding, prepare and approve these four documents:

1. `ontology-profile-v1.md`
2. `api-contract-v1.md`
3. `seed-data-template.md`
4. `query-mapping-matrix.md`

Once those are approved, the coding task can start cleanly in the next chat with minimal ambiguity.
