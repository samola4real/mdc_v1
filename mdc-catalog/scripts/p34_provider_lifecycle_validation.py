#!/usr/bin/env python3
"""P3.4 deployed trusted provider-lifecycle API validation.

This script intentionally validates the provider-facing lifecycle contract without
adding a frontend or Marketplace integration. It uses the deployed MDC API,
performs one controlled pilot registration/update flow, and prints concise
PASS/FAIL evidence.

The lifecycle bearer token is read only from
MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN and is never printed. Semantic catalogue
synchronization is intentionally not triggered here; P3.5 will use the P3.4
provider for the provider -> PostgreSQL -> Fuseki -> discovery end-to-end gate.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = os.getenv("MDC_P34_BASE_URL", "https://maasai-mdc-v1.vercel.app").rstrip("/")
TOKEN = os.getenv("MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN", "").strip()
ACTOR = "p34:provider-lifecycle-validation"
PROVIDER_ID = "p34_api_validation_provider"
INITIAL_OFFERING_ID = f"{PROVIDER_ID}_precision_metal_parts"
SECOND_OFFERING_ID = f"{PROVIDER_ID}_precision_gears"
CONCURRENCY_HEADER = "X-MDC-If-Match"
RUN_MARKER = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

PROVIDER_PAYLOAD = {
    "contract_version": "1.0",
    "provider_id": PROVIDER_ID,
    "provider_name": "P3.4 API Validation Provider",
    "country": "Finland",
    "certifications": [],
    "custom_provider_fields": {
        "pilot_scope": "p3.4_provider_lifecycle_api_validation",
    },
    "offerings": [
        {
            "service_category": "precision_metal_parts",
            "offering_name": "P3.4 precision metal parts",
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
    "offering_name": "P3.4 precision gears",
    "part_family": "gear",
    "support_status": "confirmed",
    "supported_part_types": [],
    "family_capabilities": {},
    "part_type_capabilities": {},
    "generic_capabilities": {},
}

PASSED = 0


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
            try:
                data = json.loads(raw.decode("utf-8")) if raw else None
            except Exception:
                data = None
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


def passed(label: str, detail: str = ""):
    global PASSED
    PASSED += 1
    suffix = f" — {detail}" if detail else ""
    print(f"PASS {label}{suffix}")


def expect_status(label: str, actual: int, expected: int):
    if actual != expected:
        raise AssertionError(f"{label}: expected HTTP {expected}, got {actual}")
    passed(label, str(actual))


def require_contract(data, label: str):
    if not isinstance(data, dict) or data.get("contract_version") != "1.0":
        raise AssertionError(f"{label}: contract_version is not 1.0")


def require_etag(headers: dict[str, str], label: str) -> str:
    etag = headers.get("ETag") or headers.get("Etag") or headers.get("etag")
    if not etag:
        raise AssertionError(f"{label}: missing ETag")
    passed(f"{label} returned ETag")
    return etag


def require_error_code(data, expected: str, label: str):
    if not isinstance(data, dict):
        raise AssertionError(f"{label}: missing JSON error response")
    error = data.get("error")
    code = error.get("code") if isinstance(error, dict) else None
    if code != expected:
        raise AssertionError(f"{label}: expected error code {expected!r}, got {code!r}")


def offering_ids(data) -> set[str]:
    if not isinstance(data, dict) or not isinstance(data.get("offerings"), list):
        raise AssertionError("provider offering list response is invalid")
    return {
        item.get("offering_id")
        for item in data["offerings"]
        if isinstance(item, dict) and isinstance(item.get("offering_id"), str)
    }


def main() -> int:
    if not TOKEN:
        raise RuntimeError("MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN is not set locally")

    print("P3.4 Provider Lifecycle API Validation")
    print(f"Target: {BASE_URL}")
    print(f"Controlled provider: {PROVIDER_ID}")
    print("Semantic synchronization: intentionally not executed in P3.4")

    trusted = {
        "Authorization": f"Bearer {TOKEN}",
        "X-MDC-Actor-Id": ACTOR,
    }
    auth_only = {"Authorization": f"Bearer {TOKEN}"}

    print("\n[1] Public API baseline")
    code, data, _ = request("GET", "/api/health")
    expect_status("GET /api/health", code, 200)
    require_contract(data, "health")
    passed("health contract_version", "1.0")

    code, data, _ = request("GET", "/api/catalog/filters")
    expect_status("GET /api/catalog/filters", code, 200)
    require_contract(data, "catalog filters")
    passed("catalog filters contract_version", "1.0")

    print("\n[2] Trusted boundary and validation")
    code, data, _ = request(
        "POST", "/api/provider-publication/validation", payload=PROVIDER_PAYLOAD
    )
    expect_status("anonymous validation rejected", code, 401)
    require_error_code(data, "trusted_lifecycle_auth_required", "anonymous validation")
    passed("anonymous validation error contract")

    code, data, _ = request(
        "POST",
        "/api/provider-publication/validation",
        payload={"contract_version": "1.0", "provider_id": "bad"},
        headers=trusted,
    )
    expect_status("invalid provider payload rejected", code, 400)
    if not isinstance(data, dict) or data.get("valid") is not False:
        raise AssertionError("invalid provider validation did not return valid=false")
    passed("invalid validation returned valid=false")

    code, data, _ = request(
        "POST",
        "/api/provider-publication/validation",
        payload=PROVIDER_PAYLOAD,
        headers=trusted,
    )
    expect_status("valid provider payload accepted", code, 200)
    require_contract(data, "provider validation")
    if not isinstance(data, dict) or data.get("valid") is not True:
        raise AssertionError("valid provider validation did not return valid=true")
    passed("valid validation returned valid=true")

    print("\n[3] Provider registration")
    code, data, _ = request(
        "POST", "/api/provider-publication", payload=PROVIDER_PAYLOAD, headers=auth_only
    )
    expect_status("write without actor rejected", code, 400)
    require_error_code(data, "actor_attribution_required", "missing actor write")
    passed("missing actor error contract")

    code, _, _ = request("GET", f"/api/providers/{PROVIDER_ID}")
    expect_status("anonymous provider read rejected", code, 401)

    code, data, _ = request(
        "POST", "/api/provider-publication", payload=PROVIDER_PAYLOAD, headers=trusted
    )
    if code == 201:
        require_contract(data, "provider registration")
        if data.get("provider_id") != PROVIDER_ID:
            raise AssertionError("provider registration returned unexpected provider_id")
        if data.get("publication_status") != "sync_pending":
            raise AssertionError("provider registration was not persisted as sync_pending")
        passed("authenticated provider registration", "201")
        passed("provider publication status", "sync_pending")
    elif code == 409:
        passed("authenticated provider registration", "existing controlled provider reused (409)")
    else:
        raise AssertionError(f"authenticated provider registration: expected 201/409, got {code}")

    code, data, _ = request(
        "POST", "/api/provider-publication", payload=PROVIDER_PAYLOAD, headers=trusted
    )
    expect_status("duplicate provider rejected", code, 409)
    require_error_code(data, "provider_already_exists", "duplicate provider")
    passed("duplicate provider error contract")

    print("\n[4] Provider read and optimistic concurrency")
    code, data, headers = request("GET", f"/api/providers/{PROVIDER_ID}", headers=trusted)
    expect_status("trusted provider read", code, 200)
    require_contract(data, "provider read")
    if data.get("provider_id") != PROVIDER_ID:
        raise AssertionError("provider read returned unexpected provider_id")
    provider_etag = require_etag(headers, "provider read")

    provider_patch = {
        "contract_version": "1.0",
        "custom_provider_fields": {
            "pilot_scope": "p3.4_provider_lifecycle_api_validation",
            "verified": True,
            "last_validation_run": RUN_MARKER,
        },
    }

    code, data, _ = request(
        "PATCH", f"/api/providers/{PROVIDER_ID}", payload=provider_patch, headers=trusted
    )
    expect_status("provider PATCH without concurrency precondition rejected", code, 428)
    require_error_code(data, "concurrency_precondition_required", "provider missing If-Match")
    passed("provider missing-precondition error contract")

    patch_headers = dict(trusted)
    patch_headers[CONCURRENCY_HEADER] = provider_etag
    code, data, headers = request(
        "PATCH",
        f"/api/providers/{PROVIDER_ID}",
        payload=provider_patch,
        headers=patch_headers,
    )
    expect_status("provider PATCH with current ETag", code, 200)
    require_contract(data, "provider update")
    if data.get("publication_status") != "sync_pending":
        raise AssertionError("provider update did not create sync_pending publication")
    new_provider_etag = require_etag(headers, "provider update")
    if new_provider_etag == provider_etag:
        raise AssertionError("provider ETag did not change after update")
    passed("provider ETag changed after update")
    passed("provider update publication status", "sync_pending")

    code, data, _ = request(
        "PATCH",
        f"/api/providers/{PROVIDER_ID}",
        payload=provider_patch,
        headers=patch_headers,
    )
    expect_status("stale provider ETag rejected", code, 412)
    require_error_code(data, "provider_precondition_failed", "stale provider ETag")
    passed("stale provider ETag error contract")

    print("\n[5] Offering lifecycle")
    code, data, _ = request(
        "GET", f"/api/providers/{PROVIDER_ID}/offerings", headers=trusted
    )
    expect_status("provider offering list", code, 200)
    require_contract(data, "provider offering list")
    if INITIAL_OFFERING_ID not in offering_ids(data):
        raise AssertionError(f"initial offering {INITIAL_OFFERING_ID} is missing")
    passed("initial provider offering present", INITIAL_OFFERING_ID)

    code, data, _ = request(
        "POST",
        f"/api/providers/{PROVIDER_ID}/offerings",
        payload=SECOND_OFFERING_PAYLOAD,
        headers=trusted,
    )
    if code == 201:
        require_contract(data, "offering creation")
        if data.get("offering_id") != SECOND_OFFERING_ID:
            raise AssertionError("offering creation returned unexpected offering_id")
        if data.get("publication_status") != "sync_pending":
            raise AssertionError("offering creation did not create sync_pending publication")
        passed("authenticated offering creation", "201")
        passed("offering creation publication status", "sync_pending")
    elif code == 409:
        passed("authenticated offering creation", "existing controlled offering reused (409)")
    else:
        raise AssertionError(f"authenticated offering creation: expected 201/409, got {code}")

    code, data, _ = request(
        "POST",
        f"/api/providers/{PROVIDER_ID}/offerings",
        payload=SECOND_OFFERING_PAYLOAD,
        headers=trusted,
    )
    expect_status("duplicate offering rejected", code, 409)
    require_error_code(data, "offering_already_exists", "duplicate offering")
    passed("duplicate offering error contract")

    code, data, headers = request("GET", f"/api/offerings/{SECOND_OFFERING_ID}", headers=trusted)
    expect_status("trusted offering read", code, 200)
    require_contract(data, "offering read")
    if data.get("offering_id") != SECOND_OFFERING_ID:
        raise AssertionError("offering read returned unexpected offering_id")
    offering_etag = require_etag(headers, "offering read")

    offering_patch = {
        "contract_version": "1.0",
        "offering_name": f"P3.4 precision gears validated {RUN_MARKER}",
    }

    code, data, _ = request(
        "PATCH", f"/api/offerings/{SECOND_OFFERING_ID}", payload=offering_patch, headers=trusted
    )
    expect_status("offering PATCH without concurrency precondition rejected", code, 428)
    require_error_code(data, "concurrency_precondition_required", "offering missing If-Match")
    passed("offering missing-precondition error contract")

    offering_patch_headers = dict(trusted)
    offering_patch_headers[CONCURRENCY_HEADER] = offering_etag
    code, data, headers = request(
        "PATCH",
        f"/api/offerings/{SECOND_OFFERING_ID}",
        payload=offering_patch,
        headers=offering_patch_headers,
    )
    expect_status("offering PATCH with current ETag", code, 200)
    require_contract(data, "offering update")
    if data.get("publication_status") != "sync_pending":
        raise AssertionError("offering update did not create sync_pending publication")
    new_offering_etag = require_etag(headers, "offering update")
    if new_offering_etag == offering_etag:
        raise AssertionError("offering ETag did not change after update")
    passed("offering ETag changed after update")
    passed("offering update publication status", "sync_pending")

    code, data, _ = request(
        "PATCH",
        f"/api/offerings/{SECOND_OFFERING_ID}",
        payload=offering_patch,
        headers=offering_patch_headers,
    )
    expect_status("stale offering ETag rejected", code, 412)
    require_error_code(data, "offering_precondition_failed", "stale offering ETag")
    passed("stale offering ETag error contract")

    code, data, _ = request(
        "GET", f"/api/providers/{PROVIDER_ID}/offerings", headers=trusted
    )
    expect_status("final provider offering list", code, 200)
    ids = offering_ids(data)
    missing = {INITIAL_OFFERING_ID, SECOND_OFFERING_ID} - ids
    if missing:
        raise AssertionError(f"final offering list is missing: {sorted(missing)}")
    passed("final offering list contains both controlled offerings")

    print("\n[6] P3.4 result")
    print(f"tests_passed={PASSED}")
    print("tests_failed=0")
    print("P3.4 PROVIDER LIFECYCLE API VALIDATION: PASS")
    print("NOTE: sync_pending records are intentionally left for P3.5 end-to-end synchronization/discovery.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"P3.4 PROVIDER LIFECYCLE API VALIDATION: FAIL — {exc}", file=sys.stderr)
        raise SystemExit(1)
