"""Explicit bootstrap import and canonical reads; runtime discovery still uses YAML."""

import json
from copy import deepcopy

from django.db import transaction
from django.db.models import Prefetch

from apps.providers.models import Offering, Provider, ProviderCertification


class ServiceDiscoveryImportError(ValueError):
    """Structural or identity conflict, with no payload values in the message."""


OFFERING_TEXT_FIELDS = {
    "offering_id": 512, "provider_id": 255, "service_category": 255,
    "name": 255, "part_family": 255, "support_status": 32,
}
CAPABILITY_FIELDS = (
    "family_capabilities", "part_type_capabilities", "generic_capabilities",
)


def _mapping(value, allowed, path):
    if not isinstance(value, dict):
        raise ServiceDiscoveryImportError(f"{path} must be a mapping.")
    if set(value) - set(allowed):
        raise ServiceDiscoveryImportError(f"{path} contains unsupported keys.")


def _text_fields(value, fields, path):
    for field, limit in fields.items():
        item = value.get(field)
        if not isinstance(item, str) or not item.strip() or len(item) > limit:
            raise ServiceDiscoveryImportError(
                f"{path}.{field} must be a nonempty string of at most {limit} characters."
            )


def _json_value(value, path):
    # PostgreSQL JSONB cannot represent NaN/Infinity or non-string object keys.
    if isinstance(value, dict):
        if any(not isinstance(key, str) or "\x00" in key for key in value):
            raise ServiceDiscoveryImportError(f"{path} must have JSON string keys without NUL.")
        for item in value.values():
            _json_value(item, path)
    elif isinstance(value, list):
        for item in value:
            _json_value(item, path)
    elif isinstance(value, str) and "\x00" in value:
        raise ServiceDiscoveryImportError(f"{path} must not contain NUL.")
    elif value is not None and not isinstance(value, (str, bool, int, float)):
        raise ServiceDiscoveryImportError(f"{path} must contain JSON values.")


def _validated_records(records):
    if not isinstance(records, (list, tuple)):
        raise ServiceDiscoveryImportError("Import batch must be a list or tuple of records.")
    records = deepcopy(records)
    provider_ids, offering_ids = set(), set()
    for index, record in enumerate(records):
        path = f"records[{index}]"
        _mapping(record, {"provider", "offerings", "publication_metadata"}, path)
        provider = record.get("provider")
        _mapping(provider, {"provider_id", "display_name", "country", "certifications"}, f"{path}.provider")
        _text_fields(provider, {"provider_id": 255, "display_name": 255, "country": 100}, f"{path}.provider")
        provider_id = provider["provider_id"]
        if provider_id in provider_ids:
            raise ServiceDiscoveryImportError(f"{path} duplicates a provider_id in the batch.")
        provider_ids.add(provider_id)
        certifications = provider.setdefault("certifications", [])
        if not isinstance(certifications, list):
            raise ServiceDiscoveryImportError(f"{path}.provider.certifications must be a list.")
        codes = set()
        for cert_index, certification in enumerate(certifications):
            cert_path = f"{path}.provider.certifications[{cert_index}]"
            _mapping(certification, {"code", "source_type", "confidence", "source_note"}, cert_path)
            _text_fields(certification, {"code": 255, "source_type": 64, "confidence": 64}, cert_path)
            if certification["code"] in codes:
                raise ServiceDiscoveryImportError(f"{cert_path} duplicates a certification code.")
            codes.add(certification["code"])
            if certification.get("source_note") is not None and not isinstance(certification["source_note"], str):
                raise ServiceDiscoveryImportError(f"{cert_path}.source_note must be a string or null.")
        metadata = record.setdefault("publication_metadata", {})
        if not isinstance(metadata, dict):
            raise ServiceDiscoveryImportError(f"{path}.publication_metadata must be a mapping.")
        offerings = record.get("offerings")
        if not isinstance(offerings, list):
            raise ServiceDiscoveryImportError(f"{path}.offerings must be a list.")
        for offering_index, offering in enumerate(offerings):
            offering_path = f"{path}.offerings[{offering_index}]"
            _mapping(offering, {*OFFERING_TEXT_FIELDS, "supported_part_types", *CAPABILITY_FIELDS}, offering_path)
            _text_fields(offering, OFFERING_TEXT_FIELDS, offering_path)
            if offering["provider_id"] != provider_id:
                raise ServiceDiscoveryImportError(f"{offering_path}.provider_id does not match its provider.")
            if offering["offering_id"] in offering_ids:
                raise ServiceDiscoveryImportError(f"{offering_path} duplicates an offering_id in the batch.")
            offering_ids.add(offering["offering_id"])
            if offering["support_status"] not in Offering.SupportStatus.values:
                raise ServiceDiscoveryImportError(f"{offering_path}.support_status is invalid.")
            if not isinstance(offering.setdefault("supported_part_types", []), list):
                raise ServiceDiscoveryImportError(f"{offering_path}.supported_part_types must be a list.")
            for field in CAPABILITY_FIELDS:
                if not isinstance(offering.setdefault(field, {}), dict):
                    raise ServiceDiscoveryImportError(f"{offering_path}.{field} must be a mapping.")
        _json_value(record, path)
        try:
            json.dumps(record, allow_nan=False)
        except (TypeError, ValueError):
            raise ServiceDiscoveryImportError(f"{path} must contain finite JSON values.") from None
    return records


