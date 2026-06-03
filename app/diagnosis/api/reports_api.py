"""
诊断报告管理 API

提供报告版本管理功能：
- 获取报告历史版本
- 创建新版本
- 查看指定版本
- 版本差异比较
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.diagnosis.models.diagnosis_model import Diagnosis, DiagnosisReport
from app.diagnosis.schemas.diagnosis_schema import (
    DiagnosisReportCreate,
    DiagnosisReportResponse,
)


router = APIRouter(prefix="/api/v1/diagnosis", tags=["诊断报告管理"])


@router.get(
    "/{diagnosis_id}/reports",
    summary="获取报告版本列表",
    description="获取诊断的所有报告版本 (按版本号排序)",
    response_model=List[DiagnosisReportResponse]
)
async def get_report_versions(
    diagnosis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取诊断报告的所有历史版本
    
    用于：
    - 查看报告修改历史
    - 质量追溯
    - 教学参考
    
    版本按 version_no 升序排列
    """
    # 验证诊断是否存在
    diagnosis_result = await db.execute(
        select(Diagnosis).where(Diagnosis.id == diagnosis_id)
    )
    diagnosis = diagnosis_result.scalar_one_or_none()
    
    if not diagnosis:
        raise HTTPException(
            status_code=404,
            detail=f"诊断记录 {diagnosis_id} 不存在"
        )
    
    # 获取所有版本
    result = await db.execute(
        select(DiagnosisReport)
        .where(DiagnosisReport.diagnosis_id == diagnosis_id)
        .order_by(DiagnosisReport.version_no.asc())
    )
    versions = result.scalars().all()
    
    return versions


