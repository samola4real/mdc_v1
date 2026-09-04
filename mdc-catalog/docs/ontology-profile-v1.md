# MaaS Dynamic Catalogue — Ontology Profile v1

**Status:** Week 1 finalized baseline  
**Project:** MaaSAI MaaS Dynamic Catalogue  
**Scenario:** Basic structured-search scenario  
**Pilot:** Tasowheel / TSW gear and shaft manufacturing  
**Target file:** `ontologies/mdc_core.ttl`

---

## 1. Purpose

This document defines the **MDC Tasowheel Application Profile v1**.

The full MaaSAI ontology is broader than the needs of the basic scenario. For v1, the implementation will use a smaller operational ontology profile focused on:

- MaaS Providers
- Provider Offerings
- manufacturing services
- gear and shaft manufacturing capabilities
- material and material-grade descriptors
- process, dimension, weight, batch, quality, lead-time, and certification descriptors
- structured marketplace search
- explainable provider offering matching

Manufacturing route fields are intentionally excluded from this ontology profile version.

---

## 2. Namespace

Use one base namespace for the v1 prototype:

```text
https://maasai-project.eu/ontology/mdc#
```

Recommended prefix:

```text
mdc:
```

Example identifiers:

```text
mdc:MaaSProvider
mdc:ProviderOffering
mdc:GearTransmissionService
mdc:MaterialGrade
mdc:diameterMaxMm
```

---

## 3. Modelling principles

1. **Application profile, not full ontology**  
   This profile contains only the classes and properties required for v1 search.

2. **Simple first, extensible later**  
   Use simple object and data properties for v1. More complex OWL modelling can be added later.

3. **Searchability over completeness**  
   Prioritize fields needed by the marketplace search scenario.

4. **ProviderOffering as central search entity**  
   A provider may have several offerings. Search results should return offerings.

5. **Provenance-aware capability values**  
   Important capability values must have source and confidence metadata.

6. **URI-safe identifiers**  
   Class and property identifiers must not contain spaces, ampersands, or special characters.

7. **No route modelling in v1**  
   Route steps, operation sequences, and route alternatives are not included in this profile version.

---

## 4. Naming corrections from source ontology

| Source / current name | v1 profile name | Decision |
|---|---|---|
| `ManufacturingSevice` | `ManufacturingService` | Correct typo |
| `SubstractiveProcess` | `MaterialRemovalProcess` | Use clearer manufacturing term |
| Duplicate `ProcessCapability` | `ProcessCapability` | Keep one class only |
| `Gear&TransmissionService` | `GearTransmissionService` | Use URI-safe class name |
| `Stakeholder` | `Actor` | Use `Actor` as canonical class |
| Full ontology hierarchy | MDC application profile | Use reduced v1 subset |

---

## 5. Core class hierarchy for v1

### 5.1 Actor classes

| Class | Parent | Purpose |
|---|---|---|
| `mdc:Actor` | `owl:Thing` | Generic MaaSAI ecosystem participant |
| `mdc:MaaSProvider` | `mdc:Actor` | Provider offering manufacturing services |
| `mdc:MaaSConsumer` | `mdc:Actor` | Consumer requesting manufacturing services |

### 5.2 Offering and service classes

| Class | Parent | Purpose |
|---|---|---|
| `mdc:ProviderOffering` | `owl:Thing` | Searchable provider offering |
| `mdc:ManufacturingService` | `owl:Thing` | Generic manufacturing service |
| `mdc:MachiningService` | `mdc:ManufacturingService` | Machining service |
| `mdc:GearTransmissionService` | `mdc:ManufacturingService` | Gear and transmission manufacturing service |
| `mdc:HeatTreatmentService` | `mdc:ManufacturingService` | Heat treatment / hardening service |
| `mdc:FinishingService` | `mdc:ManufacturingService` | Finishing service |
| `mdc:InspectionService` | `mdc:ManufacturingService` | Inspection/metrology service |

### 5.3 Capability classes

