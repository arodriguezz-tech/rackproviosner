from app.inventory.repository import normalize_mac, normalize_serial

def test_normalization_helpers():
    assert normalize_serial(" ab c-123 ") == "ABC-123"
    assert normalize_mac("00-11-22-aa-bb-cc") == "001122AABBCC"

def test_save_and_get_rack(sqlite_repo, rack, devices):
    sqlite_repo.save(rack,devices)
    found, rows=sqlite_repo.get_rack("RACK-001")
    assert found["rack_sku"] == "119684"
    assert {row["role"] for row in rows} == {"MX","NS1","NS2"}

def test_upsert_updates_rack_and_role(sqlite_repo, rack, devices):
    sqlite_repo.save(rack,devices)
    rack["rack_sku"]="119700"; devices[1]["model"]="SN2700"
    sqlite_repo.save(rack,devices)
    found, rows=sqlite_repo.get_rack("RACK-001")
    assert found["rack_sku"] == "119700"
    assert next(r for r in rows if r["role"]=="NS1")["model"] == "SN2700"
    assert len(rows) == 3

def test_missing_rack_returns_none_and_empty_list(sqlite_repo):
    rack,rows=sqlite_repo.get_rack("MISSING")
    assert rack is None and rows == []

def test_match_by_serial(sqlite_repo, rack, devices):
    sqlite_repo.save(rack,devices)
    state,role,reason=sqlite_repo.identity_matches("RACK-001"," ns1 001 ","")
    assert (state,role)==("VERIFIED","NS1") and "serial" in reason

def test_match_by_mac(sqlite_repo, rack, devices):
    sqlite_repo.save(rack,devices)
    state,role,reason=sqlite_repo.identity_matches("RACK-001","","00-11-22-33-44-53")
    assert (state,role)==("VERIFIED","NS2") and "MAC" in reason

def test_match_by_serial_and_mac(sqlite_repo, rack, devices):
    sqlite_repo.save(rack,devices)
    state,role,reason=sqlite_repo.identity_matches("RACK-001","MX001","00:11:22:33:44:51")
    assert (state,role)==("VERIFIED","MX") and "serial+MAC" in reason

def test_conflicting_serial_and_mac(sqlite_repo, rack, devices):
    sqlite_repo.save(rack,devices)
    state,role,_=sqlite_repo.identity_matches("RACK-001","NS1001","00:11:22:33:44:53")
    assert state == "CONFLICT" and role is None

def test_cross_rack_identity_is_unknown(sqlite_repo, rack, devices):
    sqlite_repo.save(rack,devices)
    state,role,_=sqlite_repo.identity_matches("OTHER-RACK","NS1001","")
    assert state == "UNKNOWN" and role is None

def test_delete_rack_cascades_devices(sqlite_repo, rack, devices):
    sqlite_repo.save(rack,devices); sqlite_repo.delete_rack("RACK-001")
    found,rows=sqlite_repo.get_rack("RACK-001")
    assert found is None and rows == []
