# M5-B — Temporary Fuseki connectivity and immediate semantic discovery validation

## Objective

Complete the remaining M5 semantic-integration validation after accepted M5-A.

M5-A already proved the deployed Vercel -> Django -> Neon PostgreSQL provider lifecycle. M5-B must now prove the missing end-to-end semantic path:

**provider lifecycle write -> PostgreSQL commit -> RDF rebuild -> Fuseki publication -> revision verification -> immediate canonical consumer discovery**

This is a temporary validation setup only. The future MaaSAI infrastructure may host Fuseki on AWS. Do not turn Cloudflare into a permanent architectural dependency.

## Baseline

Repository: `samola4real/mdc_v1`

Work from latest `main`, which includes accepted M5-A merge commit:

`e62f332bd97f4e76d3d32f2f322547ae8adde138`

Existing accepted M5-A facts:
- Vercel Preview project: `mdc19/maasai-mdc-v1`
- Accepted Preview database: isolated Neon `mdc_validation`
- Provider migrations through `providers.0004_cataloguesynclease` are applied
- M5-A lifecycle acceptance passed 35 requests / 81 assertions / 0 failures
- Production must remain unchanged
- M6 must not start
- Existing real local Fuseki `mdc` dataset must not be modified, replaced, exposed, reset, or used for M5-B

Create a new branch:

`phase4/m5b-semantic-validation`

Use a clean linked worktree. Do not touch or overwrite unrelated changes in the user's original checkout.

## Critical safety rule

**Do not connect the M5-A `mdc_validation` PostgreSQL database to the existing real local Fuseki `mdc` dataset.**

M4 synchronization rebuilds/replaces the full default graph from current active PostgreSQL state. The validation database is intentionally isolated and mostly empty outside disposable test data. Pointing it at the real `mdc` dataset could replace the real graph.

M5-B must use a completely isolated disposable Fuseki target.

## Phase 1 — Prepare isolated disposable Fuseki

1. Inspect the existing Docker/Fuseki setup read-only.
2. Leave the current `mdc-fuseki` container, its persistent volume, and its `mdc` dataset untouched.
3. Create a separate disposable Fuseki validation instance, preferably as a second Docker container on a different host port such as `3031`, with a separate volume or ephemeral storage and a separate dataset named `mdc_validation`.
4. Do not mount or reuse the existing Fuseki data volume.
5. Confirm locally that:
   - `/mdc_validation/sparql` is reachable;
   - `/mdc_validation/data?default` is reachable for Graph Store operations;
   - query and Graph Store refer to the same isolated dataset;
   - the real `mdc` dataset/container remains unchanged.
6. Prefer protecting the disposable Fuseki endpoints with credentials if the current application can support that safely. If a minimal config-driven HTTP Basic-auth addition is required for the SPARQL query client, implement it narrowly and preserve existing behavior/defaults. Do not hard-code credentials. Do not add provider-specific logic.

## Phase 2 — Temporary remote connectivity

The user does not have a Cloudflare-managed domain and does not want to purchase one for this temporary validation.

7. Use Cloudflare only as a **temporary transport for M5-B validation**. Do not create a permanent Cloudflare architectural dependency.
8. Prefer a temporary Quick Tunnel only if it exposes **only the isolated disposable Fuseki validation instance**, never the real `mdc-fuseki` service or host port 3030.
9. If Quick Tunnel cannot be used safely under these constraints, stop and report the exact blocker instead of weakening isolation or exposing the real Fuseki service.
10. Do not publish secrets, tunnel tokens, database URLs, Fuseki passwords, or Vercel credentials in Git, reports, terminal transcripts committed to Git, or chat.
11. Keep the temporary tunnel process alive only for the validation window. Record only the safe hostname if needed in the report; do not commit ephemeral secrets.

## Phase 3 — Configure Vercel Preview only

12. Reuse the existing Vercel project `mdc19/maasai-mdc-v1`.
13. Use Preview only. Do not modify or promote Production.
14. Continue using the isolated Neon `mdc_validation` database.
15. Configure Preview so the semantic target is the isolated remote Fuseki validation dataset:
   - `MDC_PROVIDER_PUBLICATION_ENABLED=True`
   - `MDC_PROVIDER_VALIDATION_ENABLED=True`
   - `MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=False`
   - `MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=False`
   - `MDC_PROVIDER_CONCURRENCY_REQUIRED=True`
   - `MDC_CATALOG_SYNC_ENABLED=True`
   - `MDC_CATALOG_AUTO_SYNC_ENABLED=True`
   - `MDC_DEMO_API_ENABLED=False`
   - `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT=https://<temporary-host>/mdc_validation/sparql`
   - `SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT=https://<temporary-host>/mdc_validation/data?default`
   - configure only required credentials/timeouts through environment variables
