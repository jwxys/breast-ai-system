"""
统计分析模块

提供 BI-RADS 分布、准确率、质控指标等统计功能
"""

from .services.stats_service import StatisticsService

__all__ = ["StatisticsService"]
