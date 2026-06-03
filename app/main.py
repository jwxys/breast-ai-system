"""
乳腺 AI 辅助诊断系统 - 主入口

应用启动配置和路由注册
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    startup: 应用启动时执行
    shutdown: 应用关闭时执行
    """
    # startup
    logger.info("🚀 乳腺 AI 辅助诊断系统启动中...")
    logger.info("📊 加载配置...")
    logger.info("✅ 服务启动完成")
    
    yield
    
    # shutdown
    logger.info("👋 服务关闭中...")


def create_app() -> FastAPI:
    """
    创建 FastAPI 应用实例
    
    Returns:
        FastAPI: 配置完成的应用实例
    """
    app = FastAPI(
        title="乳腺 AI 辅助诊断系统",
        description="""
完善的乳腺超声 AI 智能诊断平台，包含：

## 核心功能
- **BI-RADS 智能分级** - 基于 ACR 第 5 版指南
- **分子分型预测** - St. Gallen 共识标准
- **AI 影像分析** - 视觉大模型集成
- **统计看板** - 实时质控监测

## AI 增强
- 影像组学特征提取 (20+ 定量特征)
- 模型校准 (ECE<0.05)
- 不确定性量化 (MC Dropout)
- 可解释性增强 (Grad-CAM)
- 多模态融合 (超声 + 钼靶+MRI)
        """,
        version="3.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )
    
    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册所有模块路由
    register_routers(app)
    
    # 健康检查
    @app.get("/health", tags=["健康检查"])
    async def health_check():
        """服务健康状态检查"""
        return {
            "status": "healthy",
            "version": "3.0.0",
            "modules": ["diagnosis", "inference", "statistics", "reports"]
        }
    
    return app


def register_routers(app: FastAPI):
    """
    注册所有功能模块的路由
    
    按功能域组织：
    - diagnosis: 诊断核心功能
    - inference: AI 推理服务
    - statistics: 统计分析
    - reports: 报告管理
    """
    from app.diagnosis.api.diagnosis_api import router as diagnosis_router
    from app.diagnosis.api.reports_api import router as reports_router
    from app.inference.api.inference_api import router as inference_router
    from app.statistics.api.stats_api import router as statistics_router
    
    # 注册路由
    app.include_router(diagnosis_router)
    app.include_router(reports_router)
    app.include_router(inference_router)
    app.include_router(statistics_router)
    
    logger.info("📦 已注册路由:")
    logger.info("  - /api/v1/diagnosis (诊断核心)")
    logger.info("  - /api/v1/inference (AI 推理)")
    logger.info("  - /api/v1/statistics (统计分析)")
    logger.info("  - /api/v1/reports (报告管理)")


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
