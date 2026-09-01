import tarfile
from app.sku.service import SkuService
def data(model='SN4700',text='a'): return {'mx_model':'Nokia','ns1_model':model,'ns2_model':'SN4700','mx_text':'x','ns1_text':text,'ns2_text':'z','notes':''}
def test_new_sku(bus,tmp_path):
 s=SkuService(bus,tmp_path); r=s.save('119684',data()); assert r['_version']=='1.0' and len(r['_checksum'])==64 and bus.published_events[-1].payload['revision_type']=='major'
def test_minor_revision_archives(bus,tmp_path):
 s=SkuService(bus,tmp_path); s.save('119684',data()); r=s.save('119684',data(text='b')); assert r['_version']=='1.1'; paths=list(tmp_path.glob('*.tar.gz')); assert len(paths)==1
 with tarfile.open(paths[0]) as tf: assert 'metadata.json' in tf.getnames()
def test_major_revision(bus,tmp_path):
 s=SkuService(bus,tmp_path); s.save('119684',data()); assert s.save('119684',data(model='SN2700'))['_version']=='2.0'
def test_no_change(bus,tmp_path):
 s=SkuService(bus,tmp_path); s.save('119684',data()); count=len(bus.published_events); assert s.save('119684',data()) is None and len(bus.published_events)==count
