import os
from copy import deepcopy
from unittest import skipUnless

from django.conf import settings
from django.test import SimpleTestCase

from apps.ontology.service_discovery_rdf_generator import default_service_discovery_turtle_path
from apps.search.service_discovery_fuseki_service import retrieve_service_discovery_candidates_from_fuseki
from apps.search.service_discovery_request import CanonicalServiceDiscoverySearchRequest
from apps.search.service_discovery_sparql_service import retrieve_service_discovery_candidates


def integration_enabled() -> bool:
    return (
        os.getenv("RUN_SERVICE_DISCOVERY_FUSEKI_TESTS") == "1"
        and bool(getattr(settings, "SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT", ""))
        and default_service_discovery_turtle_path().exists()
    )


def canonical(
    service_category="precision_gears",
    part_family="gear",
    part_type="spur_gear",
) -> CanonicalServiceDiscoverySearchRequest:
    return CanonicalServiceDiscoverySearchRequest(
        request_id="req",
        consumer_id="consumer",
        selection={
            "service_category": service_category,
            "part_family": part_family,
            "part_type": part_type,
        },
        requirements={},
        match_policy={},
    )


def candidate_by_provider(response: dict, provider_id: str):
    for candidate in response["candidates"]:
        if candidate["provider"]["provider_id"] == provider_id:
            return candidate
    return None


def fields(items: list[dict]) -> set[str]:
    return {item.get("field_code") for item in items}


EXPECTED_TASOWHEEL_GRADES = ["18CrNiMo7-6", "16MnCr5", "20MnCr5"]
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


def comparable_projection(response: dict) -> dict:
    comparable = deepcopy(response)
    comparable["status"].pop("retrieval_engine", None)
    comparable["status"].pop("message", None)
    return comparable


