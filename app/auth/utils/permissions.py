"""
权限装饰器

用于保护需要特定权限的 API 端点
"""
from functools import wraps
from fastapi import HTTPException, status, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.auth.models.user_model import User, Role, Permission


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, required_permissions: List[str]):
        """
        初始化权限检查器
        
        Args:
            required_permissions: 所需权限列表，如 ['imaging_tcm.analyze']
        """
        self.required_permissions = required_permissions


def require_tcm_qualification():
    """
    要求用户具有中医执业资格
    
    检查用户是否属于中医科室或具有中医执业资格
    """
    async def checker(
        current_user: dict = Depends(lambda: None),  # TODO: 实际应用中应从 JWT 解析用户信息
        db: AsyncSession = Depends(get_db)
    ):
        """
        权限检查器
        
        验证用户是否具有中医执业资格：
        1. 用户所属科室为中医科
        2. 用户具有中医执业证书编号
        3. 用户角色包含中医相关权限
        """
        # TODO: 实际应用中应从数据库查询完整用户信息
        # 这里使用示例检查逻辑
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未授权访问"
            )
        
        # 示例：检查用户是否在允许列表中
        # 实际应用中应该从数据库查询用户的科室、执业资格等信息
        allowed_departments = ['中医科', '中西医结合科', '中医乳腺科']
        required_license_prefixes = ['TCM', '中医']
        
        # 从用户对象获取信息（需从 JWT 或数据库加载）
        user_department = getattr(current_user, 'department', None)
        user_license = getattr(current_user, 'license_number', None)
        user_roles = getattr(current_user, 'roles', [])
        
        # 检查科室
        if user_department and any(d in user_department for d in allowed_departments):
            return current_user
        
        # 检查执业资格
        if user_license and any(prefix in user_license for prefix in required_license_prefixes):
            return current_user
        
        # 检查角色（TCM_ANALYST 角色允许访问）
        if isinstance(user_roles, list) and 'TCM_ANALYST' in user_roles:
            return current_user
        
        # 权限不足
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：仅执业中医师或经授权的研究人员可访问此功能"
        )
    
    return checker


def require_permission(permission: str):
    """
    通用的权限要求装饰器
    
    Args:
        permission: 权限标识，如 'patient.read', 'diagnosis.write'
    """
    async def checker(
        current_user: dict = Depends(lambda: None),
        db: AsyncSession = Depends(get_db)
    ):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未授权访问"
            )
        
        # TODO: 实际应用中应查询用户的权限
        # 这里仅为示例
        
        user_permissions = getattr(current_user, 'permissions', [])
        
        if permission not in user_permissions and 'ADMIN' not in getattr(current_user, 'roles', []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {permission} 权限"
            )
        
        return current_user
    
    return checker


# 预定义的权限标识
class Permissions:
    """权限常量"""
    
    # 患者管理
    PATIENT_READ = "patient.read"
    PATIENT_WRITE = "patient.write"
    PATIENT_DELETE = "patient.delete"
    
    # 诊断管理
    DIAGNOSIS_READ = "diagnosis.read"
    DIAGNOSIS_WRITE = "diagnosis.write"
    
    # 影像检查
    ULTRASOUND_READ = "ultrasound.read"
    ULTRASOUND_WRITE = "ultrasound.write"
    
    # 中医模块（研究性质）
    TCM_ANALYZE = "tcm.analyze"
    TCM_READ = "tcm.read"
    TCM_WRITE = "tcm.write"
    TCM_RESEARCH = "tcm.research"
    
    # 数据管理
    DATA_EXPORT = "data.export"
    DATA_ADMIN = "data.admin"
    
    # 系统管理
    ADMIN_ALL = "admin.all"