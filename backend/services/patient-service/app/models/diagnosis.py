from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, JSON, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import sqlalchemy as sa

from shared.database import Base


class Diagnosis(Base):
    """诊断表"""
    
    __tablename__ = "diagnosis"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    lesion_id = Column(Integer, ForeignKey("lesion.id"), unique=True, nullable=False, index=True)
    diagnosis_date = Column(Date, nullable=False, default=sa.func.current_date())
    
    # 西医诊断
    western_diagnosis = Column(String(128))
    icd10_code = Column(String(16), index=True)
    diagnosis_stage = Column(String(16))  # 0/I/II/III/IV 期
    
    # 中医诊断
    tcm_diagnosis = Column(String(128))  # 乳癖/乳岩等
    tcm_zheng_type = Column(String(32), index=True)
    tcm_zheng_severity = Column(String(8))
    
    # TNM 分期
    tnm_stage = Column(String(32))
    tnmp_pathological = Column(Boolean, default=False)
    
    # 预后评估
    prognosis = Column(String(16))  # 良好/中等/较差
    recurrence_risk = Column(String(16))  # 低/中/高
    
    # 审计字段
    diagnosed_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    lesion = relationship("Lesion", back_populates="diagnosis")
    treatment_plans = relationship("TreatmentPlan", back_populates="diagnosis", lazy="selectin")
    
    def __repr__(self):
        return f"<Diagnosis(id={self.id}, lesion_id={self.lesion_id}, western='{self.western_diagnosis}')>"
