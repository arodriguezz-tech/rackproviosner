from app.core.events import EventBus
from app.discovery.lldp import parse
from app.inventory.repository import norm_mac
def test_event_bus():
    bus=EventBus(); got=[]; bus.subscribe("x",lambda e:got.append(e.payload["v"])); bus.publish("x",v=3); assert got==[3]
def test_lldp():
    text="Interface: Ethernet96, via: LLDP\nChassisID: mac 00:11:22:33:44:55\nSysName: NS2\nPortID: ifname Ethernet104\n"; n=parse(text)[0]; assert n.local_port=="Ethernet96" and n.neighbor_mac=="001122334455" and n.neighbor_port=="Ethernet104"
def test_mac(): assert norm_mac("00-11-22-aa-bb-cc")=="001122AABBCC"
