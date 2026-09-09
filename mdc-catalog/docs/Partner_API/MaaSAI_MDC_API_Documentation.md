# MaaSAI MaaS Dynamic Catalogue API

**Component name:** MaaS Dynamic Catalogue (MDC)  
**Partner-facing API document revision:** 1.1.0  
**API contract version:** `1.0`  
**Authored by:** TAU  
**Current pilot production base URL:** `https://maasai-mdc-v1.vercel.app`

---

## Changelog

| Date | Revision | Change |
|---|---:|---|
| 2026-08-31 | 1.0.0 | Initial partner-facing API document |
| 2026-09-09 | 1.1.0 | Aligned documentation with the verified M6.1 production contract: stable `/api/...` routes, `contract_version`, public response shaping, and current three-endpoint partner scope |

---

# 1. Purpose

The MaaS Dynamic Catalogue (MDC) provides the Cloud MaaS Marketplace and other MaaSAI components with a structured interface for discovering manufacturing/service offerings.

The current partner-facing API supports three functions:

1. check whether the MDC API is available;
2. retrieve controlled catalogue/filter values for Marketplace forms;
3. submit a structured service-discovery request and receive matching provider offerings.

The current public API is intentionally limited to these three endpoints while provider registration, provider publication, provider update, and provider/offering retrieval are moved to a durable PostgreSQL-backed lifecycle in the next development phase.

---

# 2. Base URL and API Versioning

## 2.1 Production base URL

```text
https://maasai-mdc-v1.vercel.app
```

All paths in this document are relative to that base URL.

## 2.2 Stable URL strategy

MDC does **not** use URL version prefixes such as:

```text
/api/v1/...
/api/v2/...
```

The stable partner-facing routes are under:

```text
/api/...
```

API contract evolution is represented by the response/request metadata field:

```json
"contract_version": "1.0"
```

For service discovery, `contract_version` may be omitted in the request; when omitted, the current baseline contract `1.0` is used.

The previously documented `/api/v1/...` routes are not part of the current API and return `404`.

---

# 3. Current Partner-Facing Endpoint Overview

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check MDC API availability |
| `GET` | `/api/catalog/filters` | Retrieve controlled values used by Marketplace forms and request validation |
| `POST` | `/api/service-discovery/search` | Submit a structured manufacturing/service request and receive matching provider offerings |

These are the only endpoints that should currently be used for new Marketplace/partner integration.

---

# 4. Health Check

## `GET /api/health`

### Purpose

Checks whether the MDC Django API is running and reachable.

### Request

No request body is required.

### Success response

**HTTP `200 OK`**

```json
{
  "contract_version": "1.0",
  "status": "ok",
  "service": "maasai-mdc"
}
```

### Response parameters

| Name | In | Description |
|---|---|---|
| `contract_version` | body | Current partner-facing API contract version |
| `status` | body | API availability status |
| `service` | body | MDC service identifier |

### Example

```bash
curl https://maasai-mdc-v1.vercel.app/api/health
```

---

# 5. Catalogue Filters

## `GET /api/catalog/filters`

### Purpose

Returns the controlled values used by the Marketplace for dropdowns, checkboxes, dependent selections, and request validation.

The response is based on the current harmonized service-discovery registry and controlled vocabularies.

### Request

No request body is required.

### Response parameters

| Name | In | Description |
|---|---|---|
| `contract_version` | body | Current API contract version |
| `service_categories` | body | Available service categories, e.g. precision gear manufacturing |
| `part_families` | body | Main categories of parts, e.g. gear, shaft, metal part |
| `part_types` | body | Specific part types grouped by part family |
| `materials` | body | Controlled material values accepted by service-discovery search |
| `processes` | body | Controlled manufacturing-process values accepted by search |
| `certifications` | body | Controlled certification values accepted by search |

### Relationship between selections

The response preserves the relationship:

```text
service_category
      ↓
part_family
      ↓
part_type
```

For example:

```text
precision_gears
      ↓
gear
      ↓
spur_gear / helical_gear / bevel_gear / ...
```

The Marketplace should use these relationships when rendering dependent form fields.

### Representative response

