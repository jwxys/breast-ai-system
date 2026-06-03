"""
RBAC 权限管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.rbac_service import RBACService, init_default_permissions
from app.schemas.rbac import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    PermissionResponse,
    UserAssignRole,
    UserPermissionResponse,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/rbac", tags=["RBAC 权限管理"])


# ==================== 角色管理 ====================

@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建新角色"""
    service = RBACService(db)
    role = await service.create_role(role_data)
    return role


@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取角色列表"""
    service = RBACService(db)
    roles = await service.list_roles(skip=skip, limit=limit)
    return roles


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取角色详情"""
    service = RBACService(db)
    role = await service.get_role(role_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新角色"""
    service = RBACService(db)
    
    try:
        role = await service.update_role(role_id, role_data)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        return role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除角色"""
    service = RBACService(db)
    
    try:
        success = await service.delete_role(role_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        return {"message": "角色删除成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== 权限管理 ====================

@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    perm_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建权限"""
    service = RBACService(db)
    permission = await service.create_permission(PermissionCreate(**perm_data))
    return permission


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取权限列表"""
    service = RBACService(db)
    permissions = await service.list_permissions(skip=skip, limit=limit)
    return permissions


@router.get("/permissions/by-resource/{resource}", response_model=List[PermissionResponse])
async def list_permissions_by_resource(
    resource: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """按资源获取权限列表"""
    service = RBACService(db)
    permissions = await service.list_permissions_by_resource(resource)
    return permissions


# ==================== 用户角色管理 ====================

@router.post("/users/{user_id}/roles")
async def assign_roles_to_user(
    user_id: int,
    role_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """给用户分配角色"""
    service = RBACService(db)
    
    try:
        user = await service.assign_role_to_user(user_id, role_ids)
        return {"message": "角色分配成功", "user_id": user.id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/users/{user_id}/roles", response_model=List[RoleResponse])
async def get_user_roles(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取用户的角色列表"""
    service = RBACService(db)
    roles = await service.get_user_roles(user_id)
    return roles


@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_user_role(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """移除用户角色"""
    service = RBACService(db)
    success = await service.remove_user_role(user_id, role_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户或角色不存在"
        )
    
    return {"message": "角色移除成功"}


@router.get("/users/{user_id}/permissions", response_model=UserPermissionResponse)
async def get_user_permissions(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取用户权限列表"""
    service = RBACService(db)
    permissions = await service.get_user_permissions(user_id)
    return {"user_id": user_id, "permissions": permissions}


@router.post("/users/{user_id}/permissions/check")
async def check_user_permission(
    user_id: int,
    permission: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """检查用户是否有指定权限"""
    service = RBACService(db)
    has_permission = await service.check_permission(user_id, permission)
    return {
        "user_id": user_id,
        "permission": permission,
        "has_permission": has_permission
    }


# ==================== 初始化 ====================

@router.post("/init")
async def init_rbac(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """初始化 RBAC 系统（仅系统管理员）"""
    await init_default_permissions(db)
    
    service = RBACService(db)
    await service.init_system_roles()
    
    return {"message": "RBAC 系统初始化成功"}
