-- 数据管理模块表结构
DROP TABLE IF EXISTS followup_record CASCADE;
DROP TABLE IF EXISTS report CASCADE;
DROP TABLE IF EXISTS inference_record CASCADE;
DROP TABLE IF EXISTS model_dataset_relation CASCADE;
DROP TABLE IF EXISTS public_dataset CASCADE;
DROP TABLE IF EXISTS training_dataset CASCADE;
DROP TABLE IF EXISTS model_weight CASCADE;

-- ============================================
-- 1. AI 模型权重管理表
-- ============================================

CREATE TABLE model_weight (
    id                  BIGSERIAL PRIMARY KEY,
    model_name          VARCHAR(128) NOT NULL,
    model_code          VARCHAR(64) UNIQUE NOT NULL,
    version             VARCHAR(32) NOT NULL,
    branch              VARCHAR(32),
    
    -- 权重文件信息
    weight_file         VARCHAR(256),
    file_size_mb        FLOAT,
    file_path           VARCHAR(512),
    
    -- 训练数据信息
    training_data_source VARCHAR(512),
    training_data_count INTEGER,
    training_start_date DATE,
    training_end_date   DATE,
    
    -- 性能指标
    metrics             JSONB,
    
    -- 合规信息
    ethics_approval_no  VARCHAR(128),
    ethics_approval_date DATE,
    
    -- 状态
    is_active           BOOLEAN DEFAULT TRUE,
    is_published        BOOLEAN DEFAULT FALSE,
    
    -- 审计字段
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE model_weight IS 'AI 模型权重元数据表';
COMMENT ON COLUMN model_weight.branch IS '所属分支：western(西医)/tcm(中医)';
COMMENT ON COLUMN model_weight.metrics IS '性能指标字典：{"dice": 0.87, "auc": 0.97, ...}';

-- ============================================
-- 2. 训练数据集表
-- ============================================

CREATE TABLE training_dataset (
    id                  BIGSERIAL PRIMARY KEY,
    dataset_name        VARCHAR(256) NOT NULL,
    dataset_code        VARCHAR(64) UNIQUE NOT NULL,
    dataset_type        VARCHAR(32),
    
    -- 数据来源
    source_type         VARCHAR(32),
    source_name         VARCHAR(256),
    source_region       VARCHAR(128),
    
    -- 数据规模
    total_count         INTEGER,
    train_count         INTEGER,
    val_count           INTEGER,
    test_count          INTEGER,
    
    -- 数据信息
    data_format         VARCHAR(64),
    annotation_type     VARCHAR(64),
    
    -- 时间范围
    collection_start_date DATE,
    collection_end_date   DATE,
    
    -- 合规信息
    ethics_approval_no  VARCHAR(128),
    license_type        VARCHAR(64),
    
    -- 描述
    description         TEXT,
    metadata            JSONB,
    
    -- 审计字段
    is_deleted          BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE training_dataset IS '训练数据集表';
COMMENT ON COLUMN training_dataset.dataset_type IS '数据类型：ultrasound/mammography/mri/questionnaire';
COMMENT ON COLUMN training_dataset.source_type IS '来源类型：hospital(医院)/public(公开)/self(自研)';

-- ============================================
-- 3. 公开数据集表
-- ============================================

CREATE TABLE public_dataset (
    id                  BIGSERIAL PRIMARY KEY,
    dataset_name        VARCHAR(256) NOT NULL,
    dataset_code        VARCHAR(64) UNIQUE NOT NULL,
    
    -- 来源信息
    publisher           VARCHAR(256),
    publish_year        INTEGER,
    journal             VARCHAR(256),
    doi                 VARCHAR(128),
    url                 VARCHAR(512),
    
    -- 数据集类型
    modality            VARCHAR(64),
    disease             VARCHAR(128),
    data_type           VARCHAR(64),
    
    -- 数据规模
    image_count         INTEGER,
    patient_count       INTEGER,
    storage_size_gb     FLOAT,
    
    -- 标注信息
    annotation_available BOOLEAN DEFAULT FALSE,
    annotation_type     VARCHAR(64),
    
    -- 使用信息
    license_type        VARCHAR(64),
    access_type         VARCHAR(32),
    usage_count         INTEGER DEFAULT 0,
    
    -- 描述
    description         TEXT,
    metadata            JSONB,
    
    -- 审计字段
    is_downloaded       BOOLEAN DEFAULT FALSE,
    download_date       TIMESTAMP,
    is_deleted          BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE public_dataset IS '公开数据集表';
COMMENT ON COLUMN public_dataset.modality IS '影像模态：ultrasound/mammography/mri/pathology';
COMMENT ON COLUMN public_dataset.access_type IS '访问类型：open(开放)/restricted(受限)';

-- ============================================
-- 4. 模型 - 数据集关联表
-- ============================================

CREATE TABLE model_dataset_relation (
    model_id            BIGINT NOT NULL REFERENCES model_weight(id),
    dataset_id          BIGINT NOT NULL REFERENCES training_dataset(id),
    PRIMARY KEY (model_id, dataset_id)
);

COMMENT ON TABLE model_dataset_relation IS '模型 - 数据集关联表';

-- ============================================
-- 5. 模型推理记录表
-- ============================================

CREATE TABLE inference_record (
    id                  BIGSERIAL PRIMARY KEY,
    model_id            BIGINT REFERENCES model_weight(id),
    patient_id          BIGINT REFERENCES patient(id),
    visit_id            BIGINT REFERENCES visit(id),
    
    -- 推理信息
    inference_type      VARCHAR(32),
    input_data          VARCHAR(512),
    output_data         VARCHAR(512),
    
    -- 推理结果
    result              JSONB,
    confidence          FLOAT,
    inference_time_ms   INTEGER,
    
    -- 审计字段
    created_by          BIGINT REFERENCES users(id),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE inference_record IS '模型推理记录表';
COMMENT ON COLUMN inference_record.inference_type IS '推理类型：segmentation/diagnosis/syndrome';

-- ============================================
-- 6. 报告表
-- ============================================

CREATE TABLE report (
    id                  BIGSERIAL PRIMARY KEY,
    report_no           VARCHAR(64) UNIQUE NOT NULL,
    report_type         VARCHAR(32) NOT NULL,
    
    -- 关联信息
    patient_id          BIGINT REFERENCES patient(id),
    visit_id            BIGINT REFERENCES visit(id),
    diagnosis_id        BIGINT REFERENCES diagnosis(id),
    
    -- 报告内容
    title               VARCHAR(256),
    content             TEXT,
    summary             VARCHAR(512),
    
    -- AI 辅助信息
    ai_assisted         BOOLEAN DEFAULT FALSE,
    ai_model_used       VARCHAR(128),
    ai_confidence       FLOAT,
    
    -- 报告状态
    status              VARCHAR(16) DEFAULT 'draft',
    published_at        TIMESTAMP,
    
    -- 审计字段
    created_by          BIGINT REFERENCES users(id),
    reviewed_by         BIGINT REFERENCES users(id),
    reviewed_at         TIMESTAMP,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE report IS '报告表';
COMMENT ON COLUMN report.report_type IS '报告类型：ai_diagnosis/followup/research';
COMMENT ON COLUMN report.status IS '状态：draft/published/archived';

-- ============================================
-- 7. 随访记录扩展表
-- ============================================

CREATE TABLE followup_record (
    id                  BIGSERIAL PRIMARY KEY,
    visit_id            BIGINT NOT NULL REFERENCES visit(id),
    patient_id          BIGINT NOT NULL REFERENCES patient(id),
    
    -- 随访信息
    followup_date       DATE NOT NULL,
    followup_type       VARCHAR(32),
    followup_method     VARCHAR(32),
    
    -- 随访内容
    chief_complaint     TEXT,
    symptoms            JSONB,
    physical_exam       JSONB,
    
    -- 生活方式
    lifestyle           JSONB,
    medication_adherence VARCHAR(16),
    
    -- 实验室检查
    lab_tests           JSONB,
    tumor_markers       JSONB,
    
    -- 影像学检查
    imaging_results     JSONB,
    
    -- 治疗方案调整
    treatment_adjustment TEXT,
    medication_change   JSONB,
    
    -- 中医信息
    tcm_syndrome        VARCHAR(64),
    tcm_prescription    VARCHAR(256),
    
    -- 生活质量评分
    qol_score           INTEGER,
    karnofsky_score     INTEGER,
    
    -- 不良事件
    adverse_events      JSONB,
    
    -- 随访结论
    conclusion          TEXT,
    next_followup_date  DATE,
    followup_plan       TEXT,
    
    -- 失访信息
    is_lost             BOOLEAN DEFAULT FALSE,
    lost_reason         VARCHAR(256),
    last_contact_date   DATE,
    
    -- 审计字段
    completed_by        BIGINT REFERENCES users(id),
    completed_at        TIMESTAMP,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE followup_record IS '随访记录扩展表';
COMMENT ON COLUMN followup_record.followup_type IS '随访类型：clinic/phone/video/home/wechat';
COMMENT ON COLUMN followup_record.medication_adherence IS '用药依从性：good/fair/poor';

-- ============================================
-- 索引创建
-- ============================================

-- 模型权重表索引
CREATE INDEX idx_model_branch ON model_weight(branch);
CREATE INDEX idx_model_active ON model_weight(is_active);
CREATE INDEX idx_model_published ON model_weight(is_published);
CREATE INDEX idx_model_code ON model_weight(model_code);

-- 训练数据集索引
CREATE INDEX idx_dataset_type ON training_dataset(dataset_type);
CREATE INDEX idx_dataset_source ON training_dataset(source_type);
CREATE INDEX idx_dataset_code ON training_dataset(dataset_code);

-- 公开数据集索引
CREATE INDEX idx_public_modality ON public_dataset(modality);
CREATE INDEX idx_public_disease ON public_dataset(disease);
CREATE INDEX idx_public_downloaded ON public_dataset(is_downloaded);
CREATE INDEX idx_public_code ON public_dataset(dataset_code);

-- 推理记录索引
CREATE INDEX idx_inference_model ON inference_record(model_id);
CREATE INDEX idx_inference_patient ON inference_record(patient_id);
CREATE INDEX idx_inference_created ON inference_record(created_at DESC);

-- 报告表索引
CREATE INDEX idx_report_type ON report(report_type);
CREATE INDEX idx_report_patient ON report(patient_id);
CREATE INDEX idx_report_status ON report(status);
CREATE INDEX idx_report_created ON report(created_at DESC);
CREATE INDEX idx_report_no ON report(report_no);

-- 随访记录索引
CREATE INDEX idx_followup_visit ON followup_record(visit_id);
CREATE INDEX idx_followup_patient ON followup_record(patient_id);
CREATE INDEX idx_followup_date ON followup_record(followup_date);
CREATE INDEX idx_followup_lost ON followup_record(is_lost);
CREATE INDEX idx_followup_next_date ON followup_record(next_followup_date);

-- ============================================
-- 初始化数据 - AI 模型权重
-- ============================================

INSERT INTO model_weight (model_name, model_code, version, branch, weight_file, file_size_mb, file_path,
                          training_data_source, training_data_count, training_start_date, training_end_date,
                          metrics, ethics_approval_no, ethics_approval_date, is_active, is_published) VALUES
('PBS-Net 病灶分割模型', 'pbs-net', 'v1.2', 'western', 'pbs_net_v12.pth', 128.0, 'models/pbs_net_v12.pth',
 '本院超声科 (2023-2025)', 2500, '2025-08-01', '2026-03-15',
 '{"dice": 0.87, "iou": 0.78, "hd95": 3.2, "inference_time_ms": 45}'::jsonb,
 'IRB-2023-BREAST-001', '2023-06-15', TRUE, TRUE),

('DFMFI 特征融合模型', 'dfmfi', 'v2.0', 'western', 'dfmfi_v20.pth', 96.0, 'models/dfmfi_v20.pth',
 '本院 + 协作医院 (2023-2025)', 3000, '2025-09-01', '2026-04-10',
 '{"accuracy": 0.94, "auc": 0.97, "sensitivity": 0.93, "specificity": 0.95, "params_m": 12.8}'::jsonb,
 'IRB-2023-BREAST-001', '2023-06-15', TRUE, TRUE),

('HXM-Net 多模态模型', 'hxm-net', 'v1.5', 'western', 'hxm_net_v15.pth', 256.0, 'models/hxm_net_v15.pth',
 '本院 (2024-2025)', 1500, '2025-10-01', '2026-02-28',
 '{"accuracy": 0.94, "auc": 0.96, "kappa": 0.89, "modality_weights": {"ultrasound": 0.45, "doppler": 0.30, "elasticity": 0.25}}'::jsonb,
 'IRB-2023-BREAST-001', '2023-06-15', TRUE, TRUE),

('体质辨识模型', 'tcm-cin', 'v3.1', 'tcm', 'tcm_constitution_v31.pth', 64.0, 'models/tcm_constitution_v31.pth',
 '3 家三甲医院 (北京/上海/广州)', 5000, '2025-08-01', '2026-01-20',
 '{"accuracy": 0.89, "macro_f1": 0.87, "kappa": 0.85}'::jsonb,
 'IRB-2025-TCM-001', '2025-07-10', TRUE, TRUE),

('证型识别模型', 'tcm-sdn', 'v2.3', 'tcm', 'tcm_syndrome_v23.pth', 72.0, 'models/tcm_syndrome_v23.pth',
 '本院 + 协作医院', 3200, '2025-10-01', '2026-03-15',
 '{"accuracy": 0.86, "main_syndrome": 0.91, "secondary_syndrome": 0.78, "kappa": 0.83}'::jsonb,
 'IRB-2025-TCM-002', '2025-09-20', TRUE, TRUE);

-- ============================================
-- 初始化数据 - 训练数据集
-- ============================================

INSERT INTO training_dataset (dataset_name, dataset_code, dataset_type, 
                              source_type, source_name, source_region,
                              total_count, train_count, val_count, test_count,
                              data_format, annotation_type,
                              collection_start_date, collection_end_date,
                              ethics_approval_no, license_type, description) VALUES
('本院乳腺超声数据集', 'breast-us-local', 'ultrasound',
 'hospital', '本院超声科', '中国',
 2500, 2000, 500, 1000,
 'dicom', 'segmentation',
 '2023-01-01', '2025-12-31',
 'IRB-2023-BREAST-001', 'internal',
 '本院 2023-2025 年乳腺超声图像，包含良恶性病灶标注'),

('多模态乳腺影像数据集', 'breast-multi-modal', 'multi-modality',
 'hospital', '本院 + 协作医院', '中国',
 3000, 2400, 600, 1200,
 'dicom', 'classification',
 '2023-01-01', '2025-12-31',
 'IRB-2023-BREAST-001', 'internal',
 '包含 B 模式、多普勒、弹性成像三模态数据'),

('中医体质问卷数据集', 'tcm-constitution', 'questionnaire',
 'hospital', '3 家三甲医院', '北京/上海/广州',
 5000, 4000, 1000, 2000,
 'csv', 'classification',
 '2025-01-01', '2025-12-31',
 'IRB-2025-TCM-001', 'internal',
 '中医体质辨识问卷数据，包含 9 种体质类型标注'),

('中医证型临床数据集', 'tcm-syndrome', 'clinical',
 'hospital', '本院 + 协作医院', '6 省市',
 3200, 2600, 600, 1000,
 'csv', 'classification',
 '2025-01-01', '2026-02-28',
 'IRB-2025-TCM-002', 'internal',
 '中医证型临床病例数据，包含 6 大证型标注');

-- ============================================
-- 初始化数据 - 公开数据集
-- ============================================

INSERT INTO public_dataset (dataset_name, dataset_code,
                            publisher, publish_year, journal, doi, url,
                            modality, disease, data_type,
                            image_count, patient_count, storage_size_gb,
                            annotation_available, annotation_type,
                            license_type, access_type, description) VALUES
('BUSI 乳腺超声数据集', 'busi',
 'PACS Journal', 2018, 'Scientific Data', '10.1038/sdata.2018.214',
 'https://scholar.cu.edu.eg/?q=afahmy/resources',
 'ultrasound', 'breast_cancer', 'image',
 780, 600, 2.5,
 TRUE, 'segmentation',
 'CC BY-NC 4.0', 'open',
 '公开乳腺超声数据集，包含正常、良性、恶性三类图像'),

('DDSM 乳腺钼靶数据集', 'ddsm',
 'University of South Florida', 1996, 'N/A', 'N/A',
 'https://wiki.cancerimagingarchive.net/display/Public/DDSM',
 'mammography', 'breast_cancer', 'image',
 2620, 2620, 15.0,
 TRUE, 'classification',
 'Public Domain', 'open',
 '公开乳腺钼靶数据集，包含良恶性病变'),

('TCGA-BRCA 乳腺癌数据集', 'tcga-brca',
 'NCI/NIH', 2012, 'N/A', '10.1038/nature11154',
 'https://portal.gdc.cancer.gov/repository?facet_filters=project.project_id:TCGA-BRCA',
 'pathology', 'breast_cancer', 'genomic',
 10000, 1000, 500.0,
 TRUE, 'multi_task',
 ' controlled', 'restricted',
 '癌症基因组图谱乳腺癌数据集，包含病理、基因组、临床数据');

-- ============================================
-- 初始化数据 - 模型 - 数据集关联
-- ============================================

INSERT INTO model_dataset_relation (model_id, dataset_id) VALUES
(1, 1),  -- PBS-Net 使用本院超声数据集
(2, 2),  -- DFMFI 使用多模态数据集
(3, 2),  -- HXM-Net 使用多模态数据集
(4, 3),  -- TCM-CIN 使用体质问卷数据集
(5, 4);  -- TCM-SDN 使用证型临床数据集

-- ============================================
-- 验证数据
-- ============================================

SELECT '模型权重' as table_name, COUNT(*) as count FROM model_weight
UNION ALL
SELECT '训练数据集', COUNT(*) FROM training_dataset
UNION ALL
SELECT '公开数据集', COUNT(*) FROM public_dataset
UNION ALL
SELECT '模型 - 数据集关联', COUNT(*) FROM model_dataset_relation;
