from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class EmotionLog(Base):
    __tablename__ = "emotion_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)

    emotion = Column(String, nullable=False)       # e.g. "stress", "fatigue"
    confidence = Column(Float, nullable=False)     # model confidence

    created_at = Column(DateTime(timezone=True), server_default=func.now())
