"""
医疗 Copilot 聊天 API 路由
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.core.database import get_db
from app.services.copilot_service import get_copilot_service

router = APIRouter(prefix="/copilot", tags=["医疗 Copilot 聊天助手"])


# ============ 请求/响应模型 ============

class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    user_id: Optional[int] = None
    patient_id: Optional[int] = None
    visit_id: Optional[int] = None
    mode: str = "general"  # general/imaging/diagnosis/control


class CreateSessionResponse(BaseModel):
    """创建会话响应"""
    session_id: str
    welcome_message: str
    mode: str
    created_at: str


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    message: str = Field(..., min_length=1, max_length=5000)


class SendMessageResponse(BaseModel):
    """发送消息响应"""
    session_id: str
    response: str
    mode: str
    suggested_actions: List[str]
    updated_at: str


class SessionStatusResponse(BaseModel):
    """会话状态响应"""
    session_id: str
    user_id: Optional[int]
    patient_id: Optional[int]
    visit_id: Optional[int]
    mode: str
    message_count: int
    status: str
    created_at: str
    updated_at: str


class MessageHistoryResponse(BaseModel):
    """消息历史响应"""
    session_id: str
    messages: List[Dict[str, Any]]
    total_count: int


class ExecuteCommandRequest(BaseModel):
    """执行系统命令请求"""
    command: str
    params: Dict[str, Any] = Field(default_factory=dict)


class ExecuteCommandResponse(BaseModel):
    """执行系统命令响应"""
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None


# ============ 依赖注入 ============

def get_service():
    """获取 Copilot 服务实例"""
    return get_copilot_service()


# ============ API 端点 ============

@router.post("/sessions", response_model=CreateSessionResponse)
async def create_copilot_session(
    request: CreateSessionRequest,
    service=Depends(get_service),
) -> CreateSessionResponse:
    """
    创建医疗 Copilot 聊天会话
    
    - **user_id**: 医生用户 ID
    - **patient_id**: 关联患者 ID (可选)
    - **visit_id**: 关联就诊 ID (可选)
    - **mode**: 初始模式 (general/imaging/diagnosis/control)
    
    返回会话 ID 和欢迎消息
    """
    try:
        session_id = await service.create_session(
            user_id=request.user_id,
            patient_id=request.patient_id,
            visit_id=request.visit_id,
            mode=request.mode,
        )
        
        session = service.get_session_status(session_id)
        
        return CreateSessionResponse(
            session_id=session_id,
            welcome_message=session.messages[-1].content,
            mode=session.mode,
            created_at=session.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/sessions/{session_id}/messages",
    response_model=SendMessageResponse,
)
async def send_copilot_message(
    session_id: str,
    request: SendMessageRequest,
    service=Depends(get_service),
) -> SendMessageResponse:
    """
    在 Copilot 会话中发送消息并获取智能回复
    
    - **session_id**: 会话 ID
    - **message**: 用户消息内容
    
    返回 AI 回复、当前模式和建议操作
    """
    try:
        session = service.get_session_status(session_id)
        
        response_text = await service.send_message(
            session_id=session_id,
            user_message=request.message,
        )
        
        session = service.get_session_status(session_id)
        
        # 生成建议操作
        suggested_actions = await generate_suggested_actions(
            session.mode,
            request.message,
        )
        
        return SendMessageResponse(
            session_id=session_id,
            response=response_text,
            mode=session.mode,
            suggested_actions=suggested_actions,
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
    获取 Copilot 会话状态
    """
    try:
        session = service.get_session_status(session_id)
        
        return SessionStatusResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            patient_id=session.patient_id,
            visit_id=session.visit_id,
            mode=session.mode,
            message_count=len([m for m in session.messages if m.role in ["user", "assistant"]]),
            status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/sessions/{session_id}/history",
    response_model=MessageHistoryResponse,
)
async def get_message_history(
    session_id: str,
    limit: int = 50,
    service=Depends(get_service),
) -> MessageHistoryResponse:
    """
    获取消息历史记录
    
    - **limit**: 最大返回条数 (默认 50)
    """
    try:
        session = service.get_session_status(session_id)
        
        # 排除 system 消息
        user_messages = [
            {"role": m.role, "content": m.content, "timestamp": m.timestamp, "metadata": m.metadata}
            for m in session.messages
            if m.role != "system"
        ][-limit:]
        
        return MessageHistoryResponse(
            session_id=session_id,
            messages=user_messages,
            total_count=len(user_messages),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/sessions/{session_id}/commands",
    response_model=ExecuteCommandResponse,
)
async def execute_system_command(
    session_id: str,
    request: ExecuteCommandRequest,
    db=Depends(get_db),
    service=Depends(get_service),
) -> ExecuteCommandResponse:
    """
    通过 Copilot 执行系统命令
    
    - **session_id**: 会话 ID
    - **command**: 命令名称
    - **params**: 命令参数
    
    支持的命令：
    - create_patient: 创建患者
    - update_patient: 更新患者
    - get_patient: 查询患者
    - create_ultrasound: 创建超声检查
    - run_ai_inference: 执行 AI 推理
    - generate_report: 生成报告
    - list_reports: 查询报告列表
    - schedule_followup: 安排随访
    - list_followups: 查询随访列表
    - export_data: 导出数据
    """
    try:
        # 验证会话
        session = service.get_session_status(session_id)
        
        # 执行命令（传入数据库会话）
        result = await service.execute_system_command(
            session_id=session_id,
            command=request.command,
            params=request.params,
            db=db,
        )
        
        # 生成友好的反馈消息
        feedback_message = generate_feedback_message(
            request.command,
            result,
        )
        
        # 将反馈添加到会话
        if feedback_message:
            from app.services.copilot_service import ChatMessage
            feedback_msg = ChatMessage(
                role="assistant",
                content=feedback_message,
                metadata={"command_result": True},
            )
            session.messages.append(feedback_msg)
        
        return ExecuteCommandResponse(
            success=result.get("success", False),
            message=result.get("message", "命令执行完成"),
            result=result,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 辅助函数 ============

async def generate_suggested_actions(mode: str, user_message: str) -> List[str]:
    """根据当前模式和消息生成建议操作"""
    
    if mode == "imaging":
        return [
            "上传超声图像",
            "查看 AI 分析报告",
            "对比历史影像",
            "调整 BI-RADS 分级",
            "生成影像诊断报告",
        ]
    
    elif mode == "diagnosis":
        return [
            "查看诊断依据",
            "中医辨证分型",
            "推荐治疗方案",
            "鉴别诊断分析",
            "生成诊断报告",
        ]
    
    elif mode == "control":
        return [
            "创建新患者",
            "安排检查",
            "生成报告",
            "导出数据",
            "安排随访",
        ]
    
    else:  # general
        return [
            "影像分析",
            "诊断辅助",
            "患者管理",
            "系统操作",
        ]


def generate_feedback_message(command: str, result: Dict[str, Any]) -> str:
    """生成命令执行的反馈消息"""
    
    if not result.get("success"):
        return f"⚠️ 命令执行失败：{result.get('error', '未知错误')}"
    
    feedback_templates = {
        "create_patient": lambda r: f"✅ 患者 **{r.get('patient_name')}** 创建成功！\n\n"
                                   f"📋 信息摘要:\n"
                                   f"- 患者 ID: {r.get('patient_id')}\n"
                                   f"- 姓名：{r.get('patient_name')}\n"
                                   f"\n下一步操作？",
        
        "create_ultrasound": lambda r: f"✅ 超声检查已创建！\n\n"
                                      f"📋 检查信息:\n"
                                      f"- 检查 ID: {r.get('ultrasound_id')}\n"
                                      f"- 患者 ID: {r.get('patient_id')}\n"
                                      f"\n需要立即执行 AI 分析吗？",
        
        "run_ai_inference": lambda r: f"🤖 AI 推理分析完成！\n\n"
                                      f"📊 分析结果:\n"
                                      f"- BI-RADS 分级：**{r.get('birads', 'N/A')}**\n"
                                      f"- 置信度：{r.get('confidence', 0) * 100:.1f}%\n"
                                      f"\n需要生成详细报告吗？",
        
        "generate_report": lambda r: f"📝 报告已生成！\n\n"
                                    f"📋 报告信息:\n"
                                    f"- 报告 ID: {r.get('report_id')}\n"
                                    f"- 患者 ID: {r.get('patient_id')}\n"
                                    f"\n需要查看或发送报告吗？",
        
        "schedule_followup": lambda r: f"📅 随访已安排！\n\n"
                                      f"📋 随访信息:\n"
                                      f"- 随访 ID: {r.get('visit_id')}\n"
                                      f"- 随访日期：{r.get('visit_date', 'TBD')}\n"
                                      f"\n需要设置提醒吗？",
        
        "export_data": lambda r: f"📤 数据导出任务已创建！\n\n"
                                f"📋 导出信息:\n"
                                f"- 导出类型：{r.get('export_type')}\n"
                                f"- 格式：{r.get('format')}\n"
                                f"- 记录数：{r.get('record_count', 0)}\n"
                                f"\n导出完成后会通知您。",
    }
    
    template = feedback_templates.get(command)
    if template:
        return template(result)
    
    return f"✅ 命令 `{command}` 执行成功！"
