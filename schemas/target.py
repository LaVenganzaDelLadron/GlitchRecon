from pydantic import BaseModel

class CreateTarget(BaseModel):
    project_id: int
    type: str
    value: str
    notes: str