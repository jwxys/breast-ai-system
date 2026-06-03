import bcrypt
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core import config
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.models.user_model import User
from fastapi import Request
from sqlalchemy.orm import selectinload

router = APIRouter()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


class Token(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """Token 数据"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 Access Token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.settings.JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        config.settings.JWT_SECRET,
        algorithm=config.settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str
) -> Optional[User]:
    """认证用户"""
    result = await session.execute(
        select(User).options(selectinload(User.role)).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db)
):
    """
    OAuth2 密码模式登录
    
    - **username**: 用户名
    - **password**: 密码
    
    返回 JWT Token，用于后续请求的认证
    
    **示例**:
    ```
    POST /api/v1/auth/login
    Content-Type: application/x-www-form-urlencoded
    
    username=admin&password=admin123
    ```
    """
    user = await authenticate_user(session, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取角色信息
    role_code = "user"
    if user.role:
        role_code = user.role.role_code
    
    # 生成 Token
    access_token_expires = timedelta(minutes=config.settings.JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": role_code,
        },
        expires_delta=access_token_expires,
    )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    await session.commit()
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds())
    )


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(
    request: Request
):
    """获取当前登录用户信息"""
    return {
        "id": getattr(request.state, "user_id", None),
        "username": getattr(request.state, "username", None),
        "role": getattr(request.state, "user_role", None),
    }
