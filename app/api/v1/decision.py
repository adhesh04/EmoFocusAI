from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.decision import DecisionRequest, DecisionResponse
from app.services.decision_service import make_decision
from app.models.user import User
from app.models.intervention import Intervention

router = APIRouter(prefix="/decision", tags=["Decision"])

@router.post("/trigger", response_model=DecisionResponse)
def trigger_decision(
    data: DecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # This calls the Contextual Bandit logic we built
        intervention = make_decision(data.session_id, current_user.id, db)
        return {
            "intervention_type": intervention.intervention_type,
            "reason": intervention.reason,
            "created_at": intervention.created_at
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/history/{session_id}")
def get_intervention_history(
    session_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # This lets you see the 'reward' column for your safety test
    interventions = db.query(Intervention).filter(
        Intervention.session_id == session_id,
        Intervention.user_id == current_user.id
    ).all()
    return interventions