import json
from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from rdflib import Literal, URIRef

from apps.ontology.service_discovery_rdf_mappings import offering_resource
from apps.search.service_discovery_fuseki_service import (
    REMOTE_RETRIEVAL_ENGINE,
    ServiceDiscoveryFusekiRetrievalError,
    execute_fuseki_sparql_query,
    retrieve_service_discovery_candidates_from_fuseki,
)
from apps.search.service_discovery_sparql_query_builder import build_service_discovery_evidence_query
from apps.search.service_discovery_request import CanonicalServiceDiscoverySearchRequest


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


class MockResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.body


def sparql_json(bindings: list[dict]) -> bytes:
    return json.dumps({"head": {"vars": []}, "results": {"bindings": bindings}}).encode("utf-8")


def literal(value) -> Literal:
    return Literal(value)


def uri(value: str) -> URIRef:
    return URIRef(value)


def sparql_literal(value: str, *, datatype: str | None = None) -> dict:
    binding = {"type": "literal", "value": value}
    if datatype:
        binding["datatype"] = datatype
    return binding


def sparql_uri(value: str) -> dict:
    return {"type": "uri", "value": value}


def candidate_row(
    provider_id: str,
    offering_id: str,
    *,
    support_status: str | None,
) -> dict:
    row = {
        "provider": uri(f"https://maasai-project.eu/ontology/mdc#provider_{provider_id}"),
        "providerId": literal(provider_id),
        "providerName": literal(provider_id.title()),
        "offering": offering_resource(offering_id),
        "offeringId": literal(offering_id),
        "offeringName": literal(offering_id.replace("_", " ").title()),
        "offeringSupportStatus": literal("confirmed"),
    }
    if support_status is not None:
        row.update(
            {
                "partTypeSupport": uri(f"https://maasai-project.eu/ontology/mdc#pts_{offering_id}"),
                "partTypeSupportStatus": literal(support_status),
                "partTypeSourceType": literal(
                    "public_web" if support_status == "candidate_requiring_confirmation" else "provider_confirmed"
                ),
                "partTypeConfidence": literal(
                    "inferred" if support_status == "candidate_requiring_confirmation" else "declared"
                ),
            }
        )
    return row


def family_capability_row(offering_id: str, field_code: str, evidence_id: str, **values) -> dict:
    row = {
        "offering": offering_resource(offering_id),
        "evidenceKind": literal("family_capability"),
        "evidence": uri(f"https://maasai-project.eu/ontology/mdc#{evidence_id}"),
        "fieldCode": literal(field_code),
        "capabilityField": uri(f"https://maasai-project.eu/ontology/mdc#{field_code}"),
        "sourceType": literal("provider_confirmed"),
        "confidence": literal("declared"),
    }
    row.update(values)
    return row


def generic_capability_row(offering_id: str, field_code: str, evidence_id: str, **values) -> dict:
    row = {
        "offering": offering_resource(offering_id),
        "evidenceKind": literal("generic_capability"),
        "evidence": uri(f"https://maasai-project.eu/ontology/mdc#{evidence_id}"),
        "fieldCode": literal(field_code),
        "capabilityField": uri(f"https://maasai-project.eu/ontology/mdc#{field_code}"),
        "sourceType": literal("not_confirmed"),
        "confidence": literal("unknown"),
    }
    row.update(values)
    return row


def material_row(
    offering_id: str,
    material_evidence: URIRef,
    *,
    flat_grade: str,
    ordered_grade: str,
    grade_index: int,
) -> dict:
    return {
        "offering": offering_resource(offering_id),
        "evidenceKind": literal("material"),
        "evidence": material_evidence,
        "material": uri("https://maasai-project.eu/ontology/mdc#AlloyedCarburizingSteel"),
        "materialCode": literal("alloyed_carburizing_steel"),
        "sequenceIndex": literal(0),
        "availableGrade": literal(flat_grade),
        "gradeEvidence": uri(f"https://maasai-project.eu/ontology/mdc#grade_{grade_index}"),
        "orderedAvailableGrade": literal(ordered_grade),
        "gradeSequenceIndex": literal(grade_index),
        "sourceType": literal("provider_confirmed"),
        "confidence": literal("declared"),
    }


def process_row(offering_id: str, process_evidence: URIRef, process_code: str, sequence_index: int) -> dict:
    return {
        "offering": offering_resource(offering_id),
        "evidenceKind": literal("process"),
        "evidence": process_evidence,
        "process": uri(f"https://maasai-project.eu/ontology/mdc#{process_code}"),
        "processCode": literal(process_code),
        "sequenceIndex": literal(sequence_index),
        "deliveryMode": literal("unspecified"),
        "sourceType": literal("provider_confirmed"),
        "confidence": literal("declared"),
    }


