from copy import deepcopy

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.api.public_contract import (
    PUBLIC_CONTRACT_VERSION,
    build_public_error,
    build_public_service_discovery_response,
    validate_contract_version,
)
from apps.api.service_discovery_publication_serializers import (
    ServiceDiscoveryPublicationSerializer,
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


@api_view(["POST"])
def provider_publication_validation(request):
    """Validate and normalize a provider payload without mutating any state."""
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
