from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from datetime import datetime, date
from pydantic import BaseModel, Field

from app.data.models.data_management_model import (
    ModelWeight, TrainingDataset, PublicDataset,
    InferenceRecord, Report, FollowupRecord,
    model_dataset_relation
)


# ============= Pydantic 模型 =============

class ModelWeightCreate(BaseModel):
    model_name: str
    model_code: str
    version: str
    branch: str
    weight_file: Optional[str] = None
    file_size_mb: Optional[float] = None
    training_data_source: Optional[str] = None
    training_data_count: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None
    ethics_approval_no: Optional[str] = None


class ModelWeightUpdate(BaseModel):
    model_name: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None
    metrics: Optional[Dict[str, Any]] = None


class TrainingDatasetCreate(BaseModel):
    dataset_name: str
    dataset_code: str
    dataset_type: str
    source_type: str
    source_name: str
    source_region: str
    total_count: int
    data_format: str
    annotation_type: str
    ethics_approval_no: Optional[str] = None


class InferenceRecordCreate(BaseModel):
    model_id: int
    patient_id: int
    visit_id: Optional[int] = None
    inference_type: str
    input_data: str
    output_data: str
    result: Dict[str, Any]
    confidence: float
    inference_time_ms: int
    created_by: int


class ReportCreate(BaseModel):
    report_no: str
    report_type: str
    patient_id: Optional[int] = None
    visit_id: Optional[int] = None
    diagnosis_id: Optional[int] = None
    title: str
    content: str
    summary: Optional[str] = None
    ai_assisted: bool = False
    ai_model_used: Optional[str] = None
    ai_confidence: Optional[float] = None


class FollowupRecordCreate(BaseModel):
    visit_id: int
    patient_id: int
    followup_date: date
    followup_type: str
    chief_complaint: Optional[str] = None
    symptoms: Optional[Dict[str, Any]] = None
    tcm_syndrome: Optional[str] = None
    tcm_prescription: Optional[str] = None
    conclusion: Optional[str] = None
    next_followup_date: Optional[date] = None
    completed_by: int


# ============= 服务类 =============

