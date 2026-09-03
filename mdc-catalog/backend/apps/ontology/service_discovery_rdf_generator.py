from __future__ import annotations

from pathlib import Path
from typing import Any

from django.conf import settings
from rdflib import Graph, Literal, RDF, XSD

from apps.ontology.service_discovery_rdf_mappings import (
    MDC,
    ServiceDiscoveryRdfMappingError,
    available_grade_evidence_resource,
    certification_evidence_resource,
    component_evidence_resource,
    family_capability_resource,
    generic_capability_resource,
    get_capability_field_concept,
    get_certification_concept,
    get_material_concept,
    get_part_family_concept,
    get_part_type_concept,
    get_process_concept,
    get_service_category_concept,
    material_evidence_resource,
    offering_resource,
    part_type_capability_resource,
    part_type_support_resource,
    process_evidence_resource,
    provider_resource,
)
from apps.providers.service_discovery_loaders import load_service_discovery_providers
from apps.providers.validators import FORBIDDEN_ROUTE_KEYS


class ServiceDiscoveryRdfGenerationError(Exception):
    pass


NUMERIC_PROPERTIES = {
    "min": MDC.minValue,
    "max": MDC.maxValue,
    "exact": MDC.exactValue,
}

TEXT_PROPERTIES = {
    "raw": MDC.rawValue,
    "unit": MDC.unit,
    "qualifier": MDC.qualifier,
    "standard": MDC.qualityStandard,
    "comparison_rule": MDC.comparisonRule,
    "normalized_order": MDC.normalizedOrder,
    "source_type": MDC.sourceType,
    "confidence": MDC.confidence,
    "source_note": MDC.sourceNote,
}

NUMBER_TEXT_PROPERTIES = {
    "best_class": MDC.bestClass,
}

BOOLEAN_PROPERTIES = {
    "approximate": MDC.approximate,
}


def _iter_nested(data: Any):
    if isinstance(data, dict):
        for key, value in data.items():
            yield key
            yield from _iter_nested(value)
    elif isinstance(data, list):
        for item in data:
            yield from _iter_nested(item)


def _reject_forbidden_fields(data: Any) -> None:
    found = sorted(set(_iter_nested(data)) & set(FORBIDDEN_ROUTE_KEYS))
    if found:
        raise ServiceDiscoveryRdfGenerationError(
            f"Forbidden harmonized publication fields cannot be serialized to RDF: {found}"
        )


def _require_mapping(callable_, value: str):
    try:
        return callable_(value)
    except ServiceDiscoveryRdfMappingError as exc:
        raise ServiceDiscoveryRdfGenerationError(str(exc)) from exc


def _typed_number(value: Any) -> Literal:
    datatype = XSD.integer if isinstance(value, int) and not isinstance(value, bool) else XSD.decimal
    return Literal(value, datatype=datatype)


def _add_record_properties(graph: Graph, subject, record: dict[str, Any]) -> None:
    for key, predicate in NUMERIC_PROPERTIES.items():
        value = record.get(key)
        if value is not None:
            graph.add((subject, predicate, _typed_number(value)))

    for key, predicate in NUMBER_TEXT_PROPERTIES.items():
        value = record.get(key)
        if value is not None:
            graph.add((subject, predicate, _typed_number(value)))

    for key, predicate in TEXT_PROPERTIES.items():
        value = record.get(key)
        if value is not None:
            graph.add((subject, predicate, Literal(value)))

    for key, predicate in BOOLEAN_PROPERTIES.items():
        value = record.get(key)
        if value is not None:
            graph.add((subject, predicate, Literal(value, datatype=XSD.boolean)))


def _add_explicit_null_fields(graph: Graph, subject, record: dict[str, Any]) -> None:
    for key, value in record.items():
        if value is None:
            graph.add((subject, MDC.explicitNullField, Literal(key)))


def _add_capability_common(
    graph: Graph,
    subject,
    *,
    field_code: str,
    record: dict[str, Any],
) -> None:
    graph.add((subject, RDF.type, MDC.CapabilityEvidence))
    graph.add((subject, MDC.capabilityField, _require_mapping(get_capability_field_concept, field_code)))
    graph.add((subject, MDC.fieldCode, Literal(field_code)))
    _add_record_properties(graph, subject, record)
    _add_explicit_null_fields(graph, subject, record)


def _add_component_capabilities(graph: Graph, parent, record: dict[str, Any]) -> None:
    for component_field, component_record in record.items():
        if not isinstance(component_record, dict):
            continue
        if component_field in {
            "source_type",
            "confidence",
            "source_note",
            "min",
            "max",
            "exact",
            "raw",
            "unit",
            "qualifier",
            "standard",
            "best_class",
            "comparison_rule",
            "normalized_order",
            "approximate",
        }:
            continue
        component = component_evidence_resource(parent, component_field)
        graph.add((parent, MDC.hasComponent, component))
        graph.add((component, RDF.type, MDC.CapabilityComponentEvidence))
        graph.add((component, MDC.componentField, _require_mapping(get_capability_field_concept, component_field)))
        graph.add((component, MDC.fieldCode, Literal(component_field)))
        _add_record_properties(graph, component, component_record)


