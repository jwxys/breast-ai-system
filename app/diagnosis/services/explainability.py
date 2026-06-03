"""
可解释性增强模块

提供 AI 决策的可视化解释和推理过程
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FeatureImportance:
    """特征重要性"""
    feature_name: str
    importance_score: float
    direction: str  # "positive" 或 "negative"
    clinical_meaning: str


class ExplainableAI:
    """
    可解释 AI 服务
    
    方法:
    1. Grad-CAM 热力图
    2. 特征重要性分析
    3. 推理链生成
    """
    
    def __init__(self):
        self.clinical_knowledge = self._load_clinical_knowledge()
    
    def _load_clinical_knowledge(self) -> Dict:
        """加载临床知识库"""
        return {
            "taller_than_wide": {
                "importance": 0.9,
                "direction": "positive",
                "explanation": "纵横比>1 (高>宽) 是乳腺恶性结节的重要征象，提示病灶呈浸润性生长"
            },
            "spiculated_margin": {
                "importance": 0.85,
                "direction": "positive",
                "explanation": "毛刺状边缘提示病灶向周围组织浸润，是恶性肿瘤的典型表现"
            },
            "posterior_shadowing": {
                "importance": 0.75,
                "direction": "positive",
                "explanation": "后方回声衰减提示病灶密度高、吸收强，多见于恶性病变"
            },
            "microlobulated": {
                "importance": 0.7,
                "direction": "positive",
                "explanation": "微小分叶提示病灶生长不均，恶性可能性增高"
            },
            "hyperechoic_halo": {
                "importance": 0.65,
                "direction": "positive",
                "explanation": "高回声晕提示周围组织反应，可见于恶性肿瘤"
            },
            "calcification_fine": {
                "importance": 0.6,
                "direction": "positive",
                "explanation": "细小钙化多见于导管内癌或浸润性癌"
            },
            "ric h_vascularity": {
                "importance": 0.55,
                "direction": "positive",
                "explanation": "丰富血流提示肿瘤血管生成，恶性病变常见"
            },
            "oval_shape": {
                "importance": 0.7,
                "direction": "negative",
                "explanation": "椭圆形是良性结节的典型形态，提示膨胀性生长"
            },
            "circumscribed_margin": {
                "importance": 0.75,
                "direction": "negative",
                "explanation": "边界清晰提示病灶有包膜或推挤周围组织，多为良性"
            },
            "posterior_enhancement": {
                "importance": 0.6,
                "direction": "negative",
                "explanation": "后方回声增强常见于囊性病变或纤维腺瘤"
            }
        }
    
    def grad_cam_heatmap(
        self,
        model,
        image: np.ndarray,
        target_layer: str = 'backbone.features.8'
    ) -> np.ndarray:
        """
        生成 Grad-CAM 热力图
        
        Args:
            model: 训练好的模型
            image: 输入图像
            target_layer: 目标卷积层
        
        Returns:
            np.ndarray: 热力图 (与图像同尺寸)
        """
        import torch
        from torch import nn
        
        model.eval()
        
        # 获取目标层的特征图和梯度
        gradients = None
        
        def backward_hook(module, grad_input, grad_output):
            nonlocal gradients
            gradients = grad_output[0]
        
        # 注册 hook
        target_module = dict(model.named_modules())[target_layer]
        handle = target_module.register_backward_hook(backward_hook)
        
        # 前向传播
        image_tensor = torch.from_numpy(image).unsqueeze(0).float()
        output = model(image_tensor)
        
        # 反向传播
        pred_class = output.argmax(dim=1)
        output[0, pred_class].backward()
        
        # 计算权重
        weights = gradients.mean(dim=(2, 3), keepdim=True)
        
        # 生成热力图
        cam = (weights * gradients).sum(dim=1).relu()
        cam = nn.functional.interpolate(cam, size=image.shape[-2:], mode='bilinear')
        
        # 归一化
        heatmap = cam[0].cpu().numpy()
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-10)
        
        handle.remove()
        return heatmap
    
    def analyze_feature_importance(
        self,
        ultrasound_features: Dict,
        prediction_prob: float
    ) -> List[FeatureImportance]:
        """
        分析特征重要性
        
        Args:
            ultrasound_features: 超声征象字典
            prediction_prob: 恶性预测概率
        
        Returns:
            List[FeatureImportance]: 特征重要性列表
        """
        importances = []
        
        # 映射临床特征
        feature_mapping = {
            "taller_than_wide": ultrasound_features.get("orientation") == "not_parallel",
            "spiculated_margin": "spiculated" in ultrasound_features.get("margin_types", []),
            "posterior_shadowing": "shadowing" in ultrasound_features.get("posterior_features", []),
            "microlobulated": "microlobulated" in ultrasound_features.get("margin_types", []),
            "calcification_fine": "fine" in ultrasound_features.get("calcification_types", []),
            "rich_vascularity": ultrasound_features.get("vascularity_grade") in ["grade_2", "grade_3"],
            "oval_shape": ultrasound_features.get("shape") == "oval",
            "circumscribed_margin": "circumscribed" in ultrasound_features.get("margin_types", []),
            "posterior_enhancement": "enhancement" in ultrasound_features.get("posterior_features", []),
        }
        
        # 计算每个特征的重要性
        for feature_name, present in feature_mapping.items():
            if present:
                knowledge = self.clinical_knowledge.get(feature_name, {})
                importances.append(FeatureImportance(
                    feature_name=self._translate_feature(feature_name),
                    importance_score=knowledge.get("importance", 0.5),
                    direction=knowledge.get("direction", "positive"),
                    clinical_meaning=knowledge.get("explanation", "")
                ))
        
        # 按重要性排序
        importances.sort(key=lambda x: x.importance_score, reverse=True)
        
        return importances
    
    def _translate_feature(self, feature_name: str) -> str:
        """翻译特征名称"""
        translations = {
            "taller_than_wide": "纵横比>1",
            "spiculated_margin": "毛刺状边缘",
            "posterior_shadowing": "后方回声衰减",
            "microlobulated": "微小分叶",
            "hyperechoic_halo": "高回声晕",
            "calcification_fine": "细小钙化",
            "rich_vascularity": "血流丰富",
            "oval_shape": "椭圆形",
            "circumscribed_margin": "边界清晰",
            "posterior_enhancement": "后方回声增强"
        }
        return translations.get(feature_name, feature_name)
    
    def generate_reasoning_chain(
        self,
        features: List[FeatureImportance],
        prediction_prob: float
    ) -> Dict:
        """
        生成推理链
        
        Args:
            features: 特征重要性列表
            prediction_prob: 预测概率
        
        Returns:
            Dict: 推理链
        """
        # 确定 BI-RADS 建议
        if prediction_prob > 0.7:
            birads_suggest = "4B-5 类"
            recommendation = "高度怀疑恶性，建议穿刺活检或手术切除"
        elif prediction_prob > 0.4:
            birads_suggest = "4A-4B 类"
            recommendation = "可疑恶性，建议穿刺活检"
        elif prediction_prob > 0.2:
            birads_suggest = "3-4A 类"
            recommendation = "可能良性，建议短期随访或活检"
        else:
            birads_suggest = "2-3 类"
            recommendation = "可能良性，建议常规随访"
        
        # 构建推理链
        reasoning_steps = []
        for i, feature in enumerate(features, 1):
            step = {
                "step": i,
                "feature": feature.feature_name,
                "impact": "增加恶性风险" if feature.direction == "positive" else "降低恶性风险",
                "evidence": feature.clinical_meaning
            }
            reasoning_steps.append(step)
        
        return {
            "prediction": f"{prediction_prob:.1%}",
            "birads_suggestion": birads_suggest,
            "reasoning_steps": reasoning_steps,
            "conclusion": recommendation,
            "key_evidence": [f.feature_name for f in features[:3]],
            "confidence_level": "高" if prediction_prob > 0.8 or prediction_prob < 0.2 else "中"
        }
    
    def create_explanation_report(
        self,
        image: np.ndarray,
        model,
        ultrasound_features: Dict
    ) -> Dict:
        """
        生成完整的解释报告
        
        Args:
            image: 超声图像
            model: AI 模型
            ultrasound_features: 超声征象
        
        Returns:
            Dict: 解释报告
        """
        # 获取预测
        import torch
        image_tensor = torch.from_numpy(image).unsqueeze(0).float()
        model.eval()
        with torch.no_grad():
            output = model(image_tensor)
            prob = torch.softmax(output, dim=1)[0, -1].item()  # 恶性概率
        
        # 生成热力图
        heatmap = self.grad_cam_heatmap(model, image)
        
        # 分析特征重要性
        importances = self.analyze_feature_importance(ultrasound_features, prob)
        
        # 生成推理链
        reasoning = self.generate_reasoning_chain(importances, prob)
        
        # 创建可视化报告 (返回数据)
        return {
            "prediction": {
                "malignancy_probability": prob,
                "birads_category": self._prob_to_birads(prob)
            },
            "visualization": {
                "heatmap": heatmap.tolist(),
                "heatmap_description": "红色区域表示 AI 关注的可疑区域"
            },
            "key_features": [
                {
                    "name": f.feature_name,
                    "importance": f"{f.importance_score:.2f}",
                    "impact": "↑ 恶性风险" if f.direction == "positive" else "↓ 恶性风险",
                    "explanation": f.clinical_meaning
                }
                for f in importances
            ],
            "reasoning_chain": reasoning,
            "final_recommendation": reasoning["conclusion"]
        }
    
    def _prob_to_birads(self, prob: float) -> str:
        """概率转 BI-RADS 分级"""
        if prob > 0.95: return "5 类"
        elif prob > 0.7: return "4C 类"
        elif prob > 0.5: return "4B 类"
        elif prob > 0.3: return "4A 类"
        elif prob > 0.1: return "3 类"
        else: return "2 类"
