from app.core import event_names as e
from app.domain.models import DiscoveryResult
from .lldp import parse
class DiscoveryService:
 COMMANDS=[('version','show version'),('eeprom','show platform syseeprom'),('lldp','show lldp neighbors')]
 def __init__(self,transport,parser,bus): self.transport=transport; self.parser=parser; self.bus=bus
 def discover(self):
  outputs={name:self.transport.run(cmd) for name,cmd in self.COMMANDS}
  result=DiscoveryResult(self.parser.parse(outputs),parse(outputs['lldp']),outputs)
  self.bus.publish(e.DISCOVERY_COMPLETED,result=result); return result
 def lldp_only(self):
  raw=self.transport.run('show lldp neighbors'); neighbors=parse(raw); self.bus.publish(e.LLDP_COMPLETED,neighbors=neighbors,raw_output=raw); return neighbors
