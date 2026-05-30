# 影像 - 中医病机分析模块测试指南

## 后端实现完成

### 1. 数据库模型
- `backend/app/models/imaging_tcm.py` - ImagingTCMCorrelation 模型

### 2. 规则引擎
- `backend/app/services/imaging_tcm_engine.py` - ImagingTCMRuleEngine
  - 20+ 项影像特征规则
  - 4 个病机维度（瘀血/痰浊/毒邪/正虚）
  - 证据等级修正（A/B/C 级）
  - 病机组合识别

### 3. 服务层
- `backend/app/services/imaging_tcm_service.py` - ImagingTCMService
  - 特征提取
  - 规则引擎调用
  - 结果保存

### 4. API 路由
- `backend/app/routers/imaging_tcm.py`
  - `POST /api/v1/imaging-tcm/ultrasound/{id}/analyze` - 执行分析
  - `GET /api/v1/imaging-tcm/ultrasound/{id}/result` - 获取结果
  - `GET /api/v1/imaging-tcm/patient/{id}/history` - 患者历史
  - `POST /api/v1/imaging-tcm/batch/analyze` - 批量分析

### 5. Schema
- `backend/app/schemas/imaging_tcm.py` - 请求/响应模型

## 测试步骤

### 1. 启动后端

```bash
cd /workspace/breast-ai-system/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 访问 API 文档

```
http://localhost:8000/api/docs
```

找到 **"影像 - 中医病机分析"** 标签

### 3. 测试分析 API

由于需要数据库中有超声检查记录，先创建测试数据：

```bash
# 调用创建患者的 API
curl -X POST http://localhost:8000/api/v1/patient/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试患者",
    "age": 45,
    "gender": "女"
  }'

# 然后创建随访和超声检查...
```

### 4. 规则引擎单元测试

```bash
cd /workspace/breast-ai-system/backend
python3 << 'EOF'
from app.services.imaging_tcm_engine import ImagingTCMRuleEngine

# 创建引擎
engine = ImagingTCMRuleEngine()

# 测试用例：典型恶性超声表现
test_features = {
    "boundary_spiculated": True,
    "morphology_irregular": True,
    "aspect_ratio": 1.5,
    "echo_hypoechoic": True,
    "echo_heterogeneous": True,
    "calcification_micro": True,
    "cdfi_grade_2": True,
    "blood_flow_penetrating": True,
    "ri_high": True,
    "elasticity_4": True,
    "growth_moderate": True,
    "lesion_size_cm": 2.5,
}

# 执行分析
result = engine.analyze(test_features)

print("=== 中医病机分析结果 ===")
print(f"主要病机：{result.primary} (强度：{result.scores.get(result.primary, 0):.2f})")
print(f"次要病机：{', '.join(result.secondary)}")
print(f"病机组合：{result.pattern}")
print(f"病性：{result.nature}")
print(f"推荐治法：{result.recommended_therapy}")
print(f"推荐方剂：{result.recommended_formula}")
print(f"置信度：{result.confidence:.2f}")
print(f"证据等级：{result.evidence_level}")
EOF
```

### 5. 预期输出

```
=== 中医病机分析结果 ===
主要病机：stasis (强度：0.65)
次要病机：toxin
病机组合：瘀毒内阻
病性：实证为主
推荐治法：活血化瘀，解毒散结
推荐方剂：仙方活命饮合桃红四物汤加减
置信度：0.78
证据等级：B
```

## 数据库注意事项

当前数据库表尚未创建（需要正确的数据库连接）。请使用以下方式之一：

### 方式 1：等待数据库服务可用

当 PostgreSQL 服务启动后，表会自动创建。

### 方式 2:使用内存模式测试

修改配置使用 SQLite 进行测试：

```python
DATABASE_URL = "sqlite+aiosqlite:////:memory:"
```

### 方式 3：Mock 测试

在测试环境中 mock 数据库操作。

## 前端集成

前端页面开发待完成。需要：

1. 在超声检查报告页面添加"中医病机分析" Tab
2. 显示病机倾向雷达图
3. 证据等级展示
4. 免责声明

## 下一步

- [ ] 数据库表创建（等待 DB 服务）
- [ ] 完整 API 测试（集成测试）
- [ ] 前端页面开发
- [ ] 临床验证数据收集

---

**实施进度**: Phase 1-2 完成 ✅  
**状态**: 等待数据库就绪后继续测试
