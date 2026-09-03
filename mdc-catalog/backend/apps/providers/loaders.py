from pathlib import Path
from typing import Any

import yaml

from apps.providers.exceptions import SeedDataError
from apps.providers.providers_utils import (
    DEFAULT_SEED_FILENAME,
    get_seed_file_path,
    list_provider_seed_files,
)
from apps.providers.validators import validate_seed_data


def load_yaml_file(path: Path) -> dict[str, Any]:
    """
    Read a YAML file and return it as a Python dictionary.

    yaml.safe_load() converts YAML into normal Python structures:
    - YAML mapping -> dict
    - YAML list -> list
    - YAML string -> str
    - YAML number -> int/float
    - YAML null -> None
    """
    if not path.exists():
        raise SeedDataError(f"Seed data file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise SeedDataError(f"Seed data file must contain a YAML object: {path}")

    return data


def merge_seed_data(seed_data_items: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Merge multiple validated provider seed files into one catalogue dictionary.

    Providers, materials, material grades, and offerings are appended.
    Duplicate provider/offering IDs are checked by validate_seed_data().
    """
    if not seed_data_items:
        raise SeedDataError("No seed data items were provided for merging.")

    merged_data: dict[str, Any] = {
        "metadata": {
            "dataset_id": "catalog_seed_v1",
            "version": "1.0",
            "status": "merged_provider_seed",
            "route_fields_included": False,
            "source_dataset_ids": [],
            "notes": [
                "Merged catalogue seed generated from provider seed files.",
                "Route/operation sequence fields are excluded from v1.",
            ],
        },
        "providers": [],
        "materials": [],
        "material_grades": [],
        "offerings": [],
    }

    for data in seed_data_items:
        validated_data = validate_seed_data(data)
        metadata = validated_data.get("metadata", {})

        dataset_id = metadata.get("dataset_id")
        if dataset_id:
            merged_data["metadata"]["source_dataset_ids"].append(dataset_id)

        merged_data["providers"].extend(validated_data.get("providers", []))
        merged_data["materials"].extend(validated_data.get("materials", []))
        merged_data["material_grades"].extend(validated_data.get("material_grades", []))
        merged_data["offerings"].extend(validated_data.get("offerings", []))

    return validate_seed_data(merged_data)


def load_provider_seed_folder() -> dict[str, Any]:
    """
    Load all provider seed files from data/curated/providers/
    and merge them into one catalogue seed dictionary.
    """
    seed_files = list_provider_seed_files()

    if not seed_files:
        raise SeedDataError("No provider seed files found.")

    seed_data_items = []

    for seed_file in seed_files:
        data = load_yaml_file(seed_file)
        seed_data_items.append(data)

    return merge_seed_data(seed_data_items)


def load_catalog_seed_data(filename: str | None = None) -> dict[str, Any]:
    """
    Load catalogue seed data.

    Preferred behavior:
    - Load all files from data/curated/providers/

    Backwards-compatible fallback:
    - If no provider seed files exist, load data/curated/tasowheel_offerings.yaml

    If filename is provided explicitly, load that single file from data/curated/.
    """
    if filename is not None:
        seed_path = get_seed_file_path(filename)
        data = load_yaml_file(seed_path)
        return validate_seed_data(data)

    provider_seed_files = list_provider_seed_files()

    if provider_seed_files:
        return load_provider_seed_folder()

    seed_path = get_seed_file_path(DEFAULT_SEED_FILENAME)
    data = load_yaml_file(seed_path)
    return validate_seed_data(data)


def load_tasowheel_seed_data() -> dict[str, Any]:
    """
    Backwards-compatible wrapper.

    New code should use load_catalog_seed_data().
    """
    return load_catalog_seed_data()