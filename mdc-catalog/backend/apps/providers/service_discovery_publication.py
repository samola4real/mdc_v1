from copy import deepcopy
import re
import unicodedata


OFFERING_ID_MAX_LENGTH = 512
OFFERING_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


class OfferingIdentityError(ValueError):
    """An offering identifier is unsafe or does not belong to its provider."""


class OfferingIdentityConflict(ValueError):
    """A deterministic or explicit offering identifier is already reserved."""


def generate_offering_id(provider_id: str, service_category: str) -> str:
    """Return the preserved legacy identifier for a provider/category pair."""
    return f"{provider_id}_{service_category}"


def _offering_name_slug(offering_name: str) -> str:
    normalized = unicodedata.normalize("NFKD", offering_name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return "_".join(re.findall(r"[a-z0-9]+", ascii_name))


def validate_offering_id(offering_id: str, *, provider_id: str | None = None) -> str:
    if (
        not isinstance(offering_id, str)
        or not offering_id
        or len(offering_id) > OFFERING_ID_MAX_LENGTH
        or not OFFERING_ID_PATTERN.fullmatch(offering_id)
    ):
        raise OfferingIdentityError(
            "offering_id must be lower snake_case and at most 512 characters."
        )
    if provider_id is not None and not offering_id.startswith(f"{provider_id}_"):
        raise OfferingIdentityError(
            "offering_id must start with the owning provider_id followed by an underscore."
        )
    return offering_id


def generate_named_offering_id(
    provider_id: str,
    service_category: str,
    offering_name: str,
) -> str:
    """Return the deterministic same-category fallback identifier."""
    name_slug = _offering_name_slug(offering_name)
    if not name_slug:
        raise OfferingIdentityError(
            "offering_name must contain identifier-safe letters or numbers when "
            "a same-category offering needs a generated identifier."
        )
    return validate_offering_id(
        f"{generate_offering_id(provider_id, service_category)}_{name_slug}",
        provider_id=provider_id,
    )


def resolve_offering_ids(
    provider_id: str,
    offerings: list[dict],
    *,
    reserved_ids=(),
) -> list[str]:
    """Resolve ordered creation IDs without overwriting a reserved identity.

    An omitted ID receives the legacy provider/category identifier when free.
    If that identifier is reserved, the deterministic provider/category/name
    form is used. A collision at either an explicit or fallback identity is
    reported instead of being silently numbered or overwritten.
    """
    reserved = set(reserved_ids)
    resolved = []
    for offering in offerings:
        if "offering_id" in offering:
            candidate = validate_offering_id(
                offering["offering_id"], provider_id=provider_id
            )
        else:
            legacy = validate_offering_id(
                generate_offering_id(provider_id, offering["service_category"]),
                provider_id=provider_id,
            )
            candidate = (
                legacy
                if legacy not in reserved
                else generate_named_offering_id(
                    provider_id,
                    offering["service_category"],
                    offering["offering_name"],
                )
            )

        if candidate in reserved:
            raise OfferingIdentityConflict(
                "offering_id is already reserved; supply a distinct explicit offering_id."
            )
        reserved.add(candidate)
        resolved.append(candidate)
    return resolved


def normalize_service_discovery_publication(validated_data: dict) -> dict:
    provider_id = validated_data["provider_id"]
    offering_ids = resolve_offering_ids(provider_id, validated_data["offerings"])

    provider = {
        "provider_id": provider_id,
        "display_name": validated_data["provider_name"],
        "country": validated_data["country"],
        "certifications": deepcopy(validated_data.get("certifications", [])),
    }

    normalized_offerings = []

    for offering_id, offering in zip(offering_ids, validated_data["offerings"]):
        normalized_offering = {
            "offering_id": offering_id,
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
