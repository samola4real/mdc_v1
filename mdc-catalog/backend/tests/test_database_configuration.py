import io
import os
import subprocess
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.database import database_config


class DatabaseConfigurationTests(SimpleTestCase):
    base_dir = Path("isolated_backend")
    # Synthetic, non-routable URL used only for parsing; no connection is made.
    database_url = "postgresql://test_user:dummy%40password@database.invalid:5432/catalogue"

    def test_absent_url_uses_sqlite_and_ignores_environment(self):
        with patch.dict(os.environ, {"DATABASE_URL": self.database_url}):
            self.assertEqual(database_config(self.base_dir), {
                "ENGINE": "django.db.backends.sqlite3", "NAME": self.base_dir / "db.sqlite3"
            })

    def test_empty_url_uses_sqlite(self):
        for value in ("", "  "):
            with self.subTest(value=value):
                self.assertEqual(database_config(self.base_dir, value)["ENGINE"], "django.db.backends.sqlite3")

    def test_postgresql_url_parsed_with_short_lived_connections(self):
        for scheme in ("postgresql", "postgres"):
            with self.subTest(scheme=scheme):
                config = database_config(self.base_dir, self.database_url.replace("postgresql:", scheme + ":"))
                self.assertEqual(config["ENGINE"], "django.db.backends.postgresql")
                self.assertEqual(config["NAME"], "catalogue")
                self.assertEqual(config["USER"], "test_user")
                self.assertEqual(config["PASSWORD"], "dummy@password")
                self.assertEqual(config["HOST"], "database.invalid")
                self.assertEqual(config["PORT"], 5432)
                self.assertEqual(config["CONN_MAX_AGE"], 0)

    def test_query_options_preserved(self):
        config = database_config(self.base_dir, self.database_url + "?sslmode=require&connect_timeout=10&application_name=mdc")
        self.assertEqual(config["OPTIONS"]["sslmode"], "require")
        self.assertEqual(str(config["OPTIONS"]["connect_timeout"]), "10")
        self.assertEqual(config["OPTIONS"]["application_name"], "mdc")

    def test_non_postgresql_url_rejected(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "DATABASE_URL must be a valid PostgreSQL URL."):
            database_config(self.base_dir, "sqlite:///other.sqlite3")

    def test_no_credentials_logged_or_exposed_in_errors(self):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output), self.assertNoLogs():
            database_config(self.base_dir, self.database_url)
            for value in (self.database_url.replace(":5432/", ":invalid/"),
                          self.database_url.replace("postgresql:", "unsupported:")):
                with self.assertRaises(ImproperlyConfigured) as caught:
                    database_config(self.base_dir, value)
                rendered = "".join(traceback.format_exception(caught.exception))
                self.assertNotIn("dummy", rendered)
                self.assertNotIn("test_user", rendered)
                self.assertNotIn("database.invalid", rendered)
        self.assertEqual(output.getvalue(), "")

    def test_settings_wire_environment_and_preserve_production_safety(self):
        script = """
import os
from config import settings as base, settings_production as production
from config.database import database_config
assert base.DATABASES['default'] == database_config(base.BASE_DIR, os.environ['DATABASE_URL'])
assert production.DATABASES == base.DATABASES
assert production.MDC_PROVIDER_PUBLICATION_ENABLED is False
"""
        for value in ("", self.database_url + "?sslmode=require"):
            with self.subTest(postgresql=bool(value)):
                # Keep only OS necessities; no developer Django or database settings.
                env = {key: os.environ[key] for key in ("SYSTEMROOT", "PATH", "TEMP", "TMP") if key in os.environ}
                env.update(DATABASE_URL=value, DJANGO_SECRET_KEY="isolated-test-secret")
                result = subprocess.run([sys.executable, "-c", script], env=env,
                                        cwd=Path(__file__).resolve().parents[1],
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
