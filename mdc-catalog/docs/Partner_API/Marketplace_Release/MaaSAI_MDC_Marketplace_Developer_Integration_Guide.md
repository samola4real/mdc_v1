# MaaSAI MaaS Dynamic Catalogue — Marketplace Developer Integration Guide

**Audience:** MaaSAI Marketplace developers  
**API contract version:** 1.0  
**API base URL:** https://maasai-mdc-v1.vercel.app

---

## 1. Introduction

This guide explains how the MaaSAI Marketplace should use the MaaS Dynamic Catalogue (MDC) API to:

1. Register manufacturing providers and publish their offerings.
2. Maintain provider and offering information.
3. Submit consumer manufacturing requirements.
4. Receive technically eligible manufacturing offerings.
5. pass those eligible offerings to the MaaS Recommendation System for comparison and ranking.

The guide is written as an implementation walkthrough. Each step includes the endpoint, request format and expected outcome.

For complete field definitions and all endpoint details, use the companion **MaaSAI MDC Marketplace API Reference**.

## 2. Integration overview

The Marketplace communicates with MDC through JSON API requests.

~~~text
Marketplace
    |
    | Provider registration / offering publication
    | Consumer manufacturing requirements
    v
MaaSAI MaaS Dynamic Catalogue
    |
    | Published provider offerings
    | Technically eligible search results
    v
MaaS Recommendation System
    |
    | Provider comparison and ranking
    v
Marketplace
~~~

MDC determines which offerings satisfy the consumer's specified technical requirements. The MaaS Recommendation System performs the subsequent ranking and recommendation.

## 3. Connection setup

### 3.1 API base URL

~~~text
https://maasai-mdc-v1.vercel.app
~~~

Use the base URL as a Postman environment variable named **base_url**.

Example request URL:

~~~text
{{base_url}}/api/health
~~~

### 3.2 Authentication and headers

For the supplied API URL, no MDC bearer token or Authorization header is required. The Marketplace is responsible for authenticating its own users.

For JSON POST and PATCH requests, use:

~~~http
Content-Type: application/json
Accept: application/json
~~~

The current API contract version is 1.0. It can be included as contract_version in JSON request bodies. The API defaults to 1.0 if it is omitted.

### 3.3 First connection check

Send:

~~~http
GET {{base_url}}/api/health
~~~

Expected response: HTTP 200.

~~~json
{
  "contract_version": "1.0",
  "status": "ok",
  "service": "maasai-mdc"
}
~~~

If this request fails, check the base URL and network connectivity before testing other operations.

## 4. Retrieve the current catalogue values

Before building provider forms or consumer search forms, call:

~~~http
GET {{base_url}}/api/catalog/filters
~~~

MDC returns:

- Service categories.
- Part families and their corresponding service categories.
- Part types grouped by part family.
- Materials.
- Manufacturing processes.
- Certifications.

Use the value fields in subsequent requests. Use labels only for display in the Marketplace.

For example, the relationship for a block request is:

~~~text
precision_metal_parts
        |
        v
metal_part
        |
        v
block
~~~

The Marketplace should use the live response rather than maintaining a separate hard-coded list of allowed values.

## 5. Provider onboarding and offering publication

A provider can publish one or more manufacturing offerings. Each offering is independently identified and may have its own supported part types and capability information.

### Step 1 — Prepare the provider publication payload

Collect the provider information:

- provider_id
- provider_name
- country
- optional provider-level certifications
- one or more offerings

Each offering must contain:

- service_category
- offering_name
- part_family
- support_status

It may also contain:

- offering_id
- supported_part_types
- family_capabilities
- part_type_capabilities
- generic_capabilities
- custom_offering_fields
- custom_capability_fields

Use controlled values returned by GET /api/catalog/filters for service categories, families, part types, materials, processes and certifications.

Do not use the old description or capabilities fields. The current publication contract uses provider_name and the structured capability maps.

### Step 2 — Understand the capability structure

Use the capability map that corresponds to the information being published.

| Capability map | What belongs in it |
|---|---|
| family_capabilities | Fields common to the part family, such as gear module or shaft length |
| part_type_capabilities | Fields specific to a part type, grouped under the part type value |
| generic_capabilities | General manufacturing information, such as materials, processes, batch size, lead time and certifications |

