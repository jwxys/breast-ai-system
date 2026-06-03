"""
知情同意书 Pydantic Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.consent.models.consent_model import ConsentStatus


class ConsentBase(BaseModel):
    """同意书基础 Schema"""
    patient_id: int
    patient_name: str
    patient_id_number: Optional[str] = None
    
    version: str = "v1.0"
    
    # 患者声明
    has_understood_ai_purpose: bool = False
    has_understood_ai_limitation: bool = False
    has_understood_tcm_research: bool = False
    has_understood_data_usage: bool = False
    has_understood_voluntary: bool = False
    agree_to_participate: bool = False
    
    # 医生信息
    doctor_id: int
    doctor_name: str
    doctor_license_number: Optional[str] = None
    doctor_department: Optional[str] = None
    
    # 机构信息
    institution_name: str
    institution_address: Optional[str] = None
    institution_contact: Optional[str] = None
    
    # 伦理委员会信息
    ethics_committee_approval_number: Optional[str] = None
    ethics_committee_contact: Optional[str] = None
    
    # 费用信息
    ai_diagnosis_fee: Optional[str] = None
    insurance_coverage: Optional[str] = None
    self_pay_amount: Optional[str] = None


class ConsentCreate(ConsentBase):
    """创建同意书"""
    pass


class ConsentUpdate(BaseModel):
    """更新同意书"""
    patient_id_number: Optional[str] = None
    institution_name: Optional[str] = None
    institution_address: Optional[str] = None
    institution_contact: Optional[str] = None
    ai_diagnosis_fee: Optional[str] = None
    insurance_coverage: Optional[str] = None
    self_pay_amount: Optional[str] = None
    ethics_committee_approval_number: Optional[str] = None


class SignConsentRequest(BaseModel):
    """签署同意书请求"""
    # 患者声明
    has_understood_ai_purpose: bool = True
    has_understood_ai_limitation: bool = True
    has_understood_tcm_research: bool = True
    has_understood_data_usage: bool = True
    has_understood_voluntary: bool = True
    agree_to_participate: bool = True
    
    # 签名
    patient_signature: Optional[str] = None  # 患者签名图片或 base64
    doctor_signature: Optional[str] = None  # 医生签名图片或 base64


class RevokeConsentRequest(BaseModel):
    """撤回同意书请求"""
    reason: str = Field(..., min_length=10, description="撤回原因")


class ConsentResponse(ConsentBase):
    """同意书响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: ConsentStatus
    
    patient_signature: Optional[str] = None
    patient_sign_date: Optional[datetime] = None
    
    family_signature: Optional[str] = None
    family_relation: Optional[str] = None
    
    doctor_signature: Optional[str] = None
    doctor_sign_date: Optional[datetime] = None
    
    doctor_explanation_notes: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    revoked_at: Optional[datetime] = None
    revoked_reason: Optional[str] = None


class ConsentListResponse(BaseModel):
    """同意书列表响应"""
    items: List[ConsentResponse]
    total: int
    skip: int = 0
    limit: int = 20
