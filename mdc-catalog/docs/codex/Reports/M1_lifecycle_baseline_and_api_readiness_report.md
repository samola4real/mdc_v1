# M1 lifecycle baseline and API readiness report

## Result

M1 is complete on `phase4/lifecycle-baseline`. The current lifecycle security
implementation already supports the temporary MaaSAI plenary pilot without an
authentication-code change. A named, commented deployment profile now records
the exact non-secret opt-in values, and focused tests prove that anonymous
lifecycle access can coexist with required ETag concurrency while the secured
mode remains available.

This work was tested locally only. It was **not deployed** to Vercel or any
other environment, and no production/Neon/Fuseki data was read or changed.

## Git and worktree baseline

| Item | Verified value |
| --- | --- |
| Repository | `https://github.com/samola4real/mdc_v1.git` |
| Fetched baseline | `origin/main` at `66eefdd00c65b4a68c1e876df1181aec1d5f7109` |
| Prompt commit | `66eefdd00c65b4a68c1e876df1181aec1d5f7109` |
| M1 branch | `phase4/lifecycle-baseline` |
| Isolated worktree | `C:\Users\Elahi\Desktop\mdc_v1_m1_worktree` |
| Implementation commit | `146f8c63b5a3632906db5676d40dc8cac05bef13` |

The isolated worktree started clean. The original checkout remained on `main`;
its pre-existing `.gitignore` and
`mdc-catalog/demo-frontend/src/pages/demo/index.js` changes were not modified,
stashed, discarded, copied, or committed. The report commit is the commit that
contains this document; the authoritative pushed branch-tip SHA is recorded in
Git metadata and in the completion summary because a commit cannot embed its
own SHA.

## Code paths inspected

- Routing and handlers: `backend/config/urls.py`, `backend/apps/api/urls.py`,
  `backend/apps/api/views/__init__.py`, `get_views.py`, `post_views.py`, and the
  legacy `backend/apps/api/views.py` used only for `/api/catalog/search`.
- Validation and security: `lifecycle_security.py`,
  `provider_lifecycle_serializers.py`,
  `service_discovery_publication_serializers.py`, and
  `service_discovery_search_serializers.py`.
- Persistence: provider models, lifecycle repository, lifecycle write service,
  service-discovery database repository, migrations, and database configuration.
- Discovery and synchronization: runtime search selection, Fuseki and local
  RDF services, YAML loader/matcher, catalogue outbox service, RDF generator,
  and the `sync_service_discovery_catalogue` management command.
- Configuration: base/local/production settings, environment parsing, and
  `.env.example`.
- Relevant public API, lifecycle, production-safety, database, runtime search,
  outbox/sync, and ETag/security tests.

## Current route and flag baseline

`/api/service-discovery/search` is the canonical public discovery POST. It is
not the provider-publication POST and does not call the lifecycle security
helper. No `/api/v1/` routes are registered.

| Route | Methods | Validation and gates | Auth, actor, concurrency | Persistence/backend and response |
| --- | --- | --- | --- | --- |
| `/api/health` | GET | None | Public | Read-only; `200` public contract |
| `/api/catalog/filters` | GET | None | Public | Read-only vocabulary response; `200` |
| `/api/catalog/search` | POST | Legacy `SearchRequestSerializer` | Public | Reads legacy seed catalogue through local matcher; `200` or `400` |
| `/api/service-discovery/search` | POST | Strict canonical search serializer and controlled vocabularies | Public; lifecycle flags do not apply | Fuseki first, then local RDF, then YAML; `200`, validation `400`, or all-backends `503` |
| `/api/provider-publication/validation` | POST | `MDC_PROVIDER_VALIDATION_ENABLED`; full publication validation | Bearer only when lifecycle auth is required; actor and If-Match do not apply | Non-mutating normalized preview; `200`, `400`, `401`/`503`, or gated `403` |
| `/api/provider-publication` | POST | `MDC_PROVIDER_PUBLICATION_ENABLED`; strict provider/offering/evidence validation; duplicate provider rejected | Bearer and actor only when their flags are true; no If-Match for creation | Atomic Django DB write plus publication history and pending outbox events; `201`, `400`, `401`, `403`, `409`, or `503`; returns pending sync status and ETag |
| `/api/providers/{provider_id}` | GET | Existing identifier | Bearer only when auth flag is true; actor/If-Match do not apply | Django DB lifecycle projection including inactive state; `200` with ETag or `404` |
| `/api/providers/{provider_id}` | PATCH | Publication gate; strict partial provider fields and complete certification validation | Conditional bearer/actor; If-Match required only when concurrency flag is true, but any supplied ETag is always validated | Atomic DB update, history, pending provider outbox event; `200` with new ETag; `400`, `401`, `403`, `404`, `412`, `428`, or `503` |
| `/api/providers/{provider_id}/offerings` | GET | Existing provider | Bearer only when auth flag is true | Ordered Django DB list; `200` (including empty list) or `404` |
| `/api/providers/{provider_id}/offerings` | POST | Publication gate; strict complete offering validation | Conditional bearer/actor; no If-Match because this creates an offering | Atomic DB write, history, pending offering outbox event; `201`; validation/not-found/conflict/gate/security errors as applicable |
| `/api/offerings/{offering_id}` | GET | Existing identifier | Bearer only when auth flag is true | Django DB lifecycle projection; `200` with ETag or `404` |
| `/api/offerings/{offering_id}` | PATCH | Publication gate; strict mutable fields and complete-state revalidation | Conditional bearer/actor; same independent If-Match behavior as provider PATCH | Atomic DB update, provider revision touch, history, pending offering outbox event; `200` with new ETag; `400`, `401`, `403`, `404`, `412`, `428`, or `503` |

