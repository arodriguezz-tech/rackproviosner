import re
from app.domain.models import DeviceIdentity
class IdentityParser:
    def __init__(self,settings): self.settings=settings
    def parse(self,outputs):
        blob="\n".join(outputs.values()); c=self.settings.load()
        def get(key):
            m=re.search(c.get("discovery",key),blob); return m.group(1).strip() if m else ""
        return DeviceIdentity(serial=get("serial_regex"),mac=get("mac_regex"),model=get("model_regex"))
