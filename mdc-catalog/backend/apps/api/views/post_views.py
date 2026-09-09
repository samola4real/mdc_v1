from copy import deepcopy

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.api.lifecycle_security import (
    attach_etag,
    authenticate_lifecycle_request,
    get_if_match_or_error,
)
from apps.api.public_contract import (
    PUBLIC_CONTRACT_VERSION,
    build_public_error,
    build_public_service_discovery_response,
    validate_contract_version,
)
from apps.api.service_discovery_publication_serializers import (
    ServiceDiscoveryPublicationSerializer,
    validate_lifecycle_offering,
)
from apps.api.provider_lifecycle_serializers import (
    OfferingCreateSerializer,
    OfferingPatchSerializer,
    ProviderPatchSerializer,
)
from apps.providers.provider_lifecycle_write_service import (
    LifecycleConflict,
    LifecycleNotFound,
    LifecyclePreconditionFailed,
    LifecycleWriteError,
    add_provider_offering,
    register_provider,
    update_offering,
    update_provider,
)
from apps.providers.service_discovery_publication import (
    normalize_service_discovery_publication,
)
from apps.api.service_discovery_search_serializers import (
    ServiceDiscoverySearchRequestSerializer,
)
from apps.search.service_discovery_normalizer import (
    normalize_service_discovery_search_request,
)
from apps.search.service_discovery_runtime_search import (
    ServiceDiscoveryRuntimeSearchError,
    search_service_discovery_with_runtime_backends,
)


def make_json_safe(value):
    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    return str(value)


def _write_disabled():
    return Response(
        build_public_error(
            code="provider_publication_disabled",
            message="Provider lifecycle writes are disabled for this environment.",
        ),
        status=status.HTTP_403_FORBIDDEN,
    )


def _contract_payload(request):
    payload = deepcopy(request.data)
    requested_contract_version = payload.pop("contract_version", None)
    validate_contract_version(requested_contract_version)
    return payload


def _invalid(code, message, details):
    return Response(
        build_public_error(
            code=code,
            message=message,
            details=make_json_safe(details),
        ),
        status=status.HTTP_400_BAD_REQUEST,
    )


