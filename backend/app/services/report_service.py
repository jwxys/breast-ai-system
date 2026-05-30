"""
Report Service

诊断报告生成与管理服务
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc

from app.models.data_management import Report
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.diagnosis import Diagnosis


class ReportService:
    """报告服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_ai_diagnosis_report(self, patient_id: int, visit_id: int, 
                                      diagnosis_id: int, created_by: int) -> Report:
        """
        生成 AI 辅助诊断报告
        
        Args:
            patient_id: 患者 ID
            visit_id: 随访 ID
            diagnosis_id: 诊断 ID
            created_by: 创建人 ID
            
        Returns:
            Report: 生成的报告对象
        """
        # Generate report number
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        report_no = f"RPT-{timestamp}-{patient_id:06d}"
        
        # Get diagnosis details
        diagnosis = self.db.query(Diagnosis).options(
            selectinload(Diagnosis.ultrasound)
        ).filter(Diagnosis.id == diagnosis_id).first()
        
        if not diagnosis:
            raise ValueError(f"Diagnosis {diagnosis_id} not found")
        
        # Get patient info
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        
        # Get visit info
        visit = self.db.query(Visit).filter(Visit.id == visit_id).first()
        
        # Build report content (Markdown format)
        title = f"乳腺超声 AI 辅助诊断报告"
        
        content = self._build_report_content(
            patient=patient,
            visit=visit,
            diagnosis=diagnosis,
            report_no=report_no
        )
        
        summary = f"患者{patient.name}，{diagnosis.birads_category}类，AI 辅助诊断"
        
        # Create report
        report = Report(
            report_no=report_no,
            report_type='ai_diagnosis',
            patient_id=patient_id,
            visit_id=visit_id,
            diagnosis_id=diagnosis_id,
            title=title,
            content=content,
            summary=summary,
            ai_assisted=True,
            ai_model_used='DFMFI/HXM-Net',
            ai_confidence=diagnosis.ai_confidence if diagnosis.ai_confidence else 0.0,
            status='draft',
            created_by=created_by
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def create_report(self, data: Dict[str, Any], created_by: int) -> Report:
        """
        创建自定义报告
        
        Args:
            data: 报告数据字典
            created_by: 创建人 ID
            
        Returns:
            Report: 创建的报告对象
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        report_no = f"RPT-{timestamp}-{data.get('patient_id', 0):06d}"
        
        report = Report(
            report_no=report_no,
            report_type=data.get('report_type', 'research'),
            patient_id=data.get('patient_id'),
            visit_id=data.get('visit_id'),
            diagnosis_id=data.get('diagnosis_id'),
            title=data.get('title', ''),
            content=data.get('content', ''),
            summary=data.get('summary', ''),
            ai_assisted=data.get('ai_assisted', False),
            ai_model_used=data.get('ai_model_used'),
            ai_confidence=data.get('ai_confidence'),
            status=data.get('status', 'draft'),
            created_by=created_by
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def get_report_by_id(self, report_id: int) -> Optional[Report]:
        """根据 ID 获取报告"""
        return self.db.query(Report).filter(Report.id == report_id).first()
    
    def get_report_by_no(self, report_no: str) -> Optional[Report]:
        """根据编号获取报告"""
        return self.db.query(Report).filter(Report.report_no == report_no).first()
    
    def get_patient_reports(self, patient_id: int) -> List[Report]:
        """获取患者的所有报告"""
        return self.db.query(Report).filter(
            Report.patient_id == patient_id
        ).order_by(desc(Report.created_at)).all()
    
    def update_report(self, report_id: int, data: Dict[str, Any]) -> Optional[Report]:
        """更新报告"""
        report = self.get_report_by_id(report_id)
        if not report:
            return None
        
        for key, value in data.items():
            if hasattr(report, key):
                setattr(report, key, value)
        
        report.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def publish_report(self, report_id: int) -> Optional[Report]:
        """发布报告"""
        report = self.get_report_by_id(report_id)
        if not report:
            return None
        
        report.status = 'published'
        report.published_at = datetime.utcnow()
        report.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def delete_report(self, report_id: int) -> bool:
        """删除报告"""
        report = self.get_report_by_id(report_id)
        if not report:
            return False
        
        self.db.delete(report)
        self.db.commit()
        
        return True
    
    def _build_report_content(self, patient: Patient, visit: Visit, 
                             diagnosis: Diagnosis, report_no: str) -> str:
        """构建报告内容 (Markdown 格式)"""
        
        content = f"""# 乳腺超声 AI 辅助诊断报告

## 基本信息

- **报告编号**: {report_no}
- **报告日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **患者姓名**: {patient.name}
- **患者性别**: {patient.gender}
- **患者年龄**: {self._calculate_age(patient.date_of_birth)}岁
- **就诊编号**: {visit.visit_no}
- **就诊日期**: {visit.visit_date.strftime('%Y-%m-%d') if visit.visit_date else 'N/A'}

---

## 诊断结果

### BI-RADS 分级

**{diagnosis.birads_category} 类**

### 诊断结论

- **侧别**: {diagnosis.laterality or '未指定'}
- **象限**: {diagnosis.quadrant or '未指定'}
- **肿瘤特征**: 
  - 形态：{diagnosis.tumor_shape or '未评估'}
  - 边缘：{diagnosis.tumor_margin or '未评估'}
  - 回声：{diagnosis.echo_pattern or '未评估'}
  - 钙化：{diagnosis.calcification or '未评估'}
  - 血流：{diagnosis.blood_flow or '未评估'}

---

## AI 辅助分析

### 模型信息

- **使用模型**: DFMFI / HXM-Net
- **模型版本**: v1.0.0
- **推理时间**: {diagnosis.ai_inference_time_ms or 0}ms

### AI 预测结果

- **预测类别**: {diagnosis.ai_prediction or 'pending'}
- **置信度**: {(diagnosis.ai_confidence or 0) * 100:.1f}%
- **BI-RADS 预测**: {diagnosis.birads_category}类

---

## 建议

根据 AI 分析结果，建议：

1. {self._get_suggestion_by_birads(diagnosis.birads_category)}

---

## 声明

本报告由 AI 辅助诊断系统生成，仅供参考，不能替代专业医生的诊断。
最终诊断请以临床医生的判断为准。

---

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**AI 辅助**: 是
"""
        
        return content
    
    def _calculate_age(self, date_of_birth: Optional[datetime]) -> int:
        """计算年龄"""
        if not date_of_birth:
            return 0
        today = datetime.today()
        return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    
    def _get_suggestion_by_birads(self, birads: int) -> str:
        """根据 BI-RADS 分级获取建议"""
        suggestions = {
            0: "需要进一步影像学检查",
            1: "阴性，常规随访",
            2: "良性发现，常规随访",
            3: "可能良性，建议短期随访 (6 个月)",
            4: "可疑恶性，建议穿刺活检",
            5: "高度可疑恶性，建议穿刺活检或手术切除",
            6: "已活检证实恶性，建议手术治疗"
        }
        return suggestions.get(birads, "请咨询专科医生")
