"""
Kimi AI 推理服务

使用 Moonshot AI (Kimi) 的 API 进行医疗对话推理
"""
import os
import json
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.config import settings


class KimiMessage(BaseModel):
    """Kimi 消息格式"""
    role: str  # "system", "user", "assistant"
    content: str


class KimiCompletionRequest(BaseModel):
    """Kimi 完成请求"""
    model: str = "moonshot-v1-8k"
    messages: List[KimiMessage]
    temperature: float = 0.7
    max_tokens: int = 2048


class KimiCompletionResponse(BaseModel):
    """Kimi 完成响应"""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class KimiAIService:
    """Kimi AI 服务"""
    
    def __init__(self):
        self.api_key = os.getenv("KIMI_API_KEY", "")
        self.base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
        self.model = os.getenv("KIMI_MODEL", "moonshot-v1-8k")
        self.client: Optional[httpx.AsyncClient] = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
        return self.client
    
    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()
            self.client = None
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        发送聊天请求到 Kimi
        
        Args:
            messages: 对话历史 [{role: "user"|"assistant", content: "..."}]
            system_prompt: 系统提示词
            temperature: 温度参数 (0-1)
            max_tokens: 最大生成 token 数
            
        Returns:
            AI 回复内容
        """
        if not self.api_key:
            # 无 API Key 时返回降级回复
            return self._fallback_response(messages)
        
        # 构建消息列表
        kimi_messages = []
        
        # 添加系统提示词
        if system_prompt:
            kimi_messages.append(KimiMessage(role="system", content=system_prompt))
        
        # 添加对话历史
        for msg in messages:
            kimi_messages.append(KimiMessage(role=msg["role"], content=msg["content"]))
        
        # 构建请求
        request = KimiCompletionRequest(
            model=self.model,
            messages=kimi_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        try:
            client = self._get_client()
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=request.model_dump(),
            )
            response.raise_for_status()
            
            # 解析响应
            data = KimiCompletionResponse(**response.json())
            assistant_message = data.choices[0]["message"]["content"]
            
            return assistant_message.strip()
            
        except httpx.HTTPError as e:
            print(f"Kimi API 请求失败：{e}")
            return self._fallback_response(messages)
        except Exception as e:
            print(f"Kimi API 异常：{e}")
            return self._fallback_response(messages)
    
    def _fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """降级回复（当 API Key 不存在或请求失败时）"""
        return """🔒 **Kimi AI 服务未配置**

请在环境变量中设置 Kimi API Key：
```bash
export KIMI_API_KEY="your-api-key"
```

或使用默认的规则引擎模式。

**当前可用功能**：
- 医学知识问答（规则引擎）
- 系统操作控制
- 报告生成指导

如需启用 Kimi AI，请联系管理员配置 API Key。"""


# 全局服务实例
_kimi_service: Optional[KimiAIService] = None


def get_kimi_service() -> KimiAIService:
    """获取 Kimi AI 服务实例"""
    global _kimi_service
    
    if _kimi_service is None:
        _kimi_service = KimiAIService()
    
    return _kimi_service


# Kimi 专用提示词
KIMI_SYSTEM_PROMPT = """你是一名专业的医疗 AI 助手"医助小樱"，协助医生完成乳腺超声诊疗工作。

## 你的核心能力

### 1. 影像分析解释
- 解释 AI 超声分析结果（BI-RADS 分级、肿块特征等）
- 说明影像处理流程和技术细节
- 回答医生关于影像质量的疑问

### 2. 诊断辅助
- 解释西医诊断依据（基于 BI-RADS 分级和临床特征）
- 提供鉴别诊断思路
- 推荐检查检验项目

### 3. 医患沟通辅助
- 解释医学术语
- 提供通俗易懂的疾病说明
- 解答患者常见疑问

## 重要说明

✅ **你仅支持西医诊断辅助**
❌ 不能进行中医辨证（未采集舌象、脉象等四诊信息）
❌ 不能提供中医处方建议
❌ 不能替代医生的专业判断

## 回复风格

- 专业但通俗易懂
- 使用结构化表达（如分点列出）
- 重要信息用**粗体**标注
- 使用 emoji 增加可读性（🔬 📊 💊 ⚠️ ✅ ❌）
- 保持客观严谨，避免绝对化表达

## 示例回复

当医生问"BI-RADS 4a 是什么意思？"时：

📊 **BI-RADS 4a 级解释**

**定义**：低度可疑恶性（恶性概率 2-10%）

**影像特征**：
- 边界部分不清
- 形态不规则
- 内部回声不均匀

**临床建议**：
1. 建议穿刺活检
2. 3-6 个月短期随访
3. 必要时多学科会诊

**说明**：大多数 BI-RADS 4a 病灶为良性，但需病理确诊。"""