```json
{
  "contract_version": "1.0",
  "service_categories": [
    {
      "value": "precision_gears",
      "label": "Precision gears",
      "part_family": "gear"
    },
    {
      "value": "precision_shafts",
      "label": "Precision shafts",
      "part_family": "shaft"
    },
    {
      "value": "precision_metal_parts",
      "label": "Precision metal parts",
      "part_family": "metal_part"
    }
  ],
  "part_families": [
    {
      "value": "gear",
      "label": "Gear",
      "service_category": "precision_gears"
    },
    {
      "value": "shaft",
      "label": "Shaft",
      "service_category": "precision_shafts"
    },
    {
      "value": "metal_part",
      "label": "Metal part",
      "service_category": "precision_metal_parts"
    }
  ],
  "part_types": {
    "gear": [
      {"value": "spur_gear", "label": "Spur gear"},
      {"value": "helical_gear", "label": "Helical gear"}
    ],
    "shaft": [
      {"value": "plain_shaft", "label": "Plain shaft"},
      {"value": "stepped_shaft", "label": "Stepped shaft"}
    ],
    "metal_part": [
      {"value": "block", "label": "Block"},
      {"value": "plate", "label": "Plate"}
    ]
  },
  "materials": [
    {"value": "steel", "label": "Steel"}
  ],
  "processes": [
    {"value": "machining", "label": "Machining"},
    {"value": "milling", "label": "Milling"}
  ],
  "certifications": [
    {"value": "ISO9001_2015", "label": "ISO 9001:2015"}
  ]
}
```

The payload above is shortened for documentation. Integrations should obtain the current complete controlled values directly from the endpoint rather than hard-coding the example values.

### Example

```bash
curl https://maasai-mdc-v1.vercel.app/api/catalog/filters
```

---

# 6. Service Discovery

## `POST /api/service-discovery/search`

### Purpose

Receives a structured service request from a MaaS Consumer/Marketplace and returns provider offerings that satisfy or partially satisfy the request according to the MDC matching policy.

### Content type

```text
Content-Type: application/json
```

## 6.1 Top-level request parameters

| Name | Required | Description |
|---|---:|---|
| `contract_version` | No | API contract version. Current supported value is `1.0`; omitted requests default to `1.0` |
| `request_id` | Yes | Unique identifier for the Marketplace request |
| `consumer_id` | Yes | Identifier of the requesting MaaS Consumer/Marketplace actor |
| `service_category` | Yes | Requested service category |
| `part_family` | Yes | Requested part family; must be consistent with `service_category` |
| `part_type` | Yes | Requested part type; must belong to the selected `part_family` |
| `requirements` | No | Structured part/manufacturing requirements |
| `match_policy` | No | Optional matching-policy controls |

## 6.2 Requirements structure

When supplied, `requirements` is divided into three groups:

```json
{
  "part_family_specifications": {},
  "part_type_specifications": {},
  "generic_requirements": {}
}
```

### `part_family_specifications`

Contains fields common to the selected part family.

Examples include gear dimensions/quality, shaft dimensions, or the bounding box for prismatic metal parts.

### `part_type_specifications`

Contains fields specific to the selected `part_type`.

Examples include `number_of_holes` for a block/plate or `face_width_mm` for some gear types.

### `generic_requirements`

May contain currently supported generic criteria such as:

```text
materials
processes
batch_size
delivery
certifications
surface_finish_ra_um
tolerance_mm
quality
weight_kg
```

Controlled values such as materials, processes, and certifications should be obtained from `GET /api/catalog/filters`.

## 6.3 Range values

Many dimensional/specification fields use a range-or-exact object:

```json
{"min": 10, "max": 100}
```

or:

```json
{"exact": 50}
```

A request may use one or more of `min`, `max`, and `exact` where valid for the selected field.

## 6.4 Representative metal-part request

