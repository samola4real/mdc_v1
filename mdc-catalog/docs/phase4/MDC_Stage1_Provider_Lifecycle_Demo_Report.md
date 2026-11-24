# MaaSAI MDC Stage 1 Provider Lifecycle Demo Report

**Date** 2026-11-24 · **Verdict** BLOCKED

## 1. Executive summary

The accepted backend is pinned in a clean worktree. All nine stored Vercel Preview settings match the Stage 1 profile. Read-only SQL confirmed the intended isolated Neon database and its four provider migrations. The remaining database gate is a successful read-only connection using the actual Vercel Preview binding. The local Vercel CLI also reported that it had no credentials, so an operator login was requested.

Stage 1 stopped before deployment or lifecycle writes. Production health, filters, and spur-gear discovery passed both baseline runs. The existing protected Preview rejected an anonymous request.

## 2. Exact deployed source commit

| Item | Result |
| --- | --- |
| Fetched GitHub `origin/main` | `004fef8f0db73ef3e12c1035ec470c131dcb99a6` |
| Pinned Stage 1 candidate | `004fef8f0db73ef3e12c1035ec470c131dcb99a6`, in a clean temporary worktree |
| Accepted M6-A merge | `2e49d7c8f7f70f440ae4e873b05cc259884586aa`, confirmed in the candidate's ancestry |
| Stage 1 deployed commit | None. The deployment gate was unmet. |
| Intended build | `mdc-catalog/` with Python 3.12 and `backend.config.wsgi:application` |

