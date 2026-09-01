class InventoryService:
    def __init__(self,repo,bus,settings): self.repo=repo; self.bus=bus; self.settings=settings
    def save_record(self,rack,devices): self.repo.save(rack,devices); self.bus.publish("inventory.saved",rack_serial=rack["rack_serial"])
    def verify(self,rack_serial,identity):
        if not self.settings.get_bool("inventory","enabled",False):
            result=("DISABLED",None,"Inventory matching disabled")
        else: result=self.repo.identity_matches(rack_serial,identity.serial,identity.mac)
        self.bus.publish("inventory.verified",state=result[0],role=result[1],reason=result[2],rack_serial=rack_serial); return result
