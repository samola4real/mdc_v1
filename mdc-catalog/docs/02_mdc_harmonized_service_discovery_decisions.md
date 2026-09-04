# MaaSAI MDC — Harmonized Service Discovery Decisions for M18

## 1. Document status and scope

Status: approved design baseline for H1-H9 implementation planning.

Phase: H0 documentation decision freeze.

Scenario: M18 structured Marketplace service publishing and consumer search.

This document freezes the agreed service-discovery, provider-publication, consumer-search, taxonomy, evidence, and migration decisions before any production code or curated provider YAML is changed. It supersedes earlier one-off Tasowheel modelling decisions only where explicitly stated.

No production code or provider YAML was modified in H0.

This document distinguishes current implemented codebase behaviour, new approved M18 design decisions, future implementation work planned for H1-H9, and provider-specific assertions that are not yet confirmed and must not be invented.

Observed current implementation baseline from `docs/01_mdc_current_codebase_implementation_inventory.md`:

- Implemented API base path is `/api/`, not `/api/v1/`.
- Active search endpoint is `POST /api/catalog/search`.
- Active API search engine is the local seed-data matcher.
- Fuseki exists as a parallel candidate-retrieval path and is not yet active behind the API endpoint.
- Current provider publication requires externally supplied `offering_id`.
- Current consumer search does not yet include `consumer_id` or `request_id`.
- Current Marketplace filters/search expose `material_grades`.
- Current Tasowheel seed model uses one bundled offering: `tasowheel_gears_shafts_precision`.

## 2. Design principles to retain

The following principles remain valid for M18:

- `ProviderOffering` remains the searchable/result entity.
- Input remains structured JSON for M18.
- All search input must be normalized before matching/query generation.
- SPARQL generation remains deterministic and based only on validated controlled inputs.
- Provenance, confidence, and unknown-value handling remain mandatory.
- Unknown evidence must not be converted into unsupported/no-match without explicit logic.
- Route steps, operation sequencing, machine sequencing, pricing, live availability, and quotation logic remain outside M18 search.
- Provider-confirmed evidence has priority over curated interpretation or inference.

## 3. Harmonized service categories

These controlled service categories are approved for harmonized MDC/Marketplace publishing and search:

| service_category value | label | part_family |
| --- | --- | --- |
| `precision_gears` | Precision gears | `gear` |
| `precision_shafts` | Precision shafts | `shaft` |
| `precision_metal_parts` | Precision metal parts | `metal_part` |

These are MDC/Marketplace-facing service categories. A provider may publish only categories it can support with evidence. The existence of a service category in the schema does not mean that every provider supports it.

`offering_id` remains an internal MDC-managed stable identity and is distinct from `service_category`.

## 4. Harmonized part families and part types

The approved controlled part families and part types are:

### `gear`

Part types:

- `spur_gear`
- `helical_gear`
- `bevel_gear`
- `worm_gear`
- `crown_gear`

### `shaft`

Part types:

- `plain_shaft`
- `stepped_shaft`
- `splined_shaft`
- `worm_shaft`
- `hollow_shaft`

### `metal_part`

Part types:

- `block`
- `plate`
- `bracket`
- `bushing`
- `roller`
- `collar`

Naming decisions:

- Use `metal_part`, not `metal parts`.
- Use singular identifiers `bushing`, `roller`, `collar`.
- A family-level capability claim does not automatically prove support for every part type below that family.
- Provider YAML must distinguish confirmed, curated/inferred, candidate-requiring-confirmation, and unknown support where applicable.

## 5. Part-specific specification-field registry decision

H1 will implement an MDC-owned specification registry used by Marketplace dynamic forms and MDC validation.

The registry must distinguish:

- family-common specification fields;
- part-type-specific specification fields;
- generic offering/capability fields.

### 5.1 Gear specification fields

Family-common fields for the currently approved external gear part types:

- `module`
- `diametral_pitch`
- `number_of_teeth`
- `outside_diameter_mm`
- `gear_quality`
- `tolerance_mm`

Terminology and semantic rules:

