# M2 — Scalable provider and offering management (Codex task prompt)

**Milestone:** M2 only. **Repository:** `samola4real/mdc_v1`. **Project root:** `mdc-catalog/`.
**Prerequisite:** M1 branch `phase4/lifecycle-baseline` merged to `origin/main` (M1 reviewed merge commit `ad8c85e30280496d80b46d8ab076e1fc45d26f09`). Refer to `docs/codex/current_refractor _plan.md` for context; the current code and passing tests are the authoritative implementation baseline.

## Goal

One provider can register and subsequently add **multiple independently identifiable offerings in the same controlled service category**, as well as in different categories. Preserve all existing provider IDs and offering IDs, and keep onboarding and search generic for future MaaSAI providers. This is an incremental backend refactor, **not** a new publication system.

## Working-copy and scope rules

1. Fetch the latest `origin/main`; confirm M1 is merged. Inspect HEAD, branch, and worktree. The original local checkout has unrelated uncommitted `.gitignore` and `mdc-catalog/demo-frontend/src/pages/demo/index.js` changes. **Do not modify, stash, commit, discard, overwrite, reset, or pull over those changes.** Create a separate clean linked worktree from current `origin/main` on `phase4/multi-offering` (or a clearly named follow-up branch if already present). If a safe worktree is unavailable, report the blocker. Never deploy or merge in this task.
2. Change only M2-relevant backend code, migrations **if actually required**, tests, and concise API/identity documentation. Do not change frontend/demo routes, production/Neon/Fuseki data, deployed Vercel configuration, authentication flags, ETag/concurrency behavior, URL paths, contract-version convention, controlled vocabulary semantics, or excluded route/operation-sequence fields. Do not implement M3 DELETE, M4 automatic sync, or M5 deployment.

## Inspect the actual M2 code paths first

Read only relevant current implementations and tests, including `apps/providers/models.py`, `provider_lifecycle_write_service.py`, `service_discovery_publication.py`, `service_discovery_db_repository.py`, `provider_lifecycle_repository.py`; `apps/api/service_discovery_publication_serializers.py`, `provider_lifecycle_serializers.py`, `views/post_views.py`, `views/get_views.py`; ontology RDF identity/generation and discovery projection, relevant database migrations and API/RDF tests. Identify and report every place that assumes `offering_id == provider_id + '_' + service_category`.

## Identity and API behavior to implement

- A provider has stable `provider_id`; each offering has a stable, globally unique `offering_id` and one parent provider. **Service category classifies an offering; it must not determine its uniqueness.** The same provider may have several distinct offerings sharing `service_category` and `part_family`.
- Preserve every existing identifier and the existing single-offering registration payload/response contract. Preserve the legacy generated `provider_id_service_category` ID when that default is unambiguous, especially for existing tests and first offering. Do not rename, bulk-rewrite, or migrate existing IDs merely to fit a new format.
- Define and document one straightforward, consistent creation contract for both initial provider registration (possibly several offerings, including same-category) and `POST /api/providers/{provider_id}/offerings`:
  - Prefer an **optional explicit stable `offering_id`** for independent offerings, constrained to the owning provider and validated against a documented safe identifier grammar/length.
  - For omitted IDs, retain the legacy ID when unused, and derive a distinct deterministic ID using a safe offering-name slug when the legacy ID is already reserved/taken. Handle same-name collisions predictably (clear conflict/validation response or documented deterministic disambiguation); do **not** silently overwrite another offering.
  - Ensure duplicate input IDs (including within one registration), cross-provider ownership conflicts, concurrent duplicate creation, and invalid/forbidden identifiers are rejected cleanly (400/409 as appropriate). Maintain DB-level global uniqueness, not only a pre-query check.
  - Modify existing externally owned identifier rejection **narrowly** so `offering_id` is accepted **only at the supported offering-creation locations**. Do not allow arbitrary nested identifiers or weaken rejection of other protected identifier fields. An existing offering's ID must remain immutable under PATCH.
- Propagate the exact chosen offering ID consistently through normalization, database write, lifecycle GET/list response, outbox events, publication snapshots, RDF URI generation, RDF serialization, and canonical discovery result mapping. Preserve offering order, null-vs-absent capability evidence, provenance and controlled field validation. Ensure two same-category offerings have separate capability evidence and distinct search results; do not collapse by category or overwrite one another.
- Check the existing `Offering.offering_id` database uniqueness and actual migrations. **Avoid an unnecessary schema migration** if the collision exists only in application-level generation/validation. If any migration is necessary, demonstrate data preservation and reversibility for existing rows.
- Retain current M1 temporary pilot no-auth opt-in and secured-mode behavior. No extra headers are required for POST creation when M1 pilot flags are opted in; PATCH concurrency remains unchanged. The public `POST /api/service-discovery/search` contract must remain intact.

## Tests and evidence

Add focused tests for (a) first registration with legacy ID unchanged, (b) initial registration with two same-category offerings, (c) POST second same-category offering after registration, (d) independent GET/list/PATCH of one offering preserving sibling, (e) duplicate explicit ID in one payload and in DB, (f) invalid/cross-provider ID and immutable ID under PATCH, (g) independent RDF nodes and query/discovery projection with distinct IDs/capabilities, (h) authenticated and M1 pilot-mode compatibility, (i) a non-TSW disposable provider. Use only disposable local test DB records/mocked RDF; do not mutate external services or real provider records. Run relevant focused tests and the entire local test suite if practical. Report exact test commands and outcomes; report remote Fuseki/deployed tests as **not run** unless actually performed.

## Report, commit and stop

Write `docs/codex/Reports/M2_scalable_multi_offering_management_report.md` with: baseline and working branch/commit; original-worktree preservation; files changed; actual former collision points; selected creation/ID contract with example payloads and error cases; model/migration decision; evidence of ID preservation; tests/results; any remaining M3/M4 risks; **not merged/not deployed** state; final branch-tip commit SHA (or report that SHA in completion summary if report commit itself cannot contain its own SHA).

Commit scoped changes and the report to the focused M2 branch with conventional messages such as `feat(providers): support independent offering identities`; push to the personal GitHub repository. Do not merge, deploy, or proceed to M3. Return a brief summary (branch, commit SHA, report path/URL, changed files, test counts, blockers), then **await review**.
