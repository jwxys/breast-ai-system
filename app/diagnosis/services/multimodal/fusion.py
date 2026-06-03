"""
多模态数据融合

融合超声 + 钼靶+MRI 多模态影像数据
提高诊断准确率
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ModalityType(str, Enum):
    """影像模态类型"""
    ULTRASOUND = "ultrasound"    # 超声
    MAMMOGRAPHY = "mammography"  # 钼靶
    MRI = "mri"                  # 磁共振


@dataclass
class MultimodalFeatures:
    """多模态融合特征"""
    # 各模态独立特征
    ultrasound_features: Dict
    mammography_features: Optional[Dict]
    mri_features: Optional[Dict]
    
    # 融合特征
    fused_features: np.ndarray
    confidence_scores: Dict[str, float]
    agreement_level: str  # high/medium/low


class MultimodalFusion:
    """
    多模态融合器
    
    融合策略:
    1. 早期融合 (特征级)
    2. 晚期融合 (决策级)
    3. 混合融合
    """
    
    def __init__(self, fusion_strategy: str = 'late'):
        """
        初始化融合器
        
        Args:
            fusion_strategy: 融合策略 (early/late/hybrid)
        """
        self.fusion_strategy = fusion_strategy
        self.modality_weights = {
            ModalityType.ULTRASOUND: 0.5,
            ModalityType.MAMMOGRAPHY: 0.3,
            ModalityType.MRI: 0.2
        }
    
    def fuse(
        self,
        features: Dict[ModalityType, Dict],
        predictions: Dict[ModalityType, float]
    ) -> MultimodalFeatures:
        """
        执行多模态融合
        
        Args:
            features: 各模态特征字典
            predictions: 各模态预测概率
        
        Returns:
            MultimodalFeatures: 融合结果
        """
        if self.fusion_strategy == 'early':
            return self._early_fusion(features)
        elif self.fusion_strategy == 'late':
            return self._late_fusion(predictions)
        else:  # hybrid
            return self._hybrid_fusion(features, predictions)
    
    def _early_fusion(
        self,
        features: Dict[ModalityType, Dict]
    ) -> MultimodalFeatures:
        """
        早期融合 (特征级融合)
        
        将各模态特征拼接为统一特征向量
        """
        feature_vectors = []
        
        for modality in [ModalityType.ULTRASOUND, ModalityType.MAMMOGRAPHY, ModalityType.MRI]:
            if modality in features:
                feat_dict = features[modality]
                # 提取数值特征
                vector = self._dict_to_vector(feat_dict)
                feature_vectors.append(vector)
        
        # 特征拼接
        if feature_vectors:
            fused = np.concatenate(feature_vectors)
        else:
            fused = np.array([])
        
        return MultimodalFeatures(
            ultrasound_features=features.get(ModalityType.ULTRASOUND, {}),
            mammography_features=features.get(ModalityType.MAMMOGRAPHY),
            mri_features=features.get(ModalityType.MRI),
            fused_features=fused,
            confidence_scores={},
            agreement_level='high'
        )
    
    def _late_fusion(
        self,
        predictions: Dict[ModalityType, float]
    ) -> MultimodalFeatures:
        """
        晚期融合 (决策级融合)
        
        加权平均各模态预测结果
        """
        # 加权平均
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for modality, prob in predictions.items():
            weight = self.modality_weights.get(modality, 0.2)
            weighted_sum += weight * prob
            weight_sum += weight
        
        fused_prob = weighted_sum / weight_sum if weight_sum > 0 else 0
        
        # 计算一致性
        probs = list(predictions.values())
        agreement = self._calculate_agreement(probs)
        
        return MultimodalFeatures(
            ultrasound_features={},
            mammography_features=None,
            mri_features=None,
            fused_features=np.array([fused_prob]),
            confidence_scores={k: v for k, v in predictions.items()},
            agreement_level=agreement
        )
    
    def _hybrid_fusion(
        self,
        features: Dict[ModalityType, Dict],
        predictions: Dict[ModalityType, float]
    ) -> MultimodalFeatures:
        """
        混合融合
        
        结合特征级和决策级融合
        """
        early_result = self._early_fusion(features)
        late_result = self._late_fusion(predictions)
        
        # 融合两者
        fused = np.concatenate([early_result.fused_features, late_result.fused_features])
        
        return MultimodalFeatures(
            ultrasound_features=features.get(ModalityType.ULTRASOUND, {}),
            mammography_features=features.get(ModalityType.MAMMOGRAPHY),
            mri_features=features.get(ModalityType.MRI),
            fused_features=fused,
            confidence_scores=late_result.confidence_scores,
            agreement_level=late_result.agreement_level
        )
    
    def _dict_to_vector(self, feat_dict: Dict) -> np.ndarray:
        """将特征字典转换为向量"""
        values = [v for v in feat_dict.values() if isinstance(v, (int, float))]
        return np.array(values)
    
    def _calculate_agreement(self, probs: List[float]) -> str:
        """
        计算模态间一致性
        
        Args:
            probs: 各模态预测概率列表
        
        Returns:
            str: 一致性等级
        """
        if len(probs) < 2:
            return 'high'
        
        std = np.std(probs)
        
        if std < 0.1:
            return 'high'    # 高度一致
        elif std < 0.2:
            return 'medium'  # 中度一致
        else:
            return 'low'     # 一致性低
    
    def handle_disagreement(
        self,
        predictions: Dict[ModalityType, float],
        agreement_level: str
    ) -> Dict:
        """
        处理模态间不一致
        
        Args:
            predictions: 各模态预测
            agreement_level: 一致性等级
        
        Returns:
            Dict: 处理建议
        """
        if agreement_level == 'high':
            return {
                "action": "use_fused",
                "message": "各模态结果一致，采用融合结果"
            }
        
        elif agreement_level == 'medium':
            # 找出最可信的模态
            most_confident = max(predictions.items(), key=lambda x: x[1])
            return {
                "action": "review",
                "message": f"模态间存在差异，建议重点参考{most_confident[0]}结果",
                "recommendation": "请上级医师会诊"
            }
        
        else:  # low
            return {
                "action": "additional_exam",
                "message": "模态间差异显著",
                "recommendation": "建议补充检查或穿刺活检"
            }
    
    def generate_multimodal_report(
        self,
        fusion_result: MultimodalFeatures,
        patient_id: str
    ) -> Dict:
        """
        生成多模态报告
        
        Args:
            fusion_result: 融合结果
            patient_id: 患者 ID
        
        Returns:
            Dict: 多模态报告
        """
        report = {
            "patient_id": patient_id,
            "modalities_used": [],
            "findings": {},
            "fusion_result": {},
            "recommendation": ""
        }
        
        # 记录的模态
        if fusion_result.ultrasound_features:
            report["modalities_used"].append("超声")
        if fusion_result.mammography_features:
            report["modalities_used"].append("钼靶")
        if fusion_result.mri_features:
            report["modalities_used"].append("MRI")
        
        # 融合结果
        if len(fusion_result.fused_features) > 0:
            report["fusion_result"]["fused_probability"] = float(fusion_result.fused_features[0])
        
        # 一致性
        report["fusion_result"]["agreement_level"] = fusion_result.agreement_level
        
        # 建议
        if fusion_result.agreement_level == 'low':
            report["recommendation"] = "各模态结果不一致，建议进一步检查或会诊"
        else:
            report["recommendation"] = "多模态结果一致，诊断可靠性高"
        
        return report
