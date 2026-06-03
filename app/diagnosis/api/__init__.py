"""
诊断模块 API 路由

导出所有 API 路由器
"""

from .diagnosis_api import router as diagnosis_router
from .reports_api import router as reports_router


__all__ = ["diagnosis_router", "reports_router"]
