from app.discovery.lldp import parse

def test_parse_multiple_neighbors():
    raw="""
Interface: Ethernet96, via: LLDP
ChassisID: mac 00:11:22:33:44:55
SysName: NS2
MgmtIP: 192.168.0.4
PortID: ifname Ethernet104
-------------------------------------------------------------------------------
Interface: Ethernet104, via: LLDP
ChassisID: mac aa-bb-cc-dd-ee-ff
SysName: TS1
PortID: Ethernet12
"""
    rows=parse(raw)
    assert len(rows)==2
    assert rows[0].local_port=="Ethernet96"
    assert rows[0].neighbor_mac=="001122334455"
    assert rows[0].neighbor_port=="Ethernet104"
    assert rows[1].neighbor_name=="TS1"

def test_empty_lldp_output(): assert parse("")==[]
