from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1 import patient, visit, ultrasound, diagnosis, treatment, auth, ai_inference, knowledge, data_management, reports
from app.routers import inquiry, copilot, imaging_tcm
from app.core.exceptions import register_exceptions
from shared.middleware.auth import AuthMiddleware
from shared.middleware.logging import LoggingMiddleware
from app.core.database import init_db, close_db

# 导入所有模型以注册到 SQLAlchemy
from app.models.user import User  # noqa: F401
from app.models.patient import Patient  # noqa: F401
from app.models.visit import Visit  # noqa: F401
from app.models.ultrasound import UltrasoundExam  # noqa: F401
from app.models.diagnosis import Diagnosis  # noqa: F401
from app.models.treatment import TreatmentPlan  # noqa: F401
from app.models.knowledge import KnowledgeArticle  # noqa: F401
from app.models.data_management import ModelWeight  # noqa: F401
from app.models.data_management import TrainingDataset  # noqa: F401
from app.models.data_management import InferenceRecord  # noqa: F401
from app.models.data_management import Report  # noqa: F401
from app.models.data_management import FollowupRecord  # noqa: F401
from app.models.imaging_tcm import ImagingTCMCorrelation  # noqa: F401



@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    await init_db()
    yield
    # 关闭时执行
    await close_db()


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    app = FastAPI(
        title="乳腺 AI 辅助诊断系统",
        description="中西医结合智能诊疗平台",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan
    )

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 中间件
    app.add_middleware(AuthMiddleware)
    app.add_middleware(LoggingMiddleware)

    # 异常处理
    register_exceptions(app)

    # 路由
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
    app.include_router(patient.router, prefix="/api/v1/patient", tags=["患者管理"])
    app.include_router(visit.router, prefix="/api/v1/visit", tags=["随访管理"])
    app.include_router(ultrasound.router, prefix="/api/v1/ultrasound", tags=["超声检查"])
    app.include_router(diagnosis.router, prefix="/api/v1/diagnosis", tags=["诊断管理"])
    app.include_router(treatment.router, prefix="/api/v1/treatment", tags=["治疗管理"])
    app.include_router(ai_inference.router, prefix="/api/v1/ai", tags=["AI 推理"])
    app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["知识库"])
    app.include_router(data_management.router, prefix="/api/v1/data", tags=["数据管理"])
    app.include_router(reports.router, prefix="/api/v1/reports", tags=["报告管理"])
    app.include_router(inquiry.router, prefix="/api/v1/inquiry", tags=["AI 超声前问诊"])
    app.include_router(copilot.router, prefix="/api/v1/copilot", tags=["医疗 Copilot 助手"])
    app.include_router(imaging_tcm.router, prefix="/api/v1/imaging-tcm", tags=["影像 - 中医病机分析"])

    # 健康检查
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "1.0.0"}

    return app


# 创建应用实例
app = create_app()
