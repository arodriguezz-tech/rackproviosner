import sqlite3
from datetime import datetime,timezone
SCHEMA="""PRAGMA foreign_keys=ON; CREATE TABLE IF NOT EXISTS racks(rack_serial TEXT PRIMARY KEY,rack_sku TEXT NOT NULL,rack_bom TEXT,rack_asset_tag TEXT,created_at TEXT,modified_at TEXT); CREATE TABLE IF NOT EXISTS devices(id INTEGER PRIMARY KEY,rack_serial TEXT NOT NULL REFERENCES racks(rack_serial) ON DELETE CASCADE,role TEXT NOT NULL,model TEXT,serial_number TEXT,normalized_serial TEXT,mac_address TEXT,normalized_mac TEXT,UNIQUE(rack_serial,role));"""
def norm_serial(v): return ''.join(v.strip().upper().split())
def norm_mac(v): return ''.join(c for c in v.upper() if c in '0123456789ABCDEF')
def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
class InventoryRepository:
 def __init__(self,path): self.path=str(path); self.initialize()
 def connect(self): c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c
 def initialize(self):
  with self.connect() as c: c.executescript(SCHEMA)
 def save(self,rack,devices):
  t=now()
  with self.connect() as c:
   c.execute('INSERT INTO racks VALUES(?,?,?,?,?,?) ON CONFLICT(rack_serial) DO UPDATE SET rack_sku=excluded.rack_sku,rack_bom=excluded.rack_bom,rack_asset_tag=excluded.rack_asset_tag,modified_at=excluded.modified_at',(rack['rack_serial'],rack['rack_sku'],rack.get('rack_bom',''),rack.get('rack_asset_tag',''),t,t))
   for d in devices:
    s=d.get('serial',''); m=d.get('mac','')
    c.execute('INSERT INTO devices(rack_serial,role,model,serial_number,normalized_serial,mac_address,normalized_mac) VALUES(?,?,?,?,?,?,?) ON CONFLICT(rack_serial,role) DO UPDATE SET model=excluded.model,serial_number=excluded.serial_number,normalized_serial=excluded.normalized_serial,mac_address=excluded.mac_address,normalized_mac=excluded.normalized_mac',(rack['rack_serial'],d['role'],d.get('model',''),s,norm_serial(s) if s else None,m,norm_mac(m) if m else None))
 def get_rack(self,rs):
  with self.connect() as c: return c.execute('SELECT * FROM racks WHERE rack_serial=?',(rs,)).fetchone(),c.execute('SELECT * FROM devices WHERE rack_serial=? ORDER BY role',(rs,)).fetchall()
 def delete(self,rs):
  with self.connect() as c: c.execute('DELETE FROM racks WHERE rack_serial=?',(rs,))
 def identity_matches(self,rs,serial,mac):
  s=norm_serial(serial) if serial else ''; m=norm_mac(mac) if mac else ''
  with self.connect() as c:
   a=c.execute('SELECT role FROM devices WHERE rack_serial=? AND normalized_serial=?',(rs,s)).fetchone() if s else None
   b=c.execute('SELECT role FROM devices WHERE rack_serial=? AND normalized_mac=?',(rs,m)).fetchone() if m else None
  if a and b and a['role']!=b['role']: return 'CONFLICT',None,'Serial and MAC map to different roles'
  hit=a or b
  if hit: return 'VERIFIED',hit['role'],'Matched by '+('serial+MAC' if a and b else 'serial' if a else 'MAC')
  return 'UNKNOWN',None,'No serial or MAC match for this rack'
