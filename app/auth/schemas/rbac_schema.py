"""
RBAC 权限管理 Schema
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ==================== 权限 Schema ====================

class PermissionBase(BaseModel):
    """权限基础 Schema"""
    name: str = Field(..., description="权限名称")
    description: str = Field("", description="权限描述")
    resource: str = Field(..., description="资源类型 (如 patient, diagnosis)")
    action: str = Field(..., description="操作类型 (如 read, create, update, delete)")


class PermissionCreate(PermissionBase):
    """创建权限"""
    pass


class PermissionResponse(PermissionBase):
    """权限响应"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 角色 Schema ====================

class RoleBase(BaseModel):
    """角色基础 Schema"""
    name: str = Field(..., description="角色名称")
    description: str = Field("", description="角色描述")
    is_system: bool = Field(False, description="是否系统角色")


class RoleCreate(RoleBase):
    """创建角色"""
    permission_ids: Optional[List[int]] = Field(None, description="权限 ID 列表")


class RoleUpdate(BaseModel):
    """更新角色"""
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    """角色响应"""
    id: int
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True


# ==================== 用户角色管理 Schema ====================

class UserAssignRole(BaseModel):
    """用户分配角色"""
    role_ids: List[int] = Field(..., description="角色 ID 列表")


class UserPermissionResponse(BaseModel):
    """用户权限响应"""
    user_id: int
    permissions: List[str] = Field([], description="权限列表 (格式：resource:action)")