```json
{
  "contract_version": "1.0",
  "request_id": "req_001",
  "consumer_id": "consumer_001",
  "service_category": "precision_metal_parts",
  "part_family": "metal_part",
  "part_type": "block",
  "requirements": {
    "part_family_specifications": {
      "bounding_box_mm": {
        "length_mm": {"max": 150},
        "width_mm": {"max": 80},
        "height_mm": {"max": 20}
      }
    },
    "part_type_specifications": {
      "number_of_holes": {"max": 4}
    },
    "generic_requirements": {
      "materials": ["steel"],
      "processes": ["machining"],
      "certifications": ["ISO9001_2015"],
      "weight_kg": 2.5,
      "tolerance_mm": {"max": 0.05},
      "surface_finish_ra_um": {"max": 1.6}
    }
  }
}
```

`requirements` may be empty when the Marketplace only wants to discover providers supporting the selected service category / part family / part type.

## 6.5 Optional match policy

The optional `match_policy` object currently supports:

| Field | Accepted values | Default |
|---|---|---|
| `optional_match_mode` | `any`, `all`, `score_only` | `any` |
| `unknown_policy` | `keep_as_unknown`, `reject_unknown` | `keep_as_unknown` |
| `minimum_score` | number from `0` to `1`, or `null` | `null` |

Example:

```json
{
  "match_policy": {
    "optional_match_mode": "any",
    "unknown_policy": "keep_as_unknown",
    "minimum_score": null
  }
}
```

---

# 7. Service-Discovery Response

## 7.1 Top-level response parameters

| Name | Description |
|---|---|
| `contract_version` | Applied API contract version |
| `request_id` | Request identifier supplied by Marketplace |
| `service_category` | Requested service category |
| `part_family` | Requested part family |
| `part_type` | Requested part type |
| `result_count` | Number of provider offerings returned |
| `results` | Matching/partially matching provider offerings |

## 7.2 Result object

Each result contains:

| Name | Description |
|---|---|
| `provider_id` | MDC provider identifier |
| `provider_name` | Provider display/legal name used by the catalogue |
| `offering_id` | Unique offering identifier |
| `offering_name` | Provider offering name |
| `service_category` | Service category of the returned offering |
| `part_family` | Part family of the returned offering |
| `match` | Match status and score |
| `matched_capabilities` | Requested manufacturing requirements that the offering satisfies |
| `unmatched_capabilities` | Requested requirements known not to be satisfied |
| `unknown_capabilities` | Requested requirements for which the catalogue does not have sufficient confirmed evidence |

## 7.3 Match object

```json
{
  "status": "full_match",
  "score": 1.0
}
```

The exact status and score depend on the request and current catalogue data.

## 7.4 Capability comparison objects

A matched capability is represented using fields such as:

```json
{
  "field": "module",
  "requested": {"exact": 2.0},
  "provided": {"min": 0.3, "max": 10.0}
}
```

An unmatched or unknown capability can additionally include a `reason`:

```json
{
  "field": "surface_finish_ra_um",
  "requested": {"max": 1.6},
  "reason": "No confirmed value is available for this requirement."
}
```

The exact `requested` and `provided` structures depend on the capability type.

## 7.5 Representative response shape

```json
{
  "contract_version": "1.0",
  "request_id": "req_001",
  "service_category": "precision_metal_parts",
  "part_family": "metal_part",
  "part_type": "block",
  "result_count": 1,
  "results": [
    {
      "provider_id": "demo_metal_works",
      "provider_name": "Demo Metal Works Oy",
      "offering_id": "demo_metal_works_precision_metal_parts",
      "offering_name": "Precision metal-part manufacturing",
      "service_category": "precision_metal_parts",
      "part_family": "metal_part",
      "match": {
        "status": "full_match",
        "score": 1.0
      },
      "matched_capabilities": [
        {
          "field": "materials",
          "requested": ["steel"],
          "provided": ["steel"]
        }
      ],
      "unmatched_capabilities": [],
      "unknown_capabilities": []
    }
  ]
}
```

This is a representative shape, not a promise of these exact provider values for every request. The live response depends on current catalogue data and matching results.

### Selection fields and capabilities

`service_category`, `part_family`, and `part_type` are used internally by MDC to select relevant offerings. They are returned as selection metadata but are not repeated inside the capability arrays.

The capability arrays are reserved for manufacturing/service requirements such as dimensions, material, process, quality, batch size, delivery, tolerance, surface finish, and similar requested criteria.

---

