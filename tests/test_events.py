import pytest
from app.core import event_names as e
from app.core.events import EventContractError
CASES=[(e.SERIAL_CONNECTED,{'ok':True,'port':'COM1','baud':9600}),(e.SERIAL_COMMAND_FINISHED,{'name':'version','output':'ok'}),(e.DISCOVERY_COMPLETED,{'result':object()}),(e.LLDP_COMPLETED,{'neighbors':[],'raw_output':''}),(e.INVENTORY_SAVED,{'rack_serial':'R1'}),(e.INVENTORY_VERIFIED,{'state':'VERIFIED','role':'NS1','reason':'match','rack_serial':'R1'}),(e.SKU_REVISION_SAVED,{'sku':'1','version':'1.0','revision_type':'major','changes':[]}),(e.SETTINGS_CHANGED,{}),(e.READINESS_EVALUATED,{'result':object()})]
@pytest.mark.parametrize('name,payload',CASES)
def test_published_received_payload(bus,name,payload):
 got=[]; bus.subscribe(name,got.append); event=bus.publish(name,**payload)
 assert bus.published_events[-1] is event; assert got==[event]; assert got[0].payload==payload
@pytest.mark.parametrize('name,payload',CASES)
def test_wildcard(bus,name,payload):
 got=[]; bus.subscribe('*',got.append); bus.publish(name,**payload); assert got[0].name==name

def test_unsubscribe(bus):
 got=[]; bus.subscribe(e.SETTINGS_CHANGED,got.append); bus.unsubscribe(e.SETTINGS_CHANGED,got.append); bus.publish(e.SETTINGS_CHANGED); assert got==[]
def test_contract_rejects_missing(bus):
 with pytest.raises(EventContractError): bus.publish(e.SERIAL_CONNECTED,ok=True)
