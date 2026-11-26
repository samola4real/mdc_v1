# Task 13 — Automatic semantic synchronization

**BLOCKED · 2026-11-26.** The local validation target is reachable and empty. The protected Vercel runtime probe requires an authenticated CLI session. Neither new Preview has been deployed, and both synchronization flags remain disabled.

Reviewed `origin/main` at `734f8bdeda12c976f3c8e8de4122895403cf8fe2`. The diagnostic and Stage 2 packages use the accepted backend source `004fef8f0db73ef3e12c1035ec470c131dcb99a6`. Task 12 infrastructure was reused from report commit `54581dd145cf1905d72c0df1396d9ec5d6999dc7`. [Task 13 prompt](../prompts_phase4/13_MDC_Stage2_Automatic_Semantic_Synchronization_Prompt.md) · [Task 12 report](12_MDC_Stage2_Fuseki_Integration_Readiness_Report.md)

## Pre-enable result

- The existing `mdc-fuseki-validation` container was running on loopback port 3031 with the dedicated `mdc_stage2_fuseki_validation_data` volume. The existing filter and Cloudflare processes were active. Local and HTTPS SPARQL both returned HTTP 200 with zero default-graph triples. Local named graphs also contained zero triples. HTTPS Graph Store HEAD returned 401 anonymously, and the public admin route returned 404. These were workstation checks.
- The local Vercel CLI returned an invalid-token error and then reported that it had no credentials. The connected Vercel tool provided read-only deployment records. Its create-deployment interface lacks the deployment-scoped environment input needed to give the new runtimes the validation endpoints, credentials and flags. Shared project variables and deployment protection were preserved.
- A separate Python 3.12 diagnostic package and the unchanged Stage 2 backend package are staged locally. The diagnostic is configured to require the `iad1` runtime, both flags explicitly off, and the canonical HTTPS query and default-graph endpoints for `mdc_validation`. Its code uses the existing MDC clients, verifies graph emptiness before any marker write and restores the empty graph after proving read-back. The package passed a syntax check. No diagnostic or Stage 2 deployment ID has been allocated.

## Read-only publication preflight

A read-only transaction used the exact Neon validation database on project `mute-cell-38148661`, branch `br-wild-haze-aej09lb1` and compute `ep-damp-water-aeg29kmn`. PostgreSQL reported `mdc_validation`, read-only mode, and 22 Django migrations including all four provider migrations through `0004_cataloguesynclease`.

| Check | Actual result |
| --- | --- |
| Current database catalogue | 3 providers and 5 offerings. The RDF contains Tasowheel, Precipart and the accepted Stage 1B disposable provider with their five exact offering IDs. |
| Publication ledger | 49 rows, with 28 `sync_pending` and 21 `synced`. The existing bounded selector returned 28 eligible publications. |
| Outbox and lease | 65 events, with 38 `pending` and 27 `succeeded`. One lease row had no owner. |
| RDF preview | 836 unpublished triples before the revision marker. The literal scan found no email addresses or credential patterns. All 15 distinct provenance notes matched the checked-in curated Tasowheel and Precipart sources. |
| Protected deployments | Stage 1B `dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea` and production `dpl_GmWLQStvb3qo551uYYUv4zLiW1XK` both remained Ready in `iad1`. The production alias still resolved to the latter. |

The checks left the validation database and both Fuseki deployments untouched. The original industrial `mdc` graph returned 731 triples with the same sorted-binding SHA-256 as Task 12, `513a1f00d138dec9edaa7de0d740397fdce0d8f1c1b939d2752007601c65e2d5`. The Stage 1B frontend pin was preserved.

## Resume and rollback

Restore the local Vercel CLI sign-in for the existing `mdc19` account with `vercel login`. Continue from the separate protected diagnostic Preview in `iad1`, with both flags `false`. Verify outbound TLS, parsed SPARQL, Graph Store authentication, one isolated default-graph write and read-back, and authenticated restoration of the empty graph. Retire that diagnostic after verification. [Vercel CLI authentication](https://vercel.com/docs/cli/login) · [Deployment-scoped runtime variables](https://vercel.com/docs/cli/deploy#env)

Only after the probe passes, create the separate protected Stage 2 Preview with the current validation-only endpoint pair and both flags `true` scoped to that deployment. Recheck the validation database and RDF projection before using `sync_service_discovery_catalogue --rebuild` and the existing bounded pending-publication processing. Verify authoritative discovery, then perform the one authorized disposable lifecycle smoke without a manual synchronization trigger. The published revision, outbox reconciliation and disposable create/delete evidence all remain pending.

A Quick Tunnel restart changes its HTTPS origin. Refresh both endpoint settings together and repeat runtime verification. If a later activation fails, stop Stage 2 writes and return to the pinned Stage 1B Preview. Retire or disable only the new runtime as appropriate. A runtime rollback preserves committed database publications and the graph for investigation. Keep the Stage 1B frontend pin and production alias in place.
