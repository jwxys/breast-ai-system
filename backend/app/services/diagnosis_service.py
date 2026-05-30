from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
from datetime import datetime
import httpx

from app.models.diagnosis import Diagnosis
from app.models.lesion import Lesion
from app.schemas.diagnosis import DiagnosisCreate, DiagnosisUpdate
# ⚠️ 中医证型识别已移除 (2026-05-29) - 无四诊数据
# from app.schemas.diagnosis import ZhengTypeRecognitionRequest
from app.core.config import settings


class DiagnosisService:
    """诊断服务层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service_url = settings.AI_SERVICE_URL
    
    async def create(self, data: DiagnosisCreate) -> Diagnosis:
        """创建诊断"""
        diagnosis = Diagnosis(
            **data.model_dump()
        )
        
        self.db.add(diagnosis)
        await self.db.commit()
        await self.db.refresh(diagnosis)
        
        return diagnosis
    
    async def get_by_lesion(self, lesion_id: int) -> Optional[Diagnosis]:
        """根据病灶获取诊断"""
        result = await self.db.execute(
            select(Diagnosis).where(Diagnosis.lesion_id == lesion_id)
        )
        return result.scalar_one_or_none()
    
    async def update(self, diagnosis_id: int, data: DiagnosisUpdate) -> Diagnosis:
        """更新诊断"""
        result = await self.db.execute(
            select(Diagnosis).where(Diagnosis.id == diagnosis_id)
        )
        diagnosis = result.scalar_one_or_none()
        
        if not diagnosis:
            raise ValueError(f"Diagnosis {diagnosis_id} not found")
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(diagnosis, key, value)
        
        await self.db.commit()
        await self.db.refresh(diagnosis)
        
        return diagnosis
    
    async def predict_molecular_subtype(
        self, 
        lesion_id: int, 
        radiomics_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分子分型预测"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ai_service_url}/api/v1/molecular-subtype",
                json={"radiomics_features": radiomics_features},
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception("分子分型预测失败")
            
            return response.json()
    
    # ⚠️ 中医证型识别方法已移除 (2026-05-29)
    # 原因：系统未采集舌象图像和脉象波形数据，证型识别无依据
    # async def recognize_zheng_type(
    #     self,
    #     patient_id: int,
    #     request: ZhengTypeRecognitionRequest
    # ) -> Dict[str, Any]:
    #     """中医证型识别"""
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(
    #             f"{self.ai_service_url}/api/v1/tcm/zheng-type",
    #             json={
    #                 "tongue_image": request.tongue_image,
    #                 "pulse_waveform": request.pulse_waveform,
    #                 "symptom_responses": request.symptom_responses
    #             },
    #             timeout=30.0
    #         )
    #         
    #         if response.status_code != 200:
    #             raise Exception("证型识别失败")
    #         
    #         result = response.json()
    #     
    #     return result
