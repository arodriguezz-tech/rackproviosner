"""PySide6 readiness panel.

The panel subscribes to readiness.evaluated and renders user-friendly outcomes.
It never calculates readiness and never displays switch commands.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core import event_names as events
from app.readiness.presenter import ReadinessPresenter


class ReadinessPanel(QWidget):
    """Display readiness and control the provisioning action button."""

    def __init__(self, event_bus, engineer_mode: bool = False, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.engineer_mode = engineer_mode
        self.presenter = ReadinessPresenter()
        self._build_ui()
        self._show_waiting_state()
        event_bus.subscribe(events.READINESS_EVALUATED, self._on_readiness_evaluated)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(12)

        header = QFrame()
        header_layout = QVBoxLayout(header)
        self.headline_label = QLabel()
        self.headline_label.setObjectName("readinessHeadline")
        self.headline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.headline_label)
        header_layout.addWidget(self.summary_label)
        root.addWidget(header)

        checks_group = QGroupBox("Safety checks")
        checks_layout = QVBoxLayout(checks_group)
        self.checks_table = QTableWidget(0, 2)
        self.checks_table.setHorizontalHeaderLabels(["Check", "Status"])
        self.checks_table.verticalHeader().setVisible(False)
        self.checks_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.checks_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        checks_layout.addWidget(self.checks_table)
        root.addWidget(checks_group)

        self.message_group = QGroupBox("What needs attention")
        message_layout = QVBoxLayout(self.message_group)
        self.message_list = QListWidget()
        message_layout.addWidget(self.message_list)
        root.addWidget(self.message_group)

        self.engineer_group = QGroupBox("Engineer details")
        engineer_layout = QVBoxLayout(self.engineer_group)
        self.engineer_table = QTableWidget(0, 3)
        self.engineer_table.setHorizontalHeaderLabels(["Check", "Code", "Technical detail"])
        self.engineer_table.verticalHeader().setVisible(False)
        self.engineer_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        engineer_layout.addWidget(self.engineer_table)
        root.addWidget(self.engineer_group)

        actions = QHBoxLayout()
        actions.addStretch()
        self.provision_button = QPushButton("Start provisioning")
        self.provision_button.setObjectName("startProvisioningButton")
        actions.addWidget(self.provision_button)
        root.addLayout(actions)

    def set_engineer_mode(self, enabled: bool) -> None:
        self.engineer_mode = enabled
        self.engineer_group.setVisible(enabled)

    def _show_waiting_state(self) -> None:
        self.headline_label.setText("Waiting for safety checks")
        self.summary_label.setText("Connect and identify the switch to continue.")
        self.provision_button.setEnabled(False)
        self.message_group.setVisible(False)
        self.engineer_group.setVisible(self.engineer_mode)

    def _on_readiness_evaluated(self, event) -> None:
        self.render(event.payload["result"])

    def render(self, result) -> None:
        view = self.presenter.present(result, self.engineer_mode)
        self.headline_label.setText(view.headline)
        self.summary_label.setText(view.summary)
        self.provision_button.setEnabled(view.action_enabled)

        self.checks_table.setRowCount(len(view.checks))
        for row, check in enumerate(view.checks):
            self.checks_table.setItem(row, 0, QTableWidgetItem(check.label))
            self.checks_table.setItem(row, 1, QTableWidgetItem(check.status_text))

        self.message_list.clear()
        self.message_list.addItems(view.user_messages)
        self.message_group.setVisible(bool(view.user_messages))

        self.engineer_table.setRowCount(len(view.checks))
        for row, check in enumerate(view.checks):
            self.engineer_table.setItem(row, 0, QTableWidgetItem(check.key))
            self.engineer_table.setItem(row, 1, QTableWidgetItem(check.technical_code))
            self.engineer_table.setItem(row, 2, QTableWidgetItem(check.technical_message))
        self.engineer_group.setVisible(view.engineer_details_visible)
