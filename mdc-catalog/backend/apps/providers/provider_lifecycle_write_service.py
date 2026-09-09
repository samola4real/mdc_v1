"""Transactional provider lifecycle writes with publication and outbox evidence."""

from copy import deepcopy

from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import Max
from django.utils import timezone

from apps.api.service_discovery_publication_serializers import (
    validate_lifecycle_offering,
)
from apps.providers.lifecycle_revision import build_entity_etag
from apps.providers.models import (
    CatalogueSyncEvent,
    Offering,
    Provider,
    ProviderCertification,
    ProviderPublication,
)
from apps.providers.service_discovery_publication import (
    generate_offering_id,
    normalize_service_discovery_publication,
)


class LifecycleConflict(Exception):
    def __init__(self, code):
        self.code = code


class LifecycleNotFound(Exception):
    def __init__(self, entity):
        self.entity = entity


class LifecyclePreconditionFailed(Exception):
    def __init__(self, entity):
        self.entity = entity


class LifecycleWriteError(Exception):
    """Safe boundary for unexpected persistence failures."""


OFFERING_JSON_FIELDS = (
    "supported_part_types",
    "family_capabilities",
    "part_type_capabilities",
    "generic_capabilities",
    "custom_offering_fields",
    "custom_capability_fields",
)

OFFERING_MUTABLE_FIELDS = (
    "offering_name",
    "support_status",
    *OFFERING_JSON_FIELDS,
    "is_active",
)


def _certification_payload(row):
    payload = {
        "code": row.code,
        "source_type": row.source_type,
        "confidence": row.confidence,
    }
    if row.source_note_present or row.source_note is not None:
        payload["source_note"] = row.source_note
    return payload


def _offering_snapshot(row, provider_id):
    return {
        "offering_id": row.offering_id,
        "provider_id": provider_id,
        "service_category": row.service_category,
        "name": row.offering_name,
        "part_family": row.part_family,
        "support_status": row.support_status,
        "supported_part_types": deepcopy(row.supported_part_types),
        "family_capabilities": deepcopy(row.family_capabilities),
        "part_type_capabilities": deepcopy(row.part_type_capabilities),
        "generic_capabilities": deepcopy(row.generic_capabilities),
        "custom_offering_fields": deepcopy(row.custom_offering_fields),
        "custom_capability_fields": deepcopy(row.custom_capability_fields),
        "is_active": row.is_active,
    }


def _provider_snapshot(provider):
    certifications = provider.certifications.order_by("sequence_index", "code")
    offerings = provider.offerings.order_by("sequence_index", "offering_id")
    return {
        "provider": {
            "provider_id": provider.provider_id,
            "display_name": provider.provider_name,
            "country": provider.country,
            "status": provider.status,
            "certifications": [_certification_payload(row) for row in certifications],
            "custom_provider_fields": deepcopy(provider.custom_provider_fields),
        },
        "offerings": [
            _offering_snapshot(row, provider.provider_id) for row in offerings
        ],
        "publication_metadata": deepcopy(provider.publication_metadata),
    }


def _create_publication(
    provider,
    operation,
    submitted_payload,
    *,
    actor_id=None,
):
    now = timezone.now()
    return ProviderPublication.objects.create(
        provider=provider,
        provider_id_snapshot=provider.provider_id,
        operation=operation,
        status=ProviderPublication.Status.SYNC_PENDING,
        contract_version="1.0",
        submitted_payload=deepcopy(submitted_payload),
        normalized_payload=_provider_snapshot(provider),
        submitted_by_external_id=actor_id,
        validated_at=now,
        persisted_at=now,
    )


def _create_sync_event(publication, entity_type, entity_id):
    return CatalogueSyncEvent.objects.create(
        publication=publication,
        entity_type=entity_type,
        entity_id=entity_id,
        operation=CatalogueSyncEvent.Operation.UPSERT,
        status=CatalogueSyncEvent.Status.PENDING,
    )


def _create_certifications(provider, certifications):
    ProviderCertification.objects.bulk_create([
        ProviderCertification(
            provider=provider,
            code=item["code"],
            source_type=item.get("source_type", "provider_confirmed"),
            confidence=item.get("confidence", "declared"),
            source_note=item.get("source_note"),
            source_note_present="source_note" in item,
            sequence_index=index,
        )
        for index, item in enumerate(certifications)
    ])


