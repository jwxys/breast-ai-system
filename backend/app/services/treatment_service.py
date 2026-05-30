from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime, timedelta
import random
import string

from app.models.treatment import TreatmentPlan, TCMPrescription
from app.models.diagnosis import Diagnosis
from app.schemas.treatment import (
    TreatmentPlanCreate,
    TreatmentPlanUpdate,
    TCMPrescriptionCreate,
    EfficacyAssessmentRequest
)


class TreatmentService:
    """治疗服务层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: TreatmentPlanCreate) -> TreatmentPlan:
        """创建治疗方案"""
        plan_no = await self._generate_plan_no()
        
        end_date = None
        if data.start_date and data.duration_weeks:
            end_date = data.start_date + timedelta(weeks=data.duration_weeks)
        
        plan = TreatmentPlan(
            plan_no=plan_no,
            **data.model_dump()
        )
        
        if end_date:
            plan.end_date = end_date
        
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        
        return plan
    
    async def get(self, plan_id: int) -> Optional[TreatmentPlan]:
        """获取治疗方案"""
        result = await self.db.execute(
            select(TreatmentPlan).where(TreatmentPlan.id == plan_id)
        )
        return result.scalar_one_or_none()
    
    async def update(self, plan_id: int, data: TreatmentPlanUpdate) -> TreatmentPlan:
        """更新治疗方案"""
        result = await self.db.execute(
            select(TreatmentPlan).where(TreatmentPlan.id == plan_id)
        )
        plan = result.scalar_one_or_none()
        
        if not plan:
            raise ValueError(f"TreatmentPlan {plan_id} not found")
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(plan, key, value)
        
        plan.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(plan)
        
        return plan
    
    async def assess_efficacy(
        self, 
        plan_id: int, 
        assessment: EfficacyAssessmentRequest
    ) -> TreatmentPlan:
        """疗效评估"""
        plan = await self.get(plan_id)
        if not plan:
            raise ValueError(f"TreatmentPlan {plan_id} not found")
        
        plan.efficacy = assessment.response_type
        plan.assessment_date = assessment.assessment_date
        
        # 根据疗效调整状态
        if assessment.response_type in ['CR', 'PR']:
            if plan.completion_rate and plan.completion_rate >= 100:
                plan.status = 'completed'
        elif assessment.response_type == 'PD':
            plan.status = 'discontinued'
        
        await self.db.commit()
        await self.db.refresh(plan)
        
        return plan
    
    async def create_prescription(self, data: TCMPrescriptionCreate) -> TCMPrescription:
        """创建中药处方"""
        prescription_no = await self._generate_prescription_no()
        
        # 验证治疗计划存在
        treatment_result = await self.db.execute(
            select(TreatmentPlan).where(TreatmentPlan.id == data.treatment_id)
        )
        treatment = treatment_result.scalar_one_or_none()
        if not treatment:
            raise ValueError(f"TreatmentPlan {data.treatment_id} not found")
        
        prescription = TCMPrescription(
            prescription_no=prescription_no,
            **data.model_dump()
        )
        
        self.db.add(prescription)
        await self.db.commit()
        await self.db.refresh(prescription)
        
        return prescription
    
    async def get_prescription(self, prescription_id: int) -> Optional[TCMPrescription]:
        """获取中药处方"""
        result = await self.db.execute(
            select(TCMPrescription).where(TCMPrescription.id == prescription_id)
        )
        return result.scalar_one_or_none()
    
    async def list_by_diagnosis(self, diagnosis_id: int) -> List[TreatmentPlan]:
        """根据诊断获取治疗方案列表"""
        result = await self.db.execute(
            select(TreatmentPlan)
            .join(Diagnosis)
            .where(Diagnosis.id == diagnosis_id)
            .order_by(TreatmentPlan.created_at.desc())
        )
        return result.scalars().all()
    
    async def _generate_plan_no(self) -> str:
        """生成治疗方案编号"""
        today = datetime.now().strftime('%Y%m%d')
        prefix = f"TP{today}"
        
        count_stmt = select(TreatmentPlan).where(
            TreatmentPlan.plan_no.like(f"{prefix}%")
        )
        result = await self.db.execute(count_stmt)
        count = result.scalars().count()
        
        return f"{prefix}{count + 1:04d}"
    
    async def _generate_prescription_no(self) -> str:
        """生成处方编号"""
        today = datetime.now().strftime('%Y%m%d')
        prefix = f"RX{today}"
        
        count_stmt = select(TCMPrescription).where(
            TCMPrescription.prescription_no.like(f"{prefix}%")
        )
        result = await self.db.execute(count_stmt)
        count = result.scalars().count()
        
        return f"{prefix}{count + 1:04d}"
