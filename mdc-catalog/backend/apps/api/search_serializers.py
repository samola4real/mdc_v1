from rest_framework import serializers

from apps.ontology.vocabularies import (
    CERTIFICATIONS,
    MATERIALS,
    MATERIAL_GRADES,
    PART_FAMILIES,
    PROCESSES,
    SERVICE_TYPES,
    get_vocabulary_values,
)
from apps.providers.validators import FORBIDDEN_ROUTE_KEYS


ALLOWED_QUALITY_STANDARDS = {
    "DIN",
    "ISO",
}

ALLOWED_UNKNOWN_POLICIES = {
    "keep_as_unknown",
    "reject_unknown",
}

ALLOWED_OPTIONAL_MATCH_MODES = {
    "any",
    "all",
    "score_only",
}

ALLOWED_PRIMARY_MATCH_MODES = {
    "any",
    "all",
}


def validate_no_unsupported_search_fields(data: dict) -> list[dict]:
    """
    Detect unsupported v1 route/machine/price fields.

    For consumer search we do not fail immediately.
    We collect warnings so the endpoint can return them in warnings[].
    """
    if not isinstance(data, dict):
        return []

    warnings = []
    unsupported_fields = sorted(set(data.keys()) & FORBIDDEN_ROUTE_KEYS)

    for field in unsupported_fields:
        warnings.append(
            {
                "field": field,
                "message": (
                    f"Field '{field}' is not supported in v1 search and will be ignored."
                ),
            }
        )

    return warnings


class PositiveRangeOrExactSerializer(serializers.Serializer):
    min = serializers.FloatField(required=False)
    max = serializers.FloatField(required=False)
    exact = serializers.FloatField(required=False)

    def validate(self, attrs):
        min_value = attrs.get("min")
        max_value = attrs.get("max")
        exact_value = attrs.get("exact")

        if min_value is not None and min_value <= 0:
            raise serializers.ValidationError({"min": "Must be positive."})

        if max_value is not None and max_value <= 0:
            raise serializers.ValidationError({"max": "Must be positive."})

        if exact_value is not None and exact_value <= 0:
            raise serializers.ValidationError({"exact": "Must be positive."})

        if min_value is not None and max_value is not None and min_value > max_value:
            raise serializers.ValidationError("min must be less than or equal to max.")

        if exact_value is not None:
            if min_value is not None and exact_value < min_value:
                raise serializers.ValidationError(
                    "exact must be greater than or equal to min."
                )

            if max_value is not None and exact_value > max_value:
                raise serializers.ValidationError(
                    "exact must be less than or equal to max."
                )

        return attrs


class PositiveRangeSerializer(serializers.Serializer):
    min = serializers.FloatField(required=False)
    max = serializers.FloatField(required=False)

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


class DiameterDimensionsSerializer(serializers.Serializer):
    diameter_mm = PositiveRangeOrExactSerializer(required=False)


class WeightSerializer(serializers.Serializer):
    max = serializers.FloatField(required=False)

    def validate_max(self, value):
        if value <= 0:
            raise serializers.ValidationError("Must be positive.")
        return value


class QualitySearchSerializer(serializers.Serializer):
    standard = serializers.ChoiceField(
        choices=sorted(ALLOWED_QUALITY_STANDARDS),
        required=False,
    )
    max_class = serializers.FloatField(required=False)

    def validate_max_class(self, value):
        if value <= 0:
            raise serializers.ValidationError("Must be positive.")
        return value


class GearParametersSerializer(serializers.Serializer):
    module = PositiveRangeSerializer(required=False)
    diametral_pitch = PositiveRangeSerializer(required=False)
    quality = QualitySearchSerializer(required=False)


class SurfaceFinishSerializer(serializers.Serializer):
    ra_um = PositiveRangeSerializer(required=False)


class DeliverySerializer(serializers.Serializer):
    max_weeks = serializers.FloatField(required=False)

    def validate_max_weeks(self, value):
        if value <= 0:
            raise serializers.ValidationError("Must be positive.")
        return value


class MatchPolicySerializer(serializers.Serializer):
    primary_match_mode = serializers.ChoiceField(
        choices=sorted(ALLOWED_PRIMARY_MATCH_MODES),
        required=False,
        default="any",
    )
    optional_match_mode = serializers.ChoiceField(
        choices=sorted(ALLOWED_OPTIONAL_MATCH_MODES),
        required=False,
        default="any",
    )
    unknown_policy = serializers.ChoiceField(
        choices=sorted(ALLOWED_UNKNOWN_POLICIES),
        required=False,
        default="keep_as_unknown",
    )
    minimum_score = serializers.FloatField(required=False, min_value=0, max_value=1)


class SearchRequestSerializer(serializers.Serializer):
    """
    Serializer for consumer catalogue search requests.

    Supports both:
    - part_family: "shaft"
    - part_families: ["shaft", "gear"]

    At least one of these must be provided.
    """

    service_type = serializers.ChoiceField(
        choices=sorted(get_vocabulary_values(SERVICE_TYPES)),
        required=False,
    )

    part_family = serializers.ChoiceField(
        choices=sorted(get_vocabulary_values(PART_FAMILIES)),
        required=False,
    )

    part_families = serializers.ListField(
        child=serializers.ChoiceField(
            choices=sorted(get_vocabulary_values(PART_FAMILIES))
        ),
        required=False,
        default=list,
        allow_empty=False,
    )

    materials = serializers.ListField(
        child=serializers.ChoiceField(choices=sorted(get_vocabulary_values(MATERIALS))),
        required=False,
        default=list,
    )

    material_grades = serializers.ListField(
        child=serializers.ChoiceField(
            choices=sorted(get_vocabulary_values(MATERIAL_GRADES))
        ),
        required=False,
        default=list,
    )

    processes = serializers.ListField(
        child=serializers.ChoiceField(choices=sorted(get_vocabulary_values(PROCESSES))),
        required=False,
        default=list,
    )

    dimensions = DiameterDimensionsSerializer(required=False, default=dict)
    weight_kg = WeightSerializer(required=False, default=dict)
    gear_parameters = GearParametersSerializer(required=False, default=dict)
    surface_finish = SurfaceFinishSerializer(required=False, default=dict)

    batch_size = serializers.IntegerField(required=False, min_value=1)

    delivery = DeliverySerializer(required=False, default=dict)

    certifications = serializers.ListField(
        child=serializers.ChoiceField(
            choices=sorted(get_vocabulary_values(CERTIFICATIONS))
        ),
        required=False,
        default=list,
    )

    traceability_required = serializers.BooleanField(required=False, default=False)

    industry = serializers.CharField(required=False, allow_blank=True)

    match_policy = MatchPolicySerializer(required=False, default=dict)

    def validate(self, attrs):
        """
        Store unsupported-field warnings and enforce that at least one
        part-family field is supplied.
        """
        self.unsupported_field_warnings = validate_no_unsupported_search_fields(
            getattr(self, "initial_data", {})
        )

        part_family = attrs.get("part_family")
        part_families = attrs.get("part_families", [])

        if not part_family and not part_families:
            raise serializers.ValidationError(
                {
                    "part_family": "Provide either 'part_family' or 'part_families'.",
                    "part_families": "Provide either 'part_family' or 'part_families'.",
                }
            )

        return attrs