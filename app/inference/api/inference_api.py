"""
AI 模型推理 API

提供实时 AI 诊断预测服务
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import numpy as np
from PIL import Image
import io

from app.core.database import get_db


router = APIRouter(prefix="/api/v1/inference", tags=["AI 推理"])


@router.post("/predict", summary="AI 诊断预测")
async def predict_birads(
    image: UploadFile = File(..., description="超声图像"),
    patient_age: Optional[int] = Form(None, description="患者年龄"),
    db: AsyncSession = Depends(get_db)
):
    """
    实时 AI 诊断预测
    
    上传超声图像，返回:
    - BI-RADS 分级预测
    - 恶性概率
    - 不确定性评估
    - 可解释性报告
    """
    # 加载图像
    try:
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data)).convert('RGB')
        img_array = np.array(img)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"图像加载失败：{str(e)}")
    
    # TODO: 加载模型并预测
    # model = load_model()
    # prediction = model.predict(img_array)
    
    # 模拟预测结果
    return {
        "code": 200,
        "data": {
            "birads_prediction": "4A",
            "malignancy_probability": 0.35,
            "uncertainty": 0.12,
            "uncertainty_level": "medium",
            "confidence_message": "AI 预测可信度中等，建议结合临床判断",
            "key_features": [
                {"name": "形状", "value": "不规则形", "importance": 0.8},
                {"name": "边缘", "value": "边界不清", "importance": 0.7},
                {"name": "回声", "value": "低回声", "importance": 0.6}
            ],
            "recommendation": "建议穿刺活检以明确诊断"
        }
    }


@router.post("/radiomics", summary="影像组学特征提取")
async def extract_radiomics(
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    提取影像组学特征
    
    返回 6 大类 20+ 定量特征
    """
    from app.diagnosis.services.radiomics_extractor import RadiomicsExtractor
    
    try:
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data)).convert('L')
        img_array = np.array(img)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"图像加载失败：{str(e)}")
    
    # 创建提取器
    extractor = RadiomicsExtractor(img_array[np.newaxis, ...])
    
    # 提取特征
    try:
        features = extractor.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"特征提取失败：{str(e)}")
    
    return {
        "code": 200,
        "data": {
            "features": features,
            "total_features": len(features),
            "categories": [
                "形态学", "一阶统计", "GLCM 纹理", "GLRLM 纹理", "小波"
            ]
        }
    }


@router.post("/explain", summary="可解释性分析")
async def explain_prediction(
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    生成 AI 预测解释报告
    
    包括:
    - Grad-CAM 热力图
    - 特征重要性
    - 推理链
    """
    from app.diagnosis.services.explainability import ExplainableAI
    
    try:
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data)).convert('RGB')
        img_array = np.array(img) / 255.0
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"图像加载失败：{str(e)}")
    
    # 创建 XAI 服务
    xai = ExplainableAI()
    
    # TODO: 加载模型
    # model = load_model()
    
    # 生成解释报告
    # report = xai.create_explanation_report(img_array, model, features={})
    
    return {
        "code": 200,
        "data": {
            "visualization": "热力图数据",
            "key_features": [],
            "reasoning_chain": {
                "steps": [],
                "conclusion": "待实现"
            }
        }
    }


@router.post("/multimodal-fusion", summary="多模态融合诊断")
async def multimodal_fusion(
    ultrasound_image: UploadFile = File(..., alias="ultrasound"),
    mammography_image: Optional[UploadFile] = File(None, alias="mammography"),
    mri_image: Optional[UploadFile] = File(None, alias="mri"),
    db: AsyncSession = Depends(get_db)
):
    """
    多模态影像融合诊断
    
    支持:
    - 超声 + 钼靶融合
    - 超声+MRI 融合
    - 三模态融合
    """
    from app.diagnosis.services.multimodal.fusion import MultimodalFusion, ModalityType
    
    # 加载各模态图像
    features = {}
    
    # 超声 (必需)
    us_data = await ultrasound_image.read()
    us_img = Image.open(io.BytesIO(us_data))
    features[ModalityType.ULTRASOUND] = {"loaded": True}
    
    # 钼靶 (可选)
    if mammography_image:
        mg_data = await mammography_image.read()
        mg_img = Image.open(io.BytesIO(mg_data))
        features[ModalityType.MAMMOGRAPHY] = {"loaded": True}
    
    # MRI(可选)
    if mri_image:
        mri_data = await mri_image.read()
        mri_img = Image.open(io.BytesIO(mri_data))
        features[ModalityType.MRI] = {"loaded": True}
    
    # 创建融合器
    fusion = MultimodalFusion(fusion_strategy='late')
    
    # 模拟各模态预测
    predictions = {
        ModalityType.ULTRASOUND: 0.6,
    }
    if ModalityType.MAMMOGRAPHY in features:
        predictions[ModalityType.MAMMOGRAPHY] = 0.5
    if ModalityType.MRI in features:
        predictions[ModalityType.MRI] = 0.7
    
    # 执行融合
    result = fusion.fuse(features, predictions)
    
    # 处理不一致
    disagreement_result = fusion.handle_disagreement(
        predictions,
        result.agreement_level
    )
    
    return {
        "code": 200,
        "data": {
            "fused_probability": float(result.fused_features[0]) if len(result.fused_features) > 0 else 0,
            "modality_predictions": {k.value: v for k, v in predictions.items()},
            "agreement_level": result.agreement_level,
            "disagreement_handling": disagreement_result
        }
    }
