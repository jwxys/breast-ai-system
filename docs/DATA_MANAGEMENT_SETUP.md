# 数据管理模块 - 快速启动指南

## 📦 已完成实现

### 后端代码
- ✅ **数据模型**: `backend/app/models/data_management.py` (412 行)
- ✅ **服务层**: `backend/app/services/data_management_service.py` (510 行)
- ✅ **API 路由**: `backend/app/api/v1/data_management.py` (580 行)
- ✅ **数据库脚本**: `backend/scripts/init_data_management.sql` (420 行)

### 前端代码
- ✅ **管理页面**: `frontend/src/pages/DataManagement/index.tsx` (450 行)
- ✅ **样式文件**: `frontend/src/pages/DataManagement/index.css` (50 行)

---

## 🚀 启动步骤

### 1. 数据库初始化

```bash
# 进入 backend 目录
cd /workspace/breast-ai-system/backend

# 执行数据管理模块 SQL 脚本
PGPASSWORD='breast_ai_pass2024' psql -h localhost -U breast_ai \
  -d breast_ai_db -f scripts/init_data_management.sql

# 验证数据
PGPASSWORD='breast_ai_pass2024' psql -h localhost -U breast_ai \
  -d breast_ai_db -c "
  SELECT 
    'model_weight' as table_name, COUNT(*) as count FROM model_weight
  UNION ALL SELECT 'training_dataset', COUNT(*) FROM training_dataset
  UNION ALL SELECT 'public_dataset', COUNT(*) FROM public_dataset
  UNION ALL SELECT 'model_dataset_relation', COUNT(*) FROM model_dataset_relation;
"
```

**预期输出**:
```
table_name             | count
-----------------------+-------
model_weight           |     5
training_dataset       |     4
public_dataset         |     3
model_dataset_relation |     5
```

### 2. 创建权重存储目录

```bash
cd /workspace/breast-ai-system/backend

# 创建目录
mkdir -p models uploads/weights

# 查看 README
cat models/README.md

# (可选) 下载权重文件
# wget https://example.com/weights/pbs_net_v12.pth -O models/pbs_net_v12.pth
# wget https://example.com/weights/dfmfi_v20.pth -O models/dfmfi_v20.pth
# wget https://example.com/weights/hxm_net_v15.pth -O models/hxm_net_v15.pth
# wget https://example.com/weights/tcm_constitution_v31.pth -O models/tcm_constitution_v31.pth
# wget https://example.com/weights/tcm_syndrome_v23.pth -O models/tcm_syndrome_v23.pth
```

### 3. 启动后端服务

```bash
cd /workspace/breast-ai-system/backend

# 设置环境变量
export DATABASE_URL="postgresql+asyncpg://breast_ai:breast_ai_pass2024@localhost:5432/breast_ai_db"

# 启动后端
uvicorn app.main:create_app --host 0.0.0.0 --port 8000 --factory

# 或者后台运行
nohup uvicorn app.main:create_app --host 0.0.0.0 --port 8000 --factory > /tmp/backend.log 2>&1 &
```

### 4. 启动前端

```bash
cd /workspace/breast-ai-system/frontend

# 安装依赖 (如果未安装)
npm install

# 启动开发服务器
npm run dev
```

---

## 🧪 验证 API

### 测试模型权重

```bash
# 获取所有模型权重
curl http://localhost:8000/api/v1/data/weights | python3 -m json.tool

# 获取西医分支模型
curl "http://localhost:8000/api/v1/data/weights?branch=western" | python3 -m json.tool

# 获取统计信息
curl http://localhost:8000/api/v1/data/weights/stats | python3 -m json.tool

# 获取特定模型详情
curl http://localhost:8000/api/v1/data/weights/1 | python3 -m json.tool
```

### 测试数据集

```bash
# 获取训练数据集
curl http://localhost:8000/api/v1/data/datasets | python3 -m json.tool

# 按类型筛选
curl "http://localhost:8000/api/v1/data/datasets?dataset_type=ultrasound"

# 获取公开数据集
curl http://localhost:8000/api/v1/data/public-datasets | python3 -m json.tool

# 按模态筛选
curl "http://localhost:8000/api/v1/data/public-datasets?modality=ultrasound"
```

### 测试创建操作

