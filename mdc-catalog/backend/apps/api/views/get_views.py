from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.api.public_contract import (
    PUBLIC_CONTRACT_VERSION,
    build_public_error,
    build_public_catalog_filters,
    build_public_health_response,
)
from apps.providers.provider_lifecycle_repository import (
    get_offering_lifecycle,
    get_provider_lifecycle,
    list_provider_lifecycle_offerings,
)


@api_view(["GET"])
def health(request):
    return Response(build_public_health_response())


@api_view(["GET"])
def catalog_filters(request):
    return Response(build_public_catalog_filters())


def _not_found(entity):
    return Response(
        build_public_error(
            code=f"{entity}_not_found",
            message=f"The requested {entity} was not found.",
        ),
        status=status.HTTP_404_NOT_FOUND,
    )


@api_view(["GET"])
def provider_detail(request, provider_id):
    provider = get_provider_lifecycle(provider_id)
    if provider is None:
        return _not_found("provider")
    return Response({"contract_version": PUBLIC_CONTRACT_VERSION, **provider})


@api_view(["GET"])
def provider_offerings(request, provider_id):
    offerings = list_provider_lifecycle_offerings(provider_id)
    if offerings is None:
        return _not_found("provider")
    return Response(
        {
            "contract_version": PUBLIC_CONTRACT_VERSION,
            "provider_id": provider_id,
            "offerings": offerings,
        }
    )


@api_view(["GET"])
def offering_detail(request, offering_id):
    offering = get_offering_lifecycle(offering_id)
    if offering is None:
        return _not_found("offering")
    return Response({"contract_version": PUBLIC_CONTRACT_VERSION, **offering})
