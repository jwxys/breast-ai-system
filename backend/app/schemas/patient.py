from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


# ⚠️ 中医枚举类已移除（2026-05-29）
# 原因：无四诊信息采集，体质和证型判定无依据
# class ConstitutionType(str, Enum):
#     """体质类型枚举"""
#     PEACEFUL = "平和质"
#     QI_DEFICIENT = "气虚质"
#     # ... 其他体质
#
# class ZhengType(str, Enum):
#     """证型枚举"""
#     LIVER_QI_STAGNATION = "肝郁气滞"
#     SPLEEN_PHLEGM = "脾虚痰湿"
#     # ... 其他证型


class PatientBase(BaseModel):
    """患者基础 schema"""
    name: str = Field(..., min_length=1, max_length=64, description="姓名")
    gender: str = Field(default='F', pattern='^[MF]$', description="性别")
    birth_date: date = Field(..., description="出生日期")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号")
    email: Optional[str] = Field(None, email=True, description="邮箱")
    address: Optional[str] = Field(None, max_length=256, description="地址")
    
    # ⚠️ 中医字段已移除（2026-05-29）
    # 原因：无四诊信息采集，体质和证型判定无依据
    # 详见：docs/TCM_INTEGRATION_ANALYSIS_AND_FIX.md
    # constitution: Optional[ConstitutionType] = Field(None, description="体质类型")
    # constitution_score: Optional[float] = Field(None, ge=0, le=100, description="体质分数")
    # zheng_type: Optional[ZhengType] = Field(None, description="证型")
    # zheng_severity: Optional[str] = Field(None, pattern='^[轻重中]$', description="证型严重程度")


class PatientCreate(PatientBase):
    """创建患者请求"""
    pass


class PatientUpdate(BaseModel):
    """更新患者请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$')
    email: Optional[str] = Field(None, email=True)
    address: Optional[str] = Field(None, max_length=256)
    
    # ⚠️ 中医字段已移除（2026-05-29）
    # constitution: Optional[ConstitutionType] = None
    # zheng_type: Optional[ZhengType] = None
    # zheng_severity: Optional[str] = None


class PatientResponse(PatientBase):
    """患者响应"""
    id: int
    patient_no: str
    age: Optional[int]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    """患者列表响应"""
    data: List[PatientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, data: List, total: int, page: int, page_size: int):
        return cls(
            data=data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
