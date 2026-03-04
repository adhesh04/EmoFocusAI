from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.session import Session as StudySession
from app.models.journal import Journal
from app.schemas.journal import JournalCreate, JournalOut
from app.services.journal_service import analyze_journal
from app.models.user import User

router = APIRouter(prefix="/journal", tags=["Journal"])

@router.post("/log", response_model=JournalOut)
def log_journal(
    data: JournalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = (
        db.query(StudySession)
        .filter(
            StudySession.id == data.session_id,
            StudySession.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    analysis = analyze_journal(data.text)

    journal = Journal(
        session_id=data.session_id,
        raw_text=data.text,
        dominant_emotion=analysis.get("emotion"),
        stress_score=analysis.get("stress_score"),
        cognitive_state=analysis.get("cognitive_state"),
        summary=analysis.get("summary")
    )

    db.add(journal)
    db.commit()
    db.refresh(journal)
    return journal
