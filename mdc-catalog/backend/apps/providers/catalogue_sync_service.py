"""Durable PostgreSQL outbox -> RDF/Fuseki synchronization for M7.5.

PostgreSQL remains the operational source of truth. The semantic catalogue is
rebuilt from the current active DB-backed canonical projection and replaces the
configured Fuseki default graph through the Graph Store Protocol.
"""

from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.conf import settings
from django.db import DatabaseError, transaction
from django.db.models import Min
from django.utils import timezone

from apps.ontology.service_discovery_rdf_generator import (
    ServiceDiscoveryRdfGenerationError,
    build_service_discovery_graph,
)
from apps.providers.models import CatalogueSyncEvent, ProviderPublication
from apps.providers.service_discovery_db_repository import (
    load_service_discovery_providers_from_db,
)


class CatalogueSyncError(Exception):
    """Base safe synchronization error."""


class CatalogueSyncDisabled(CatalogueSyncError):
    pass


class CatalogueSyncConfigurationError(CatalogueSyncError):
    pass


class CatalogueSyncNotFound(CatalogueSyncError):
    pass


class CatalogueSyncTransportError(CatalogueSyncError):
    """Safe wrapper that intentionally excludes endpoint/response details."""


ELIGIBLE_EVENT_STATUSES = (
    CatalogueSyncEvent.Status.PENDING,
    CatalogueSyncEvent.Status.FAILED,
)


@dataclass(frozen=True)
class SyncAttempt:
    publication_id: Any
    event_ids: tuple[Any, ...]


def _ensure_sync_enabled() -> None:
    if not getattr(settings, "MDC_CATALOG_SYNC_ENABLED", False):
        raise CatalogueSyncDisabled("Catalogue synchronization is disabled for this environment.")


def _configured_graph_store_endpoint(endpoint: str | None = None) -> str:
    resolved = (
        endpoint
        or getattr(settings, "SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT", "")
        or ""
    ).strip()
    if not resolved:
        raise CatalogueSyncConfigurationError(
            "The service-discovery Fuseki graph-store endpoint is not configured."
        )
    parsed = urlparse(resolved)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise CatalogueSyncConfigurationError(
            "The service-discovery Fuseki graph-store endpoint must use HTTP or HTTPS."
        )
    return resolved


def _timeout_seconds(timeout_seconds: float | None = None) -> float:
    if timeout_seconds is not None:
        value = timeout_seconds
    else:
        value = getattr(settings, "FUSEKI_SYNC_TIMEOUT_SECONDS", 10.0)
    try:
        value = float(value)
    except (TypeError, ValueError) as exc:
        raise CatalogueSyncConfigurationError(
            "FUSEKI_SYNC_TIMEOUT_SECONDS must be a positive number."
        ) from exc
    if value <= 0:
        raise CatalogueSyncConfigurationError(
            "FUSEKI_SYNC_TIMEOUT_SECONDS must be a positive number."
        )
    return value


