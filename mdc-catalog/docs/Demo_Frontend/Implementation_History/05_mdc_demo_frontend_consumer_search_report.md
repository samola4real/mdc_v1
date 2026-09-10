# MaaSAI MDC Demo Frontend - F4 Consumer Search Integration Report

## 1. Purpose and scope

F4 connected the MDC Demo Console consumer search page to the existing F2 search service.

Only `/demo/consumer-search` was integrated. Provider publication, admin/demo mutation actions, catalog loading, RDF regeneration, Fuseki reload, and direct Fuseki access remain disconnected.

## 2. Endpoint connected

Connected only:

```text
POST /api/service-discovery/search
```

The page calls:

```javascript
searchServiceDiscovery(payload)
```

from:

```text
subsystem/frontend/src/services/mdc/search.service.js
```

No service module was modified in F4.

## 3. Search form fields

The consumer search form includes:

- Consumer ID
- Request ID
- Service category
- Part family
- Part type
- Material
- Processes
- Certification
- Technical requirements
- Gear-specific fields:
  - module
  - diametral pitch
  - outside diameter mm
  - gear quality
  - face width mm
  - tolerance mm
- Shaft-specific fields:
  - length mm
  - outer diameter mm
  - spline module
  - internal diameter mm
  - wall thickness mm
  - tolerance mm

Default values are demo-friendly and include:

```text
consumer_id: consumer_demo_001
service_category: precision_gears
part_family: gear
part_type: spur_gear
material: alloyed_carburizing_steel
processes: hobbing, turn_mill
certification: ISO9001_2015
module: 2.0
outside_diameter_mm: 100
```

## 4. Request payload structure

F4 builds the search payload in one isolated helper:

```javascript
buildSearchPayload(form)
```

Implemented high-level shape:

```javascript
{
    request_id,
    consumer_id,
    selection: {
        service_category,
        part_family,
        part_type
    },
    requirements: {
        part_family_specifications: {
            material,
            processes,
            certification
        },
        part_type_specifications: {
            // gear or shaft technical fields
        },
        generic_requirements: {
            technical_requirements
        }
    },
    match_policy: {
        unknown_policy: 'keep_as_unknown',
        optional_match_mode: 'score_only'
    }
}
```

The page includes a collapsible `Request payload preview` panel showing the exact JSON submitted.

## 5. Result rendering approach

Created result helpers:

```text
subsystem/frontend/src/components/mdc/SearchResultsList.js
subsystem/frontend/src/components/mdc/SearchResultCard.js
subsystem/frontend/src/components/mdc/SearchErrorMessage.js
subsystem/frontend/src/components/mdc/SearchPayloadPreview.js
```

Result rendering supports response arrays from:

```javascript
response.results
response.data.results
response
```

Each result card displays:

- Provider name
- Provider ID
- Offering name
- Offering ID
- Part type support status
- Match/suitability status
- Materials
- Available grades
- Processes
- Certifications
- Matched evidence
- Unknown evidence
- Warnings

Missing optional fields render as `Not provided`.

Scores are hidden by default and only shown in `Advanced/debug` details if present.

## 6. Loading/error/empty-result behaviour

Submit behavior:

- Clears previous error and response.
- Sets loading state.
- Calls `searchServiceDiscovery(payload)`.
- Keeps form values visible.
- Shows results on success.
- Shows friendly errors on failure.
- Does not navigate away.

Loading behavior:

- `Search MDC` button shows `Searching MDC...`.
- Button is disabled while the request is active.
- An inline info message is shown during search.

Empty result behavior:

```text
No providers found for this request. Try changing part type, material, process or optional requirements.
```

Error behavior:

- 404:

```text
The service-discovery search endpoint is not available yet. Check whether the backend search endpoint has been activated.
```

- Network error:

```text
Cannot reach MDC backend at the configured API URL. Check that Django is running at http://localhost:8000.
```

- 400:

