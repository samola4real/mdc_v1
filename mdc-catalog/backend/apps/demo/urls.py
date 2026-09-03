from django.urls import path

from apps.demo.views import get_views, post_views


urlpatterns = [
    path("health", get_views.health, name="demo-health"),
    path(
        "service-discovery/backend-status",
        get_views.service_discovery_backend_status,
        name="demo-service-discovery-backend-status",
    ),
    path(
        "service-discovery/fuseki-smoke-test",
        get_views.service_discovery_fuseki_smoke_test,
        name="demo-service-discovery-fuseki-smoke-test",
    ),
    path(
        "service-discovery/regenerate-rdf",
        post_views.service_discovery_regenerate_rdf,
        name="demo-service-discovery-regenerate-rdf",
    ),
    path(
        "service-discovery/reload-fuseki",
        post_views.service_discovery_reload_fuseki,
        name="demo-service-discovery-reload-fuseki",
    ),
    path(
        "provider-publication/preview",
        post_views.provider_publication_preview,
        name="demo-provider-publication-preview",
    ),
    path(
        "provider-publication/state",
        get_views.provider_publication_state,
        name="demo-provider-publication-state",
    ),
    path(
        "provider-publication/simulate-update",
        post_views.provider_publication_simulate_update,
        name="demo-provider-publication-simulate-update",
    ),
]
