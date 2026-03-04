from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class JournalCreate(BaseModel):
    session_id: int
    text: str

class JournalOut(BaseModel):
    id: int
    raw_text: str
    dominant_emotion: Optional[str]
    stress_score: Optional[float]
    cognitive_state: Optional[str]
    summary: Optional[str]
    created_at: datetime

    model_config = {
    "from_attributes": True
}
