from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import skipUnless

from django.test import SimpleTestCase
from rdflib import Graph

from apps.ontology.service_discovery_rdf_generator import (
    build_service_discovery_graph,
    default_service_discovery_turtle_path,
)
from apps.search.service_discovery_request import CanonicalServiceDiscoverySearchRequest
from apps.search.service_discovery_sparql_query_builder import ServiceDiscoverySparqlQueryBuildError
from apps.search.service_discovery_sparql_service import (
    ServiceDiscoverySparqlRetrievalError,
    load_service_discovery_rdf_graph,
    retrieve_service_discovery_candidates,
)


def canonical(
    service_category="precision_gears",
    part_family="gear",
    part_type="spur_gear",
    *,
    requirements=None,
    match_policy=None,
) -> CanonicalServiceDiscoverySearchRequest:
    return CanonicalServiceDiscoverySearchRequest(
        request_id="req",
        consumer_id="consumer",
        selection={
            "service_category": service_category,
            "part_family": part_family,
            "part_type": part_type,
        },
        requirements=requirements or {},
        match_policy=match_policy or {},
    )


def candidate_by_provider(response: dict, provider_id: str):
    for candidate in response["candidates"]:
        if candidate["provider"]["provider_id"] == provider_id:
            return candidate
    return None


def fields(evidence: list[dict]) -> set[str]:
    return {item.get("field_code") for item in evidence}


EXPECTED_TASOWHEEL_PROCESSES = [
    "machining",
    "hobbing",
    "gear_shaping",
    "deburring",
    "hard_turning",
    "grinding",
    "tooth_grinding",
    "gear_grinding",
    "gear_cutting",
    "surface_grinding",
    "milling",
    "turn_mill",
]

EXPECTED_TASOWHEEL_CERTIFICATIONS = [
    "ISO9001_2015",
    "ISO14001_2015",
    "ISO_TS_16949_partial",
    "APQP",
]


class ServiceDiscoverySparqlServiceTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.graph = build_service_discovery_graph()

    def test_load_service_discovery_rdf_graph_parses_temporary_harmonized_turtle(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "harmonized.ttl"
            self.graph.serialize(destination=str(path), format="turtle")

            loaded = load_service_discovery_rdf_graph(path)

        self.assertGreater(len(loaded), 0)

    def test_missing_invalid_and_empty_graph_errors(self):
        with self.assertRaises(ServiceDiscoverySparqlRetrievalError):
            load_service_discovery_rdf_graph(Path("missing_harmonized.ttl"))

        with TemporaryDirectory() as temp_dir:
            invalid = Path(temp_dir) / "invalid.ttl"
            invalid.write_text("@prefix broken", encoding="utf-8")
            with self.assertRaises(ServiceDiscoverySparqlRetrievalError):
                load_service_discovery_rdf_graph(invalid)

        with self.assertRaises(ServiceDiscoverySparqlRetrievalError):
            retrieve_service_discovery_candidates(canonical(), graph=Graph())

    def test_graph_argument_bypasses_file_loading_and_no_legacy_bundled_offering_returns(self):
        response = retrieve_service_discovery_candidates(canonical(), graph=self.graph)

        offering_ids = {
            candidate["offering"]["offering_id"]
            for candidate in response["candidates"]
        }
        self.assertIn("tasowheel_precision_gears", offering_ids)
        self.assertNotIn("tasowheel_gears_shafts_precision", offering_ids)

    @skipUnless(default_service_discovery_turtle_path().exists(), "Default H6 harmonized Turtle is absent.")
    def test_optional_default_generated_turtle_smoke(self):
        response = retrieve_service_discovery_candidates(canonical())

        self.assertTrue(response["status"]["retrieval_executed"])
        self.assertTrue(response["candidates"])

    def test_confirmed_tasowheel_gear_subtypes_retrieve_confirmed_support(self):
        for part_type in ["spur_gear", "helical_gear", "bevel_gear", "worm_gear"]:
            response = retrieve_service_discovery_candidates(
                canonical(part_type=part_type),
                graph=self.graph,
            )
            tasowheel = candidate_by_provider(response, "tasowheel")

            self.assertEqual(
                tasowheel["requested_part_type_support"]["evidence_status"],
                "confirmed",
                part_type,
            )
            self.assertEqual(tasowheel["requested_part_type_support"]["source_type"], "provider_confirmed")
            self.assertEqual(tasowheel["requested_part_type_support"]["confidence"], "declared")

    def test_unasserted_tasowheel_gear_and_shaft_subtypes_are_not_unsupported(self):
        crown = retrieve_service_discovery_candidates(
            canonical(part_type="crown_gear"),
            graph=self.graph,
        )
        tasowheel_crown = candidate_by_provider(crown, "tasowheel")
        self.assertIsNotNone(tasowheel_crown)
        self.assertEqual(
            tasowheel_crown["requested_part_type_support"]["evidence_status"],
            "not_asserted",
        )
        self.assertIsNone(tasowheel_crown["requested_part_type_support"]["support_status"])
        self.assertIsNone(tasowheel_crown["requested_part_type_support"]["source_type"])
        self.assertIsNone(tasowheel_crown["requested_part_type_support"]["confidence"])
        self.assertNotEqual(
            tasowheel_crown["requested_part_type_support"]["evidence_status"],
            "unsupported",
        )

        for part_type in ["stepped_shaft", "worm_shaft"]:
            response = retrieve_service_discovery_candidates(
                canonical("precision_shafts", "shaft", part_type),
                graph=self.graph,
            )
            tasowheel = candidate_by_provider(response, "tasowheel")
            self.assertIsNotNone(tasowheel, part_type)
            self.assertEqual(
                tasowheel["requested_part_type_support"]["evidence_status"],
                "not_asserted",
                part_type,
            )

    def test_confirmed_tasowheel_shaft_subtypes_retrieve_confirmed_support(self):
        for part_type in ["splined_shaft", "plain_shaft", "hollow_shaft"]:
            response = retrieve_service_discovery_candidates(
                canonical("precision_shafts", "shaft", part_type),
                graph=self.graph,
            )
            tasowheel = candidate_by_provider(response, "tasowheel")

            self.assertEqual(
                tasowheel["requested_part_type_support"]["evidence_status"],
                "confirmed",
                part_type,
            )

    def test_precipart_crown_gear_candidate_is_not_promoted(self):
        response = retrieve_service_discovery_candidates(
            canonical(part_type="crown_gear"),
            graph=self.graph,
        )
        precipart = candidate_by_provider(response, "precipart")

        self.assertEqual(
            precipart["requested_part_type_support"]["evidence_status"],
            "candidate_requiring_confirmation",
        )
        self.assertEqual(
            precipart["requested_part_type_support"]["support_status"],
            "candidate_requiring_confirmation",
        )
        self.assertEqual(precipart["requested_part_type_support"]["source_type"], "public_web")
        self.assertEqual(precipart["requested_part_type_support"]["confidence"], "inferred")

    def test_retrieval_does_not_perform_matching_or_scoring(self):
        response = retrieve_service_discovery_candidates(
            canonical(
                requirements={"part_family_specifications": {"module": {"exact": 2}}},
                match_policy={"unknown_policy": "reject_unknown", "minimum_score": 1.0},
            ),
            graph=self.graph,
        )

        self.assertTrue(response["status"]["retrieval_executed"])
        self.assertEqual(response["status"]["retrieval_engine"], "local_harmonized_sparql_rdflib")
        self.assertFalse(response["status"]["matching_executed"])
        self.assertNotIn("result_count", response)
        for candidate in response["candidates"]:
            self.assertNotIn("score", candidate)
            self.assertNotIn("selection_score", candidate)
            self.assertNotIn("optional_score", candidate)
            self.assertNotIn("match", candidate)
            self.assertNotIn("matched_attributes", candidate)
            self.assertNotIn("unmatched_attributes", candidate)
            self.assertNotIn("unknown_attributes", candidate)
            self.assertNotIn("hard_filters_passed", candidate)
            self.assertNotIn(
                candidate["requested_part_type_support"]["evidence_status"],
                {"full_match", "partial_match", "unknown_match"},
            )
        self.assertEqual(response["query_interpretation"]["requirements"]["part_family_specifications"]["module"]["exact"], 2)

    def test_tasowheel_gear_evidence_projection(self):
        response = retrieve_service_discovery_candidates(canonical(), graph=self.graph)
        tasowheel = candidate_by_provider(response, "tasowheel")
        family = tasowheel["evidence"]["family_capabilities"]

        self.assertTrue({"module", "diametral_pitch", "outside_diameter_mm", "gear_quality"} <= fields(family))
        dp = next(item for item in family if item["field_code"] == "diametral_pitch")
        quality = next(item for item in family if item["field_code"] == "gear_quality")
        self.assertEqual(dp["raw"], "DP 85-2.5")
        self.assertEqual(float(dp["min"]), 2.5)
        self.assertEqual(float(dp["max"]), 85.0)
        self.assertEqual(dp["normalized_order"], "ascending")
        self.assertEqual(quality["quality_standard"], "DIN")
        self.assertEqual(float(quality["best_class"]), 4.0)
        self.assertEqual(quality["comparison_rule"], "lower_or_equal_is_better")

    def test_tasowheel_shaft_evidence_projection_and_scope(self):
        response = retrieve_service_discovery_candidates(
            canonical("precision_shafts", "shaft", "splined_shaft"),
            graph=self.graph,
        )
        tasowheel = candidate_by_provider(response, "tasowheel")
        family = tasowheel["evidence"]["family_capabilities"]
        part_type = tasowheel["evidence"]["part_type_capabilities"]

        self.assertTrue({"length_mm", "outer_diameter_mm"} <= fields(family))
        length = next(item for item in family if item["field_code"] == "length_mm")
        self.assertEqual(float(length["max"]), 500.0)
        self.assertEqual(length["source_type"], "public_web")
        self.assertEqual(length["confidence"], "publicly_confirmed")

        spline = next(item for item in part_type if item["field_code"] == "spline_module")
        self.assertEqual(spline["part_type_code"], "splined_shaft")
        self.assertEqual(float(spline["min"]), 0.3)
        self.assertEqual(float(spline["max"]), 10.0)
        self.assertNotIn("spline_module", fields(family))

    def test_tasowheel_material_process_certification_and_deferred_fields(self):
        response = retrieve_service_discovery_candidates(canonical(), graph=self.graph)
        tasowheel = candidate_by_provider(response, "tasowheel")
        evidence = tasowheel["evidence"]

        materials = evidence["materials"]
        self.assertTrue(any(item["material_code"] == "alloyed_carburizing_steel" for item in materials))
        self.assertEqual(
            materials[0]["available_grades"],
            ["18CrNiMo7-6", "16MnCr5", "20MnCr5"],
        )
        self.assertEqual(len(materials[0]["available_grades"]), 3)
        self.assertNotIn("material_grades", materials[0])
        self.assertNotIn("sequence_index", str(materials[0]))

        process_codes = [item["process_code"] for item in evidence["processes"]]
        self.assertEqual(process_codes, EXPECTED_TASOWHEEL_PROCESSES)
        self.assertNotIn("sequence_index", str(evidence["processes"]))

        certification_codes = [item["certification_code"] for item in evidence["certifications"]]
        self.assertEqual(certification_codes, EXPECTED_TASOWHEEL_CERTIFICATIONS)
        self.assertTrue(all(item["evidence_scope"] == "provider" for item in evidence["certifications"]))
        self.assertNotIn("sequence_index", str(evidence["certifications"]))

        surface_finish = next(
            item
            for item in evidence["generic_capabilities"]
            if item["field_code"] == "surface_finish_ra_um"
        )
        self.assertIn("max", surface_finish)
        self.assertIsNone(surface_finish["max"])
        self.assertEqual(surface_finish["source_type"], "not_confirmed")
        self.assertEqual(surface_finish["confidence"], "unknown")

        all_fields = fields(evidence["family_capabilities"]) | fields(evidence["part_type_capabilities"]) | fields(evidence["generic_capabilities"])
        for forbidden_field in [
            "face_width_mm",
            "tolerance_mm",
            "spline_diametral_pitch",
            "shaft_quality",
            "spline_quality",
        ]:
            self.assertNotIn(forbidden_field, all_fields)

    def test_tasowheel_shaft_surface_finish_explicit_null_and_ordered_evidence(self):
        response = retrieve_service_discovery_candidates(
            canonical("precision_shafts", "shaft", "splined_shaft"),
            graph=self.graph,
        )
        tasowheel = candidate_by_provider(response, "tasowheel")
        evidence = tasowheel["evidence"]

        surface_finish = next(
            item
            for item in evidence["generic_capabilities"]
            if item["field_code"] == "surface_finish_ra_um"
        )
        self.assertIn("max", surface_finish)
        self.assertIsNone(surface_finish["max"])
        self.assertEqual(
            evidence["materials"][0]["available_grades"],
            ["18CrNiMo7-6", "16MnCr5", "20MnCr5"],
        )
        self.assertEqual(
            [item["process_code"] for item in evidence["processes"]],
            EXPECTED_TASOWHEEL_PROCESSES,
        )
        self.assertEqual(
            [item["certification_code"] for item in evidence["certifications"]],
            EXPECTED_TASOWHEEL_CERTIFICATIONS,
        )
        self.assertNotIn("tolerance_mm", fields(evidence["generic_capabilities"]))

    def test_candidate_ordering_and_evidence_deduplication(self):
        response = retrieve_service_discovery_candidates(
            canonical(part_type="crown_gear"),
            graph=self.graph,
        )
        statuses = [
            candidate["requested_part_type_support"]["evidence_status"]
            for candidate in response["candidates"]
        ]
        self.assertEqual(statuses, sorted(statuses, key={"confirmed": 0, "candidate_requiring_confirmation": 1, "not_asserted": 2}.get))

        tasowheel = candidate_by_provider(response, "tasowheel")
        self.assertIsNotNone(tasowheel)
        process_codes = [item["process_code"] for item in tasowheel["evidence"]["processes"]]
        material_codes = [item["material_code"] for item in tasowheel["evidence"]["materials"]]
        cert_codes = [item["certification_code"] for item in tasowheel["evidence"]["certifications"]]
        self.assertEqual(len(process_codes), len(set(process_codes)))
        self.assertEqual(len(material_codes), len(set(material_codes)))
        self.assertEqual(len(cert_codes), len(set(cert_codes)))

    def test_unmapped_selection_raises_clear_error(self):
        with self.assertRaises(ServiceDiscoverySparqlQueryBuildError):
            retrieve_service_discovery_candidates(
                canonical(part_type="not_a_part_type"),
                graph=self.graph,
            )
