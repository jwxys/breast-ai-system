from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import aiofiles
import uuid
from datetime import datetime

from app.core.database import get_db
from app.services.ultrasound_service import UltrasoundService
from app.schemas.ultrasound import (
    UltrasoundCreate,
    UltrasoundResponse,
    AIAnalysisRequest,
    AIAnalysisResponse,
    AnnotationRequest
)


router = APIRouter()


@router.post("/upload", response_model=UltrasoundResponse)
async def upload_ultrasound(
    image: UploadFile = File(...),
    visit_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """上传超声图像"""
    # 保存文件
    file_id = str(uuid.uuid4())
    file_ext = image.filename.split(".")[-1] if "." in image.filename else "png"
    file_path = f"uploads/ultrasound/{datetime.now().strftime('%Y/%m/%d')}/{file_id}.{file_ext}"
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await image.read()
        await out_file.write(content)
    
    # 创建检查记录
    service = UltrasoundService(db)
    ultrasound = await service.create({
        "visit_id": visit_id,
        "image_path": file_path
    })
    
    return ultrasound


@router.post("/{ultrasound_id}/analyze", response_model=AIAnalysisResponse)
async def analyze_ultrasound(
    ultrasound_id: int,
    db: AsyncSession = Depends(get_db)
):
    """AI 分析超声图像"""
    service = UltrasoundService(db)
    result = await service.analyze(ultrasound_id)
    return result


@router.post("/{ultrasound_id}/annotation")
async def submit_annotation(
    ultrasound_id: int,
    annotation: AnnotationRequest,
    db: AsyncSession = Depends(get_db)
):
    """提交标注结果"""
    service = UltrasoundService(db)
    await service.submit_annotation(ultrasound_id, annotation)
    return {"message": "标注提交成功"}


@router.get("/{ultrasound_id}", response_model=UltrasoundResponse)
async def get_ultrasound(
    ultrasound_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取超声检查详情"""
    service = UltrasoundService(db)
    ultrasound = await service.get(ultrasound_id)
    if not ultrasound:
        raise HTTPException(status_code=404, detail="检查记录不存在")
    return ultrasound


@router.put("/{ultrasound_id}/review")
async def review_ultrasound(
    ultrasound_id: int,
    status: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """审核超声检查"""
    service = UltrasoundService(db)
    await service.review(ultrasound_id, status)
    return {"message": "审核完成"}
