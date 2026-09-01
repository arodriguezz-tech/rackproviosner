from collections import defaultdict
from dataclasses import dataclass,field
from typing import Any,Callable
@dataclass(frozen=True)
class Event:
 name:str; payload:dict[str,Any]=field(default_factory=dict)
class EventContractError(ValueError): pass
class EventBus:
 def __init__(self,contracts=None): self.handlers=defaultdict(list); self.contracts=contracts or {}; self.published_events=[]
 def subscribe(self,event_name,handler): self.handlers[event_name].append(handler)
 def unsubscribe(self,event_name,handler):
  if handler in self.handlers.get(event_name,[]): self.handlers[event_name].remove(handler)
 def publish(self,event_name,**payload):
  required=self.contracts.get(event_name)
  if required is not None:
   missing=set(required)-set(payload)
   if missing: raise EventContractError(f"{event_name} missing: {', '.join(sorted(missing))}")
  event=Event(event_name,payload); self.published_events.append(event)
  for h in tuple(self.handlers.get(event_name,())): h(event)
  for h in tuple(self.handlers.get('*',())): h(event)
  return event
