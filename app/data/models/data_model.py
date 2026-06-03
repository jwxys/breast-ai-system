from sqlalchemy import Column, BigInteger, String, Text, Integer, Boolean, DateTime, ForeignKey, Float, JSON, Date, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ModelWeight(Base):
    """AI 模型权重元数据表"""
    __tablename__ = 'model_weight'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_name = Column(String(128), nullable=False, comment='模型名称')
    model_code = Column(String(64), unique=True, nullable=False, comment='模型编码')
    version = Column(String(32), nullable=False, comment='版本号')
    branch = Column(String(32), comment='所属分支：western/tcm')
    
    # 权重文件信息
    weight_file = Column(String(256), comment='权重文件名')
    file_size_mb = Column(Float, comment='文件大小 (MB)')
    file_path = Column(String(512), comment='存储路径')
    
    # 训练数据信息
    training_data_source = Column(String(512), comment='训练数据来源')
    training_data_count = Column(Integer, comment='训练数据例数')
    training_start_date = Column(Date, comment='训练开始日期')
    training_end_date = Column(Date, comment='训练结束日期')
    
    # 性能指标
    metrics = Column(JSON, comment='性能指标字典')
    
    # 合规信息
    ethics_approval_no = Column(String(128), comment='伦理审批号')
    ethics_approval_date = Column(Date, comment='伦理审批日期')
    
    # 状态
    is_active = Column(Boolean, default=True, comment='是否启用')
    is_published = Column(Boolean, default=False, comment='是否发布')
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    training_datasets = relationship("TrainingDataset", secondary="model_dataset_relation", back_populates="models")
    inference_records = relationship("InferenceRecord", back_populates="model")


class TrainingDataset(Base):
    """训练数据集表"""
    __tablename__ = 'training_dataset'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    dataset_name = Column(String(256), nullable=False, comment='数据集名称')
    dataset_code = Column(String(64), unique=True, nullable=False, comment='数据集编码')
    dataset_type = Column(String(32), comment='数据类型：ultrasound/mammography/mri/questionnaire')
    
    # 数据来源
    source_type = Column(String(32), comment='来源类型：hospital/public/self')
    source_name = Column(String(256), comment='来源机构名称')
    source_region = Column(String(128), comment='来源地区')
    
    # 数据规模
    total_count = Column(Integer, comment='总例数')
    train_count = Column(Integer, comment='训练集例数')
    val_count = Column(Integer, comment='验证集例数')
    test_count = Column(Integer, comment='测试集例数')
    
    # 数据信息
    data_format = Column(String(64), comment='数据格式：dicom/nii/png/csv')
    annotation_type = Column(String(64), comment='标注类型：segmentation/classification/detection')
    
    # 时间范围
    collection_start_date = Column(Date, comment='收集开始日期')
    collection_end_date = Column(Date, comment='收集结束日期')
    
    # 合规信息
    ethics_approval_no = Column(String(128), comment='伦理审批号')
    license_type = Column(String(64), comment='许可类型')
    
    # 描述
    description = Column(Text, comment='数据集描述')
    extra_metadata = Column(JSON, comment='元数据')
    
    # 审计字段
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    models = relationship("ModelWeight", secondary="model_dataset_relation", back_populates="training_datasets")


class PublicDataset(Base):
    """公开数据集表"""
    __tablename__ = 'public_dataset'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    dataset_name = Column(String(256), nullable=False, comment='数据集名称')
    dataset_code = Column(String(64), unique=True, nullable=False, comment='数据集编码')
    
    # 来源信息
    publisher = Column(String(256), comment='发布机构')
    publish_year = Column(Integer, comment='发布年份')
    journal = Column(String(256), comment='发表期刊')
    doi = Column(String(128), comment='DOI')
    url = Column(String(512), comment='下载链接')
    
    # 数据集类型
    modality = Column(String(64), comment='影像模态：ultrasound/mammography/mri/pathology')
    disease = Column(String(128), comment='疾病类型')
    data_type = Column(String(64), comment='数据类型：image/clinical/genomic')
    
    # 数据规模
    image_count = Column(Integer, comment='图像数量')
    patient_count = Column(Integer, comment='患者数量')
    storage_size_gb = Column(Float, comment='存储大小 (GB)')
    
    # 标注信息
    annotation_available = Column(Boolean, default=False, comment='是否有标注')
    annotation_type = Column(String(64), comment='标注类型')
    
    # 使用信息
    license_type = Column(String(64), comment='许可类型')
    access_type = Column(String(32), comment='访问类型：open/restricted')
    usage_count = Column(Integer, default=0, comment='使用次数')
    
    # 描述
    description = Column(Text, comment='数据集描述')
    extra_metadata = Column(JSON, comment='元数据')
    
    # 审计字段
    is_downloaded = Column(Boolean, default=False, comment='是否已下载')
    download_date = Column(DateTime, comment='下载日期')
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 模型 - 数据集关联表
model_dataset_relation = Table(
    'model_dataset_relation',
    Base.metadata,
    Column('model_id', BigInteger, ForeignKey('model_weight.id'), primary_key=True),
    Column('dataset_id', BigInteger, ForeignKey('training_dataset.id'), primary_key=True)
)


