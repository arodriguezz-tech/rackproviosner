import pytest
from app.inventory.repository import norm_serial,norm_mac
from app.inventory.service import InventoryService
from app.domain.models import DeviceIdentity
from app.testing.fakes import FakeBus,FakeRepo,FakeSettings

def test_normalizers(): assert norm_serial(' ab 12 ')=='AB12' and norm_mac('00-aa-bb-cc-dd-ee')=='00AABBCCDDEE'
def test_repo_crud(repo,rack,devices):
 repo.save(rack,devices); r,d=repo.get_rack('RACK001'); assert r['rack_sku']=='119684' and len(d)==3; repo.delete('RACK001'); assert repo.get_rack('RACK001')==(None,[])
def test_repo_upsert(repo,rack,devices):
 repo.save(rack,devices); rack['rack_sku']='NEW'; devices[1]['model']='SN2700'; repo.save(rack,devices); r,d=repo.get_rack('RACK001'); assert r['rack_sku']=='NEW' and next(x for x in d if x['role']=='NS1')['model']=='SN2700'
@pytest.mark.parametrize('serial,mac,role',[('NS1001','','NS1'),('','00-11-22-33-44-53','NS2'),('MX001','00:11:22:33:44:51','MX')])
def test_identity_matches(repo,rack,devices,serial,mac,role): repo.save(rack,devices); assert repo.identity_matches('RACK001',serial,mac)[1]==role
def test_identity_conflict(repo,rack,devices): repo.save(rack,devices); assert repo.identity_matches('RACK001','NS1001','00:11:22:33:44:53')[0]=='CONFLICT'
def test_cross_rack_unknown(repo,rack,devices): repo.save(rack,devices); assert repo.identity_matches('OTHER','NS1001','')[0]=='UNKNOWN'
def make_service(enabled=True): return InventoryService(FakeRepo(),FakeBus(),FakeSettings(enabled))
def test_service_save(rack,devices):
 s=make_service(); s.save_record(rack,devices); assert len(s.repo.saved)==1 and s.bus.events[0][0]=='inventory.saved'
@pytest.mark.parametrize('field',["rack_serial","rack_sku"])
def test_required_rack(field,rack,devices):
 s=make_service(); rack[field]=''
 with pytest.raises(ValueError): s.save_record(rack,devices)
def test_missing_role(rack,devices):
 with pytest.raises(ValueError): make_service().save_record(rack,devices[:-1])
def test_duplicate_role(rack,devices):
 devices[2]['role']='NS1'
 with pytest.raises(ValueError): make_service().save_record(rack,devices)
def test_missing_model(rack,devices):
 devices[0]['model']=''
 with pytest.raises(ValueError): make_service().save_record(rack,devices)
def test_missing_identity(rack,devices):
 devices[0]['serial']=devices[0]['mac']=''
 with pytest.raises(ValueError): make_service().save_record(rack,devices)
def test_bad_mac(rack,devices):
 devices[0]['mac']='bad'
 with pytest.raises(ValueError): make_service().save_record(rack,devices)
def test_duplicate_serial(rack,devices):
 devices[2]['serial']=devices[1]['serial']
 with pytest.raises(ValueError): make_service().save_record(rack,devices)
def test_duplicate_mac(rack,devices):
 devices[2]['mac']=devices[1]['mac']
 with pytest.raises(ValueError): make_service().save_record(rack,devices)
def test_verify_enabled():
 s=make_service(); s.repo.result=('VERIFIED','NS1','match'); assert s.verify('R1',DeviceIdentity(serial='S'))[1]=='NS1'
def test_verify_disabled(): assert make_service(False).verify('R1',DeviceIdentity())[0]=='DISABLED'
