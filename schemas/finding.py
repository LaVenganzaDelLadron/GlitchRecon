from pydantic import BaseModel

class Finding(BaseModel):
    scan_id: int
    title: str
    severity: str
    description: str
    evidence: str
    remediation: str
    cve: str
    cvss: str