# 8. Service-Discovery Error Responses

Public API errors use the current contract metadata plus an `error` object.

General shape:

```json
{
  "contract_version": "1.0",
  "error": {
    "code": "invalid_service_discovery_request",
    "message": "Invalid service-discovery search request.",
    "details": {}
  }
}
```

## Current relevant status codes

| HTTP status | Error code | Meaning |
|---:|---|---|
| `200` | — | Search completed successfully |
| `400` | `invalid_service_discovery_request` | Request fields, controlled values, selection relationships, or requirement structure are invalid |
| `400` | `unsupported_contract_version` | An unsupported explicit `contract_version` was submitted |
| `503` | `service_discovery_search_unavailable` | No configured service-discovery backend could complete the search |

The public `503` response deliberately does not expose backend implementation/fallback details.

---

# 9. Example Service-Discovery Call

```bash
curl -X POST https://maasai-mdc-v1.vercel.app/api/service-discovery/search \
  -H "Content-Type: application/json" \
  -d '{
    "contract_version": "1.0",
    "request_id": "req_001",
    "consumer_id": "consumer_001",
    "service_category": "precision_gears",
    "part_family": "gear",
    "part_type": "spur_gear",
    "requirements": {}
  }'
```

---

# 10. Integration Guidance

Marketplace integrations should:

1. call `/api/catalog/filters` rather than hard-code controlled values;
2. keep `service_category`, `part_family`, and `part_type` mutually consistent using the filter relationships;
3. generate a stable unique `request_id` for each logical service-discovery request;
4. submit only supported requirement fields for the selected part type;
5. treat `unknown_capabilities` as missing/insufficient confirmed catalogue information rather than automatically assuming incompatibility;
6. treat `unmatched_capabilities` as known incompatibilities for the corresponding requested criteria;
7. use the returned `match.status` and `match.score` together with capability arrays when presenting results to the user;
8. use `/api/...` routes only and do not call `/api/v1/...`.

---

# 11. Current Scope and Deferred Provider APIs

The current partner-facing contract intentionally does **not** expose provider lifecycle APIs.

The following functions are planned for a later PostgreSQL-backed phase:

- provider registration/publication;
- provider-publication validation;
- provider edit/update;
- provider retrieval/listing;
- offering retrieval/update;
- publication/version history;
- controlled synchronization from PostgreSQL to RDF/Fuseki.

They are deferred because state-changing provider workflows require durable persistence, authorization, version/history management, transactional consistency, and reliable RDF/Fuseki synchronization.

Partners should therefore not integrate against legacy/internal provider routes at this stage.

---

# 12. Current Security and Deployment Notes

The current MDC deployment is a MaaSAI pilot deployment.

Current production safety configuration includes:

```text
/api/demo/*                -> unavailable
/api/provider-publication  -> disabled
```

Authentication/authorization for broader production partner access is a later hardening/integration concern. Integrators should not assume that anonymous access is a permanent production contract.

The current search runtime preserves the harmonized MDC service-discovery stack and may use RDFLib/YAML fallback when an external Fuseki endpoint is not configured. Backend/fallback implementation details are intentionally not exposed in the public search response.

---

# 13. Production Verification Status

The M6.1 contract was verified on Vercel Preview and Production before this document revision.

Verified production behavior:

```text
GET  /api/health                       -> 200
GET  /api/catalog/filters              -> 200
POST /api/service-discovery/search     -> 200

GET  /api/v1/health                    -> 404
GET  /api/v1/catalog/filters           -> 404
POST /api/v1/service-discovery/search  -> 404

GET  /api/demo/health                  -> 404
POST /api/provider-publication         -> 403
```

A verified service-discovery smoke request returned:

```text
contract_version = 1.0
result_count = 2
```

---

# 14. Current Partner API Summary

```text
Cloud MaaS Marketplace
        |
        | GET filters / POST structured request
        v
MaaS Dynamic Catalogue API
        |
        | harmonized service discovery
        v
Provider offering matches
```

Current public endpoints:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Current API contract version:

```text
1.0
```

Provider lifecycle APIs will be added only after the durable PostgreSQL-backed provider lifecycle is implemented and verified.
