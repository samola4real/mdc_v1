# MaaS Dynamic Catalogue — Pilot Assumptions v1

**Status:** Week 1 finalized draft  
**Project:** MaaSAI MaaS Dynamic Catalogue  
**Scenario:** Basic structured-search scenario  
**Pilot:** Tasowheel / TSW gear and shaft manufacturing  
**Applies to:** `data/curated/tasowheel_offerings.yaml`, `ontologies/mdc_tasowheel_profile.ttl`, `/api/v1/catalog/search`

---

## 1. Purpose

This document records the assumptions used to represent the Tasowheel / TSW pilot in the MaaS Dynamic Catalogue v1.

The purpose of v1 is to support **structured marketplace search** for provider offerings. It is not intended to model full process routing, scheduling, pricing, or quotation-level manufacturability.

---

## 2. Source documents

The v1 pilot data is based on the following project sources:

| Source | Use in v1 |
|---|---|
| `Questionnaire for MaaS Providers.docx` | Provider-confirmed offering-level capability data |
| `MaaSAI - Machine list - TSW (ID 199622).xlsx` | Supporting machine/process capability context |
| `architecture.md` | Agreed architecture baseline |
| `ontology-profile-v1.md` | Agreed ontology application profile |
| `api-contract-v1.md` | Agreed API contract |

Provider-confirmed questionnaire values should take priority over public-web or inferred values.

---

## 3. Scope decision for this version

### 3.1 In scope

For this version, the TSW pilot will be represented as:

- one MaaS Provider: `tasowheel`
- one primary searchable ProviderOffering: `tasowheel_gears_shafts_precision`
- offering-level capability values for:
  - part families
  - materials and material grades
  - processes
  - diameter range
  - weight limit
  - gear module range
  - diametral pitch range
  - batch size range
  - quality class
  - normal lead time
  - certifications

### 3.2 Explicitly out of scope

The following are **not modelled as queryable fields in v1**:

- manufacturing route steps
- operation sequencing
- route alternatives
- machine-to-route assignment
- scheduling or capacity planning
- pricing or quotation calculation
- real-time machine availability
- subcontractor selection

The Excel routing sheet and the questionnaire route description may be retained as background information, but **route fields must not be exposed in the v1 API or used in v1 matching**.

---

## 4. Provider profile assumption

| Field | v1 value |
|---|---|
| Provider ID | `tasowheel` |
| Display name | `Tasowheel Oy` |
| Provider type | `MaaSProvider` |
| Country | Finland |
| Data status | `provider_confirmed_seed_v1` |
| Primary offering | `tasowheel_gears_shafts_precision` |

---

## 5. Primary offering assumption

| Field | v1 value |
|---|---|
| Offering ID | `tasowheel_gears_shafts_precision` |
| Offering name | High-quality gears and shafts |
| Service type | `gear_manufacturing` |
| Ontology service concept | `mdc:GearTransmissionService` |
| Search result entity | `ProviderOffering` |
| First-demo priority | Required |

---

## 6. Confirmed TSW capability values

The following values are treated as provider-confirmed for v1 because they are stated in the provider questionnaire.

| Capability | v1 value | Search use |
|---|---|---|
| Part families | gears, shafts | part-family matching |
| Batch size | 100–2000 pcs | range filtering / scoring |
| Module range | 0.3–10 | gear-parameter filtering |
| Diametral pitch range | raw: DP 85–2.5 | optional gear-parameter filtering |
| Diameter range | 10–450 mm | hard range filtering |
| Quality | up to DIN4 | gear quality filtering |
| Weight | up to approx. 200 kg | weight filtering |
| Lead time | normal 8–12 weeks, case-dependent | soft/conditional delivery matching |
| Materials | 18CrNiMo7-6, 16MnCr5, 20MnCr5, other alloyed carburizing steels | material/material-grade matching |
| Certifications | ISO 9001:2015, ISO 14001:2015, partial ISO/TS 16949, APQP | certification matching |

---

## 7. Material assumptions

### 7.1 Generic material family

TSW should be represented as supporting:

- `steel`
- `alloyed_carburizing_steel`

### 7.2 Confirmed material grades

The following material grades should be represented explicitly:

