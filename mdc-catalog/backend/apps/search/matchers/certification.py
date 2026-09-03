from typing import Any

from apps.search.matchers.common import evaluate_list_optional_match


def extract_provider_certifications(provider: dict[str, Any]) -> list[str]:
    """
    Extract certification codes from provider.certifications.
    """
    certifications = []

    for certification in provider.get("certifications", []):
        if not isinstance(certification, dict):
            continue

        code = certification.get("code")
        if isinstance(code, str):
            certifications.append(code)

    return sorted(set(certifications))


def evaluate_certification_optional_match(
    *,
    requested_certifications: list[str],
    provider: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Evaluate requested certifications against provider certifications.
    """
    return evaluate_list_optional_match(
        field="certifications",
        requested_values=requested_certifications,
        provided_values=extract_provider_certifications(provider),
        unknown_reason="No confirmed certification data is available for this provider.",
    )

