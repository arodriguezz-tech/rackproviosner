from app.domain.models import RuleResult
class DiscoveryRule:
 def evaluate(self,c):
  ok=bool(c['identity'].serial and c['identity'].model)
  return RuleResult('discovery','PASS' if ok else 'FAIL','' if ok else 'DISC-001','Identity incomplete')
class InventoryRule:
 def evaluate(self,c):
  state=c['inventory_state']; status='PASS' if state=='VERIFIED' else 'WARNING' if state=='DISABLED' else 'FAIL'
  return RuleResult('inventory',status,'' if status=='PASS' else 'INV-001',state)
class SkuModelRule:
 def evaluate(self,c):
  ok=c['identity'].model.strip().lower()==c['expected_model'].strip().lower()
  return RuleResult('sku_model','PASS' if ok else 'FAIL','' if ok else 'SKU-001','Model match' if ok else 'Model mismatch')
class LldpRule:
 def evaluate(self,c):
  ok=len(c['neighbors'])>=c.get('minimum_neighbors',0)
  return RuleResult('lldp','PASS' if ok else 'FAIL','' if ok else 'LLDP-001','Neighbor count')
class ProfileRule:
 def evaluate(self,c):
  ok=bool(c.get('profile_available'))
  return RuleResult('profile','PASS' if ok else 'FAIL','' if ok else 'PROF-001','Profile available' if ok else 'Profile missing')
