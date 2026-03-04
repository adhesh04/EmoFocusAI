from pydantic import BaseModel
from datetime import datetime

class FocusCreate(BaseModel):
    session_id: int
    focus_score: float

class FocusOut(BaseModel):
    id: int
    focus_score: float
    created_at: datetime

    model_config = {
    "from_attributes": True
}
