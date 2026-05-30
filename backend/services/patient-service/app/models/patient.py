from sqlalchemy import Column, String, Integer, Date, Boolean, Enum, Numeric, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import sqlalchemy as sa

from shared.database import Base


class Patient(Base):
    """患者基本信息表"""
    
    __tablename__ = "patient"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 基本信息
    patient_no = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(64), nullable=False)
    gender = Column(String(1), default='F')
    birth_date = Column(Date, nullable=False)
    id_card = Column(String(18), unique=True)
    phone = Column(String(20))
    email = Column(String(128))
    address = Column(String(256))
    
    # 中医信息
    constitution = Column(String(32), index=True)
    constitution_score = Column(Numeric(5, 2))
    zheng_type = Column(String(32), index=True)
    zheng_severity = Column(String(8))
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 关系
    visits = relationship("Visit", back_populates="patient", lazy="selectin")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, patient_no='{self.patient_no}', name='{self.name}')>"
