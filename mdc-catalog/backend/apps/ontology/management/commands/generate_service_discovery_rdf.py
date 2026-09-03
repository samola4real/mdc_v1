from pathlib import Path

from django.core.management.base import BaseCommand

from apps.ontology.service_discovery_rdf_generator import (
    build_service_discovery_graph,
    generate_service_discovery_turtle,
)


class Command(BaseCommand):
    help = "Generate harmonized MDC service-discovery RDF Turtle from parallel provider data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            help="Optional output Turtle path.",
        )

    def handle(self, *args, **options):
        output = Path(options["output"]) if options.get("output") else None
        graph = build_service_discovery_graph()
        output_path = generate_service_discovery_turtle(output_path=output)

        self.stdout.write(
            self.style.SUCCESS(
                "Generated harmonized service-discovery RDF "
                f"from harmonized service-discovery provider data with "
                f"{len(graph)} triples: {output_path}"
            )
        )
