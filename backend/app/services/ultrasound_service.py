from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
from datetime import datetime
import httpx

from app.models.ultrasound import UltrasoundExam
from app.models.lesion import Lesion
from app.schemas.ultrasound import UltrasoundCreate, AnnotationRequest
from app.core.config import settings


class UltrasoundService:
    """超声检查服务层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service_url = settings.AI_SERVICE_URL
    
    async def create(self, data: UltrasoundCreate) -> UltrasoundExam:
        """创建超声检查记录"""
        exam_no = await self._generate_exam_no()
        
        ultrasound = UltrasoundExam(
            exam_no=exam_no,
            **data.model_dump()
        )
        
        self.db.add(ultrasound)
        await self.db.commit()
        await self.db.refresh(ultrasound)
        
        return ultrasound
    
    async def get(self, ultrasound_id: int) -> Optional[UltrasoundExam]:
        """获取超声检查"""
        result = await self.db.execute(
            select(UltrasoundExam).where(UltrasoundExam.id == ultrasound_id)
        )
        return result.scalar_one_or_none()
    
    async def analyze(self, ultrasound_id: int) -> Dict[str, Any]:
        """AI 分析"""
        ultrasound = await self.get(ultrasound_id)
        if not ultrasound:
            raise ValueError(f"Ultrasound {ultrasound_id} not found")
        
        # 调用 AI 推理服务
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ai_service_url}/api/v1/analyze",
                json={
                    "image_path": ultrasound.image_path,
                    "ultrasound_id": ultrasound_id
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise Exception("AI 分析失败")
            
            ai_result = response.json()
        
        # 更新检查记录
        ultrasound.ai_analysis = ai_result.get('results')
        ultrasound.ai_model_version = ai_result.get('ai_model_version', 'v1.0')
        ultrasound.ai_confidence = ai_result.get('confidence', 0.0)
        ultrasound.birads_category = ai_result.get('birads_category')
        ultrasound.birads_ai_predicted = ai_result.get('birads_category')
        ultrasound.lesion_count = len(ai_result.get('lesions', []))
        
        await self.db.commit()
        await self.db.refresh(ultrasound)
        
        return {
            "analysis_id": f"A{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "completed",
            "results": ai_result,
            "ai_model_version": ultrasound.ai_model_version,
            "confidence": float(ultrasound.ai_confidence)
        }
    
    async def submit_annotation(self, ultrasound_id: int, data: AnnotationRequest):
        """提交标注"""
        ultrasound = await self.get(ultrasound_id)
        if not ultrasound:
            raise ValueError(f"Ultrasound {ultrasound_id} not found")
        
        # 更新 BI-RADS 分级
        ultrasound.birads_category = data.birads_category
        ultrasound.review_status = "pending"
        
        # 创建病灶记录
        for lesion_data in data.lesions:
            lesion = Lesion(
                ultrasound_id=ultrasound_id,
                lesion_no=f"L{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                location=lesion_data.location,
                quadrant=lesion_data.quadrant,
                distance_from_nipple=lesion_data.distance_from_nipple,
                max_diameter=lesion_data.max_diameter,
                shape=lesion_data.shape,
                margin=lesion_data.margin,
                echo_pattern=lesion_data.echo_pattern,
            )
            self.db.add(lesion)
        
        await self.db.commit()
    
    async def review(self, ultrasound_id: int, status: str):
        """审核"""
        ultrasound = await self.get(ultrasound_id)
        if not ultrasound:
            raise ValueError(f"Ultrasound {ultrasound_id} not found")
        
        ultrasound.review_status = status
        ultrasound.reviewed_at = datetime.utcnow()
        
        await self.db.commit()
    
    async def _generate_exam_no(self) -> str:
        """生成检查编号"""
        from sqlalchemy import func
        
        today = datetime.now().strftime('%Y%m%d')
        prefix = f"US{today}"
        
        count_stmt = select(func.count(UltrasoundExam.id)).where(
            UltrasoundExam.exam_no.like(f"{prefix}%")
        )
        result = await self.db.execute(count_stmt)
        count = result.scalar() or 0
        
        return f"{prefix}{count + 1:04d}"
