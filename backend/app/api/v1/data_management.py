from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os

from app.core.database import get_db
from app.services.data_management_service import (
    ModelWeightService, ModelWeightCreate, ModelWeightUpdate,
    TrainingDatasetService, TrainingDatasetCreate,
    PublicDatasetService,
    InferenceRecordService, InferenceRecordCreate,
    ReportService, ReportCreate,
    FollowupRecordService, FollowupRecordCreate
)
from shared.file_manager import weight_file_manager

router = APIRouter()


# ============= 模型权重管理 =============

@router.get("/weights", summary="获取模型权重列表")
async def get_model_weights(
    branch: Optional[str] = Query(None, description="分支：western/tcm"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    session: AsyncSession = Depends(get_db)
):
    """获取 AI 模型权重列表"""
    weights = await ModelWeightService.get_all(
        session, branch=branch, is_active=is_active
    )
    
    return {
        "code": 200,
        "data": [
            {
                "id": w.id,
                "model_name": w.model_name,
                "model_code": w.model_code,
                "version": w.version,
                "branch": w.branch,
                "weight_file": w.weight_file,
                "file_size_mb": w.file_size_mb,
                "training_data_count": w.training_data_count,
                "metrics": w.metrics,
                "ethics_approval_no": w.ethics_approval_no,
                "is_active": w.is_active,
                "is_published": w.is_published,
            }
            for w in weights
        ]
    }


@router.get("/weights/stats", summary="获取模型权重统计")
async def get_model_weights_stats(
    session: AsyncSession = Depends(get_db)
):
    """获取模型权重统计信息"""
    stats = await ModelWeightService.get_statistics(session)
    return {"code": 200, "data": stats}


@router.get("/weights/{weight_id}", summary="获取模型权重详情")
async def get_model_weight(
    weight_id: int,
    session: AsyncSession = Depends(get_db)
):
    """获取 AI 模型权重详情"""
    weight = await ModelWeightService.get_by_id(session, weight_id)
    
    if not weight:
        raise HTTPException(status_code=404, detail="模型权重不存在")
    
    return {
        "code": 200,
        "data": {
            "id": weight.id,
            "model_name": weight.model_name,
            "model_code": weight.model_code,
            "version": weight.version,
            "branch": weight.branch,
            "weight_file": weight.weight_file,
            "file_size_mb": weight.file_size_mb,
            "training_data_source": weight.training_data_source,
            "training_data_count": weight.training_data_count,
            "metrics": weight.metrics,
            "ethics_approval_no": weight.ethics_approval_no,
            "is_active": weight.is_active,
            "is_published": weight.is_published,
        }
    }


@router.post("/weights", summary="创建模型权重")
async def create_model_weight(
    data: ModelWeightCreate,
    session: AsyncSession = Depends(get_db)
):
    """创建新的 AI 模型权重记录"""
    existing = await ModelWeightService.get_by_code(session, data.model_code)
    if existing:
        raise HTTPException(status_code=400, detail="模型编码已存在")
    
    weight = await ModelWeightService.create(session, data)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": {"id": weight.id, "model_code": weight.model_code}
    }


