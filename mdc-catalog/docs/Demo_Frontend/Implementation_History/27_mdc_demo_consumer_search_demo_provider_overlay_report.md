# F7 Consumer Search Demo Provider Overlay Report

## 1. Purpose and scope

This frontend-only change lets Consumer Search display matching providers that were registered through the demo provider workflow.

The overlay is display-only. It does not publish provider data into RDF/Fuseki, curated YAML, generated data, or the real service-discovery catalogue.

## 2. Demo overlay design

Consumer Search still executes the real backend search first through `POST /api/service-discovery/search`.

After that search completes, the frontend loads demo provider state and appends matching demo registered providers to the displayed result panels. Demo overlay results are clearly marked with `Demo registered provider` and `Source: Demo registered provider`.

## 3. How demo provider state is loaded

`ConsumerSearchMockup.js` imports and calls the existing service helper:

```javascript
getProviderDemoState()
```

This uses the existing demo endpoint:

```text
GET /api/demo/provider-publication/state
```

The service module was not modified.

## 4. How registered providers are matched to search payload

Matching is intentionally simple and conservative for the demo.

The overlay first checks controlled fields when available:

- `service_category`
- `part_family`
- `supported_part_types`

A provider offering can match when its controlled service category, part family, or supported part type matches the current search payload.

If controlled fields are absent, the overlay inspects:

- custom offering fields
- custom capability fields
- offering name
- provider name
- description

Text matching is case-insensitive. To avoid unrelated matches, material/process/certification terms are only used as supporting evidence after a part-family, service-category, part-type, or Metal part domain term has matched.

## 5. How demo results are converted into panels

Matching registered providers are converted into result objects compatible with the existing `ProviderResultAccordion`.

Each demo result includes:

- provider name and ID
- offering name and ID
- match status
- matched demo fields
- materials/processes/certifications when available
- provider summary
- demo offering fields
- demo capability fields
- source tag

The main UI does not show raw demo state JSON or `[object Object]`.

## 6. How backend and demo results are merged

The final displayed result list is:

```text
backend search results + matching demo registered providers
```

The backend response object is not used to alter backend search logic. It is augmented only for frontend display with merged `results` and `demo_overlay` metadata.

## 7. Duplicate prevention

The overlay collects provider IDs from backend results. If a registered demo provider has the same provider ID as a backend result, the demo overlay result is not appended.

This prevents duplicate provider panels when the same provider appears in the real catalogue and demo state.

## 8. Empty-state behaviour

If backend and demo results are both empty, the existing empty-state message remains:

```text
No providers found for this request. Try changing part type, material, process or optional requirements.
```

If backend results are empty but demo overlay results exist, Consumer Search shows:

```text
No catalogue providers found, but demo registered providers match this request.
```

Then it renders the demo provider panels.

## 9. Error handling if demo state is unavailable

If the demo state endpoint fails, Consumer Search does not crash.

The UI keeps backend search results and shows a non-blocking warning:

```text
Demo registered providers could not be loaded.
```

## 10. Files modified

- `subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `subsystem/frontend/src/components/mdc/SearchResultsList.js`
- `subsystem/frontend/src/components/mdc/ProviderResultAccordion.js`
- `docs/27_mdc_demo_consumer_search_demo_provider_overlay_report.md`

## 11. Commands run

- `Get-Content -Path C:\Users\Elahi\.codex\attachments\410a91af-2015-4899-a454-31bba84063c5\pasted-text.txt`
- `Get-Content -Path subsystem/frontend/src/pages/demo/consumer-search.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/SearchResultsList.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/SearchResultCard.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/ProviderResultAccordion.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/searchResultFormatters.js`
- `Get-Content -Path subsystem/frontend/src/services/mdc/search.service.js`
- `Get-Content -Path subsystem/frontend/src/services/mdc/demoAdmin.service.js`
- `Get-Content -Path subsystem/frontend/src/components/mdc/mockData.js`
- `rg -n "getProviderDemoState|provider-publication/state|state.providers" subsystem/frontend/src`
- `rg -n "demo_overlay|getProviderDemoState|buildDemoOverlayResults|demoProviderWarning|Demo registered provider" subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js subsystem/frontend/src/components/mdc/SearchResultsList.js subsystem/frontend/src/components/mdc/ProviderResultAccordion.js`
- `git status --short subsystem/frontend/src/components/mdc/ConsumerSearchMockup.js subsystem/frontend/src/components/mdc/SearchResultsList.js subsystem/frontend/src/components/mdc/ProviderResultAccordion.js docs/27_mdc_demo_consumer_search_demo_provider_overlay_report.md`
- `npm run lint` from `subsystem/frontend`

## 12. Manual verification notes

Recommended browser checks while backend and frontend are running:

1. Register a demo Metal part provider from `/demo/provider`.
2. Open `/demo/consumer-search`.
3. Search for `Part family = Metal part` and `Part type = Block`.
4. Confirm backend catalogue results still render when present.
5. Confirm a matching registered provider appears as a `Demo registered provider` panel when backend catalogue results are empty.
6. Expand the panel and confirm provider summary, offering, custom offering fields, custom capability fields, materials/processes/certifications, and source are readable.
7. Confirm Gear and Shaft searches do not show unrelated Metal part demo providers.
8. Stop or block the demo state endpoint and confirm backend results still display without crashing.

## 13. Remaining limitations

This is a demo overlay. It does not publish provider data into RDF/Fuseki or the real search catalogue.

Matching is intentionally simple text/control-field matching for the Monday demo. It is not a replacement for real semantic matching, H5 evidence scoring, RDF publication, or Fuseki reload.
