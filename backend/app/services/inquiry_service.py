"""
AI 超声前问诊对话服务

使用微调后的 Kimi K2.5 模型进行交互式问诊
"""

import os
import asyncio
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field

# 延迟导入 torch
torch = None


class InquiryMessage(BaseModel):
    """问诊消息"""
    role: str = Field(..., description="角色：user/assistant")
    content: str = Field(..., description="消息内容")


class InquirySession(BaseModel):
    """问诊会话"""
    session_id: str
    patient_id: Optional[int] = None
    visit_id: Optional[int] = None
    messages: List[InquiryMessage] = []
    created_at: str
    updated_at: str
    status: str = "active"  # active/completed/closed
    
    # 收集的信息
    collected_fields: Dict[str, Any] = Field(default_factory=dict)


class InquiryService:
    """超声前问诊服务"""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        use_default_model: bool = False,
    ):
        self.model_path = model_path or "ai_chat/results/kimi-k2-inquiry/adapter"
        self.use_default_model = use_default_model
        
        # 延迟导入 torch
        global torch
        try:
            import torch as torch_module
            torch = torch_module
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        except ImportError:
            torch = None
            self.device = None
        
        # 模型和分词器 (延迟加载)
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
        # 会话存储
        self.sessions: Dict[str, InquirySession] = {}
        
        # 系统提示词
        self.system_prompt = """你是一名专业的乳腺超声检查前问诊助手，名字叫"小樱"。你的任务是在患者进行超声检查前，通过自然对话收集必要的医疗信息。

## 你的角色
- 友好、专业、有同理心的 AI 医疗助手
- 专门针对乳腺诊疗场景进行优化
- 使用温和、易懂的中文与患者交流
- 保护患者隐私，不询问与检查无关的信息

## 需要收集的信息
按以下顺序逐步询问：
1. **基本信息**：称呼、年龄、联系方式
2. **主诉**：哪里不舒服、主要症状、发现时间
3. **现病史**：症状详细描述、疼痛程度、与月经关系
4. **既往史**：乳腺疾病史、手术史、药物过敏
5. **家族史**：乳腺疾病家族史
6. **月经生育史**：月经周期、生育情况
7. **生活方式**：作息、饮食、运动习惯
8. **检查准备**：解释检查流程、注意事项

## 对话原则
1. **一次只问一个问题**，不要连珠炮式提问
2. **同理心回应**：理解患者的担忧，给予安慰
3. **医学准确**：使用正确的医学术语，但要用通俗语言解释
4. **自然流畅**：像真实医生一样的对话风格
5. **鼓励患者**：对患者的担忧给予积极回应

## 输出格式
- 用自然对话方式回复
- 不要使用项目符号或列表
- 长度适中，50-150 字为宜
- 在合适时机总结已收集的信息

## 安全边界
- 不提供诊断结果
- 不开具处方或用药建议
- 遇到紧急情况建议患者立即就医
- 不讨论与乳腺检查无关的医疗问题"""
        
    async def initialize(self) -> bool:
        """异步初始化模型"""
        if not self.use_default_model:
            try:
                # 延迟导入，避免启动失败
                from unsloth import FastLanguageModel
                
                print(f"加载微调模型：{self.model_path}")
                
                if not os.path.exists(self.model_path):
                    print(f"警告：模型路径不存在，使用默认模型")
                    self.use_default_model = True
                    return await self._load_default_model()
                
                # 加载微调后的模型
                self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                    model_name=self.model_path,
                    max_seq_length=4096,
                    dtype=None,
                    load_in_4bit=False,
                )
                
                FastLanguageModel.for_inference(self.model)
                self.is_loaded = True
                print("✅ 微调模型加载成功")
                return True
                
            except Exception as e:
                print(f"加载微调模型失败：{e}")
                print("降级使用默认模型")
                self.use_default_model = True
                return await self._load_default_model()
        else:
            return await self._load_default_model()
    
    async def _load_default_model(self) -> bool:
        """加载默认模型 (规则引擎)"""
        print("使用规则引擎模式 (无模型)")
        self.is_loaded = True
        return True
    
    async def create_session(
        self,
        patient_id: Optional[int] = None,
        visit_id: Optional[int] = None,
    ) -> str:
        """创建新会话"""
        import uuid
        
        session_id = str(uuid.uuid4())
        
        session = InquirySession(
            session_id=session_id,
            patient_id=patient_id,
            visit_id=visit_id,
            messages=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        
        self.sessions[session_id] = session
        
        # 发送欢迎消息
        welcome_msg = InquiryMessage(
            role="assistant",
            content="您好！我是您的 AI 健康助手小樱，专门协助乳腺诊疗相关的问诊工作。在检查开始前，我想了解您的一些基本情况，这样可以帮助医生更准确地为您诊断。我们的对话是完全保密的，请放心。请问您贵姓？"
        )
        session.messages.append(welcome_msg)
        
        return session_id
    
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
        user_msg = InquiryMessage(role="user", content=user_message)
        session.messages.append(user_msg)
        
        # 获取 AI 回复
        if self.use_default_model:
            response = await self._rule_based_response(session)
        else:
            response = await self._model_inference(session)
        
        # 更新会话
        session.messages.append(InquiryMessage(role="assistant", content=response))
        session.updated_at = datetime.now().isoformat()
        
        # 智能收集信息
        await self._update_collected_fields(session, user_message)
        
        return response
    
    async def _model_inference(self, session: InquirySession) -> str:
        """使用模型推理"""
        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        messages.extend([
            {"role": m.role, "content": m.content}
            for m in session.messages
        ])
        
        # Tokenize
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        
        # Decode (只取新生成的部分)
        response = self.tokenizer.decode(
            outputs[0][inputs.shape[1]:],
            skip_special_tokens=True,
        )
        
        return response.strip()
    
    async def _rule_based_response(self, session: InquirySession) -> str:
        """规则引擎响应 (降级方案)"""
        # 简单的基于规则的回复
        last_user_msg = session.messages[-1].content.lower()
        
        # 关键词匹配
        if any(kw in last_user_msg for kw in ["你是什么", "你是谁", "你是哪位"]):
            return "您好！我是您的 AI 健康助手小樱，专门协助乳腺诊疗相关的问诊工作。我会帮助您完成检查前的信息采集，让医生更好地了解您的情况。"
        
        elif any(kw in last_user_msg for kw in ["姓什么", "贵姓", "怎么称呼"]):
            user_name = self._extract_name(last_user_msg)
            if user_name:
                session.collected_fields["称呼"] = user_name
                return f"{user_name}您好！请问您今年多大年龄了？"
            else:
                return "好的，请问您怎么称呼？"
        
        elif any(kw in last_user_msg for kw in ["多大", "年龄", "几岁"]):
            age = self._extract_age(last_user_msg)
            if age:
                session.collected_fields["年龄"] = age
                return f"好的，{age}岁。请问您的手机号是多少？方便我们后续联系您和发送检查报告。"
            else:
                return "好的，请告诉我您的年龄。"
        
        elif any(kw in last_user_msg for kw in ["手机号", "电话", "联系方式"]):
            phone = self._extract_phone(last_user_msg)
            if phone:
                session.collected_fields["联系方式"] = phone
                return f"好的，已经记录您的联系方式。请问您今天主要是哪里不舒服来做检查呢？"
            else:
                return "好的，请留下您的联系电话。"
        
        else:
            # 默认回复
            return "明白了，感谢您的配合。请问还有其他需要了解的情况吗？或者您对检查有什么疑问？"
    
    async def _update_collected_fields(
        self,
        session: InquirySession,
        user_message: str,
    ):
        """智能更新收集的字段"""
        # 简单的信息提取
        # 实际应用中应使用 NER 或更复杂的提取方法
        pass
    
    def _extract_name(self, text: str) -> Optional[str]:
        """提取姓名"""
        # 简化实现
        if "姓" in text and " " in text:
            return text.split("姓")[1][:1]
        return None
    
    def _extract_age(self, text: str) -> Optional[int]:
        """提取年龄"""
        import re
        match = re.search(r'(\d+) 岁', text)
        if match:
            return int(match.group(1))
        return None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """提取电话号码"""
        import re
        match = re.search(r'1[3-9]\d{9}', text)
        if match:
            return match.group(0)
        return None
    
    def get_session_status(self, session_id: str) -> InquirySession:
        """获取会话状态"""
        if session_id not in self.sessions:
            raise ValueError(f"会话不存在：{session_id}")
        return self.sessions[session_id]
    
    def close_session(self, session_id: str) -> None:
        """关闭会话"""
        if session_id in self.sessions:
            self.sessions[session_id].status = "closed"
            self.sessions[session_id].updated_at = datetime.now().isoformat()


# 单例
_inquiry_service: Optional[InquiryService] = None


def get_inquiry_service(
    model_path: Optional[str] = None,
) -> InquiryService:
    """获取问诊服务实例"""
    global _inquiry_service
    
    if _inquiry_service is None:
        _inquiry_service = InquiryService(model_path=model_path)
    
    return _inquiry_service
