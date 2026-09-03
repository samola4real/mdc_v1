from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.demo.provider_demo_services import read_provider_demo_state
from apps.demo.services import demo_api_required


@api_view(["GET"])
@demo_api_required
def health(request):
    return Response(
        {
            "status": "ok",
            "app": "mdc_demo",
            "demo_api_enabled": True,
            "message": (
                "MDC demo API is enabled. These endpoints are temporary "
                "and not part of the Marketplace API contract."
            ),
        }
    )


@api_view(["GET"])
@demo_api_required
def service_discovery_backend_status(request):
    return Response(
        {
            "demo_api_enabled": True,
            "active_backend": "fuseki_with_h5_policy",
            "fallback_backends": [
                "local_rdflib_with_h5_policy",
                "harmonized_yaml_h5_matcher",
            ],
            "fuseki_dataset": "mdc-service-discovery",
            "marketplace_shared_api_unchanged": True,
            "endpoint_activation_status": "demo_only_not_marketplace_contract",
        }
    )


@api_view(["GET"])
@demo_api_required
def service_discovery_fuseki_smoke_test(request):
    return Response(
        {
            "status": "not_implemented",
            "message": (
                "Fuseki smoke-test execution will be implemented in a later "
                "demo phase."
            ),
            "mutates_state": False,
        }
    )


@api_view(["GET"])
@demo_api_required
def provider_publication_state(request):
    try:
        return Response(read_provider_demo_state())
    except Exception:
        return Response(
            {
                "status": "demo_provider_state_unavailable",
                "message": "Demo provider state could not be loaded.",
                "providers": {},
                "updates": {},
                "last_updated": None,
            },
            status=500,
        )
