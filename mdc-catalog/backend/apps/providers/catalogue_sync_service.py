"""Durable PostgreSQL outbox -> RDF/Fuseki synchronization.

PostgreSQL remains the operational source of truth. The semantic catalogue is
rebuilt from the current active DB-backed canonical projection and replaces the
configured Fuseki default graph through the Graph Store Protocol.
"""

from __future__ import annotations

import base64
import hashlib
import math
import socket
import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlparse
from urllib.request import Request, urlopen

from django.conf import settings
from django.db import DatabaseError, connection, transaction
from django.db.models import Count, Max, Min, Q
from django.utils import timezone
from rdflib import Literal

from apps.ontology.service_discovery_rdf_generator import (
    ServiceDiscoveryRdfGenerationError,
    build_service_discovery_graph,
)
from apps.ontology.service_discovery_rdf_mappings import MDC
from apps.providers.models import (
    CatalogueSyncEvent,
    CatalogueSyncLease,
    ProviderPublication,
)
from apps.providers.service_discovery_db_repository import (
    load_service_discovery_providers_from_db,
)
from apps.search.service_discovery_fuseki_service import (
    ServiceDiscoveryFusekiRetrievalError,
    execute_fuseki_sparql_query,
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


class CatalogueChangedDuringSync(CatalogueSyncError):
    """A newer committed lifecycle write made the just-built graph stale."""


class CatalogueSyncBusy(CatalogueSyncError):
    """Another worker owns the global graph-replacement lease."""


class CatalogueSyncVisibilityError(CatalogueSyncError):
    """The query endpoint did not expose the graph revision just written."""


class CatalogueSyncTransactionError(CatalogueSyncError):
    """Automatic synchronization was requested before the DB commit boundary."""


ELIGIBLE_EVENT_STATUSES = (
    CatalogueSyncEvent.Status.PENDING,
    CatalogueSyncEvent.Status.FAILED,
)
STALE_PROCESSING_FAILURE_CODE = "processing_lease_expired"
SYNC_LEASE_KEY = "service_discovery_catalogue"
MAX_REBUILD_ATTEMPTS = 3
CATALOGUE_STATE_SUBJECT = MDC.CatalogueState
CATALOGUE_REVISION_PREDICATE = MDC.catalogueRevision


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


def _graph_store_authorization_header() -> str | None:
    username = getattr(settings, "SERVICE_DISCOVERY_FUSEKI_USERNAME", "") or ""
    password = getattr(settings, "SERVICE_DISCOVERY_FUSEKI_PASSWORD", "") or ""
    username = username.strip()

    if bool(username) != bool(password):
        raise CatalogueSyncConfigurationError(
            "Fuseki synchronization username and password must be configured together."
        )
    if not username:
        return None

    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def _positive_finite_number(value, setting_name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise CatalogueSyncConfigurationError(
            f"{setting_name} must be a positive number."
        ) from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise CatalogueSyncConfigurationError(
            f"{setting_name} must be a positive number."
        )
    return parsed


def _timeout_seconds(timeout_seconds: float | None = None) -> float:
    value = (
        timeout_seconds
        if timeout_seconds is not None
        else getattr(settings, "FUSEKI_SYNC_TIMEOUT_SECONDS", 10.0)
    )
    return _positive_finite_number(value, "FUSEKI_SYNC_TIMEOUT_SECONDS")


def _processing_lease_seconds(stale_after_seconds: float | None = None) -> float:
    value = (
        stale_after_seconds
        if stale_after_seconds is not None
        else getattr(settings, "MDC_CATALOG_SYNC_PROCESSING_LEASE_SECONDS", 900)
    )
    return _positive_finite_number(
        value,
        "MDC_CATALOG_SYNC_PROCESSING_LEASE_SECONDS",
    )


def _configured_query_endpoint() -> str:
    endpoint = (
        getattr(settings, "SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT", "") or ""
    ).strip()
    if not endpoint:
        raise CatalogueSyncConfigurationError(
            "The service-discovery Fuseki query endpoint is not configured."
        )
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise CatalogueSyncConfigurationError(
            "The service-discovery Fuseki query endpoint must use HTTP or HTTPS."
        )
    return endpoint


def _dataset_identity(endpoint: str, expected_suffix: str) -> tuple[str, str, str]:
    parsed = urlparse(endpoint)
    path = parsed.path.rstrip("/")
    suffix = f"/{expected_suffix}"
    if not path.endswith(suffix):
        raise CatalogueSyncConfigurationError(
            "The Fuseki endpoints must use canonical dataset paths."
        )
    return parsed.scheme.lower(), parsed.netloc.lower(), path[: -len(suffix)]


def validate_authoritative_fuseki_configuration() -> tuple[str, str]:
    """Require query and default Graph Store endpoints for one dataset."""
    query_endpoint = _configured_query_endpoint()
    graph_endpoint = _configured_graph_store_endpoint()
    if _dataset_identity(query_endpoint, "sparql") != _dataset_identity(
        graph_endpoint, "data"
    ):
        raise CatalogueSyncConfigurationError(
            "The Fuseki query and Graph Store endpoints must target the same dataset."
        )
    graph_query = dict(parse_qsl(urlparse(graph_endpoint).query, keep_blank_values=True))
    if "default" not in graph_query:
        raise CatalogueSyncConfigurationError(
            "Automatic synchronization requires the Fuseki default graph endpoint."
        )
    return query_endpoint, graph_endpoint


def _acquire_sync_lease() -> uuid.UUID:
    owner_token = uuid.uuid4()
    now = timezone.now()
    expires_at = now + timedelta(seconds=_processing_lease_seconds())
    with transaction.atomic():
        lease, _created = CatalogueSyncLease.objects.select_for_update().get_or_create(
            key=SYNC_LEASE_KEY
        )
        if (
            lease.owner_token is not None
            and lease.expires_at is not None
            and lease.expires_at > now
        ):
            raise CatalogueSyncBusy(
                "Catalogue synchronization is already in progress."
            )
        lease.owner_token = owner_token
        lease.expires_at = expires_at
        lease.save(update_fields=["owner_token", "expires_at", "updated_at"])
    return owner_token


def _release_sync_lease(owner_token: uuid.UUID) -> None:
    with transaction.atomic():
        lease = (
            CatalogueSyncLease.objects.select_for_update()
            .filter(key=SYNC_LEASE_KEY)
            .first()
        )
        if lease is None or lease.owner_token != owner_token:
            return
        lease.owner_token = None
        lease.expires_at = None
        lease.save(update_fields=["owner_token", "expires_at", "updated_at"])


def replace_service_discovery_graph_in_fuseki(
    graph,
    *,
    endpoint: str | None = None,
    timeout_seconds: float | None = None,
) -> None:
    """Replace the configured Fuseki default graph with one Turtle document."""
    resolved_endpoint = _configured_graph_store_endpoint(endpoint)
    timeout = _timeout_seconds(timeout_seconds)
    authorization = _graph_store_authorization_header()
    try:
        serialized = graph.serialize(format="turtle")
    except Exception:
        raise ServiceDiscoveryRdfGenerationError(
            "Catalogue RDF serialization failed."
        ) from None
    body = serialized if isinstance(serialized, bytes) else serialized.encode("utf-8")
    headers = {
        "Content-Type": "text/turtle; charset=utf-8",
        "Accept": "text/plain, */*;q=0.1",
    }
    if authorization:
        headers["Authorization"] = authorization
    request = Request(
        resolved_endpoint,
        data=body,
        headers=headers,
        method="PUT",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
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


def _catalogue_write_watermark() -> tuple[int, Any]:
    value = CatalogueSyncEvent.objects.aggregate(
        total=Count("id"), latest_created_at=Max("created_at")
    )
    return value["total"], value["latest_created_at"]


def _revision_for_watermark(watermark: tuple[int, Any]) -> str:
    total, latest_created_at = watermark
    latest = latest_created_at.isoformat() if latest_created_at is not None else "none"
    return hashlib.sha256(f"{total}:{latest}".encode("utf-8")).hexdigest()


def _add_catalogue_revision(graph, revision: str) -> None:
    graph.add(
        (
            CATALOGUE_STATE_SUBJECT,
            CATALOGUE_REVISION_PREDICATE,
            Literal(revision),
        )
    )


def _query_visible_revision(
    *,
    query_endpoint: str,
    timeout_seconds: float | None = None,
) -> str:
    timeout = _timeout_seconds(timeout_seconds)
    query = f"""
        SELECT ?revision WHERE {{
            <{CATALOGUE_STATE_SUBJECT}> <{CATALOGUE_REVISION_PREDICATE}> ?revision .
        }}
        LIMIT 2
    """
    try:
        rows = execute_fuseki_sparql_query(
            query,
            endpoint=query_endpoint,
            timeout_seconds=timeout,
        )
    except ServiceDiscoveryFusekiRetrievalError as exc:
        raise CatalogueSyncVisibilityError(
            "The synchronized Fuseki revision could not be queried."
        ) from exc
    if len(rows) != 1 or "revision" not in rows[0]:
        raise CatalogueSyncVisibilityError(
            "The synchronized Fuseki revision marker is missing or ambiguous."
        )
    return str(rows[0]["revision"])


def verify_current_catalogue_visibility(
    *,
    timeout_seconds: float | None = None,
) -> str:
    """Confirm that canonical Fuseki reads the current committed DB revision."""
    _ensure_sync_enabled()
    query_endpoint, _graph_endpoint = validate_authoritative_fuseki_configuration()
    watermark = _catalogue_write_watermark()
    expected = _revision_for_watermark(watermark)
    visible = _query_visible_revision(
        query_endpoint=query_endpoint,
        timeout_seconds=timeout_seconds,
    )
    if visible != expected or _catalogue_write_watermark() != watermark:
        raise CatalogueSyncVisibilityError(
            "Fuseki does not expose the current committed catalogue revision."
        )
    return expected


def _publish_current_graph(
    *,
    endpoint: str | None = None,
    timeout_seconds: float | None = None,
    verify_visibility: bool = False,
) -> dict[str, Any]:
    query_endpoint = None
    graph_endpoint = endpoint
    if verify_visibility:
        query_endpoint, configured_graph_endpoint = (
            validate_authoritative_fuseki_configuration()
        )
        graph_endpoint = endpoint or configured_graph_endpoint

    for _attempt_number in range(MAX_REBUILD_ATTEMPTS):
        watermark_before = _catalogue_write_watermark()
        graph = _build_current_db_graph()
        business_triple_count = len(graph)
        revision = _revision_for_watermark(watermark_before)
        _add_catalogue_revision(graph, revision)
        if _catalogue_write_watermark() != watermark_before:
            continue

        replace_service_discovery_graph_in_fuseki(
            graph,
            endpoint=graph_endpoint,
            timeout_seconds=timeout_seconds,
        )
        if _catalogue_write_watermark() != watermark_before:
            continue

        if verify_visibility:
            visible = _query_visible_revision(
                query_endpoint=query_endpoint,
                timeout_seconds=timeout_seconds,
            )
            if visible != revision:
                raise CatalogueSyncVisibilityError(
                    "Fuseki did not expose the synchronized catalogue revision."
                )
            if _catalogue_write_watermark() != watermark_before:
                continue

        return {
            "triple_count": business_triple_count,
            "revision": revision,
        }
    raise CatalogueChangedDuringSync()


def rebuild_service_discovery_catalogue(
    *,
    endpoint: str | None = None,
    timeout_seconds: float | None = None,
) -> dict[str, int]:
    """Explicit DB -> RDF -> Fuseki rebuild without fabricating outbox history."""
    _ensure_sync_enabled()
    lease_token = _acquire_sync_lease()
    try:
        result = _publish_current_graph(
            endpoint=endpoint,
            timeout_seconds=timeout_seconds,
            verify_visibility=getattr(
                settings, "MDC_CATALOG_AUTO_SYNC_ENABLED", False
            ),
        )
        return {"triple_count": result["triple_count"]}
    finally:
        _release_sync_lease(lease_token)


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

        claimed_at = timezone.now()
        for event in events:
            event.status = CatalogueSyncEvent.Status.PROCESSING
            event.attempt_count += 1
            event.last_error = ""
            # M7.6 uses processed_at as the processing lease start while a row is
            # PROCESSING, then replaces it with success/failure completion time.
            event.processed_at = claimed_at
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


def recover_stale_processing_sync(
    *,
    stale_after_seconds: float | None = None,
) -> dict[str, int]:
    """Return abandoned PROCESSING rows to a visible, retryable failed state.

    Recovery is database-only. It never calls RDF generation or Fuseki. Rows are
    locked before mutation so a finalizer cannot be silently overwritten.
    """
    _ensure_sync_enabled()
    lease_seconds = _processing_lease_seconds(stale_after_seconds)
    now = timezone.now()
    cutoff = now - timedelta(seconds=lease_seconds)

    with transaction.atomic():
        stale_events = list(
            CatalogueSyncEvent.objects.select_for_update()
            .filter(status=CatalogueSyncEvent.Status.PROCESSING)
            .filter(
                Q(processed_at__lt=cutoff)
                | Q(processed_at__isnull=True, created_at__lt=cutoff)
            )
            .order_by("created_at", "id")
        )
        if not stale_events:
            return {"events": 0, "publications": 0}

        publication_ids = {event.publication_id for event in stale_events}
        publications = {
            publication.id: publication
            for publication in ProviderPublication.objects.select_for_update().filter(
                id__in=publication_ids
            )
        }

        for event in stale_events:
            event.status = CatalogueSyncEvent.Status.FAILED
            event.last_error = STALE_PROCESSING_FAILURE_CODE
            event.processed_at = now
        CatalogueSyncEvent.objects.bulk_update(
            stale_events,
            ["status", "last_error", "processed_at"],
        )

        for publication in publications.values():
            publication.status = ProviderPublication.Status.SYNC_FAILED
            publication.completed_at = None
        ProviderPublication.objects.bulk_update(
            list(publications.values()),
            ["status", "completed_at"],
        )

    return {
        "events": len(stale_events),
        "publications": len(publications),
    }


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
    if isinstance(exc, CatalogueChangedDuringSync):
        return "catalogue_changed_during_sync"
    if isinstance(exc, CatalogueSyncTransportError):
        return "fuseki_transport_error"
    if isinstance(exc, CatalogueSyncConfigurationError):
        return "sync_configuration_error"
    if isinstance(exc, CatalogueSyncVisibilityError):
        return "query_visibility_error"
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
    verify_visibility: bool = False,
) -> dict[str, Any]:
    """Attempt one publication once; failed events are retryable on a later call."""
    _ensure_sync_enabled()
    if verify_visibility and connection.in_atomic_block:
        raise CatalogueSyncTransactionError(
            "Automatic synchronization must run after the lifecycle transaction commits."
        )
    if verify_visibility:
        validate_authoritative_fuseki_configuration()
    lease_token = _acquire_sync_lease()
    try:
        attempt = _claim_publication(publication_id)
        if attempt is None:
            if verify_visibility:
                publication = ProviderPublication.objects.get(pk=publication_id)
                if publication.status == ProviderPublication.Status.SYNCED:
                    verify_current_catalogue_visibility(
                        timeout_seconds=timeout_seconds
                    )
            return {"status": "noop", "event_count": 0, "triple_count": 0}

        result = _publish_current_graph(
            endpoint=endpoint,
            timeout_seconds=timeout_seconds,
            verify_visibility=verify_visibility,
        )
        _finalize_success(attempt)
        return {
            "status": "succeeded",
            "event_count": len(attempt.event_ids),
            "triple_count": result["triple_count"],
            "revision": result["revision"],
        }
    except CatalogueSyncBusy:
        raise
    except Exception as exc:
        if "attempt" not in locals() or attempt is None:
            raise
        failure_code = _safe_failure_code(exc)
        _finalize_failure(attempt, failure_code)
        return {
            "status": "failed",
            "event_count": len(attempt.event_ids),
            "triple_count": 0,
            "failure_code": failure_code,
        }
    finally:
        _release_sync_lease(lease_token)


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
            verify_visibility=getattr(
                settings, "MDC_CATALOG_AUTO_SYNC_ENABLED", False
            ),
        )
        status_name = result["status"]
        summary[status_name] += 1
        summary["events"] += result["event_count"]
    return summary
