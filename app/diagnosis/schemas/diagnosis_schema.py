"""
诊断模块 Pydantic Schema

定义 API 请求/响应的数据结构
支持数据验证、序列化和文档生成
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Any
from datetime import datetime
from enum import Enum


# ========= 枚举类型 =========

class ReportType(str, Enum):
    """报告类型"""
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    POST_OP = "post_op"
    PATHOLOGY = "pathology"


class ReportStatus(str, Enum):
    """报告状态"""
    DRAFT = "draft"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    CANCELLED = "cancelled"


# ========= 通用字段类型 =========

class UltrasoundFeatures(BaseModel):
    """超声征象数据结构"""
    shape: Optional[str] = Field(None, description="形状：oval/round/irregular")
    orientation: Optional[str] = Field(None, description="纵横比：parallel/not_parallel")
    margin_types: Optional[List[str]] = Field(None, description="边缘类型列表")
    echo_pattern: Optional[str] = Field(None, description="回声模式")
    echo_homogeneity: Optional[str] = Field(None, description="回声均匀性")
    calcification_present: Optional[bool] = Field(False, description="是否伴钙化")
    calcification_types: Optional[List[str]] = Field(None, description="钙化类型列表")
    posterior_features: Optional[List[str]] = Field(None, description="后方回声特征")
    vascularity_grade: Optional[str] = Field(None, description="血流分级：grade_0-3")
    vessel_pattern: Optional[str] = Field(None, description="血管形态")
    elastography: Optional[str] = Field(None, description="弹性成像结果")
    strain_ratio: Optional[float] = Field(None, description="应变比值")


class AIFeatures(BaseModel):
    """AI 分析结果"""
    detected: bool = Field(..., description="是否检测到病灶")
    bounding_box: Optional[Dict[str, float]] = Field(None, description="边界框")
    birads_prediction: Optional[str] = Field(None, description="AI 预测 BI-RADS")
    malignancy_probability: Optional[float] = Field(None, description="恶性概率")
    confidence: Optional[float] = Field(None, description="置信度")
    extracted_features: Optional[UltrasoundFeatures] = Field(None, description="提取的征象")
    highlighted_regions: Optional[List[Dict]] = Field(None, description="高亮区域")
    differential_diagnosis: Optional[List[str]] = Field(None, description="鉴别诊断")


class MolecularSubtypeData(BaseModel):
    """分子分型数据"""
    subtype: str = Field(..., description="分子分型名称")
    confidence: float = Field(..., description="置信度")
    er_status: str = Field(..., description="ER 状态")
    pr_status: str = Field(..., description="PR 状态")
    her2_status: str = Field(..., description="HER2 状态")
    ki67_value: float = Field(..., description="Ki-67 指数")
    treatment_plan: Optional[Dict[str, str]] = Field(None, description="治疗方案")


# ========= 请求 Schema =========

class DiagnosisCreate(BaseModel):
    """
    创建诊断请求
    
    用于 POST /api/v1/diagnosis
    """
    patient_id: int = Field(..., description="患者 ID")
    lesion_id: int = Field(..., description="病灶 ID")
    visit_id: Optional[int] = Field(None, description="就诊 ID")
    
    report_type: ReportType = Field(ReportType.INITIAL, description="报告类型")
    
    # BI-RADS 评估
    birads_category: str = Field(..., description="BI-RADS 分级")
    birads_assessment_basis: Optional[str] = Field(None, description="评估依据")
    birads_key_features: Optional[List[str]] = Field(None, description="关键征象")
    malignancy_risk: Optional[float] = Field(None, description="恶性风险")
    
    recommendation: Optional[str] = Field(None, description="处理建议")
    followup_interval: Optional[str] = Field(None, description="随访间隔")
    
    # AI 辅助
    ai_assisted: Optional[bool] = Field(False, description="是否 AI 辅助")
    ai_model_name: Optional[str] = Field(None, description="AI 模型")
    ai_birads_prediction: Optional[str] = Field(None, description="AI 预测分级")
    ai_malignancy_probability: Optional[float] = Field(None, description="AI 恶性概率")
    ai_confidence: Optional[float] = Field(None, description="AI 置信度")
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 1,
                "lesion_id": 1,
                "birads_category": "4B",
                "malignancy_risk": 0.30,
                "recommendation": "建议穿刺活检",
                "ai_assisted": True
            }
        }


class DiagnosisUpdate(BaseModel):
    """
    更新诊断请求
    
    用于 PATCH /api/v1/diagnosis/{id}
    """
    birads_category: Optional[str] = Field(None, description="BI-RADS 分级")
    birads_assessment_basis: Optional[str] = Field(None, description="评估依据")
    malignancy_risk: Optional[float] = Field(None, description="恶性风险")
    recommendation: Optional[str] = Field(None, description="处理建议")
    followup_interval: Optional[str] = Field(None, description="随访间隔")
    ai_assisted: Optional[bool] = Field(None, description="是否 AI 辅助")


class BIRADSAssessmentRequest(BaseModel):
    """
    BI-RADS 评估请求
    
    用于 POST /api/v1/diagnosis/assess-birads
    """
    ultrasound_features: UltrasoundFeatures = Field(..., description="超声征象")
    include_explanation: bool = Field(True, description="是否包含详细说明")
    clinical_factors: Optional[Dict[str, Any]] = Field(None, description="临床因素")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ultrasound_features": {
                    "shape": "irregular",
                    "orientation": "not_parallel",
                    "margin_types": ["angular", "spiculated"],
                    "echo_pattern": "hypoechoic",
                    "vascularity_grade": "grade_2"
                },
                "include_explanation": True,
                "clinical_factors": {
                    "age": 55,
                    "lesion_size": 25.5,
                    "family_history": True
                }
            }
        }


class ConcordanceCheckRequest(BaseModel):
    """
    一致性检查请求
    
    用于比较 AI 评估与医师诊断
    """
    ai_result: Dict[str, Any] = Field(..., description="AI 评估结果")
    physician_diagnosis: Dict[str, Any] = Field(..., description="医师诊断结果")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ai_result": {
                    "birads_category": "4C",
                    "malignancy_risk": 0.55,
                    "key_features": ["不规则形", "毛刺状边缘"]
                },
                "physician_diagnosis": {
                    "birads_category": "4B",
                    "malignancy_risk": 0.35,
                    "key_features": ["不规则形", "边界不清"]
                }
            }
        }


class ConcordanceCheckResponse(BaseModel):
    """一致性检查响应"""
    level: str = Field(..., description="一致性等级")
    score: float = Field(..., description="一致性评分 (0-100)")
    birads_diff: int = Field(..., description="BI-RADS 分级差异")
    agreement_details: Dict[str, bool] = Field(..., description="各项征象一致性")
    discordance_reasons: List[str] = Field(..., description="分歧原因列表")
    recommendation: str = Field(..., description="处理建议")
    
    class Config:
        json_schema_extra = {
            "example": {
                "level": "moderate",
                "score": 72.5,
                "birads_diff": 1,
                "agreement_details": {
                    "shape": True,
                    "margin": False,
                    "orientation": True
                },
                "discordance_reasons": ["边缘特征识别不一致"],
                "recommendation": "中度一致，建议复核..."
            }
        }


class LesionMarkupRequest(BaseModel):
    """病灶标记请求"""
    bounding_box: Dict[str, float] = Field(..., description="边界框 {x, y, width, height}")
    laterality: str = Field(..., description="侧别 L/R")
    image_dimensions: Dict[str, int] = Field(..., description="图像尺寸 {width, height}")
    nipple_position: Optional[Dict[str, float]] = Field(None, description="乳头位置")
    skin_line: Optional[List[Dict[str, float]]] = Field(None, description="皮肤线")
    pectoralis_line: Optional[List[Dict[str, float]]] = Field(None, description="胸肌线")


class LesionMarkupResponse(BaseModel):
    """病灶标记响应"""
    roi: Dict[str, Any] = Field(..., description="ROI 数据")
    location: Dict[str, Any] = Field(..., description="位置信息")
    spatial_relationship: Dict[str, Any] = Field(..., description="空间关系")


class LNAssessmentRequest(BaseModel):
    """淋巴结评估请求"""
    ultrasound_features: Dict[str, Any] = Field(..., description="淋巴结超声特征")
    clinical_context: Optional[Dict[str, Any]] = Field(None, description="临床背景")


class LNAssessmentResponse(BaseModel):
    """淋巴结评估响应"""
    status: str = Field(..., description="淋巴结状态")
    n_stage: Optional[str] = Field(None, description="N 分期")
    confidence: float = Field(..., description="置信度")
    suspicious_features: List[str] = Field(..., description="可疑特征")
    recommendation: str = Field(..., description="建议")
    metrics: Dict[str, Any] = Field(..., description="测量指标")


class LesionTrackingRequest(BaseModel):
    """病灶追踪请求"""
    measurements: List[Dict[str, Any]] = Field(..., description="测量数据列表")
    baseline_date: str = Field(..., description="基线日期")


class GrowthAnalysisResponse(BaseModel):
    """生长分析响应"""
    growth_rate: str = Field(..., description="生长速度分级")
    size_change_percent: float = Field(..., description="大小变化%")
    velocity_mm_per_month: float = Field(..., description="生长速度 mm/月")
    doubling_time_days: Optional[int] = Field(None, description="倍增时间")
    morphological_changes: List[str] = Field(..., description="形态变化")
    malignancy_risk: float = Field(..., description="恶性风险预测")


class TreatmentResponseRequest(BaseModel):
    """治疗反应评估请求"""
    baseline_diameter: float = Field(..., description="基线最长径 (mm)")
    follow_up_diameter: float = Field(..., description="随访最长径 (mm)")
    baseline_date: str = Field(..., description="基线日期")
    follow_up_date: str = Field(..., description="随访日期")


class TreatmentResponseResponse(BaseModel):
    """治疗反应评估响应"""
    response: str = Field(..., description="治疗反应 (CR/PR/SD/PD)")
    target_lesion_change: float = Field(..., description="靶病灶变化%")
    summary_stage: str = Field(..., description="总结分期")
    recommendation: str = Field(..., description="治疗建议")


class MolecularSubtypeRequest(BaseModel):
    """
    分子分型预测请求
    
    用于 POST /api/v1/diagnosis/predict-subtype
    """
    er_status: bool = Field(..., description="ER 状态：True=阳性")
    pr_percentage: float = Field(..., description="PR 阳性百分比 (0-100)")
    her2_status: int = Field(..., description="HER2 状态：0/1/2/3")
    ki67_percentage: float = Field(..., description="Ki-67 指数 (0-100)")
    grade: Optional[str] = Field(None, description="组织学分级")
    
    class Config:
        json_schema_extra = {
            "example": {
                "er_status": True,
                "pr_percentage": 80,
                "her2_status": 0,
                "ki67_percentage": 10,
                "grade": "G1"
            }
        }


class AIDiagnosisRequest(BaseModel):
    """
    AI 诊断请求
    
    用于 POST /api/v1/diagnosis/ai-analyze
    """
    lesion_id: int = Field(..., description="病灶 ID")
    image_urls: List[str] = Field(..., description="超声图像 URLs")
    patient_info: Optional[Dict[str, Any]] = Field(None, description="患者临床信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lesion_id": 1,
                "image_urls": ["https://storage/image1.jpg", "https://storage/image2.jpg"],
                "patient_info": {
                    "age": 45,
                    "gender": "女",
                    "symptoms": "左侧乳房可触及肿块"
                }
            }
        }


class DiagnosisReportCreate(BaseModel):
    """
    创建诊断报告版本
    
    用于 POST /api/v1/diagnosis/{id}/report
    """
    ultrasound_findings: str = Field(..., description="超声所见")
    impression: str = Field(..., description="诊断印象")
    recommendations: str = Field(..., description="具体建议")
    changes_from_previous: Optional[str] = Field(None, description="变更说明")
    change_reason: Optional[str] = Field(None, description="修改原因")


# ========= 响应 Schema =========

class BIRADSAssessmentResponse(BaseModel):
    """
    BI-RADS 评估响应
    """
    birads_category: str = Field(..., description="BI-RADS 分级")
    malignancy_risk: float = Field(..., description="恶性风险 (%)")
    recommendation: str = Field(..., description="处理建议")
    key_features: List[str] = Field(..., description="关键征象列表")
    explanation: Optional[str] = Field(None, description="分级详细说明")


class MolecularSubtypeResponse(BaseModel):
    """
    分子分型预测响应
    """
    subtype: str = Field(..., description="分子分型")
    confidence: float = Field(..., description="置信度")
    er_status: str = Field(..., description="ER 状态")
    pr_status: str = Field(..., description="PR 状态")
    her2_status: str = Field(..., description="HER2 状态")
    ki67_value: float = Field(..., description="Ki-67 指数")
    treatment_plan: Optional[Dict[str, str]] = Field(None, description="治疗方案")
    description: Optional[str] = Field(None, description="分型详细说明")


class AIDiagnosisResponse(BaseModel):
    """
    AI 诊断响应
    """
    detected: bool = Field(..., description="是否检测到病灶")
    bounding_box: Optional[Dict[str, float]] = Field(None, description="边界框")
    birads_prediction: str = Field(..., description="AI 预测 BI-RADS")
    malignancy_probability: float = Field(..., description="恶性概率")
    confidence: float = Field(..., description="置信度")
    extracted_features: Optional[UltrasoundFeatures] = Field(None, description="提取征象")
    highlighted_regions: Optional[List[Dict]] = Field(None, description="高亮区域")
    differential_diagnosis: Optional[List[str]] = Field(None, description="鉴别诊断")


class DiagnosisResponse(BaseModel):
    """
    诊断详情响应
    
    用于 GET /api/v1/diagnosis/{id}
    """
    id: int
    report_no: str
    patient_id: int
    lesion_id: int
    
    report_type: ReportType
    report_status: ReportStatus
    
    # BI-RADS
    birads_category: str
    birads_assessment_basis: Optional[str]
    birads_key_features: Optional[List[str]]
    malignancy_risk: Optional[float]
    recommendation: Optional[str]
    followup_interval: Optional[str]
    
    # AI 辅助
    ai_assisted: bool
    ai_model_name: Optional[str]
    ai_birads_prediction: Optional[str]
    ai_malignancy_probability: Optional[float]
    ai_confidence: Optional[float]
    
    # 病理
    pathology_performed: bool
    pathology_type: Optional[str]
    pathology_grade: Optional[str]
    
    # 分子分型
    molecular_subtype: Optional[str]
    
    # 审计
    created_at: datetime
    created_by: Optional[int]
    reviewed_by: Optional[int]
    
    class Config:
        from_attributes = True


class DiagnosisListResponse(BaseModel):
    """
    诊断列表响应
    
    用于 GET /api/v1/diagnosis
    """
    code: int = 200
    data: List[DiagnosisResponse]
    total: int
    page: int = 1
    page_size: int = 10


class DiagnosisReportResponse(BaseModel):
    """
    诊断报告版本响应
    """
    id: int
    diagnosis_id: int
    version_no: int
    ultrasound_findings: str
    impression: str
    recommendations: str
    changes_from_previous: Optional[str]
    created_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


# ========= 综合评估响应 =========

class ComprehensiveAssessmentResponse(BaseModel):
    """
    综合诊断评估响应
    
    整合 BI-RADS、分子分型、AI 分析
    """
    lesion_id: int
    lesion_no: str
    assessment_time: str
    
    birads_assessment: BIRADSAssessmentResponse
    molecular_subtype: Optional[MolecularSubtypeResponse]
    ai_analysis: Optional[AIDiagnosisResponse]
    
    conclusion: str
    treatment_recommendations: Optional[Dict[str, str]]
