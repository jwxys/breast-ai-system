"""
统计分析服务 - 完整实现

提供 BI-RADS 分布、准确率、质控指标等统计功能
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Dict, Optional
from datetime import datetime


class StatisticsService:
    """统计分析服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_birads_distribution(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """BI-RADS 分级分布统计"""
        from app.diagnosis.models.diagnosis_model import Diagnosis
        
        query = select(
            Diagnosis.birads_category,
            func.count().label('count')
        ).group_by(Diagnosis.birads_category)
        
        if start_date:
            query = query.where(Diagnosis.created_at >= start_date)
        if end_date:
            query = query.where(Diagnosis.created_at <= end_date)
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        distribution = {"0": 0, "1": 0, "2": 0, "3": 0, "4A": 0, "4B": 0, "4C": 0, "5": 0, "6": 0}
        for row in rows:
            if row[0] in distribution:
                distribution[row[0]] = row[1]
        
        total = sum(distribution.values())
        percentages = {k: (v / total * 100) if total > 0 else 0 for k, v in distribution.items()}
        
        return {"distribution": distribution, "percentages": percentages, "total": total}
    
    async def get_accuracy_metrics(self, start_date: Optional[datetime] = None) -> Dict:
        """AI 诊断准确率统计"""
        from app.diagnosis.models.diagnosis_model import Diagnosis
        
        query = select(Diagnosis).where(
            Diagnosis.pathology_performed == True,
            Diagnosis.ai_assisted == True
        )
        if start_date:
            query = query.where(Diagnosis.created_at >= start_date)
        
        result = await self.db.execute(query)
        diagnoses = result.scalars().all()
        
        tp = fp = tn = fn = 0
        birads_high_risk = {"4C", "5", "6"}
        
        for d in diagnoses:
            ai_malignant = d.ai_birads_prediction in birads_high_risk
            pathology_malignant = d.molecular_subtype in ["Basal-like", "HER2-enriched"]
            
            if ai_malignant and pathology_malignant: tp += 1
            elif ai_malignant and not pathology_malignant: fp += 1
            elif not ai_malignant and not pathology_malignant: tn += 1
            else: fn += 1
        
        total = tp + tn + fp + fn or 1
        return {
            "accuracy": (tp + tn) / total,
            "sensitivity": tp / (tp + fn) if (tp + fn) else 0,
            "specificity": tn / (tn + fp) if (tn + fp) else 0,
            "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn}
        }
