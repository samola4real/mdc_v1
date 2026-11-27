# MaaSAI MaaS Dynamic Catalogue — Marketplace API Reference

**Audience:** MaaSAI Marketplace developers  
**API contract version:** 1.0  
**Base URL:** https://maasai-mdc-v1.vercel.app  
**Document purpose:** Complete reference for the Marketplace-facing MDC API

---

## 1. Purpose and scope

The MaaSAI MaaS Dynamic Catalogue (MDC) provides API services for publishing manufacturing providers and their offerings, retrieving the available catalogue values, and discovering offerings that satisfy a consumer's manufacturing requirements.

This reference defines the requests, fields, responses and operating rules required to integrate the Marketplace with MDC.

The API returns technically eligible manufacturing offerings. The MaaS Recommendation System can use those eligible offerings as input for its subsequent comparison and ranking.

## 2. Connection details

### 2.1 Base URL

~~~text
https://maasai-mdc-v1.vercel.app
~~~

All endpoint paths in this document are relative to this base URL.

### 2.2 Authentication

For the supplied Marketplace API URL, no MDC bearer token or Authorization header is required.

The Marketplace remains responsible for authenticating its own users before allowing them to register providers, publish offerings or submit consumer requests.

### 2.3 Request headers

For JSON POST and PATCH requests, send:

~~~http
Content-Type: application/json
Accept: application/json
~~~

GET requests do not require a request body.

### 2.4 API routes and contract version

