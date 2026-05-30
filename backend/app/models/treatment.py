from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class TreatmentPlan(Base):
    """治疗计划表"""
    __tablename__ = "treatment"
    
    id = Column(Integer, primary_key=True, index=True)
    diagnosis_id = Column(Integer, ForeignKey("diagnosis.id"), nullable=False, index=True)
    treatment_no = Column(String(32), unique=True, nullable=False)
    treatment_type = Column(String(64), index=True)
    
    # 状态
    status = Column(String(16), default='planned', index=True)
    
    # 审计字段
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TCMPrescription(Base):
    """中医处方表"""
    __tablename__ = "tcm_prescription"
    
    id = Column(Integer, primary_key=True, index=True)
    treatment_id = Column(Integer, ForeignKey("treatment.id"), nullable=False)
    prescription_name = Column(String(256))
    ingredients = Column(Text)
    usage = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
