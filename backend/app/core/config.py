from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "乳腺 AI 辅助诊断系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    
    # 应用根目录
    ROOT_DIR: str = str(Path(__file__).parent.parent.parent.parent)
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/breast_ai"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PREFIX: str = "breast_ai:"
    
    # JWT 配置
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN: int = 7200  # 2 小时
    JWT_EXPIRE_MINUTES: int = 120
    
    # CORS 配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://breast-ai.online",
    ]
    
    # 对象存储配置
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_BUCKET: str = "breast-ai"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    
    # AI 服务配置
    AI_SERVICE_URL: str = "http://localhost:8005"
    AI_MODEL_TIMEOUT: int = 60
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
