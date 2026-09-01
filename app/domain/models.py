from dataclasses import dataclass, field

@dataclass
class DeviceIdentity:
    serial: str=""; mac: str=""; model: str=""; role: str|None=None
@dataclass
class LldpNeighbor:
    local_port: str; neighbor_mac: str=""; neighbor_name: str=""; neighbor_ip: str=""; neighbor_port: str=""
@dataclass
class DiscoveryResult:
    identity: DeviceIdentity; neighbors: list[LldpNeighbor]=field(default_factory=list); raw_outputs: dict[str,str]=field(default_factory=dict)