The existing local edits in the original checkout were preserved. [Accepted source](https://github.com/samola4real/mdc_v1/tree/004fef8f0db73ef3e12c1035ec470c131dcb99a6/mdc-catalog) · [Prior deployment audit](https://github.com/samola4real/mdc_v1/blob/6ebf685021c5c093d64e0185a1e742fe3731c163/mdc-catalog/docs/phase4/MDC_Vercel_Demo_Deployment_Audit_2026-11-23.md)

## 3. Vercel project and Preview deployment

| Item | Result |
| --- | --- |
| Team and project | `mdc19/maasai-mdc-v1` |
| Project ID | `prj_DekMQdOYuuH0A5yNsCkFmOC4uD9j` |
| Access to project metadata | The authenticated Vercel integration returned the exact project, deployment, alias, and Preview environment records. |
| Local deployment access | The CLI returned `No existing credentials found` for the scoped project inspection. An interactive operator login was requested. The retry reported the same result. |
| Stage 1 Preview URL, deployment ID and build status | None. No Stage 1 artifact was created. |

[Vercel project](https://vercel.com/mdc19/maasai-mdc-v1)

## 4. PostgreSQL database binding and migration evidence

| Check | Evidence |
| --- | --- |
| Intended Neon target | `maasai-mdc-validation`, project `mute-cell-38148661`, branch `main` (`br-wild-haze-aej09lb1`), database `mdc_validation` |
| Direct Neon connection | Read-only SQL against that exact project, branch, and database returned `current_database() = mdc_validation`. The branch metadata and compute inventory matched the project and branch. |
| Provider migrations | `0001_initial`, `0002_canonical_parity_fields`, `0003_alter_providerpublication_operation`, and `0004_cataloguesynclease` were applied. These are all provider migrations in the pinned source. |
| Required relations | All six tables were present: `providers_provider`, `providers_offering`, `providers_providercertification`, `providers_providerpublication`, `providers_cataloguesyncevent`, and `providers_cataloguesynclease`. |
| Vercel Preview database binding | **Unverified.** Vercel lists a distinct, sensitive Preview `DATABASE_URL`. The metadata exposes its scope and type. The direct Neon SQL verifies the intended target independently of Vercel. The audit still needs a successful connection using the value injected by Vercel. |
| `neondb` | The supplied read-only evidence records `0001` and `0002` only, with no sync lease table. No Stage 1 query, migration, or write targeted `neondb`. |

The historical M5-A and M5-B runs used the isolated validation database. No database was created, no migrations ran, and no database credentials were printed or stored in the report. [M5-A verification](../codex/Reports/M5A_postgresql_lifecycle_vercel_postman_report.md) · [M5-B verification](../codex/Reports/M5B_fuseki_immediate_discovery_validation_report.md) · [Provider migrations](../../backend/apps/providers/migrations) · [Vercel sensitive environment variables](https://vercel.com/docs/environment-variables/sensitive-environment-variables)

## 5. Preview configuration

All entries below were confirmed by reading the existing non-secret project values explicitly scoped to Preview. The eligible settings already match the requested profile, so no changes were applied. Runtime evidence for a new deployment is pending.

| Setting | Confirmed Preview value |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `config.settings_production` |
| `MDC_PROVIDER_PUBLICATION_ENABLED` | `True` |
| `MDC_PROVIDER_VALIDATION_ENABLED` | `True` |
| `MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED` | `False` |
| `MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED` | `False` |
| `MDC_PROVIDER_CONCURRENCY_REQUIRED` | `True` |
| `MDC_CATALOG_SYNC_ENABLED` | `False` |
| `MDC_CATALOG_AUTO_SYNC_ENABLED` | `False` |
| `MDC_DEMO_API_ENABLED` | `False` |

Vercel also lists Preview entries for `DJANGO_SECRET_KEY`, `DATABASE_URL`, and `DJANGO_ALLOWED_HOSTS`. Their values were excluded from the inspection.

## 6. Authentication and Deployment Protection

Vercel project metadata reports `all_except_custom_domains` for Vercel Authentication. An anonymous `GET /api/health` returned an edge `401` on existing Preview `dpl_8YpgEJ4DH9YUB5ZrdwLpH4yMBLSX`. The response contained neither the MDC contract marker nor an MDC Bearer challenge.

The Preview project settings disable the MDC Bearer and actor requirements and enable concurrency checks. Authorized Vercel-protected access and the no-Bearer, no-actor, strong-ETag behavior still need to be exercised on the new deployment. No bypass credential was used or exported. [Vercel Deployment Protection](https://vercel.com/docs/deployment-protection) · [Vercel CLI authenticated requests](https://vercel.com/docs/cli/curl)

## 7. Complete endpoint test matrix

These are the Stage 1 endpoint acceptance cases. All new Preview cases are pending. The three Production public baseline endpoints passed separately.

| Method | Route | Stage 1 expected result | Live evidence |
| --- | --- | --- | --- |
| GET | `/api/health` | `200` with approved Vercel access. Anonymous request denied at the edge. | New Preview pending. Production `200` twice. Existing Preview anonymous `401`. |
| GET | `/api/catalog/filters` | `200` with catalogue vocabulary | New Preview pending. Production `200` twice. |
| POST | `/api/service-discovery/search` | `200` with Tasowheel and Precipart for the documented spur-gear query | New Preview pending. Production `200` and two expected matches twice. |
| POST | `/api/provider-publication/validation` | `200` with normalized payload and `400` for invalid input | Pending |
| POST | `/api/provider-publication` | `201` with provider ETag and pending publication. Duplicate provider identity `409`. | Pending |
| GET | `/api/providers/{provider_id}` | `404` initially and after cleanup. `200` plus strong ETag for the registered provider. | Pending |
| PATCH | `/api/providers/{provider_id}` | `200` with a current ETag and persisted changes. `428` when absent and `412` when stale. | Pending |
| DELETE | `/api/providers/{provider_id}` | `200` with a current ETag. Provider and remaining child are absent afterward. | Pending |
| GET | `/api/providers/{provider_id}/offerings` | `200` listing both independently addressable same-category offerings. `404` after provider cleanup. | Pending |
| POST | `/api/providers/{provider_id}/offerings` | `201` for a distinct offering in the existing category. Duplicate offering ID `409`. | Pending |
| GET | `/api/offerings/{offering_id}` | `200` for each offering with its own ETag. `404` after deletion. | Pending |
| PATCH | `/api/offerings/{offering_id}` | `200` with a current ETag. Whole-map replacement removes the selected optional attribute. Sibling unchanged. Stale ETag `412`. | Pending |
| DELETE | `/api/offerings/{offering_id}` | `200` with a current ETag and `428` when missing. Sibling remains present. | Pending |

[M6 Marketplace contract](../Partner_API/MaaSAI_MDC_M6_Marketplace_Integration_Guide.md) · [Joint test checklist](../Partner_API/MaaSAI_MDC_M6_Marketplace_Joint_Test_Checklist.md)

## 8. HTTP request and assertion totals

| Suite | Requests | Assertions | Failures |
| --- | ---: | ---: | ---: |
| Production baseline before and after preflight | 6 | 20 | 0 |
| Existing Preview anonymous boundary probe | 1 | 3 | 0 |
| New Preview Stage 1 acceptance | 0 | 0 | 0 |
| **Total HTTP** | **7** | **23** | **0** |

Production assertions checked HTTP status, contract version, health state, vocabulary presence, result count, and both expected providers. The protection probe checked the edge status, absence of the app contract, and absence of an MDC Bearer challenge. The new Preview row records an unrun suite.

## 9. PostgreSQL lifecycle and publication results

Pending. No provider, offering, publication, or outbox rows were created, updated, or deleted. With both synchronization flags disabled, the expected acceptance tuple is `accepted / sync_pending / pending`. Stage 1 should verify relational state through lifecycle GETs and capture publication IDs. Immediate discovery for new provider records requires the separate semantic validation.

## 10. Cleanup evidence

No disposables were created. Cleanup was therefore unnecessary. A later acceptance run must use unique disposable IDs and confirm the second offering is absent after individual deletion, the first survives that deletion, and both offerings and the provider are absent after aggregate deletion. After an ambiguous response, inspect current state and refresh the ETag before retrying.

## 11. Production preservation evidence

The public alias `maasai-mdc-v1.vercel.app` resolved before and after preflight to `dpl_GmWLQStvb3qo551uYYUv4zLiW1XK`. The deployment was `READY` and its source metadata identified `b9275258bf4a2455814ad9b2af9621e0a5d01327`. The Production public health, filters, and search requests each returned `200` in both runs. The spur-gear query returned Tasowheel and Precipart in both runs. Production variables, aliases, application code, real provider records, and Fuseki configuration and graph contents were unchanged by this task. [Production health](https://maasai-mdc-v1.vercel.app/api/health) · [Production filters](https://maasai-mdc-v1.vercel.app/api/catalog/filters)

## 12. Remaining Stage 2 requirements

Stage 2 remains deferred. Authoritative semantic acceptance requires a stable same-dataset Fuseki query and protected Graph Store pair, verified database and graph snapshots, private outbox retry and lease recovery, and exact offering-ID discovery checks after successful create, update, and delete. The accepted M5-B temporary infrastructure supplied historical evidence. A new Stage 2 operation was outside this task. [M6 readiness checklist](../Partner_API/MaaSAI_MDC_M6_Production_Readiness_Checklist.md)

## 13. Postman configuration after unblocking

1. Import the M6 collection and environment. Set `base_url` to the newly verified protected Preview. Set `automatic_sync_enabled=false` and `concurrency_required=true`.
2. Omit MDC Bearer authorization and `X-MDC-Actor-Id`. Use the approved Vercel protection access separately. Keep the bypass secret in the local vault and exclude it from shared collections, exported environments, and logs.
3. Verify anonymous rejection and authorized health before mutations. Run canonical spur-gear discovery separately because the collection skips automatic sync search assertions in this profile.
4. Run the lifecycle and cleanup folders with disposable IDs. Add any matrix checks missing from the collection, including invalid and duplicate requests and independent sibling verification. Retain the resource ETags and publication receipts. Use `If-Match` as the canonical header. When Vercel intermediary handling interferes, use the existing `X-MDC-If-Match` transport alias with the same strong ETag.
5. Record actual request and assertion totals and verify final `404` responses before leaving the Preview available for manual testing.

[M6 collection](../Partner_API/MaaSAI_MDC_M6_Marketplace_Integration.postman_collection.json) · [M6 environment](../Partner_API/MaaSAI_MDC_M6_Marketplace_Integration.postman_environment.json)

## 14. Rollback instructions

This run requires no service rollback. In a later failed Preview run, stop acceptance traffic and keep Vercel protection active. Resolve any ambiguous writes by inspecting the disposable resources and publication receipts in `mdc_validation`. Clean up only verified disposable resources through the API with fresh ETags. Keep the public alias on the recorded Production deployment and leave both synchronization switches off. If a later authorized Preview setting changes, restore its recorded Preview value and verify the next build inherits it.

## 15. Final verdict and unblock steps

**BLOCKED.** The pinned candidate, stored profile, Preview protection policy, isolated Neon schema and Production baseline are verified. The actual Preview database binding, CLI deployment access and every Stage 1 lifecycle operation remain outstanding.

1. Sign in interactively with `vercel login` using an account that can deploy to `mdc19/maasai-mdc-v1`. Use an approved Vercel access method for protected testing. Keep credentials out of chat and command output.
2. Using an operator-controlled read-only Preview preflight with lifecycle writes disabled, compare the compute endpoint used by the injected `DATABASE_URL` against the Neon endpoints for `br-wild-haze-aej09lb1`. Open a read-only SQL connection using that binding and check `SELECT current_database()`. Return only the project, branch, database name, and connection outcome. If the existing binding cannot be traced, the operator can securely set the **Preview-only** value from the verified existing `mdc_validation` database and repeat the connection check.
3. After both gates pass, deploy the pinned SHA to protected Preview, verify access and source, and execute the live endpoint matrix and cleanup. No Stage 2 changes or Production promotion are part of Stage 1.
