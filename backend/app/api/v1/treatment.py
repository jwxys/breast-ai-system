from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.treatment_service import TreatmentService
from app.schemas.treatment import (
    TreatmentPlanCreate,
    TreatmentPlanUpdate,
    TreatmentPlanResponse,
    TCMPrescriptionCreate,
    TCMPrescriptionResponse,
    EfficacyAssessmentRequest
)


router = APIRouter()


@router.post("/plan", response_model=TreatmentPlanResponse)
async def create_treatment_plan(
    plan_data: TreatmentPlanCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建治疗方案"""
    service = TreatmentService(db)
    plan = await service.create(plan_data)
    return plan


@router.get("/plan/{plan_id}", response_model=TreatmentPlanResponse)
async def get_treatment_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取治疗方案"""
    service = TreatmentService(db)
    plan = await service.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="治疗方案不存在")
    return plan


@router.put("/plan/{plan_id}", response_model=TreatmentPlanResponse)
async def update_treatment_plan(
    plan_id: int,
    plan_data: TreatmentPlanUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新治疗方案"""
    service = TreatmentService(db)
    plan = await service.update(plan_id, plan_data)
    return plan


@router.post("/plan/{plan_id}/efficacy", response_model=TreatmentPlanResponse)
async def assess_efficacy(
    plan_id: int,
    assessment: EfficacyAssessmentRequest,
    db: AsyncSession = Depends(get_db)
):
    """疗效评估"""
    service = TreatmentService(db)
    plan = await service.assess_efficacy(plan_id, assessment)
    return plan


@router.post("/prescription", response_model=TCMPrescriptionResponse)
async def create_prescription(
    prescription_data: TCMPrescriptionCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建中药处方"""
    service = TreatmentService(db)
    prescription = await service.create_prescription(prescription_data)
    return prescription


@router.get("/prescription/{prescription_id}", response_model=TCMPrescriptionResponse)
async def get_prescription(
    prescription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取中药处方"""
    service = TreatmentService(db)
    prescription = await service.get_prescription(prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="处方不存在")
    return prescription


@router.get("/diagnosis/{diagnosis_id}/plans")
async def list_treatment_plans(
    diagnosis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取诊断的治疗方案列表"""
    service = TreatmentService(db)
    plans = await service.list_by_diagnosis(diagnosis_id)
    return {"data": plans}
