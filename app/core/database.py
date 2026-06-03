"""
数据库配置与连接管理

支持异步数据库操作
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import os

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+asyncmy://root:password@localhost/breast_ai"
)

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # 开发环境设为 True 显示 SQL
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session 工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base 类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话 (依赖注入)
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    
    Yields:
        AsyncSession: 数据库会话
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库
    创建所有表结构
    """
    async with engine.begin() as conn:
        # 导入所有模型
        from app.diagnosis.models import lesion_model, diagnosis_model
        from app.patient.models import patient_model
        from app.auth.models import user_model
        
        # 创建表
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
