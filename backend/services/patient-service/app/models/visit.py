from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, JSON, Enum as SQLEnum, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import sqlalchemy as sa

from shared.database import Base


class Visit(Base):
    """随访记录表"""
    
    __tablename__ = "visit"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)
    visit_no = Column(String(32), unique=True, nullable=False)
    visit_date = Column(Date, nullable=False, default=sa.func.current_date())
    visit_type = Column(String(16), nullable=False)  # 初诊/复诊/随访
    
    # 临床信息
    chief_complaint = Column(String(512))
    history_present_illness = Column(String(2048))
    physical_exam = Column(JSON)
    
    # 风险评估
    risk_level = Column(String(16), index=True)  # low/medium/high/very_high
    risk_factors = Column(JSON)
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    
    # 关系
    patient = relationship("Patient", back_populates="visits")
    ultrasounds = relationship("UltrasoundExam", back_populates="visit", lazy="selectin")
    
    def __repr__(self):
        return f"<Visit(id={self.id}, visit_no='{self.visit_no}', patient_id={self.patient_id})>"