Unsupported methods return DRF `405`. Provider/offering DELETE is **M3**, not
M1. Multiple distinct offerings in the same service category are **M2**, not
M1: offering IDs are currently generated from `provider_id + service_category`,
and the globally unique `offering_id` makes a second same-category offering
conflict.

### Relevant switches

| Setting | Current behavior |
| --- | --- |
| `MDC_PROVIDER_PUBLICATION_ENABLED` | Gates registration, provider PATCH, offering creation, and offering PATCH |
| `MDC_PROVIDER_VALIDATION_ENABLED` | Separately gates the non-mutating validation POST |
| `MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED` | When true, lifecycle reads/writes/validation require the configured Bearer service token; it never protects canonical discovery |
| `MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED` | When true, write requests require `X-MDC-Actor-Id`; it does not affect reads or validation |
| `MDC_PROVIDER_CONCURRENCY_REQUIRED` | When true, PATCH requires a strong lifecycle ETag through `If-Match` (or the existing pilot transport alias `X-MDC-If-Match`) |
| `MDC_CATALOG_SYNC_ENABLED` | Enables explicit sync processing; it does not invoke sync automatically after a lifecycle write |
| `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` | Configures the first-choice canonical discovery backend |
| `SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT` | Configures explicit default-graph replacement for catalogue sync |

## Named pilot configuration

The designated M1 MaaSAI plenary pilot must explicitly set these values in its
deployment environment:

```dotenv
MDC_PROVIDER_PUBLICATION_ENABLED=True
MDC_PROVIDER_VALIDATION_ENABLED=True
MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=False
MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN=
MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=False
MDC_PROVIDER_CONCURRENCY_REQUIRED=True
MDC_CATALOG_SYNC_ENABLED=False
```

This is reversible: removing these overrides restores production defaults of
publication/validation/sync disabled and lifecycle auth, actor attribution, and
concurrency required. No new or redundant pilot flag was introduced. The
service-token value is intentionally empty because authentication is disabled;
no secret was committed. `MDC_PROVIDER_CONCURRENCY_REQUIRED=True` keeps stale
update protection independent of the temporary auth bypass. Sync remains false
for M1 because automatic provider-to-discovery synchronization belongs to M4.

## Database and canonical discovery behavior

- `DATABASE_URL` selects PostgreSQL only. An absent/blank URL falls back to
  SQLite; other database schemes are rejected. Cloud/serverless connections use
  `CONN_MAX_AGE=0`. The isolated worktree's inspected local runtime selected
  SQLite. The production settings do not themselves require `DATABASE_URL`, so
  deployment configuration must be checked in M5 rather than inferred here.
- The canonical discovery handler always attempts Fuseki first. If its query
  endpoint is blank/unavailable it falls back to the checked-in generated RDF
  through RDFLib, then to checked-in harmonized provider YAML. If every backend
  fails it returns a safe `503`.
