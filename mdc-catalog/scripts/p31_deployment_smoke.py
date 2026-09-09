#!/usr/bin/env python3
"""P3.1 safe deployment smoke checks.

Uses only Python stdlib. Never prints bearer credentials or DATABASE_URL values.
Set MDC_P31_BASE_URL to override the production alias. Set
MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN locally only when running the authenticated
lifecycle checks.
"""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = os.getenv("MDC_P31_BASE_URL", "https://maasai-mdc-v1.vercel.app").rstrip("/")
TOKEN = os.getenv("MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN", "").strip()
ACTOR = "p31:deployment-smoke"

SEARCH_PAYLOAD = {
    "request_id": "p31_smoke_001",
    "consumer_id": "p31_smoke",
    "service_category": "precision_gears",
    "part_family": "gear",
    "part_type": "spur_gear",
    "requirements": {},
}


def request(method: str, path: str, *, payload=None, headers=None):
    body = None
    resolved_headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        resolved_headers["Content-Type"] = "application/json"
    if headers:
        resolved_headers.update(headers)
    req = Request(BASE_URL + path, data=body, headers=resolved_headers, method=method)
    try:
        with urlopen(req, timeout=20) as response:
            raw = response.read()
            return response.status, json.loads(raw.decode("utf-8")) if raw else None
    except HTTPError as exc:
        raw = exc.read()
        try:
            payload_out = json.loads(raw.decode("utf-8")) if raw else None
        except Exception:
            payload_out = None
        return exc.code, payload_out
    except URLError as exc:
        raise RuntimeError("deployment endpoint unavailable") from exc


def expect(label: str, actual: int, expected: int):
    if actual != expected:
        raise AssertionError(f"{label}: expected HTTP {expected}, got {actual}")
    print(f"PASS {label}: {actual}")


def main() -> int:
    print(f"P3.1 smoke target: {BASE_URL}")

    code, data = request("GET", "/api/health")
    expect("canonical health", code, 200)
    if not isinstance(data, dict) or data.get("contract_version") != "1.0":
        raise AssertionError("canonical health did not return contract_version 1.0")

    code, _ = request("GET", "/api/catalog/filters")
    expect("canonical filters", code, 200)

    code, data = request("POST", "/api/service-discovery/search", payload=SEARCH_PAYLOAD)
    expect("canonical search", code, 200)
    if not isinstance(data, dict) or data.get("contract_version") != "1.0":
        raise AssertionError("canonical search did not return contract_version 1.0")

    for method, path, payload in (
        ("GET", "/api/v1/health", None),
        ("GET", "/api/v1/catalog/filters", None),
        ("POST", "/api/v1/service-discovery/search", SEARCH_PAYLOAD),
    ):
        code, _ = request(method, path, payload=payload)
        expect(f"absent {path}", code, 404)

    code, _ = request("GET", "/api/demo/health")
    expect("demo disabled", code, 404)

    code, _ = request("GET", "/api/providers/tasowheel")
    expect("anonymous lifecycle rejected", code, 401)

    code, _ = request("POST", "/api/provider-publication", payload={})
    expect("anonymous lifecycle write rejected", code, 401)

    if TOKEN:
        trusted = {
            "Authorization": f"Bearer {TOKEN}",
            "X-MDC-Actor-Id": ACTOR,
        }
        code, data = request("GET", "/api/providers/tasowheel", headers=trusted)
        expect("authenticated lifecycle DB read", code, 200)
        if not isinstance(data, dict) or data.get("provider_id") != "tasowheel":
            raise AssertionError("authenticated lifecycle read did not return tasowheel")

        code, _ = request(
            "POST",
            "/api/provider-publication",
            payload={},
            headers=trusted,
        )
        expect("authenticated lifecycle writes feature-disabled", code, 403)
    else:
        print("SKIP authenticated lifecycle checks: local service token env is not set")

    print("P3.1 deployment smoke PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"P3.1 deployment smoke FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
