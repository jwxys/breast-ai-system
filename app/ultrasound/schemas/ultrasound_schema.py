from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ReviewStatus(str, Enum):
    """审核状态"""
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class UltrasoundBase(BaseModel):
    """超声检查基础 schema"""
    visit_id: int = Field(..., description="随访 ID")


class UltrasoundCreate(UltrasoundBase):
    """创建超声检查"""
    image_path: str = Field(..., description="图像路径")


class UltrasoundResponse(UltrasoundBase):
    """超声检查响应"""
    id: int
    exam_no: str
    exam_date: datetime
    image_path: str
    birads_category: Optional[str]
    lesion_count: int
    ai_analysis: Optional[Dict[str, Any]]
    review_status: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AIAnalysisRequest(BaseModel):
    """AI 分析请求"""
    model_version: Optional[str] = "latest"


class AIAnalysisResponse(BaseModel):
    """AI 分析响应"""
    analysis_id: str
    status: str
    results: Dict[str, Any]
    ai_model_version: str
    confidence: float


class LesionAnnotation(BaseModel):
    """病灶标注"""
    location: str
    quadrant: str
    distance_from_nipple: float
    segmentation: List[List[int]]
    max_diameter: float
    shape: str
    margin: str
    echo_pattern: str


class AnnotationRequest(BaseModel):
    """标注提交请求"""
    lesions: List[LesionAnnotation]
    birads_category: str
    annotator_id: int


class BIRADSFeatures(BaseModel):
    """BI-RADS 特征"""
    shape: str
    orientation: str
    margin: str
    edge: str
    echo_pattern: str
    calcification: str
    posterior_feature: str
