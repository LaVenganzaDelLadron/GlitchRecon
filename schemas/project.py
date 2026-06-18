from pydantic import BaseModel

class CreateProject(BaseModel):
    name: str
    description: str
    scope: str
    status: str
