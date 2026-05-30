"""
影像 - 中医病机分析规则引擎

基于循证医学文献，将超声影像特征映射到中医病机倾向
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class EvidenceLevel(str, Enum):
    """证据等级"""
    A = "A"  # 多中心 RCT，Meta 分析
    B = "B"  # 单中心对照研究，样本量>100
    C = "C"  # 观察性研究，专家共识


class Pathomechanism(str, Enum):
    """中医病机"""
    STASIS = "stasis"  # 瘀血
    PHLEGM = "phlegm"  # 痰浊
    TOXIN = "toxin"  # 毒邪
    DEFICIENCY = "deficiency"  # 正虚


@dataclass
class FeatureRule:
    """特征规则"""
    target: Pathomechanism  # 目标病机
    weight: float  # 权重 (-1.0 到 +1.0)
    evidence: EvidenceLevel  # 证据等级
    description: str  # 规则描述


@dataclass
class TCMAnalysisResult:
    """中医病机分析结果"""
    scores: Dict[str, float]  # 病机评分
    evidence: Dict[str, str]  # 证据摘要
    primary: str  # 主要病机
    secondary: List[str]  # 次要病机
    pattern: str  # 病机组合
    nature: str  # 病性（实证/虚证/虚实夹杂）
    recommended_therapy: Optional[str]  # 推荐治法
    recommended_formula: Optional[str]  # 参考方剂
    confidence: float  # 置信度
    evidence_level: str  # 总体证据等级


class ImagingTCMRuleEngine:
    """影像 - 中医病机规则引擎（激进版）"""
    
    VERSION = "2.0-aggressive"
    
    # 证据等级修正系数
    EVIDENCE_MODIFIER = {
        EvidenceLevel.A: 1.0,
        EvidenceLevel.B: 0.8,
        EvidenceLevel.C: 0.6,
    }
    
    # 特征规则库（20+ 项特征）
    FEATURE_RULES = {
        # ========== 1. 形态学特征 ==========
        "boundary_clear": FeatureRule(
            target=Pathomechanism.PHLEGM,
            weight=-0.2,
            evidence=EvidenceLevel.B,
            description="边界清晰 → 痰湿凝结（偏良性）"
        ),
        "boundary_unclear": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.4,
            evidence=EvidenceLevel.B,
            description="边界不清 → 瘀血内阻"
        ),
        "boundary_spiculated": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.5,
            evidence=EvidenceLevel.B,
            description="毛刺征 → 瘀毒互结"
        ),
        "boundary_angular": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.4,
            evidence=EvidenceLevel.C,
            description="角征/尖角 → 毒邪深陷"
        ),
        "morphology_regular": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.1,
            evidence=EvidenceLevel.B,
            description="形态规则 → 气滞为主（轻）"
        ),
        "morphology_irregular": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.3,
            evidence=EvidenceLevel.B,
            description="形态不规则 → 气滞血瘀"
        ),
        "morphology_crab claw": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.6,
            evidence=EvidenceLevel.C,
            description="蟹足样 → 毒邪走窜"
        ),
        "edge_smooth": FeatureRule(
            target=Pathomechanism.DEFICIENCY,
            weight=-0.2,
            evidence=EvidenceLevel.C,
            description="边缘光整 → 正气尚存"
        ),
        "edge_blurred": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.3,
            evidence=EvidenceLevel.B,
            description="边缘模糊 → 痰瘀互结"
        ),
        "edge_microlobulated": FeatureRule(
            target=Pathomechanism.PHLEGM,
            weight=0.2,
            evidence=EvidenceLevel.C,
            description="微分叶 → 气滞痰凝"
        ),
        "edge_macrol obulated": FeatureRule(
            target=Pathomechanism.PHLEGM,
            weight=0.3,
            evidence=EvidenceLevel.C,
            description="宏分叶 → 痰湿壅盛"
        ),
        "capsule_intact": FeatureRule(
            target=Pathomechanism.DEFICIENCY,
            weight=-0.3,
            evidence=EvidenceLevel.C,
            description="包膜完整 → 正气固摄"
        ),
        "capsule_broken": FeatureRule(
            target=Pathomechanism.DEFICIENCY,
            weight=0.4,
            evidence=EvidenceLevel.C,
            description="包膜不完整 → 正气亏虚"
        ),
        "capsule_absent": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.5,
            evidence=EvidenceLevel.C,
            description="无包膜 → 毒邪扩散"
        ),
        
        # ========== 2. 内部回声特征 ==========
        "echo_anechoic": FeatureRule(
            target=Pathomechanism.PHLEGM,
            weight=0.4,
            evidence=EvidenceLevel.B,
            description="无回声（囊性） → 痰饮水湿"
        ),
        "echo_hypoechoic": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.3,
            evidence=EvidenceLevel.B,
            description="低回声 → 血瘀/气滞"
        ),
        "echo_hyperechoic": FeatureRule(
            target=Pathomechanism.PHLEGM,
            weight=0.3,
            evidence=EvidenceLevel.C,
            description="高回声 → 痰湿/脂肪"
        ),
        "echo_heterogeneous": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.3,
            evidence=EvidenceLevel.B,
            description="回声不均匀 → 痰瘀互结"
        ),
        "calcification_none": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0,
            evidence=EvidenceLevel.B,
            description="无钙化"
        ),
        "calcification_coarse": FeatureRule(
            target=Pathomechanism.PHLEGM,
            weight=0.4,
            evidence=EvidenceLevel.B,
            description="粗大钙化 → 痰浊久凝"
        ),
        "calcification_micro": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.5,
            evidence=EvidenceLevel.B,
            description="点状微钙化 → 痰毒互结"
        ),
        "calcification_cluster": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.6,
            evidence=EvidenceLevel.B,
            description="簇状钙化 → 毒邪深重"
        ),
        "calcification_arc": FeatureRule(
            target=Pathomechanism.PHLEGM,
            weight=0.3,
            evidence=EvidenceLevel.C,
            description="弧形钙化 → 痰湿凝聚"
        ),
        "liquefaction_present": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.6,
            evidence=EvidenceLevel.C,
            description="液化坏死 → 热毒炽盛，肉腐血败"
        ),
        
        # ========== 3. 血流动力学特征 ==========
        "cdfi_grade_0": FeatureRule(
            target=Pathomechanism.PHLEGM,
            weight=0.3,
            evidence=EvidenceLevel.C,
            description="0 级血流 → 痰凝/阴寒"
        ),
        "cdfi_grade_1": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.2,
            evidence=EvidenceLevel.C,
            description="I 级血流 → 轻度血瘀"
        ),
        "cdfi_grade_2": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.4,
            evidence=EvidenceLevel.B,
            description="II 级血流 → 血瘀明显"
        ),
        "cdfi_grade_3": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.5,
            evidence=EvidenceLevel.B,
            description="III 级血流 → 热毒炽盛/血热"
        ),
        "blood_flow_peripheral": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.3,
            evidence=EvidenceLevel.C,
            description="周边型血流 → 气滞血瘀（早期）"
        ),
        "blood_flow_penetrating": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.5,
            evidence=EvidenceLevel.B,
            description="穿入型血流 → 瘀血内阻（进展）"
        ),
        "blood_flow_reticular": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.6,
            evidence=EvidenceLevel.C,
            description="网状型血流 → 热毒炽盛（晚期）"
        ),
        "ri_high": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.3,
            evidence=EvidenceLevel.C,
            description="RI>0.7 → 瘀血/毒邪"
        ),
        
        # ========== 4. 弹性成像特征 ==========
        "elasticity_1_2": FeatureRule(
            target=Pathomechanism.PHLEGM,
            weight=0.2,
            evidence=EvidenceLevel.C,
            description="弹性 1-2 分（软） → 痰湿/气滞"
        ),
        "elasticity_3": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.3,
            evidence=EvidenceLevel.B,
            description="弹性 3 分（中等） → 气滞血瘀"
        ),
        "elasticity_4": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.5,
            evidence=EvidenceLevel.B,
            description="弹性 4 分（硬） → 瘀毒内阻"
        ),
        "elasticity_5": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.6,
            evidence=EvidenceLevel.C,
            description="弹性 5 分（很硬） → 毒邪深重"
        ),
        "strain_ratio_high": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.5,
            evidence=EvidenceLevel.C,
            description="硬度比>4.5 → 瘀毒深重"
        ),
        
        # ========== 5. 生长动力学特征 ==========
        "growth_stable": FeatureRule(
            target=Pathomechanism.DEFICIENCY,
            weight=-0.3,
            evidence=EvidenceLevel.C,
            description="稳定（>1 年无变化） → 正气充足"
        ),
        "growth_slow": FeatureRule(
            target=Pathomechanism.PHLEGM,
            weight=0.3,
            evidence=EvidenceLevel.C,
            description="缓慢生长 → 痰湿凝结"
        ),
        "growth_moderate": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.2,
            evidence=EvidenceLevel.C,
            description="中等生长 → 正邪相争"
        ),
        "growth_fast": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.5,
            evidence=EvidenceLevel.C,
            description="快速生长 → 热毒炽盛，正气不足"
        ),
        "size_large": FeatureRule(
            target=Pathomechanism.TOXIN,
            weight=0.3,
            evidence=EvidenceLevel.C,
            description=">3cm → 病深邪重"
        ),
        "multifocal": FeatureRule(
            target=Pathomechanism.STASIS,
            weight=0.3,
            evidence=EvidenceLevel.C,
            description="多灶性 → 痰瘀互结，病情复杂"
        ),
    }
    
    # 病机组合模式
    PATTERN_MAPPING = {
        frozenset(["stasis", "phlegm"]): "痰瘀互结",
        frozenset(["stasis", "toxin"]): "瘀毒内阻",
        frozenset(["phlegm", "toxin"]): "痰毒互结",
        frozenset(["stasis", "phlegm", "toxin"]): "痰瘀毒互结",
        frozenset(["deficiency", "stasis"]): "气虚血瘀",
        frozenset(["deficiency", "phlegm"]): "脾虚痰湿",
        frozenset(["deficiency", "toxin"]): "正虚毒盛",
        frozenset(["stasis"]): "瘀血内阻",
        frozenset(["phlegm"]): "痰湿凝结",
        frozenset(["toxin"]): "毒邪内蕴",
        frozenset(["deficiency"]): "正气亏虚",
    }
    
    # 治法推荐
    THERAPY_MAPPING = {
        "痰瘀互结": "化痰散结，活血化瘀",
        "瘀毒内阻": "活血化瘀，解毒散结",
        "痰毒互结": "化痰软坚，清热解毒",
        "痰瘀毒互结": "化痰祛瘀，解毒散结",
        "气虚血瘀": "益气活血，化瘀散结",
        "脾虚痰湿": "健脾化痰，软坚散结",
        "正虚毒盛": "扶正解毒，托里排脓",
        "瘀血内阻": "活血化瘀，理气散结",
        "痰湿凝结": "化痰散结，理气通络",
        "毒邪内蕴": "清热解毒，消肿散结",
        "正气亏虚": "扶正固本，益气养血",
    }
    
    # 方剂推荐
    FORMULA_MAPPING = {
        "痰瘀互结": "海藻玉壶汤合血府逐瘀汤加减",
        "瘀毒内阻": "仙方活命饮合桃红四物汤加减",
        "痰毒互结": "消瘰丸合五味消毒饮加减",
        "痰瘀毒互结": "仙方活命饮合海藻玉壶汤加减",
        "气虚血瘀": "补阳还五汤加减",
        "脾虚痰湿": "六君子汤合消瘰丸加减",
        "正虚毒盛": "托里消毒散加减",
        "瘀血内阻": "血府逐瘀汤加减",
        "痰湿凝结": "二陈汤合消瘰丸加减",
        "毒邪内蕴": "五味消毒饮加减",
        "正气亏虚": "八珍汤加减",
    }
    
    def __init__(self, version: Optional[str] = None):
        self.version = version or self.VERSION
    
    def analyze(self, features: Dict) -> TCMAnalysisResult:
        """
        分析影像特征，计算病机倾向
        
        Args:
            features: 影像特征字典
            
        Returns:
            TCMAnalysisResult: 分析结果
        """
        # 初始化评分
        scores = {p.value: 0.0 for p in Pathomechanism}
        evidence_notes = {p.value: [] for p in Pathomechanism}
        
        # 应用规则
        for feature_key, value in features.items():
            if value is None:
                continue
                
            rule = self.FEATURE_RULES.get(feature_key)
            if not rule:
                continue
            
            # 特殊处理：某些特征需要特定值才触发
            if isinstance(value, bool):
                if not value and "present" in feature_key:
                    continue
                if value and "absent" in feature_key:
                    continue
            elif isinstance(value, (int, float)):
                # 数值型特征需要阈值判断
                if "aspect_ratio" in feature_key and value <= 1.0:
                    continue
                if "ri" in feature_key and value <= 0.7:
                    continue
                if "strain_ratio" in feature_key and value <= 2.5:
                    continue
                if "elasticity" in feature_key:
                    # 弹性评分已经在规则中定义
                    pass
            
            # 累加评分
            modifier = self.EVIDENCE_MODIFIER[rule.evidence]
            weighted_score = rule.weight * modifier
            scores[rule.target.value] += weighted_score
            evidence_notes[rule.target.value].append(rule.description)
        
        # 归一化（0-1）
        max_possible = self._calculate_max_score(features)
        normalized_scores = {
            k: min(1.0, max(0.0, v / max_possible)) if max_possible > 0 else 0.0
            for k, v in scores.items()
        }
        
        # 确定主要/次要病机
        sorted_scores = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_scores[0][0] if sorted_scores[0][1] >= 0.3 else None
        secondary = [
            s[0] for s in sorted_scores[1:]
            if 0.3 <= s[1] < 0.7 and s[0] != primary
        ]
        
        # 病机组合
        all_significant = {k for k, v in normalized_scores.items() if v >= 0.3}
        pattern = self._identify_pattern(all_significant)
        
        # 病性判断
        nature = self._determine_nature(normalized_scores)
        
        # 推荐治法与方剂
        therapy = self.THERAPY_MAPPING.get(pattern) if pattern else None
        formula = self.FORMULA_MAPPING.get(pattern) if pattern else None
        
        # 置信度计算
        confidence = self._calculate_confidence(normalized_scores, features)
        
        # 证据等级
        evidence_level = self._determine_evidence_level(features)
        
        return TCMAnalysisResult(
            scores=normalized_scores,
            evidence={k: "; ".join(v[:3]) for k, v in evidence_notes.items()},  # 最多 3 条证据
            primary=primary or "无明显病机倾向",
            secondary=secondary,
            pattern=pattern or "病机不显",
            nature=nature,
            recommended_therapy=therapy,
            recommended_formula=formula,
            confidence=confidence,
            evidence_level=evidence_level,
        )
    
    def _calculate_max_score(self, features: Dict) -> float:
        """计算可能的最大得分（用于归一化）"""
        max_score = 0.0
        for feature_key in features:
            rule = self.FEATURE_RULES.get(feature_key)
            if rule and rule.weight > 0:
                modifier = self.EVIDENCE_MODIFIER[rule.evidence]
                max_score += rule.weight * modifier
        return max_score if max_score > 0 else 1.0
    
    def _identify_pattern(self, pathomechanisms: set) -> Optional[str]:
        """识别病机组合模式"""
        if not pathomechanisms:
            return None
        
        # 尝试精确匹配
        pattern_key = frozenset(pathomechanisms)
        if pattern_key in self.PATTERN_MAPPING:
            return self.PATTERN_MAPPING[pattern_key]
        
        # 尝试子集匹配
        for key in sorted(self.PATTERN_MAPPING.keys(), key=len, reverse=True):
            if key.issubset(pattern_key):
                return self.PATTERN_MAPPING[key]
        
        return None
    
    def _determine_nature(self, scores: Dict[str, float]) -> str:
        """判断病性（虚实）"""
        excess_score = scores.get("stasis", 0) + scores.get("phlegm", 0) + scores.get("toxin", 0)
        deficiency_score = scores.get("deficiency", 0)
        
        if excess_score > deficiency_score * 2:
            return "实证为主"
        elif deficiency_score > excess_score:
            return "虚证为主"
        elif excess_score > 0.3 or deficiency_score > 0.3:
            return "虚实夹杂"
        else:
            return "病性不显"
    
    def _calculate_confidence(self, scores: Dict[str, float], features: Dict) -> float:
        """计算置信度"""
        # 特征完整性
        feature_completeness = len([k for k, v in features.items() if v is not None]) / 15.0  # 假设 15 个关键特征
        
        # 评分显著性
        max_score = max(scores.values()) if scores else 0
        
        # 综合置信度
        confidence = 0.6 * feature_completeness + 0.4 * max_score
        return min(1.0, confidence)
    
    def _determine_evidence_level(self, features: Dict) -> str:
        """确定总体证据等级"""
        evidence_counts = {"A": 0, "B": 0, "C": 0}
        
        for feature_key in features:
            rule = self.FEATURE_RULES.get(feature_key)
            if rule:
                evidence_counts[rule.evidence.value] += 1
        
        # 根据证据分布决定总体等级
        if evidence_counts["A"] > 0:
            return "A"
        elif evidence_counts["B"] >= 3:
            return "B"
        elif evidence_counts["B"] > 0 or evidence_counts["C"] >= 3:
            return "C"
        else:
            return "C"  # 默认
