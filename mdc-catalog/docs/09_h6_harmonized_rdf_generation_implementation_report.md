# MaaSAI MDC — H6 Harmonized RDF Generation Implementation Report

## 1. Status and scope

Phase: H6.

Purpose: parallel harmonized ontology mappings and RDF generation.

Source data is only the parallel harmonized YAML under:

```text
data/curated/service_discovery/providers/
```

Legacy RDF generation remains unchanged. Fuseki loading and SPARQL are not activated in H6. The active API endpoint remains unchanged.

## 2. Verified prerequisite tests

Focused amended H1 + H2 + H3 + H4 + H5 verification:

```text
Ran 148 tests in 0.971s

OK
```

Accepted Tasowheel shaft baseline:

```text
tasowheel_precision_shafts.family_capabilities.length_mm.max = 500
```

No claim is made that the full legacy project test suite passes.

## 3. Existing RDF path inspected

Inspected legacy RDF files:

- `backend/apps/ontology/rdf_mappings.py`
- `backend/apps/ontology/rdf_generator.py`
- `backend/apps/ontology/management/commands/generate_catalog_rdf.py`
- `data/generated/mdc_catalog.ttl`

The legacy generator uses the existing MDC namespace:

```text
https://maasai-project.eu/ontology/mdc#
```

It also uses existing identity predicates such as `mdc:MaaSProvider`, `mdc:ProviderOffering`, `mdc:providerId`, `mdc:offeringId`, `mdc:displayName`, `mdc:offeredBy`, and `mdc:supportsPartFamily`.

The current ontology/SHACL files under `ontologies/` are zero-byte placeholders:

- `ontologies/mdc_core.ttl`
- `ontologies/mdc_mappings.ttl`
- `ontologies/mdc_tasowheel_profile.ttl`
- `ontologies/shacl/mdc_v1_shapes.ttl`

None of the legacy RDF, ontology, SHACL, SPARQL, Fuseki, settings, API, matcher, or provider YAML files were modified.

## 4. New parallel RDF path

H6 introduces this inactive parallel path:

```text
data/curated/service_discovery/providers/
-> backend/apps/ontology/service_discovery_rdf_generator.py
-> data/generated/service_discovery/mdc_service_discovery_catalog.ttl
```

The generated output file is created only when the repository owner runs the management command after focused testing. Codex did not manually create the generated Turtle output file.

## 5. RDF graph contract

Provider resources are emitted as `mdc:MaaSProvider` with provider ID and display name.

Offering resources are emitted as `mdc:ProviderOffering` with:

- `mdc:offeredBy`;
- `mdc:offeringId`;
- `mdc:displayName`;
- `mdc:serviceCategory`;
- `mdc:supportsPartFamily`;
- `mdc:supportStatus`.

Service-category, part-family, part-type, capability-field, material, process, and certification values are resolved through deterministic controlled mappings. Unknown/unmapped identifiers raise generation errors instead of producing uncontrolled RDF URIs.

Part-type support is represented through explicit `mdc:PartTypeSupportEvidence` nodes connected by `mdc:hasPartTypeSupport`. Candidate support remains candidate; it is not promoted to confirmed.

Family, part-type, and generic capabilities are represented as `mdc:CapabilityEvidence` nodes connected by:

- `mdc:hasFamilyCapability`;
- `mdc:hasPartTypeCapability`;
- `mdc:hasGenericCapability`.

Capability evidence preserves typed numeric, boolean and text properties where present:

- `mdc:minValue`;
- `mdc:maxValue`;
- `mdc:exactValue`;
- `mdc:rawValue`;
- `mdc:unit`;
- `mdc:qualifier`;
- `mdc:approximate`;
- `mdc:qualityStandard`;
- `mdc:bestClass`;
- `mdc:comparisonRule`;
- `mdc:sourceType`;
- `mdc:confidence`;
- `mdc:sourceNote`.

Composite dimensions such as `bounding_box_mm` use component evidence nodes linked by `mdc:hasComponent`.

Material evidence is emitted through `mdc:MaterialEvidence` nodes. Named grades are emitted as `mdc:availableGrade` literals only. No `mdc:supportsMaterialGrade` consumer-search-style predicate is emitted.

Process evidence is emitted through `mdc:ProcessEvidence` nodes using only harmonized offering evidence. No route, route-step, machine-order, operation-sequence, pricing or capacity-calendar RDF is emitted.

