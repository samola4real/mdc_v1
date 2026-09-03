
from pathlib import Path
from typing import Any

from django.conf import settings
from rdflib import Graph, Literal, Namespace, RDF, XSD

from apps.ontology.rdf_mappings import (
    CERTIFICATION_CONCEPTS,
    MATERIAL_CONCEPTS,
    PART_FAMILY_CONCEPTS,
    PROCESS_CONCEPTS,
    SERVICE_TYPE_CONCEPTS,
)
from apps.providers.services import get_seed_data


MDC = Namespace("https://maasai-project.eu/ontology/mdc#")


def safe_identifier(value: str) -> str:
    """
    Convert IDs/codes into URI-safe fragments.

    Example:
    18CrNiMo7-6 -> 18CrNiMo7_6
    """
    return (
        value.replace("-", "_")
        .replace("/", "_")
        .replace(" ", "_")
        .replace(".", "_")
    )


def provider_uri(provider_id: str):
    return MDC[f"provider_{safe_identifier(provider_id)}"]


def offering_uri(offering_id: str):
    return MDC[f"offering_{safe_identifier(offering_id)}"]


def material_grade_uri(grade_id: str):
    return MDC[f"MaterialGrade_{safe_identifier(grade_id)}"]


def add_literal_if_present(
    graph: Graph,
    subject,
    predicate,
    value: Any,
    datatype=None,
) -> None:
    """
    Add a literal triple only when value is not None.
    """
    if value is None:
        return

    graph.add((subject, predicate, Literal(value, datatype=datatype)))


def add_provider(graph: Graph, provider: dict[str, Any]) -> None:
    provider_id = provider["provider_id"]
    subject = provider_uri(provider_id)

    graph.add((subject, RDF.type, MDC.MaaSProvider))

    add_literal_if_present(graph, subject, MDC.providerId, provider_id)
    add_literal_if_present(graph, subject, MDC.displayName, provider.get("display_name"))
    add_literal_if_present(graph, subject, MDC.legalName, provider.get("legal_name"))
    add_literal_if_present(graph, subject, MDC.country, provider.get("country"))
    add_literal_if_present(graph, subject, MDC.sourceType, provider.get("source_type"))
    add_literal_if_present(graph, subject, MDC.dataConfidence, provider.get("confidence"))

    for certification in provider.get("certifications", []):
        code = certification.get("code")
        concept_name = CERTIFICATION_CONCEPTS.get(code)

        if not concept_name:
            continue

        certification_node = MDC[concept_name]

        graph.add((certification_node, RDF.type, MDC.Certification))
        graph.add((subject, MDC.hasCertification, certification_node))


def add_materials(graph: Graph, seed_data: dict[str, Any]) -> None:
    for material in seed_data.get("materials", []):
        material_id = material.get("material_id")
        concept_name = MATERIAL_CONCEPTS.get(material_id)

        if not concept_name:
            continue

        material_node = MDC[concept_name]

        graph.add((material_node, RDF.type, MDC.Material))
        add_literal_if_present(graph, material_node, MDC.materialId, material_id)
        add_literal_if_present(graph, material_node, MDC.label, material.get("label"))


def add_material_grades(graph: Graph, seed_data: dict[str, Any]) -> None:
    for grade in seed_data.get("material_grades", []):
        grade_id = grade.get("grade_id")
        material_id = grade.get("material_id")

        if not grade_id:
            continue

        grade_node = material_grade_uri(grade_id)

        graph.add((grade_node, RDF.type, MDC.MaterialGrade))
        add_literal_if_present(graph, grade_node, MDC.materialGradeCode, grade_id)
        add_literal_if_present(graph, grade_node, MDC.label, grade.get("label"))
        add_literal_if_present(graph, grade_node, MDC.sourceType, grade.get("source_type"))
        add_literal_if_present(graph, grade_node, MDC.dataConfidence, grade.get("confidence"))

        material_concept_name = MATERIAL_CONCEPTS.get(material_id)
        if material_concept_name:
            graph.add((grade_node, MDC.gradeOfMaterial, MDC[material_concept_name]))


