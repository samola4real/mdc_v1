# MDC v1 P3.6 — AWS Migration / Readiness Plan

## Status

**COMPLETE — PLANNING / READINESS MILESTONE.**

P3.5 completed the functional Phase 3 pilot proof. P3.6 defines how the current temporary Vercel + Neon + temporary/local Fuseki arrangement can move to AWS without redesigning MDC domain logic, API contracts, persistence semantics, H1-H9 matching, or RDF generation.

This milestone does **not** perform the AWS migration. It establishes the target architecture, migration order, readiness gaps, acceptance gates, rollback approach, and retirement criteria for the temporary pilot infrastructure.

## 1. Architectural decision retained

The long-term platform direction remains:

```text
Application/API: Django + Django REST Framework
Operational source of truth: PostgreSQL
Semantic catalogue/search layer: RDF + Apache Jena Fuseki
Public API contract: /api/... + contract_version
Cloud target: AWS
```

Vercel and Neon remain temporary pilot/development infrastructure only.

No AWS-specific SDK, database extension, service API, or deployment assumption should be introduced into provider lifecycle logic, persistence models, H1-H9 matching, RDF generation, or external API contracts.

## 2. Proven pre-migration baseline

Phase 3 has already proven the following application behavior before any AWS move:

```text
trusted provider lifecycle API
        |
        v
PostgreSQL persistence
        |
        v
ProviderPublication + CatalogueSyncEvent outbox
        |
        v
DB-backed RDF graph generation
        |
        v
Fuseki Graph Store synchronization
        |
        v
Fuseki SPARQL
        |
        v
POST /api/service-discovery/search
```

P3.5 final evidence included:

```text
p34_api_validation_provider synchronized successfully
4 related publications -> synced
5 related sync events -> succeeded exactly once
Fuseki graph -> 731 triples
canonical deployed search -> returned p34_api_validation_provider
contract_version -> 1.0
```

This behavior becomes the functional regression baseline for AWS migration acceptance.

## 3. Current temporary pilot architecture

```text
Internet / trusted pilot client
        |
        v
Vercel-hosted Django API
        |
        +------> Neon PostgreSQL
        |
        +------> temporary remotely reachable Fuseki SPARQL endpoint

Trusted local operator
        |
        +------> Neon PostgreSQL
        |
        +------> local Fuseki Graph Store writes
```

Current safety policy:

```text
Vercel MDC_CATALOG_SYNC_ENABLED=False
PostgreSQL = source of truth
Fuseki write path = trusted operator only
```

The temporary Cloudflare tunnel used for pilot Fuseki query reachability is not part of the target architecture.

## 4. Recommended AWS target architecture

The following is the recommended **baseline**, not a permanent lock-in to individual AWS products:

```text
                       Internet / MaaSAI Marketplace
                                  |
                                  v
                         HTTPS load balancer
                                  |
                                  v
                    Django / DRF application service
                    (containerized AWS compute)
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
             PostgreSQL service         Internal Fuseki service
             private network            private network
             source of truth            semantic/search layer
                    |                           |
                    |                           +--> persistent RDF/TDB storage
                    |
                    +--> publication/outbox

Trusted synchronization task
        |
        +--> PostgreSQL
        +--> internal Fuseki Graph Store endpoint
```

A practical first AWS implementation would typically use:

- **Django runtime:** containerized service on ECS/Fargate or equivalent AWS container compute;
- **PostgreSQL:** managed standard PostgreSQL, with Amazon RDS for PostgreSQL as the simplest default candidate;
- **Fuseki:** containerized Apache Jena Fuseki on AWS compute with durable persistent storage;
- **container registry:** Amazon ECR;
- **HTTPS ingress:** Application Load Balancer or equivalent managed ingress;
- **secrets:** AWS Secrets Manager and/or Systems Manager Parameter Store;
- **networking:** VPC with public ingress only at the HTTP boundary and PostgreSQL/Fuseki on private network paths;
- **logs/metrics:** CloudWatch or equivalent AWS observability;
- **DNS/TLS:** platform-managed DNS/certificate services as selected by the MaaSAI deployment architecture.

