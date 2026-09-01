"""SKU revision classification, archive creation, and persistence.

Layer rule: this module should depend only on lower-level modules documented in ARCHITECTURE.md.
"""

import hashlib,json,tarfile,tempfile
from pathlib import Path
from app.core.database import app_connection,now
from app.core.paths import ARCHIVE
class SkuService:
    def __init__(self,repo,bus): self.repo=repo; self.bus=bus
    def classify(self,old,new):
        if not old: return "major","NEW_SKU",["New SKU created"]
        hard=[]; changes=[]
        for r in ("mx","ns1","ns2"):
            if old[r+"_model"]!=new[r+"_model"]: hard.append(r.upper()+" model changed")
            if old[r+"_text"]!=new[r+"_text"]: changes.append(r.upper()+" configuration changed")
        if old["notes"]!=new["notes"]: changes.append("Notes changed")
        return ("major","MODEL_CHANGED",hard+changes) if hard else (("minor","CONTENT_CHANGED",changes) if changes else ("none","NO_CHANGE",[]))
    def save(self,sku,desc,new):
        meta,row=self.repo.load(sku); old=dict(row) if row else None; typ,trig,changes=self.classify(old,new)
        if typ=="none": return typ,None,changes
        path=None
        if meta:
            oldver=f"{meta['current_major']}.{meta['current_minor']}"; path=ARCHIVE/f"{sku}_v{oldver}.tar.gz"; package={"sku":sku,"version":oldver,"description":meta["description"],"content":old}
            with tempfile.TemporaryDirectory() as td:
                p=Path(td)/"metadata.json"; p.write_text(json.dumps(package,indent=2),encoding="utf-8")
                with tarfile.open(path,"w:gz") as tf: tf.add(p,arcname="metadata.json")
            major,minor=(meta["current_major"]+1,0) if typ=="major" else (meta["current_major"],meta["current_minor"]+1)
        else: major,minor=1,0
        check=hashlib.sha256(json.dumps(new,sort_keys=True).encode()).hexdigest(); t=now()
        with app_connection() as c:
            c.execute("INSERT INTO sku VALUES(?,?,?,?,?) ON CONFLICT(sku) DO UPDATE SET description=excluded.description,current_major=excluded.current_major,current_minor=excluded.current_minor,modified_at=excluded.modified_at",(sku,desc,major,minor,t))
            c.execute("INSERT INTO sku_content VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(sku) DO UPDATE SET mx_text=excluded.mx_text,ns1_text=excluded.ns1_text,ns2_text=excluded.ns2_text,notes=excluded.notes,mx_model=excluded.mx_model,ns1_model=excluded.ns1_model,ns2_model=excluded.ns2_model",(sku,new["mx_text"],new["ns1_text"],new["ns2_text"],new["notes"],new["mx_model"],new["ns1_model"],new["ns2_model"]))
            c.execute("INSERT INTO sku_revision(sku,major,minor,revision_type,trigger,change_summary,created_at,archive_path,checksum) VALUES(?,?,?,?,?,?,?,?,?)",(sku,major,minor,typ,trig,"; ".join(changes),t,str(path) if path else None,check))
        self.bus.publish("sku.revision.saved",sku=sku,version=f"{major}.{minor}",revision_type=typ,changes=changes); return typ,f"{major}.{minor}",changes
