"""
病灶模型 - 乳腺超声病灶结构化数据模型

基于 BI-RADS 超声词表和 CDE 标准设计
支持病灶特征、弹性成像、血流信号等多维度记录
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Date, Numeric, 
    ForeignKey, Text, DateTime, JSON, Boolean, Enum
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class LesionShape(enum.Enum):
    """
    病灶形状分类
    
    依据：ACR BI-RADS Ultrasound 第 5 版
    """
    OVAL = "oval"              # 椭圆形 (宽大于高，良性特征)
    ROUND = "round"            # 圆形 (等比例，可疑)
    IRREGULAR = "irregular"    # 不规则形 (恶性特征)


class LesionOrientation(enum.Enum):
    """
    病灶纵横比
    
    重要恶性征象：纵横比>1 (taller-than-wide)
    """
    PARALLEL = "parallel"              # 平行生长 (宽>高，良性)
    NOT_PARALLEL = "not_parallel"      # 非平行生长 (高>宽，恶性)


class MarginType(enum.Enum):
    """
    病灶边缘特征
    
    恶性征象：毛刺状、微小分叶、成角
    """
    CIRCUMSCRIBED = "circumscribed"        # 边界清晰 (良性)
    INDISTINCT = "indistinct"              # 边界不清
    ANGULAR = "angular"                    # 成角 (恶性)
    MICROLOBULATED = "microlobulated"      # 微小分叶 (恶性)
    SPICULATED = "spiculated"              # 毛刺状 (高度恶性)


class EchoPattern(enum.Enum):
    """
    内部回声模式
    
    反映病灶内部组织成分
    """
    ANECHOIC = "anechoic"              # 无回声 (囊肿)
    HYPOECHOIC = "hypoechoic"          # 低回声 (实性/恶性)
    ISOECHOIC = "isoechoic"            # 等回声
    HYPERECHOIC = "hyperechoic"        # 高回声 (脂肪/纤维)
    HETEROGENEOUS = "heterogeneous"    # 混合回声 (复杂病变)
    COMPLEX_CYSTIC = "complex_cystic"  # 囊实性混合


class CalcificationType(enum.Enum):
    """
    钙化类型
    
    粗大钙化多为良性，微钙化高度可疑恶性
    """
    NONE = "none"                    # 无钙化
    COARSE = "coarse"                # 粗大钙化 (>0.5mm，良性)
    FINE = "fine"                    # 细小钙化 (可疑)
    PUNCTATE = "punctate"            # 点状钙化
    PLEOMORPHIC = "pleomorphic"      # 多形性钙化 (高度恶性)
    LINEAR = "linear"                # 线样钙化 (导管内癌)


class Vascularity(enum.Enum):
    """
    血流信号分级 (CDFI)
    
    Adler 半定量分级标准
    """
    GRADE_0 = "grade_0"        # 无血流
    GRADE_1 = "grade_1"        # 少许血流 (1-2 个点状)
    GRADE_2 = "grade_2"        # 中等血流 (3-4 个点状或 1 条血管)
    GRADE_3 = "grade_3"        # 丰富血流 (>5 个点状或多条血管)


class ElastographyResult(enum.Enum):
    """
    弹性成像结果
    
    评估组织硬度，恶性病灶通常更硬
    """
    SOFT = "soft"              # 软 (良性)
    INTERMEDIATE = "intermediate"  # 中等硬度
    HARD = "hard"              # 硬 (可疑恶性)
    VERY_HARD = "very_hard"    # 很硬 (高度可疑)


class Lesion(Base):
    """
    乳腺病灶记录表
    
    完整记录超声所见特征，支持 BI-RADS 分级和 AI 诊断
    
    字段设计依据:
    - ACR BI-RADS Atlas, 5th Edition
    - 中国乳腺癌超声检查指南
    - CDE 乳腺癌临床数据标准
    """
    __tablename__ = "lesions"  # 改为复数形式，符合 SQLAlchemy 约定
    
    # ========= 基本信息 =========
    id = Column(Integer, primary_key=True, index=True)
    lesion_no = Column(String(32), unique=True, nullable=False, index=True, 
                       comment="病灶编号 (自动生成)")
    
    # 患者关联
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, 
                        index=True, comment="患者 ID")
    ultrasound_id = Column(Integer, ForeignKey("ultrasound_studies.id"), 
                           nullable=False, index=True, comment="超声检查 ID")
    
    # 病灶定位
    laterality = Column(String(8), nullable=False, 
                        comment="侧别：left/right/bilateral")
    quadrant = Column(String(16), 
                      comment="象限：upper_outer/upper_inner/lower_outer/lower_inner/central")
    clock_position = Column(String(8), 
                            comment="钟点位置：如 2:00, 10:00")
    distance_from_nipple = Column(Numeric(4, 1), 
                                  comment="距乳头距离 (cm)")
    
    # ========= 二维超声征象 =========
    
    # 大小测量 (三维)
    size_ap = Column(Numeric(6, 2), comment="前后径 (cm)")
    size_transverse = Column(Numeric(6, 2), comment="横径 (cm)")
    size_ap_transverse_ratio = Column(Numeric(4, 2), 
                                      comment="前后径/横径比值 (恶性征象：>1)")
    
    # 形状特征
    shape = Column(Enum(LesionShape), 
                   comment="形状：椭圆形/圆形/不规则形")
    orientation = Column(Enum(LesionOrientation), 
                         comment="纵横比：平行/非平行 (taller-than-wide)")
    
    # 边缘特征 (多值，JSON 存储)
    margin_types = Column(JSON, 
                          comment="边缘类型列表：[circumscribed, angular, spiculated...]")
    margin_description = Column(Text, 
                                comment="边缘详细描述")
    
    # 内部回声
    echo_pattern = Column(Enum(EchoPattern), 
                          comment="回声模式")
    echo_homogeneity = Column(String(16), 
                              comment="回声均匀性：homogeneous/heterogeneous")
    
    # 后方回声特征
    posterior_features = Column(JSON, 
                                comment="后方回声：enhancement/shadowing/no_change/mixed")
    
    # 钙化特征
    calcification_present = Column(Boolean, default=False, 
                                   comment="是否伴钙化")
    calcification_types = Column(JSON, 
                                 comment="钙化类型列表")
    calcification_distribution = Column(String(32), 
                                        comment="钙化分布：focal/linear/segmental/diffuse")
    
    # ========= 多普勒血流 =========
    vascularity_grade = Column(Enum(Vascularity), 
                               comment="血流信号分级 (Adler 0-3 级)")
    vessel_pattern = Column(String(32), 
                            comment="血管形态：regular/irregular/penetrating")
    ri_value = Column(Numeric(3, 2), 
                      comment="阻力指数 RI (恶性通常>0.7)")
    pi_value = Column(Numeric(3, 2), 
                      comment="搏动指数 PI")
    
    # ========= 弹性成像 =========
    elastography_used = Column(Boolean, default=False, 
                               comment="是否进行弹性成像")
    elasticity_score = Column(Enum(ElastographyResult), 
                              comment="弹性评分")
    strain_ratio = Column(Numeric(4, 2), 
                          comment="应变比值 (病灶/脂肪，>3.5 可疑恶性)")
    
    # ========= BI-RADS 分级 =========
    birads_category = Column(String(8), nullable=False, index=True, 
                             comment="BI-RADS 分级：0/1/2/3/4A/4B/4C/5/6")
    birads_assessment = Column(Text, 
                               comment="BI-RADS 评估依据说明")
    birads_recommendation = Column(String(128), 
                                   comment="处理建议：随访/活检/手术")
    
    # ========= 病理结果 (术后填充) =========
    pathology_performed = Column(Boolean, default=False, 
                                 comment="是否进行病理检查")
    pathology_date = Column(Date, 
                            comment="病理检查日期")
    pathology_type = Column(String(64), 
                            comment="病理类型：IDC/DCIS/ILC/FA/cyst...")
    pathology_grade = Column(String(8), 
                             comment="组织学分级：G1/G2/G3")
    
    # 免疫组化
    er_status = Column(String(8), comment="ER 状态：阳性/阴性/+...")
    pr_status = Column(String(8), comment="PR 状态")
    her2_status = Column(String(8), comment="HER2 状态：0/1+/2+/3+")
    ki67_value = Column(Numeric(5, 2), comment="Ki-67 指数 (%)")
    
    # 分子分型
    molecular_subtype = Column(String(32), 
                               comment="分子分型：Luminal A/Luminal B/HER2+/Basal-like")
    
    # ========= AI 辅助诊断 =========
    ai_assisted = Column(Boolean, default=False, 
                         comment="是否使用 AI 辅助诊断")
    ai_birads_prediction = Column(String(8), 
                                  comment="AI 预测 BI-RADS 分级")
    ai_confidence = Column(Numeric(5, 4), 
                           comment="AI 置信度 (0-1)")
    ai_malignancy_probability = Column(Numeric(5, 4), 
                                       comment="AI 预测恶性概率")
    ai_highlighted_features = Column(JSON, 
                                     comment="AI 强调的关键征象")
    
    # ========= 审计字段 =========
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, 
                        comment="创建时间")
    updated_at = Column(DateTime, nullable=False, 
                        default=datetime.utcnow, onupdate=datetime.utcnow, 
                        comment="更新时间")
    created_by = Column(Integer, ForeignKey("users.id"), 
                        comment="创建者 (医生 ID)")
    reviewed_by = Column(Integer, ForeignKey("users.id"), 
                         comment="审核者 (上级医师 ID)")
    review_status = Column(String(16), default="draft", 
                           comment="审核状态：draft/pending/approved")
    
    # ========= 关系 =========
    patient = relationship("Patient", back_populates="lesions")
    ultrasound_study = relationship("UltrasoundStudy", back_populates="lesions")
    diagnoses = relationship("Diagnosis", back_populates="lesion", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lesion(id={self.id}, lesion_no='{self.lesion_no}', birads='{self.birads_category}')>"
