"""Database configuration without connections or credential logging."""

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


def database_config(base_dir, database_url=None):
    if not database_url or not database_url.strip():
        return {"ENGINE": "django.db.backends.sqlite3", "NAME": base_dir / "db.sqlite3"}

    try:
        config = dj_database_url.parse(database_url.strip(), conn_max_age=0)
        if config["ENGINE"] != "django.db.backends.postgresql":
            raise ValueError("Unsupported database engine")
    except (ValueError, KeyError):
        # Parser errors may contain the URL; never expose them or chain credentials.
        raise ImproperlyConfigured("DATABASE_URL must be a valid PostgreSQL URL.") from None
    return config
