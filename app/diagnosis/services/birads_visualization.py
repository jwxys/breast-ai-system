"""
BI-RADS 评估可视化模块

生成可视化数据用于前端图表展示
"""

from typing import Dict, List, Any
from pydantic import BaseModel


class VisualizationData(BaseModel):
    """可视化数据结构"""
    birads_category: str
    risk_gauge: Dict[str, Any]
    feature_scores: List[Dict[str, Any]]
    decision_tree: List[Dict[str, Any]]
    radar_chart: Dict[str, float]


class BIRADSVisualization:
    """
    BI-RADS 评估可视化生成器
    """
    
    RISK_THRESHOLDS = [
        {"category": "1-2", "max": 0, "color": "#28a745"},
        {"category": "3", "max": 2, "color": "#5cb85c"},
        {"category": "4A", "max": 10, "color": "#f0ad4e"},
        {"category": "4B", "max": 50, "color": "#ff9800"},
        {"category": "4C", "max": 95, "color": "#ff5722"},
        {"category": "5", "max": 100, "color": "#d9534f"},
    ]
    
    # BI-RADS 特征权重分组
    FEATURE_GROUPS = {
        "shape": ["irregular_shape", "taller_than_wide", "round_shape"],
        "margin": ["spiculated_margin", "angular_margin", "microlobulated_margin", "indistinct_margin", "echogenic_halo"],
        "echo": ["marked_hypoechoic", "heterogeneous_echo", "hypoechoic"],
        "calcification": ["fine_calcification", "pleomorphic_calcification", "linear_calcification", "branched_calcification"],
        "vascularity": ["rich_vascularity", "irregular_vessels", "penetrating_vessels", "central_vessels"],
        "posterior": ["posterior_shadowing", "mixed_posterior", "no_posterior"]
    }
    
    @classmethod
    def generate_visualization_data(
        cls,
        ultrasound_features: Dict,
        malignant_score: float,
        birads_category: str
    ) -> VisualizationData:
        """生成可视化数据"""
        risk_gauge = cls._generate_risk_gauge(malignant_score)
        feature_scores = cls._generate_feature_scores(ultrasound_features)
        decision_tree = cls._generate_decision_tree(ultrasound_features, birads_category)
        radar_chart = cls._generate_radar_chart(ultrasound_features)
        
        return VisualizationData(
            birads_category=birads_category,
            risk_gauge=risk_gauge,
            feature_scores=feature_scores,
            decision_tree=decision_tree,
            radar_chart=radar_chart
        )
    
    @classmethod
    def _generate_risk_gauge(cls, score: float) -> Dict[str, Any]:
        """生成风险仪表盘数据"""
        return {
            "min": 0,
            "max": 100,
            "current": min(score, 100),
            "thresholds": cls.RISK_THRESHOLDS,
            "level": cls._get_risk_level(score)
        }
    
    @classmethod
    def _get_risk_level(cls, score: float) -> str:
        """获取风险等级描述"""
        if score <= 2:
            return "可能良性"
        elif score <= 10:
            return "低度可疑"
        elif score <= 50:
            return "中度可疑"
        elif score <= 95:
            return "高度可疑"
        else:
            return "高度提示恶性"
    
    @classmethod
    def _generate_feature_scores(cls, features: Dict) -> List[Dict[str, Any]]:
        """生成特征贡献度数据"""
        from app.diagnosis.services.birads_engine import BIRADSEngine
        
        weights = BIRADSEngine.MALIGNANT_FEATURE_WEIGHTS
        feature_list = []
        
        # 形状
        if features.get("shape") == "irregular":
            feature_list.append({"name": "不规则形", "score": weights.get("irregular_shape", 0), "group": "形状"})
        if features.get("orientation") == "not_parallel":
            feature_list.append({"name": "纵横比>1", "score": weights.get("taller_than_wide", 0), "group": "形状"})
        
        # 边缘
        margin_map = {
            "spiculated": "spiculated_margin",
            "angular": "angular_margin",
            "microlobulated": "microlobulated_margin",
            "indistinct": "indistinct_margin"
        }
        for margin_type in features.get("margin_types") or []:
            if margin_type in margin_map:
                key = margin_map[margin_type]
                feature_list.append({"name": f"{margin_type}状边缘", "score": weights.get(key, 0), "group": "边缘"})
        
        # 回声
        if features.get("echo_pattern") == "marked_hypoechoic":
            feature_list.append({"name": "明显低回声", "score": weights.get("marked_hypoechoic", 0), "group": "回声"})
        elif features.get("echo_pattern") == "heterogeneous":
            feature_list.append({"name": "回声不均", "score": weights.get("heterogeneous_echo", 0), "group": "回声"})
        
        # 钙化
        if features.get("calcification_present"):
            for calc_type in features.get("calcification_types") or []:
                calc_map = {"fine": "fine_calcification", "pleomorphic": "pleomorphic_calcification", "linear": "linear_calcification"}
                if calc_type in calc_map:
                    feature_list.append({"name": f"{calc_type}钙化", "score": weights.get(calc_map[calc_type], 0), "group": "钙化"})
        
        # 后方回声
        posterior = features.get("posterior_features") or []
        if "shadowing" in posterior:
            feature_list.append({"name": "后方衰减", "score": weights.get("posterior_shadowing", 0), "group": "后方回声"})
        
        # 按分数排序
        feature_list.sort(key=lambda x: x["score"], reverse=True)
        
        return feature_list
    
    @classmethod
    def _generate_decision_tree(cls, features: Dict, birads: str) -> List[Dict[str, Any]]:
        """生成决策树路径"""
        path = []
        
        # 第 1 层:形状
        shape = features.get("shape")
        if shape == "irregular":
            path.append({"step": 1, "feature": "形状", "value": "不规则形", "score_impact": "+2.5", "decision": "增加恶性风险"})
        elif shape == "oval":
            path.append({"step": 1, "feature": "形状", "value": "椭圆形", "score_impact": "0", "decision": "良性特征"})
        
        # 第 2 层：纵横比
        if features.get("orientation") == "not_parallel":
            path.append({"step": 2, "feature": "纵横比", "value": ">1 (taller-than-wide)", "score_impact": "+7.0", "decision": "强恶性征象"})
        
        # 第 3 层：边缘
        margin_types = features.get("margin_types") or []
        if "spiculated" in margin_types:
            path.append({"step": 3, "feature": "边缘", "value": "毛刺状", "score_impact": "+8.0", "decision": "最强恶性征象"})
        elif "angular" in margin_types:
            path.append({"step": 3, "feature": "边缘", "value": "成角", "score_impact": "+2.0", "decision": "恶性征象"})
        
        # 第 4 层:最终分级
        path.append({"step": 4, "feature": "BI-RADS 分级", "value": birads, "score_impact": "-", "decision": cls._get_recommendation(birads)})
        
        return path
    
    @classmethod
    def _get_recommendation(cls, birads: str) -> str:
        """获取分级建议"""
        recommendations = {
            "2": "定期随访",
            "3": "短期随访 (3-6 个月)",
            "4A": "穿刺活检",
            "4B": "穿刺活检",
            "4C": "穿刺活检或手术",
            "5": "手术切除"
        }
        return recommendations.get(birads, "进一步评估")
    
    @classmethod
    def _generate_radar_chart(cls, features: Dict) -> Dict[str, float]:
        """生成雷达图数据 (5 个维度)"""
        return {
            "shape": 1.0 if features.get("shape") == "irregular" else (0.3 if features.get("shape") == "round" else 0.1),
            "margin": cls._calculate_margin_score(features.get("margin_types") or []),
            "echo": cls._calculate_echo_score(features.get("echo_pattern", "")),
            "calcification": 1.0 if features.get("calcification_present") else 0.0,
            "posterior": cls._calculate_posterior_score(features.get("posterior_features") or [])
        }
    
    @classmethod
    def _calculate_margin_score(cls, margins: List[str]) -> float:
        """计算边缘维度分数"""
        score_map = {"spiculated": 1.0, "angular": 0.8, "microlobulated": 0.6, "indistinct": 0.4, "circumscribed": 0.1}
        if not margins:
            return 0.1
        return max([score_map.get(m, 0.1) for m in margins])
    
    @classmethod
    def _calculate_echo_score(cls, echo: str) -> float:
        """计算回声维度分数"""
        score_map = {"marked_hypoechoic": 1.0, "heterogeneous": 0.6, "hypoechoic": 0.4, "anechoic": 0.1, "isoechoic": 0.2}
        return score_map.get(echo, 0.2)
    
    @classmethod
    def _calculate_posterior_score(cls, posterior: List[str]) -> float:
        """计算后方回声维度分数"""
        if "shadowing" in posterior:
            return 1.0
        elif "mixed" in posterior:
            return 0.6
        elif "enhancement" in posterior:
            return 0.2
        return 0.3