Use the unversioned routes beginning with **/api/**. Do not prepend **/api/v1/**.

The current contract version is **1.0**. JSON request bodies may include:

~~~json
{
  "contract_version": "1.0"
}
~~~

The field is optional. If omitted, MDC uses contract version 1.0. GET requests do not require it.

---

## 3. Endpoint overview

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/health | Check API availability |
| GET | /api/catalog/filters | Retrieve current catalogue values and relationships |
| POST | /api/provider-publication/validation | Validate a provider publication without registering it |
| POST | /api/provider-publication | Register a provider and its initial offerings |
| GET | /api/providers/{provider_id} | Retrieve provider details and offering summaries |
| PATCH | /api/providers/{provider_id} | Update provider information |
| DELETE | /api/providers/{provider_id} | Delete a provider and its offerings |
| GET | /api/providers/{provider_id}/offerings | List a provider's offerings |
| POST | /api/providers/{provider_id}/offerings | Add an offering to an existing provider |
| GET | /api/offerings/{offering_id} | Retrieve full offering details |
| PATCH | /api/offerings/{offering_id} | Update an offering |
| DELETE | /api/offerings/{offering_id} | Delete one offering |
| POST | /api/service-discovery/search | Find offerings that satisfy a consumer request |

---

## 4. Common data rules

### 4.1 Controlled values

Use **GET /api/catalog/filters** to retrieve current service categories, part families, part types, materials, processes and certifications.

Use the returned value fields in API requests. The labels are intended for display; the values are the identifiers to send to MDC.

The relationship between the main selection fields is:

~~~text
service_category
      |
      v
part_family
      |
      v
part_type
~~~

The selected part family must belong to the selected service category, and the selected part type must belong to that part family.

### 4.2 Provider and offering identifiers

- A provider ID must be unique and use lowercase letters, digits and underscores in lower snake_case format.
- An offering ID must be unique, use lower snake_case and, when supplied, begin with its owning provider ID followed by an underscore.
- Provider and offering IDs are identifiers, not display names.
- Provider and offering IDs cannot be changed through PATCH.
- Multiple offerings may use the same service category. Each offering must have its own offering ID.

For reliable integration, supply an explicit offering ID when registering or adding an offering.

### 4.3 Offering support status

The accepted values are:

| Value | Meaning |
|---|---|
| confirmed | The provider has confirmed that the offering or part type is supported |
| candidate_requiring_confirmation | Support is a candidate and still requires confirmation |
| unknown | Support has not been confirmed |

Set the status according to the provider's actual confirmation. Service discovery requires confirmed support for the requested part type.

### 4.4 Evidence metadata

Capability values may include evidence metadata:

| Field | Accepted values |
|---|---|
| source_type | provider_confirmed, public_web, curated, not_confirmed |
| confidence | declared, publicly_confirmed, curated, inferred, unknown |

For a supported part type, both source_type and confidence are required. For capability records and provider certification records, they may be omitted. If supplied, they must use the accepted values.

Use source_type = not_confirmed together with confidence = unknown.

Provider-level certifications are objects with a required code and optional evidence metadata:

~~~json
{
  "code": "ISO9001_2015",
  "source_type": "provider_confirmed",
  "confidence": "declared"
}
~~~

The code must be one of the current values returned by GET /api/catalog/filters. Duplicate certification codes are not accepted for the same provider.

### 4.5 Unsupported legacy publication fields

The current provider publication contract does not accept the old top-level **description** or **capabilities** fields.

Use the current fields instead:

- Provider information: provider_name, country and custom_provider_fields.
- Family-level capabilities: family_capabilities.
- Part-type capabilities: part_type_capabilities.
- General manufacturing capabilities: generic_capabilities.
- Additional provider-defined information: custom_provider_fields, custom_offering_fields or custom_capability_fields.

Do not send a single capabilities object in place of the three structured capability maps.

### 4.6 Updating and deleting existing records

You only need to use an **ETag** when updating or deleting an existing provider or offering. You do not need an ETag when registering a provider, adding an offering or performing a service-discovery search.

Think of an ETag as a version label that MDC gives to a provider or offering. It helps prevent an update based on old information from accidentally overwriting a more recent change.

**How to use it:**

1. First, send a GET request for the provider or offering you want to change.
2. In the GET response headers, find the value named **ETag**. MDC generates this value; you do not create it.
3. When sending the PATCH or DELETE request, send that same value in the **If-Match** header.

For example, a GET response will contain a header similar to this:

~~~http
ETag: "<value-generated-by-MDC>"
~~~

The quotation marks are part of the value returned by MDC. Copy the complete value exactly as it appears. You do not need to type a value or add quotation marks yourself.

In Postman, save the returned value in an environment variable and use it like this:

~~~http
If-Match: {{provider_etag}}
~~~

For an offering, use:

~~~http
If-Match: {{offering_etag}}
~~~

**Which operations need it?**

- **PATCH:** Always send the latest ETag. Some deployments may enforce this check; sending it consistently also protects against overwriting a change made by another user.
- **DELETE:** The latest ETag is required.

If another user changes the provider or offering after you retrieve it, MDC returns HTTP **412**. Retrieve the record again, review the latest information and retry with the new ETag. If a required ETag is missing, MDC returns HTTP **428**.

| HTTP status | Meaning |
|---:|---|
| 400 | Invalid request or incorrectly formatted ETag |
| 404 | Provider or offering not found |
| 409 | Provider or offering ID already exists |
| 412 | The record changed after you retrieved it; GET it again |
| 428 | A required If-Match header was not supplied |
| 503 | The operation or catalogue publication could not be confirmed |

PATCH changes only the scalar fields supplied. A supplied object/map field is a whole-map replacement: include every entry that must remain. Do not send only one nested map member if other existing members must be preserved.

---

## 5. Health check

### GET /api/health

Checks whether the MDC API is available.

**Request body:** None.

**Successful response — HTTP 200**

~~~json
{
  "contract_version": "1.0",
  "status": "ok",
  "service": "maasai-mdc"
}
~~~

Example:

~~~bash
curl --request GET "https://maasai-mdc-v1.vercel.app/api/health"
~~~

---

## 6. Catalogue filters

### GET /api/catalog/filters

Returns the current controlled values used when creating provider offerings and consumer search requests.

**Request body:** None.

The response contains:

| Field | Description |
|---|---|
| contract_version | API contract version |
| service_categories | Service categories and their associated part families |
| part_families | Part families and their associated service categories |
| part_types | Part types grouped by part family |
| materials | Accepted material values |
| processes | Accepted manufacturing-process values |
| certifications | Accepted certification values |

Representative response:

~~~json
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
      {"value": "helical_gear", "label": "Helical gear"},
      {"value": "bevel_gear", "label": "Bevel gear"},
      {"value": "worm_gear", "label": "Worm gear"},
      {"value": "crown_gear", "label": "Crown gear"}
    ],
    "shaft": [
      {"value": "plain_shaft", "label": "Plain shaft"},
      {"value": "stepped_shaft", "label": "Stepped shaft"},
      {"value": "splined_shaft", "label": "Splined shaft"},
      {"value": "worm_shaft", "label": "Worm shaft"},
      {"value": "hollow_shaft", "label": "Hollow shaft"}
    ],
    "metal_part": [
      {"value": "block", "label": "Block"},
      {"value": "plate", "label": "Plate"},
      {"value": "bracket", "label": "Bracket"},
      {"value": "bushing", "label": "Bushing"},
      {"value": "roller", "label": "Roller"},
      {"value": "collar", "label": "Collar"}
    ]
  },
  "materials": [
    {"value": "steel", "label": "Steel"}
  ],
  "processes": [
    {"value": "machining", "label": "Machining"}
  ],
  "certifications": [
    {"value": "ISO9001_2015", "label": "ISO 9001:2015"}
  ]
}
~~~

The response above is shortened to illustrate the structure. The live endpoint returns the current complete values. Retrieve it when the Marketplace starts and refresh it when needed; do not rely on this shortened example as the complete vocabulary.

Example:

~~~bash
curl --request GET "https://maasai-mdc-v1.vercel.app/api/catalog/filters"
~~~

---

## 7. Provider validation and registration

### 7.1 Validate a provider publication

**POST /api/provider-publication/validation**

Validates and normalizes a provider publication payload without registering the provider.

Set the request body to **Body → raw → JSON** in Postman. Paste the complete payload below. This is the same payload you will use for the registration request in Section 7.2. Use a new provider_id and matching offering_id if you have already registered this test provider.

**Request headers:**

~~~http
Content-Type: application/json
Accept: application/json
~~~

**Request body (copy into Postman):**

~~~json
{
  "contract_version": "1.0",
  "provider_id": "marketplace_api_test_20261127_01",
  "provider_name": "Marketplace API Test Works",
  "country": "Finland",
  "certifications": [],
  "offerings": [
    {
      "offering_id": "marketplace_api_test_20261127_01_block_cell",
      "service_category": "precision_metal_parts",
      "offering_name": "Precision block manufacturing",
      "part_family": "metal_part",
      "support_status": "confirmed",
      "supported_part_types": [
        {
          "part_type": "block",
          "support_status": "confirmed",
          "source_type": "provider_confirmed",
          "confidence": "declared"
        }
      ],
      "family_capabilities": {},
      "part_type_capabilities": {
        "block": {
          "bounding_box_mm": {
            "length_mm": {
              "max": 150,
              "source_type": "provider_confirmed",
              "confidence": "declared"
            },
            "width_mm": {
              "max": 80,
              "source_type": "provider_confirmed",
              "confidence": "declared"
            },
            "height_mm": {
              "max": 20,
              "source_type": "provider_confirmed",
              "confidence": "declared"
            }
          },
          "number_of_holes": {
            "max": 4,
            "source_type": "provider_confirmed",
            "confidence": "declared"
          }
        }
      },
      "generic_capabilities": {
        "materials": [
          {
            "material": "steel",
            "available_grades": ["18CrNiMo7-6"],
            "source_type": "provider_confirmed",
            "confidence": "declared"
          }
        ],
        "processes": [
          {
            "process": "machining",
            "delivery_mode": "in_house",
            "source_type": "provider_confirmed",
            "confidence": "declared"
          }
        ],
        "certifications": [
          {
            "code": "ISO9001_2015",
            "source_type": "provider_confirmed",
            "confidence": "declared"
          }
        ]
      },
      "custom_offering_fields": {},
      "custom_capability_fields": {}
    }
  ]
}
~~~

**Successful response — HTTP 200**

~~~json
{
  "contract_version": "1.0",
  "valid": true,
  "message": "The provider publication payload is valid.",
  "warnings": [],
  "normalized_payload": {
    "provider": {
      "provider_id": "marketplace_api_test_20261127_01",
      "display_name": "Marketplace API Test Works",
      "country": "Finland",
      "certifications": []
    },
    "offerings": [
      {
        "offering_id": "marketplace_api_test_20261127_01_block_cell",
        "provider_id": "marketplace_api_test_20261127_01",
        "service_category": "precision_metal_parts",
        "name": "Precision block manufacturing",
        "part_family": "metal_part",
        "support_status": "confirmed"
      }
    ]
  }
}
~~~

The normalized response is abbreviated. A valid response confirms that the submitted payload passed validation; it does not register the provider.

**Invalid response — HTTP 400**

~~~json
{
  "contract_version": "1.0",
  "valid": false,
  "message": "The provider publication payload is invalid.",
  "warnings": [],
  "error": {
    "code": "invalid_provider_publication",
    "details": {
      "field": "The submitted value is not accepted."
    }
  }
}
~~~

The actual details identify the field or value that needs correction.

### 7.2 Register a provider and its initial offerings

**POST /api/provider-publication**

Registers one provider and one or more offerings in a single request.

#### Top-level request fields

| Field | Required | Type | Description |
|---|---:|---|---|
| provider_id | Yes | string | Unique provider identifier in lower snake_case |
| provider_name | Yes | string | Provider's name |
| country | Yes | string | Provider's country |
| offerings | Yes | array of objects | At least one offering is required |
| certifications | No | array of objects | Provider-level certifications |
| publication_metadata | No | object | Evidence metadata for the publication |
| custom_provider_fields | No | object | Additional provider-defined information |
| contract_version | No | string | Current value is 1.0 |

#### Offering fields

| Field | Required | Type | Description |
|---|---:|---|---|
| offering_id | No, recommended | string | Unique offering identifier beginning with provider_id and an underscore |
| service_category | Yes | string | Controlled service category |
| offering_name | Yes | string | Name of the manufacturing offering |
| part_family | Yes | string | Controlled part family associated with the category |
| support_status | Yes | string | confirmed, candidate_requiring_confirmation or unknown |
| supported_part_types | No | array of objects | Part types supported by this offering |
| family_capabilities | No | object | Capabilities common to the selected part family |
| part_type_capabilities | No | object | Capabilities grouped by part type |
| generic_capabilities | No | object | General manufacturing capabilities |
| custom_offering_fields | No | object | Additional offering information |
| custom_capability_fields | No | object | Additional capability information |

#### Supported part-type record

Each entry in supported_part_types must contain:

| Field | Required | Description |
|---|---:|---|
| part_type | Yes | Controlled part type belonging to the offering's part family |
| support_status | Yes | confirmed, candidate_requiring_confirmation or unknown |
| source_type | Yes | Evidence source |
| confidence | Yes | Evidence confidence |

A part type may have a corresponding entry in part_type_capabilities only when its support_status is confirmed.

#### Capability map guidance

**family_capabilities**

Use for fields shared by a part family. Examples include gear module, diametral pitch and gear quality, or shaft length and outer diameter.

**part_type_capabilities**

Use an object keyed by the supported part type. For example, use a key of block for block-specific dimensions and hole count, or spur_gear for spur-gear-specific dimensions.

**generic_capabilities**

Use for general manufacturing information. Supported fields are:

- materials
- processes
- batch_size
- lead_time_weeks
- certifications
- surface_finish_ra_um
- tolerance_mm
- quality
- weight_kg

The structure of material, process and certification records is different from the consumer search request:

- Provider material capability: an array of objects containing material and optional available_grades.
- Provider process capability: an array of objects containing process and optional delivery_mode.
- Provider certification capability: an array of objects containing code.

For provider material records, available_grades is a list of grade strings. Material grades are provider capability information; they are not a separate consumer search criterion.

The provider capability record shapes are:

~~~json
{
  "materials": [
    {
      "material": "steel",
      "available_grades": ["18CrNiMo7-6"],
      "source_type": "provider_confirmed",
      "confidence": "declared"
    }
  ],
  "processes": [
    {
      "process": "machining",
      "delivery_mode": "in_house",
      "source_type": "provider_confirmed",
      "confidence": "declared"
    }
  ],
  "certifications": [
    {
      "code": "ISO9001_2015",
      "source_type": "provider_confirmed",
      "confidence": "declared"
    }
  ],
  "batch_size": {"min": 100, "max": 2000},
  "lead_time_weeks": {"min": 8, "max": 12},
  "surface_finish_ra_um": {"max": 1.6},
  "tolerance_mm": {"max": 0.05},
  "weight_kg": {"max": 200},
  "quality": {"standard": "DIN", "max_class": 4}
}
~~~

The example shows the shape of each supported field; include only the capabilities that the provider actually confirms. Numeric capability values are objects using positive min, max and/or exact values.

The accepted delivery_mode values are in_house, subcontracted and unspecified.

For quality capability records, standard may be AGMA, DIN or ISO.

**Request body (Postman: Body → raw → JSON):**

#### Complete example: provider offering block manufacturing

The following example uses a provider with a confirmed block-manufacturing offering. Use a unique provider ID when testing. If the ID already exists, registration returns a conflict.

~~~json
{
  "contract_version": "1.0",
  "provider_id": "marketplace_api_test_20261127_01",
  "provider_name": "Marketplace API Test Works",
  "country": "Finland",
  "certifications": [],
  "offerings": [
    {
      "offering_id": "marketplace_api_test_20261127_01_block_cell",
      "service_category": "precision_metal_parts",
      "offering_name": "Precision block manufacturing",
      "part_family": "metal_part",
      "support_status": "confirmed",
      "supported_part_types": [
        {
          "part_type": "block",
          "support_status": "confirmed",
          "source_type": "provider_confirmed",
          "confidence": "declared"
        }
      ],
      "family_capabilities": {},
      "part_type_capabilities": {
        "block": {
          "bounding_box_mm": {
            "length_mm": {
              "max": 150,
              "source_type": "provider_confirmed",
              "confidence": "declared"
            },
            "width_mm": {
              "max": 80,
              "source_type": "provider_confirmed",
              "confidence": "declared"
            },
            "height_mm": {
              "max": 20,
              "source_type": "provider_confirmed",
              "confidence": "declared"
            }
          },
          "number_of_holes": {
            "max": 4,
            "source_type": "provider_confirmed",
            "confidence": "declared"
          }
        }
      },
      "generic_capabilities": {
        "materials": [
          {
            "material": "steel",
            "available_grades": ["18CrNiMo7-6"],
            "source_type": "provider_confirmed",
            "confidence": "declared"
          }
        ],
        "processes": [
          {
            "process": "machining",
            "delivery_mode": "in_house",
            "source_type": "provider_confirmed",
            "confidence": "declared"
          }
        ],
        "certifications": [
          {
            "code": "ISO9001_2015",
            "source_type": "provider_confirmed",
            "confidence": "declared"
          }
        ]
      },
      "custom_offering_fields": {},
      "custom_capability_fields": {}
    }
  ]
}
~~~

For metal_part offerings, family_capabilities must be empty. Use the part-type-specific map for the block, plate, bracket, bushing, roller or collar capabilities.

#### Successful registration response

With the current Marketplace API profile, a completed publication returns HTTP 201 and a receipt similar to:

~~~json
{
  "contract_version": "1.0",
  "status": "completed",
  "operation": "create",
  "provider_id": "marketplace_api_test_20261127_01",
  "publication_id": "00000000-0000-0000-0000-000000000001",
  "publication_status": "synced",
  "sync_status": "succeeded",
  "offering_ids": [
    "marketplace_api_test_20261127_01_block_cell"
  ]
}
~~~

The publication_id is the identifier for this publication receipt. Retain it for support enquiries.

A successful receipt with status = completed, publication_status = synced and sync_status = succeeded confirms that the offering is available to service discovery. No additional publication request is needed.

---

## 8. Provider operations

### 8.1 Retrieve provider details

**GET /api/providers/{provider_id}**

Returns provider information, provider-level certifications and a summary of its offerings.

Example:

~~~bash
curl --request GET "https://maasai-mdc-v1.vercel.app/api/providers/marketplace_api_test_20261127_01" --header "Accept-Encoding: identity"
~~~

Representative response body:

~~~json
{
  "contract_version": "1.0",
  "provider_id": "marketplace_api_test_20261127_01",
  "provider_name": "Marketplace API Test Works",
  "country": "Finland",
  "status": "active",
  "custom_provider_fields": {},
  "publication_metadata": {},
  "certifications": [],
  "offerings": [
    {
      "offering_id": "marketplace_api_test_20261127_01_block_cell",
      "offering_name": "Precision block manufacturing",
      "service_category": "precision_metal_parts",
      "part_family": "metal_part",
      "support_status": "confirmed",
      "is_active": true
    }
  ]
}
~~~

The response includes an **ETag** header. If you plan to update or delete this provider, save the complete header value in Postman as `provider_etag`.

### 8.2 Update provider information

**PATCH /api/providers/{provider_id}**

At least one editable field is required.

Accepted fields:

| Field | Type | Description |
|---|---|---|
| provider_name | string | Updated provider name |
| country | string | Updated country |
| status | string | draft, active, suspended or archived |
| certifications | array of objects | Replaces the provider-level certification list |
| publication_metadata | object | Replaces publication metadata |
| custom_provider_fields | object | Replaces custom provider fields |

Example:

~~~json
{
  "provider_name": "Marketplace API Test Works Updated",
  "custom_provider_fields": {
    "marketplace_reference": "provider-record-001"
  }
}
~~~

Send the latest provider ETag in the `If-Match` header, for example `If-Match: {{provider_etag}}`. Postman should store the complete ETag value returned by GET, including its quotation marks. A successful update returns HTTP 200, a publication receipt and a new ETag.

### 8.3 Delete a provider

**DELETE /api/providers/{provider_id}**

Deletes the provider and all offerings belonging to it.

- No request body is required.
- The latest ETag in the `If-Match` header is required.
- A successful request returns HTTP 200 and a deletion receipt.
- Retrieve the provider again before deletion if any provider or offering changes have occurred since the last provider detail read.

Example:

~~~http
DELETE /api/providers/marketplace_api_test_20261127_01
If-Match: {{provider_etag}}
~~~

A completed deletion receipt includes the target provider, publication_id, publication_status, sync_status and the removed offering IDs.

---

## 9. Offering operations

### 9.1 List a provider's offerings

**GET /api/providers/{provider_id}/offerings**

Returns the provider's offerings, including their capability maps.

Example:

~~~bash
curl --request GET "https://maasai-mdc-v1.vercel.app/api/providers/marketplace_api_test_20261127_01/offerings"
~~~

The response contains contract_version, provider_id and an offerings array.

### 9.2 Add an offering

**POST /api/providers/{provider_id}/offerings**

Adds one offering to an existing provider.

Required fields:

- service_category
- offering_name
- part_family
- support_status

Optional fields:

- offering_id
- supported_part_types
- family_capabilities
- part_type_capabilities
- generic_capabilities
- custom_offering_fields
- custom_capability_fields

The offering fields and capability rules are the same as those described in Section 7.2.

**Request body (Postman: Body → raw → JSON):**

~~~json
{
  "contract_version": "1.0",
  "offering_id": "marketplace_api_test_20261127_01_plate_cell",
  "service_category": "precision_metal_parts",
  "offering_name": "Precision plate manufacturing",
  "part_family": "metal_part",
  "support_status": "confirmed",
  "supported_part_types": [
    {
      "part_type": "plate",
      "support_status": "confirmed",
      "source_type": "provider_confirmed",
      "confidence": "declared"
    }
  ],
  "family_capabilities": {},
  "part_type_capabilities": {
    "plate": {
      "bounding_box_mm": {
        "length_mm": {"max": 300},
        "width_mm": {"max": 200},
        "height_mm": {"max": 25}
      },
      "number_of_holes": {"max": 8}
    }
  },
  "generic_capabilities": {},
  "custom_offering_fields": {},
  "custom_capability_fields": {}
}
~~~

The offering ID must be unique and belong to the provider in the URL. A successful request returns HTTP 201, the new offering ID and a publication receipt.

### 9.3 Retrieve full offering details

**GET /api/offerings/{offering_id}**

Returns the full offering, including its supported part types and capability maps.

Example:

~~~bash
curl --request GET "https://maasai-mdc-v1.vercel.app/api/offerings/marketplace_api_test_20261127_01_block_cell" --header "Accept-Encoding: identity"
~~~

The response includes an **ETag** header. If you plan to update or delete this offering, save the complete header value in Postman as `offering_etag`.

### 9.4 Update an offering

**PATCH /api/offerings/{offering_id}**

Accepted fields:

| Field | Type | Description |
|---|---|---|
| offering_name | string | Updated offering name |
| support_status | string | Updated offering support status |
| supported_part_types | array | Replaces supported part-type records |
| family_capabilities | object | Replaces the family capability map |
| part_type_capabilities | object | Replaces the part-type capability map |
| generic_capabilities | object | Replaces the generic capability map |
| custom_offering_fields | object | Replaces custom offering fields |
| custom_capability_fields | object | Replaces custom capability fields |
| is_active | boolean | Activates or deactivates the offering |

The service category, part family and offering ID are not editable through PATCH.

Example:

~~~json
{
  "offering_name": "Precision block manufacturing - updated",
  "part_type_capabilities": {
    "block": {
      "bounding_box_mm": {
        "length_mm": {"max": 180},
        "width_mm": {"max": 90},
        "height_mm": {"max": 25}
      },
      "number_of_holes": {"max": 6}
    }
  }
}
~~~

Send the latest offering ETag in the `If-Match` header, for example `If-Match: {{offering_etag}}`. Postman should store the complete ETag value returned by GET, including its quotation marks. Because part_type_capabilities is a whole-map replacement, the example includes every block capability that should remain after the update.

A successful update returns HTTP 200, a publication receipt and a new ETag.

### 9.5 Delete one offering

**DELETE /api/offerings/{offering_id}**

Deletes only the selected offering. Other offerings belonging to the same provider remain.

- No request body is required.
- The latest ETag in the `If-Match` header is required.
- A successful request returns HTTP 200 and a deletion receipt.

Example:

~~~http
DELETE /api/offerings/marketplace_api_test_20261127_01_block_cell
If-Match: {{offering_etag}}
~~~

---

## 10. Service discovery

### POST /api/service-discovery/search

Submits a consumer's manufacturing requirements and returns the offerings that satisfy them.

MDC performs technical eligibility checking. It does not perform the final provider ranking or recommendation. The eligible offerings can be passed to the MaaS Recommendation System for that purpose.

### 10.1 Request fields

| Field | Required | Type | Description |
|---|---:|---|---|
| contract_version | No | string | Current value is 1.0 |
| request_id | Yes | string | Unique identifier for the search request |
| consumer_id | Yes | string | Identifier of the requesting consumer |
| service_category | Yes | string | Controlled service category |
| part_family | Yes | string | Part family associated with the category |
| part_type | Yes | string | Part type belonging to the selected family |
| requirements | No | object | Technical and general manufacturing requirements |
| match_policy | No | object | Optional matching-policy compatibility fields |

### 10.2 Requirements structure

The requirements object has three groups:

~~~json
{
  "part_family_specifications": {},
  "part_type_specifications": {},
  "generic_requirements": {}
}
~~~

Use the groups as follows:

- part_family_specifications: requirements common to the selected part family.
- part_type_specifications: requirements specific to the selected part type.
- generic_requirements: general requirements such as material, process, batch size, delivery, certification, tolerance, quality and weight.

A field must appear in the correct group for the selected part type. Do not repeat the same field in more than one group.

### 10.3 Part-family and part-type fields

The accepted fields depend on the selected part type.

**Gear**

| Scope | Accepted fields |
|---|---|
| part_family_specifications | module, diametral_pitch, number_of_teeth, outside_diameter_mm, gear_quality, tolerance_mm |
| spur_gear | face_width_mm |
| helical_gear | face_width_mm, helix_angle_deg |
| bevel_gear | face_width_mm, shaft_angle_deg |
| worm_gear | center_distance_mm, shaft_angle_deg |
| crown_gear | face_width_mm, inner_diameter_mm |

**Shaft**

| Scope | Accepted fields |
|---|---|
| part_family_specifications | length_mm, outer_diameter_mm, tolerance_mm |
| plain_shaft | principal_diameter_mm |
| stepped_shaft | number_of_steps |
| splined_shaft | spline_module, spline_length_mm |
| worm_shaft | worm_module, number_of_starts |
| hollow_shaft | inner_diameter_mm, wall_thickness_mm |

**Metal parts**

| Part type | part_family_specifications | part_type_specifications |
|---|---|---|
| block | bounding_box_mm | number_of_holes |
| plate | bounding_box_mm | number_of_holes |
| bracket | bounding_box_mm | vertical_flange_length_mm, horizontal_flange_length_mm |
| bushing | inner_diameter_mm, outer_diameter_mm, overall_length_mm, tolerance_mm | flange_diameter_mm |
| roller | inner_diameter_mm, outer_diameter_mm, overall_length_mm, tolerance_mm | None |
| collar | inner_diameter_mm, outer_diameter_mm, overall_length_mm, tolerance_mm | None |

For bounding_box_mm, provide one or more of length_mm, width_mm and height_mm.

### 10.4 Generic requirement fields

| Field | Type | Example |
|---|---|---|
| materials | array of controlled strings | ["steel"] |
| processes | array of controlled strings | ["machining"] |
| certifications | array of controlled strings | ["ISO9001_2015"] |
| batch_size | positive integer | 500 |
| delivery | object | {"max_weeks": 12} |
| surface_finish_ra_um | range or exact object | {"max": 1.6} |
| tolerance_mm | range or exact object | {"max": 0.05} |
| quality | object | {"standard": "DIN", "max_class": 4} |
| weight_kg | positive number | 25 |

Material, process and certification values must be taken from GET /api/catalog/filters.

Material grades are not accepted as a separate search criterion. They may be included in provider material capability records as available_grades.

### 10.5 Range and exact values

For numeric requirements, use one or more of min, max and exact.

~~~json
{"min": 10, "max": 100}
~~~

~~~json
{"exact": 50}
~~~

The values must be positive. If min and max are both supplied, min must not exceed max. For integer fields such as number_of_holes, use integer values.

For quality, provide both standard and max_class:

~~~json
{
  "standard": "DIN",
  "max_class": 4
}
~~~

For a bounding box:

~~~json
{
  "length_mm": {"max": 150},
  "width_mm": {"max": 80},
  "height_mm": {"max": 20}
}
~~~

### 10.6 Matching behaviour

MDC applies strict technical eligibility:

- Every supplied requirement must be satisfied.
- The requested part type must have confirmed support.
- An offering with missing or unconfirmed evidence for a required criterion is not returned as eligible.
- Partial matches are not returned as eligible results.
- An omitted requirement does not impose a constraint.

The optional match_policy object accepts:

| Field | Accepted values |
|---|---|
| optional_match_mode | any, all, score_only |
| unknown_policy | keep_as_unknown, reject_unknown |
| minimum_score | A number from 0 to 1, or null |

The current service applies strict eligibility regardless of legacy permissive policy values. A permissive value does not allow a partial or unknown offering to be returned as eligible. For normal Marketplace requests, omit match_policy or send the strict values:

~~~json
{
  "optional_match_mode": "all",
  "unknown_policy": "reject_unknown",
  "minimum_score": null
}~~~

### 10.7 Complete example: search for block manufacturing

This example searches for block-manufacturing offerings that can satisfy the requested bounding box and hole count and support the selected material, process and certification.

**Request body (Postman: Body → raw → JSON):**

~~~json
{
  "contract_version": "1.0",
  "request_id": "marketplace_block_search_001",
  "consumer_id": "marketplace_consumer_001",
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
      "certifications": ["ISO9001_2015"]
    }
  }
}
~~~

### 10.8 Search response

A successful search returns HTTP 200. The response includes the request ID, selected category/family/type, result_count and results.

Representative response:

~~~json
{
  "contract_version": "1.0",
  "request_id": "marketplace_block_search_001",
  "service_category": "precision_metal_parts",
  "part_family": "metal_part",
  "part_type": "block",
  "result_count": 1,
  "results": [
    {
      "provider_id": "marketplace_api_test_20261127_01",
      "provider_name": "Marketplace API Test Works",
      "offering_id": "marketplace_api_test_20261127_01_block_cell",
      "offering_name": "Precision block manufacturing",
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
~~~

The example shows the response structure. The actual result_count and provider offerings depend on the current catalogue and the submitted requirements.

Each result identifies both the provider and the specific offering. Use offering_id as the offering identifier; do not treat service_category as an offering ID.

The returned score is compatibility metadata, not the final recommendation ranking. The MaaS Recommendation System is responsible for comparing and ranking the eligible offerings.

If the Marketplace needs the complete published capability record for a returned offering, call GET /api/offerings/{offering_id}.

### 10.9 No eligible offerings

If no offering satisfies all supplied requirements, MDC returns HTTP 200 with:

~~~json
{
  "contract_version": "1.0",
  "request_id": "marketplace_block_search_001",
  "service_category": "precision_metal_parts",
  "part_family": "metal_part",
  "part_type": "block",
  "result_count": 0,
  "results": []
}
~~~

This is a successful search with no eligible offerings, not an API error.

---

## 11. Error handling

Errors use a JSON response containing contract_version and an error object.

Representative format:

~~~json
{
  "contract_version": "1.0",
  "error": {
    "code": "invalid_provider_publication",
    "message": "The provider publication payload is invalid.",
    "details": {}
  }
}
~~~

| HTTP status | Meaning | Recommended action |
|---:|---|---|
| 200 | Request completed | Read the response body; a search may validly return zero results |
| 201 | Provider or offering created | Retain returned IDs, publication receipt and ETag |
| 400 | Invalid request or unsupported field | Correct the field/value identified in error.details |
| 404 | Provider or offering not found | Verify the ID and request URL |
| 409 | Provider or offering already exists | Use a unique ID or retrieve the existing record |
| 412 | ETag is stale | GET the current resource, review it and retry with the latest ETag |
| 428 | If-Match is missing | GET the resource and supply its latest ETag |
| 503 | Service or publication could not be confirmed | Read the resource before deciding whether a write needs retrying |

A lifecycle write may have been accepted even when the response is HTTP 503. Retain publication_id if present, GET the relevant provider or offering, and confirm its current state before retrying. Do not blindly repeat a registration request.

---

## 12. Recommended API call sequence

For a new provider:

1. GET /api/health.
2. GET /api/catalog/filters.
3. POST /api/provider-publication/validation with the complete provider payload.
4. Correct any validation errors and repeat validation.
5. POST /api/provider-publication with the same validated payload.
6. Confirm the completed publication receipt.
7. GET /api/providers/{provider_id} and retain the ETag.
8. GET /api/providers/{provider_id}/offerings to review the published offerings.

For consumer discovery:

1. GET /api/catalog/filters if current controlled values are not already available.
2. Build the request using the correct service category, part family and part type.
3. POST /api/service-discovery/search.
4. Pass the eligible offering results to the MaaS Recommendation System.
5. If full offering details are needed, GET /api/offerings/{offering_id}.

For updates or deletion, retrieve the current resource first, save its ETag and send it in the `If-Match` header. Postman can save and reuse the value automatically.

---

## 13. API summary

~~~text
GET    /api/health
GET    /api/catalog/filters
POST   /api/provider-publication/validation
POST   /api/provider-publication
GET    /api/providers/{provider_id}
PATCH  /api/providers/{provider_id}
DELETE /api/providers/{provider_id}
GET    /api/providers/{provider_id}/offerings
POST   /api/providers/{provider_id}/offerings
GET    /api/offerings/{offering_id}
PATCH  /api/offerings/{offering_id}
DELETE /api/offerings/{offering_id}
POST   /api/service-discovery/search
~~~

**Current API contract version: 1.0**
