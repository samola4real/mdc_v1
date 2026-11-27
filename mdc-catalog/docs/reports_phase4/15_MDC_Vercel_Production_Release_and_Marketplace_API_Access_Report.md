# Task 15 — Vercel production release and Marketplace API access

**READY · 2026-11-27.** The stable URL `https://maasai-mdc-v1.vercel.app` serves the accepted strict MDC backend for temporary Marketplace integration. It passed a clean-client smoke without bearer, actor, bypass or session headers. Automatic registration and cascade deletion succeeded, and cleanup restored the approved business-data baseline. [Task 15 prompt](../prompts_phase4/15_MDC_Vercel_Production_Release_and_Marketplace_API_Access_Prompt.md)

## Release and data gates

| Check | Actual evidence |
| --- | --- |
| Source and package | Fetched `origin/main` at `4cd41d8b76db399e8b4ee0283ef00154aa7047e1`. Archived tested backend commit `c6980293c5de9fd1e9d7449d664be8fa847d3a2e`. The archive was byte-identical to the accepted Task 14A package, SHA-256 `354f6af20dcbdd89a26a2e582e9e75343f6154aac26ddd58e76d3bd78572f210`. The upload contained the backend, data, ontology and existing dependency files. |
| Previous production | `dpl_GmWLQStvb3qo551uYYUv4zLiW1XK`, source `b9275258bf4a2455814ad9b2af9621e0a5d01327`. Anonymous stable health returned canonical HTTP 200. Exact provider read and publication validation both returned canonical HTTP 401 `trusted_lifecycle_auth_required`. The rejection came from MDC. The developer's earlier test URL is unknown. |
| Former production catalogue | Read-only `neondb` inventory and exact legacy operator GETs agreed on 5 providers and 8 offerings. Two providers, three offerings and four certification records for Precipart and Tasowheel matched the validation business fields. The five other offerings belonged to the documented `demo_machining_provider`, `p32_pilot_provider` and `p34_api_validation_provider` test fixtures. They stay in `neondb` and are outside the temporary validation API view. The former database and its schema were preserved. |
| New database and graph | Neon `maasai-mdc-validation`, project `mute-cell-38148661`, branch `br-wild-haze-aej09lb1`, compute `ep-damp-water-aeg29kmn`, database `mdc_validation`. The read-only check found 22 migrations through `providers.0004_cataloguesynclease`. The accepted 3-provider, 5-offering catalogue matched the 837-triple isolated Fuseki default graph on `mdc-fuseki-validation`, loopback port 3031. The approved dataset contains the retained demo provider and the two public industrial baselines. |
| Recovery point | Read-only full-row backup of 3 providers, 5 offerings and 6 certifications taken at 2026-11-27 10:23:57 EET. The Windows user DPAPI-encrypted backup was decrypted in memory to verify it and retained outside Git as `validation-business-pre-cutover.dpapi`. Ciphertext SHA-256 `379946ed0f591eedf221e6ddf9fc04b8f87594f1ea080a1ab1e10e0a1f2b2239`. Neon reported a six-hour point-in-time recovery window. |
| Runtime and deployment | Vercel `mdc19/maasai-mdc-v1`, project `prj_DekMQdOYuuH0A5yNsCkFmOC4uD9j`. CLI 48.9.2 staged Production with domain assignment skipped. `dpl_AdG2ZD9Lhic25LQ4E6rf7YJLgsPF` reached Ready in `iad1`. Build logs confirmed Python 3.12. The generated URL is `https://maasai-mdc-v1-gbl21zn2x-mdc19.vercel.app`. Both production aliases still resolved to the previous deployment during staging. |

