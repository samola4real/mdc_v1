from pathlib import Path

from django.conf import settings


DEFAULT_SEED_FILENAME = "tasowheel_offerings.yaml"


def get_curated_data_dir() -> Path:
    """
    Return the curated data directory.

    Expected location:
    data/curated/
    """
    return Path(settings.CURATED_DATA_DIR)


def get_provider_seed_dir() -> Path:
    """
    Return the multi-provider seed directory.

    Expected location:
    data/curated/providers/
    """
    return Path(settings.PROVIDER_SEED_DIR)


def get_seed_file_path(filename: str = DEFAULT_SEED_FILENAME) -> Path:
    """
    Return the absolute path to a curated seed data file.

    Backwards-compatible single-file location:
    data/curated/tasowheel_offerings.yaml
    """
    return get_curated_data_dir() / filename


def get_provider_seed_file_path(provider_id: str) -> Path:
    """
    Return the expected seed file path for one provider.

    Example:
    provider_id = "tasowheel"
    -> data/curated/providers/tasowheel.yaml
    """
    return get_provider_seed_dir() / f"{provider_id}.yaml"


def list_provider_seed_files() -> list[Path]:
    """
    Return all provider seed files from data/curated/providers/.

    Supported extensions:
    - .yaml
    - .yml
    """
    provider_seed_dir = get_provider_seed_dir()

    if not provider_seed_dir.exists():
        return []

    yaml_files = list(provider_seed_dir.glob("*.yaml"))
    yml_files = list(provider_seed_dir.glob("*.yml"))

    return sorted(yaml_files + yml_files)


def find_duplicate_values(values: list[str]) -> list[str]:
    """
    Return duplicate values from a list.

    Example:
    ["a", "b", "a"] -> ["a"]
    """
    seen = set()
    duplicates = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)

    return sorted(duplicates)