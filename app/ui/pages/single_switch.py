"""Single-switch discovery workflow UI.

Layer rule: this module should depend only on lower-level modules documented in ARCHITECTURE.md.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QFormLayout,QGroupBox,QComboBox,QLineEdit,QPushButton,QLabel,QProgressBar,QPlainTextEdit,QSplitter
class SingleSwitchPage(QWidget):
    def __init__(self,discovery,inventory,sku_repo,bus,settings):
        super().__init__(); self.discovery=discovery; self.inventory=inventory; self.bus=bus; self.settings=settings; self.result=None; self._build(); self._subscribe(); self.refresh_ports(); self.sku.addItems(sku_repo.list())
    def _build(self):
        l=QVBoxLayout(self); g=QGroupBox("Rack Entry"); f=QFormLayout(g); self.position=QComboBox(); self.position.addItems([f"RK{i}" for i in range(1617,1633)]); self.rack_serial=QLineEdit(); self.bom=QLineEdit(); self.asset=QLineEdit(); self.sku=QComboBox(); self.sku.setEditable(True)
        for n,w in [("Rack Position",self.position),("Rack Serial",self.rack_serial),("Rack BOM",self.bom),("Rack Asset Tag",self.asset),("Rack SKU",self.sku)]: f.addRow(n,w)
        l.addWidget(g); r=QHBoxLayout(); self.port=QComboBox(); self.baud=QComboBox(); self.baud.addItems(["9600","19200","38400","57600","115200"]); self.baud.setCurrentText(self.settings.get("general","default_baud","9600")); self.refresh=QPushButton("Refresh Ports"); self.connect=QPushButton("Connect"); self.discover=QPushButton("Discover"); self.lldp=QPushButton("LLDP Check"); self.apply=QPushButton("Apply Configuration"); self.apply.setEnabled(False); self.apply.setToolTip("Alpha safety lock")
        for w in [QLabel("Port"),self.port,QLabel("Baud"),self.baud,self.refresh,self.connect,self.discover,self.lldp,self.apply]: r.addWidget(w)
        l.addLayout(r); r=QHBoxLayout(); self.status=QLabel("Discovery: Not connected"); self.role=QLabel("Role: Unknown"); self.progress=QProgressBar(); r.addWidget(self.status); r.addWidget(self.role); r.addWidget(self.progress,1); l.addLayout(r); sp=QSplitter(Qt.Orientation.Horizontal); self.console=QPlainTextEdit(); self.console.setReadOnly(True); self.actions=QPlainTextEdit(); self.actions.setReadOnly(True)
        for title,w in [("Console",self.console),("Action Output",self.actions)]: b=QGroupBox(title); q=QVBoxLayout(b); q.addWidget(w); sp.addWidget(b)
        l.addWidget(sp,1); self.refresh.clicked.connect(self.refresh_ports); self.connect.clicked.connect(self.toggle); self.discover.clicked.connect(self.start); self.lldp.clicked.connect(self.discovery.lldp_only)
    def _subscribe(self):
        self.bus.subscribe("console.received",lambda e:self.console.insertPlainText(e.payload["text"])); self.bus.subscribe("serial.connected",self.on_connected); self.bus.subscribe("serial.disconnected",lambda e:self.on_connected(e)); self.bus.subscribe("serial.command.started",lambda e:self.log("Running: "+e.payload["command"])); self.bus.subscribe("serial.error",lambda e:self.log("Serial error: "+e.payload["message"])); self.bus.subscribe("serial.blocked",lambda e:self.log("BLOCKED: "+e.payload["reason"])); self.bus.subscribe("discovery.started",lambda e:self.set_stage("Discovery: Running",20)); self.bus.subscribe("discovery.command.completed",lambda e:self.set_stage("Discovery: "+e.payload["command"]+" complete",min(80,self.progress.value()+20))); self.bus.subscribe("discovery.completed",self.completed); self.bus.subscribe("lldp.completed",self.lldp_completed); self.bus.subscribe("inventory.verified",lambda e:self.log(f"Inventory: {e.payload['state']} - {e.payload['reason']}"))
    def refresh_ports(self): self.port.clear(); self.port.addItems(self.discovery.ports())
    def toggle(self):
        if self.discovery.session.port.isOpen(): self.discovery.disconnect()
        elif self.port.currentText(): self.discovery.connect(self.port.currentText(),self.baud.currentText())
    def on_connected(self,e):
        ok=e.payload.get("ok",False); self.connect.setText("Disconnect" if ok else "Connect"); self.set_stage("Discovery: Console connected" if ok else "Discovery: Not connected",10 if ok else 0)
    def start(self):
        if not self.rack_serial.text().strip(): self.log("BLOCKED: Enter Rack Serial first."); return
        self.discovery.discover()
    def completed(self,e):
        self.result=e.payload["result"]; i=self.result.identity; self.log(f"Identity: serial={i.serial or '?'} MAC={i.mac or '?'} model={i.model or '?'}"); self.log(f"LLDP parsed: {len(self.result.neighbors)} neighbor(s)")
        for n in self.result.neighbors: self.log(f"{n.local_port} -> {n.neighbor_mac or n.neighbor_name or '?'} remote-port={n.neighbor_port or '?'}")
        state,role,reason=self.inventory.verify(self.rack_serial.text().strip(),i); ready=state in ("VERIFIED","DISABLED"); self.role.setText("Role: "+(role or state)); self.set_stage("Discovery: Complete" if ready else "Discovery: BLOCKED",100 if ready else 90)
    def lldp_completed(self,e):
        neighbors=e.payload["neighbors"]
        self.log(f"LLDP parsed: {len(neighbors)} neighbor(s)")
        for n in neighbors:
            self.log(f"{n.local_port} -> {n.neighbor_mac or n.neighbor_name or '?'} remote-port={n.neighbor_port or '?'}")

    def set_stage(self,text,value): self.status.setText(text); self.progress.setValue(value)
    def log(self,text): self.actions.appendPlainText(text)
