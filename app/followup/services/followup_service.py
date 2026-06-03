"""
随访管理服务

支持：
- 随访计划生成
- 随访提醒
- 疗效评估
- 复发风险预测
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_


class FollowupType(str, Enum):
    """随访类型"""
    ROUTINE = "routine"          # 常规随访
    SHORT_TERM = "short_term"    # 短期随访 (3-6 个月)
    POST_OP = "post_op"          # 术后随访
    CHEMO = "chemo"              # 化疗期间随访
    ENDOCRINE = "endocrine"      # 内分泌治疗随访


class FollowupStatus(str, Enum):
    """随访状态"""
    PENDING = "pending"          # 待随访
    COMPLETED = "completed"      # 已完成
    OVERDUE = "overdue"          # 已逾期
    CANCELLED = "cancelled"      # 已取消


@dataclass
class FollowupPlan:
    """随访计划"""
    patient_id: int
    diagnosis_id: int
    followup_type: FollowupType
    interval_months: int
    next_followup_date: datetime
    examination_items: List[str]
    notes: str


class FollowupService:
    """
    随访管理服务
    
    功能：
    1. 自动生成随访计划
    2. 随访提醒
    3. 疗效评估
    4. 复发风险预测
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_followup_plan(
        self,
        patient_id: int,
        diagnosis_id: int,
        birads_category: str,
        pathology_type: Optional[str] = None,
        treatment_type: Optional[str] = None
    ) -> FollowupPlan:
        """
        自动生成随访计划
        
        Args:
            patient_id: 患者 ID
            diagnosis_id: 诊断 ID
            birads_category: BI-RADS 分级
            pathology_type: 病理类型
            treatment_type: 治疗类型
        
        Returns:
            FollowupPlan: 随访计划
        """
        # 根据 BI-RADS 分级确定随访间隔
        followup_config = self._get_followup_config(
            birads_category,
            pathology_type,
            treatment_type
        )
        
        # 计算下次随访日期
        next_date = datetime.utcnow() + timedelta(
            days=followup_config['interval_days']
        )
        
        return FollowupPlan(
            patient_id=patient_id,
            diagnosis_id=diagnosis_id,
            followup_type=followup_config['type'],
            interval_months=followup_config['interval_days'] // 30,
            next_followup_date=next_date,
            examination_items=followup_config['examinations'],
            notes=followup_config['notes']
        )
    
    def _get_followup_config(
        self,
        birads: str,
        pathology: Optional[str],
        treatment: Optional[str]
    ) -> Dict:
        """
        获取随访配置
        
        基于 NCCN 和中国抗癌协会指南
        """
        # BI-RADS 2-3 类 (良性/可能良性)
        if birads in ["2", "3"]:
            return {
                "type": FollowupType.ROUTINE,
                "interval_days": 180,  # 6 个月
                "examinations": ["乳腺超声", "临床体检"],
                "notes": "常规随访，观察病灶变化"
            }
        
        # BI-RADS 4A (低度可疑)
        elif birads == "4A":
            return {
                "type": FollowupType.SHORT_TERM,
                "interval_days": 90,  # 3 个月
                "examinations": ["乳腺超声", "钼靶", "肿瘤标志物"],
                "notes": "短期密切随访，建议穿刺活检"
            }
        
        # BI-RADS 4B-5 (可疑/高度可疑恶性)
        elif birads in ["4B", "4C", "5"]:
            if pathology and "浸润性" in pathology:
                # 已确诊恶性
                return self._get_post_cancer_config(treatment)
            else:
                # 待确诊
                return {
                    "type": FollowupType.SHORT_TERM,
                    "interval_days": 30,  # 1 个月
                    "examinations": ["穿刺活检", "乳腺超声", "钼靶"],
                    "notes": "尽快明确诊断"
                }
        
        # 默认
        return {
            "type": FollowupType.ROUTINE,
            "interval_days": 365,
            "examinations": ["乳腺超声"],
            "notes": "常规年度体检"
        }
    
    def _get_post_cancer_config(self, treatment: Optional[str]) -> Dict:
        """
        乳腺癌术后随访配置
        
        基于 NCCN 指南
        """
        if treatment == "endocrine":
            return {
                "type": FollowupType.ENDOCRINE,
                "interval_days": 90,
                "examinations": [
                    "乳腺超声",
                    "妇科超声 (他莫昔芬监测)",
                    "骨密度 (芳香化酶抑制剂)"
                ],
                "notes": "内分泌治疗期间定期随访"
            }
        elif treatment == "chemo":
            return {
                "type": FollowupType.CHEMO,
                "interval_days": 21,
                "examinations": [
                    "血常规",
                    "肝肾功能",
                    "心脏超声 (蒽环类)"
                ],
                "notes": "化疗期间每周期随访"
            }
        else:
            # 术后常规
            return {
                "type": FollowupType.POST_OP,
                "interval_days": 90,
                "examinations": [
                    "乳腺超声",
                    "钼靶 (年度)",
                    "肿瘤标志物"
                ],
                "notes": "术后定期复查，监测复发"
            }
    
    async def get_overdue_followups(self, days: int = 7) -> List:
        """
        获取逾期随访列表
        
        Args:
            days: 逾期天数阈值
        
        Returns:
            List: 逾期随访列表
        """
        from app.followup.models.followup_model import Followup
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(Followup).where(
                and_(
                    Followup.status == FollowupStatus.PENDING,
                    Followup.scheduled_date < cutoff_date
                )
            )
        )
        
        return result.scalars().all()
    
    async def calculate_recurrence_risk(
        self,
        patient_id: int,
        molecular_subtype: str,
        tnm_stage: str,
        treatment_completed: bool
    ) -> Dict:
        """
        计算复发风险
        
        基于分子分型和 TNM 分期
        
        Args:
            patient_id: 患者 ID
            molecular_subtype: 分子分型
            tnm_stage: TNM 分期
            treatment_completed: 治疗是否完成
        
        Returns:
            Dict: 风险评估
        """
        # 基础风险 (基于分子分型)
        subtype_risk = {
            "Luminal A": 0.15,      # 15%
            "Luminal B": 0.25,      # 25%
            "HER2-enriched": 0.35,  # 35%
            "Basal-like": 0.45,     # 45%
        }
        
        base_risk = subtype_risk.get(molecular_subtype, 0.25)
        
        # 分期调整
        stage_multiplier = {
            "I": 0.5,
            "II": 1.0,
            "III": 2.0,
            "IV": 4.0,
        }
        
        risk = base_risk * stage_multiplier.get(tnm_stage, 1.0)
        
        # 治疗完成调整
        if treatment_completed:
            risk *= 0.7  # 完成治疗降低 30% 风险
        
        # 风险分级
        if risk < 0.15:
            risk_level = "低危"
            recommendation = "常规随访，每 6-12 个月"
        elif risk < 0.30:
            risk_level = "中危"
            recommendation = "密切随访，每 3-6 个月"
        else:
            risk_level = "高危"
            recommendation = "强化随访，每 1-3 个月，考虑强化治疗"
        
        return {
            "recurrence_risk": risk,
            "risk_percentage": f"{risk*100:.1f}%",
            "risk_level": risk_level,
            "5year_dfs": f"{(1-risk)*100:.1f}%",
            "recommendation": recommendation
        }
