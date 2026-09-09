from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from apps.providers.service_discovery_db_repository import (
    ServiceDiscoveryImportError,
    import_service_discovery_provider_records,
)
from apps.providers.service_discovery_loaders import (
    ServiceDiscoveryProviderLoadError,
    load_service_discovery_providers,
)


class Command(BaseCommand):
    help = "Atomically import curated harmonized YAML snapshots into the configured database."

    def add_arguments(self, parser):
        parser.add_argument("--directory", type=Path, help="Override the curated provider directory.")

    def handle(self, *args, **options):
        try:
            records = load_service_discovery_providers(options["directory"])
            summary = import_service_discovery_provider_records(records)
        except ServiceDiscoveryImportError as exc:
            raise CommandError(str(exc)) from None
        except (ServiceDiscoveryProviderLoadError, OSError, UnicodeError):
            # YAML parser exceptions can contain complete source lines.
            raise CommandError("Unable to load provider YAML; check the directory and YAML syntax.") from None
        except DatabaseError:
            # Driver errors can contain connection details or rejected row contents.
            raise CommandError("Database import failed; the entire batch was rolled back.") from None
        self.stdout.write(self.style.SUCCESS(
            f"Providers imported/updated: {summary['providers']}; "
            f"offerings synchronized: {summary['offerings']}; "
            f"certifications synchronized: {summary['certifications']}."
        ))
