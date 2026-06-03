"""
诊断报告模型 - 存储 AI 辅助诊断结果和医师报告

支持多模态诊断数据：超声所见、AI 分析、病理结果、分子分型
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, 
    ForeignKey, Boolean, Numeric, JSON, Enum
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ReportType(str, enum.Enum):
    """报告类型"""
    INITIAL = "initial"          # 初诊报告
    FOLLOW_UP = "follow_up"      # 随访报告
    POST_OP = "post_op"          # 术后报告
    PATHOLOGY = "pathology"      # 病理报告


class ReportStatus(str, enum.Enum):
    """报告状态"""
    DRAFT = "draft"              # 草稿
    PRELIMINARY = "preliminary"  # 初步报告
    FINAL = "final"              # 正式报告
    AMENDED = "amended"          # 修改报告
    CANCELLED = "cancelled"      # 作废


class Diagnosis(Base):
    """
    诊断记录表
    
    存储完整的诊断决策数据，包括：
    - BI-RADS 分级及依据
    - 恶性风险评估
    - 分子分型 (如有病理)
    - 治疗建议
    - AI 辅助诊断结果
    """
    __tablename__ = "diagnoses"
    
    # ========= 基本信息 =========
    id = Column(Integer, primary_key=True, index=True)
    report_no = Column(String(32), unique=True, nullable=False, index=True,
                       comment="报告编号 (自动生成)")
    
    # 关联字段
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, 
                        index=True, comment="患者 ID")
    lesion_id = Column(Integer, ForeignKey("lesions.id"), nullable=False, 
                       index=True, comment="病灶 ID")
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True, 
                      index=True, comment="就诊 ID")
    
    # 报告属性
    report_type = Column(Enum(ReportType), nullable=False, default=ReportType.INITIAL,
                         comment="报告类型")
    report_status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.DRAFT,
                           comment="报告状态")
    
    # ========= BI-RADS 评估 =========
    birads_category = Column(String(8), nullable=False, index=True,
                             comment="BI-RADS 分级：0/1/2/3/4A/4B/4C/5/6")
    birads_assessment_basis = Column(Text,
                                     comment="BI-RADS 评估依据")
    birads_key_features = Column(JSON,
                                 comment="关键超声征象列表")
    malignancy_risk = Column(Numeric(5, 4),
                             comment="恶性风险概率 (0-1)")
    
    # 处理建议
    recommendation = Column(String(256),
                            comment="处理建议：随访/活检/手术等")
    followup_interval = Column(String(32),
                               comment="随访间隔：3 个月/6 个月/12 个月")
    
    # ========= AI 辅助诊断 =========
    ai_assisted = Column(Boolean, default=False,
                         comment="是否使用 AI 辅助")
    ai_model_name = Column(String(64),
                           comment="AI 模型名称")
    ai_birads_prediction = Column(String(8),
                                  comment="AI 预测 BI-RADS 分级")
    ai_malignancy_probability = Column(Numeric(5, 4),
                                       comment="AI 预测恶性概率")
    ai_confidence = Column(Numeric(5, 4),
                           comment="AI 置信度")
    ai_extracted_features = Column(JSON,
                                   comment="AI 提取的超声征象")
    ai_highlighted_regions = Column(JSON,
                                    comment="AI 标注的可疑区域")
    ai_differential_diagnosis = Column(JSON,
                                       comment="AI 鉴别诊断建议")
    
    # ========= 病理诊断 (术后填充) =========
    pathology_performed = Column(Boolean, default=False,
                                 comment="是否进行病理检查")
    pathology_date = Column(DateTime,
                            comment="病理检查日期")
    pathology_type = Column(String(64),
                            comment="病理类型：IDC/DCIS/ILC/FA/cyst...")
    pathology_grade = Column(String(8),
                             comment="组织学分级：G1/G2/G3")
    pathology_report_url = Column(String(512),
                                  comment="病理报告附件 URL")
    
    # 免疫组化
    er_status = Column(String(16),
                       comment="ER 状态：阳性/阴性/+")
    er_percentage = Column(Numeric(5, 2),
                           comment="ER 阳性细胞百分比")
    pr_status = Column(String(16),
                       comment="PR 状态")
    pr_percentage = Column(Numeric(5, 2),
                           comment="PR 阳性细胞百分比")
    her2_status = Column(String(8),
                         comment="HER2 状态：0/1+/2+/3+")
    her2_fish_result = Column(String(32),
                              comment="HER2 FISH 结果：阳性/阴性/不确定")
    ki67_value = Column(Numeric(5, 2),
                        comment="Ki-67 指数 (%)")
    
    # 分子分型
    molecular_subtype = Column(String(32),
                               comment="分子分型：Luminal A/Luminal B/HER2+/Basal-like")
    molecular_subtype_confidence = Column(Numeric(5, 4),
                                          comment="分子分型预测置信度")
    
    # ========= 治疗建议 =========
    treatment_recommendations = Column(JSON,
                                       comment="治疗方案建议")
    prognosis_assessment = Column(Text,
                                  comment="预后评估")
    
    # ========= 审计字段 =========
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow,
                        comment="创建时间")
    updated_at = Column(DateTime, nullable=False, 
                        default=datetime.utcnow, onupdate=datetime.utcnow,
                        comment="更新时间")
    created_by = Column(Integer, ForeignKey("users.id"),
                        comment="创建者 (诊断医师 ID)")
    reviewed_by = Column(Integer, ForeignKey("users.id"),
                         comment="审核者 (上级医师 ID)")
    reviewed_at = Column(DateTime,
                         comment="审核时间")
    
    # ========= 关系 =========
    patient = relationship("Patient", back_populates="diagnoses")
    lesion = relationship("Lesion", back_populates="diagnoses")
    report_versions = relationship("DiagnosisReport", back_populates="diagnosis", 
                                   cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Diagnosis(id={self.id}, report_no='{self.report_no}', birads='{self.birads_category}')>"


class DiagnosisReport(Base):
    """
    诊断报告版本表
    
    支持报告多次修改，保留历史版本
    用于质量追溯和教学
    """
    __tablename__ = "diagnosis_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    diagnosis_id = Column(Integer, ForeignKey("diagnoses.id"), nullable=False, 
                          index=True, comment="关联诊断 ID")
    version_no = Column(Integer, nullable=False, default=1,
                        comment="版本号 (从 1 开始)")
    
    # 报告内容
    ultrasound_findings = Column(Text,
                                 comment="超声所见详细描述")
    impression = Column(Text,
                        comment="诊断印象/结论")
    recommendations = Column(Text,
                             comment="具体建议")
    
    # 报告差异 (与上一版本的变更说明)
    changes_from_previous = Column(Text,
                                   comment="与上一版本的变更说明")
    change_reason = Column(String(256),
                           comment="修改原因")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # ========= 关系 =========
    diagnosis = relationship("Diagnosis", back_populates="report_versions")
    
    def __repr__(self):
        return f"<DiagnosisReport(id={self.id}, diagnosis_id={self.diagnosis_id}, version={self.version_no})>"
