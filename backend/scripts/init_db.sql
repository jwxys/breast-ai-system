-- 乳腺 AI 系统数据库初始化脚本
-- PostgreSQL 14+

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- 模糊搜索

-- 删除已存在的表（级联删除）
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS treatment CASCADE;
DROP TABLE IF EXISTS diagnosis CASCADE;
DROP TABLE IF EXISTS lesion CASCADE;
DROP TABLE IF EXISTS ultrasound CASCADE;
DROP TABLE IF EXISTS visit CASCADE;
DROP TABLE IF EXISTS patient CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS permissions CASCADE;

-- ============================================
-- 1. 权限管理表
-- ============================================

-- 角色表
CREATE TABLE roles (
    id              BIGSERIAL PRIMARY KEY,
    role_name       VARCHAR(64) UNIQUE NOT NULL,
    role_code       VARCHAR(64) UNIQUE NOT NULL,
    description     TEXT,
    is_system       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 权限表
CREATE TABLE permissions (
    id              BIGSERIAL PRIMARY KEY,
    permission_name VARCHAR(128) UNIQUE NOT NULL,
    resource        VARCHAR(64) NOT NULL,
    action          VARCHAR(32) NOT NULL,
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户表
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    username        VARCHAR(64) UNIQUE NOT NULL,
    email           VARCHAR(128) UNIQUE NOT NULL,
    password_hash   VARCHAR(256) NOT NULL,
    real_name       VARCHAR(64),
    phone           VARCHAR(20),
    department      VARCHAR(128),  -- 科室
    title           VARCHAR(64),   -- 职称
    role_id         BIGINT REFERENCES roles(id),
    is_active       BOOLEAN DEFAULT TRUE,
    last_login      TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色权限关联表
CREATE TABLE role_permissions (
    role_id         BIGINT REFERENCES roles(id) ON DELETE CASCADE,
    permission_id   BIGINT REFERENCES permissions(id) ON DELETE CASCADE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);

-- ============================================
-- 2. 患者管理表
-- ============================================

-- 患者基本信息表
CREATE TABLE patient (
    id              BIGSERIAL PRIMARY KEY,
    patient_no      VARCHAR(32) UNIQUE NOT NULL,
    name            VARCHAR(64) NOT NULL,
    gender          CHAR(1) NOT NULL DEFAULT 'F',
    birth_date      DATE NOT NULL,
    age             INTEGER,
    id_card         VARCHAR(18) UNIQUE,
    phone           VARCHAR(20),
    email           VARCHAR(128),
    address         TEXT,
    
    -- 中医信息
    constitution    VARCHAR(32),
    constitution_score NUMERIC(5,2),
    zheng_type      VARCHAR(32),
    zheng_severity  VARCHAR(8),
    
    -- 风险评估
    risk_level      VARCHAR(16),
    risk_score      NUMERIC(5,2),
    
    -- 审计字段
    created_by      BIGINT REFERENCES users(id),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted      BOOLEAN DEFAULT FALSE
);

-- 索引
CREATE INDEX idx_patient_no ON patient(patient_no);
CREATE INDEX idx_patient_name ON patient(name);
CREATE INDEX idx_patient_phone ON patient(phone);
CREATE INDEX idx_patient_constitution ON patient(constitution);
CREATE INDEX idx_patient_zheng ON patient(zheng_type);
CREATE INDEX idx_patient_risk ON patient(risk_level);

-- ============================================
-- 3. 随访管理表
-- ============================================

-- 随访记录表
CREATE TABLE visit (
    id              BIGSERIAL PRIMARY KEY,
    patient_id      BIGINT NOT NULL REFERENCES patient(id),
    visit_no        VARCHAR(32) UNIQUE NOT NULL,
    visit_date      DATE NOT NULL,
    visit_type      VARCHAR(32) NOT NULL,
    
    -- 临床检查
    chief_complaint TEXT,
    present_illness TEXT,
    past_history    JSONB,
    family_history  JSONB,
    menstrual_history JSONB,
    
    -- 体格检查
    physical_exam   JSONB,
    breast_exam     JSONB,
    lymph_node_exam JSONB,
    
    -- 影像学检查
    ultrasound_exam JSONB,
    mammography     JSONB,
    mri             JSONB,
    
    -- BI-RADS 评估
    birads_category VARCHAR(8),
    birads_assessment TEXT,
    
    -- 实验室检查
    lab_tests       JSONB,
    tumor_markers   JSONB,
    
    -- 诊断
    preliminary_diagnosis TEXT,
    differential_diagnosis TEXT,
    
    -- 治疗建议
    treatment_plan  TEXT,
    followup_plan   TEXT,
    
    -- 审计字段
    created_by      BIGINT REFERENCES users(id),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted      BOOLEAN DEFAULT FALSE
);

-- 索引
CREATE INDEX idx_visit_patient ON visit(patient_id);
CREATE INDEX idx_visit_date ON visit(visit_date);
CREATE INDEX idx_visit_type ON visit(visit_type);
CREATE INDEX idx_visit_birads ON visit(birads_category);

-- ============================================
-- 4. 超声检查表
-- ============================================

-- 超声图像表
CREATE TABLE ultrasound (
    id              BIGSERIAL PRIMARY KEY,
    visit_id        BIGINT NOT NULL REFERENCES visit(id),
    image_no        VARCHAR(32) UNIQUE NOT NULL,
    image_path      VARCHAR(512) NOT NULL,
    image_type      VARCHAR(32),  -- B-mode/Color Doppler/Elasticity
    
    -- 扫描参数
    probe_freq      VARCHAR(32),
    depth           NUMERIC(5,2),
    gain            INTEGER,
    
    -- 图像质量
    quality_score   NUMERIC(5,2),
    plane_type      VARCHAR(32),
    
    -- BI-RADS 特征
    location        JSONB,
    size            JSONB,
    shape           VARCHAR(32),
    orientation     VARCHAR(32),
    margin          JSONB,
    echo_pattern    VARCHAR(32),
    posterior_feature VARCHAR(32),
    calcification   JSONB,
    vascularity     VARCHAR(32),
    
    -- AI 分析结果
    ai_segmentation JSONB,
    ai_score        NUMERIC(5,2),
    ai_prediction   VARCHAR(32),
    ai_confidence   NUMERIC(5,2),
    
    -- 审计字段
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by     BIGINT REFERENCES users(id),
    reviewed_at     TIMESTAMP
);

-- 索引
CREATE INDEX idx_ultrasound_visit ON ultrasound(visit_id);
CREATE INDEX idx_ultrasound_path ON ultrasound(image_path);
CREATE INDEX idx_ultrasound_quality ON ultrasound(quality_score);

-- ============================================
-- 5. 病灶表
-- ============================================

-- 病灶记录表
CREATE TABLE lesion (
    id              BIGSERIAL PRIMARY KEY,
    ultrasound_id   BIGINT NOT NULL REFERENCES ultrasound(id),
    lesion_no       VARCHAR(32) UNIQUE NOT NULL,
    
    -- 病灶特征
    location        JSONB,
    size            JSONB,  -- {length, width, height, unit}
    shape           VARCHAR(32),
    orientation     VARCHAR(32),
    margin          JSONB,
    echo_pattern    VARCHAR(32),
    posterior_feature VARCHAR(32),
    calcification   JSONB,
    vascularity     VARCHAR(32),
    elasticity      VARCHAR(32),
    
    -- BI-RADS 分级
    birads_category VARCHAR(8),
    birads_features JSONB,
    
    -- 病理结果
    pathology_type  VARCHAR(64),
    pathology_result VARCHAR(128),
    ihc_results     JSONB,
    
    -- 分子分型
    molecular_type  VARCHAR(32),
    er_status       VARCHAR(8),
    pr_status       VARCHAR(8),
    her2_status     VARCHAR(8),
    ki67_value      NUMERIC(5,2),
    
    -- 审计字段
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_lesion_ultrasound ON lesion(ultrasound_id);
CREATE INDEX idx_lesion_birads ON lesion(birads_category);
CREATE INDEX idx_lesion_pathology ON lesion(pathology_type);
CREATE INDEX idx_lesion_molecular ON lesion(molecular_type);

-- ============================================
-- 6. 诊断表
-- ============================================

-- 诊断记录表
CREATE TABLE diagnosis (
    id              BIGSERIAL PRIMARY KEY,
    lesion_id       BIGINT UNIQUE NOT NULL REFERENCES lesion(id),
    diagnosis_no    VARCHAR(32) UNIQUE NOT NULL,
    
    -- 诊断类型
    diagnosis_type  VARCHAR(32),  -- 影像/病理/临床
    diagnosis_date  DATE NOT NULL,
    
    -- ICD 编码
    icd10_code      VARCHAR(16),
    icd10_name      VARCHAR(256),
    
    -- 诊断结果
    diagnosis_result VARCHAR(512),
    malignancy      VARCHAR(16),  -- 良性/恶性/可疑
    
    -- 中医诊断
    tcm_diagnosis   VARCHAR(256),
    tcm_zheng       VARCHAR(32),
    tcm_method      VARCHAR(512),
    
    -- AI 辅助诊断
    ai_model        VARCHAR(64),
    ai_result       JSONB,
    ai_confidence   NUMERIC(5,2),
    doctor_review   TEXT,
    
    -- 审核
    status          VARCHAR(16) DEFAULT 'draft',
    reviewed_by     BIGINT REFERENCES users(id),
    reviewed_at     TIMESTAMP,
    
    -- 审计字段
    created_by      BIGINT REFERENCES users(id),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_diagnosis_lesion ON diagnosis(lesion_id);
CREATE INDEX idx_diagnosis_type ON diagnosis(diagnosis_type);
CREATE INDEX idx_diagnosis_date ON diagnosis(diagnosis_date);
CREATE INDEX idx_diagnosis_status ON diagnosis(status);

-- ============================================
-- 7. 治疗表
-- ============================================

-- 治疗计划表
CREATE TABLE treatment (
    id              BIGSERIAL PRIMARY KEY,
    diagnosis_id    BIGINT NOT NULL REFERENCES diagnosis(id),
    treatment_no    VARCHAR(32) UNIQUE NOT NULL,
    
    -- 治疗类型
    treatment_type  VARCHAR(64),  -- 手术/化疗/放疗/内分泌/靶向/中医
    treatment_phase VARCHAR(32),  -- 新辅助/辅助/姑息
    
    -- 治疗方案
    regimen_name    VARCHAR(256),
    regimen_details JSONB,
    
    -- 中医治疗
    tcm_prescription JSONB,
    tcm_method      TEXT,
    
    -- 时间
    start_date      DATE,
    end_date        DATE,
    duration_cycles INTEGER,
    
    -- 疗效评估
    response_evaluation VARCHAR(32),
    response_date   DATE,
    pfs_months      NUMERIC(5,2),
    os_months       NUMERIC(5,2),
    
    -- 不良反应
    adverse_events  JSONB,
    
    -- 状态
    status          VARCHAR(16) DEFAULT 'planned',
    
    -- 审计字段
    created_by      BIGINT REFERENCES users(id),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_treatment_diagnosis ON treatment(diagnosis_id);
CREATE INDEX idx_treatment_type ON treatment(treatment_type);
CREATE INDEX idx_treatment_status ON treatment(status);

-- ============================================
-- 8. 审计日志表
-- ============================================

CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    action          VARCHAR(64) NOT NULL,
    resource        VARCHAR(128) NOT NULL,
    resource_id     BIGINT,
    old_value       JSONB,
    new_value       JSONB,
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_resource ON audit_log(resource);
CREATE INDEX idx_audit_created ON audit_log(created_at);

-- ============================================
-- 9. 初始数据
-- ============================================

-- 插入角色
INSERT INTO roles (role_name, role_code, description, is_system) VALUES
('超级管理员', 'super_admin', '系统超级管理员', TRUE),
('医生', 'doctor', '执业医师', FALSE),
('技师', 'technician', '超声技师', FALSE),
('护士', 'nurse', '护理人员', FALSE),
('研究员', 'researcher', '科研人员', FALSE);

-- 插入权限
INSERT INTO permissions (permission_name, resource, action, description) VALUES
-- 患者管理
('patient:read', 'patient', 'read', '查看患者'),
('patient:create', 'patient', 'create', '新建患者'),
('patient:update', 'patient', 'update', '修改患者'),
('patient:delete', 'patient', 'delete', '删除患者'),
-- 随访管理
('visit:read', 'visit', 'read', '查看随访'),
('visit:create', 'visit', 'create', '新建随访'),
('visit:update', 'visit', 'update', '修改随访'),
-- 超声检查
('ultrasound:read', 'ultrasound', 'read', '查看超声'),
('ultrasound:upload', 'ultrasound', 'upload', '上传超声'),
('ultrasound:annotate', 'ultrasound', 'annotate', '标注超声'),
-- 诊断管理
('diagnosis:read', 'diagnosis', 'read', '查看诊断'),
('diagnosis:create', 'diagnosis', 'create', '新建诊断'),
('diagnosis:approve', 'diagnosis', 'approve', '审核诊断'),
-- 治疗管理
('treatment:read', 'treatment', 'read', '查看治疗'),
('treatment:create', 'treatment', 'create', '新建治疗'),
('treatment:update', 'treatment', 'update', '修改治疗'),
-- 系统管理
('user:manage', 'user', 'manage', '用户管理'),
('role:manage', 'role', 'manage', '角色管理'),
('system:config', 'system', 'config', '系统配置');

-- 分配权限给超级管理员角色
INSERT INTO role_permissions (role_id, permission_id)
SELECT 1, id FROM permissions;

-- 分配基础权限给医生角色
INSERT INTO role_permissions (role_id, permission_id)
SELECT 2, id FROM permissions 
WHERE resource IN ('patient', 'visit', 'ultrasound', 'diagnosis', 'treatment')
AND action IN ('read', 'create', 'update');

-- 插入默认管理员用户 (密码：admin123)
-- 使用 bcrypt 加密，实际应该用程序生成
INSERT INTO users (username, email, password_hash, real_name, role_id, is_active)
VALUES (
    'admin',
    'admin@breast-ai.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS2MebAJy',
    '系统管理员',
    1,
    TRUE
);

-- ============================================
-- 10. 视图和函数
-- ============================================

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为所有需要更新时间的表添加触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patient_updated_at BEFORE UPDATE ON patient
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_visit_updated_at BEFORE UPDATE ON visit
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_diagnosis_updated_at BEFORE UPDATE ON diagnosis
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_treatment_updated_at BEFORE UPDATE ON treatment
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建患者编号生成函数
CREATE OR REPLACE FUNCTION generate_patient_no()
RETURNS TRIGGER AS $$
BEGIN
    NEW.patient_no = 'P' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || 
                     LPAD(NEXTVAL('patient_id_seq')::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER generate_patient_no_before_insert
    BEFORE INSERT ON patient
    FOR EACH ROW
    WHEN (NEW.patient_no IS NULL)
    EXECUTE FUNCTION generate_patient_no();

-- 创建随访编号生成函数
CREATE OR REPLACE FUNCTION generate_visit_no()
RETURNS TRIGGER AS $$
BEGIN
    NEW.visit_no = 'V' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || 
                   LPAD(NEXTVAL('visit_id_seq')::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER generate_visit_no_before_insert
    BEFORE INSERT ON visit
    FOR EACH ROW
    WHEN (NEW.visit_no IS NULL)
    EXECUTE FUNCTION generate_visit_no();

-- ============================================
-- 11. 统计视图
-- ============================================

-- 患者统计视图
CREATE VIEW v_patient_stats AS
SELECT
    COUNT(*) AS total_patients,
    COUNT(*) FILTER (WHERE risk_level = 'high' OR risk_level = 'very_high') AS high_risk_count,
    COUNT(*) FILTER (WHERE constitution = '气郁质') AS qiyu_count,
    COUNT(*) FILTER (WHERE constitution = '痰湿质') AS tanshi_count,
    COUNT(*) FILTER (WHERE constitution = '血瘀质') AS xueyu_count,
    AVG(risk_score) AS avg_risk_score
FROM patient
WHERE is_deleted = FALSE;

-- BI-RADS 分布视图
CREATE VIEW v_birads_distribution AS
SELECT
    birads_category,
    COUNT(*) AS patient_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
FROM visit
WHERE birads_category IS NOT NULL AND is_deleted = FALSE
GROUP BY birads_category
ORDER BY birads_category;

-- 随访状态视图
CREATE VIEW v_followup_status AS
SELECT
    p.id AS patient_id,
    p.patient_no,
    p.name,
    MAX(v.visit_date) AS last_visit_date,
    p.next_followup_date,
    CASE
        WHEN p.next_followup_date < CURRENT_DATE THEN 'overdue'
        WHEN p.next_followup_date < CURRENT_DATE + INTERVAL '7 days' THEN 'upcoming'
        ELSE 'on_schedule'
    END AS status,
    CASE
        WHEN p.next_followup_date < CURRENT_DATE 
        THEN CURRENT_DATE - p.next_followup_date
        ELSE 0
    END AS overdue_days
FROM patient p
LEFT JOIN visit v ON p.id = v.patient_id
WHERE p.is_deleted = FALSE
GROUP BY p.id, p.patient_no, p.name, p.next_followup_date;

-- 诊断统计视图
CREATE VIEW v_diagnosis_stats AS
SELECT
    diagnosis_type,
    malignancy,
    COUNT(*) AS count,
    DATE_TRUNC('month', diagnosis_date) AS month
FROM diagnosis
GROUP BY diagnosis_type, malignancy, DATE_TRUNC('month', diagnosis_date)
ORDER BY month, diagnosis_type;

-- 治疗效果视图
CREATE VIEW v_treatment_outcomes AS
SELECT
    t.treatment_type,
    t.response_evaluation,
    COUNT(*) AS patient_count,
    AVG(t.pfs_months) AS avg_pfs,
    AVG(t.os_months) AS avg_os
FROM treatment t
WHERE t.status IN ('completed', 'ongoing')
GROUP BY t.treatment_type, t.response_evaluation;

COMMENT ON TABLE patient IS '患者基本信息表';
COMMENT ON TABLE visit IS '随访记录表';
COMMENT ON TABLE ultrasound IS '超声图像表';
COMMENT ON TABLE lesion IS '病灶记录表';
COMMENT ON TABLE diagnosis IS '诊断记录表';
COMMENT ON TABLE treatment IS '治疗计划表';
COMMENT ON TABLE users IS '用户表';
COMMENT ON TABLE roles IS '角色表';
COMMENT ON TABLE permissions IS '权限表';
COMMENT ON TABLE audit_log IS '审计日志表';
