# F5_C4 Demo Provider State Read Frontend Report

## 1. Purpose and scope

This frontend-only change makes saved demo providers visible in the Provider page `Update Existing Provider` section. It does not modify consumer search, role/login, admin/audit, runtime config, packages, or backend code.

## 2. State endpoint consumed

The frontend demo service now exposes:

```javascript
getProviderDemoState()
```

It calls:

```http
GET /api/demo/provider-publication/state
```

through the existing demo API path helper.

## 3. How demo providers are merged into update list

`ProviderDemoPanel.js` keeps the static Tasowheel rows as the baseline update list. When the component opens, it calls `getProviderDemoState()`, maps saved providers and offerings into update-table rows, and merges those rows with the static rows by offering ID.

The update table now includes a Provider column, so rows can display examples such as:

- `Tasowheel Oy / Precision gears`
- `Tasowheel Oy / Precision shafts`
- `TAU / xxxx`

Saved flexible providers use generic update defaults where controlled fields are not present.

## 4. Refresh-after-register behaviour

After a successful `Register for demo` save with `action: "register_provider"`, the Provider page calls `getProviderDemoState()` again. This reloads backend demo state so the newly registered provider can appear in `Update Existing Provider` immediately.

## 5. Error handling

If the state endpoint is unavailable or returns an unreadable response, the UI falls back to the static Tasowheel rows and does not crash. The update panel shows a warning that saved demo providers could not be loaded.

## 6. Files modified

- `subsystem/frontend/src/services/mdc/demoAdmin.service.js`
- `subsystem/frontend/src/components/mdc/ProviderDemoPanel.js`

## 7. Commands run

- `Get-Content` to inspect requested files and related context.
- `rg` to find provider-state references and confirm the existing static list behavior.
- `git diff` to inspect the modified frontend files.
- `npm run lint` from `subsystem/frontend`.

## 8. Manual verification notes

Manual browser verification was not run in this session. Recommended manual test:

1. Start backend.
2. Start frontend with `npm run dev`.
3. Open `/demo/provider`.
4. Register a new provider.
5. Confirm successful save.
6. Open `Update Existing Provider`.
7. Confirm the new provider/offering appears.
8. Refresh the page.
9. Confirm it still appears from backend demo state.
10. Confirm consumer search behavior is unchanged.

## 9. Remaining limitations

Saved flexible providers may not have controlled update fields such as `service_category`, `part_family`, or `supported_part_types`. The update editor maps those rows to generic defaults where needed. Consumer search reflection is intentionally out of scope for this task.
