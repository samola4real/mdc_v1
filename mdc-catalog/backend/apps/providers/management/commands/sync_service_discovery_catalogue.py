import uuid

from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from apps.ontology.service_discovery_rdf_generator import (
    ServiceDiscoveryRdfGenerationError,
)
from apps.providers.catalogue_sync_service import (
    CatalogueChangedDuringSync,
    CatalogueSyncConfigurationError,
    CatalogueSyncDisabled,
    CatalogueSyncNotFound,
    CatalogueSyncTransportError,
    process_pending_catalogue_sync,
    rebuild_service_discovery_catalogue,
    recover_stale_processing_sync,
)


class Command(BaseCommand):
    help = (
        "Synchronize the DB-backed service-discovery catalogue to Fuseki. "
        "Default mode processes pending/failed outbox publications."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum outbox publications to process in this run (default: 100).",
        )
        parser.add_argument(
            "--publication-id",
            type=uuid.UUID,
            default=None,
            help="Process/retry one publication UUID.",
        )
        parser.add_argument(
            "--rebuild",
            action="store_true",
            help="Explicitly replace Fuseki from the current DB catalogue without outbox changes.",
        )
        parser.add_argument(
            "--recover-stale",
            action="store_true",
            help=(
                "Recover expired PROCESSING outbox leases to FAILED/retryable state "
                "without contacting Fuseki."
            ),
        )

    def handle(self, *args, **options):
        rebuild = options["rebuild"]
        recover_stale = options["recover_stale"]
        limit = options["limit"]
        publication_id = options["publication_id"]

        selected_modes = sum(
            [
                bool(rebuild),
                bool(recover_stale),
                publication_id is not None,
                limit is not None,
            ]
        )
        if selected_modes > 1:
            raise CommandError(
                "--rebuild, --recover-stale, --limit, and --publication-id are mutually exclusive."
            )
        if limit is not None and limit <= 0:
            raise CommandError("--limit must be greater than zero.")

        try:
            if rebuild:
                result = rebuild_service_discovery_catalogue()
                self.stdout.write(
                    self.style.SUCCESS(
                        "Catalogue rebuild succeeded; "
                        f"triples synchronized: {result['triple_count']}."
                    )
                )
                return

            if recover_stale:
                result = recover_stale_processing_sync()
                self.stdout.write(
                    self.style.SUCCESS(
                        "Catalogue sync lease recovery completed; "
                        f"events={result['events']}; publications={result['publications']}."
                    )
                )
                return

            summary = process_pending_catalogue_sync(
                limit=limit if limit is not None else 100,
                publication_id=publication_id,
            )
        except CatalogueSyncDisabled as exc:
            raise CommandError(str(exc)) from None
        except CatalogueSyncConfigurationError as exc:
            raise CommandError(str(exc)) from None
        except CatalogueSyncNotFound as exc:
            raise CommandError(str(exc)) from None
        except CatalogueChangedDuringSync:
            raise CommandError(
                "Catalogue changed during synchronization; retry is required."
            ) from None
        except CatalogueSyncTransportError:
            raise CommandError("Catalogue synchronization transport failed.") from None
        except ServiceDiscoveryRdfGenerationError:
            raise CommandError("Catalogue RDF generation failed.") from None
        except DatabaseError:
            raise CommandError("Catalogue synchronization database operation failed.") from None
        except ValueError as exc:
            raise CommandError(str(exc)) from None

        self.stdout.write(
            "Catalogue synchronization: "
            f"selected={summary['selected']}; "
            f"succeeded={summary['succeeded']}; "
            f"failed={summary['failed']}; "
            f"noop={summary['noop']}; "
            f"events={summary['events']}."
        )
        if summary["failed"]:
            raise CommandError("Catalogue synchronization completed with failures.")
        self.stdout.write(self.style.SUCCESS("Catalogue synchronization completed successfully."))
