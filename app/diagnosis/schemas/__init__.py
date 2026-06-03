"""
诊断模块 Pydantic Schema

用于 API 请求/响应的数据验证和序列化
"""

from .diagnosis_schema import (
    # 诊断相关
    DiagnosisCreate,
    DiagnosisUpdate,
    DiagnosisResponse,
    DiagnosisListResponse,
    
    # BI-RADS 评估
    BIRADSAssessmentRequest,
    BIRADSAssessmentResponse,
    
    # 分子分型
    MolecularSubtypeRequest,
    MolecularSubtypeResponse,
    
    # AI 诊断
    AIDiagnosisRequest,
    AIDiagnosisResponse,
    
    # 报告
    DiagnosisReportCreate,
    DiagnosisReportResponse,
)


__all__ = [
    "DiagnosisCreate",
    "DiagnosisUpdate",
    "DiagnosisResponse",
    "DiagnosisListResponse",
    "BIRADSAssessmentRequest",
    "BIRADSAssessmentResponse",
    "MolecularSubtypeRequest",
    "MolecularSubtypeResponse",
    "AIDiagnosisRequest",
    "AIDiagnosisResponse",
    "DiagnosisReportCreate",
    "DiagnosisReportResponse",
]
