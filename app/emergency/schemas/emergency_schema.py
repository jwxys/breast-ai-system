"""
应急联系人 Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.emergency.models.emergency_contact_model import ContactType


class ContactBase(BaseModel):
    """联系人基础 Schema"""
    name: str = Field(..., min_length=2, max_length=64, description="姓名")
    title: Optional[str] = Field(None, max_length=128, description="职务/职称")
    organization: Optional[str] = Field(None, max_length=256, description="所属机构")
    contact_type: ContactType = Field(default=ContactType.EMERGENCY, description="联系人类型")
    
    # 联系方式
    phone_primary: str = Field(..., min_length=7, max_length=20, description="主要电话")
    phone_secondary: Optional[str] = Field(None, max_length=20, description="备用电话")
    email: Optional[str] = Field(None, max_length=128, description="电子邮箱")
    wechat: Optional[str] = Field(None, max_length=64, description="微信号")
    address: Optional[str] = Field(None, description="地址")
    
    # 职责
    responsibilities: Optional[str] = Field(None, description="职责描述")
    available_hours: Optional[str] = Field(None, max_length=128, description="可联系时间")
    
    # 排序
    priority: int = Field(default=0, ge=0, description="优先级")
    is_active: bool = Field(default=True, description="是否启用")
    
    # 备注
    notes: Optional[str] = Field(None, description="备注信息")


class ContactCreate(ContactBase):
    """创建联系人"""
    pass


class ContactUpdate(BaseModel):
    """更新联系人"""
    name: Optional[str] = Field(None, min_length=2, max_length=64)
    title: Optional[str] = Field(None, max_length=128)
    organization: Optional[str] = Field(None, max_length=256)
    contact_type: Optional[ContactType] = None
    phone_primary: Optional[str] = Field(None, min_length=7, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=128)
    wechat: Optional[str] = Field(None, max_length=64)
    address: Optional[str] = None
    responsibilities: Optional[str] = None
    available_hours: Optional[str] = Field(None, max_length=128)
    priority: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class ContactResponse(ContactBase):
    """联系人响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ContactListResponse(BaseModel):
    """联系人列表响应"""
    items: List[ContactResponse]
    total: int
    skip: int = 0
    limit: int = 20
