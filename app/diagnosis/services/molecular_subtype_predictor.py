"""
乳腺癌分子分型预测服务

基于 IHC 标志物 (ER/PR/HER2/Ki-67) 和临床特征
预测分子分型，指导个体化治疗
"""

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class MolecularSubtype(str, Enum):
    """
    乳腺癌分子分型
    
    基于 PAM50 基因检测简化版 (IHC4)
    """
    LUMINAL_A = "Luminal A"      # 激素受体阳性，低增殖
    LUMINAL_B_HER2_NEG = "Luminal B (HER2-)"  # 激素受体阳性，高增殖
    LUMINAL_B_HER2_POS = "Luminal B (HER2+)"  # 激素受体阳性，HER2 阳性
    HER2_ENRICHED = "HER2-enriched"  # HER2 阳性，激素受体阴性
    BASAL_LIKE = "Basal-like"    # 三阴性，基底样
    NORMAL_LIKE = "Normal-like"  # 正常乳腺样 (少见)


class TreatmentRecommendation:
    """治疗建议生成器"""
    
    @staticmethod
    def get_treatment_plan(subtype: MolecularSubtype) -> Dict:
        """
        根据分子分型生成治疗建议
        
        Args:
            subtype: 分子分型
        
        Returns:
            Dict: 治疗方案
        """
        plans = {
            MolecularSubtype.LUMINAL_A: {
                "内分泌治疗": "首选 (他莫昔芬/芳香化酶抑制剂)",
                "化疗": "通常不需要 (低复发风险)",
                "靶向治疗": "不需要 (HER2 阴性)",
                "放疗": "保乳术后必需，部分全切患者可豁免",
                "预后": "最好，5 年生存率>90%"
            },
            MolecularSubtype.LUMINAL_B_HER2_NEG: {
                "内分泌治疗": "必需 (他莫昔芬/芳香化酶抑制剂)",
                "化疗": "通常需要 (高 Ki-67)",
                "靶向治疗": "不需要 (HER2 阴性)",
                "放疗": "保乳术后必需",
                "预后": "较好，但复发风险高于 Luminal A"
            },
            MolecularSubtype.LUMINAL_B_HER2_POS: {
                "内分泌治疗": "必需",
                "化疗": "必需",
                "靶向治疗": "必需 (曲妥珠单抗/帕妥珠单抗)",
                "放疗": "保乳术后必需",
                "预后": "中等，复发风险中等"
            },
            MolecularSubtype.HER2_ENRICHED: {
                "内分泌治疗": "不适用 (ER/PR 阴性)",
                "化疗": "必需 + 抗 HER2 双靶治疗",
                "靶向治疗": "必需 (曲妥珠单抗 + 帕妥珠单抗)",
                "放疗": "根据手术方式和分期决定",
                "预后": "抗 HER2 治疗显著改善预后"
            },
            MolecularSubtype.BASAL_LIKE: {
                "内分泌治疗": "不适用 (三阴性)",
                "化疗": "必需 (新辅助 + 辅助)",
                "靶向治疗": "无 HER2 靶点，可考虑免疫治疗",
                "放疗": "根据手术方式和分期决定",
                "预后": "较差，易早期复发，5 年后复发风险降低"
            },
            MolecularSubtype.NORMAL_LIKE: {
                "内分泌治疗": "可考虑",
                "化疗": "低风险可不使用",
                "靶向治疗": "不需要",
                "放疗": "保乳术后必需",
                "预后": "好，类似 Luminal A"
            }
        }
        
        return plans.get(subtype, {"error": "未知分型，无法生成治疗建议"})


@dataclass
class SubtypePrediction:
    """分子分型预测结果"""
    subtype: MolecularSubtype
    confidence: float           # 置信度 (0-1)
    er_status: str              # ER 状态
    pr_status: str              # PR 状态
    her2_status: str            # HER2 状态
    ki67_value: float           # Ki-67 指数
    grade: Optional[str] = None # 组织学分级
    treatment_plan: Optional[Dict] = None


