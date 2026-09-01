import pytest
from app.inventory.repository import InventoryRepository
from app.inventory.service import InventoryService
from tests.fakes import FakeEventBus, FakeRepository, FakeSettings

@pytest.fixture
def rack():
    return {"rack_serial":"RACK-001","rack_sku":"119684","rack_bom":"GEN11","rack_asset_tag":"AT-001"}

@pytest.fixture
def devices():
    return [
        {"role":"MX","model":"Nokia 7215 IXS","serial":"MX001","mac":"00:11:22:33:44:51"},
        {"role":"NS1","model":"SN4700","serial":"NS1001","mac":"00:11:22:33:44:52"},
        {"role":"NS2","model":"SN4700","serial":"NS2001","mac":"00:11:22:33:44:53"},
    ]

@pytest.fixture
def fake_stack():
    repo=FakeRepository(); bus=FakeEventBus(); settings=FakeSettings(True)
    return InventoryService(repo,bus,settings), repo, bus, settings

@pytest.fixture
def sqlite_repo(tmp_path):
    return InventoryRepository(tmp_path / "inventory.db")
