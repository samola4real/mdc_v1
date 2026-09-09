"""Read-only provider lifecycle projections backed by Django persistence."""

from copy import deepcopy

from django.db.models import Prefetch

from apps.providers.models import Offering, Provider, ProviderCertification


def _certification_payload(certification):
    payload = {
        "code": certification.code,
        "source_type": certification.source_type,
        "confidence": certification.confidence,
    }
    if certification.source_note_present or certification.source_note is not None:
        payload["source_note"] = certification.source_note
    return payload


def _offering_summary(offering):
    return {
        "offering_id": offering.offering_id,
        "offering_name": offering.offering_name,
        "service_category": offering.service_category,
        "part_family": offering.part_family,
        "support_status": offering.support_status,
        "is_active": offering.is_active,
    }


def _offering_payload(offering):
    return {
        **_offering_summary(offering),
        "provider_id": offering.provider.provider_id,
        "supported_part_types": deepcopy(offering.supported_part_types),
        "family_capabilities": deepcopy(offering.family_capabilities),
        "part_type_capabilities": deepcopy(offering.part_type_capabilities),
        "generic_capabilities": deepcopy(offering.generic_capabilities),
        "custom_offering_fields": deepcopy(offering.custom_offering_fields),
        "custom_capability_fields": deepcopy(offering.custom_capability_fields),
    }


def get_provider_lifecycle(provider_id):
    """Return all lifecycle states, including draft providers and inactive offerings."""
    provider = (
        Provider.objects.filter(provider_id=provider_id)
        .prefetch_related(
            Prefetch(
                "certifications",
                queryset=ProviderCertification.objects.order_by("sequence_index", "code"),
                to_attr="lifecycle_certifications",
            ),
            Prefetch(
                "offerings",
                queryset=Offering.objects.order_by("sequence_index", "offering_id"),
                to_attr="lifecycle_offerings",
            ),
        )
        .first()
    )
    if provider is None:
        return None
    return {
        "provider_id": provider.provider_id,
        "provider_name": provider.provider_name,
        "country": provider.country,
        "status": provider.status,
        "custom_provider_fields": deepcopy(provider.custom_provider_fields),
        "publication_metadata": deepcopy(provider.publication_metadata),
        "certifications": [
            _certification_payload(certification)
            for certification in provider.lifecycle_certifications
        ],
        "offerings": [
            _offering_summary(offering) for offering in provider.lifecycle_offerings
        ],
    }


def list_provider_lifecycle_offerings(provider_id):
    """Return None for an unknown provider and an ordered list for a known provider."""
    provider = Provider.objects.filter(provider_id=provider_id).only("id").first()
    if provider is None:
        return None
    offerings = (
        Offering.objects.filter(provider=provider)
        .select_related("provider")
        .order_by("sequence_index", "offering_id")
    )
    return [_offering_payload(offering) for offering in offerings]


def get_offering_lifecycle(offering_id):
    offering = (
        Offering.objects.filter(offering_id=offering_id)
        .select_related("provider")
        .first()
    )
    return _offering_payload(offering) if offering is not None else None
