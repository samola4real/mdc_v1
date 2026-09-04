# MaaS Dynamic Catalogue — Query Mapping Matrix v1

**Status:** Week 1 finalized draft  
**Project:** MaaSAI MaaS Dynamic Catalogue  
**Scenario:** Basic structured-search scenario  
**Pilot:** Tasowheel / TSW gear and shaft manufacturing  
**Applies to:** `POST /api/v1/catalog/search`

---

## 1. Purpose

This document maps the marketplace `SearchRequest` fields to the ontology-backed catalogue model.

It defines:

- which request fields are supported in v1
- which ontology properties or seed-data fields they map to
- whether each field is hard, soft, or unknown-aware
- how the search result should explain matches and gaps

Route-related fields are intentionally excluded from v1.

---

## 2. Matching types

| Type | Meaning |
|---|---|
| `hard` | Known incompatibility can reject or produce `no_match` |
| `soft` | Used for scoring/explanation but should not reject alone |
| `unknown-aware` | If data is missing, return as `unknown_attributes` |
| `informational` | Returned as evidence/detail but not used for filtering |

---

## 3. Field-to-ontology mapping

| SearchRequest field | Seed-data field | Ontology path/property | Match type | v1 behavior |
|---|---|---|---|---|
| `service_type` | `offerings[].service_type` | `ProviderOffering -> hasServiceType -> ManufacturingService` | hard | Must match controlled service value |
| `part_family` | `offerings[].part_families[]` | `ProviderOffering -> supportsPartFamily -> PartFamily` | hard if supplied | Match if requested part family is listed |
| `materials[]` | `offerings[].supported_materials[]` | `ProviderOffering -> supportsMaterial -> Material` | unknown-aware | Match known supported materials; unknown if not confirmed |
| `material_grades[]` | `offerings[].supported_material_grades[]` | `ProviderOffering -> supportsMaterialGrade -> MaterialGrade` | unknown-aware | Match listed grades; unknown if unlisted but material family may still match |
| `processes[]` | `offerings[].processes[]` | `ProviderOffering -> supportsProcess -> Process` | soft | Improves score; matched process shown in explanation |
| `dimensions.diameter_mm.min` | `capabilities.diameter_mm.min` | `mdc:diameterMinMm` | hard | Requested minimum should not be below provider range if supplied |
| `dimensions.diameter_mm.max` | `capabilities.diameter_mm.max` | `mdc:diameterMaxMm` | hard | Requested max must be <= provider max |
| `weight_kg.max` | `capabilities.weight_kg.max` | `mdc:weightMaxKg` | hard/unknown-aware | Requested max must be <= provider max when known |
| `gear_parameters.module.min` | `capabilities.module.min` | `mdc:moduleMin` | hard | Requested module range must overlap supported range |
| `gear_parameters.module.max` | `capabilities.module.max` | `mdc:moduleMax` | hard | Requested module range must overlap supported range |
| `gear_parameters.diametral_pitch.min` | `capabilities.diametral_pitch.min` | `mdc:dpMin` | hard if supplied | Optional DP range search; use normalized ascending values |
| `gear_parameters.diametral_pitch.max` | `capabilities.diametral_pitch.max` | `mdc:dpMax` | hard if supplied | Optional DP range search; preserve raw DP note as evidence |
| `gear_parameters.quality.standard` | `capabilities.quality.standard` | `ProviderOffering -> hasQualityStandard -> QualityStandard` | hard if supplied | Match standard such as DIN |
| `gear_parameters.quality.max_class` | `capabilities.quality.best_class` | `mdc:qualityClassMax` / `mdc:qualityBestClass` | hard if supplied | For DIN, provider best class must be <= requested max class |
| `surface_finish.ra_um.max` | `capabilities.surface_finish_ra_um.max` | `mdc:surfaceRaMinUm` | unknown-aware | Return unknown unless confirmed |
| `tolerance_mm.max` | `capabilities.tolerance_mm.min` | `mdc:toleranceMinMm` | unknown-aware | Return unknown unless confirmed; do not infer from DIN4 |
| `batch_size` | `capabilities.batch_size.min/max` | `mdc:batchMin`, `mdc:batchMax` | hard/soft | Match if batch is within 100–2000; outside range may be no_match or partial depending policy |
| `delivery.max_weeks` | `capabilities.lead_time_weeks.min/max` | `mdc:leadTimeMinWeeks`, `mdc:leadTimeMaxWeeks` | soft/conditional | Normal range is 8–12 weeks; below 8 requires confirmation |
| `certifications[]` | `providers[].certifications[]` | `MaaSProvider -> hasCertification -> Certification` | hard for known required certs | Match ISO9001/ISO14001/APQP/partial ISO_TS if present |
| `traceability_required` | `capabilities.traceability` | `ProviderOffering -> supportsTraceability` | unknown-aware | Unknown unless explicitly confirmed |
| `industry` | `offerings[].industries[]` | `ProviderOffering -> supportsIndustry -> IndustrySector` | soft/unknown-aware | Use only if controlled vocabulary is finalized |
| `match_policy.unknown_policy` | request-only | internal search behavior | informational | Default: `keep_as_unknown` |
| `match_policy.minimum_score` | request-only | internal scoring behavior | informational | Optional threshold after scoring |