The old protected lifecycle credential was used only for the nonmutating historical database-binding comparison. All staged application calls omitted MDC bearer and actor headers. Stage 1B and both accepted Stage 2 Previews remained protected. The original Task 13 tunnel origin and paired Graph Store were already current, so the release reused the existing route filter, container and tunnel. [Task 14A closure](14A_MDC_Strict_Technical_Eligibility_Correction_Report.md) · [Task 13 runtime gate](13_MDC_Stage2_Automatic_Semantic_Synchronization_Report.md) · [Documented P3.2 pilot](../Phase_3/02_mdc_v1_p32_trusted_lifecycle_pilot_enablement.md) · [Documented P3.4 fixture](../Phase_3/04_mdc_v1_p34_provider_lifecycle_api_validation.md)

### Effective profile

| Runtime setting | Released setting |
| --- | --- |
| Django | `config.settings_production`, `DEBUG=False`, Vercel hosts allowed, existing server secret |
| Provider publication and validation | `MDC_PROVIDER_PUBLICATION_ENABLED=True`, `MDC_PROVIDER_VALIDATION_ENABLED=True` |
| Lifecycle identity | `MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED=False`, `MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED=False`. Lifecycle service token unused. |
| Concurrency and demo routes | `MDC_PROVIDER_CONCURRENCY_REQUIRED=True`, `MDC_DEMO_API_ENABLED=False`. Staged demo health returned 404. |
| Semantic synchronization | `MDC_CATALOG_SYNC_ENABLED=True` and `MDC_CATALOG_AUTO_SYNC_ENABLED=True`. The current validation HTTPS origin supplies `/mdc_validation/sparql` and `/mdc_validation/data?default`. The existing validation-only Graph Store credentials and 10 s client timeouts stayed internal. |
| Vercel protection | Generated deployment and Preview URLs remained protected. Existing project protection allowed anonymous traffic on the stable aliases. Release overrides were deployment-scoped, preserving the shared project variables. |

## Staged acceptance

The protected staged client supplied only Vercel staging access. It ran 42 requests, with 33 successful responses and nine expected rejections or absence checks. One fictional provider, `mdc_stage1b_task15_20261127_d2a4317f`, owned the `_gear` and `_shaft` offerings. Protected preflight also found the exact prior acceptance offering list. Strict baseline results included Tasowheel only for Spur gear Module 4, both baseline gears for Module 1, the accepted Roller for Steel and Aluminum with Turning, both Plain shaft offers at outer diameter 80 mm and length max 500 mm, and HTTP 200 with no Crown gear offerings.

| Canonical operation | Observed result |
| --- | --- |
| `GET /api/health` | 200, canonical liveness |
| `GET /api/catalog/filters` | 200, controlled vocabularies |
| `POST /api/service-discovery/search` | 200, strict eligibility. With the disposable gear at range 1–5, Module 4 included it. At range 1–3, Module 4 excluded it and Module 3 still included it, with no score cutoff. |
| `POST /api/provider-publication/validation` | 200, `valid=true` |
| `POST /api/provider-publication` | 201, disposable provider and gear, strong provider ETag |
| `GET /api/providers/{provider_id}` | 200, exact identity, strong ETag |
| `PATCH /api/providers/{provider_id}` | 200, changed only the disposable name, new strong ETag and updated RDF display name |
| `GET /api/providers/{provider_id}/offerings` | 200, exact listing before and after addition and removal |
| `POST /api/providers/{provider_id}/offerings` | 201, exact Plain shaft sibling, immediately discoverable |
| `GET /api/offerings/{offering_id}` | 200 with strong ETag, then 404 after deletion |
| `PATCH /api/offerings/{offering_id}` | 200, Gear Module maximum 5→3 and preserved remaining family evidence |
| `DELETE /api/offerings/{offering_id}` | 200, shaft disappeared from detail and discovery, gear remained |
| `DELETE /api/providers/{provider_id}` | 200, provider and remaining gear disappeared from API, PostgreSQL, RDF and search |