class ModelWeightService:
    """模型权重服务"""
    
    @staticmethod
    async def get_all(
        session: AsyncSession,
        branch: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 100
    ) -> List[ModelWeight]:
        """获取所有模型权重"""
        query = select(ModelWeight)
        
        if branch:
            query = query.where(ModelWeight.branch == branch)
        if is_active is not None:
            query = query.where(ModelWeight.is_active == is_active)
        
        query = query.order_by(ModelWeight.created_at.desc()).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_id(session: AsyncSession, weight_id: int) -> Optional[ModelWeight]:
        """根据 ID 获取"""
        result = await session.execute(
            select(ModelWeight).where(ModelWeight.id == weight_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_code(session: AsyncSession, model_code: str) -> Optional[ModelWeight]:
        """根据编码获取"""
        result = await session.execute(
            select(ModelWeight).where(ModelWeight.model_code == model_code)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(
        session: AsyncSession,
        data: ModelWeightCreate
    ) -> ModelWeight:
        """创建模型权重"""
        weight = ModelWeight(**data.dict())
        session.add(weight)
        await session.flush()
        await session.commit()
        await session.refresh(weight)
        return weight
    
    @staticmethod
    async def update(
        session: AsyncSession,
        weight_id: int,
        data: ModelWeightUpdate
    ) -> Optional[ModelWeight]:
        """更新模型权重"""
        update_data = {k: v for k, v in data.dict().items() if v is not None}
        if not update_data:
            return await ModelWeightService.get_by_id(session, weight_id)
        
        await session.execute(
            update(ModelWeight)
            .where(ModelWeight.id == weight_id)
            .values(**update_data, updated_at=datetime.utcnow())
        )
        await session.commit()
        return await ModelWeightService.get_by_id(session, weight_id)
    
    @staticmethod
    async def get_statistics(session: AsyncSession) -> Dict[str, Any]:
        """获取统计信息"""
        # 总数
        total_result = await session.execute(
            select(func.count(ModelWeight.id))
        )
        total = total_result.scalar()
        
        # 按分支统计
        branch_result = await session.execute(
            select(ModelWeight.branch, func.count(ModelWeight.id))
            .group_by(ModelWeight.branch)
        )
        by_branch = dict(branch_result.all())
        
        # 总存储大小
        size_result = await session.execute(
            select(func.sum(ModelWeight.file_size_mb))
            .where(ModelWeight.is_active == True)
        )
        total_size = size_result.scalar() or 0
        
        return {
            "total": total,
            "by_branch": by_branch,
            "total_size_mb": total_size,
        }


class TrainingDatasetService:
    """训练数据集服务"""
    
    @staticmethod
    async def get_all(
        session: AsyncSession,
        dataset_type: Optional[str] = None,
        source_type: Optional[str] = None,
        limit: int = 100
    ) -> List[TrainingDataset]:
        """获取所有数据集"""
        query = select(TrainingDataset).where(TrainingDataset.is_deleted == False)
        
        if dataset_type:
            query = query.where(TrainingDataset.dataset_type == dataset_type)
        if source_type:
            query = query.where(TrainingDataset.source_type == source_type)
        
        query = query.order_by(TrainingDataset.created_at.desc()).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_id(session: AsyncSession, dataset_id: int) -> Optional[TrainingDataset]:
        """根据 ID 获取"""
        result = await session.execute(
            select(TrainingDataset)
            .where(TrainingDataset.id == dataset_id, TrainingDataset.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(
        session: AsyncSession,
        data: TrainingDatasetCreate
    ) -> TrainingDataset:
        """创建数据集"""
        dataset = TrainingDataset(**data.dict())
        session.add(dataset)
        await session.flush()
        await session.commit()
        await session.refresh(dataset)
        return dataset
    
    @staticmethod
    async def link_to_model(
        session: AsyncSession,
        model_id: int,
        dataset_id: int
    ) -> bool:
        """关联模型和数据集"""
        try:
            await session.execute(
                model_dataset_relation.insert().values(
                    model_id=model_id,
                    dataset_id=dataset_id
                )
            )
            await session.commit()
            return True
        except Exception:
            await session.rollback()
            return False


class PublicDatasetService:
    """公开数据集服务"""
    
    @staticmethod
    async def get_all(
        session: AsyncSession,
        modality: Optional[str] = None,
        is_downloaded: Optional[bool] = None,
        limit: int = 100
    ) -> List[PublicDataset]:
        """获取所有公开数据集"""
        query = select(PublicDataset).where(PublicDataset.is_deleted == False)
        
        if modality:
            query = query.where(PublicDataset.modality == modality)
        if is_downloaded is not None:
            query = query.where(PublicDataset.is_downloaded == is_downloaded)
        
        query = query.order_by(PublicDataset.publish_year.desc()).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def mark_as_downloaded(
        session: AsyncSession,
        dataset_id: int
    ) -> bool:
        """标记为已下载"""
        try:
            await session.execute(
                update(PublicDataset)
                .where(PublicDataset.id == dataset_id)
                .values(
                    is_downloaded=True,
                    download_date=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            )
            await session.commit()
            return True
        except Exception:
            await session.rollback()
            return False


class InferenceRecordService:
    """推理记录服务"""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        data: InferenceRecordCreate
    ) -> InferenceRecord:
        """创建推理记录"""
        record = InferenceRecord(**data.dict())
        session.add(record)
        await session.flush()
        await session.commit()
        await session.refresh(record)
        return record
    
    @staticmethod
    async def get_by_model(
        session: AsyncSession,
        model_id: int,
        limit: int = 50
    ) -> List[InferenceRecord]:
        """获取模型的推理记录"""
        result = await session.execute(
            select(InferenceRecord)
            .where(InferenceRecord.model_id == model_id)
            .order_by(InferenceRecord.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_patient(
        session: AsyncSession,
        patient_id: int,
        limit: int = 50
    ) -> List[InferenceRecord]:
        """获取患者的推理记录"""
        result = await session.execute(
            select(InferenceRecord)
            .where(InferenceRecord.patient_id == patient_id)
            .order_by(InferenceRecord.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_statistics(
        session: AsyncSession,
        model_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """获取推理统计"""
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(
            func.date(InferenceRecord.created_at).label('date'),
            func.count(InferenceRecord.id).label('count'),
            func.avg(InferenceRecord.confidence).label('avg_confidence'),
            func.avg(InferenceRecord.inference_time_ms).label('avg_time')
        ).where(
            InferenceRecord.created_at >= start_date
        )
        
        if model_id:
            query = query.where(InferenceRecord.model_id == model_id)
        
        query = query.group_by(func.date(InferenceRecord.created_at))
        result = await session.execute(query)
        
        daily_stats = [
            {
                "date": str(row.date),
                "count": row.count,
                "avg_confidence": float(row.avg_confidence) if row.avg_confidence else 0,
                "avg_time_ms": float(row.avg_time) if row.avg_time else 0,
            }
            for row in result.fetchall()
        ]
        
        return {"daily_stats": daily_stats}


class ReportService:
    """报告服务"""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        data: ReportCreate,
        created_by: int
    ) -> Report:
        """创建报告"""
        report = Report(**data.dict(), created_by=created_by)
        
        # 生成报告编号
        if not report.report_no:
            today = date.today().strftime("%Y%m%d")
            result = await session.execute(
                select(func.max(Report.report_no))
                .where(Report.report_no.like(f"RPT-{today}%"))
            )
            max_no = result.scalar()
            if max_no:
                next_seq = int(max_no.split("-")[-1]) + 1
            else:
                next_seq = 1
            report.report_no = f"RPT-{today}-{next_seq:04d}"
        
        session.add(report)
        await session.flush()
        await session.commit()
        await session.refresh(report)
        return report
    
    @staticmethod
    async def get_by_id(session: AsyncSession, report_id: int) -> Optional[Report]:
        """根据 ID 获取"""
        result = await session.execute(
            select(Report).where(Report.id == report_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def publish(
        session: AsyncSession,
        report_id: int,
        reviewed_by: int
    ) -> bool:
        """发布报告"""
        try:
            await session.execute(
                update(Report)
                .where(Report.id == report_id)
                .values(
                    status='published',
                    reviewed_by=reviewed_by,
                    reviewed_at=datetime.utcnow(),
                    published_at=datetime.utcnow()
                )
            )
            await session.commit()
            return True
        except Exception:
            await session.rollback()
            return False


class FollowupRecordService:
    """随访记录服务"""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        data: FollowupRecordCreate
    ) -> FollowupRecord:
        """创建随访记录"""
        record = FollowupRecord(**data.dict())
        session.add(record)
        await session.flush()
        await session.commit()
        await session.refresh(record)
        return record
    
    @staticmethod
    async def get_by_patient(
        session: AsyncSession,
        patient_id: int,
        limit: int = 50
    ) -> List[FollowupRecord]:
        """获取患者的随访记录"""
        result = await session.execute(
            select(FollowupRecord)
            .where(FollowupRecord.patient_id == patient_id)
            .order_by(FollowupRecord.followup_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_overdue_followups(
        session: AsyncSession,
        days: int = 7
    ) -> List[FollowupRecord]:
        """获取超期未随访记录"""
        from datetime import timedelta
        cutoff_date = date.today() - timedelta(days=days)
        
        result = await session.execute(
            select(FollowupRecord)
            .where(
                FollowupRecord.next_followup_date < date.today(),
                FollowupRecord.is_lost == False,
                FollowupRecord.is_deleted == False
            )
            .order_by(FollowupRecord.next_followup_date)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def mark_as_lost(
        session: AsyncSession,
        record_id: int,
        reason: str
    ) -> bool:
        """标记为失访"""
        try:
            await session.execute(
                update(FollowupRecord)
                .where(FollowupRecord.id == record_id)
                .values(
                    is_lost=True,
                    lost_reason=reason,
                    last_contact_date=date.today()
                )
            )
            await session.commit()
            return True
        except Exception:
            await session.rollback()
            return False
