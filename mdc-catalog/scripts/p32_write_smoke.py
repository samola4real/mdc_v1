#!/usr/bin/env python3
"""P3.2 Stage B trusted lifecycle write smoke.

This is a controlled pilot write against the deployed lifecycle API. It creates
(or safely reuses on rerun) one clearly named P3.2 pilot provider, exercises
provider and offering optimistic concurrency, and keeps semantic sync disabled.

The production Vercel pilot uses X-MDC-If-Match rather than the standard
If-Match request header because the platform boundary can apply HTTP
conditional semantics after the Django write has already committed. The API
continues to support canonical If-Match; this script uses the transport-safe
pilot alias only for the temporary Vercel deployment.

The bearer token is read from the environment and is never printed.
"""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = os.getenv("MDC_P32_BASE_URL", "https://maasai-mdc-v1.vercel.app").rstrip("/")
TOKEN = os.getenv("MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN", "").strip()
ACTOR = "p32:trusted-write-smoke"
PROVIDER_ID = "p32_pilot_provider"
OFFERING_ID = f"{PROVIDER_ID}_precision_gears"
CONCURRENCY_HEADER = "X-MDC-If-Match"

PROVIDER_PAYLOAD = {
    "contract_version": "1.0",
    "provider_id": PROVIDER_ID,
    "provider_name": "P3.2 Trusted Pilot Provider",
    "country": "Finland",
    "certifications": [],
    "custom_provider_fields": {"pilot_scope": "p3.2_trusted_lifecycle"},
    "offerings": [
        {
            "service_category": "precision_metal_parts",
            "offering_name": "Pilot precision metal parts",
            "part_family": "metal_part",
            "support_status": "confirmed",
            "supported_part_types": [
                {
                    "part_type": "bracket",
                    "support_status": "confirmed",
                    "source_type": "provider_confirmed",
                    "confidence": "declared",
                }
            ],
            "part_type_capabilities": {},
            "generic_capabilities": {},
        }
    ],
}

