"""Orchestrates read-only switch discovery commands.

This service owns workflow state, but delegates transport to SerialSession and
parsing to IdentityParser/LLDP parser. Results are published through EventBus.
"""

from enum import Enum, auto

from app.core import event_names as events
from app.domain.models import DiscoveryResult
from .lldp import parse as parse_lldp


class DiscoveryMode(Enum):
    """Active command workflow."""

    IDLE = auto()
    FULL = auto()
    LLDP_ONLY = auto()


class DiscoveryService:
    """Coordinate serial commands and publish structured discovery results."""

    FULL_DISCOVERY_COMMANDS = (
        ("version", "show version", 2200),
        ("eeprom", "show platform syseeprom", 2600),
        ("lldp", "show lldp neighbors", 2800),
    )

    def __init__(self, session, parser, bus):
        self.session = session
        self.parser = parser
        self.bus = bus
        self.mode = DiscoveryMode.IDLE
        self.command_queue = []
        self.outputs = {}

        session.console.connect(
            lambda text: bus.publish(events.CONSOLE_RECEIVED, text=text)
        )
        session.event.connect(self._on_serial_event)

    def ports(self):
        """Return currently available system serial ports."""
        return self.session.available_ports()

    def connect(self, port, baud):
        """Open a serial connection using the requested settings."""
        return self.session.open(port, baud)

    def disconnect(self):
        """Close the current serial connection."""
        self.session.close()

    def discover(self):
        """Start the complete read-only identity and LLDP workflow."""
        if self.mode is not DiscoveryMode.IDLE:
            self.bus.publish(events.SERIAL_BLOCKED, reason="Discovery already running")
            return

        self.mode = DiscoveryMode.FULL
        self.outputs = {}
        self.command_queue = list(self.FULL_DISCOVERY_COMMANDS)
        self.bus.publish(events.DISCOVERY_STARTED)
        self._run_next_command()

    def lldp_only(self):
        """Collect and parse LLDP without starting a full identity workflow."""
        if self.mode is not DiscoveryMode.IDLE:
            self.bus.publish(events.SERIAL_BLOCKED, reason="Discovery already running")
            return

        self.mode = DiscoveryMode.LLDP_ONLY
        self.outputs = {}
        self.session.run("lldp", "show lldp neighbors", 2800)

    def _run_next_command(self):
        if self.command_queue:
            self.session.run(*self.command_queue.pop(0))
            return
        self._complete_full_discovery()

    def _complete_full_discovery(self):
        result = DiscoveryResult(
            identity=self.parser.parse(self.outputs),
            neighbors=parse_lldp(self.outputs.get("lldp", "")),
            raw_outputs=dict(self.outputs),
        )
        self.mode = DiscoveryMode.IDLE
        self.bus.publish(events.DISCOVERY_COMPLETED, result=result)

    def _complete_lldp(self, output):
        neighbors = parse_lldp(output)
        self.mode = DiscoveryMode.IDLE
        self.bus.publish(events.LLDP_COMPLETED, neighbors=neighbors, raw_output=output)

    def _on_serial_event(self, name, payload):
        """Forward transport events and advance the active workflow."""
        self.bus.publish(name, **payload)
        if name != events.SERIAL_COMMAND_FINISHED:
            return

        command_name = payload["name"]
        output = payload["output"]
        self.outputs[command_name] = output

        if self.mode is DiscoveryMode.LLDP_ONLY:
            self._complete_lldp(output)
            return

        if self.mode is DiscoveryMode.FULL:
            self.bus.publish(
                events.DISCOVERY_COMMAND_COMPLETED, command=command_name
            )
            self._run_next_command()
