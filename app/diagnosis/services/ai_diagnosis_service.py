"""
AI 深度学习诊断服务

基于多模态大模型 (视觉 + 临床) 分析超声图像
提供病灶检测、特征提取、BI-RADS 分级预测
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass


@dataclass
class AIAnalysisResult:
    """AI 分析结果"""
    detected: bool                      # 是否检测到病灶
    bounding_box: Optional[Dict]        # 病灶边界框 [x1, y1, x2, y2]
    segmentation_mask: Optional[np.ndarray]  # 分割掩码
    features: Dict                      # 提取的超声征象
    birads_prediction: str              # AI 预测 BI-RADS 分级
    malignancy_probability: float       # 恶性概率 (0-1)
    confidence: float                   # 整体置信度
    highlighted_regions: List[Dict]     # 可疑区域高亮
    differential_diagnosis: List[str]   # 鉴别诊断建议


class AIDiagnosisService:
    """
    AI 深度学习诊断服务
    
    集成 Kimi/通义视觉大模型
    实现端到端的超声图像分析
    """
    
    def __init__(self, api_key: str, model_name: str = "kimi-vision"):
        """
        初始化 AI 诊断服务
        
        Args:
            api_key: API Key
            model_name: 模型名称 (kimi-vision / tongyi-vision)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_endpoint = self._get_api_endpoint(model_name)
    
    def _get_api_endpoint(self, model_name: str) -> str:
        """获取模型 API 端点"""
        endpoints = {
            "kimi-vision": "https://api.moonshot.cn/v1/chat/completions",
            "tongyi-vision": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        }
        return endpoints.get(model_name, endpoints["kimi-vision"])
    
    async def analyze_ultrasound(
        self,
        image_urls: List[str],
        patient_info: Optional[Dict] = None
    ) -> AIAnalysisResult:
        """
        分析超声图像
        
        Args:
            image_urls: 超声图像 URL 列表
            patient_info: 患者临床信息 (年龄、性别、主诉等)
        
        Returns:
            AIAnalysisResult: AI 分析结果
        
        Raises:
            Exception: API 调用失败
        """
        # 1. 构建多模态提示词
        prompt = self._build_analysis_prompt(patient_info)
        
        # 2. 调用视觉大模型 API
        api_response = await self._call_vision_api(
            prompt=prompt,
            image_urls=image_urls
        )
        
        # 3. 解析 AI 响应
        result = self._parse_ai_response(api_response)
        
        return result
    
    def _build_analysis_prompt(self, patient_info: Optional[Dict]) -> str:
        """
        构建分析提示词
        
        Args:
            patient_info: 患者信息
        
        Returns:
            str: 结构化提示词
        """
        base_prompt = """
你是一位经验丰富的乳腺超声诊断专家。请分析提供的乳腺超声图像，完成以下任务：

## 分析任务

### 1. 病灶检测与定位
- 是否发现可疑病灶？
- 病灶的位置和范围
- 单发还是多发？

### 2. 形态学特征分析
请详细描述以下特征：
- **形状**: 椭圆形 / 圆形 / 不规则形
- **纵横比**: 平行生长 (宽>高) 还是非平行生长 (高>宽，taller-than-wide)
- **边缘**: 
  - 边界清晰 (circumscribed)
  - 边界不清 (indistinct)
  - 成角 (angular)
  - 微小分叶 (microlobulated)
  - 毛刺状 (spiculated)

### 3. 内部回声特征
- **回声模式**: 无回声 / 低回声 / 等回声 / 高回声 / 混合回声
- **回声均匀性**: 均匀 / 不均匀

### 4. 后方回声特征
- 后方回声增强
- 后方回声衰减
- 无明显改变
- 混合回声

### 5. 钙化分析
- 是否伴钙化？
- 钙化类型:
  - 粗大钙化 (>0.5mm)
  - 细小钙化
  - 点状钙化
  - 多形性钙化
  - 线样钙化

### 6. CDFI 血流评估
- 血流分级 (Adler 0-3 级)
- 血管形态：规则 / 不规则 / 穿入型

### 7. BI-RADS 分级预测
根据 ACR BI-RADS Ultrasound (第 5 版) 标准:
- 0 级：评估不完全
- 1 级：阴性
- 2 级：良性
- 3 级：可能良性 (恶性风险≤2%)
- 4A 级：低度可疑 (2-10%)
- 4B 级：中度可疑 (10-50%)
- 4C 级：高度可疑 (50-95%)
- 5 级：高度提示恶性 (>95%)

### 8. 恶性风险评估
- 恶性概率估计 (0-100%)
- 关键恶性征象说明

### 9. 鉴别诊断建议
- 可能的诊断 (前 3 位)
- 需要鉴别的疾病
- 建议的进一步检查

## 输出格式

请严格按照以下 JSON 格式输出:
{
    "detected": true/false,
    "bounding_box": {"x1": 0, "y1": 0, "x2": 100, "y2": 100},
    "features": {
        "shape": "oval|round|irregular",
        "orientation": "parallel|not_parallel",
        "margin_types": ["circumscribed", "angular"],
        "echo_pattern": "hypoechoic|...",
        "echo_homogeneity": "homogeneous|heterogeneous",
        "posterior_features": ["enhancement", "shadowing"],
        "calcification_present": true/false,
        "calcification_types": ["fine", "pleomorphic"],
        "vascularity_grade": "grade_0|grade_1|grade_2|grade_3",
        "vessel_pattern": "regular|irregular|penetrating"
    },
    "birads_category": "0|1|2|3|4A|4B|4C|5|6",
    "malignancy_probability": 0.0-1.0,
    "confidence": 0.0-1.0,
    "key_findings": ["关键发现 1", "关键发现 2"],
    "differential_diagnosis": ["疾病 1", "疾病 2", "疾病 3"],
    "recommendations": ["建议 1", "建议 2"]
}
"""
        
        # 添加患者临床信息
        if patient_info:
            clinical_context = f"""

## 患者临床信息
- 年龄：{patient_info.get('age', '未知')} 岁
- 性别：{patient_info.get('gender', '未知')}
- 主诉：{patient_info.get('symptoms', '无')}

请结合上述临床表现综合分析。
"""
            base_prompt += clinical_context
        
        return base_prompt
    
    async def _call_vision_api(
        self,
        prompt: str,
        image_urls: List[str]
    ) -> Dict:
        """
        调用视觉大模型 API
        
        Args:
            prompt: 分析提示词
            image_urls: 图像 URL 列表
        
        Returns:
            Dict: API 响应
        
        Raises:
            Exception: API 调用失败
        """
        import httpx
        
        # 构建多模态请求
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    *[{"type": "image_url", "image_url": url} for url in image_urls]
                ]
            }
        ]
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.1  # 低温度，提高确定性
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_endpoint,
                json=payload,
                headers=headers,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise Exception(f"AI API 调用失败：{response.status_code} - {response.text}")
            
            return response.json()
    
    def _parse_ai_response(self, api_response: Dict) -> AIAnalysisResult:
        """
        解析 AI 响应 响应
        
        Args:
            api_response: API 响应
        
        Returns:
            AIAnalysisResult: 结构化分析结果
        """
        import json
        import re
        
        # 提取 JSON 内容
        content = api_response["choices"][0]["message"]["content"]
        
        # 尝试提取 JSON 块
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析
            json_str = content
        
        # 解析 JSON
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # 降级处理：构建默认结果
            data = self._build_fallback_result()
        
        # 构建分析结果
        return AIAnalysisResult(
            detected=data.get("detected", False),
            bounding_box=data.get("bounding_box"),
            segmentation_mask=None,  # 视觉 API 暂不支持分割
            features=data.get("features", {}),
            birads_prediction=data.get("birads_category", "0"),
            malignancy_probability=data.get("malignancy_probability", 0.0),
            confidence=data.get("confidence", 0.5),
            highlighted_regions=self._extract_highlighted_regions(data),
            differential_diagnosis=data.get("differential_diagnosis", [])
        )
    
    def _build_fallback_result(self) -> Dict:
        """构建降级结果 (当 JSON 解析失败时)"""
        return {
            "detected": False,
            "features": {
                "shape": "unknown",
                "orientation": "unknown",
                "margin_types": [],
                "echo_pattern": "unknown"
            },
            "birads_category": "0",
            "malignancy_probability": 0.0,
            "confidence": 0.0,
            "differential_diagnosis": ["需进一步检查"]
        }
    
    def _extract_highlighted_regions(self, data: Dict) -> List[Dict]:
        """提取可疑区域高亮"""
        # 如果 API 返回 bounding box，作为主要可疑区域
        regions = []
        
        if data.get("bounding_box"):
            regions.append({
                "type": "lesion",
                "box": data["bounding_box"],
                "confidence": data.get("confidence", 0.5),
                "description": "可疑病灶区域"
            })
        
        return regions