For a metal_part offering, family_capabilities must be empty. Use part_type_capabilities for the selected metal part type.

For a part-type capability map, the key must be a part type listed in supported_part_types. The part type must have confirmed support before capabilities for that part type are published.

Use custom_offering_fields and custom_capability_fields for additional provider-defined information that does not yet have a corresponding controlled field. Do not place free-text values in controlled fields such as service_category, part_family, part_type, materials or processes.

### Step 3 — Validate the complete payload

Send the complete provider publication body to:

~~~http
POST {{base_url}}/api/provider-publication/validation
Content-Type: application/json
Accept: application/json
~~~

**Request body:** In Postman, select **Body → raw → JSON** and paste the complete provider JSON payload shown in Section 6. Do not send only the provider ID or only the offering object. The validation request uses the full provider object, including its offerings.

The validation endpoint does not register the provider or create an offering.

A valid response is HTTP 200:

~~~json
{
  "contract_version": "1.0",
  "valid": true,
  "message": "The provider publication payload is valid.",
  "warnings": [],
  "normalized_payload": {}
}
~~~

The normalized_payload is the validated representation. The example above is shortened; the actual response contains the normalized provider and offering data.

If the response is HTTP 400, inspect error.details, correct the identified field and validate again.

### Step 4 — Register the provider

After validation succeeds, send the same JSON body to:

~~~http
POST {{base_url}}/api/provider-publication
Content-Type: application/json
Accept: application/json
~~~

**Request body:** Use **Body → raw → JSON** and paste the same complete payload from Section 6. Do not change the provider or offering IDs between validation and registration.

A successful registration returns HTTP 201 and a publication receipt.

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

Retain the provider_id, offering_ids and publication_id. A completed/synced/succeeded receipt confirms that the published offerings are available to service discovery.

### Step 5 — Read the registered provider

Send:

~~~http
GET {{base_url}}/api/providers/{{provider_id}}
Accept-Encoding: identity
~~~

The response contains the provider details and a summary of its offerings. The HTTP response also includes a strong ETag header.

Retain the ETag if the provider may be updated or deleted later.

To retrieve the provider's complete offering records, send:

~~~http
GET {{base_url}}/api/providers/{{provider_id}}/offerings
~~~

## 6. Complete provider publication example

This example is designed to be copied into Postman. It registers a provider with a confirmed block-manufacturing offering. The capability values are chosen so that the same offering can be found by the block search example in Section 9.

Use a unique provider_id and matching offering_id for each test run. If the provider ID already exists, MDC returns HTTP 409.

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

## 7. Add another offering to an existing provider

Use:

~~~http
POST {{base_url}}/api/providers/{{provider_id}}/offerings
Content-Type: application/json
Accept: application/json
~~~

**Request body:** In Postman, select **Body → raw → JSON** and paste the complete single-offering payload shown below. The body contains one offering object, not the complete provider object.

Example:

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

A successful request returns HTTP 201 and a receipt containing the new offering ID.

## 8. Update provider or offering information

### 8.1 Update provider information

First retrieve the provider:

~~~http
GET {{base_url}}/api/providers/{{provider_id}}
Accept-Encoding: identity
~~~

The GET response includes an **ETag** header. Think of this as the current version label for the provider. In Postman, the script in Section 10.3 saves it as `provider_etag`. Then send the PATCH request with:

~~~http
PATCH {{base_url}}/api/providers/{{provider_id}}
If-Match: {{provider_etag}}
Content-Type: application/json
~~~

Do not type an ETag yourself. Postman inserts the value returned by MDC, including any quotation marks that are part of it.

Example body:

~~~json
{
  "provider_name": "Marketplace API Test Works Updated",
  "custom_provider_fields": {
    "marketplace_reference": "provider-record-001"
  }
}
~~~

At least one editable field must be supplied. Provider fields that can be updated include provider_name, country, status, certifications, publication_metadata and custom_provider_fields.

### 8.2 Update an offering

First retrieve the full offering:

~~~http
GET {{base_url}}/api/offerings/{{offering_id}}
Accept-Encoding: identity
~~~