@router.post("/weights/{weight_id}/upload", summary="上传权重文件")
async def upload_weight_file(
    weight_id: int,
    file: UploadFile = File(..., description="权重文件"),
    version: str = Form(..., description="版本号"),
    session: AsyncSession = Depends(get_db)
):
    """
    上传 AI 模型权重文件
    
    - **weight_id**: 权重记录 ID
    - **file**: 权重文件 (.pth, .pt, .bin, .onnx, .json)
    - **version**: 版本号
    """
    # 获取模型信息
    weight = await ModelWeightService.get_by_id(session, weight_id)
    if not weight:
        raise HTTPException(status_code=404, detail="权重记录不存在")
    
    try:
        # 上传文件
        result = await weight_file_manager.upload_weight(
            file=file,
            model_code=weight.model_code,
            version=version,
            session=session
        )
        
        return {
            "code": 200,
            "message": "上传成功",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weights/{weight_id}/load", summary="加载权重到内存")
async def load_model_weight(
    weight_id: int,
    session: AsyncSession = Depends(get_db)
):
    """加载权重文件到推理引擎"""
    weight = await ModelWeightService.get_by_id(session, weight_id)
    if not weight:
        raise HTTPException(status_code=404, detail="权重记录不存在")
    
    if not weight.file_path:
        raise HTTPException(status_code=400, detail="权重文件未上传")
    
    try:
        from services.inference_service import inference_engine
        
        # 这里需要根据模型类型选择对应的模型类
        # 简化处理，只加载不实例化
        weight_path = str(weight_file_manager.WEIGHTS_DIR / weight.weight_file)
        
        if os.path.exists(weight_path):
            # TODO: 实际加载模型需要模型类定义
            return {
                "code": 200,
                "message": "权重文件存在，可加载",
                "data": {
                    "path": weight_path,
                    "size_mb": weight.file_size_mb,
                    "device": "cpu"  # 实际应该根据配置
                }
            }
        else:
            raise HTTPException(status_code=404, detail="权重文件不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weights/storage/stats", summary="获取存储统计")
async def get_storage_stats():
    """获取权重文件存储统计"""
    stats = weight_file_manager.get_storage_stats()
    return {"code": 200, "data": stats}


@router.get("/weights/{weight_id}", summary="获取模型权重详情")
async def get_model_weight(
    weight_id: int,
    session: AsyncSession = Depends(get_db)
):
    """获取 AI 模型权重详情"""
    result = await session.execute(
        select(ModelWeight).where(ModelWeight.id == weight_id)
    )
    weight = result.scalar_one_or_none()
    
    if not weight:
        raise HTTPException(status_code=404, detail="模型权重不存在")
    
    return {
        "code": 200,
        "data": {
            "id": weight.id,
            "model_name": weight.model_name,
            "model_code": weight.model_code,
            "version": weight.version,
            "branch": weight.branch,
            "weight_file": weight.weight_file,
            "file_size_mb": weight.file_size_mb,
            "training_data_source": weight.training_data_source,
            "training_data_count": weight.training_data_count,
            "training_start_date": weight.training_start_date,
            "training_end_date": weight.training_end_date,
            "metrics": weight.metrics,
            "ethics_approval_no": weight.ethics_approval_no,
            "ethics_approval_date": weight.ethics_approval_date,
            "is_active": weight.is_active,
            "is_published": weight.is_published,
            "created_at": weight.created_at,
        }
    }


# ============= 训练数据集管理 =============

@router.get("/datasets", summary="获取训练数据集列表")
async def get_training_datasets(
    dataset_type: Optional[str] = Query(None, description="数据类型"),
    source_type: Optional[str] = Query(None, description="来源类型"),
    session: AsyncSession = Depends(get_db)
):
    """获取训练数据集列表"""
    datasets = await TrainingDatasetService.get_all(
        session, dataset_type=dataset_type, source_type=source_type
    )
    
    return {
        "code": 200,
        "data": [
            {
                "id": d.id,
                "dataset_name": d.dataset_name,
                "dataset_code": d.dataset_code,
                "dataset_type": d.dataset_type,
                "source_type": d.source_type,
                "source_name": d.source_name,
                "source_region": d.source_region,
                "total_count": d.total_count,
                "train_count": d.train_count,
                "val_count": d.val_count,
                "test_count": d.test_count,
                "data_format": d.data_format,
                "ethics_approval_no": d.ethics_approval_no,
            }
            for d in datasets
        ]
    }


@router.get("/datasets/{dataset_id}", summary="获取训练数据集详情")
async def get_training_dataset(
    dataset_id: int,
    session: AsyncSession = Depends(get_db)
):
    """获取训练数据集详情"""
    dataset = await TrainingDatasetService.get_by_id(session, dataset_id)
    
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    return {
        "code": 200,
        "data": {
            "id": dataset.id,
            "dataset_name": dataset.dataset_name,
            "dataset_code": dataset.dataset_code,
            "dataset_type": dataset.dataset_type,
            "source_type": dataset.source_type,
            "source_name": dataset.source_name,
            "total_count": dataset.total_count,
        }
    }


@router.post("/datasets", summary="创建训练数据集")
async def create_training_dataset(
    data: TrainingDatasetCreate,
    session: AsyncSession = Depends(get_db)
):
    """创建新的训练数据集"""
    dataset = await TrainingDatasetService.create(session, data)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": {"id": dataset.id, "dataset_code": dataset.dataset_code}
    }


