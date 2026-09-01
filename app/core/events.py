"""Minimal synchronous Event Bus for UI/service communication."""

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
        self.published_events: list[Event] = []

    def subscribe(self, event_name: str, handler: Callable[[Event], None]) -> None:
        self._handlers[event_name].append(handler)

    def publish(self, event_name: str, **payload: Any) -> Event:
        event = Event(event_name, payload)
        self.published_events.append(event)
        for handler in tuple(self._handlers.get(event_name, ())):
            handler(event)
        return event
