"""Small synchronous event bus used for in-process module communication."""
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass(frozen=True)
class Event:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[Callable[[Event], None]]] = defaultdict(list)

    def subscribe(self, name: str, handler: Callable[[Event], None]) -> None:
        self._handlers[name].append(handler)

    def publish(self, name: str, **payload: Any) -> Event:
        event = Event(name=name, payload=payload)
        for handler in tuple(self._handlers.get(name, ())):
            handler(event)
        for handler in tuple(self._handlers.get("*", ())):
            handler(event)
        return event
