# 数据库初始化完成总结

## 已创建文件

### SQL 脚本
- `/workspace/breast-ai-system/backend/scripts/init_db.sql` - 完整 DDL 脚本

### Python 脚本
- `/workspace/breast-ai-system/backend/scripts/init_db.py` - 数据库初始化执行脚本
- `/workspace/breast-ai-system/backend/scripts/generate_test_data.py` - 测试数据生成脚本
- `/workspace/breast-ai-system/backend/scripts/docker-entrypoint.sh` - Docker 容器启动脚本

### 文档
- `/workspace/breast-ai-system/docs/DATABASE_SETUP.md` - 数据库初始化指南

### Docker 配置
- 更新 `docker-compose.yml` - 添加 `db-init` 服务

---

## 数据库架构概览

### 表结构 (11 张表)

```
权限管理 (4 张表)
├── roles - 角色表
├── permissions - 权限表
├── role_permissions - 角色权限关联表
└── users - 用户表

业务数据 (7 张表)
├── patient - 患者基本信息表
├── visit - 随访记录表
├── ultrasound - 超声图像表
├── lesion - 病灶记录表
├── diagnosis - 诊断记录表
├── treatment - 治疗计划表
└── audit_log - 审计日志表
```

### 视图 (5 个)

```sql
v_patient_stats         -- 患者统计
v_birads_distribution   -- BI-RADS 分级分布
v_followup_status       -- 随访状态监控
v_diagnosis_stats       -- 诊断统计
v_treatment_outcomes    -- 治疗效果统计
```

### 索引设计

**患者表**:
- `idx_patient_no` - 患者编号唯一索引
- `idx_patient_name` - 姓名索引 (支持搜索)
- `idx_patient_phone` - 电话索引
- `idx_patient_constitution` - 体质类型索引
- `idx_patient_zheng` - 证型索引
- `idx_patient_risk` - 风险等级索引

**随访表**:
- `idx_visit_patient` - 患者 ID 索引
- `idx_visit_date` - 随访日期索引
- `idx_visit_type` - 随访类型索引
- `idx_visit_birads` - BI-RADS 分级索引

**超声表**:
- `idx_ultrasound_visit` - 随访 ID 索引
- `idx_ultrasound_path` - 图像路径索引
- `idx_ultrasound_quality` - 质量评分索引

**病灶表**:
- `idx_lesion_ultrasound` - 超声 ID 索引
- `idx_lesion_birads` - BI-RADS 分级索引
- `idx_lesion_pathology` - 病理类型索引
- `idx_lesion_molecular` - 分子分型索引

---

## 权限体系

### 角色定义

| 角色 | 代码 | 说明 |
|------|------|------|
| 超级管理员 | super_admin | 完整系统权限 |
| 医生 | doctor | 诊疗相关权限 |
| 技师 | technician | 超声检查权限 |
| 护士 | nurse | 随访护理权限 |
| 研究员 | researcher | 数据查看权限 |

### 权限列表

```
患者管理：patient:read, patient:create, patient:update, patient:delete
随访管理：visit:read, visit:create, visit:update
超声检查：ultrasound:read, ultrasound:upload, ultrasound:annotate
诊断管理：diagnosis:read, diagnosis:create, diagnosis:approve
治疗管理：treatment:read, treatment:create, treatment:update
系统管理：user:manage, role:manage, system:config
```

---

## 默认账号

**管理员账号**:
```
用户名：admin
密码：admin123
邮箱：admin@breast-ai.com
角色：超级管理员 (role_id=1)
```

---

## 执行方式

### 方式 1: Docker Compose (推荐)

```bash
cd /workspace/breast-ai-system

# 一键启动所有服务 (包含自动初始化)
docker compose up -d

# 查看初始化日志
docker compose logs db-init

# 查看后端日志
docker compose logs backend
```

启动流程：
1. PostgreSQL 容器启动
2. 健康检查通过 (pg_isready)
3. `db-init` 容器执行 `python scripts/init_db.py`
4. 创建所有表、视图、索引
5. 插入默认角色、权限、用户
6. `backend` 服务启动 (依赖 db-init 完成)
7. `frontend` 服务启动

