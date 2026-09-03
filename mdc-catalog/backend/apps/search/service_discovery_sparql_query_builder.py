from __future__ import annotations

from rdflib import URIRef

from apps.ontology.service_discovery_rdf_mappings import (
    MDC,
    ServiceDiscoveryRdfMappingError,
    get_part_family_concept,
    get_part_type_concept,
    get_service_category_concept,
)
from apps.search.service_discovery_request import CanonicalServiceDiscoverySearchRequest


class ServiceDiscoverySparqlQueryBuildError(Exception):
    pass


PREFIXES = f"""
PREFIX mdc: <{MDC}>
""".strip()


def _resolve_selection(canonical_request: CanonicalServiceDiscoverySearchRequest) -> tuple[URIRef, URIRef, URIRef]:
    selection = canonical_request.selection
    try:
        return (
            get_service_category_concept(selection["service_category"]),
            get_part_family_concept(selection["part_family"]),
            get_part_type_concept(selection["part_type"]),
        )
    except (KeyError, ServiceDiscoveryRdfMappingError) as exc:
        raise ServiceDiscoverySparqlQueryBuildError(
            f"Cannot build harmonized SPARQL query for uncontrolled selection: {selection}"
        ) from exc


def _uri(value: URIRef) -> str:
    value_text = str(value)
    namespace_text = str(MDC)
    if value_text.startswith(namespace_text):
        return f"mdc:{value_text.removeprefix(namespace_text)}"
    return value.n3()


def build_service_discovery_candidate_query(
    canonical_request: CanonicalServiceDiscoverySearchRequest,
) -> str:
    service_category, part_family, part_type = _resolve_selection(canonical_request)
    values = f"({_uri(service_category)} {_uri(part_family)} {_uri(part_type)})"

    return f"""
{PREFIXES}

SELECT
    ?provider
    ?providerId
    ?providerName
    ?offering
    ?offeringId
    ?offeringName
    ?offeringSupportStatus
    ?partTypeSupport
    ?partTypeSupportStatus
    ?partTypeSourceType
    ?partTypeConfidence
    ?partTypeSourceNote
WHERE {{
    VALUES (?requestedServiceCategory ?requestedPartFamily ?requestedPartType) {{
        {values}
    }}

    ?offering a mdc:ProviderOffering ;
        mdc:offeredBy ?provider ;
        mdc:offeringId ?offeringId ;
        mdc:displayName ?offeringName ;
        mdc:serviceCategory ?requestedServiceCategory ;
        mdc:supportsPartFamily ?requestedPartFamily ;
        mdc:supportStatus ?offeringSupportStatus .

    ?provider a mdc:MaaSProvider ;
        mdc:providerId ?providerId ;
        mdc:displayName ?providerName .

    OPTIONAL {{
        ?offering mdc:hasPartTypeSupport ?partTypeSupport .
        ?partTypeSupport mdc:partType ?supportPartType ;
            mdc:supportStatus ?partTypeSupportStatus ;
            mdc:sourceType ?partTypeSourceType ;
            mdc:confidence ?partTypeConfidence .
        FILTER(?supportPartType = ?requestedPartType)
        OPTIONAL {{ ?partTypeSupport mdc:sourceNote ?partTypeSourceNote . }}
    }}
}}
ORDER BY ?providerId ?offeringId
""".strip()


