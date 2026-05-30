from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, JSON, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import sqlalchemy as sa

from shared.database import Base


class TreatmentPlan(Base):
    """治疗方案表"""
    
    __tablename__ = "treatment_plan"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    diagnosis_id = Column(Integer, ForeignKey("diagnosis.id"), nullable=False, index=True)
    plan_no = Column(String(32), unique=True, nullable=False)
    
    # 治疗类型
    treatment_category = Column(String(32), index=True)  # 手术/化疗/放疗/内分泌/靶向/中医
    
    # 具体方案
    treatment_name = Column(String(128))
    treatment_detail = Column(JSON)
    
    # 用药信息
    medications = Column(JSON)
    dosage = Column(String(128))
    frequency = Column(String(64))
    duration_weeks = Column(Integer)
    
    # 时间计划
    start_date = Column(Date)
    end_date = Column(Date)
    scheduled_date = Column(Date)
    
    # 执行状态
    status = Column(String(16), default='planned', index=True)
    completion_rate = Column(Numeric(5, 2))
    
    # 疗效评估
    efficacy = Column(String(16))  # CR/PR/SD/PD
    assessment_date = Column(Date)
    
    # 审计字段
    prescribed_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    diagnosis = relationship("Diagnosis", back_populates="treatment_plans")
    prescriptions = relationship("TCMPrescription", back_populates="treatment", lazy="selectin")
    
    def __repr__(self):
        return f"<TreatmentPlan(id={self.id}, plan_no='{self.plan_no}', category='{self.treatment_category}')>"


class TCMPrescription(Base):
    """中药处方表"""
    
    __tablename__ = "tcm_prescription"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    treatment_id = Column(Integer, ForeignKey("treatment_plan.id"), nullable=False, index=True)
    prescription_no = Column(String(32), unique=True, nullable=False)
    
    # 处方信息
    formula_name = Column(String(128), index=True)
    formula_source = Column(String(256))
    
    # 处方组成
    ingredients = Column(JSON, nullable=False)
    total_dose = Column(String(64))
    
    # 用法
    usage = Column(String(256))
    frequency = Column(String(64))
    duration_days = Column(Integer)
    
    # 加减化裁
    modifications = Column(JSON)
    
    # 审核
    reviewed_by = Column(Integer)
    review_status = Column(String(16), default='pending')
    
    # 审计字段
    prescribed_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    treatment = relationship("TreatmentPlan", back_populates="prescriptions")
    
    def __repr__(self):
        return f"<TCMPrescription(id={self.id}, formula='{self.formula_name}')>"