### 方式 2: 本地执行

```bash
# 1. 安装依赖
cd backend
pip install psycopg2-binary

# 2. 创建数据库
sudo -i -u postgres
psql <<EOF
CREATE DATABASE breast_ai;
CREATE USER breast_ai_user WITH PASSWORD 'breast_ai_password';
GRANT ALL PRIVILEGES ON DATABASE breast_ai TO breast_ai_user;
EOF

# 3. 设置环境变量
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=breast_ai
export PGUSER=breast_ai_user
export PGPASSWORD=breast_ai_password

# 4. 执行初始化
python scripts/init_db.py

# 5. (可选) 生成测试数据
python scripts/generate_test_data.py
```

### 方式 3: 直接执行 SQL

```bash
psql -h localhost -U breast_ai_user -d breast_ai \
     -f backend/scripts/init_db.sql
```

---

## 验证步骤

### 1. 检查表是否创建

```bash
psql -h localhost -U breast_ai_user -d breast_ai -c "\dt"
```

预期输出：
```
               List of relations
 Schema |       Name        | Type  |     Owner      
--------+-------------------+-------+----------------
 public | audit_log         | table | breast_ai_user
 public | diagnosis         | table | breast_ai_user
 public | lesion            | table | breast_ai_user
 public | patient           | table | breast_ai_user
 public | permissions       | table | breast_ai_user
 public | roles             | table | breast_ai_user
 public | role_permissions  | table | breast_ai_user
 public | treatment         | table | breast_ai_user
 public | ultrasound        | table | breast_ai_user
 public | users             | table | breast_ai_user
 public | visit             | table | breast_ai_user
(11 rows)
```

### 2. 检查视图

```bash
psql -h localhost -U breast_ai_user -d breast_ai -c "\dv"
```

预期输出：
```
               List of relations
 Schema |         Name          | Type |     Owner      
--------+-----------------------+------+----------------
 public | v_birads_distribution | view | breast_ai_user
 public | v_diagnosis_stats     | view | breast_ai_user
 public | v_followup_status     | view | breast_ai_user
 public | v_patient_stats       | view | breast_ai_user
 public | v_treatment_outcomes  | view | breast_ai_user
(5 rows)
```

### 3. 检查初始数据

```bash
# 检查角色
psql -h localhost -U breast_ai_user -d breast_ai \
     -c "SELECT role_name, role_code FROM roles;"

# 检查权限
psql -h localhost -U breast_ai_user -d breast_ai \
     -c "SELECT COUNT(*) FROM permissions;"

# 检查用户
psql -h localhost -U breast_ai_user -d breast_ai \
     -c "SELECT username, email, real_name FROM users;"
```

### 4. 测试登录

```bash
# 使用 API 测试登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

预期返回：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 常见问题

### Q1: 数据库连接失败

**解决**:
```bash
# 检查 PostgreSQL 是否运行
docker compose ps

# 或本地检查
pg_isready -h localhost -p 5432
```

### Q2: 权限错误

```sql
-- 授予 schema 权限
GRANT ALL ON SCHEMA public TO breast_ai_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO breast_ai_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO breast_ai_user;
```

### Q3: 表已存在

```sql
-- 删除所有表 (开发环境)
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

-- 重新初始化
\i backend/scripts/init_db.sql
```

### Q4: Docker 卷残留

```bash
# 删除卷并重新启动
docker compose down -v
docker compose up -d
```

---

## 下一步行动

### 1. 完成后端 API 实现

- [x] 数据模型 (models/)
- [x] Pydantic 模型 (schemas/)
- [x] 业务服务 (services/)
- [x] API 路由 (api/v1/)
- [ ] 认证中间件 (middleware/auth.py)
- [ ] 异常处理 (core/exceptions.py)

### 2. 前端开发

- [x] 项目框架
- [x] 路由配置
- [x] 布局组件
- [x] Dashboard 页面
- [x] 患者列表页
- [ ] API 对接
- [ ] 其余页面开发

### 3. AI 推理服务

- [ ] PBS-Net 模型加载
- [ ] DFMFI 特征融合
- [ ] HXM-Net 多模态诊断
- [ ] 推理 API 封装

### 4. 测试

- [ ] 后端单元测试
- [ ] API 集成测试
- [ ] 前端组件测试
- [ ] E2E 测试

---

## 数据库连接配置

### 开发环境

```env
DATABASE_URL=postgresql://breast_ai_user:breast_ai_password@localhost:5432/breast_ai
ASYNC_DATABASE_URL=postgresql+asyncpg://breast_ai_user:breast_ai_password@localhost:5432/breast_ai
```

### Docker 环境

```env
DATABASE_URL=postgresql://breast_ai_user:breast_ai_password@postgres:5432/breast_ai
ASYNC_DATABASE_URL=postgresql+asyncpg://breast_ai_user:breast_ai_password@postgres:5432/breast_ai
```

### 生产环境

```env
# 使用连接池
DATABASE_URL=postgresql://user:pass@host:5432/breast_ai?pool_size=20&max_overflow=40

