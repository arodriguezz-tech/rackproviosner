from app.discovery.parser import IdentityParser
from app.discovery.lldp import parse
from app.discovery.service import DiscoveryService
from app.testing.fakes import FakeTransport
PAT={'serial':r'Serial:\s*(\S+)','mac':r'MAC:\s*(\S+)','model':r'Model:\s*(.+)'}
RAW='Interface: Ethernet96, via: LLDP\nChassisID: mac 00:11:22:33:44:55\nSysName: NS2\nMgmtIP: 192.168.0.4\nPortID: ifname Ethernet104\n'
def test_identity_parser():
 i=IdentityParser(PAT).parse({'x':'Serial: S1\nMAC: 00:11:22:33:44:55\nModel: SN4700'}); assert (i.serial,i.mac,i.model)==('S1','00:11:22:33:44:55','SN4700')
def test_identity_parser_missing(): assert IdentityParser(PAT).parse({'x':'none'}).serial==''
def test_lldp_parse():
 n=parse(RAW)[0]; assert n.local_port=='Ethernet96' and n.neighbor_mac=='001122334455' and n.neighbor_name=='NS2' and n.neighbor_ip=='192.168.0.4' and n.neighbor_port=='Ethernet104'
def test_lldp_empty(): assert parse('')==[]
def test_discovery_service(bus):
 t=FakeTransport({'show version':'Model: SN4700','show platform syseeprom':'Serial: S1\nMAC: 00:11:22:33:44:55','show lldp neighbors':RAW}); got=[]; bus.subscribe('discovery.completed',got.append); r=DiscoveryService(t,IdentityParser(PAT),bus).discover(); assert r.identity.serial=='S1' and len(r.neighbors)==1 and len(got)==1 and len(t.commands)==3
def test_lldp_only(bus):
 t=FakeTransport({'show lldp neighbors':RAW}); got=[]; bus.subscribe('lldp.completed',got.append); n=DiscoveryService(t,IdentityParser(PAT),bus).lldp_only(); assert len(n)==1 and got[0].payload['raw_output']==RAW
