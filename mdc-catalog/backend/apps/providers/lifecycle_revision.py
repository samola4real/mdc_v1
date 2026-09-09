"""Opaque HTTP revision helpers for persisted provider lifecycle entities."""

from hashlib import sha256


def build_entity_etag(entity_type: str, external_id: str, updated_at) -> str:
    """Build a strong opaque ETag without exposing internal timestamps."""
    timestamp = updated_at.isoformat() if updated_at is not None else ""
    digest = sha256(
        f"{entity_type}:{external_id}:{timestamp}".encode("utf-8")
    ).hexdigest()
    return f'"{digest}"'
