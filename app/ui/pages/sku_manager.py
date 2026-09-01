"""Engineer-facing SKU configuration editors.

Layer rule: this module should depend only on lower-level modules documented in ARCHITECTURE.md.
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QComboBox,QLineEdit,QPushButton,QLabel,QTabWidget,QPlainTextEdit,QMessageBox
from app.ui.highlighter import ShellHighlighter
class SkuManagerPage(QWidget):
    def __init__(self,repo,service,bus):
        super().__init__(); self.repo=repo; self.service=service; self.high=[]; l=QVBoxLayout(self); r=QHBoxLayout(); self.pick=QComboBox(); self.pick.setEditable(True); self.pick.addItems(repo.list()); self.desc=QLineEdit(); b=QPushButton("Save Revision"); r.addWidget(QLabel("SKU")); r.addWidget(self.pick); r.addWidget(QLabel("Description")); r.addWidget(self.desc,1); r.addWidget(b); l.addLayout(r); self.tabs=QTabWidget(); self.models={}; self.editors={}
        for role in ("mx","ns1","ns2"):
            w=QWidget(); v=QVBoxLayout(w); m=QLineEdit(); e=QPlainTextEdit(); e.setFont(QFont("Consolas",10)); v.addWidget(QLabel("Expected model")); v.addWidget(m); v.addWidget(e); self.models[role]=m; self.editors[role]=e; self.high.append(ShellHighlighter(e.document())); self.tabs.addTab(w,role.upper())
        self.notes=QPlainTextEdit(); self.tabs.addTab(self.notes,"Notes"); l.addWidget(self.tabs,1); self.pick.currentTextChanged.connect(self.load); b.clicked.connect(self.save); bus.subscribe("sku.revision.saved",lambda e: QMessageBox.information(self,"Revision",f"Saved {e.payload['revision_type']} revision {e.payload['version']}.")); self.load(self.pick.currentText())
    def load(self,sku):
        m,d=self.repo.load(sku); self.desc.setText(m["description"] if m else "")
        for r in ("mx","ns1","ns2"): self.models[r].setText(d[r+"_model"] if d else ""); self.editors[r].setPlainText(d[r+"_text"] if d else "")
        self.notes.setPlainText(d["notes"] if d else "")
    def save(self):
        sku=self.pick.currentText().strip()
        if not sku: QMessageBox.warning(self,"SKU","Enter a SKU."); return
        data={"notes":self.notes.toPlainText()}
        for r in ("mx","ns1","ns2"): data[r+"_model"]=self.models[r].text(); data[r+"_text"]=self.editors[r].toPlainText()
        typ,_,_=self.service.save(sku,self.desc.text(),data)
        if typ=="none": QMessageBox.information(self,"Revision","No changes detected.")
        if self.pick.findText(sku)<0: self.pick.addItem(sku)