| Class | Parent | Purpose |
|---|---|---|
| `mdc:ManufacturingCapability` | `owl:Thing` | Generic capability |
| `mdc:ProcessCapability` | `mdc:ManufacturingCapability` | Supported process capability |
| `mdc:MaterialCapability` | `mdc:ManufacturingCapability` | Supported material capability |
| `mdc:PrecisionCapability` | `mdc:ManufacturingCapability` | Tolerance/quality capability |
| `mdc:DimensionalCapability` | `mdc:ManufacturingCapability` | Size/envelope capability |
| `mdc:WeightCapability` | `mdc:ManufacturingCapability` | Weight capability |
| `mdc:BatchCapability` | `mdc:ManufacturingCapability` | Batch/volume capability |
| `mdc:SurfaceFinishCapability` | `mdc:ManufacturingCapability` | Surface finish capability |
| `mdc:InspectionCapability` | `mdc:ManufacturingCapability` | Inspection/metrology capability |
| `mdc:CertificationBackedCapability` | `mdc:ManufacturingCapability` | Capability supported by certification |

### 5.4 Process classes

| Class | Parent | Purpose |
|---|---|---|
| `mdc:Process` | `owl:Thing` | Generic process |
| `mdc:MaterialRemovalProcess` | `mdc:Process` | Parent for subtractive processes |
| `mdc:Machining` | `mdc:MaterialRemovalProcess` | Generic machining process |
| `mdc:Turning` | `mdc:MaterialRemovalProcess` | Turning |
| `mdc:Milling` | `mdc:MaterialRemovalProcess` | Milling |
| `mdc:Grinding` | `mdc:MaterialRemovalProcess` | Grinding |
| `mdc:GearGrinding` | `mdc:Grinding` | Gear grinding / tooth grinding |
| `mdc:Hobbing` | `mdc:MaterialRemovalProcess` | Gear hobbing |
| `mdc:GearShaping` | `mdc:MaterialRemovalProcess` | Gear shaping |
| `mdc:HardTurning` | `mdc:Turning` | Hard turning |
| `mdc:HeatTreatment` | `mdc:Process` | Heat treatment / hardening |
| `mdc:InspectionProcess` | `mdc:Process` | Inspection / quality checking |

### 5.5 Material classes

| Class | Parent | Purpose |
|---|---|---|
| `mdc:Material` | `owl:Thing` | Generic material |
| `mdc:Metal` | `mdc:Material` | Generic metal |
| `mdc:Steel` | `mdc:Metal` | Steel |
| `mdc:AlloyedCarburizingSteel` | `mdc:Steel` | Alloyed carburizing steel |
| `mdc:StainlessSteel` | `mdc:Steel` | Stainless steel |
| `mdc:Aluminum` | `mdc:Metal` | Aluminum |
| `mdc:Titanium` | `mdc:Metal` | Titanium |
| `mdc:NickelAlloy` | `mdc:Metal` | Nickel alloy |
| `mdc:MaterialGrade` | `owl:Thing` | Specific material grade such as 18CrNiMo7-6 |

### 5.6 Part-family classes

| Class | Parent | Purpose |
|---|---|---|
| `mdc:PartFamily` | `owl:Thing` | Generic part family |
| `mdc:Gear` | `mdc:PartFamily` | Generic gear |
| `mdc:SpurGear` | `mdc:Gear` | Spur gear |
| `mdc:HelicalGear` | `mdc:Gear` | Helical gear |
| `mdc:Shaft` | `mdc:PartFamily` | Shaft |
| `mdc:TransmissionComponent` | `mdc:PartFamily` | Transmission component |

### 5.7 Request and requirement classes

