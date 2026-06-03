"""
工作流优化服务

提供:
1. 历史检查对比
2. 病灶生长追踪
3. 随访计划自动生成
4. 提醒通知
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np


class FollowUpPriority(str, Enum):
    """随访优先级"""
    ROUTINE = "routine"       # 常规随访 (年度)
    SHORT_TERM = "short"      # 短期随访 (3-6 个月)
    URGENT = "urgent"         # 紧急随访 (1-2 个月)
    IMMEDIATE = "immediate"   # 立即处理


class FollowUpStatus(str, Enum):
    """随访状态"""
    SCHEDULED = "scheduled"   # 已安排
    COMPLETED = "completed"   # 已完成
    OVERDUE = "overdue"       # 已逾期
    CANCELLED = "cancelled"   # 已取消


@dataclass
class FollowUpPlan:
    """随访计划"""
    plan_id: str
    patient_id: int
    lesion_id: int
    priority: FollowUpPriority
    recommended_date: datetime
    latest_date: datetime  # 最晚随访日期
    followUp_type: str     # 超声/MRI/钼靶
    reason: str
    birads_category: str
    status: FollowUpStatus = FollowUpStatus.SCHEDULED
    previous_changes: List[Dict] = field(default_factory=list)
    notes: str = ""


@dataclass
class ComparisonResult:
    """对比结果"""
    lesion_id: int
    comparison_date: datetime
    previous_exam: Dict
    current_exam: Dict
    size_change_mm: float
    size_change_percent: float
    volume_change_percent: float
    birads_change: Optional[str]  # BI-RADS 变化
    new_features: List[str]       # 新出现的征象
    disappeared_features: List[str]  # 消失的征象
    growth_rate_mm_per_month: float
    doubling_time_days: Optional[float]  # 倍增时间
    assessment: str  # 稳定性评估
    recommendation: str


class WorkflowOptimizer:
    """
    工作流优化服务
    
    功能:
    1. 历史检查一键对比
    2. 病灶生长自动分析
    3. 随访计划智能生成
    4. 逾期随访提醒
    """
    
    # BI-RADS 分级对应的随访间隔 (月)
    BIRADS_FOLLOWUP_INTERVALS = {
        '1': 12,   # 年度筛查
        '2': 12,   # 年度随访
        '3': 6,    # 6 个月短期随访
        '4A': 2,   # 2 个月内处理
        '4B': 1,   # 1 个月内处理
        '4C': 1,   # 1 个月内处理
        '5': 1,    # 立即处理
        '6': 1,    # 治疗中随访
    }
    
    # 必须紧急处理的情况
    URGENT_CONDITIONS = {
        '快速生长': 20,  # >20mm/月
        '体积倍增': 180,  # <180 天翻倍
        '分级升级': True,  # BI-RADS 升级
    }
    
    def __init__(self):
        """初始化工作流优化器"""
        self.followUp_plans: List[FollowUpPlan] = []
    
    def compare_examinations(
        self,
        current_exam: Dict,
        previous_exam: Dict,
        days_interval: int
    ) -> ComparisonResult:
        """
        对比两次检查
        
        Args:
            current_exam: 当前检查数据
            previous_exam: 历史检查数据
            days_interval: 间隔天数
        
        Returns:
            ComparisonResult: 对比结果
        """
        # 1. 提取病灶信息
        current_lesion = current_exam.get('lesion', {})
        previous_lesion = previous_exam.get('lesion', {})
        
        # 2. 计算大小变化
        current_size = self._extract_size(current_lesion)
        previous_size = self._extract_size(previous_lesion)
        
        size_change_mm = current_size - previous_size
        size_change_percent = (size_change_mm / previous_size * 100) if previous_size > 0 else 0
        
        # 3. 计算体积变化 (假设椭球体)
        current_volume = self._calculate_volume(current_lesion)
        previous_volume = self._calculate_volume(previous_lesion)
        volume_change_percent = ((current_volume - previous_volume) / previous_volume * 100) if previous_volume > 0 else 0
        
        # 4. 计算生长速度
        months_interval = days_interval / 30.44
        growth_rate = size_change_mm / months_interval if months_interval > 0 else 0
        
        # 5. 计算倍增时间
        doubling_time = self._calculate_doubling_time(size_change_percent, months_interval)
        
        # 6. BI-RADS 变化
        birads_change = self._compare_birads(
            previous_lesion.get('birads_category'),
            current_lesion.get('birads_category')
        )
        
        # 7. 征象变化
        new_features, disappeared = self._compare_features(
            previous_lesion.get('features', {}),
            current_lesion.get('features', {})
        )
        
        # 8. 稳定性评估
        assessment = self._assess_stability(
            size_change_percent,
            growth_rate,
            birads_change,
            new_features
        )
        
        # 9. 生成建议
        recommendation = self._generate_comparison_recommendation(
            assessment,
            current_lesion.get('birads_category'),
            growth_rate,
            new_features
        )
        
        return ComparisonResult(
            lesion_id=current_lesion.get('id', 0),
            comparison_date=datetime.now(),
            previous_exam={
                'exam_date': previous_exam.get('exam_date'),
                'size_mm': previous_size,
                'volume_mm3': previous_volume,
                'birads': previous_lesion.get('birads_category')
            },
            current_exam={
                'exam_date': current_exam.get('exam_date'),
                'size_mm': current_size,
                'volume_mm3': current_volume,
                'birads': current_lesion.get('birads_category')
            },
            size_change_mm=size_change_mm,
            size_change_percent=size_change_percent,
            volume_change_percent=volume_change_percent,
            birads_change=birads_change,
            new_features=new_features,
            disappeared_features=disappeared,
            growth_rate_mm_per_month=growth_rate,
            doubling_time_days=doubling_time,
            assessment=assessment,
            recommendation=recommendation
        )
    
    def _extract_size(self, lesion: Dict) -> float:
        """提取病灶大小 (长径)"""
        dimensions = lesion.get('dimensions', {})
        return max(
            dimensions.get('length', 0),
            dimensions.get('width', 0),
            dimensions.get('height', 0)
        )
    
    def _calculate_volume(self, lesion: Dict) -> float:
        """
        计算病灶体积 (椭球体公式)
        
        V = 4/3 × π × (长/2) × (宽/2) × (高/2)
        """
        dimensions = lesion.get('dimensions', {})
        l = dimensions.get('length', 0) / 2
        w = dimensions.get('width', 0) / 2
        h = dimensions.get('height', 0) / 2
        
        if l == 0 or w == 0 or h == 0:
            return 0
        
        volume = (4.0 / 3.0) * np.pi * l * w * h
        return volume
    
    def _calculate_doubling_time(
        self,
        size_change_percent: float,
        months_interval: float
    ) -> Optional[float]:
        """
        计算体积倍增时间
        
        基于指数生长模型:
        Doubling Time = ln(2) / growth_rate
        
        Returns:
            float: 倍增时间 (天), None 表示无法计算
        """
        if size_change_percent <= 0 or months_interval <= 0:
            return None
        
        # 月度生长率
        monthly_growth_rate = size_change_percent / months_interval
        
        # 倍增时间 (月)
        if monthly_growth_rate > 0:
            doubling_months = np.log(2) / np.log(1 + monthly_growth_rate / 100)
            return doubling_months * 30.44  # 转换为天
        
        return None
    
    def _compare_birads(
        self,
        previous_birads: Optional[str],
        current_birads: Optional[str]
    ) -> Optional[str]:
        """比较 BI-RADS 分级变化"""
        if not previous_birads or not current_birads:
            return None
        
        birads_order = ['1', '2', '3', '4A', '4B', '4C', '5', '6']
        
        try:
            prev_idx = birads_order.index(previous_birads)
            curr_idx = birads_order.index(current_birads)
            
            if curr_idx > prev_idx:
                diff = curr_idx - prev_idx
                return f"升级 {prev_idx}→{curr_idx} (+{diff}级)"
            elif curr_idx < prev_idx:
                diff = prev_idx - curr_idx
                return f"降级 {prev_idx}→{curr_idx} (-{diff}级)"
            else:
                return "无变化"
        except ValueError:
            return None
    
    def _compare_features(
        self,
        previous_features: Dict,
        current_features: Dict
    ) -> Tuple[List[str], List[str]]:
        """
        比较征象变化
        
        Returns:
            (new_features, disappeared_features)
        """
        new_features = []
        disappeared = []
        
        # 特征映射
        feature_names = {
            'irregular_shape': '不规则形',
            'taller_than_wide': '纵横比>1',
            'spiculated_margin': '毛刺状边缘',
            'microlobulated_margin': '微小分叶',
            'indistinct_margin': '边界不清',
            'marked_hypoechoic': '明显低回声',
            'heterogeneous_echo': '回声不均匀',
            'fine_calcification': '细小钙化',
            'rich_vascularity': '血流丰富',
            'posterior_shadowing': '后方回声衰减',
        }
        
        for feature, name in feature_names.items():
            prev_value = previous_features.get(feature, False)
            curr_value = current_features.get(feature, False)
            
            if curr_value and not prev_value:
                new_features.append(name)
            elif prev_value and not curr_value:
                disappeared.append(name)
        
        return new_features, disappeared
    
    def _assess_stability(
        self,
        size_change_percent: float,
        growth_rate: float,
        birads_change: Optional[str],
        new_features: List[str]
    ) -> str:
        """评估病灶稳定性"""
        #  RECIST 1.1 标准
        if size_change_percent <= -30:
            size_status = "显著缩小"
        elif size_change_percent <= -5:
            size_status = "缩小"
        elif size_change_percent <= 20:
            size_status = "稳定"
        else:
            size_status = "增大"
        
        # 生长速度评估
        if growth_rate > 20:
            growth_status = "快速生长"
        elif growth_rate > 10:
            growth_status = "中等生长"
        elif growth_rate > 2:
            growth_status = "缓慢生长"
        else:
            growth_status = "基本稳定"
        
        # 综合评估
        if birads_change and "升级" in birads_change:
            return "进展"
        elif new_features:
            return f"进展 (新增：{', '.join(new_features)})"
        elif growth_rate > 20:
            return "快速进展"
        elif size_change_percent > 20:
            return "增大"
        elif size_change_percent < -30:
            return "显著缓解"
        elif abs(size_change_percent) <= 20:
            return "稳定"
        else:
            return size_status
    
    def _generate_comparison_recommendation(
        self,
        assessment: str,
        current_birads: str,
        growth_rate: float,
        new_features: List[str]
    ) -> str:
        """生成对比后建议"""
        recommendations = []
        
        # 基于稳定性
        if "进展" in assessment:
            recommendations.append("病灶进展，建议尽快处理")
        elif "显著缓解" in assessment:
            recommendations.append("治疗有效，继续随访")
        elif "稳定" in assessment:
            recommendations.append("病灶稳定，按计划随访")
        
        # 基于生长速度
        if growth_rate > 20:
            recommendations.append("⚠️ 快速生长，建议穿刺活检")
        elif growth_rate > 10:
            recommendations.append("生长较快，建议密切随访")
        
        # 基于新征象
        if '毛刺状边缘' in new_features:
            recommendations.append("新出现毛刺征，恶性风险增加")
        if '纵横比>1' in new_features:
            recommendations.append("新出现纵横比>1，建议高度重视")
        if '细小钙化' in new_features:
            recommendations.append("新出现钙化，建议进一步评估")
        
        # 基于 BI-RADS
        if current_birads in ['4B', '4C', '5']:
            recommendations.append(f"BI-RADS {current_birads}类，建议穿刺活检")
        elif current_birads == '3':
            recommendations.append("BI-RADS 3 类，建议 6 个月短期随访")
        
        return "; ".join(recommendations) if recommendations else "继续常规随访"
    
    def generate_followup_plan(
        self,
        patient_id: int,
        lesion_id: int,
        birads_category: str,
        exam_date: datetime = None,
        special_conditions: Dict = None
    ) -> FollowUpPlan:
        """
        自动生成随访计划
        
        Args:
            patient_id: 患者 ID
            lesion_id: 病灶 ID
            birads_category: BI-RADS 分级
            exam_date: 检查日期
            special_conditions: 特殊情况 (生长速度/倍增时间等)
        
        Returns:
            FollowUpPlan: 随访计划
        """
        if exam_date is None:
            exam_date = datetime.now()
        
        # 1. 确定基础随访间隔
        base_interval = self.BIRADS_FOLLOWUP_INTERVALS.get(birads_category, 6)
        
        # 2. 根据特殊情况调整
        if special_conditions:
            # 快速生长
            growth_rate = special_conditions.get('growth_rate', 0)
            if growth_rate > 20:
                base_interval = min(base_interval, 1)
            
            # 短倍增时间
            doubling_time = special_conditions.get('doubling_time', float('inf'))
            if doubling_time and doubling_time < 180:
                base_interval = min(base_interval, 2)
            
            # 新征象出现
            if special_conditions.get('new_features'):
                base_interval = max(1, base_interval - 1)
        
        # 3. 确定优先级
        if base_interval <= 1:
            priority = FollowUpPriority.IMMEDIATE
        elif base_interval <= 2:
            priority = FollowUpPriority.URGENT
        elif base_interval <= 6:
            priority = FollowUpPriority.SHORT_TERM
        else:
            priority = FollowUpPriority.ROUTINE
        
        # 4. 确定随访类型
        if birads_category in ['4A', '4B', '4C', '5']:
            followup_type = "穿刺活检"
            reason = f"BI-RADS {birads_category}类，需病理确诊"
        elif birads_category == '3':
            followup_type = "超声随访"
            reason = "BI-RADS 3 类，短期随访观察稳定性"
        elif birads_category == '2':
            followup_type = "超声随访"
            reason = "良性病变，年度随访"
        else:
            followup_type = "超声随访"
            reason = "常规筛查"
        
        # 5. 创建随访计划
        recommended_date = exam_date + timedelta(days=base_interval * 30)
        latest_date = recommended_date + timedelta(days=15)  # 允许推迟 15 天
        
        plan_id = f"FU{exam_date.strftime('%Y%m%d')}_{patient_id}_{lesion_id}"
        
        plan = FollowUpPlan(
            plan_id=plan_id,
            patient_id=patient_id,
            lesion_id=lesion_id,
            priority=priority,
            recommended_date=recommended_date,
            latest_date=latest_date,
            followUp_type=followup_type,
            reason=reason,
            birads_category=birads_category
        )
        
        self.followUp_plans.append(plan)
        return plan
    
    def get_overdue_followups(self, patient_id: int = None) -> List[FollowUpPlan]:
        """
        获取逾期随访计划
        
        Args:
            patient_id: 患者 ID (可选，为 None 时返回所有)
        
        Returns:
            List[FollowUpPlan]: 逾期随访列表
        """
        today = datetime.now()
        overdue = []
        
        for plan in self.followUp_plans:
            if plan.status != FollowUpStatus.SCHEDULED:
                continue
            
            if patient_id and plan.patient_id != patient_id:
                continue
            
            if today > plan.latest_date:
                plan.status = FollowUpStatus.OVERDUE
                overdue.append(plan)
        
        return overdue
    
    def get_followup_reminders(self, days_ahead: int = 7) -> List[FollowUpPlan]:
        """
        获取即将到期的随访提醒
        
        Args:
            days_ahead: 提前提醒天数
        
        Returns:
            List[FollowUpPlan]: 即将到期的随访
        """
        today = datetime.now()
        reminder_date = today + timedelta(days=days_ahead)
        reminders = []
        
        for plan in self.followUp_plans:
            if plan.status != FollowUpStatus.SCHEDULED:
                continue
            
            if today <= plan.recommended_date <= reminder_date:
                reminders.append(plan)
        
        # 按优先级排序
        priority_order = {
            FollowUpPriority.IMMEDIATE: 0,
            FollowUpPriority.URGENT: 1,
            FollowUpPriority.SHORT_TERM: 2,
            FollowUpPriority.ROUTINE: 3,
        }
        
        reminders.sort(key=lambda p: priority_order[p.priority])
        
        return reminders
    
    def get_patient_followup_history(
        self,
        patient_id: int,
        lesion_id: int = None
    ) -> List[Dict]:
        """
        获取患者随访历史
        
        Args:
            patient_id: 患者 ID
            lesion_id: 病灶 ID (可选)
        
        Returns:
            List[Dict]: 随访历史摘要
        """
        history = []
        
        for plan in self.followUp_plans:
            if plan.patient_id != patient_id:
                continue
            
            if lesion_id and plan.lesion_id != lesion_id:
                continue
            
            history.append({
                'plan_id': plan.plan_id,
                'lesion_id': plan.lesion_id,
                'priority': plan.priority.value,
                'recommended_date': plan.recommended_date.isoformat(),
                'followup_type': plan.followUp_type,
                'status': plan.status.value,
                'birads_category': plan.birads_category
            })
        
        # 按日期排序 (最近在前)
        history.sort(key=lambda x: x['recommended_date'], reverse=True)
        
        return history