def build_service_discovery_evidence_query(
    offering_resources: list[URIRef],
) -> str:
    if not offering_resources:
        raise ServiceDiscoverySparqlQueryBuildError(
            "Cannot build evidence query without offering resources."
        )
    for offering in offering_resources:
        if not isinstance(offering, URIRef):
            raise ServiceDiscoverySparqlQueryBuildError(
                "Evidence query offering resources must be RDFLib URIRef values."
            )

    values = "\n        ".join(_uri(offering) for offering in offering_resources)

    return f"""
{PREFIXES}

SELECT
    ?offering
    ?evidenceKind
    ?evidence
    ?fieldCode
    ?capabilityField
    ?appliesToPartType
    ?partTypeCode
    ?minValue
    ?maxValue
    ?exactValue
    ?rawValue
    ?unit
    ?qualifier
    ?approximate
    ?qualityStandard
    ?bestClass
    ?comparisonRule
    ?normalizedOrder
    ?explicitNullField
    ?sequenceIndex
    ?material
    ?materialCode
    ?availableGrade
    ?gradeEvidence
    ?orderedAvailableGrade
    ?gradeSequenceIndex
    ?process
    ?processCode
    ?deliveryMode
    ?certification
    ?certificationCode
    ?evidenceScope
    ?sourceType
    ?confidence
    ?sourceNote
WHERE {{
    VALUES ?offering {{
        {values}
    }}

    {{
        ?offering mdc:hasFamilyCapability ?evidence .
        BIND("family_capability" AS ?evidenceKind)
        ?evidence mdc:fieldCode ?fieldCode ;
            mdc:capabilityField ?capabilityField .
        OPTIONAL {{ ?evidence mdc:minValue ?minValue . }}
        OPTIONAL {{ ?evidence mdc:maxValue ?maxValue . }}
        OPTIONAL {{ ?evidence mdc:exactValue ?exactValue . }}
        OPTIONAL {{ ?evidence mdc:rawValue ?rawValue . }}
        OPTIONAL {{ ?evidence mdc:unit ?unit . }}
        OPTIONAL {{ ?evidence mdc:qualifier ?qualifier . }}
        OPTIONAL {{ ?evidence mdc:approximate ?approximate . }}
        OPTIONAL {{ ?evidence mdc:qualityStandard ?qualityStandard . }}
        OPTIONAL {{ ?evidence mdc:bestClass ?bestClass . }}
        OPTIONAL {{ ?evidence mdc:comparisonRule ?comparisonRule . }}
        OPTIONAL {{ ?evidence mdc:normalizedOrder ?normalizedOrder . }}
        OPTIONAL {{ ?evidence mdc:explicitNullField ?explicitNullField . }}
        OPTIONAL {{ ?evidence mdc:sourceType ?sourceType . }}
        OPTIONAL {{ ?evidence mdc:confidence ?confidence . }}
        OPTIONAL {{ ?evidence mdc:sourceNote ?sourceNote . }}
    }}
    UNION
    {{
        ?offering mdc:hasPartTypeCapability ?evidence .
        BIND("part_type_capability" AS ?evidenceKind)
        ?evidence mdc:fieldCode ?fieldCode ;
            mdc:capabilityField ?capabilityField ;
            mdc:appliesToPartType ?appliesToPartType ;
            mdc:partTypeCode ?partTypeCode .
        OPTIONAL {{ ?evidence mdc:minValue ?minValue . }}
        OPTIONAL {{ ?evidence mdc:maxValue ?maxValue . }}
        OPTIONAL {{ ?evidence mdc:exactValue ?exactValue . }}
        OPTIONAL {{ ?evidence mdc:rawValue ?rawValue . }}
        OPTIONAL {{ ?evidence mdc:unit ?unit . }}
        OPTIONAL {{ ?evidence mdc:qualifier ?qualifier . }}
        OPTIONAL {{ ?evidence mdc:approximate ?approximate . }}
        OPTIONAL {{ ?evidence mdc:qualityStandard ?qualityStandard . }}
        OPTIONAL {{ ?evidence mdc:bestClass ?bestClass . }}
        OPTIONAL {{ ?evidence mdc:comparisonRule ?comparisonRule . }}
        OPTIONAL {{ ?evidence mdc:normalizedOrder ?normalizedOrder . }}
        OPTIONAL {{ ?evidence mdc:explicitNullField ?explicitNullField . }}
        OPTIONAL {{ ?evidence mdc:sourceType ?sourceType . }}
        OPTIONAL {{ ?evidence mdc:confidence ?confidence . }}
        OPTIONAL {{ ?evidence mdc:sourceNote ?sourceNote . }}
    }}
    UNION
    {{
        ?offering mdc:hasGenericCapability ?evidence .
        BIND("generic_capability" AS ?evidenceKind)
        ?evidence mdc:fieldCode ?fieldCode ;
            mdc:capabilityField ?capabilityField .
        OPTIONAL {{ ?evidence mdc:minValue ?minValue . }}
        OPTIONAL {{ ?evidence mdc:maxValue ?maxValue . }}
        OPTIONAL {{ ?evidence mdc:exactValue ?exactValue . }}
        OPTIONAL {{ ?evidence mdc:rawValue ?rawValue . }}
        OPTIONAL {{ ?evidence mdc:unit ?unit . }}
        OPTIONAL {{ ?evidence mdc:qualifier ?qualifier . }}
        OPTIONAL {{ ?evidence mdc:approximate ?approximate . }}
        OPTIONAL {{ ?evidence mdc:qualityStandard ?qualityStandard . }}
        OPTIONAL {{ ?evidence mdc:bestClass ?bestClass . }}
        OPTIONAL {{ ?evidence mdc:comparisonRule ?comparisonRule . }}
        OPTIONAL {{ ?evidence mdc:normalizedOrder ?normalizedOrder . }}
        OPTIONAL {{ ?evidence mdc:explicitNullField ?explicitNullField . }}
        OPTIONAL {{ ?evidence mdc:sourceType ?sourceType . }}
        OPTIONAL {{ ?evidence mdc:confidence ?confidence . }}
        OPTIONAL {{ ?evidence mdc:sourceNote ?sourceNote . }}
    }}
    UNION
    {{
        ?offering mdc:hasMaterialEvidence ?evidence .
        BIND("material" AS ?evidenceKind)
        ?evidence mdc:material ?material ;
            mdc:materialCode ?materialCode .
        OPTIONAL {{ ?evidence mdc:sequenceIndex ?sequenceIndex . }}
        OPTIONAL {{ ?evidence mdc:availableGrade ?availableGrade . }}
        OPTIONAL {{
            ?evidence mdc:hasAvailableGradeEvidence ?gradeEvidence .
            ?gradeEvidence a mdc:AvailableGradeEvidence ;
                mdc:availableGrade ?orderedAvailableGrade ;
                mdc:sequenceIndex ?gradeSequenceIndex .
        }}
        OPTIONAL {{ ?evidence mdc:sourceType ?sourceType . }}
        OPTIONAL {{ ?evidence mdc:confidence ?confidence . }}
        OPTIONAL {{ ?evidence mdc:sourceNote ?sourceNote . }}
    }}
    UNION
    {{
        ?offering mdc:hasProcessEvidence ?evidence .
        BIND("process" AS ?evidenceKind)
        ?evidence mdc:process ?process ;
            mdc:processCode ?processCode .
        OPTIONAL {{ ?evidence mdc:sequenceIndex ?sequenceIndex . }}
        OPTIONAL {{ ?evidence mdc:deliveryMode ?deliveryMode . }}
        OPTIONAL {{ ?evidence mdc:sourceType ?sourceType . }}
        OPTIONAL {{ ?evidence mdc:confidence ?confidence . }}
        OPTIONAL {{ ?evidence mdc:sourceNote ?sourceNote . }}
    }}
    UNION
    {{
        ?offering mdc:offeredBy ?provider .
        ?provider mdc:hasCertificationEvidence ?evidence .
        BIND("certification" AS ?evidenceKind)
        BIND("provider" AS ?evidenceScope)
        ?evidence mdc:certification ?certification ;
            mdc:certificationCode ?certificationCode .
        OPTIONAL {{ ?evidence mdc:sequenceIndex ?sequenceIndex . }}
        OPTIONAL {{ ?evidence mdc:sourceType ?sourceType . }}
        OPTIONAL {{ ?evidence mdc:confidence ?confidence . }}
        OPTIONAL {{ ?evidence mdc:sourceNote ?sourceNote . }}
    }}
}}
ORDER BY ?offering ?evidenceKind ?sequenceIndex ?evidence ?gradeSequenceIndex ?availableGrade
""".strip()
