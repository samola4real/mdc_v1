# Task 07 — Provider Area UI audit

## Executive summary

Provider Area uses one in-memory draft for provider and offering fields. Part family chooses the service category and the capability template. The count and support status of selected part types further determine which dimensions the builder sends. The offline checks reproduced omitted metal dimensions, grade loss after a material selection is reversed, and silent custom-field collisions. Update flows also have paths that discard a draft or attach it to the wrong offering after a refresh. [Form state and conditions](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L51-L86), [Refresh](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L104-L118), [Payload builder](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L149-L222)

### Reviewed source and evidence

- The permanent checkout at `C:/Users/Elahi/Desktop/mdc_v1` was fast-forwarded to `origin/main` at `dfc714c37f30354848d77ed816bea1f1c45a1ce8`. Scope is `/demo/provider`, its rendered components, form and payload helpers, and its catalogue and lifecycle clients. Existing local edits include the root `.gitignore`, Contact page and TAU logo, and adjacent demo chooser copy. The chooser's local diff changes only the Provider role description to `REMOVED`. The audited route, panel, builder, and clients match the reviewed commit. [Task 07 prompt](../prompts_phase4/07_MDC_Provider_Area_UI_Audit_Prompt.md)
- The existing localhost server returned HTTP 200 for the Provider route. A fresh signed-out Edge session loaded the route and navigated to Home. The protected Preview's read-only `GET /api/catalog/filters` returned HTTP 200 and contract `1.0`. This supplied the live vocabulary below. The authenticated form walkthrough and server acceptance of the example payloads remain unverified. [Page access rule](../../demo-frontend/src/config/routes.js#L21), [Route guard](../../demo-frontend/src/pages/_app.js#L15-L39), [Catalogue client](../../demo-frontend/src/services/mdc/catalog.service.js#L1-L23)
- The field and workflow trace comes from source. Inline Node assertions imported the actual builder and hydration functions. The offline scenarios reproduced the family and material event assignments from the panel and used synthetic drafts or snapshots. The observed outputs are summarized below. No form was submitted. [Selection handlers](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L237-L266), [Material handler](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L319-L332), [Builder exports](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L225-L263)

## Screen and component hierarchy