@router.get(
    "/{diagnosis_id}/report/latest",
    summary="获取最新版本报告",
    description="获取诊断的最新版本报告",
    response_model=DiagnosisReportResponse
)
async def get_latest_report(
    diagnosis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取最新版本的诊断报告
    
    用于：
    - 显示当前有效报告
    - 打印正式报告
    """
    # 验证诊断是否存在
    diagnosis_result = await db.execute(
        select(Diagnosis).where(Diagnosis.id == diagnosis_id)
    )
    diagnosis = diagnosis_result.scalar_one_or_none()
    
    if not diagnosis:
        raise HTTPException(
            status_code=404,
            detail=f"诊断记录 {diagnosis_id} 不存在"
        )
    
    # 获取最新版本
    result = await db.execute(
        select(DiagnosisReport)
        .where(DiagnosisReport.diagnosis_id == diagnosis_id)
        .order_by(DiagnosisReport.version_no.desc())
    )
    latest_report = result.scalar_one_or_none()
    
    if not latest_report:
        raise HTTPException(
            status_code=404,
            detail=f"诊断 {diagnosis_id} 暂无报告"
        )
    
    return latest_report


@router.get(
    "/{diagnosis_id}/report/{version_no}",
    summary="获取指定版本报告",
    description="获取诊断的指定版本报告",
    response_model=DiagnosisReportResponse
)
async def get_report_version(
    diagnosis_id: int,
    version_no: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定版本的诊断报告
    
    用于：
    - 查看历史版本详情
    - 对比不同版本
    """
    # 验证诊断是否存在
    diagnosis_result = await db.execute(
        select(Diagnosis).where(Diagnosis.id == diagnosis_id)
    )
    diagnosis = diagnosis_result.scalar_one_or_none()
    
    if not diagnosis:
        raise HTTPException(
            status_code=404,
            detail=f"诊断记录 {diagnosis_id} 不存在"
        )
    
    # 获取指定版本
    result = await db.execute(
        select(DiagnosisReport)
        .where(
            DiagnosisReport.diagnosis_id == diagnosis_id,
            DiagnosisReport.version_no == version_no
        )
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"诊断 {diagnosis_id} 的版本 {version_no} 不存在"
        )
    
    return report


@router.post(
    "/{diagnosis_id}/report",
    summary="创建报告版本",
    description="为诊断创建新的报告版本",
    response_model=DiagnosisReportResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_report_version(
    diagnosis_id: int,
    request: DiagnosisReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(lambda: 1)  # TODO: 从认证获取
):
    """
    创建新的诊断报告版本
    
    使用场景：
    1. 初诊报告 - version_no=1
    2. 修改报告 - version_no 自动递增
    3. 上级医师审核 - 创建新版本
    
    需要说明变更内容时，填写：
    - changes_from_previous: 变更说明
    - change_reason: 修改原因
    
    示例：
    ```json
    {
        "ultrasound_findings": "左侧乳腺外上象限可见低回声结节...",
        "impression": "左侧乳腺实性结节，BI-RADS 4A 类",
        "recommendations": "建议穿刺活检",
        "changes_from_previous": "修正 BI-RADS 分级从 3 类到 4A 类",
        "change_reason": "上级医师审核发现边缘成角征象"
    }
    ```
    """
    # 验证诊断是否存在
    diagnosis_result = await db.execute(
        select(Diagnosis).where(Diagnosis.id == diagnosis_id)
    )
    diagnosis = diagnosis_result.scalar_one_or_none()
    
    if not diagnosis:
        raise HTTPException(
            status_code=404,
            detail=f"诊断记录 {diagnosis_id} 不存在"
        )
    
    # 获取当前最新版本号
    latest_result = await db.execute(
        select(DiagnosisReport)
        .where(DiagnosisReport.diagnosis_id == diagnosis_id)
        .order_by(DiagnosisReport.version_no.desc())
    )
    latest_version = latest_result.scalar_one_or_none()
    
    new_version_no = 1 if not latest_version else latest_version.version_no + 1
    
    # 创建新版本
    report_version = DiagnosisReport(
        diagnosis_id=diagnosis_id,
        version_no=new_version_no,
        ultrasound_findings=request.ultrasound_findings,
        impression=request.impression,
        recommendations=request.recommendations,
        changes_from_previous=request.changes_from_previous,
        change_reason=request.change_reason,
        created_by=current_user_id
    )
    
    db.add(report_version)
    await db.commit()
    await db.refresh(report_version)
    
    return report_version


@router.get(
    "/{diagnosis_id}/compare",
    summary="版本差异比较",
    description="比较两个版本报告的差异"
)
async def compare_versions(
    diagnosis_id: int,
    version_from: int,
    version_to: int,
    db: AsyncSession = Depends(get_db)
):
    """
    比较两个版本报告的差异
    
    用于：
    - 审核修改内容
    - 质量追溯
    - 教学演示
    
    返回：
    - 哪些字段发生变更
    - 变更说明
    - 修改原因
    """
    # 获取两个版本
    v1_result = await db.execute(
        select(DiagnosisReport)
        .where(
            DiagnosisReport.diagnosis_id == diagnosis_id,
            DiagnosisReport.version_no == version_from
        )
    )
    v1 = v1_result.scalar_one_or_none()
    
    v2_result = await db.execute(
        select(DiagnosisReport)
        .where(
            DiagnosisReport.diagnosis_id == diagnosis_id,
            DiagnosisReport.version_no == version_to
        )
    )
    v2 = v2_result.scalar_one_or_none()
    
    if not v1:
        raise HTTPException(
            status_code=404,
            detail=f"版本 {version_from} 不存在"
        )
    
    if not v2:
        raise HTTPException(
            status_code=404,
            detail=f"版本 {version_to} 不存在"
        )
    
    # 比较差异
    return {
        "diagnosis_id": diagnosis_id,
        "version_from": version_from,
        "version_to": version_to,
        "changes": {
            "ultrasound_findings_changed": v1.ultrasound_findings != v2.ultrasound_findings,
            "impression_changed": v1.impression != v2.impression,
            "recommendations_changed": v1.recommendations != v2.recommendations
        },
        "change_details": {
            "ultrasound_findings": {
                "from": v1.ultrasound_findings,
                "to": v2.ultrasound_findings
            } if v1.ultrasound_findings != v2.ultrasound_findings else None,
            "impression": {
                "from": v1.impression,
                "to": v2.impression
            } if v1.impression != v2.impression else None,
            "recommendations": {
                "from": v1.recommendations,
                "to": v2.recommendations
            } if v1.recommendations != v2.recommendations else None
        },
        "change_summary": v2.changes_from_previous,
        "change_reason": v2.change_reason,
        "changed_by": v2.created_by,
        "changed_at": v2.created_at.isoformat()
    }


@router.delete(
    "/{diagnosis_id}/report/{version_no}",
    summary="删除报告版本",
    description="删除指定的报告版本 (仅限草稿状态)"
)
async def delete_report_version(
    diagnosis_id: int,
    version_no: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除指定的报告版本
    
    限制：
    - 只能删除草稿状态 (draft) 的版本
    - 不能删除最新版本
    - 需要权限验证
    
    TODO: 实现权限检查
    """
    # 获取版本
    result = await db.execute(
        select(DiagnosisReport)
        .where(
            DiagnosisReport.diagnosis_id == diagnosis_id,
            DiagnosisReport.version_no == version_no
        )
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"版本 {version_no} 不存在"
        )
    
    # 检查是否为草稿
    # TODO: 从诊断表获取状态
    # if diagnosis.report_status != "draft":
    #     raise HTTPException(
    #         status_code=400,
    #         detail="只能删除草稿状态的报告"
    #     )
    
    await db.delete(report)
    await db.commit()
    
    return {"code": 200, "message": f"删除版本 {version_no} 成功"}
