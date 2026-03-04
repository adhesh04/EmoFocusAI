from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.db.session import get_db
from app.models.session import Session as StudySession
from app.schemas.session import SessionOut
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/start", response_model=SessionOut)
def start_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    active_session = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == current_user.id,
            StudySession.is_active == True
        )
        .first()
    )

    if active_session:
        raise HTTPException(status_code=400, detail="Session already active")

    session = StudySession(user_id=current_user.id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.post("/end/{session_id}", response_model=SessionOut)
def end_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = (
        db.query(StudySession)
        .filter(
            StudySession.id == session_id,
            StudySession.user_id == current_user.id,
            StudySession.is_active == True
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Active session not found")

    session.end_time = datetime.utcnow()
    session.is_active = False
    db.commit()
    db.refresh(session)
    return session

@router.get("/", response_model=List[SessionOut])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(StudySession)
        .filter(StudySession.user_id == current_user.id)
        .order_by(StudySession.start_time.desc())
        .all()
    )