| Class | Parent | Purpose |
|---|---|---|
| `mdc:ConsumerRequest` | `owl:Thing` | Marketplace user request |
| `mdc:MaterialRequirement` | `owl:Thing` | Requested material |
| `mdc:MaterialGradeRequirement` | `owl:Thing` | Requested material grade |
| `mdc:ProcessRequirement` | `owl:Thing` | Requested process |
| `mdc:DimensionRequirement` | `owl:Thing` | Requested dimensions/envelope |
| `mdc:ToleranceRequirement` | `owl:Thing` | Requested tolerance/quality |
| `mdc:SurfaceRequirement` | `owl:Thing` | Requested surface finish |
| `mdc:WeightRequirement` | `owl:Thing` | Requested part weight |
| `mdc:BatchSizeRequirement` | `owl:Thing` | Requested batch size |
| `mdc:DeliveryRequirement` | `owl:Thing` | Requested delivery time |
| `mdc:CertificationRequirement` | `owl:Thing` | Requested certification |
| `mdc:TraceabilityRequirement` | `owl:Thing` | Requested traceability |

### 5.8 Business and quality classes

| Class | Parent | Purpose |
|---|---|---|
| `mdc:LeadTimeDescriptor` | `owl:Thing` | Lead-time information |
| `mdc:AvailabilityDescriptor` | `owl:Thing` | Availability status |
| `mdc:QualityDescriptor` | `owl:Thing` | Generic quality descriptor |
| `mdc:PrecisionLevel` | `mdc:QualityDescriptor` | Precision/quality level |
| `mdc:SurfaceFinishDescriptor` | `mdc:QualityDescriptor` | Surface finish descriptor |
| `mdc:Certification` | `owl:Thing` | Certification artifact |
| `mdc:TraceabilityRecord` | `owl:Thing` | Traceability artifact |
| `mdc:FacilityLocation` | `owl:Thing` | Provider/facility location |
| `mdc:IndustrySector` | `owl:Thing` | Industry/sector tag |
| `mdc:QualityStandard` | `owl:Thing` | DIN/ISO/etc. standard concept |

---

## 6. Object properties

| Property | Domain | Range | Purpose |
|---|---|---|---|
| `mdc:hasOffering` | `mdc:MaaSProvider` | `mdc:ProviderOffering` | Provider owns/offers an offering |
| `mdc:offeredBy` | `mdc:ProviderOffering` | `mdc:MaaSProvider` | Offering belongs to provider |
| `mdc:hasServiceType` | `mdc:ProviderOffering` | `mdc:ManufacturingService` | Classifies the offering |
| `mdc:hasCapability` | `mdc:ProviderOffering` | `mdc:ManufacturingCapability` | Links offering to capability |
| `mdc:supportsProcess` | `mdc:ProviderOffering` | `mdc:Process` | Supported process |
| `mdc:supportsMaterial` | `mdc:ProviderOffering` | `mdc:Material` | Supported material |
| `mdc:supportsMaterialGrade` | `mdc:ProviderOffering` | `mdc:MaterialGrade` | Supported material grade |
| `mdc:gradeOfMaterial` | `mdc:MaterialGrade` | `mdc:Material` | Links a grade to its material family |
| `mdc:supportsPartFamily` | `mdc:ProviderOffering` | `mdc:PartFamily` | Supported part family |
| `mdc:hasCertification` | `mdc:MaaSProvider` or `mdc:ProviderOffering` | `mdc:Certification` | Certification evidence |
| `mdc:hasLocation` | `mdc:MaaSProvider` | `mdc:FacilityLocation` | Provider/facility location |
| `mdc:supportsIndustry` | `mdc:ProviderOffering` | `mdc:IndustrySector` | Supported industry |
| `mdc:hasQualityStandard` | `mdc:ProviderOffering` | `mdc:QualityStandard` | Quality standard |
| `mdc:hasAvailabilityStatus` | `mdc:ProviderOffering` | `mdc:AvailabilityDescriptor` | Availability status |

---

## 7. Data properties

