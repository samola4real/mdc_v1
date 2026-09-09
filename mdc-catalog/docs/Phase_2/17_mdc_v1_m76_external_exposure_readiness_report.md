# MDC v1 M7.6 External Exposure Readiness Report

## Outcome

M7.6 is complete at the code/readiness level. The provider lifecycle is now protected behind a replaceable trusted service-to-service boundary suitable for MaaSAI Marketplace integration, while the established public discovery API remains unchanged.

The milestone does **not** enable provider lifecycle writes in production. Production defaults still keep publication, validation, and catalogue synchronization disabled. Real remote Fuseki write authentication/network policy was not exercised. M7.6 therefore establishes a safe external-integration boundary and deployment-readiness baseline without turning the lifecycle routes into anonymous public APIs.

Completion marker:

```text
READY_FOR_M7_COMPLETION_REVIEW
```

## Architecture preserved

```text
Marketplace / trusted MaaSAI service
        |
        | trusted service credential + actor attribution
        v
Django / DRF lifecycle boundary
        |
        +--> PostgreSQL operational source of truth
        |
        +--> ProviderPublication audit/history
        |
        +--> CatalogueSyncEvent outbox
                  |
                  v
             RDF / Fuseki
```

The implementation remains cloud-provider neutral. The temporary pilot may use Vercel + managed PostgreSQL, while the future target may move to AWS without changing provider models, API routes, publication semantics, or the PostgreSQL/RDF split.

## Stable API contract

The canonical public discovery routes remain unchanged:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

Provider lifecycle routes remain the existing stable unversioned routes:

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

No `/api/v1/...` lifecycle or discovery routes were introduced. Contract evolution continues through `contract_version: "1.0"` metadata rather than URL versioning.

## Trusted lifecycle authentication

M7.6 adds a small replaceable trusted service boundary for provider lifecycle routes.

Pilot request contract:

```text
Authorization: Bearer <service credential>
X-MDC-Actor-Id: <trusted upstream actor identifier>
```

The service token is loaded only from environment/secret configuration and is compared in constant time. Missing or invalid client credentials return a safe 401. If authentication is required but the server credential is absent, the lifecycle boundary fails closed with a safe 503 rather than allowing anonymous access.

Public discovery endpoints do not require this lifecycle credential.

The shared-token mechanism is deliberately isolated so a later Marketplace OAuth/JWT/API-gateway identity can replace it without changing provider persistence or lifecycle semantics.

## Actor attribution

Accepted registration/update/offering writes persist the trusted upstream actor into:

```text
ProviderPublication.submitted_by_external_id
```

The actor identifier is taken from the trusted header, not from provider-controlled JSON. It is bounded and rejects control characters. Unauthorized, disabled, validation-only, rejected, or otherwise non-mutating requests do not create publication history.

The bearer credential itself is never persisted.

## Optimistic concurrency

M7.6 adds HTTP ETag/If-Match protection for provider/offering updates.

Provider and offering detail GET responses return an opaque strong `ETag` header. The value is not exposed as an internal timestamp or UUID in the response body.

When concurrency protection is required, PATCH clients must return the current ETag using:

```text
If-Match: "<opaque-etag>"
```

Behavior:

- correct current ETag -> PATCH may proceed;
- stale ETag -> HTTP 412 with a stable redacted error;
- missing required `If-Match` -> HTTP 428;
- malformed/weak/multi-value preconditions -> safe 400;
- successful PATCH -> new ETag returned.

Provider aggregate revision changes when representation-relevant provider, certification, offering-creation, or offering-summary state changes. Offering revision changes when the offering itself changes.

Database `select_for_update()` locking remains in place, so the external optimistic-concurrency guard complements rather than replaces transactional write locking.

## Stale outbox processing recovery

M7.5 documented the crash window where a worker/process could terminate after claiming an event and leave it in `processing`.

M7.6 adds explicit processing-lease recovery through the existing internal command:

```text
python manage.py sync_service_discovery_catalogue --recover-stale
```

Recovery behavior:

- only expired `processing` rows older than the configured lease are recovered;
- fresh processing rows are untouched;
- stale rows become `failed` with fixed safe code `processing_lease_expired`;
- publication becomes `sync_failed` with `completed_at = null`;
- `attempt_count` is preserved;
- recovered events become retryable through the ordinary M7.5 path;
- recovery is transactional/concurrency-safe;
- recovery itself does not contact Fuseki.

Configuration:

```text
MDC_CATALOG_SYNC_PROCESSING_LEASE_SECONDS
```

## Error contract

Trusted lifecycle routes now preserve the following external classes:

```text
400  invalid payload / actor metadata / precondition format
401  missing or invalid trusted credential
403  lifecycle feature disabled
404  provider or offering not found
409  duplicate provider/offering identity
412  stale If-Match revision
428  required If-Match missing
503  trusted auth configuration or persistence unavailable
```

Responses remain redacted and are not designed to expose SQL, filesystem paths, environment values, service credentials, internal database UUIDs, sync-event UUIDs, or stack traces.

## Production safety defaults

Production defaults are intentionally fail-closed:

```text
MDC_PROVIDER_PUBLICATION_ENABLED=False
MDC_PROVIDER_VALIDATION_ENABLED=False
MDC_CATALOG_SYNC_ENABLED=False
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
```

Therefore the presence of M7.6 code does not itself expose provider registration/update functionality.

