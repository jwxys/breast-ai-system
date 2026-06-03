"""
患者知情同意书模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ConsentStatus(str, enum.Enum):
    """同意状态"""
    PENDING = "pending"  # 待签署
    SIGNED = "signed"  # 已签署
    EXPIRED = "expired"  # 已过期
    REVOKED = "revoked"  # 已撤回


class InformedConsent(Base):
    """患者知情同意书"""
    __tablename__ = "informed_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 患者信息
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    patient_name = Column(String(64), nullable=False)
    patient_id_number = Column(String(18))  # 身份证号
    
    # 同意书信息
    version = Column(String(16), nullable=False, default="v1.0")  # 同意书版本
    status = Column(Enum(ConsentStatus), nullable=False, default=ConsentStatus.PENDING)
    
    # 患者声明
    has_understood_ai_purpose = Column(Boolean, default=False)  # 理解 AI 诊断目的
    has_understood_ai_limitation = Column(Boolean, default=False)  # 理解 AI 局限性
    has_understood_tcm_research = Column(Boolean, default=False)  # 理解中医模块为研究性质
    has_understood_data_usage = Column(Boolean, default=False)  # 理解数据使用
    has_understood_voluntary = Column(Boolean, default=False)  # 理解自愿原则
    agree_to_participate = Column(Boolean, default=False)  # 同意参与
    
    # 签署信息
    patient_signature = Column(String(256))  # 患者签名（图片路径或 base64）
    patient_sign_date = Column(DateTime)  # 签署日期
    
    family_signature = Column(String(256))  # 家属签名（如适用）
    family_relation = Column(String(64))  # 与患者关系
    
    # 医生信息
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_name = Column(String(64), nullable=False)
    doctor_license_number = Column(String(64))  # 执业医师号码
    doctor_department = Column(String(128))  # 科室
    doctor_signature = Column(String(256))  # 医生签名
    doctor_sign_date = Column(DateTime)  # 签署日期
    
    # 机构信息
    institution_name = Column(String(256))  # 医疗机构名称
    institution_address = Column(Text)  # 机构地址
    institution_contact = Column(String(64))  # 联系电话
    
    # 伦理委员会信息
    ethics_committee_approval_number = Column(String(64))  # 伦理批准号
    ethics_committee_contact = Column(String(128))  # 伦理委员会联系方式
    
    # 费用信息
    ai_diagnosis_fee = Column(String(64))  # AI 诊断费用
    insurance_coverage = Column(Text)  # 医保报销情况
    self_pay_amount = Column(String(64))  # 自费金额
    
    # 解释说明
    doctor_explanation_notes = Column(Text)  # 医生解释备注
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    revoked_at = Column(DateTime)  # 撤回时间
    revoked_reason = Column(Text)  # 撤回原因
    
    # 关联
    patient = relationship("Patient", back_populates="consents")
    doctor = relationship("User", foreign_keys=[doctor_id])
    
    def __repr__(self):
        return f"<InformedConsent(patient_id={self.patient_id}, status={self.status})>"
