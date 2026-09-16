# MaaSAI MaaS Dynamic Catalogue (MDC)

## Current API Documentation and Integration Reference

**Document status:** Authoritative current API reference for the MDC v1 pilot  
**Documentation date:** 16 September 2026  
**API implementation baseline audited:** `bca326367495e92b26dc9e290da04e9056b226a8` (`main`)  
**Public contract version:** `1.0`  
**Repository:** `samola4real/mdc_v1`  
**Backend location:** `mdc-catalog/backend/`  
**Hosted pilot base URL:** `https://maasai-mdc-v1.vercel.app`  
**Local development base URL:** `http://localhost:8000`

> **Current-source rule.** This document is derived from the current Django URL configuration, serializers, lifecycle security helpers, public response builders, controlled-vocabulary registry, persistence services, and accepted Phase 2/Phase 3 implementation baseline. Older Week 1 examples, `/api/v1/...` paths, and legacy payloads are historical only.

> **Integration rule.** New Marketplace/consumer integrations should use only the canonical public API unless a separate trusted provider-lifecycle integration has been explicitly agreed. Trusted lifecycle credentials must never be embedded in browser code.

---

## Contents

1. [API at a glance](#1-api-at-a-glance)
2. [Base URLs, content type, and versioning](#2-base-urls-content-type-and-versioning)
3. [Public API](#3-public-api)
4. [Catalogue filters and controlled vocabulary](#4-catalogue-filters-and-controlled-vocabulary)
5. [Service-discovery request contract](#5-service-discovery-request-contract)
6. [Service-discovery matching and response contract](#6-service-discovery-matching-and-response-contract)
7. [Trusted provider lifecycle API](#7-trusted-provider-lifecycle-api)
8. [Provider-publication contract](#8-provider-publication-contract)
9. [Provider and offering read/update contracts](#9-provider-and-offering-readupdate-contracts)
10. [Authentication, actor attribution, and ETag concurrency](#10-authentication-actor-attribution-and-etag-concurrency)
11. [Error contract and HTTP status codes](#11-error-contract-and-http-status-codes)
12. [Demo-only API](#12-demo-only-api)
13. [Legacy and unsupported routes](#13-legacy-and-unsupported-routes)
14. [cURL/Postman quick-start examples](#14-curlpostman-quick-start-examples)
15. [CMM integration guidance](#15-cmm-integration-guidance)
16. [Security and operational boundaries](#16-security-and-operational-boundaries)
17. [Source-of-truth code map](#17-source-of-truth-code-map)

---

# 1. API at a glance

## 1.1 Canonical public API

These are the endpoints to give to a new consumer/Marketplace integration.

| Method | Path | Authentication | Purpose |
|---|---|---|---|
| `GET` | `/api/health` | None | Service health and contract version |
| `GET` | `/api/catalog/filters` | None | Dynamic controlled values for search forms |
| `POST` | `/api/service-discovery/search` | None | Search provider offerings against structured requirements |

There is **no current `/api/v1/...` route**. URL versioning is intentionally not used.

## 1.2 Trusted provider lifecycle API

These endpoints are a separate server-to-server integration surface.

| Method | Path | Typical protection | Purpose |
|---|---|---|---|
| `POST` | `/api/provider-publication/validation` | Bearer service token | Validate/normalize a provider publication without writing |
| `POST` | `/api/provider-publication` | Bearer + actor | Register a provider and offerings |
| `GET` | `/api/providers/{provider_id}` | Bearer | Read one provider lifecycle representation |
| `PATCH` | `/api/providers/{provider_id}` | Bearer + actor + ETag precondition | Update editable provider fields |
| `GET` | `/api/providers/{provider_id}/offerings` | Bearer | List that provider's offerings |
| `POST` | `/api/providers/{provider_id}/offerings` | Bearer + actor | Create another offering for that provider |
| `GET` | `/api/offerings/{offering_id}` | Bearer | Read one offering lifecycle representation |
| `PATCH` | `/api/offerings/{offering_id}` | Bearer + actor + ETag precondition | Update editable offering fields |

There is **no collection `GET /api/providers`** endpoint and there are **no DELETE endpoints** in the current lifecycle API.

## 1.3 Demo-only API

The `/api/demo/...` namespace supports the MDC Demo Frontend and is **not** part of the Marketplace API contract. Production settings normally disable it unless a specific demo environment is deliberately configured.

---

# 2. Base URLs, content type, and versioning

## 2.1 Base URLs

Hosted pilot:

```text
https://maasai-mdc-v1.vercel.app
```

Local development:

```text
http://localhost:8000
```

Examples in this document use:

```text
{{base_url}}
```

## 2.2 Content type

For request bodies:

```http
Content-Type: application/json
Accept: application/json
```

Responses are JSON.

## 2.3 Contract version

The active public contract is `1.0`.

For canonical POST/PATCH/create request bodies, `contract_version` is optional. If omitted, the server uses `1.0`. If supplied, it must equal `1.0`.

Unsupported version example:

```json
{
  "contract_version": "1.0",
  "error": {
    "code": "unsupported_contract_version",
    "message": "Unsupported contract_version '2.0'. Supported versions: ['1.0']"
  }
}
```

HTTP status: `400 Bad Request`.

### Versioning policy

- Canonical routes remain under `/api/...`.
- Do not use `/api/v1/...`.
- Contract evolution is represented by `contract_version` metadata rather than a URL prefix.
- Existing legacy routes do not define the current partner contract.

---

# 3. Public API

## 3.1 `GET /api/health`

Purpose: verify that the MDC HTTP service is available.

### Request

```http
GET {{base_url}}/api/health
Accept: application/json
```

### Response — `200 OK`

```json
{
  "contract_version": "1.0",
  "status": "ok",
  "service": "maasai-mdc"
}
```

This response deliberately stays small and does not expose database credentials, Fuseki credentials, or internal lifecycle state.

---

## 3.2 `GET /api/catalog/filters`

Purpose: provide the current controlled values needed to render consumer search controls dynamically.

### Request

```http
GET {{base_url}}/api/catalog/filters
Accept: application/json
```

### Response shape — `200 OK`

```json
{
  "contract_version": "1.0",
  "service_categories": [
    {
      "value": "precision_gears",
      "label": "Precision gears",
      "part_family": "gear"
    }
  ],
  "part_families": [
    {
      "value": "gear",
      "label": "Gear",
      "service_category": "precision_gears"
    }
  ],
  "part_types": {
    "gear": [
      { "value": "spur_gear", "label": "Spur gear" }
    ]
  },
  "materials": [],
  "processes": [],
  "certifications": []
}
```

The real response contains all currently registered values listed in Section 4. Clients should load this endpoint rather than hard-code the vocabulary permanently.

---

## 3.3 `POST /api/service-discovery/search`

Purpose: search provider offerings against a controlled selection and optional manufacturing requirements.

### Minimal valid request

```json
{
  "contract_version": "1.0",
  "request_id": "req-001",
  "consumer_id": "consumer-001",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear"
}
```

`requirements` and `match_policy` are optional and default to empty/default structures.

### Representative gear request

```json
{
  "contract_version": "1.0",
  "request_id": "req-gear-001",
  "consumer_id": "consumer-001",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear",
  "requirements": {
    "part_family_specifications": {
      "module": { "exact": 2.0 },
      "outside_diameter_mm": { "max": 100 },
      "gear_quality": {
        "standard": "DIN",
        "max_class": 6
      }
    },
    "part_type_specifications": {
      "face_width_mm": { "exact": 25 }
    },
    "generic_requirements": {
      "materials": ["alloyed_carburizing_steel"],
      "processes": ["hobbing"],
      "batch_size": 500,
      "delivery": { "max_weeks": 10 },
      "certifications": ["ISO9001_2015"],
      "weight_kg": 20
    }
  },
  "match_policy": {
    "optional_match_mode": "score_only",
    "unknown_policy": "keep_as_unknown",
    "minimum_score": null
  }
}
```

### Representative response — `200 OK`

```json
{
  "contract_version": "1.0",
  "request_id": "req-gear-001",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear",
  "result_count": 1,
  "results": [
    {
      "provider_id": "example_provider",
      "provider_name": "Example Provider",
      "offering_id": "example_provider_precision_gears",
      "offering_name": "Precision gear manufacturing",
      "service_category": "precision_gears",
      "part_family": "gear",
      "match": {
        "status": "full_match",
        "score": 1.0
      },
      "matched_capabilities": [
        {
          "field": "module",
          "requested": { "exact": 2.0 },
          "provided": { "min": 0.5, "max": 6.0 }
        }
      ],
      "unmatched_capabilities": [],
      "unknown_capabilities": []
    }
  ]
}
```

The example response illustrates the public shape; provider values depend on the current catalogue.

---

# 4. Catalogue filters and controlled vocabulary

## 4.1 Service-category / part-family pairs

| `service_category` | `part_family` |
|---|---|
| `precision_gears` | `gear` |
| `precision_shafts` | `shaft` |
| `precision_metal_parts` | `metal_part` |

The pair is strict. A request that combines a category with the wrong family is rejected.

## 4.2 Part types

**Gear**

- `spur_gear`
- `helical_gear`
- `bevel_gear`
- `worm_gear`
- `crown_gear`

**Shaft**

- `plain_shaft`
- `stepped_shaft`
- `splined_shaft`
- `worm_shaft`
- `hollow_shaft`

**Metal part**

- `block`
- `plate`
- `bracket`
- `bushing`
- `roller`
- `collar`

## 4.3 Materials

- `steel`
- `alloyed_carburizing_steel`
- `stainless_steel`
- `aluminum`
- `titanium`
- `nickel_alloy`

`material_grades` are **not accepted as a canonical consumer search criterion**. Provider publications may carry available grade evidence inside material capability records.

## 4.4 Processes

- `machining`
- `turning`
- `milling`
- `hobbing`
- `gear_shaping`
- `deburring`
- `hard_turning`
- `grinding`
- `tooth_grinding`
- `gear_grinding`
- `gear_cutting`
- `surface_grinding`
- `heat_treatment`
- `turn_mill`
- `inspection`

## 4.5 Certifications

- `ISO9001_2015`
- `ISO14001_2015`
- `ISO_TS_16949_partial`
- `APQP`
- `aerospace_traceability`
- `full_traceability`

---

# 5. Service-discovery request contract

## 5.1 Top-level fields

| Field | Required | Type | Notes |
|---|---:|---|---|
| `contract_version` | No | string | If present, must be `1.0` |
| `request_id` | Yes | string | Non-empty caller request identifier |
| `consumer_id` | Yes | string | Non-empty consumer identifier |
| `service_category` | Yes | string | Controlled value from filters |
| `part_family` | Yes | string | Must match the service category |
| `part_type` | Yes | string | Must belong to the selected family |
| `requirements` | No | object | Three strict requirement groups |
| `match_policy` | No | object | Search/matching policy |

Unknown top-level fields are rejected.

The request is also recursively screened for route/operation fields that are intentionally outside the v1 contract. These forbidden keys include `routes`, `route_steps`, `operation_sequence`, `machine_sequence`, `process_order`, `subcontractor_route`, `cycle_time`, `setup_time`, `machine_availability`, `pricing`, and `capacity_calendar`.

## 5.2 Requirement groups

```json
{
  "requirements": {
    "part_family_specifications": {},
    "part_type_specifications": {},
    "generic_requirements": {}
  }
}
```

A field must appear in the group assigned to it for the selected part type. Duplicate fields across groups are rejected.

### Range/exact shape

Most dimensional fields use:

```json
{ "min": 10, "max": 100 }
```

or:

```json
{ "exact": 25 }
```

`min`, `max`, and `exact` values must be positive. If both `min` and `max` are present, `min <= max`. If `exact` is combined with bounds, it must lie inside them.

### Quality shape

```json
{
  "standard": "DIN",
  "max_class": 6
}
```

For search requests, `standard` must be a non-empty string and `max_class` a positive number.

### Bounding-box shape

For prismatic metal parts:

```json
{
  "bounding_box_mm": {
    "length_mm": { "max": 200 },
    "width_mm": { "max": 120 },
    "height_mm": { "max": 50 }
  }
}
```

At least one bounding-box component is required when the field is supplied.

## 5.3 Family and part-type field matrix

### Gear family — `part_family_specifications`

- `module`
- `diametral_pitch`
- `number_of_teeth`
- `outside_diameter_mm`
- `gear_quality`
- `tolerance_mm`

### Gear part-type-specific fields — `part_type_specifications`

| Part type | Allowed fields |
|---|---|
| `spur_gear` | `face_width_mm` |
| `helical_gear` | `face_width_mm`, `helix_angle_deg` |
| `bevel_gear` | `face_width_mm`, `shaft_angle_deg` |
| `worm_gear` | `center_distance_mm`, `shaft_angle_deg` |
| `crown_gear` | `face_width_mm`, `inner_diameter_mm` |

### Shaft family — `part_family_specifications`

- `length_mm`
- `outer_diameter_mm`
- `tolerance_mm`

### Shaft part-type-specific fields

| Part type | Allowed fields |
|---|---|
| `plain_shaft` | `principal_diameter_mm` |
| `stepped_shaft` | `number_of_steps` |
| `splined_shaft` | `spline_module`, `spline_length_mm` |
| `worm_shaft` | `worm_module`, `number_of_starts` |
| `hollow_shaft` | `inner_diameter_mm`, `wall_thickness_mm` |

### Prismatic metal parts

For `block` and `plate`:

- family: `bounding_box_mm`
- part type: `number_of_holes`

For `bracket`:

- family: `bounding_box_mm`
- part type: `vertical_flange_length_mm`, `horizontal_flange_length_mm`

### Rotational metal parts

For `bushing`, `roller`, and `collar`, family-common fields are:

- `inner_diameter_mm`
- `outer_diameter_mm`
- `overall_length_mm`
- `tolerance_mm`

`bushing` additionally accepts `flange_diameter_mm` in `part_type_specifications`. `roller` and `collar` currently have no additional type-specific fields.

## 5.4 Generic requirements

Allowed generic fields are:

| Field | Shape |
|---|---|
| `materials` | list of controlled material values |
| `processes` | list of controlled process values |
| `batch_size` | positive integer |
| `delivery` | `{ "max_weeks": <positive number> }` |
| `certifications` | list of controlled certification values |
| `surface_finish_ra_um` | range/exact object |
| `tolerance_mm` | range/exact object when not scoped to the selected profile |
| `quality` | `{ "standard": "...", "max_class": ... }` when not otherwise scoped |
| `weight_kg` | positive number |

A generic field that belongs to a selected part type's family/type scope must be supplied in that scoped group instead. `material_grades` is explicitly rejected.

## 5.5 Match policy

Default policy:

```json
{
  "optional_match_mode": "any",
  "unknown_policy": "keep_as_unknown",
  "minimum_score": null
}
```

Allowed values:

- `optional_match_mode`: `any`, `all`, `score_only`
- `unknown_policy`: `keep_as_unknown`, `reject_unknown`
- `minimum_score`: `null` or a number from `0` to `1`

`primary_match_mode` is not part of the harmonized request contract and is rejected.

---

# 6. Service-discovery matching and response contract

## 6.1 Candidate selection

The runtime first restricts candidates to offerings with the requested `service_category` and `part_family`. Requested part-type support is then evaluated as confirmed or unknown/candidate, and optional family/type/generic requirements are evaluated against provider evidence.

The harmonized matcher semantics are shared across the supported runtime retrieval paths so public response meaning does not depend on whether candidate records originated from remote Fuseki, local RDFLib, or fallback harmonized data.

## 6.2 Match status

Public `match.status` values are:

| Status | Meaning |
|---|---|
| `full_match` | Requested part type is confirmed and all supplied capability checks matched |
| `partial_match` | Requested part type is confirmed but one or more supplied capability checks are not fully matched |
| `unknown_match` | Service category/family match, but requested part-type support is not confirmed |

An `unknown_match` is not the same as a confirmed suitable provider.

## 6.3 Capability arrays

Each result may contain:

- `matched_capabilities`
- `unmatched_capabilities`
- `unknown_capabilities`

A public capability object contains:

```json
{
  "field": "module",
  "requested": { "exact": 2 },
  "provided": { "min": 0.3, "max": 10 }
}
```

For unmatched/unknown items, a `reason` can also be present. Internal provenance keys such as `source_type`, `confidence`, and `source_note` are removed from the public capability values.

Service-category, part-family, and part-type selection checks are not repeated in the public capability arrays; the selected values are represented separately in the response.

## 6.4 Score and filtering

The current harmonized matcher combines part-type selection confidence and optional-requirement coverage into a deterministic score. Internally, the current weighting is 70% selection and 30% optional-requirement coverage.

`minimum_score` filters out results below the requested threshold. `unknown_policy: reject_unknown` removes candidates whose requested part type or evaluated requirements remain unknown.

Results are ordered deterministically, primarily by descending score; otherwise-equal results use stable provider/offering identifiers.

The public contract currently has no pagination fields.

---

# 7. Trusted provider lifecycle API

The lifecycle API manages authoritative provider/offering state in PostgreSQL. It is intentionally separate from public discovery and from the demo-provider JSON workflow.

## 7.1 Lifecycle summary

| Method | Endpoint | Typical success |
|---|---|---:|
| `POST` | `/api/provider-publication/validation` | `200` |
| `POST` | `/api/provider-publication` | `201` |
| `GET` | `/api/providers/{provider_id}` | `200` + `ETag` |
| `PATCH` | `/api/providers/{provider_id}` | `200` + new `ETag` |
| `GET` | `/api/providers/{provider_id}/offerings` | `200` |
| `POST` | `/api/providers/{provider_id}/offerings` | `201` + offering `ETag` |
| `GET` | `/api/offerings/{offering_id}` | `200` + `ETag` |
| `PATCH` | `/api/offerings/{offering_id}` | `200` + new `ETag` |

Production settings default lifecycle authentication, actor attribution for writes, and concurrency protection to enabled. Provider validation and provider publication/write availability are separate deployment feature flags, so a deployment may return `403` even when a route exists.

## 7.2 Lifecycle write behavior

An accepted lifecycle write:

1. validates the request;
2. performs the domain change inside a database transaction;
3. records a `ProviderPublication`;
4. creates one or more `CatalogueSyncEvent` outbox rows;
5. returns with `publication_status: "sync_pending"` and `sync_status: "pending"`.

The request does **not** write to Fuseki synchronously. Semantic synchronization is a separate trusted operator workflow.

---

# 8. Provider-publication contract

## 8.1 `POST /api/provider-publication/validation`

Validates and normalizes a provider-publication request without persisting it.

### Headers

```http
Authorization: Bearer <trusted-service-token>
Content-Type: application/json
Accept: application/json
```

Actor attribution is not required for this non-mutating validation request.

### Valid response — `200 OK`

```json
{
  "contract_version": "1.0",
  "valid": true,
  "message": "The provider publication payload is valid.",
  "warnings": [],
  "normalized_payload": {
    "provider": {},
    "offerings": []
  }
}
```

### Invalid response — `400 Bad Request`

```json
{
  "contract_version": "1.0",
  "valid": false,
  "message": "The provider publication payload is invalid.",
  "warnings": [],
  "error": {
    "code": "invalid_provider_publication",
    "details": {}
  }
}
```

## 8.2 `POST /api/provider-publication`

Registers a provider and one or more offerings.

### Required headers in a protected production-style deployment

```http
Authorization: Bearer <trusted-service-token>
X-MDC-Actor-Id: <authenticated-actor-id>
Content-Type: application/json
Accept: application/json
```

### Top-level provider fields

| Field | Required | Notes |
|---|---:|---|
| `contract_version` | No | `1.0` if supplied |
| `provider_id` | Yes | Lower snake_case; pattern `^[a-z0-9]+(?:_[a-z0-9]+)*$` |
| `provider_name` | Yes | Max 255 chars |
| `country` | Yes | Max 120 chars in publication contract |
| `certifications` | No | List of certification evidence objects |
| `offerings` | Yes | Non-empty list |
| `publication_metadata` | No | Evidence metadata; defaults to provider-confirmed/declared |
| `custom_provider_fields` | No | JSON object for bounded non-controlled facts |

### Offering fields

Required:

- `service_category`
- `offering_name`
- `part_family`
- `support_status`

Optional/defaulted:

- `supported_part_types`
- `family_capabilities`
- `part_type_capabilities`
- `generic_capabilities`
- `custom_offering_fields`
- `custom_capability_fields`

One publication cannot contain two offerings with the same `service_category`.

### Support status values

- `confirmed`
- `candidate_requiring_confirmation`
- `unknown`

### Evidence metadata

Allowed `source_type` values:

- `provider_confirmed`
- `public_web`
- `curated`
- `not_confirmed`

Allowed `confidence` values:

- `declared`
- `publicly_confirmed`
- `curated`
- `inferred`
- `unknown`

If `source_type` is `not_confirmed`, confidence must be `unknown`, and vice versa.

### Supported part-type record

Every supplied part-type item requires:

```json
{
  "part_type": "spur_gear",
  "support_status": "confirmed",
  "source_type": "provider_confirmed",
  "confidence": "declared"
}
```

The part type must belong to the offering's selected family. Part-type capability data can only be published for a part type whose support status is `confirmed`.

### Provider material capability record

```json
{
  "material": "alloyed_carburizing_steel",
  "available_grades": ["18CrNiMo7-6", "16MnCr5", "20MnCr5"],
  "source_type": "provider_confirmed",
  "confidence": "declared"
}
```

Material grade strings are provider-side evidence; they are not a consumer search vocabulary in v1.

### Process capability record

```json
{
  "process": "hobbing",
  "delivery_mode": "in_house",
  "source_type": "provider_confirmed",
  "confidence": "declared"
}
```

Allowed `delivery_mode` values are `in_house`, `subcontracted`, and `unspecified`.

### Provider-side quality standards

For provider capability validation, the current allowed named standards are:

- `AGMA`
- `DIN`
- `ISO`

### Complete representative publication

```json
{
  "contract_version": "1.0",
  "provider_id": "demo_precision_gears",
  "provider_name": "Demo Precision Gears Oy",
  "country": "Finland",
  "certifications": [
    {
      "code": "ISO9001_2015",
      "source_type": "provider_confirmed",
      "confidence": "declared"
    }
  ],
  "publication_metadata": {
    "source_type": "provider_confirmed",
    "confidence": "declared"
  },
  "custom_provider_fields": {
    "website": "https://example.invalid"
  },
  "offerings": [
    {
      "service_category": "precision_gears",
      "offering_name": "Precision gear manufacturing",
      "part_family": "gear",
      "support_status": "confirmed",
      "supported_part_types": [
        {
          "part_type": "spur_gear",
          "support_status": "confirmed",
          "source_type": "provider_confirmed",
          "confidence": "declared"
        }
      ],
      "family_capabilities": {
        "module": {
          "min": 0.5,
          "max": 6,
          "source_type": "provider_confirmed",
          "confidence": "declared"
        },
        "outside_diameter_mm": {
          "min": 20,
          "max": 300,
          "source_type": "provider_confirmed",
          "confidence": "declared"
        }
      },
      "part_type_capabilities": {
        "spur_gear": {
          "face_width_mm": {
            "min": 5,
            "max": 80,
            "source_type": "provider_confirmed",
            "confidence": "declared"
          }
        }
      },
      "generic_capabilities": {
        "materials": [
          {
            "material": "alloyed_carburizing_steel",
            "available_grades": ["18CrNiMo7-6", "16MnCr5"],
            "source_type": "provider_confirmed",
            "confidence": "declared"
          }
        ],
        "processes": [
          {
            "process": "hobbing",
            "delivery_mode": "in_house",
            "source_type": "provider_confirmed",
            "confidence": "declared"
          }
        ],
        "batch_size": {
          "min": 10,
          "max": 1000,
          "source_type": "provider_confirmed",
          "confidence": "declared"
        },
        "lead_time_weeks": {
          "min": 4,
          "max": 10,
          "source_type": "provider_confirmed",
          "confidence": "declared"
        },
        "weight_kg": {
          "max": 100,
          "source_type": "provider_confirmed",
          "confidence": "declared"
        }
      },
      "custom_offering_fields": {},
      "custom_capability_fields": {}
    }
  ]
}
```

`offering_id` must not be supplied. MDC owns it and generates:

```text
<provider_id>_<service_category>
```

For the example above:

```text
demo_precision_gears_precision_gears
```

### Registration response — `201 Created`

```json
{
  "contract_version": "1.0",
  "status": "accepted",
  "operation": "create",
  "provider_id": "demo_precision_gears",
  "publication_id": "<uuid>",
  "publication_status": "sync_pending",
  "sync_status": "pending",
  "offering_ids": [
    "demo_precision_gears_precision_gears"
  ]
}
```

The response also carries a strong provider `ETag` header.

## 8.3 Server-owned and forbidden fields

Publication requests reject externally owned identifiers including:

- `offering_id`
- `facility_id`
- `material_id`
- `grade_id`

`display_name` is also rejected; use `provider_name`.

Credential-bearing key names such as `api_key`, `access_token`, `credential`, `credentials`, `database_url`, `password`, `private_key`, `refresh_token`, `secret`, and `token` are recursively rejected in publication JSON.

Route/operation-sequence fields listed in Section 5 are also rejected.

---

# 9. Provider and offering read/update contracts

## 9.1 `GET /api/providers/{provider_id}`

Requires lifecycle authentication when enabled.

### Response — `200 OK`

```json
{
  "contract_version": "1.0",
  "provider_id": "demo_precision_gears",
  "provider_name": "Demo Precision Gears Oy",
  "country": "Finland",
  "status": "active",
  "custom_provider_fields": {},
  "publication_metadata": {
    "source_type": "provider_confirmed",
    "confidence": "declared"
  },
  "certifications": [],
  "offerings": [
    {
      "offering_id": "demo_precision_gears_precision_gears",
      "offering_name": "Precision gear manufacturing",
      "service_category": "precision_gears",
      "part_family": "gear",
      "support_status": "confirmed",
      "is_active": true
    }
  ]
}
```

HTTP response header:

```http
ETag: "<strong-revision-value>"
```

Provider status values are:

- `draft`
- `active`
- `suspended`
- `archived`

## 9.2 `PATCH /api/providers/{provider_id}`

Editable fields:

- `provider_name`
- `country`
- `status`
- `certifications`
- `publication_metadata`
- `custom_provider_fields`

At least one editable field is required. Unknown fields and server-owned identifiers are rejected.

Example:

```json
{
  "contract_version": "1.0",
  "provider_name": "Demo Precision Gears Oy — updated",
  "custom_provider_fields": {
    "reviewed": true
  }
}
```

Required protected-write headers normally include bearer auth, `X-MDC-Actor-Id`, and the current `If-Match` value.

A successful PATCH returns the accepted lifecycle-write envelope and a new provider ETag.

## 9.3 `GET /api/providers/{provider_id}/offerings`

Response:

```json
{
  "contract_version": "1.0",
  "provider_id": "demo_precision_gears",
  "offerings": [
    {
      "offering_id": "demo_precision_gears_precision_gears",
      "offering_name": "Precision gear manufacturing",
      "service_category": "precision_gears",
      "part_family": "gear",
      "support_status": "confirmed",
      "is_active": true,
      "provider_id": "demo_precision_gears",
      "supported_part_types": [],
      "family_capabilities": {},
      "part_type_capabilities": {},
      "generic_capabilities": {},
      "custom_offering_fields": {},
      "custom_capability_fields": {}
    }
  ]
}
```

The collection list does not expose an individual ETag per item. Fetch a specific offering before an ETag-protected offering PATCH.

## 9.4 `POST /api/providers/{provider_id}/offerings`

Creates one complete offering for an existing provider.

Required fields:

- `service_category`
- `offering_name`
- `part_family`
- `support_status`

Optional fields use the same controlled offering rules as publication.

Example:

```json
{
  "contract_version": "1.0",
  "service_category": "precision_shafts",
  "offering_name": "Precision shaft manufacturing",
  "part_family": "shaft",
  "support_status": "confirmed",
  "supported_part_types": [
    {
      "part_type": "plain_shaft",
      "support_status": "confirmed",
      "source_type": "provider_confirmed",
      "confidence": "declared"
    }
  ],
  "family_capabilities": {
    "length_mm": {
      "max": 500,
      "source_type": "provider_confirmed",
      "confidence": "declared"
    },
    "outer_diameter_mm": {
      "min": 10,
      "max": 150,
      "source_type": "provider_confirmed",
      "confidence": "declared"
    }
  },
  "part_type_capabilities": {
    "plain_shaft": {
      "principal_diameter_mm": {
        "min": 10,
        "max": 150,
        "source_type": "provider_confirmed",
        "confidence": "declared"
      }
    }
  },
  "generic_capabilities": {},
  "custom_offering_fields": {},
  "custom_capability_fields": {}
}
```

The offering ID is generated by MDC from provider ID + service category. A duplicate generated ID returns `409 offering_already_exists`.

A successful create returns `201`, the accepted lifecycle-write envelope, `offering_id`, and an offering ETag header.

## 9.5 `GET /api/offerings/{offering_id}`

Returns the full lifecycle offering representation, including:

- identity/name/category/family/support status;
- `is_active`;
- provider ID;
- supported part types;
- family capabilities;
- part-type capabilities;
- generic capabilities;
- custom offering fields;
- custom capability fields.

The response includes the current strong `ETag` header.

## 9.6 `PATCH /api/offerings/{offering_id}`

Editable fields:

- `offering_name`
- `support_status`
- `supported_part_types`
- `family_capabilities`
- `part_type_capabilities`
- `generic_capabilities`
- `custom_offering_fields`
- `custom_capability_fields`
- `is_active`

At least one field is required. The resulting complete offering is revalidated against the harmonized contract before persistence.

Example:

```json
{
  "contract_version": "1.0",
  "offering_name": "Precision shaft manufacturing — reviewed",
  "is_active": true
}
```

A successful PATCH returns `200`, the accepted lifecycle-write envelope, and a new offering ETag.

---

# 10. Authentication, actor attribution, and ETag concurrency

## 10.1 Bearer authentication

When lifecycle authentication is enabled:

```http
Authorization: Bearer <MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN>
```

Missing/invalid authentication returns:

```json
{
  "contract_version": "1.0",
  "error": {
    "code": "trusted_lifecycle_auth_required",
    "message": "Trusted provider lifecycle authentication is required."
  }
}
```

HTTP `401`, with:

```http
WWW-Authenticate: Bearer
```

If authentication is required but the server has no configured token, the safe response is `503 trusted_lifecycle_auth_unavailable`.

## 10.2 Actor attribution

For writes when actor attribution is enabled:

```http
X-MDC-Actor-Id: marketplace-user-or-service-id
```

The value must be non-empty, at most 255 characters, and contain no control characters.

Missing required actor attribution returns `400 actor_attribution_required`.

## 10.3 ETags

Provider and individual offering reads return strong quoted ETags:

```http
ETag: "..."
```

For PATCH, send the exact current ETag:

```http
If-Match: "..."
```

The current Vercel pilot also accepts the temporary transport-compatibility header:

```http
X-MDC-If-Match: "..."
```

`If-Match` is the canonical contract. Do not send both headers with different values.

Valid lifecycle ETags must be one strong quoted value. Weak ETags (`W/`), wildcard `*`, comma-separated lists, malformed/unquoted values, and conflicting headers are rejected.

### Concurrency outcomes

| HTTP | Code | Meaning |
|---:|---|---|
| `428` | `concurrency_precondition_required` | Update requires an ETag precondition |
| `400` | `invalid_concurrency_precondition` | ETag syntax invalid or headers conflict |
| `412` | `provider_precondition_failed` | Provider has changed since the client read it |
| `412` | `offering_precondition_failed` | Offering has changed since the client read it |

After a successful PATCH, store the new ETag before another update.

---

# 11. Error contract and HTTP status codes

## 11.1 Standard public/lifecycle error envelope

Most canonical errors use:

```json
{
  "contract_version": "1.0",
  "error": {
    "code": "error_code",
    "message": "Human-readable message",
    "details": {}
  }
}
```

`details` is included only when relevant.

## 11.2 Important error codes

| HTTP | Code | Meaning |
|---:|---|---|
| `400` | `unsupported_contract_version` | Submitted contract version is not supported |
| `400` | `invalid_service_discovery_request` | Search payload failed strict validation |
| `503` | `service_discovery_search_unavailable` | Runtime search backend unavailable |
| `401` | `trusted_lifecycle_auth_required` | Bearer service authentication required/invalid |
| `503` | `trusted_lifecycle_auth_unavailable` | Server requires lifecycle auth but token configuration unavailable |
| `400` | `invalid_actor_attribution` | Actor header malformed |
| `400` | `actor_attribution_required` | Actor header required for write |
| `403` | `provider_validation_disabled` | Validation feature disabled |
| `403` | `provider_publication_disabled` | Lifecycle writes disabled |
| `400` | `invalid_provider_publication` | Registration/publication payload invalid |
| `400` | `invalid_provider_update` | Provider PATCH invalid |
| `400` | `invalid_offering` | Offering-create payload invalid |
| `400` | `invalid_offering_update` | Offering PATCH invalid |
| `404` | `provider_not_found` | Provider ID does not exist |
| `404` | `offering_not_found` | Offering ID does not exist |
| `409` | `provider_already_exists` | Duplicate provider registration |
| `409` | `offering_already_exists` | Generated offering ID already exists |
| `428` | `concurrency_precondition_required` | PATCH requires current ETag |
| `400` | `invalid_concurrency_precondition` | Invalid or conflicting ETag precondition |
| `412` | `provider_precondition_failed` | Provider ETag stale |
| `412` | `offering_precondition_failed` | Offering ETag stale |
| `503` | `provider_lifecycle_write_unavailable` | Safe boundary for unexpected persistence failure |

DRF may also return normal HTTP `405 Method Not Allowed` when a route is called with an unsupported method.

---

# 12. Demo-only API

These routes exist only to support the demonstration frontend and are not partner/Marketplace contract endpoints.

| Method | Path | Current purpose |
|---|---|---|
| `GET` | `/api/demo/health` | Demo namespace availability |
| `GET` | `/api/demo/service-discovery/backend-status` | Demo-reported/static backend metadata |
| `GET` | `/api/demo/service-discovery/fuseki-smoke-test` | Reserved smoke-test; currently reports `not_implemented` with HTTP 200 |
| `POST` | `/api/demo/service-discovery/regenerate-rdf` | Reserved; currently `501 not_implemented`, no mutation |
| `POST` | `/api/demo/service-discovery/reload-fuseki` | Reserved; currently `501 not_implemented`, no mutation |
| `GET` | `/api/demo/provider-publication/state` | Demo JSON provider state |
| `POST` | `/api/demo/provider-publication/preview` | Preview demo provider payload |
| `POST` | `/api/demo/provider-publication/simulate-update` | Save/update demo JSON state |

When the demo API is disabled and Django is not in debug mode, these routes return `404`.

Important: demo provider state is not PostgreSQL lifecycle state, and demo save does not replace trusted provider publication.

---

# 13. Legacy and unsupported routes

## 13.1 Retained legacy route

```text
POST /api/catalog/search
```

This is retained historical/legacy behavior and is **not** the current integration target. It uses an older request/response model.

New consumers must use:

```text
POST /api/service-discovery/search
```

## 13.2 Unsupported versioned routes

These are not current routes:

```text
/api/v1/health
/api/v1/catalog/filters
/api/v1/service-discovery/search
```

Do not give `/api/v1/...` URLs to partners.

## 13.3 No public synchronization endpoint

There is no public HTTP API for:

- rebuilding RDF;
- writing the Fuseki graph;
- consuming the catalogue-sync outbox.

Semantic synchronization is an operator-controlled backend workflow.

---

# 14. cURL/Postman quick-start examples

## 14.1 Suggested Postman environment variables

```text
base_url
lifecycle_token
actor_id
provider_id
provider_etag
offering_id
offering_etag
```

## 14.2 Health

```bash
curl -s "{{base_url}}/api/health"
```

## 14.3 Catalogue filters

```bash
curl -s "{{base_url}}/api/catalog/filters"
```

## 14.4 Public search

```bash
curl -X POST "{{base_url}}/api/service-discovery/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "contract_version": "1.0",
    "request_id": "req-001",
    "consumer_id": "consumer-001",
    "service_category": "precision_gears",
    "part_family": "gear",
    "part_type": "spur_gear",
    "requirements": {},
    "match_policy": {
      "optional_match_mode": "score_only",
      "unknown_policy": "keep_as_unknown",
      "minimum_score": null
    }
  }'
```

## 14.5 Trusted validation

```bash
curl -X POST "{{base_url}}/api/provider-publication/validation" \
  -H "Authorization: Bearer {{lifecycle_token}}" \
  -H "Content-Type: application/json" \
  -d @provider-publication.json
```

## 14.6 Register provider

```bash
curl -X POST "{{base_url}}/api/provider-publication" \
  -H "Authorization: Bearer {{lifecycle_token}}" \
  -H "X-MDC-Actor-Id: {{actor_id}}" \
  -H "Content-Type: application/json" \
  -d @provider-publication.json
```

## 14.7 Read provider and capture ETag

```bash
curl -i "{{base_url}}/api/providers/{{provider_id}}" \
  -H "Authorization: Bearer {{lifecycle_token}}"
```

Store the response `ETag` before PATCH.

## 14.8 Provider PATCH

```bash
curl -X PATCH "{{base_url}}/api/providers/{{provider_id}}" \
  -H "Authorization: Bearer {{lifecycle_token}}" \
  -H "X-MDC-Actor-Id: {{actor_id}}" \
  -H "If-Match: {{provider_etag}}" \
  -H "Content-Type: application/json" \
  -d '{"provider_name":"Updated Provider Name"}'
```

Never put a real lifecycle token in committed scripts, screenshots, shared Postman exports, browser code, or documentation.

---

# 15. CMM integration guidance

## 15.1 Consumer-side integration

A future CMM consumer UI can safely integrate with:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Recommended flow:

```text
CMM browser
   -> GET /api/catalog/filters
   -> render current controlled form
   -> POST /api/service-discovery/search
   -> display provider candidates + matched/unmatched/unknown evidence
```

## 15.2 Provider-side integration

Trusted lifecycle credentials must remain server-side:

```text
Provider user
   -> CMM browser
   -> CMM backend / BFF
      -> Authorization: Bearer <trusted service token>
      -> X-MDC-Actor-Id: <authenticated user/service>
      -> ETag / If-Match handling
      -> MDC lifecycle API
```

The browser must not hold `MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN`.

## 15.3 Provider publication flow

```text
CMM provider form
   -> server-side validation/mapping
   -> POST /api/provider-publication/validation
   -> user confirms
   -> POST /api/provider-publication
   -> PostgreSQL transaction
   -> publication + outbox pending
   -> trusted operator synchronization
   -> RDF/Fuseki projection
   -> discoverable through public search
```

---

# 16. Security and operational boundaries

- Public search/filter/health endpoints do not require lifecycle credentials.
- Trusted provider lifecycle is a separate authenticated surface.
- Production settings default trusted authentication, actor attribution on writes, and ETag concurrency on updates to enabled.
- Provider validation/publication are feature-gated independently.
- Demo routes are feature-gated and should remain disabled on normal production unless deliberately required.
- PostgreSQL is the lifecycle source of truth.
- RDF/Fuseki is a derived semantic/search layer.
- Catalogue synchronization is not a public web action.
- Do not expose database URLs, lifecycle tokens, Django secrets, Fuseki passwords, or private keys.
- Do not use provider custom fields to smuggle credentials or redefine controlled fields.
- Do not reintroduce route/operation-sequence fields in the current v1 contract.
- Do not infer API behavior from historical Week 1 documents when current routing/serializers differ.

---

# 17. Source-of-truth code map

The following current files define the API described here:

| Concern | Source file |
|---|---|
| Root routing | `backend/config/urls.py` |
| Canonical API routing | `backend/apps/api/urls.py` |
| GET endpoints | `backend/apps/api/views/get_views.py` |
| POST/PATCH endpoints | `backend/apps/api/views/post_views.py` |
| Public response contract/version | `backend/apps/api/public_contract.py` |
| Search request validation | `backend/apps/api/service_discovery_search_serializers.py` |
| Service-discovery registry | `backend/apps/ontology/service_discovery_registry.py` |
| Materials/processes/certifications | `backend/apps/ontology/vocabularies.py` |
| Provider publication validation | `backend/apps/api/service_discovery_publication_serializers.py` |
| Provider/offering PATCH/create serializers | `backend/apps/api/provider_lifecycle_serializers.py` |
| Lifecycle authentication/concurrency | `backend/apps/api/lifecycle_security.py` |
| Lifecycle reads | `backend/apps/providers/provider_lifecycle_repository.py` |
| Lifecycle writes/outbox | `backend/apps/providers/provider_lifecycle_write_service.py` |
| Provider/offering model states | `backend/apps/providers/models.py` |
| Demo API routing | `backend/apps/demo/urls.py` |
| Demo GET behavior | `backend/apps/demo/views/get_views.py` |
| Demo POST behavior | `backend/apps/demo/views/post_views.py` |

For deeper implementation, operational, Postman, synchronization, and deployment guidance, read:

```text
mdc-catalog/docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md
```

For browser/demo behavior, read:

```text
mdc-catalog/docs/Demo_Frontend/MDC_Demo_Frontend_Comprehensive_Implementation_Report_and_User_Manual.md
```

---

## Final integration summary

For most external consumers, the MDC API is intentionally small:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

For trusted provider onboarding and maintenance, use the separately authenticated lifecycle surface. Keep lifecycle credentials and ETag handling in a server-side integration layer, not in the browser.