Certification evidence is emitted through provider-level `mdc:CertificationEvidence` nodes and is not duplicated onto offerings unless future YAML explicitly represents offering-level certification evidence.

Explicit unknown records such as `source_type: not_confirmed` and `confidence: unknown` are emitted with provenance/confidence but without fabricated numeric values. Absent records are not materialised as unsupported or unknown RDF assertions.

Forbidden route, machine, process-sequence, price and capacity fields are rejected recursively.

## 6. Tasowheel graph outcome

Tasowheel RDF contains exactly two harmonized offerings:

- `tasowheel_precision_gears`
- `tasowheel_precision_shafts`

It does not contain:

- `tasowheel_gears_shafts_precision`
- `tasowheel_precision_metal_parts`

Confirmed gear part-type support evidence is emitted only for:

- `spur_gear`
- `helical_gear`
- `bevel_gear`
- `worm_gear`

No confirmed support is emitted for `crown_gear` or `internal_gear`.

Confirmed shaft part-type support evidence is emitted only for:

- `splined_shaft`
- `plain_shaft`
- `hollow_shaft`

No confirmed support is emitted for `stepped_shaft` or `worm_shaft`.

Tasowheel gear family capability evidence includes:

- `module`: `0.3` to `10`;
- `diametral_pitch`: `2.5` to `85`, with raw `DP 85-2.5`;
- `outside_diameter_mm`: `10` to `450`;
- `gear_quality`: DIN, best class `4`, lower-or-equal-is-better comparison.

Tasowheel gear RDF does not fabricate:

- gear-family `outer_diameter_mm`;
- confirmed `tolerance_mm` derived from DIN4;
- confirmed `face_width_mm`.

Tasowheel shaft family capability evidence includes:

- `length_mm.max = 500`, with YAML provenance `source_type: public_web` and `confidence: publicly_confirmed`;
- `outer_diameter_mm`: `10` to `450`.

Tasowheel shaft part-type capability evidence includes:

- `splined_shaft.spline_module`: `0.3` to `10`.

Tasowheel shaft RDF does not emit:

- shaft-family `module`;
- shaft-family `diametral_pitch`;
- shaft-family `gear_quality`;
- shaft `tolerance_mm` derived from DIN4;
- `spline_diametral_pitch`;
- `shaft_quality`;
- `spline_quality`.

Both Tasowheel offerings carry generic evidence for:

- `alloyed_carburizing_steel`, with named grades as evidence literals;
- approved scoped processes;
- `batch_size`: `100` to `2000` pcs;
- `lead_time_weeks`: `8` to `12`;
- `weight_kg.max`: approximately `200`.

Tasowheel provider-level certification evidence is emitted for:

- `ISO9001_2015`;
- `ISO_TS_16949_partial`;
- `APQP`;
- `ISO14001_2015`.

## 7. Other provider evidence handling

H6 generates RDF for every harmonized YAML file present in:

```text
data/curated/service_discovery/providers/
```

For Precipart, public-source provenance is preserved. Candidate `crown_gear` evidence remains `candidate_requiring_confirmation` and is not promoted to confirmed support.

For demo provider records, only evidence represented in harmonized YAML is generated. No additional service categories, part types or capability values are inferred.

## 8. Files created and modified

Created H6 implementation files:

- `backend/apps/ontology/service_discovery_rdf_mappings.py`
- `backend/apps/ontology/service_discovery_rdf_generator.py`
- `backend/apps/ontology/management/commands/generate_service_discovery_rdf.py`

Created H6 test files:

- `backend/tests/test_service_discovery_rdf_mappings.py`
- `backend/tests/test_service_discovery_rdf_generator.py`
- `backend/tests/test_generate_service_discovery_rdf_command.py`

Created H6 report:

- `docs/09_h6_harmonized_rdf_generation_implementation_report.md`

No existing implementation module was modified. No harmonized or legacy YAML was modified. No existing generated legacy Turtle was modified. No ontology, SPARQL, Fuseki, settings, API or matcher file was modified.

## 9. Tests created

`backend/tests/test_service_discovery_rdf_mappings.py` covers controlled concept mappings, deterministic resource helpers and unknown identifier rejection.

`backend/tests/test_service_discovery_rdf_generator.py` covers:

