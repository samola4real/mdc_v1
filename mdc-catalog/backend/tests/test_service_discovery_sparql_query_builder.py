from django.test import SimpleTestCase

from apps.search.service_discovery_request import CanonicalServiceDiscoverySearchRequest
from apps.search.service_discovery_sparql_query_builder import (
    ServiceDiscoverySparqlQueryBuildError,
    build_service_discovery_candidate_query,
    build_service_discovery_evidence_query,
)
from apps.ontology.service_discovery_rdf_mappings import offering_resource


def canonical(selection: dict) -> CanonicalServiceDiscoverySearchRequest:
    return CanonicalServiceDiscoverySearchRequest(
        request_id="req",
        consumer_id="consumer",
        selection=selection,
        requirements={},
        match_policy={},
    )


class ServiceDiscoverySparqlQueryBuilderTests(SimpleTestCase):
    def test_candidate_query_uses_controlled_gear_concepts_and_optional_part_type_support(self):
        query = build_service_discovery_candidate_query(
            canonical(
                {
                    "service_category": "precision_gears",
                    "part_family": "gear",
                    "part_type": "spur_gear",
                }
            )
        )

        self.assertIn("mdc:PrecisionGears", query)
        self.assertIn("mdc:Gear", query)
        self.assertIn("mdc:SpurGear", query)
        self.assertIn("?providerId", query)
        self.assertIn("?offeringId", query)
        self.assertIn("mdc:serviceCategory ?requestedServiceCategory", query)
        self.assertIn("mdc:supportsPartFamily ?requestedPartFamily", query)
        self.assertIn("OPTIONAL", query)
        self.assertIn("mdc:partType ?supportPartType", query)
        self.assertIn("FILTER(?supportPartType = ?requestedPartType)", query)
        self.assertIn("?partTypeSourceType", query)
        self.assertIn("?partTypeConfidence", query)
        self.assertIn("ORDER BY ?providerId ?offeringId", query)

        optional_start = query.index("OPTIONAL")
        self.assertNotIn("mdc:partType ?supportPartType", query[:optional_start])
        self.assertNotIn("FILTER(?supportPartType = ?requestedPartType)", query[:optional_start])

    def test_candidate_query_supports_shaft_selection(self):
        query = build_service_discovery_candidate_query(
            canonical(
                {
                    "service_category": "precision_shafts",
                    "part_family": "shaft",
                    "part_type": "splined_shaft",
                }
            )
        )

        self.assertIn("mdc:PrecisionShafts", query)
        self.assertIn("mdc:Shaft", query)
        self.assertIn("mdc:SplinedShaft", query)

    def test_unknown_selection_raises_without_raw_query_construction(self):
        with self.assertRaises(ServiceDiscoverySparqlQueryBuildError):
            build_service_discovery_candidate_query(
                canonical(
                    {
                        "service_category": "precision_gears . ?x ?y ?z",
                        "part_family": "gear",
                        "part_type": "spur_gear",
                    }
                )
            )

    def test_evidence_query_rejects_empty_or_non_uri_values(self):
        with self.assertRaises(ServiceDiscoverySparqlQueryBuildError):
            build_service_discovery_evidence_query([])

        with self.assertRaises(ServiceDiscoverySparqlQueryBuildError):
            build_service_discovery_evidence_query(["not a URIRef"])

    def test_evidence_query_contains_values_unions_and_evidence_projection(self):
        query = build_service_discovery_evidence_query(
            [offering_resource("tasowheel_precision_gears")]
        )

        self.assertIn("VALUES ?offering", query)
        self.assertIn("mdc:offering_tasowheel_precision_gears", query)
        self.assertIn("mdc:hasFamilyCapability", query)
        self.assertIn("mdc:hasPartTypeCapability", query)
        self.assertIn("mdc:hasGenericCapability", query)
        self.assertIn("mdc:hasMaterialEvidence", query)
        self.assertIn("mdc:hasProcessEvidence", query)
        self.assertIn("mdc:hasCertificationEvidence", query)
        self.assertIn("UNION", query)
        self.assertIn("?sourceType", query)
        self.assertIn("?confidence", query)
        self.assertIn("?availableGrade", query)
        self.assertIn("?normalizedOrder", query)
        self.assertIn("mdc:normalizedOrder", query)
        self.assertIn("?explicitNullField", query)
        self.assertIn("mdc:explicitNullField", query)
        self.assertIn("?sequenceIndex", query)
        self.assertIn("mdc:sequenceIndex", query)
        self.assertIn("?gradeEvidence", query)
        self.assertIn("?orderedAvailableGrade", query)
        self.assertIn("?gradeSequenceIndex", query)
        self.assertIn("mdc:hasAvailableGradeEvidence", query)
        self.assertIn("mdc:AvailableGradeEvidence", query)
        self.assertNotIn("supportsMaterialGrade", query)
        self.assertNotIn("tasowheel_gears_shafts_precision", query)
