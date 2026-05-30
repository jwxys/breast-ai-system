from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class Diagnosis(Base):
    """诊断记录表"""
    __tablename__ = "diagnosis"
    
    id = Column(Integer, primary_key=True, index=True)
    lesion_id = Column(Integer, unique=True)
    diagnosis_no = Column(String(32), unique=True, nullable=False)
    diagnosis_type = Column(String(32), index=True)
    diagnosis_date = Column(Date, nullable=False, index=True)
    
    # 诊断结果
    malignancy = Column(String(16))
    
    # 状态
    status = Column(String(16), default='draft', index=True)
    
    # 审计字段
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    reports = relationship("Report", back_populates="diagnosis")
