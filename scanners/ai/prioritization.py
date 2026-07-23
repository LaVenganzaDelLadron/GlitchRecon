"""Evidence-based priority calculation without vulnerability discovery."""
from __future__ import annotations
from app.models.schemas import Finding,Severity
class FindingPrioritizer:
    """Ranks existing scanner findings by declared severity and confidence."""
    _WEIGHTS={Severity.CRITICAL:5,Severity.HIGH:4,Severity.MEDIUM:3,Severity.LOW:2,Severity.INFO:1}
    def prioritize(self,findings:list[Finding])->list[Finding]:
        """Return a stable highest-risk-first ordering of supplied findings."""
        return sorted(findings,key=lambda item:(self._WEIGHTS[item.severity],item.confidence),reverse=True)
