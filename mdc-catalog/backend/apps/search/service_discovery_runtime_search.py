from copy import deepcopy

from django.conf import settings

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
    """
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
