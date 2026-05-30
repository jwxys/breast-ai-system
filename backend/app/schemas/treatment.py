from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class TreatmentCategory(str, Enum):
    """治疗类别"""
    SURGERY = "手术"
    CHEMOTHERAPY = "化疗"
    RADIOTHERAPY = "放疗"
    ENDOCRINE = "内分泌治疗"
    TARGETED = "靶向治疗"
    TCM = "中医治疗"


class TreatmentStatus(str, Enum):
    """治疗状态"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"


class IngredientBase(BaseModel):
    """药材基础 schema"""
    herb_code: str
    herb_name: str
    dose: str
    role: Optional[str] = None  # 君/臣/佐/使


class TCMPrescriptionCreate(BaseModel):
    """创建中药处方"""
    treatment_id: int
    formula_name: str = Field(..., max_length=128)
    formula_source: Optional[str] = Field(None, max_length=256)
    ingredients: List[IngredientBase]
    usage: str = Field(..., max_length=256)
    frequency: str = Field(..., max_length=64)
    duration_days: int


class TreatmentPlanBase(BaseModel):
    """治疗方案基础 schema"""
    treatment_category: TreatmentCategory = Field(..., description="治疗类别")
    treatment_name: str = Field(..., max_length=128, description="治疗名称")
    treatment_detail: Optional[Dict[str, Any]] = Field(None, description="治疗详情")
    start_date: Optional[date] = None
    duration_weeks: Optional[int] = None


class TreatmentPlanCreate(TreatmentPlanBase):
    """创建治疗方案"""
    diagnosis_id: int = Field(..., description="诊断 ID")


class TreatmentPlanUpdate(BaseModel):
    """更新治疗方案"""
    treatment_name: Optional[str] = None
    treatment_detail: Optional[Dict[str, Any]] = None
    status: Optional[TreatmentStatus] = None
    completion_rate: Optional[float] = None


class TreatmentPlanResponse(TreatmentPlanBase):
    """治疗方案响应"""
    id: int
    plan_no: str
    diagnosis_id: int
    status: str
    start_date: Optional[date]
    end_date: Optional[date]
    efficacy: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TCMPrescriptionResponse(BaseModel):
    """中药处方响应"""
    id: int
    prescription_no: str
    treatment_id: int
    formula_name: str
    formula_source: Optional[str]
    ingredients: List[IngredientBase]
    usage: str
    frequency: str
    duration_days: int
    review_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class EfficacyAssessmentRequest(BaseModel):
    """疗效评估请求"""
    assessment_date: date
    response_type: str  # CR/PR/SD/PD
    change_from_baseline: float
    symptom_improvement: bool
    adverse_events: Optional[List[str]] = []