@router.post("/datasets/{dataset_id}/link-model", summary="关联模型和数据集")
async def link_model_dataset(
    dataset_id: int,
    model_id: int = Query(..., description="模型 ID"),
    session: AsyncSession = Depends(get_db)
):
    """将数据集关联到模型"""
    success = await TrainingDatasetService.link_to_model(session, model_id, dataset_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="关联失败")
    
    return {"code": 200, "message": "关联成功"}


# ============= 公开数据集管理 =============

@router.get("/public-datasets", summary="获取公开数据集列表")
async def get_public_datasets(
    modality: Optional[str] = Query(None, description="影像模态"),
    is_downloaded: Optional[bool] = Query(None, description="是否已下载"),
    session: AsyncSession = Depends(get_db)
):
    """获取公开数据集列表"""
    datasets = await PublicDatasetService.get_all(
        session, modality=modality, is_downloaded=is_downloaded
    )
    
    return {
        "code": 200,
        "data": [
            {
                "id": d.id,
                "dataset_name": d.dataset_name,
                "publisher": d.publisher,
                "publish_year": d.publish_year,
                "modality": d.modality,
                "image_count": d.image_count,
                "storage_size_gb": d.storage_size_gb,
                "is_downloaded": d.is_downloaded,
            }
            for d in datasets
        ]
    }


@router.post("/public-datasets/{dataset_id}/download", summary="标记公开数据集已下载")
async def mark_public_dataset_downloaded(
    dataset_id: int,
    session: AsyncSession = Depends(get_db)
):
    """标记公开数据集为已下载"""
    success = await PublicDatasetService.mark_as_downloaded(session, dataset_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="操作失败")
    
    return {"code": 200, "message": "已标记为下载"}


# ============= 推理记录管理 =============

@router.get("/inference-records", summary="获取推理记录列表")
async def get_inference_records(
    model_id: Optional[int] = Query(None, description="模型 ID"),
    patient_id: Optional[int] = Query(None, description="患者 ID"),
    limit: int = Query(50, le=200, description="返回数量限制"),
    session: AsyncSession = Depends(get_db)
):
    """获取模型推理记录"""
    if model_id:
        records = await InferenceRecordService.get_by_model(session, model_id, limit)
    elif patient_id:
        records = await InferenceRecordService.get_by_patient(session, patient_id, limit)
    else:
        records = []
    
    return {
        "code": 200,
        "data": [
            {
                "id": r.id,
                "model_id": r.model_id,
                "patient_id": r.patient_id,
                "inference_type": r.inference_type,
                "confidence": r.confidence,
                "inference_time_ms": r.inference_time_ms,
                "created_at": r.created_at.isoformat(),
            }
            for r in records
        ]
    }


@router.post("/inference-records", summary="创建推理记录")
async def create_inference_record(
    data: InferenceRecordCreate,
    session: AsyncSession = Depends(get_db)
):
    """创建推理记录"""
    record = await InferenceRecordService.create(session, data)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": {"id": record.id}
    }


# ============= 报告管理 =============

@router.get("/reports", summary="获取报告列表")
async def get_reports(
    report_type: Optional[str] = Query(None, description="报告类型"),
    patient_id: Optional[int] = Query(None, description="患者 ID"),
    status: Optional[str] = Query(None, description="状态"),
    limit: int = Query(20, le=100, description="返回数量限制"),
    session: AsyncSession = Depends(get_db)
):
    """获取报告列表"""
    # TODO: 实现 ReportService.get_list 方法
    return {"code": 200, "data": []}