The exact AWS services may change without affecting MDC application/domain architecture.

## 5. PostgreSQL migration strategy

### 5.1 Principle

MDC already uses Django ORM and a standard PostgreSQL `DATABASE_URL`. The database configuration explicitly rejects non-PostgreSQL URLs when PostgreSQL is selected and contains no Neon-specific application dependency.

Therefore the Neon -> AWS PostgreSQL migration should be operational rather than architectural.

### 5.2 Recommended migration path

For the current small pilot dataset:

```text
1. Provision AWS PostgreSQL.
2. Apply Django schema/migrations to the target database.
3. Take a final logical backup/export from Neon.
4. Restore/import to AWS PostgreSQL.
5. Validate row counts and representative provider/offering/publication/outbox records.
6. Point the AWS Django deployment at the new DATABASE_URL.
7. Run read-only/API smoke tests before writes are enabled.
```

A `pg_dump` / `pg_restore` style logical migration is sufficient for the current pilot scale. If the production database later grows enough to require low-downtime continuous replication, the infrastructure team can select a managed replication/migration approach without changing MDC models.

### 5.3 Database acceptance checks

At minimum verify:

- Django migrations are fully applied;
- provider count matches source;
- offering count matches source;
- certification count matches source;
- `ProviderPublication` history matches source;
- `CatalogueSyncEvent` history/status matches source;
- provider/offering ETags still behave correctly after migration;
- lifecycle create/update transactions remain atomic;
- no Neon-specific extension or branch dependency exists.

## 6. Fuseki migration strategy

### 6.1 Do not make RDF the operational migration source

PostgreSQL remains the source of truth. Therefore the preferred AWS Fuseki bootstrap is:

```text
AWS PostgreSQL authoritative catalogue
        |
        v
existing DB-backed RDF generator
        |
        v
new AWS Fuseki dataset
```

The existing local Fuseki TDB dataset does not need to become the authoritative migration artifact.

### 6.2 Recommended bootstrap

```text
1. Deploy a private AWS Fuseki service/dataset.
2. Configure its SPARQL query endpoint for the Django runtime.
3. Keep Graph Store write endpoint private.
4. Configure write credentials only for the trusted synchronization execution environment.
5. Build the full RDF graph from AWS PostgreSQL.
6. Replace/bootstrap the Fuseki default graph using the existing synchronization implementation.
7. Run direct SPARQL verification.
8. Run canonical `/api/service-discovery/search` verification.
```

This preserves the exact model already proven in P3.3 and P3.5.

## 7. Synchronization execution model on AWS

Do **not** convert synchronization into a new anonymous/public HTTP endpoint merely for AWS deployment.

Recommended first model:

```text
trusted one-off/scheduled AWS task
        |
        v
python backend/manage.py sync_service_discovery_catalogue
```

Possible operational implementations include a one-off container task, scheduled task, or controlled internal worker.

Important invariants:

- only the trusted execution environment has Graph Store write access;
- deployed public Django instances do not need Fuseki write credentials;
- PostgreSQL publication/outbox remains the durable synchronization queue;
- stale-processing recovery remains explicit/operator-controlled;
- whole-graph replacement can remain for the current small catalogue and be optimized later only if scale requires it.

## 8. Network/security model

Recommended target boundary:

```text
PUBLIC
HTTPS ingress / canonical MDC API

PRIVATE
PostgreSQL
Fuseki SPARQL where practical
Fuseki Graph Store write endpoint
synchronization worker/task
```

Security requirements:

- terminate public traffic with TLS;
- PostgreSQL must not be publicly exposed;
- Fuseki Graph Store must not be publicly exposed;
- use security groups/private routing between application, database, Fuseki, and synchronization task;
- move `DJANGO_SECRET_KEY`, lifecycle token, database credentials, and Fuseki write credentials into AWS-managed secret/config storage;
- never bake secrets into container images or repository files;
- rotate the current pilot lifecycle token during/after production cutover;
- rotate any database/Fuseki credentials that were used during pilot validation;
- keep `MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=True`;
- keep `MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=True`;
- keep `MDC_PROVIDER_CONCURRENCY_REQUIRED=True`.

