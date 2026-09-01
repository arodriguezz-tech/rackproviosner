"""Inventory business rules and event publication."""
from app.core import event_names as events
from app.inventory.repository import normalize_mac, normalize_serial

REQUIRED_ROLES = {"MX", "NS1", "NS2"}

class InventoryService:
    def __init__(self, repository, bus, settings):
        self.repository = repository
        self.bus = bus
        self.settings = settings

    def save_record(self, rack: dict, devices: list[dict]) -> None:
        """Validate, normalize, persist, then publish inventory.saved."""
        clean_rack = self._normalize_rack(rack)
        clean_devices = self._normalize_devices(devices)
        self._validate_rack(clean_rack)
        self._validate_roles(clean_devices)
        self._validate_devices(clean_devices)
        self._validate_duplicates(clean_devices)
        self.repository.save(clean_rack, clean_devices)
        self.bus.publish(events.INVENTORY_SAVED, rack_serial=clean_rack["rack_serial"])

    def verify(self, rack_serial, identity):
        if not self.settings.get_bool("inventory", "enabled", False):
            result = ("DISABLED", None, "Inventory matching disabled")
        else:
            result = self.repository.identity_matches(rack_serial, identity.serial, identity.mac)
        self.bus.publish(events.INVENTORY_VERIFIED, state=result[0], role=result[1],
                         reason=result[2], rack_serial=rack_serial)
        return result

    @staticmethod
    def _normalize_rack(rack):
        return {"rack_serial": rack.get("rack_serial", "").strip(),
                "rack_sku": rack.get("rack_sku", "").strip(),
                "rack_bom": rack.get("rack_bom", "").strip(),
                "rack_asset_tag": rack.get("rack_asset_tag", "").strip()}

    @staticmethod
    def _normalize_devices(devices):
        return [{"role": d.get("role", "").strip().upper(),
                 "model": d.get("model", "").strip(),
                 "serial": normalize_serial(d.get("serial", "")),
                 "mac": normalize_mac(d.get("mac", "")),
                 "notes": d.get("notes", "").strip()} for d in devices]

    @staticmethod
    def _validate_rack(rack):
        if not rack["rack_serial"]: raise ValueError("Rack Serial is required.")
        if not rack["rack_sku"]: raise ValueError("Rack SKU is required.")

    @staticmethod
    def _validate_roles(devices):
        roles = [d["role"] for d in devices]
        duplicates = {r for r in roles if roles.count(r) > 1}
        if duplicates:
            raise ValueError("Duplicate roles: " + ", ".join(sorted(duplicates)))
        missing = REQUIRED_ROLES - set(roles)
        if missing:
            raise ValueError("Missing roles: " + ", ".join(sorted(missing)))

    @staticmethod
    def _validate_devices(devices):
        for d in devices:
            if not d["model"]: raise ValueError(f"{d['role']} model is required.")
            if not d["serial"] and not d["mac"]:
                raise ValueError(f"{d['role']} requires a serial number or MAC address.")
            if d["mac"] and len(d["mac"]) != 12:
                raise ValueError(f"{d['role']} MAC address is invalid.")

    @staticmethod
    def _validate_duplicates(devices):
        serials = [d["serial"] for d in devices if d["serial"]]
        macs = [d["mac"] for d in devices if d["mac"]]
        if len(serials) != len(set(serials)): raise ValueError("Duplicate device serial detected.")
        if len(macs) != len(set(macs)): raise ValueError("Duplicate MAC address detected.")
