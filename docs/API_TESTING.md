# API 测试报告

## 状态

**后端服务**: ⏸️ 暂停（需要数据库支持）

当前环境缺少 PostgreSQL 数据库，无法启动完整的后端服务。

## 已完成的工作

### 1. 认证模块 ✅

**文件**: `backend/app/api/v1/auth.py`

实现了 OAuth2 + JWT 认证：
- POST `/api/v1/auth/login` - 用户登录
- GET `/api/v1/auth/me` - 获取当前用户信息

**登录示例**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**预期响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 2. 用户模型 ✅

**文件**: `backend/app/models/user.py`

定义了完整的 RBAC 权限模型：
- `User` - 用户表
- `Role` - 角色表
- `Permission` - 权限表
- `RolePermission` - 角色权限关联表

### 3. 认证中间件 ✅

**文件**: `backend/shared/middleware/auth.py`

实现了 JWT Token 验证：
- 自动验证 Bearer Token
- 跳过公开路径（登录、健康检查、API 文档）
- 将用户信息注入请求上下文

### 4. 数据库初始化脚本 ✅

**文件**: `backend/scripts/init_db.sql` (772 行)

完整的 DDL 脚本包含：
- 11 张表（权限 + 业务）
- 5 个统计视图
- 触发器和存储过程
- 初始数据（角色、权限、管理员账号）

### 5. 数据模型 ✅

已创建所有核心模型：
- `Patient` - 患者
- `Visit` - 随访
- `UltrasoundExam` - 超声检查
- `Lesion` - 病灶
- `Diagnosis` - 诊断
- `TreatmentPlan` - 治疗计划
- `TCMPrescription` - 中医处方

## 启动步骤

### 方法 1: Docker Compose（推荐）

```bash
cd /workspace/breast-ai-system
docker compose up -d
```

这会自动：
1. 启动 PostgreSQL 14
2. 执行 `init_db.sql` 初始化数据库
3. 启动后端服务
4. 启动前端服务

### 方法 2: 本地环境

```bash
# 1. 安装 PostgreSQL
sudo apt install postgresql-14

# 2. 创建数据库
sudo -u postgres psql <<EOF
CREATE DATABASE breast_ai;
CREATE USER breast_ai_user WITH PASSWORD 'breast_ai_password';
GRANT ALL PRIVILEGES ON DATABASE breast_ai TO breast_ai_user;
EOF

# 3. 执行初始化
cd backend
python scripts/init_db.py

# 4. 启动后端
uvicorn app.main:create_app --host 0.0.0.0 --port 8000 --factory

# 5. 测试登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## API 端点

### 认证相关
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 用户登录 |
| GET | `/api/v1/auth/me` | 获取当前用户 |

### 患者管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/patient/` | 患者列表 |
| POST | `/api/v1/patient/` | 创建患者 |
| GET | `/api/v1/patient/{id}` | 患者详情 |
| PUT | `/api/v1/patient/{id}` | 更新患者 |
| DELETE | `/api/v1/patient/{id}` | 删除患者 |

### 随访管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/visit/` | 随访列表 |
| POST | `/api/v1/visit/` | 创建随访 |
| GET | `/api/v1/visit/{id}` | 随访详情 |
| PUT | `/api/v1/visit/{id}` | 更新随访 |

### 超声检查
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/ultrasound/upload` | 上传图像 |
| POST | `/api/v1/ultrasound/annotate` | AI 标注 |
| GET | `/api/v1/ultrasound/{id}` | 详情 |

### 诊断管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/diagnosis/` | 诊断列表 |
| POST | `/api/v1/diagnosis/` | 创建诊断 |
| POST | `/api/v1/diagnosis/zheng-type` | 中医证型识别 |

### 治疗管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/treatment/` | 治疗列表 |
| POST | `/api/v1/treatment/` | 创建治疗计划 |
| POST | `/api/v1/treatment/recommend` | 治疗方案推荐 |

## 默认账号

```
用户名：admin
密码：admin123
角色：超级管理员
```

## 下一步

1. **安装 Docker** - 推荐使用 Docker Compose 一键启动
2. **或安装 PostgreSQL** - 在本地环境安装数据库
3. **执行初始化** - 运行 `python scripts/init_db.py`
4. **启动服务** - `uvicorn app.main:create_app --factory`
5. **访问 API 文档** - http://localhost:8000/api/docs

## 相关文件

**核心代码**:
- `backend/app/api/v1/auth.py` - 认证 API
- `backend/app/models/user.py` - 用户模型
- `backend/shared/middleware/auth.py` - 认证中间件
- `backend/app/core/exceptions.py` - 异常处理

**数据库**:
- `backend/scripts/init_db.sql` - DDL 脚本
- `backend/scripts/init_db.py` - 初始化执行脚本
- `backend/scripts/generate_test_data.py` - 测试数据生成
- `docs/DATABASE_SETUP.md` - 数据库安装指南
- `docs/DB_INIT_SUMMARY.md` - 初始化总结

**配置**:
- `backend/app/core/config.py` - 应用配置
- `backend/app/core/database.py` - 数据库连接
- `docker-compose.yml` - Docker 编排