---

## 4. Fields excluded from v1 mapping

The following fields must not be mapped in v1:

| Excluded field | Reason |
|---|---|
| `route_steps` | Routes are out of scope for this version |
| `operation_sequence` | Routes are out of scope for this version |
| `machine_sequence` | Machine-level routing is out of scope |
| `cycle_time` | Not available and out of scope |
| `setup_time` | Not available and out of scope |
| `machine_availability` | Real-time availability is out of scope |
| `price` / `cost` | Pricing engine is out of scope |

---

## 5. TSW confirmed capability mapping

| Capability | TSW confirmed value | Seed-data field | Search behavior |
|---|---|---|---|
| Batch size | 100–2000 pcs | `batch_size.min/max` | Match inside range |
| Module | 0.3–10 | `module.min/max` | Range overlap |
| Diametral pitch | raw DP 85–2.5 | `diametral_pitch.min/max/raw` | Optional range overlap |
| Diameter | 10–450 mm | `diameter_mm.min/max` | Hard range |
| Quality | DIN4 | `quality.standard/best_class` | DIN class comparison |
| Weight | up to approx. 200 kg | `weight_kg.max` | Hard if supplied, with approximate evidence |
| Lead time | normal 8–12 weeks | `lead_time_weeks.min/max` | Soft/conditional |
| Materials | alloyed carburizing steels | `supported_materials` | Match generic steel/alloyed carburizing steel |
| Material grades | 18CrNiMo7-6, 16MnCr5, 20MnCr5 | `supported_material_grades` | Match listed grades |
| Surface finish | not confirmed | `surface_finish_ra_um.max` | Unknown |
| General tolerance | not confirmed | `tolerance_mm.min` | Unknown |
| Aerospace traceability | not confirmed | `traceability` | Unknown |

---

## 6. Quality-class comparison rule

For DIN gear quality classes, lower class numbers indicate higher quality.

Use this rule for v1:

```text
provider_best_class <= requested_max_class
```

Example:

| Provider best class | Request max class | Result |
|---:|---:|---|
| 4 | 4 | matched |
| 4 | 5 | matched |
| 4 | 3 | no_match / requires confirmation |

---

## 7. Lead-time comparison rule

TSW normal lead time is case-dependent, but represented as 8–12 weeks.

| Request | Result |
|---|---|
| `delivery.max_weeks >= 12` | matched |
| `8 <= delivery.max_weeks < 12` | partial / conditional |
| `delivery.max_weeks < 8` | unmatched or requires confirmation |
| missing delivery | ignore criterion |

---

## 8. Explanation mapping

Search results should explain each supplied request field using one of these statuses:

| Status | When used |
|---|---|
| `matched` | Provider/offering data satisfies the request |
| `unmatched` | Known provider/offering data conflicts with the request |
| `unknown` | Provider/offering data does not confirm or deny the request |
| `ignored` | Field was absent or not applicable |

Example unknown fields for TSW v1:

- `surface_finish.ra_um`
- `tolerance_mm`
- `aerospace_traceability`

---

## 9. SPARQL template groups

| Template group | Uses fields |
|---|---|
| `service_type_filter` | `service_type` |
| `part_family_filter` | `part_family` |
| `material_filter` | `materials[]` |
| `material_grade_filter` | `material_grades[]` |
| `process_filter` | `processes[]` |
| `diameter_range_filter` | `dimensions.diameter_mm.min/max` |
| `weight_filter` | `weight_kg.max` |
| `module_range_filter` | `gear_parameters.module.min/max` |
| `diametral_pitch_range_filter` | `gear_parameters.diametral_pitch.min/max` |
| `quality_filter` | `gear_parameters.quality` |
| `batch_filter` | `batch_size` |
| `lead_time_filter` | `delivery.max_weeks` |
| `certification_filter` | `certifications[]` |
| `evidence_projection` | all matched capability values |

No template should accept raw, unvalidated text.

---

## 10. Review checklist

Before coding search logic, confirm:

- [ ] `material_grades[]` is added to API contract.
- [ ] Route fields remain excluded.
- [ ] TSW questionnaire values are reflected in seed data.
- [ ] Surface finish and general tolerance remain unknown.
- [ ] DIN quality comparison rule is accepted.
- [ ] Lead-time comparison rule is accepted.
- [ ] Unsupported fields behavior is finalized in API contract.
---
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