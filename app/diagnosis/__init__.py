"""
诊断模块

提供完整的乳腺诊断功能：
- BI-RADS 智能分级
- 分子分型预测
- AI 影像分析
- 报告版本管理
"""

from .models import Lesion, Diagnosis, DiagnosisReport
from .services import (
    BIRADSEngine,
    MolecularSubtypePredictor,
    AIDiagnosisService,
    DiagnosisService,
)
from .schemas import (
    DiagnosisCreate,
    DiagnosisResponse,
    BIRADSAssessmentResponse,
)

__all__ = [
    # Models
    "Lesion",
    "Diagnosis",
    "DiagnosisReport",
    
    # Services
    "BIRADSEngine",
    "MolecularSubtypePredictor",
    "AIDiagnosisService",
    "DiagnosisService",
    
    # Schemas
    "DiagnosisCreate",
    "DiagnosisResponse",
    "BIRADSAssessmentResponse",
]
