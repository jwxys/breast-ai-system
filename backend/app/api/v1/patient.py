from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.patient_service import PatientService
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)


router = APIRouter()


@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新患者"""
    service = PatientService(db)
    patient = await service.create(patient_data)
    return patient


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    constitution: str = None,
    zheng_type: str = None,
    risk_level: str = None,
    db: AsyncSession = Depends(get_db)
):
    """获取患者列表"""
    service = PatientService(db)
    patients, total = await service.list(
        page=page,
        page_size=page_size,
        constitution=constitution,
        zheng_type=zheng_type,
        risk_level=risk_level
    )
    return PatientListResponse(
        data=patients,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取患者详情"""
    service = PatientService(db)
    patient = await service.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新患者信息"""
    service = PatientService(db)
    patient = await service.update(patient_id, patient_data)
    return patient


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除患者（软删除）"""
    service = PatientService(db)
    await service.delete(patient_id)
    return {"message": "删除成功"}
