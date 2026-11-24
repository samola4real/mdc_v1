# MaaSAI MDC Stage 1 Provider Lifecycle Demo — Resume Report

**Verdict PASS** · 2026-11-24, Europe/Helsinki

## 1. Outcome

**VERIFIED** Stage 1 passed on the protected Preview of the accepted backend. The live suite ran **38 requests and 166 assertions with zero failures**. It exercised validation, registration, same-category offerings, updates, strong ETag enforcement, and deletion without supplying MDC Bearer authorization or an actor header. Read-only Neon inspection matched all seven publication receipts and confirmed zero disposable operational rows. Production continued serving the original deployment.

The previous blocked report remains at its original path and commit. This report follows the updated resume instructions from `39e4570cc7839806e1db2a03bf5a7f58437f4acf`. [Resume prompt](../prompts_phase4/01_MDC_Stage1_Provider_Lifecycle_Demo_Prompt.md#resume-instructions--2026-11-24-after-blocked-attempt) · [Previous blocked report](https://github.com/samola4real/mdc_v1/blob/4e380b6a91e9500587cecfc06f9bb81a025278ee/mdc-catalog/docs/phase4/MDC_Stage1_Provider_Lifecycle_Demo_Report.md)

## 2. Deployment and source evidence

| Item | Verified result |
| --- | --- |
| Vercel team and project | `mdc19/maasai-mdc-v1`, `prj_DekMQdOYuuH0A5yNsCkFmOC4uD9j` |
| CLI session | Vercel CLI `48.9.2`. `vercel whoami` succeeded from the execution context. Scoped project inspection returned the exact project ID. |
| Stage 1 Preview | [Protected Preview](https://maasai-mdc-v1-2ps4wdme5-mdc19.vercel.app) |
| Stage 1 deployment | `dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea`, `READY`, created through CLI as Preview, with no assigned aliases |
| Deployed source | `004fef8f0db73ef3e12c1035ec470c131dcb99a6` from a clean detached worktree |
| Runtime | Upload root `mdc-catalog/`. Build log reported Python 3.12. The WSGI entry point is `backend.config.wsgi:application`. |
| Artifact verification | Vercel upload digests matched the pinned checkout for `.python-version`, `pyproject.toml`, `backend/config/wsgi.py`, `backend/apps/api/views/post_views.py`, and `backend/apps/providers/provider_lifecycle_write_service.py`. The CLI checked the Git SHA and clean status immediately before upload. |

The Preview remains available for authorized manual testing. [Vercel deployment](https://vercel.com/mdc19/maasai-mdc-v1/dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea) · [Pinned application source](https://github.com/samola4real/mdc_v1/tree/004fef8f0db73ef3e12c1035ec470c131dcb99a6/mdc-catalog)

## 3. Actual Preview database binding

**VERIFIED** A separate protected runtime probe used Vercel's injected Preview `DATABASE_URL`. Publication, validation, and both synchronization flags were explicitly disabled for that probe. The probe matched the configured and connected compute to the Neon branch endpoint, opened a read-only transaction, checked `current_database()` and confirmed the applied migrations and required tables. The authenticated probe returned `200`. Anonymous requests to its generated host were denied at the Vercel edge with `401`.

| Check | Verified result |
| --- | --- |
| Neon project | `maasai-mdc-validation`, `mute-cell-38148661` |
| Neon branch | `main`, `br-wild-haze-aej09lb1` |
| Database | `mdc_validation` |
| Migrations | `0001_initial`, `0002_canonical_parity_fields`, `0003_alter_providerpublication_operation`, `0004_cataloguesynclease` |
| Required tables | Provider, offering, provider certification, provider publication, catalogue sync event, and catalogue sync lease |
| Restore capability | The Neon project reported a 21,600-second history window. No restore was needed. |

**VERIFIED** The probe and application deployment used the same unqualified Preview database entry. Its metadata matched before and after both runs, and neither deployment supplied a database override. The exact publication IDs returned by the Stage 1 application were subsequently found in `mdc_validation`. No migration was run and the stored sensitive value was never retrieved.

The first probe build `dpl_HZyNYatLSKPedcpXoZQhKgFTW2xG` reported `PYTHON_ENTRYPOINT_NOT_FOUND`. The retry `dpl_AFcZr8gYtV9w7WRjorQo4EEKpJi3` supplied the explicit entry point in the temporary probe package and reached `READY`. The diagnostic code was confined to the separate probe deployment. [Vercel Python runtime](https://vercel.com/docs/functions/runtimes/python) · [Provider migrations](../../backend/apps/providers/migrations)

## 4. Preview profile and access

**VERIFIED** All nine existing Preview values match the requested profile. The Stage 1 application inherited them. Preview and Production environment metadata stayed unchanged throughout the run.

| Setting | Value |
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

**VERIFIED** Anonymous `GET /api/health` on the new Preview returned Vercel `401`, with no MDC contract body or Bearer challenge. The same request through the authenticated Vercel CLI returned MDC `200`. The acceptance client supplied neither an MDC `Authorization` header nor `X-MDC-Actor-Id`. The subsequent creates, updates, and deletes succeeded, and Django enforced missing and stale strong ETags. [Vercel CLI protected access](https://vercel.com/docs/cli/curl) · [Deployment Protection](https://vercel.com/docs/deployment-protection)

## 5. Live endpoint results

**VERIFIED** All thirteen canonical Stage 1 methods were exercised against the same protected Preview. The HTTP codes below include the number of occurrences in the 38-request suite.

| Method | Route | Observed status and count | Result |
| --- | --- | --- | --- |
| GET | `/api/health` | `200` × 1 | Healthy, contract `1.0` |
| GET | `/api/catalog/filters` | `200` × 1 | Vocabulary present |
| POST | `/api/service-discovery/search` | `200` × 1 | Standalone spur-gear search returned Tasowheel and Precipart |
| POST | `/api/provider-publication/validation` | `200` × 1, `400` × 1 | Valid payload normalized. Invalid payload returned `invalid_provider_publication`. |
| POST | `/api/provider-publication` | `201` × 1, `409` × 1 | Registered disposable provider and first offering. Duplicate provider returned `provider_already_exists`. |
| GET | `/api/providers/{provider_id}` | `200` × 3, `404` × 2 | Initially absent, strong ETag on reads, update persisted, then absent after deletion |
| PATCH | `/api/providers/{provider_id}` | `200` × 1, `428` × 1, `412` × 1 | Current ETag succeeded. Missing ETag returned `concurrency_precondition_required` and stale ETag returned `provider_precondition_failed`. |
| DELETE | `/api/providers/{provider_id}` | `200` × 1 | Deleted provider and remaining offering using the latest provider ETag |
| GET | `/api/providers/{provider_id}/offerings` | `200` × 3, `404` × 1 | Listed first offering, both same-category IDs, then only the survivor. List became absent with the provider. |
| POST | `/api/providers/{provider_id}/offerings` | `201` × 1, `409` × 1 | Created the second independent ID in the same category. Duplicate ID returned `offering_already_exists`. |
| GET | `/api/offerings/{offering_id}` | `200` × 6, `404` × 5 | Both offerings read independently with strong ETags. The first remained unchanged when the second was edited. The final reads confirmed absence. |
| PATCH | `/api/offerings/{offering_id}` | `200` × 2, `412` × 1 | Updated the second offering. Whole-map replacement removed the vertical flange attribute and kept the horizontal value. Stale ETag returned `offering_precondition_failed`. |
| DELETE | `/api/offerings/{offering_id}` | `200` × 1, `428` × 1 | Missing ETag rejected. Deletion with the latest ETag removed the second offering while preserving the first. |

The suite used M6 request examples and sent strong revisions through `X-MDC-If-Match` because the earlier M5-A Vercel run documented false precondition failures from intermediary handling of `If-Match`. The pinned backend retains the canonical `If-Match` contract. **NOT VERIFIED** Current live coverage of the canonical header's intermediary behavior. [M6 contract and examples](../Partner_API/MaaSAI_MDC_M6_Marketplace_Integration_Guide.md) · [M5-A transport evidence](../codex/Reports/M5A_postgresql_lifecycle_vercel_postman_report.md)

| Acceptance total | Count |
| --- | ---: |
| Live Preview requests | 38 |
| Assertions | 166 |
| Assertion failures | 0 |
| Expected error responses | 15 |

Expected negative cases are included in the assertion totals. Protection and database preflight probes, the six public Production baseline requests, and the final read-only cleanup query are separate from this suite.

## 6. Publication and cleanup evidence

**VERIFIED** The disposable provider `mdc_stage1_resume_20261124_d435cbb08b` and its two disposable offerings were the only test targets. The seven successful write receipts each reported `accepted / sync_pending / pending`. The suite verified `404` for both offerings, the provider, and its offering list at the end. A read-only SQL check in the verified Neon branch returned the following counts for the same disposable identities and receipt IDs.

| Database evidence | Count |
| --- | ---: |
| Remaining disposable operational providers | 0 |
| Remaining disposable operational offerings | 0 |
| Remaining certifications for the disposable provider | 0 |
| Publications matched to HTTP receipt IDs | 7 |
| Publications in `sync_pending` | 7 |
| Publications with detached provider and redacted payload or tombstone | 7 |
| Delete publications | 2 |
| Outbox events pending with zero attempts and no processed timestamp | 9 |
| Delete outbox events | 3 |

The retained publications and outbox events are expected. The test did not invoke Fuseki updates, outbox recovery, or synchronization. **NOT VERIFIED** Immediate semantic visibility of new provider records, which belongs to Stage 2.

## 7. Production and repository preservation

**VERIFIED** Before and after Stage 1, `maasai-mdc-v1.vercel.app` mapped to `dpl_GmWLQStvb3qo551uYYUv4zLiW1XK`. The deployment was `READY`, with source `b9275258bf4a2455814ad9b2af9621e0a5d01327` and its original aliases. Health, filters, and standalone discovery returned `200` in both runs. The spur-gear search returned the same two expected matches. No Production deployment, alias, or environment setting was changed.

**VERIFIED** The GitHub resume branch starts from current fetched `origin/main`, `39e4570cc7839806e1db2a03bf5a7f58437f4acf`. Only this report is added. The previous blocked-report branch stays at `4e380b6a91e9500587cecfc06f9bb81a025278ee`. The original checkout retained its unrelated frontend and `.gitignore` edits. The application uploaded from the separate pinned worktree. [Public Production health](https://maasai-mdc-v1.vercel.app/api/health) · [Public catalogue filters](https://maasai-mdc-v1.vercel.app/api/catalog/filters)

## 8. Postman configuration

1. Import the existing M6 collection and environment. Set `base_url` to the protected Preview URL in Section 2, `automatic_sync_enabled=false`, and `concurrency_required=true`.
2. Select no MDC authorization and omit the actor header. Supply the operator-approved Vercel protection credential separately through the local vault. Exclude it from exports and logs.
3. Verify edge denial without Vercel authentication and `200` from authorized health before running writes. Run the spur-gear discovery request separately because automatic-mode discovery assertions are skipped in the collection.
4. Use unique disposable IDs and latest strong ETags. The live suite used the documented Vercel transport alias. Complete the cleanup folder and verify the final `404` responses.

[M6 Postman collection](../Partner_API/MaaSAI_MDC_M6_Marketplace_Integration.postman_collection.json) · [M6 Postman environment](../Partner_API/MaaSAI_MDC_M6_Marketplace_Integration.postman_environment.json) · [M6 joint-test checklist](../Partner_API/MaaSAI_MDC_M6_Marketplace_Joint_Test_Checklist.md)

## 9. Rollback and Stage 2 prerequisites

Keep Vercel protection active and stop Preview test traffic if a subsequent run fails. Retire only the affected Preview by its exact deployment ID in the existing project. The read-only probe and the Stage 1 application are separate deployment IDs. This run changed no stored Preview settings, so no configuration rollback is needed. If an ambiguous response follows a disposable write, read the resource and publication state before retrying, then use the latest strong ETag for cleanup. Leave the Production alias on its recorded deployment.

Stage 2 requires a verified stable Fuseki query and Graph Store pair for the same dataset, a recoverable graph and database state, and a private outbox recovery path. Validate exact offering-ID visibility and removal after publication in that stage. [M6 production readiness checklist](../Partner_API/MaaSAI_MDC_M6_Production_Readiness_Checklist.md) · [Historical M5-B validation](../codex/Reports/M5B_fuseki_immediate_discovery_validation_report.md)
