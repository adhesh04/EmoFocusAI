from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SessionCreate(BaseModel):
    pass  # no body needed, backend controls start time

class SessionOut(BaseModel):
    id: int
    start_time: datetime
    end_time: Optional[datetime]
    is_active: bool

    # class Config:
    #     orm_mode = True
    model_config = {
    "from_attributes": True
}
