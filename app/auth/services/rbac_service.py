"""
RBAC 权限管理服务
角色基于访问控制，支持角色创建、权限分配、用户角色管理
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.auth.models.user_model import User, Role, Permission, UserRole
from app.schemas.rbac import (
    RoleCreate,
    RoleUpdate,
    PermissionCreate,
    UserAssignRole,
)


class RBACService:
    """RBAC 权限管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== 角色管理 ====================

    async def create_role(self, role_data: RoleCreate) -> Role:
        """创建新角色"""
        role = Role(
            name=role_data.name,
            description=role_data.description,
            is_system=role_data.is_system or False,
        )
        
        # 分配权限
        if role_data.permission_ids:
            for perm_id in role_data.permission_ids:
                result = await self.db.execute(
                    select(Permission).where(Permission.id == perm_id)
                )
                permission = result.scalar_one_or_none()
                if permission:
                    role.permissions.append(permission)
        
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def get_role(self, role_id: int) -> Optional[Role]:
        """获取角色详情"""
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        return result.scalar_one_or_none()

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        """更新角色"""
        result = await self.db.execute(
            select(Role).where(Role.id == role_id)
        )
        role = result.scalar_one_or_none()
        
        if not role:
            return None
        
        # 系统角色不可修改
        if role.is_system:
            raise ValueError("系统角色不可修改")
        
        if role_data.name:
            role.name = role_data.name
        if role_data.description:
            role.description = role_data.description
        
        # 更新权限
        if role_data.permission_ids is not None:
            role.permissions = []
            for perm_id in role_data.permission_ids:
                perm_result = await self.db.execute(
                    select(Permission).where(Permission.id == perm_id)
                )
                permission = perm_result.scalar_one_or_none()
                if permission:
                    role.permissions.append(permission)
        
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        result = await self.db.execute(
            select(Role).where(Role.id == role_id)
        )
        role = result.scalar_one_or_none()
        
        if not role:
            return False
        
        # 系统角色不可删除
        if role.is_system:
            raise ValueError("系统角色不可删除")
        
        await self.db.delete(role)
        await self.db.commit()
        return True

    async def list_roles(self, skip: int = 0, limit: int = 20) -> List[Role]:
        """获取角色列表"""
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    # ==================== 权限管理 ====================

    async def create_permission(self, perm_data: PermissionCreate) -> Permission:
        """创建权限"""
        permission = Permission(
            name=perm_data.name,
            description=perm_data.description,
            resource=perm_data.resource,
            action=perm_data.action,
        )
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def get_permission(self, perm_id: int) -> Optional[Permission]:
        """获取权限详情"""
        result = await self.db.execute(
            select(Permission).where(Permission.id == perm_id)
        )
        return result.scalar_one_or_none()

    async def list_permissions(self, skip: int = 0, limit: int = 50) -> List[Permission]:
        """获取权限列表"""
        result = await self.db.execute(
            select(Permission)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_permissions_by_resource(self, resource: str) -> List[Permission]:
        """按资源获取权限列表"""
        result = await self.db.execute(
            select(Permission).where(Permission.resource == resource)
        )
        return list(result.scalars().all())

    # ==================== 用户角色管理 ====================

    async def assign_role_to_user(
        self, user_id: int, role_ids: List[int]
    ) -> User:
        """给用户分配角色"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("用户不存在")
        
        # 验证角色存在
        roles = []
        for role_id in role_ids:
            role_result = await self.db.execute(
                select(Role).where(Role.id == role_id)
            )
            role = role_result.scalar_one_or_none()
            if not role:
                raise ValueError(f"角色 {role_id} 不存在")
            roles.append(role)
        
        # 清除旧角色
        stmt = delete(UserRole).where(UserRole.user_id == user_id)
        await self.db.execute(stmt)
        
        # 分配新角色
        for role in roles:
            user_role = UserRole(user_id=user_id, role_id=role.id)
            self.db.add(user_role)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_roles(self, user_id: int) -> List[Role]:
        """获取用户的角色列表"""
        result = await self.db.execute(
            select(Role)
            .join(UserRole)
            .where(UserRole.user_id == user_id)
            .options(selectinload(Role.permissions))
        )
        return list(result.scalars().all())

    async def remove_user_role(self, user_id: int, role_id: int) -> bool:
        """移除用户角色"""
        result = await self.db.execute(
            select(UserRole)
            .where(UserRole.user_id == user_id)
            .where(UserRole.role_id == role_id)
        )
        user_role = result.scalar_one_or_none()
        
        if not user_role:
            return False
        
        await self.db.delete(user_role)
        await self.db.commit()
        return True

    # ==================== 权限检查 ====================

    async def check_permission(self, user_id: int, permission: str) -> bool:
        """
        检查用户是否有指定权限
        permission 格式：resource:action (如 patient:read, diagnosis:write)
        """
        try:
            resource, action = permission.split(':')
        except ValueError:
            raise ValueError(f"权限格式错误：{permission}. 应为 resource:action")
        
        user_roles = await self.get_user_roles(user_id)
        
        for role in user_roles:
            for perm in role.permissions:
                if perm.resource == resource and perm.action == action:
                    return True
        
        return False

    async def get_user_permissions(self, user_id: int) -> List[str]:
        """获取用户所有权限"""
        user_roles = await self.get_user_roles(user_id)
        permissions = set()
        
        for role in user_roles:
            for perm in role.permissions:
                permissions.add(f"{perm.resource}:{perm.action}")
        
        return sorted(list(permissions))

    # ==================== 初始化系统角色 ====================

    async def init_system_roles(self):
        """初始化系统默认角色"""
        # 系统管理员
        admin_perms = await self.list_permissions()
        admin_role = Role(
            name="系统管理员",
            description="拥有所有权限",
            is_system=True,
            permissions=admin_perms,
        )
        
        # 医生
        doctor_perms = await self.list_permissions_by_resource('patient')
        doctor_perms += await self.list_permissions_by_resource('diagnosis')
        doctor_perms += await self.list_permissions_by_resource('visit')
        doctor_role = Role(
            name="医生",
            description="拥有患者、诊断、随访读写权限",
            is_system=True,
            permissions=doctor_perms,
        )
        
        # 研究人员
        researcher_perms = await self.list_permissions_by_resource('patient')
        researcher_perms = [p for p in researcher_perms if p.action == 'read']
        researcher_perms += await self.list_permissions_by_resource('data_management')
        researcher_role = Role(
            name="研究人员",
            description="拥有患者数据读取和数据分析权限",
            is_system=True,
            permissions=researcher_perms,
        )
        
        # 批量添加
        self.db.add_all([admin_role, doctor_role, researcher_role])
        await self.db.commit()


async def init_default_permissions(db: AsyncSession):
    """初始化默认权限"""
    default_permissions = [
        # 患者管理
        Permission(name="查看患者", resource="patient", action="read"),
        Permission(name="创建患者", resource="patient", action="create"),
        Permission(name="编辑患者", resource="patient", action="update"),
        Permission(name="删除患者", resource="patient", action="delete"),
        
        # 诊断管理
        Permission(name="查看诊断", resource="diagnosis", action="read"),
        Permission(name="创建诊断", resource="diagnosis", action="create"),
        Permission(name="编辑诊断", resource="diagnosis", action="update"),
        Permission(name="删除诊断", resource="diagnosis", action="delete"),
        
        # 随访管理
        Permission(name="查看随访", resource="visit", action="read"),
        Permission(name="创建随访", resource="visit", action="create"),
        Permission(name="编辑随访", resource="visit", action="update"),
        Permission(name="删除随访", resource="visit", action="delete"),
        
        # 超声检查
        Permission(name="查看超声", resource="ultrasound", action="read"),
        Permission(name="创建超声", resource="ultrasound", action="create"),
        Permission(name="编辑超声", resource="ultrasound", action="update"),
        
        # 影像中医分析
        Permission(name="查看中医分析", resource="tcm_analysis", action="read"),
        Permission(name="执行中医分析", resource="tcm_analysis", action="execute"),
        
        # AI 推理
        Permission(name="AI 推理", resource="ai_inference", action="execute"),
        
        # 数据管理
        Permission(name="查看数据", resource="data_management", action="read"),
        Permission(name="导出数据", resource="data_management", action="export"),
        Permission(name="导入数据", resource="data_management", action="import"),
        
        # 系统管理
        Permission(name="用户管理", resource="user", action="manage"),
        Permission(name="角色管理", resource="role", action="manage"),
        Permission(name="系统设置", resource="settings", action="manage"),
        
        # 知情同意
        Permission(name="查看知情同意书", resource="informed_consent", action="read"),
        Permission(name="签署知情同意书", resource="informed_consent", action="sign"),
        
        # 3D 建模
        Permission(name="3D 建模", resource="breast_3d", action="execute"),
    ]
    
    db.add_all(default_permissions)
    await db.commit()