- `outside_diameter_mm` is the preferred canonical gear field for the tooth-tip/addendum boundary diameter of external gears.
- For spur and helical gears, it represents the external tooth-tip diameter.
- For bevel gears, it represents the outside diameter at the crown/outer end of the gear.
- For `worm_gear`, interpreted in this taxonomy as the worm wheel/gear member, it represents its outside diameter.
- For crown gears, it represents the outer boundary diameter; `inner_diameter_mm` is additionally used to represent the inner boundary.
- `outer_diameter_mm` is reserved for shafts and rotational metal parts rather than gears.
- Future `internal_gear` support must use `inside_diameter_mm` rather than automatically inheriting `outside_diameter_mm`.
- `gear_quality`, such as DIN/ISO/AGMA gear accuracy class, must not be confused with general dimensional `tolerance_mm`.
- Existing Tasowheel `DIN4` evidence is gear-quality evidence and must never be converted into a general ± tolerance value.

Part-type-specific fields:

| part_type | fields |
| --- | --- |
| `spur_gear` | `face_width_mm` |
| `helical_gear` | `face_width_mm`, `helix_angle_deg` |
| `bevel_gear` | `face_width_mm`, `shaft_angle_deg` |
| `worm_gear` | `center_distance_mm`, `shaft_angle_deg` |
| `crown_gear` | `face_width_mm`, `inner_diameter_mm` |

Additional note for `worm_gear`:

- `center_distance_mm` is a mating/interface requirement for a worm-gear pair and must not automatically be interpreted as a standalone manufactured-part dimension.

### 5.2 Shaft specification fields

Family-common fields for `shaft`:

- `length_mm`
- `outer_diameter_mm`
- `tolerance_mm`

Part-type-specific fields:

| part_type | fields |
| --- | --- |
| `plain_shaft` | `principal_diameter_mm` |
| `stepped_shaft` | `number_of_steps` |
| `splined_shaft` | `spline_module`, `spline_length_mm` |
| `worm_shaft` | `worm_module`, `number_of_starts` |
| `hollow_shaft` | `inner_diameter_mm`, `wall_thickness_mm` |

### 5.3 Metal-part specification fields

Two geometry groupings exist inside `metal_part`.

Prismatic geometry part types:

- `block`
- `plate`
- `bracket`

Common field for prismatic metal parts:

- `bounding_box_mm`, composed of:
  - `length_mm`
  - `width_mm`
  - `height_mm`

Specific fields:

| part_type | fields |
| --- | --- |
| `block` | `number_of_holes` |
| `plate` | `number_of_holes` |
| `bracket` | `vertical_flange_length_mm`, `horizontal_flange_length_mm` |

Rotational geometry part types:

- `bushing`
- `roller`
- `collar`

Common fields for rotational metal parts:

- `inner_diameter_mm`
- `outer_diameter_mm`
- `overall_length_mm`
- `tolerance_mm`

Specific fields:

| part_type | fields |
| --- | --- |
| `bushing` | `flange_diameter_mm` |
| `roller` | none confirmed in the present decision |
| `collar` | none confirmed in the present decision |

Clarifications:

- `bounding_box_mm` is a specification structure, not a selectable part type.
- It is intended for prismatic/complex components such as blocks, plates, and brackets.
- Bounding-box matching is not yet implemented in the current codebase and belongs to later implementation phases.

## 6. Generic offering and requirement fields

These generic fields can apply across service categories, subject to provider evidence:

| field | meaning / rule |
| --- | --- |
| `materials` | Consumer-selectable material-family criteria |
| `material_grade_evidence` | Provider/result evidence only for M18; not consumer-selectable search input |
| `processes` | Supported manufacturing processes; delivery mode must distinguish in-house/subcontracted/unspecified where known |
| `batch_size` | Provider range and consumer desired quantity |
| `lead_time_weeks` / consumer `delivery.max_weeks` | Provider range and consumer acceptable maximum |
| `certifications` | Provider or offering evidence; matching policy to remain explicit |
| `surface_finish_ra_um` | Optional and unknown-aware |
| `tolerance_mm` | Optional and unknown-aware; separate from gear-quality class |
| `quality` / `gear_quality` | Standard-specific quality capability; avoid applying gear-quality fields to non-gears |
| `weight_kg` | Optional offering envelope |

## 7. Dynamic Marketplace form behaviour

M18 Marketplace UI decision:

- Consumer selects one `service_category`.
- Consumer selects one `part_family`, consistent with that service category.
- Consumer selects one `part_type`.
- Marketplace displays only:
  - the family-common fields for that selected family;
  - the part-type-specific fields for that selected type;
  - the generic requirements fields.