| Grade | v1 material family |
|---|---|
| `18CrNiMo7-6` | alloyed carburizing steel |
| `16MnCr5` | alloyed carburizing steel |
| `20MnCr5` | alloyed carburizing steel |

Other commonly used alloyed carburizing steels may be noted, but should not be treated as an exhaustive list.

### 7.3 Materials not confirmed

The following should remain supported in the API schema only, but **not asserted for TSW unless confirmed**:

- aluminum
- titanium
- nickel alloy
- stainless steel
- composites
- polymers

---

## 8. Process assumptions

The questionnaire and machine list support representing TSW with the following process capabilities:

| v1 process value | Ontology concept | Note |
|---|---|---|
| `machining` | `mdc:MachiningService` / generic process grouping | broad process capability |
| `turning` | `mdc:Turning` | inferred from turn-mill / hard turning context |
| `milling` | `mdc:Milling` | broad machining capability |
| `hobbing` | `mdc:Hobbing` | gear cutting capability |
| `gear_shaping` | `mdc:GearShaping` | gear cutting capability |
| `hard_turning` | `mdc:HardTurning` | hard machining capability |
| `grinding` | `mdc:Grinding` | grinding capability |
| `gear_grinding` | `mdc:GearGrinding` | tooth grinding / gear grinding capability |
| `heat_treatment` | `mdc:HeatTreatment` | subcontracted; do not treat as in-house without confirmation |
| `inspection` | `mdc:InspectionProcess` | quality checking capability |

Process capabilities are represented as capability support only. They are **not route steps** in v1.

---

## 9. Quality, tolerance, and surface assumptions

| Field | v1 decision |
|---|---|
| Gear quality | Store `DIN`, class `4`, with rule: lower/equal class number is higher or equal quality |
| General ± tolerance in mm | Unknown; do not infer from DIN class |
| Surface finish / Ra | Unknown; keep in API schema but return as unknown if requested |
| Traceability | Not confirmed beyond quality/certification statements |
| Aerospace traceability | Not confirmed; keep as unknown unless TSW confirms |

---

## 10. Lead-time assumption

The normal delivery time is represented as:

```yaml
lead_time_weeks:
  min: 8
  max: 12
  qualifier: normal_case_dependent
```

Matching policy:

| User delivery request | v1 behavior |
|---|---|
| `delivery.max_weeks >= 12` | matched |
| `8 <= delivery.max_weeks < 12` | partial/conditional match |
| `delivery.max_weeks < 8` | unmatched or requires confirmation |
| no delivery requested | ignore delivery criterion |

Because TSW states lead time depends on the case, delivery should not be used as the only hard rejection criterion unless explicitly configured.

---

## 11. Machine-list use in v1

The machine list should be used to support and validate process capability modelling. It should **not** override offering-level limits from the questionnaire.

| Excel data | v1 use |
|---|---|
| Machine groups | Support process vocabulary and future asset modelling |
| Machine types | Support process-to-machine interpretation |
| Machine maxima | Store only if/when machine-level RDF is added; do not use as offering maximum in first demo |
| Control system | Out of API scope for v1 |
| Automation | Out of API scope for v1 |
| Route sheet | Out of query/API scope for v1 |

Important rule: **offering-level search limits must come from provider-confirmed offering data, not from individual machine maxima.**

---

## 12. Open questions for TSW

These are not blockers for v1, but should be clarified for later versions.

- What surface roughness / Ra values can TSW provide?
- What general dimensional tolerances, if any, should be exposed in the catalogue?
- Which material grades beyond the three listed can be safely advertised?
- Which industry sectors should be exposed in the marketplace filter?
- Is aerospace-grade traceability supported?
- Should heat treatment be represented as subcontracted capability in search results?
- Can machine-level maxima be shared publicly, or should they remain internal/contextual?

---

## 13. Week 1 decision summary

| Decision | Status |
|---|---|
| Result entity is `ProviderOffering` | confirmed |
| Use one primary TSW offering for first demo | confirmed |
| Route fields excluded from v1 | confirmed |
| Use provider-confirmed questionnaire values for seed data | confirmed |
| Keep surface finish as unknown | confirmed |
| Add material-grade support | required |
| Add lead-time range from questionnaire | required |
| Keep deterministic SPARQL template strategy | confirmed |
