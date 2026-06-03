from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class UltrasoundExam(Base):
    """超声图像表"""
    __tablename__ = "ultrasound"
    
    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visit.id"), nullable=False, index=True)
    image_no = Column(String(32), unique=True, nullable=False)
    image_path = Column(String(512), nullable=False, index=True)
    image_type = Column(String(32))
    
    # 图像质量
    quality_score = Column(Numeric(5, 2))
    
    # AI 分析结果
    ai_score = Column(Numeric(5, 2))
    ai_prediction = Column(String(32))
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    visit = relationship("Visit")
    tcm_correlations = relationship("ImagingTCMCorrelation", back_populates="ultrasound", cascade="all, delete-orphan")
