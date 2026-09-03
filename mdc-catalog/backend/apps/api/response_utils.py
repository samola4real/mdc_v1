from apps.providers.services import (
    get_offerings_for_provider,

)

def build_provider_response(provider: dict) -> dict:
    """
    Convert internal provider seed data into API-friendly provider response.
    """
    offerings = get_offerings_for_provider(provider["provider_id"])

    return {
        "provider_id": provider["provider_id"],
        "legal_name": provider.get("legal_name", ""),
        "display_name": provider.get("display_name", ""),
        "provider_type": provider.get("provider_type", ""),
        "country": provider.get("country", ""),
        "source_type": provider.get("source_type"),
        "confidence": provider.get("confidence"),
        "facilities": provider.get("facilities", []),
        "certifications": [
            certification.get("code")
            for certification in provider.get("certifications", [])
        ],
        "offerings": [
            {
                "offering_id": offering["offering_id"],
                "name": offering.get("name", ""),
                "service_type": offering.get("service_type", ""),
            }
            for offering in offerings
        ],
    }


def build_offering_response(offering: dict) -> dict:
    """
    Convert internal offering seed data into API-friendly offering response.
    """
    supported_materials = [
        material_entry["material"]
        for material_entry in offering.get("supported_materials", [])
    ]

    return {
        "offering_id": offering["offering_id"],
        "provider_id": offering["provider_id"],
        "name": offering.get("name", ""),
        "service_type": offering.get("service_type", ""),
        "ontology_service_concept": offering.get("ontology_service_concept"),
        "source_type": offering.get("source_type"),
        "confidence": offering.get("confidence"),
        "part_families": offering.get("part_families", []),
        "processes": offering.get("processes", []),
        "materials": supported_materials,
        "material_grades": offering.get("supported_material_grades", []),
        "capabilities": offering.get("capabilities", {}),
        "notes": offering.get("notes", []),
    }