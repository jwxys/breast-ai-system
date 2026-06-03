"""
病灶动态追踪服务

监测病灶随时间的变化:
1. 大小变化 (RECIST 1.1 标准)
2. 形态演变
3. 生长速度评估
4. 治疗反应评估
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class GrowthRate(str, Enum):
    """生长速度"""
    REGRESSING = "regressing"  # 退缩
    STABLE = "stable"  # 稳定
    SLOW_GROWTH = "slow_growth"  # 缓慢生长
    MODERATE_GROWTH = "moderate_growth"  # 中等生长
    RAPID_GROWTH = "rapid_growth"  # 快速生长


class TreatmentResponse(str, Enum):
    """治疗反应"""
    CR = "CR"  # 完全缓解
    PR = "PR"  # 部分缓解
    SD = "SD"  # 疾病稳定
    PD = "PD"  # 疾病进展


@dataclass
class LesionMeasurement:
    """病灶测量数据"""
    date: datetime
    longest_diameter_mm: float  # 最长径 (RECIST)
    short_axis_mm: Optional[float]  # 短轴
    area_mm2: Optional[float]  # 面积
    volume_mm3: Optional[float]  # 体积
    birads_category: str
    notes: Optional[str]


@dataclass
class GrowthAnalysis:
    """生长分析结果"""
    growth_rate: GrowthRate
    doubling_time_days: Optional[int]  # 倍增时间
    size_change_percent: float  # 大小变化%
    velocity_mm_per_month: float  # 生长速度 mm/月
    volume_change_percent: Optional[float]  # 体积变化%
    morphological_changes: List[str]  # 形态变化


@dataclass
class TreatmentResponseAssessment:
    """治疗反应评估"""
    response: TreatmentResponse
    target_lesion_change: float  # 靶病灶变化%
    summary_stage: str  # 总体分期
    recommendation: str


class LesionTracker:
    """
    病灶动态追踪器
    
    基于 RECIST 1.1 标准评估病灶变化
    """
    
    # RECIST 1.1 评估阈值
    RECIST_THRESHOLDS = {
        "PR": -30,  # 缩小≥30%
        "PD": 20,  # 增大≥20% 且绝对值增加≥5mm
        "SD_min": -30,  # 稳定下限
        "SD_max": 20,  # 稳定上限
    }
    
    # 生长速度分级阈值
    GROWTH_THRESHOLDS = {
        "rapid": 20,  # >20mm/月
        "moderate": 10,  # 10-20mm/月
        "slow": 2,  # 2-10mm/月
        "stable": 2,  # <2mm/月
    }
    
    # 倍增时间计算常数
    DOUBLING_TIME_FACTOR = 0.693  # ln(2)
    
    @classmethod
    def analyze_growth(
        cls,
        measurements: List[LesionMeasurement]
    ) -> GrowthAnalysis:
        """
        分析病灶生长情况
        
        Args:
            measurements: 按时间排序的测量列表
        
        Returns:
            GrowthAnalysis: 生长分析结果
        """
        if len(measurements) < 2:
            return cls._create_empty_growth_analysis()
        
        # 获取首尾测量
        first = measurements[0]
        last = measurements[-1]
        
        # 计算时间间隔 (天)
        time_diff = (last.date - first.date).days
        if time_diff <= 0:
            return cls._create_empty_growth_analysis()
        
        # 计算大小变化
        size_change = last.longest_diameter_mm - first.longest_diameter_mm
        size_change_percent = (size_change / first.longest_diameter_mm * 100) if first.longest_diameter_mm > 0 else 0
        
        # 计算生长速度 (mm/月)
        velocity = (size_change / time_diff) * 30.44  # 平均每月天数
        
        # 确定生长速度分级
        growth_rate = cls._determine_growth_rate(velocity, size_change_percent)
        
        # 计算倍增时间
        doubling_time = cls._calculate_doubling_time(
            first.longest_diameter_mm,
            last.longest_diameter_mm,
            time_diff
        )
        
        # 计算体积变化 (如果有体积数据)
        volume_change = None
        if first.volume_mm3 and last.volume_mm3 and first.volume_mm3 > 0:
            volume_change = (last.volume_mm3 - first.volume_mm3) / first.volume_mm3 * 100
        
        # 识别形态变化
        morphological_changes = cls._identify_morphological_changes(measurements)
        
        return GrowthAnalysis(
            growth_rate=growth_rate,
            doubling_time_days=doubling_time,
            size_change_percent=round(size_change_percent, 1),
            velocity_mm_per_month=round(velocity, 2),
            volume_change_percent=round(volume_change, 1) if volume_change else None,
            morphological_changes=morphological_changes
        )
    
    @classmethod
    def assess_treatment_response(
        cls,
        baseline: LesionMeasurement,
        follow_up: LesionMeasurement,
        target_lesions: Optional[List[Dict]] = None
    ) -> TreatmentResponseAssessment:
        """
        评估治疗反应 (RECIST 1.1)
        
        Args:
            baseline: 基线测量
            follow_up: 随访测量
            target_lesions: 靶病灶列表
        
        Returns:
            TreatmentResponseAssessment: 治疗反应评估
        """
        # 计算靶病灶变化
        if baseline.longest_diameter_mm > 0:
            target_change = (
                follow_up.longest_diameter_mm - baseline.longest_diameter_mm
            ) / baseline.longest_diameter_mm * 100
        else:
            target_change = 0
        
        # 确定治疗反应
        response = cls._determine_response(target_change, baseline, follow_up)
        
        # 生成总结分期
        summary = cls._generate_summary_stage(response, baseline, follow_up)
        
        # 生成建议
        recommendation = cls._generate_treatment_recommendation(response)
        
        return TreatmentResponseAssessment(
            response=response,
            target_lesion_change=round(target_change, 1),
            summary_stage=summary,
            recommendation=recommendation
        )
    
    @classmethod
    def predict_malignancy_risk_from_growth(cls, growth_analysis: GrowthAnalysis) -> float:
        """
        基于生长特征预测恶性风险
        
        Args:
            growth_analysis: 生长分析结果
        
        Returns:
            float: 恶性风险 (0-1)
        """
        risk_score = 0.5  # 基线风险
        
        # 生长速度评分
        if growth_analysis.growth_rate == GrowthRate.RAPID_GROWTH:
            risk_score += 0.3
        elif growth_analysis.growth_rate == GrowthRate.MODERATE_GROWTH:
            risk_score += 0.15
        elif growth_analysis.growth_rate == GrowthRate.STABLE:
            risk_score -= 0.1
        elif growth_analysis.growth_rate == GrowthRate.REGRESSING:
            risk_score -= 0.3
        
        # 倍增时间评分
        if growth_analysis.doubling_time:
            if growth_analysis.doubling_time < 90:  # <3 个月
                risk_score += 0.2
            elif growth_analysis.doubling_time < 180:  # <6 个月
                risk_score += 0.1
            elif growth_analysis.doubling_time > 365:  # >1 年
                risk_score -= 0.15
        
        # 体积变化评分
        if growth_analysis.volume_change_percent:
            if growth_analysis.volume_change_percent > 50:
                risk_score += 0.15
            elif growth_analysis.volume_change_percent < -20:
                risk_score -= 0.2
        
        return max(0.0, min(1.0, risk_score))
    
    @classmethod
    def _determine_growth_rate(cls, velocity: float, change_percent: float) -> GrowthRate:
        """确定生长速度分级"""
        if change_percent < -20:
            return GrowthRate.REGRESSING
        elif abs(velocity) < cls.GROWTH_THRESHOLDS["stable"]:
            return GrowthRate.STABLE
        elif velocity < cls.GROWTH_THRESHOLDS["slow"]:
            return GrowthRate.SLOW_GROWTH
        elif velocity < cls.GROWTH_THRESHOLDS["moderate"]:
            return GrowthRate.MODERATE_GROWTH
        else:
            return GrowthRate.RAPID_GROWTH
    
    @classmethod
    def _calculate_doubling_time(cls, d1: float, d2: float, days: int) -> Optional[int]:
        """
        计算体积倍增时间
        
        假设球体：体积 ∝ 直径³
        """
        if d1 <= 0 or d2 <= 0 or d2 <= d1:
            return None
        
        # 体积比
        volume_ratio = (d2 / d1) ** 3
        
        if volume_ratio <= 1:
            return None
        
        # 倍增时间公式
        doublings = math.log(volume_ratio, 2)
        if doublings <= 0:
            return None
        
        doubling_time = int(days / doublings)
        return doubling_time
    
    @classmethod
    def _determine_response(
        cls,
        change: float,
        baseline: LesionMeasurement,
        follow_up: LesionMeasurement
    ) -> TreatmentResponse:
        """确定治疗反应"""
        abs_change = follow_up.longest_diameter_mm - baseline.longest_diameter_mm
        
        # 完全缓解 (CR): 所有病灶消失
        if follow_up.longest_diameter_mm == 0:
            return TreatmentResponse.CR
        
        # 部分缓解 (PR): 缩小≥30%
        if change <= cls.RECIST_THRESHOLDS["PR"]:
            return TreatmentResponse.PR
        
        # 疾病进展 (PD): 增大≥20% 且绝对值增加≥5mm
        if change >= cls.RECIST_THRESHOLDS["PD"] and abs_change >= 5:
            return TreatmentResponse.PD
        
        # 疾病稳定 (SD)
        return TreatmentResponse.SD
    
    @classmethod
    def _generate_summary_stage(
        cls,
        response: TreatmentResponse,
        baseline: LesionMeasurement,
        follow_up: LesionMeasurement
    ) -> str:
        """生成总结分期"""
        if response == TreatmentResponse.CR:
            return "完全缓解 - 靶病灶消失"
        elif response == TreatmentResponse.PR:
            return f"部分缓解 - 靶病灶缩小{abs(follow_up.longest_diameter_mm - baseline.longest_diameter_mm):.1f}mm"
        elif response == TreatmentResponse.SD:
            change = follow_up.longest_diameter_mm - baseline.longest_diameter_mm
            direction = "增大" if change > 0 else "缩小"
            return f"疾病稳定 - 靶病灶{direction}{abs(change):.1f}mm"
        else:
            return f"疾病进展 - 靶病灶增大{follow_up.longest_diameter_mm - baseline.longest_diameter_mm:.1f}mm"
    
    @classmethod
    def _generate_treatment_recommendation(cls, response: TreatmentResponse) -> str:
        """生成治疗建议"""
        recommendations = {
            TreatmentResponse.CR: "继续当前治疗方案，定期影像学随访",
            TreatmentResponse.PR: "治疗有效，继续当前方案，2-3 个月后复查",
            TreatmentResponse.SD: "疾病稳定，继续监测，如持续稳定>6 个月可考虑调整方案",
            TreatmentResponse.PD: "疾病进展，建议重新评估治疗方案，考虑二线治疗或临床试验",
        }
        return recommendations.get(response, "建议多学科会诊")
    
    @classmethod
    def _create_empty_growth_analysis(cls) -> GrowthAnalysis:
        """创建空的生长分析"""
        return GrowthAnalysis(
            growth_rate=GrowthRate.STABLE,
            doubling_time_days=None,
            size_change_percent=0.0,
            velocity_mm_per_month=0.0,
            volume_change_percent=None,
            morphological_changes=[]
        )
    
    @classmethod
    def _identify_morphological_changes(cls, measurements: List[LesionMeasurement]) -> List[str]:
        """识别形态变化"""
        changes = []
        
        if len(measurements) < 2:
            return changes
        
        first_birads = measurements[0].birads_category
        last_birads = measurements[-1].birads_category
        
        if first_birads != last_birads:
            changes.append(f"BI-RADS 分级变化 ({first_birads}→{last_birads})")
        
        # 检查备注中的形态描述变化
        if measurements[0].notes and measurements[-1].notes:
            if "边界" in measurements[0].notes and "边界" in measurements[-1].notes:
                if measurements[0].notes != measurements[-1].notes:
                    changes.append("边缘特征变化")
        
        return changes


import math
