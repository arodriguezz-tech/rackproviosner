"""pytest-qt widget tests.

These tests run when PySide6 and pytest-qt are installed. They are skipped in a
headless environment that lacks those optional dependencies.
"""

import pytest

pytest.importorskip("PySide6")
pytest.importorskip("pytestqt")

from app.core import event_names as events
from app.core.events import EventBus
from app.domain.models import ReadinessResult, RuleResult
from app.ui.readiness_panel import ReadinessPanel


def result(ready=True):
    return ReadinessResult(
        ready=ready,
        status="READY" if ready else "BLOCKED",
        checks=[
            RuleResult("inventory", "PASS"),
            RuleResult(
                "sku_model",
                "PASS" if ready else "FAIL",
                "" if ready else "SKU-001",
                "" if ready else "Expected SN4700, found SN2700",
            ),
        ],
        blockers=[] if ready else ["SKU-001"],
    )


@pytest.mark.ui
def test_initial_state_is_safe_and_disabled(qtbot):
    panel = ReadinessPanel(EventBus())
    qtbot.addWidget(panel)
    assert panel.headline_label.text() == "Waiting for safety checks"
    assert not panel.provision_button.isEnabled()


@pytest.mark.ui
def test_ready_event_enables_button(qtbot):
    bus = EventBus()
    panel = ReadinessPanel(bus)
    qtbot.addWidget(panel)
    bus.publish(events.READINESS_EVALUATED, result=result(True))
    assert panel.headline_label.text() == "Ready to provision"
    assert panel.provision_button.isEnabled()
    assert panel.checks_table.rowCount() == 2


@pytest.mark.ui
def test_blocked_event_disables_button_and_shows_friendly_message(qtbot):
    bus = EventBus()
    panel = ReadinessPanel(bus)
    qtbot.addWidget(panel)
    bus.publish(events.READINESS_EVALUATED, result=result(False))
    assert panel.headline_label.text() == "Provisioning blocked"
    assert not panel.provision_button.isEnabled()
    assert panel.message_list.item(0).text() == (
        "The detected hardware does not match this rack configuration."
    )


@pytest.mark.ui
def test_technician_mode_hides_engineer_details(qtbot):
    panel = ReadinessPanel(EventBus(), engineer_mode=False)
    qtbot.addWidget(panel)
    panel.render(result(False))
    assert not panel.engineer_group.isVisible()


@pytest.mark.ui
def test_engineer_mode_shows_codes_and_details(qtbot):
    panel = ReadinessPanel(EventBus(), engineer_mode=True)
    qtbot.addWidget(panel)
    panel.show()
    panel.render(result(False))
    assert panel.engineer_group.isVisible()
    assert panel.engineer_table.item(1, 1).text() == "SKU-001"
    assert "Expected SN4700" in panel.engineer_table.item(1, 2).text()
