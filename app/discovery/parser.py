import re
from app.domain.models import DeviceIdentity
class IdentityParser:
 def __init__(self,patterns): self.patterns=patterns
 def parse(self,outputs):
  blob='\n'.join(outputs.values())
  def get(key):
   m=re.search(self.patterns[key],blob); return m.group(1).strip() if m else ''
  return DeviceIdentity(serial=get('serial'),mac=get('mac'),model=get('model'))
