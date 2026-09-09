"""Trusted service boundary and HTTP concurrency helpers for provider lifecycle APIs."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from hmac import compare_digest

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from apps.api.public_contract import build_public_error


ACTOR_HEADER = "X-MDC-Actor-Id"
AUTHORIZATION_HEADER = "Authorization"
MAX_ACTOR_LENGTH = 255
MAX_IF_MATCH_LENGTH = 160


@dataclass(frozen=True)
class LifecycleSecurityContext:
    actor_id: str | None


def _error(code: str, message: str, http_status: int, *, authenticate: bool = False):
    response = Response(
        build_public_error(code=code, message=message),
        status=http_status,
    )
    if authenticate:
        response["WWW-Authenticate"] = "Bearer"
    return response


def _validated_actor_id(request) -> tuple[str | None, Response | None]:
    raw = request.headers.get(ACTOR_HEADER, "")
    actor_id = raw.strip()
    if not actor_id:
        return None, None
    if len(actor_id) > MAX_ACTOR_LENGTH or any(ord(character) < 32 for character in actor_id):
        return None, _error(
            "invalid_actor_attribution",
            "The lifecycle actor identifier is invalid.",
            status.HTTP_400_BAD_REQUEST,
        )
    return actor_id, None


def authenticate_lifecycle_request(request, *, write: bool = False):
    """Return a trusted context or a safe response.

    This intentionally implements only a small replaceable pilot service-token
    boundary. A future Marketplace OAuth/JWT/API-gateway identity can replace
    this helper without changing provider persistence or publication semantics.
    """
    actor_id, actor_error = _validated_actor_id(request)
    if actor_error is not None:
        return None, actor_error

    auth_required = bool(
        getattr(settings, "MDC_PROVIDER_LIFECYCLE_AUTH_REQUIRED", False)
    )
    if auth_required:
        configured_token = (
            getattr(settings, "MDC_PROVIDER_LIFECYCLE_SERVICE_TOKEN", "") or ""
        ).strip()
        if not configured_token:
            return None, _error(
                "trusted_lifecycle_auth_unavailable",
                "Trusted provider lifecycle authentication is unavailable.",
                status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        authorization = request.headers.get(AUTHORIZATION_HEADER, "")
        scheme, separator, supplied_token = authorization.partition(" ")
        valid = (
            bool(separator)
            and scheme == "Bearer"
            and bool(supplied_token)
            and compare_digest(supplied_token, configured_token)
        )
        if not valid:
            return None, _error(
                "trusted_lifecycle_auth_required",
                "Trusted provider lifecycle authentication is required.",
                status.HTTP_401_UNAUTHORIZED,
                authenticate=True,
            )

    if write and getattr(settings, "MDC_PROVIDER_LIFECYCLE_ACTOR_REQUIRED", False):
        if not actor_id:
            return None, _error(
                "actor_attribution_required",
                "A lifecycle actor identifier is required for this write.",
                status.HTTP_400_BAD_REQUEST,
            )

    return LifecycleSecurityContext(actor_id=actor_id), None


def build_entity_etag(entity_type: str, external_id: str, updated_at) -> str:
    """Build a strong opaque ETag without exposing internal timestamps."""
    timestamp = updated_at.isoformat() if updated_at is not None else ""
    digest = sha256(
        f"{entity_type}:{external_id}:{timestamp}".encode("utf-8")
    ).hexdigest()
    return f'"{digest}"'


def get_if_match_or_error(request):
    """Resolve If-Match according to the configured optimistic-concurrency mode."""
    value = request.headers.get("If-Match")
    if value is None or not value.strip():
        if getattr(settings, "MDC_PROVIDER_CONCURRENCY_REQUIRED", False):
            return None, _error(
                "concurrency_precondition_required",
                "If-Match is required for this lifecycle update.",
                428,
            )
        return None, None

    value = value.strip()
    if len(value) > MAX_IF_MATCH_LENGTH or not (
        value.startswith('"') and value.endswith('"')
    ):
        return None, _error(
            "invalid_concurrency_precondition",
            "If-Match must contain a valid strong lifecycle ETag.",
            status.HTTP_400_BAD_REQUEST,
        )
    return value, None


def attach_etag(response: Response, etag: str | None) -> Response:
    if etag:
        response["ETag"] = etag
    return response
