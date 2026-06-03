"""
AI 超声前问诊 API 路由
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.services.inquiry_service import get_inquiry_service

router = APIRouter(prefix="/inquiry", tags=["AI 超声前问诊"])


# ============ 请求/响应模型 ============

class CreateInquirySessionRequest(BaseModel):
    """创建问诊会话请求"""
    patient_id: Optional[int] = None
    visit_id: Optional[int] = None


class CreateInquirySessionResponse(BaseModel):
    """创建问诊会话响应"""
    session_id: str
    welcome_message: str
    created_at: str


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    message: str = Field(..., description="用户消息内容", min_length=1, max_length=2000)


class SendMessageResponse(BaseModel):
    """发送消息响应"""
    session_id: str
    response: str
    collected_fields: Dict[str, Any]
    updated_at: str


class SessionStatusResponse(BaseModel):
    """会话状态响应"""
    session_id: str
    patient_id: Optional[int]
    visit_id: Optional[int]
    message_count: int
    collected_fields: Dict[str, Any]
    status: str
    created_at: str
    updated_at: str


# ============ 依赖注入 ============

def get_service():
    """获取问诊服务实例"""
    return get_inquiry_service()


# ============ API 端点 ============

@router.post("/sessions", response_model=CreateInquirySessionResponse)
async def create_inquiry_session(
    request: CreateInquirySessionRequest,
    service=Depends(get_service),
) -> CreateInquirySessionResponse:
    """
    创建新的超声前问诊会话
    
    - **patient_id**: 患者 ID (可选)
    - **visit_id**: 就诊 ID (可选)
    
    返回会话 ID 和欢迎消息
    """
    try:
        session_id = await service.create_session(
            patient_id=request.patient_id,
            visit_id=request.visit_id,
        )
        
        session = service.get_session_status(session_id)
        
        return CreateInquirySessionResponse(
            session_id=session_id,
            welcome_message=session.messages[0].content,
            created_at=session.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/sessions/{session_id}/messages",
    response_model=SendMessageResponse,
)
async def send_inquiry_message(
    session_id: str,
    request: SendMessageRequest,
    service=Depends(get_service),
) -> SendMessageResponse:
    """
    在问诊会话中发送消息并获取 AI 回复
    
    - **session_id**: 会话 ID
    - **message**: 用户消息内容
    
    返回 AI 回复和已收集的信息字段
    """
    try:
        # 验证会话存在
        session = service.get_session_status(session_id)
        
        # 发送消息
        response_text = await service.send_message(
            session_id=session_id,
            user_message=request.message,
        )
        
        # 获取更新后的会话
        session = service.get_session_status(session_id)
        
        return SendMessageResponse(
            session_id=session_id,
            response=response_text,
            collected_fields=session.collected_fields,
            updated_at=session.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sessions/{session_id}",
    response_model=SessionStatusResponse,
)
async def get_session_status(
    session_id: str,
    service=Depends(get_service),
) -> SessionStatusResponse:
    """
    获取问诊会话状态
    
    - **session_id**: 会话 ID
    
    返回会话信息和已收集的信息字段
    """
    try:
        session = service.get_session_status(session_id)
        
        return SessionStatusResponse(
            session_id=session.session_id,
            patient_id=session.patient_id,
            visit_id=session.visit_id,
            message_count=len(session.messages),
            collected_fields=session.collected_fields,
            status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions/{session_id}/close")
async def close_session(
    session_id: str,
    service=Depends(get_service),
):
    """
    关闭问诊会话
    
    - **session_id**: 会话 ID
    
    关闭后会话将不再接受新消息
    """
    try:
        service.close_session(session_id)
        return {"message": "会话已关闭", "session_id": session_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "AI 超声前问诊",
        "timestamp": datetime.now().isoformat(),
    }
