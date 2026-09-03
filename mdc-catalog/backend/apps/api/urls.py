
from django.urls import path

from apps.api import views

# Create your tests here.


urlpatterns = [
    path("health", views.health, name="health"),
    path("catalog/filters", views.catalog_filters, name="catalog-filters"),
    path("catalog/search", views.catalog_search, name="catalog-search"),
    path(
        "service-discovery/search",
        views.service_discovery_search,
        name="service-discovery-search",
    ),
    
    
    path(
        "provider-publication",
        views.provider_publication,
        name="provider-publication",
    ),
    path(
        "providers/<str:provider_id>",
        views.provider_detail,
        name="provider-detail",
    ),
    path(
        "offerings/<str:offering_id>",
        views.offering_detail,
        name="offering-detail",
    ),

    
]
