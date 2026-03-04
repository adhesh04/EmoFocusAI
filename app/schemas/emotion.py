from pydantic import BaseModel
from datetime import datetime

class EmotionCreate(BaseModel):
    session_id: int
    emotion: str
    confidence: float

class EmotionOut(BaseModel):
    id: int
    emotion: str
    confidence: float
    created_at: datetime

    model_config = {
    "from_attributes": True
}
