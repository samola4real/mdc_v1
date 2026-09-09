# MDC v1 — M7.6 External Exposure Readiness

## Execution intent

Implement and verify **M7.6 only**. Do not start a later milestone automatically.

Repository: `samola4real/mdc_v1`
Project root: `mdc-catalog/`

M7.5 is accepted. PostgreSQL is the durable operational source of truth for provider lifecycle state, and RDF/Fuseki synchronization is implemented through a durable outbox and an operator/scheduler-invoked management command. The service-discovery runtime remains unchanged.

The purpose of M7.6 is to make the provider lifecycle suitable for a trusted Marketplace/service-to-service integration without making anonymous provider lifecycle operations public.

## Non-negotiable architecture

Preserve:

```text
Marketplace / trusted MaaSAI service
        |
        | authenticated service-to-service lifecycle requests
        v
Django / DRF
        |
        v
PostgreSQL operational source of truth
        |
        v
CatalogueSyncEvent outbox
        |
        v
RDF/Fuseki semantic catalogue
```

The future hosting target is AWS, but the current pilot may use Vercel + managed PostgreSQL. Application code must remain cloud-provider neutral. Do not introduce Neon-specific, Vercel-specific, or AWS-specific domain logic.

## Stable API rules

Do not change the canonical public discovery routes:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Do not introduce `/api/v1/...` routes. Continue using `contract_version: "1.0"` metadata.

Provider lifecycle routes remain the existing unversioned routes:

```text
POST  /api/provider-publication/validation
POST  /api/provider-publication
GET   /api/providers/{provider_id}
PATCH /api/providers/{provider_id}
GET   /api/providers/{provider_id}/offerings
POST  /api/providers/{provider_id}/offerings
GET   /api/offerings/{offering_id}
PATCH /api/offerings/{offering_id}
```

These routes are trusted-integration APIs. They are **not anonymous public Marketplace APIs**.

## 1. Trusted service-to-service authorization boundary

Add a small cloud-neutral authentication boundary for provider lifecycle routes only.

Recommended pilot contract:

```text
Authorization: Bearer <MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN>
X-MDC-Actor-Id: <Marketplace/user/service actor identifier>
```

Requirements:

- Use constant-time token comparison.
- Never log, return, commit, or persist the bearer token.
- Token comes only from environment/secrets.
- Public discovery endpoints must remain unaffected.
- When lifecycle auth is required but the configured token is missing, fail closed with a safe service-unavailable response.
- Missing/invalid bearer credentials return a safe 401 response without revealing token details.
- For accepted lifecycle writes, require a safe actor identifier when configured to do so and persist it into `ProviderPublication.submitted_by_external_id`.
- Validate actor IDs conservatively: non-empty, bounded length, no control/NUL characters.
- The actor header is attribution metadata, not an authorization policy by itself.
- Keep the auth helper replaceable so a later Marketplace OAuth/JWT/API-gateway identity can replace the shared-token pilot without changing provider models or lifecycle semantics.

Recommended settings:

```text
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED
MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED
```

Safe defaults:

- base/local may default auth-required to false for existing developer workflows;
- production must default auth-required to true;
- production must never silently allow anonymous lifecycle access because a token is absent.

`MDC_PROVIDER_PUBLICATION_ENABLED=False` remains the production default until an explicit enablement decision after verification.

## 2. Optimistic concurrency for PATCH lifecycle operations

The current transactional row locks protect database writes but do not protect an external editor from overwriting a newer state prepared by another client.

Add lightweight HTTP ETag/If-Match support without redesigning the schema.

Requirements:

- Provider detail GET returns an `ETag` header derived from the provider aggregate revision.
- Offering detail GET returns an `ETag` header derived from the offering revision.
- Do not expose raw internal timestamps/UUIDs in response bodies.
- Provider aggregate revision must change when provider fields, certifications, offering creation, or offering summary-visible fields change.
- Offering revision must change when an offering is patched.
- PATCH can validate `If-Match` against the row after `select_for_update()` locking.
- A stale `If-Match` returns HTTP 412 with a stable safe error code.
- If concurrency preconditions are configured as required and `If-Match` is missing, return HTTP 428.
- Successful PATCH responses should return the new `ETag` header.
- Preserve existing PATCH semantics and immutable identifiers.

Recommended setting:

```text
MDC_PROVIDER_CONCURRENCY_REQUIRED
```

Production should default this to true. Base/local may default false so existing internal tests remain backwards compatible while M7.6 tests explicitly verify the required mode.

## 3. Actor-aware publication history

Every accepted registration/update/offering write already creates one `ProviderPublication`.

Extend write-service calls so the trusted actor ID from the request is persisted to:

```text
ProviderPublication.submitted_by_external_id
```

Requirements:

- no migration should be needed because the field already exists;
- validation-only requests remain non-mutating;
- rejected/disabled/unauthorized requests create no publication history;
- actor attribution must not be accepted from the JSON body as a provider-controlled field.

## 4. Stale outbox processing recovery

M7.5 documents that a process terminated after claiming events can leave them in `processing`.

Implement explicit lease/timeout recovery using existing `CatalogueSyncEvent.processed_at` / event timestamps; add a migration only if existing fields cannot safely express the recovery state.

Requirements:

