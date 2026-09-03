from __future__ import annotations

import json
import socket
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from rdflib import Literal, URIRef

from apps.search.service_discovery_request import CanonicalServiceDiscoverySearchRequest
from apps.search.service_discovery_sparql_query_builder import (
    build_service_discovery_candidate_query,
    build_service_discovery_evidence_query,
)
from apps.search.service_discovery_sparql_service import (
    assemble_service_discovery_retrieval_projection,
    service_discovery_candidate_offering_resources,
)


class ServiceDiscoveryFusekiRetrievalError(Exception):
    pass


REMOTE_RETRIEVAL_ENGINE = "remote_harmonized_sparql_fuseki"
REMOTE_RETRIEVAL_MESSAGE = (
    "Candidate and evidence retrieval executed over the harmonized Fuseki dataset. "
    "Matching and scoring are not performed in H8."
)


def _configured_endpoint(endpoint: str | None) -> str:
    resolved = endpoint or getattr(settings, "SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT", "")
    if not resolved:
        raise ServiceDiscoveryFusekiRetrievalError(
            "SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT is not configured for harmonized Fuseki retrieval."
        )
    return resolved


def _binding_to_rdflib_value(binding: dict[str, Any]) -> Any:
    if not isinstance(binding, dict):
        raise ServiceDiscoveryFusekiRetrievalError("Malformed SPARQL result binding.")

    binding_type = binding.get("type")
    value = binding.get("value")
    if binding_type is None or value is None:
        raise ServiceDiscoveryFusekiRetrievalError("Malformed SPARQL result binding.")

    if binding_type == "uri":
        return URIRef(value)
    if binding_type in {"literal", "typed-literal"}:
        datatype = binding.get("datatype")
        if datatype:
            return Literal(value, datatype=URIRef(datatype))
        return Literal(value)

    raise ServiceDiscoveryFusekiRetrievalError(
        f"Unsupported SPARQL binding type in harmonized Fuseki result: {binding_type}"
    )


def _rows_from_sparql_json(result: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        bindings = result["results"]["bindings"]
    except (KeyError, TypeError) as exc:
        raise ServiceDiscoveryFusekiRetrievalError(
            "Fuseki returned malformed SPARQL JSON results."
        ) from exc

    if not isinstance(bindings, list):
        raise ServiceDiscoveryFusekiRetrievalError(
            "Fuseki returned malformed SPARQL JSON bindings."
        )

    rows: list[dict[str, Any]] = []
    for binding_row in bindings:
        if not isinstance(binding_row, dict):
            raise ServiceDiscoveryFusekiRetrievalError(
                "Fuseki returned a malformed SPARQL binding row."
            )
        rows.append(
            {
                variable_name: _binding_to_rdflib_value(binding)
                for variable_name, binding in binding_row.items()
            }
        )
    return rows


def execute_fuseki_sparql_query(
    query: str,
    *,
    endpoint: str | None = None,
    timeout_seconds: float = 10.0,
) -> list[dict]:
    if not query or not query.strip():
        raise ServiceDiscoveryFusekiRetrievalError("SPARQL query must not be empty.")

    resolved_endpoint = _configured_endpoint(endpoint)
    request_body = urlencode({"query": query}).encode("utf-8")
    request = Request(
        resolved_endpoint,
        data=request_body,
        headers={
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        raise ServiceDiscoveryFusekiRetrievalError(
            f"Harmonized Fuseki query failed with HTTP {error.code}: {error_body}"
        ) from error
    except (URLError, socket.timeout, TimeoutError) as error:
        raise ServiceDiscoveryFusekiRetrievalError(
            "Harmonized Fuseki query endpoint is unavailable."
        ) from error

    try:
        result = json.loads(response_body)
    except json.JSONDecodeError as error:
        raise ServiceDiscoveryFusekiRetrievalError(
            "Harmonized Fuseki query returned a non-JSON response."
        ) from error

    return _rows_from_sparql_json(result)


def retrieve_service_discovery_candidates_from_fuseki(
    canonical_request: CanonicalServiceDiscoverySearchRequest,
    *,
    endpoint: str | None = None,
    timeout_seconds: float = 10.0,
) -> dict:
    candidate_query = build_service_discovery_candidate_query(canonical_request)
    candidate_rows = execute_fuseki_sparql_query(
        candidate_query,
        endpoint=endpoint,
        timeout_seconds=timeout_seconds,
    )

    evidence_rows = []
    offering_resources = service_discovery_candidate_offering_resources(candidate_rows)
    if offering_resources:
        evidence_query = build_service_discovery_evidence_query(offering_resources)
        evidence_rows = execute_fuseki_sparql_query(
            evidence_query,
            endpoint=endpoint,
            timeout_seconds=timeout_seconds,
        )

    return assemble_service_discovery_retrieval_projection(
        canonical_request,
        candidate_rows=candidate_rows,
        evidence_rows=evidence_rows,
        retrieval_engine=REMOTE_RETRIEVAL_ENGINE,
        message=REMOTE_RETRIEVAL_MESSAGE,
    )
