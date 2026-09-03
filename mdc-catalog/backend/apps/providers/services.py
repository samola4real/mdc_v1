from copy import deepcopy
from functools import lru_cache
from typing import Any

from apps.providers.loaders import load_catalog_seed_data


class ProviderNotFoundError(Exception):
    """Raised when a provider ID does not exist in the seed data."""


class OfferingNotFoundError(Exception):
    """Raised when an offering ID does not exist in the seed data."""


@lru_cache(maxsize=1)
def get_seed_data() -> dict[str, Any]:
    """
    Return cached catalogue seed data.

    lru_cache stores the loaded YAML result in memory after the first call.
    That means we do not re-read the YAML files on every lookup.

    During development/tests, call clear_seed_cache() if the YAML files change.
    """
    return load_catalog_seed_data()


def clear_seed_cache() -> None:
    """
    Clear cached seed data.

    Useful in tests or after editing YAML files while the server is running.
    """
    get_seed_data.cache_clear()


def list_providers() -> list[dict[str, Any]]:
    """
    Return all providers from seed data.
    """
    providers = get_seed_data().get("providers", [])
    return deepcopy(providers)


def list_offerings() -> list[dict[str, Any]]:
    """
    Return all offerings from seed data.
    """
    offerings = get_seed_data().get("offerings", [])
    return deepcopy(offerings)


def get_provider_by_id(provider_id: str) -> dict[str, Any]:
    """
    Find one provider by provider_id.
    """
    for provider in get_seed_data().get("providers", []):
        if provider.get("provider_id") == provider_id:
            return deepcopy(provider)

    raise ProviderNotFoundError(f"Provider not found: {provider_id}")


def get_offering_by_id(offering_id: str) -> dict[str, Any]:
    """
    Find one offering by offering_id.
    """
    for offering in get_seed_data().get("offerings", []):
        if offering.get("offering_id") == offering_id:
            return deepcopy(offering)

    raise OfferingNotFoundError(f"Offering not found: {offering_id}")


def get_offerings_for_provider(provider_id: str) -> list[dict[str, Any]]:
    """
    Return all offerings owned by one provider.

    This first checks that the provider exists.
    """
    get_provider_by_id(provider_id)

    offerings = [
        offering
        for offering in get_seed_data().get("offerings", [])
        if offering.get("provider_id") == provider_id
    ]

    return deepcopy(offerings)