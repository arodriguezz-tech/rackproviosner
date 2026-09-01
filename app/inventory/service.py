from app.core import event_names as e
from .repository import norm_serial,norm_mac
REQUIRED={'MX','NS1','NS2'}
class InventoryService:
 def __init__(self,repo,bus,settings): self.repo=repo; self.bus=bus; self.settings=settings
 def save_record(self,rack,devices):
  rack={k:rack.get(k,'').strip() for k in ('rack_serial','rack_sku','rack_bom','rack_asset_tag')}
  devices=[{'role':d.get('role','').strip().upper(),'model':d.get('model','').strip(),'serial':norm_serial(d.get('serial','')),'mac':norm_mac(d.get('mac',''))} for d in devices]
  if not rack['rack_serial']: raise ValueError('Rack Serial is required')
  if not rack['rack_sku']: raise ValueError('Rack SKU is required')
  roles=[d['role'] for d in devices]
  dup={r for r in roles if roles.count(r)>1}
  if dup: raise ValueError('Duplicate roles')
  missing=REQUIRED-set(roles)
  if missing: raise ValueError('Missing roles')
  for d in devices:
   if not d['model']: raise ValueError(f"{d['role']} model is required")
   if not d['serial'] and not d['mac']: raise ValueError(f"{d['role']} identity is required")
   if d['mac'] and len(d['mac'])!=12: raise ValueError(f"{d['role']} MAC is invalid")
  ss=[d['serial'] for d in devices if d['serial']]; mm=[d['mac'] for d in devices if d['mac']]
  if len(ss)!=len(set(ss)): raise ValueError('Duplicate serial')
  if len(mm)!=len(set(mm)): raise ValueError('Duplicate MAC')
  self.repo.save(rack,devices); self.bus.publish(e.INVENTORY_SAVED,rack_serial=rack['rack_serial'])
 def verify(self,rs,identity):
  result=('DISABLED',None,'Inventory disabled') if not self.settings.get_bool('inventory','enabled',False) else self.repo.identity_matches(rs,identity.serial,identity.mac)
  self.bus.publish(e.INVENTORY_VERIFIED,state=result[0],role=result[1],reason=result[2],rack_serial=rs); return result