```text
The search request was rejected by the backend. Please check the selected part type and requirement fields.
```

Backend details are shown in a collapsible debug panel when available.

## 7. Files modified/created

Created:

```text
docs/05_mdc_demo_frontend_consumer_search_report.md
subsystem/frontend/src/components/mdc/SearchErrorMessage.js
subsystem/frontend/src/components/mdc/SearchPayloadPreview.js
subsystem/frontend/src/components/mdc/SearchResultCard.js
subsystem/frontend/src/components/mdc/SearchResultsList.js
```

Modified:

```text
subsystem/frontend/src/pages/demo/consumer-search.js
subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js
subsystem/frontend/src/components/mdc/EvidenceList.js
subsystem/frontend/src/components/mdc/StatusTag.js
subsystem/frontend/src/components/mdc/mockData.js
```

## 8. Safety boundary confirmation

Confirmed:

- No provider publication endpoints were connected.
- No admin demo mutation endpoints were connected.
- No RDF regeneration endpoint was connected.
- No Fuseki reload endpoint was connected.
- No Fuseki smoke-test endpoint was connected.
- No catalog filters endpoint was connected.
- No browser code calls Fuseki directly.
- No route/menu/auth changes were made.
- No `.env`, package, or backend changes were made.
- No F2 service files were modified.

## 9. Commands run and results

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

The `/demo/consumer-search` route built successfully.

Build also reported the existing lint warnings above and:

```text
Browserslist: caniuse-lite is outdated.
```

No package update was performed.

## 10. Browser/manual verification result

Browser verification was not performed in this run.

Direct backend endpoint check from PowerShell:

```text
POST http://localhost:8000/api/service-discovery/search -> 404
```

This means the F4 page should show the configured `search endpoint is not available yet` error state until the backend search endpoint is activated.

## 11. Known assumptions about backend payload/response shape

Payload assumption:

- The frontend uses the high-level harmonized search shape documented in the F4 task brief.
- The exact backend contract should be confirmed once the search endpoint is active.
- Payload construction is isolated in `buildSearchPayload(form)` so adjustments can be made in one place.

Response assumptions:

- Result arrays may appear in `response.results`, `response.data.results`, or as a direct array.
- Result cards tolerate missing provider/offering/evidence/score fields.
- Score is not shown as a primary result field and appears only in advanced/debug details.

## 12. Recommended next phase: F5 Provider demo integration

Recommended F5 scope:

- Connect provider preview to `POST /api/demo/provider-publication/preview`.
- Keep provider simulate-update isolated under demo-only endpoint handling.
- Add loading, validation error, and preview result states.
- Continue avoiding RDF regeneration and Fuseki reload until the admin phase.

## F4_B payload contract alignment

The backend search endpoint became active and returned a clean `400` for the previous F4 payload:

```text
request contains unknown fields: ['selection']
```

