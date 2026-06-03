"""
统计分析 API

提供 BI-RADS 分布、准确率、质控指标等统计接口
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.statistics.services.stats_service import StatisticsService


router = APIRouter(prefix="/api/v1/statistics", tags=["统计分析"])


@router.get("/birads-distribution", summary="BI-RADS 分布统计")
async def get_birads_distribution(
    days: int = Query(30, description="统计天数"),
    db: AsyncSession = Depends(get_db)
):
    """
    BI-RADS 分级分布统计
    
    支持按时间范围统计
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    service = StatisticsService(db)
    return await service.get_birads_distribution(start_date, end_date)


@router.get("/accuracy-metrics", summary="AI 准确率统计")
async def get_accuracy_metrics(
    days: int = Query(90, description="统计天数"),
    db: AsyncSession = Depends(get_db)
):
    """
    AI 诊断准确率统计
    
    指标包括：
    - 准确率 (accuracy)
    - 敏感度 (sensitivity)
    - 特异度 (specificity)
    - 混淆矩阵
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    service = StatisticsService(db)
    metrics = await service.get_accuracy_metrics(start_date)
    
    return {
        "code": 200,
        "data": metrics,
        "period": f"最近 {days} 天"
    }


@router.get("/quality-control", summary="质控指标")
async def get_quality_control(
    db: AsyncSession = Depends(get_db)
):
    """
    质控指标统计
    
    包括：
    - 报告完整率
    - AI 使用率
    - 审核率
    - 活检率
    """
    service = StatisticsService(db)
    return await service.get_quality_control_metrics()


@router.get("/dashboard", summary="统计看板")
async def get_statistics_dashboard(
    days: int = Query(30, description="统计天数"),
    db: AsyncSession = Depends(get_db)
):
    """
    综合统计看板
    
    包含所有核心统计指标的概览
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    service = StatisticsService(db)
    
    # 并行获取各项统计
    birads_dist = await service.get_birads_distribution(start_date, end_date)
    accuracy = await service.get_accuracy_metrics(start_date)
    qc_metrics = await service.get_quality_control_metrics()
    
    return {
        "code": 200,
        "data": {
            "birads_distribution": birads_dist,
            "accuracy_metrics": accuracy,
            "quality_control": qc_metrics,
            "period": f"最近 {days} 天"
        }
    }