def certification_row(offering_id: str, certification_evidence: URIRef, code: str, sequence_index: int) -> dict:
    return {
        "offering": offering_resource(offering_id),
        "evidenceKind": literal("certification"),
        "evidence": certification_evidence,
        "certification": uri(f"https://maasai-project.eu/ontology/mdc#{code}"),
        "certificationCode": literal(code),
        "evidenceScope": literal("provider"),
        "sequenceIndex": literal(sequence_index),
        "sourceType": literal("provider_confirmed"),
        "confidence": literal("declared"),
    }


class ServiceDiscoveryFusekiServiceTests(SimpleTestCase):
    @override_settings(SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="")
    def test_missing_endpoint_configuration_raises(self):
        with self.assertRaises(ServiceDiscoveryFusekiRetrievalError):
            execute_fuseki_sparql_query("SELECT * WHERE { ?s ?p ?o }")

    @override_settings(SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="http://configured.example/query")
    @patch("apps.search.service_discovery_fuseki_service.urlopen")
    def test_explicit_endpoint_overrides_setting_and_sends_read_query(self, mock_urlopen):
        mock_urlopen.return_value = MockResponse(sparql_json([]))

        execute_fuseki_sparql_query(
            "SELECT * WHERE { ?s ?p ?o }",
            endpoint="http://explicit.example/query",
            timeout_seconds=3,
        )

        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://explicit.example/query")
        self.assertEqual(mock_urlopen.call_args.kwargs["timeout"], 3)
        self.assertEqual(request.get_method(), "POST")
        body = parse_qs(request.data.decode("utf-8"))
        self.assertEqual(body["query"], ["SELECT * WHERE { ?s ?p ?o }"])
        self.assertNotIn("update", body)
        self.assertNotIn("load", body)
        headers = {key.lower(): value for key, value in request.header_items()}
        self.assertEqual(headers["accept"], "application/sparql-results+json")
        self.assertEqual(headers["content-type"], "application/x-www-form-urlencoded")

    @override_settings(SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="http://configured.example/query")
    @patch("apps.search.service_discovery_fuseki_service.urlopen")
    def test_configured_endpoint_is_used_without_explicit_endpoint(self, mock_urlopen):
        mock_urlopen.return_value = MockResponse(sparql_json([]))

        execute_fuseki_sparql_query("SELECT * WHERE { ?s ?p ?o }")

        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://configured.example/query")

    @override_settings(SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="http://configured.example/query")
    def test_http_and_result_errors_raise_clear_retrieval_error(self):
        with patch("apps.search.service_discovery_fuseki_service.urlopen", side_effect=URLError("down")):
            with self.assertRaises(ServiceDiscoveryFusekiRetrievalError):
                execute_fuseki_sparql_query("SELECT * WHERE { ?s ?p ?o }")

        http_error = HTTPError("http://configured.example/query", 500, "error", {}, BytesIO(b"server error"))
        with patch("apps.search.service_discovery_fuseki_service.urlopen", side_effect=http_error):
            with self.assertRaises(ServiceDiscoveryFusekiRetrievalError):
                execute_fuseki_sparql_query("SELECT * WHERE { ?s ?p ?o }")

        with patch("apps.search.service_discovery_fuseki_service.urlopen", return_value=MockResponse(b"not json")):
            with self.assertRaises(ServiceDiscoveryFusekiRetrievalError):
                execute_fuseki_sparql_query("SELECT * WHERE { ?s ?p ?o }")

        malformed_result = json.dumps({"results": {"bindings": [{"x": {"type": "bnode", "value": "abc"}}]}}).encode("utf-8")
        with patch("apps.search.service_discovery_fuseki_service.urlopen", return_value=MockResponse(malformed_result)):
            with self.assertRaises(ServiceDiscoveryFusekiRetrievalError):
                execute_fuseki_sparql_query("SELECT * WHERE { ?s ?p ?o }")

    @override_settings(SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT="http://configured.example/query")
    @patch("apps.search.service_discovery_fuseki_service.urlopen")
    def test_sparql_json_bindings_convert_to_rdflib_values(self, mock_urlopen):
        mock_urlopen.return_value = MockResponse(
            sparql_json(
                [
                    {
                        "offering": sparql_uri(str(offering_resource("tasowheel_precision_gears"))),
                        "offeringId": sparql_literal("tasowheel_precision_gears"),
                    }
                ]
            )
        )

        rows = execute_fuseki_sparql_query("SELECT * WHERE { ?s ?p ?o }")

        self.assertIsInstance(rows[0]["offering"], URIRef)
        self.assertEqual(str(rows[0]["offeringId"]), "tasowheel_precision_gears")

    @patch("apps.search.service_discovery_fuseki_service.build_service_discovery_candidate_query", return_value="candidate query")
    @patch("apps.search.service_discovery_fuseki_service.build_service_discovery_evidence_query", return_value="evidence query")
    @patch("apps.search.service_discovery_fuseki_service.execute_fuseki_sparql_query")
    def test_remote_retrieval_uses_h7_query_builders_and_remote_status(
        self,
        mock_execute,
        mock_evidence_query,
        mock_candidate_query,
    ):
        mock_execute.side_effect = [
            [candidate_row("tasowheel", "tasowheel_precision_gears", support_status="confirmed")],
            [],
        ]

        response = retrieve_service_discovery_candidates_from_fuseki(canonical(), endpoint="http://fuseki/query")

        mock_candidate_query.assert_called_once()
        mock_evidence_query.assert_called_once()
        self.assertEqual(mock_execute.call_args_list[0].args[0], "candidate query")
        self.assertEqual(mock_execute.call_args_list[1].args[0], "evidence query")
        self.assertTrue(response["status"]["retrieval_executed"])
        self.assertEqual(response["status"]["retrieval_engine"], REMOTE_RETRIEVAL_ENGINE)
        self.assertFalse(response["status"]["matching_executed"])
        self.assertNotIn("score", response["candidates"][0])
        self.assertNotIn("match", response["candidates"][0])

    @patch("apps.search.service_discovery_fuseki_service.build_service_discovery_candidate_query", return_value="candidate query")
    @patch("apps.search.service_discovery_fuseki_service.build_service_discovery_evidence_query")
    @patch("apps.search.service_discovery_fuseki_service.execute_fuseki_sparql_query", return_value=[])
    def test_no_candidate_response_is_successful_and_skips_evidence_query(
        self,
        mock_execute,
        mock_evidence_query,
        _mock_candidate_query,
    ):
        response = retrieve_service_discovery_candidates_from_fuseki(canonical(), endpoint="http://fuseki/query")

        self.assertEqual(response["candidates"], [])
        self.assertTrue(response["status"]["retrieval_executed"])
        self.assertEqual(mock_execute.call_count, 1)
        mock_evidence_query.assert_not_called()

    @patch("apps.search.service_discovery_fuseki_service.execute_fuseki_sparql_query")
    def test_confirmed_not_asserted_and_candidate_support_are_reconstructed(self, mock_execute):
        mock_execute.side_effect = [
            [
                candidate_row("tasowheel", "tasowheel_precision_gears", support_status=None),
                candidate_row("precipart", "precipart_precision_gears", support_status="candidate_requiring_confirmation"),
                candidate_row("alpha", "alpha_precision_gears", support_status="confirmed"),
            ],
            [],
        ]

        response = retrieve_service_discovery_candidates_from_fuseki(
            canonical(part_type="crown_gear"),
            endpoint="http://fuseki/query",
        )

        statuses = [
            candidate["requested_part_type_support"]["evidence_status"]
            for candidate in response["candidates"]
        ]
        self.assertEqual(statuses, ["confirmed", "candidate_requiring_confirmation", "not_asserted"])
        tasowheel = next(candidate for candidate in response["candidates"] if candidate["provider"]["provider_id"] == "tasowheel")
        self.assertEqual(tasowheel["requested_part_type_support"]["evidence_status"], "not_asserted")
        self.assertNotEqual(tasowheel["requested_part_type_support"]["evidence_status"], "unsupported")

    @patch("apps.search.service_discovery_fuseki_service.execute_fuseki_sparql_query")
    def test_mocked_evidence_rows_reconstruct_and_deduplicate_deterministically(self, mock_execute):
        offering_id = "tasowheel_precision_gears"
        material_evidence = uri("https://maasai-project.eu/ontology/mdc#material1")
        process_evidence = uri("https://maasai-project.eu/ontology/mdc#process1")
        certification_evidence = uri("https://maasai-project.eu/ontology/mdc#cert1")
        mock_execute.side_effect = [
            [candidate_row("tasowheel", offering_id, support_status="confirmed")],
            [
                family_capability_row(
                    offering_id,
                    "module",
                    "capability_module",
                    minValue=literal(0.3),
                    maxValue=literal(10),
                ),
                {
                    "offering": offering_resource(offering_id),
                    "evidenceKind": literal("part_type_capability"),
                    "evidence": uri("https://maasai-project.eu/ontology/mdc#spline_module"),
                    "fieldCode": literal("spline_module"),
                    "capabilityField": uri("https://maasai-project.eu/ontology/mdc#SplineModule"),
                    "appliesToPartType": uri("https://maasai-project.eu/ontology/mdc#SplinedShaft"),
                    "partTypeCode": literal("splined_shaft"),
                    "minValue": literal(0.3),
                    "maxValue": literal(10),
                    "sourceType": literal("provider_confirmed"),
                    "confidence": literal("declared"),
                },
                {
                    "offering": offering_resource(offering_id),
                    "evidenceKind": literal("generic_capability"),
                    "evidence": uri("https://maasai-project.eu/ontology/mdc#batch"),
                    "fieldCode": literal("batch_size"),
                    "capabilityField": uri("https://maasai-project.eu/ontology/mdc#BatchSize"),
                    "minValue": literal(100),
                    "maxValue": literal(2000),
                    "unit": literal("pcs"),
                    "sourceType": literal("provider_confirmed"),
                    "confidence": literal("declared"),
                },
                {
                    "offering": offering_resource(offering_id),
                    "evidenceKind": literal("material"),
                    "evidence": material_evidence,
                    "material": uri("https://maasai-project.eu/ontology/mdc#AlloyedCarburizingSteel"),
                    "materialCode": literal("alloyed_carburizing_steel"),
                    "availableGrade": literal("18CrNiMo7-6"),
                    "sourceType": literal("provider_confirmed"),
                    "confidence": literal("declared"),
                },
                {
                    "offering": offering_resource(offering_id),
                    "evidenceKind": literal("material"),
                    "evidence": material_evidence,
                    "material": uri("https://maasai-project.eu/ontology/mdc#AlloyedCarburizingSteel"),
                    "materialCode": literal("alloyed_carburizing_steel"),
                    "availableGrade": literal("18CrNiMo7-6"),
                    "sourceType": literal("provider_confirmed"),
                    "confidence": literal("declared"),
                },
                {
                    "offering": offering_resource(offering_id),
                    "evidenceKind": literal("process"),
                    "evidence": process_evidence,
                    "process": uri("https://maasai-project.eu/ontology/mdc#Hobbing"),
                    "processCode": literal("hobbing"),
                    "deliveryMode": literal("unspecified"),
                    "sourceType": literal("provider_confirmed"),
                    "confidence": literal("declared"),
                },
                {
                    "offering": offering_resource(offering_id),
                    "evidenceKind": literal("process"),
                    "evidence": process_evidence,
                    "process": uri("https://maasai-project.eu/ontology/mdc#Hobbing"),
                    "processCode": literal("hobbing"),
                    "deliveryMode": literal("unspecified"),
                    "sourceType": literal("provider_confirmed"),
                    "confidence": literal("declared"),
                },
                {
                    "offering": offering_resource(offering_id),
                    "evidenceKind": literal("certification"),
                    "evidence": certification_evidence,
                    "certification": uri("https://maasai-project.eu/ontology/mdc#ISO90012015"),
                    "certificationCode": literal("ISO9001_2015"),
                    "evidenceScope": literal("provider"),
                    "sourceType": literal("provider_confirmed"),
                    "confidence": literal("declared"),
                },
                {
                    "offering": offering_resource(offering_id),
                    "evidenceKind": literal("certification"),
                    "evidence": certification_evidence,
                    "certification": uri("https://maasai-project.eu/ontology/mdc#ISO90012015"),
                    "certificationCode": literal("ISO9001_2015"),
                    "evidenceScope": literal("provider"),
                    "sourceType": literal("provider_confirmed"),
                    "confidence": literal("declared"),
                },
            ],
        ]

        response = retrieve_service_discovery_candidates_from_fuseki(canonical(), endpoint="http://fuseki/query")
        evidence = response["candidates"][0]["evidence"]

        self.assertEqual([item["field_code"] for item in evidence["family_capabilities"]], ["module"])
        self.assertEqual([item["field_code"] for item in evidence["part_type_capabilities"]], ["spline_module"])
        self.assertEqual([item["field_code"] for item in evidence["generic_capabilities"]], ["batch_size"])
        self.assertEqual(len(evidence["materials"]), 1)
        self.assertEqual(evidence["materials"][0]["available_grades"], ["18CrNiMo7-6"])
        self.assertNotIn("material_grades", evidence["materials"][0])
        self.assertEqual([item["process_code"] for item in evidence["processes"]], ["hobbing"])
        self.assertEqual([item["certification_code"] for item in evidence["certifications"]], ["ISO9001_2015"])
        self.assertEqual(evidence["certifications"][0]["evidence_scope"], "provider")

    @patch("apps.search.service_discovery_fuseki_service.execute_fuseki_sparql_query")
    def test_remote_retrieval_reconstructs_repaired_fidelity_metadata(self, mock_execute):
        offering_id = "tasowheel_precision_gears"
        material_evidence = uri("https://maasai-project.eu/ontology/mdc#material1")
        mock_execute.side_effect = [
            [candidate_row("tasowheel", offering_id, support_status="confirmed")],
            [
                family_capability_row(
                    offering_id,
                    "diametral_pitch",
                    "dp",
                    minValue=literal(2.5),
                    maxValue=literal(85),
                    rawValue=literal("DP 85-2.5"),
                    normalizedOrder=literal("ascending"),
                ),
                generic_capability_row(
                    offering_id,
                    "surface_finish_ra_um",
                    "surface",
                    explicitNullField=literal("max"),
                ),
                material_row(
                    offering_id,
                    material_evidence,
                    flat_grade="16MnCr5",
                    ordered_grade="16MnCr5",
                    grade_index=1,
                ),
                material_row(
                    offering_id,
                    material_evidence,
                    flat_grade="18CrNiMo7-6",
                    ordered_grade="18CrNiMo7-6",
                    grade_index=0,
                ),
                material_row(
                    offering_id,
                    material_evidence,
                    flat_grade="20MnCr5",
                    ordered_grade="20MnCr5",
                    grade_index=2,
                ),
                material_row(
                    offering_id,
                    material_evidence,
                    flat_grade="18CrNiMo7-6",
                    ordered_grade="18CrNiMo7-6",
                    grade_index=0,
                ),
                process_row(
                    offering_id,
                    uri("https://maasai-project.eu/ontology/mdc#process_hobbing"),
                    "hobbing",
                    1,
                ),
                process_row(
                    offering_id,
                    uri("https://maasai-project.eu/ontology/mdc#process_machining"),
                    "machining",
                    0,
                ),
                certification_row(
                    offering_id,
                    uri("https://maasai-project.eu/ontology/mdc#cert_iso14001"),
                    "ISO14001_2015",
                    1,
                ),
                certification_row(
                    offering_id,
                    uri("https://maasai-project.eu/ontology/mdc#cert_iso9001"),
                    "ISO9001_2015",
                    0,
                ),
            ],
        ]

        response = retrieve_service_discovery_candidates_from_fuseki(canonical(), endpoint="http://fuseki/query")
        evidence = response["candidates"][0]["evidence"]

        dp = evidence["family_capabilities"][0]
        self.assertEqual(dp["normalized_order"], "ascending")
        self.assertEqual(float(dp["min"]), 2.5)
        self.assertEqual(float(dp["max"]), 85.0)
        surface = evidence["generic_capabilities"][0]
        self.assertIn("max", surface)
        self.assertIsNone(surface["max"])
        self.assertEqual(
            evidence["materials"][0]["available_grades"],
            ["18CrNiMo7-6", "16MnCr5", "20MnCr5"],
        )
        self.assertEqual([item["process_code"] for item in evidence["processes"]], ["machining", "hobbing"])
        self.assertEqual(
            [item["certification_code"] for item in evidence["certifications"]],
            ["ISO9001_2015", "ISO14001_2015"],
        )
        self.assertNotIn("sequence_index", str(evidence))
        self.assertNotIn("route", str(evidence).lower())
        self.assertNotIn("operation_sequence", str(evidence))
        self.assertNotIn("match", response["candidates"][0])
        self.assertNotIn("score", response["candidates"][0])

    def test_evidence_query_used_by_h8_contains_repaired_fidelity_projection(self):
        query = build_service_discovery_evidence_query(
            [offering_resource("tasowheel_precision_gears")]
        )

        self.assertIn("mdc:normalizedOrder", query)
        self.assertIn("mdc:explicitNullField", query)
        self.assertIn("mdc:sequenceIndex", query)
        self.assertIn("mdc:hasAvailableGradeEvidence", query)
        self.assertIn("mdc:AvailableGradeEvidence", query)
