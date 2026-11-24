# MDC Demo Frontend

This existing Next.js Pages Router application uses the MaaSAI Keycloak login and
Provider, Consumer and Admin pages to exercise the accepted Stage 1 MDC Preview.

## Local Stage 1B setup

The Docker runtime is Node.js 20.18.0. Use a compatible Node runtime and npm that
supports the existing lockfile. Start the server on loopback.

```bash
npm ci
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Open `http://localhost:3000/demo` with the approved test account. The existing
Keycloak client must permit that localhost redirect and web origin. Next.js
loads the approved Preview credential from the server environment or the
Git-ignored `.env.local`.

```dotenv
MDC_VERCEL_PROTECTION_BYPASS=<approved-Stage-1-Preview-bypass>
```

The loopback session policy verifies the signed MAASAI Keycloak access token,
expiry, subject, token type and `myClient` authorized party. It confirms the same
subject through Keycloak UserInfo and recognizes signed demo roles from the realm
and `myClient` claims. Keep the Preview credential in the server environment.

An explicitly configured `MDC_KEYCLOAK_AUDIENCE` enables strict audience
validation and requires `MDC_KEYCLOAK_ROLE_SOURCE` set to `client` or `realm`
for the approved role claim. A role source alone restricts the loopback session
policy to that claim. The relay is available on loopback only.

The browser sends its Keycloak access token to `/api/mdc` on the same origin.
The server checks the verified role and forwards only the canonical routes to
the pinned protected Preview. Writes use disposable provider IDs starting with
`mdc_stage1b_` and offering IDs prefixed by their provider ID. The client uses
canonical `If-Match` with the current resource ETag. The server uses the
Stage 1 Vercel header alias upstream. Registration and editing leave semantic
publication pending while catalogue sync is disabled.

## Verification

```bash
node --experimental-default-type=module tests/stage1b.test.mjs
npm run lint
npm run build
```

Use unique disposable IDs, confirm each persisted change, and delete the test
records with fresh ETags. The Consumer page uses current catalogue filters and
canonical results. Admin health checks API liveness.

## Repository and release boundary

GitHub is the controlled development source after the sanitized snapshot import.
GitLab remains the historical and official release repository.

- [Sanitized snapshot provenance](../docs/Demo_Frontend/00_frontend_sanitized_snapshot_import_provenance.md)
- [GitHub-to-GitLab release mapping](../docs/Demo_Frontend/01_frontend_github_to_gitlab_release_mapping.md)
- [Comprehensive MDC implementation report and user manual](../docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md)
