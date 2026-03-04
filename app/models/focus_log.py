from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class FocusLog(Base):
    __tablename__ = "focus_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)

    focus_score = Column(Float, nullable=False)  # 0.0 → 1.0

    created_at = Column(DateTime(timezone=True), server_default=func.now())
