"""
Report API Endpoints

报告管理 RESTful API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from shared.middleware.auth import get_current_user
from app.models.user import User
from app.models.data_management import Report
from app.services.report_service import ReportService
from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/", response_model=ReportResponse, status_code=201)
def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新报告"""
    service = ReportService(db)
    
    try:
        report = service.create_report(
            data=report_data.model_dump(exclude={'created_by'}),
            created_by=current_user.id
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-ai-diagnosis", response_model=ReportResponse, status_code=201)
def generate_ai_diagnosis_report(
    patient_id: int,
    visit_id: int,
    diagnosis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成 AI 辅助诊断报告"""
    service = ReportService(db)
    
    try:
        report = service.generate_ai_diagnosis_report(
            patient_id=patient_id,
            visit_id=visit_id,
            diagnosis_id=diagnosis_id,
            created_by=current_user.id
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取报告详情"""
    service = ReportService(db)
    report = service.get_report_by_id(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.get("/number/{report_no}", response_model=ReportResponse)
def get_report_by_number(
    report_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据报告编号获取报告"""
    service = ReportService(db)
    report = service.get_report_by_no(report_no)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.get("/patient/{patient_id}", response_model=List[ReportResponse])
def get_patient_reports(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取患者的所有报告"""
    service = ReportService(db)
    reports = service.get_patient_reports(patient_id)
    return reports


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    report_data: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新报告"""
    service = ReportService(db)
    report = service.update_report(
        report_id=report_id,
        data=report_data.model_dump(exclude_unset=True)
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.post("/{report_id}/publish", response_model=ReportResponse)
def publish_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发布报告"""
    service = ReportService(db)
    report = service.publish_report(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.delete("/{report_id}", status_code=204)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除报告"""
    service = ReportService(db)
    success = service.delete_report(report_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return None


@router.get("/", response_model=List[ReportResponse])
def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    report_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取报告列表"""
    query = db.query(Report)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    if status:
        query = query.filter(Report.status == status)
    
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    return reports