The backend serializer/tests were inspected at:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\backend\apps\api\service_discovery_search_serializers.py
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\backend\tests\test_service_discovery_search_serializer.py
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\backend\tests\test_service_discovery_search_endpoint.py
```

The frontend payload was changed from the previous nested shape:

```javascript
{
    request_id,
    consumer_id,
    selection: {
        service_category,
        part_family,
        part_type
    },
    requirements: {
        part_family_specifications,
        part_type_specifications,
        generic_requirements
    },
    match_policy
}
```

to the backend-accepted shape:

```javascript
{
    request_id,
    consumer_id,
    service_category,
    part_family,
    part_type,
    requirements: {
        part_family_specifications: {
            module: { exact },
            diametral_pitch: { min, max },
            outside_diameter_mm: { max },
            gear_quality: { standard, max_class },
            tolerance_mm: { max }
        },
        part_type_specifications: {
            face_width_mm: { exact }
        },
        generic_requirements: {
            materials: [...],
            processes: [...],
            certifications: [...]
        }
    },
    match_policy: {
        unknown_policy: 'keep_as_unknown',
        optional_match_mode: 'score_only',
        minimum_score: null
    }
}
```

Selection values are now top-level fields. The frontend no longer sends a top-level `selection` wrapper. The request payload preview panel shows the corrected payload because it renders the same `buildSearchPayload(form)` output submitted to `searchServiceDiscovery(payload)`.

Files modified for F4_B:

```text
subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js
subsystem/frontend/src/components/mdc/mockData.js
docs/05_mdc_demo_frontend_consumer_search_report.md
```

Commands run:

```text
npm run lint
```

Result: succeeded with the same existing unrelated warnings in `AppMenuitem.js`, `layout.js`, and `_document.js`.

```text
npm run build
```

First sandboxed run failed with the known worker-process error:

```text
Error: spawn EPERM
```

The approved rerun succeeded:

```text
Compiled successfully
Generated static pages: 22/22
```

Manual backend endpoint result:

```text
POST http://localhost:8000/api/service-discovery/search -> 200
```

The response returned `result_count: 2` and `status.search_executed: true`. No remaining backend validation error was observed for the corrected default gear payload.

## F4_C provider-panel result display

Previous UI problem:

```text
[object Object] values appeared in the visible result UI, and the result card exposed too much raw backend JSON.
```

The result display was refactored into a consumer-facing provider accordion model:

```text
SearchResultsList
  -> ProviderResultAccordion
      -> closed provider AccordionTab
      -> Provider summary
      -> Why this provider is suitable table
      -> Provider manufacturing capability
      -> Material tags
      -> Process tags
      -> Certification tags
      -> Not confirmed / ask provider
      -> Demo action buttons
      -> Advanced/debug response JSON
```

Provider results now appear under:

```text
Suitable providers found
```

Each provider is one closed `AccordionTab` with a simple header:

```text
Provider name
Offering name | Part type supported
Suitability tag
```

Main UI wording now uses consumer-friendly labels such as:

```text
Suitable
Candidate
Evidence incomplete
Confirmed
Not confirmed
Matched
```

Raw backend terms such as `partial_match`, `score`, `search_engine`, and full response JSON are not shown in the main result UI. Score and raw JSON are available only inside the collapsed `Advanced/debug response JSON` panel.

Formatter/helper added:

```text
subsystem/frontend/src/components/mdc/searchResultFormatters.js
```

Formatter responsibilities:

- Convert snake_case field names to readable labels.
- Map known field codes such as `module`, `outside_diameter_mm`, `gear_quality`, and `face_width_mm`.
- Map certification codes such as `ISO9001_2015` to `ISO 9001:2015`.
- Format range/exact objects such as `{ exact }`, `{ min, max }`, `{ max }`, and quality objects.
- Format arrays and nested objects as readable compact text.
- Prevent `[object Object]` from appearing in visible UI.

Files created for F4_C:

```text
subsystem/frontend/src/components/mdc/searchResultFormatters.js
subsystem/frontend/src/components/mdc/ProviderResultAccordion.js
```

Files modified for F4_C:

```text
subsystem/frontend/src/components/mdc/SearchResultsList.js
subsystem/frontend/src/components/mdc/SearchResultCard.js
docs/05_mdc_demo_frontend_consumer_search_report.md
```

Commands run:

```text
npm run lint
```

First run found and fixed a syntax error in `ProviderResultAccordion.js`. Final result: succeeded with the same existing unrelated warnings in `AppMenuitem.js`, `layout.js`, and `_document.js`.

```text
npm run build
```

First sandboxed run failed with the known worker-process error:

```text
Error: spawn EPERM
```

The approved rerun succeeded:

```text
Compiled successfully
Generated static pages: 22/22
```

Manual browser verification was not performed in this run.

Remaining UI issue before F5:

- The provider panel UI should still be reviewed in-browser with a live search response to confirm spacing and accordion header fit across desktop/mobile.
