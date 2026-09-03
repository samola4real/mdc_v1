from django.urls import path

from apps.api import views


urlpatterns = [
    path("health", views.health, name="v1-health"),
    path("catalog/filters", views.catalog_filters, name="v1-catalog-filters"),
    path(
        "service-discovery/search",
        views.service_discovery_search,
        name="v1-service-discovery-search",
    ),
]
