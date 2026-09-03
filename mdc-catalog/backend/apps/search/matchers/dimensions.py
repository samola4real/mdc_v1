from typing import Any

from apps.search.matchers.common import (
    evaluate_max_value_optional_match,
    evaluate_numeric_range_optional_match,
)
from apps.search.request import CanonicalSearchRequest


def extract_capability(offering: dict[str, Any], capability_name: str) -> dict[str, Any]:
    """
    Extract one capability dictionary from offering.capabilities.
    """
    capabilities = offering.get("capabilities", {})

    if not isinstance(capabilities, dict):
        return {}

    capability = capabilities.get(capability_name, {})

    if not isinstance(capability, dict):
        return {}

    return capability


def extract_requested_diameter(
    canonical_request: CanonicalSearchRequest,
) -> dict[str, Any]:
    """
    Extract requested diameter from canonical optional criteria.
    """
    dimensions = canonical_request.optional_criteria.get("dimensions", {})

    if not isinstance(dimensions, dict):
        return {}

    diameter = dimensions.get("diameter_mm", {})

    if not isinstance(diameter, dict):
        return {}

    return diameter


def extract_requested_module(
    canonical_request: CanonicalSearchRequest,
) -> dict[str, Any]:
    """
    Extract requested gear module from canonical optional criteria.
    """
    gear_parameters = canonical_request.optional_criteria.get("gear_parameters", {})

    if not isinstance(gear_parameters, dict):
        return {}

    module = gear_parameters.get("module", {})

    if not isinstance(module, dict):
        return {}

    return module


def extract_requested_diametral_pitch(
    canonical_request: CanonicalSearchRequest,
) -> dict[str, Any]:
    """
    Extract requested diametral pitch from canonical optional criteria.
    """
    gear_parameters = canonical_request.optional_criteria.get("gear_parameters", {})

    if not isinstance(gear_parameters, dict):
        return {}

    diametral_pitch = gear_parameters.get("diametral_pitch", {})

    if not isinstance(diametral_pitch, dict):
        return {}

    return diametral_pitch


def extract_requested_surface_finish(
    canonical_request: CanonicalSearchRequest,
) -> dict[str, Any]:
    """
    Extract requested surface finish from canonical optional criteria.
    """
    surface_finish = canonical_request.optional_criteria.get("surface_finish", {})

    if not isinstance(surface_finish, dict):
        return {}

    ra_um = surface_finish.get("ra_um", {})

    if not isinstance(ra_um, dict):
        return {}

    return ra_um


def evaluate_diameter_optional_match(
    *,
    canonical_request: CanonicalSearchRequest,
    offering: dict[str, Any],
) -> dict[str, Any] | None:
    return evaluate_numeric_range_optional_match(
        field="diameter_mm",
        requested_range=extract_requested_diameter(canonical_request),
        provided_range=extract_capability(offering, "diameter_mm"),
        unknown_reason="No confirmed diameter range is available for this offering.",
    )


def evaluate_weight_optional_match(
    *,
    requested_weight: dict[str, Any],
    offering: dict[str, Any],
) -> dict[str, Any] | None:
    requested_max = requested_weight.get("max") if isinstance(requested_weight, dict) else None

    return evaluate_max_value_optional_match(
        field="weight_kg",
        requested_max=requested_max,
        provided_max=extract_capability(offering, "weight_kg").get("max"),
        unknown_reason="No confirmed weight capability is available for this offering.",
    )


def evaluate_module_optional_match(
    *,
    canonical_request: CanonicalSearchRequest,
    offering: dict[str, Any],
) -> dict[str, Any] | None:
    return evaluate_numeric_range_optional_match(
        field="module",
        requested_range=extract_requested_module(canonical_request),
        provided_range=extract_capability(offering, "module"),
        unknown_reason="No confirmed module range is available for this offering.",
    )


def evaluate_diametral_pitch_optional_match(
    *,
    canonical_request: CanonicalSearchRequest,
    offering: dict[str, Any],
) -> dict[str, Any] | None:
    return evaluate_numeric_range_optional_match(
        field="diametral_pitch",
        requested_range=extract_requested_diametral_pitch(canonical_request),
        provided_range=extract_capability(offering, "diametral_pitch"),
        unknown_reason="No confirmed diametral pitch range is available for this offering.",
    )


def evaluate_surface_finish_optional_match(
    *,
    canonical_request: CanonicalSearchRequest,
    offering: dict[str, Any],
) -> dict[str, Any] | None:
    surface_finish_request = extract_requested_surface_finish(canonical_request)

    return evaluate_max_value_optional_match(
        field="surface_finish.ra_um",
        requested_max=surface_finish_request.get("max"),
        provided_max=extract_capability(offering, "surface_finish_ra_um").get("max"),
        unknown_reason="No confirmed surface finish value is available for this offering.",
    )
