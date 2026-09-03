from pathlib import Path
from typing import Any

import yaml

from apps.providers.exceptions import SeedDataError
from apps.providers.providers_utils import get_provider_seed_file_path
from apps.providers.validators import validate_seed_data


class ProviderRepositoryError(Exception):
    """Raised when provider seed data cannot be written safely."""


def get_single_provider_id(seed_data: dict[str, Any]) -> str:
    """
    Return the provider_id from normalized single-provider seed data.

    Provider-publication writes one provider file at a time.
    """
    providers = seed_data.get("providers", [])

    if len(providers) != 1:
        raise ProviderRepositoryError(
            "Provider publication seed data must contain exactly one provider."
        )

    provider_id = providers[0].get("provider_id")
    if not provider_id:
        raise ProviderRepositoryError("Provider publication seed data has no provider_id.")

    return provider_id


def write_yaml_file(path: Path, data: dict[str, Any]) -> None:
    """
    Write a Python dictionary as YAML.

    sort_keys=False keeps the YAML order readable:
    metadata, providers, materials, material_grades, offerings.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(
            data,
            file,
            sort_keys=False,
            allow_unicode=True,
        )


def save_provider_seed_data(
    seed_data: dict[str, Any],
    *,
    overwrite: bool = True,
) -> Path:
    """
    Validate and save one provider's normalized seed data.

    Writes to:
    data/curated/providers/{provider_id}.yaml
    """
    try:
        validated_seed_data = validate_seed_data(seed_data)
    except SeedDataError:
        raise
    except Exception as exc:
        raise ProviderRepositoryError(
            f"Provider seed data validation failed: {exc}"
        ) from exc

    provider_id = get_single_provider_id(validated_seed_data)
    target_path = get_provider_seed_file_path(provider_id)

    if target_path.exists() and not overwrite:
        raise ProviderRepositoryError(
            f"Provider seed file already exists and overwrite=False: {target_path}"
        )

    write_yaml_file(target_path, validated_seed_data)

    # Import locally to avoid import cycles.
    from apps.providers.services import clear_seed_cache

    clear_seed_cache()

    return target_path


def load_saved_provider_seed_file(path: Path) -> dict[str, Any]:
    """
    Read back a saved provider YAML file.

    This is useful for tests and debugging.
    """
    if not path.exists():
        raise ProviderRepositoryError(f"Provider seed file does not exist: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ProviderRepositoryError(f"Provider seed file is not a YAML object: {path}")

    return validate_seed_data(data)