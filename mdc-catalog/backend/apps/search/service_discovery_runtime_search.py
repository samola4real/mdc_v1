from copy import deepcopy

from django.conf import settings

from apps.providers.catalogue_sync_service import (
    CatalogueSyncError,
    verify_current_catalogue_visibility,
)

from apps.search.service_discovery_fuseki_service import (
    ServiceDiscoveryFusekiRetrievalError,
)
from apps.search.service_discovery_local_matcher import (
    search_service_discovery_catalog,
)
from apps.search.service_discovery_matching_alignment import (
    ServiceDiscoveryMatchingAlignmentError,
    search_service_discovery_catalog_via_fuseki,
    search_service_discovery_catalog_via_local_rdf,
)
from apps.search.service_discovery_request import (
    CanonicalServiceDiscoverySearchRequest,
)
from apps.search.service_discovery_sparql_service import (
    ServiceDiscoverySparqlRetrievalError,
)


class ServiceDiscoveryRuntimeSearchError(Exception):
    pass


RECOVERABLE_SEARCH_ERRORS = (
    ServiceDiscoveryFusekiRetrievalError,
    ServiceDiscoverySparqlRetrievalError,
    ServiceDiscoveryMatchingAlignmentError,
    OSError,
    TimeoutError,
)


FUSEKI_FALLBACK_WARNING = (
    "Primary Fuseki backend unavailable; used local RDFLib fallback."
)
YAML_FALLBACK_WARNING = (
    "Fuseki and RDFLib backends unavailable; used harmonized YAML fallback."
)


def _with_added_warnings(response: dict, warnings: list[str]) -> dict:
    updated = deepcopy(response)
    updated["warnings"] = [
        *updated.get("warnings", []),
        *warnings,
    ]
    return updated


def search_service_discovery_with_runtime_backends(
    canonical_request: CanonicalServiceDiscoverySearchRequest,
) -> dict:
    """
    Try Fuseki+H5, then RDFLib+H5, then harmonized YAML+H5.

    Automatic publication mode is deliberately authoritative: it first proves
    that canonical Fuseki exposes the current DB revision and never falls back
    to checked-in RDF/YAML that may still contain deleted or stale offerings.
    """
    if getattr(settings, "MDC_CATALOG_AUTO_SYNC_ENABLED", False):
        try:
            revision_before = verify_current_catalogue_visibility(
                timeout_seconds=getattr(settings, "FUSEKI_TIMEOUT_SECONDS", 10.0)
            )
            response = search_service_discovery_catalog_via_fuseki(
                canonical_request,
                timeout_seconds=getattr(settings, "FUSEKI_TIMEOUT_SECONDS", 10.0),
            )
            revision_after = verify_current_catalogue_visibility(
                timeout_seconds=getattr(settings, "FUSEKI_TIMEOUT_SECONDS", 10.0)
            )
            if revision_after != revision_before:
                raise ServiceDiscoveryRuntimeSearchError(
                    "The authoritative catalogue changed during search."
                )
            return response
        except (CatalogueSyncError, *RECOVERABLE_SEARCH_ERRORS) as exc:
            raise ServiceDiscoveryRuntimeSearchError(
                "The authoritative service-discovery catalogue is unavailable."
            ) from exc

    failure_messages = []

    try:
        return search_service_discovery_catalog_via_fuseki(
            canonical_request,
            timeout_seconds=getattr(settings, "FUSEKI_TIMEOUT_SECONDS", 10.0),
        )
    except RECOVERABLE_SEARCH_ERRORS as exc:
        failure_messages.append(f"Fuseki backend failed: {exc}")

    try:
        response = search_service_discovery_catalog_via_local_rdf(canonical_request)
        return _with_added_warnings(response, [FUSEKI_FALLBACK_WARNING])
    except RECOVERABLE_SEARCH_ERRORS as exc:
        failure_messages.append(f"RDFLib backend failed: {exc}")

    try:
        response = search_service_discovery_catalog(canonical_request)
        return _with_added_warnings(response, [YAML_FALLBACK_WARNING])
    except RECOVERABLE_SEARCH_ERRORS as exc:
        failure_messages.append(f"YAML backend failed: {exc}")

    raise ServiceDiscoveryRuntimeSearchError(
        "All service-discovery search backends failed."
    )