A real lifecycle service token is not present in `.env.example` and must be supplied through deployment secret management.

## Trusted integration documentation

Partner/trusted-service documentation is available at:

```text
mdc-catalog/docs/partner_api/mdc_v1_trusted_provider_lifecycle_integration.md
```

It documents the stable public discovery routes, trusted lifecycle routes, bearer-service boundary, actor attribution, ETag/If-Match workflow, publication/sync-pending semantics, retry behavior, and secret-management expectations without exposing internal SQL/model identifiers or credential values.

## Verification

### Focused SQLite gate

```text
64 tests run
64 passed
0 failed
```

This covered the M7.6 trusted boundary, actor attribution, optimistic concurrency, stale-sync recovery, provider lifecycle reads/writes, M7.5 sync behavior, and configuration safety.

### Managed PostgreSQL gate

```text
98 tests run
98 passed
0 failed
```

The test suite used Django's isolated PostgreSQL test database. The tests themselves completed successfully. Neon temporarily retained one session to Django's generated `test_neondb`, causing only teardown/drop to fail after the test result had already reported `OK`.

The leftover `test_neondb` was then explicitly deleted through Neon. Post-cleanup verification confirmed the validation project retained only:

```text
neondb
mdc_validation
```

The configured `mdc_validation` catalogue database was preserved.

### Full local regression

```text
manage.py check: PASS
makemigrations --check --dry-run: PASS, no changes detected
537 tests run
528 passed
0 failed
9 existing opt-in skips
```

During the full suite the existing harmonized RDF generator produced the accepted 673-triple catalogue.

### Maintained H1-H9 regression

```text
230 tests run
225 passed
0 failed
5 existing opt-in remote Fuseki skips
```

H1-H9 behavior therefore remains aligned after M7.6.

## Public discovery compatibility

M7.6 did not change the canonical service-discovery runtime selection or public discovery contract. Public health, filter, and service-discovery search remain outside the lifecycle bearer boundary.

Provider lifecycle GET/validation/write operations are the trusted-integration surface and are protected when the M7.6 auth setting is enabled.

## Deployment/readiness gate

M7.6 prepares, but does not automatically perform, lifecycle exposure.

For the temporary Vercel + managed-PostgreSQL pilot, the safe deployment sequence is:

1. Deploy the M7.6 code with production settings.
2. Keep `MDC_PROVIDER_PUBLICATION_ENABLED=False`, `MDC_PROVIDER_VALIDATION_ENABLED=False`, and `MDC_CATALOG_SYNC_ENABLED=False` initially.
3. Configure `MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True`, `MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True`, and `MDC_PROVIDER_CONCURRENCY_REQUIRED=True`.
4. Store the lifecycle service token only in Vercel secret/environment configuration; never in Git or frontend code.
5. Verify public discovery routes still work anonymously.
6. Verify lifecycle routes reject missing/invalid credentials.
7. Only after a deliberate pilot enablement decision, enable validation/publication for the trusted Marketplace integration.
8. Configure semantic-sync credentials/network policy separately before enabling real Fuseki writes.

For the future AWS deployment, retain the same environment-variable contract and Django/PostgreSQL/RDF architecture. The shared-token pilot may be replaced by Marketplace OAuth/JWT/API Gateway/IAM-backed identity at the lifecycle-security helper boundary without redesigning the provider lifecycle model.

## Exposure status at milestone completion

- Code readiness: **PASS**
- Managed PostgreSQL verification: **PASS**
- Public discovery compatibility: **PASS**
- Trusted lifecycle protection: **PASS**
- Production fail-closed defaults: **PASS**
- H1-H9 non-regression: **PASS**
- RDF parity/baseline: **673 triples preserved**
- Real remote Fuseki write authentication exercised: **NO**
- Provider lifecycle write exposure enabled in production: **NO**
- Vercel lifecycle write deployment enabled: **NO**

These `NO` items are deliberate safety boundaries, not failed M7.6 gates.

## Known operational limitations

- The current lifecycle bearer token is a pilot service-to-service mechanism, not the final Marketplace identity architecture.
- Token rotation/revocation orchestration is operational rather than domain-model logic.
- Synchronization remains operator/scheduler-invoked; M7.6 does not add a permanent worker scheduler or monitoring platform.
- Whole-graph Fuseki replacement remains the current correctness-first catalogue-size strategy.
- Real Fuseki write credentials, authentication mode, and production network policy still require environment-specific verification.
- Rate limiting, WAF/API-gateway policy, centralized audit export, monitoring/alerting, and production secret-rotation procedures belong to deployment/operations hardening.
- Future AWS hosting remains an infrastructure migration target; Vercel and Neon are temporary pilot infrastructure rather than permanent architectural dependencies.

## M7 status

With M7.6 complete, the M7 persistence/provider-lifecycle sequence is technically complete:

```text
M7.1  PostgreSQL/Django foundation                  COMPLETE
M7.2  harmonized DB repository + migration          COMPLETE
       managed PostgreSQL validation                COMPLETE
M7.3  validation + DB-backed lifecycle reads        COMPLETE
M7.4  registration/update lifecycle                 COMPLETE
M7.5  RDF/Fuseki synchronization                    COMPLETE
M7.6  external exposure readiness                   COMPLETE
```

Next action is an M7 completion review rather than automatic implementation of another milestone.

```text
READY_FOR_M7_COMPLETION_REVIEW
```