A flat request allowing multiple unrelated part types creates ambiguity about which technical fields apply to which part. The current backend may temporarily retain older `part_families` support during migration, but the new M18 Marketplace contract is single-part-type-per-request.

Examples:

- Selecting `spur_gear` exposes `module`, `diametral_pitch`, `number_of_teeth`, `outside_diameter_mm`, `gear_quality`, `tolerance_mm`, and `face_width_mm`, plus generic requirements.
- Selecting `hollow_shaft` exposes `length_mm`, `outer_diameter_mm`, `tolerance_mm`, `inner_diameter_mm`, and `wall_thickness_mm`, plus generic requirements.
- Selecting `bracket` exposes `bounding_box_mm.length_mm`, `bounding_box_mm.width_mm`, `bounding_box_mm.height_mm`, `horizontal_flange_length_mm`, and `vertical_flange_length_mm`, plus generic requirements.

## 8. Provider publication contract decision

Future external provider publication shape, conceptually:

Providers publish:

- `provider_id`
- `provider_name`
- `country`
- certifications/evidence where available
- one or more offerings containing:
  - `service_category`
  - `offering_name`
  - `part_family`
  - `supported_part_types`
  - `family_capabilities`
  - `part_type_capabilities`
  - `generic_capabilities`
  - support/evidence/provenance/confidence metadata

ID and naming decisions:

- External API field is `provider_name`.
- Existing internal/RDF property may remain `display_name` / `mdc:displayName`; mapping will be implemented later.
- Marketplace/provider supplies `provider_id`.
- Marketplace/provider does not need to supply `offering_id`.
- MDC generates/manages stable internal `offering_id`.
- Internal `offering_id` must remain in storage, RDF, SPARQL results, and API result/detail responses.

Future contract example only; not implemented H0 code:

```yaml
provider_id: example_provider
provider_name: Example Provider
country: Finland
certifications:
  - code: ISO9001_2015
    source_type: provider_confirmed
    confidence: declared
offerings:
  - service_category: precision_gears
    offering_name: Precision gear manufacturing
    part_family: gear
    supported_part_types:
      - part_type: spur_gear
        support_status: confirmed
        source_type: provider_confirmed
        confidence: declared
      - part_type: crown_gear
        support_status: candidate_requiring_confirmation
        source_type: curated
        confidence: inferred
    family_capabilities:
      module:
        min: 0.5
        max: 8
        source_type: provider_confirmed
        confidence: declared
    part_type_capabilities:
      spur_gear:
        face_width_mm:
          min: 5
          max: 80
          source_type: provider_confirmed
          confidence: declared
    generic_capabilities:
      materials:
        - material: steel
          source_type: provider_confirmed
          confidence: declared
      batch_size:
        min: 10
        max: 1000
        unit: pcs
        source_type: provider_confirmed
        confidence: declared
```

## 9. Tasowheel migration decision

Current confirmed Tasowheel evidence supports:

- broad `gear` family capability;
- broad `shaft` family capability;
- batch size `100-2000 pcs`;
- diameter `10-450 mm`;
- module `0.3-10`;
- diametral pitch raw value `DP 85-2.5`, normalized as `2.5-85`;
- gear quality up to `DIN4`;
- weight up to approximately `200 kg`;
- normal lead time `8-12 weeks`, case dependent;
- alloyed carburizing steel/material-grade evidence;
- stated certifications.

Future harmonized Tasowheel offerings:

- `tasowheel_precision_gears`
- `tasowheel_precision_shafts`

Do not publish for Tasowheel without additional confirmation:

- `tasowheel_precision_metal_parts`
- confirmed support for every listed gear subtype;
- confirmed support for every listed shaft subtype;
- surface-finish values;
- general dimensional tolerance values;
- traceability values beyond current certification evidence;
- in-house heat-treatment claims when the source only supports subcontracted/route context.

Legacy handling:

- Current internal offering `tasowheel_gears_shafts_precision` is a legacy bundled offering.
- H3 will decide and implement migration mapping from the legacy offering to the new narrower offerings.
- H0 must not edit the YAML.

## 10. Precipart and future-provider modelling decision

The harmonized schema is intended to support Tasowheel, Precipart, current demo providers, and future providers.

Providers must publish only offerings and part types supported by evidence. A provider may support all three categories, some categories, or one category. Confirmed capability and candidate/requiring-confirmation capability must remain distinguishable.

H3 will migrate provider YAML after publication schema validation is implemented.