def _create_offering(provider, item, sequence_index, *, offering_id=None):
    return Offering.objects.create(
        provider=provider,
        offering_id=offering_id or generate_offering_id(
            provider.provider_id, item["service_category"]
        ),
        offering_name=item["offering_name"],
        service_category=item["service_category"],
        part_family=item["part_family"],
        support_status=item["support_status"],
        sequence_index=sequence_index,
        **{field: deepcopy(item.get(field, [] if field == "supported_part_types" else {}))
           for field in OFFERING_JSON_FIELDS},
    )


def _entity_etag(entity_type, row):
    external_id = row.provider_id if entity_type == "provider" else row.offering_id
    return build_entity_etag(entity_type, external_id, row.updated_at)


def _assert_expected_etag(entity_type, row, expected_etag):
    if expected_etag is None:
        return
    if not compare_etags(_entity_etag(entity_type, row), expected_etag):
        raise LifecyclePreconditionFailed(entity_type)


def compare_etags(current_etag, expected_etag):
    # ETags are opaque SHA-256 values generated server-side. Exact comparison is
    # intentional; weak/list/wildcard preconditions are not accepted in M7.6.
    return current_etag == expected_etag


def _touch_provider(provider):
    provider.updated_at = timezone.now()
    provider.save(update_fields=["updated_at"])


def _result(publication, provider, offering_ids, *, offering_id=None, etag=None):
    result = {
        "contract_version": "1.0",
        "status": "accepted",
        "operation": publication.operation,
        "provider_id": provider.provider_id,
        "publication_id": str(publication.id),
        "publication_status": publication.status,
        "sync_status": "pending",
        "offering_ids": offering_ids,
    }
    if offering_id is not None:
        result["offering_id"] = offering_id
    if etag is not None:
        result["_etag"] = etag
    return result


def register_provider(validated_data, submitted_payload, *, actor_id=None):
    provider_id = validated_data["provider_id"]
    normalized = normalize_service_discovery_publication(validated_data)
    if Provider.objects.filter(provider_id=provider_id).exists():
        raise LifecycleConflict("provider_already_exists")
    try:
        with transaction.atomic():
            provider = Provider.objects.create(
                provider_id=provider_id,
                provider_name=validated_data["provider_name"],
                country=validated_data["country"],
                status=Provider.Status.ACTIVE,
                publication_metadata=deepcopy(validated_data.get("publication_metadata", {})),
                custom_provider_fields=deepcopy(validated_data.get("custom_provider_fields", {})),
            )
            _create_certifications(provider, validated_data.get("certifications", []))
            offerings = [
                _create_offering(
                    provider,
                    item,
                    index,
                    offering_id=normalized["offerings"][index]["offering_id"],
                )
                for index, item in enumerate(validated_data["offerings"])
            ]
            # Provider revision represents the aggregate exposed by provider GET.
            _touch_provider(provider)
            publication = _create_publication(
                provider,
                ProviderPublication.Operation.CREATE,
                submitted_payload,
                actor_id=actor_id,
            )
            _create_sync_event(publication, CatalogueSyncEvent.EntityType.PROVIDER, provider_id)
            for offering in offerings:
                _create_sync_event(
                    publication, CatalogueSyncEvent.EntityType.OFFERING, offering.offering_id
                )
        return _result(
            publication,
            provider,
            [offering.offering_id for offering in offerings],
            etag=_entity_etag("provider", provider),
        )
    except IntegrityError as exc:
        try:
            if Provider.objects.filter(provider_id=provider_id).exists():
                raise LifecycleConflict("provider_already_exists") from exc
        except DatabaseError:
            pass
        raise LifecycleWriteError from exc
    except DatabaseError as exc:
        raise LifecycleWriteError from exc


