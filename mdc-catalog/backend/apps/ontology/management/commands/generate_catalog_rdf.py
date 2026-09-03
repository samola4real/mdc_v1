
from django.core.management.base import BaseCommand

from apps.ontology.rdf_generator import build_catalog_graph, write_catalog_turtle


class Command(BaseCommand):
    help = "Generate MDC catalogue RDF Turtle file from provider seed data."

    def handle(self, *args, **options):
        graph = build_catalog_graph()
        output_path = write_catalog_turtle()

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated RDF catalogue with {len(graph)} triples: {output_path}"
            )
        )