class InferenceRecord(Base):
    """模型推理记录表"""
    __tablename__ = 'inference_record'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_id = Column(BigInteger, ForeignKey('model_weight.id'), comment='模型 ID')
    patient_id = Column(BigInteger, ForeignKey('patient.id'), comment='患者 ID')
    visit_id = Column(BigInteger, ForeignKey('visit.id'), comment='随访 ID')
    
    # 推理信息
    inference_type = Column(String(32), comment='推理类型：segmentation/diagnosis/syndrome')
    input_data = Column(String(512), comment='输入数据路径')
    output_data = Column(String(512), comment='输出数据路径')
    
    # 推理结果
    result = Column(JSON, comment='推理结果')
    confidence = Column(Float, comment='置信度')
    inference_time_ms = Column(Integer, comment='推理时间 (ms)')
    
    # 审计字段
    created_by = Column(BigInteger, ForeignKey('users.id'), comment='操作人 ID')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    model = relationship("ModelWeight", back_populates="inference_records")


class Report(Base):
    """报告表"""
    __tablename__ = 'report'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_no = Column(String(64), unique=True, nullable=False, comment='报告编号')
    report_type = Column(String(32), nullable=False, comment='报告类型：ai_diagnosis/followup/research')
    
    # 关联信息
    patient_id = Column(BigInteger, ForeignKey('patient.id'), comment='患者 ID')
    visit_id = Column(BigInteger, ForeignKey('visit.id'), comment='随访 ID')
    diagnosis_id = Column(BigInteger, ForeignKey('diagnosis.id'), comment='诊断 ID')
    
    # 报告内容
    title = Column(String(256), comment='报告标题')
    content = Column(Text, comment='报告内容 (Markdown)')
    summary = Column(String(512), comment='报告摘要')
    
    # AI 辅助信息
    ai_assisted = Column(Boolean, default=False, comment='是否 AI 辅助')
    ai_model_used = Column(String(128), comment='使用的 AI 模型')
    ai_confidence = Column(Float, comment='AI 置信度')
    
    # 报告状态
    status = Column(String(16), default='draft', comment='状态：draft/published/archived')
    published_at = Column(DateTime, comment='发布时间')
    
    # 审计字段
    created_by = Column(BigInteger, ForeignKey('users.id'), comment='创建人 ID')
    reviewed_by = Column(BigInteger, ForeignKey('users.id'), comment='审核人 ID')
    reviewed_at = Column(DateTime, comment='审核时间')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    patient = relationship("Patient", back_populates="reports")
    visit = relationship("Visit", back_populates="reports")
    diagnosis = relationship("Diagnosis", back_populates="reports")


class FollowupRecord(Base):
    """随访记录扩展表"""
    __tablename__ = 'followup_record'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    visit_id = Column(BigInteger, ForeignKey('visit.id'), nullable=False, comment='随访 ID')
    patient_id = Column(BigInteger, ForeignKey('patient.id'), nullable=False, comment='患者 ID')
    
    # 随访信息
    followup_date = Column(Date, nullable=False, comment='随访日期')
    followup_type = Column(String(32), comment='随访类型：clinic/phone/video/home/wechat')
    followup_method = Column(String(32), comment='随访方式：routine/special')
    
    # 随访内容
    chief_complaint = Column(Text, comment='主诉')
    symptoms = Column(JSON, comment='症状记录')
    physical_exam = Column(JSON, comment='体格检查')
    
    # 生活方式
    lifestyle = Column(JSON, comment='生活方式记录')
    medication_adherence = Column(String(16), comment='用药依从性')
    
    # 实验室检查
    lab_tests = Column(JSON, comment='实验室检查')
    tumor_markers = Column(JSON, comment='肿瘤标志物')
    
    # 影像学检查
    imaging_results = Column(JSON, comment='影像学检查结果')
    
    # 治疗方案调整
    treatment_adjustment = Column(Text, comment='治疗方案调整')
    medication_change = Column(JSON, comment='药物调整')
    
    # 中医信息
    tcm_syndrome = Column(String(64), comment='中医证型')
    tcm_prescription = Column(String(256), comment='中医方剂')
    
    # 生活质量评分
    qol_score = Column(Integer, comment='生活质量评分')
    karnofsky_score = Column(Integer, comment='KPS 评分')
    
    # 不良事件
    adverse_events = Column(JSON, comment='不良事件记录')
    
    # 随访结论
    conclusion = Column(Text, comment='随访结论')
    next_followup_date = Column(Date, comment='下次随访日期')
    followup_plan = Column(Text, comment='随访计划')
    
    # 失访信息
    is_lost = Column(Boolean, default=False, comment='是否失访')
    lost_reason = Column(String(256), comment='失访原因')
    last_contact_date = Column(Date, comment='最后联系日期')
    
    # 审计字段
    completed_by = Column(BigInteger, ForeignKey('users.id'), comment='完成人 ID')
    completed_at = Column(DateTime, comment='完成时间')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
