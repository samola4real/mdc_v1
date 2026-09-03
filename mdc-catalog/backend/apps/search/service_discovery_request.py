from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CanonicalServiceDiscoverySearchRequest:
    request_id: str
    consumer_id: str
    selection: dict[str, Any]
    requirements: dict[str, Any]
    match_policy: dict[str, Any]
    warnings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "consumer_id": self.consumer_id,
            "selection": self.selection,
            "requirements": self.requirements,
            "match_policy": self.match_policy,
            "warnings": self.warnings,
        }
