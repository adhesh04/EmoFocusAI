from sqlalchemy.orm import Session
from datetime import datetime

from app.models.focus_log import FocusLog
from app.models.emotion_log import EmotionLog
from app.models.journal import Journal
from app.models.session import Session as StudySession
from app.models.intervention import Intervention
from app.ml.decision_models.contextual_bandit import select_intervention

def get_user_intervention_stats(user_id: int, db: Session):
    stats = {}

    rows = (
        db.query(Intervention)
        .filter(
            Intervention.user_id == user_id,
            Intervention.reward.isnot(None)
        )
        .all()
    )

    for row in rows:
        action = row.intervention_type
        if action not in stats:
            stats[action] = {"total": 0.0, "count": 0}

        stats[action]["total"] += row.reward
        stats[action]["count"] += 1

    # Convert to avg reward
    for action in stats:
        stats[action]["avg_reward"] = (
            stats[action]["total"] / stats[action]["count"]
        )

    return stats


def make_decision(session_id: int, user_id: int, db: Session):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == user_id
    ).first()

    if not session:
        raise ValueError("Session not found")

    # Latest focus
    focus_log = (
        db.query(FocusLog)
        .filter(FocusLog.session_id == session_id)
        .order_by(FocusLog.created_at.desc())
        .first()
    )
    focus_before = focus_log.focus_score if focus_log else 0.5

    # Build user-specific policy
    user_stats = get_user_intervention_stats(user_id, db)
    intervention_type = select_intervention(user_stats)

    intervention = Intervention(
        user_id=user_id,
        session_id=session_id,
        intervention_type=intervention_type,
        reason="Selected via contextual bandit policy",
        focus_before=focus_before
    )

    db.add(intervention)
    db.commit()
    db.refresh(intervention)

    return intervention
