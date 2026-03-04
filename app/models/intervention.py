from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.models.base import Base

class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)

    intervention_type = Column(String, nullable=False)
    reason = Column(String, nullable=False)

    focus_before = Column(Float, nullable=True)
    focus_after = Column(Float, nullable=True)
    reward = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