- Lifecycle writes persist Provider/Offering rows and transactionally create
  `ProviderPublication` plus pending `CatalogueSyncEvent` rows. They do not call
  RDF generation, Fuseki, the runtime search service, or the sync processor.
- The only current DB-to-RDF-to-Fuseki path is explicit invocation of
  `sync_service_discovery_catalogue` (pending-event processing or `--rebuild`),
  with sync enabled and a graph-store endpoint configured. Therefore a newly
  accepted DB provider is **not automatically discoverable**. Search fallbacks
  can also remain stale because they read generated RDF/YAML rather than the
  lifecycle database.

No deployed environment variables, Neon database, or live Fuseki endpoint were
inspected, so this report does not claim which backend a current deployment is
successfully reaching.

## Likely POST blockers from current code

These are code-supported possibilities, not a diagnosis of the Marketplace
team's reported failures:

- Using `/api/v1/...` or confusing public discovery POST with provider
  publication; only unversioned `/api/...` routes exist.
- Publication or validation feature gates remaining false.
- Lifecycle Bearer/actor requirements remaining true on a non-pilot deployment,
  a missing server token while auth is required, or malformed headers.
- Strict payload shape, controlled-vocabulary, evidence, identifier, JSON-safety,
  or duplicate provider/offering validation failures.
- The current generated offering identity colliding when a provider adds a
  second offering in the same category.
- Missing migrations, unavailable/misconfigured PostgreSQL, host/HTTPS routing,
  or an environment selecting different settings. CORS can affect browsers but
  does not explain a direct Postman/server POST by itself.

## M2-M4 dependencies and blockers

- **M2:** define stable independently supplied/generated offering identities,
  migrate without changing existing IDs, and remove the service-category-based
  collision while preserving validation and RDF identity fidelity.
- **M3:** add provider/offering DELETE routes, cascade/operational-history rules,
  delete outbox events, repeat-delete behavior, and explicit attribute-removal
  semantics. Current PATCH replaces submitted JSON fields but is not the final
  M3 removal contract.
- **M4:** invoke durable outbox processing automatically after accepted writes;
  align the query endpoint and graph-store endpoint to the same intended
  dataset; decide success/failure visibility and retries; update/remove RDF for
  all lifecycle actions; and prove the next canonical discovery request sees
  the committed state without falling back to stale RDF/YAML.

## Tests

All tests used disposable Django test databases or mocks. The full suite's RDF
artifact was written under the operating-system temporary directory. No named
provider or production record was mutated.

| Command | Result |
| --- | --- |
| `python manage.py test tests.test_public_api_contract tests.test_service_discovery_search_endpoint tests.test_provider_detail_api tests.test_provider_publication_api tests.test_provider_publication_validation_api tests.test_provider_lifecycle_write_api tests.test_m76_external_exposure_readiness tests.test_production_route_safety tests.test_database_configuration tests.test_service_discovery_runtime_search --verbosity 1` | 107 passed, 0 failed, 0 skipped |
| `python manage.py test tests.test_m1_lifecycle_pilot_readiness --verbosity 2` | 4 passed, 0 failed, 0 skipped |
| `python manage.py test tests --verbosity 1` | 548 passed, 0 failed, 13 skipped |

The tests ran with the existing local virtual environment on Python 3.11.9,
although `pyproject.toml` declares Python `>=3.12`. This did not cause a test
failure, but Python 3.12+ deployment parity remains to be verified later.

## Files changed

- `.env.example`: documented the named, explicit, reversible pilot profile.
- `backend/tests/test_m1_lifecycle_pilot_readiness.py`: added focused pilot,
  secured-mode, public discovery, production override, and ETag tests.
- `docs/codex/Reports/M1_lifecycle_baseline_and_api_readiness_report.md`: this
  baseline and evidence report.

No application runtime code, demo frontend, provider data, route scope, API
versioning, external infrastructure, or deployment configuration was changed.

## Outstanding questions

- Which future controlled environment and database will be designated for the
  pilot in M5?
- Do its Fuseki query and graph-store endpoints address the same dataset, and
  what worker/trigger will own outbox processing in M4?
- Does the Marketplace use the canonical payload/route, and does its proxy need
  the existing `X-MDC-If-Match` compatibility header?
- What independent offering-ID contract should M2 adopt while preserving all
  existing provider/offering identifiers?

Deployment state: **not deployed**. M1 stops here pending review before M2.
