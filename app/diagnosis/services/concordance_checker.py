"""
诊断一致性检查服务

比较 AI 评估与医师诊断的差异
提供一致性评分和分歧解释
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ConcordanceLevel(str, Enum):
    """一致性等级"""
    PERFECT = "perfect"  # 完全一致 (±0 级)
    HIGH = "high"        # 高度一致 (±1 级 within 4A-C)
    MODERATE = "moderate"  # 中度一致 (±1 级 crossing 4A-C boundaries)
    LOW = "low"          # 低度一致 (±2 级)
    POOR = "poor"        # 差异大 (≥3 级)


@dataclass
class ConcordanceResult:
    """一致性检查结果"""
    level: ConcordanceLevel
    score: float  # 0-100 一致性评分
    birads_diff: int  # BI-RADS 分级差异
    agreement_details: Dict[str, bool]  # 各项征象一致性
    discordance_reasons: list[str]  # 分歧原因
    recommendation: str  # 建议


class ConcordanceChecker:
    """
    诊断一致性检查器
    
    比较 AI 评估与医师诊断:
    1. BI-RADS 分级一致性
    2. 超声征象识别一致性
    3. 恶性风险评分一致性
    """
    
    # BI-RADS 分级数值映射
    BIRADS_NUMERIC = {
        "0": 0, "1": 1, "2": 2, "3": 3,
        "4A": 4.1, "4B": 4.2, "4C": 4.3,
        "5": 5, "6": 6
    }
    
    # 恶性风险阈值
    RISK_THRESHOLDS = {
        "CATEGORY_3": 2,    # ≤2%
        "CATEGORY_4A": 10,  # 2-10%
        "CATEGORY_4B": 50,  # 10-50%
        "CATEGORY_4C": 95,  # 50-95%
        "CATEGORY_5": 100   # ≥95%
    }
    
    @classmethod
    def check_concordance(
        cls,
        ai_result: Dict,
        physician_diagnosis: Dict
    ) -> ConcordanceResult:
        """
        检查 AI 与医师诊断的一致性
        
        Args:
            ai_result: AI 评估结果
                {
                    "birads_category": "4C",
                    "malignancy_risk": 0.55,
                    "key_features": ["不规则形", "毛刺状边缘", ...]
                }
            physician_diagnosis: 医师诊断
                {
                    "birads_category": "4B",
                    "malignancy_risk": 0.35,
                    "key_features": ["不规则形", "边界不清", ...]
                }
        
        Returns:
            ConcordanceResult: 一致性检查结果
        """
        # 1. 计算 BI-RADS 分级差异
        ai_numeric = cls.BIRADS_NUMERIC.get(ai_result.get("birads_category", "3"), 3)
        physician_numeric = cls.BIRADS_NUMERIC.get(physician_diagnosis.get("birads_category", "3"), 3)
        birads_diff = abs(ai_numeric - physician_numeric)
        
        # 2. 计算恶性风险差异
        ai_risk = ai_result.get("malignancy_risk", 0) * 100 if ai_result.get("malignancy_risk", 0) <= 1 else ai_result.get("malignancy_risk", 0)
        physician_risk = physician_diagnosis.get("malignancy_risk", 0) * 100 if physician_diagnosis.get("malignancy_risk", 0) <= 1 else physician_diagnosis.get("malignancy_risk", 0)
        risk_diff = abs(ai_risk - physician_risk)
        
        # 3. 比较关键征象一致性
        ai_features = set(ai_result.get("key_features", []))
        physician_features = set(physician_diagnosis.get("key_features", []))
        
        agreement_details = cls._compare_features(
            ai_features,
            physician_features
        )
        
        # 4. 确定一致性等级
        level = cls._determine_level(birads_diff, risk_diff, agreement_details)
        
        # 5. 计算一致性评分
        score = cls._calculate_score(birads_diff, risk_diff, agreement_details)
        
        # 6. 识别分歧原因
        discordance_reasons = cls._identify_discordance(
            birads_diff,
            risk_diff,
            agreement_details,
            ai_result,
            physician_diagnosis
        )
        
        # 7. 生成建议
        recommendation = cls._generate_recommendation(
            level,
            discordance_reasons,
            ai_result,
            physician_diagnosis
        )
        
        return ConcordanceResult(
            level=level,
            score=score,
            birads_diff=int(birads_diff),
            agreement_details=agreement_details,
            discordance_reasons=discordance_reasons,
            recommendation=recommendation
        )
    
    @classmethod
    def _compare_features(
        cls,
        ai_features: set,
        physician_features: set
    ) -> Dict[str, bool]:
        """比较征象识别一致性"""
        all_features = ai_features | physician_features
        
        agreement = {}
        
        # 形状一致性
        shape_terms = {"椭圆形", "圆形", "不规则形"}
        ai_shape = ai_features & shape_terms
        physician_shape = physician_features & shape_terms
        agreement["shape"] = bool(ai_shape == physician_shape and ai_shape)
        
        # 边缘一致性
        margin_terms = {"边界清晰", "边界不清", "毛刺状", "成角", "微小分叶"}
        ai_margin = ai_features & margin_terms
        physician_margin = physician_features & margin_terms
        agreement["margin"] = bool(ai_margin == physician_margin and ai_margin)
        
        # 纵横比一致性
        orientation_terms = {"纵横比>1", "taller-than-wide"}
        ai_orientation = ai_features & orientation_terms
        physician_orientation = physician_features & orientation_terms
        agreement["orientation"] = (ai_orientation == physician_orientation)
        
        # 回声一致性
        echo_terms = {"低回声", "明显低回声", "回声不均", "无回声"}
        ai_echo = ai_features & echo_terms
        physician_echo = physician_features & echo_terms
        agreement["echo"] = bool(ai_echo == physician_echo and ai_echo)
        
        # 钙化一致性
        calcification_terms = {"钙化", "微钙化", "细小钙化"}
        ai_calc = ai_features & calcification_terms
        physician_calc = physician_features & calcification_terms
        agreement["calcification"] = (ai_calc == physician_calc)
        
        # 后方回声一致性
        posterior_terms = {"后方衰减", "后方增强", "混合回声"}
        ai_posterior = ai_features & posterior_terms
        physician_posterior = physician_features & posterior_terms
        agreement["posterior"] = (ai_posterior == physician_posterior)
        
        return agreement
    
    @classmethod
    def _determine_level(
        cls,
        birads_diff: float,
        risk_diff: float,
        agreement_details: Dict[str, bool]
    ) -> ConcordanceLevel:
        """确定一致性等级"""
        # 计算征象一致性比例
        agreement_count = sum(agreement_details.values())
        total_features = len(agreement_details)
        agreement_ratio = agreement_count / total_features if total_features > 0 else 0
        
        # 分级差异判断
        if birads_diff == 0 and risk_diff < 10:
            return ConcordanceLevel.PERFECT
        
        if birads_diff <= 0.3 and risk_diff < 15 and agreement_ratio >= 0.8:
            return ConcordanceLevel.HIGH
        
        if birads_diff <= 1.0 and risk_diff < 25 and agreement_ratio >= 0.6:
            return ConcordanceLevel.MODERATE
        
        if birads_diff <= 2.0 and risk_diff < 40:
            return ConcordanceLevel.LOW
        
        return ConcordanceLevel.POOR
    
    @classmethod
    def _calculate_score(
        cls,
        birads_diff: float,
        risk_diff: float,
        agreement_details: Dict[str, bool]
    ) -> float:
        """
        计算一致性评分 (0-100)
        
        权重:
        - BI-RADS 分级：40%
        - 恶性风险：30%
        - 征象识别：30%
        """
        # BI-RADS 评分 (0-40)
        if birads_diff == 0:
            birads_score = 40
        elif birads_diff <= 0.3:
            birads_score = 35
        elif birads_diff <= 1.0:
            birads_score = 25
        elif birads_diff <= 2.0:
            birads_score = 15
        else:
            birads_score = 0
        
        # 恶性风险评分 (0-30)
        if risk_diff < 10:
            risk_score = 30
        elif risk_diff < 20:
            risk_score = 20
        elif risk_diff < 30:
            risk_score = 10
        else:
            risk_score = 0
        
        # 征象识别评分 (0-30)
        agreement_count = sum(agreement_details.values())
        total_features = len(agreement_details)
        feature_score = (agreement_count / total_features * 30) if total_features > 0 else 0
        
        return round(birads_score + risk_score + feature_score, 1)
    
    @classmethod
    def _identify_discordance(
        cls,
        birads_diff: float,
        risk_diff: float,
        agreement_details: Dict[str, bool],
        ai_result: Dict,
        physician_diagnosis: Dict
    ) -> list[str]:
        """识别分歧原因"""
        reasons = []
        
        if birads_diff > 0:
            ai_cat = ai_result.get("birads_category", "N/A")
            phy_cat = physician_diagnosis.get("birads_category", "N/A")
            reasons.append(f"BI-RADS 分级不同：AI 评估为{ai_cat}级，医师诊断为{phy_cat}级")
        
        if risk_diff >= 20:
            ai_risk = ai_result.get("malignancy_risk", 0) * 100 if ai_result.get("malignancy_risk", 0) <= 1 else ai_result.get("malignancy_risk", 0)
            phy_risk = physician_diagnosis.get("malignancy_risk", 0) * 100 if physician_diagnosis.get("malignancy_risk", 0) <= 1 else physician_diagnosis.get("malignancy_risk", 0)
            reasons.append(f"恶性风险评估差异：AI 评估{ai_risk:.1f}%，医师评估{phy_risk:.1f}%")
        
        if not agreement_details.get("shape", True):
            reasons.append("形状征象识别不一致")
        
        if not agreement_details.get("margin", True):
            reasons.append("边缘特征识别不一致")
        
        if not agreement_details.get("orientation", True):
            reasons.append("纵横比评估不一致")
        
        if not agreement_details.get("echo", True):
            reasons.append("回声模式评估不一致")
        
        return reasons
    
    @classmethod
    def _generate_recommendation(
        cls,
        level: ConcordanceLevel,
        discordance_reasons: list[str],
        ai_result: Dict,
        physician_diagnosis: Dict
    ) -> str:
        """生成处理建议"""
        if level == ConcordanceLevel.PERFECT:
            return "AI 与医师诊断完全一致，可按原计划处理"
        
        if level == ConcordanceLevel.HIGH:
            return "AI 与医师诊断高度一致，建议按医师诊断处理，AI 结果供参考"
        
        if level == ConcordanceLevel.MODERATE:
            reasons_str = "、".join(discordance_reasons[:2])
            return f"中度一致，建议复核：{reasons_str}。可考虑多学科会诊 (MDT)"
        
        if level == ConcordanceLevel.LOW:
            return "低度一致，强烈建议多学科会诊 (MDT) 或上级医师复核"
        
        return "差异显著，必须进行多学科会诊 (MDT)，重新评估超声图像和临床信息"
