from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List, Dict, Any
from enum import Enum


class VisitType(str, Enum):
    """随访类型"""
    INITIAL = "初诊"
    FOLLOWUP = "复诊"
    ROUTINE = "随访"


class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class VisitBase(BaseModel):
    """随访基础 schema"""
    visit_date: date = Field(..., description="随访日期")
    visit_type: VisitType = Field(..., description="随访类型")
    chief_complaint: Optional[str] = Field(None, max_length=512, description="主诉")
    history_present_illness: Optional[str] = Field(None, max_length=2048, description="现病史")
    physical_exam: Optional[Dict[str, Any]] = Field(None, description="体格检查")


class VisitCreate(VisitBase):
    """创建随访"""
    patient_id: int = Field(..., description="患者 ID")


class VisitUpdate(BaseModel):
    """更新随访"""
    chief_complaint: Optional[str] = None
    history_present_illness: Optional[str] = None
    physical_exam: Optional[Dict[str, Any]] = None
    risk_level: Optional[RiskLevel] = None


class VisitResponse(VisitBase):
    """随访响应"""
    id: int
    visit_no: str
    patient_id: int
    risk_level: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class VisitListResponse(BaseModel):
    """随访列表响应"""
    data: List[VisitResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, data: List, total: int, page: int, page_size: int):
        return cls(
            data=data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )


class RiskAssessmentRequest(BaseModel):
    """风险评估请求"""
    birads_category: str
    constitution: Optional[str] = None
    zheng_type: Optional[str] = None
    symptoms: Optional[List[str]] = []
    family_history: bool = False


class RiskAssessmentResponse(BaseModel):
    """风险评估响应"""
    risk_level: str
    risk_score: float
    risk_factors: List[Dict[str, Any]]
    recommendation: str
