from app.domain.models import DiscoveryResult
from .lldp import parse as parse_lldp
class DiscoveryService:
    COMMANDS=[("version","show version",2200),("eeprom","show platform syseeprom",2600),("lldp","show lldp neighbors",2800)]
    def __init__(self,session,parser,bus):
        self.session=session; self.parser=parser; self.bus=bus; self.queue=[]; self.outputs={}; session.console.connect(lambda text:bus.publish("console.received",text=text)); session.event.connect(self._serial_event)
    def ports(self): return self.session.available_ports()
    def connect(self,port,baud): return self.session.open(port,baud)
    def disconnect(self): self.session.close()
    def discover(self): self.outputs={}; self.queue=list(self.COMMANDS); self.bus.publish("discovery.started"); self._next()
    def lldp_only(self): self.session.run("lldp","show lldp neighbors",2800)
    def _next(self):
        if self.queue: self.session.run(*self.queue.pop(0))
        else:
            result=DiscoveryResult(self.parser.parse(self.outputs),parse_lldp(self.outputs.get("lldp","")),dict(self.outputs)); self.bus.publish("discovery.completed",result=result)
    def _serial_event(self,name,payload):
        self.bus.publish(name,**payload)
        if name=="serial.command.finished": self.outputs[payload["name"]]=payload["output"]; self.bus.publish("discovery.command.completed",command=payload["name"]); self._next() if self.queue else self._next()
