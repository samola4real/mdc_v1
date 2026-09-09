#!/usr/bin/env python3
"""P3.3 direct-Fuseki and deployed-discovery verification.

Use --direct-only before configuring Vercel. Without --direct-only the script
also requires the canonical deployed search to return the DB-created P3.2 pilot
provider, which proves the deployed runtime can consume the synchronized graph.
No credentials or full endpoint URLs are printed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOTENV_PATH = PROJECT_ROOT / ".env"
MDC_NS = "https://maasai-project.eu/ontology/mdc#"
PROVIDER_ID = "p32_pilot_provider"
OFFERING_ID = "p32_pilot_provider_precision_metal_parts"
BASE_URL = os.getenv("MDC_P33_BASE_URL", "https://maasai-mdc-v1.vercel.app").rstrip("/")

SEARCH_PAYLOAD = {
    "request_id": "p33_fuseki_probe_001",
    "consumer_id": "p33_fuseki_probe",
    "service_category": "precision_metal_parts",
    "part_family": "metal_part",
    "part_type": "bracket",
    "requirements": {},
}


def read_dotenv_value(name: str) -> str:
    if not DOTENV_PATH.exists():
        return ""
    for raw_line in DOTENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == name:
            return value.strip().strip('"').strip("'")
    return ""


def env_value(name: str) -> str:
    return (os.getenv(name) or read_dotenv_value(name)).strip()


def sparql_json(endpoint: str, query: str) -> dict:
    body = urlencode({"query": query}).encode("utf-8")
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
        with urlopen(req, timeout=20) as response:
            raw = response.read()
            if response.status < 200 or response.status >= 300:
                raise AssertionError(f"Fuseki query returned HTTP {response.status}")
    except HTTPError as exc:
        raise AssertionError(f"Fuseki query returned HTTP {exc.code}") from None
    except (URLError, TimeoutError, OSError):
        raise AssertionError("Fuseki query endpoint is unreachable") from None
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        raise AssertionError("Fuseki query response was not JSON") from None
    if not isinstance(data, dict):
        raise AssertionError("Fuseki query response was not an object")
    return data


def ask(endpoint: str, pattern: str) -> bool:
    data = sparql_json(endpoint, f"ASK {{ {pattern} }}")
    return data.get("boolean") is True


def triple_count(endpoint: str) -> int:
    data = sparql_json(endpoint, "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }")
    try:
        return int(data["results"]["bindings"][0]["count"]["value"])
    except Exception:
        raise AssertionError("Could not read Fuseki triple count") from None


def deployed_search() -> dict:
    body = json.dumps(SEARCH_PAYLOAD).encode("utf-8")
    req = Request(
        BASE_URL + "/api/service-discovery/search",
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=25) as response:
            raw = response.read()
            if response.status != 200:
                raise AssertionError(f"deployed canonical search returned HTTP {response.status}")
    except HTTPError as exc:
        raise AssertionError(f"deployed canonical search returned HTTP {exc.code}") from None
    except (URLError, TimeoutError, OSError):
        raise AssertionError("deployed canonical search is unreachable") from None
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        raise AssertionError("deployed canonical search did not return JSON") from None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--direct-only", action="store_true")
    args = parser.parse_args()

    endpoint = env_value("SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT")
    if not endpoint:
        raise AssertionError("SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT is not configured locally")

    count = triple_count(endpoint)
    if count <= 0:
        raise AssertionError("Fuseki graph contains no triples")
    print(f"PASS Fuseki graph contains triples: {count}")

    provider_pattern = f'?provider <{MDC_NS}providerId> "{PROVIDER_ID}" .'
    if not ask(endpoint, provider_pattern):
        raise AssertionError(f"Fuseki graph does not contain provider {PROVIDER_ID}")
    print(f"PASS Fuseki contains provider: {PROVIDER_ID}")

    offering_pattern = f'?offering <{MDC_NS}offeringId> "{OFFERING_ID}" .'
    if not ask(endpoint, offering_pattern):
        raise AssertionError(f"Fuseki graph does not contain offering {OFFERING_ID}")
    print(f"PASS Fuseki contains offering: {OFFERING_ID}")

    if args.direct_only:
        print("P3.3 direct Fuseki verification PASS")
        return 0

    data = deployed_search()
    if data.get("contract_version") != "1.0":
        raise AssertionError("deployed canonical search contract_version is not 1.0")
    results = data.get("results")
    if not isinstance(results, list):
        raise AssertionError("deployed canonical search results are missing")
    provider_ids = {item.get("provider_id") for item in results if isinstance(item, dict)}
    if PROVIDER_ID not in provider_ids:
        raise AssertionError(
            "deployed canonical search did not return the DB-created P3.2 pilot provider"
        )
    print(f"PASS deployed canonical search returned synchronized provider: {PROVIDER_ID}")
    print("P3.3 Fuseki/deployed discovery verification PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"P3.3 Fuseki verification FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
