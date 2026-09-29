# MaaSAI MDC M6 plenary demonstration runbook

This runbook demonstrates the frozen MDC `1.0` API with disposable data. It
does not describe an internal Django implementation and does not authorize a
Production deployment.

## Preconditions and go/no-go check

The MDC operator must confirm every item before the presenter starts:

- reviewed `{{base_url}}` is deployed and explicitly approved for lifecycle
  mutation;
- PostgreSQL is reachable, backed up as required, and has zero pending
  migrations;
- durable protected Fuseki query and default-graph Graph Store URLs resolve to
  the same origin and dataset;
- `MDC_PROVIDER_PUBLICATION_ENABLED=True`;
- `MDC_PROVIDER_VALIDATION_ENABLED=True`;
- `MDC_CATALOG_SYNC_ENABLED=True`;
- `MDC_CATALOG_AUTO_SYNC_ENABLED=True`;
- `MDC_PROVIDER_CONCURRENCY_REQUIRED=True`;
- approved pilot values for lifecycle auth and actor requirements are recorded;
  the M6 Postman package assumes both are `False` only when that exception is
  explicitly approved;
- `MDC_DEMO_API_ENABLED=False`;
- an operator-owned retry/monitoring path for pending/failed outbox work is
  active;
- no secret value will be shown in Postman, screenshots, logs, or plenary
  slides.

Preflight must return `200` from health and filters. Canonical search must
return `200` and a contract `1.0` response before any write. If it returns
`503`, stop; do not create demo data while semantic visibility is unhealthy.

Use a unique ID such as `marketplace_m6_<date>_<suffix>`. Confirm GET provider
returns `404` before registration. Record status, response, identifiers, ETags,
and search evidence for every step.

## Demonstration sequence

| Step | Request | Expected status | Presenter verifies |
| ---: | --- | --- | --- |
| 1 | `GET /api/health` | `200` | `contract_version=1.0`, `status=ok` |
| 2 | `GET /api/catalog/filters` | `200` | Intended service category/family/type appear in controlled values |
| 3 | Canonical search | `200` | Search is available; disposable ID is absent |
| 4 | Validate provider body | `200` | `valid=true`; normalized payload contains intended provider/offering IDs |
| 5 | Register provider + first offering | `201` | Receipt is `completed/synced/succeeded`; capture publication ID and provider ETag |
| 6 | Immediate canonical search | `200` | Exact first `offering_id` appears for the exact `provider_id` |
| 7 | POST second same-category offering | `201` | Distinct offering ID; `completed/synced/succeeded` |
| 8 | Immediate canonical search | `200` | Both IDs appear independently, despite identical category |
| 9 | GET then PATCH provider/offering | `200` / `200` | GET supplies current ETag; PATCH supplies `If-Match`; receipt completes; new ETag captured |
| 10 | Immediate canonical search | `200` | Updated provider/offering display value is visible |
| 11 | PATCH a selected map without one optional attribute | `200` | Whole selected map retains intended sibling and omits removed attribute; receipt completes |
| 12 | Immediate requirement search | `200` | Retained field matches and removed field is no longer positive evidence |
| 13 | GET then DELETE second offering | `200` / `200` | Current ETag used; deletion receipt completes |
| 14 | Immediate canonical search | `200` | Deleted offering absent; first sibling still present |
| 15 | GET then DELETE provider | `200` / `200` | Current provider ETag used; receipt lists dependent offering IDs and completes |
| 16 | Immediate canonical search and GET checks | `200`, then `404` | No result for disposable provider; provider and both offering GETs are absent |

Do not advance to the next search until the mutation receipt is
`completed/synced/succeeded`. A normal-looking response with pending/failed sync
is not semantic success.

## Recovery and failure procedure

### Lifecycle response is 503 after PostgreSQL commit

1. Save `publication_id`, `provider_id`, `offering_id`, operation, publication
   status, and sync status from the response.
2. Do not repeat registration, offering creation, PATCH, or DELETE.
3. GET the provider/offering to determine the committed operational state. A
   resource present after a create/update or absent after DELETE is evidence
   that PostgreSQL committed even though semantic publication did not finish.
4. Give the publication ID to the MDC operator. Marketplace does not call a
   recovery endpoint.
5. The operator inspects `ProviderPublication` and `CatalogueSyncEvent` state
   and confirms whether work is pending, failed, or already succeeded.
6. After correcting Fuseki/configuration, the operator safely runs the existing
   idempotent recovery command for the specific publication:

   ```text
   python manage.py sync_service_discovery_catalogue --publication-id <uuid>
   ```

   The command is an operator interface, never a Marketplace API.
7. The operator confirms the event succeeded and the query-visible catalogue
   revision equals the current PostgreSQL watermark.
8. Marketplace repeats only the safe GET/search verification, not the original
   write.

For a backlog of pending/failed events, the operator may run the command's
reviewed batch mode according to the deployment runbook. One scheduler/worker
must own this responsibility; plenary presenters must not improvise it.

### Stale or missing ETag

- `428`: GET the resource, capture its current strong ETag, review the latest
  representation, then retry once with `If-Match`.
- `412`: another write won. GET again, reconcile the intended change with the
  current representation, then send a new PATCH/DELETE only if still correct.
- Never replace the header with `*`, a weak ETag, or a comma-separated list.

### Fuseki unavailable or revision mismatch

- Stop lifecycle demonstrations; do not weaken authoritative search or switch
  to checked-in RDF/YAML.
- Confirm query and Graph Store endpoint shapes select the same dataset.
- Confirm network reachability and Graph Store credentials without printing
  them.
- Treat a Graph Store `200` as insufficient until the revision is visible from
  the canonical query endpoint.
- Restore service, process recorded outbox work, verify revision visibility,
  then resume with safe reads/search.

### Cleanup interrupted

GET each disposable resource. If it exists, obtain its current ETag and use the
normal public DELETE route. If a DELETE returns a post-commit sync `503`, follow
the recovery sequence and verify absence; do not blindly repeat DELETE. Never
clean operational rows with direct SQL.

## Evidence package

Retain a redacted export containing request name/time, HTTP status, response
body, provider/offering IDs, publication ID, ETag presence, and search matches.
Exclude database URLs, bearer tokens, Fuseki credentials, Vercel credentials,
and environment dumps. Mark the demonstration incomplete if cleanup or the
final revision/search proof is missing.
