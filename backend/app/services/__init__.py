"""
服务层模块
"""

from app.services.patient_service import PatientService
from app.services.visit_service import VisitService
from app.services.ultrasound_service import UltrasoundService
from app.services.diagnosis_service import DiagnosisService
from app.services.treatment_service import TreatmentService
from app.services.knowledge_service import KnowledgeService
from app.services.report_service import ReportService
from app.services.inquiry_service import InquiryService, get_inquiry_service
from app.services.copilot_service import MedicalCopilotService, get_copilot_service

__all__ = [
    "PatientService",
    "VisitService",
    "UltrasoundService",
    "DiagnosisService",
    "TreatmentService",
    "KnowledgeService",
    "ReportService",
    "InquiryService",
    "get_inquiry_service",
    "MedicalCopilotService",
    "get_copilot_service",
]
