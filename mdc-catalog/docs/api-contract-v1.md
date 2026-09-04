# MaaS Dynamic Catalogue — API Contract v1

**Status:** Week 1 finalized baseline  
**Project:** MaaSAI MaaS Dynamic Catalogue  
**Scenario:** Basic structured-search scenario  
**Pilot:** Tasowheel / TSW gear and shaft manufacturing  
**Base path:** `/api/v1`

---

## 1. Purpose

This document defines the v1 REST API contract for the **MaaS Dynamic Catalogue (MDC)** basic scenario.

The API allows the **Cloud MaaS Marketplace** to:

- retrieve available catalogue filter values
- submit a structured manufacturing search request
- receive matching MaaS Provider offerings
- inspect provider and offering detail records
- check service health

The main endpoint is:

```http
POST /api/v1/catalog/search
```

Route fields and route-step queries are not part of API v1.

---

## 2. API design principles

1. **Marketplace-friendly JSON**  
   Request and response bodies should be easy for a frontend marketplace to consume.

2. **Controlled vocabulary input**  
   Fields such as `service_type`, `part_family`, `processes`, `materials`, `material_grades`, and `certifications` must use controlled values where defined.

3. **Explainable results**  
   Every search result must explain matched, unknown, and unmatched attributes.

4. **Unknown does not always mean rejection**  
   If a requested field is not confirmed in v1 data, the result may still be returned as `partial_match`.

5. **Stable contract for future NLP scenario**  
   The future natural-language extraction layer must produce the same `SearchRequest` structure.

6. **No route fields in v1**  
   Operation sequences, route steps, and machine routes are excluded from this API version.

---

## 3. Endpoint overview

| Method | Endpoint | Purpose | v1 priority |
|---|---|---|---|
| `GET` | `/api/v1/health` | Health check | Required |
| `GET` | `/api/v1/catalog/filters` | UI filter values | Required |
| `POST` | `/api/v1/catalog/search` | Main catalogue search | Required |
| `GET` | `/api/v1/providers/{provider_id}` | Provider detail | Recommended |
| `GET` | `/api/v1/offerings/{offering_id}` | Offering detail | Recommended |

---

## 4. `GET /api/v1/health`

### Example response

```json
{
  "status": "ok",
  "service": "maasai-mdc",
  "version": "v1"
}
```

### Acceptance criteria

- Returns HTTP `200` when Django service is running.
- Does not require Fuseki for basic service check.
- May later include Fuseki status as an optional field.

---

## 5. `GET /api/v1/catalog/filters`

### Purpose

Returns controlled vocabulary values that the marketplace UI can use for dropdowns and checkboxes.

### Example response

```json
{
  "service_types": [
    {"value": "gear_manufacturing", "label": "Gear manufacturing"},
    {"value": "shaft_manufacturing", "label": "Shaft manufacturing"},
    {"value": "machining", "label": "Machining"},
    {"value": "heat_treatment", "label": "Heat treatment"},
    {"value": "inspection", "label": "Inspection"},
    {"value": "finishing", "label": "Finishing"}
  ],
  "part_families": [
    {"value": "gear", "label": "Gear"},
    {"value": "spur_gear", "label": "Spur gear"},
    {"value": "helical_gear", "label": "Helical gear"},
    {"value": "shaft", "label": "Shaft"},
    {"value": "transmission_component", "label": "Transmission component"}
  ],
  "processes": [
    {"value": "machining", "label": "Machining"},
    {"value": "turning", "label": "Turning"},
    {"value": "milling", "label": "Milling"},
    {"value": "hobbing", "label": "Hobbing"},
    {"value": "gear_shaping", "label": "Gear shaping"},
    {"value": "hard_turning", "label": "Hard turning"},
    {"value": "grinding", "label": "Grinding"},
    {"value": "gear_grinding", "label": "Gear grinding / tooth grinding"},
    {"value": "heat_treatment", "label": "Heat treatment"},
    {"value": "inspection", "label": "Inspection / quality checking"}
  ],
  "materials": [
    {"value": "steel", "label": "Steel"},
    {"value": "alloyed_carburizing_steel", "label": "Alloyed carburizing steel"},
    {"value": "stainless_steel", "label": "Stainless steel"},
    {"value": "aluminum", "label": "Aluminum"},
    {"value": "titanium", "label": "Titanium"},
    {"value": "nickel_alloy", "label": "Nickel alloy"}
  ],
  "material_grades": [
    {"value": "18CrNiMo7-6", "label": "18CrNiMo7-6"},
    {"value": "16MnCr5", "label": "16MnCr5"},
    {"value": "20MnCr5", "label": "20MnCr5"}
  ],
  "certifications": [
    {"value": "ISO9001_2015", "label": "ISO 9001:2015"},
    {"value": "ISO14001_2015", "label": "ISO 14001:2015"},
    {"value": "ISO_TS_16949_partial", "label": "Partial ISO/TS 16949 implementation"},
    {"value": "APQP", "label": "Advanced Product Quality Planning"},
    {"value": "aerospace_traceability", "label": "Aerospace traceability"},
    {"value": "full_traceability", "label": "Full traceability"}
  ]
}
```

