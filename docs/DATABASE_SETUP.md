# 数据库初始化指南

## 方法一：Docker Compose（推荐）

### 启动所有服务（包含自动初始化）

```bash
cd breast-ai-system
docker compose up -d

# 查看初始化日志
docker compose logs db-init
```

初始化流程：
1. PostgreSQL 启动
2. 健康检查通过
3. `db-init` 容器自动执行 `init_db.py`
4. 创建所有表、视图和初始数据
5. `backend` 服务在初始化完成后启动

### 手动重新初始化

```bash
# 删除现有数据
docker compose down -v

# 重新启动并初始化
docker compose up -d
```

## 方法二：本地执行

### 前提条件

1. 安装 PostgreSQL 14+
2. 安装 Python 依赖

```bash
cd backend
pip install psycopg2-binary
```

### 创建数据库

```bash
# 切换到 postgres 用户
sudo -i -u postgres

# 创建数据库和用户
psql <<EOF
CREATE DATABASE breast_ai;
CREATE USER breast_ai_user WITH PASSWORD 'breast_ai_password';
GRANT ALL PRIVILEGES ON DATABASE breast_ai TO breast_ai_user;
\\c breast_ai
GRANT ALL ON SCHEMA public TO breast_ai_user;
EOF
```

### 执行初始化脚本

```bash
# 设置环境变量
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=breast_ai
export PGUSER=breast_ai_user
export PGPASSWORD=breast_ai_password

# 执行初始化
cd backend
python scripts/init_db.py
```

### 验证初始化

```bash
psql -h localhost -U breast_ai_user -d breast_ai

# 查看所有表
\dt

# 查看用户
SELECT username, email, real_name FROM users;

# 查看角色
SELECT role_name, role_code FROM roles;
```

## 方法三：直接使用 SQL 文件

```bash
psql -h localhost -U breast_ai_user -d breast_ai -f backend/scripts/init_db.sql
```

## 创建的表（共 11 张）

| 表名 | 说明 |
|------|------|
| `roles` | 角色表 |
| `permissions` | 权限表 |
| `role_permissions` | 角色权限关联表 |
| `users` | 用户表 |
| `patient` | 患者基本信息表 |
| `visit` | 随访记录表 |
| `ultrasound` | 超声图像表 |
| `lesion` | 病灶记录表 |
| `diagnosis` | 诊断记录表 |
| `treatment` | 治疗计划表 |
| `audit_log` | 审计日志表 |

## 创建的视图（共 5 个）

| 视图名 | 说明 |
|--------|------|
| `v_patient_stats` | 患者统计 |
| `v_birads_distribution` | BI-RADS 分布 |
| `v_followup_status` | 随访状态 |
| `v_diagnosis_stats` | 诊断统计 |
| `v_treatment_outcomes` | 治疗效果 |

## 默认账号

**管理员账号：**
- 用户名：`admin`
- 密码：`admin123`
- 角色：超级管理员

**测试数据：**
- 角色：5 个（超级管理员、医生、技师、护士、研究员）
- 权限：19 个（覆盖所有资源操作）

## 常见问题

### 1. 权限错误

```sql
-- 授予 schema 权限
GRANT ALL ON SCHEMA public TO breast_ai_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO breast_ai_user;
```

### 2. 扩展不存在

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### 3. 序列权限

```sql
-- 授予序列权限
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO breast_ai_user;
```

### 4. 查看表结构

```sql
-- 查看 patient 表结构
\d patient

-- 查看所有索引
\di
```

### 5. 清空数据（开发环境）

```sql
-- 删除所有表（级联）
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

-- 重新执行初始化
\i backend/scripts/init_db.sql
```

## 数据库连接字符串

```bash
# 开发环境
postgresql://breast_ai_user:breast_ai_password@localhost:5432/breast_ai

# Docker 环境
postgresql://breast_ai_user:breast_ai_password@postgres:5432/breast_ai

# AsyncPG（后端使用）
postgresql+asyncpg://breast_ai_user:breast_ai_password@postgres:5432/breast_ai
```

## 下一步

数据库初始化完成后：

1. 启动后端服务：`cd backend && uvicorn app.main:app --reload`
2. 访问 API 文档：http://localhost:8000/docs
3. 使用 admin/admin123 登录测试
