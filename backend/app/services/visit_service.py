from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Tuple, List, Optional
from datetime import datetime, timedelta
import random
import string

from app.models.visit import Visit
from app.schemas.visit import VisitCreate, VisitUpdate, RiskAssessmentRequest
from app.models.patient import Patient


class VisitService:
    """随访服务层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: VisitCreate) -> Visit:
        """创建随访记录"""
        visit_no = await self._generate_visit_no()
        
        visit = Visit(
            visit_no=visit_no,
            **data.model_dump()
        )
        
        self.db.add(visit)
        await self.db.commit()
        await self.db.refresh(visit)
        
        return visit
    
    async def get(self, visit_id: int) -> Optional[Visit]:
        """获取随访记录"""
        result = await self.db.execute(
            select(Visit).where(Visit.id == visit_id)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        patient_id: Optional[int] = None,
        visit_type: Optional[str] = None
    ) -> Tuple[List[Visit], int]:
        """获取随访列表"""
        stmt = select(Visit)
        count_stmt = select(func.count(Visit.id))
        
        if patient_id:
            stmt = stmt.where(Visit.patient_id == patient_id)
            count_stmt = count_stmt.where(Visit.patient_id == patient_id)
        
        if visit_type:
            stmt = stmt.where(Visit.visit_type == visit_type)
            count_stmt = count_stmt.where(Visit.visit_type == visit_type)
        
        # 分页
        offset = (page - 1) * page_size
        stmt = stmt.order_by(Visit.visit_date.desc()).offset(offset).limit(page_size)
        
        result = await self.db.execute(stmt)
        visits = result.scalars().all()
        
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        return visits, total
    
    async def update(self, visit_id: int, data: VisitUpdate) -> Visit:
        """更新随访记录"""
        visit = await self.get(visit_id)
        if not visit:
            raise ValueError(f"Visit {visit_id} not found")
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(visit, key, value)
        
        visit.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(visit)
        
        return visit
    
    async def assess_risk(self, visit_id: int, assessment: RiskAssessmentRequest) -> dict:
        """风险评估"""
        # 风险评分逻辑
        risk_score = 0.0
        risk_factors = []
        
        # BI-RADS 分级权重
        birads_weights = {
            '1': 0.0, '2': 0.1, '3': 0.3,
            '4A': 0.5, '4B': 0.7, '4C': 0.85, '5': 0.95
        }
        birads_score = birads_weights.get(assessment.birads_category, 0.3)
        risk_score += birads_score * 0.4
        risk_factors.append({
            "factor": f"BI-RADS {assessment.birads_category}类",
            "weight": 0.4,
            "score": birads_score
        })
        
        # 体质权重
        if assessment.constitution in ['气郁质', '血瘀质', '痰湿质']:
            risk_score += 0.25
            risk_factors.append({
                "factor": f"{assessment.constitution}",
                "weight": 0.25,
                "score": 0.25
            })
        
        # 症状权重
        if len(assessment.symptoms) > 2:
            risk_score += 0.15
            risk_factors.append({
                "factor": "症状明显",
                "weight": 0.15,
                "score": 0.15
            })
        
        # 家族史
        if assessment.family_history:
            risk_score += 0.2
            risk_factors.append({
                "factor": "家族史",
                "weight": 0.2,
                "score": 0.2
            })
        
        # 风险等级判定
        if risk_score < 0.25:
            risk_level = "low"
            recommendation = "常规随访，12 个月复查"
        elif risk_score < 0.45:
            risk_level = "medium"
            recommendation = "3-6 个月随访，建议中医干预"
        elif risk_score < 0.65:
            risk_level = "high"
            recommendation = "3 个月随访，穿刺活检"
        else:
            risk_level = "very_high"
            recommendation = "立即转诊，多学科会诊"
        
        # 更新随访记录
        visit = await self.get(visit_id)
        if visit:
            visit.risk_level = risk_level
            visit.risk_factors = risk_factors
            await self.db.commit()
        
        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 2),
            "risk_factors": risk_factors,
            "recommendation": recommendation
        }
    
    async def generate_followup_plan(self, visit_id: int) -> dict:
        """生成随访计划"""
        visit = await self.get(visit_id)
        if not visit:
            raise ValueError(f"Visit {visit_id} not found")
        
        # 根据风险等级确定随访间隔
        interval_map = {
            "low": 12,
            "medium": 6,
            "high": 3,
            "very_high": 1
        }
        
        interval_months = interval_map.get(visit.risk_level or "medium", 6)
        next_visit = visit.visit_date + timedelta(days=interval_months * 30)
        reminder_date = next_visit - timedelta(days=7)
        
        # 随访项目
        items_map = {
            "low": ["ultrasound", "clinical_exam"],
            "medium": ["ultrasound", "mammography", "clinical_exam"],
            "high": ["ultrasound", "mammography", "tumor_markers", "clinical_exam"],
            "very_high": ["ultrasound", "mri", "tumor_markers", "mdt_consultation"]
        }
        
        scheduled_items = items_map.get(visit.risk_level or "medium", [])
        
        return {
            "next_visit_date": next_visit.isoformat(),
            "reminder_date": reminder_date.isoformat(),
            "interval_months": interval_months,
            "scheduled_items": scheduled_items,
            "risk_level": visit.risk_level
        }
    
    async def _generate_visit_no(self) -> str:
        """生成随访编号"""
        today = datetime.now().strftime('%Y%m%d')
        prefix = f"V{today}"
        
        count_stmt = select(func.count(Visit.id)).where(
            Visit.visit_no.like(f"{prefix}%")
        )
        result = await self.db.execute(count_stmt)
        count = result.scalar() or 0
        
        return f"{prefix}{count + 1:04d}"
