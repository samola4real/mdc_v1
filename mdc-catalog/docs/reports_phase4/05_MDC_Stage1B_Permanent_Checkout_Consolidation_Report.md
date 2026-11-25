# Task 05 — Stage 1B permanent checkout consolidation

**PASS · 2026-11-25.** The operator accepted Task 05 after checking the Stage 1B frontend on `http://localhost:3000/`. The permanent development checkout is `C:/Users/Elahi/Desktop/mdc_v1`.

## Integration and local changes

- Fetched `origin/main` at `2fc1beb911591f9e4954f8ab1945b58fb5dfb590` and verified the reviewed Stage 1B tip `4c2d2b344f717d8cb8ed9ff7bf90c656ea703986`. The merge tree matched the reviewed frontend and retained main's newer prompts. The permanent `main` fast-forwarded from `004fef8f0db73ef3e12c1035ec470c131dcb99a6` to merge commit `7c5ecb59c3e68c827d40dfb0982659d8036c36ed`. [PR #9](https://github.com/samola4real/mdc_v1/pull/9)
- Verified all four original local edits in stash `9f0e35c84925c118052f0fed4d87896b1febad3d` (`Task 05 pre-consolidation local changes`). Reapplied the root `.gitignore` and `src/pages/demo/index.js` edits as unstaged changes. The local Next.js upgrade in `package.json` and `package-lock.json` remains in the stash so the permanent frontend uses the reviewed dependencies.
- Copied the working `.env.local` byte for byte into the permanent frontend. Git ignores the file, and an explicit Windows ACL restricts access to the local user, System, and Administrators. Next.js loaded the server-side bypass automatically with the existing MaaSAI loopback session policy. A local scan found zero matches for the bypass value across 20 public files and two loopback responses.

## Permanent checkout verification

| Check | Evidence |
| --- | --- |
| Locked install | On Node `22.15.0` and npm `10.9.2`, installed Next.js `14.0.3` matched the reviewed lockfile. A clean `npm ci` retry with a fresh cache resolved three empty package directories from the first install. |
| Regression, lint, and build | 10 of 10 Stage 1B tests passed. Lint and production build passed with existing React hook, stylesheet, and Browserslist warnings. The build included `/demo/provider` and `/api/mdc/[...path]`. |
| Local process and browser | PID `32440` on `127.0.0.1:3000` resolved to the permanent Next.js installation. Edge rendered the updated MaaSAI Home and Home, Contact, and Help sidebar. The Provider route compiled and redirected the anonymous session to Home. The MaaSAI login form opened for `myClient` with S256 PKCE and a `localhost:3000` return origin. |
| Anonymous relay | Browser requests to `/api/mdc/health` and `/api/mdc/catalog/filters` each returned HTTP `401` with `keycloak_token_required` and `Cache-Control: no-store`. Neither response exposed the Preview bypass header. |
| Protected Preview health | After the operator approved HTTPS use of the saved bypass at the fixed Preview host, `GET /api/health` returned HTTP `200` with JSON contract `1.0`, status `ok`, and service `maasai-mdc`. The request used the ignored configuration in the permanent frontend. |
| Provider Area functional acceptance | The operator confirmed that the permanent frontend loaded correctly, all three part families were available, and the service category and capability fields updated dynamically. |

Verification used read-only requests. Provider registration and the remaining validation, discovery, and Consumer-only authorization checks are reserved for functional testing. The previously disclosed bypass remains flagged for rotation by the Vercel project owner. [Task 04 report](04_MDC_Stage1B_Frontend_Backend_Connectivity_Report.md)

## Worktree retirement

After operator acceptance, `git worktree remove` retired `C:/Users/Elahi/AppData/Local/Temp/mdc-stage1b-20261124-4b9fc439`. Before removal, the stopped checkout was clean and held only generated dependencies and build output plus a byte-identical copy of the permanent `.env.local`. The retained branch `phase4/stage1b-frontend-integration` at `4c2d2b344f717d8cb8ed9ff7bf90c656ea703986` provides the rollback reference. The working configuration is in the permanent frontend.

## Startup

```powershell
Set-Location -LiteralPath 'C:/Users/Elahi/Desktop/mdc_v1/mdc-catalog/demo-frontend'
npm run dev -- --hostname 127.0.0.1 --port 3000
```

[MaaSAI frontend](http://localhost:3000/)
