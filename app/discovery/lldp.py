"""Parser for human-readable SONiC `show lldp neighbors` output."""
import re
from app.domain.models import LldpNeighbor
from app.inventory.repository import normalize_mac

def parse(text: str) -> list[LldpNeighbor]:
    patterns = {
        "local_port": re.compile(r"^\s*Interface:\s*([^,\s]+)", re.I),
        "neighbor_mac": re.compile(r"^\s*ChassisID:\s*mac\s+([0-9A-Fa-f:.-]+)", re.I),
        "neighbor_name": re.compile(r"^\s*SysName:\s*(.+?)\s*$", re.I),
        "neighbor_ip": re.compile(r"^\s*MgmtIP:\s*(\S+)", re.I),
        "neighbor_port": re.compile(r"^\s*PortID:\s*(?:ifname\s+)?(.+?)\s*$", re.I),
    }
    neighbors = []
    current = None
    for line in text.replace("\r", "").splitlines():
        match = patterns["local_port"].search(line)
        if match:
            if current: neighbors.append(LldpNeighbor(**current))
            current = {"local_port": match.group(1), "neighbor_mac": "",
                       "neighbor_name": "", "neighbor_ip": "", "neighbor_port": ""}
            continue
        if current is None: continue
        for key, pattern in patterns.items():
            if key == "local_port": continue
            match = pattern.search(line)
            if match:
                current[key] = normalize_mac(match.group(1)) if key == "neighbor_mac" else match.group(1).strip()
                break
    if current: neighbors.append(LldpNeighbor(**current))
    return neighbors
