"""Data-only readiness models shared by the service, presenter, and UI."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RuleResult:
    name: str
    status: str
    code: str = ""
    message: str = ""


@dataclass(frozen=True)
class ReadinessResult:
    ready: bool
    status: str
    checks: list[RuleResult]
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
