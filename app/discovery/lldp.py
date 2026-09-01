import re
from app.domain.models import LldpNeighbor
from app.inventory.repository import norm_mac
def parse(text):
 pats={'local_port':re.compile(r'^\s*Interface:\s*([^,\s]+)',re.I),'neighbor_mac':re.compile(r'^\s*ChassisID:\s*mac\s+([0-9A-Fa-f:.-]+)',re.I),'neighbor_name':re.compile(r'^\s*SysName:\s*(.+?)\s*$',re.I),'neighbor_ip':re.compile(r'^\s*MgmtIP:\s*(\S+)',re.I),'neighbor_port':re.compile(r'^\s*PortID:\s*(?:ifname\s+)?(.+?)\s*$',re.I)}
 out=[]; cur=None
 for line in text.replace('\r','').splitlines():
  m=pats['local_port'].search(line)
  if m:
   if cur: out.append(LldpNeighbor(**cur))
   cur={'local_port':m.group(1),'neighbor_mac':'','neighbor_name':'','neighbor_ip':'','neighbor_port':''}; continue
  if not cur: continue
  for k,p in pats.items():
   if k=='local_port': continue
   m=p.search(line)
   if m: cur[k]=norm_mac(m.group(1)) if k=='neighbor_mac' else m.group(1).strip(); break
 if cur: out.append(LldpNeighbor(**cur))
 return out
