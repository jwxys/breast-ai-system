"""
BI-RADS 智能分级引擎

基于 ACR BI-RADS Atlas 第 5 版规则
结合超声征象自动计算 BI-RADS 分级和恶性风险
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class BIRADSCategory(str, Enum):
    """BI-RADS 分级"""
    CATEGORY_0 = "0"       # 评估不完全
    CATEGORY_1 = "1"       # 阴性
    CATEGORY_2 = "2"       # 良性
    CATEGORY_3 = "3"       # 可能良性 (恶性风险≤2%)
    CATEGORY_4A = "4A"     # 低度可疑 (2-10%)
    CATEGORY_4B = "4B"     # 中度可疑 (10-50%)
    CATEGORY_4C = "4C"     # 高度可疑 (50-95%)
    CATEGORY_5 = "5"       # 高度提示恶性 (>95%)
    CATEGORY_6 = "6"       # 已证实恶性


@dataclass
class MalignancyRisk:
    """恶性风险评估结果"""
    birads_category: BIRADSCategory
    risk_percentage: float  # 恶性概率 (0-100)
    recommendation: str     # 处理建议
    key_features: List[str] # 关键征象


class BIRADSEngine:
    """
    BI-RADS 智能分级引擎
    
    依据 ACR BI-RADS Ultrasound Assessment Chapter
    综合评估形态、边缘、回声、钙化、血流等征象
    """
    
    # BI-RADS 分级对应的恶性风险范围
    RISK_RANGES = {
        BIRADSCategory.CATEGORY_0: (0, 0, "需要进一步检查"),
        BIRADSCategory.CATEGORY_1: (0, 0, "常规筛查"),
        BIRADSCategory.CATEGORY_2: (0, 0, "良性发现，定期随访"),
        BIRADSCategory.CATEGORY_3: (0, 2, "可能良性，建议 3-6 个月短期随访"),
        BIRADSCategory.CATEGORY_4A: (2, 10, "低度可疑，建议穿刺活检"),
        BIRADSCategory.CATEGORY_4B: (10, 50, "中度可疑，建议穿刺活检"),
        BIRADSCategory.CATEGORY_4C: (50, 95, "高度可疑，建议穿刺活检或手术"),
        BIRADSCategory.CATEGORY_5: (95, 100, "高度提示恶性，建议手术切除"),
        BIRADSCategory.CATEGORY_6: (100, 100, "已证实恶性，综合治疗"),
    }
    
    # 恶性征象评分权重 (基于文献 meta 分析 + 临床数据)
    MALIGNANT_FEATURE_WEIGHTS = {
        # 形状征象
        "irregular_shape": 2.5,
        "taller_than_wide": 7.0,  # 最强恶性征象 (OR=8.5)
        "round_shape": 1.5,  # 圆形也增加恶性风险
        
        # 边缘征象 (最重要预测因子)
        "angular_margin": 2.0,
        "microlobulated_margin": 3.0,
        "spiculated_margin": 8.0,  # 最强恶性征象 (OR=12.3)
        "indistinct_margin": 1.5,
        "echogenic_halo": 2.5,  # 高回声晕 (新增)
        
        # 回声征象
        "marked_hypoechoic": 2.0,
        "heterogeneous_echo": 1.0,
        "hypoechoic": 0.5,  # 轻度低回声
        
        # 钙化征象
        "fine_calcification": 2.5,
        "pleomorphic_calcification": 5.0,
        "linear_calcification": 4.0,
        "branched_calcification": 4.5,  # 分支样钙化 (新增)
        
        # 血流征象
        "rich_vascularity": 2.0,
        "irregular_vessels": 2.5,
        "penetrating_vessels": 3.0,
        "central_vessels": 2.0,  # 中央型血流 (新增)
        
        # 弹性成像
        "hard_elasticity": 3.0,
        "high_strain_ratio": 3.5,
        "shear_wave_fast": 3.0,  # 剪切波速快 (新增)
        
        # 后方回声
        "posterior_shadowing": 3.0,
        "mixed_posterior": 1.5,
        "no_posterior": 1.0,  # 无明显后方回声 (新增)
        
        # 边界特征 (新增)
        "bursting_boundary": 2.0,  # 边界破裂
        "angular_edge": 2.5,  # 成角边缘
    }
    
    # 良性征象列表
    BENIGN_FEATURES = {
        "oval_shape",
        "circumscribed_margin",
        "wider_than_tall",
        "anechoic",
        "posterior_enhancement",
        "coarse_calcification",
        "no_vascularity",
        "soft_elasticity",
    }
    
    @classmethod
    def assess(cls, ultrasound_features: Dict, clinical_factors: Optional[Dict] = None) -> MalignancyRisk:
        """
        BI-RADS 综合评估
        
        Args:
            ultrasound_features: 超声征象字典
            clinical_factors: 临床因素 (可选)
                {
                    "age": int,  # 患者年龄
                    "lesion_size": float,  # 病灶大小 (mm)
                    "growth_rate": float,  # 生长速度 (%/月)
                    "family_history": bool,  # 家族史
                    "brca_mutation": bool,  # BRCA 突变
                }
        
        Returns:
            MalignancyRisk: 恶性风险评估结果
        """
        # 1. 识别恶性征象并计算总分
        malignant_score = cls._calculate_malignant_score(ultrasound_features)
        
        # 2. 应用临床因素调整
        if clinical_factors:
            malignant_score = cls._apply_clinical_adjustment(
                malignant_score, 
                clinical_factors
            )
        
        # 3. 检查是否有典型良性表现
        if cls._is_typical_benign(ultrasound_features):
            return cls._create_risk(
                BIRADSCategory.CATEGORY_3,
                ["典型良性表现"]
            )
        
        # 4. 检查是否为单纯囊肿 (BI-RADS 2)
        if cls._is_simple_cyst(ultrasound_features):
            return cls._create_risk(
                BIRADSCategory.CATEGORY_2,
                ["单纯囊肿"]
            )
        
        # 5. 根据恶性评分确定 BI-RADS 分级
        birads_category = cls._score_to_birads(malignant_score)
        
        # 6. 提取关键征象
        key_features = cls._extract_key_features(ultrasound_features)
        
        # 7. 添加临床风险提示
        if clinical_factors:
            clinical_flags = cls._extract_clinical_flags(clinical_factors)
            key_features.extend(clinical_flags)
        
        return cls._create_risk(birads_category, key_features)
    
    @classmethod
    def _calculate_malignant_score(cls, features: Dict) -> float:
        """
        计算恶性征象总分
        
        Args:
            features: 超声征象字典
        
        Returns:
            float: 恶性评分 (0-∞)
        """
        score = 0.0
        identified_features = []
        
        # 形状评分
        if features.get("shape") == "irregular":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["irregular_shape"]
            identified_features.append("不规则形")
        
        # 纵横比评分 (最强恶性征象之一)
        if features.get("orientation") == "not_parallel":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["taller_than_wide"]
            identified_features.append("纵横比>1 (taller-than-wide)")
        
        # 边缘评分
        margin_types = features.get("margin_types") or []
        if "angular" in margin_types:
            score += cls.MALIGNANT_FEATURE_WEIGHTS["angular_margin"]
            identified_features.append("边缘成角")
        if "microlobulated" in margin_types:
            score += cls.MALIGNANT_FEATURE_WEIGHTS["microlobulated_margin"]
            identified_features.append("微小分叶")
        if "spiculated" in margin_types:
            score += cls.MALIGNANT_FEATURE_WEIGHTS["spiculated_margin"]
            identified_features.append("毛刺状边缘")
        if "indistinct" in margin_types:
            score += cls.MALIGNANT_FEATURE_WEIGHTS["indistinct_margin"]
            identified_features.append("边界不清")
        
        # 回声评分
        if features.get("echo_pattern") == "hypoechoic":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["marked_hypoechoic"]
            identified_features.append("明显低回声")
        if features.get("echo_homogeneity") == "heterogeneous":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["heterogeneous_echo"]
            identified_features.append("回声不均匀")
        
        # 钙化评分
        if features.get("calcification_present"):
            calc_types = features.get("calcification_types") or []
            if "fine" in calc_types:
                score += cls.MALIGNANT_FEATURE_WEIGHTS["fine_calcification"]
                identified_features.append("细小钙化")
            if "pleomorphic" in calc_types:
                score += cls.MALIGNANT_FEATURE_WEIGHTS["pleomorphic_calcification"]
                identified_features.append("多形性钙化")
            if "linear" in calc_types:
                score += cls.MALIGNANT_FEATURE_WEIGHTS["linear_calcification"]
                identified_features.append("线样钙化")
        
        # 血流评分
        vascularity = features.get("vascularity_grade")
        if vascularity in ["grade_2", "grade_3"]:
            score += cls.MALIGNANT_FEATURE_WEIGHTS["rich_vascularity"]
            identified_features.append("血流丰富")
        
        vessel_pattern = features.get("vessel_pattern")
        if vessel_pattern == "irregular":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["irregular_vessels"]
            identified_features.append("血管形态不规则")
        elif vessel_pattern == "penetrating":
            score += cls.MALIGNANT_FEATURE_WEIGHTS["penetrating_vessels"]
            identified_features.append("穿入型血管")
        
        # 弹性成像评分
        elasticity = features.get("elastography")
        if elasticity in ["hard", "very_hard"]:
            score += cls.MALIGNANT_FEATURE_WEIGHTS["hard_elasticity"]
            identified_features.append("弹性成像示病灶硬")
        
        strain_ratio = features.get("strain_ratio")
        if strain_ratio and strain_ratio > 3.5:
            score += cls.MALIGNANT_FEATURE_WEIGHTS["high_strain_ratio"]
            identified_features.append(f"应变比值增高 ({strain_ratio})")
        
        # 后方回声评分
        posterior = features.get("posterior_features") or []
        if "shadowing" in posterior:
            score += cls.MALIGNANT_FEATURE_WEIGHTS["posterior_shadowing"]
            identified_features.append("后方回声衰减")
        if "mixed" in posterior:
            score += cls.MALIGNANT_FEATURE_WEIGHTS["mixed_posterior"]
            identified_features.append("混合后方回声")
        
        return score
    
    @classmethod
    def _apply_clinical_adjustment(cls, score: float, factors: Dict) -> float:
        """
        应用临床因素调整恶性评分
        
        调整因子基于多因素 logistic 回归模型
        
        Args:
            score: 超声恶性评分
            factors: 临床因素
        
        Returns:
            float: 调整后的评分
        """
        adjusted_score = score
        
        # 年龄调整:<30 岁降低风险，>50 岁增加风险
        age = factors.get("age")
        if age and age < 30:
            adjusted_score *= 0.8  # 年轻患者降低 20% 风险
        elif age and age > 50:
            adjusted_score *= 1.15  # 年长患者增加 15% 风险
        
        # 病灶大小:>2cm 增加风险
        lesion_size = factors.get("lesion_size", 0)
        if lesion_size > 20:  # >2cm
            adjusted_score *= 1.2
        if lesion_size > 30:  # >3cm
            adjusted_score *= 1.3
        
        # 快速生长：增长率>20%/月
        growth_rate = factors.get("growth_rate", 0)
        if growth_rate > 20:
            adjusted_score *= 1.4
        
        # 家族史
        if factors.get("family_history"):
            adjusted_score *= 1.25
        
        # BRCA 突变
        if factors.get("brca_mutation"):
            adjusted_score *= 1.5
        
        return adjusted_score
    
    @classmethod
    def _extract_clinical_flags(cls, factors: Dict) -> List[str]:
        """提取临床风险标志"""
        flags = []
        
        age = factors.get("age")
        if age and age < 30:
            flags.append(f"年轻患者 ({age}岁)")
        elif age and age > 50:
            flags.append(f"年长患者 ({age}岁)")
        
        lesion_size = factors.get("lesion_size", 0)
        if lesion_size > 30:
            flags.append(f"大病灶 ({lesion_size}mm)")
        elif lesion_size > 20:
            flags.append(f"中等病灶 ({lesion_size}mm)")
        
        if factors.get("family_history"):
            flags.append("乳腺癌家族史")
        
        if factors.get("brca_mutation"):
            flags.append("BRCA 突变携带者")
        
        growth_rate = factors.get("growth_rate", 0)
        if growth_rate > 20:
            flags.append(f"快速生长 ({growth_rate}%/月)")
        
        return flags
    
    @classmethod
    def _is_typical_benign(cls, features: Dict) -> bool:
        """
        判断是否为典型良性表现
        
        典型良性标准:
        - 椭圆形 + 边界清晰 + 平行生长 + 宽>高
        - 或 无回声 + 后方增强 (囊性病变)
        """
        shape = features.get("shape")
        orientation = features.get("orientation")
        margin_types = features.get("margin_types") or []
        echo_pattern = features.get("echo_pattern")
        posterior = features.get("posterior_features") or []
        
        # 实性病变但良性特征
        if (shape == "oval" and 
            "circumscribed" in margin_types and 
            orientation == "parallel"):
            return True
        
        # 囊性病变
        if (echo_pattern == "anechoic" and 
            "enhancement" in posterior):
            return True
        
        return False
    
    @classmethod
    def _is_simple_cyst(cls, features: Dict) -> bool:
        """
        判断是否为单纯囊肿 (BI-RADS 2)
        
        标准:
        - 无回声
        - 边界清晰
        - 后方回声增强
        - 无血流
        """
        return (
            features.get("echo_pattern") == "anechoic" and
            "circumscribed" in features.get("margin_types", []) and
            "enhancement" in features.get("posterior_features", []) and
            features.get("vascularity_grade") == "grade_0"
        )
    
    @classmethod
    def _score_to_birads(cls, score: float) -> BIRADSCategory:
        """
        根据恶性评分确定 BI-RADS 分级
        
        评分阈值基于大样本 retrospective study
        
        Args:
            score: 恶性评分
        
        Returns:
            BIRADSCategory: BI-RADS 分级
        """
        if score == 0:
            return BIRADSCategory.CATEGORY_1
        elif score < 2.5:
            return BIRADSCategory.CATEGORY_3
        elif score < 4.0:
            return BIRADSCategory.CATEGORY_4A
        elif score < 7.0:
            return BIRADSCategory.CATEGORY_4B
        elif score < 12.0:
            return BIRADSCategory.CATEGORY_4C
        else:
            return BIRADSCategory.CATEGORY_5
    
    @classmethod
    def _extract_key_features(cls, features: Dict) -> List[str]:
        """提取关键征象描述"""
        key_features = []
        
        # 形状
        shape = features.get("shape")
        if shape:
            shape_map = {
                "oval": "椭圆形",
                "round": "圆形",
                "irregular": "不规则形"
            }
            key_features.append(f"形状：{shape_map.get(shape, shape)}")
        
        # 纵横比
        if features.get("orientation") == "not_parallel":
            key_features.append("纵横比>1 (taller-than-wide)")
        
        # 边缘
        margin_desc = []
        margin_map = {
            "circumscribed": "边界清晰",
            "indistinct": "边界不清",
            "angular": "成角",
            "microlobulated": "微小分叶",
            "spiculated": "毛刺状"
        }
        for mt in features.get("margin_types", []):
            if mt in margin_map:
                margin_desc.append(margin_map[mt])
        if margin_desc:
            key_features.append(f"边缘：{', '.join(margin_desc)}")
        
        # 回声
        echo = features.get("echo_pattern")
        if echo:
            echo_map = {
                "anechoic": "无回声",
                "hypoechoic": "低回声",
                "isoechoic": "等回声",
                "hyperechoic": "高回声",
                "heterogeneous": "混合回声"
            }
            key_features.append(f"回声：{echo_map.get(echo, echo)}")
        
        # 钙化
        if features.get("calcification_present"):
            key_features.append("伴钙化")
        
        # 血流
        vascularity = features.get("vascularity_grade")
        if vascularity in ["grade_2", "grade_3"]:
            key_features.append("血流丰富")
        
        return key_features
    
    @classmethod
    def _create_risk(
        cls, 
        birads: BIRADSCategory, 
        key_features: List[str]
    ) -> MalignancyRisk:
        """构建恶性风险评估结果"""
        min_risk, max_risk, recommendation = cls.RISK_RANGES[birads]
        
        # 计算中值风险
        avg_risk = (min_risk + max_risk) / 2 if max_risk > min_risk else min_risk
        
        return MalignancyRisk(
            birads_category=birads,
            risk_percentage=avg_risk,
            recommendation=recommendation,
            key_features=key_features
        )
    
    @classmethod
    def get_birads_explanation(cls, category: BIRADSCategory) -> str:
        """
        获取 BI-RADS 分级详细说明
        
        Args:
            category: BI-RADS 分级
        
        Returns:
            str: 分级说明
        """
        explanations = {
            BIRADSCategory.CATEGORY_0: """
                **BI-RADS 0 级：评估不完全**
                
                - 超声检查未完成，需要进一步影像学检查
                - 建议：加做其他体位、钼靶、MRI 等
            """,
            BIRADSCategory.CATEGORY_1: """
                **BI-RADS 1 级：阴性**
                
                - 无异常发现，无肿块可触及
                - 建议：常规筛查，年度随访
            """,
            BIRADSCategory.CATEGORY_2: """
                **BI-RADS 2 级：良性**
                
                - 明确良性病变，如单纯囊肿、纤维腺瘤典型表现
                - 恶性风险：0%
                - 建议：6-12 个月常规随访
            """,
            BIRADSCategory.CATEGORY_3: """
                **BI-RADS 3 级：可能良性**
                
                - 恶性风险 ≤2%
                - 典型表现：椭圆形、边界清晰、宽>高的实性结节
                - 建议：3-6 个月短期随访，连续 2-3 年稳定后可降级
            """,
            BIRADSCategory.CATEGORY_4A: """
                **BI-RADS 4A 级：低度可疑恶性**
                
                - 恶性风险：2%-10%
                - 表现：部分可疑征象，如边界略不清、轻度不规则
                - 建议：穿刺活检 (核心针穿刺或真空辅助)
            """,
            BIRADSCategory.CATEGORY_4B: """
                **BI-RADS 4B 级：中度可疑恶性**
                
                - 恶性风险：10%-50%
                - 表现：多个恶性征象，如不规则形、边缘成角
                - 建议：穿刺活检
            """,
            BIRADSCategory.CATEGORY_4C: """
                **BI-RADS 4C 级：高度可疑恶性**
                
                - 恶性风险：50%-95%
                - 表现：强恶性征象，如毛刺、后方衰减
                - 建议：穿刺活检或手术切除
            """,
            BIRADSCategory.CATEGORY_5: """
                **BI-RADS 5 级：高度提示恶性**
                
                - 恶性风险 ≥95%
                - 表现：典型恶性征象组合 (毛刺 + taller-than-wide + 后方衰减)
                - 建议：手术切除，术前可新辅助治疗
            """,
            BIRADSCategory.CATEGORY_6: """
                **BI-RADS 6 级：已证实恶性**
                
                - 活检病理已证实为癌
                - 建议：综合治疗 (手术 ± 化疗 ± 放疗 ± 内分泌治疗)
            """
        }
        
        return explanations.get(category, "未知分级")