def update_provider(
    provider_id,
    changes,
    submitted_payload,
    *,
    actor_id=None,
    expected_etag=None,
):
    try:
        with transaction.atomic():
            try:
                provider = Provider.objects.select_for_update().get(provider_id=provider_id)
            except Provider.DoesNotExist as exc:
                raise LifecycleNotFound("provider") from exc

            _assert_expected_etag("provider", provider, expected_etag)

            update_fields = []
            for field in (
                "provider_name", "country", "status", "publication_metadata",
                "custom_provider_fields",
            ):
                if field in changes:
                    setattr(provider, field, deepcopy(changes[field]))
                    update_fields.append(field)
            if "certifications" in changes:
                provider.certifications.all().delete()
                _create_certifications(provider, changes["certifications"])

            provider.updated_at = timezone.now()
            provider.save(update_fields=[*update_fields, "updated_at"])

            publication = _create_publication(
                provider,
                ProviderPublication.Operation.UPDATE,
                submitted_payload,
                actor_id=actor_id,
            )
            _create_sync_event(
                publication, CatalogueSyncEvent.EntityType.PROVIDER, provider.provider_id
            )
            offering_ids = list(
                provider.offerings.order_by("sequence_index", "offering_id")
                .values_list("offering_id", flat=True)
            )
        return _result(
            publication,
            provider,
            offering_ids,
            etag=_entity_etag("provider", provider),
        )
    except DatabaseError as exc:
        raise LifecycleWriteError from exc


def add_provider_offering(
    provider_id,
    offering_data,
    submitted_payload,
    *,
    actor_id=None,
):
    offering_id = generate_offering_id(provider_id, offering_data["service_category"])
    try:
        with transaction.atomic():
            try:
                provider = Provider.objects.select_for_update().get(provider_id=provider_id)
            except Provider.DoesNotExist as exc:
                raise LifecycleNotFound("provider") from exc
            if Offering.objects.filter(offering_id=offering_id).exists():
                raise LifecycleConflict("offering_already_exists")
            maximum = provider.offerings.aggregate(value=Max("sequence_index"))["value"]
            offering = _create_offering(
                provider, offering_data, 0 if maximum is None else maximum + 1
            )
            _touch_provider(provider)
            publication = _create_publication(
                provider,
                ProviderPublication.Operation.UPDATE,
                submitted_payload,
                actor_id=actor_id,
            )
            _create_sync_event(
                publication, CatalogueSyncEvent.EntityType.OFFERING, offering.offering_id
            )
        return _result(
            publication,
            provider,
            [offering.offering_id],
            offering_id=offering.offering_id,
            etag=_entity_etag("offering", offering),
        )
    except LifecycleConflict:
        raise
    except IntegrityError as exc:
        try:
            if Offering.objects.filter(offering_id=offering_id).exists():
                raise LifecycleConflict("offering_already_exists") from exc
        except DatabaseError:
            pass
        raise LifecycleWriteError from exc
    except DatabaseError as exc:
        raise LifecycleWriteError from exc


def update_offering(
    offering_id,
    changes,
    submitted_payload,
    *,
    actor_id=None,
    expected_etag=None,
):
    try:
        with transaction.atomic():
            try:
                offering = (
                    Offering.objects.select_for_update()
                    .select_related("provider")
                    .get(offering_id=offering_id)
                )
            except Offering.DoesNotExist as exc:
                raise LifecycleNotFound("offering") from exc
            provider = Provider.objects.select_for_update().get(pk=offering.provider_id)
            _assert_expected_etag("offering", offering, expected_etag)

            complete = {
                "service_category": offering.service_category,
                "offering_name": changes.get("offering_name", offering.offering_name),
                "part_family": offering.part_family,
                "support_status": changes.get("support_status", offering.support_status),
                **{
                    field: deepcopy(changes.get(field, getattr(offering, field)))
                    for field in OFFERING_JSON_FIELDS
                },
            }
            validate_lifecycle_offering(complete)
            update_fields = []
            for field in OFFERING_MUTABLE_FIELDS:
                if field in changes:
                    setattr(offering, field, deepcopy(changes[field]))
                    update_fields.append(field)
            offering.updated_at = timezone.now()
            offering.save(update_fields=[*update_fields, "updated_at"])
            _touch_provider(provider)
            publication = _create_publication(
                provider,
                ProviderPublication.Operation.UPDATE,
                submitted_payload,
                actor_id=actor_id,
            )
            _create_sync_event(
                publication, CatalogueSyncEvent.EntityType.OFFERING, offering.offering_id
            )
        return _result(
            publication,
            provider,
            [offering.offering_id],
            offering_id=offering.offering_id,
            etag=_entity_etag("offering", offering),
        )
    except DatabaseError as exc:
        raise LifecycleWriteError from exc
