# MDC Infrastructure Portability Decision

**Date:** 2026-09-09  
**Project:** MaaSAI MaaS Dynamic Catalogue (MDC)  
**Related milestone:** M7 — Persistence and Provider Lifecycle

---

## Decision

The long-term deployment target for the MaaSAI Marketplace, MDC, and related catalogue services is AWS.

The current Vercel deployment and the proposed Neon PostgreSQL connection are temporary pilot/development infrastructure used to accelerate the current MDC implementation and verification work. They are not intended to become permanent architectural dependencies.

The durable architectural choices are therefore:

```text
Application/API layer: Django / DRF
Operational persistence: PostgreSQL
Semantic layer: RDF + Apache Jena Fuseki
API contract: stable /api/... URLs + contract_version metadata
```

The temporary/current hosting arrangement is:

```text
Django API -> Vercel
PostgreSQL -> Neon (pilot candidate)
```

The future integrated deployment is expected to be:

```text
Marketplace + MDC + related catalogue services -> AWS
PostgreSQL -> AWS-hosted PostgreSQL service selected by the deployment/platform architecture
RDF/Fuseki -> AWS-hosted deployment as appropriate
```

No specific AWS PostgreSQL product is locked in by this decision. The implementation must remain compatible with standard PostgreSQL so that deployment can later use an AWS-managed PostgreSQL option without redesigning the MDC data model or API layer.

---

## Portability Requirements

M7 and later persistence work must follow these rules:

1. Use Django ORM and standard PostgreSQL features as the primary persistence abstraction.
2. Configure the database through environment variables, primarily `DATABASE_URL` or equivalent deployment configuration.
3. Do not introduce Neon-specific SDKs, APIs, database extensions, branch semantics, or application-level dependencies unless they are optional operational tooling only.
4. Do not introduce Vercel-specific application logic into provider lifecycle, persistence, H1-H9 matching, RDF generation, or API contracts.
5. Keep credentials, hostnames, and cloud-provider configuration outside source code.
6. Preserve the ability to move from the current Vercel/Neon pilot setup to AWS through deployment/configuration changes rather than domain-model or API redesign.
7. PostgreSQL remains the operational source-of-truth technology; the cloud hosting provider may change.
8. RDF/Fuseki remains the semantic catalogue layer and is independent of the temporary hosting provider.

---

## M7.1 Consequence

M7.1 should build a **cloud-provider-neutral PostgreSQL/Django foundation**.

Neon compatibility is useful for the current pilot because MDC is presently deployed on Vercel, but Neon must be treated only as one temporary PostgreSQL host.

The M7.1 database configuration should therefore behave conceptually as:

```text
DATABASE_URL absent
        -> SQLite fallback for local/current compatibility

DATABASE_URL points to standard PostgreSQL
        -> Django PostgreSQL configuration
```

The application must not need to know whether the PostgreSQL connection is provided by Neon today or an AWS PostgreSQL service later.

---

## Migration Principle

The intended future infrastructure transition should be operational rather than architectural:

```text
Current pilot
Vercel + Neon PostgreSQL
        |
        | deployment migration
        v
Future MaaSAI platform
AWS + AWS-hosted PostgreSQL
```

The following should remain unchanged through that migration where possible:

- Django models;
- provider lifecycle domain logic;
- harmonized provider/offering schema;
- external API contracts;
- H1-H9 matching semantics;
- RDF generation semantics;
- PostgreSQL-backed publication history and outbox model.

This portability decision supersedes any wording that could be interpreted as making Vercel or Neon permanent MDC architecture components.