def add_offering(graph: Graph, offering: dict[str, Any]) -> None:
    subject = offering_uri(offering["offering_id"])
    provider = provider_uri(offering["provider_id"])

    graph.add((subject, RDF.type, MDC.ProviderOffering))
    graph.add((provider, MDC.hasOffering, subject))
    graph.add((subject, MDC.offeredBy, provider))

    add_literal_if_present(graph, subject, MDC.offeringId, offering.get("offering_id"))
    add_literal_if_present(graph, subject, MDC.providerId, offering.get("provider_id"))
    add_literal_if_present(graph, subject, MDC.displayName, offering.get("name"))
    add_literal_if_present(graph, subject, MDC.sourceType, offering.get("source_type"))
    add_literal_if_present(graph, subject, MDC.dataConfidence, offering.get("confidence"))

    service_type = offering.get("service_type")
    service_concept = SERVICE_TYPE_CONCEPTS.get(service_type)
    if service_concept:
        graph.add((subject, MDC.hasServiceType, MDC[service_concept]))

    for part_family in offering.get("part_families", []):
        concept_name = PART_FAMILY_CONCEPTS.get(part_family)
        if concept_name:
            graph.add((subject, MDC.supportsPartFamily, MDC[concept_name]))

    for process in offering.get("processes", []):
        concept_name = PROCESS_CONCEPTS.get(process)
        if concept_name:
            graph.add((subject, MDC.supportsProcess, MDC[concept_name]))

    for material_entry in offering.get("supported_materials", []):
        material_id = material_entry.get("material")
        concept_name = MATERIAL_CONCEPTS.get(material_id)

        if concept_name:
            graph.add((subject, MDC.supportsMaterial, MDC[concept_name]))

    for grade_id in offering.get("supported_material_grades", []):
        graph.add((subject, MDC.supportsMaterialGrade, material_grade_uri(grade_id)))

    add_capabilities(graph, subject, offering.get("capabilities", {}))


def add_capabilities(graph: Graph, subject, capabilities: dict[str, Any]) -> None:
    batch = capabilities.get("batch_size", {})
    add_literal_if_present(graph, subject, MDC.batchMin, batch.get("min"), XSD.integer)
    add_literal_if_present(graph, subject, MDC.batchMax, batch.get("max"), XSD.integer)

    diameter = capabilities.get("diameter_mm", {})
    add_literal_if_present(graph, subject, MDC.diameterMinMm, diameter.get("min"), XSD.decimal)
    add_literal_if_present(graph, subject, MDC.diameterMaxMm, diameter.get("max"), XSD.decimal)

    weight = capabilities.get("weight_kg", {})
    add_literal_if_present(graph, subject, MDC.weightMaxKg, weight.get("max"), XSD.decimal)
    add_literal_if_present(graph, subject, MDC.weightApproximate, weight.get("approximate"), XSD.boolean)

    module = capabilities.get("module", {})
    add_literal_if_present(graph, subject, MDC.moduleMin, module.get("min"), XSD.decimal)
    add_literal_if_present(graph, subject, MDC.moduleMax, module.get("max"), XSD.decimal)

    dp = capabilities.get("diametral_pitch", {})
    add_literal_if_present(graph, subject, MDC.dpMin, dp.get("min"), XSD.decimal)
    add_literal_if_present(graph, subject, MDC.dpMax, dp.get("max"), XSD.decimal)
    add_literal_if_present(graph, subject, MDC.dpRaw, dp.get("raw"))

    quality = capabilities.get("quality", {})
    add_literal_if_present(graph, subject, MDC.qualityClassBest, quality.get("best_class"), XSD.decimal)

    lead_time = capabilities.get("lead_time_weeks", {})
    add_literal_if_present(graph, subject, MDC.leadTimeMinWeeks, lead_time.get("min"), XSD.decimal)
    add_literal_if_present(graph, subject, MDC.leadTimeMaxWeeks, lead_time.get("max"), XSD.decimal)
    add_literal_if_present(graph, subject, MDC.leadTimeQualifier, lead_time.get("qualifier"))

    surface = capabilities.get("surface_finish_ra_um", {})
    add_literal_if_present(graph, subject, MDC.surfaceRaMinUm, surface.get("max"), XSD.decimal)

    tolerance = capabilities.get("tolerance_mm", {})
    add_literal_if_present(graph, subject, MDC.toleranceMinMm, tolerance.get("min"), XSD.decimal)


def build_catalog_graph(seed_data: dict[str, Any] | None = None) -> Graph:
    """
    Build RDF graph from current provider seed data.
    """
    seed_data = seed_data or get_seed_data()

    graph = Graph()
    graph.bind("mdc", MDC)

    for provider in seed_data.get("providers", []):
        add_provider(graph, provider)

    add_materials(graph, seed_data)
    add_material_grades(graph, seed_data)

    for offering in seed_data.get("offerings", []):
        add_offering(graph, offering)

    return graph


def get_generated_catalog_path(filename: str = "mdc_catalog.ttl") -> Path:
    output_dir = Path(settings.GENERATED_DATA_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / filename


def write_catalog_turtle(filename: str = "mdc_catalog.ttl") -> Path:
    """
    Generate Turtle RDF from current seed data and write it to data/generated.
    """
    graph = build_catalog_graph()
    output_path = get_generated_catalog_path(filename)

    graph.serialize(destination=str(output_path), format="turtle")

    return output_path