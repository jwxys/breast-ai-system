from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class DiagnosisBase(BaseModel):
    """诊断基础 schema"""
    western_diagnosis: str = Field(..., max_length=128, description="西医诊断")
    icd10_code: Optional[str] = Field(None, max_length=16, description="ICD-10 编码")
    
    # ⚠️ 中医字段已移除（2026-05-29）
    # 原因：无四诊信息采集（舌象、脉象、问诊），中医诊断无依据
    # 详见：docs/TCM_INTEGRATION_ANALYSIS_AND_FIX.md
    # tcm_diagnosis: Optional[str] = Field(None, max_length=128, description="中医诊断")
    # tcm_zheng_type: Optional[str] = Field(None, max_length=32, description="中医证型")
    # tcm_zheng_severity: Optional[str] = Field(None, max_length=8, description="证型严重程度")


class DiagnosisCreate(DiagnosisBase):
    """创建诊断"""
    lesion_id: int = Field(..., description="病灶 ID")
    diagnosis_stage: Optional[str] = Field(None, max_length=16, description="分期")
    prognosis: Optional[str] = Field(None, max_length=16, description="预后")
    recurrence_risk: Optional[str] = Field(None, max_length=16, description="复发风险")


class DiagnosisUpdate(BaseModel):
    """更新诊断"""
    western_diagnosis: Optional[str] = None
    icd10_code: Optional[str] = None
    prognosis: Optional[str] = None
    recurrence_risk: Optional[str] = None
    tnm_stage: Optional[str] = None
    
    # ⚠️ 中医字段已移除（2026-05-29）
    # tcm_diagnosis: Optional[str] = None
    # tcm_zheng_type: Optional[str] = None


class DiagnosisResponse(DiagnosisBase):
    """诊断响应"""
    id: int
    lesion_id: int
    diagnosis_date: date
    diagnosis_stage: Optional[str]
    tnm_stage: Optional[str]
    prognosis: Optional[str]
    recurrence_risk: Optional[str]
    diagnosed_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MolecularSubtypeRequest(BaseModel):
    """分子分型预测请求"""
    radiomics_features: Dict[str, Any] = Field(..., description="影像组学特征")


class MolecularSubtypeResponse(BaseModel):
    """分子分型预测响应"""
    predicted_subtype: str
    probabilities: Dict[str, float]
    ihc_prediction: Dict[str, Any]


# ⚠️ 证型识别相关 Schema 已移除（2026-05-29）
# 原因：系统未采集舌象图像和脉象波形数据，无法进行中医证型识别
# class ZhengTypeRecognitionRequest(BaseModel):
#     """证型识别请求"""
#     tongue_image: str
#     pulse_waveform: List[float]
#     symptom_responses: Dict[str, int]
#
# class ZhengTypeRecognitionResponse(BaseModel):
#     """证型识别响应"""
#     primary_zheng: str
#     secondary_zheng: Optional[str]
#     probabilities: Dict[str, float]
#     treatment_principle: str
#     prescription: str
