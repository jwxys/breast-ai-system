from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, ForeignKey, Text, DateTime, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Visit(Base):
    """随访记录表"""
    __tablename__ = "visit"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)
    visit_no = Column(String(32), unique=True, nullable=False)
    visit_date = Column(Date, nullable=False, index=True)
    visit_type = Column(String(32), nullable=False)
    
    # 临床检查
    chief_complaint = Column(Text)
    present_illness = Column(Text)
    past_history = Column(Text)
    family_history = Column(Text)
    
    # 影像学检查
    birads_category = Column(String(8), index=True)
    
    # 审计字段
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # 关联
    patient = relationship("Patient", back_populates="visits")
    reports = relationship("Report", back_populates="visit")
