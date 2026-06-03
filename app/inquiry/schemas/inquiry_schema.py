"""
智能症状问诊服务
基于知识图谱 + LLM 的多轮对话问诊
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

from pydantic import BaseModel, Field


class SymptomInfo(BaseModel):
    """症状信息"""
    name: str = Field(..., description="症状名称")
    severity: int = Field(1, ge=1, le=10, description="严重程度 1-10")
    duration: Optional[str] = Field(None, description="持续时间")
    frequency: Optional[str] = Field(None, description="发作频率")
    trigger_factors: List[str] = Field([], description="诱发因素")
    associated_symptoms: List[str] = Field([], description="伴随症状")


class PatientInfo(BaseModel):
    """患者基本信息"""
    age: Optional[int] = Field(None, description="年龄")
    menstrual_status: Optional[str] = Field(None, description="月经状态")
    menopause_age: Optional[int] = Field(None, description="绝经年龄")
    first_birth_age: Optional[int] = Field(None, description="初产年龄")
    breastfeeding_history: Optional[bool] = Field(None, description="哺乳史")
    family_history: Optional[bool] = Field(None, description="乳腺癌家族史")
    hormone_therapy: Optional[bool] = Field(None, description="激素治疗史")
    previous_breast_disease: Optional[bool] = Field(None, description="乳腺疾病史")


class ChiefComplaint(BaseModel):
    """主诉"""
    primary_symptom: str = Field(..., description="主要症状")
    onset_time: Optional[str] = Field(None, description="发现时间")
    symptom_type: str = Field(..., description="症状类型")


class DialogueState(BaseModel):
    """对话状态"""
    current_step: str = Field("greeting", description="当前步骤")
    collected_symptoms: List[SymptomInfo] = Field([], description="已收集症状")
    patient_info: Optional[PatientInfo] = Field(None, description="患者信息")
    chief_complaint: Optional[ChiefComplaint] = Field(None, description="主诉")
    missing_info: List[str] = Field([], description="缺失信息")
    risk_level: Optional[str] = Field(None, description="风险等级评估")
    completeness: float = Field(0.0, ge=0.0, le=1.0, description="信息完整度")


class DialogueTurn(BaseModel):
    """对话回合"""
    role: str = Field(..., description="角色 (user/assistant)")
    content: str = Field(..., description="对话内容")
    timestamp: datetime = Field(default_factory=datetime.now)
    intent: Optional[str] = Field(None, description="意图识别")
    entities: List[Dict] = Field([], description="实体提取")
    state_snapshot: Optional[DialogueState] = Field(None, description="状态快照")


class SymptomChatRequest(BaseModel):
    """问诊请求"""
    session_id: str = Field(..., description="会话 ID")
    message: str = Field(..., description="用户消息")
    patient_id: Optional[int] = Field(None, description="患者 ID")


class SymptomChatResponse(BaseModel):
    """问诊响应"""
    response: str = Field(..., description="AI 回复")
    follow_up_questions: List[str] = Field([], description="追问问题")
    collected_info: Dict = Field({}, description="已采集信息")
    completeness: float = Field(0.0, description="完整度")
    is_complete: bool = Field(False, description="信息采集是否完成")
    risk_assessment: Optional[str] = Field(None, description="风险评估")
    next_step: str = Field("", description="下一步建议")