### Acceptance criteria

- Returns HTTP `200`.
- Values match `docs/ontology-profile-v1.md`.
- This endpoint does not require a SPARQL query in v1; values may come from static backend vocabulary definitions.

---

## 6. `POST /api/v1/catalog/search`

### Purpose

Main structured search endpoint.

The marketplace sends a structured manufacturing request. The MDC validates it, maps it to ontology concepts, executes SPARQL against Fuseki, and returns provider offering matches.

---

## 7. Search request schema

### Example request

```json
{
  "service_type": "gear_manufacturing",
  "part_family": "spur_gear",
  "materials": ["steel"],
  "material_grades": ["18CrNiMo7-6"],
  "processes": ["gear_grinding"],
  "dimensions": {
    "diameter_mm": {"max": 300}
  },
  "weight_kg": {"max": 50},
  "gear_parameters": {
    "module": {"min": 1, "max": 5},
    "diametral_pitch": {"min": 5, "max": 40},
    "quality": {"standard": "DIN", "max_class": 4}
  },
  "surface_finish": {
    "ra_um": {"max": 1.6}
  },
  "batch_size": 100,
  "delivery": {"max_weeks": 12},
  "certifications": ["ISO9001_2015"],
  "traceability_required": false,
  "industry": "power_transmission",
  "match_policy": {
    "unknown_policy": "keep_as_unknown",
    "minimum_score": 0.5
  }
}
```

---

## 8. Search request fields

| Field | Type | Required? | Rule |
|---|---|---:|---|
| `service_type` | string | Yes | Must be controlled vocabulary value |
| `part_family` | string | No | Controlled vocabulary if supplied |
| `materials` | array[string] | No | Controlled vocabulary if supplied |
| `material_grades` | array[string] | No | Controlled material-grade value if supplied |
| `processes` | array[string] | No | Controlled vocabulary if supplied |
| `dimensions.diameter_mm.min` | number | No | Must be positive if supplied |
| `dimensions.diameter_mm.max` | number | No | Must be positive if supplied |
| `weight_kg.max` | number | No | Must be positive if supplied |
| `gear_parameters.module.min` | number | No | Must be positive if supplied |
| `gear_parameters.module.max` | number | No | Must be positive and >= min if supplied |
| `gear_parameters.diametral_pitch.min` | number | No | Must be positive if supplied |
| `gear_parameters.diametral_pitch.max` | number | No | Must be positive and >= min if supplied |
| `gear_parameters.quality.standard` | string | No | Allowed values: `DIN`, `ISO` |
| `gear_parameters.quality.max_class` | number/string | No | Standard-specific |
| `surface_finish.ra_um.max` | number | No | Must be positive if supplied; TSW value unknown in v1 |
| `batch_size` | integer | No | Must be greater than 0 if supplied |
| `delivery.max_weeks` | number | No | Must be positive if supplied |
| `certifications` | array[string] | No | Controlled vocabulary if supplied |
| `traceability_required` | boolean | No | Defaults to `false` if absent |
| `industry` | string | No | Use controlled vocabulary when finalized; soft matching only in v1 |
| `match_policy.unknown_policy` | string | No | Default `keep_as_unknown` |
| `match_policy.minimum_score` | number | No | Optional threshold between 0 and 1 |

### Fields excluded from API v1

The following request fields are not supported in this version:

- `route_steps`
- `operation_sequence`
- `machine_sequence`
- `cycle_time`
- `setup_time`
- `machine_availability`
- `price`

If supplied, these fields should be ignored with a warning or rejected depending on final strictness mode.

---

## 9. Request validation rules