```bash
# 创建新模型权重
curl -X POST http://localhost:8000/api/v1/data/weights \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "测试模型",
    "model_code": "test-model",
    "version": "v1.0",
    "branch": "western",
    "file_size_mb": 100.0,
    "training_data_count": 1000,
    "metrics": {"accuracy": 0.90},
    "ethics_approval_no": "IRB-TEST-001"
  }' | python3 -m json.tool

# 关联模型和数据集
curl -X POST "http://localhost:8000/api/v1/data/datasets/1/link-model?model_id=6"
```

---

## 📊 API 端点总览

### 模型权重 (4 个)

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/data/weights` | GET | 获取权重列表 |
| `/api/v1/data/weights/stats` | GET | 获取统计 |
| `/api/v1/data/weights/{id}` | GET | 获取详情 |
| `/api/v1/data/weights` | POST | 创建权重 |

### 训练数据集 (4 个)

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/data/datasets` | GET | 获取列表 |
| `/api/v1/data/datasets/{id}` | GET | 获取详情 |
| `/api/v1/data/datasets` | POST | 创建数据集 |
| `/api/v1/data/datasets/{id}/link-model` | POST | 关联模型 |

### 公开数据集 (2 个)

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/data/public-datasets` | GET | 获取列表 |
| `/api/v1/data/public-datasets/{id}/download` | POST | 标记下载 |

### 推理记录 (2 个)

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/data/inference-records` | GET | 获取记录 |
| `/api/v1/data/inference-records` | POST | 创建记录 |

### 报告管理 (2 个)

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/data/reports` | GET | 获取列表 |
| `/api/v1/data/reports` | POST | 创建报告 |

### 随访记录 (3 个)

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/data/followup-records` | GET | 获取记录 |
| `/api/v1/data/followup-records` | POST | 创建记录 |
| `/api/v1/data/followup-records/overdue` | GET | 超期随访 |

---

## 🎨 前端访问

启动前端后访问：

**http://localhost:5173/#/data**

### 页面功能

1. **总览 Tab**
   - 4 个统计卡片
   - 分支权重分布饼图
   - 数据类型分布柱状图

2. **模型权重 Tab**
   - 5 个模型列表
   - 性能指标 Badge
   - 分支标签 (西医/中医)
   - 伦理审批状态

3. **训练数据集 Tab**
   - 4 个自研数据集
   - 数据来源和地区
   - 数据量和格式

4. **公开数据集 Tab**
   - 3 个公开数据集
   - 访问类型标签
   - 下载状态
   - 下载按钮

---

## 📝 数据样例

### 模型权重响应

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "model_name": "PBS-Net 病灶分割模型",
      "model_code": "pbs-net",
      "version": "v1.2",
      "branch": "western",
      "weight_file": "pbs_net_v12.pth",
      "file_size_mb": 128.0,
      "file_path": "models/pbs_net_v12.pth",
      "training_data_count": 2500,
      "metrics": {
        "dice": 0.87,
        "iou": 0.78,
        "hd95": 3.2,
        "inference_time_ms": 45
      },
      "ethics_approval_no": "IRB-2023-BREAST-001",
      "is_active": true,
      "is_published": true
    }
  ]
}
```

### 统计信息响应

```json
{
  "code": 200,
  "data": {
    "total": 5,
    "by_branch": {
      "western": 3,
      "tcm": 2
    },
    "total_size_mb": 616.0
  }
}
```

---

## 🔧 常见问题

### Q1: 数据库连接失败？

**A**: 检查 PostgreSQL 服务状态
```bash
service postgresql status
service postgresql start
```

### Q2: API 404 错误？

**A**: 确保后端服务已启动且使用了正确的路由前缀
```bash
curl http://localhost:8000/health
```

### Q3: 前端页面空白？

**A**: 检查浏览器控制台是否有错误，确认路由配置正确
```bash
# 重新启动前端
cd frontend && npm run dev
```

### Q4: 权重文件不存在？

**A**: 权重文件需要单独下载或训练
```bash
ls -lh backend/models/*.pth
```

---

## 📚 相关文档

- [后端实现完整报告](./DATA_MANAGEMENT_BACKEND_COMPLETE.md)
- [数据管理模块完成报告](./DATA_MANAGEMENT_COMPLETE.md)
- [权重来源说明](./WEIGHT_SOURCE.md)
- [API 测试指南](./API_TESTING.md)

---

**最后更新**: 2026-05-27  
**维护**: AI 研发中心
