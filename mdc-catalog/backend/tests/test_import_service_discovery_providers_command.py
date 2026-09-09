import io
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import OperationalError
from django.test import TestCase

from apps.providers.models import Provider
from apps.providers.service_discovery_db_repository import load_service_discovery_providers_from_db
from apps.providers.service_discovery_loaders import (
    get_default_service_discovery_provider_dir, load_service_discovery_providers,
)


class ImportServiceDiscoveryProvidersCommandTests(TestCase):
    def test_default_directory_import_and_idempotent_summary(self):
        for _ in range(2):
            output = io.StringIO()
            call_command("import_service_discovery_providers", stdout=output, no_color=True)
            self.assertEqual(output.getvalue(),
                             "Providers imported/updated: 3; offerings synchronized: 4; certifications synchronized: 5.\n")
            self.assertEqual(load_service_discovery_providers_from_db(), load_service_discovery_providers())

    def test_directory_override_reuses_loader(self):
        with TemporaryDirectory() as directory:
            target = Path(directory)
            source = get_default_service_discovery_provider_dir() / "tasowheel.yaml"
            (target / "tasowheel.yml").write_bytes(source.read_bytes())
            output = io.StringIO()
            call_command("import_service_discovery_providers", "--directory", directory, stdout=output)
            self.assertEqual(load_service_discovery_providers_from_db(), load_service_discovery_providers(target))
            self.assertIn("Providers imported/updated: 1; offerings synchronized: 2; certifications synchronized: 4.",
                          output.getvalue())

    def test_invalid_yaml_error_does_not_expose_source(self):
        with TemporaryDirectory() as directory:
            (Path(directory) / "invalid.yaml").write_text("secret_payload: [invalid", encoding="utf-8")
            with self.assertRaises(CommandError) as caught:
                call_command("import_service_discovery_providers", "--directory", directory)
            self.assertNotIn("secret_payload", str(caught.exception))
            self.assertFalse(Provider.objects.exists())

    def test_missing_directory_reports_safe_error(self):
        with TemporaryDirectory() as directory:
            with self.assertRaisesMessage(CommandError, "Unable to load provider YAML"):
                call_command("import_service_discovery_providers", "--directory", str(Path(directory) / "absent"))

    def test_invalid_second_file_does_not_import_first_file(self):
        with TemporaryDirectory() as directory:
            source = get_default_service_discovery_provider_dir() / "tasowheel.yaml"
            (Path(directory) / "a.yaml").write_bytes(source.read_bytes())
            (Path(directory) / "z.yaml").write_text("provider: {}\nofferings: []\n", encoding="utf-8")
            with self.assertRaises(CommandError):
                call_command("import_service_discovery_providers", "--directory", directory)
            self.assertFalse(Provider.objects.exists())

    def test_empty_directory_is_safe_noop(self):
        call_command("import_service_discovery_providers", stdout=io.StringIO())
        with TemporaryDirectory() as directory:
            output = io.StringIO()
            call_command("import_service_discovery_providers", "--directory", directory, stdout=output)
            self.assertIn("Providers imported/updated: 0", output.getvalue())
            self.assertEqual(Provider.objects.count(), 3)

    def test_database_error_is_redacted(self):
        with patch("apps.providers.service_discovery_db_repository.Provider.objects.update_or_create",
                   side_effect=OperationalError("password=secret host=private row=payload")):
            with self.assertRaises(CommandError) as caught:
                call_command("import_service_discovery_providers")
        self.assertEqual(str(caught.exception), "Database import failed; the entire batch was rolled back.")