def _write_exception_response(exc):
    if isinstance(exc, LifecycleNotFound):
        return Response(
            build_public_error(
                code=f"{exc.entity}_not_found",
                message=f"The requested {exc.entity} was not found.",
            ),
            status=status.HTTP_404_NOT_FOUND,
        )
    if isinstance(exc, LifecyclePreconditionFailed):
        return Response(
            build_public_error(
                code=f"{exc.entity}_precondition_failed",
                message=(
                    f"The requested {exc.entity} changed after it was retrieved; "
                    "fetch the current representation and retry."
                ),
            ),
            status=status.HTTP_412_PRECONDITION_FAILED,
        )
    if isinstance(exc, LifecycleConflict):
        messages = {
            "provider_already_exists": "The provider is already registered.",
            "offering_already_exists": "The offering is already registered.",
        }
        return Response(
            build_public_error(code=exc.code, message=messages[exc.code]),
            status=status.HTTP_409_CONFLICT,
        )
    return Response(
        build_public_error(
            code="provider_lifecycle_write_unavailable",
            message="The provider lifecycle write could not be completed.",
        ),
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


def _parse_contract_or_response(request):
    try:
        return _contract_payload(request), None
    except ValueError as exc:
        return None, Response(
            build_public_error(code="unsupported_contract_version", message=str(exc)),
            status=status.HTTP_400_BAD_REQUEST,
        )


def _trusted_context_or_response(request, *, write=False):
    return authenticate_lifecycle_request(request, write=write)


def _write_response(result, http_status):
    result = dict(result)
    etag = result.pop("_etag", None)
    return attach_etag(Response(result, status=http_status), etag)


@api_view(["POST"])
def provider_publication(request):
    security, security_error = _trusted_context_or_response(request, write=True)
    if security_error is not None:
        return security_error
    if not getattr(settings, "MDC_PROVIDER_PUBLICATION_ENABLED", False):
        return _write_disabled()
    payload, error_response = _parse_contract_or_response(request)
    if error_response is not None:
        return error_response
    serializer = ServiceDiscoveryPublicationSerializer(data=payload)
    try:
        is_valid = serializer.is_valid()
        validation_errors = getattr(serializer, "_errors", None)
    except ValidationError as exc:
        is_valid = False
        validation_errors = exc.detail
    if not is_valid:
        return _invalid(
            "invalid_provider_publication",
            "The provider publication payload is invalid.",
            validation_errors,
        )
    try:
        result = register_provider(
            serializer.validated_data,
            payload,
            actor_id=security.actor_id,
        )
    except (LifecycleConflict, LifecycleNotFound, LifecyclePreconditionFailed, LifecycleWriteError) as exc:
        return _write_exception_response(exc)
    return _write_response(result, status.HTTP_201_CREATED)


def provider_update(request, provider_id):
    security, security_error = _trusted_context_or_response(request, write=True)
    if security_error is not None:
        return security_error
    if not getattr(settings, "MDC_PROVIDER_PUBLICATION_ENABLED", False):
        return _write_disabled()
    expected_etag, precondition_error = get_if_match_or_error(request)
    if precondition_error is not None:
        return precondition_error
    payload, error_response = _parse_contract_or_response(request)
    if error_response is not None:
        return error_response
    serializer = ProviderPatchSerializer(data=payload)
    try:
        serializer.is_valid(raise_exception=True)
    except ValidationError as exc:
        return _invalid("invalid_provider_update", "The provider update is invalid.", exc.detail)
    try:
        result = update_provider(
            provider_id,
            serializer.validated_data,
            payload,
            actor_id=security.actor_id,
            expected_etag=expected_etag,
        )
    except (LifecycleConflict, LifecycleNotFound, LifecyclePreconditionFailed, LifecycleWriteError) as exc:
        return _write_exception_response(exc)
    return _write_response(result, status.HTTP_200_OK)


def provider_offering_create(request, provider_id):
    security, security_error = _trusted_context_or_response(request, write=True)
    if security_error is not None:
        return security_error
    if not getattr(settings, "MDC_PROVIDER_PUBLICATION_ENABLED", False):
        return _write_disabled()
    payload, error_response = _parse_contract_or_response(request)
    if error_response is not None:
        return error_response
    serializer = OfferingCreateSerializer(data=payload)
    try:
        serializer.is_valid(raise_exception=True)
        offering = validate_lifecycle_offering(serializer.validated_data)
    except ValidationError as exc:
        return _invalid("invalid_offering", "The offering payload is invalid.", exc.detail)
    try:
        result = add_provider_offering(
            provider_id,
            offering,
            payload,
            actor_id=security.actor_id,
        )
    except (LifecycleConflict, LifecycleNotFound, LifecyclePreconditionFailed, LifecycleWriteError) as exc:
        return _write_exception_response(exc)
    return _write_response(result, status.HTTP_201_CREATED)


def offering_update(request, offering_id):
    security, security_error = _trusted_context_or_response(request, write=True)
    if security_error is not None:
        return security_error
    if not getattr(settings, "MDC_PROVIDER_PUBLICATION_ENABLED", False):
        return _write_disabled()
    expected_etag, precondition_error = get_if_match_or_error(request)
    if precondition_error is not None:
        return precondition_error
    payload, error_response = _parse_contract_or_response(request)
    if error_response is not None:
        return error_response
    serializer = OfferingPatchSerializer(data=payload)
    try:
        serializer.is_valid(raise_exception=True)
        result = update_offering(
            offering_id,
            serializer.validated_data,
            payload,
            actor_id=security.actor_id,
            expected_etag=expected_etag,
        )
    except ValidationError as exc:
        return _invalid("invalid_offering_update", "The offering update is invalid.", exc.detail)
    except (LifecycleConflict, LifecycleNotFound, LifecyclePreconditionFailed, LifecycleWriteError) as exc:
        return _write_exception_response(exc)
    return _write_response(result, status.HTTP_200_OK)


@api_view(["POST"])
def provider_publication_validation(request):
    """Validate and normalize a provider payload without mutating any state."""
    _security, security_error = _trusted_context_or_response(request, write=False)
    if security_error is not None:
        return security_error
    if not getattr(settings, "MDC_PROVIDER_VALIDATION_ENABLED", False):
        return Response(
            build_public_error(
                code="provider_validation_disabled",
                message="Provider validation is disabled for this environment.",
            ),
            status=status.HTTP_403_FORBIDDEN,
        )

    payload = deepcopy(request.data)
    requested_contract_version = payload.pop("contract_version", None)
    try:
        validate_contract_version(requested_contract_version)
    except ValueError as exc:
        return Response(
            build_public_error(
                code="unsupported_contract_version",
                message=str(exc),
            ),
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = ServiceDiscoveryPublicationSerializer(data=payload)
    try:
        is_valid = serializer.is_valid()
        validation_errors = getattr(serializer, "_errors", None)
    except ValidationError as exc:
        is_valid = False
        validation_errors = exc.detail

    if not is_valid:
        return Response(
            {
                "contract_version": PUBLIC_CONTRACT_VERSION,
                "valid": False,
                "message": "The provider publication payload is invalid.",
                "warnings": [],
                "error": {
                    "code": "invalid_provider_publication",
                    "details": make_json_safe(validation_errors),
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "contract_version": PUBLIC_CONTRACT_VERSION,
            "valid": True,
            "message": "The provider publication payload is valid.",
            "warnings": [],
            "normalized_payload": normalize_service_discovery_publication(
                serializer.validated_data
            ),
        }
    )


@api_view(["POST"])
def service_discovery_search(request):
    payload = request.data.copy()
    requested_contract_version = payload.pop("contract_version", None)

    try:
        validate_contract_version(requested_contract_version)
    except ValueError as exc:
        return Response(
            build_public_error(
                code="unsupported_contract_version",
                message=str(exc),
            ),
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = ServiceDiscoverySearchRequestSerializer(data=payload)

    try:
        is_valid = serializer.is_valid()
        validation_errors = getattr(serializer, "_errors", None)
    except ValidationError as exc:
        is_valid = False
        validation_errors = exc.detail

    if not is_valid:
        return Response(
            build_public_error(
                code="invalid_service_discovery_request",
                message="Invalid service-discovery search request.",
                details=make_json_safe(validation_errors),
            ),
            status=status.HTTP_400_BAD_REQUEST,
        )

    canonical_request = normalize_service_discovery_search_request(
        serializer.validated_data
    )

    try:
        internal_response = search_service_discovery_with_runtime_backends(
            canonical_request
        )
    except ServiceDiscoveryRuntimeSearchError:
        return Response(
            build_public_error(
                code="service_discovery_search_unavailable",
                message="Service-discovery search is temporarily unavailable.",
            ),
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response(
        build_public_service_discovery_response(
            internal_response,
            canonical_request=canonical_request,
        ),
        status=status.HTTP_200_OK,
    )