| Rule | Error behavior |
|---|---|
| `service_type` is missing | `400 Bad Request` |
| `service_type` is not in vocabulary | `400 Bad Request` |
| controlled vocabulary field has unknown value | `400 Bad Request` |
| numeric field is negative or zero where positive required | `400 Bad Request` |
| `module.min > module.max` | `400 Bad Request` |
| `diametral_pitch.min > diametral_pitch.max` | `400 Bad Request` |
| `batch_size <= 0` | `400 Bad Request` |
| unsupported route/machine/price field present | return warning in `warnings[]`; do not use for search |
| Fuseki unavailable | `503 Service Unavailable` |

---

## 10. Query interpretation object

The response should include a `query_interpretation` object so the marketplace and developer can see how user input was mapped.

Example:

```json
{
  "service_type": {
    "input": "gear_manufacturing",
    "mapped_concept": "mdc:GearTransmissionService"
  },
  "materials": [
    {"input": "steel", "mapped_concept": "mdc:Steel"}
  ],
  "material_grades": [
    {"input": "18CrNiMo7-6", "mapped_concept": "mdc:MaterialGrade_18CrNiMo7_6"}
  ],
  "processes": [
    {"input": "gear_grinding", "mapped_concept": "mdc:GearGrinding"}
  ]
}
```

---

## 11. Search response schema

### Example response

```json
{
  "request_id": "generated-request-id",
  "warnings": [],
  "query_interpretation": {
    "service_type": {
      "input": "gear_manufacturing",
      "mapped_concept": "mdc:GearTransmissionService"
    },
    "materials": [
      {"input": "steel", "mapped_concept": "mdc:Steel"}
    ],
    "material_grades": [
      {"input": "18CrNiMo7-6", "mapped_concept": "mdc:MaterialGrade_18CrNiMo7_6"}
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
        "score": 0.86,
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
          "field": "material_grades",
          "requested": "18CrNiMo7-6",
          "provided": "18CrNiMo7-6",
          "status": "matched",
          "confidence": "declared"
        },
        {
          "field": "diameter_mm.max",
          "requested": 300,
          "provided_min": 10,
          "provided_max": 450,
          "status": "matched",
          "confidence": "declared"
        },
        {
          "field": "batch_size",
          "requested": 100,
          "provided_min": 100,
          "provided_max": 2000,
          "status": "matched",
          "confidence": "declared"
        },
        {
          "field": "delivery.max_weeks",
          "requested": 12,
          "provided_min": 8,
          "provided_max": 12,
          "status": "matched",
          "confidence": "declared"
        }
      ],
      "unknown_attributes": [
        {
          "field": "surface_finish.ra_um",
          "requested": 1.6,
          "reason": "No confirmed surface roughness value in v1 seed data"
        }
      ],
      "unmatched_attributes": [],
      "evidence": [
        {"field": "diameter_mm", "value": "10-450", "unit": "mm", "source_type": "provider_confirmed", "confidence": "declared"},
        {"field": "module", "value": "0.3-10", "source_type": "provider_confirmed", "confidence": "declared"},
        {"field": "quality", "value": "DIN4", "source_type": "provider_confirmed", "confidence": "declared"},
        {"field": "lead_time_weeks", "value": "8-12", "source_type": "provider_confirmed", "confidence": "declared"}
      ]
    }
  ]
}
```

---

## 12. Match object

| Field | Type | Meaning |
|---|---|---|
| `status` | string | `full_match`, `partial_match`, `no_match`, or `unknown` |
| `score` | number | 0–1 score based on applicable criteria |
| `hard_filters_passed` | boolean | Whether hard constraints passed |

---

## 13. Attribute explanation objects

### Matched attribute

```json
{
  "field": "diameter_mm.max",
  "requested": 300,
  "provided_max": 450,
  "status": "matched",
  "confidence": "declared"
}
```

### Unknown attribute

```json
{
  "field": "surface_finish.ra_um",
  "requested": 1.6,
  "reason": "No confirmed surface roughness value in v1 seed data"
}
```

### Unmatched attribute

```json
{
  "field": "diameter_mm.max",
  "requested": 700,
  "provided_max": 450,
  "status": "unmatched",
  "reason": "Requested diameter exceeds known provider maximum"
}
```

---

## 14. Error response format

```json
{
  "error": {
    "code": "invalid_request",
    "message": "The request payload is invalid.",
    "details": [
      {"field": "service_type", "message": "This field is required."}
    ]
  }
}
```