The missing precondition returned 428 `concurrency_precondition_required`. A real earlier ETag returned 412 `provider_precondition_failed`. Exact detail reads confirmed the rejected requests preserved the name and ETag. Every conditional write used a current strong `X-MDC-If-Match` value obtained by an identity-encoded detail read. Stage cleanup restored the original row fingerprints and 837 validation triples before cutover.

## Cutover and clean-client proof

Vercel promoted the tested staged Production deployment without rebuilding it. Both `maasai-mdc-v1.vercel.app` and `maasai-mdc-v1-mdc19.vercel.app` were independently resolved to `dpl_AdG2ZD9Lhic25LQ4E6rf7YJLgsPF`. The old deployment remained Ready and available for rollback. Anonymous requests to the generated release hostname and the three protected Preview hostnames still returned a Vercel 302. [Released deployment](https://vercel.com/mdc19/maasai-mdc-v1/dpl_AdG2ZD9Lhic25LQ4E6rf7YJLgsPF) · [Vercel deployment protection](https://vercel.com/docs/deployment-protection) · [Vercel promotion](https://vercel.com/docs/cli/promote)

A clean client made 21 requests to the stable URL with no Authorization, actor, bypass or cookie header. Health, filters, exact provider/offerings reads, publication validation and discovery returned canonical HTTP 200. Module 4 returned only Tasowheel before the short smoke, both baseline gears qualified at Module 1, and Crown gear returned zero. The separate `mdc_stage1b_task15_20261127_651ef802` provider and gear were registered with HTTP 201, visible on the next Module 4 search, and removed by a fresh strong-ETag cascade with HTTP 200. Exact details returned 404, and the next Module 4 search again returned only Tasowheel.

Staged request times ranged from 160 to 1,818 ms. Stable smoke times ranged from 163 to 1,613 ms. The new production deployment's 25-minute Vercel log check returned no error or fatal groups. All three focused Marketplace handoff asset tests passed.

### Automatic publication receipts

Each intended write returned `completed / synced / succeeded`. Read-only database and SPARQL checks verified every receipt and the current database/Fuseki revision. All 12 scoped events succeeded on their first attempt. Automatic mode supplied the RDF changes.

| Phase and action | Receipt | Visible validated revision |
| --- | --- | --- |
| Stage register | `ccda2549-21c4-4657-a7fa-91feb483b180` | `ea0e3425901c9231be592bd0e47775eabe254ef4af4b6fe6e3f7ae5f5964e604` |
| Stage provider PATCH | `46477915-1373-4971-9332-239fc1921d9a` | `bf6017438ed9a959e08c30d81b06f14eb7b05065df92fa23618b4d18df066b53` |
| Stage offering PATCH | `e719904e-9ce3-4835-bd93-50524ab5f6ff` | `6e1be9976c202238cc114468bdab89ed5582d837deac87ba4f3429b67ed20cb7` |
| Stage add shaft | `c5431719-960a-4617-b291-9bb5114bb094` | `0084940bc190114c0cf60b50d36a39934ff8f8f4f236c5094521bdb8a99e5f8d` |
| Stage delete shaft | `691d25f9-76f3-40c0-96de-7fa88c8cec4e` | `1e3dbe62a1316629fc95599c85324aa4d4457c81c45900e1a5d46334ca6428e9` |
| Stage provider cascade | `6ddf44f4-d0e1-45f0-9683-55b61dfd00f0` | `2ef645395981196846f5620177b40547314a1d8c5924437d84be4239459f1065` |
| Stable register | `d0312904-b260-470f-b287-dd7cfda7d135` | `495eadab9a85f892ce3dc265ed3fdbb747e58a073f172918d5b11fc13d1b2f30` |
| Stable provider cascade | `c9787f83-17bf-4f6b-bdca-4f5a1f0a92ab` | `7c79b16dba232163baa27d0c6553c298572f9475aa4c508ad6d4ded80e4348d4` |

Final cleanup left 3 providers, 5 offerings, 837 validation triples, 68 synced publications and 94 succeeded events. The accepted provider and offering row fingerprints matched the pre-release check. There were zero pending, failed or processing events, zero owned leases and zero disposable RDF identities. The original industrial `mdc` dataset retained 731 triples and sorted-binding SHA-256 `513a1f00d138dec9edaa7de0d740397fdce0d8f1c1b939d2752007601c65e2d5`. The industrial datasets, previous deployments, frontend and unrelated local work were preserved.

## Marketplace handoff

The MDC demo API is ready at `https://maasai-mdc-v1.vercel.app`. Use **No Auth**, contract `1.0` and the unversioned `/api/` routes. The Marketplace server can call it without a bearer token, actor header, Vercel bypass or session cookie. Keycloak authenticates users inside Marketplace. Use approved demo records because direct MDC calls are public. [API guide](../Partner_API/MaaSAI_MDC_API_Documentation.md) · [13-operation matrix and payloads](../Partner_API/MaaSAI_MDC_M6_Marketplace_Integration_Guide.md#frozen-endpoint-matrix) · [Postman collection](../Partner_API/MaaSAI_MDC_M6_Marketplace_Integration.postman_collection.json) · [Stable No Auth environment](../Partner_API/MaaSAI_MDC_Marketplace_Demo.postman_environment.json)

```bash
curl https://maasai-mdc-v1.vercel.app/api/health
curl https://maasai-mdc-v1.vercel.app/api/catalog/filters
curl -X POST https://maasai-mdc-v1.vercel.app/api/service-discovery/search \
  -H 'Content-Type: application/json' \
  --data '{"contract_version":"1.0","request_id":"marketplace-smoke-001","consumer_id":"marketplace-demo","service_category":"precision_gears","part_family":"gear","part_type":"spur_gear","requirements":{"part_family_specifications":{"module":{"exact":4}}}}'
```

The Module 4 smoke returns the eligible Tasowheel gear. MDC requires confirmed evidence for every criterion, and the MaaS Recommendation System ranks the eligible list. The separate `material_grades` filter remains unsupported. For PATCH and DELETE, GET the exact detail with `Accept-Encoding: identity` and send its strong `ETag` as `If-Match` or `X-MDC-If-Match`. A 503 or timed-out write can have committed. Keep the `publication_id`, read back the exact identity and coordinate recovery before retrying.

## Operations and rollback

The MDC operator keeps Docker Desktop, `mdc-fuseki-validation`, the existing validation route filter and Cloudflare tunnel online. Start a stopped validation container with `docker start mdc-fuseki-validation`. If the filter or tunnel stops, use the existing startup commands below from separate PowerShell terminals. Marketplace calls the stable API directly and needs no local frontend or Django server.

```powershell
node.exe (Join-Path $env:LOCALAPPDATA 'MaaSAI\mdc-stage2-fuseki\validation-routes.cjs')
cloudflared.exe tunnel --no-autoupdate --protocol http2 --metrics 127.0.0.1:0 --url http://127.0.0.1:3032
```

Keep writes on the corrected stable runtime because the retained Previews share `mdc_validation`. A changed Quick Tunnel hostname requires verifying the new paired HTTPS endpoints and staging a coordinated production-scoped release before restoring write traffic. For a committed publication needing recovery, the operator can run `python manage.py sync_service_discovery_catalogue --publication-id <uuid>` privately with the verified validation pairing and retry the corresponding read. [Validation startup and endpoint configuration](12_MDC_Stage2_Fuseki_Integration_Readiness_Report.md#restart-and-rollback)

The exact rollback target is `dpl_GmWLQStvb3qo551uYYUv4zLiW1XK`. Stop new writes and use `vercel rollback dpl_GmWLQStvb3qo551uYYUv4zLiW1XK --scope mdc19` from the linked project, then resolve both aliases again. This restores the former authentication and database profile. Validation database commits and receipts stay available for recovery. [Vercel rollback](https://vercel.com/docs/cli/rollback)
