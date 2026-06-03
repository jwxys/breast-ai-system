"""
API v1 路由模块
"""

from app.api.v1 import auth
from app.api.v1 import patient
from app.api.v1 import visit
from app.api.v1 import ultrasound
from app.api.v1 import diagnosis
from app.api.v1 import treatment
from app.api.v1 import ai_inference
from app.api.v1 import knowledge
from app.api.v1 import data_management
from app.api.v1 import reports

__all__ = [
    "auth",
    "patient",
    "visit",
    "ultrasound",
    "diagnosis",
    "treatment",
    "ai_inference",
    "knowledge",
    "data_management",
    "reports",
]
