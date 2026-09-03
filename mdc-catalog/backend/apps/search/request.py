from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CanonicalSearchRequest:
    """
    Canonical internal representation of a consumer search request.

    Important design rule:
    primary_filters may contain multiple required search filters.

    Example:
    {
        "part_families": ["shaft"],
        "service_types": ["machining"]
    }

    In Phase E, we start with part_families as the first required primary filter.
    Later, more primary filters can be added without changing this dataclass.
    """

    primary_filters: dict[str, Any]
    optional_criteria: dict[str, Any] = field(default_factory=dict)
    match_policy: dict[str, Any] = field(default_factory=dict)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the dataclass to a plain dictionary.

        This is useful for tests, API responses, and future search code.
        """
        return {
            "primary_filters": self.primary_filters,
            "optional_criteria": self.optional_criteria,
            "match_policy": self.match_policy,
            "warnings": self.warnings,
        }