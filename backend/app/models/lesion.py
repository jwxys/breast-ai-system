from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Lesion(Base):
    """病灶记录表"""
    __tablename__ = "lesion"
    
    id = Column(Integer, primary_key=True, index=True)
    ultrasound_id = Column(Integer, ForeignKey("ultrasound.id"), nullable=False, index=True)
    lesion_no = Column(String(32), unique=True, nullable=False)
    
    # 病灶特征
    size = Column(String(128))
    shape = Column(String(32))
    margin = Column(String(128))
    
    # BI-RADS 分级
    birads_category = Column(String(8), index=True)
    
    # 病理结果
    pathology_type = Column(String(64))
    molecular_type = Column(String(32))
    er_status = Column(String(8))
    pr_status = Column(String(8))
    her2_status = Column(String(8))
    ki67_value = Column(Numeric(5, 2))
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
