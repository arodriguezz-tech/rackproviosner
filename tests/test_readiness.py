import pytest
from app.domain.models import DeviceIdentity,LldpNeighbor
from app.readiness.rules import DiscoveryRule,InventoryRule,SkuModelRule,LldpRule,ProfileRule
from app.readiness.service import ReadinessService
RULES=[DiscoveryRule(),InventoryRule(),SkuModelRule(),LldpRule(),ProfileRule()]
def context(**kw):
 c={'identity':DeviceIdentity('S1','M1','SN4700','NS1'),'inventory_state':'VERIFIED','expected_model':'SN4700','neighbors':[LldpNeighbor('Ethernet96')],'minimum_neighbors':1,'profile_available':True}; c.update(kw); return c
def test_ready(bus):
 got=[]; bus.subscribe('readiness.evaluated',got.append); r=ReadinessService(bus,RULES).evaluate(context()); assert r.ready and r.status=='READY' and got[0].payload['result'] is r
@pytest.mark.parametrize('change,code',[({'identity':DeviceIdentity()},'DISC-001'),({'inventory_state':'UNKNOWN'},'INV-001'),({'expected_model':'SN2700'},'SKU-001'),({'neighbors':[]},'LLDP-001'),({'profile_available':False},'PROF-001')])
def test_each_blocker(bus,change,code):
 r=ReadinessService(bus,RULES).evaluate(context(**change)); assert not r.ready and code in r.blockers
def test_inventory_disabled_is_warning(bus):
 r=ReadinessService(bus,RULES).evaluate(context(inventory_state='DISABLED')); assert r.ready and 'INV-001' in r.warnings