def _add_provider(graph: Graph, provider: dict[str, Any]) -> None:
    provider_id = provider["provider_id"]
    subject = provider_resource(provider_id)

    graph.add((subject, RDF.type, MDC.MaaSProvider))
    graph.add((subject, MDC.providerId, Literal(provider_id)))
    graph.add((subject, MDC.displayName, Literal(provider.get("display_name", ""))))

    country = provider.get("country")
    if country:
        graph.add((subject, MDC.country, Literal(country)))

    for sequence_index, certification in enumerate(provider.get("certifications", [])):
        code = certification["code"]
        node = certification_evidence_resource(provider_id, code)
        graph.add((subject, MDC.hasCertificationEvidence, node))
        graph.add((node, RDF.type, MDC.CertificationEvidence))
        graph.add((node, MDC.certification, _require_mapping(get_certification_concept, code)))
        graph.add((node, MDC.certificationCode, Literal(code)))
        graph.add((node, MDC.sequenceIndex, Literal(sequence_index, datatype=XSD.integer)))
        _add_record_properties(graph, node, certification)


def _add_part_type_support(graph: Graph, offering_subject, offering_id: str, support: dict[str, Any]) -> None:
    part_type = support["part_type"]
    node = part_type_support_resource(offering_id, part_type)
    graph.add((offering_subject, MDC.hasPartTypeSupport, node))
    graph.add((node, RDF.type, MDC.PartTypeSupportEvidence))
    graph.add((node, MDC.partType, _require_mapping(get_part_type_concept, part_type)))
    graph.add((node, MDC.partTypeCode, Literal(part_type)))
    graph.add((node, MDC.supportStatus, Literal(support["support_status"])))
    _add_record_properties(graph, node, support)


def _add_family_capabilities(graph: Graph, offering_subject, offering_id: str, capabilities: dict[str, Any]) -> None:
    for field_code, record in capabilities.items():
        if not isinstance(record, dict):
            raise ServiceDiscoveryRdfGenerationError(f"Capability {field_code} must be an object.")
        node = family_capability_resource(offering_id, field_code)
        graph.add((offering_subject, MDC.hasFamilyCapability, node))
        _add_capability_common(graph, node, field_code=field_code, record=record)
        _add_component_capabilities(graph, node, record)


def _add_part_type_capabilities(
    graph: Graph,
    offering_subject,
    offering_id: str,
    capabilities_by_part_type: dict[str, dict[str, Any]],
) -> None:
    for part_type, capabilities in capabilities_by_part_type.items():
        _require_mapping(get_part_type_concept, part_type)
        for field_code, record in capabilities.items():
            if not isinstance(record, dict):
                raise ServiceDiscoveryRdfGenerationError(
                    f"Part-type capability {part_type}.{field_code} must be an object."
                )
            node = part_type_capability_resource(offering_id, part_type, field_code)
            graph.add((offering_subject, MDC.hasPartTypeCapability, node))
            _add_capability_common(graph, node, field_code=field_code, record=record)
            graph.add((node, MDC.appliesToPartType, _require_mapping(get_part_type_concept, part_type)))
            graph.add((node, MDC.partTypeCode, Literal(part_type)))
            _add_component_capabilities(graph, node, record)


def _add_materials(graph: Graph, offering_subject, offering_id: str, materials: list[dict[str, Any]]) -> None:
    for sequence_index, material in enumerate(materials):
        code = material["material"]
        node = material_evidence_resource(offering_id, code)
        graph.add((offering_subject, MDC.hasMaterialEvidence, node))
        graph.add((node, RDF.type, MDC.MaterialEvidence))
        graph.add((node, MDC.material, _require_mapping(get_material_concept, code)))
        graph.add((node, MDC.materialCode, Literal(code)))
        graph.add((node, MDC.sequenceIndex, Literal(sequence_index, datatype=XSD.integer)))
        for grade_sequence_index, grade in enumerate(material.get("available_grades", [])):
            graph.add((node, MDC.availableGrade, Literal(grade)))
            grade_node = available_grade_evidence_resource(
                offering_id,
                code,
                grade_sequence_index,
            )
            graph.add((node, MDC.hasAvailableGradeEvidence, grade_node))
            graph.add((grade_node, RDF.type, MDC.AvailableGradeEvidence))
            graph.add((grade_node, MDC.availableGrade, Literal(grade)))
            graph.add((grade_node, MDC.sequenceIndex, Literal(grade_sequence_index, datatype=XSD.integer)))
        _add_record_properties(graph, node, material)


