from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ScanStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    email = Column(String, nullable=False, index=True)
    project_name = Column(String)
    source = Column(String)  # zip | github
    status = Column(Enum(ScanStatus), default=ScanStatus.pending)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    plan_selected = Column(String)  # laudo | correcao
    health_score_initial = Column(Float)
    health_score_final = Column(Float)
    findings_json = Column(JSON)
    report_hash = Column(String, unique=True, index=True)
    preference_id = Column(String)
    payment_id = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="scans")
