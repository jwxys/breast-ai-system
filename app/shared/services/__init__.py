"""
服务层模块
"""

from app.patient.services.patient_service import PatientService
from app.visit.services.visit_service import VisitService
from app.ultrasound.services.ultrasound_service import UltrasoundService
from app.shared.services.diagnosis_service import DiagnosisService
from app.treatment.services.treatment_service import TreatmentService
from app.knowledge.services.knowledge_service import KnowledgeService
from app.inquiry.services.inquiry_service import InquiryService, get_inquiry_service
from app.copilot.services.copilot_service import MedicalCopilotService, get_copilot_service

__all__ = [
    "PatientService",
    "VisitService",
    "UltrasoundService",
    "DiagnosisService",
    "TreatmentService",
    "KnowledgeService",
    "InquiryService",
    "get_inquiry_service",
    "MedicalCopilotService",
    "get_copilot_service",
]
