"""
影像 - 中医病机关联分析模型

用于存储超声影像特征与中医病机倾向的关联分析结果
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ImagingTCMCorrelation(Base):
    """超声影像与中医病机关联分析表"""
    
    __tablename__ = "imaging_tcm_correlation"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联 ID
    ultrasound_id = Column(Integer, ForeignKey("ultrasound.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    
    # 影像特征提取
    # 1. 形态学特征
    boundary_type = Column(String(32))  # 清晰/不清/毛刺/角征
    morphology = Column(String(32))  # 规则/不规则/蟹足样
    aspect_ratio = Column(Float)  # 纵横比
    edge_type = Column(String(32))  # 光整/模糊/微分叶/宏分叶
    capsule_status = Column(String(32))  # 完整/不完整/无包膜
    
    # 2. 内部回声特征
    echo_type = Column(String(32))  # 无回声/低回声/等回声/高回声
    echo_homogeneity = Column(String(32))  # 均匀/不均匀
    calcification_type = Column(String(32))  # 无/粗大/点状/簇状/弧形
    liquefaction = Column(Boolean)  # 是否有液化坏死
    
    # 3. 血流动力学特征
    cdfi_grade = Column(String(16))  # 0 级/I 级/II 级/III 级
    blood_flow_distribution = Column(String(32))  # 周边型/穿入型/网状型
    resistive_index = Column(Float)  # RI 阻力指数
    
    # 4. 弹性成像特征
    elasticity_score = Column(Integer)  # 1-5 分
    strain_ratio = Column(Float)  # 硬度比
    
    # 5. 生长动力学特征
    growth_rate = Column(String(16))  # 稳定/缓慢/中等/快速
    lesion_size_cm = Column(Float)  # 最大径 (cm)
    multifocality = Column(Boolean)  # 是否多灶
    
    # 中医病机倾向评分（0-1）
    stasis_score = Column(Float, default=0.0)  # 瘀血倾向
    stasis_evidence = Column(String(256))  # 瘀血证据摘要
    
    phlegm_score = Column(Float, default=0.0)  # 痰浊倾向
    phlegm_evidence = Column(String(256))  # 痰浊证据摘要
    
    toxin_score = Column(Float, default=0.0)  # 毒邪倾向
    toxin_evidence = Column(String(256))  # 毒邪证据摘要
    
    deficiency_score = Column(Float, default=0.0)  # 正虚倾向
    deficiency_evidence = Column(String(256))  # 正虚证据摘要
    
    # 综合判断
    primary_pathomechanism = Column(String(32))  # 主要病机
    secondary_pathomechanism = Column(String(32))  # 次要病机
    pattern_combination = Column(String(64))  # 病机组合（如"痰瘀互结"）
    nature = Column(String(32))  # 病性（实证/虚证/虚实夹杂）
    
    # 证据等级与置信度
    overall_evidence_level = Column(String(8))  # A/B/C 级
    confidence = Column(Float)  # 总体置信度 (0-1)
    
    # 治疗建议（仅供参考）
    recommended_therapy = Column(String(256))  # 推荐治法
    recommended_formula = Column(String(256))  # 参考方剂
    
    # 元数据
    analysis_version = Column(String(32))  # 分析引擎版本
    rule_engine_version = Column(String(32))  # 规则引擎版本
    
    # 审核状态
    reviewed = Column(Boolean, default=False)  # 是否已审核
    reviewed_by = Column(Integer, ForeignKey("users.id"))  # 审核医师 ID
    review_date = Column(DateTime)  # 审核时间
    review_notes = Column(Text)  # 审核意见
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    ultrasound = relationship("UltrasoundExam", back_populates="tcm_correlations")
    patient = relationship("Patient", backref="tcm_correlations")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<ImagingTCMCorrelation(id={self.id}, ultrasound_id={self.ultrasound_id}, primary={self.primary_pathomechanism})>"

    
    # ========== 辅助方法 ==========
    
    def get_all_scores(self) -> dict:
        """获取所有病机评分"""
        return {
            "stasis": self.stasis_score,
            "phlegm": self.phlegm_score,
            "toxin": self.toxin_score,
            "deficiency": self.deficiency_score,
        }
    
    def get_significant_tendencies(self, threshold: float = 0.3) -> list:
        """获取显著倾向（超过阈值）"""
        scores = self.get_all_scores()
        return [
            {"pathomechanism": k, "score": v}
            for k, v in scores.items()
            if v >= threshold
        ]
    
    def is_positive(self, threshold: float = 0.3) -> bool:
        """是否有显著病机倾向"""
        return any(score >= threshold for score in self.get_all_scores().values())
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "ultrasound_id": self.ultrasound_id,
            "patient_id": self.patient_id,
            "imaging_features": {
                "boundary": self.boundary_type,
                "morphology": self.morphology,
                "aspect_ratio": self.aspect_ratio,
                "echo_type": self.echo_type,
                "calcification": self.calcification_type,
                "cdfi_grade": self.cdfi_grade,
                "elasticity_score": self.elasticity_score,
                "growth_rate": self.growth_rate,
                "lesion_size": self.lesion_size_cm,
            },
            "tcm_tendencies": {
                "stasis": {
                    "score": self.stasis_score,
                    "evidence": self.stasis_evidence,
                    "level": self._interpret_score(self.stasis_score)
                },
                "phlegm": {
                    "score": self.phlegm_score,
                    "evidence": self.phlegm_evidence,
                    "level": self._interpret_score(self.phlegm_score)
                },
                "toxin": {
                    "score": self.toxin_score,
                    "evidence": self.toxin_evidence,
                    "level": self._interpret_score(self.toxin_score)
                },
                "deficiency": {
                    "score": self.deficiency_score,
                    "evidence": self.deficiency_evidence,
                    "level": self._interpret_score(self.deficiency_score)
                },
            },
            "integrated_analysis": {
                "primary_pathomechanism": self.primary_pathomechanism,
                "secondary_pathomechanism": self.secondary_pathomechanism,
                "pattern_combination": self.pattern_combination,
                "nature": self.nature,
            },
            "evidence": {
                "overall_level": self.overall_evidence_level,
                "confidence": self.confidence,
            },
            "recommendations": {
                "therapy": self.recommended_therapy,
                "formula": self.recommended_formula,
            },
            "disclaimer": {
                "warning": "⚠️ 本分析仅基于影像学特征的相关性研究",
                "evidence_statement": f"证据等级为{self.overall_evidence_level}级，不能作为独立辨证依据",
                "usage_limitation": "仅供执业中医师参考，不能替代四诊合参",
                "research_status": "本功能为研究性质，正在进行多中心临床验证"
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @staticmethod
    def _interpret_score(score: float) -> str:
        """解读评分"""
        if score < 0.3:
            return "轻度/无提示"
        elif score < 0.5:
            return "中度倾向"
        elif score < 0.7:
            return "明显倾向"
        else:
            return "显著倾向"
