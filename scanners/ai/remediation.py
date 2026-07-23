"""Deterministic remediation guidance for existing findings."""
from __future__ import annotations
from app.models.schemas import Finding
class RemediationAdvisor:
    """Maps observed finding families to concise remediation starting points."""
    def recommend(self,finding:Finding)->str:
        """Return guidance based on scanner ID, without asserting new vulnerabilities."""
        family=finding.scanner_id.split(".",1)[0]
        guidance={"misconfiguration":"Review the observed configuration and apply the relevant secure default.","secrets":"Remove exposed material, rotate affected credentials, and prevent future publication.","client_side":"Review the observed browser control and enforce an appropriate policy.","http":"Review the observed HTTP behavior against the application’s requirements."}
        return guidance.get(family,"Review the scanner evidence and apply the control appropriate to the confirmed observation.")
