"""Headless presentation tests: run without PySide6."""

import pytest
from app.domain.models import ReadinessResult, RuleResult
from app.readiness.presenter import ReadinessPresenter


def ready_result():
    return ReadinessResult(
        ready=True,
        status="READY",
        checks=[
            RuleResult("inventory", "PASS"),
            RuleResult("discovery", "PASS"),
            RuleResult("sku_model", "PASS"),
            RuleResult("lldp", "PASS"),
            RuleResult("profile", "PASS"),
        ],
    )


def blocked_result(code="SKU-001"):
    return ReadinessResult(
        ready=False,
        status="BLOCKED",
        checks=[
            RuleResult("inventory", "PASS"),
            RuleResult("sku_model", "FAIL", code, "Expected SN4700, found SN2700"),
        ],
        blockers=[code],
    )


@pytest.mark.presenter
def test_ready_view_enables_action():
    view = ReadinessPresenter().present(ready_result())
    assert view.headline == "Ready to provision"
    assert view.action_enabled is True
    assert all(check.status_text == "Verified" for check in view.checks)


@pytest.mark.presenter
def test_blocked_view_disables_action():
    view = ReadinessPresenter().present(blocked_result())
    assert view.headline == "Provisioning blocked"
    assert view.action_enabled is False


@pytest.mark.presenter
def test_technician_view_uses_friendly_message():
    view = ReadinessPresenter().present(blocked_result())
    assert view.user_messages == [
        "The detected hardware does not match this rack configuration."
    ]


@pytest.mark.presenter
def test_technician_view_hides_internal_code_and_detail():
    view = ReadinessPresenter().present(blocked_result(), engineer_mode=False)
    failed = view.checks[1]
    assert failed.technical_code == ""
    assert failed.technical_message == ""
    assert "SKU-001" not in " ".join(view.user_messages)


@pytest.mark.presenter
def test_engineer_view_exposes_code_and_detail():
    view = ReadinessPresenter().present(blocked_result(), engineer_mode=True)
    failed = view.checks[1]
    assert view.engineer_details_visible is True
    assert failed.technical_code == "SKU-001"
    assert failed.technical_message == "Expected SN4700, found SN2700"


@pytest.mark.presenter
@pytest.mark.parametrize(
    "code,expected",
    [
        ("DISC-001", "The switch could not be identified completely."),
        ("INV-001", "Inventory information could not be verified."),
        ("LLDP-001", "Required network connections were not detected."),
        ("PROF-001", "The required switch configuration is unavailable."),
    ],
)
def test_each_block_code_has_friendly_text(code, expected):
    assert ReadinessPresenter().present(blocked_result(code)).user_messages == [expected]


@pytest.mark.presenter
def test_unknown_code_has_safe_generic_text():
    view = ReadinessPresenter().present(blocked_result("NEW-999"))
    assert view.user_messages == ["A required safety check did not pass."]
