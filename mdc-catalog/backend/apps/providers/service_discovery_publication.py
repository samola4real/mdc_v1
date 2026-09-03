from copy import deepcopy


def generate_offering_id(provider_id: str, service_category: str) -> str:
    return f"{provider_id}_{service_category}"


def normalize_service_discovery_publication(validated_data: dict) -> dict:
    provider_id = validated_data["provider_id"]

    provider = {
        "provider_id": provider_id,
        "display_name": validated_data["provider_name"],
        "country": validated_data["country"],
        "certifications": deepcopy(validated_data.get("certifications", [])),
    }

    normalized_offerings = []

    for offering in validated_data["offerings"]:
        normalized_offering = {
            "offering_id": generate_offering_id(
                provider_id,
                offering["service_category"],
            ),
            "provider_id": provider_id,
            "service_category": offering["service_category"],
            "name": offering["offering_name"],
            "part_family": offering["part_family"],
            "support_status": offering["support_status"],
            "supported_part_types": deepcopy(
                offering.get("supported_part_types", []),
            ),
            "family_capabilities": deepcopy(
                offering.get("family_capabilities", {}),
            ),
            "part_type_capabilities": deepcopy(
                offering.get("part_type_capabilities", {}),
            ),
            "generic_capabilities": deepcopy(
                offering.get("generic_capabilities", {}),
            ),
        }
        normalized_offerings.append(normalized_offering)

    normalized = {
        "provider": provider,
        "offerings": normalized_offerings,
    }

    if "publication_metadata" in validated_data:
        normalized["publication_metadata"] = deepcopy(
            validated_data.get("publication_metadata") or {},
        )

    return normalized
