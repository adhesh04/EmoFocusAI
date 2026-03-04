from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.session import Session as StudySession
from app.models.emotion_log import EmotionLog
from app.schemas.emotion import EmotionCreate, EmotionOut
from app.models.user import User

router = APIRouter(prefix="/emotion", tags=["Emotion"])

@router.post("/log", response_model=EmotionOut)
def log_emotion(
    data: EmotionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = (
        db.query(StudySession)
        .filter(
            StudySession.id == data.session_id,
            StudySession.user_id == current_user.id,
            StudySession.is_active == True
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Active session not found")

    log = EmotionLog(
        session_id=data.session_id,
        emotion=data.emotion,
        confidence=data.confidence
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
