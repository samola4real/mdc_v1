# Task 16F — Stage A spline correction and production release readiness

**27 November 2026 · READY FOR RELEASE APPROVAL**

## Decision summary

- **Spline correction verified in isolation.** Exact spline module 2 returns the Demo Metal Works and Tasowheel shaft offerings in both strict and lenient discovery after a conditional PATCH. It returned only Tasowheel before the correction. The existing Provider registration, add-offering and edit paths now write newly entered spline points as `exact`.
- **Authoritative read gate passed.** A new protected Preview ran the full Task 16E backend source with both sync flags active and write routes disabled. All 23 targeted API cases passed. Private runtime logs captured 22 successful searches after the existing revision guard checked the paired PostgreSQL and Fuseki catalogue before and after discovery.
- **Production and shared data remain at the baseline.** The stable alias retained its Task 15 deployment. The same strict smoke responses, six exact record fingerprints and the 837-triple validation graph matched before and after Stage A. The shared Demo spline still has `value: 2`.
- **Stage B requires explicit operator authorization.** The proposed changes are the single shared spline PATCH, the production cutover, and the separately scoped Precipart certificate publication if approved. The report includes the payloads and data rollback order. The existing Graph Store write-credential binding is required for any later production deployment with publication enabled.

[Protected authoritative Preview](https://maasai-mdc-v1-7l62onih5-mdc19.vercel.app/api/health) · [Signed-in local Consumer](http://localhost:3003/demo/consumer-search)

## 1. Spline capability and active writers

The exact shared record is provider `mdc_stage1b_accept_20261126_a`, offering `mdc_stage1b_accept_20261126_a_shaft`. The stable exact GET returned HTTP 200 with a strong ETag and the following scoped map.

```json
{
  "splined_shaft": {
    "spline_module": {
      "value": 2,
      "confidence": "declared",
      "source_type": "provider_confirmed"
    }
  }
}
```

A read-only Neon transaction on `mdc_validation` confirmed the same map. The original 26 November 2026 09:58:40 UTC update recorded `value: 2` in both the submitted and normalized spline record. A later synchronized update retained it without submitting a new spline value. The form offered a single decimal **Spline module** entry for Splined shaft. The Consumer serialized that single metric module as `exact`. Together, the original update and the one-point control establish the intent as exact module 2, with the original declared provenance. [Shared exact GETs](assets/task16f-final-production-release/shared-detail-before.json) · [Original publication history](assets/task16f-final-production-release/spline-publication-history.json) · [Task 16E probe](assets/task16e-comprehensive-discovery-validation/legacy-spline-probe.json)

The active Provider UI registered and edited that point as `value`. The existing lifecycle serializer accepts the numeric capability record and carries its field into normalized and persisted JSON. Discovery and the harmonized RDF projection use the scoped `exact`, `min` and `max` fields for comparable range evidence. A legacy point can therefore appear in exact details while remaining insufficient for an exact search.

The shared Provider form now emits `exact` for newly entered points. Manage Offering still displays a saved legacy point as an editable draft. An unrelated edit leaves its stored map intact. An explicit point change replaces the legacy key and retains its provenance and other typed capabilities. Saved ranges and conflicting point shapes remain protected from the single-point editor. The matcher and its accepted eligibility rules are unchanged. [Writer](../../demo-frontend/src/components/mdc/providerRegistrationPayload.js) · [Edit mapping](../../demo-frontend/src/components/mdc/providerManagementDraft.js) · [RDF projection](../../backend/apps/ontology/service_discovery_rdf_generator.py)

## 2. Isolated correction and exact expected-versus-actual searches

The test imported the frozen Task 16E five-offering catalogue into in-memory SQLite. It used the existing conditional lifecycle API and an isolated RDFLib graph. The Fuseki client and revision-check transport used SPARQL bindings from that graph. The automatic publication code produced a single offering sync event and the `completed / synced / succeeded` receipt. The corrected map matched the database and exact GET. The parent and target ETags changed, the other business fields and records compared equal, and the sibling metal detail stayed identical. Missing and stale preconditions returned 428 and 412. A negative module was rejected with 400 and the old detail remained intact. [Isolated test and receipt evidence](assets/task16f-final-production-release/isolated-spline.json)

The independent expectation used the confirmed Tasowheel inclusive spline range 0.3–10 and the corrected Demo exact point 2. The table applies to each of the two separately executed modes, strict and explicit lenient. D-S means `mdc_stage1b_accept_20261126_a_shaft` for Demo Metal Works Oy. T-S means `tasowheel_precision_shafts` for Tasowheel Oy. Offering order and identities were checked across direct matching, RDFLib and the mocked Fuseki retrieval path.

| Requested exact spline module | Before expected | Before actual | After expected | After actual | Result in both modes |
| ---: | --- | --- | --- | --- | --- |
| Omitted | D-S, T-S (2) | D-S, T-S (2) | D-S, T-S (2) | D-S, T-S (2) | PASS |
| 0.299 | None (0) | None (0) | None (0) | None (0) | PASS |
| 0.3 | T-S (1) | T-S (1) | T-S (1) | T-S (1) | PASS |
| 1 | T-S (1) | T-S (1) | T-S (1) | T-S (1) | PASS |
| 1.99 | T-S (1) | T-S (1) | T-S (1) | T-S (1) | PASS |
| **2** | T-S (1) | T-S (1) | **D-S, T-S (2)** | **D-S, T-S (2)** | **PASS** |
| 2.01 | T-S (1) | T-S (1) | T-S (1) | T-S (1) | PASS |
| 3 | T-S (1) | T-S (1) | T-S (1) | T-S (1) | PASS |
| 4 | T-S (1) | T-S (1) | T-S (1) | T-S (1) | PASS |
| 10 | T-S (1) | T-S (1) | T-S (1) | T-S (1) | PASS |
| 10.001 | None (0) | None (0) | None (0) | None (0) | PASS |
| 12 | None (0) | None (0) | None (0) | None (0) | PASS |

This covers 48 before/after requests across three paths. Exact module 2 displayed `{"exact": 2}` in the Demo match evidence. With Steel/Titanium and Turning added, strict returned zero because the exact material intersection did not hold. Lenient returned both, with Demo full and Tasowheel partial because Turning remained unconfirmed. The negative module search returned HTTP 400. Gear and Roller result bodies matched before and after in both modes. A frontend fixture also checked that changing the spline point retains an additional spline length and a different subtype's measurements.

The corrected results above are isolated. The existing hosted Fuseki dataset is shared and was exercised read-only. Its exact module 2 search still returns T-S only in both modes. [Shared Preview smoke](assets/task16f-final-production-release/authoritative-preview-smoke.json) · [Shared data after verification](assets/task16f-final-production-release/shared-after-verification.json)

## 3. Protected authoritative Preview

| Evidence | Verified result |
| --- | --- |
| Project and deployment | `mdc19/maasai-mdc-v1`, `dpl_AnNpcrAY9RdN2hmDjfWAq11ricNy`, Ready in `iad1`. An anonymous health request redirected with 302. Authorized health, filters and exact reads returned 200. Legacy demo health returned 404. |
| Source | Backend archive from `ff025fd7b0b9d411cabd7a08f78362767562f6ee`, SHA-256 `8c39e0c9cbf3eda14fc047e32101174944de3fade685864a31b851e256a76308`. Six uploaded source digests matched, including the runtime, settings, certification vocabulary, curated Precipart and generated RDF. |
| Runtime binding | Existing project Preview database entry connected to the current validation catalogue. Deployment-scoped HTTPS query and default Graph Store URLs pointed to the same `mdc_validation` dataset. Anonymous Graph Store HEAD returned 401. The read guard requires the paired endpoint URLs and reads the DB watermark and SPARQL revision. This configuration supplied no Graph Store credential overrides. |
| Effective profile | `MDC_CATALOG_SYNC_ENABLED=True` and `MDC_CATALOG_AUTO_SYNC_ENABLED=True`. Publication, validation and demo were all `False` in the runtime proof. Lifecycle actor and concurrency safeguards remained enabled. |
| Exact revision proof | 22 successful smoke searches produced private Vercel logs after both guard checks. The logged revision `7c79b16dba232163baa27d0c6553c298572f9475aa4c508ad6d4ded80e4348d4` matched independent Fuseki SELECTs before and after. The synchronized Roller came from the current validation graph, with 837 triples. |
| Failure mode | With automatic mode enabled, missing or changed visibility returns a canonical 503 and skips bundled fallback. Existing targeted local tests exercised the unavailable and changing revision paths. |
| Production preservation | The production alias stayed at `dpl_AdG2ZD9Lhic25LQ4E6rf7YJLgsPF`, Task 15 source `c6980293c5de9fd1e9d7449d664be8fa847d3a2e`. The 15-search strict smoke and ancillary reads compared byte-for-byte, SHA-256 `091b2165acf70056d1310993b66343e616c9a58c35d81c0052f40fc3b17ab2e7`. |

The opt-in proof logs only a successful existing read guard, its revision fingerprint and boolean flags. It runs in a protected Preview profile and adds no public diagnostic route or response fields. The candidate contains the full reviewed local certification source. Authoritative runtime reads the shared graph, where the certificate remains unpublished.

| Live query | Result |
| --- | --- |
| Module 1 / 4 / 12 in strict and lenient | Precipart plus Tasowheel / Tasowheel / zero |
| Strict generic Steel, default and legacy any/all/score_only policies | Zero |
| Lenient Steel + Titanium | Tasowheel's alloyed steel confirms the OR group and Titanium remains unconfirmed. Precipart is retained with unconfirmed material preferences. |
| Lenient Aluminum + Titanium | Two hard-eligible offerings with unresolved material alternatives |
| Required ISO 9001 + ISO 14001 | Tasowheel only |
| ISO 13485, AS9100, or ISO 9001 + AS9100 in shared data | Zero |
| Exact spline module 2, strict and lenient | Tasowheel shaft only on the shared graph |
| Roller, strict and lenient | Retained Demo metal offering in both |
| Lenient explicit cutoff of zero | Canonical HTTP 400 |

[Deployment details](https://vercel.com/mdc19/maasai-mdc-v1/AnNpcrAY9RdN2hmDjfWAq11ricNy) · [Verified package](assets/task16f-final-production-release/candidate-source.json) · [Sanitized private logs](assets/task16f-final-production-release/authoritative-preview-logs.json) · [Read-only graph checks](assets/task16f-final-production-release/validation-graph-before.json) · [Production smoke](assets/task16f-final-production-release/production-strict-before.json)

## 4. Focused regression and frontend verification

| Check | Result |
| --- | --- |
| Django focused suite | **50 passed, zero skipped**, in-memory SQLite. Spline lifecycle, conditional writes, automatic synchronization, no-fallback behavior, matching alignment, Task 16E certification checks and Marketplace handoff. The initial fixture adapter passed RDFLib Rows to a helper that expects dictionaries. Converting them to binding dictionaries fixed the test harness. |
| Frontend suite | **98 passed**, zero skips via `node --experimental-test-isolation=none --test` over the six frontend test files. Registration and edited spline points serialize canonically. Other data and range guards were exercised. |
| Targeted lint and build | Changed JavaScript lint passed and isolated `next build` produced 20 static pages. Existing layout hook, stylesheet and Browserslist notices remain. |
| Signed-in Edge | The loopback :3003 app sent the actual canonical `spline_module.exact: 2`. All catalogue, exact detail and search reads used the same pinned candidate and existing role gate. The unrelated gear case preserved exact offering details, grades, material alternatives and PDF export. The PDF was 61,400 bytes and had its PDF header/end marker. Anonymous relay GET returned 401. |

The backend command used Django `call_command("test", ...)` with `tests.test_task16f_spline_correction`, `tests.test_provider_lifecycle_write_api`, `tests.test_m4_automatic_semantic_sync`, `tests.test_service_discovery_runtime_search`, `tests.test_service_discovery_matching_alignment`, `tests.test_task16e_certifications` and `tests.test_m6a_marketplace_handoff`. Set a disposable in-memory SQLite database, clear live endpoints, and optionally point `TASK16F_ISOLATED_EVIDENCE` at a writable evidence file. The test overrides the isolated sync settings and mocks graph I/O. [Targeted test](../../backend/tests/test_task16f_spline_correction.py) · [Signed-in browser checks](assets/task16f-final-production-release/signed-in-consumer.json) · [Shared spline screenshot](assets/task16f-final-production-release/shared-preview-spline.png)

## 5. Proposed Stage B plan and rollback

### Shared Demo spline correction

After approval, use the existing stable canonical `PATCH /api/offerings/mdc_stage1b_accept_20261126_a_shaft`. Fetch the exact provider and offer with `Accept-Encoding: identity`, confirm ownership, and back up the complete current `part_type_capabilities` map. Use its fresh strong offering ETag as `X-MDC-If-Match`. The approved delta changes only the `splined_shaft.spline_module` key from `value` to `exact`. If the fresh full map matches the Stage A read, the complete replacement body is:

```json
{
  "contract_version": "1.0",
  "part_type_capabilities": {
    "splined_shaft": {
      "spline_module": {
        "exact": 2,
        "confidence": "declared",
        "source_type": "provider_confirmed"
      }
    }
  }
}
```

If fresh shared detail already has the same canonical exact point, verify discovery and skip the write. If the record has other edits, reconcile them with the approved delta before acting. Expected outcome is HTTP 200 with `completed / synced / succeeded`, a changed strong offering and parent revision, the exact target map, and automatic graph visibility. Immediately test module 2 for both offers and modules 1 and 3 for Tasowheel only. If stable rejects the canonical conditional patch or the sync receipt is incomplete, stop new writes and resolve ordering or recovery before cutover. The verified Task 15 archived validator accepted both the legacy and canonical spline shapes in isolation.

### Precipart certification

SQS 42929 names Precipart SA's single Lyss site and covers precision and gearing work. The certificate shows EN 9100:2018 equivalent to AS9100 D and validity through 29 January 2029. The public gear capability page also describes Farmingdale. Publish only after the operator confirms the intended Swiss offering is fulfilled within the certified Lyss scope and explicitly approves this change. The ISO 13485 certificate covers distribution and remains an option only for this manufacturing offering. No current separate Lyss ISO 9001 certificate was established. [SQS 42929](https://www.precipart.com/wp-content/uploads/2026/03/102353_de_EN9100_42929_25.pdf) · [Precipart gear facilities](https://www.precipart.com/products-capabilities/gears-motion-control/precision-gears/) · [ISO 13485 certificate](https://www.precipart.com/wp-content/uploads/2024/08/102353_en_13485_24.pdf)

Publish the certification after the new stable runtime is proven. Back up the complete `generic_capabilities` map from the exact offering GET, verify it and the current site scope, and use its latest strong `X-MDC-If-Match`. Stage A confirmed that exact map is empty. For that current map, the proposed `PATCH /api/offerings/precipart_precision_gears` body is:

```json
{
  "contract_version": "1.0",
  "generic_capabilities": {
    "certifications": [
      {
        "code": "AS9100_D",
        "source_type": "public_web",
        "confidence": "publicly_confirmed",
        "source_note": "SQS 42929, Precipart SA, Werkstrasse 37, Lyss, Switzerland. EN 9100:2018 (AS9100 D equivalent), precision and gearing scope. Issued 2026-01-30, valid to 2029-01-29. https://www.precipart.com/wp-content/uploads/2026/03/102353_de_EN9100_42929_25.pdf"
      }
    ]
  }
}
```

On a new revision with unrelated fields, carry those fields into the full replacement. Verify the receipt, exact certification scope and graph revision. AS9100 plus module 1 should return Precipart and AS9100 plus module 4 should return zero. ISO 13485 and ISO 9001 + AS9100 should still return zero for the reviewed gear scope.

The original Task 15 archive accepted the exact spline body and its legacy rollback body. It did not list AS9100, rejected that offering payload and failed graph construction with `Unsupported certification identifier: AS9100_D` in an isolated replay. Once AS9100 is published, an older runtime cannot safely rebuild the catalogue while that code is stored. If necessary, restore the saved Precipart map using the current compatible runtime, fresh ETag and automatic sync, then verify the graph and move the alias under separate approval. Restoring the old Demo spline representation is a separate guarded PATCH only if ordered by the operator. An alias change alone leaves PostgreSQL and Fuseki data intact. [Task 15 compatibility replay](assets/task16f-final-production-release/task15-compatibility.json)

### Runtime cutover and handoff for approval

1. Recheck the stable alias, exact candidate code, current paired database and Fuseki revision, and readiness of the already approved secure production write binding. Execute the conditional Demo spline correction and the post-write acceptance checks first.
2. Use the Task 15 production-target staging procedure with automatic domain assignment disabled. Carry the public temporary No Auth contract 1.0 profile, strong ETags, validation and both synchronization flags into the staged production runtime. Verify exact deployed source, strict default and lenient opt-in, named certification options, deprecated paths and authorization boundary before switching the stable alias. An explicitly approved disposable lifecycle probe may verify sync and cleanup. [Task 15 release procedure](15_MDC_Vercel_Production_Release_and_Marketplace_API_Access_Report.md)
3. Apply Precipart's offering update only within separately confirmed scope after the cutover. Keep the guarded recovery order above available during the acceptance window.
4. Consolidate to main and update the permanent localhost frontend relay only under the approved scope. Use a single stable backend origin for reads and writes, keep Keycloak roles, disposable scope and ETag forwarding, and reserve Preview authorization for protected Preview origins. Verify signed-in Consumer, Provider and Admin. Update the release-specific Partner API guide, Postman collection and environment after the actual stable checks, with the strict and lenient contracts, certificate evidence scopes and temporary public authentication posture.

## 6. Git and review location

| Reference | Revision |
| --- | --- |
| Fetched main | `931a9c7d619edbfabee3ebfc5157af203fdb945e` |
| Reviewed Task 16E | `85cbe6626d5ba11d289555d0b65d6725cc3b0634` |
| Task 16F prompt and branch start | `74904b254fcd2379b7aa9cb1fa751dc19a1aa838` |
| Candidate source and spline writer | `ff025fd7b0b9d411cabd7a08f78362767562f6ee` |
| Isolated tests and local read relay | `b21a239fcba0457ae9cdb69213f1b1ddd69f0ece` |

The task branch is `phase4/task16f-final-production-release`. The report follows the implementation commits. The permanent checkout and its :3000 server, both stashes, unrelated edits and untracked logo, existing dependencies and ignored configuration were preserved. The :3001 and :3002 servers remained active. Task 16F runs as a separate loopback app at :3003. To restart, open `%TEMP%/mdc-task16f/mdc-catalog/demo-frontend`, use the approved local server-only Preview access environment, and run `npm run dev -- --hostname 127.0.0.1 --port 3003`.

Stage A ends at independent review. The next operator decision is approval of the Demo correction and production cutover, with a separate scope decision for Precipart and any hosted write probe.
