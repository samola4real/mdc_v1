from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase

from apps.providers.service_discovery_loaders import (
    ServiceDiscoveryProviderLoadError,
    load_service_discovery_providers,
)


class ServiceDiscoveryProviderLoaderTests(SimpleTestCase):
    def test_loads_harmonized_provider_records_in_file_name_order(self):
        records = load_service_discovery_providers()
        provider_ids = [record["provider"]["provider_id"] for record in records]

        self.assertEqual(provider_ids, sorted(provider_ids))
        self.assertIn("tasowheel", provider_ids)
        self.assertIn("demo_machining_provider", provider_ids)
        self.assertIn("precipart", provider_ids)

    def test_loader_uses_only_harmonized_internal_shape(self):
        records = load_service_discovery_providers()

        for record in records:
            self.assertIn("provider", record)
            self.assertIn("offerings", record)
            self.assertNotIn("metadata", record)
            self.assertNotIn("materials", record)
            self.assertNotIn("material_grades", record)

    def test_missing_directory_raises_clear_error(self):
        missing = Path("does_not_exist_service_discovery_dir")

        with self.assertRaises(ServiceDiscoveryProviderLoadError):
            load_service_discovery_providers(missing)

    def test_invalid_yaml_raises_clear_error(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            (path / "broken.yaml").write_text("provider: [", encoding="utf-8")

            with self.assertRaises(ServiceDiscoveryProviderLoadError):
                load_service_discovery_providers(path)

    def test_non_mapping_root_raises_clear_error(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            (path / "list.yaml").write_text("- not\n- mapping\n", encoding="utf-8")

            with self.assertRaises(ServiceDiscoveryProviderLoadError):
                load_service_discovery_providers(path)
