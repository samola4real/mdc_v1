import tempfile
from pathlib import Path

from django.test import SimpleTestCase, override_settings
from rdflib import RDF

from apps.ontology.rdf_generator import (
    MDC,
    build_catalog_graph,
    offering_uri,
    provider_uri,
    write_catalog_turtle,
)
from apps.providers.services import clear_seed_cache


class RdfGeneratorTests(SimpleTestCase):
    def setUp(self):
        clear_seed_cache()

    def test_catalog_graph_contains_tasowheel_provider(self):
        graph = build_catalog_graph()

        tasowheel = provider_uri("tasowheel")

        self.assertIn(
            (tasowheel, RDF.type, MDC.MaaSProvider),
            graph,
        )

        self.assertEqual(
            str(graph.value(tasowheel, MDC.providerId)),
            "tasowheel",
        )

        self.assertEqual(
            str(graph.value(tasowheel, MDC.displayName)),
            "Tasowheel Oy",
        )

    def test_catalog_graph_contains_tasowheel_offering(self):
        graph = build_catalog_graph()

        tasowheel = provider_uri("tasowheel")
        offering = offering_uri("tasowheel_gears_shafts_precision")

        self.assertIn(
            (offering, RDF.type, MDC.ProviderOffering),
            graph,
        )

        self.assertIn(
            (tasowheel, MDC.hasOffering, offering),
            graph,
        )

        self.assertIn(
            (offering, MDC.offeredBy, tasowheel),
            graph,
        )

    def test_catalog_graph_contains_part_family_links(self):
        graph = build_catalog_graph()

        offering = offering_uri("tasowheel_gears_shafts_precision")

        self.assertIn(
            (offering, MDC.supportsPartFamily, MDC.Shaft),
            graph,
        )

        self.assertIn(
            (offering, MDC.supportsPartFamily, MDC.Gear),
            graph,
        )

        self.assertIn(
            (offering, MDC.supportsPartFamily, MDC.SpurGear),
            graph,
        )

        self.assertIn(
            (offering, MDC.supportsPartFamily, MDC.HelicalGear),
            graph,
        )

    def test_catalog_graph_contains_material_and_grade_links(self):
        graph = build_catalog_graph()

        offering = offering_uri("tasowheel_gears_shafts_precision")

        self.assertIn(
            (offering, MDC.supportsMaterial, MDC.Steel),
            graph,
        )

        self.assertIn(
            (offering, MDC.supportsMaterial, MDC.AlloyedCarburizingSteel),
            graph,
        )

        supported_grades = list(
            graph.objects(offering, MDC.supportsMaterialGrade)
        )

        supported_grade_values = {str(value) for value in supported_grades}

        self.assertTrue(
            any("MaterialGrade_18CrNiMo7_6" in value for value in supported_grade_values)
        )
        self.assertTrue(
            any("MaterialGrade_16MnCr5" in value for value in supported_grade_values)
        )
        self.assertTrue(
            any("MaterialGrade_20MnCr5" in value for value in supported_grade_values)
        )

    def test_catalog_graph_contains_capability_literals(self):
        graph = build_catalog_graph()

        offering = offering_uri("tasowheel_gears_shafts_precision")

        diameter_min = graph.value(offering, MDC.diameterMinMm)
        diameter_max = graph.value(offering, MDC.diameterMaxMm)
        batch_min = graph.value(offering, MDC.batchMin)
        batch_max = graph.value(offering, MDC.batchMax)
        lead_time_min = graph.value(offering, MDC.leadTimeMinWeeks)
        lead_time_max = graph.value(offering, MDC.leadTimeMaxWeeks)

        self.assertEqual(float(diameter_min), 10.0)
        self.assertEqual(float(diameter_max), 450.0)
        self.assertEqual(int(batch_min), 100)
        self.assertEqual(int(batch_max), 2000)
        self.assertEqual(float(lead_time_min), 8.0)
        self.assertEqual(float(lead_time_max), 12.0)

    def test_write_catalog_turtle_creates_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            with override_settings(GENERATED_DATA_DIR=Path(temporary_directory)):
                output_path = write_catalog_turtle("test_catalog.ttl")

                self.assertTrue(output_path.exists())
                self.assertEqual(output_path.name, "test_catalog.ttl")

                turtle_text = output_path.read_text(encoding="utf-8")

                self.assertIn("provider_tasowheel", turtle_text)
                self.assertIn("offering_tasowheel_gears_shafts_precision", turtle_text)
                self.assertIn("supportsPartFamily", turtle_text)
                self.assertIn("supportsMaterial", turtle_text)
                self.assertIn("diameterMaxMm", turtle_text)