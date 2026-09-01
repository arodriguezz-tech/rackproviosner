"""Convert ReadinessResult into a UI-safe view model.

This presenter is intentionally independent of Qt. It can be fully tested in a
headless environment and guarantees that Technician Mode never displays raw
commands, event names, or internal error codes.
"""

from dataclasses import dataclass, field
from app.domain.models import ReadinessResult
from .messages import BLOCK_MESSAGES, CHECK_LABELS, STATUS_LABELS


@dataclass(frozen=True)
class CheckView:
    key: str
    label: str
    status: str
    status_text: str
    technical_code: str = ""
    technical_message: str = ""


@dataclass(frozen=True)
class ReadinessViewModel:
    headline: str
    summary: str
    ready: bool
    action_enabled: bool
    checks: list[CheckView] = field(default_factory=list)
    user_messages: list[str] = field(default_factory=list)
    engineer_details_visible: bool = False


class ReadinessPresenter:
    """Build technician or engineer views from one authoritative result."""

    def present(self, result: ReadinessResult, engineer_mode: bool = False) -> ReadinessViewModel:
        checks = []
        for rule in result.checks:
            checks.append(
                CheckView(
                    key=rule.name,
                    label=CHECK_LABELS.get(rule.name, "System check"),
                    status=rule.status,
                    status_text=STATUS_LABELS.get(rule.status, rule.status.title()),
                    technical_code=rule.code if engineer_mode else "",
                    technical_message=rule.message if engineer_mode else "",
                )
            )

        messages = [BLOCK_MESSAGES.get(code, "A required safety check did not pass.")
                    for code in result.blockers]
        if not messages and result.warnings:
            messages = [BLOCK_MESSAGES.get(code, "A safety check needs review.")
                        for code in result.warnings]

        if result.ready:
            headline = "Ready to provision"
            summary = "All required safety checks passed."
        else:
            headline = "Provisioning blocked"
            summary = "Resolve the items below before continuing."

        return ReadinessViewModel(
            headline=headline,
            summary=summary,
            ready=result.ready,
            action_enabled=result.ready,
            checks=checks,
            user_messages=messages,
            engineer_details_visible=engineer_mode,
        )
