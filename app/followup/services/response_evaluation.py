"""
疗效评估服务

支持实体瘤疗效评价 (RECIST 1.1)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class ResponseCategory(str, Enum):
    """疗效分类 (RECIST 1.1)"""
    CR = "CR"    # 完全缓解
    PR = "PR"    # 部分缓解
    SD = "SD"    # 疾病稳定
    PD = "PD"    # 疾病进展


@dataclass
class TumorMeasurement:
    """肿瘤测量数据"""
    date: datetime
    measurements: List[float]  # 最长径 (mm)
    sum_longest_diameter: float


class ResponseEvaluator:
    """
    疗效评估器
    
    基于 RECIST 1.1 标准
    """
    
    def __init__(
        self,
        baseline: TumorMeasurement,
        current: TumorMeasurement
    ):
        """
        初始化评估器
        
        Args:
            baseline: 基线测量
            current: 当前测量
        """
        self.baseline = baseline
        self.current = current
    
    def evaluate(self) -> Dict:
        """
        评估疗效
        
        Returns:
            Dict: 评估结果
        """
        baseline_sld = self.baseline.sum_longest_diameter
        current_sld = self.current.sum_longest_diameter
        
        # 计算变化百分比
        change_pct = ((current_sld - baseline_sld) / baseline_sld) * 100
        
        # RECIST 1.1 标准
        if current_sld == 0:
            response = ResponseCategory.CR
            response_desc = "完全缓解 - 所有病灶消失"
        elif change_pct <= -30:
            response = ResponseCategory.PR
            response_desc = "部分缓解 - 缩小≥30%"
        elif -30 < change_pct < 20:
            response = ResponseCategory.SD
            response_desc = "疾病稳定 - 变化在 -30% 到 20% 之间"
        else:  # change_pct >= 20
            response = ResponseCategory.PD
            response_desc = "疾病进展 - 增大≥20% 或出现新病灶"
        
        return {
            "response_category": response.value,
            "response_description": response_desc,
            "baseline_sld_mm": baseline_sld,
            "current_sld_mm": current_sld,
            "change_percentage": f"{change_pct:+.1f}%",
            "evaluation_date": self.current.date.isoformat()
        }


class SurvivalAnalyzer:
    """
    生存分析服务
    
    计算：
    - 无病生存期 (DFS)
    - 无进展生存期 (PFS)
    - 总生存期 (OS)
    """
    
    def __init__(self, diagnosis_date: datetime):
        self.diagnosis_date = diagnosis_date
    
    def calculate_dfs(self, last_followup_date: datetime, recurrence: bool) -> Dict:
        """
        计算无病生存期
        
        Args:
            last_followup_date: 最后随访日期
            recurrence: 是否复发
        
        Returns:
            Dict: DFS 数据
        """
        dfs_months = (last_followup_date - self.diagnosis_date).days / 30
        
        return {
            "dfs_months": round(dfs_months, 1),
            "dfs_years": round(dfs_months / 12, 1),
            "recurrence": recurrence,
            "disease_free": not recurrence
        }
    
    def calculate_pfs(self, progression_date: Optional[datetime]) -> Optional[Dict]:
        """
        计算无进展生存期
        
        Args:
            progression_date: 疾病进展日期
        
        Returns:
            Dict: PFS 数据或 None
        """
        if not progression_date:
            return None
        
        pfs_months = (progression_date - self.diagnosis_date).days / 30
        
        return {
            "pfs_months": round(pfs_months, 1),
            "progression_date": progression_date.isoformat()
        }
    
    def predict_survival(
        self,
        molecular_subtype: str,
        tnm_stage: str,
        age: int
    ) -> Dict:
        """
        预测生存率
        
        基于 SEER 数据库和中国临床数据
        
        Args:
            molecular_subtype: 分子分型
            tnm_stage: TNM 分期
            age: 年龄
        
        Returns:
            Dict: 生存率预测
        """
        # 基础生存率 (5 年 OS)
        base_survival = {
            ("Luminal A", "I"): 0.98,
            ("Luminal A", "II"): 0.95,
            ("Luminal A", "III"): 0.88,
            ("Luminal A", "IV"): 0.65,
            ("Luminal B", "I"): 0.96,
            ("Luminal B", "II"): 0.92,
            ("Luminal B", "III"): 0.82,
            ("Luminal B", "IV"): 0.55,
            ("HER2-enriched", "I"): 0.94,
            ("HER2-enriched", "II"): 0.88,
            ("HER2-enriched", "III"): 0.75,
            ("HER2-enriched", "IV"): 0.45,
            ("Basal-like", "I"): 0.90,
            ("Basal-like", "II"): 0.82,
            ("Basal-like", "III"): 0.65,
            ("Basal-like", "IV"): 0.30,
        }
        
        key = (molecular_subtype, tnm_stage)
        survival_rate = base_survival.get(key, 0.70)
        
        # 年龄调整
        if age < 40:
            survival_rate *= 0.95  # 年轻患者预后稍差
        elif age > 70:
            survival_rate *= 0.90  # 老年患者预后稍差
        
        return {
            "molecular_subtype": molecular_subtype,
            "tnm_stage": tnm_stage,
            "predicted_5yr_os": f"{survival_rate*100:.1f}%",
            "predicted_10yr_os": f"{survival_rate*0.9*100:.1f}%",
            "risk_factors": self._get_risk_factors(molecular_subtype, age)
        }
    
    def _get_risk_factors(self, subtype: str, age: int) -> List[str]:
        """获取风险因素"""
        factors = []
        
        if subtype == "Basal-like":
            factors.append("三阴性预后较差")
        elif subtype == "HER2-enriched":
            factors.append("HER2 阳性，建议靶向治疗")
        
        if age < 40:
            factors.append("年轻患者 (<40 岁)")
        elif age > 70:
            factors.append("老年患者 (>70 岁)")
        
        return factors
