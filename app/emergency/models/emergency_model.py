"""
应急联系人模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ContactType(str, enum.Enum):
    """联系人类型"""
    EMERGENCY = "emergency"  # 紧急联系人
    MEDICAL = "medical"  # 医疗联系人
    ADMIN = "admin"  # 行政联系人
    TECHNICAL = "technical"  # 技术支持
    ETHICS = "ethics"  # 伦理委员会
    OTHER = "other"  # 其他


class EmergencyContact(Base):
    """应急联系人表"""
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基本信息
    name = Column(String(64), nullable=False)  # 姓名
    title = Column(String(128))  # 职务/职称
    organization = Column(String(256))  # 所属机构
    contact_type = Column(Enum(ContactType), nullable=False, default=ContactType.EMERGENCY)
    
    # 联系方式
    phone_primary = Column(String(20), nullable=False)  # 主要电话
    phone_secondary = Column(String(20))  # 备用电话
    email = Column(String(128))  # 电子邮箱
    wechat = Column(String(64))  # 微信号
    address = Column(Text)  # 地址
    
    # 职责描述
    responsibilities = Column(Text)  # 职责描述
    available_hours = Column(String(128))  # 可联系时间（如"24 小时"、"工作日 9:00-17:00"）
    
    # 排序和状态
    priority = Column(Integer, default=0)  # 优先级（数字越小越优先）
    is_active = Column(Boolean, default=True)  # 是否启用
    
    # 备注
    notes = Column(Text)  # 备注信息
    
    # 审计字段
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<EmergencyContact(name={self.name}, type={self.contact_type.value})>"
