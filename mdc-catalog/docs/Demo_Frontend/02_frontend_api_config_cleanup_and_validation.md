# Frontend API/Config Cleanup and Validation

## Purpose and scope

This milestone aligns the imported MaaSAI MDC demonstration frontend with the current public MDC API contract. The UI remains an illustrative pilot and is not the real Cloud MaaS Marketplace (CMM). Work started from `fc3e1675b98a91ff8628e4e17e3fd17ff6db6c2f` on `demo-frontend-integration`; the accepted sanitized baseline `e411e7300cfbe2f9f3f9fe245027f2c0c341cd38` remains in its ancestry.

No backend application code, original frontend repository content, Git remotes, GitLab state, package versions, or lockfile content was changed.

## Changed files by category

- API services: removed the unused stale `provider.service.js` browser lifecycle client and its barrel export; updated `client.js` error-envelope handling.
- Consumer search: updated `ConsumerSearchMockup.js`, `SearchResultsList.js`, `ProviderResultAccordion.js`, and `searchResultFormatters.js` for canonical filters and flattened result capabilities while retaining demo/historical compatibility.
- Demo boundary and access: updated provider wording, runtime status/error wording, and `routes.js`.
- Pages Router cleanup: moved `DashboardContent.js` and `NotFoundPage.js` from `src/pages/home/` to `src/components/home/`, then updated `/` and `/404` imports.
- Runtime/documentation: clarified `runtimeConfig.js` and `public/config.js`; replaced the generic README; removed the staging-only README draft.
- Baseline hygiene: normalized only the nine inherited whitespace files approved for this cleanup.
- Milestone evidence: added this report.

## Current API mapping

Canonical public browser calls:

- `GET /api/health`
- `GET /api/catalog/filters`
- `POST /api/service-discovery/search`

Demo-only calls retained for the illustrative provider/admin experience:

- `GET /api/demo/provider-publication/state`
- `POST /api/demo/provider-publication/preview`
- `POST /api/demo/provider-publication/simulate-update`
- existing read/status and explicitly demo-admin calls under `/api/demo/...`

The obsolete browser helpers for `/provider-publication/validate`, `/provider-publication/publish`, and collection-level `GET /api/providers` had no callers and were deleted. Trusted lifecycle writes remain server-to-server concerns requiring a future CMM or backend-for-frontend boundary; no service token, bearer header, actor header, or If-Match behavior was added to browser code.

## Filters and result normalization

Consumer search loads contract `1.0` filters from `/api/catalog/filters`, converts `{value,label}` entries for PrimeReact, derives service category from the selected family, and uses family-keyed part types without silently excluding newly returned values. Materials, processes, and certifications come from the canonical response. The prior static vocabulary is used only as a visible demo fallback if filter loading fails. Material grades are not sent as a canonical search criterion, and `match_policy.optional_match_mode` remains `score_only`.

The result adapter maps `matched_capabilities`, `unmatched_capabilities`, and `unknown_capabilities` into the existing suitability presentation while preserving their fields, values, statuses, and reasons. Canonical provider/offering fields and the response-level `part_type` are propagated for display. Materials, processes, and certifications remain visible when returned as capability entries. Historical/internal attributes remain compatible, and browser-generated overlay entries retain their explicit “Demo registered provider” label without inventing canonical evidence.

## Routes, runtime, and documentation

`/demo` remains public. `/demo/provider`, `/demo/consumer-search`, and `/demo/admin-audit` now require an authenticated Keycloak session at the central route layer. `DemoRoleGuard` remains a presentation control for selected demo roles, not a backend authorization boundary.

The production build no longer generates `/home/DashboardContent` or `/home/NotFoundPage`; intended home pages remain. Browser runtime configuration continues to load from `window.MAASAI_CONFIG` in `/config.js`. Localhost is documented only as a development default. Deployments must provide an appropriate HTTPS MDC API URL and matching CORS/origin policy, and browser configuration must contain no trusted lifecycle token or other secret. Provider/admin demo actions require a deliberately demo-enabled backend environment.

The project README now documents purpose, role/API boundaries, Node/npm expectations, commands, safe runtime configuration, deployment constraints, provenance, and the GitHub-development-to-GitLab-release boundary. Existing provenance and release-mapping documents remain authoritative.

## Validation

- `npm ci`: PASS using the committed lockfile; 358 packages installed, 0 vulnerabilities reported.
- `npm run lint`: PASS (exit 0); five pre-existing warnings remain in layout and stylesheet-loading code.
- `npm run build`: PASS on Node 22.15.0/npm 10.9.2 after rerunning outside a sandbox child-process restriction. The Docker baseline remains Node 20.18.0.
- Route table: PASS for `/`, `/demo`, `/demo/provider`, `/demo/consumer-search`, `/demo/admin-audit`, and `/404`; accidental component routes absent.
- Public smoke: PASS. Health, filters, and search returned HTTP 200 with contract `1.0`; filters contained all expected keys; search returned the flattened public result structure and capability arrays.
- Package manifests: unchanged after install.
- Generated `node_modules` and `.next`: ignored and untracked.
- `git diff --check`: required to pass before commit with no exception.

No GitHub Actions workflow was added. The workflow was optional, no existing frontend workflow defined a compatible repository policy, and adding CI would broaden this targeted milestone. Stronger automated frontend tests and scoped CI remain future work.

## Limitations and completion boundary

Future work is limited to real CMM/server-side lifecycle integration, deployment ownership for HTTPS/CORS/Keycloak configuration, stronger automated tests, and separately approved GitLab release preparation. This milestone does not claim that client-side roles secure backend APIs.

The completed change is committed with `fix: align MDC demo frontend with current API contract` on `demo-frontend-integration` and pushed only to the personal GitHub `origin` after every gate passes. The resulting commit SHA and local/remote synchronization are recorded in the execution report accompanying this document.
