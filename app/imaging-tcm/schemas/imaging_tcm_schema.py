"""
影像 - 中医病机分析 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class ImagingFeaturesInput(BaseModel):
    """影像特征输入（手动录入或从 AI 提取）"""
    
    # 1. 形态学特征
    boundary_type: Optional[str] = Field(None, description="边界类型：clear/unclear/spiculated/angular")
    morphology: Optional[str] = Field(None, description="形态：regular/irregular/crab-claw")
    aspect_ratio: Optional[float] = Field(None, description="纵横比")
    edge_type: Optional[str] = Field(None, description="边缘类型：smooth/blurred/microlobulated/macrol obulated")
    capsule_status: Optional[str] = Field(None, description="包膜状态：intact/broken/absent")
    
    # 2. 内部回声特征
    echo_type: Optional[str] = Field(None, description="回声类型：anechoic/hypoechoic/isoechogenic/hyperechoic")
    echo_homogeneity: Optional[str] = Field(None, description="均匀度：homogeneous/heterogeneous")
    calcification_type: Optional[str] = Field(None, description="钙化类型：none/coarse/micro/cluster/arc")
    liquefaction: Optional[bool] = Field(None, description="液化坏死")
    
    # 3. 血流动力学特征
    cdfi_grade: Optional[str] = Field(None, description="CDFI 分级：grade_0/grade_1/grade_2/grade_3")
    blood_flow_distribution: Optional[str] = Field(None, description="血流分布：peripheral/penetrating/reticular")
    resistive_index: Optional[float] = Field(None, description="RI 阻力指数")
    
    # 4. 弹性成像特征
    elasticity_score: Optional[int] = Field(None, description="弹性评分 (1-5)")
    strain_ratio: Optional[float] = Field(None, description="硬度比")
    
    # 5. 生长动力学特征
    growth_rate: Optional[str] = Field(None, description="生长速度：stable/slow/moderate/fast")
    lesion_size_cm: Optional[float] = Field(None, description="肿块大小 (cm)")
    multifocality: Optional[bool] = Field(None, description="多灶性")


class PathomechanismTendency(BaseModel):
    """病机倾向"""
    
    pathomechanism: str = Field(..., description="病机名称")
    score: float = Field(..., description="评分 (0-1)")
    level: str = Field(..., description="倾向程度")
    evidence: Optional[str] = Field(None, description="证据摘要")


class TCMAnalysisResponse(BaseModel):
    """中医病机分析响应"""
    
    ultrasound_id: int = Field(..., description="超声检查 ID")
    patient_id: int = Field(..., description="患者 ID")
    
    # 影像特征摘要
    imaging_features: ImagingFeaturesInput = Field(..., description="影像特征")
    
    # 病机倾向
    tcm_tendencies: Dict[str, PathomechanismTendency] = Field(..., description="病机倾向")
    
    # 综合判断
    primary_pathomechanism: str = Field(..., description="主要病机")
    secondary_pathomechanism: Optional[str] = Field(None, description="次要病机")
    pattern_combination: str = Field(..., description="病机组合")
    nature: str = Field(..., description="病性")
    
    # 证据等级
    overall_evidence_level: str = Field(..., description="证据等级")
    confidence: float = Field(..., description="置信度")
    
    # 治疗建议
    recommended_therapy: Optional[str] = Field(None, description="推荐治法")
    recommended_formula: Optional[str] = Field(None, description="参考方剂")
    
    # 免责声明
    disclaimer: Dict[str, str] = Field(..., description="免责声明")
    
    # 元数据
    analysis_version: str = Field(..., description="分析引擎版本")
    created_at: datetime = Field(..., description="分析时间")
    
    class Config:
        from_attributes = True


class BatchAnalysisRequest(BaseModel):
    """批量分析请求"""
    
    ultrasound_ids: List[int] = Field(..., description="超声检查 ID 列表")


class BatchAnalysisResponse(BaseModel):
    """批量分析响应"""
    
    results: List[TCMAnalysisResponse] = Field(..., description="分析结果列表")
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
