# MaaSAI MDC v1 — Trusted Provider Lifecycle Integration

## Purpose

This document describes the MDC interfaces intended for integration with the MaaSAI Marketplace or another trusted MaaSAI service.

MDC uses stable, unversioned `/api/...` URLs. The current contract metadata value is:

```json
{"contract_version": "1.0"}
```

Do not call `/api/v1/...` routes; they are not part of the MDC contract.

## Public discovery interfaces

The established discovery interfaces remain:

```text
GET  /api/health
GET  /api/catalog/filters
POST /api/service-discovery/search
```

These interfaces are separate from provider lifecycle administration and do not require the M7.6 trusted lifecycle bearer credential.

## Trusted provider lifecycle interfaces

The following routes are intended for a trusted Marketplace/service integration, not direct anonymous browser access:

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

### Authentication

When the trusted lifecycle boundary is enabled, send:

```text
Authorization: Bearer <service credential>
```

The credential is issued/configured out-of-band and must be stored in the Marketplace/deployment secret-management system. It must never be embedded in frontend JavaScript, source control, screenshots, provider payloads, or ordinary API documentation.

The current shared bearer token is a pilot service-to-service boundary. It is intentionally isolated behind an MDC helper so a later Marketplace OAuth/JWT/API-gateway identity can replace it without changing provider persistence or lifecycle semantics.

### Actor attribution on writes

Trusted write requests should send:

```text
X-MDC-Actor-Id: <trusted Marketplace/user/service actor identifier>
```

MDC stores this value in the accepted publication history so a persisted change can be traced to the trusted upstream actor. The actor identifier is attribution metadata; it is not itself a bearer credential and must not contain secrets.

## Provider registration

```text
POST /api/provider-publication
```

The request uses the harmonized provider-publication contract. Provider-supplied business/free-text information that is not an official MDC controlled vocabulary value belongs in the supported `custom_*` staging fields rather than being promoted into controlled search fields.

A successful registration is persisted transactionally in PostgreSQL. MDC creates publication history and pending semantic synchronization events. The response can therefore report a state such as:

```text
publication_status: sync_pending
sync_status: pending
```

This means the operational provider state is durable even though RDF/Fuseki convergence is still pending.

## Validation-only request

```text
POST /api/provider-publication/validation
```

This validates/normalizes the provider publication payload without changing PostgreSQL, YAML, RDF, Fuseki, publication history, or sync events.

## Provider/offering reads

```text
GET /api/providers/{provider_id}
GET /api/providers/{provider_id}/offerings
GET /api/offerings/{offering_id}
```

Provider and offering detail responses do not expose internal database UUIDs or timestamps.

Provider detail and offering detail return an HTTP `ETag` header representing the current external lifecycle revision.

Example:

```text
ETag: "<opaque revision>"
```

Treat the ETag as opaque. Do not derive business meaning from it.

## Safe PATCH updates

```text
PATCH /api/providers/{provider_id}
PATCH /api/offerings/{offering_id}
```

When optimistic concurrency is required, first retrieve the current entity and then send its ETag back in:

```text
If-Match: "<ETag from GET>"
```

Successful PATCH responses return the new ETag.

Important responses:

```text
412  entity changed after the client's GET; fetch again and retry
428  If-Match is required but missing
```

This prevents a stale edit screen from silently overwriting a newer accepted update.

## Adding an offering

```text
POST /api/providers/{provider_id}/offerings
```

The provider identity comes from the path. MDC owns/generates the offering identifier. Client-supplied `provider_id` or MDC-owned `offering_id` values are rejected in the offering body.

## Error semantics

Trusted lifecycle clients should handle these HTTP classes:

```text
400  invalid payload/metadata/precondition format
401  missing or invalid trusted service credential
403  lifecycle feature disabled in the target environment
404  provider/offering not found
409  duplicate provider/offering identity
412  stale If-Match revision
428  required If-Match missing
503  trusted auth configuration or persistence/synchronization service unavailable
```

Error responses are intentionally redacted and do not contain credentials, SQL, filesystem paths, internal database identifiers, or stack traces.

## Retry and synchronization expectations

Accepted provider writes are committed to PostgreSQL before asynchronous/operator semantic synchronization. Fuseki failure therefore does not erase the accepted operational state.

The M7 outbox records pending/failed synchronization work and supports retries. Integration clients should not repeatedly resubmit an accepted provider write merely because semantic synchronization is still pending. Use the publication/sync status returned by MDC and the agreed operational monitoring/retry mechanism.

## Deployment policy

For production-like environments:

- provider publication is disabled by default until explicit enablement;
- provider validation is disabled by default until explicit enablement;
- catalogue synchronization is disabled by default until explicit enablement;
- trusted lifecycle authentication defaults to required;
- actor attribution defaults to required for writes;
- optimistic concurrency defaults to required for PATCH.

The temporary pilot may run on Vercel + managed PostgreSQL. The future MaaSAI deployment may run on AWS. The API and persistence contract intentionally does not depend on either cloud provider.

## Secret exchange

Actual bearer credentials, database URLs, Fuseki credentials, and deployment secrets are not part of this document. Exchange and configure them only through the approved secret-management/operations channel.
