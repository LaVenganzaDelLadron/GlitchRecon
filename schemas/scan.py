from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class CreateScan(BaseModel):
    project_id: int
    target_id: int
    scanner: str
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class PlanScan(BaseModel):
    project_id: int
    target_id: int
    goal: str
    provider: str = "ollama"
