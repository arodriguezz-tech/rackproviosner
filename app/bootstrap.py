"""Application composition root. Creates services and injects dependencies.

Layer rule: this module should depend only on lower-level modules documented in ARCHITECTURE.md.
"""

import sys
from dataclasses import dataclass
from PySide6.QtWidgets import QApplication
from app.core.database import initialize
from app.core.events import EventBus
from app.core.settings import SettingsService
from app.inventory.repository import InventoryRepository
from app.inventory.service import InventoryService
from app.discovery.serial import SerialSession
from app.discovery.parser import IdentityParser
from app.discovery.service import DiscoveryService
from app.sku.repository import SkuRepository
from app.sku.service import SkuService
from app.ui.main_window import MainWindow
@dataclass
class Services:
    bus:EventBus; settings:SettingsService; inventory_repo:InventoryRepository; inventory:InventoryService; discovery:DiscoveryService; sku_repo:SkuRepository; sku:SkuService
def build_services():
    bus=EventBus(); settings=SettingsService(); inv_repo=InventoryRepository(); inventory=InventoryService(inv_repo,bus,settings); discovery=DiscoveryService(SerialSession(),IdentityParser(settings),bus); sku_repo=SkuRepository(); sku=SkuService(sku_repo,bus); return Services(bus,settings,inv_repo,inventory,discovery,sku_repo,sku)
def run():
    initialize(); app=QApplication(sys.argv); app.setApplicationName("Rack Provisioner Alpha v2"); win=MainWindow(build_services()); win.show(); return app.exec()
