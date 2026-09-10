# MaaSAI MDC Demo Frontend - F5_B Keycloak Role Access Report

## 1. Purpose and scope

F5_B added lightweight frontend role access for the temporary MDC Demo Console using the existing Keycloak authentication state.

This is demo UI access control only. It does not implement backend authorization, production Marketplace authentication, user registration, or custom credential storage.

## 2. Existing Keycloak integration inspected

Inspected:

```text
subsystem/frontend/src/layout/context/AuthContext.js
subsystem/frontend/src/services/keycloak/keycloak.js
subsystem/frontend/src/pages/_app.js
subsystem/frontend/src/config/routes.js
subsystem/frontend/src/layout/AppMenu.js
subsystem/frontend/src/layout/AppTopbar.js
```

The existing auth flow already provides:

- Keycloak initialization.
- `authenticated`
- `isInitialized`
- `roles`
- `keycloak`
- `login()`
- `logout()`

F5_B reused those values and did not replace the auth architecture.

## 3. Role detection approach

Created:

```text
subsystem/frontend/src/components/mdc/demoAuth.js
```

Role detection reads from:

```text
AuthContext.roles
keycloak.tokenParsed.realm_access.roles
keycloak.tokenParsed.resource_access[clientId].roles
all keycloak.tokenParsed.resource_access.*.roles
```

Recognized role aliases:

```text
provider, mdc_provider, maas_provider -> provider
consumer, mdc_consumer, maas_consumer -> consumer
admin, mdc_admin, maas_admin -> admin
```

Admin wins when multiple roles exist.

## 4. Demo route access rules

Created:

```text
subsystem/frontend/src/components/mdc/DemoRoleGuard.js
```

Wrapped pages:

```text
/demo/provider        -> provider, admin
/demo/consumer-search -> consumer, admin
/demo/admin-audit     -> admin
```

Unauthenticated users see a login prompt using the existing `login()` function.

Authenticated users without a recognized MDC demo role see:

```text
You are logged in, but no MDC demo role was found.
Please use a Keycloak user with Provider, Consumer or Admin demo role.
```

Authenticated users with the wrong role see a role-specific access message.

The central route config remains public for demo routes so each page can render its own login/role message rather than being redirected away by `_app.js`.

## 5. Demo sidebar/menu behaviour

Updated:

```text
subsystem/frontend/src/layout/AppMenu.js
```

For authenticated MDC demo users, the sidebar is reduced to MDC demo entries only.

Provider sees:

```text
MDC Demo
- Dashboard
- Provider Demo
```

Consumer sees:

```text
MDC Demo
- Dashboard
- Consumer Search
```

Admin sees:

```text
MDC Demo
- Dashboard
- Provider Demo
- Consumer Search
- Admin / Audit
```

Unauthenticated users and users without detected demo roles retain the broader existing menu model, with protected page access still handled by existing route logic and page guards.

## 6. Login/logout behaviour

The existing topbar login/logout behavior was preserved.

- Not logged in: topbar `Login` calls existing Keycloak `login()`.
- Logged in: topbar profile dropdown exposes existing `logout()`.
- Demo page login prompts also call existing `login()`.

No custom auth storage or fake login page was added.

## 7. Provider/consumer demo flow supported

Provider flow:

```text
Login as provider -> /demo shows Provider landing -> Provider Demo accessible -> Consumer/Admin pages blocked
```

Consumer flow:

```text
Login as consumer -> /demo shows Consumer landing -> Consumer Search accessible -> Provider/Admin pages blocked
```

Admin flow:

```text
Login as admin -> /demo shows Admin landing -> all demo pages accessible
```

## 8. Files modified/created

Created:

```text
docs/07_mdc_demo_frontend_role_access_report.md
subsystem/frontend/src/components/mdc/demoAuth.js
subsystem/frontend/src/components/mdc/DemoRoleGuard.js
```

Modified:

```text
subsystem/frontend/src/pages/demo/index.js
subsystem/frontend/src/pages/demo/provider.js
subsystem/frontend/src/pages/demo/consumer-search.js
subsystem/frontend/src/pages/demo/admin-audit.js
subsystem/frontend/src/layout/AppMenu.js
```

## 9. Safety boundary confirmation

Confirmed:

- No backend code was modified.
- No packages were installed or changed.
- No `.env` file was added.
- No runtime config was modified.
- No MDC API service module was modified.
- No production auth implementation was added.
- No fake login page was created.
- No existing template pages or routes were deleted.

## 10. Commands run and results

Commands were run from:

```text
C:\Users\Elahi\Desktop\template-frontend\subsystem\frontend
```

### `npm run lint`

Result: succeeded with existing unrelated warnings.

Warnings:

```text
./src/layout/AppMenuitem.js
34:8  Warning: React Hook useEffect has missing dependencies: 'item.to', 'key', 'router.events', 'router.pathname', and 'setActiveMenu'.  react-hooks/exhaustive-deps

./src/layout/layout.js
74:8  Warning: React Hook useEffect has a missing dependency: 'bindMenuOutsideClickListener'.  react-hooks/exhaustive-deps
80:8  Warning: React Hook useEffect has a missing dependency: 'bindProfileMenuOutsideClickListener'.  react-hooks/exhaustive-deps
93:8  Warning: React Hook useEffect has missing dependencies: 'hideMenu', 'hideProfileMenu', and 'router.events'.  react-hooks/exhaustive-deps

./src/pages/_document.js
27:21  Warning: Do not include stylesheets manually.  @next/next/no-css-tags
```

### `npm run build`

First sandboxed run failed with the known worker-process restriction:

```text
Error: spawn EPERM
```

The command was rerun with approved escalation for `npm run build`.

Escalated result: succeeded.

Build output:

```text
Compiled successfully
Generated static pages: 22/22
```

## 11. Manual verification result

Manual Keycloak login testing was not performed in this Codex run because it requires interactive browser login sessions and test Keycloak users.

Expected manual checks:

```text
Unauthenticated /demo/provider -> login prompt
Provider user -> /demo/provider accessible, /demo/consumer-search blocked
Consumer user -> /demo/consumer-search accessible, /demo/provider blocked
Admin user -> all demo pages accessible
```

## 12. Remaining risks/questions

- Keycloak realm/client role names must match one of the configured aliases or the user will see the no-demo-role message.
- If the active Keycloak adapter does not expose `clientId`, resource roles are still collected from all resources as a fallback.
- In-browser role/menu behavior needs manual verification with real provider, consumer, and admin users.

## 13. Recommended next phase

Recommended next phase:

```text
F5_C - Provider add/register and update-existing-provider demo behaviour
```
