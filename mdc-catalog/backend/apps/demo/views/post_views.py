from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.demo.provider_demo_services import (
    preview_provider_demo_payload,
    simulate_provider_demo_update,
)
from apps.demo.services import demo_api_required


def _not_implemented_response(message):
    return Response(
        {
            "status": "not_implemented",
            "message": message,
            "mutates_state": False,
        },
        status=status.HTTP_501_NOT_IMPLEMENTED,
    )


@api_view(["POST"])
@demo_api_required
def service_discovery_regenerate_rdf(request):
    return _not_implemented_response(
        "This demo RDF regeneration action is reserved for a later controlled "
        "demo phase."
    )


@api_view(["POST"])
@demo_api_required
def service_discovery_reload_fuseki(request):
    return _not_implemented_response(
        "This demo Fuseki reload action is reserved for a later controlled "
        "demo phase."
    )


@api_view(["POST"])
@demo_api_required
def provider_publication_preview(request):
    try:
        return Response(preview_provider_demo_payload(request.data), status=status.HTTP_200_OK)
    except Exception as exc:
        return Response(
            {
                "status": "invalid_demo_provider_payload",
                "message": "Provider demo preview payload was rejected.",
                "errors": [str(exc)],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@demo_api_required
def provider_publication_simulate_update(request):
    try:
        return Response(simulate_provider_demo_update(request.data), status=status.HTTP_200_OK)
    except Exception as exc:
        return Response(
            {
                "status": "invalid_demo_provider_payload",
                "message": "Provider demo update payload was rejected.",
                "errors": [str(exc)],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
