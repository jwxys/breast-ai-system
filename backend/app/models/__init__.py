# 导入所有模型以注册到 SQLAlchemy
from app.models.user import User
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.ultrasound import UltrasoundExam
from app.models.diagnosis import Diagnosis
from app.models.treatment import TreatmentPlan
from app.models.knowledge import KnowledgeCategory, KnowledgeArticle, KnowledgeTag
from app.models.data_management import (
    ModelWeight,
    TrainingDataset,
    PublicDataset,
    InferenceRecord,
    Report,
    FollowupRecord
)
from app.models.imaging_tcm import ImagingTCMCorrelation

__all__ = [
    "User",
    "Patient",
    "Visit",
    "UltrasoundExam",
    "Diagnosis",
    "TreatmentPlan",
    "KnowledgeCategory",
    "KnowledgeArticle",
    "KnowledgeTag",
    "ModelWeight",
    "TrainingDataset",
    "PublicDataset",
    "InferenceRecord",
    "Report",
    "FollowupRecord",
    "ImagingTCMCorrelation",
]
