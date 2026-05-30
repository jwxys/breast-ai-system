from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Tuple, List, Optional

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from datetime import datetime


class PatientService:
    """患者服务层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: PatientCreate) -> Patient:
        """创建患者"""
        patient_no = await self._generate_patient_no()
        
        patient = Patient(
            patient_no=patient_no,
            **data.model_dump()
        )
        
        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)
        
        return patient
    
    async def get(self, patient_id: int) -> Optional[Patient]:
        """获取患者"""
        result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id, Patient.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        constitution: str = None,
        zheng_type: str = None,
        risk_level: str = None
    ) -> Tuple[List[Patient], int]:
        """获取患者列表"""
        from sqlalchemy import func
        
        # 构建查询
        stmt = select(Patient).where(Patient.is_active == True)
        count_stmt = select(func.count(Patient.id)).where(Patient.is_active == True)
        
        # 添加筛选条件
        if constitution:
            stmt = stmt.where(Patient.constitution == constitution)
            count_stmt = count_stmt.where(Patient.constitution == constitution)
        if zheng_type:
            stmt = stmt.where(Patient.zheng_type == zheng_type)
            count_stmt = count_stmt.where(Patient.zheng_type == zheng_type)
        
        # 分页
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        # 执行查询
        result = await self.db.execute(stmt)
        patients = result.scalars().all()
        
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        return patients, total
    
    async def update(self, patient_id: int, data: PatientUpdate) -> Patient:
        """更新患者"""
        patient = await self.get(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(patient, key, value)
        
        patient.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(patient)
        
        return patient
    
    async def delete(self, patient_id: int) -> None:
        """软删除患者"""
        patient = await self.get(patient_id)
        if patient:
            patient.is_active = False
            patient.updated_at = datetime.utcnow()
            await self.db.commit()
    
    async def _generate_patient_no(self) -> str:
        """生成患者编号"""
        from sqlalchemy import func
        
        today = datetime.now().strftime('%Y%m%d')
        prefix = f"P{today}"
        
        # 计数今日已创建的患者数
        count_stmt = select(func.count(Patient.id)).where(
            Patient.patient_no.like(f"{prefix}%")
        )
        result = await self.db.execute(count_stmt)
        count = result.scalar() or 0
        
        return f"{prefix}{count + 1:04d}"
