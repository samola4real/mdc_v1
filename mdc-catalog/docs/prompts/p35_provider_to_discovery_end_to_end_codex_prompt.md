# Codex Prompt — P3.5 Provider to Discovery End-to-End Validation

Execute P3.5 from the current `main` branch. Do not modify tracked code unless explicitly instructed after a failed gate. Do not print secrets.

## Goal

Prove that the provider created through the deployed P3.4 lifecycle API moves through PostgreSQL -> outbox -> RDF/Fuseki -> deployed canonical discovery.

Controlled provider:

```text
p34_api_validation_provider
```

## Rules

- keep Vercel Production `MDC_CATALOG_SYNC_ENABLED=False`;
- do not configure Fuseki Graph Store credentials in Vercel;
- do not create a public sync endpoint;
- do not delete or reset pilot data;
- do not print `DATABASE_URL`, lifecycle token, Fuseki password, or other secrets;
- no Git commits/pushes;
- if a required tunnel/query endpoint is unavailable, stop and report the blocker instead of changing unrelated code.

## Steps

1. Pull and confirm clean/synchronized worktree.
2. Syntax-check `scripts/p35_provider_to_discovery_verify.py`.
3. Confirm the remote Fuseki query path used by Vercel is live. Reuse the current Cloudflare Quick Tunnel if still running. If its hostname changed, update only `SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT` in Vercel Production and redeploy; keep `MDC_CATALOG_SYNC_ENABLED=False`.
4. Run:

```powershell
& '..\.venv\Scripts\python.exe' scripts\p33_fuseki_preflight.py --require-remote
```

5. Before synchronization, run:

```powershell
& '..\.venv\Scripts\python.exe' scripts\p35_provider_to_discovery_verify.py --expect-absent
```

This must prove `p34_api_validation_provider` is absent from Fuseki and deployed discovery before synchronization. If it is already present, stop and report that the pre-sync evidence cannot be established.

6. Process the existing pending outbox from the trusted local environment only:

```powershell
$env:MDC_CATALOG_SYNC_ENABLED = "True"
& '..\.venv\Scripts\python.exe' backend\manage.py sync_service_discovery_catalogue
Remove-Item Env:MDC_CATALOG_SYNC_ENABLED -ErrorAction SilentlyContinue
```

Do not run `--rebuild`. Do not create new provider lifecycle writes.

7. Run the post-sync verification:

```powershell
& '..\.venv\Scripts\python.exe' scripts\p35_provider_to_discovery_verify.py
```

Expected final marker:

```text
P3.5 PROVIDER TO DISCOVERY END-TO-END VALIDATION: PASS
```

8. Confirm Git worktree remains clean. Do not commit or push.

## Return this report

```text
# P3.5 PROVIDER TO DISCOVERY END-TO-END VALIDATION REPORT

## 1. Local/remote preflight
- git status: PASS/FAIL
- script syntax: PASS/FAIL
- remote Fuseki preflight: PASS/FAIL
- Vercel sync flag remained False: PASS/FAIL

## 2. Pre-synchronization evidence
- p34 provider absent from Fuseki: PASS/FAIL
- p34 offering absent from Fuseki: PASS/FAIL
- p34 provider absent from deployed canonical search: PASS/FAIL

## 3. Synchronization
- management command result: <summary>
- semantic sync executed from trusted local environment: YES/NO
- Vercel-side sync executed: NO

## 4. Post-synchronization evidence
- Fuseki triple count: <count>
- p34 provider present in Fuseki: PASS/FAIL
- p34 offering present in Fuseki: PASS/FAIL
- deployed canonical search returned p34 provider: PASS/FAIL
- contract_version 1.0: PASS/FAIL

## 5. Changes
- tracked code changes: NONE/<details>
- Git commits/pushes: NONE

## 6. Final gate
P3.5 PROVIDER TO DISCOVERY END-TO-END VALIDATION: PASS/FAIL
```