| HTTP status | Code | Meaning |
|---:|---|---|
| `400` | `invalid_request` | Request schema or validation error |
| `404` | `not_found` | Provider/offering not found |
| `503` | `catalog_store_unavailable` | Fuseki unavailable |
| `500` | `internal_error` | Unexpected backend error |

---

## 15. `GET /api/v1/providers/{provider_id}`

### Example response

```json
{
  "provider_id": "tasowheel",
  "display_name": "Tasowheel Oy",
  "country": "Finland",
  "certifications": [
    "ISO9001_2015",
    "ISO14001_2015",
    "ISO_TS_16949_partial",
    "APQP"
  ],
  "offerings": [
    {"offering_id": "tasowheel_gears_shafts_precision", "name": "High-quality gears and shafts"}
  ]
}
```

---

## 16. `GET /api/v1/offerings/{offering_id}`

### Example response

```json
{
  "offering_id": "tasowheel_gears_shafts_precision",
  "provider_id": "tasowheel",
  "name": "High-quality gears and shafts",
  "service_type": "gear_manufacturing",
  "part_families": ["gear", "spur_gear", "helical_gear", "shaft", "transmission_component"],
  "processes": ["machining", "turning", "milling", "hobbing", "gear_shaping", "hard_turning", "grinding", "gear_grinding", "heat_treatment", "inspection"],
  "materials": ["steel", "alloyed_carburizing_steel"],
  "material_grades": ["18CrNiMo7-6", "16MnCr5", "20MnCr5"],
  "capabilities": {
    "batch_size": {"min": 100, "max": 2000, "unit": "pcs", "confidence": "declared", "source_type": "provider_confirmed"},
    "diameter_mm": {"min": 10, "max": 450, "confidence": "declared", "source_type": "provider_confirmed"},
    "weight_kg": {"max": 200, "approximate": true, "confidence": "declared", "source_type": "provider_confirmed"},
    "module": {"min": 0.3, "max": 10, "confidence": "declared", "source_type": "provider_confirmed"},
    "diametral_pitch": {"min": 2.5, "max": 85, "raw": "DP 85-2.5", "confidence": "declared", "source_type": "provider_confirmed"},
    "quality": {"standard": "DIN", "best_class": 4, "confidence": "declared", "source_type": "provider_confirmed"},
    "lead_time_weeks": {"min": 8, "max": 12, "qualifier": "normal_case_dependent", "confidence": "declared", "source_type": "provider_confirmed"},
    "surface_finish_ra_um": {"max": null, "confidence": "unknown", "source_type": "not_confirmed"}
  }
}
```

Route fields are intentionally absent from this response.

---

## 17. Acceptance scenarios

### Positive search

Input:

- service type: `gear_manufacturing`
- part family: `spur_gear`
- material grade: `18CrNiMo7-6`
- diameter max: `300`
- module: `1–5`
- batch size: `100`
- delivery: `12 weeks`
- quality: `DIN4`

Expected:

- Tasowheel gear/shaft offering returned.
- Status is `full_match` or `partial_match`.
- Evidence includes diameter `10–450 mm`, module `0.3–10`, batch `100–2000`, lead time `8–12`, and quality `DIN4`.

### Negative diameter search

Input:

- service type: `gear_manufacturing`
- diameter max: `700`

Expected:

- Tasowheel offering is not returned, or is returned with `no_match` depending on implementation choice.
- Reason states that requested diameter exceeds provider maximum.

### Unknown surface finish

Input:

- service type: `gear_manufacturing`
- surface finish Ra: `1.6`

Expected:

- Tasowheel may still be returned.
- `surface_finish.ra_um` appears in `unknown_attributes`.
- Result status is `partial_match`.

### ISO9001 certification

Input:

- service type: `gear_manufacturing`
- certification: `ISO9001_2015`

Expected:

- Tasowheel returned.
- Certification listed as matched.

### Short lead-time request

Input:

- service type: `gear_manufacturing`
- delivery max: `4 weeks`

Expected:

- Result is not a full match.
- Lead time is returned as unmatched or requires confirmation because normal lead time is 8–12 weeks.

---

## 18. Review checklist

Before implementation:

- [x] Endpoint list approved.
- [x] SearchRequest schema updated with `material_grades`.
- [x] Route fields excluded.
- [x] Search response schema updated with provider-confirmed TSW values.
- [x] Validation rules approved.
- [x] Error response format approved.
- [x] Unknown policy approved.
- [x] Acceptance scenarios updated.
