# MaaSAI MDC M6 Production and plenary readiness checklist

This checklist separates verified software behavior from deployment gates. M6-A
does not configure infrastructure, change Production, or authorize release.

## Already proven and accepted

- [x] M1: lifecycle/API baseline and readiness verified.
- [x] M2: independently addressable multi-offering providers, including
  multiple offerings in one service category.
- [x] M3: provider/offering PATCH and permanent operational DELETE, selected-map
  removal, tombstone/audit retention, and strong ETag protection.
- [x] M4: transactional publication/outbox, automatic full RDF rebuild,
  Graph Store replacement, query-visible revision verification, authoritative
  search behavior, and safe recovery primitives.
- [x] M5-A: Vercel Preview plus isolated Neon `mdc_validation` PostgreSQL
  lifecycle acceptance — 35 requests, 81 assertions, 0 failures.
- [x] M5-B: disposable Fuseki plus temporary transport semantic acceptance —
  39 requests, 88 assertions, 0 failures — proving immediate discovery after
  register/update and immediate absence after offering/provider deletion.
- [x] Production remained unchanged during M5-A/M5-B.
- [x] M6-A: frozen contract, partner examples, Postman package, plenary runbook,
  recovery guidance, and joint-test procedure prepared.

## Required before Production or plenary enablement

- [ ] Provision a durable, remotely hosted, protected Fuseki query + default
  Graph Store pair. Temporary Quick Tunnels are not acceptable.
- [ ] Prove query and Graph Store endpoints use the same origin and dataset and
  that credentials authorize only the intended operations.
- [ ] Confirm Production/plenary PostgreSQL connectivity, backup/rollback plan,
  and zero pending migrations through `providers.0004_cataloguesynclease`.
- [ ] Review and approve every Production/plenary environment value, including
  publication, validation, sync, automatic sync, concurrency, auth/actor,
  allowed-host and demo flags. Exchange secret values out of band.
- [ ] Install an owned, monitored retry/worker/scheduler arrangement for
  pending/failed `CatalogueSyncEvent` work and stale processing recovery.
- [ ] Assign final incident, database, Fuseki, and rollback/recovery ownership.
- [ ] Explicitly approve any temporary no-auth/no-actor pilot mode for that
  exact deployment. Secure defaults remain the Production expectation.
- [ ] Execute a disposable pre-plenary smoke test: migrate, health, filters,
  search, validate, register, immediate search, update, delete, immediate
  absence, and complete cleanup.
- [ ] Execute the joint Marketplace-originated test using the M6 checklist and
  retain redacted evidence.
- [ ] Confirm final dataset/revision health and no disposable operational rows.
- [ ] Approve Production promotion/plenary environment through the normal
  change process.
- [ ] Only after all gates pass, create and document the release tag.

## Release decision

Current decision after M6-A: **package ready for joint integration; Production
and plenary release not yet approved**. The blocking gates are durable protected
Fuseki hosting, owned retry operations, environment/migration approval, and an
actual joint Marketplace test. M6-A deliberately does not solve or bypass them.