def _add_processes(graph: Graph, offering_subject, offering_id: str, processes: list[dict[str, Any]]) -> None:
    for sequence_index, process in enumerate(processes):
        code = process["process"]
        node = process_evidence_resource(offering_id, code)
        graph.add((offering_subject, MDC.hasProcessEvidence, node))
        graph.add((node, RDF.type, MDC.ProcessEvidence))
        graph.add((node, MDC.process, _require_mapping(get_process_concept, code)))
        graph.add((node, MDC.processCode, Literal(code)))
        graph.add((node, MDC.sequenceIndex, Literal(sequence_index, datatype=XSD.integer)))
        delivery_mode = process.get("delivery_mode")
        if delivery_mode is not None:
            graph.add((node, MDC.deliveryMode, Literal(delivery_mode)))
        _add_record_properties(graph, node, process)


def _add_generic_capabilities(graph: Graph, offering_subject, offering_id: str, generic: dict[str, Any]) -> None:
    if "materials" in generic:
        _add_materials(graph, offering_subject, offering_id, generic["materials"])
    if "processes" in generic:
        _add_processes(graph, offering_subject, offering_id, generic["processes"])

    for field_code, record in generic.items():
        if field_code in {"materials", "processes"}:
            continue
        if field_code == "certifications":
            continue
        if not isinstance(record, dict):
            raise ServiceDiscoveryRdfGenerationError(
                f"Generic capability {field_code} must be an object."
            )
        node = generic_capability_resource(offering_id, field_code)
        graph.add((offering_subject, MDC.hasGenericCapability, node))
        _add_capability_common(graph, node, field_code=field_code, record=record)
        _add_component_capabilities(graph, node, record)


def _add_offering(graph: Graph, provider: dict[str, Any], offering: dict[str, Any]) -> None:
    offering_id = offering["offering_id"]
    subject = offering_resource(offering_id)
    provider_subject = provider_resource(provider["provider_id"])

    graph.add((subject, RDF.type, MDC.ProviderOffering))
    graph.add((provider_subject, MDC.hasOffering, subject))
    graph.add((subject, MDC.offeredBy, provider_subject))
    graph.add((subject, MDC.offeringId, Literal(offering_id)))
    graph.add((subject, MDC.providerId, Literal(offering["provider_id"])))
    graph.add((subject, MDC.displayName, Literal(offering.get("name", ""))))
    graph.add((subject, MDC.serviceCategory, _require_mapping(get_service_category_concept, offering["service_category"])))
    graph.add((subject, MDC.supportsPartFamily, _require_mapping(get_part_family_concept, offering["part_family"])))
    graph.add((subject, MDC.supportStatus, Literal(offering["support_status"])))

    for support in offering.get("supported_part_types", []):
        _add_part_type_support(graph, subject, offering_id, support)

    _add_family_capabilities(graph, subject, offering_id, offering.get("family_capabilities", {}))
    _add_part_type_capabilities(graph, subject, offering_id, offering.get("part_type_capabilities", {}))
    _add_generic_capabilities(graph, subject, offering_id, offering.get("generic_capabilities", {}))


def _validate_record(record: dict[str, Any]) -> None:
    if not isinstance(record, dict):
        raise ServiceDiscoveryRdfGenerationError("Provider record root must be a dictionary.")
    if "provider" not in record or "offerings" not in record:
        raise ServiceDiscoveryRdfGenerationError("Provider record must contain provider and offerings.")
    provider = record["provider"]
    if not isinstance(provider, dict) or "provider_id" not in provider:
        raise ServiceDiscoveryRdfGenerationError("Provider record has invalid provider block.")
    if not isinstance(record["offerings"], list):
        raise ServiceDiscoveryRdfGenerationError("Provider record offerings must be a list.")


def build_service_discovery_graph(provider_records: list[dict] | None = None) -> Graph:
    provider_records = provider_records if provider_records is not None else load_service_discovery_providers()
    for record in provider_records:
        _reject_forbidden_fields(record)
        _validate_record(record)

    graph = Graph()
    graph.bind("mdc", MDC)
    graph.bind("rdf", RDF)
    graph.bind("xsd", XSD)

    for record in provider_records:
        provider = record["provider"]
        _add_provider(graph, provider)
        for offering in record["offerings"]:
            _add_offering(graph, provider, offering)

    return graph


def default_service_discovery_turtle_path() -> Path:
    return Path(settings.GENERATED_DATA_DIR) / "service_discovery" / "mdc_service_discovery_catalog.ttl"


def generate_service_discovery_turtle(
    *,
    provider_records: list[dict] | None = None,
    output_path: Path | None = None,
) -> Path:
    graph = build_service_discovery_graph(provider_records=provider_records)
    output_path = output_path or default_service_discovery_turtle_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=str(output_path), format="turtle")
    return output_path
