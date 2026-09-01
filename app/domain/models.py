"""Shared domain models.

Dataclasses in this module contain data only. They must not access SQLite, Qt
widgets, serial ports, or settings.
"""

from dataclasses import dataclass, field


@dataclass
class DeviceIdentity:
    """Identity values discovered directly from one switch."""

    serial: str = ""
    mac: str = ""
    model: str = ""
    role: str | None = None


@dataclass
class LldpNeighbor:
    """One normalized LLDP neighbor relationship."""

    local_port: str
    neighbor_mac: str = ""
    neighbor_name: str = ""
    neighbor_ip: str = ""
    neighbor_port: str = ""


@dataclass
class DiscoveryResult:
    """Complete output of a full switch discovery workflow."""

    identity: DeviceIdentity
    neighbors: list[LldpNeighbor] = field(default_factory=list)
    raw_outputs: dict[str, str] = field(default_factory=dict)
