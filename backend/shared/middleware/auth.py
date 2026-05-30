from fastapi import Request, HTTPException
from jose import jwt, JWTError
from datetime import datetime

from app.core import config


class AuthMiddleware:
    """认证中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        request = Request(scope, receive=receive)
        
        # 跳过公开路径
        public_paths = [
            "/health",
            "/api/health",
            "/api/v1/auth/login",
            "/api/v1/copilot",  # Copilot 测试用
            "/api/docs",
            "/api/redoc",
            "/openapi.json",
            "/api/openapi.json",
        ]
        
        if any(request.url.path.startswith(path) for path in public_paths):
            return await self.app(scope, receive, send)
        
        # 验证 Token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="未提供认证 Token")
        
        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(
                token,
                config.settings.JWT_SECRET,
                algorithms=[config.settings.JWT_ALGORITHM]
            )
            
            # 将用户信息存入请求上下文
            request.state.user_id = payload.get("sub")
            request.state.username = payload.get("username")
            request.state.user_role = payload.get("role")
            
        except JWTError:
            raise HTTPException(status_code=401, detail="Token 无效或已过期")
        
        return await self.app(scope, receive, send)


def get_current_user(request: Request) -> dict:
    """获取当前用户（依赖注入）"""
    return {
        "user_id": getattr(request.state, "user_id", None),
        "username": getattr(request.state, "username", None),
        "role": getattr(request.state, "user_role", None)
    }
