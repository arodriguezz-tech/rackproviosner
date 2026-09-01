"""Synchronous in-process event bus used for module communication.

Layer rule: this module should depend only on lower-level modules documented in ARCHITECTURE.md.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

@dataclass(frozen=True)
class Event:
    name: str
    payload: dict[str,Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))

class EventBus:
    def __init__(self): self._handlers=defaultdict(list)
    def subscribe(self,name:str,handler:Callable[[Event],None]): self._handlers[name].append(handler)
    def unsubscribe(self,name,handler):
        if handler in self._handlers.get(name,[]): self._handlers[name].remove(handler)
    def publish(self,name:str,**payload):
        event=Event(name,payload)
        for handler in tuple(self._handlers.get(name,())): handler(event)
        for handler in tuple(self._handlers.get("*",())): handler(event)
        return event