| Property | Type | Unit / format | Purpose |
|---|---|---|---|
| `mdc:providerId` | `xsd:string` | stable slug | Provider ID |
| `mdc:offeringId` | `xsd:string` | stable slug | Offering ID |
| `mdc:legalName` | `xsd:string` | text | Provider legal name |
| `mdc:displayName` | `xsd:string` | text | UI display name |
| `mdc:description` | `xsd:string` | text | Human-readable description |
| `mdc:materialGradeCode` | `xsd:string` | text | Material grade code |
| `mdc:diameterMinMm` | `xsd:decimal` | mm | Minimum diameter |
| `mdc:diameterMaxMm` | `xsd:decimal` | mm | Maximum diameter |
| `mdc:lengthMaxMm` | `xsd:decimal` | mm | Maximum shaft/part length, optional |
| `mdc:weightMaxKg` | `xsd:decimal` | kg | Maximum part weight |
| `mdc:weightApproximate` | `xsd:boolean` | true/false | Indicates approximate weight value |
| `mdc:moduleMin` | `xsd:decimal` | module | Minimum gear module |
| `mdc:moduleMax` | `xsd:decimal` | module | Maximum gear module |
| `mdc:dpMin` | `xsd:decimal` | diametral pitch | Lower DP bound after normalization |
| `mdc:dpMax` | `xsd:decimal` | diametral pitch | Upper DP bound after normalization |
| `mdc:dpRaw` | `xsd:string` | text | Raw DP string from provider source |
| `mdc:qualityClassBest` | `xsd:decimal` | standard-specific | Best achievable quality class |
| `mdc:toleranceMinMm` | `xsd:decimal` | mm | Best/lowest tolerance if known |
| `mdc:surfaceRaMinUm` | `xsd:decimal` | µm | Best surface finish if known |
| `mdc:batchMin` | `xsd:integer` | pieces | Minimum batch |
| `mdc:batchMax` | `xsd:integer` | pieces | Maximum batch |
| `mdc:leadTimeMinWeeks` | `xsd:decimal` | weeks | Minimum normal lead time |
| `mdc:leadTimeMaxWeeks` | `xsd:decimal` | weeks | Maximum normal lead time |
| `mdc:leadTimeQualifier` | `xsd:string` | text | e.g. normal_case_dependent |
| `mdc:dataConfidence` | `xsd:string` | enum | declared / inferred / estimated / unknown |
| `mdc:sourceType` | `xsd:string` | enum | provider_confirmed / machine_list / public_web / curated / not_confirmed |
| `mdc:sourceNote` | `xsd:string` | text | Evidence note |

---

## 8. Controlled vocabularies

### 8.1 Service types

| UI value | Ontology concept |
|---|---|
| `gear_manufacturing` | `mdc:GearTransmissionService` |
| `shaft_manufacturing` | `mdc:GearTransmissionService` |
| `machining` | `mdc:MachiningService` |
| `heat_treatment` | `mdc:HeatTreatmentService` |
| `inspection` | `mdc:InspectionService` |
| `finishing` | `mdc:FinishingService` |

### 8.2 Part families

| UI value | Ontology concept |
|---|---|
| `gear` | `mdc:Gear` |
| `spur_gear` | `mdc:SpurGear` |
| `helical_gear` | `mdc:HelicalGear` |
| `shaft` | `mdc:Shaft` |
| `transmission_component` | `mdc:TransmissionComponent` |

### 8.3 Processes

| UI value | Ontology concept |
|---|---|
| `machining` | `mdc:Machining` |
| `turning` | `mdc:Turning` |
| `milling` | `mdc:Milling` |
| `hobbing` | `mdc:Hobbing` |
| `gear_shaping` | `mdc:GearShaping` |
| `hard_turning` | `mdc:HardTurning` |
| `grinding` | `mdc:Grinding` |
| `gear_grinding` | `mdc:GearGrinding` |
| `heat_treatment` | `mdc:HeatTreatment` |
| `inspection` | `mdc:InspectionProcess` |

### 8.4 Materials