16. Ensure M4 same-dataset validation accepts the configured query and Graph Store pair.
17. Deploy a fresh Preview from the reviewed branch commit and record the exact deployed SHA and Preview URL.

## Phase 4 — Full M5 semantic acceptance

18. Reuse the original full M5 semantic lifecycle intent, but operate only on disposable `postman_m5b_*` provider IDs and the isolated validation database/dataset.
19. Run live HTTP/Postman acceptance against the deployed Preview and verify at minimum:

   a. baseline health/filters/search are reachable;

   b. register a disposable provider with one offering;

   c. lifecycle response reports verified completion (`completed/synced/succeeded` or the exact current contract equivalent), not merely pending;

   d. the **very next canonical** `POST /api/service-discovery/search` finds that new offering through authoritative Fuseki;

   e. add a second same-category offering; immediate search finds both distinct offering IDs;

   f. PATCH offering/provider data; immediate search reflects the updated searchable values where the query contract supports them;

   g. remove an optional searchable attribute through the supported whole-selected-map PATCH semantics; verify PostgreSQL and semantic result behavior;

   h. DELETE the second offering with current ETag; the next canonical search no longer returns it while the sibling remains;

   i. DELETE the provider with current ETag; the next canonical search no longer returns the provider/offerings;

   j. negative concurrency/validation cases continue to behave as documented;

   k. no unrelated provider data exists or changes in the isolated validation database/dataset.

20. Verify the M4 revision marker round-trip rather than treating HTTP 200 from Graph Store alone as success.
21. Verify canonical search is operating in authoritative Fuseki-only auto-sync mode during the test. A stale/unavailable Fuseki revision must result in the expected safe failure behavior rather than YAML/local-RDF fallback.
22. Inspect `ProviderPublication` and `CatalogueSyncEvent` states after the definitive run. Successful events should reflect completed/succeeded synchronization rather than remaining pending.
23. Clean up disposable operational provider/offering rows through the public lifecycle API, not direct SQL. Confirm semantic disappearance after cleanup.
24. If any mutation commits to PostgreSQL but semantic publication returns 503/failed, do not blindly repeat non-idempotent registration. Inspect current provider/publication/outbox state first and use the existing recovery path.

## Phase 5 — Regression, documentation, and teardown

25. Run focused lifecycle/sync/search tests and the full Django suite. Also run:
   - `manage.py check`
   - `makemigrations --check --dry-run`
   - `git diff --check`
26. Fix the previously noted partner-guide documentation inconsistency if still present: automatic verified synchronization should use the current actual lifecycle contract (M4 reports completed/synced/succeeded). Do not change runtime behavior merely to match stale prose.
27. Stop/remove the temporary Quick Tunnel after evidence is collected.
28. Leave the disposable Fuseki validation container stopped or remove it if its only purpose was this test. Do not touch the real `mdc-fuseki` container or dataset.
29. Do not promote Preview to Production.

## Required report

Write:

`mdc-catalog/docs/codex/Reports/M5B_fuseki_immediate_discovery_validation_report.md`

Also append a concise M5-B outcome section to:

`mdc-catalog/docs/codex/Reports/M5_vercel_deployment_and_postman_validation_report.md`

The report must include:
- branch and final commit;
- deployed Preview URL and exact deployed commit;
- isolated Neon database name;
- isolated Fuseki container/dataset identity and proof that real `mdc` was untouched;
- temporary tunnel method/status;
- safe endpoint shapes without secrets;
- all relevant environment flag values (non-secret only);
- live request count/assertion count/failures;
- evidence for register -> immediate search -> update -> immediate search -> delete -> immediate absence;
- revision verification outcome;
- outbox/publication states;
- regression results;
- cleanup/teardown status;
- any remaining blocker before Production/plenary;
- explicit statement that Production was unchanged and M6 was not started.

## Stop conditions

Stop and report rather than improvising if any of the following occurs:
- the only way forward would expose or modify the real `mdc` Fuseki dataset;
- the validation database cannot be isolated from real provider data;
- Cloudflare temporary transport cannot safely target only the disposable Fuseki instance;
- a required secret/permission is unavailable;
- a migration or deployment action appears destructive;
- the deployed API contract differs materially from the accepted M4/M5-A behavior.

Commit and push the scoped changes to `phase4/m5b-semantic-validation`. Do not merge to main. Return a short completion summary for review.
