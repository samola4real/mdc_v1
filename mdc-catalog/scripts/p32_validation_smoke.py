#!/usr/bin/env python3
"""P3.2 Stage A trusted validation smoke.

Uses only Python stdlib. The bearer token is read from
MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN and is never printed.
"""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = os.getenv("MDC_P32_BASE_URL", "https://maasai-mdc-v1.vercel.app").rstrip("/")
TOKEN = os.getenv("MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN", "").strip()
ACTOR = "p32:validation-smoke"

VALID_PAYLOAD = {
    "contract_version": "1.0",
    "provider_id": "p32_validation_probe",
    "provider_name": "P3.2 Validation Probe",
    "country": "Finland",
    "offerings": [
        {
            "service_category": "precision_metal_parts",
            "offering_name": "Precision metal parts",
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
            "part_type_capabilities": {
                "bracket": {
                    "bounding_box_mm": {
                        "length_mm": {"max": 160},
                        "width_mm": {"max": 80},
                        "height_mm": {"max": 70},
                        "source_type": "provider_confirmed",
                        "confidence": "declared",
                    }
                }
            },
        }
    ],
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
            data = json.loads(raw.decode("utf-8")) if raw else None
        except Exception:
            data = None
        return exc.code, data
    except URLError as exc:
        raise RuntimeError("deployment endpoint unavailable") from exc


def expect(label: str, actual: int, expected: int):
    if actual != expected:
        raise AssertionError(f"{label}: expected HTTP {expected}, got {actual}")
    print(f"PASS {label}: {actual}")


def main() -> int:
    if not TOKEN:
        raise RuntimeError("MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN is not set locally")

    print(f"P3.2 Stage A target: {BASE_URL}")

    code, data = request("GET", "/api/health")
    expect("public health unchanged", code, 200)
    if not isinstance(data, dict) or data.get("contract_version") != "1.0":
        raise AssertionError("health contract_version is not 1.0")

    code, _ = request("POST", "/api/provider-publication/validation", payload=VALID_PAYLOAD)
    expect("anonymous validation rejected", code, 401)

    trusted = {
        "Authorization": f"Bearer {TOKEN}",
        "X-MDC-Actor-Id": ACTOR,
    }

    code, data = request(
        "POST",
        "/api/provider-publication/validation",
        payload=VALID_PAYLOAD,
        headers=trusted,
    )
    expect("authenticated valid validation", code, 200)
    if not isinstance(data, dict) or data.get("valid") is not True:
        raise AssertionError("valid validation did not return valid=true")
    if data.get("contract_version") != "1.0":
        raise AssertionError("validation contract_version is not 1.0")

    code, data = request(
        "POST",
        "/api/provider-publication/validation",
        payload={"contract_version": "1.0", "provider_id": "bad"},
        headers=trusted,
    )
    expect("authenticated invalid validation", code, 400)
    if not isinstance(data, dict) or data.get("valid") is not False:
        raise AssertionError("invalid validation did not return valid=false")

    code, _ = request(
        "POST",
        "/api/provider-publication",
        payload=VALID_PAYLOAD,
        headers=trusted,
    )
    expect("provider writes still disabled", code, 403)

    code, data = request("GET", "/api/providers/tasowheel", headers=trusted)
    expect("trusted DB read still works", code, 200)
    if not isinstance(data, dict) or data.get("provider_id") != "tasowheel":
        raise AssertionError("trusted provider read did not return tasowheel")

    print("P3.2 Stage A validation smoke PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"P3.2 Stage A validation smoke FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
