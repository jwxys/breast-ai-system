"""
诊断报告服务

支持报告版本管理、历史追溯
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime

from app.diagnosis.models.diagnosis_model import Diagnosis, DiagnosisReport


class ReportService:
    """
    诊断报告服务
    
    功能:
    1. 创建报告版本
    2. 获取历史版本
    3. 版本差异比较
    4. 报告质量管理
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_version(
        self,
        diagnosis_id: int,
        ultrasound_findings: str,
        impression: str,
        recommendations: str,
        created_by: int,
        changes_from_previous: Optional[str] = None,
        change_reason: Optional[str] = None
    ) -> DiagnosisReport:
        """
        创建新的报告版本
        
        Args:
            diagnosis_id: 诊断 ID
            ultrasound_findings: 超声所见
            impression: 诊断印象
            recommendations: 建议
            created_by: 创建者
            changes_from_previous: 变更说明
            change_reason: 修改原因
        
        Returns:
            DiagnosisReport: 创建的报告版本
        """
        # 获取当前最新版本号
        result = await self.db.execute(
            select(DiagnosisReport)
            .where(DiagnosisReport.diagnosis_id == diagnosis_id)
            .order_by(DiagnosisReport.version_no.desc())
        )
        latest_version = result.scalar_one_or_none()
        
        new_version_no = 1 if not latest_version else latest_version.version_no + 1
        
        # 创建新版本
        report_version = DiagnosisReport(
            diagnosis_id=diagnosis_id,
            version_no=new_version_no,
            ultrasound_findings=ultrasound_findings,
            impression=impression,
            recommendations=recommendations,
            changes_from_previous=changes_from_previous,
            change_reason=change_reason,
            created_by=created_by
        )
        
        self.db.add(report_version)
        await self.db.commit()
        await self.db.refresh(report_version)
        
        return report_version
    
    async def get_versions(self, diagnosis_id: int) -> List[DiagnosisReport]:
        """
        获取诊断的所有报告版本
        
        Args:
            diagnosis_id: 诊断 ID
        
        Returns:
            List[DiagnosisReport]: 版本列表 (按版本号排序)
        """
        result = await self.db.execute(
            select(DiagnosisReport)
            .where(DiagnosisReport.diagnosis_id == diagnosis_id)
            .order_by(DiagnosisReport.version_no.asc())
        )
        return result.scalars().all()
    
    async def get_latest_version(self, diagnosis_id: int) -> Optional[DiagnosisReport]:
        """
        获取最新版本的报告
        
        Args:
            diagnosis_id: 诊断 ID
        
        Returns:
            Optional[DiagnosisReport]: 最新版本报告
        """
        result = await self.db.execute(
            select(DiagnosisReport)
            .where(DiagnosisReport.diagnosis_id == diagnosis_id)
            .order_by(DiagnosisReport.version_no.desc())
        )
        return result.scalar_one_or_none()
    
    async def get_version(
        self, 
        diagnosis_id: int, 
        version_no: int
    ) -> Optional[DiagnosisReport]:
        """
        获取指定版本的报告
        
        Args:
            diagnosis_id: 诊断 ID
            version_no: 版本号
        
        Returns:
            Optional[DiagnosisReport]: 指定版本报告
        """
        result = await self.db.execute(
            select(DiagnosisReport)
            .where(
                DiagnosisReport.diagnosis_id == diagnosis_id,
                DiagnosisReport.version_no == version_no
            )
        )
        return result.scalar_one_or_none()
    
    async def compare_versions(
        self,
        diagnosis_id: int,
        version_from: int,
        version_to: int
    ) -> dict:
        """
        比较两个版本的差异
        
        Args:
            diagnosis_id: 诊断 ID
            version_from: 起始版本号
            version_to: 目标版本号
        
        Returns:
            dict: 差异对比结果
        """
        v1 = await self.get_version(diagnosis_id, version_from)
        v2 = await self.get_version(diagnosis_id, version_to)
        
        if not v1 or not v2:
            return {"error": "版本不存在"}
        
        return {
            "version_from": version_from,
            "version_to": version_to,
            "changes": {
                "ultrasound_findings_changed": v1.ultrasound_findings != v2.ultrasound_findings,
                "impression_changed": v1.impression != v2.impression,
                "recommendations_changed": v1.recommendations != v2.recommendations
            },
            "change_summary": v2.changes_from_previous
        }