`data/curated/providers/precipart.yaml` was present locally in H0 and was inspected for context. It contains Precipart provider/publication-style data, including provider-level `provider_id: precipart`, `provider_name: Precipart`, European operations, certification strings, supported material-family strings, and three offerings:

- `precipart_precision_gears`, with `part_family: gear`, several listed gear `part_types`, gear dimensional/quality fields, and `candidate_mapping_requiring_confirmation` for `crown_gear: face_gear`.
- `precipart_custom_turned_components`, with `part_family: metal_part`, `geometry_class: rotationally_symmetric`, candidate part types requiring confirmation including `bushing`, `roller`, `collar`, `plain_shaft`, and `stepped_shaft`, plus process-envelope fields.
- `precipart_custom_milled_components`, with `part_family: metal_part`, `geometry_class: prismatic_or_complex`, one confirmed component example, candidate part types requiring confirmation including `block`, `bracket`, and `plate`, plus milling process-envelope fields.

These observations are not yet a validated MDC migration. Do not claim additional Precipart-specific values beyond locally inspected evidence.

## 11. Material and material-grade decision

M18 rule:

- Consumers search using `materials` only.
- `material_grades` must not be presented as consumer-search filters in the new M18 contract.
- Provider publication and internal seed/RDF representation may retain confirmed material-grade evidence.
- Search responses may return material grades nested under material evidence when available.

Conceptual response evidence example:

```json
{
  "materials": [
    {
      "material": "alloyed_carburizing_steel",
      "available_grades": [
        "18CrNiMo7-6",
        "16MnCr5",
        "20MnCr5"
      ],
      "source_type": "provider_confirmed",
      "confidence": "declared"
    }
  ]
}
```

This replaces the older intent to treat material grades as public Marketplace search criteria, while retaining evidence internally.

## 12. Consumer search-request decision

Target M18 consumer request shape, conceptually:

Required metadata:

- `request_id`
- `consumer_id`

Required selected product context:

- `service_category`
- `part_family`
- `part_type`

Requirement groupings:

- `requirements.part_family_specifications`
- `requirements.part_type_specifications`
- `requirements.generic_requirements`

Match policy:

- Retain explicit unknown-handling and optional matching policy concepts.
- Actual final scoring-policy implementation remains a later code decision.

Illustrative `spur_gear` search:

```json
{
  "request_id": "req_2026_000001",
  "consumer_id": "consumer_demo_001",
  "service_category": "precision_gears",
  "part_family": "gear",
  "part_type": "spur_gear",
  "requirements": {
    "part_family_specifications": {
      "module": {"min": 1.0, "max": 5.0},
      "diametral_pitch": {"min": 5, "max": 40},
      "number_of_teeth": {"min": 20, "max": 80},
      "outside_diameter_mm": {"max": 300},
      "gear_quality": {"standard": "DIN", "max_class": 4},
      "tolerance_mm": {"max": 0.02}
    },
    "part_type_specifications": {
      "face_width_mm": {"max": 60}
    },
    "generic_requirements": {
      "materials": ["alloyed_carburizing_steel"],
      "batch_size": 100,
      "delivery": {"max_weeks": 12},
      "certifications": ["ISO9001_2015"]
    }
  },
  "match_policy": {
    "unknown_policy": "keep_as_unknown",
    "optional_match_mode": "any"
  }
}
```

Illustrative `bracket` search:

```json
{
  "request_id": "req_2026_000002",
  "consumer_id": "consumer_demo_001",
  "service_category": "precision_metal_parts",
  "part_family": "metal_part",
  "part_type": "bracket",
  "requirements": {
    "part_family_specifications": {
      "bounding_box_mm": {
        "length_mm": {"max": 160},
        "width_mm": {"max": 80},
        "height_mm": {"max": 70}
      }
    },
    "part_type_specifications": {
      "vertical_flange_length_mm": {"max": 70},
      "horizontal_flange_length_mm": {"max": 120}
    },
    "generic_requirements": {
      "materials": ["steel"],
      "batch_size": 50,
      "delivery": {"max_weeks": 8}
    }
  },
  "match_policy": {
    "unknown_policy": "keep_as_unknown",
    "optional_match_mode": "score_only"
  }
}
```

This target request is not currently implemented. Current code still uses `part_family` / `part_families` plus broad optional fields. Migration/backward-compatibility strategy will be decided during H4.

## 13. Search response and material evidence decision

