import hashlib,json,tarfile,tempfile
from pathlib import Path
from app.core import event_names as e
class SkuService:
 def __init__(self,bus,archive_dir): self.bus=bus; self.archive_dir=Path(archive_dir); self.archive_dir.mkdir(exist_ok=True); self.records={}
 def classify(self,old,new):
  if old is None: return 'major',['New SKU']
  major=any(old.get(r+'_model')!=new.get(r+'_model') for r in ('mx','ns1','ns2'))
  changes=[k for k in new if old.get(k)!=new.get(k)]
  return ('major' if major else 'minor' if changes else 'none'),changes
 def save(self,sku,new):
  old=self.records.get(sku); typ,changes=self.classify(old,new)
  if typ=='none': return None
  old_version=old['_version'] if old else None
  if old:
   path=self.archive_dir/f'{sku}_v{old_version}.tar.gz'
   with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'metadata.json'; p.write_text(json.dumps(old,indent=2))
    with tarfile.open(path,'w:gz') as tf: tf.add(p,arcname='metadata.json')
  if old:
   ma,mi=map(int,old_version.split('.')); version=f'{ma+1}.0' if typ=='major' else f'{ma}.{mi+1}'
  else: version='1.0'
  record=dict(new); record['_version']=version; record['_checksum']=hashlib.sha256(json.dumps(new,sort_keys=True).encode()).hexdigest(); self.records[sku]=record
  self.bus.publish(e.SKU_REVISION_SAVED,sku=sku,version=version,revision_type=typ,changes=changes); return record
