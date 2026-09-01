class FakeSettings:
 def __init__(self,enabled=True): self.enabled=enabled
 def get_bool(self,*args): return self.enabled
class FakeBus:
 def __init__(self): self.events=[]
 def publish(self,name,**payload): self.events.append((name,payload))
class FakeRepo:
 def __init__(self): self.saved=[]; self.result=('UNKNOWN',None,'No match')
 def save(self,rack,devices): self.saved.append((rack,devices))
 def identity_matches(self,*args): return self.result
class FakeTransport:
 def __init__(self,outputs): self.outputs=outputs; self.commands=[]
 def run(self,command): self.commands.append(command); return self.outputs.get(command,'')
