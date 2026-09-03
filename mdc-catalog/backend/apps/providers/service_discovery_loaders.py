from pathlib import Path
from typing import Any

import yaml
from django.conf import settings


class ServiceDiscoveryProviderLoadError(ValueError):
    pass


def get_default_service_discovery_provider_dir() -> Path:
    return settings.PROJECT_ROOT / "data" / "curated" / "service_discovery" / "providers"


def load_service_discovery_providers(
    directory: Path | None = None,
) -> list[dict[str, Any]]:
    provider_dir = directory or get_default_service_discovery_provider_dir()

    if not provider_dir.exists() or not provider_dir.is_dir():
        raise ServiceDiscoveryProviderLoadError(
            f"Harmonized service-discovery provider directory does not exist: {provider_dir}"
        )

    records = []
    for path in sorted(
        [
            *provider_dir.glob("*.yaml"),
            *provider_dir.glob("*.yml"),
        ],
        key=lambda item: item.name,
    ):
        try:
            with path.open(encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            raise ServiceDiscoveryProviderLoadError(
                f"Invalid YAML in harmonized provider file {path}: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise ServiceDiscoveryProviderLoadError(
                f"Harmonized provider file must contain a mapping: {path}"
            )

        records.append(data)

    return records