The GET response includes an **ETag** header. In Postman, the script in Section 10.3 saves it as `offering_etag`. Then send the PATCH request with:

~~~http
PATCH {{base_url}}/api/offerings/{{offering_id}}
If-Match: {{offering_etag}}
Content-Type: application/json
~~~

Postman reuses the complete value returned by MDC. You do not need to type the value or add quotation marks yourself.

Example body:

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

Important: map fields such as part_type_capabilities are replaced as a whole. Include every capability entry that should remain after the update. A partial map submission can remove entries that were previously present.

The service category, part family and offering ID cannot be changed through PATCH.

A successful update returns HTTP 200, a publication receipt and a new ETag.

### 8.3 Delete a provider

First retrieve the provider again and save its latest ETag as `provider_etag`. Then send:

~~~http
DELETE {{base_url}}/api/providers/{{provider_id}}
If-Match: {{provider_etag}}
~~~

No request body is required. The ETag is required for deletion. Deleting a provider also deletes all its offerings.

### 8.4 Delete one offering

First retrieve the offering and save its latest ETag as `offering_etag`. Then send:

~~~http
DELETE {{base_url}}/api/offerings/{{offering_id}}
If-Match: {{offering_etag}}
~~~

No request body is required. Only the selected offering is deleted.

## 9. Consumer service discovery

### Step 1 — Prepare the consumer request

The Marketplace must submit the selected service category, part family and part type, together with any technical or general manufacturing requirements.

Use the live values returned by GET /api/catalog/filters.

### Step 2 — Send the search request

Use:

~~~http
POST {{base_url}}/api/service-discovery/search
Content-Type: application/json
Accept: application/json
~~~

**Request body:** In Postman, select **Body → raw → JSON** and paste the complete search payload below.

Complete block search example:

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

### Step 3 — Interpret the response

A successful request returns HTTP 200.

The response includes:

- request_id: the identifier supplied by the Marketplace.
- service_category, part_family and part_type: the selected service and part.
- result_count: number of eligible offerings returned.
- results: provider and offering identities, match information and capability comparisons.

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

The example response is illustrative. Actual results depend on the current published offerings and the consumer's requirements.

### Step 4 — Pass eligible offerings to the Recommendation System

MDC returns technically eligible offerings. The Marketplace should pass the returned provider and offering identities, together with the relevant result information, to the MaaS Recommendation System.

The Recommendation System is responsible for comparing and ranking the eligible offerings according to the consumer's broader preferences and priorities.

MDC does not return partial matches as eligible results. Every supplied requirement must be satisfied. If no offering qualifies, the API returns HTTP 200 with result_count = 0 and an empty results array.

### Step 5 — Retrieve full offering details when needed

The service-discovery response contains the offering identity and capability comparison. If the Marketplace needs the full published offering record, use:

~~~http
GET {{base_url}}/api/offerings/{{offering_id}}
~~~

## 10. Postman setup and practical test sequence

### 10.1 Create an environment

Create a Postman environment with the following variables:

| Variable | Value |
|---|---|
| base_url | https://maasai-mdc-v1.vercel.app |
| provider_id | marketplace_api_test_20261127_01 |
| offering_id | marketplace_api_test_20261127_01_block_cell |
| provider_etag | Leave empty until the provider is retrieved |
| offering_etag | Leave empty until the offering is retrieved |

Choose **No Auth** for the collection or individual requests. Do not add a bearer token.

### 10.2 Run the requests in this order

| Order | Method | Request | Expected result |
|---:|---|---|---|
| 1 | GET | {{base_url}}/api/health | HTTP 200 |
| 2 | GET | {{base_url}}/api/catalog/filters | HTTP 200 with catalogue values |
| 3 | POST | {{base_url}}/api/provider-publication/validation | HTTP 200 and valid = true |
| 4 | POST | {{base_url}}/api/provider-publication | HTTP 201 and completed publication receipt |
| 5 | GET | {{base_url}}/api/providers/{{provider_id}} | HTTP 200 and provider ETag |
| 6 | GET | {{base_url}}/api/providers/{{provider_id}}/offerings | HTTP 200 and offering list |
| 7 | GET | {{base_url}}/api/offerings/{{offering_id}} | HTTP 200 and offering ETag |
| 8 | POST | {{base_url}}/api/service-discovery/search | HTTP 200; the test block offering should be eligible for the matching example request |
| 9 | DELETE | {{base_url}}/api/providers/{{provider_id}} | HTTP 200 and completed deletion receipt |

