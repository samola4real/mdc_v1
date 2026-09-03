from copy import deepcopy

from apps.search.service_discovery_request import CanonicalServiceDiscoverySearchRequest


def normalize_service_discovery_search_request(
    validated_data: dict,
    *,
    warnings: list | None = None,
) -> CanonicalServiceDiscoverySearchRequest:
    return CanonicalServiceDiscoverySearchRequest(
        request_id=validated_data["request_id"],
        consumer_id=validated_data["consumer_id"],
        selection={
            "service_category": validated_data["service_category"],
            "part_family": validated_data["part_family"],
            "part_type": validated_data["part_type"],
        },
        requirements=deepcopy(validated_data["requirements"]),
        match_policy=deepcopy(validated_data["match_policy"]),
        warnings=deepcopy(warnings or []),
    )
