"""Top-level navigation and engineer-mode visibility.

Layer rule: this module should depend only on lower-level modules documented in ARCHITECTURE.md.
"""

from PySide6.QtWidgets import QMainWindow,QTabWidget,QWidget,QVBoxLayout,QLabel,QTableWidget,QTableWidgetItem,QHeaderView
from app.ui.pages.single_switch import SingleSwitchPage
from app.ui.pages.inventory import InventoryPage
from app.ui.pages.sku_manager import SkuManagerPage
from app.ui.pages.settings import SettingsPage
class HistoryPage(QWidget):
    def __init__(self,repo,bus):
        super().__init__(); self.repo=repo; l=QVBoxLayout(self); self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(["SKU","Version","Type","Trigger","Summary","Created"]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); l.addWidget(self.table); bus.subscribe("sku.revision.saved",lambda e:self.refresh()); self.refresh()
    def refresh(self):
        rows=self.repo.history(); self.table.setRowCount(len(rows))
        for i,x in enumerate(rows):
            for j,v in enumerate([x["sku"],f"{x['major']}.{x['minor']}",x["revision_type"],x["trigger"],x["change_summary"],x["created_at"]]): self.table.setItem(i,j,QTableWidgetItem(v or ""))
class MainWindow(QMainWindow):
    def __init__(self,services):
        super().__init__(); self.services=services; self.setWindowTitle("Rack Provisioner Alpha v2"); self.resize(1280,820); self.tabs=QTabWidget(); self.setCentralWidget(self.tabs); self.tabs.addTab(SingleSwitchPage(services.discovery,services.inventory,services.sku_repo,services.bus,services.settings),"Single Switch"); multi=QWidget(); q=QVBoxLayout(multi); q.addWidget(QLabel("Multi Switch module scaffold. It will coordinate three independent DiscoveryService workers.")); q.addStretch(); self.tabs.addTab(multi,"Multi Switch"); self.tabs.addTab(InventoryPage(services.inventory_repo),"Inventory Mapping"); self.tabs.addTab(SkuManagerPage(services.sku_repo,services.sku,services.bus),"SKU Manager"); self.history_index=self.tabs.addTab(HistoryPage(services.sku_repo,services.bus),"Revision History"); self.tabs.addTab(SettingsPage(services.settings,services.inventory,services.bus),"Settings"); services.bus.subscribe("settings.changed",lambda e:self.apply_visibility()); self.apply_visibility();
        if services.settings.get("general","startup_page","single_switch")=="multi_switch": self.tabs.setCurrentIndex(1)
    def apply_visibility(self): self.tabs.setTabVisible(self.history_index,self.services.settings.get_bool("general","engineer_mode",False))
