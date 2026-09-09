# Codex Prompt — P3.3 Final Remote Fuseki + Vercel Validation

## Role

You are executing the final remote-consumption gate for MaaSAI MDC Phase 3 milestone P3.3 on the user's Windows machine.

Work carefully, but move efficiently. Prefer inspection and verification over code changes. Do not change repository code unless an actual blocker is proven and cannot be resolved operationally. Do not commit or push anything; ChatGPT will review the result and finalize the Phase 3 report in GitHub.

## Repository / environment

Local repository root:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Project root:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

Python virtual environment is one directory above `mdc-catalog`:

```text
..\.venv\Scripts\python.exe
```

Vercel production alias:

```text
https://maasai-mdc-v1.vercel.app
```

Vercel project/scope historically used:

```text
project: maasai-mdc-v1
scope: mdc19
```

The user already has Docker Desktop running, the local Apache Jena Fuseki container is running, and a temporary Cloudflare Quick Tunnel is now running. Do not stop the tunnel until all final verification is complete.

## Confirmed P3.3 state — do not repeat destructive work

P3.3 local gates have already passed:

```text
P3.3 Fuseki preflight PASS
```

Real synchronization already completed successfully:

```text
Catalogue synchronization: selected=5; succeeded=5; failed=0; noop=0; events=6.
Catalogue synchronization completed successfully.
```

PostgreSQL evidence already verified:

```text
CatalogueSyncEvent: 6 succeeded, attempt_count=1, errors=0
ProviderPublication for p32_pilot_provider: 5 synced/completed
```

Direct Fuseki verification already passed:

```text
PASS Fuseki graph contains triples: 702
PASS Fuseki contains provider: p32_pilot_provider
PASS Fuseki contains offering: p32_pilot_provider_precision_metal_parts
P3.3 direct Fuseki verification PASS
```

Do NOT rerun the synchronization command unless explicitly instructed later. Do NOT use `--rebuild`.

## Architecture / safety rules

These rules are mandatory:

1. PostgreSQL `neondb` remains the operational source of truth.
2. Fuseki remains the semantic/search layer.
3. The local Graph Store endpoint remains local and protected; do not configure it in Vercel.
4. Do not configure Fuseki write username/password in Vercel.
5. Vercel production must keep:

```text
MDC_CATALOG_SYNC_ENABLED=False
```

6. The only Fuseki setting that Vercel needs for this final gate is the remotely reachable SPARQL query endpoint:

```text
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT=https://<quick-tunnel-host>/mdc/sparql
```

7. Do not print or echo secrets from `.env`, `DATABASE_URL`, Django secret, lifecycle service token, or Fuseki credentials.
8. Do not paste `.env` contents into the terminal transcript/report.
9. Do not delete databases, branches, Vercel projects, or other infrastructure.
10. Do not remove/replace unrelated Vercel environment variables.
11. No `/api/v1` route is canonical. Public discovery remains:

```text
POST /api/service-discovery/search
contract_version = 1.0
```

## Goal

Complete the final P3.3 proof:

```text
PostgreSQL
  -> synchronized RDF
  -> local Fuseki
  -> Cloudflare temporary public SPARQL endpoint
  -> Vercel production MDC
  -> POST /api/service-discovery/search
  -> returns p32_pilot_provider
```

Because `p32_pilot_provider` was created through PostgreSQL lifecycle operations in P3.2 and was not part of the original curated YAML baseline, returning it from deployed canonical discovery is the key proof that Vercel is consuming the synchronized Fuseki graph.

## Step 1 — locate the running Quick Tunnel URL

From PowerShell, inspect the currently running Cloudflare tunnel without exposing secrets.

If it is a Docker container, locate it first, for example:

```powershell
docker ps --filter "ancestor=cloudflare/cloudflared:latest" --format "{{.ID}} {{.Names}}"
```

Then inspect only enough logs to find the generated URL:

```powershell
docker logs <container-name-or-id> 2>&1 | Select-String "trycloudflare.com"
```

If Cloudflare was launched another way, inspect the already-running process/window or use an equivalent safe method.

Extract only the public base URL:

```text
https://<random>.trycloudflare.com
```

Do not restart the tunnel if it is healthy.

Construct:

```text
REMOTE_QUERY_ENDPOINT=https://<random>.trycloudflare.com/mdc/sparql
```

## Step 2 — prove the public SPARQL endpoint works before touching Vercel

From `mdc-catalog`, set only a process-local override for the query endpoint:

```powershell
$env:SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT = "https://<random>.trycloudflare.com/mdc/sparql"
```

Do not alter `.env` for this temporary remote endpoint unless absolutely necessary.

Run:

```powershell
& '..\.venv\Scripts\python.exe' scripts\p33_fuseki_preflight.py --require-remote
```

Expected important lines:

```text
PASS Fuseki query endpoint configured: https://<...>.trycloudflare.com/mdc/sparql
PASS Fuseki SPARQL ASK reachable (...)
PASS Fuseki graph-store authenticated HEAD: 200
PASS no graph write attempted
P3.3 Fuseki preflight PASS
```

