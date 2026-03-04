from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

DIGITAL_STATE = {}

@router.post("/signal")
def update_digital_signal(
    session_id: int,
    window_name: str,
    window_score: float,
    user=Depends(get_current_user)
):
    DIGITAL_STATE[session_id] = window_score
    return {"status": "ok"}
