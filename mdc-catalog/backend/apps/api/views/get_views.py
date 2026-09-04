from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.api.public_contract import (
    build_public_catalog_filters,
    build_public_health_response,
)


@api_view(["GET"])
def health(request):
    return Response(build_public_health_response())


@api_view(["GET"])
def catalog_filters(request):
    return Response(build_public_catalog_filters())
