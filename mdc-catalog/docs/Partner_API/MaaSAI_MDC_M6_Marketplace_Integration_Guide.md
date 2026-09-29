# MaaSAI MDC M6 Marketplace integration guide

Status: frozen integration contract for M6-A. Contract version: `1.0`.

Use a deployment URL supplied by the MDC operator as `{{base_url}}`. No
`/api/v1/` partner routes exist. All canonical routes are directly below
`/api/`.

## Contract rules that Marketplace must preserve

- A provider owns one or more independently addressable offerings.
- Multiple offerings may share a service category. `offering_id`, not
  `service_category`, is the offering identity.
- `provider_id` and `offering_id` are immutable. An explicit offering ID must
  use lower snake case and start with its provider ID.
- Route, operation, and process sequence fields are not accepted. Manufacturing
  `processes` are unordered capabilities.
- PATCH changes only supplied scalar fields, but every supplied map field is a
  whole-map replacement. To remove one optional nested attribute, send the
  complete selected map without that attribute and retain every wanted sibling.
- DELETE permanently removes the operational provider/offering. Minimal
  redacted publication, tombstone, and outbox history remains for audit and
  recovery.
- With automatic synchronization enabled, a lifecycle write is complete only
  after MDC replaces the RDF graph and reads the same revision marker through
  the canonical Fuseki query endpoint.
- Marketplace never calls a synchronization endpoint. There is no public sync
  API.
- A `503` publication receipt can mean PostgreSQL committed but Fuseki
  verification did not complete. Retain its `publication_id`, inspect the
  operational resource, and coordinate recovery. Never blindly replay a
  non-idempotent registration.

## Frozen endpoint matrix

| Method and route | Purpose and request | Success | PostgreSQL / semantic behavior | Main errors and retry guidance |
| --- | --- | --- | --- | --- |
| `GET /api/health` | Liveness; no body | `200`, `contract_version`, `status`, `service` | Read-only; no Fuseki dependency | Transport/`5xx`: retry with bounded backoff |
| `GET /api/catalog/filters` | Current controlled service categories, families, types, materials, processes and certifications; no body | `200` filter document | Read-only; no mutation | Transport/`5xx`: retry; do not permanently hard-code the example vocabulary |
| `POST /api/service-discovery/search` | Required `request_id`, `consumer_id`, `service_category`, `part_family`, `part_type`; optional `requirements`, `match_policy`, `contract_version` | `200`, result count and offering-level matches | Read-only. In automatic mode, authoritative Fuseki and its current revision are required | `400` invalid contract/taxonomy/requirements; `503` unavailable or stale semantic catalogue. Retrying a read is safe |
| `POST /api/provider-publication/validation` | Same provider publication body as registration; optional `contract_version` | `200`, `valid=true`, normalized payload | Read-only; no PostgreSQL or Fuseki mutation | `400` invalid publication; `401/403/503` security/configuration gates |
| `POST /api/provider-publication` | Required provider ID/name/country and at least one valid offering; optional certifications, metadata, custom fields | `201`; accepted or completed receipt; strong provider `ETag` | Creates provider, offerings, publication and outbox events. Automatic success also verifies Fuseki visibility | `400`, `401`, `403`, `409`, `503`. On post-commit `503`, GET provider and recover by publication ID; do not repeat POST |
| `GET /api/providers/{provider_id}` | Provider and offering summaries; no body | `200` plus strong `ETag` | Read-only PostgreSQL | `401/404/503`; safe to retry |
| `PATCH /api/providers/{provider_id}` | Optional editable fields: `provider_name`, `country`, `status`, `certifications`, `publication_metadata`, `custom_provider_fields`; at least one required | `200` receipt plus new strong `ETag` | Updates PostgreSQL and creates publication/outbox work; automatic success verifies Fuseki | `400`, `401`, `403`, `404`, `409`, `412`, `428`, `503`. GET a fresh ETag before retrying stale writes |
| `DELETE /api/providers/{provider_id}` | No body; current strong `If-Match` is always required | `200` deletion receipt and deleted offering IDs | Permanently removes provider aggregate from operational PostgreSQL; retains minimal audit/outbox history; automatic success verifies semantic absence | `400` malformed ETag, `404`, `412`, `428`, `503`. Do not replay if the resource is already absent |
| `GET /api/providers/{provider_id}/offerings` | Lists independently addressable offerings; no body | `200` provider ID and offerings | Read-only PostgreSQL | `401/404/503` |
| `POST /api/providers/{provider_id}/offerings` | Required category, name, family and support status; optional explicit `offering_id`, selected maps and part types | `201` receipt plus offering ID and strong `ETag` | Adds one offering and publication/outbox work; automatic success verifies Fuseki | `400`, `401`, `403`, `404`, `409`, `503`. On ambiguous `503`, GET the offering before deciding any retry |
| `GET /api/offerings/{offering_id}` | Full offering record; no body | `200` plus strong `ETag` | Read-only PostgreSQL | `401/404/503` |
| `PATCH /api/offerings/{offering_id}` | Optional `offering_name`, `support_status`, `supported_part_types`, capability/custom maps, `is_active`; identity/classification are immutable | `200` receipt plus new strong `ETag` | Updates offering, publication and outbox; automatic success verifies Fuseki | `400`, `401`, `403`, `404`, `412`, `428`, `503`; GET current state/ETag before retry |
| `DELETE /api/offerings/{offering_id}` | No body; current strong `If-Match` is always required | `200` deletion receipt | Permanently removes only that operational offering; siblings remain; audit/outbox retained; automatic success verifies semantic absence | `400`, `404`, `412`, `428`, `503`; do not repeat after confirmed absence |

