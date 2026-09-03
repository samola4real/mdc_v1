

import json
import socket
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


class SparqlClientError(Exception):
    """
    Base error for SPARQL client failures.
    """


class SparqlEndpointUnavailable(SparqlClientError):
    """
    Raised when Fuseki cannot be reached.
    """


class SparqlQueryError(SparqlClientError):
    """
    Raised when Fuseki rejects or fails a SPARQL query.
    """


def get_fuseki_query_endpoint() -> str:
    """
    Return configured Fuseki SPARQL query endpoint.
    """
    return settings.FUSEKI_QUERY_ENDPOINT


def get_fuseki_timeout_seconds() -> float:
    """
    Return configured Fuseki request timeout.
    """
    return settings.FUSEKI_TIMEOUT_SECONDS


def execute_select_query(query: str) -> dict[str, Any]:
    """
    Execute a SPARQL SELECT query against Fuseki.

    Returns raw SPARQL JSON results:

    {
        "head": {"vars": [...]},
        "results": {"bindings": [...]}
    }

    This function should only be called when Fuseki is running.
    """
    if not query or not query.strip():
        raise SparqlQueryError("SPARQL query must not be empty.")

    request_body = urlencode(
        {
            "query": query,
        }
    ).encode("utf-8")

    request = Request(
        get_fuseki_query_endpoint(),
        data=request_body,
        headers={
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urlopen(
            request,
            timeout=get_fuseki_timeout_seconds(),
        ) as response:
            response_body = response.read().decode("utf-8")

    except HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        raise SparqlQueryError(
            f"Fuseki query failed with HTTP {error.code}: {error_body}"
        ) from error

    except (URLError, socket.timeout, TimeoutError) as error:
        raise SparqlEndpointUnavailable(
            f"Fuseki endpoint is unavailable: {get_fuseki_query_endpoint()}"
        ) from error

    try:
        return json.loads(response_body)

    except json.JSONDecodeError as error:
        raise SparqlQueryError(
            "Fuseki returned a non-JSON response."
        ) from error


def get_bindings(result: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extract result bindings from a SPARQL SELECT JSON response.
    """
    return result.get("results", {}).get("bindings", [])


def binding_value(
    binding: dict[str, Any],
    variable_name: str,
    default: Any = None,
) -> Any:
    """
    Extract one variable value from a SPARQL JSON binding.

    Example SPARQL JSON binding:

    {
        "providerId": {
            "type": "literal",
            "value": "tasowheel"
        }
    }
    """
    variable = binding.get(variable_name)

    if not isinstance(variable, dict):
        return default

    return variable.get("value", default)