SECOND_OFFERING_PAYLOAD = {
    "contract_version": "1.0",
    "service_category": "precision_gears",
    "offering_name": "Pilot precision gears",
    "part_family": "gear",
    "support_status": "confirmed",
    "supported_part_types": [],
    "family_capabilities": {},
    "part_type_capabilities": {},
    "generic_capabilities": {},
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
        with urlopen(req, timeout=25) as response:
            raw = response.read()
            data = json.loads(raw.decode("utf-8")) if raw else None
            return response.status, data, dict(response.headers.items())
    except HTTPError as exc:
        raw = exc.read()
        try:
            data = json.loads(raw.decode("utf-8")) if raw else None
        except Exception:
            data = None
        return exc.code, data, dict(exc.headers.items())
    except URLError as exc:
        raise RuntimeError("deployment endpoint unavailable") from exc


def expect(label: str, actual: int, expected: int):
    if actual != expected:
        raise AssertionError(f"{label}: expected HTTP {expected}, got {actual}")
    print(f"PASS {label}: {actual}")


def require_etag(headers: dict[str, str], label: str) -> str:
    etag = headers.get("ETag") or headers.get("Etag") or headers.get("etag")
    if not etag:
        raise AssertionError(f"{label}: missing ETag")
    return etag


def main() -> int:
    if not TOKEN:
        raise RuntimeError("MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN is not set locally")

    print(f"P3.2 Stage B target: {BASE_URL}")
    trusted = {
        "Authorization": f"Bearer {TOKEN}",
        "X-MDC-Actor-Id": ACTOR,
    }

    code, data, _ = request("GET", "/api/health")
    expect("public health unchanged", code, 200)
    if not isinstance(data, dict) or data.get("contract_version") != "1.0":
        raise AssertionError("health contract_version is not 1.0")

    code, _, _ = request("POST", "/api/provider-publication", payload=PROVIDER_PAYLOAD)
    expect("anonymous provider registration rejected", code, 401)

    code, data, _ = request(
        "POST", "/api/provider-publication", payload=PROVIDER_PAYLOAD, headers=trusted
    )
    if code == 201:
        print("PASS authenticated provider registration: 201")
        if not isinstance(data, dict) or data.get("provider_id") != PROVIDER_ID:
            raise AssertionError("provider registration returned unexpected provider")
        if data.get("publication_status") != "sync_pending":
            raise AssertionError("provider registration was not persisted as sync_pending")
    elif code == 409:
        print("PASS authenticated provider registration: existing pilot provider reused (409)")
    else:
        raise AssertionError(f"authenticated provider registration: expected 201/409, got {code}")

    code, data, headers = request("GET", f"/api/providers/{PROVIDER_ID}", headers=trusted)
    expect("trusted provider read", code, 200)
    if not isinstance(data, dict) or data.get("provider_id") != PROVIDER_ID:
        raise AssertionError("trusted provider read returned unexpected provider")
    provider_etag = require_etag(headers, "provider read")

    provider_patch = {
        "contract_version": "1.0",
        "custom_provider_fields": {
            "pilot_scope": "p3.2_trusted_lifecycle",
            "verified": True,
        },
    }
    patch_headers = dict(trusted)
    patch_headers[CONCURRENCY_HEADER] = provider_etag
    code, data, headers = request(
        "PATCH",
        f"/api/providers/{PROVIDER_ID}",
        payload=provider_patch,
        headers=patch_headers,
    )
    expect("provider update with current revision", code, 200)
    if not isinstance(data, dict) or data.get("publication_status") != "sync_pending":
        raise AssertionError("provider update did not create sync_pending publication")
    new_provider_etag = require_etag(headers, "provider update")
    if new_provider_etag == provider_etag:
        raise AssertionError("provider ETag did not change after update")

    code, _, _ = request(
        "PATCH",
        f"/api/providers/{PROVIDER_ID}",
        payload=provider_patch,
        headers=patch_headers,
    )
    expect("stale provider revision rejected", code, 412)

    code, data, _ = request(
        "POST",
        f"/api/providers/{PROVIDER_ID}/offerings",
        payload=SECOND_OFFERING_PAYLOAD,
        headers=trusted,
    )
    if code == 201:
        print("PASS authenticated offering creation: 201")
        if not isinstance(data, dict) or data.get("offering_id") != OFFERING_ID:
            raise AssertionError("offering creation returned unexpected offering_id")
    elif code == 409:
        print("PASS authenticated offering creation: existing pilot offering reused (409)")
    else:
        raise AssertionError(f"authenticated offering creation: expected 201/409, got {code}")

    code, data, headers = request("GET", f"/api/offerings/{OFFERING_ID}", headers=trusted)
    expect("trusted offering read", code, 200)
    if not isinstance(data, dict) or data.get("offering_id") != OFFERING_ID:
        raise AssertionError("trusted offering read returned unexpected offering")
    offering_etag = require_etag(headers, "offering read")

    offering_patch = {
        "contract_version": "1.0",
        "offering_name": "Pilot precision gears - verified",
    }
    offering_patch_headers = dict(trusted)
    offering_patch_headers[CONCURRENCY_HEADER] = offering_etag
    code, data, headers = request(
        "PATCH",
        f"/api/offerings/{OFFERING_ID}",
        payload=offering_patch,
        headers=offering_patch_headers,
    )
    expect("offering update with current revision", code, 200)
    if not isinstance(data, dict) or data.get("publication_status") != "sync_pending":
        raise AssertionError("offering update did not create sync_pending publication")
    new_offering_etag = require_etag(headers, "offering update")
    if new_offering_etag == offering_etag:
        raise AssertionError("offering ETag did not change after update")

    code, _, _ = request(
        "PATCH",
        f"/api/offerings/{OFFERING_ID}",
        payload=offering_patch,
        headers=offering_patch_headers,
    )
    expect("stale offering revision rejected", code, 412)

    code, _, _ = request("GET", "/api/catalog/filters")
    expect("public filters unchanged", code, 200)

    print("P3.2 Stage B trusted write smoke PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"P3.2 Stage B trusted write smoke FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
