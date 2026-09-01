from app.core import event_names as e
from app.domain.models import ReadinessResult
class ReadinessService:
 def __init__(self,bus,rules): self.bus=bus; self.rules=rules
 def evaluate(self,context):
  checks=[r.evaluate(context) for r in self.rules]
  blockers=[x.code for x in checks if x.status=='FAIL']; warnings=[x.code for x in checks if x.status=='WARNING']
  result=ReadinessResult(not blockers,'READY' if not blockers else 'BLOCKED',checks,blockers,warnings)
  self.bus.publish(e.READINESS_EVALUATED,result=result); return result
