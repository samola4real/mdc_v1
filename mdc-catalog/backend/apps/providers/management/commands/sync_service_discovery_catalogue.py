import uuid

from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from apps.providers.catalogue_sync_service import (
    CatalogueSyncConfigurationError,
    CatalogueSyncDisabled,
    CatalogueSyncNotFound,
    process_pending_catalogue_sync,
    rebuild_service_discovery_catalogue,
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

    def handle(self, *args, **options):
        rebuild = options["rebuild"]
        limit = options["limit"]
        publication_id = options["publication_id"]

        if rebuild and (limit is not None or publication_id is not None):
            raise CommandError("--rebuild cannot be combined with --limit or --publication-id.")
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
