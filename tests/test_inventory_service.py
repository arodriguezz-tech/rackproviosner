import pytest
from app.core import event_names as events
from app.domain.models import DeviceIdentity

def test_save_record_normalizes_persists_and_publishes(fake_stack, rack, devices):
    service, repo, bus, _ = fake_stack
    devices[0]["mac"] = "00-11-22-33-44-51"
    devices[1]["serial"] = " ns1 001 "
    service.save_record(rack, devices)
    saved_rack, saved_devices = repo.saved[0]
    assert saved_rack["rack_serial"] == "RACK-001"
    assert saved_devices[0]["mac"] == "001122334451"
    assert saved_devices[1]["serial"] == "NS1001"
    assert bus.events_named(events.INVENTORY_SAVED) == [{"rack_serial":"RACK-001"}]

@pytest.mark.parametrize("field,message", [("rack_serial","Rack Serial"),("rack_sku","Rack SKU")])
def test_required_rack_fields(fake_stack, rack, devices, field, message):
    service, repo, _, _ = fake_stack; rack[field] = ""
    with pytest.raises(ValueError, match=message): service.save_record(rack, devices)
    assert repo.saved == []

def test_missing_role_is_rejected(fake_stack, rack, devices):
    service, _, _, _ = fake_stack
    with pytest.raises(ValueError, match="Missing roles: NS2"): service.save_record(rack, devices[:-1])

def test_duplicate_role_is_rejected(fake_stack, rack, devices):
    service, _, _, _ = fake_stack; devices[2]["role"] = "NS1"
    with pytest.raises(ValueError, match="Duplicate roles: NS1"): service.save_record(rack, devices)

def test_duplicate_serial_is_rejected(fake_stack, rack, devices):
    service, _, _, _ = fake_stack; devices[2]["serial"] = devices[1]["serial"]
    with pytest.raises(ValueError, match="Duplicate device serial"): service.save_record(rack, devices)

def test_duplicate_mac_is_rejected_after_normalization(fake_stack, rack, devices):
    service, _, _, _ = fake_stack; devices[2]["mac"] = "00-11-22-33-44-52"
    with pytest.raises(ValueError, match="Duplicate MAC"): service.save_record(rack, devices)

def test_device_requires_identity(fake_stack, rack, devices):
    service, _, _, _ = fake_stack; devices[1]["serial"]=""; devices[1]["mac"]=""
    with pytest.raises(ValueError, match="NS1 requires"): service.save_record(rack, devices)

def test_invalid_mac_is_rejected(fake_stack, rack, devices):
    service, _, _, _ = fake_stack; devices[1]["mac"]="BAD-MAC"
    with pytest.raises(ValueError, match="NS1 MAC address is invalid"): service.save_record(rack, devices)

def test_verify_uses_repository_and_publishes(fake_stack):
    service, repo, bus, _ = fake_stack; repo.match_result=("VERIFIED","NS1","Matched by serial")
    result=service.verify("RACK-001",DeviceIdentity(serial="NS1001"))
    assert result[0:2] == ("VERIFIED","NS1")
    assert bus.events_named(events.INVENTORY_VERIFIED)[0]["role"] == "NS1"

def test_verify_can_be_disabled(fake_stack):
    service, repo, bus, settings = fake_stack; settings.inventory_enabled=False
    assert service.verify("RACK-001",DeviceIdentity())[0] == "DISABLED"
    assert repo.match_result == ("UNKNOWN",None,"No match")
