from datetime import datetime

from pydantic import BaseModel

class CreateScan(BaseModel):
    project_id: int
    target_id: int
    scanner: str
    status: str
    started_at: datetime
    finished_at: datetime