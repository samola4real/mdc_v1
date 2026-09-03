from typing import Any

from apps.search.matchers.common import evaluate_scalar_optional_match


def evaluate_service_type_optional_match(
    *,
    requested_service_type: Any,
    provided_service_type: Any,
) -> dict[str, Any] | None:
    """
    Evaluate service type as optional scoring criteria.
    """
    return evaluate_scalar_optional_match(
        field="service_type",
        requested_value=requested_service_type,
        provided_value=provided_service_type,
        unknown_reason="Service type is not confirmed for this offering.",
    )
