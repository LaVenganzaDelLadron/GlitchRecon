from pydantic import BaseModel

class CreateProject(BaseModel):
    owner_id: int
    name: str
    description: str
    scope: str
    status: str