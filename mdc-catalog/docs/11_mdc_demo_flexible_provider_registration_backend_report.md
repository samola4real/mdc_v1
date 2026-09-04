# MaaSAI MDC - Flexible Provider Registration Backend Report

## 1. Purpose and scope

This implements F5_C2 Backend for the temporary demo provider-publication
endpoints:

```text
POST /api/demo/provider-publication/preview
POST /api/demo/provider-publication/simulate-update
```

The change is limited to flexible demo registration validation and demo state
preservation.

## 2. Original validation problem

The register-new-provider demo flow could reject free-text provider business
terms such as `precision_manufacturing` because the demo input was treated as
if it were already a controlled MDC ontology field.

## 3. Backend validation changes

`register_provider` now accepts flexible provider-entered business information
as staging data. It no longer requires controlled `service_category`,
`part_family`, or `supported_part_types`.

`update_existing_provider` keeps the existing controlled validation behavior.

## 4. Custom offering fields support

`custom_offering_fields` is accepted as a list of objects. Each object requires:

```text
name
value
```

`unit` and `notes` are preserved if supplied.

## 5. Custom capability fields support

`capabilities.custom_capability_fields` is accepted as a list of objects. Each
object requires:

```text
name
value
```

`unit` and `notes` are optional and preserved.

## 6. Handling of invalid controlled service_category in register_provider

For `register_provider`, invalid controlled offering values such as
`service_category = precision_manufacturing` are moved into
`custom_offering_fields` when safe, and a warning is returned. Valid controlled
values are preserved.

## 7. Demo state preservation

`simulate-update` saves normalized demo state to:

```text
data/demo/provider_demo_state.json
```

It preserves `custom_offering_fields` and
`capabilities.custom_capability_fields`.

## 8. Files modified

```text
backend/apps/demo/provider_demo_services.py
backend/tests/test_demo_provider_publication.py
docs/11_mdc_demo_flexible_provider_registration_backend_report.md
```

## 9. Tests and results

Focused verification command:

```text
..\..\.venv\Scripts\python.exe manage.py test tests.test_demo_provider_publication tests.test_demo_api_foundation -v 2
```

Result:

```text
Ran 23 tests in 0.093s
OK
```

## 10. Safety confirmation

This change did not modify frontend files, shared API endpoints, search backend
logic, curated YAML, generated RDF/Turtle, Fuseki configuration or dataset,
Docker, requirements, persistence models, or migrations.

Route and operation fields remain rejected by key and by custom field name.

## 11. Remaining limitations

Flexible registration stores demo staging information only. It does not publish
provider data to the Marketplace contract, regenerate RDF, reload Fuseki, or
make custom fields searchable through the shared service-discovery endpoint.
