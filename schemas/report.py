from pydantic import BaseModel

class CreateReport(BaseModel):
    project_id: int
    name: str
    format: str
    path: str
    generated_by: str