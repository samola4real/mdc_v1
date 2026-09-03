from django.test import SimpleTestCase

from apps.ontology.service_discovery_rdf_mappings import (
    MDC,
    ServiceDiscoveryRdfMappingError,
    available_grade_evidence_resource,
    certification_evidence_resource,
    get_capability_field_concept,
    get_certification_concept,
    get_material_concept,
    get_part_family_concept,
    get_part_type_concept,
    get_process_concept,
    get_service_category_concept,
    offering_resource,
    provider_resource,
)


class ServiceDiscoveryRdfMappingsTests(SimpleTestCase):
    def test_required_service_category_and_family_mappings_exist(self):
        self.assertEqual(get_service_category_concept("precision_gears"), MDC.PrecisionGears)
        self.assertEqual(get_service_category_concept("precision_shafts"), MDC.PrecisionShafts)
        self.assertEqual(get_service_category_concept("precision_metal_parts"), MDC.PrecisionMetalParts)
        self.assertEqual(get_part_family_concept("gear"), MDC.Gear)
        self.assertEqual(get_part_family_concept("shaft"), MDC.Shaft)
        self.assertEqual(get_part_family_concept("metal_part"), MDC.MetalPart)

    def test_all_approved_part_type_mappings_exist(self):
        for part_type in [
            "spur_gear",
            "helical_gear",
            "bevel_gear",
            "worm_gear",
            "crown_gear",
            "plain_shaft",
            "stepped_shaft",
            "splined_shaft",
            "worm_shaft",
            "hollow_shaft",
            "block",
            "plate",
            "bracket",
            "bushing",
            "roller",
            "collar",
        ]:
            self.assertTrue(str(get_part_type_concept(part_type)).startswith(str(MDC)))

    def test_capability_material_process_and_certification_mappings_exist(self):
        for field in [
            "module",
            "diametral_pitch",
            "outside_diameter_mm",
            "gear_quality",
            "length_mm",
            "outer_diameter_mm",
            "spline_module",
            "batch_size",
            "lead_time_weeks",
            "weight_kg",
            "surface_finish_ra_um",
            "bounding_box_mm",
        ]:
            self.assertTrue(str(get_capability_field_concept(field)).startswith(str(MDC)))

        self.assertEqual(
            get_material_concept("alloyed_carburizing_steel"),
            MDC.AlloyedCarburizingSteel,
        )

        for process in [
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
        ]:
            self.assertTrue(str(get_process_concept(process)).startswith(str(MDC)))

        for certification in [
            "ISO9001_2015",
            "ISO_TS_16949_partial",
            "APQP",
            "ISO14001_2015",
        ]:
            self.assertTrue(str(get_certification_concept(certification)).startswith(str(MDC)))

    def test_resource_helpers_are_deterministic(self):
        self.assertEqual(provider_resource("tasowheel"), provider_resource("tasowheel"))
        self.assertEqual(
            offering_resource("tasowheel_precision_gears"),
            offering_resource("tasowheel_precision_gears"),
        )
        self.assertEqual(
            certification_evidence_resource("tasowheel", "ISO9001_2015"),
            certification_evidence_resource("tasowheel", "ISO9001_2015"),
        )
        self.assertEqual(
            available_grade_evidence_resource("tasowheel_precision_gears", "alloyed_carburizing_steel", 0),
            available_grade_evidence_resource("tasowheel_precision_gears", "alloyed_carburizing_steel", 0),
        )
        self.assertNotEqual(
            available_grade_evidence_resource("tasowheel_precision_gears", "alloyed_carburizing_steel", 0),
            available_grade_evidence_resource("tasowheel_precision_gears", "alloyed_carburizing_steel", 1),
        )

    def test_unknown_identifiers_raise_mapping_error(self):
        for getter in [
            get_service_category_concept,
            get_part_family_concept,
            get_part_type_concept,
            get_capability_field_concept,
            get_material_concept,
            get_process_concept,
            get_certification_concept,
        ]:
            with self.assertRaises(ServiceDiscoveryRdfMappingError):
                getter("not_controlled")
