# F5_C - Provider Add/Register and Update Existing Provider Demo Flow

## 1. Purpose and scope

F5_C implements a demo-only provider-side workflow for the Monday demo:

- Register a new provider profile.
- Update an existing provider/offering capability.
- Preview provider payloads before saving.
- Save demo-only state to a local JSON file.

This phase intentionally does not implement production onboarding, real login/user management, curated YAML publishing, RDF regeneration, Fuseki reloads, or consumer-search reflection. Consumer search reflection is deferred to F7.

## 2. Provider registration flow

The `/demo/provider` page now includes a `Register New Provider` mode.

Supported registration UI:

- Load sample provider.
- Provider ID.
- Provider name.
- Country.
- Offering ID.
- Offering name.
- Service category.
- Part family.
- Supported part types.
- Materials.
- Available grades.
- Processes.
- Certifications.
- Capability ranges.
- Preview.
- Register for demo.
- Payload preview.
- Result panel.

The sample provider button fills:

- Provider: `Demo Gear Provider Oy`
- Provider ID: `demo_gear_provider`
- Country: `Finland`
- Offering: `Precision gears`
- Offering ID: `demo_gear_provider_precision_gears`
- Part family: `gear`
- Supported part types: `spur_gear`, `helical_gear`
- Module range: `1-8`
- Diameter range: `20-300 mm`
- Materials: `alloyed_carburizing_steel`
- Grades: `16MnCr5`, `20MnCr5`
- Processes: `machining`, `hobbing`, `gear_grinding`
- Certification: `ISO9001_2015`

## 3. Existing provider update flow

The `/demo/provider` page now includes an `Update Existing Provider` mode for updating the existing Tasowheel precision gears capability.

Supported update UI:

- Existing provider context: `Tasowheel Oy`.
- Existing offering context: `Precision gears`.
- Editable processes.
- Editable outside diameter max.
- Editable module max.
- Editable material grades.
- Editable certifications.
- Preview update.
- Save update for demo.
- Payload preview.
- Result panel.

The default update example includes `gear_cutting` in the process set and raises outside diameter max from the previous demo baseline to `500 mm`.

## 4. Backend demo state strategy

Provider demo state is stored in:

```text
data/demo/provider_demo_state.json
```

The state file uses a readable JSON structure:

```json
{
  "providers": {},
  "updates": {},
  "last_updated": "..."
}
```

`register_provider` saves normalized provider payloads under `providers`. `update_existing_provider` saves normalized update payloads under `updates`.

No database models, migrations, curated YAML files, RDF/Turtle files, generated data files, or Fuseki datasets are updated by this flow.

## 5. Endpoints implemented

Implemented demo-only endpoints:

```http
POST /api/demo/provider-publication/preview
POST /api/demo/provider-publication/simulate-update
```

Preview behavior:

- Accepts registration/update JSON payloads.
- Validates required fields.
- Validates controlled vocabulary values where available.
- Rejects route/operation fields.
- Returns a normalized preview.
- Returns warnings for unknown optional capability fields.
- Does not save state.
- Returns `200` for valid preview.
- Returns `400` for invalid payload.

Simulate update behavior:

- Accepts the same payload shape.
- Runs the same validation.
- Saves normalized demo state to `data/demo/provider_demo_state.json`.
- Returns a saved provider/offering summary.
- Does not affect curated data, generated data, Fuseki, or consumer search.

The shared provider-publication routes remain out of scope.

## 6. Frontend pages/components changed

Changed frontend files:

- `subsystem/frontend/src/components/mdc/ProviderDemoPanel.js`
- `subsystem/frontend/src/components/mdc/providerPayloadBuilder.js`
- `subsystem/frontend/src/components/mdc/ProviderActionResult.js`

The existing `/demo/provider` page uses the updated provider panel component.

## 7. Backend files changed

Changed or created backend files:

- `backend/apps/demo/provider_demo_services.py`
- `backend/apps/demo/views/post_views.py`
- `backend/tests/test_demo_api_foundation.py`
- `backend/tests/test_demo_provider_publication.py`

## 8. Fields supported

Payload support includes:

- `action`
- `provider_id`
- `provider_name`
- `country`
- `certifications`
- `publication_metadata`
- `offerings`
- `offering_id`
- `offering_name`
- `service_category`
- `part_family`
- `supported_part_types`
- `capabilities`
- `materials`
- `available_grades`
- `processes`
- `module_min`
- `module_max`
- `diameter_min_mm`
- `diameter_max_mm`

Supported actions:

- `register_provider`
- `update_existing_provider`

## 9. Fields intentionally excluded

Excluded by design:

- Production onboarding fields.
- Login/user management fields.
- Route fields.
- Operation fields.
- File upload fields.
- XML upload fields.
- Curated YAML publication fields.
- RDF/Fuseki control fields.
- Consumer search overlay fields.

## 10. Safety confirmation

This phase did not intentionally modify:

- Curated provider YAML.
- RDF/Turtle files.
- Fuseki dataset or reload flow.
- Search backend logic.
- Consumer search frontend pages/components.
- Persistence models.
- Migrations.
- Shared provider-publication validate/publish endpoints.

The backend worktree already contains unrelated modified/deleted curated and generated files from outside this phase. Those were not edited as part of F5_C.

## 11. Tests and results

Backend focused tests:

```powershell
python manage.py test tests.test_demo_api_foundation tests.test_demo_provider_publication -v 2
```

Result: failed before test discovery because Django is not installed or the backend virtual environment is not active in this shell:

```text
ModuleNotFoundError: No module named 'django'
ImportError: Couldn't import Django.
```

Backend syntax check:

```powershell
python -c "import ast, pathlib; files=['backend/apps/demo/provider_demo_services.py','backend/apps/demo/views/post_views.py','backend/tests/test_demo_provider_publication.py','backend/tests/test_demo_api_foundation.py']; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8')) for f in files]; print('AST parse OK')"
```

Result: passed.

Frontend lint:

```powershell
npm run lint
```

Result: passed with existing warnings in layout/document files unrelated to F5_C.

Frontend build:

```powershell
npm run build
```

Result:

- Sandbox run failed with `spawn EPERM`.
- Escalated run compiled successfully.
- Build then failed during page-data collection because `/workspace/designer` is referenced but its page module is missing:

```text
PageNotFoundError: Cannot find module for page: /workspace/designer
Error: Failed to collect page data for /workspace/designer
```

This failure is unrelated to the provider demo files changed in F5_C.

## 12. Manual verification

Manual browser verification was not performed in this pass.

Recommended manual flow:

1. Login as Admin or Provider.
2. Open `/demo/provider`.
3. Open `Register New Provider`.
4. Click `Load sample provider`.
5. Click `Preview`.
6. Confirm preview success.
7. Click `Register for demo`.
8. Confirm success message and state file creation/update.
9. Open `Update Existing Provider`.
10. Confirm Tasowheel precision gears context.
11. Add `gear_cutting` or change diameter/module/grades/certifications.
12. Click `Preview update`.
13. Click `Save update for demo`.
14. Confirm no `[object Object]` appears in the main UI.

## 13. Remaining limitations before Monday demo

- Backend tests need the Django environment or virtual environment activated.
- Frontend production build is blocked by the pre-existing missing `/workspace/designer` page module.
- Manual browser verification still needs to be performed.
- Consumer search reflection is intentionally deferred to F7.