- recover only genuinely stale `processing` events older than a configurable threshold;
- mark recovered events `failed` with a fixed safe code such as `processing_lease_expired`;
- set the publication to `sync_failed`, `completed_at = null`;
- recovered events must become eligible for an ordinary retry;
- never reset `attempt_count`;
- never recover fresh processing rows;
- recovery must be transactional and concurrency-safe;
- expose recovery through the existing internal synchronization management command, not a public HTTP route.

Recommended setting:

```text
MDC_CATALOG_SYNC_PROCESSING_LEASE_SECONDS
```

Recommended command mode:

```text
python manage.py sync_service_discovery_catalogue --recover-stale
```

Keep it explicit and safe. It must not contact Fuseki merely to recover database state.

## 5. Error contract and exposure hardening

Review provider lifecycle responses to ensure:

- 400 invalid payload;
- 401 missing/invalid trusted credential when auth is required;
- 403 feature disabled;
- 404 unknown provider/offering;
- 409 duplicate identity conflict;
- 412 stale If-Match;
- 428 missing required If-Match;
- redacted 503 for unavailable auth configuration or persistence failures.

No response may expose SQL, filesystem paths, stack traces, endpoint credentials, environment values, bearer tokens, internal provider/offering UUIDs, or sync-event UUIDs.

## 6. Production safety configuration

Update `.env.example`, base settings, and production settings.

Production requirements:

```text
MDC_PROVIDER_PUBLICATION_ENABLED=False
MDC_PROVIDER_VALIDATION_ENABLED=False
MDC_CATALOG_SYNC_ENABLED=False
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
```

Do not put a real token in `.env.example`.

The presence of lifecycle code must not mean lifecycle write exposure is enabled.

## 7. Partner/trusted integration documentation

Create/update a concise partner-facing trusted lifecycle integration document describing:

- canonical discovery routes;
- trusted lifecycle routes;
- stable unversioned URL strategy + `contract_version`;
- bearer service credential requirement for lifecycle routes;
- `X-MDC-Actor-Id` attribution on writes;
- GET `ETag` + PATCH `If-Match` behavior;
- publication/sync-pending semantics;
- safe retry expectation;
- lifecycle APIs remain trusted-service APIs, not direct anonymous browser endpoints;
- actual secrets must be supplied out-of-band through deployment secret management.

Do not document internal SQL/models/UUIDs or credential values.

## 8. Tests

Add focused tests covering at least:

### Trusted boundary
- public discovery works without lifecycle token;
- lifecycle GET/validation/write protected when auth required;
- invalid token rejected;
- missing server token fails closed;
- valid token accepted;
- actor required for writes when configured;
- actor attribution appears in `ProviderPublication`;
- token is never persisted.

### Concurrency
- GET provider/offering returns ETag;
- correct If-Match patch succeeds;
- stale If-Match returns 412 and does not mutate;
- missing required If-Match returns 428 and does not mutate;
- provider aggregate ETag changes after certification/provider/offering-visible changes;
- offering ETag changes after offering patch.

### Stale sync recovery
- fresh processing event untouched;
- stale processing event becomes failed/retryable;
- attempt count preserved;
- publication becomes sync_failed;
- recovery command does not contact Fuseki;
- retry after recovery can succeed through the normal M7.5 path.

### Non-regression
- no `/api/v1/...` lifecycle routes;
- provider publication remains production-disabled by default;
- no route/source switch for service discovery;
- no migration drift unless an intentional migration is required.

## 9. Verification gates

Run focused tests first.

Then verify against managed PostgreSQL using an isolated temporary test database where practical. Never reset/drop the configured catalogue database.

Then run:

```text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test -v 1
```

Run the separately maintained H1-H9 regression set and preserve existing optional remote Fuseki skips.

Do not perform a real remote Fuseki write merely to satisfy M7.6. Real deployment credentials/network policy can be verified separately.

## 10. Deployment/readiness gate

After code/test gates pass, prepare explicit deployment verification instructions for the temporary Vercel/managed-PostgreSQL pilot and the future AWS environment.

Do not make Vercel or Neon a permanent architecture dependency.

The final M7.6 report must state separately:

- code readiness;
- managed PostgreSQL verification;
- public discovery compatibility;
- trusted lifecycle protection;
- production-default feature flags;
- whether real remote Fuseki write authentication was exercised;
- whether provider lifecycle write exposure was actually enabled;
- remaining operational limitations.

## 11. Files/conventions

Preserve the project convention:

- GET handlers in `backend/apps/api/views/get_views.py`;
- POST/PATCH lifecycle handlers in `backend/apps/api/views/post_views.py`.

Prefer small dedicated helpers/services over adding more legacy logic to `backend/apps/api/views.py`.

Do not modify unrelated user files. Do not commit `.env`, `.env.local`, database artifacts, credentials, generated RDF, temporary harnesses, or secret-bearing output.

## 12. Report

Create:

```text
mdc-catalog/docs/Phase_2/17_mdc_v1_m76_external_exposure_readiness_report.md
```

Do not start another milestone automatically.

Successful completion marker:

```text
READY_FOR_M7_COMPLETION_REVIEW
```

## Standing Git authorization

For this repository, normal fast-forward milestone commits/pushes to `origin/main` are pre-authorized after required gates pass. Still stop for force-push, history rewrite, a different repository/branch target, unexpected unrelated files, secrets, destructive infrastructure/database operations, unresolved conflicts, or failed technical gates.
