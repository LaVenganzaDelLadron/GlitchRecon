"""Finding correlation helpers that operate only on scanner evidence."""
from __future__ import annotations
from collections import defaultdict
from app.models.schemas import Finding

class FindingCorrelation:
    """Groups already discovered findings by scanner evidence characteristics."""
    def correlate(self, findings:list[Finding])->dict[str,list[str]]:
        """Return finding IDs grouped by their observed scanner category prefix."""
        groups:dict[str,list[str]]=defaultdict(list)
        for finding in findings: groups[finding.scanner_id.split(".",1)[0]].append(finding.id)
        return dict(groups)
