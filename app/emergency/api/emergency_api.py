"""
应急联系人 API 路由
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.future import select as future_select

from app.core.database import get_db
from app.emergency.models.emergency_contact_model import EmergencyContact, ContactType
from app.auth.models.user_model import User
from app.schemas.emergency_contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse
)

router = APIRouter(prefix="/api/v1/emergency-contacts", tags=["应急联系人"])


@router.get("", response_model=ContactListResponse)
async def get_contact_list(
    contact_type: Optional[ContactType] = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)  # TODO: 添加认证
):
    """获取应急联系人列表"""
    query = select(EmergencyContact).where(EmergencyContact.is_active == is_active)
    
    if contact_type:
        query = query.where(EmergencyContact.contact_type == contact_type)
    
    query = query.order_by(EmergencyContact.priority, EmergencyContact.name)
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    contacts = result.scalars().all()
    
    # 计算总数
    count_query = select(func.count(EmergencyContact.id)).where(
        EmergencyContact.is_active == is_active
    )
    if contact_type:
        count_query = count_query.where(EmergencyContact.contact_type == contact_type)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return ContactListResponse(
        items=[ContactResponse.model_validate(c) for c in contacts],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)
):
    """获取应急联系人详情"""
    result = await db.execute(
        select(EmergencyContact).where(EmergencyContact.id == contact_id)
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="联系人不存在"
        )
    
    return ContactResponse.model_validate(contact)


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)
):
    """创建应急联系人"""
    contact = EmergencyContact(**contact_data.model_dump())
    
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    
    return ContactResponse.model_validate(contact)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)
):
    """更新应急联系人"""
    result = await db.execute(
        select(EmergencyContact).where(EmergencyContact.id == contact_id)
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="联系人不存在"
        )
    
    update_data = contact_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contact, key, value)
    
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    
    return ContactResponse.model_validate(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)
):
    """删除应急联系人（软删除）"""
    result = await db.execute(
        select(EmergencyContact).where(EmergencyContact.id == contact_id)
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="联系人不存在"
        )
    
    contact.is_active = False
    db.add(contact)
    await db.commit()
    
    return None


@router.get("/types", response_model=List[dict])
async def get_contact_types():
    """获取联系人类型列表"""
    return [
        {"value": ContactType.EMERGENCY.value, "label": "紧急联系人", "color": "red"},
        {"value": ContactType.MEDICAL.value, "label": "医疗联系人", "color": "blue"},
        {"value": ContactType.ADMIN.value, "label": "行政联系人", "color": "green"},
        {"value": ContactType.TECHNICAL.value, "label": "技术支持", "color": "orange"},
        {"value": ContactType.ETHICS.value, "label": "伦理委员会", "color": "purple"},
        {"value": ContactType.OTHER.value, "label": "其他", "color": "gray"},
    ]


@router.get("/quick-access", response_model=List[ContactResponse])
async def get_quick_access_contacts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)
):
    """获取快速访问联系人（优先级前 5 位）"""
    result = await db.execute(
        select(EmergencyContact)
        .where(EmergencyContact.is_active == True)
        .order_by(EmergencyContact.priority)
        .limit(5)
    )
    contacts = result.scalars().all()
    
    return [ContactResponse.model_validate(c) for c in contacts]
