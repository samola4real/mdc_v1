# M1 — Lifecycle baseline and API readiness (Codex task prompt)

**Status:** Implementation task, milestone M1 only. **Repository:** `samola4real/mdc_v1`. **Working directory:** `mdc-catalog/`.

## Project instruction and scope

Follow the milestone plan at `docs/codex/current_refractor _plan.md` (note the space in its filename), particularly M1. Read current code and tests as the authority for implemented behavior; use the latest integrated backend/frontend manuals only to clarify an ambiguity, not obsolete milestone documents. Do not start M2–M6 in this task. Do not alter the demo frontend, real provider data, route/operation-sequence scope, API URL versioning, or established canonical public search contract.

The user wants a **backend-first MaaSAI plenary pilot**, accessed from Postman and later from other MaaSAI components. For this pilot, the API should work **without JWT, bearer token, API key, or actor header** on the explicitly configured pilot deployment. This is a **temporary, reversible configuration**, not removal of the existing authentication code or its secured-mode tests. Keep existing `/api/` routes (do not add `/api/v1/`). The future target of M4 is that a successfully published change is visible to the next canonical discovery request, but **do not implement synchronization in M1**.

## Required execution procedure

1. Confirm actual repository root, branch, HEAD, remotes, and worktree status. Fetch `origin/main` before implementation. Do not overwrite user changes or run hard reset. If unsafe/dirty, stop and report the blocker. Create a focused branch `phase4/lifecycle-baseline` from up-to-date `origin/main` (or, if the name exists, use a clearly named M1 follow-up branch). Do not merge to main or deploy.
2. Audit only the current code paths relevant to M1: URL routing; GET/POST lifecycle views; serializers; lifecycle security and concurrency; provider models/repository/write service; production/local settings and env example; database configuration; current catalogue outbox, RDF/Fuseki integration and runtime discovery selection; relevant tests. Distinguish actual behavior from claims in old docs.
3. Produce a concise **baseline table** of current GET/POST/PATCH routes, supported methods, validation, feature gates, auth/actor requirements, concurrency requirements, persistence target and response behavior. Record clearly that DELETE and multiple distinct offerings in the same service category are **M3/M2 work, not M1**.
4. Audit whether the existing switches `MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED`, `MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED`, `MDC_PROVIDER_CONCURRENCY_REQUIRED`, and publication/validation/sync flags already permit the required pilot configuration. Reuse them rather than introducing redundant flags. Make the **smallest necessary** configuration/documentation/test changes for a named, explicitly opted-in pilot mode: no authorization or actor header required for the scoped lifecycle API when auth/actor flags are false; preserve the secured-mode behavior when true. Keep ETag / If-Match concurrency semantics independent and unchanged. If no code change is necessary, state so and document the exact non-secret pilot variables and tests. Do not silently switch secure defaults off in general production settings. Do not put secrets in source or commit `.env`.
5. Check whether `POST /api/service-discovery/search` is public and distinguish its behavior from provider-publication POST. Assess likely POST blockers from actual settings/code (feature flags, validation, authentication, database configuration), without asserting a specific cause for the Marketplace team's failures unless evidence exists.
6. Establish which canonical discovery backend is selected by settings and runtime. Trace whether a newly committed provider record currently becomes discoverable automatically or needs explicit outbox/Fuseki synchronization. Identify exact relevant code paths and M4 blockers, without changing sync behavior now.
7. Test using disposable in-memory/test-database records only. Never mutate real Tasowheel, Framo Morat, production Vercel or Neon records. Run targeted tests for public GET/POST, provider lifecycle GET/POST/PATCH, opt-in unauthenticated pilot mode, preserved authenticated mode and ETag checks; run an appropriate regression suite if feasible. Record commands, counts, and all skips/failures honestly. Never claim deployed behavior based on local tests.
8. Write the M1 report to `docs/codex/Reports/M1_lifecycle_baseline_and_api_readiness_report.md`. Include: checked branch/commit and worktree; code paths inspected; implemented changes (or none); route/flag matrix; pilot configuration values (no secrets); current DB and actual discovery-backend behavior; M2–M4 dependency/blocker list; tests and results; files changed; outstanding questions; deployment state explicitly **not deployed**; final commit SHA.
9. Commit only intended M1 changes and report on the focused branch, with a conventional commit message such as `chore(lifecycle): establish pilot baseline`. Push that branch to the personal GitHub repository only. Do **not** merge, deploy to Vercel, write into production data, rotate credentials, change external infrastructure, or begin M2. If push/auth permissions are unavailable, report this accurately and provide the local branch/commit information.

## Acceptance gate

- M1 report exists at the specified path on the pushed branch and is reviewable.
- Existing canonical public API behavior and provider lifecycle payloads remain intact.
- The temporary pilot no-auth configuration is explicit and reversible; secured-mode code/tests are preserved; ETag tests remain valid.
- The report distinguishes local/test findings from deployed facts and identifies the concrete M2 and M4 integration risks.
- No real provider data, shared Vercel configuration, or frontend code was modified.

**Stop after M1 and send the user a short completion summary**: branch, commit SHA, report path/URL, changed files, test counts, blockers, and “awaiting review before M2.”