Lifecycle read/write authentication is deployment-configurable. The approved
pilot/plenary profile may set lifecycle auth and actor requirements off, but the
secure implementation and secure defaults remain. Do not send invented bearer
or actor values in that no-auth profile. PATCH requires `If-Match` when
`MDC_PROVIDER_CONCURRENCY_REQUIRED=True`; DELETE always requires it.

## Quick start

1. Call filters and build requests only from returned controlled values.
2. Validate the complete provider body without mutation.
3. Register one provider and its first offering. Retain `provider_id`,
   `offering_id`, `publication_id`, receipt statuses, and provider `ETag`.
4. GET the provider and retain the latest strong `ETag`.
5. POST a second offering with a distinct ID, even when its category matches.
6. GET before PATCH; send the current `If-Match`; retain the returned ETag.
7. Remove an optional map member by resending the whole selected map without
   that member and with every sibling that must remain.
8. Only after a `completed/synced/succeeded` receipt, run canonical search and
   verify the exact provider/offering IDs.
9. GET the second offering, DELETE with its current ETag, and verify its sibling
   remains in search.
10. GET the provider, DELETE with its current ETag, and verify every disposable
    offering disappears.

Use a disposable identifier such as `marketplace_m6_20260929_001`; never use a
real provider for integration testing.

## Stable request examples

### Registration

```json
{
  "contract_version": "1.0",
  "provider_id": "marketplace_m6_20260929_001",
  "provider_name": "Marketplace M6 Disposable Works",
  "country": "Finland",
  "offerings": [
    {
      "offering_id": "marketplace_m6_20260929_001_bracket_primary",
      "service_category": "precision_metal_parts",
      "offering_name": "Disposable bracket cell",
      "part_family": "metal_part",
      "support_status": "confirmed",
      "supported_part_types": [
        {
          "part_type": "bracket",
          "support_status": "confirmed",
          "source_type": "provider_confirmed",
          "confidence": "declared"
        }
      ],
      "family_capabilities": {},
      "part_type_capabilities": {
        "bracket": {
          "horizontal_flange_length_mm": {
            "max": 140,
            "source_type": "provider_confirmed",
            "confidence": "declared"
          },
          "vertical_flange_length_mm": {
            "max": 75,
            "source_type": "provider_confirmed",
            "confidence": "declared"
          }
        }
      },
      "generic_capabilities": {},
      "custom_offering_fields": {},
      "custom_capability_fields": {}
    }
  ]
}
```

### Second same-category offering

