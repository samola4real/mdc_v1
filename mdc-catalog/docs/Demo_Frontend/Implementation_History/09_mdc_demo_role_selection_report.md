# F5_B1 - Demo Role Selection After Keycloak Login

## 1. Purpose and scope

F5_B1 adds a demo-only role selection step after Keycloak authentication. The goal is to let an authenticated demo user choose whether the current browser session should behave as Provider, Consumer or Admin.

This task only changes frontend demo role-selection behavior. It does not change provider forms, consumer search, admin/audit actions, backend code, API services, packages, environment files or runtime config.

## 2. Role selection behaviour

When an authenticated user opens `/demo` and no demo role has been selected in the browser session, the MDC Demo Console shows:

- Provider: manage provider profile, offerings and capabilities.
- Consumer: search for suitable providers.
- Admin: view all demo areas.

For a Keycloak admin demo user, all three choices are available. For a non-admin demo user, the chooser is constrained to roles present in the user's Keycloak token.

The `/demo` dashboard also shows the current selected demo role plus:

- `Switch role`
- `Logout`

`Switch role` clears the selected demo role and returns the dashboard to the role-selection screen. `Logout` clears the selected demo role and then calls the existing Keycloak logout function.

## 3. Session/local storage key used

Selected demo role is stored in `sessionStorage`:

```text
mdc_demo_selected_role
```

Supported values:

```text
provider
consumer
admin
```

A small browser event is dispatched after role changes so the sidebar and guards refresh without requiring a page reload.

## 4. Demo page access rules

After authentication, demo page access is based on the selected demo role:

- `provider` can access `/demo/provider`.
- `consumer` can access `/demo/consumer-search`.
- `admin` can access `/demo/provider`, `/demo/consumer-search` and `/demo/admin-audit`.

`/demo` itself remains the landing and role-selection page.

If no role is selected, guarded demo pages show a message asking the user to choose Provider, Consumer or Admin on the MDC Demo Console.

If a stale or manually edited selected role is not available for the current Keycloak login, the dashboard asks the user to switch role.

## 5. Sidebar filtering behaviour

The MDC Demo sidebar now filters from the selected demo role:

- No selected role: `Dashboard`
- Provider selected: `Dashboard`, `Provider Demo`
- Consumer selected: `Dashboard`, `Consumer Search`
- Admin selected: `Dashboard`, `Provider Demo`, `Consumer Search`, `Admin / Audit`

An authenticated MDC demo user continues to see only the MDC Demo section while using the demo console.

## 6. Files modified

Modified files:

- `subsystem/frontend/src/components/mdc/demoAuth.js`
- `subsystem/frontend/src/components/mdc/DemoRoleGuard.js`
- `subsystem/frontend/src/pages/demo/index.js`
- `subsystem/frontend/src/layout/AppMenu.js`

No new runtime source file was created for this task.

## 7. Manual verification steps

Recommended browser verification:

1. Open `/demo`.
2. If not logged in, click `Login`.
3. After Keycloak login, confirm role choices appear.
4. Select `Provider`.
5. Confirm sidebar shows `Dashboard` and `Provider Demo`.
6. Open `/demo/provider`.
7. Confirm `/demo/consumer-search` shows the wrong-role message.
8. Click `Switch role`.
9. Select `Consumer`.
10. Confirm sidebar shows `Dashboard` and `Consumer Search`.
11. Open `/demo/consumer-search`.
12. Confirm `/demo/provider` shows the wrong-role message.
13. Switch to `Admin`.
14. Confirm all MDC demo pages are visible.

Manual browser verification was not performed in this pass.

## 8. Commands run

```powershell
npm run lint
```

Result: passed with existing unrelated warnings in layout/document files.

`npm run build` was not run, per task instruction.

## 9. Remaining issues

- Manual browser verification still needs to be performed against the running `npm run dev` app and Keycloak login.
- Existing lint warnings remain in files outside this task's scope.
