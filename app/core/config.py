"""
应用配置模块
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "乳腺 AI 辅助诊断系统"
    APP_VERSION: str = "3.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    
    # JWT 配置
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI 服务配置
    KIMI_API_KEY: Optional[str] = None
    TONGYI_API_KEY: Optional[str] = None
    AI_SERVICE_URL: Optional[str] = None
    AI_MODEL_NAME: str = "default"
    AI_TIMEOUT: int = 60
    
    # 文件存储
    FILE_STORAGE_PATH: str = "/workspace/breast-ai-system/storage"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