@router.post("/reports", summary="创建报告")
async def create_report(
    data: ReportCreate,
    created_by: int = Query(..., description="创建人 ID"),
    session: AsyncSession = Depends(get_db)
):
    """创建报告"""
    report = await ReportService.create(session, data, created_by)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": {"id": report.id, "report_no": report.report_no}
    }


# ============= 随访记录管理 =============

@router.get("/followup-records", summary="获取随访记录列表")
async def get_followup_records(
    patient_id: Optional[int] = Query(None, description="患者 ID"),
    is_lost: Optional[bool] = Query(None, description="是否失访"),
    limit: int = Query(20, le=100, description="返回数量限制"),
    session: AsyncSession = Depends(get_db)
):
    """获取随访记录列表"""
    records = await FollowupRecordService.get_by_patient(session, patient_id, limit) if patient_id else []
    
    return {
        "code": 200,
        "data": [
            {
                "id": r.id,
                "visit_id": r.visit_id,
                "patient_id": r.patient_id,
                "followup_date": str(r.followup_date),
                "followup_type": r.followup_type,
                "conclusion": r.conclusion,
                "is_lost": r.is_lost,
            }
            for r in records
        ]
    }


@router.post("/followup-records", summary="创建随访记录")
async def create_followup_record(
    data: FollowupRecordCreate,
    session: AsyncSession = Depends(get_db)
):
    """创建随访记录"""
    record = await FollowupRecordService.create(session, data)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": {"id": record.id}
    }


@router.get("/followup-records/overdue", summary="获取超期随访")
async def get_overdue_followups(
    days: int = Query(7, description="超期天数"),
    session: AsyncSession = Depends(get_db)
):
    """获取超期未随访记录"""
    records = await FollowupRecordService.get_overdue_followups(session, days)
    
    return {
        "code": 200,
        "data": [
            {
                "id": r.id,
                "patient_id": r.patient_id,
                "next_followup_date": str(r.next_followup_date),
            }
            for r in records
        ]
    }