A warning that query and Graph Store endpoints use different hosts is acceptable here because that is deliberate: query is tunneled, write stays local.

Then run a remote direct verification:

```powershell
& '..\.venv\Scripts\python.exe' scripts\p33_fuseki_verify.py --direct-only
```

Required:

```text
PASS Fuseki graph contains triples: 702
PASS Fuseki contains provider: p32_pilot_provider
PASS Fuseki contains offering: p32_pilot_provider_precision_metal_parts
P3.3 direct Fuseki verification PASS
```

If this fails, STOP. Do not modify Vercel. Diagnose only the tunnel/public query path and report the exact non-secret error.

## Step 3 — inspect Vercel environment safely

Confirm the local project is linked to the intended Vercel project/scope. Use current CLI help/inspection if needed rather than guessing command syntax:

```powershell
npx vercel@latest --help
npx vercel@latest env --help
```

Inspect Production environment variable names/status without printing secret values.

Confirm in particular:

```text
MDC_CATALOG_SYNC_ENABLED=False
```

Do not add the Graph Store endpoint or Fuseki write credentials to Vercel.

Check whether `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` already exists in Production.

- If absent, add it for Production with the current Quick Tunnel SPARQL URL.
- If present, update/replace only that exact variable using the currently supported Vercel CLI mechanism.
- If the installed/current CLI requires a destructive remove operation before replacement and there is no safe `--force`/update mechanism, STOP and report that fact before deleting anything.

When entering the value, use only:

```text
https://<random>.trycloudflare.com/mdc/sparql
```

Never include Fuseki credentials in the URL.

## Step 4 — redeploy Production

Once the Production query endpoint is configured, redeploy the existing project from the correct linked project root. Historically the working command has been:

```powershell
npx vercel@latest deploy --prod --yes --scope mdc19
```

If current CLI/project linkage requires a slightly different invocation, inspect and use the supported equivalent. Do not create a new Vercel project.

Record the production deployment URL/alias, but do not expose any secrets.

Keep the Cloudflare tunnel running throughout deployment and verification.

## Step 5 — smoke the deployed canonical API

Check:

```text
GET https://maasai-mdc-v1.vercel.app/api/health -> 200
```

Canonical discovery must remain:

```text
POST https://maasai-mdc-v1.vercel.app/api/service-discovery/search
```

No URL-versioned `/api/v1/service-discovery/search` should be introduced.

## Step 6 — run the final P3.3 verification

Ensure the process-local `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` still points to the Quick Tunnel SPARQL URL, then run:

```powershell
& '..\.venv\Scripts\python.exe' scripts\p33_fuseki_verify.py
```

Required final evidence:

```text
PASS Fuseki graph contains triples: 702
PASS Fuseki contains provider: p32_pilot_provider
PASS Fuseki contains offering: p32_pilot_provider_precision_metal_parts
PASS deployed canonical search returned synchronized provider: p32_pilot_provider
P3.3 Fuseki/deployed discovery verification PASS
```

The deployed canonical response must have:

```text
contract_version = 1.0
```

and include:

```text
provider_id = p32_pilot_provider
```

If deployed discovery does not return the provider, inspect application behavior/logging and configuration, but do not rerun synchronization and do not weaken the public API contract.

## Step 7 — final safety verification

Before reporting success, verify:

- Cloudflare tunnel was used only as a temporary remote query path.
- Vercel Production query endpoint points to the temporary Quick Tunnel URL.
- `MDC_CATALOG_SYNC_ENABLED=False` remains true in Vercel Production.
- no Graph Store endpoint was added to Vercel.
- no Fuseki username/password was added to Vercel.
- no secrets were committed or printed.
- no database/provider/publication data was modified during this remote-consumption gate.

Do not stop the Cloudflare tunnel yet; keep it alive until ChatGPT has reviewed the final result. After P3.3 is accepted, the temporary tunnel can be stopped and the temporary Vercel query endpoint can be handled as directed.

## Final response format

Return one concise execution report with these headings:

```text
P3.3 FINAL REMOTE GATE REPORT

1. Quick Tunnel
- status:
- public SPARQL endpoint reachable: PASS/FAIL

2. Remote preflight/direct Fuseki
- preflight --require-remote: PASS/FAIL
- triple count:
- p32 provider present: PASS/FAIL
- p32 offering present: PASS/FAIL

3. Vercel Production
- intended project/scope confirmed: PASS/FAIL
- query endpoint configured: PASS/FAIL
- MDC_CATALOG_SYNC_ENABLED still False: PASS/FAIL
- graph-store/write credentials NOT configured: PASS/FAIL
- production deployment: PASS/FAIL

4. Deployed canonical discovery
- /api/health: status
- contract_version: value
- p32_pilot_provider returned: PASS/FAIL
- final p33_fuseki_verify.py: PASS/FAIL

5. Changes made
- environment/config changes only
- code changes: NONE, or list exact files if a blocker genuinely required a change
- Git commits/pushes: NONE

6. Final gate
P3.3 FINAL REMOTE GATE: PASS/FAIL
```

If any required gate fails, do not claim P3.3 complete. Include the exact non-secret failure and the smallest recommended next action.