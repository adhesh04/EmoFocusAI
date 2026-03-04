from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.session import Session as StudySession
from app.models.focus_log import FocusLog
from app.models.intervention import Intervention
from app.models.emotion_log import EmotionLog
from app.schemas.focus import FocusCreate, FocusOut
from app.models.user import User
import math
from datetime import datetime, timezone
# actual perception model -------------------------
import base64
import cv2
import numpy as np
from app.services.focus_service import FocusService
from pydantic import BaseModel

from app.services.deep_policy_bandit import DeepPolicyBandit
bandit = DeepPolicyBandit()

# from app.services.intervention_bandit import InterventionBandit
# bandit = InterventionBandit()

focus_service = FocusService()
# ---------------- Intervention Memory ----------------
low_focus_tracker = {}  # session_id → consecutive low frames
FOCUS_THRESHOLD = 0.55
# LOW_FOCUS_LIMIT = 3   # ~ 4.5 seconds (since frame every 1.5s)
LOW_FOCUS_LIMIT = 8
#---------------------------------------------------

router = APIRouter(prefix="/focus", tags=["Focus"])

@router.post("/log", response_model=FocusOut)
def log_focus(
    data: FocusCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Verify the session exists and belongs to the user
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

# 2. Save the new Focus Log
    log = FocusLog(
        session_id=data.session_id,
        focus_score=data.focus_score
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    # 3. RL REWARD LOGIC: Update the latest intervention
    # We find the most recent intervention for this session that doesn't have a reward yet
    intervention = (
        db.query(Intervention)
        .filter(
            Intervention.session_id == data.session_id,
            Intervention.reward.is_(None)
        )
        .order_by(Intervention.created_at.desc())
        .first()
    )

    # if intervention:
        # intervention.focus_after = data.focus_score
        # intervention.reward = intervention.focus_after - intervention.focus_before
        # db.commit()

        # # 🔥 NEW: Update bandit
        # # bandit.update(
        # #     user_id=current_user.id,
        # #     action=intervention.intervention_type,
        # #     reward=intervention.reward
        # # )
        # bandit.update(intervention.reward)

    return log

#---------------------------------------------
#actual perception model continuation
#---------------------------------------------
# @router.post("/frame", response_model=FocusOut)
# def process_focus_frame(
#     session_id: int,
#     image_base64: str,
#     digital_score: float,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):

class FrameInput(BaseModel):
    session_id: int
    image_base64: str
    digital_score: float


@router.post("/frame")
def process_focus_frame(
    data: FrameInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    
):
    # Extract values from request body
    session_id = data.session_id
    image_base64 = data.image_base64
    digital_score = data.digital_score

    # 1. Verify session
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

    # 2. Decode image
    try:
        # Handle the base64 string (removing the header if present in future)
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
            
        img_bytes = base64.b64decode(image_base64)
        img_np = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image data")

    # 3. Run perception (The ML Brain)
    result = focus_service.process_frame(frame, digital_score)

    if not result:
        # Return 204 if the frame was skipped due to FPS limit
        raise HTTPException(status_code=204, detail="Frame skipped")

    focus_score = result["focus"]

    # 4. Save focus log (The exact same logic as your manual /log)
    log = FocusLog(
        session_id=session_id,
        focus_score=focus_score
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    emotion_log = EmotionLog(
    session_id=session_id,
    emotion=result["emotion"],
    confidence=0.5  # since heuristic model
    )
    db.add(emotion_log)
    db.commit()


    # ---------------- Intervention Trigger Logic ----------------
    triggered = False
    selected_action = None

    if focus_score < FOCUS_THRESHOLD:
        low_focus_tracker[session_id] = low_focus_tracker.get(session_id, 0) + 1
    else:
        low_focus_tracker[session_id] = 0

    # If sustained low focus
    if low_focus_tracker[session_id] >= LOW_FOCUS_LIMIT:
        
        # Find previous intervention
        previous = (
            db.query(Intervention)
            .filter(
                Intervention.session_id == session_id,
                Intervention.reward.is_(None)
                )
            .order_by(Intervention.created_at.desc())
            .first()
        )

        if previous and previous.reward is None:
            now = datetime.now(timezone.utc)
            duration_seconds = (now - previous.created_at).total_seconds()

            reward = math.log(duration_seconds + 1)

            previous.reward = reward
            db.commit()

            print("Reward computed (log duration):", reward)

            bandit.update(reward)

        # Prevent duplicate spam
        existing = db.query(Intervention).filter(
            Intervention.session_id == session_id,
            Intervention.reward.is_(None)
        ).first()
        if existing:
            selected_action = existing.intervention_type
        else:
            # selected_action = bandit.select_action(db, current_user.id)
            selected_action = bandit.select_action(
                focus_score,
                digital_score,
                result["emotion"],
                current_user.id
            )
            print("Saving intervention:", selected_action)
            intervention = Intervention(
                user_id=current_user.id,
                session_id=session_id,
                intervention_type=selected_action,
                reason="Sustained low focus",
                focus_before=focus_score
            )
            db.add(intervention)
            db.commit()
        # if not existing:
        #     selected_action = bandit.select_action(db, current_user.id)

        #     intervention = Intervention(
        #         user_id=current_user.id,
        #         session_id=session_id,
        #         intervention_type=selected_action,
        #         reason="Sustained low focus",
        #         focus_before=focus_score
        #     )
        #     db.add(intervention)
        #     db.commit()

        triggered = True
        low_focus_tracker[session_id] = 0
    # 5. RL reward update (Matches your manual /log perfectly)
    # intervention = (
    #     db.query(Intervention)
    #     .filter(
    #         Intervention.session_id == session_id,
    #         Intervention.reward.is_(None)
    #     )
    #     .order_by(Intervention.created_at.desc())
    #     .first()
    # )

    # if intervention:
    #     intervention.focus_after = focus_score
    #     intervention.reward = intervention.focus_after - intervention.focus_before
    #     db.commit()

    return {
    "focus_score": focus_score,
    "emotion": result["emotion"],
    "intervention_triggered": triggered,
    "intervention_type": selected_action if triggered else None
    }