For requests 3 and 4, use the complete provider payload from Section 6. For request 8, use the block search payload from Section 9.

### 10.3 Save and reuse ETags in Postman

You do not need to understand or manually create an ETag. MDC returns it in the GET response headers. The following scripts save the complete value automatically, including the quotation marks returned by MDC.

After **GET provider details**, add this script in the Postman **Scripts → Post-response** (or **Tests**) tab:

~~~javascript
const etag = pm.response.headers.get("ETag");
if (!etag) {
  throw new Error("MDC did not return an ETag for this provider.");
}
pm.environment.set("provider_etag", etag);
~~~

After **GET offering details**, use:

~~~javascript
const etag = pm.response.headers.get("ETag");
if (!etag) {
  throw new Error("MDC did not return an ETag for this offering.");
}
pm.environment.set("offering_etag", etag);
~~~

For a provider PATCH or DELETE request, add this request header:

~~~http
If-Match: {{provider_etag}}
~~~

For an offering PATCH or DELETE request, add:

~~~http
If-Match: {{offering_etag}}
~~~

Do not put quotation marks around the Postman variable. The variable already contains the complete value returned by MDC.

**In simple terms:** GET retrieves the current record and saves its version label; PATCH or DELETE sends that same label back to MDC. If the record has changed in the meantime, retrieve it again and use the new value.

### 10.4 Clean up test data

Provider registration creates a real provider record and makes its eligible offering available to search. Use a unique test provider ID and delete that provider when testing is complete.

Before deleting, retrieve the provider again and use its latest ETag. Provider deletion also deletes the provider's offerings.

Do not use an existing production provider ID for integration tests.

---

## 11. Error handling and retry guidance

| HTTP status | What it means | What to do |
|---:|---|---|
| 400 | Invalid field, value or request structure | Read error.details and correct the request |
| 404 | Provider or offering does not exist | Check the ID and endpoint |
| 409 | The provider or offering ID already exists | Use a new unique ID or retrieve the existing record |
| 412 | The ETag is no longer current | GET the resource and use its latest ETag |
| 428 | If-Match is missing | GET the resource and include its latest ETag |
| 503 | The operation or publication could not be confirmed | Read the response receipt and GET the resource before retrying |

Do not blindly repeat a provider registration or offering creation after an HTTP 503. The request may have been accepted even if the final response could not confirm publication. Check the provider or offering first.

A service-discovery response with HTTP 200 and zero results is not an error. It means no offering satisfies all the supplied requirements.

## 12. Implementation checklist

Before completing the Marketplace integration, confirm that:

- [ ] The Marketplace uses the supplied base URL and unversioned /api/ routes.
- [ ] The Marketplace retrieves controlled values from GET /api/catalog/filters.
- [ ] Provider publication uses provider_name and the structured capability maps.
- [ ] Each offering has a support_status.
- [ ] Each supported part-type record contains part_type, support_status, source_type and confidence.
- [ ] The provider publication validation endpoint is called before registration.
- [ ] Provider and offering IDs are stored and reused for subsequent requests.
- [ ] PATCH and DELETE requests send the latest ETag in the If-Match header (PATCH is recommended; DELETE requires it).
- [ ] Service-discovery requests use the correct requirements group for each field.
- [ ] The Marketplace treats MDC results as technically eligible offerings and sends them to the Recommendation System for ranking.
- [ ] Test providers are deleted after integration testing.

---

## 13. Support information to include when reporting an API issue

When reporting an issue, include:

1. HTTP method and endpoint path.
2. HTTP status code.
3. Request body, with any confidential business information removed.
4. Response body.
5. Provider ID or offering ID, if applicable.
6. Publication ID, if the response contains one.
7. The approximate time of the request.

Do not include passwords, access tokens or other credentials in an issue report.
