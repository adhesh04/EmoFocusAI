from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.session import Session as StudySession
from app.models.focus_log import FocusLog
from app.models.emotion_log import EmotionLog
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# -----------------------------
# 1️⃣ Session Summary
# -----------------------------
@router.get("/session/{session_id}/summary")
def session_summary(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate session ownership
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Aggregate focus stats
    stats = db.query(
        func.avg(FocusLog.focus_score),
        func.max(FocusLog.focus_score),
        func.min(FocusLog.focus_score),
        func.count(FocusLog.id)
    ).filter(FocusLog.session_id == session_id).first()

    return {
        "avg_focus": round(stats[0] or 0, 3),
        "max_focus": round(stats[1] or 0, 3),
        "min_focus": round(stats[2] or 0, 3),
        "total_frames": stats[3] or 0
    }


# -----------------------------
# 2️⃣ Focus Trend
# -----------------------------
@router.get("/session/{session_id}/focus-trend")
def focus_trend(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    logs = db.query(FocusLog).filter(
        FocusLog.session_id == session_id
    ).order_by(FocusLog.created_at).all()

    return [
        {
            "timestamp": log.created_at,
            "focus": log.focus_score
        }
        for log in logs
    ]


# -----------------------------
# 3️⃣ Emotion Distribution
# -----------------------------
@router.get("/session/{session_id}/emotion-distribution")
def emotion_distribution(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    results = db.query(
        EmotionLog.emotion,
        func.count(EmotionLog.id)
    ).filter(
        EmotionLog.session_id == session_id
    ).group_by(EmotionLog.emotion).all()

    return {emotion: count for emotion, count in results}