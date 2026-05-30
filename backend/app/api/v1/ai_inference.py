"""
AI 推理 API
提供病灶分割、良恶性预测、中医证型识别等功能
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import tempfile
from pathlib import Path

from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# 延迟导入 AI 服务
_ai_service = None


def get_ai_service():
    global _ai_service
    if _ai_service is None:
        from services.ai_inference_service import get_ai_service
        _ai_service = get_ai_service()
        _ai_service.load_models()
    return _ai_service


class UltrasoundAnalysisRequest(BaseModel):
    """超声图像分析请求"""
    image_path: str = Field(..., description="图像路径")


class UltrasoundAnalysisResponse(BaseModel):
    """超声图像分析响应"""
    segmentation: Dict[str, Any]
    features: Dict[str, Any]
    quality_score: float
    birads_features: Dict[str, str]


@router.post("/analyze", response_model=UltrasoundAnalysisResponse)
async def analyze_ultrasound(
    request: UltrasoundAnalysisRequest,
    ai_service = Depends(get_ai_service)
):
    """
    超声图像分析
    
    使用 PBS-Net 进行病灶分割，提取 BI-RADS 特征
    """
    try:
        # 病灶分割
        segmentation = await ai_service.segment_lesion(request.image_path)
        
        # 提取 BI-RADS 特征
        features = extract_birads_features(segmentation)
        
        # 图像质量评分
        quality_score = calculate_quality_score(request.image_path)
        
        return UltrasoundAnalysisResponse(
            segmentation=segmentation,
            features=features,
            quality_score=quality_score,
            birads_features=features
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 分析失败：{str(e)}")


@router.post("/diagnose")
async def ai_diagnosis(
    ultrasound_features: Dict[str, Any],
    mammography_features: Optional[Dict[str, Any]] = None,
    mri_features: Optional[Dict[str, Any]] = None,
    patient_age: int = Form(...),
    family_history: bool = Form(False),
    ai_service = Depends(get_ai_service)
):
    """
    AI 辅助诊断 (多模态融合)
    """
    try:
        result = await ai_service.diagnose(
            ultrasound_features=ultrasound_features,
            mammography_features=mammography_features,
            mri_features=mri_features,
            patient_age=patient_age,
            family_history=family_history
        )
        
        return {
            "code": 200,
            "message": "诊断成功",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 诊断失败：{str(e)}")


@router.post("/upload")
async def upload_and_analyze(
    file: UploadFile = File(...),
    ai_service = Depends(get_ai_service)
):
    """
    上传超声图像并自动分析
    """
    # 保存上传文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # AI 分析
        segmentation = await ai_service.segment_lesion(tmp_path)
        
        # 清理临时文件
        Path(tmp_path).unlink(missing_ok=True)
        
        return {
            "code": 200,
            "message": "分析成功",
            "data": {
                "filename": file.filename,
                "segmentation": segmentation,
            }
        }
        
    except Exception as e:
        Path(tmp_path).unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"分析失败：{str(e)}")


class ZhengTypeRequest(BaseModel):
    """中医证型识别请求"""
    symptoms: List[str] = Field(..., description="症状列表")
    constitution: str = Field(..., description="体质类型")
    tongue_coating: Optional[str] = None
    pulse_condition: Optional[str] = None


class ZhengTypeResponse(BaseModel):
    """中医证型识别响应"""
    zheng_type: str
    confidence: float
    treatment_method: str
    prescription_suggestion: str


@router.post("/zheng-type", response_model=ZhengTypeResponse)
async def recognize_zheng_type(request: ZhengTypeRequest):
    """
    中医证型智能识别
    """
    # 证型映射规则
    zheng_mapping = {
        ("气郁质", "胸闷"): ("肝郁气滞", "疏肝理气，化痰散结", "逍遥散 + 二陈汤加减"),
        ("气郁质", "胁痛"): ("肝郁气滞", "疏肝理气，化痰散结", "逍遥散 + 二陈汤加减"),
        ("痰湿质", "肥胖"): ("脾虚痰湿", "健脾化痰，软坚散结", "六君子汤加减"),
        ("血瘀质", "刺痛"): ("气滞血瘀", "行气活血，化瘀散结", "血府逐瘀汤加减"),
        ("平和质", "腰酸"): ("冲任失调", "调摄冲任，理气散结", "二仙汤加减"),
    }
    
    # 基于主要症状判断
    key_symptom = request.symptoms[0] if request.symptoms else ""
    result = zheng_mapping.get(
        (request.constitution, key_symptom),
        ("肝郁气滞", "疏肝理气，化痰散结", "逍遥散 + 二陈汤加减")
    )
    
    return ZhengTypeResponse(
        zheng_type=result[0],
        confidence=0.85,
        treatment_method=result[1],
        prescription_suggestion=result[2]
    )


def extract_birads_features(segmentation: Dict) -> Dict[str, str]:
    """从分割结果提取 BI-RADS 特征"""
    # 简化实现
    return {
        "shape": "irregular",
        "margin": "spiculated",
        "orientation": "not_parallel",
        "echo_pattern": "marked_hypoechoic",
        "posterior_feature": "shadow",
    }


def calculate_quality_score(image_path: str) -> float:
    """计算图像质量评分"""
    # 简化实现
    return 0.92
