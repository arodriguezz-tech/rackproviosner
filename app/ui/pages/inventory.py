from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLineEdit,QPushButton,QLabel,QTableWidget,QTableWidgetItem,QHeaderView
class InventoryPage(QWidget):
    def __init__(self,repo):
        super().__init__(); self.repo=repo; l=QVBoxLayout(self); r=QHBoxLayout(); self.search=QLineEdit(); b=QPushButton("Search Rack"); r.addWidget(QLabel("Rack Serial")); r.addWidget(self.search); r.addWidget(b); l.addLayout(r); self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels(["Role","Model","Serial","MAC","Rack"]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); l.addWidget(self.table); b.clicked.connect(self.find)
    def find(self):
        _,rows=self.repo.get_rack(self.search.text().strip()); self.table.setRowCount(len(rows))
        for i,d in enumerate(rows):
            for j,v in enumerate([d["role"],d["model"],d["serial_number"],d["mac_address"],d["rack_serial"]]): self.table.setItem(i,j,QTableWidgetItem(v or ""))