The authenticated route first renders the **Provider Dashboard** heading card. Its inner `DemoRoleGuard` mounts the panel for a selected Provider or Admin demo role that the session may use. The guard can show login status, role selection, or role denial messages. The Provider Area sidebar entry uses the same selected-role restriction. Role choice is stored in session storage. The form draft belongs to the mounted panel. [Provider page](../../demo-frontend/src/pages/demo/provider.js#L6-L19), [Demo role guard](../../demo-frontend/src/components/mdc/DemoRoleGuard.js#L28-L85), [Sidebar entry and visibility](../../demo-frontend/src/layout/AppMenu.js#L17-L43), [Role storage](../../demo-frontend/src/components/mdc/demoAuth.js#L58-L95)

```text
/demo/provider
├─ Card · MDC Demo Console / Provider Dashboard
└─ DemoRoleGuard
   └─ ProviderDemoPanel
      ├─ Toast and disposable-ID message
      ├─ Catalogue error and read-back warning, when set
      ├─ Register New Provider / Update Existing Provider
      ├─ Form fieldset, disabled while a request is active
      │  ├─ Update Existing Provider card, in update mode
      │  │  ├─ Provider ID to look up, Load provider, Add offering if eligible
      │  │  ├─ Read-only message for a loaded baseline provider
      │  │  └─ Offerings DataTable with StatusTag
      │  ├─ Provider information, in register mode or after provider load
      │  ├─ Offering information, in register/add or with a loaded offering
      │  ├─ Additional offering information, same condition
      │  └─ Capability information, same condition
      │     ├─ Family template and supported part types, if recognized
      │     ├─ Shared capability controls
      │     └─ Custom capability rows and Add capability field
      ├─ Mode-specific action buttons
      ├─ ProviderPayloadPreview · Advanced / payload preview
      └─ ProviderActionResult · status, receipt, MDC response details
```

The panel implements the sections as render functions. PrimeReact supplies Card, Panel, field widgets, Buttons, Messages, Toast, DataTable and Column. The panel calls the form builder for each render, the filter client on mount, and the provider service on user actions. The result and preview components consume props from the panel. The table uses a shared `StatusTag` for each offering's support status. [Panel imports](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L1-L26), [Main render](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L544-L640), [Preview component](../../demo-frontend/src/components/mdc/ProviderPayloadPreview.js#L4-L7), [Action result](../../demo-frontend/src/components/mdc/ProviderActionResult.js#L18-L46)

## Field inventory and payload paths

Initial text values, multi-selections and custom-row lists are empty. Support status starts as Confirmed. Quality standard starts as `null`. Numeric draft keys start unset. Hydrating an offering sets missing mapped bounds and dimensions to `null`. Unless stated otherwise, form controls are active whenever rendered outside a busy request. The action gates enforce the requiredness shown below. [Initial form and hydration](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L33-L44), [Hydration assignments](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L103-L137), [Button guards](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L604-L634)

Provider paths are on the registration object or provider PATCH. Offering paths are relative to `offerings[0]` on registration, the body of Create offering, or an offering PATCH. Changes to nested maps are sent as whole map values at the corresponding top-level key. New controlled records and numeric capability records receive `source_type: "provider_confirmed"` and `confidence: "declared"`. An existing visible record generally keeps its untouched children and metadata. [Range and selection helpers](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L47-L100), [Output builders](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L213-L263)

### Provider information

Shown in register mode and after a successful provider load in update mode. Add offering uses the loaded provider identity internally.

| Label and input | Default, values and editability | JSON path |
| --- | --- | --- |
| Provider name · text | Blank, then hydrated from `provider_name`. Trimmed nonempty value required for Register and Validate. Editable after load. | `provider_name` |
| Provider ID · text | Blank. Editable in register and read-only in update. Trimmed and checked by the disposable provider/offering ID gate for registration. | `provider_id` on registration. The loaded ID is the update and delete URL identity. |
| Country · text | Blank, then saved country. Trimmed nonempty value required for Register and Validate. Free text with no list or format check at the action gate. | `country` |
| Short description / notes · auto-resizing textarea | Blank. Optional free text. A blank edit removes the description from the previous custom map. | `custom_provider_fields.description` |
| Provider certifications · chip multi-select | Empty. Live certification vocabulary. Hydrates the saved record codes. Optional. | `certifications[].code` plus record provenance |

[Provider information JSX](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L210-L235), [Provider hydration and description](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L103-L110), [Registration and provider patch](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L140-L146), [Provider payload fields](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L232-L253)

### Offering information

Shown in register and add modes, and after an offering is loaded in update mode. The screen places Service category before Part family.

| Label and input | Default, values and editability | JSON path |
| --- | --- | --- |
| Offering name · text | Blank or saved name. Trimmed nonempty value required for creation. The update button has a patch-presence gate. | `offering_name` |
| Offering ID · text | Blank on creation, read-only on update. Supplied by the user and required to satisfy the disposable format and loaded provider prefix. | `offering_id` on create. The loaded ID is the offering detail/PATCH/DELETE URL identity. |
| Service category · read-only text | Blank until family selection or hydration. It displays the category code. Add can inherit the selected offering's category. Required by the creation gate. | `service_category` on creation |
| Part family · dropdown | Blank, then catalogue choices. Disabled until filters load and in update. Selecting it sets the category and clears selected part types. Required on creation. | `part_family` on creation |
| Support status · dropdown | Confirmed by default. Choices are Confirmed (`confirmed`), Requires confirmation (`candidate_requiring_confirmation`), and Unknown (`unknown`). Editable for loaded offerings. | `support_status`. Newly selected types inherit it at `supported_part_types[].support_status`. |

[Offering information JSX](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L237-L267), [Statuses and creation gate](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L28-L38), [Readiness and derived state](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L63-L78), [Offering primitives and part records](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L149-L154), [Offering create and patch](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L213-L263)

### Additional offering information

Starts with zero custom rows. **Add field** appends a blank Field name and Field value, both text inputs. **Remove** deletes that draft row. The builder emits a row when its trimmed name and value are nonempty. New rows map to string values at `custom_offering_fields[trimmed name]`. A loaded scalar or object with a scalar `value` can appear as a row. Original object fields such as unit and notes may be present in hydrated state and the JSON map. This section exposes only name and value. [Custom offering rows](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L270-L315), [Custom row projection and merge](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L64-L93), [Offering map output](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L213-L222)

### Capability information by family

The family template comes before shared capability controls. Every template starts with a chip multi-select of Supported gear, shaft, or metal part types. The options belong to the selected family. The multi-select starts empty and hydrates saved type codes. Each selected type maps to `supported_part_types[].part_type` with status and provenance. No part-type selection is required by the creation gate. There is no per-type support-status control. [Capability rendering](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L365-L478), [Supported record mapping](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L95-L100), [Hydration](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L113-L135), [Transformed part records](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L149-L153)

| Field and input | Visibility, default and units | JSON path |
| --- | --- | --- |
| Gear · Module min / max · numeric | Both always present for Gear. Blank initially, 1–2 fractional digits configured, no displayed unit. | `family_capabilities.module.min`, `.max` |
| Gear · Diameter min / max · numeric | Both always present for Gear. Blank initially, suffix mm. | `family_capabilities.outside_diameter_mm.min`, `.max` |
| Gear · Quality standard/class · dropdown | Always present for Gear. Starts blank, choices DIN, ISO, AGMA from the panel. | `family_capabilities.gear_quality.standard` |
| Gear · Quality class · text | Always present for Gear. Blank initially. A positive finite numeric conversion produces a number. Some other nonempty strings take the custom class path. | `family_capabilities.gear_quality.best_class` or `custom_capability_fields.quality_class` |
| Shaft · Length max · numeric | Always present for Shaft. Blank initially, suffix mm. | `family_capabilities.length_mm.max` |
| Shaft · Outer diameter min / max · numeric | Both always present for Shaft. Blank initially, suffix mm. | `family_capabilities.outer_diameter_mm.min`, `.max` |
| Shaft · Spline module · numeric | Visible whenever `splined_shaft` is selected. Blank initially, 1–2 fractional digits configured, no displayed unit. The builder requires confirmed support for that type. | `part_type_capabilities.splined_shaft.spline_module.value` |
| Metal part · Maximum length / width / height-thickness · numeric | Visible only for exactly one selected Block, Plate, or Bracket. Blank initially, suffix mm. | `part_type_capabilities[part type].bounding_box_mm.{length_mm,width_mm,height_mm}.max` |
| Metal part · Maximum diameter · numeric | Visible only for exactly one selected Bushing, Roller, or Collar. Blank initially, suffix mm. | `part_type_capabilities[part type].outer_diameter_mm.max` |
| Metal part · Tolerance / Surface finish · two text inputs | Visible for Metal part at every selection count. Blank initially. Free text with no separate unit input. | `custom_capability_fields.tolerance`, `.surface_finish` |

These capability inputs are optional at the UI action gate. The bound inputs are independent. The panel supplies no explicit lower/upper relation, range sign, or required companion check, and module suffixes are absent. [Family controls](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L365-L470), [Numeric key maps](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L7-L31), [Range and quality mapping](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L48-L61), [Quality and part-type serialization](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L162-L210)

### Shared and custom capability controls

These render in every visible Capability information panel, including the empty creation form before family selection. Their selectors share the same entire catalogue lists across families.

| Label and input | Default, options and conditions | JSON path |
| --- | --- | --- |
| Materials · chip multi-select | Empty. Live material vocabulary, optional. Selecting a different set usually clears the draft grade text. | `generic_capabilities.materials[].material` |
| Material grades · text | Blank, placeholder “Comma-separated grades”. Enabled only for exactly one material. Provider-supplied free text. Existing single-material grades are joined with a comma and space on load. | `generic_capabilities.materials[0].available_grades` when edited with one material |
| Processes · chip multi-select | Empty. Live process vocabulary, optional. New record has `delivery_mode: "unspecified"`. | `generic_capabilities.processes[].process` with delivery mode and provenance |
| Batch size min / max · numeric | Blank. Unit is a batch count from the field name. The controls display no suffix. | `generic_capabilities.batch_size.min`, `.max` |
| Lead time min weeks / max weeks · numeric | Blank, with weeks in the labels. | `generic_capabilities.lead_time_weeks.min`, `.max` |
| Weight max · numeric | Blank, suffix kg. The form exposes the maximum. | `generic_capabilities.weight_kg.max` |
| Notes · auto-resizing textarea | Blank and optional free text. It is part of the offering draft. | `custom_capability_fields.notes` |
| Custom Field name / Value / Unit / Notes · four text inputs | Zero rows initially. **Add capability field** appends four empty strings. **Remove** drops a row. A trimmed name and value are necessary to emit it. Unit and notes are optional text. | `custom_capability_fields[trimmed name].value` plus optional `.unit` and `.notes` for a new row |

[Shared controls](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L319-L362), [Custom capability controls](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L473-L541), [Generic key maps](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L7-L11), [Custom maps, materials and processes](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L149-L189)

### Lookup, table, preview and results

| Surface | Contents and condition |
| --- | --- |
| Provider ID to look up · text | Update only. Starts empty. **Load provider** requires trimmed text and idle state. The lookup input has no disposable-ID format requirement because baseline identities can be read. After refresh it shows the ID requested. It is separate from the loaded provider ID. |
| Offerings table · single row selection | Visible throughout update mode. Columns are Provider, Offering, Service category, Part family, Supported part types, Materials, Processes, and Status. The first four are sortable. The next three join saved codes with commas. Status is the offering support code. Selection is disabled while busy. The table scrolls responsively and paginates above three rows at three rows per page. Empty message is “No offerings loaded”. Row identity is `offering_id` internally. |
| Advanced / payload preview | Collapsed, toggleable JSON panel. Shows the single-offering registration envelope, the add-offering body, or `{ provider, offering }` patch drafts in update. The patch wrapper is for display. Save buttons send the selected entity's object. |
| Result panel, receipt and toast | Initially empty. A request clears the previous result and warning, then shows a success or error message. Errors also raise a 3.5-second warning toast. A publication receipt shows ID and status if returned, plus “Semantic synchronization pending” for pending sync. The collapsed details panel displays response JSON or error details. |

[Table data projection](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L39-L49), [Lookup and table](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L544-L578), [Status style mapping](../../demo-frontend/src/components/mdc/StatusTag.js#L4-L32), [Preview](../../demo-frontend/src/components/mdc/ProviderPayloadPreview.js#L4-L7), [Request feedback](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L121-L151), [Result rendering](../../demo-frontend/src/components/mdc/ProviderActionResult.js#L18-L46)

## Catalogue options and dependency matrix

The vocabulary below is the contract `1.0` response observed on the protected Preview. The local panel asks for it once on mount. The client checks the contract version and array shape, falls back from a missing label to the item value, and constructs one category per family from `service_categories[].part_family`. The family dropdown receives catalogue labels. The service category text receives its code. Panel templates and input-to-capability rules are defined in frontend code. [Catalogue normalization](../../demo-frontend/src/services/mdc/catalog.service.js#L3-L23), [Catalogue load](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L80-L86), [Family change handler](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L248-L265), [Template selection](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L466-L478)

| Part family | Automatic service category | Complete supported part-type options |
| --- | --- | --- |
| Gear · `gear` | `precision_gears` | Spur gear (`spur_gear`), Helical gear (`helical_gear`), Bevel gear (`bevel_gear`), Worm gear (`worm_gear`), Crown gear (`crown_gear`) |
| Shaft · `shaft` | `precision_shafts` | Plain shaft (`plain_shaft`), Stepped shaft (`stepped_shaft`), Splined shaft (`splined_shaft`), Worm shaft (`worm_shaft`), Hollow shaft (`hollow_shaft`) |
| Metal part · `metal_part` | `precision_metal_parts` | Block (`block`), Plate (`plate`), Bracket (`bracket`), Bushing (`bushing`), Roller (`roller`), Collar (`collar`) |

| Shared option set | Live codes in response order |
| --- | --- |
| Materials | `steel`, `alloyed_carburizing_steel`, `stainless_steel`, `aluminum`, `titanium`, `nickel_alloy` |
| Processes | `machining`, `turning`, `milling`, `hobbing`, `gear_shaping`, `deburring`, `hard_turning`, `grinding`, `tooth_grinding`, `gear_grinding`, `gear_cutting`, `surface_grinding`, `heat_treatment`, `turn_mill`, `inspection` |
| Certifications | `ISO9001_2015`, `ISO14001_2015`, `ISO_TS_16949_partial`, `APQP`, `aerospace_traceability`, `full_traceability` |

### Offering choices through Capability information

| Controlling action | State and visible controls | Payload and round-trip consequence |
| --- | --- | --- |
| No Part family yet | No family-specific controls. Shared and custom capability controls are available. | The preview can contain shared draft capabilities. Create and Validate stay disabled. |
| Select or change Part family in register/add | Sets `partFamily` and calculated `serviceCategory`. Clears only `partTypes`. React replaces the rendered family template. Shared settings, old template draft values, and custom rows stay in `form`. | New offering receives the family and category. Family numeric maps use the current family. Switching back can expose old draft values. Tolerance and finish can follow the draft even when hidden. |
| Gear with zero, one, or multiple part types | Module, diameter, and quality controls stay visible across all three counts. | Family values stay at `family_capabilities`. The UI adds no gear-specific per-type dimension editor. Zero types can serialize as `[]`. |
| Shaft with zero types or types without Splined shaft | Length and outer diameter stay visible. Spline module is hidden. Its draft key is retained if previously entered. | Shaft family values serialize independently. A removed spline type loses its part entry from the constructed map. |
| Shaft with Splined shaft alone or alongside other types | An inclusion test exposes Spline module at both counts. | The spline value serializes when the selected `splined_shaft` record is confirmed. A previously selected eligible draft spline value can reappear when Splined shaft is restored. |
| Metal part with zero types | Tolerance, surface finish, and shared controls remain. Box and round editors are hidden. | New offering has no type dimensions. Existing part entries for deselected types are filtered out of the constructed map. |
| Exactly one Block, Plate, or Bracket | Shows the same three box controls and draft keys whichever single type is selected. | When confirmed, values go under the current type's `bounding_box_mm`. Replacing the sole type can reuse values typed for the former type. |
| Exactly one Bushing, Roller, or Collar | Shows the one shared Maximum diameter draft key. | When confirmed, it goes under the current type's `outer_diameter_mm.max`. Switching the single type can reuse that number. |
| Metal part with multiple types, including Block + Roller or Block + Plate | Both dimension editors hide for every multi-type selection. Their draft keys remain in memory. Tolerance and surface finish remain visible. | A new multi-type offering carries no typed dimensions from those keys. An update can preserve stored maps for retained confirmed types while ignoring unsaved box/round edits. |
| Change the offering's Support status | Updates the overall selector. It has no effect on which dimension controls render. | It sets the offering status and defaults new supported-type records. Previously loaded records keep their own status and provenance. Typed output is gated by each type's recorded confirmed status. |
| Deselect a supported type on an existing offering | The handler changes only the array. Shared dimension state is still present. Each refreshed multi-type offering starts with blank metal dimension inputs. | The supported list drops that type. An emitted change to the part-type map excludes its entire stored branch. Other selected confirmed branches are retained where available. |

[Family and status event handling](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L248-L265), [Exact-one type gates](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L67-L78), [Gear, shaft and metal rendering](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L365-L470), [Read-back projection](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L113-L137), [Support and part-map construction](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L149-L211)

### Other selection effects

| Action | Input and payload behavior |
| --- | --- |
| Pick zero or several materials | Grade text is disabled. A material selection event clears draft grades unless it leaves the same sole material. When a changed material list is emitted, surviving saved records keep their original per-material grades and metadata. Removed records and their grades leave the replacement list. |
| Pick exactly one material | Grade text enables. A fresh selection begins blank. Hydration fills it only if the stored offering has exactly one material. Reducing a loaded multi-material record to one shows a blank field even when a retained grade list still exists. |
| Type grades | Splits on commas, trims fields and drops empty tokens. Repeated nonempty grades are kept. Editing a sole material's grade text emits the replacement list, including `[]` after clearing. |
| Change processes | The same live options apply to all families. Existing selected codes carry their saved delivery mode and evidence. New values use `unspecified`. Removing a selection drops that record from the replacement array. |
| Change certifications | Uses the provider's shared catalogue list. The builder keeps the first previous record matching each selected code. New codes gain default evidence. Removed codes leave the array. |
| Reorder or repeat values | Array comparisons are order-sensitive. The builder maps each selected entry in order and finds the first previous record with its key. Loaded duplicate keys can therefore share the first record's metadata when the array is rebuilt. The live option lists have unique codes. Grade text and custom-row inputs permit repeated text directly. |
| Add, rename, clear or remove custom rows | Rows append blank. The last complete row for the same trimmed, case-sensitive name wins. An incomplete new row is omitted. If the old editable name is missing from the complete rows, the old key is deleted from the replacement map. Opaque stored values stay in the map. A newly entered row with an opaque key is ignored. |
| Edit or erase one bound | Only the edited leaf changes. A blank leaf is removed. Other bounds and untouched metadata survive. A range entry with no fields beyond the two default evidence keys is removed. |

[Row state operations](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L88-L102), [Material and process inputs](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L319-L356), [Range and custom-row logic](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L47-L97), [Material and process arrays](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L177-L189), [Certification and patch comparison](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L242-L263)

## Lifecycle modes and request flow

### Draft and snapshot

`mode` starts as `register`. `form` holds both entities' controls. `lookupId` is a separate editable string. `snapshot` contains provider response and ETag, offering list, and selected offering response and ETag. Table cells come from the snapshot. A modified draft changes the payload preview without changing those cells. `loadingAction` drives the busy display, and an `inFlight` ref rejects a second action while a request is running. `actionResult`, `filterError`, and `stateLoadWarning` drive feedback. [State and derived values](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L39-L86), [Action handler](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L121-L153)

**Refresh** requests provider detail and its offering list concurrently. It requests the preferred offering if present, otherwise the first item, then hydrates the form. A provider with an empty offering list gets only the provider fields. Switching either top mode clears form, snapshot, result, and warning. It keeps the typed lookup ID. There is no separate per-offering draft store in the panel. [Refresh and mode switching](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L104-L119), [Mode operations](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L155-L190)

### Actions and enablement

Browser routes below are relative to the local `/api/mdc` relay. Creation readiness requires loaded filters, nonblank offering name, family and category, and a matching disposable provider/offering ID pair. IDs use lowercase letters and digits separated by single underscores and begin with `mdc_stage1b_`. The provider ID limit is 255 characters and the offering ID limit is 512. Creation requires an offering ID beginning with its provider ID followed by an underscore and a suffix. [Creation readiness](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L67-L78), [ID predicates](../../demo-frontend/src/services/mdc/stage1bScope.js#L1-L13), [Service methods](../../demo-frontend/src/services/mdc/provider.service.js#L3-L17)

| Action | Trigger and request | State or result |
| --- | --- | --- |
| Register New Provider | Idle top mode button. | Resets to a blank provider and one blank offering. |
| Validate publication | Register only. Idle and creation-ready, with trimmed nonempty name and country. `POST /provider-publication/validation`. | Sends the publication envelope. The result is feedback only. The current draft remains editable. |
| Register provider | Same enablement as Validate. `POST /provider-publication`. | Sends `contract_version: "1.0"`, provider identity/name/country, optional description, certifications, and exactly one offering. Success inspects by switching to update and refreshing the submitted provider and offering. |
| Update Existing Provider / Load provider | Mode button clears the previous draft. Load requires a nonblank lookup and idle state. `GET /providers/{id}` and `GET /providers/{id}/offerings`, then `GET /offerings/{id}` if a row exists. | Load clears the former snapshot and form before the request. The first offering is loaded initially. Baseline provider data can be read. |
| Select offering | Select a different row while idle. `GET /offerings/{id}`. | Hydrates the chosen offering and copies the four current provider draft fields. It has no mechanism to stash the previous offering draft. A click on the current row is ignored. |
| Add offering | Loaded provider has a disposable ID. The button is visible in the update card and needs filters and idle state. | Switches to add, hides provider and lookup sections, and initializes from the saved provider. Only the current offering family and category are carried into the offering draft. |
| Create offering | Add only. Idle, creation-ready, and manageable provider. `POST /providers/{providerId}/offerings`. | Body is an offering creation object. The provider ID is in the URL. The read-back returns to update and prefers the new offering ID. |
| Save provider | Update with a loaded disposable provider, its strong ETag, an idle state and a nonempty provider patch. `PATCH /providers/{providerId}` with If-Match. | Sends the provider patch alone. Refresh normally replays dirty offering fields over the fresh form. It works when there are no offerings. |
| Save offering | Update with a selected offering, manageable provider, strong offering ETag, idle state and nonempty offering patch. `PATCH /offerings/{offeringId}` with If-Match. | Sends the offering patch alone. Refresh normally replays dirty provider fields. Offering ID, family, and service category are excluded from PATCH construction. |
| Delete offering | Same entity/idle/ETag requirements, with disposable offering ID checked against the loaded provider. Browser confirmation. `DELETE /offerings/{offeringId}` with If-Match. | Refreshes without preserving a draft. If the selected offering is gone, refresh chooses the first remaining offering or leaves provider-only fields. |
| Delete provider | Loaded disposable provider, its strong ETag, idle state and browser confirmation. `DELETE /providers/{providerId}` with If-Match. | On success clears the snapshot and form in update. The lookup remains. |

[Read-back and mode transitions](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L104-L208), [Lookup controls](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L544-L558), [Action buttons](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L588-L639), [Creation and PATCH outputs](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L225-L263), [Service methods](../../demo-frontend/src/services/mdc/provider.service.js#L8-L17)

### Transport and feedback boundary

The default client uses a relative `/api/mdc` path, obtains the current Keycloak access token, and sends JSON through Axios. Only detail reads request wrapped `{ data, status, etag }` for hydration and concurrency. The generic list read returns the body. The loopback relay checks the endpoint, permitted role, and disposable scope for writes, then forwards to the pinned Preview. On PATCH and DELETE it forwards the conditional value as `X-MDC-If-Match`. The browser gets the upstream status, contract `1.0` JSON and ETag when present. [Runtime path](../../demo-frontend/src/config/runtimeConfig.js#L9-L14), [Browser client](../../demo-frontend/src/services/mdc/client.js#L9-L55), [Relay route and write rules](../../demo-frontend/src/pages/api/mdc/%5B...path%5D.js#L14-L50), [Conditional forwarding and response](../../demo-frontend/src/pages/api/mdc/%5B...path%5D.js#L136-L175)

The result card uses a generic response message and the receipt fields when present. Field-level errors are available as collapsed response details. On write success, transport uncertainty, 404/409/412/428 or a 5xx response, `runAction` may run the read-back handler. If read-back fails, it clears the snapshot and warns to load current state. An HTTP response can therefore show an accepted receipt even when the form could not reload. Actual validation of payload content is an API decision. [Result component](../../demo-frontend/src/components/mdc/ProviderActionResult.js#L7-L46), [Error normalization](../../demo-frontend/src/services/mdc/client.js#L16-L28), [Read-back handling](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L121-L159)

## Offline payload examples

These are excerpts from the actual builder output for synthetic values, using the observed catalogue codes. They illustrate serialization with no claim about server validation.

### Gear with Spur gear and Helical gear

The same family values appeared with zero, one, and two selected gear types. The single-material grade was placed on the material record.

```json
{
  "part_family": "gear",
  "service_category": "precision_gears",
  "supported_part_types": [
    {"part_type": "spur_gear", "support_status": "confirmed", "source_type": "provider_confirmed", "confidence": "declared"},
    {"part_type": "helical_gear", "support_status": "confirmed", "source_type": "provider_confirmed", "confidence": "declared"}
  ],
  "family_capabilities": {
    "module": {"min": 1.5, "max": 3, "source_type": "provider_confirmed", "confidence": "declared"},
    "gear_quality": {"standard": "ISO", "best_class": 6, "source_type": "provider_confirmed", "confidence": "declared"}
  },
  "generic_capabilities": {
    "materials": [
      {"material": "steel", "available_grades": ["18CrNiMo7-6"], "source_type": "provider_confirmed", "confidence": "declared"}
    ]
  }
}
```

### Shaft with Plain shaft and Splined shaft

The form can emit a spline value with both types selected. In the offline sample, changing a new draft's overall status to Requires confirmation omitted the spline entry. Hydrating that candidate snapshot and changing only the overall status to Confirmed plus editing spline module emitted `{"support_status":"confirmed"}`.

```json
{
  "part_family": "shaft",
  "service_category": "precision_shafts",
  "family_capabilities": {
    "length_mm": {"max": 300, "source_type": "provider_confirmed", "confidence": "declared"},
    "outer_diameter_mm": {"max": 50, "source_type": "provider_confirmed", "confidence": "declared"}
  },
  "part_type_capabilities": {
    "splined_shaft": {
      "spline_module": {"value": 2, "source_type": "provider_confirmed", "confidence": "declared"}
    }
  }
}
```

### Metal part with a single Block

The sole Block serialized all three box dimensions. A sole Roller in a separate example serialized `part_type_capabilities.roller.outer_diameter_mm.max: 70`. Adding Roller to the Block draft produced two supported type records and an empty `part_type_capabilities` map.

```json
{
  "part_family": "metal_part",
  "service_category": "precision_metal_parts",
  "part_type_capabilities": {
    "block": {
      "bounding_box_mm": {
        "length_mm": {"max": 80, "source_type": "provider_confirmed", "confidence": "declared"},
        "width_mm": {"max": 50, "source_type": "provider_confirmed", "confidence": "declared"},
        "height_mm": {"max": 12, "source_type": "provider_confirmed", "confidence": "declared"}
      }
    }
  },
  "custom_capability_fields": {"tolerance": "0.1 mm", "surface_finish": "Ra 1.6"}
}
```

[Example mapping](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L149-L239)

## Critical findings

### 1. High · Additional metal types suppress dimension edits

Select Block and enter maximum length 80 mm, then add Roller. The box editor disappears and the new-offering payload includes both types but no typed dimensions. This also happens with two box types. For a saved Block with maximum length 80 mm, the offline update from 80 to 100 plus adding Roller produced a supported-types patch and no part-capability patch. The prior 80 mm stays in the stored map while the draft 100 mm is absent from the request. The action gate stays available when the other creation or update conditions are met. [Exact-one rendering](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L74-L78), [Metal controls](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L425-L454), [Part-map construction and patch diff](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L191-L210), [Patch emission](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L254-L260)

### 2. High · Draft dimensions can attach to a different type

Enter 80 mm for Block, then change the sole type to Plate. The same form key is still populated. The offline payload attached 80 mm to `part_type_capabilities.plate`. An analogous reuse is possible among the round-type diameter controls. Separately, entering metal tolerance and surface finish then choosing Gear hid those inputs and still emitted both custom keys in the gear payload. Family-specific numeric maps are selected by family. Shared values and free custom rows also survive the family switch. [Family change](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L254-L258), [Selection handlers and shared dimension keys](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L425-L461), [Custom note mapping](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L149-L161), [Typed output](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L198-L210)

### 3. High · Existing per-type measurements are invisible in multi-type edits

Hydrate a saved Block and Roller with both types confirmed and their maps populated. Both dimension draft values are blank in the offline hydration. Narrowing to Roller enables Maximum diameter with a blank draft value even though the outgoing retained Roller branch can still contain 70 mm. The same selection change emits a part-map replacement dropping the entire saved Block branch. This creates a risk of overwriting a hidden retained value or unintentionally removing a complete type's capabilities. An unchanged hydrated snapshot produced no patch. [Hydration's single-type projection](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L117-L137), [Metal controls](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L425-L454), [Filter and merge of part branches](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L191-L211), [Diff generation](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L254-L260)

### 4. High · Reversing a material selection can clear saved grades

Load an offering with Steel and a saved grade, add Titanium, then remove Titanium. The material codes return to the original list, but grade text was cleared on both transitions. The offline patch emitted Steel with `available_grades: []`. A second scenario exposed the inverse confusion. Hydrating a two-material offering and removing the other material showed an empty grade input while the payload retained Steel's saved grades. Removing any material drops its record and its evidence with it. [Material event handler](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L319-L332), [Single-material hydration](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L118-L124), [Replacement array and grade split](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L177-L184)

### 5. High · Overall support and typed eligibility can diverge

Select Splined shaft on a new Draft and choose Requires confirmation. The spline input remains visible even when its value cannot be emitted. For a loaded candidate Splined shaft, changing the overall dropdown to Confirmed does not promote the saved part-type status. Removing then re-adding the same type within the same unsaved draft still looks up the previous record. The panel cannot show or edit its distinct status. The same rule governs metal dimensions. Because the constructed part map keeps only selected confirmed branches, a full-map patch can exclude any stored branch that no longer meets that condition. [Support selector](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L261-L264), [Spline and metal visibility](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L416-L453), [Existing type record reuse](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L95-L101), [Part serialization](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L149-L154), [Confirmed eligibility](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L191-L211)

### 6. High · Custom names can overwrite or hide data

Add two complete custom offering rows named “Inspection method”, including one with surrounding spaces. Only the last survives in the map. A dedicated Notes value then overrides a custom capability row named `notes`, dropping that row's unit and notes. With only a custom `notes` object, hydration projects it to the dedicated text input as `[object Object]`. The same reserved-name mechanism applies to tolerance, surface finish and quality class. An editable row dropped, renamed, or cleared to an incomplete row can remove its earlier visible key. The UI accepts duplicate names and reserved names without feedback. [Custom row controls](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L270-L315), [Capability row controls](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L473-L541), [Map keys and duplicates](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L64-L93), [Reserved field hydration](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L125-L136), [Dedicated fields overriding custom keys](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L155-L175)

### 7. Medium · The form has a partial projection of richer records

Loading custom scalar, structured and opaque values gives different behavior. Changing a numeric custom offering value from 10 to 11 in the offline example emitted the string `"11"`. A new row using an opaque existing key was ignored and that object's original value was preserved. Existing typed records keep remote provenance and unexposed numeric siblings even when a visible leaf is edited. The UI can show only one selected material's grades, a record's certification code, a process code, exposed dimensions, and a subset of custom values. It exposes no editors for evidence, process delivery mode, arbitrary provider custom keys, other family bounds such as length minimum, or stored provider/offering active-state fields. This limits inspection and makes the meaning of retained data difficult to see. [Existing custom row projection and edits](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L47-L97), [Hydration subset](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L103-L137), [Metadata and array preservation](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L149-L189), [Visible table fields](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L561-L572)

### 8. High · Mode changes and row changes discard drafts

Editing an offering then selecting a different row retains only the provider draft. The old offering edit disappears after the detail read. Clicking either mode button, including the already selected one, clears the form and snapshot. Loading another provider clears the current form before the request, so a failed lookup can also lose it. Starting Add offering hydrates from the saved provider, dropping dirty provider and offering fields. Deleting an offering refreshes both drafts. None of these paths checks for unsaved changes before replacing the state. [Lookup reset](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L544-L558), [Switch, selection, add and delete](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L161-L208), [Mode button handlers](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L588-L603)

### 9. High · Read-back can discard attempted edits or replay them on a different offering

A 412 is eligible for the same read-back as success. The selected save preserves the other entity's dirty fields. A successful reload therefore replaces the attempted edits on the entity that had the stale ETag. In a separate concurrency scenario, save a provider while retaining a dirty selected offering. If that offering disappears before read-back, refresh selects the first available offering and replays old dirty offering keys over the new form. A later save can target the replacement offering with its fresh ETag. These are source-derived scenarios. Concurrent writes were outside the audit. [Refresh fallback and dirty-field replay](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L104-L118), [Error read-back eligibility](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L121-L159), [Save arguments](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L620-L628)

### 10. Medium · Read-only provider fields look editable

Load a baseline provider. The update card says that the provider is read-only, yet the visible name, notes, material, process and capability widgets accept local changes in source. The preview can display changes that have no enabled write action. The ID and Part family have their own locks, and the write buttons use separate disposable gates. The table shows saved snapshot values while the form can diverge. [Editable controls](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L210-L265), [Read-only message and snapshot table](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L544-L578), [Write button gates](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L620-L634)

### 11. Medium · ID and required-field feedback stops at button enablement

Register or Validate stay disabled until the offering ID starts with the complete provider ID followed by another underscore and a suffix. The banner mentions only the general disposable prefix. The inputs have no per-field reason, generated ID, or required-field marks, so two apparently disposable IDs can leave the actions disabled. Update save requires a nonempty patch and an ETag. Clearing name or country can produce an empty-string patch without the create-time nonblank gate. For an offering outside the relay's disposable format on an otherwise manageable provider, Save offering can enable because it lacks Delete offering's offering-ID check. The relay rejects such a write. [ID predicates](../../demo-frontend/src/services/mdc/stage1bScope.js#L1-L13), [Creation and write controls](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L77-L78), [Banner and buttons](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L584-L634), [Provider patch](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L242-L253), [Relay scope](../../demo-frontend/src/pages/api/mdc/%5B...path%5D.js#L43-L50), [Relay rejection](../../demo-frontend/src/pages/api/mdc/%5B...path%5D.js#L136-L141)

### 12. Medium · Validation feedback can describe an earlier draft

Validate does not set a validated flag and Register shares its creation gate. Editing the form after validation leaves the last result on screen. A successful transport response is shown as “completed” or “accepted” even when domain details such as `valid` are available only in the collapsed JSON panel. An invalid HTTP response supplies general guidance or a toast, with no link from a rejected field to its control. On a write with a failed read-back, receipt and warning can refer to the same action with different outcomes. [Field and action state](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L88-L95), [Read-back](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L121-L148), [Parallel creation gates](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L604-L613), [Result text and details](../../demo-frontend/src/components/mdc/ProviderActionResult.js#L18-L46)

### 13. Medium · Numeric and quality inputs have inconsistent semantics

Independent minimum and maximum fields can construct single-sided or reversed ranges. The form has no shared range check, and acceptance of negative values or unusual bounds is a backend-validation question. Gear quality uses Number conversion plus a positivity and finiteness check. Non-numeric or nonpositive text generally goes to a custom string. The offline value `Infinity` was neither emitted as a numeric class nor stored in the custom class because it is positive and nonfinite. Module and spline module configure decimal digits with no unit label, while diameter bounds and weight display units. [Shared numeric JSX](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L338-L356), [Gear/spline inputs](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L371-L421), [Range construction](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L48-L61), [Gear quality conversion](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L162-L175)

### 14. Medium · Catalogue options and templates can disagree

The same materials and processes appear for each family. The live process options include the distinct entries Tooth grinding and Gear grinding / tooth grinding with overlapping labels. The UI can present combinations without communicating whether a family or part type supports them. A future second category for one family would silently replace the first in the category lookup. An unfamiliar family value with a category could meet creation checks and render only shared capabilities. A catalogue load error disables creation and displays a message. The fetch runs again on remount, and the panel offers no retry control. Existing provider lookup and patch gates use separate conditions. [Observed vocabulary](#catalogue-options-and-dependency-matrix), [Catalogue normalization](../../demo-frontend/src/services/mdc/catalog.service.js#L7-L23), [Loading and creation readiness](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L77-L86), [Shared options](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L319-L337), [Template fallback](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L466-L478), [Error message and mode controls](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L581-L603), [Update buttons](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L620-L634)

### 15. Medium · Record context is easy to lose during lookup and creation

Changing lookup text keeps actions targeted at the loaded provider until Load provider is pressed. The loaded ID appears separately inside Provider information. Add mode hides that lookup card and provider information. Its payload preview contains an offering body while the actual provider target is in the URL. The table uses the same empty text before lookup and after a successful empty list. Two similarly named offerings can be hard to distinguish because IDs are visible only after selection. The Status column shows support codes and omits the lifecycle active state. The candidate code uses the shared tag's default info style. [Row projection](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L39-L49), [Lookup and table](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L544-L578), [Hidden sections in Add](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L594-L602), [Create offering target](../../demo-frontend/src/components/mdc/ProviderDemoPanel.js#L616-L619), [Table status mapping](../../demo-frontend/src/components/mdc/StatusTag.js#L4-L32)

### 16. Low · Normalization and repeated input can produce surprising patches

Adding spaces to an existing provider name can enable Save provider because the dirty check compares the raw draft. The sent name then gets trimmed. Offering equality compares the constructed, trimmed name instead. Grade input trims tokens but keeps duplicates. Editing a joined grade list splits every comma, so a stored grade label with an embedded comma has no delimiter escape in the text editor. A change in selection order can also affect the generated PATCH. [Trim and comparison helpers](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L1-L5), [Grade joining and splitting](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L122-L124), [Grade output](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L177-L183), [Offering name construction](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L213-L221), [Entity patch comparisons](../../demo-frontend/src/components/mdc/providerPayloadBuilder.js#L242-L261)

## Open questions for the redesign discussion

- Which part-type capability values are expected when one offering covers several types, and which combinations may intentionally omit per-type dimensions or spline data?
- Which ranges, units, quality classes and material grade formats does the canonical contract accept? The current action gates leave these decisions to the backend.
- How should existing per-type statuses, source evidence, delivery modes and multiple materials' grades be interpreted when editing stored records?
- In the Provider Area, what does a provider expect to keep after switching an offering, removing a type, retrying a stale save, or returning from Add offering?
- Which conditions matter on the authenticated screen for keyboard navigation, narrow layouts, and reliable field-level feedback? The browser evidence here covers the signed-out route. The authenticated interaction findings are based on source and offline payload reproduction.
