from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Numeric, LargeBinary, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import sqlalchemy as sa

from shared.database import Base


class UltrasoundExam(Base):
    """超声检查表"""
    
    __tablename__ = "ultrasound_exam"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_id = Column(Integer, ForeignKey("visit.id"), nullable=False, index=True)
    exam_no = Column(String(32), unique=True, nullable=False)
    exam_date = Column(DateTime, nullable=False, default=sa.func.current_timestamp())
    
    # 图像信息
    image_path = Column(String(512), nullable=False)
    image_hash = Column(String(64))
    image_size = Column(Integer)
    image_dimension = Column(JSON)
    
    # AI 分析结果
    ai_analysis = Column(JSON)
    ai_model_version = Column(String(32))
    ai_confidence = Column(Numeric(5, 4))
    
    # BI-RADS 评估
    birads_category = Column(String(8), index=True)
    birads_features = Column(JSON)
    birads_ai_predicted = Column(String(8))
    
    # 病灶数量
    lesion_count = Column(Integer, default=0)
    
    # 审核状态
    review_status = Column(String(16), default='pending')  # pending/reviewed/approved
    reviewed_by = Column(Integer)
    reviewed_at = Column(DateTime)
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer)
    
    # 关系
    visit = relationship("Visit", back_populates="ultrasounds")
    lesions = relationship("Lesion", back_populates="ultrasound", lazy="selectin")
    
    def __repr__(self):
        return f"<UltrasoundExam(id={self.id}, exam_no='{self.exam_no}')>"


class Lesion(Base):
    """病灶表"""
    
    __tablename__ = "lesion"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ultrasound_id = Column(Integer, ForeignKey("ultrasound_exam.id"), nullable=False, index=True)
    lesion_no = Column(String(32), unique=True, nullable=False)
    
    # 位置信息
    location = Column(String(32))  # 左/右乳 + 象限
    quadrant = Column(String(8))   # 外上/外下/内上/内下/乳晕后
    distance_from_nipple = Column(Numeric(5, 2))  # 距乳头距离 (mm)
    
    # 大小测量
    max_diameter = Column(Numeric(6, 2))  # 最大径 (mm)
    perpendicular_diameter = Column(Numeric(6, 2))  # 垂直径 (mm)
    volume = Column(Numeric(8, 2))  # 体积 (mm³)
    
    # 影像特征
    shape = Column(String(16))  # 规则/不规则
    orientation = Column(String(16))  # 平行/非平行
    margin = Column(String(16))  # 清晰/模糊
    edge = Column(String(16))  # 光滑/分叶/毛刺
    echo_pattern = Column(String(16))  # 无/低/等/高/混合回声
    calcification = Column(String(16))  # 无/微/粗钙化
    posterior_feature = Column(String(16))  # 增强/衰减/无变化
    
    # AI 分割
    segmentation_mask = Column(LargeBinary)
    segmentation_dice = Column(Numeric(5, 4))
    
    # 病理结果
    pathology_status = Column(String(16), index=True)  # 待病理/良性/恶性
    pathology_type = Column(String(64))
    pathology_date = Column(DateTime)
    pathology_report_id = Column(String(64))
    
    # 分子分型（恶性时）
    er_status = Column(String(8))
    pr_status = Column(String(8))
    her2_status = Column(String(8))
    ki67_index = Column(Numeric(5, 2))
    molecular_subtype = Column(String(32), index=True)
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    ultrasound = relationship("UltrasoundExam", back_populates="lesions")
    diagnosis = relationship("Diagnosis", back_populates="lesion", uselist=False)
    
    def __repr__(self):
        return f"<Lesion(id={self.id}, lesion_no='{self.lesion_no}', location='{self.location}')>"
