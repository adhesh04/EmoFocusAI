from pydantic import BaseModel, Field
from datetime import datetime

class DecisionRequest(BaseModel):
    session_id: int = Field(default=1)

class DecisionResponse(BaseModel):
    intervention_type: str
    reason: str
    created_at: datetime