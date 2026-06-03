"""
腋窝淋巴结评估服务

基于超声特征评估腋窝淋巴结状态:
1. 淋巴结形态学评估
2. 良恶性判断
3. N 分期建议
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class LNStatus(str, Enum):
    """淋巴结状态"""
    BENIGN = "benign"  # 良性
    SUSPICIOUS = "suspicious"  # 可疑
    MALIGNANT = "malignant"  # 恶性


class NStage(str, Enum):
    """N 分期"""
    N0 = "N0"  # 无区域淋巴结转移
    N1 = "N1"  # 同侧腋窝淋巴结转移，可活动
    N2 = "N2"  # 同侧腋窝淋巴结转移，固定或融合
    N3 = "N3"  # 同侧锁骨下/上淋巴结转移


@dataclass
class LNAssessment:
    """淋巴结评估结果"""
    status: LNStatus
    n_stage: Optional[NStage]
    confidence: float
    suspicious_features: List[str]
    recommendation: str
    metrics: Dict[str, any]


class LymphNodeAssessment:
    """
    腋窝淋巴结评估器
    
    评估标准基于:
    - ACR BI-RADS Atlas
    - NCCN Guidelines
    - EUSOMA Recommendations
    """
    
    # 正常淋巴结特征
    NORMAL_LN_FEATURES = {
        "cortex_thickness_max_mm": 3.0,  # 皮质厚度≤3mm
        "hilum_present": True,  # 淋巴门存在
        "shape": "oval",  # 椭圆形
        "l/s_ratio_min": 0.5,  # 长短径比≥0.5
    }
    
    # 恶性淋巴结特征权重
    MALIGNANT_FEATURE_WEIGHTS = {
        "cortical_thickening": 3.0,  # 皮质增厚 (>3mm)
        "hilum_absent": 2.5,  # 淋巴门消失
        "round_shape": 2.0,  # 圆形 (L/S<0.5)
        "hypoechoic": 1.5,  # 明显低回声
        "irregular_margin": 2.0,  # 边缘不规则
        "extracapsular_spread": 4.0,  # 包膜外侵犯
        "necrosis": 3.5,  # 坏死
        "calcification": 2.0,  # 钙化
        "internal_vascularity": 2.5,  # 内部血流
    }
    
    @classmethod
    def assess(
        cls,
        ultrasound_features: Dict,
        clinical_context: Optional[Dict] = None
    ) -> LNAssessment:
        """
        评估腋窝淋巴结
        
        Args:
            ultrasound_features: 超声特征
                {
                    "cortical_thickness_mm": float,
                    "hilum_present": bool,
                    "shape": "oval|round|irregular",
                    "long_axis_mm": float,
                    "short_axis_mm": float,
                    "echo_pattern": "hypoechoic|isoechoic|...",
                    "margin": "smooth|irregular",
                    "internal_echo": "homogeneous|heterogeneous|necrotic",
                    "calcification_present": bool,
                    "vascularity_pattern": "hilum|peripheral|internal|none"
                }
            clinical_context: 临床背景
                {
                    "primary_tumor_size": float,  # 原发肿瘤大小
                    "primary_tumor_location": str,  # 原发肿瘤位置
                    "palpable_nodes": bool  # 可触及淋巴结
                }
        
        Returns:
            LNAssessment: 淋巴结评估结果
        """
        # 1. 计算恶性特征评分
        malignant_score = cls._calculate_malignant_score(ultrasound_features)
        
        # 2. 识别可疑特征
        suspicious_features = cls._identify_suspicious_features(ultrasound_features)
        
        # 3. 确定淋巴结状态
        status = cls._determine_status(malignant_score, suspicious_features)
        
        # 4. 计算置信度
        confidence = cls._calculate_confidence(malignant_score, ultrasound_features)
        
        # 5. 评估 N 分期
        n_stage = cls._determine_n_stage(
            status,
            ultrasound_features,
            clinical_context
        )
        
        # 6. 生成建议
        recommendation = cls._generate_recommendation(
            status,
            n_stage,
            clinical_context
        )
        
        # 7. 提取测量指标
        metrics = cls._extract_metrics(ultrasound_features)
        
        return LNAssessment(
            status=status,
            n_stage=n_stage,
            confidence=confidence,
            suspicious_features=suspicious_features,
            recommendation=recommendation,
            metrics=metrics
        )
    
    @classmethod
    def _calculate_malignant_score(cls, features: Dict) -> float:
        """计算恶性评分"""
        score = 0.0
        
        # 皮质厚度
        cortical_thickness = features.get("cortical_thickness_mm", 0)
        if cortical_thickness > 3.0:
            score += cls.MALIGNANT_FEATURE_WEIGHTS["cortical_thickening"]
        if cortical_thickness > 5.0:  # 显著增厚
            score += 2.0
        
        # 淋巴门
        if not features.get("hilum_present", True):
            score += cls.MALIGNANT_FEATURE_WEIGHTS["hilum_absent"]
        
        # 形状
        shape = features.get("shape", "oval")
        if shape == "round":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["round_shape"]
        elif shape == "irregular":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["round_shape"] * 1.5
        
        # 长短径比
        if features.get("long_axis_mm", 0) > 0:
            l_s_ratio = features.get("short_axis_mm", 0) / features.get("long_axis_mm", 1)
            if l_s_ratio < 0.5:
                score += cls.MALIGNANT_FEATURE_WEIGHTS["round_shape"] * 0.5
        
        # 回声
        echo = features.get("echo_pattern", "")
        if echo == "marked_hypoechoic":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["hypoechoic"]
        
        # 边缘
        if features.get("margin") == "irregular":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["irregular_margin"]
        
        # 内部回声
        if features.get("internal_echo") == "necrotic":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["necrosis"]
        
        # 钙化
        if features.get("calcification_present", False):
            score += cls.MALIGNANT_FEATURE_WEIGHTS["calcification"]
        
        # 血流模式
        vascularity = features.get("vascularity_pattern", "none")
        if vascularity == "internal":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["internal_vascularity"]
        elif vascularity == "peripheral":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["internal_vascularity"] * 0.8
        
        # 包膜外侵犯
        if features.get("extracapsular_spread", False):
            score += cls.MALIGNANT_FEATURE_WEIGHTS["extracapsular_spread"]
        
        return score
    
    @classmethod
    def _identify_suspicious_features(cls, features: Dict) -> List[str]:
        """识别可疑特征"""
        suspicious = []
        
        if features.get("cortical_thickness_mm", 0) > 3.0:
            suspicious.append(f"皮质增厚 ({features.get('cortical_thickness_mm')}mm)")
        
        if not features.get("hilum_present", True):
            suspicious.append("淋巴门消失")
        
        if features.get("shape") in ["round", "irregular"]:
            suspicious.append(f"形态异常 ({features.get('shape')})")
        
        if features.get("long_axis_mm", 0) > 0:
            l_s_ratio = features.get("short_axis_mm", 0) / features.get("long_axis_mm", 1)
            if l_s_ratio < 0.5:
                suspicious.append(f"L/S 比降低 ({l_s_ratio:.2f})")
        
        if features.get("echo_pattern") == "marked_hypoechoic":
            suspicious.append("明显低回声")
        
        if features.get("margin") == "irregular":
            suspicious.append("边缘不规则")
        
        if features.get("internal_echo") == "necrotic":
            suspicious.append("内部坏死")
        
        if features.get("calcification_present", False):
            suspicious.append("伴钙化")
        
        vascularity = features.get("vascularity_pattern", "none")
        if vascularity in ["internal", "peripheral"]:
            suspicious.append(f"异常血流 ({vascularity})")
        
        if features.get("extracapsular_spread", False):
            suspicious.append("包膜外侵犯")
        
        return suspicious
    
    @classmethod
    def _determine_status(cls, score: float, suspicious_features: List[str]) -> LNStatus:
        """确定淋巴结状态"""
        if score >= 8.0 or "包膜外侵犯" in suspicious_features or "内部坏死" in suspicious_features:
            return LNStatus.MALIGNANT
        elif score >= 4.0 or len(suspicious_features) >= 3:
            return LNStatus.SUSPICIOUS
        else:
            return LNStatus.BENIGN
    
    @classmethod
    def _calculate_confidence(cls, score: float, features: Dict) -> float:
        """计算置信度"""
        # 基于特征数量和质量
        feature_count = sum([
            features.get("cortical_thickness_mm", 0) > 0,
            features.get("hilum_present") is not None,
            features.get("shape") is not None,
            features.get("long_axis_mm", 0) > 0,
            features.get("long_axis_mm", 0) > 0,
        ])
        
        base_confidence = min(0.95, 0.5 + feature_count * 0.1)
        
        # 根据评分调整
        if score >= 8.0:
            confidence_multiplier = 1.0
        elif score >= 4.0:
            confidence_multiplier = 0.9
        else:
            confidence_multiplier = 0.85
        
        return round(base_confidence * confidence_multiplier, 2)
    
    @classmethod
    def _determine_n_stage(
        cls,
        status: LNStatus,
        features: Dict,
        clinical_context: Optional[Dict]
    ) -> Optional[NStage]:
        """确定 N 分期"""
        if status == LNStatus.BENIGN:
            return NStage.N0
        
        if status == LNStatus.MALIGNANT:
            # 检查是否有包膜外侵犯或融合
            if features.get("extracapsular_spread") or features.get("fixed", False):
                return NStage.N2
            
            # 检查锁骨区域
            location = features.get("location", "axillary")
            if "infraclavicular" in location or "supraclavicular" in location:
                return NStage.N3
            
            return NStage.N1
        
        # SUSPICIOUS 状态
        if clinical_context and clinical_context.get("palpable_nodes"):
            return NStage.N1
        
        return None
    
    @classmethod
    def _generate_recommendation(
        cls,
        status: LNStatus,
        n_stage: Optional[NStage],
        clinical_context: Optional[Dict]
    ) -> str:
        """生成处理建议"""
        if status == LNStatus.BENIGN:
            return "腋窝淋巴结呈良性表现，建议常规随访"
        
        if status == LNStatus.SUSPICIOUS:
            if n_stage == NStage.N1:
                return "可疑腋窝淋巴结转移，建议超声引导下细针穿刺活检 (FNA)"
            else:
                return "可疑淋巴结，建议短期 (2-3 个月) 复查或穿刺活检"
        
        if status == LNStatus.MALIGNANT:
            if n_stage == NStage.N2:
                return "高度怀疑淋巴结转移伴包膜外侵犯，建议 FNA 或核心针活检，多学科会诊"
            elif n_stage == NStage.N3:
                return "可疑锁骨区域淋巴结转移，建议活检 + 全身评估"
            else:
                return "高度怀疑淋巴结转移，建议超声引导下 FNA 或核心针活检证实"
        
        return "建议进一步评估"
    
    @classmethod
    def _extract_metrics(cls, features: Dict) -> Dict[str, any]:
        """提取测量指标"""
        metrics = {
            "cortical_thickness_mm": features.get("cortical_thickness_mm", 0),
            "long_axis_mm": features.get("long_axis_mm", 0),
            "short_axis_mm": features.get("short_axis_mm", 0),
            "l_s_ratio": 0.0,
            "hilum_present": features.get("hilum_present", True),
            "vascularity_pattern": features.get("vascularity_pattern", "none")
        }
        
        if metrics["long_axis_mm"] > 0:
            metrics["l_s_ratio"] = round(
                metrics["short_axis_mm"] / metrics["long_axis_mm"], 2
            )
        
        return metrics

