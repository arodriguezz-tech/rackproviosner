"""Reusable test doubles. They keep service tests isolated and deterministic."""
from collections import defaultdict

class FakeRepository:
    def __init__(self):
        self.saved = []
        self.match_result = ("UNKNOWN", None, "No match")
    def save(self, rack, devices): self.saved.append((rack, devices))
    def identity_matches(self, rack_serial, serial, mac): return self.match_result

class FakeEventBus:
    def __init__(self): self.events = []
    def publish(self, name, **payload): self.events.append((name, payload))
    def events_named(self, name): return [p for n, p in self.events if n == name]

class FakeSettings:
    def __init__(self, inventory_enabled=True): self.inventory_enabled = inventory_enabled
    def get_bool(self, section, key, default=False):
        return self.inventory_enabled if (section, key) == ("inventory", "enabled") else default
