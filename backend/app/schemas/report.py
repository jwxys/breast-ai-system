"""
Report Schemas

报告相关的 Pydantic 模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ReportBase(BaseModel):
    """报告基础模型"""
    report_type: str = Field(..., description="报告类型")
    patient_id: Optional[int] = Field(None, description="患者 ID")
    visit_id: Optional[int] = Field(None, description="随访 ID")
    diagnosis_id: Optional[int] = Field(None, description="诊断 ID")
    title: Optional[str] = Field(None, description="报告标题")
    content: Optional[str] = Field(None, description="报告内容")
    summary: Optional[str] = Field(None, description="报告摘要")
    ai_assisted: bool = Field(False, description="是否 AI 辅助")
    ai_model_used: Optional[str] = Field(None, description="使用的 AI 模型")
    ai_confidence: Optional[float] = Field(None, description="AI 置信度")
    status: str = Field("draft", description="报告状态")


class ReportCreate(ReportBase):
    """创建报告请求"""
    pass


class ReportUpdate(BaseModel):
    """更新报告请求"""
    report_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    ai_assisted: Optional[bool] = None
    ai_model_used: Optional[str] = None
    ai_confidence: Optional[float] = None


class ReportResponse(ReportBase):
    """报告响应模型"""
    id: int
    report_no: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class ReportListItem(BaseModel):
    """报告列表项"""
    id: int
    report_no: str
    report_type: str
    title: Optional[str]
    summary: Optional[str]
    status: str
    patient_name: Optional[str]
    created_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
