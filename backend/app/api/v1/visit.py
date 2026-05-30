from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.services.visit_service import VisitService
from app.schemas.visit import (
    VisitCreate,
    VisitUpdate,
    VisitResponse,
    VisitListResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse
)


router = APIRouter()


@router.post("/", response_model=VisitResponse)
async def create_visit(
    visit_data: VisitCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建随访记录"""
    service = VisitService(db)
    visit = await service.create(visit_data)
    return visit


@router.get("/", response_model=VisitListResponse)
async def list_visits(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = None,
    visit_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取随访列表"""
    service = VisitService(db)
    visits, total = await service.list(
        page=page,
        page_size=page_size,
        patient_id=patient_id,
        visit_type=visit_type
    )
    return VisitListResponse.create(
        data=visits,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{visit_id}", response_model=VisitResponse)
async def get_visit(
    visit_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取随访详情"""
    service = VisitService(db)
    visit = await service.get(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="随访记录不存在")
    return visit


@router.put("/{visit_id}", response_model=VisitResponse)
async def update_visit(
    visit_id: int,
    visit_data: VisitUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新随访记录"""
    service = VisitService(db)
    visit = await service.update(visit_id, visit_data)
    return visit


@router.post("/{visit_id}/risk-assessment", response_model=RiskAssessmentResponse)
async def assess_risk(
    visit_id: int,
    assessment: RiskAssessmentRequest,
    db: AsyncSession = Depends(get_db)
):
    """风险评估"""
    service = VisitService(db)
    result = await service.assess_risk(visit_id, assessment)
    return result


@router.post("/{visit_id}/followup-plan")
async def generate_followup_plan(
    visit_id: int,
    db: AsyncSession = Depends(get_db)
):
    """生成随访计划"""
    service = VisitService(db)
    plan = await service.generate_followup_plan(visit_id)
    return {"message": "随访计划生成成功", "plan": plan}
