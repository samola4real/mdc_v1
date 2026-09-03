from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

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
def service_discovery_search(request):
    serializer = ServiceDiscoverySearchRequestSerializer(data=request.data)

    try:
        is_valid = serializer.is_valid()
        validation_errors = getattr(serializer, "_errors", None)
    except ValidationError as exc:
        is_valid = False
        validation_errors = exc.detail

    if not is_valid:
        return Response(
            {
                "status": {
                    "search_executed": False,
                    "search_engine": "not_executed",
                    "message": "Invalid service-discovery search request.",
                },
                "errors": make_json_safe(validation_errors),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    canonical_request = normalize_service_discovery_search_request(
        serializer.validated_data
    )

    try:
        response = search_service_discovery_with_runtime_backends(canonical_request)
    except ServiceDiscoveryRuntimeSearchError as exc:
        return Response(
            {
                "error": {
                    "code": "service_discovery_search_unavailable",
                    "message": "Service-discovery search is temporarily unavailable.",
                    "details": str(exc),
                }
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response(response, status=status.HTTP_200_OK)
