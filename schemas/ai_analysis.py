from pydantic import BaseModel

class CreateAIAnalysisRequest(BaseModel):
    finding_id: int
    model: str
    prompt: str
    response: str