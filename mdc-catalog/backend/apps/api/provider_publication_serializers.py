from rest_framework import serializers

from apps.ontology.vocabularies import (
    CERTIFICATIONS,
    MATERIALS,
    PART_FAMILIES,
    PROCESSES,
    SERVICE_TYPES,
    get_vocabulary_values,
)
from apps.providers.validators import FORBIDDEN_ROUTE_KEYS


ALLOWED_SOURCE_TYPES = {
    "provider_confirmed",
    "machine_list",
    "curated",
    "public_web",
    "not_confirmed",
}

ALLOWED_CONFIDENCE_VALUES = {
    "declared",
    "curated",
    "inferred",
    "estimated",
    "unknown",
}

ALLOWED_PUBLICATION_STATUSES = {
    "draft",
    "published",
}

ALLOWED_QUALITY_STANDARDS = {
    "DIN",
    "ISO",
}


def validate_no_forbidden_route_fields(data: dict, *, location: str) -> None:
    """
    Reject route/machine/price fields in provider publication payloads.

    Provider publication is stricter than search:
    unsupported fields should not be stored accidentally.
    """
    if not isinstance(data, dict):
        return

    forbidden_fields = sorted(set(data.keys()) & FORBIDDEN_ROUTE_KEYS)

    if forbidden_fields:
        raise serializers.ValidationError(
            {
                "forbidden_fields": (
                    f"Unsupported v1 route/machine/price fields in {location}: "
                    f"{forbidden_fields}"
                )
            }
        )


def validate_provider_publication_raw_payload(data: dict) -> None:
    """
    Check forbidden v1 route/machine/price fields in the raw publication payload.

    This is done at the top-level serializer because nested DRF serializers do
    not always expose self.initial_data.
    """
    if not isinstance(data, dict):
        return

    validate_no_forbidden_route_fields(
        data,
        location="provider publication payload",
    )

    provider = data.get("provider")
    if isinstance(provider, dict):
        validate_no_forbidden_route_fields(
            provider,
            location="provider",
        )

    offerings = data.get("offerings")
    if isinstance(offerings, list):
        for index, offering in enumerate(offerings):
            if not isinstance(offering, dict):
                continue

            offering_id = offering.get("offering_id", f"index {index}")

            validate_no_forbidden_route_fields(
                offering,
                location=f"offering {offering_id}",
            )

            capabilities = offering.get("capabilities")
            if isinstance(capabilities, dict):
                validate_no_forbidden_route_fields(
                    capabilities,
                    location=f"offering {offering_id} capabilities",
                )


class FacilityPublicationSerializer(serializers.Serializer):
    facility_id = serializers.SlugField(required=True)
    city = serializers.CharField(required=True, max_length=120)
    country = serializers.CharField(required=True, max_length=120)


class CertificationPublicationSerializer(serializers.Serializer):
    code = serializers.ChoiceField(
        choices=sorted(get_vocabulary_values(CERTIFICATIONS)),
        required=True,
    )
    label = serializers.CharField(required=False, allow_blank=True, max_length=200)


class ProviderPublicationInfoSerializer(serializers.Serializer):
    provider_id = serializers.SlugField(required=True)
    legal_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    display_name = serializers.CharField(required=True, max_length=255)
    provider_type = serializers.CharField(default="MaaSProvider", max_length=120)
    country = serializers.CharField(required=True, max_length=120)
    facilities = FacilityPublicationSerializer(many=True, required=False, default=list)
    certifications = CertificationPublicationSerializer(
        many=True,
        required=False,
        default=list,
    )


class MaterialGradePublicationSerializer(serializers.Serializer):
    grade_id = serializers.CharField(required=True, max_length=120)
    label = serializers.CharField(required=False, allow_blank=True, max_length=200)
    material_id = serializers.ChoiceField(
        choices=sorted(get_vocabulary_values(MATERIALS)),
        required=True,
    )