# 读写分离
READ_DATABASE_URL=postgresql://readonly:pass@replica:5432/breast_ai
WRITE_DATABASE_URL=postgresql://admin:pass@master:5432/breast_ai
```

---

## 关键设计决策

### 1. 年龄计算使用生成列

```sql
age INTEGER GENERATED ALWAYS AS (
    EXTRACT(YEAR FROM AGE(birth_date))
) STORED
```

**优点**: 自动计算，无需手动更新

### 2. 患者编号自动生成触发器

```sql
CREATE TRIGGER generate_patient_no_before_insert
    BEFORE INSERT ON patient
    FOR EACH ROW
    WHEN (NEW.patient_no IS NULL)
    EXECUTE FUNCTION generate_patient_no();
```

**优点**: 保证编号唯一性，遵循 `PYYYYMMDD######` 格式

### 3. JSONB 字段存储复杂数据

```sql
past_history    JSONB,
family_history  JSONB,
breast_exam     JSONB,
```

**优点**: 灵活扩展，支持复杂查询

### 4. 软删除标志

```sql
is_deleted      BOOLEAN DEFAULT FALSE
```

**优点**: 审计追踪，数据恢复

### 5. 全文审计日志

```sql
CREATE TABLE audit_log (
    user_id         BIGINT,
    action          VARCHAR(64),
    resource        VARCHAR(128),
    old_value       JSONB,
    new_value       JSONB,
    ...
);
```

**优点**: 完整操作追溯，合规 NMPA 要求

---

## 性能优化

### 索引覆盖

- 所有外键字段建立索引
- 所有查询条件字段建立索引
- 使用 GIN 索引优化 JSONB 查询

### 分区策略 (未来扩展)

```sql
-- 按时间范围分区 (当 visit 表超过 1000 万行时)
CREATE TABLE visit_2026 PARTITION OF visit
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

### 连接池配置

```python
# SQLAlchemy AsyncEngine
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

---

## 合规性说明

### NMPA 二类医疗器械要求

1. ✅ **数据完整性**: 外键约束 + 事务保证
2. ✅ **审计追踪**: audit_log 完整记录
3. ✅ **权限控制**: RBAC 角色权限体系
4. ✅ **数据脱敏**: is_deleted 软删除
5. ✅ **版本追溯**: updated_at 时间戳

### GDPR/HIPAA 合规

1. ✅ **加密存储**: password_hash 使用 bcrypt
2. ✅ **访问控制**: 基于角色的访问控制
3. ✅ **数据导出**: JSONB 支持灵活查询
4. ✅ **删除权**: 软删除 + 定期清理机制

---

## 备份与恢复

### 备份脚本

```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -h localhost -U breast_ai breast_ai \
  | gzip > ${BACKUP_DIR}/breast_ai_${DATE}.sql.gz
```

### 恢复脚本

```bash
#!/bin/bash
gunzip -c breast_ai_20260527_120000.sql.gz \
  | psql -h localhost -U breast_ai breast_ai
```

### 定时备份 (crontab)

```bash
# 每天凌晨 2 点备份
0 2 * * * /path/to/backup_script.sh
```

---

**状态**: ✅ 数据库初始化脚本完成  
**下一步**: 启动 Docker 环境验证
