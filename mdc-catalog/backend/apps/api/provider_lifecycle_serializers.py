"""Strict request serializers for M7.4 partial lifecycle writes."""

from rest_framework import serializers

from apps.api.service_discovery_publication_serializers import (
    _reject_externally_owned_identifiers,
    _reject_forbidden_fields,
    _validate_json_safety,
    validate_provider_certifications,
    validate_publication_metadata,
)
from apps.providers.models import Offering, Provider


class StrictPartialSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("The request payload must be an object.")
        unsupported = set(data) - set(self.fields)
        if unsupported:
            raise serializers.ValidationError(
                {"unsupported_fields": sorted(unsupported)}
            )
        _reject_forbidden_fields(data)
        _reject_externally_owned_identifiers(data)
        _validate_json_safety(data)
        return super().to_internal_value(data)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("At least one editable field is required.")
        return attrs


class ProviderPatchSerializer(StrictPartialSerializer):
    provider_name = serializers.CharField(required=False, max_length=255)
    country = serializers.CharField(required=False, max_length=100)
    status = serializers.ChoiceField(required=False, choices=Provider.Status.values)
    certifications = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    publication_metadata = serializers.DictField(required=False)
    custom_provider_fields = serializers.DictField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if "certifications" in attrs:
            validate_provider_certifications(attrs["certifications"])
        if "publication_metadata" in attrs:
            validate_publication_metadata(attrs["publication_metadata"])
        return attrs


class OfferingCreateSerializer(StrictPartialSerializer):
    service_category = serializers.CharField(max_length=255)
    offering_name = serializers.CharField(max_length=255)
    part_family = serializers.CharField(max_length=255)
    support_status = serializers.ChoiceField(choices=Offering.SupportStatus.values)
    supported_part_types = serializers.ListField(
        child=serializers.DictField(), required=False, default=list
    )
    family_capabilities = serializers.DictField(required=False, default=dict)
    part_type_capabilities = serializers.DictField(required=False, default=dict)
    generic_capabilities = serializers.DictField(required=False, default=dict)
    custom_offering_fields = serializers.DictField(required=False, default=dict)
    custom_capability_fields = serializers.DictField(required=False, default=dict)


class OfferingPatchSerializer(StrictPartialSerializer):
    offering_name = serializers.CharField(required=False, max_length=255)
    support_status = serializers.ChoiceField(
        required=False, choices=Offering.SupportStatus.values
    )
    supported_part_types = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    family_capabilities = serializers.DictField(required=False)
    part_type_capabilities = serializers.DictField(required=False)
    generic_capabilities = serializers.DictField(required=False)
    custom_offering_fields = serializers.DictField(required=False)
    custom_capability_fields = serializers.DictField(required=False)
    is_active = serializers.BooleanField(required=False)