class NumericRangeSerializer(serializers.Serializer):
    min = serializers.FloatField(required=False, allow_null=True)
    max = serializers.FloatField(required=False, allow_null=True)

    def validate(self, attrs):
        min_value = attrs.get("min")
        max_value = attrs.get("max")

        if min_value is not None and min_value <= 0:
            raise serializers.ValidationError({"min": "Must be positive."})

        if max_value is not None and max_value <= 0:
            raise serializers.ValidationError({"max": "Must be positive."})

        if min_value is not None and max_value is not None and min_value > max_value:
            raise serializers.ValidationError("min must be less than or equal to max.")

        return attrs


class BatchSizeCapabilitySerializer(serializers.Serializer):
    min = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    max = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    unit = serializers.CharField(required=False, default="pcs", max_length=20)

    def validate(self, attrs):
        min_value = attrs.get("min")
        max_value = attrs.get("max")

        if min_value is not None and max_value is not None and min_value > max_value:
            raise serializers.ValidationError("min must be less than or equal to max.")

        return attrs


class WeightCapabilitySerializer(serializers.Serializer):
    max = serializers.FloatField(required=False, allow_null=True)
    approximate = serializers.BooleanField(required=False, allow_null=True)

    def validate_max(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Must be positive.")
        return value


class DiametralPitchCapabilitySerializer(serializers.Serializer):
    min = serializers.FloatField(required=False, allow_null=True)
    max = serializers.FloatField(required=False, allow_null=True)
    raw = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    normalized_order = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    def validate(self, attrs):
        min_value = attrs.get("min")
        max_value = attrs.get("max")

        if min_value is not None and min_value <= 0:
            raise serializers.ValidationError({"min": "Must be positive."})

        if max_value is not None and max_value <= 0:
            raise serializers.ValidationError({"max": "Must be positive."})

        if min_value is not None and max_value is not None and min_value > max_value:
            raise serializers.ValidationError("min must be less than or equal to max.")

        return attrs


class QualityCapabilitySerializer(serializers.Serializer):
    standard = serializers.ChoiceField(
        choices=sorted(ALLOWED_QUALITY_STANDARDS),
        required=False,
        allow_null=True,
    )
    best_class = serializers.FloatField(required=False, allow_null=True)
    comparison_rule = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    def validate_best_class(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Must be positive.")
        return value


class LeadTimeCapabilitySerializer(serializers.Serializer):
    min = serializers.FloatField(required=False, allow_null=True)
    max = serializers.FloatField(required=False, allow_null=True)
    qualifier = serializers.CharField(required=False, allow_blank=True, max_length=120)

    def validate(self, attrs):
        min_value = attrs.get("min")
        max_value = attrs.get("max")

        if min_value is not None and min_value <= 0:
            raise serializers.ValidationError({"min": "Must be positive."})

        if max_value is not None and max_value <= 0:
            raise serializers.ValidationError({"max": "Must be positive."})

        if min_value is not None and max_value is not None and min_value > max_value:
            raise serializers.ValidationError("min must be less than or equal to max.")

        return attrs


class SurfaceFinishCapabilitySerializer(serializers.Serializer):
    max = serializers.FloatField(required=False, allow_null=True)

    def validate_max(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Must be positive.")
        return value


class ToleranceCapabilitySerializer(serializers.Serializer):
    min = serializers.FloatField(required=False, allow_null=True)

    def validate_min(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Must be positive.")
        return value


class TraceabilityCapabilitySerializer(serializers.Serializer):
    aerospace_traceability = serializers.BooleanField(required=False, allow_null=True)
    full_traceability = serializers.BooleanField(required=False, allow_null=True)


class OfferingCapabilitiesPublicationSerializer(serializers.Serializer):
    batch_size = BatchSizeCapabilitySerializer(required=False, default=dict)
    diameter_mm = NumericRangeSerializer(required=False, default=dict)
    weight_kg = WeightCapabilitySerializer(required=False, default=dict)
    module = NumericRangeSerializer(required=False, default=dict)
    diametral_pitch = DiametralPitchCapabilitySerializer(required=False, default=dict)
    quality = QualityCapabilitySerializer(required=False, default=dict)
    lead_time_weeks = LeadTimeCapabilitySerializer(required=False, default=dict)
    surface_finish_ra_um = SurfaceFinishCapabilitySerializer(
        required=False,
        default=dict,
    )
    tolerance_mm = ToleranceCapabilitySerializer(required=False, default=dict)
    traceability = TraceabilityCapabilitySerializer(required=False, default=dict)


class OfferingPublicationSerializer(serializers.Serializer):
    offering_id = serializers.SlugField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    service_type = serializers.ChoiceField(
        choices=sorted(get_vocabulary_values(SERVICE_TYPES)),
        required=True,
    )
    part_families = serializers.ListField(
        child=serializers.ChoiceField(
            choices=sorted(get_vocabulary_values(PART_FAMILIES))
        ),
        required=True,
        allow_empty=False,
    )
    processes = serializers.ListField(
        child=serializers.ChoiceField(choices=sorted(get_vocabulary_values(PROCESSES))),
        required=True,
        allow_empty=False,
    )
    supported_materials = serializers.ListField(
        child=serializers.ChoiceField(choices=sorted(get_vocabulary_values(MATERIALS))),
        required=True,
        allow_empty=False,
    )
    supported_material_grades = MaterialGradePublicationSerializer(
        many=True,
        required=False,
        default=list,
    )
    capabilities = OfferingCapabilitiesPublicationSerializer(required=True)
    notes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )

    def validate(self, attrs):
        supported_materials = set(attrs.get("supported_materials", []))

        for grade in attrs.get("supported_material_grades", []):
            material_id = grade["material_id"]
            if material_id not in supported_materials:
                raise serializers.ValidationError(
                    {
                        "supported_material_grades": (
                            f"Material grade {grade['grade_id']} uses material_id "
                            f"{material_id}, but that material is not listed in "
                            "supported_materials."
                        )
                    }
                )

        return attrs


class PublicationMetadataSerializer(serializers.Serializer):
    source_type = serializers.ChoiceField(
        choices=sorted(ALLOWED_SOURCE_TYPES),
        default="provider_confirmed",
    )
    confidence = serializers.ChoiceField(
        choices=sorted(ALLOWED_CONFIDENCE_VALUES),
        default="declared",
    )
    status = serializers.ChoiceField(
        choices=sorted(ALLOWED_PUBLICATION_STATUSES),
        default="draft",
    )


class ProviderPublicationSerializer(serializers.Serializer):
    provider = ProviderPublicationInfoSerializer(required=True)
    offerings = OfferingPublicationSerializer(
        many=True,
        required=True,
        allow_empty=False,
    )
    publication_metadata = PublicationMetadataSerializer(required=False)

    def validate(self, attrs):
        validate_provider_publication_raw_payload(
            getattr(self, "initial_data", {})
        )

        provider_id = attrs["provider"]["provider_id"]

        offering_ids = []
        for offering in attrs["offerings"]:
            offering_ids.append(offering["offering_id"])

        duplicate_offering_ids = sorted(
            {
                offering_id
                for offering_id in offering_ids
                if offering_ids.count(offering_id) > 1
            }
        )

        if duplicate_offering_ids:
            raise serializers.ValidationError(
                {"offerings": f"Duplicate offering_id values: {duplicate_offering_ids}"}
            )

        for offering in attrs["offerings"]:
            expected_prefix = f"{provider_id}_"
            if not offering["offering_id"].startswith(expected_prefix):
                raise serializers.ValidationError(
                    {
                        "offerings": (
                            f"Offering ID '{offering['offering_id']}' should start "
                            f"with provider_id prefix '{expected_prefix}'."
                        )
                    }
                )

        return attrs