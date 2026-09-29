# MaaSAI MDC M6 Marketplace joint-test checklist

Status: **prepared, not executed**. No Marketplace-originated client calls or
Marketplace environment were available during M6-A.

## Connection values

- Base URL: `https://<approved-mdc-backend>`
- Contract: `1.0`; paths are `/api/...`, never `/api/v1/...`.
- Profile: approved no-auth/no-actor pilot only. Do not add placeholder secrets.
- Generate one disposable lower-snake-case `provider_id` and two distinct
  provider-prefixed `offering_id` values.

Marketplace must retain between calls: provider ID, both offering IDs, every
`publication_id`, latest provider ETag, latest offering ETag, and the exact
search request/matches.

## Ordered joint test

| # | Marketplace request | Expected evidence to capture |
| ---: | --- | --- |
| 1 | `GET /api/health` | `200`, contract `1.0`, timestamp |
| 2 | `GET /api/catalog/filters` | `200`; selected category/family/type exist |
| 3 | `POST /api/service-discovery/search` | `200`; disposable ID absent; semantic service healthy |
| 4 | `POST /api/provider-publication/validation` | `200`, `valid=true`; no mutation |
| 5 | `POST /api/provider-publication` | `201`, exact IDs, publication ID, `completed/synced/succeeded`, ETag |
| 6 | Immediate canonical search | `200`; exact first offering ID appears. This is the first semantic-visibility proof |
| 7 | `GET /api/providers/{provider_id}` | `200`; save current provider ETag |
| 8 | `POST /api/providers/{provider_id}/offerings` | `201`; distinct second ID with same category; completed sync receipt |
| 9 | Immediate canonical search | Both offering IDs visible independently |
| 10 | PATCH provider with current `If-Match` | `200`; completed receipt and new ETag |
| 11 | GET then PATCH second offering with current `If-Match` | `200`; completed receipt and new ETag |
| 12 | Immediate canonical search | Updated searchable names/capabilities visible |
| 13 | PATCH whole selected map without one optional attribute | `200`; completed receipt; PostgreSQL GET omits it and retains sibling |
| 14 | Immediate requirement search | Retained attribute remains evidence; removed attribute is not positive evidence |
| 15 | Optional negative: PATCH with prior stale ETag | `412`; no mutation |
| 16 | Optional negative: DELETE without ETag | `428`; no mutation |
| 17 | GET then DELETE second offering | `200`; completed deletion receipt |
| 18 | Immediate canonical search | Deleted ID absent; first sibling present |
| 19 | GET then DELETE provider | `200`; completed deletion receipt and dependent IDs |
| 20 | Immediate canonical search and final GETs | No disposable matches; provider and both offerings return `404` |

Expected error classes are `400` invalid input/header format, `401` trusted
credential failure when enabled, `403` disabled feature, `404` absent resource,
`409` identity conflict, `412` stale ETag, `428` missing required ETag, and
`503` persistence/synchronization/search unavailable. For lifecycle `503`, save
the receipt and stop mutation replay. MDC operations must inspect committed
state and recover the recorded publication.

## Cleanup and acceptance evidence

Cleanup is part of the test, not an optional follow-up. Delete the second
offering first and prove the sibling remains, then delete the provider and prove
all disposable offerings disappear.

The joint test is accepted only when evidence contains:

- request name/order and UTC time;
- HTTP status and redacted response for every request;
- provider ID, both offering IDs and publication IDs;
- ETag presence and the value linkage between GET and conditional mutation
  (the raw value may be redacted consistently);
- search result rows proving immediate create/update visibility and delete
  absence;
- final `404` reads and cleanup confirmation;
- MDC operator confirmation that the outbox succeeded and the query-visible
  revision is current.

After execution, replace the status at the top with the date, Marketplace client
identity/team, target environment, evidence location, request/assertion totals,
and pass/fail result. Do not mark M6 complete before that evidence exists.