def import_service_discovery_provider_records(records):
    """Synchronize full provider snapshots atomically; leave absent providers alone.

    Missing optional containers become empty lists/dicts. No ontology remapping,
    publication history, sync events, or runtime source changes are performed.
    """
    records = _validated_records(records)
    summary = {"providers": 0, "offerings": 0, "certifications": 0}
    with transaction.atomic():
        requested_owners = {
            offering["offering_id"]: record["provider"]["provider_id"]
            for record in records for offering in record["offerings"]
        }
        # Check ownership before any stale-row deletions can erase that evidence.
        existing_owners = Offering.objects.select_for_update().filter(
            offering_id__in=requested_owners
        ).values_list("offering_id", "provider__provider_id")
        for offering_id, owner in existing_owners:
            if requested_owners[offering_id] != owner:
                raise ServiceDiscoveryImportError("An offering_id belongs to another provider.")
        for record in records:
            source = record["provider"]
            provider, _ = Provider.objects.update_or_create(
                provider_id=source["provider_id"],
                defaults={
                    "provider_name": source["display_name"], "country": source["country"],
                    "status": Provider.Status.ACTIVE,
                    "publication_metadata": record["publication_metadata"],
                },
            )
            codes = []
            for sequence, certification in enumerate(source["certifications"]):
                codes.append(certification["code"])
                ProviderCertification.objects.update_or_create(
                    provider=provider, code=certification["code"],
                    defaults={
                        "source_type": certification["source_type"],
                        "confidence": certification["confidence"],
                        "source_note": certification.get("source_note"),
                        "source_note_present": "source_note" in certification,
                        "sequence_index": sequence,
                    },
                )
            provider.certifications.exclude(code__in=codes).delete()
            offering_ids = []
            for sequence, offering in enumerate(record["offerings"]):
                offering_ids.append(offering["offering_id"])
                # Never transfer an existing external offering identity to another provider.
                existing = Offering.objects.select_for_update().filter(
                    offering_id=offering["offering_id"]
                ).first()
                if existing is not None and existing.provider_id != provider.pk:
                    raise ServiceDiscoveryImportError("An offering_id belongs to another provider.")
                Offering.objects.update_or_create(
                    offering_id=offering["offering_id"], provider=provider,
                    defaults={
                        "offering_name": offering["name"],
                        "service_category": offering["service_category"],
                        "part_family": offering["part_family"],
                        "support_status": offering["support_status"],
                        "supported_part_types": offering["supported_part_types"],
                        **{field: offering[field] for field in CAPABILITY_FIELDS},
                        "sequence_index": sequence, "is_active": True,
                    },
                )
            provider.offerings.exclude(offering_id__in=offering_ids).delete()
            summary["providers"] += 1
            summary["offerings"] += len(offering_ids)
            summary["certifications"] += len(codes)
    return summary


def _active_providers():
    return Provider.objects.filter(status=Provider.Status.ACTIVE).order_by("provider_id").prefetch_related(
        Prefetch("offerings", queryset=Offering.objects.filter(is_active=True).order_by(
            "sequence_index", "offering_id"
        ), to_attr="canonical_offerings"),
        Prefetch("certifications", queryset=ProviderCertification.objects.order_by(
            "sequence_index", "code"
        ), to_attr="canonical_certifications"),
    )


def _canonical_record(provider):
    certifications = []
    for row in provider.canonical_certifications:
        certification = {"code": row.code, "source_type": row.source_type, "confidence": row.confidence}
        if row.source_note_present or row.source_note is not None:
            certification["source_note"] = row.source_note
        certifications.append(certification)
    return {
        "provider": {
            "provider_id": provider.provider_id, "display_name": provider.provider_name,
            "country": provider.country, "certifications": certifications,
        },
        "offerings": [
            {
                "offering_id": row.offering_id, "provider_id": provider.provider_id,
                "service_category": row.service_category, "name": row.offering_name,
                "part_family": row.part_family, "support_status": row.support_status,
                "supported_part_types": deepcopy(row.supported_part_types),
                **{field: deepcopy(getattr(row, field)) for field in CAPABILITY_FIELDS},
            }
            for row in provider.canonical_offerings
        ],
        "publication_metadata": deepcopy(provider.publication_metadata),
    }


def load_service_discovery_providers_from_db():
    """Return active providers/offerings in explicit canonical order (three queries)."""
    return [_canonical_record(provider) for provider in _active_providers()]


def get_service_discovery_provider_from_db(provider_id):
    """Return an active canonical provider, or None for missing/inactive identities."""
    provider = _active_providers().filter(provider_id=provider_id).first()
    return _canonical_record(provider) if provider is not None else None