```json
{
  "offering_id": "marketplace_m6_20260929_001_bracket_flexible",
  "service_category": "precision_metal_parts",
  "offering_name": "Disposable flexible bracket cell",
  "part_family": "metal_part",
  "support_status": "confirmed",
  "supported_part_types": [
    {
      "part_type": "bracket",
      "support_status": "confirmed",
      "source_type": "provider_confirmed",
      "confidence": "declared"
    }
  ],
  "family_capabilities": {},
  "part_type_capabilities": {
    "bracket": {
      "horizontal_flange_length_mm": {
        "max": 160,
        "source_type": "provider_confirmed",
        "confidence": "declared"
      },
      "vertical_flange_length_mm": {
        "max": 80,
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

### Provider PATCH

```json
{
  "provider_name": "Marketplace M6 Disposable Works Updated",
  "custom_provider_fields": {"marketplace_reference": "joint-test"}
}
```

### Offering PATCH

```json
{
  "offering_name": "Disposable flexible bracket cell updated",
  "part_type_capabilities": {
    "bracket": {
      "horizontal_flange_length_mm": {
        "max": 180,
        "source_type": "provider_confirmed",
        "confidence": "declared"
      },
      "vertical_flange_length_mm": {
        "max": 90,
        "source_type": "provider_confirmed",
        "confidence": "declared"
      }
    }
  }
}
```

### Whole-selected-map attribute removal

This removes `vertical_flange_length_mm` and retains the horizontal sibling:

```json
{
  "part_type_capabilities": {
    "bracket": {
      "horizontal_flange_length_mm": {
        "max": 180,
        "source_type": "provider_confirmed",
        "confidence": "declared"
      }
    }
  }
}
```

### Canonical search

```json
{
  "contract_version": "1.0",
  "request_id": "marketplace_request_001",
  "consumer_id": "maasai_marketplace",
  "service_category": "precision_metal_parts",
  "part_family": "metal_part",
  "part_type": "bracket",
  "requirements": {
    "part_family_specifications": {},
    "part_type_specifications": {
      "horizontal_flange_length_mm": {"max": 170}
    },
    "generic_requirements": {}
  }
}
```

A matching response contains offering-level identity, never category-as-ID:

```json
{
  "contract_version": "1.0",
  "request_id": "marketplace_request_001",
  "service_category": "precision_metal_parts",
  "part_family": "metal_part",
  "part_type": "bracket",
  "result_count": 1,
  "results": [
    {
      "provider_id": "marketplace_m6_20260929_001",
      "provider_name": "Marketplace M6 Disposable Works Updated",
      "offering_id": "marketplace_m6_20260929_001_bracket_flexible",
      "offering_name": "Disposable flexible bracket cell updated",
      "service_category": "precision_metal_parts",
      "part_family": "metal_part",
      "match": {"status": "full_match", "score": 1.0},
      "matched_capabilities": [],
      "unmatched_capabilities": [],
      "unknown_capabilities": []
    }
  ]
}
```

## Receipts and deletion

Verified automatic success keeps the operation's normal `201` or `200`:

```json
{
  "contract_version": "1.0",
  "status": "completed",
  "operation": "update",
  "provider_id": "marketplace_m6_20260929_001",
  "publication_id": "00000000-0000-0000-0000-000000000001",
  "publication_status": "synced",
  "sync_status": "succeeded",
  "offering_ids": ["marketplace_m6_20260929_001_bracket_flexible"]
}
```

When automatic mode is disabled, a committed write can return the normal
operation status with `accepted/sync_pending/pending`. When automatic mode is
enabled but verification does not complete, the receipt is `503` and can be
`accepted/sync_failed/failed` or `accepted/sync_pending/pending`:

```json
{
  "contract_version": "1.0",
  "status": "accepted",
  "operation": "create",
  "provider_id": "marketplace_m6_20260929_001",
  "publication_id": "00000000-0000-0000-0000-000000000002",
  "publication_status": "sync_failed",
  "sync_status": "failed",
  "offering_ids": ["marketplace_m6_20260929_001_bracket_primary"],
  "error": {
    "code": "catalogue_publication_incomplete",
    "message": "The lifecycle change is committed, but authoritative catalogue publication is not complete. Automated recovery can retry the recorded publication without repeating the lifecycle mutation."
  }
}
```

DELETE sends no body and requires the current strong ETag:

```http
DELETE {{base_url}}/api/offerings/marketplace_m6_20260929_001_bracket_flexible
If-Match: "current-strong-etag"
```

```json
{
  "contract_version": "1.0",
  "status": "completed",
  "operation": "delete",
  "target": {
    "entity_type": "offering",
    "entity_id": "marketplace_m6_20260929_001_bracket_flexible"
  },
  "provider_id": "marketplace_m6_20260929_001",
  "publication_id": "00000000-0000-0000-0000-000000000003",
  "publication_status": "synced",
  "sync_status": "succeeded"
}
```

Provider deletion uses the same pattern and additionally returns the removed
`offering_ids`.

## Error examples

Errors include `contract_version` and a redacted `error` object. Representative
classes are:

```json
{"contract_version":"1.0","error":{"code":"invalid_provider_publication","message":"The provider publication payload is invalid.","details":{}}}
```

```json
{"contract_version":"1.0","error":{"code":"provider_not_found","message":"The requested provider was not found."}}
```

```json
{"contract_version":"1.0","error":{"code":"offering_already_exists","message":"The offering is already registered."}}
```

```json
{"contract_version":"1.0","error":{"code":"offering_precondition_failed","message":"The requested offering changed after it was retrieved; fetch the current representation and retry."}}
```

```json
{"contract_version":"1.0","error":{"code":"concurrency_precondition_required","message":"If-Match is required for this lifecycle write."}}
```

```json
{"contract_version":"1.0","error":{"code":"service_discovery_search_unavailable","message":"Service-discovery search is temporarily unavailable."}}
```

These correspond to `400`, `404`, `409`, `412`, `428`, and `503`. `401` is
missing/invalid trusted credentials when auth is enabled; `403` is a disabled
lifecycle feature. Never infer commit outcome from the HTTP class alone: for a
lifecycle `503`, inspect the returned receipt and GET current operational state.