- harmonized data-source isolation;
- provider/offering identity;
- service category and family triples;
- Tasowheel part-type evidence scope;
- Precipart candidate/public evidence preservation;
- gear and shaft capability evidence;
- material, process and certification evidence;
- composite capability components;
- explicit unknown capability records;
- forbidden-field rejection;
- unmapped capability rejection.

`backend/tests/test_generate_service_discovery_rdf_command.py` covers:

- temporary `--output` path support;
- parseable Turtle output;
- harmonized Tasowheel offering IDs;
- absence of the legacy bundled offering ID;
- command output message with path, triple count and harmonized data statement;
- no overwrite of the legacy generated path in the temporary-output test;
- no Fuseki loading.

## 10. Runtime verification responsibility

The repository owner will run focused amended H1 + H2 + H3 + H4 + H5 + H6 tests in the activated Django-enabled `.venv`. The full legacy test suite is not required at this H-phase checkpoint.

## 11. Focused H1-H6 verification command

```powershell
python manage.py test tests.test_service_discovery_registry tests.test_api_v1 tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_service_discovery_provider_yaml_migration tests.test_service_discovery_search_serializer tests.test_service_discovery_search_normalizer tests.test_service_discovery_search_response_contract tests.test_service_discovery_provider_loader tests.test_service_discovery_local_matcher tests.test_service_discovery_local_search_response tests.test_service_discovery_rdf_mappings tests.test_service_discovery_rdf_generator tests.test_generate_service_discovery_rdf_command -v 2
```

## 12. Repository-owner generation command after focused tests pass

```powershell
python manage.py generate_service_discovery_rdf
```

Expected output target:

```text
data/generated/service_discovery/mdc_service_discovery_catalog.ttl
```

H6 is not accepted until the repository owner reports:

- focused tests passed;
- the generation command completed successfully;
- the new harmonized Turtle file was created.

## 13. Required H7 considerations

1. SPARQL must query only the new harmonized RDF graph/dataset path when validating H7; it must not mix legacy bundled offering data with the harmonized graph.

2. H7 queries must distinguish confirmed part-type support from `candidate_requiring_confirmation` and absence/unknown evidence.

3. H7 query projection must retain provenance/confidence for material, process, certification and capability evidence.

4. Available material grades may be returned as evidence but must not become harmonized consumer search criteria.

5. Shaft DP and shaft quality remain deferred and must not be introduced through SPARQL templates without an approved schema change.

6. API/Fuseki activation remains a later decision; H7 retrieval testing must remain parallel until H9 migration comparison.

## 14. Issues before H7

The current ontology and SHACL files are placeholders. A future ontology/SHACL formalization should align them with the H6 evidence-node model.

The legacy RDF generator uses flatter direct predicates such as process/material support. The new harmonized RDF path intentionally uses evidence nodes to preserve scope and provenance.

Generated Turtle is pending repository-owner command execution.

Focused H1-H6 runtime verification is pending repository-owner execution.

## Repository-owner H6 completion confirmation before H7

The repository owner confirmed that the focused H1-H6 verification command passed and that the harmonized RDF generation command completed successfully.

The repository owner also confirmed that the expected harmonized Turtle file was generated:

```text
data/generated/service_discovery/mdc_service_discovery_catalog.ttl
```

The exact focused-test count, elapsed time and terminal generation output were not supplied in this H7 implementation task and are therefore not recorded here.

No claim is made that the full legacy project test suite passes at this checkpoint.

## 15. Completion checklist

- [x] H5 focused verification baseline recorded.
- [x] New harmonized RDF mapping module exists.
- [x] New harmonized RDF generator exists.
- [x] New harmonized RDF management command exists.
- [x] Generator reads only harmonized provider YAML.
- [x] Legacy RDF generator/output remains unchanged.
- [x] Provider/offering identity triples implemented.
- [x] Part-type support evidence scope preserved.
- [x] Family/part-type/generic capability scope preserved.
- [x] Tasowheel corrected shaft evidence represented safely.
- [x] Tasowheel process evidence represented only from amended harmonized YAML.
- [x] Material grades represented as evidence only.
- [x] Precipart candidate/public provenance preserved where applicable.
- [x] Forbidden route/machine/price RDF rejected.
- [x] H6 focused tests exist.
- [x] Repository owner ran focused H1-H6 verification.
- [x] Repository owner generated harmonized Turtle output.
- [x] Ready for H7 review.
