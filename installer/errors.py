"""Fail-closed, report-safe installer errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InstallerError(RuntimeError):
    message: str
    code: str = "INSTALLER_ERROR"
    resource_type: str | None = None
    candidates: list[dict[str, Any]] = field(default_factory=list)
    action: str | None = None
    config_key: str | None = None
    retry_safe: bool = True

    def __post_init__(self) -> None:
        RuntimeError.__init__(self, self.message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "BLOCKED",
            "code": self.code,
            "message": self.message,
            "unresolved_resource_type": self.resource_type,
            "candidates": self.candidates,
            "configuration_key": self.config_key,
            "required_action": self.action,
            "retry_safe": self.retry_safe,
        }
