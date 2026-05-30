"""
影像 - 中医病机分析 API 路由

研究用途：基于超声影像特征的中医病机倾向分析
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.schemas.imaging_tcm import (
    TCMAnalysisResponse,
    PathomechanismTendency,
    ImagingFeaturesInput,
)
from app.services.imaging_tcm_service import ImagingTCMService
from app.models.imaging_tcm import ImagingTCMCorrelation


router = APIRouter(prefix="/imaging-tcm", tags=["影像 - 中医病机分析"])


@router.post(
    "/ultrasound/{ultrasound_id}/analyze",
    response_model=TCMAnalysisResponse,
    summary="超声影像中医病机分析",
    description="""
**研究用途**：基于超声影像特征进行中医病机倾向分析

⚠️ **重要声明**：
- 本功能为研究性质，证据等级有限（B/C 级）
- 分析结果仅供参考，不能作为辨证依据
- 必须结合四诊信息（舌象、脉象、问诊）进行综合判断
- 仅供执业中医师参考使用

## 分析流程

1. 提取超声影像特征（边界、形态、回声、血流、弹性等）
2. 应用循证规则引擎（20+ 项特征规则）
3. 计算病机倾向评分（瘀血/痰浊/毒邪/正虚）
4. 生成综合判断和治疗建议

## 输出内容

- 病机倾向评分（0-1）
- 证据摘要（基于哪些特征）
- 病机组合模式
- 病性判断（虚实）
- 推荐治法与方剂（仅供参考）
    """
)
async def analyze_ultrasound_tcm(
    ultrasound_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    对指定超声检查进行中医病机分析
    """
    service = ImagingTCMService()
    
    # 执行分析
    correlation = await service.analyze_ultrasound(db, ultrasound_id)
    
    if not correlation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到超声检查记录 (ID={ultrasound_id})"
        )
    
    return correlation.to_dict()


@router.get(
    "/ultrasound/{ultrasound_id}/result",
    response_model=TCMAnalysisResponse,
    summary="获取中医病机分析结果"
)
async def get_tcm_analysis_result(
    ultrasound_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    获取已完成的中医病机分析结果
    
    如果尚未分析，将自动触 发分析
    """
    # 查询已有结果
    result = await db.execute(
        select(ImagingTCMCorrelation).where(
            ImagingTCMCorrelation.ultrasound_id == ultrasound_id
        )
    )
    correlation = result.scalar_one_or_none()
    
    # 如果没有，触发分析
    if not correlation:
        service = ImagingTCMService()
        correlation = await service.analyze_ultrasound(db, ultrasound_id)
    
    if not correlation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到超声检查记录"
        )
    
    return correlation.to_dict()


@router.get(
    "/patient/{patient_id}/history",
    response_model=List[TCMAnalysisResponse],
    summary="患者中医病机分析历史"
)
async def get_patient_tcm_history(
    patient_id: int,
    limit: int = Query(10, ge=1, le=100, description="返回数量限制"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取患者的中医病机分析历史记录
    
    用于追踪病机演变趋势
    """
    result = await db.execute(
        select(ImagingTCMCorrelation)
        .where(ImagingTCMCorrelation.patient_id == patient_id)
        .order_by(ImagingTCMCorrelation.created_at.desc())
        .limit(limit)
    )
    correlations = result.scalars().all()
    
    return [c.to_dict() for c in correlations]


@router.post(
    "/batch/analyze",
    summary="批量分析",
    description="批量分析多个超声检查（用于回顾性研究）"
)
async def batch_analyze(
    ultrasound_ids: List[int],
    db: AsyncSession = Depends(get_db),
):
    """
    批量分析多个超声检查
    
    用于回顾性研究或数据迁移
    """
    service = ImagingTCMService()
    results = []
    failed = []
    
    for us_id in ultrasound_ids:
        try:
            correlation = await service.analyze_ultrasound(db, us_id)
            if correlation:
                results.append(correlation.to_dict())
            else:
                failed.append(us_id)
        except Exception as e:
            failed.append(us_id)
    
    return {
        "results": results,
        "success_count": len(results),
        "failed_count": len(failed),
        "failed_ids": failed,
    }


@router.put(
    "/correlation/{correlation_id}/review",
    summary="审核分析结果",
    description="由执业中医师审核分析结果"
)
async def review_correlation(
    correlation_id: int,
    reviewed: bool,
    review_notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    审核中医病机分析结果
    
    由执业中医师确认或修正自动分析结果
    """
    result = await db.execute(
        select(ImagingTCMCorrelation).where(
            ImagingTCMCorrelation.id == correlation_id
        )
    )
    correlation = result.scalar_one_or_none()
    
    if not correlation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到分析记录"
        )
    
    # 更新审核状态
    correlation.reviewed = reviewed
    # correlation.reviewed_by = current_user.id  # 需要认证后再启用
    correlation.review_notes = review_notes
    correlation.review_date = datetime.utcnow()
    
    await db.commit()
    await db.refresh(correlation)
    
    return {
        "id": correlation.id,
        "reviewed": reviewed,
        "reviewed_by": None,  # current_user.username,  # 需要认证后再启用
        "review_date": correlation.review_date.isoformat(),
        "review_notes": review_notes,
    }


@router.get(
    "/statistics/evidence-level",
    summary="证据等级统计"
)
async def get_evidence_level_statistics(
    db: AsyncSession = Depends(get_db),
):
    """
    统计各证据等级的分析结果分布
    
    用于质量控制和研究
    """
    from sqlalchemy import func
    
    result = await db.execute(
        select(
            ImagingTCMCorrelation.overall_evidence_level,
            func.count(ImagingTCMCorrelation.id)
        )
        .group_by(ImagingTCMCorrelation.overall_evidence_level)
    )
    
    stats = {row[0]: row[1] for row in result.all()}
    
    return {
        "evidence_level_distribution": stats,
        "total_count": sum(stats.values()),
    }


@router.get(
    "/help/pathomechanism",
    summary="病机术语解释"
)
async def get_pathomechanism_help():
    """
    获取中医病机术语解释
    
    帮助西医医生理解中医病机概念
    """
    return {
        "pathomechanisms": {
            "stasis": {
                "name": "瘀血",
                "definition": "血液运行不畅或离经之血积存体内",
                "imaging_features": "边界不清、形态不规则、低回声、丰富血流",
                "clinical_manifestations": "肿块质硬、固定、刺痛、舌质紫黯"
            },
            "phlegm": {
                "name": "痰浊",
                "definition": "水液代谢障碍形成的病理产物",
                "imaging_features": "囊性、钙化、边界清晰",
                "clinical_manifestations": "体胖痰多、胸闷、苔腻"
            },
            "toxin": {
                "name": "毒邪",
                "definition": "致病力强的邪气，常为热极生毒",
                "imaging_features": "毛刺征、微钙化、弹性评分高、快速生长",
                "clinical_manifestations": "肿块坚硬、疼痛、发热、舌红苔黄"
            },
            "deficiency": {
                "name": "正虚",
                "definition": "正气不足，抗病能力下降",
                "imaging_features": "边界清晰、生长缓慢、后方回声衰减",
                "clinical_manifestations": "乏力、气短、面色无华、脉弱"
            }
        }
    }
