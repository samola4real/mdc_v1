# F5_C6 Update Provider Pagination Report

## 1. Purpose and scope

This frontend-only change adds pagination to the `Update Existing Provider` list on `/demo/provider`.

## 2. Component updated

Updated:

- `subsystem/frontend/src/components/mdc/ProviderDemoPanel.js`

The pagination was added to the existing PrimeReact `DataTable` used by the update provider/offering list.

## 3. Pagination behaviour

The update list now uses DataTable pagination:

```jsx
paginator={updateRows.length > 3}
rows={3}
```

Pagination controls appear when there are more than three provider/offering rows.

## 4. Rows per page

Rows per page is set to:

```text
3
```

## 5. Data-loading behaviour preserved

The existing update list data source is unchanged. The table still receives the same `updateRows` array, which is populated from:

- static Tasowheel rows
- saved demo providers loaded from backend demo state

No provider row loading, mapping, or merging logic was changed.

## 6. Files modified

- `subsystem/frontend/src/components/mdc/ProviderDemoPanel.js`

## 7. Commands run

- `Get-Content` to inspect requested files.
- `npm run lint` from `subsystem/frontend`.

## 8. Manual verification notes

Manual browser verification was not run in this session. Recommended checks:

1. Open `/demo/provider`.
2. Switch to `Update Existing Provider`.
3. Confirm only three rows are visible per page when more than three rows exist.
4. Confirm paginator controls move between pages.
5. Confirm selecting a provider/offering still fills the update form.
6. Confirm Preview update still uses the selected row.
7. Confirm Save update for demo still uses the selected row.
8. Confirm newly registered providers still appear after demo state reload.

## 9. Remaining limitations

The table may return to the first page after demo state reload, which is acceptable for this task.
