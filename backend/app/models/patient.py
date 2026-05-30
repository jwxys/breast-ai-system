from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class Patient(Base):
    # Add reports relationship at the end
    """患者基本信息表"""
    __tablename__ = "patient"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_no = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(64), nullable=False)
    gender = Column(String(1), nullable=False, default='F')
    birth_date = Column(Date, nullable=False)
    age = Column(Integer)
    id_card = Column(String(18), unique=True)
    phone = Column(String(20), index=True)
    email = Column(String(128))
    address = Column(Text)
    
    # ⚠️ 中医字段已移除（2026-05-29）
    # 原因：无四诊信息采集（舌象、脉象、问诊），辨证无依据
    # 详见：docs/TCM_INTEGRATION_ANALYSIS_AND_FIX.md
    # constitution = Column(String(32), index=True)
    # constitution_score = Column(Numeric(5, 2))
    # zheng_type = Column(String(32), index=True)
    # zheng_severity = Column(String(8))
    
    # 风险评估
    risk_level = Column(String(16), index=True)
    risk_score = Column(Numeric(5, 2))
    
    # 审计字段
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # 关联
    visits = relationship("Visit", back_populates="patient")
    
    class Config:
        # 允许使用 model_ 前缀的关系
        pass
    reports = relationship('Report', back_populates='patient')