class MolecularSubtypePredictor:
    """
    分子分型预测器
    
    基于 St. Gallen 共识和 ASCO/CAP 指南
    使用 IHC4 标志物 (ER/PR/HER2/Ki-67) 进行分型
    支持超声特征无创预测 (术前评估)
    """
    
    # 超声特征与分子分型的关联 (基于 radiomics 研究)
    ULTRASOUND_SUBTYPE_FEATURES = {
        MolecularSubtype.LUMINAL_A: {
            "shape": "oval",  # 椭圆形
            "margin": "circumscribed",  # 边界清晰
            "echo": "hypoechoic",  # 低回声
            "calcification": False,  # 少钙化
            "posterior": "enhancement_or_none",  # 增强或无变化
            "score_bonus": 0.15  # 符合时增加该分型概率
        },
        MolecularSubtype.LUMINAL_B_HER2_NEG: {
            "shape": "irregular_or_round",
            "margin": "indistinct_or_microlobulated",
            "echo": "heterogeneous",  # 回声不均
            "calcification": True,  # 可伴钙化
            "posterior": "mixed",
            "score_bonus": 0.20
        },
        MolecularSubtype.HER2_ENRICHED: {
            "shape": "irregular",
            "margin": "spiculated_or_angular",  # 毛刺/成角
            "echo": "marked_hypoechoic",  # 明显低回声
            "calcification": True,  # 常见微钙化
            "posterior": "shadowing",  # 后方衰减
            "score_bonus": 0.25
        },
        MolecularSubtype.BASAL_LIKE: {
            "shape": "round_or_irregular",  # 圆形或不规则
            "margin": "circumscribed",  # 边界清晰 (模拟良性)
            "echo": "hypoechoic",
            "calcification": False,
            "posterior": "enhancement",  # 后方增强 (特征性)
            "score_bonus": 0.22
        }
    }
    
    # 分子分型判定标准 (St. Gallen 2013)
    SUBTYPE_CRITERIA = {
        MolecularSubtype.LUMINAL_A: {
            "ER": "阳性",
            "PR": "高表达 (≥20%)",
            "HER2": "阴性",
            "Ki-67": "低 (<14-20%)"
        },
        MolecularSubtype.LUMINAL_B_HER2_NEG: {
            "ER": "阳性",
            "PR": "低表达 (<20%) 或任何",
            "HER2": "阴性",
            "Ki-67": "高 (≥14-20%)"
        },
        MolecularSubtype.LUMINAL_B_HER2_POS: {
            "ER": "阳性",
            "PR": "任何",
            "HER2": "阳性",
            "Ki-67": "任何"
        },
        MolecularSubtype.HER2_ENRICHED: {
            "ER": "阴性",
            "PR": "阴性",
            "HER2": "阳性",
            "Ki-67": "任何"
        },
        MolecularSubtype.BASAL_LIKE: {
            "ER": "阴性",
            "PR": "阴性",
            "HER2": "阴性",  # 三阴性
            "Ki-67": "任何 (通常高)"
        },
        MolecularSubtype.NORMAL_LIKE: {
            "ER": "阳性/阴性",
            "PR": "任何",
            "HER2": "阴性",
            "Ki-67": "低"
        }
    }
    
    @classmethod
    def predict(
        cls,
        er_status: bool,
        pr_percentage: float,
        her2_status: int,
        ki67_percentage: float,
        grade: Optional[str] = None
    ) -> SubtypePrediction:
        """
        预测分子分型
        
        Args:
            er_status: ER 状态 (True=阳性, False=阴性)
            pr_percentage: PR 阳性百分比 (0-100)
            her2_status: HER2 状态 (0/1+/2+/3+)
            ki67_percentage: Ki-67 指数 (0-100)
            grade: 组织学分级 (G1/G2/G3)
        
        Returns:
            SubtypePrediction: 分型预测结果
        
        Example:
            predictor.predict(
                er_status=True,
                pr_percentage=80,
                her2_status=0,
                ki67_percentage=10
            )
            # 返回: Luminal A 型
        """
        # 1. 标准化 HER2 状态
        her2_positive = her2_status in [3, '3+'] or (
            her2_status in [2, '2+'] and False  # FISH 未检测，暂按阴性
        )
        
        # 2. 判定分子分型
        subtype = cls._determine_subtype(
            er_positive=er_status,
            pr_high=pr_percentage >= 20,
            her2_positive=her2_positive,
            ki67_low=ki67_percentage < 14,
        )
        
        # 3. 计算置信度
        confidence = cls._calculate_confidence(
            subtype=subtype,
            er_status=er_status,
            pr_percentage=pr_percentage,
            her2_status=her2_status,
            ki67_percentage=ki67_percentage
        )
        
        # 4. 生成治疗建议
        treatment_plan = TreatmentRecommendation.get_treatment_plan(subtype)
        
        return SubtypePrediction(
            subtype=subtype,
            confidence=confidence,
            er_status="阳性" if er_status else "阴性",
            pr_status=f"{pr_percentage}%" if pr_percentage else "未知",
            her2_status=cls._format_her2(her2_status),
            ki67_value=ki67_percentage,
            grade=grade,
            treatment_plan=treatment_plan
        )
    
    @classmethod
    def _determine_subtype(
        cls,
        er_positive: bool,
        pr_high: bool,
        her2_positive: bool,
        ki67_low: bool
    ) -> MolecularSubtype:
        """
        判定分子分型
        
        决策树:
        1. HER2 阳性 → Luminal B (HER2+) 或 HER2-enriched
        2. 三阴性 → Basal-like
        3. HR 阳性 + HER2 阴性 → Luminal A 或 Luminal B (HER2-)
        """
        # HER2 阳性
        if her2_positive:
            if er_positive:
                return MolecularSubtype.LUMINAL_B_HER2_POS
            else:
                return MolecularSubtype.HER2_ENRICHED
        
        # 三阴性 (ER-/PR-/HER2-)
        if not er_positive:
            return MolecularSubtype.BASAL_LIKE
        
        # HR 阳性 + HER2 阴性
        if er_positive and not her2_positive:
            if ki67_low and pr_high:
                return MolecularSubtype.LUMINAL_A
            else:
                return MolecularSubtype.LUMINAL_B_HER2_NEG
        
        # 默认
        return MolecularSubtype.LUMINAL_A
    
    @classmethod
    def _calculate_confidence(
        cls,
        subtype: MolecularSubtype,
        er_status: bool,
        pr_percentage: float,
        her2_status: int,
        ki67_percentage: float
    ) -> float:
        """
        计算预测置信度
        
        基于标志物表达的极端程度
        越接近阈值，置信度越低
        
        Args:
            subtype: 预测分型
            er_status: ER 状态
            pr_percentage: PR 百分比
            her2_status: HER2 状态
            ki67_percentage: Ki-67 百分比
        
        Returns:
            float: 置信度 (0-1)
        """
        base_confidence = 0.9  # 基础置信度
        
        # PR 表达接近阈值时降低置信度
        if subtype == MolecularSubtype.LUMINAL_A and pr_percentage < 30:
            base_confidence -= 0.15
        
        # Ki-67 接近阈值时降低置信度
        if subtype in [MolecularSubtype.LUMINAL_A, 
                       MolecularSubtype.LUMINAL_B_HER2_NEG]:
            if 10 <= ki67_percentage <= 20:
                base_confidence -= 0.12
        
        # HER2 2+ 状态 (不确定) 降低置信度
        if her2_status == 2:
            base_confidence -= 0.15
        
        return max(0.6, min(0.98, base_confidence))
    
    @classmethod
    def _format_her2(cls, her2_status) -> str:
        """格式化 HER2 状态"""
        if her2_status == 0:
            return "0 (阴性)"
        elif her2_status == 1:
            return "1+ (阴性)"
        elif her2_status == 2:
            return "2+ (需 FISH 确认)"
        elif her2_status == 3:
            return "3+ (阳性)"
        else:
            return str(her2_status)
    
    @classmethod
    def get_subtype_description(cls, subtype: MolecularSubtype) -> str:
        """
        获取分子分型详细说明
        
        Args:
            subtype: 分子分型
        
        Returns:
            str: 详细说明
        """
        descriptions = {
            MolecularSubtype.LUMINAL_A: """
                **Luminal A 型** (最好预后)
                
                - 特征：ER/PR 强阳性，HER2 阴性，Ki-67 低表达
                - 占比：约 40-50% 乳腺癌
                - 生物学行为：惰性，生长慢，转移晚
                - 治疗：以内分泌治疗为主
                - 5 年生存率：>90%
            """,
            MolecularSubtype.LUMINAL_B_HER2_NEG: """
                **Luminal B 型 (HER2 阴性)**
                
                - 特征：ER 阳性，HER2 阴性，Ki-67 高 (≥14-20%) 或 PR<20%
                - 占比：约 20-30%
                - 生物学行为：增殖活跃，复发风险高于 Luminal A
                - 治疗：内分泌治疗 + 化疗
                - 5 年生存率：75-85%
            """,
            MolecularSubtype.LUMINAL_B_HER2_POS: """
                **Luminal B 型 (HER2 阳性)**
                
                - 特征：ER 阳性，HER2 阳性
                - 占比：约 10-15%
                - 生物学行为：侵袭性中等
                - 治疗：内分泌治疗 + 化疗 + 抗 HER2 靶向
                - 5 年生存率：70-80%
            """,
            MolecularSubtype.HER2_ENRICHED: """
                **HER2 富集型**
                
                - 特征：ER/PR 阴性，HER2 阳性
                - 占比：约 15-20%
                - 生物学行为：侵袭性较强，易复发转移
                - 治疗：化疗 + 抗 HER2 双靶
                - 预后：抗 HER2 治疗显著改善生存
                - 5 年生存率：65-75%
            """,
            MolecularSubtype.BASAL_LIKE: """
                **基底样型 (三阴性)**
                
                - 特征：ER/PR/HER2 阴性 (三阴性)
                - 占比：约 15-20%
                - 生物学行为：高度侵袭，早期复发，内脏转移倾向
                - 治疗：化疗为主，可探索免疫治疗
                - 预后：较差，无标准内分泌/靶向治疗
                - 5 年生存率：55-65%
            """,
            MolecularSubtype.NORMAL_LIKE: """
                **正常乳腺样** (罕见)
                
                - 特征：基因表达类似正常乳腺组织
                - 占比：<5%
                - 生物学行为：惰性
                - 治疗：类似 Luminal A
                - 预后：良好
            """
        }
        
        return descriptions.get(subtype, "未知分型")
    
    @classmethod
    def predict_from_ultrasound(cls, ultrasound_features: Dict) -> Dict[str, float]:
        """
        基于超声特征预测分子分型概率分布
        
        使用 radiomics 特征与分子分型的关联模型
        适合术前无创评估
        
        Args:
            ultrasound_features: 超声征象
                {
                    "shape": "oval|round|irregular",
                    "margin_types": [...],
                    "echo_pattern": "...",
                    "calcification_present": bool,
                    "posterior_features": [...]
                }
        
        Returns:
            Dict[str, float]: 各分子分型的概率分布
                {"Luminal A": 0.15, "HER2-enriched": 0.45, ...}
        """
        # 初始化概率分布
        probabilities = {
            MolecularSubtype.LUMINAL_A: 0.25,
            MolecularSubtype.LUMINAL_B_HER2_NEG: 0.25,
            MolecularSubtype.HER2_ENRICHED: 0.25,
            MolecularSubtype.BASAL_LIKE: 0.25
        }
        
        # 提取超声特征
        shape = ultrasound_features.get("shape", "")
        margin_types = ultrasound_features.get("margin_types") or []
        echo_pattern = ultrasound_features.get("echo_pattern", "")
        calcification = ultrasound_features.get("calcification_present", False)
        posterior = ultrasound_features.get("posterior_features") or []
        
        # 评估各分型的匹配度
        for subtype, criteria in cls.ULTRASOUND_SUBTYPE_FEATURES.items():
            match_score = 0.0
            
            # 形状匹配
            expected_shape = criteria["shape"]
            if expected_shape == "oval" and shape == "oval":
                match_score += 0.2
            elif expected_shape == "irregular" and shape == "irregular":
                match_score += 0.2
            elif expected_shape == "round_or_irregular" and shape in ["round", "irregular"]:
                match_score += 0.15
            elif expected_shape == "irregular_or_round" and shape in ["irregular", "round"]:
                match_score += 0.15
            
            # 边缘匹配
            margin_desc = " ".join(margin_types)
            if "circumscribed" in criteria["margin"] and "circumscribed" in margin_desc:
                match_score += 0.2
            elif "spiculated" in criteria["margin"] and "spiculated" in margin_desc:
                match_score += 0.25
            elif "indistinct" in criteria["margin"] and "indistinct" in margin_desc:
                match_score += 0.15
            elif "angular" in criteria["margin"] and "angular" in margin_desc:
                match_score += 0.2
            
            # 回声匹配
            if criteria["echo"] == "hypoechoic" and echo_pattern == "hypoechoic":
                match_score += 0.15
            elif criteria["echo"] == "marked_hypoechoic" and echo_pattern == "marked_hypoechoic":
                match_score += 0.2
            elif criteria["echo"] == "heterogeneous" and echo_pattern == "heterogeneous":
                match_score += 0.15
            
            # 钙化匹配
            if criteria["calcification"] == calcification:
                match_score += 0.15
            
            # 后方回声匹配
            if "enhancement" in criteria["posterior"] and "enhancement" in posterior:
                match_score += 0.15
            elif "shadowing" in criteria["posterior"] and "shadowing" in posterior:
                match_score += 0.2
            elif "mixed" in criteria["posterior"] and "mixed" in posterior:
                match_score += 0.1
            
            # 应用匹配度 Bonus
            if match_score > 0.5:
                probabilities[subtype] += criteria["score_bonus"]
        
        # 归一化概率分布
        total = sum(probabilities.values())
        probabilities = {k: round(v / total, 3) for k, v in probabilities.items()}
        
        # 转为基础类型字符串的字典
        return {k.value: v for k, v in probabilities.items()}
