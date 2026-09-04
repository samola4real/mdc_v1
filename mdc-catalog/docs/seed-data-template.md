# MaaS Dynamic Catalogue — Seed Data Template v1

**Status:** Week 1 finalized draft  
**Project:** MaaSAI MaaS Dynamic Catalogue  
**Scenario:** Basic structured-search scenario  
**Pilot:** Tasowheel / TSW gear and shaft manufacturing  
**Target seed file:** `data/curated/tasowheel_offerings.yaml`

---

## 1. Purpose

This document defines the curated YAML seed-data structure used to create the initial Tasowheel RDF catalogue graph.

The seed data is the bridge between provider-confirmed pilot information and the ontology-backed catalogue.

For v1, the seed data represents **provider offerings and capability ranges**, not manufacturing routes.

---

## 2. Design principles

1. **Provider-confirmed values first**  
   Use TSW questionnaire values as the highest-priority source.

2. **Offering-level capability first**  
   Store search limits at offering level, not machine level.

3. **No route fields in v1**  
   Do not include operation sequence, route steps, or route alternatives.

4. **Preserve uncertainty**  
   Unknown values must be explicit rather than guessed.

5. **Keep provenance**  
   Important values must include `source_type`, `confidence`, and optional `source_note`.

---

## 3. Allowed source types

| Value | Meaning |
|---|---|
| `provider_confirmed` | Confirmed by TSW questionnaire or direct provider data |
| `machine_list` | Derived from TSW machine list, not necessarily offering-level capability |
| `curated` | Manually normalized by project team |
| `public_web` | Publicly available source |
| `not_confirmed` | Field exists in schema but not confirmed |

---

## 4. Allowed confidence values

| Value | Meaning |
|---|---|
| `declared` | Explicitly declared by provider/source |
| `curated` | Normalized by the project team from a source value |
| `inferred` | Inferred from available data |
| `estimated` | Estimated, should be avoided in v1 unless clearly marked |
| `unknown` | Not available or not confirmed |

---

## 5. YAML structure

```yaml
metadata:
  dataset_id: tasowheel_seed_v1
  version: 1.0
  status: provider_confirmed_seed
  route_fields_included: false
  notes:
    - Route/operation sequence fields are excluded from v1.
    - Offering-level capability values come from the TSW questionnaire.

providers:
  - provider_id: tasowheel
    legal_name: Tasowheel Oy
    display_name: Tasowheel Oy
    provider_type: MaaSProvider
    country: Finland
    source_type: provider_confirmed
    confidence: declared
    facilities:
      - facility_id: tasowheel_tampere
        city: Tampere
        country: Finland
        confidence: curated
    certifications:
      - code: ISO9001_2015
        label: ISO 9001:2015
        confidence: declared
        source_type: provider_confirmed
      - code: ISO14001_2015
        label: ISO 14001:2015
        confidence: declared
        source_type: provider_confirmed
      - code: ISO_TS_16949_partial
        label: Partial implementation of ISO/TS 16949
        confidence: declared
        source_type: provider_confirmed
      - code: APQP
        label: Advanced Product Quality Planning
        confidence: declared
        source_type: provider_confirmed

materials:
  - material_id: steel
    label: Steel
    ontology_concept: mdc:Steel
  - material_id: alloyed_carburizing_steel
    label: Alloyed carburizing steel
    ontology_concept: mdc:Steel
    parent_material_id: steel

material_grades:
  - grade_id: 18CrNiMo7-6
    label: 18CrNiMo7-6
    material_id: alloyed_carburizing_steel
    confidence: declared
    source_type: provider_confirmed
  - grade_id: 16MnCr5
    label: 16MnCr5
    material_id: alloyed_carburizing_steel
    confidence: declared
    source_type: provider_confirmed
  - grade_id: 20MnCr5
    label: 20MnCr5
    material_id: alloyed_carburizing_steel
    confidence: declared
    source_type: provider_confirmed

offerings:
  - offering_id: tasowheel_gears_shafts_precision
    provider_id: tasowheel
    name: High-quality gears and shafts
    service_type: gear_manufacturing
    ontology_service_concept: mdc:GearTransmissionService
    source_type: provider_confirmed
    confidence: declared
    part_families:
      - gear
      - spur_gear
      - helical_gear
      - shaft
      - transmission_component
    processes:
      - machining
      - turning
      - milling
      - hobbing
      - gear_shaping
      - hard_turning
      - grinding
      - gear_grinding
      - heat_treatment
      - inspection
    supported_materials:
      - material: steel
        confidence: declared
        source_type: provider_confirmed
      - material: alloyed_carburizing_steel
        confidence: declared
        source_type: provider_confirmed
    supported_material_grades:
      - 18CrNiMo7-6
      - 16MnCr5
      - 20MnCr5
    capabilities:
      batch_size:
        min: 100
        max: 2000
        unit: pcs
        confidence: declared
        source_type: provider_confirmed
      diameter_mm:
        min: 10
        max: 450
        confidence: declared
        source_type: provider_confirmed
      weight_kg:
        max: 200
        approximate: true
        confidence: declared
        source_type: provider_confirmed
      module:
        min: 0.3
        max: 10
        confidence: declared
        source_type: provider_confirmed
      diametral_pitch:
        min: 2.5
        max: 85
        raw: "DP 85-2.5"
        normalized_order: ascending
        confidence: declared
        source_type: provider_confirmed
      quality:
        standard: DIN
        best_class: 4
        comparison_rule: lower_or_equal_is_better
        confidence: declared
        source_type: provider_confirmed
      lead_time_weeks:
        min: 8
        max: 12
        qualifier: normal_case_dependent
        confidence: declared
        source_type: provider_confirmed
      surface_finish_ra_um:
        max: null
        confidence: unknown
        source_type: not_confirmed
      tolerance_mm:
        min: null
        confidence: unknown
        source_type: not_confirmed
      traceability:
        aerospace_traceability: null
        full_traceability: null
        confidence: unknown
        source_type: not_confirmed
    notes:
      - TSW specializes in power transmission components, especially gears and shafts.
      - Heat treatment is known from provider data but should not be interpreted as an in-house capability unless confirmed.
      - Route sequencing is intentionally excluded from v1.
```

