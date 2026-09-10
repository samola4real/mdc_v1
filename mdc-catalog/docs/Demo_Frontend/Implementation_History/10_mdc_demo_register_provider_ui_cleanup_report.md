# F5_C1 - Register New Provider UI Cleanup and Flexible Capability Structure

## 1. Purpose and scope

F5_C1 cleans up the `/demo/provider` registration UI and replaces the gear-specific registration form with a flexible template-based capability form.

This is a frontend-only correction. It does not modify backend code, consumer search, role/login logic, admin/audit actions, API service modules, packages, `.env`, runtime config, route config or Keycloak files.

## 2. UI sections after cleanup

The provider page now presents a simpler provider area with:

- `Register New Provider`
- `Update Existing Provider`

Register mode now shows only:

- `Provider information`
- `Offering information`
- `Capability information`

Removed from the main UI:

- Provider Demo descriptive text.
- Provider demo workflow explanatory card.
- Load sample provider button.
- Gear capability fields heading.

The payload preview remains collapsed under `Advanced / payload preview`.

## 3. Capability templates added

The registration flow now supports these helper templates:

- Gear manufacturing
- Shaft manufacturing
- Metal-part manufacturing
- General precision manufacturing

The template selector includes the requested guidance text: choose a template for useful capability fields, and use General precision manufacturing when the provider does not fit a specific template.

## 4. Fields shown for each template

Gear manufacturing:

- Supported gear part types
- Module min/max
- Diameter min/max
- Quality standard/class
- Materials
- Material grades
- Processes
- Certifications
- Batch size min/max
- Lead time min/max
- Weight max
- Notes

Shaft manufacturing:

- Supported shaft part types
- Length max
- Outer diameter min/max
- Spline module
- Materials
- Material grades
- Processes
- Certifications
- Batch size min/max
- Lead time min/max
- Weight max
- Notes

Metal-part manufacturing:

- Supported metal part types
- Maximum length
- Maximum width
- Maximum height/thickness
- Maximum diameter
- Maximum weight
- Materials
- Material grades
- Processes
- Certifications
- Tolerance
- Surface finish
- Batch size min/max
- Lead time min/max
- Notes

General precision manufacturing:

- Capability description
- Supported part types / keywords
- Maximum size / dimensions
- Maximum weight
- Materials
- Material grades
- Processes
- Certifications
- Batch size min/max
- Lead time min/max
- Notes

## 5. Payload builder adjustment

The frontend payload builder now includes:

- `description`
- `capability_template`
- template-specific capability fields inside `capabilities`
- shared capability fields inside `capabilities`

The payload shape remains compatible with the existing preview/register button flow:

```javascript
{
  action: "register_provider",
  provider_id,
  provider_name,
  country,
  description,
  offerings: [
    {
      offering_id,
      offering_name,
      service_category,
      part_family,
      capability_template,
      supported_part_types,
      capabilities: {}
    }
  ]
}
```

Generic or template-specific values are kept under `capabilities` rather than adding many new top-level fields.

## 6. Files modified/created

Modified files:

- `subsystem/frontend/src/pages/demo/provider.js`
- `subsystem/frontend/src/components/mdc/ProviderDemoPanel.js`
- `subsystem/frontend/src/components/mdc/providerPayloadBuilder.js`
- `subsystem/frontend/src/components/mdc/ProviderPayloadPreview.js`
- `subsystem/frontend/src/components/mdc/mockData.js`

Created file:

- `docs/10_mdc_demo_register_provider_ui_cleanup_report.md`

## 7. Safety confirmation

This task did not modify:

- Backend code
- Consumer search pages/components
- Role/login logic
- Admin/audit pages
- API service modules
- Packages
- `.env` files
- Runtime config
- Route config
- Keycloak files

## 8. Commands run

```powershell
npm run lint
```

Result: passed with existing unrelated warnings in layout/document files.

`npm run build` was not run, per task instruction.

## 9. Manual verification notes

Manual browser verification was not performed in this pass.

Recommended check:

1. Run `npm run dev`.
2. Open `http://localhost:3000/demo/provider`.
3. Select `Register New Provider`.
4. Confirm `Provider information`, `Offering information` and `Capability information` are visible.
5. Select `Metal-part manufacturing` and confirm metal-part fields appear.
6. Select `General precision manufacturing` and confirm generic fields appear.
7. Confirm `Load sample provider` does not appear.
8. Confirm no `[object Object]` appears.
9. Confirm preview/register buttons still exist.

## 10. Remaining issues

- Manual browser verification still needs to be performed in the running dev app.
- Backend validation may not accept every new frontend helper value until a later backend vocabulary phase. New template-specific data is kept inside `capabilities` where possible, but unsupported top-level vocabulary values can still be rejected by the existing backend.
