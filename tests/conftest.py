import pytest
from app.core.events import EventBus
from app.core.contracts import CONTRACTS
from app.inventory.repository import InventoryRepository
@pytest.fixture
def bus(): return EventBus(CONTRACTS)
@pytest.fixture
def devices(): return [
 {'role':'MX','model':'Nokia 7215 IXS','serial':'MX001','mac':'00:11:22:33:44:51'},
 {'role':'NS1','model':'SN4700','serial':'NS1001','mac':'00:11:22:33:44:52'},
 {'role':'NS2','model':'SN4700','serial':'NS2001','mac':'00:11:22:33:44:53'}]
@pytest.fixture
def rack(): return {'rack_serial':'RACK001','rack_sku':'119684','rack_bom':'GEN11','rack_asset_tag':'AT1'}
@pytest.fixture
def repo(tmp_path): return InventoryRepository(tmp_path/'inventory.db')
