from sqlalchemy import Column, Integer, Text, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)

    raw_text = Column(Text, nullable=False)

    dominant_emotion = Column(String, nullable=True)
    stress_score = Column(Float, nullable=True)      # 0.0 → 1.0
    cognitive_state = Column(String, nullable=True)  # overwhelmed, focused, etc.
    summary = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