Target response additions/renames:

- Echo `request_id`.
- Echo `consumer_id`.
- Provider object exposes `provider_name` externally.
- Offering object exposes internal `offering_id`, `service_category`, `offering_name`, and `part_family`.

The target response preserves:

- `match`
- `matched_attributes`
- `unmatched_attributes`
- `unknown_attributes`
- `evidence`

Material grade values may appear only as nested material evidence, not as consumer-request matches for M18.

Existing response output currently uses `display_name` and old offering naming and will be migrated later.

## 14. Consumer request persistence decision

Consumer request history is transactional application data. It should be stored in the Django relational database, not in generated catalogue RDF and not initially in Fuseki.

Fuseki remains for provider/offering/capability catalogue search.

Target stored request record includes:

- `request_id`
- `consumer_id`
- submitted payload
- normalized request
- result count
- response snapshot
- search engine used
- status
- created and updated timestamps

Target future endpoints:

- `GET /api/catalog/requests/{request_id}`
- `GET /api/catalog/requests?consumer_id={consumer_id}`

Authentication/authorization protection is required for production so consumers cannot access another consumer's requests.

Implementation belongs to H8.

## 15. Route, machine, price and availability exclusion

The following remain outside M18 searchable/provider-publication capability fields:

- `routes`
- `route_steps`
- `operation_sequence`
- `machine_sequence`
- `process_order`
- `subcontractor_route`
- `cycle_time`
- `setup_time`
- `machine_availability`
- `pricing`
- `capacity_calendar`

Process capability support is allowed. A typical manufacturing route must not be modelled as a queryable public route in M18.

Subcontracted processes, such as heat treatment where applicable, must not be presented as confirmed in-house capability without evidence.

## 16. Implementation phase roadmap after H0

| Phase | Purpose |
| --- | --- |
| H1 | Implement taxonomy and dynamic field-profile registry for Marketplace forms |
| H2 | Revise provider publication contract and internal offering-ID generation |
| H3 | Migrate Tasowheel, Precipart if available, and demo-provider YAML files |
| H4 | Update consumer search request/response contract and metadata |
| H5 | Update local matcher and add/expand local search API tests |
| H6 | Extend ontology mappings and RDF generation |
| H7 | Extend deterministic SPARQL and Fuseki candidate/evidence retrieval |
| H8 | Add consumer request database persistence and retrieval APIs |
| H9 | Reload Fuseki, compare local versus Fuseki results, and decide API search-engine migration |

H0 does not implement any of these phases. Existing local matcher and Fuseki work must remain untouched until the corresponding implementation phase.

## 17. Known current implementation differences that future phases must address

| Topic | Current implementation | H0 target decision | Future phase |
| --- | --- | --- | --- |
| API paths | `/api/...` | Retain actual path unless a separate versioning decision is made | documentation/API planning |
| Active API matcher | local seed-data matcher | Retain until H9 migration decision | H5/H9 |
| Tasowheel offerings | one bundled offering | two evidence-supported narrower offerings | H3 |
| External provider name | `display_name` | `provider_name` | H2/H4 |
| Offering ID input | externally required | MDC-managed internally | H2 |
| Part taxonomy | limited mixed `part_families` | category/family/type hierarchy | H1/H3/H4 |
| Consumer material grade input | accepted/exposed | not exposed or accepted as M18 search criterion | H1/H4/H5 |
| Consumer/request IDs | absent | required | H4/H8 |
| Generic dimensions | diameter only | typed specifications; bounding box for relevant metal parts | H1/H4/H5/H6 |
| Fuseki | parallel retrieval path | retained, extended later | H6/H7/H9 |
| RDF surface property concern | possible current max/Min mismatch | review before extending RDF | H6 |

## 18. Approval checklist

- [ ] Service categories approved.
- [ ] Part families and part types approved.
- [ ] Specification-field registry approved.
- [ ] Single-part-type-per-request M18 decision approved.
- [ ] Provider publication structure approved.
- [ ] MDC-managed offering IDs approved.
- [ ] External `provider_name` approved.
- [ ] Materials-only consumer search approved.
- [ ] Grade-as-evidence response model approved.
- [ ] `request_id` and `consumer_id` approved.
- [ ] Relational database request history approved.
- [ ] Route exclusions approved.
- [ ] Tasowheel evidence-constrained migration approved.
- [ ] Implementation phases H1-H9 approved.
