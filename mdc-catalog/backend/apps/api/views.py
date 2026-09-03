
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from apps.api.provider_publication_serializers import ProviderPublicationSerializer
from apps.api.search_serializers import SearchRequestSerializer
from apps.search.normalizer import normalize_search_request

from apps.ontology.vocabularies import get_catalog_filters
from apps.search.local_matcher import find_offerings_matching_primary_filters

from apps.providers.exceptions import SeedDataError
from apps.providers.normalizers import normalize_provider_publication
from apps.providers.providers_utils import get_provider_seed_file_path
from apps.providers.repositories import (
    ProviderRepositoryError,
    save_provider_seed_data,
)

from apps.providers.services import (
    OfferingNotFoundError,
    ProviderNotFoundError,
    get_offering_by_id,
    get_offerings_for_provider,
    get_provider_by_id,
)

from .response_utils import (get_offerings_for_provider,
                             build_provider_response,
                             build_offering_response
)




#! Create your views here.

@api_view(["GET"])
def health(request):
    return Response(
        {
            "status": "ok",
            "service": "maasai-mdc",
            "version": "v1",
        }
    )


@api_view(["GET"])
def catalog_filters(request):
    return Response(get_catalog_filters())


@api_view(["GET"])
def provider_detail(request, provider_id: str):
    """
    Return one provider and its offering summaries.
    """
    try:
        provider = get_provider_by_id(provider_id)
    except ProviderNotFoundError:
        return Response(
            {
                "error": {
                    "code": "not_found",
                    "message": f"Provider not found: {provider_id}",
                }
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(build_provider_response(provider))


@api_view(["GET"])
def offering_detail(request, offering_id: str):
    """
    Return one provider offering with searchable capability data.
    """
    try:
        offering = get_offering_by_id(offering_id)
    except OfferingNotFoundError:
        return Response(
            {
                "error": {
                    "code": "not_found",
                    "message": f"Offering not found: {offering_id}",
                }
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(build_offering_response(offering))











# ? POST

@api_view(["POST"])
def provider_publication(request):
    """
    Accept a provider-publication payload, validate it, normalize it,
    and save it as a provider seed YAML file.

    Current Basic MDC behavior:
    - file-backed storage
    - one provider publication per request
    - no RDF generation yet
    - no Fuseki update yet
    """
    serializer = ProviderPublicationSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                "error": {
                    "code": "invalid_provider_publication",
                    "message": "The provider publication payload is invalid.",
                    "details": serializer.errors,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        provider_id = serializer.validated_data["provider"]["provider_id"]
        target_path = get_provider_seed_file_path(provider_id)
        existed_before_save = target_path.exists()

        normalized_seed_data = normalize_provider_publication(
            serializer.validated_data
        )

        saved_path = save_provider_seed_data(normalized_seed_data)

    except (SeedDataError, ProviderRepositoryError, ValueError) as exc:
        return Response(
            {
                "error": {
                    "code": "provider_publication_failed",
                    "message": "The provider publication could not be saved.",
                    "details": str(exc),
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    created_or_updated = "updated" if existed_before_save else "created"

    return Response(
        {
            "status": "accepted",
            "provider_id": provider_id,
            "created_or_updated": created_or_updated,
            # "saved_path": str(saved_path),
            "storage": {
                "type": "file_backed_seed_repository",
                "file_name": saved_path.name,
            },
            "offerings": [
                {
                    "offering_id": offering["offering_id"],
                    "service_type": offering["service_type"],
                }
                for offering in normalized_seed_data["offerings"]
            ],
            "next_steps": {
                "rdf_generation_required": True,
                "rdf_generation_done": False,
            },
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def catalog_search(request):
    """
    Consumer catalogue search endpoint.

    Current F1.2 behavior:
    - validate marketplace search payload
    - normalize it into CanonicalSearchRequest
    - run local primary part-family matching
    - return provider/offering results

    Current limitation:
    - only primary part-family matching is implemented
    - optional criteria are interpreted but not matched yet
    - no RDF/SPARQL yet
    """
    serializer = SearchRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                "error": {
                    "code": "invalid_search_request",
                    "message": "The search request payload is invalid.",
                    "details": serializer.errors,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    canonical_request = normalize_search_request(
        serializer.validated_data,
        warnings=getattr(serializer, "unsupported_field_warnings", []),
    )

    canonical_data = canonical_request.to_dict()

    results = find_offerings_matching_primary_filters(canonical_request)

    return Response(
        {
            "request": canonical_data,
            "warnings": canonical_data["warnings"],
            "query_interpretation": {
                "primary_filters": canonical_data["primary_filters"],
                "optional_criteria": canonical_data["optional_criteria"],
                "match_policy": canonical_data["match_policy"],
            },
            "result_count": len(results),
            "results": results,
        "status": {
            "search_executed": True,
            "search_engine": "local_seed_catalog_matcher",
            "message": (
                "Search executed using local seed-data matching. "
                "Primary part-family matching and local optional criteria matching are implemented. "
                "RDF/SPARQL search is not implemented yet."
            ),
        },
        },
        status=status.HTTP_200_OK,
    )