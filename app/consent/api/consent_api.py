"""
知情同意书 API 路由
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.consent.models.consent_model import InformedConsent, ConsentStatus
from app.auth.models.user_model import User
from app.schemas.informed_consent import (
    ConsentCreate,
    ConsentUpdate,
    ConsentResponse,
    ConsentListResponse,
    SignConsentRequest,
    RevokeConsentRequest
)

router = APIRouter(prefix="/api/v1/consents", tags=["知情同意书"])


@router.get("", response_model=ConsentListResponse)
async def get_consent_list(
    patient_id: Optional[int] = None,
    status: Optional[ConsentStatus] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)  # TODO: 添加认证
):
    """获取知情同意书列表"""
    query = select(InformedConsent)
    
    if patient_id:
        query = query.where(InformedConsent.patient_id == patient_id)
    if status:
        query = query.where(InformedConsent.status == status)
    
    query = query.offset(skip).limit(limit).order_by(InformedConsent.created_at.desc())
    result = await db.execute(query)
    consents = result.scalars().all()
    
    total_query = select(InformedConsent.id)
    if patient_id:
        total_query = total_query.where(InformedConsent.patient_id == patient_id)
    if status:
        total_query = total_query.where(InformedConsent.status == status)
    total = len((await db.execute(total_query)).all())
    
    return ConsentListResponse(
        items=[ConsentResponse.model_validate(c) for c in consents],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{consent_id}", response_model=ConsentResponse)
async def get_consent(
    consent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)
):
    """获取知情同意书详情"""
    result = await db.execute(
        select(InformedConsent).where(InformedConsent.id == consent_id)
    )
    consent = result.scalar_one_or_none()
    
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知情同意书不存在"
        )
    
    return ConsentResponse.model_validate(consent)


@router.post("", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
async def create_consent(
    consent_data: ConsentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)
):
    """创建知情同意书"""
    consent = InformedConsent(**consent_data.model_dump())
    
    db.add(consent)
    await db.commit()
    await db.refresh(consent)
    
    return ConsentResponse.model_validate(consent)


@router.post("/{consent_id}/sign", response_model=ConsentResponse)
async def sign_consent(
    consent_id: int,
    sign_data: SignConsentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)
):
    """签署知情同意书"""
    result = await db.execute(
        select(InformedConsent).where(InformedConsent.id == consent_id)
    )
    consent = result.scalar_one_or_none()
    
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知情同意书不存在"
        )
    
    if consent.status != ConsentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"当前状态为{consent.status.value}，无法签署"
        )
    
    # 更新患者声明
    consent.has_understood_ai_purpose = sign_data.has_understood_ai_purpose
    consent.has_understood_ai_limitation = sign_data.has_understood_ai_limitation
    consent.has_understood_tcm_research = sign_data.has_understood_tcm_research
    consent.has_understood_data_usage = sign_data.has_understood_data_usage
    consent.has_understood_voluntary = sign_data.has_understood_voluntary
    consent.agree_to_participate = sign_data.agree_to_participate
    
    # 患者签署
    consent.patient_signature = sign_data.patient_signature
    consent.patient_sign_date = datetime.utcnow()
    
    # 医生签署
    consent.doctor_signature = sign_data.doctor_signature
    consent.doctor_sign_date = datetime.utcnow()
    
    # 更新状态
    consent.status = ConsentStatus.SIGNED
    
    db.add(consent)
    await db.commit()
    await db.refresh(consent)
    
    return ConsentResponse.model_validate(consent)


@router.post("/{consent_id}/revoke", response_model=ConsentResponse)
async def revoke_consent(
    consent_id: int,
    revoke_data: RevokeConsentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)
):
    """撤回知情同意"""
    result = await db.execute(
        select(InformedConsent).where(InformedConsent.id == consent_id)
    )
    consent = result.scalar_one_or_none()
    
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知情同意书不存在"
        )
    
    if consent.status == ConsentStatus.REVOKED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="同意书已撤回"
        )
    
    consent.status = ConsentStatus.REVOKED
    consent.revoked_at = datetime.utcnow()
    consent.revoked_reason = revoke_data.reason
    
    db.add(consent)
    await db.commit()
    await db.refresh(consent)
    
    return ConsentResponse.model_validate(consent)


@router.get("/template", response_model=dict)
async def get_consent_template():
    """获取知情同意书模板"""
    return {
        "version": "v1.0",
        "template_url": "/docs/legal/INFORMED_CONSENT_TEMPLATE.md",
        "fields": [
            {"name": "patient_name", "label": "患者姓名", "required": True},
            {"name": "patient_id_number", "label": "身份证号", "required": False},
            {"name": "institution_name", "label": "医疗机构名称", "required": True},
            {"name": "institution_address", "label": "机构地址", "required": True},
            {"name": "institution_contact", "label": "联系电话", "required": True},
            {"name": "ai_diagnosis_fee", "label": "AI 诊断费用", "required": True},
            {"name": "insurance_coverage", "label": "医保报销情况", "required": True},
            {"name": "self_pay_amount", "label": "自费金额", "required": True},
            {"name": "ethics_committee_approval_number", "label": "伦理批准号", "required": True},
        ]
    }
