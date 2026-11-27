# MaaSAI MaaS Dynamic Catalogue API

**Component name:** MaaS Dynamic Catalogue (MDC)  
**Partner-facing API document revision:** 1.2.0\
**API contract version:** `1.0`  
**Authored by:** TAU  
**Current pilot production base URL:** `https://maasai-mdc-v1.vercel.app`

---

## Changelog

| Date | Revision | Change |
|---|---:|---|
| 2026-08-31 | 1.0.0 | Initial partner-facing API document |
| 2026-09-09 | 1.1.0 | Aligned documentation with the verified M6.1 production contract: stable `/api/...` routes, `contract_version`, public response shaping, and current three-endpoint partner scope |
| 2026-11-27 | 1.2.0 | Recorded the temporary Marketplace release with all 13 canonical operations, strict eligibility and automatic synchronization |

---

# 1. Purpose

The MaaS Dynamic Catalogue (MDC) provides the Cloud MaaS Marketplace and other MaaSAI components with a structured interface for discovering manufacturing/service offerings.

The partner API covers health, controlled catalogue filters, strict service discovery, and provider and offering lifecycle operations. The stable URL currently serves the approved validation catalogue for temporary Marketplace integration and demonstration use.

---

# 2. Base URL and API Versioning

## 2.1 Production base URL

```text
https://maasai-mdc-v1.vercel.app
```

All paths in this document are relative to that base URL.

Use **No Auth** for this profile. Send Marketplace server requests without an
MDC bearer token, actor header or Vercel bypass. MaaSAI Keycloak authenticates
Marketplace users. The MDC URL itself is directly callable, so use approved
demo records. [Postman environment](MaaSAI_MDC_Marketplace_Demo.postman_environment.json)

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

For the ten provider and offering lifecycle operations, see the
[endpoint matrix](MaaSAI_MDC_M6_Marketplace_Integration_Guide.md#frozen-endpoint-matrix).

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

Returns the offerings with confirmed support for the requested service category, family and part type that satisfy every supplied technical requirement. The MaaS Recommendation System compares and ranks the eligible offerings.

This is an intentional change from the earlier permissive discovery behavior on the same contract version. A failed requirement, partial coverage of a list or bounding box, or missing or unconfirmed required evidence excludes an offering. Omitted requirements and empty selection lists impose no constraint.

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
| `match_policy` | No | Compatibility policy fields and optional additional score restriction |

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

Use the controlled values from `GET /api/catalog/filters`. Each requested material, process and certification must be supported by the offering or by certification evidence applying to it. The search contract accepts material families. Available grades remain evidence, and `material_grades` as a separate search criterion returns HTTP 400.

## 6.3 Range values

Many dimensional/specification fields use a range-or-exact object:

```json
{"min": 10, "max": 100}
```

or:

```json
{"exact": 50}
```

A request may use one or more of `min`, `max`, and `exact` where valid for the selected field. A dimensional range must cover the requested endpoints, including equality, and every supplied component of a bounding box must match. Generic tolerance and surface finish compare the reported provider maximum with the requested bounds. An `exact` value for these two generic fields acts as an upper limit, as does `max`.

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

## 6.5 Match policy compatibility

The optional `match_policy` object currently supports:

| Field | Accepted values | Effective value |
|---|---|---|
| `optional_match_mode` | `any`, `all`, `score_only` | `all` |
| `unknown_policy` | `keep_as_unknown`, `reject_unknown` | `reject_unknown` for required evidence |
| `minimum_score` | number from `0` to `1`, or `null` | Optional restriction applied after eligibility, default `null` |

MDC normalizes and applies the strict policy for every accepted caller. Legacy values cannot admit a partial or unknown result.

Example:

```json
{
  "match_policy": {
    "optional_match_mode": "all",
    "unknown_policy": "reject_unknown"
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
| `results` | All eligible offerings in stable provider and offering ID order. Empty when none qualify. |

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
| `unmatched_capabilities` | Compatibility field, empty for eligible offerings |
| `unknown_capabilities` | Compatibility field, empty for eligible offerings |

## 7.3 Match object

```json
{
  "status": "full_match",
  "score": 1.0
}
```

Eligible results carry `full_match` and score `1.0` for compatibility. Ranking is the Recommendation System's responsibility.

## 7.4 Capability comparison objects

A matched capability is represented using fields such as:

```json
{
  "field": "module",
  "requested": {"exact": 2.0},
  "provided": {"min": 0.3, "max": 10.0}
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
| `200` | — | Search completed, with `result_count: 0` and `results: []` when no offering qualifies |
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

Marketplace integrations use the following discovery rules.

1. Load controlled values from `/api/catalog/filters`.
2. Keep `service_category`, `part_family` and `part_type` consistent using the filter relationships.
3. Generate a unique `request_id` for each logical search and submit supported fields for the selected part type.
4. Send the returned eligible offerings to the MaaS Recommendation System for ranking.
5. Treat HTTP 200 with `results: []` as a successful search with zero eligible offerings.
6. Use the canonical unversioned `/api/...` routes.

---

# 11. Provider and Offering Lifecycle

Validate the registration body with `POST /api/provider-publication/validation` before registering through `POST /api/provider-publication`. Use the provider and offering IDs returned by MDC in subsequent detail, list, add, update and delete calls.

Use a current strong `ETag` for PATCH and DELETE. Request detail with `Accept-Encoding: identity` to preserve the strong ETag through Vercel. Send it with `If-Match` or the existing `X-MDC-If-Match` alias. HTTP 428 means the precondition is missing, and HTTP 412 means the revision changed. Reload the resource and review the new state before using a fresh ETag.

Automatic writes are complete when the receipt says `completed / synced / succeeded`. A timeout or HTTP 503 can follow a committed PostgreSQL write. Retain any `publication_id`, read the exact resource and coordinate with the operator before retrying the write. [Lifecycle request examples and recovery](MaaSAI_MDC_M6_Marketplace_Integration_Guide.md)

---

# 12. Current Security and Deployment Notes

The temporary public integration profile uses the validation database and its
isolated Fuseki dataset. Lifecycle validation, conditional writes and automatic
publication are active. Discovery checks the current synchronized Fuseki
revision and returns HTTP 503 if the authoritative catalogue is unavailable.
Demo routes remain disabled. The operator retains the internal Graph Store
credentials and handles synchronization recovery.

---

# 13. Production Verification Status

Task 15 verified all 13 canonical operations on the staged production build.
After cutover, the stable URL returned canonical JSON for health, filters,
search, exact detail reads and validation. A disposable registration and
cascade deletion both completed automatic synchronization using a clean client.
The Module 4 search returned only `tasowheel_precision_gears` after cleanup.
[Task 15 release evidence](../reports_phase4/15_MDC_Vercel_Production_Release_and_Marketplace_API_Access_Report.md)

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

Catalogue discovery endpoints:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Current API contract version:

```text
1.0
```

The [canonical lifecycle matrix](MaaSAI_MDC_M6_Marketplace_Integration_Guide.md#frozen-endpoint-matrix) covers provider validation and publication, exact provider and offering reads, updates and deletion.