@router.post("/inference/segmentation", summary="执行 AI 分割推理")
async def execute_segmentation(
    image: UploadFile = File(..., description="医学影像"),
    model_code: str = Form(default="pbs-net", description="模型编码"),
    patient_id: int = Form(..., description="患者 ID"),
    visit_id: Optional[int] = Form(None, description="随访 ID"),
    created_by: int = Form(..., description="操作人 ID"),
    session: AsyncSession = Depends(get_db)
):
    """
    执行 AI 病灶分割推理 (PBS-Net)
    
    - **image**: 上传的医学影像
    - **model_code**: 模型编码 (默认 pbs-net)
    - **patient_id**: 患者 ID
    - **visit_id**: 随访 ID (可选)
    - **created_by**: 操作人 ID
    """
    from services.inference_service import inference_engine
    from shared.file_manager import weight_file_manager
    
    # 保存上传的图像
    uploads_dir = weight_file_manager.UPLOADS_DIR
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    image_path = uploads_dir / f"{patient_id}_{image.filename}"
    
    with open(image_path, 'wb') as f:
        content = await image.read()
        f.write(content)
    
    # 执行推理
    result = await inference_engine.inference_segmentation(
        model_code=model_code,
        image_path=str(image_path),
        patient_id=patient_id,
        visit_id=visit_id,
        created_by=created_by,
        session=session
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return {
        "code": 200,
        "message": "推理成功",
        "data": result
    }


@router.post("/inference/diagnosis", summary="执行 AI 诊断推理")
async def execute_diagnosis(
    image: UploadFile = File(..., description="医学影像"),
    model_code: str = Form(default="dfmfi", description="模型编码"),
    patient_id: int = Form(..., description="患者 ID"),
    visit_id: Optional[int] = Form(None, description="随访 ID"),
    created_by: int = Form(..., description="操作人 ID"),
    session: AsyncSession = Depends(get_db)
):
    """
    执行 AI 诊断推理 (DFMFI/HXM-Net)
    
    - **image**: 上传的医学影像
    - **model_code**: 模型编码 (默认 dfmfi)
    - **patient_id**: 患者 ID
    - **visit_id**: 随访 ID (可选)
    - **created_by**: 操作人 ID
    """
    from services.inference_service import inference_engine
    from shared.file_manager import weight_file_manager
    
    # 保存上传的图像
    uploads_dir = weight_file_manager.UPLOADS_DIR
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    image_path = uploads_dir / f"{patient_id}_{image.filename}"
    
    with open(image_path, 'wb') as f:
        content = await image.read()
        f.write(content)
    
    # 执行推理
    result = await inference_engine.inference_diagnosis(
        model_code=model_code,
        image_path=str(image_path),
        patient_id=patient_id,
        visit_id=visit_id,
        created_by=created_by,
        session=session
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return {
        "code": 200,
        "message": "推理成功",
        "data": result
    }


@router.get("/inference/device/info", summary="获取推理设备信息")
async def get_inference_device_info():
    """获取 AI 推理设备信息"""
    from services.inference_service import inference_engine
    
    return {
        "code": 200,
        "data": inference_engine.get_device_info()
    }


@router.get("/public-datasets/{dataset_id}", summary="获取公开数据集详情")
async def get_public_dataset(
    dataset_id: int,
    session: AsyncSession = Depends(get_db)
):
    """获取公开数据集详情"""
    result = await session.execute(
        select(PublicDataset).where(
            PublicDataset.id == dataset_id,
            PublicDataset.is_deleted == False
        )
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    return {
        "code": 200,
        "data": {
            "id": dataset.id,
            "dataset_name": dataset.dataset_name,
            "dataset_code": dataset.dataset_code,
            "publisher": dataset.publisher,
            "publish_year": dataset.publish_year,
            "journal": dataset.journal,
            "doi": dataset.doi,
            "url": dataset.url,
            "modality": dataset.modality,
            "disease": dataset.disease,
            "image_count": dataset.image_count,
            "patient_count": dataset.patient_count,
            "storage_size_gb": dataset.storage_size_gb,
            "annotation_available": dataset.annotation_available,
            "annotation_type": dataset.annotation_type,
            "license_type": dataset.license_type,
            "access_type": dataset.access_type,
            "description": dataset.description,
            "metadata": dataset.metadata,
        }
    }


# ============= 推理记录管理 =============

@router.get("/inference-records", summary="获取推理记录列表")
async def get_inference_records(
    model_id: Optional[int] = Query(None, description="模型 ID"),
    patient_id: Optional[int] = Query(None, description="患者 ID"),
    limit: int = Query(20, le=100, description="返回数量限制"),
    session: AsyncSession = Depends(get_db)
):
    """获取模型推理记录"""
    query = select(InferenceRecord)
    
    if model_id:
        query = query.where(InferenceRecord.model_id == model_id)
    if patient_id:
        query = query.where(InferenceRecord.patient_id == patient_id)
    
    query = query.order_by(InferenceRecord.created_at.desc()).limit(limit)
    result = await session.execute(query)
    records = result.scalars().all()
    
    return {
        "code": 200,
        "data": [
            {
                "id": r.id,
                "model_id": r.model_id,
                "patient_id": r.patient_id,
                "inference_type": r.inference_type,
                "result": r.result,
                "confidence": r.confidence,
                "inference_time_ms": r.inference_time_ms,
                "created_at": r.created_at,
            }
            for r in records
        ]
    }


# ============= 报告管理 =============

@router.get("/reports", summary="获取报告列表")
async def get_reports(
    report_type: Optional[str] = Query(None, description="报告类型"),
    patient_id: Optional[int] = Query(None, description="患者 ID"),
    status: Optional[str] = Query(None, description="状态"),
    limit: int = Query(20, le=100, description="返回数量限制"),
    session: AsyncSession = Depends(get_db)
):
    """获取报告列表"""
    query = select(Report)
    
    if report_type:
        query = query.where(Report.report_type == report_type)
    if patient_id:
        query = query.where(Report.patient_id == patient_id)
    if status:
        query = query.where(Report.status == status)
    
    query = query.order_by(Report.created_at.desc()).limit(limit)
    result = await session.execute(query)
    reports = result.scalars().all()
    
    return {
        "code": 200,
        "data": [
            {
                "id": r.id,
                "report_no": r.report_no,
                "report_type": r.report_type,
                "patient_id": r.patient_id,
                "title": r.title,
                "summary": r.summary,
                "ai_assisted": r.ai_assisted,
                "ai_model_used": r.ai_model_used,
                "ai_confidence": r.ai_confidence,
                "status": r.status,
                "published_at": r.published_at,
                "created_at": r.created_at,
            }
            for r in reports
        ]
    }


@router.get("/reports/{report_id}", summary="获取报告详情")
async def get_report(
    report_id: int,
    session: AsyncSession = Depends(get_db)
):
    """获取报告详情"""
    result = await session.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return {
        "code": 200,
        "data": {
            "id": report.id,
            "report_no": report.report_no,
            "report_type": report.report_type,
            "title": report.title,
            "content": report.content,
            "summary": report.summary,
            "ai_assisted": report.ai_assisted,
            "ai_model_used": report.ai_model_used,
            "ai_confidence": report.ai_confidence,
            "status": report.status,
            "published_at": report.published_at,
            "created_by": report.created_by,
            "reviewed_by": report.reviewed_by,
            "reviewed_at": report.reviewed_at,
            "created_at": report.created_at,
        }
    }


# ============= 随访记录管理 =============

@router.get("/followup-records", summary="获取随访记录列表")
async def get_followup_records(
    patient_id: Optional[int] = Query(None, description="患者 ID"),
    is_lost: Optional[bool] = Query(None, description="是否失访"),
    limit: int = Query(20, le=100, description="返回数量限制"),
    session: AsyncSession = Depends(get_db)
):
    """获取随访记录列表"""
    query = select(FollowupRecord)
    
    if patient_id:
        query = query.where(FollowupRecord.patient_id == patient_id)
    if is_lost is not None:
        query = query.where(FollowupRecord.is_lost == is_lost)
    
    query = query.order_by(FollowupRecord.followup_date.desc()).limit(limit)
    result = await session.execute(query)
    records = result.scalars().all()
    
    return {
        "code": 200,
        "data": [
            {
                "id": r.id,
                "visit_id": r.visit_id,
                "patient_id": r.patient_id,
                "followup_date": r.followup_date,
                "followup_type": r.followup_type,
                "tcm_syndrome": r.tcm_syndrome,
                "qol_score": r.qol_score,
                "karnofsky_score": r.karnofsky_score,
                "conclusion": r.conclusion,
                "next_followup_date": r.next_followup_date,
                "is_lost": r.is_lost,
                "completed_at": r.completed_at,
            }
            for r in records
        ]
    }


@router.get("/followup-records/{record_id}", summary="获取随访记录详情")
async def get_followup_record(
    record_id: int,
    session: AsyncSession = Depends(get_db)
):
    """获取随访记录详情"""
    result = await session.execute(
        select(FollowupRecord).where(FollowupRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="随访记录不存在")
    
    return {
        "code": 200,
        "data": {
            "id": record.id,
            "visit_id": record.visit_id,
            "patient_id": record.patient_id,
            "followup_date": record.followup_date,
            "followup_type": record.followup_type,
            "chief_complaint": record.chief_complaint,
            "symptoms": record.symptoms,
            "physical_exam": record.physical_exam,
            "lifestyle": record.lifestyle,
            "tcm_syndrome": record.tcm_syndrome,
            "tcm_prescription": record.tcm_prescription,
            "qol_score": record.qol_score,
            "karnofsky_score": record.karnofsky_score,
            "conclusion": record.conclusion,
            "next_followup_date": record.next_followup_date,
            "is_lost": record.is_lost,
            "completed_by": record.completed_by,
            "completed_at": record.completed_at,
        }
    }