The current bearer service-token boundary is acceptable for controlled pilot/trusted service use. A future Marketplace OAuth/JWT/gateway identity can replace that boundary without changing provider persistence or publication semantics.

## 9. Application portability audit

### Already AWS-portable

The current repository already has the important portability properties:

- Django/DRF application layer;
- `DATABASE_URL`-driven standard PostgreSQL configuration;
- Django ORM persistence;
- no Neon-specific SDK or schema dependency;
- Fuseki endpoints supplied by environment configuration;
- no Vercel-specific provider/domain persistence logic;
- `/api/...` contract independent of deployment platform;
- PostgreSQL-backed publication/outbox synchronization design;
- RDF/Fuseki separated from operational persistence.

### Deployment work still required before a real AWS cutover

These are infrastructure/deployment tasks, not domain redesign:

1. **Container packaging** — add/approve the production container definition for Django and Fuseki deployment.
2. **Production WSGI/ASGI server** — select and configure the production Python application server for the AWS container runtime.
3. **AWS infrastructure definition** — VPC, subnets, ingress, compute, PostgreSQL, Fuseki storage, secret management, IAM, logs and monitoring.
4. **AWS environment configuration** — explicitly configure `DJANGO_ALLOWED_HOSTS`, CORS/CSRF origins, `DATABASE_URL`, lifecycle flags/secrets, and Fuseki endpoints.
5. **Synchronization task definition** — create the internal/operator execution path for `sync_service_discovery_catalogue`.
6. **Persistent Fuseki storage validation** — validate the selected AWS storage option with the chosen Jena/Fuseki dataset mode.
7. **Backup/restore runbook** — PostgreSQL backups and Fuseki rebuild procedure.
8. **Observability** — HTTP errors, application logs, DB health, synchronization failures, and Fuseki availability.
9. **CI/CD** — build/test image, deploy application, run migrations safely, validate health, and support rollback.
10. **Environment-template cleanup** — ensure deployment documentation includes the optional Fuseki write-auth variables while keeping real values secret.

None of these gaps require changing the MDC public API or provider/ontology model.

## 10. Recommended migration phases

### AWS-0 — infrastructure preparation

Provision in parallel with the current pilot:

- AWS network/security boundary;
- PostgreSQL target;
- Django runtime target;
- Fuseki target and persistent storage;
- secret/config management;
- logs/monitoring.

No pilot services are retired.

### AWS-1 — application deployment without cutover

Deploy the same MDC release to AWS with writes initially controlled.

Validate:

```text
GET /api/health
GET /api/catalog/filters
POST /api/service-discovery/search
```

Then validate trusted lifecycle reads.

### AWS-2 — PostgreSQL migration

- backup Neon;
- migrate PostgreSQL data;
- verify counts/history;
- point AWS Django to AWS PostgreSQL;
- run migrations/checks;
- validate lifecycle API behavior.

### AWS-3 — semantic layer bootstrap

- generate RDF from AWS PostgreSQL;
- synchronize the new AWS Fuseki dataset;
- verify representative providers/offerings directly through SPARQL;
- verify canonical search through the AWS Django deployment.

### AWS-4 — end-to-end acceptance

Repeat the proven Phase 3 sequence using a controlled AWS validation provider:

```text
provider publication/update
        -> AWS PostgreSQL
        -> outbox
        -> trusted AWS synchronization task
        -> AWS Fuseki
        -> canonical discovery
```

### AWS-5 — traffic cutover

Only after AWS-4 passes:

- point Marketplace/consumer traffic to the AWS endpoint;
- keep the old pilot temporarily available for rollback;
- monitor errors, latency, DB health and semantic search;
- freeze old pilot writes during the final cutover window if needed.

### AWS-6 — pilot retirement

Retire Vercel/Neon/temporary tunnel only after an agreed observation period and explicit operational approval.

