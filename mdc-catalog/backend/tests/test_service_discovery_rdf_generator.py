from copy import deepcopy

from django.test import SimpleTestCase
from rdflib import Literal, RDF

from apps.ontology.service_discovery_rdf_generator import (
    ServiceDiscoveryRdfGenerationError,
    build_service_discovery_graph,
)
from apps.ontology.service_discovery_rdf_mappings import (
    MDC,
    available_grade_evidence_resource,
    offering_resource,
    provider_resource,
)


def objects_for(graph, subject, predicate):
    return set(graph.objects(subject, predicate))


def capability_nodes(graph, offering_id, predicate, field_code):
    offering = offering_resource(offering_id)
    return [
        node
        for node in graph.objects(offering, predicate)
        if (node, MDC.fieldCode, Literal(field_code)) in graph
    ]


def numeric_value(graph, subject, predicate):
    return float(graph.value(subject, predicate))


def sequence_index(graph, subject):
    return int(graph.value(subject, MDC.sequenceIndex))


def tasowheel_graph():
    return build_service_discovery_graph()


class ServiceDiscoveryRdfGeneratorTests(SimpleTestCase):
    def test_default_generation_uses_harmonized_records_without_legacy_offering(self):
        graph = tasowheel_graph()

        self.assertIn(
            (offering_resource("tasowheel_precision_gears"), MDC.offeringId, Literal("tasowheel_precision_gears")),
            graph,
        )
        self.assertIn(
            (offering_resource("tasowheel_precision_shafts"), MDC.offeringId, Literal("tasowheel_precision_shafts")),
            graph,
        )
        self.assertNotIn(
            (None, MDC.offeringId, Literal("tasowheel_gears_shafts_precision")),
            graph,
        )
        self.assertNotIn(
            (None, MDC.offeringId, Literal("tasowheel_precision_metal_parts")),
            graph,
        )

    def test_synthetic_provider_records_bypass_file_loading(self):
        record = {
            "provider": {
                "provider_id": "synthetic",
                "display_name": "Synthetic Provider",
                "country": "Finland",
                "certifications": [],
            },
            "offerings": [
                {
                    "offering_id": "synthetic_precision_gears",
                    "provider_id": "synthetic",
                    "service_category": "precision_gears",
                    "name": "Synthetic gears",
                    "part_family": "gear",
                    "support_status": "confirmed",
                    "supported_part_types": [],
                    "family_capabilities": {},
                    "part_type_capabilities": {},
                    "generic_capabilities": {},
                }
            ],
        }

        graph = build_service_discovery_graph(provider_records=[record])

        self.assertIn((provider_resource("synthetic"), MDC.providerId, Literal("synthetic")), graph)
        self.assertNotIn((provider_resource("tasowheel"), None, None), graph)

    def test_provider_offering_identity_category_and_family(self):
        graph = tasowheel_graph()
        provider = provider_resource("tasowheel")
        gear = offering_resource("tasowheel_precision_gears")
        shaft = offering_resource("tasowheel_precision_shafts")

        self.assertIn((provider, RDF.type, MDC.MaaSProvider), graph)
        self.assertIn((provider, MDC.providerId, Literal("tasowheel")), graph)
        self.assertIn((provider, MDC.displayName, Literal("Tasowheel Oy")), graph)
        self.assertIn((gear, MDC.serviceCategory, MDC.PrecisionGears), graph)
        self.assertIn((gear, MDC.supportsPartFamily, MDC.Gear), graph)
        self.assertIn((shaft, MDC.serviceCategory, MDC.PrecisionShafts), graph)
        self.assertIn((shaft, MDC.supportsPartFamily, MDC.Shaft), graph)

    def test_tasowheel_part_type_support_scope(self):
        graph = tasowheel_graph()

        gear_supports = {
            str(graph.value(node, MDC.partTypeCode))
            for node in graph.objects(
                offering_resource("tasowheel_precision_gears"),
                MDC.hasPartTypeSupport,
            )
            if str(graph.value(node, MDC.supportStatus)) == "confirmed"
        }
        shaft_supports = {
            str(graph.value(node, MDC.partTypeCode))
            for node in graph.objects(
                offering_resource("tasowheel_precision_shafts"),
                MDC.hasPartTypeSupport,
            )
            if str(graph.value(node, MDC.supportStatus)) == "confirmed"
        }

        self.assertEqual(gear_supports, {"spur_gear", "helical_gear", "bevel_gear", "worm_gear"})
        self.assertNotIn("crown_gear", gear_supports)
        self.assertNotIn("internal_gear", gear_supports)
        self.assertEqual(shaft_supports, {"splined_shaft", "plain_shaft", "hollow_shaft"})
        self.assertNotIn("stepped_shaft", shaft_supports)
        self.assertNotIn("worm_shaft", shaft_supports)

    def test_precipart_candidate_crown_gear_is_not_promoted(self):
        graph = tasowheel_graph()
        crown_nodes = [
            node
            for node in graph.objects(
                offering_resource("precipart_precision_gears"),
                MDC.hasPartTypeSupport,
            )
            if str(graph.value(node, MDC.partTypeCode)) == "crown_gear"
        ]

        self.assertEqual(len(crown_nodes), 1)
        self.assertIn(
            (crown_nodes[0], MDC.supportStatus, Literal("candidate_requiring_confirmation")),
            graph,
        )
        self.assertNotIn((crown_nodes[0], MDC.supportStatus, Literal("confirmed")), graph)
        self.assertIn((crown_nodes[0], MDC.sourceType, Literal("public_web")), graph)

    def test_tasowheel_gear_capabilities_are_scoped_and_not_fabricated(self):
        graph = tasowheel_graph()

        module = capability_nodes(graph, "tasowheel_precision_gears", MDC.hasFamilyCapability, "module")[0]
        dp = capability_nodes(graph, "tasowheel_precision_gears", MDC.hasFamilyCapability, "diametral_pitch")[0]
        outside = capability_nodes(graph, "tasowheel_precision_gears", MDC.hasFamilyCapability, "outside_diameter_mm")[0]
        quality = capability_nodes(graph, "tasowheel_precision_gears", MDC.hasFamilyCapability, "gear_quality")[0]

        self.assertEqual(numeric_value(graph, module, MDC.minValue), 0.3)
        self.assertEqual(numeric_value(graph, module, MDC.maxValue), 10.0)
        self.assertEqual(numeric_value(graph, dp, MDC.minValue), 2.5)
        self.assertEqual(numeric_value(graph, dp, MDC.maxValue), 85.0)
        self.assertIn((dp, MDC.rawValue, Literal("DP 85-2.5")), graph)
        self.assertIn((dp, MDC.normalizedOrder, Literal("ascending")), graph)
        self.assertEqual(list(graph.objects(dp, MDC.explicitNullField)), [])
        self.assertEqual(numeric_value(graph, outside, MDC.minValue), 10.0)
        self.assertEqual(numeric_value(graph, outside, MDC.maxValue), 450.0)
        self.assertIn((quality, MDC.qualityStandard, Literal("DIN")), graph)
        self.assertEqual(numeric_value(graph, quality, MDC.bestClass), 4.0)
        self.assertIn((quality, MDC.comparisonRule, Literal("lower_or_equal_is_better")), graph)

        self.assertEqual(capability_nodes(graph, "tasowheel_precision_gears", MDC.hasFamilyCapability, "outer_diameter_mm"), [])
        self.assertEqual(capability_nodes(graph, "tasowheel_precision_gears", MDC.hasFamilyCapability, "tolerance_mm"), [])
        self.assertEqual(capability_nodes(graph, "tasowheel_precision_gears", MDC.hasPartTypeCapability, "face_width_mm"), [])

    def test_tasowheel_shaft_capabilities_are_scoped_and_deferred_fields_absent(self):
        graph = tasowheel_graph()

        length = capability_nodes(graph, "tasowheel_precision_shafts", MDC.hasFamilyCapability, "length_mm")[0]
        outer = capability_nodes(graph, "tasowheel_precision_shafts", MDC.hasFamilyCapability, "outer_diameter_mm")[0]
        spline = capability_nodes(graph, "tasowheel_precision_shafts", MDC.hasPartTypeCapability, "spline_module")[0]

        self.assertEqual(numeric_value(graph, length, MDC.maxValue), 500.0)
        self.assertIn((length, MDC.sourceType, Literal("public_web")), graph)
        self.assertIn((length, MDC.confidence, Literal("publicly_confirmed")), graph)
        self.assertEqual(numeric_value(graph, outer, MDC.minValue), 10.0)
        self.assertEqual(numeric_value(graph, outer, MDC.maxValue), 450.0)
        self.assertIn((spline, MDC.partTypeCode, Literal("splined_shaft")), graph)
        self.assertEqual(numeric_value(graph, spline, MDC.minValue), 0.3)
        self.assertEqual(numeric_value(graph, spline, MDC.maxValue), 10.0)

        for field in [
            "module",
            "diametral_pitch",
            "gear_quality",
            "tolerance_mm",
            "spline_diametral_pitch",
            "shaft_quality",
            "spline_quality",
        ]:
            self.assertEqual(
                capability_nodes(graph, "tasowheel_precision_shafts", MDC.hasFamilyCapability, field),
                [],
                field,
            )

    def test_tasowheel_material_process_and_certification_evidence(self):
        graph = tasowheel_graph()
        for offering_id in ["tasowheel_precision_gears", "tasowheel_precision_shafts"]:
            material_nodes = list(
                graph.objects(offering_resource(offering_id), MDC.hasMaterialEvidence)
            )
            self.assertTrue(
                any((node, MDC.materialCode, Literal("alloyed_carburizing_steel")) in graph for node in material_nodes)
            )
            grades = set()
            for node in material_nodes:
                grades.update(str(value) for value in graph.objects(node, MDC.availableGrade))
            self.assertEqual({"18CrNiMo7-6", "16MnCr5", "20MnCr5"} & grades, {"18CrNiMo7-6", "16MnCr5", "20MnCr5"})
            material = next(
                node
                for node in material_nodes
                if (node, MDC.materialCode, Literal("alloyed_carburizing_steel")) in graph
            )
            self.assertEqual(sequence_index(graph, material), 0)
            ordered_grade_nodes = sorted(
                graph.objects(material, MDC.hasAvailableGradeEvidence),
                key=lambda node: sequence_index(graph, node),
            )
            self.assertEqual(
                [str(graph.value(node, MDC.availableGrade)) for node in ordered_grade_nodes],
                ["18CrNiMo7-6", "16MnCr5", "20MnCr5"],
            )
            self.assertIn(
                (
                    available_grade_evidence_resource(offering_id, "alloyed_carburizing_steel", 0),
                    RDF.type,
                    MDC.AvailableGradeEvidence,
                ),
                graph,
            )

            process_nodes = list(graph.objects(offering_resource(offering_id), MDC.hasProcessEvidence))
            process_codes = {str(graph.value(node, MDC.processCode)) for node in process_nodes}
            for process in ["hobbing", "gear_shaping", "deburring", "gear_grinding", "surface_grinding", "turn_mill"]:
                self.assertIn(process, process_codes)
            self.assertEqual(
                [
                    str(graph.value(node, MDC.processCode))
                    for node in sorted(process_nodes, key=lambda item: sequence_index(graph, item))
                ],
                [
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
                ],
            )

            for node in graph.objects(offering_resource(offering_id), MDC.hasProcessEvidence):
                self.assertIn((node, MDC.deliveryMode, Literal("unspecified")), graph)

        self.assertEqual(list(graph.triples((None, MDC.supportsMaterialGrade, None))), [])
        self.assertEqual(list(graph.triples((None, MDC.route_steps, None))), [])
        self.assertEqual(list(graph.triples((None, MDC.route, None))), [])
        self.assertEqual(list(graph.triples((None, MDC.operationSequence, None))), [])
        self.assertEqual(list(graph.triples((None, MDC.machineSequence, None))), [])
        self.assertEqual(list(graph.triples((None, MDC.processOrder, None))), [])

        certification_nodes = list(graph.objects(provider_resource("tasowheel"), MDC.hasCertificationEvidence))
        self.assertEqual(
            {str(graph.value(node, MDC.certificationCode)) for node in certification_nodes},
            {"ISO9001_2015", "ISO_TS_16949_partial", "APQP", "ISO14001_2015"},
        )
        self.assertEqual(
            [
                str(graph.value(node, MDC.certificationCode))
                for node in sorted(certification_nodes, key=lambda item: sequence_index(graph, item))
            ],
            ["ISO9001_2015", "ISO14001_2015", "ISO_TS_16949_partial", "APQP"],
        )

    def test_composite_unknown_forbidden_and_unmapped_safety_behaviour(self):
        record = {
            "provider": {
                "provider_id": "synthetic_metal",
                "display_name": "Synthetic Metal",
                "country": "Finland",
                "certifications": [],
            },
            "offerings": [
                {
                    "offering_id": "synthetic_metal_precision_metal_parts",
                    "provider_id": "synthetic_metal",
                    "service_category": "precision_metal_parts",
                    "name": "Precision metal parts",
                    "part_family": "metal_part",
                    "support_status": "confirmed",
                    "supported_part_types": [
                        {
                            "part_type": "bracket",
                            "support_status": "confirmed",
                            "source_type": "provider_confirmed",
                            "confidence": "declared",
                        }
                    ],
                    "family_capabilities": {},
                    "part_type_capabilities": {
                        "bracket": {
                            "bounding_box_mm": {
                                "length_mm": {"max": 150, "source_type": "provider_confirmed", "confidence": "declared"},
                                "width_mm": {"max": 80, "source_type": "provider_confirmed", "confidence": "declared"},
                                "height_mm": {"max": 60, "source_type": "provider_confirmed", "confidence": "declared"},
                                "source_type": "provider_confirmed",
                                "confidence": "declared",
                            }
                        }
                    },
                    "generic_capabilities": {
                        "surface_finish_ra_um": {
                            "max": None,
                            "source_type": "not_confirmed",
                            "confidence": "unknown",
                        }
                    },
                }
            ],
        }

        graph = build_service_discovery_graph(provider_records=[record])
        bounding = capability_nodes(
            graph,
            "synthetic_metal_precision_metal_parts",
            MDC.hasPartTypeCapability,
            "bounding_box_mm",
        )[0]
        self.assertEqual(len(list(graph.objects(bounding, MDC.hasComponent))), 3)
        unknown = capability_nodes(
            graph,
            "synthetic_metal_precision_metal_parts",
            MDC.hasGenericCapability,
            "surface_finish_ra_um",
        )[0]
        self.assertIn((unknown, MDC.sourceType, Literal("not_confirmed")), graph)
        self.assertEqual(list(graph.objects(unknown, MDC.maxValue)), [])
        self.assertIn((unknown, MDC.explicitNullField, Literal("max")), graph)
        self.assertEqual(
            list(graph.objects(offering_resource("synthetic_metal_precision_metal_parts"), MDC.hasGenericCapability)),
            [unknown],
        )

        forbidden = deepcopy(record)
        forbidden["offerings"][0]["generic_capabilities"]["pricing"] = {"currency": "EUR"}
        with self.assertRaises(ServiceDiscoveryRdfGenerationError):
            build_service_discovery_graph(provider_records=[forbidden])

        unmapped = deepcopy(record)
        unmapped["offerings"][0]["generic_capabilities"]["unknown_capability"] = {
            "max": 1,
            "source_type": "provider_confirmed",
            "confidence": "declared",
        }
        with self.assertRaises(ServiceDiscoveryRdfGenerationError):
            build_service_discovery_graph(provider_records=[unmapped])