def replace_service_discovery_graph_in_fuseki(
    graph,
    *,
    endpoint: str | None = None,
    timeout_seconds: float | None = None,
) -> None:
    """Replace the configured Fuseki default graph with one Turtle document."""
    resolved_endpoint = _configured_graph_store_endpoint(endpoint)
    timeout = _timeout_seconds(timeout_seconds)
    serialized = graph.serialize(format="turtle")
    body = serialized if isinstance(serialized, bytes) else serialized.encode("utf-8")
    request = Request(
        resolved_endpoint,
        data=body,
        headers={
            "Content-Type": "text/turtle; charset=utf-8",
            "Accept": "text/plain, */*;q=0.1",
        },
        method="PUT",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            # Reading is unnecessary. A successful 2xx response is sufficient and
            # avoids accidentally retaining/logging server response content.
            status_code = getattr(response, "status", 200)
            if status_code < 200 or status_code >= 300:
                raise CatalogueSyncTransportError(
                    "Fuseki graph replacement returned a non-success status."
                )
    except HTTPError as exc:
        raise CatalogueSyncTransportError(
            f"Fuseki graph replacement failed with HTTP {exc.code}."
        ) from None
    except (URLError, socket.timeout, TimeoutError, OSError):
        raise CatalogueSyncTransportError(
            "Fuseki graph replacement endpoint is unavailable."
        ) from None


def _build_current_db_graph():
    provider_records = load_service_discovery_providers_from_db()
    return build_service_discovery_graph(provider_records=provider_records)


def rebuild_service_discovery_catalogue(
    *,
    endpoint: str | None = None,
    timeout_seconds: float | None = None,
) -> dict[str, int]:
    """Explicit DB -> RDF -> Fuseki rebuild without fabricating outbox history."""
    _ensure_sync_enabled()
    graph = _build_current_db_graph()
    replace_service_discovery_graph_in_fuseki(
        graph,
        endpoint=endpoint,
        timeout_seconds=timeout_seconds,
    )
    return {"triple_count": len(graph)}


def _claim_publication(publication_id) -> SyncAttempt | None:
    """Claim all pending/failed events for one publication in a short transaction."""
    with transaction.atomic():
        try:
            publication = ProviderPublication.objects.select_for_update().get(
                pk=publication_id
            )
        except ProviderPublication.DoesNotExist as exc:
            raise CatalogueSyncNotFound("Publication not found.") from exc

        events = list(
            CatalogueSyncEvent.objects.select_for_update()
            .filter(
                publication=publication,
                status__in=ELIGIBLE_EVENT_STATUSES,
            )
            .order_by("created_at", "id")
        )
        if not events:
            return None

        now = timezone.now()
        for event in events:
            event.status = CatalogueSyncEvent.Status.PROCESSING
            event.attempt_count += 1
            event.last_error = ""
            # While PROCESSING, processed_at records the start of this attempt.
            # It is replaced with the completion/failure timestamp on finalization.
            event.processed_at = now
        CatalogueSyncEvent.objects.bulk_update(
            events,
            ["status", "attempt_count", "last_error", "processed_at"],
        )

        publication.status = ProviderPublication.Status.SYNC_PENDING
        publication.completed_at = None
        publication.save(update_fields=["status", "completed_at"])

        return SyncAttempt(
            publication_id=publication.id,
            event_ids=tuple(event.id for event in events),
        )


def _finalize_success(attempt: SyncAttempt) -> None:
    with transaction.atomic():
        publication = ProviderPublication.objects.select_for_update().get(
            pk=attempt.publication_id
        )
        events = list(
            CatalogueSyncEvent.objects.select_for_update()
            .filter(pk__in=attempt.event_ids)
            .order_by("created_at", "id")
        )
        now = timezone.now()
        for event in events:
            if event.status != CatalogueSyncEvent.Status.PROCESSING:
                continue
            event.status = CatalogueSyncEvent.Status.SUCCEEDED
            event.last_error = ""
            event.processed_at = now
        CatalogueSyncEvent.objects.bulk_update(
            events, ["status", "last_error", "processed_at"]
        )

        has_unsucceeded = publication.sync_events.exclude(
            status=CatalogueSyncEvent.Status.SUCCEEDED
        ).exists()
        if has_unsucceeded:
            publication.status = ProviderPublication.Status.SYNC_PENDING
            publication.completed_at = None
        else:
            publication.status = ProviderPublication.Status.SYNCED
            publication.completed_at = now
        publication.save(update_fields=["status", "completed_at"])


def _safe_failure_code(exc: Exception) -> str:
    if isinstance(exc, CatalogueSyncTransportError):
        return "fuseki_transport_error"
    if isinstance(exc, CatalogueSyncConfigurationError):
        return "sync_configuration_error"
    if isinstance(exc, ServiceDiscoveryRdfGenerationError):
        return "rdf_generation_error"
    if isinstance(exc, DatabaseError):
        return "database_read_error"
    return "catalogue_sync_internal_error"


def _finalize_failure(attempt: SyncAttempt, failure_code: str) -> None:
    with transaction.atomic():
        publication = ProviderPublication.objects.select_for_update().get(
            pk=attempt.publication_id
        )
        events = list(
            CatalogueSyncEvent.objects.select_for_update()
            .filter(pk__in=attempt.event_ids)
            .order_by("created_at", "id")
        )
        now = timezone.now()
        for event in events:
            if event.status != CatalogueSyncEvent.Status.PROCESSING:
                continue
            event.status = CatalogueSyncEvent.Status.FAILED
            event.last_error = failure_code
            event.processed_at = now
        CatalogueSyncEvent.objects.bulk_update(
            events, ["status", "last_error", "processed_at"]
        )
        publication.status = ProviderPublication.Status.SYNC_FAILED
        publication.completed_at = None
        publication.save(update_fields=["status", "completed_at"])


def process_publication_sync(
    publication_id,
    *,
    endpoint: str | None = None,
    timeout_seconds: float | None = None,
) -> dict[str, Any]:
    """Attempt one publication once; failed events are retryable on a later call."""
    _ensure_sync_enabled()
    attempt = _claim_publication(publication_id)
    if attempt is None:
        return {"status": "noop", "event_count": 0, "triple_count": 0}

    try:
        graph = _build_current_db_graph()
        replace_service_discovery_graph_in_fuseki(
            graph,
            endpoint=endpoint,
            timeout_seconds=timeout_seconds,
        )
    except Exception as exc:  # settle the durable outbox before returning a safe result
        failure_code = _safe_failure_code(exc)
        _finalize_failure(attempt, failure_code)
        return {
            "status": "failed",
            "event_count": len(attempt.event_ids),
            "triple_count": 0,
            "failure_code": failure_code,
        }

    _finalize_success(attempt)
    return {
        "status": "succeeded",
        "event_count": len(attempt.event_ids),
        "triple_count": len(graph),
    }


def _eligible_publication_ids(limit: int) -> list[Any]:
    rows = (
        CatalogueSyncEvent.objects.filter(status__in=ELIGIBLE_EVENT_STATUSES)
        .values("publication_id")
        .annotate(first_created_at=Min("created_at"))
        .order_by("first_created_at", "publication_id")[:limit]
    )
    return [row["publication_id"] for row in rows]


def process_pending_catalogue_sync(
    *,
    limit: int = 100,
    publication_id=None,
    endpoint: str | None = None,
    timeout_seconds: float | None = None,
) -> dict[str, int]:
    """Process each selected publication at most once in this invocation."""
    _ensure_sync_enabled()
    if limit <= 0:
        raise ValueError("limit must be greater than zero.")

    if publication_id is not None:
        publication_ids = [publication_id]
    else:
        publication_ids = _eligible_publication_ids(limit)

    summary = {
        "selected": len(publication_ids),
        "succeeded": 0,
        "failed": 0,
        "noop": 0,
        "events": 0,
    }
    for selected_publication_id in publication_ids:
        result = process_publication_sync(
            selected_publication_id,
            endpoint=endpoint,
            timeout_seconds=timeout_seconds,
        )
        status = result["status"]
        summary[status] += 1
        summary["events"] += result["event_count"]
    return summary
