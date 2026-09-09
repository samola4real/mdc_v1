from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.api.lifecycle_security import (
    attach_etag,
    authenticate_lifecycle_request,
)
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


def _trusted_read_or_response(request):
    _context, error_response = authenticate_lifecycle_request(request, write=False)
    return error_response


@api_view(["GET", "PATCH"])
def provider_detail(request, provider_id):
    if request.method == "PATCH":
        from apps.api.views.post_views import provider_update
        return provider_update(request, provider_id)

    error_response = _trusted_read_or_response(request)
    if error_response is not None:
        return error_response

    provider = get_provider_lifecycle(provider_id)
    if provider is None:
        return _not_found("provider")
    etag = provider.pop("_etag", None)
    return attach_etag(
        Response({"contract_version": PUBLIC_CONTRACT_VERSION, **provider}),
        etag,
    )


@api_view(["GET", "POST"])
def provider_offerings(request, provider_id):
    if request.method == "POST":
        from apps.api.views.post_views import provider_offering_create
        return provider_offering_create(request, provider_id)

    error_response = _trusted_read_or_response(request)
    if error_response is not None:
        return error_response

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


@api_view(["GET", "PATCH"])
def offering_detail(request, offering_id):
    if request.method == "PATCH":
        from apps.api.views.post_views import offering_update
        return offering_update(request, offering_id)

    error_response = _trusted_read_or_response(request)
    if error_response is not None:
        return error_response

    offering = get_offering_lifecycle(offering_id)
    if offering is None:
        return _not_found("offering")
    etag = offering.pop("_etag", None)
    return attach_etag(
        Response({"contract_version": PUBLIC_CONTRACT_VERSION, **offering}),
        etag,
    )
