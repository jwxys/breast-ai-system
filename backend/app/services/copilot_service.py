"""
医疗 Copilot 聊天服务

贯穿整个项目的智能助手，支持：
1. 超声影像分析解释
2. 诊断结果说明
3. 系统控制操作
4. 自然语言交互
"""

from __future__ import annotations

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.services.patient_service import PatientService
    from app.services.ultrasound_service import UltrasoundService
    from app.services.report_service import ReportService
    from app.services.visit_service import VisitService

# 延迟导入
torch = None
SQLAlchemy = None
AsyncSession = None


class MedicalCopilotService:
    """医疗 Copilot 服务"""
    
    def __init__(self, model_path: Optional[str] = None, use_default_model: bool = False):
        self.model_path = model_path or "ai_chat/results/medical-copilot/adapter"
        self.use_default_model = use_default_model
        
        # 延迟导入数据库
        global SQLAlchemy, AsyncSession
        try:
            from sqlalchemy.orm import Session as SQLAlchemySession
            from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType
            SQLAlchemy = SQLAlchemySession
            AsyncSession = AsyncSessionType
        except ImportError:
            pass
        
        # 延迟导入 torch
        global torch
        try:
            import torch as torch_module
            torch = torch_module
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        except ImportError:
            torch = None
            self.device = None
        
        # 模型和分词器
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
        # 会话存储
        self.sessions: Dict[str, ChatSession] = {}
        
        # 数据库会话（可选）
        self.db: Optional[Any] = None
        
        # 系统提示词
        self.system_prompt = """你是一名专业的医疗 AI 助手"医助小樱"，协助医生完成乳腺超声诊疗工作。

## 你的核心能力

### 1. 影像分析解释
- 解释 AI 超声分析结果（BI-RADS 分级、肿块特征等）
- 说明影像处理流程和技术细节
- 回答医生关于影像质量的疑问

### 2. 诊断结果说明
- 解释西医诊断依据（基于 BI-RADS 分级和临床特征）
- 提供鉴别诊断建议
- 推荐治疗方案
- 解答诊断相关问题

### 3. 系统控制操作
- 根据医生指令操作系统功能
- 执行患者管理、检查安排等操作
- 生成报告、导出数据等

## 重要说明

⚠️ 当前系统**未提供中医辨证功能**，因为未采集舌象、脉象等四诊信息。
⚠️ 不提供中医诊断、证型判定、方剂建议。
"""
    
    def _get_mode_name(self, mode: str) -> str:
        """获取模式中文名称"""
        names = {
            "general": "通用对话",
            "imaging": "影像分析",
            "diagnosis": "诊断辅助",
            "control": "系统控制",
        }
        return names.get(mode, "通用对话")
    
    def _get_welcome_message(self, mode: str) -> str:
        """根据模式返回欢迎消息"""
        messages = {
            "general": """您好！我是您的医疗 AI 助手小樱。我可以协助您完成以下工作：

📋 **患者管理** - 创建患者档案、查询病史
🔬 **超声检查** - 执行检查、AI 分析
📊 **诊断辅助** - 西医诊断建议
📝 **报告生成** - 自动生成检查报告
📈 **随访管理** - 制定随访计划
⚙️ **系统操作** - 数据导出、系统设置

请问今天需要我协助什么？""",
            
            "imaging": """您好！我已在**影像分析模式**。

我可以帮您：
- 解释 AI 超声分析结果
- 说明 BI-RADS 分级依据
- 分析肿块特征（大小、形态、边界等）
- 对比历史影像变化

请上传影像或描述需要分析的内容。""",
            
            "diagnosis": """您好！我已在**诊断辅助模式**。

我可以帮您：
- 解释西医诊断依据
- 提供鉴别诊断建议
- 推荐治疗方案

⚠️ 重要说明：当前系统未提供中医辨证功能（未采集舌象、脉象等四诊信息）。""",
            
            "control": """您好！我已在**系统控制模式**。

我可以帮您执行：
- 患者档案管理操作
- 检查流程控制
- 报告生成 and 发送
- 数据导出 and 统计

请告诉我需要执行的操作。""",
        }
        
        return messages.get(mode, messages["general"])
    
    async def send_message(
        self,
        session_id: str,
        user_message: str,
    ) -> str:
        """发送消息并获取回复"""
        if session_id not in self.sessions:
            raise ValueError(f"会话不存在：{session_id}")
        
        session = self.sessions[session_id]
        
        # 添加用户消息
        user_msg = ChatMessage(role="user", content=user_message)
        session.messages.append(user_msg)
        
        # 检测意图并切换到对应模式
        detected_mode = await self._detect_intent(user_message)
        if detected_mode != session.mode:
            session.mode = detected_mode
            mode_switch_msg = ChatMessage(
                role="assistant",
                content=f"已切换到**{self._get_mode_name(detected_mode)}模式**",
                metadata={"mode_switch": True},
            )
            session.messages.append(mode_switch_msg)
        
        # 获取 AI 回复
        if self.use_default_model:
            response = await self._rule_based_response(session, user_message)
        else:
            response = await self._model_inference(session)
        
        # 添加 AI 回复
        assistant_msg = ChatMessage(role="assistant", content=response)
        session.messages.append(assistant_msg)
        session.updated_at = datetime.now().isoformat()
        
        return response
    
    async def _detect_intent(self, user_message: str) -> str:
        """检测用户意图，返回对应模式"""
        message_lower = user_message.lower()
        
        # 影像分析相关
        imaging_keywords = ["影像", "超声", "bi-rads", "肿块", "回声", "边界", "形态", "钙化", "血流"]
        if any(kw in message_lower for kw in imaging_keywords):
            return "imaging"
        
        # 诊断相关
        diagnosis_keywords = ["诊断", "辨证", "分型", "证型", "舌苔", "脉象", "治则", "方剂"]
        if any(kw in message_lower for kw in diagnosis_keywords):
            return "diagnosis"
        
        # 系统控制相关
        control_keywords = ["创建", "删除", "更新", "导出", "生成", "发送", "安排", "设置", "操作"]
        if any(kw in message_lower for kw in control_keywords):
            return "control"
        
        return "general"
    
    def _get_mode_name(self, mode: str) -> str:
        """获取模式中文名称"""
        names = {
            "general": "通用对话",
            "imaging": "影像分析",
            "diagnosis": "诊断辅助",
            "control": "系统控制",
        }
        return names.get(mode, "通用对话")
    
    async def _model_inference(self, session: ChatSession) -> str:
        """使用模型推理"""
        messages = [{"role": m.role, "content": m.content} for m in session.messages]
        
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        
        response = self.tokenizer.decode(
            outputs[0][inputs.shape[1]:],
            skip_special_tokens=True,
        )
        
        return response.strip()
    
    async def _rule_based_response(
        self,
        session: ChatSession,
        user_message: str,
    ) -> str:
        """规则引擎响应（降级方案）"""
        
        # 意图识别 + 回复
        message_lower = user_message.lower()
        
        # 影像分析
        if "影像" in message_lower or "超声" in message_lower:
            return """我理解您在询问影像相关内容。

**影像分析功能**：
1. **AI 自动分析** - 上传超声图像后，AI 会自动检测肿块并分析特征
2. **BI-RADS 分级** - 根据形态、边界、回声等特征给出分级建议
3. **详细解释** - 点击报告可查看每个特征的详细分析

**当前状态**：
- 影像处理模块：✅ 就绪
- AI 推理服务：✅ 运行中

您想查看哪个患者的影像分析结果？"""
        
        # 诊断相关
        elif "诊断" in message_lower or "辨证" in message_lower:
            return """我理解您在询问诊断相关内容。

⚠️  **重要说明**：当前系统**仅支持西医诊断**（基于 BI-RADS 分级和超声特征）。

**系统功能**：
1. **西医诊断辅助** - 基于 BI-RADS 分级和临床特征
2. **鉴别诊断建议** - 提供鉴别诊断思路
3. **治疗方案推荐** - 基于西医诊疗指南

**系统限制**：
❌ 未采集中医四诊信息（舌象、脉象、详细问诊）
❌ 无法进行中医辨证
❌ 不提供中医处方建议

如需中医诊疗，请：
- 由执业中医师面诊
- 完成中医四诊信息采集
- 进行规范的中医辨证
"""
        
        # 系统控制
        elif any(kw in message_lower for kw in ["创建", "删除", "导出", "生成"]):
            return """我理解您想执行系统操作。

**可用操作**：
- 📋 `创建患者` - 新建患者档案
- 📝 `生成报告` - 生成检查报告
- 📤 `导出数据` - 导出统计报表
- 📅 `安排检查` - 预约超声检查
- ⚙️ `系统设置` - 配置系统参数

请告诉我具体要执行什么操作？例如："创建患者张三，35 岁" 或 "导出上个月的数据"。"""
        
        # 通用对话
        else:
            return """您好！我是您的医疗 AI 助手小樱。

我可以协助您：
- 🔬 **影像分析** - 解释 AI 超声分析结果
- 📊 **诊断辅助** - 中西医结合诊断建议
- ⚙️ **系统操作** - 患者管理、报告生成等
- 💬 **健康咨询** - 乳腺健康相关知识

请问有什么可以帮您？"""
    
    def get_session_status(self, session_id: str) -> ChatSession:
        """获取会话状态"""
        if session_id not in self.sessions:
            raise ValueError(f"会话不存在：{session_id}")
        return self.sessions[session_id]
    
    def close_session(self, session_id: str) -> None:
        """关闭会话"""
        if session_id in self.sessions:
            self.sessions[session_id].status = "closed"
            self.sessions[session_id].updated_at = datetime.now().isoformat()
    
    async def execute_system_command(
        self,
        session_id: str,
        command: str,
        params: Dict[str, Any],
        db: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """执行系统命令（由聊天触发）
        
        Args:
            session_id: 会话 ID
            command: 命令名称
            params: 命令参数
            db: 数据库会话（可选，如果不传则创建临时会话）
        """
        # 导入所需的服务
        from app.database import get_db_session
        
        # 获取数据库会话
        temp_db = False
        if db is None:
            try:
                db = await get_db_session().__anext__()
                temp_db = True
            except Exception as e:
                return {
                    "success": False,
                    "error": f"数据库连接失败：{str(e)}",
                }
        
        try:
            supported_commands = [
                "create_patient",
                "update_patient",
                "get_patient",
                "create_ultrasound",
                "run_ai_inference",
                "generate_report",
                "list_reports",
                "schedule_followup",
                "list_followups",
                "export_data",
            ]
            
            if command not in supported_commands:
                return {
                    "success": False,
                    "error": f"不支持的命令：{command}",
                    "supported": supported_commands,
                }
            
            # 执行对应命令
            if command == "create_patient":
                from app.services.patient_service import PatientService
                result = await self._cmd_create_patient(
                    params=params,
                    service=PatientService(db),
                )
            elif command == "update_patient":
                from app.services.patient_service import PatientService
                result = await self._cmd_update_patient(
                    params=params,
                    service=PatientService(db),
                )
            elif command == "get_patient":
                from app.services.patient_service import PatientService
                result = await self._cmd_get_patient(
                    params=params,
                    service=PatientService(db),
                )
            elif command == "create_ultrasound":
                from app.services.ultrasound_service import UltrasoundService
                result = await self._cmd_create_ultrasound(
                    params=params,
                    service=UltrasoundService(db),
                )
            elif command == "run_ai_inference":
                from app.services.ultrasound_service import UltrasoundService
                result = await self._cmd_run_ai_inference(
                    params=params,
                    service=UltrasoundService(db),
                )
            elif command == "generate_report":
                from app.services.report_service import ReportService
                result = await self._cmd_generate_report(
                    params=params,
                    service=ReportService(db),
                )
            elif command == "list_reports":
                from app.services.report_service import ReportService
                result = await self._cmd_list_reports(
                    params=params,
                    service=ReportService(db),
                )
            elif command == "schedule_followup":
                from app.services.visit_service import VisitService
                result = await self._cmd_schedule_followup(
                    params=params,
                    service=VisitService(db),
                )
            elif command == "list_followups":
                from app.services.visit_service import VisitService
                result = await self._cmd_list_followups(
                    params=params,
                    service=VisitService(db),
                )
            elif command == "export_data":
                result = await self._cmd_export_data(
                    params=params,
                )
            else:
                result = {
                    "success": False,
                    "error": "命令未实现",
                }
            
            # 添加成功标记
            if isinstance(result, dict):
                result.setdefault("success", True)
            
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"命令执行失败：{str(e)}",
            }
        finally:
            # 关闭临时创建的数据库会话
            if temp_db and db:
                try:
                    await db.close()
                except:
                    pass
    
    async def _cmd_create_patient(
        self,
        params: Dict[str, Any],
        service: 'PatientService',
    ) -> Dict[str, Any]:
        """创建患者"""
        from app.schemas.patient import PatientCreate
        
        # 参数验证
        required_fields = ["name", "age", "gender"]
        for field in required_fields:
            if field not in params:
                return {
                    "success": False,
                    "message": f"缺少必要字段：{field}",
                }
        
        # 构建患者创建对象
        patient_data = PatientCreate(
            name=params["name"],
            age=params.get("age"),
            gender=params.get("gender", "female"),
            phone=params.get("phone"),
            id_number=params.get("id_number"),
            address=params.get("address"),
            allergy_history=params.get("allergy_history"),
            family_history=params.get("family_history"),
            menstrual_history=params.get("menstrual_history"),
        )
        
        # 调用服务创建
        patient = await service.create(patient_data)
        
        return {
            "success": True,
            "message": f"患者 {patient.name} 创建成功",
            "patient_id": patient.id,
            "patient_name": patient.name,
            "patient_no": patient.patient_no,
        }
    
    async def _cmd_update_patient(
        self,
        params: Dict[str, Any],
        service: 'PatientService',
    ) -> Dict[str, Any]:
        """更新患者"""
        patient_id = params.get("patient_id")
        if not patient_id:
            return {"success": False, "message": "缺少患者 ID"}
        
        from app.schemas.patient import PatientUpdate
        
        update_data = PatientUpdate(**{
            k: v for k, v in params.items()
            if k not in ["patient_id"] and v is not None
        })
        
        patient = await service.update(patient_id, update_data)
        
        return {
            "success": True,
            "message": f"患者 {patient.name} 信息已更新",
            "patient_id": patient.id,
        }
    
    async def _cmd_get_patient(
        self,
        params: Dict[str, Any],
        service: 'PatientService',
    ) -> Dict[str, Any]:
        """查询患者"""
        patient_id = params.get("patient_id")
        if not patient_id:
            return {"success": False, "message": "缺少患者 ID"}
        
        patient = await service.get(patient_id)
        
        if not patient:
            return {"success": False, "message": f"患者 {patient_id} 不存在"}
        
        return {
            "success": True,
            "message": f"找到患者：{patient.name}",
            "patient": {
                "id": patient.id,
                "name": patient.name,
                "age": patient.age,
                "gender": patient.gender,
                "phone": patient.phone,
                "patient_no": patient.patient_no,
            },
        }
    
    async def _cmd_update_patient(
        self,
        params: Dict[str, Any],
        service: 'PatientService',
    ) -> Dict[str, Any]:
        """更新患者"""
        patient_id = params.get("patient_id")
        if not patient_id:
            return {"success": False, "message": "缺少患者 ID"}
        
        from app.schemas.patient import PatientUpdate
        
        update_data = PatientUpdate(**{
            k: v for k, v in params.items()
            if k not in ["patient_id"] and v is not None
        })
        
        patient = await service.update(patient_id, update_data)
        
        return {
            "success": True,
            "message": f"患者 {patient.name} 信息已更新",
            "patient_id": patient.id,
        }
    
    async def _cmd_create_ultrasound(
        self,
        params: Dict[str, Any],
        service: 'UltrasoundService',
    ) -> Dict[str, Any]:
        """创建超声检查"""
        from app.schemas.ultrasound import UltrasoundCreate
        
        patient_id = params.get("patient_id")
        if not patient_id:
            return {"success": False, "message": "缺少患者 ID"}
        
        ultrasound_data = UltrasoundCreate(
            patient_id=patient_id,
            exam_date=params.get("exam_date"),
            exam_type=params.get("exam_type", "乳腺超声"),
            clinical_findings=params.get("clinical_findings"),
            examiner_id=params.get("examiner_id"),
        )
        
        ultrasound = await service.create(ultrasound_data)
        
        return {
            "success": True,
            "message": f"超声检查已创建",
            "ultrasound_id": ultrasound.id,
            "patient_id": ultrasound.patient_id,
            "exam_no": ultrasound.exam_no,
        }
    
    async def _cmd_run_ai_inference(
        self,
        params: Dict[str, Any],
        service: 'UltrasoundService',
    ) -> Dict[str, Any]:
        """执行 AI 推理"""
        ultrasound_id = params.get("ultrasound_id")
        if not ultrasound_id:
            return {"success": False, "message": "缺少超声检查 ID"}
        
        # 调用 UltrasoundService 的 analyze 方法
        result = await service.analyze(ultrasound_id)
        
        return {
            "success": True,
            "message": f"AI 推理分析完成",
            "ultrasound_id": ultrasound_id,
            "birads": result.get("birads"),
            "birads_score": result.get("birads_score"),
            "features": result.get("features"),
            "confidence": result.get("confidence", 0),
            "suggestion": result.get("suggestion"),
        }
    
    async def _cmd_create_ultrasound(
        self,
        params: Dict[str, Any],
        service: 'UltrasoundService',
    ) -> Dict[str, Any]:
        """创建超声检查"""
        from app.schemas.ultrasound import UltrasoundCreate
        
        patient_id = params.get("patient_id")
        if not patient_id:
            return {"success": False, "message": "缺少患者 ID"}
        
        ultrasound_data = UltrasoundCreate(
            patient_id=patient_id,
            exam_date=params.get("exam_date"),
            exam_type=params.get("exam_type", "乳腺超声"),
            clinical_findings=params.get("clinical_findings"),
            examiner_id=params.get("examiner_id"),
        )
        
        ultrasound = await service.create(ultrasound_data)
        
        return {
            "success": True,
            "message": f"超声检查已创建",
            "ultrasound_id": ultrasound.id,
            "patient_id": ultrasound.patient_id,
        }
    
    async def _cmd_run_ai_inference(
        self,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """执行 AI 推理"""
        ultrasound_id = params.get("ultrasound_id")
        if not ultrasound_id:
            return {"success": False, "message": "缺少超声检查 ID"}
        
        # TODO: 调用 AI 推理服务
        # from app.services.ai_inference_service import AIInferenceService
        # result = await AIInferenceService().run(ultrasound_id)
        
        return {
            "success": True,
            "message": f"AI 推理已完成",
            "ultrasound_id": ultrasound_id,
            "birads": "4a",  # 示例数据
            "confidence": 0.85,
        }
    
    async def _cmd_generate_report(
        self,
        params: Dict[str, Any],
        service: 'ReportService',
    ) -> Dict[str, Any]:
        """生成报告"""
        patient_id = params.get("patient_id")
        visit_id = params.get("visit_id")
        ultrasound_id = params.get("ultrasound_id")
        doctor_id = params.get("doctor_id")
        
        if not patient_id:
            return {"success": False, "message": "缺少患者 ID"}
        
        if not visit_id:
            return {"success": False, "message": "缺少就诊 ID"}
        
        # 调用 ReportService 的 generate_ai_diagnosis_report 方法
        result = service.generate_ai_diagnosis_report(
            patient_id=patient_id,
            visit_id=visit_id,
            ultrasound_id=ultrasound_id,
            created_by=doctor_id or 1,  # 默认使用第一个医生
        )
        
        return {
            "success": True,
            "message": f"报告已生成",
            "report_id": result.get("report_id"),
            "report_no": result.get("report_no"),
            "patient_id": patient_id,
        }
    
    async def _cmd_list_reports(
        self,
        params: Dict[str, Any],
        service: 'ReportService',
    ) -> Dict[str, Any]:
        """查询报告列表"""
        patient_id = params.get("patient_id")
        limit = params.get("limit", 10)
        
        if not patient_id:
            return {"success": False, "message": "缺少患者 ID"}
        
        # 调用 ReportService 的 get_patient_reports 方法
        reports = service.get_patient_reports(patient_id)
        
        # 格式化报告列表
        report_list = [
            {
                "id": r.id,
                "report_no": r.report_no,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "birads": r.birads,
                "conclusion": r.conclusion,
            }
            for r in reports[:limit]
        ]
        
        return {
            "success": True,
            "message": f"查询到 {len(report_list)} 份报告",
            "reports": report_list,
            "total": len(reports),
        }
    
    async def _cmd_schedule_followup(
        self,
        params: Dict[str, Any],
        service: 'VisitService',
    ) -> Dict[str, Any]:
        """安排随访"""
        from app.schemas.visit import VisitCreate
        
        patient_id = params.get("patient_id")
        if not patient_id:
            return {"success": False, "message": "缺少患者 ID"}
        
        followup_data = VisitCreate(
            patient_id=patient_id,
            visit_type=params.get("visit_type", "随访"),
            visit_date=params.get("visit_date"),
            purpose=params.get("purpose"),
            doctor_id=params.get("doctor_id"),
        )
        
        visit = await service.create(followup_data)
        
        return {
            "success": True,
            "message": f"随访已安排",
            "visit_id": visit.id,
            "visit_date": visit.visit_date.isoformat() if visit.visit_date else None,
            "visit_no": visit.visit_no,
        }
    
    async def _cmd_list_followups(
        self,
        params: Dict[str, Any],
        service: 'VisitService',
    ) -> Dict[str, Any]:
        """查询随访列表"""
        patient_id = params.get("patient_id")
        limit = params.get("limit", 10)
        
        if not patient_id:
            return {"success": False, "message": "缺少患者 ID"}
        
        # 调用 VisitService 的 list 方法
        visits = await service.list(patient_id=patient_id, limit=limit)
        
        # 格式化随访列表
        visit_list = [
            {
                "id": v.id,
                "visit_no": v.visit_no,
                "visit_type": v.visit_type,
                "visit_date": v.visit_date.isoformat() if v.visit_date else None,
                "purpose": v.purpose,
            }
            for v in visits
        ]
        
        return {
            "success": True,
            "message": f"查询到 {len(visit_list)} 条随访记录",
            "followups": visit_list,
            "total": len(visits),
        }
    
    async def _cmd_export_data(
        self,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """导出数据"""
        export_type = params.get("type", "patients")
        date_from = params.get("date_from")
        date_to = params.get("date_to")
        format = params.get("format", "csv")
        
        # TODO: 实现实际的数据导出功能
        # 现在返回一个模拟结果
        record_count = 0  # 从数据库查询实际数量
        
        return {
            "success": True,
            "message": f"数据导出任务已创建",
            "export_type": export_type,
            "format": format,
            "date_from": date_from,
            "date_to": date_to,
            "record_count": record_count,
            "file_path": f"/exports/{export_type}_{datetime.now().strftime('%Y%m%d')}.{format}",
        }


# 单例
_copilot_service: Optional[MedicalCopilotService] = None


def get_copilot_service(
    model_path: Optional[str] = None,
) -> MedicalCopilotService:
    """获取医疗 Copilot 服务实例"""
    global _copilot_service
    
    if _copilot_service is None:
        _copilot_service = MedicalCopilotService(model_path=model_path)
    
    return _copilot_service