| UI value | Ontology concept | v1 note |
|---|---|---|
| `steel` | `mdc:Steel` | Supported for TSW |
| `alloyed_carburizing_steel` | `mdc:AlloyedCarburizingSteel` | Supported for TSW |
| `stainless_steel` | `mdc:StainlessSteel` | Supported in schema; do not assert for TSW unless confirmed |
| `aluminum` | `mdc:Aluminum` | Supported in schema; do not assert for TSW unless confirmed |
| `titanium` | `mdc:Titanium` | Supported in schema; do not assert for TSW unless confirmed |
| `nickel_alloy` | `mdc:NickelAlloy` | Supported in schema; do not assert for TSW unless confirmed |

### 8.5 Material grades

| UI value | Ontology concept | Material family |
|---|---|---|
| `18CrNiMo7-6` | `mdc:MaterialGrade_18CrNiMo7_6` | `mdc:AlloyedCarburizingSteel` |
| `16MnCr5` | `mdc:MaterialGrade_16MnCr5` | `mdc:AlloyedCarburizingSteel` |
| `20MnCr5` | `mdc:MaterialGrade_20MnCr5` | `mdc:AlloyedCarburizingSteel` |

### 8.6 Certifications

| UI value | Ontology concept | v1 note |
|---|---|---|
| `ISO9001_2015` | `mdc:ISO9001_2015` | Known for TSW |
| `ISO14001_2015` | `mdc:ISO14001_2015` | Known for TSW |
| `ISO_TS_16949_partial` | `mdc:ISO_TS_16949_partial` | Partial implementation, known for TSW |
| `APQP` | `mdc:APQP` | Known for TSW |
| `aerospace_traceability` | `mdc:AerospaceTraceability` | Supported in schema, unknown unless confirmed |
| `full_traceability` | `mdc:FullTraceability` | Supported in schema, unknown unless confirmed |

---

## 9. Tasowheel v1 individuals / instances

### 9.1 Provider

| Field | Value |
|---|---|
| Provider URI | `mdc:provider_tasowheel` |
| Provider ID | `tasowheel` |
| Display name | `Tasowheel Oy` |
| Type | `mdc:MaaSProvider` |
| Country | Finland |

### 9.2 Primary offering

| Field | Value |
|---|---|
| Offering URI | `mdc:offering_tasowheel_gears_shafts_precision` |
| Offering ID | `tasowheel_gears_shafts_precision` |
| Service type | `mdc:GearTransmissionService` |
| v1 priority | Required |

---

## 10. Route modelling decision

Route concepts are intentionally excluded from `mdc_core.ttl` v1.

Do not create v1 classes/properties such as:

- `mdc:Route`
- `mdc:RouteStep`
- `mdc:hasRouteStep`
- `mdc:hasOperationSequence`
- `mdc:nextStep`
- `mdc:subcontractedRouteStep`

These can be introduced in a future version if the catalogue needs process-chain planning or route-aware matching.

---

## 11. SHACL validation targets

The following SHACL shapes should be created later in:

```text
ontologies/shacl/mdc_v1_shapes.ttl
```

| Shape | Purpose |
|---|---|
| `ProviderShape` | Provider has ID, name, and type |
| `OfferingShape` | Offering has ID, provider, and service type |
| `MaterialGradeShape` | Material grade has code and parent material |
| `CapabilityShape` | Capability values use valid units and datatypes |
| `DimensionShape` | Dimension min/max values are positive and consistent |
| `BatchShape` | Batch min/max values are positive and consistent |
| `QualityShape` | Quality standard and class appear together |
| `LeadTimeShape` | Lead-time min/max values are positive and consistent |
| `SourceShape` | Important capability values include source and confidence metadata |

---

## 12. Review checklist

Before creating `mdc_core.ttl`, confirm:

- [x] Namespace is approved.
- [x] Naming corrections are approved.
- [x] Core class list is sufficient for v1.
- [x] Route modelling is excluded from v1.
- [x] Material grades are included.
- [x] Object properties are sufficient for SPARQL queries.
- [x] Data properties cover all required SearchRequest fields.
- [x] Controlled vocabularies match the marketplace UI requirements.
- [x] Unknown and unconfirmed fields are not incorrectly asserted for TSW.