---

## 6. Required fields for v1 seed data

| Field | Required? | Notes |
|---|---:|---|
| `metadata.dataset_id` | Yes | Stable dataset identifier |
| `metadata.route_fields_included` | Yes | Must be `false` for v1 |
| `providers[].provider_id` | Yes | Stable slug |
| `providers[].display_name` | Yes | UI display name |
| `providers[].certifications` | Yes | At least known certifications |
| `materials` | Yes | At least generic steel support |
| `material_grades` | Yes | TSW-confirmed grades |
| `offerings[].offering_id` | Yes | Stable offering slug |
| `offerings[].provider_id` | Yes | Must reference provider |
| `offerings[].service_type` | Yes | Controlled value |
| `offerings[].part_families` | Yes | At least gears/shafts |
| `offerings[].processes` | Yes | Controlled process values |
| `offerings[].capabilities` | Yes | Searchable numeric/quality fields |
| `confidence` / `source_type` | Yes for important values | Needed for explainable evidence |

---

## 7. Fields intentionally excluded from v1 seed data

Do not include these as queryable fields in `tasowheel_offerings.yaml` v1:

- `routes`
- `route_steps`
- `operation_sequence`
- `machine_sequence`
- `process_order`
- `subcontractor_route`
- `cycle_time`
- `setup_time`
- `machine_availability`
- `pricing`
- `capacity_calendar`

---

## 8. Transformation expectation

The RDF generation script should transform this YAML into:

- one `mdc:MaaSProvider` instance
- one primary `mdc:ProviderOffering` instance
- material and material-grade concepts
- object links for service type, process, material, part family, certification
- data properties for diameter, weight, module, DP, batch, quality, and lead time
- provenance/confidence data for explainable search results

---

## 9. Review checklist

Before generating RDF, confirm:

- [ ] `route_fields_included` is `false`.
- [ ] TSW provider ID is `tasowheel`.
- [ ] Primary offering ID is `tasowheel_gears_shafts_precision`.
- [ ] Batch size is `100–2000`.
- [ ] Diameter range is `10–450 mm`.
- [ ] Weight max is approximately `200 kg`.
- [ ] Module range is `0.3–10`.
- [ ] DP range preserves raw value `DP 85-2.5`.
- [ ] Lead time is `8–12 weeks`, case-dependent.
- [ ] Surface finish and general tolerance remain unknown.