@skipUnless(
    integration_enabled(),
    (
        "Harmonized Fuseki integration tests require "
        "RUN_SERVICE_DISCOVERY_FUSEKI_TESTS=1, SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT, "
        "and an existing H6 harmonized Turtle file."
    ),
)
class ServiceDiscoveryFusekiIntegrationTests(SimpleTestCase):
    def local(self, request):
        return retrieve_service_discovery_candidates(
            request,
            ttl_path=default_service_discovery_turtle_path(),
        )

    def remote(self, request):
        return retrieve_service_discovery_candidates_from_fuseki(request)

    def test_remote_dataset_returns_harmonized_tasowheel_candidates_only(self):
        response = self.remote(canonical())
        offering_ids = {
            candidate["offering"]["offering_id"]
            for candidate in response["candidates"]
        }

        self.assertTrue(response["candidates"])
        self.assertIn("tasowheel_precision_gears", offering_ids)
        self.assertNotIn("tasowheel_gears_shafts_precision", offering_ids)
        self.assertNotIn("tasowheel_precision_metal_parts", offering_ids)

    def test_local_and_remote_outputs_are_equivalent_for_key_selections(self):
        selections = [
            canonical("precision_gears", "gear", "spur_gear"),
            canonical("precision_gears", "gear", "crown_gear"),
            canonical("precision_shafts", "shaft", "splined_shaft"),
            canonical("precision_shafts", "shaft", "stepped_shaft"),
        ]

        for request in selections:
            with self.subTest(request=request.selection):
                local = self.local(request)
                remote = self.remote(request)

                self.assertTrue(remote["status"]["retrieval_executed"])
                self.assertFalse(remote["status"]["matching_executed"])
                self.assertEqual(
                    comparable_projection(remote),
                    comparable_projection(local),
                )

    def test_remote_preserves_tasowheel_and_precipart_part_type_statuses(self):
        spur = self.remote(canonical("precision_gears", "gear", "spur_gear"))
        tasowheel_spur = candidate_by_provider(spur, "tasowheel")
        self.assertEqual(
            tasowheel_spur["requested_part_type_support"]["evidence_status"],
            "confirmed",
        )

        crown = self.remote(canonical("precision_gears", "gear", "crown_gear"))
        tasowheel_crown = candidate_by_provider(crown, "tasowheel")
        self.assertEqual(
            tasowheel_crown["requested_part_type_support"]["evidence_status"],
            "not_asserted",
        )
        precipart = candidate_by_provider(crown, "precipart")
        if precipart is not None:
            self.assertEqual(
                precipart["requested_part_type_support"]["evidence_status"],
                "candidate_requiring_confirmation",
            )

    def test_remote_tasowheel_evidence_and_deferred_fields(self):
        gear = self.remote(canonical("precision_gears", "gear", "spur_gear"))
        tasowheel_gear = candidate_by_provider(gear, "tasowheel")
        gear_evidence = tasowheel_gear["evidence"]

        self.assertTrue(
            {"module", "diametral_pitch", "outside_diameter_mm", "gear_quality"}
            <= fields(gear_evidence["family_capabilities"])
        )
        dp = next(item for item in gear_evidence["family_capabilities"] if item["field_code"] == "diametral_pitch")
        self.assertEqual(dp["raw"], "DP 85-2.5")
        self.assertEqual(dp["normalized_order"], "ascending")
        gear_surface = next(
            item
            for item in gear_evidence["generic_capabilities"]
            if item["field_code"] == "surface_finish_ra_um"
        )
        self.assertIn("max", gear_surface)
        self.assertIsNone(gear_surface["max"])
        self.assertEqual(
            gear_evidence["materials"][0]["available_grades"],
            EXPECTED_TASOWHEEL_GRADES,
        )
        self.assertEqual(
            [item["process_code"] for item in gear_evidence["processes"]],
            EXPECTED_TASOWHEEL_PROCESSES,
        )
        self.assertEqual(
            [item["certification_code"] for item in gear_evidence["certifications"]],
            EXPECTED_TASOWHEEL_CERTIFICATIONS,
        )
        self.assertNotIn("sequence_index", str(gear_evidence))

        shaft = self.remote(canonical("precision_shafts", "shaft", "splined_shaft"))
        tasowheel_shaft = candidate_by_provider(shaft, "tasowheel")
        shaft_evidence = tasowheel_shaft["evidence"]
        shaft_family_fields = fields(shaft_evidence["family_capabilities"])
        shaft_part_fields = fields(shaft_evidence["part_type_capabilities"])

        length = next(item for item in shaft_evidence["family_capabilities"] if item["field_code"] == "length_mm")
        self.assertEqual(float(length["max"]), 500.0)
        self.assertIn("outer_diameter_mm", shaft_family_fields)
        self.assertIn("spline_module", shaft_part_fields)

        shaft_surface = next(
            item
            for item in shaft_evidence["generic_capabilities"]
            if item["field_code"] == "surface_finish_ra_um"
        )
        self.assertIn("max", shaft_surface)
        self.assertIsNone(shaft_surface["max"])
        self.assertEqual(
            [item["process_code"] for item in shaft_evidence["processes"]],
            EXPECTED_TASOWHEEL_PROCESSES,
        )
        self.assertEqual(
            [item["certification_code"] for item in shaft_evidence["certifications"]],
            EXPECTED_TASOWHEEL_CERTIFICATIONS,
        )
        material_codes = {item["material_code"] for item in shaft_evidence["materials"]}
        self.assertIn("alloyed_carburizing_steel", material_codes)
        self.assertEqual(
            shaft_evidence["materials"][0]["available_grades"],
            EXPECTED_TASOWHEEL_GRADES,
        )
        self.assertNotIn("material_grades", shaft_evidence["materials"][0])
        self.assertNotIn("sequence_index", str(shaft_evidence))

        all_fields = shaft_family_fields | shaft_part_fields | fields(shaft_evidence["generic_capabilities"])
        for forbidden_field in [
            "spline_diametral_pitch",
            "shaft_quality",
            "spline_quality",
            "tolerance_mm",
            "diametral_pitch",
            "gear_quality",
        ]:
            self.assertNotIn(forbidden_field, all_fields)
