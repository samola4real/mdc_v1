#!/usr/bin/env python3
"""P3.3 non-mutating real-Fuseki preflight.

Reads only the specific required values from the process environment or the
project .env file. Endpoint values and DATABASE_URL are never printed in full.
Credentials are never printed. No Fuseki graph write occurs.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOTENV_PATH = PROJECT_ROOT / ".env"
REQUIRED = (
    "DATABASE_URL",
    "SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT",
    "SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT",
)
USERNAME_NAME = "SERVICE_DISCOVERY_FUSEKI_USERNAME"
PASSWORD_NAME = "SERVICE_DISCOVERY_FUSEKI_PASSWORD"


def read_dotenv_value(name: str) -> str:
    """Read .env with last-assignment-wins semantics, matching dotenv behavior."""
    if not DOTENV_PATH.exists():
        return ""
    resolved = ""
    for raw_line in DOTENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        if key.strip() != name:
            continue
        resolved = raw_value.strip().strip('"').strip("'")
    return resolved


def value(name: str) -> str:
    return (os.getenv(name) or read_dotenv_value(name)).strip()


def safe_endpoint_label(raw: str) -> str:
    parsed = urlparse(raw)
    host = parsed.hostname or "<missing-host>"
    port = f":{parsed.port}" if parsed.port else ""
    query_marker = "?default" if parsed.query == "default" else ""
    return f"{parsed.scheme}://{host}{port}{parsed.path}{query_marker}"


def validate_http_url(name: str, raw: str):
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise AssertionError(f"{name} must be a valid HTTP(S) URL")
    return parsed


def authorization_header(username: str, password: str) -> str | None:
    if bool(username) != bool(password):
        raise AssertionError(
            "SERVICE_DISCOVERY_FUSEKI_USERNAME and SERVICE_DISCOVERY_FUSEKI_PASSWORD must be configured together"
        )
    if not username:
        return None
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def query_ask(endpoint: str) -> bool:
    sparql = "ASK { ?s ?p ?o }"
    body = urlencode({"query": sparql}).encode("utf-8")
    req = Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Accept": "application/sparql-results+json, application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=15) as response:
            raw = response.read()
            if response.status < 200 or response.status >= 300:
                raise AssertionError(f"Fuseki query endpoint returned HTTP {response.status}")
    except HTTPError as exc:
        raise AssertionError(f"Fuseki query endpoint returned HTTP {exc.code}") from None
    except (URLError, TimeoutError, OSError):
        raise AssertionError("Fuseki query endpoint is unreachable") from None

    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        raise AssertionError("Fuseki query endpoint did not return SPARQL JSON") from None
    if not isinstance(data, dict) or "boolean" not in data:
        raise AssertionError("Fuseki query endpoint response was not an ASK result")
    return bool(data["boolean"])


def graph_store_head(endpoint: str, auth_header: str | None) -> int:
    headers = {"Accept": "text/turtle, */*;q=0.1"}
    if auth_header:
        headers["Authorization"] = auth_header
    req = Request(endpoint, headers=headers, method="HEAD")
    try:
        with urlopen(req, timeout=15) as response:
            return response.status
    except HTTPError as exc:
        return exc.code
    except (URLError, TimeoutError, OSError):
        raise AssertionError("Fuseki graph-store endpoint is unreachable") from None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-remote",
        action="store_true",
        help="Fail if the query endpoint is localhost-only; use for the final Vercel gate.",
    )
    args = parser.parse_args()

    resolved = {name: value(name) for name in REQUIRED}
    missing = [name for name, item in resolved.items() if not item]
    if missing:
        print("P3.3 Fuseki preflight FAIL: missing configuration:", file=sys.stderr)
        for name in missing:
            print(f"- {name}", file=sys.stderr)
        return 1

    print("PASS DATABASE_URL configured (value hidden)")

    query = resolved["SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT"]
    graph_store = resolved["SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT"]
    username = value(USERNAME_NAME)
    password = value(PASSWORD_NAME)
    auth_header = authorization_header(username, password)

    query_parsed = validate_http_url("SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT", query)
    graph_parsed = validate_http_url("SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT", graph_store)

    print(f"PASS Fuseki query endpoint configured: {safe_endpoint_label(query)}")
    print(f"PASS Fuseki graph-store endpoint configured: {safe_endpoint_label(graph_store)}")
    if auth_header:
        print("PASS Fuseki write credentials configured (values hidden)")
    else:
        print("INFO Fuseki write credentials not configured")

    local_hosts = {"localhost", "127.0.0.1", "::1"}
    query_is_local = (query_parsed.hostname or "").lower() in local_hosts
    if args.require_remote and query_is_local:
        raise AssertionError(
            "Fuseki query endpoint is localhost-only; the final Vercel discovery gate needs a remotely reachable endpoint"
        )
    if query_is_local:
        print("INFO Fuseki is local-only; local synchronization gate can proceed, remote/Vercel gate remains pending")

    if (query_parsed.hostname or "").lower() != (graph_parsed.hostname or "").lower():
        print("WARN query and graph-store endpoints use different hosts; verify they target the same dedicated dataset")

    has_any_triples = query_ask(query)
    print(f"PASS Fuseki SPARQL ASK reachable (graph_has_triples={str(has_any_triples).lower()})")

    status = graph_store_head(graph_store, auth_header)
    if status == 401:
        raise AssertionError("Fuseki graph-store endpoint requires valid write credentials (HTTP 401)")
    if status == 403:
        raise AssertionError("Fuseki graph-store credentials are authenticated but not authorized (HTTP 403)")
    if status < 200 or status >= 300:
        raise AssertionError(f"Fuseki graph-store HEAD returned HTTP {status}")
    print(f"PASS Fuseki graph-store authenticated HEAD: {status}")

    print("PASS no graph write attempted")
    print("P3.3 Fuseki preflight PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"P3.3 Fuseki preflight FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
