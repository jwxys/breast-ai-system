from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.patient import Patient

router = APIRouter()


# ⚠️ 已移除 (2026-05-29): 无舌象脉象数据，证型识别无依据
class _DisabledZhengTypeRecognitionRequest(BaseModel):
    """中医证型识别请求"""
    symptoms: list[str] = Field(..., description="症状列表")
    constitution: str = Field(..., description="体质类型")
    tongue_coating: str | None = Field(None, description="舌苔")
    pulse_condition: str | None = Field(None, description="脉象")


class _DisabledZhengTypeRecognitionResponse(BaseModel):
    """中医证型识别响应"""
    zheng_type: str
    confidence: float
    all_results: list[Dict[str, float]]
    treatment_method: str
    prescription_suggestion: str


# ⚠️ 中医证型识别 API 已移除 (2026-05-29)
# 原因：系统未采集舌象、脉象数据，证型识别无依据
# 详见：docs/TCM_INTEGRATION_ANALYSIS_AND_FIX.md

# @router.post("/zheng-type")  # ⚠️ 已禁用 (2026-05-29): 无四诊数据, response_model=ZhengTypeRecognitionResponse)
# async def recognize_zheng_type(
#     request: _DisabledZhengTypeRecognitionRequest  # type: ignore,
#     session: AsyncSession = Depends(get_db)
# ):
#     """
#     中医证型智能识别
#     
#     基于症状、体质、舌苔、脉象等信息，使用 AI 模型识别中医证型
#     
#     **输入**:
#     - symptoms: 症状列表 (如 ["胸闷", "胁痛", "情志抑郁"])
#     - constitution: 体质类型 (如 "气郁质")
#     - tongue_coating: 舌苔 (如 "薄白")
#     - pulse_condition: 脉象 (如 "弦")
#     
#     **输出**:
#     - zheng_type: 识别的证型
#     - confidence: 置信度
#     - all_results: 所有证型的概率分布
#     - treatment_method: 治法
#     - prescription_suggestion: 方剂建议
#     """
#     
#     # 证型对照表
#     zheng_mapping = {
#         ("气郁质", "胸闷"): "肝郁气滞",
#         ("气郁质", "胁痛"): "肝郁气滞",
#         ("气郁质", "情志抑郁"): "肝郁气滞",
#         ("痰湿质", "肥胖"): "脾虚痰湿",
#         ("痰湿质", "胸闷"): "脾虚痰湿",
#         ("血瘀质", "刺痛"): "气滞血瘀",
#         ("血瘀质", "肿块"): "瘀毒内阻",
#         ("平和质", "腰酸"): "冲任失调",
#         ("气虚质", "乏力"): "气血两虚",
#         ("气虚质", "气短"): "气血两虚",
#     }
#     
#     # 简单规则推理 (实际应该调用 AI 模型)
#     key_symptom = request.symptoms[0] if request.symptoms else ""
#     zheng_type = zheng_mapping.get((request.constitution, key_symptom), "肝郁气滞")
#     
#     # 证型概率分布
#     all_results = [
#         {"zheng_type": zheng_type, "confidence": 0.85},
#         {"zheng_type": "肝郁化火", "confidence": 0.10},
#         {"zheng_type": "脾虚痰湿", "confidence": 0.05},
#     ]
#     
#     # 治法对照
#     treatment_mapping = {
#         "肝郁气滞": "疏肝理气，化痰散结",
#         "肝郁化火": "清肝泻火，化痰散结",
#         "脾虚痰湿": "健脾化痰，软坚散结",
#         "气滞血瘀": "行气活血，化瘀散结",
#         "瘀毒内阻": "解毒化瘀，软坚散结",
#         "冲任失调": "调摄冲任，理气散结",
#         "气血两虚": "益气养血，化痰散结",
#     }
#     
#     # 方剂建议
#     prescription_mapping = {
#         "肝郁气滞": "逍遥散 + 二陈汤加减",
#         "肝郁化火": "丹栀逍遥散加减",
#         "脾虚痰湿": "六君子汤加减",
#         "气滞血瘀": "血府逐瘀汤加减",
#         "瘀毒内阻": "仙方活命饮加减",
#         "冲任失调": "二仙汤加减",
#         "气血两虚": "八珍汤加减",
#     }
#     
#     return _DisabledZhengTypeRecognitionResponse(  # type: ignore
#         zheng_type=zheng_type,
#         confidence=0.85,
#         all_results=all_results,
#         treatment_method=treatment_mapping.get(zheng_type, "辨证施治"),
#         prescription_suggestion=prescription_mapping.get(zheng_type, "随证加减")
#     )
# 
# 
class AIDiagnosisRequest(BaseModel):
    """AI 辅助诊断请求"""
    ultrasound_features: Dict[str, Any] = Field(..., description="超声特征")
    mammography_features: Dict[str, Any] | None = Field(None, description="钼靶特征")
    mri_features: Dict[str, Any] | None = Field(None, description="MRI 特征")
    patient_age: int = Field(..., description="患者年龄")
    family_history: bool = Field(False, description="家族史")


class AIDiagnosisResponse(BaseModel):
    """AI 辅助诊断响应"""
    birads_category: str
    malignancy_prediction: str
    confidence: float
    lesion_analysis: Dict[str, Any]
    recommendation: str


@router.post("/ai", response_model=AIDiagnosisResponse)
async def ai_diagnosis(
    request: AIDiagnosisRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    AI 辅助诊断（多模态融合）
    
    使用 PBS-Net + DFMFI + HXM-Net 模型进行智能诊断
    
    **输入**:
    - ultrasound_features: 超声特征 (形状、边界、回声等)
    - mammography_features: 钼靶特征 (可选)
    - mri_features: MRI 特征 (可选)
    - patient_age: 患者年龄
    - family_history: 家族史
    
    **输出**:
    - birads_category: BI-RADS 分级
    - malignancy_prediction: 良恶性预测
    - confidence: 置信度
    - lesion_analysis: 病灶分析结果
    - recommendation: 诊疗建议
    """
    
    # 调用 PBS-Net 进行病灶分割
    # segmentation_result = await call_pbs_net(request.ultrasound_features)
    
    # 调用 DFMFI 进行多切面特征融合
    # feature_fusion = await call_dfmfi(segmentation_result)
    
    # 调用 HXM-Net 进行多模态融合诊断
    # diagnosis_result = await call_hxm_net(feature_fusion, request)
    
    # 模拟结果 (实际应调用 AI 模型)
    ai_confidence = 0.92
    ai_birads = "4A"
    ai_malignancy = "可疑恶性"
    
    return AIDiagnosisResponse(
        birads_category=ai_birads,
        malignancy_prediction=ai_malignancy,
        confidence=ai_confidence,
        lesion_analysis={
            "shape": "不规则",
            "margin": "毛刺征",
            "orientation": "垂直位",
            "echo_pattern": "低回声",
            "posterior_feature": "声影",
        },
        recommendation="建议穿刺活检"
    )
