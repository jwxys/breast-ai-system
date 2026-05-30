from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from .config import settings


# 数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

# 会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """基础模型类"""
    
    # 配置以允许 model_ 前缀
    if hasattr(DeclarativeBase, 'model_config'):
        model_config = {"protected_namespaces": ()}
    pass


async def init_db():
    """初始化数据库连接"""
    async with engine.begin() as conn:
        # 可以在这里执行数据库迁移
        pass
    print("数据库连接初始化成功")


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
    print("数据库连接已关闭")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（依赖注入）"""
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
