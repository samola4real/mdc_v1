from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase
from rdflib import Graph, Literal

from apps.ontology.service_discovery_rdf_mappings import (
    MDC,
    family_capability_resource,
    offering_resource,
)


class GenerateServiceDiscoveryRdfCommandTests(SimpleTestCase):
    def test_command_writes_parseable_turtle_to_output_override(self):
        legacy_output = Path(settings.GENERATED_DATA_DIR) / "mdc_catalog.ttl"
        legacy_exists_before = legacy_output.exists()
        legacy_mtime_before = legacy_output.stat().st_mtime if legacy_exists_before else None

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "service_discovery.ttl"

            call_command("generate_service_discovery_rdf", "--output", str(output_path))

            self.assertTrue(output_path.exists())
            graph = Graph()
            graph.parse(output_path, format="turtle")
            self.assertIn(
                (
                    offering_resource("tasowheel_precision_gears"),
                    MDC.offeringId,
                    Literal("tasowheel_precision_gears"),
                ),
                graph,
            )
            self.assertIn(
                (
                    offering_resource("tasowheel_precision_shafts"),
                    MDC.offeringId,
                    Literal("tasowheel_precision_shafts"),
                ),
                graph,
            )
            self.assertNotIn(
                (None, MDC.offeringId, Literal("tasowheel_gears_shafts_precision")),
                graph,
            )
            self.assertIn(
                (
                    family_capability_resource("tasowheel_precision_gears", "diametral_pitch"),
                    MDC.normalizedOrder,
                    Literal("ascending"),
                ),
                graph,
            )
            self.assertIn((None, MDC.sequenceIndex, None), graph)

        self.assertEqual(legacy_output.exists(), legacy_exists_before)
        if legacy_exists_before:
            self.assertEqual(legacy_output.stat().st_mtime, legacy_mtime_before)

    def test_command_output_message_mentions_path_triples_and_harmonized_data(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "service_discovery.ttl"
            from io import StringIO

            stdout = StringIO()
            call_command(
                "generate_service_discovery_rdf",
                "--output",
                str(output_path),
                stdout=stdout,
            )
            message = stdout.getvalue()

        self.assertIn(str(output_path), message)
        self.assertIn("triples", message)
        self.assertIn("harmonized service-discovery provider data", message)
        self.assertNotIn("Fuseki", message)
