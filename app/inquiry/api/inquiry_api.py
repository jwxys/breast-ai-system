"""
智能问诊模块 - AI 问诊对话 API

基于大语言模型的智能问诊系统
模拟医生问诊流程，收集患者症状信息
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel


router = APIRouter()


# ========= 数据传输对象 =========

class ChatMessage(BaseModel):
    """
    对话消息模型
    
    Attributes:
        role: 角色 (user/assistant)
        content: 消息内容
        timestamp: 时间戳
    """
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """
    问诊对话请求
    
    Attributes:
        patient_id: 患者 ID
        message: 患者当前消息
        conversation_history: 历史对话 (可选)
    """
    patient_id: str
    message: str
    conversation_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    """
    问诊对话响应
    
    Attributes:
        response: AI 回复内容
        suggested_questions: 建议问题列表
        symptom_tags: 提取的症状标签
        need_followup: 是否需要继续问诊
    """
    response: str
    suggested_questions: List[str]
    symptom_tags: List[str]
    need_followup: bool


# ========= API 接口 =========

@router.post("/inquiry/chat",
             summary="智能问诊对话",
             description="与 AI 医生进行问诊对话",
             response_model=ChatResponse,
             tags=["智能问诊"])
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    AI 智能问诊
    
    基于 Kimi/通义大模型，模拟医生问诊流程：
    1. 理解患者主诉
    2. 提取症状信息
    3. 生成针对性问题
    4. 评估是否需要继续问诊
    
    Args:
        request: 对话请求
        db: 数据库会话
    
    Returns:
        ChatResponse: AI 回复和建议
    
    Raises:
        HTTPException:
            - 400: 参数错误
            - 500: AI 服务调用失败
    
    Example:
        POST /api/v1/inquiry/chat
        {
            "patient_id": "patient_001",
            "message": "医生，我乳房有个肿块",
            "conversation_history": []
        }
        
        Response:
        {
            "response": "请问肿块发现多久了？",
            "suggested_questions": ["肿块会移动吗？", "有疼痛感吗？"],
            "symptom_tags": ["乳房肿块"],
            "need_followup": true
        }
    """
    try:
        # 1. 构建对话上下文
        context = build_context(request.conversation_history)
        
        # 2. 调用 AI 问诊服务
        ai_response = await symptom_chat_service.chat(
            message=request.message,
            context=context,
            patient_id=request.patient_id
        )
        
        # 3. 提取症状标签
        symptom_tags = await extract_symptoms(ai_response["response"])
        
        # 4. 生成建议问题
        suggested_questions = generate_followup_questions(
            symptom_tags=symptom_tags,
            conversation_history=request.conversation_history
        )
        
        # 5. 判断是否需要继续问诊
        need_followup = should_continue_inquiry(
            symptom_tags=symptom_tags,
            conversation_length=len(request.conversation_history or [])
        )
        
        # 6. 保存对话记录
        await save_conversation(
            db=db,
            patient_id=request.patient_id,
            messages=[
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": ai_response["response"]}
            ]
        )
        
        return ChatResponse(
            response=ai_response["response"],
            suggested_questions=suggested_questions,
            symptom_tags=symptom_tags,
            need_followup=need_followup
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问诊失败：{str(e)}")


@router.get("/inquiry/history/{patient_id}",
            summary="获取问诊历史",
            description="获取患者的问诊记录",
            tags=["智能问诊"])
async def get_inquiry_history(
    patient_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取患者问诊历史记录
    
    Args:
        patient_id: 患者 ID
        skip: 跳过记录数
        limit: 每页数量
        db: 数据库会话
    
    Returns:
        List[Conversation]: 问诊历史记录
    
    Example:
        GET /api/v1/inquiry/history/patient_001
    """
    history = await inquiry_service.get_history(
        db=db,
        patient_id=patient_id,
        skip=skip,
        limit=limit
    )
    
    return {
        "code": 200,
        "data": history
    }


@router.post("/inquiry/summary",
             summary="生成问诊总结",
             description="基于对话历史生成病情总结",
             tags=["智能问诊"])
async def generate_inquiry_summary(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """
    生成病情总结
    
    AI 分析完整对话历史，生成结构化病情摘要：
    - 主诉
    - 现病史
    - 症状列表
    - 初步建议
    
    Args:
        patient_id: 患者 ID
        db: 数据库会话
    
    Returns:
        dict: 病情总结
    
    Example:
        POST /api/v1/inquiry/summary
        {
            "patient_id": "patient_001"
        }
    """
    # 获取完整对话历史
    history = await inquiry_service.get_full_history(db, patient_id)
    
    # 调用 AI 生成总结
    summary = await ai_summary_service.generate(history)
    
    return {
        "code": 200,
        "data": {
            "chief_complaint": summary["主诉"],          # 主要症状
            "history_present": summary["现病史"],        # 病程描述
            "symptoms": summary["症状列表"],             # 症状清单
            "suggestions": summary["初步建议"]           # 就医建议
        }
    }


# ========= 辅助函数 =========

def build_context(history: List[ChatMessage]) -> str:
    """
    构建对话上下文
    
    Args:
        history: 历史对话列表
    
    Returns:
        str: 格式化的上下文文本
    """
    if not history:
        return ""
    
    context_lines = []
    for msg in history[-5:]:  # 只保留最近 5 轮
        role = "患者" if msg.role == "user" else "医生"
        context_lines.append(f"{role}: {msg.content}")
    
    return "\n".join(context_lines)


async def extract_symptoms(text: str) -> List[str]:
    """
    从文本中提取症状标签
    
    Args:
        text: 对话文本
    
    Returns:
        List[str]: 症状标签列表
    
    Example:
        ["乳房肿块", "疼痛", "乳头溢液"]
    """
    # TODO: 调用症状提取模型或关键词匹配
    return []


def generate_followup_questions(
    symptom_tags: List[str],
    conversation_history: List[ChatMessage]
) -> List[str]:
    """
    生成建议问题
    
    根据已收集的症状，生成下一步建议问题
    
    Args:
        symptom_tags: 已识别的症状标签
        conversation_history: 对话历史
    
    Returns:
        List[str]: 建议问题列表
    
    Example:
        [
            "肿块会移动吗？",
            "有疼痛感吗？",
            "乳头有溢液吗？"
        ]
    """
    question_templates = {
        "乳房肿块": ["肿块会移动吗？", "肿块质地如何？"],
        "疼痛": ["疼痛是持续性的还是间歇性的？", "疼痛程度如何？"],
        "乳头溢液": ["溢液是什么颜色？", "是自发溢液还是挤压后？"]
    }
    
    questions = []
    for tag in symptom_tags:
        if tag in question_templates:
            questions.extend(question_templates[tag])
    
    # 过滤掉已问 over 的问题
    asked = set()
    for msg in conversation_history or []:
        if "?" in msg.content or "？" in msg.content:
            asked.add(msg.content)
    
    return [q for q in questions if q not in asked][:3]


def should_continue_inquiry(
    symptom_tags: List[str],
    conversation_length: int
) -> bool:
    """
    判断是否需要继续问诊
    
    Args:
        symptom_tags: 症状标签
        conversation_length: 对话轮数
    
    Returns:
        bool: 是否需要继续
    """
    # 如果对话已超过 10 轮，或已收集 5+ 个症状，结束问诊
    if conversation_length >= 10 or len(symptom_tags) >= 5:
        return False
    
    # 否则继续
    return True


async def save_conversation(
    db: Session,
    patient_id: str,
    messages: List[dict]
):
    """
    保存对话记录到数据库
    
    Args:
        db: 数据库会话
        patient_id: 患者 ID
        messages: 对话消息列表
    """
    # TODO: 实现数据库保存逻辑
    pass


def get_db():
    """获取数据库会话"""
    pass