Do not delete the pilot database or deployment as part of P3.6.

## 11. Rollback strategy

Before cutover:

- preserve a verified Neon backup/export;
- preserve the known-good application release/commit;
- record current environment configuration securely;
- do not delete the current Vercel deployment;
- treat Fuseki as rebuildable from PostgreSQL.

If AWS acceptance fails before final cutover, continue using the current pilot while the AWS issue is repaired.

If failure occurs immediately after cutover, route traffic back to the previous known-good endpoint and reconcile any writes performed during the cutover window before retrying.

## 12. CI/CD target

Recommended deployment flow:

```text
GitHub main
   |
   v
unit/focused/full validation gates
   |
   v
build immutable application image
   |
   v
push image to AWS registry
   |
   v
run deployment/migrations
   |
   v
AWS health + canonical API smoke
   |
   v
promote/retain previous revision for rollback
```

Database migrations and semantic synchronization must remain explicit steps; image deployment alone must not silently trigger destructive data or Fuseki writes.

## 13. What must remain unchanged during migration

Unless a separate functional milestone explicitly changes them, AWS migration must preserve:

- `GET /api/health`;
- `GET /api/catalog/filters`;
- `POST /api/service-discovery/search`;
- no public `/api/v1` route;
- `contract_version = "1.0"`;
- provider lifecycle route semantics;
- provider/offering IDs;
- Django models and PostgreSQL source-of-truth role;
- publication/outbox audit behavior;
- H1-H9 matching behavior;
- RDF namespace and generation semantics;
- trusted synchronization boundary;
- ETag/concurrency behavior.

A cloud migration must not be used as an excuse to redesign the API or ontology model.

## 14. AWS migration acceptance checklist

A future AWS cutover can be accepted when all of the following are demonstrated:

### Application

- production Django deployment healthy;
- canonical APIs return expected contract;
- no `/api/v1` route reintroduced;
- security headers/TLS configuration valid.

### PostgreSQL

- schema/migrations correct;
- data counts reconciled;
- representative provider/offering/history records verified;
- lifecycle create/update + ETag behavior passed;
- backup/restore procedure tested.

### Fuseki

- private durable Fuseki dataset available;
- direct SPARQL works;
- Graph Store writes restricted to trusted synchronization task;
- full graph successfully rebuilt from PostgreSQL;
- no temporary public tunnel required.

### End-to-end

- provider write -> PostgreSQL -> outbox -> Fuseki -> canonical search passes;
- deployed search consumes the AWS Fuseki graph;
- PostgreSQL remains authoritative;
- synchronization failure remains retryable/auditable.

### Operations

- secrets stored outside source control;
- logs/metrics available;
- rollback tested/documented;
- CI/CD path agreed;
- Vercel/Neon retirement approved only after observation period.

## 15. Recommended first AWS production shape

For MDC's present scale, avoid unnecessary distributed complexity.

Recommended first production shape:

```text
1 Django application service
1 managed PostgreSQL database
1 private Fuseki service/dataset
1 trusted synchronization task definition
managed secrets + logging + HTTPS ingress
```

Scale horizontally or introduce queues/workers only when measured catalogue size, request volume, availability targets, or synchronization latency require it.

## 16. P3.6 conclusion

The Phase 3 implementation is AWS-ready at the **application architecture level**. The remaining work is primarily infrastructure packaging, provisioning, data migration, security/configuration, and operational validation.

The most important design property has been preserved:

```text
Vercel + Neon + temporary Fuseki
        |
        | operational migration
        v
AWS application runtime + AWS PostgreSQL + AWS-hosted Fuseki
```

without changing:

```text
MDC API contract
provider lifecycle model
PostgreSQL source-of-truth semantics
H1-H9 matching
RDF generation
publication/outbox synchronization model
```

## Final milestone marker

```text
P3.6 COMPLETE
PHASE_3_COMPLETE
```

A future AWS implementation/cutover should be opened as a separate deployment phase/milestone rather than extending Phase 3.
