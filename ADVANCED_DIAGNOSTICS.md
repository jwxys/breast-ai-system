# 乳腺诊断系统 - 高级功能使用指南

## 概述

本系统提供以下高级诊断功能：

1. **BI-RADS 智能分级** - 基于 ACR 第 5 版指南自动评估
2. **分子分型预测** - 基于病理标志物预测分子亚型
3. **AI 影像分析** - 视觉大模型辅助诊断
4. **综合决策支持** - 多模态整合的诊断建议

---

## 1. BI-RADS 智能分级

### 功能说明

基于超声征象自动计算 BI-RADS 分级和恶性风险。

### 使用示例

```python
from app.diagnosis.services.birads_engine import BIRADSEngine

# 构建超声征象
ultrasound_features = {
    "shape": "irregular",                    # 不规则形
    "orientation": "not_parallel",           # taller-than-wide (恶性征象)
    "margin_types": ["angular", "spiculated"],  # 成角 + 毛刺
    "echo_pattern": "hypoechoic",            # 低回声
    "echo_homogeneity": "heterogeneous",     # 不均匀
    "calcification_present": True,
    "calcification_types": ["fine"],         # 细小钙化
    "vascularity_grade": "grade_2",          # 血流丰富
    "vessel_pattern": "irregular",           # 血管不规则
    "elastography": "hard",                  # 弹性成像示硬
    "strain_ratio": 4.2,                      # 应变比值>3.5
    "posterior_features": ["shadowing"]      # 后方衰减
}

# 评估
result = BIRADSEngine.assess(ultrasound_features)

print(f"BI-RADS 分级：{result.birads_category.value}")  # 输出：5
print(f"恶性风险：{result.risk_percentage}%")          # 输出：97.5
print(f"处理建议：{result.recommendation}")             # 输出：高度提示恶性，建议手术切除
print(f"关键征象：{result.key_features}")
```

### 输出示例

```
BI-RADS 分级：5
恶性风险：97.5%
处理建议：高度提示恶性，建议手术切除
关键征象：[
    "形状：不规则形",
    "纵横比>1 (taller-than-wide)",
    "边缘：成角, 毛刺状",
    "回声：低回声",
    "伴钙化",
    "血流丰富",
    "后方回声衰减"
]
```

### BI-RADS 分级标准

| 分级 | 恶性风险 | 处理建议 |
|------|---------|---------|
| 0 级 | - | 需要进一步检查 |
| 1 级 | 0% | 常规筛查 |
| 2 级 | 0% | 6-12 个月随访 |
| 3 级 | ≤2% | 3-6 个月短期随访 |
| 4A 级 | 2-10% | 穿刺活检 |
| 4B 级 | 10-50% | 穿刺活检 |
| 4C 级 | 50-95% | 穿刺活检或手术 |
| 5 级 | >95% | 手术切除 |
| 6 级 | 100% | 综合治疗 |

---

## 2. 分子分型预测

### 功能说明

基于免疫组化标志物 (ER/PR/HER2/Ki-67) 预测分子分型，指导个体化治疗。

### 使用示例

```python
from app.diagnosis.services.molecular_subtype_predictor import MolecularSubtypePredictor

# 输入病理数据
prediction = MolecularSubtypePredictor.predict(
    er_status=True,              # ER 阳性
    pr_percentage=80,            # PR 80% 阳性
    her2_status=0,               # HER2 阴性
    ki67_percentage=10,          # Ki-67 10%
    grade="G1"                   # 组织学分级 G1
)

print(f"分子分型：{prediction.subtype.value}")
print(f"置信度：{prediction.confidence:.1%}")
print(f"治疗方案：{prediction.treatment_plan}")
```

### 输出示例

```
分子分型：Luminal A
置信度：95.0%

治疗方案:
{
    "内分泌治疗": "首选 (他莫昔芬/芳香化酶抑制剂)",
    "化疗": "通常不需要 (低复发风险)",
    "靶向治疗": "不需要 (HER2 阴性)",
    "放疗": "保乳术后必需，部分全切患者可豁免",
    "预后": "最好，5 年生存率>90%"
}
```

### 分子分型判定标准

| 分型 | ER | PR | HER2 | Ki-67 | 占比 | 预后 |
|------|----|----|------|-------|------|------|
| Luminal A | + | ≥20% | - | <14% | 40-50% | 最好 |
| Luminal B (HER2-) | + | <20% | - | ≥14% | 20-30% | 较好 |
| Luminal B (HER2+) | + | 任意 | + | 任意 | 10-15% | 中等 |
| HER2 富集型 | - | - | + | 任意 | 15-20% | 抗 HER2 改善 |
| 基底样型 (三阴性) | - | - | - | 任意 | 15-20% | 较差 |

---

## 3. AI 影像分析

### 功能说明

集成 Kimi/通义视觉大模型，自动分析超声图像。

### 使用示例

```python
from app.diagnosis.services.ai_diagnosis_service import AIDiagnosisService

# 初始化服务
ai_service = AIDiagnosisService(
    api_key="sk-xxx",           # Kimi API Key
    model_name="kimi-vision"
)

# 分析超声图像
result = await ai_service.analyze_ultrasound(
    image_urls=[
        "https://storage/ultrasound/patient_001_01.jpg",
        "https://storage/ultrasound/patient_001_02.jpg"
    ],
    patient_info={
        "age": 45,
        "gender": "女",
        "symptoms": "左侧乳房可触及肿块 2 周"
    }
)

print(f"AI 检测到病灶：{result.detected}")
print(f"AI 预测 BI-RADS: {result.birads_prediction}")
print(f"恶性概率：{result.malignancy_probability:.1%}")
print(f"置信度：{result.confidence:.1%}")
print(f"鉴别诊断：{result.differential_diagnosis}")
```

### AI 分析提示词

AI 服务使用以下结构化提示词分析图像：

```
你是一位经验丰富的乳腺超声诊断专家。请分析提供的乳腺超声图像：

1. 病灶检测与定位
   - 是否发现可疑病灶？
   - 病灶位置和范围
   - 单发还是多发？

2. 形态学特征分析
   - 形状：椭圆形/圆形/不规则形
   - 纵横比：平行/非平行
   - 边缘特征：清晰/成角/分叶/毛刺

3. 内部回声
   - 回声模式：无/低/等/高/混合
   - 均匀性：均匀/不均匀

4. 钙化分析
   - 是否伴钙化？
   - 钙化类型

5. CDFI 血流
   - 血流分级 (Adler 0-3)
   - 血管形态

6. BI-RADS 分级预测
   - 0-6 级分类

7. 恶性风险评估
   - 恶性概率 (0-100%)
   - 关键恶性征象

8. 鉴别诊断
   - 前 3 位可能诊断
   - 建议进一步检查
```

---

## 4. 综合诊断决策

### 功能说明

整合多项分析结果，生成综合诊断报告。

### 使用示例

```python
from app.shared.services.diagnosis_service import DiagnosisService
from app.models.lesion import Lesion

# 创建服务实例
service = DiagnosisService(db=session)

# 获取病灶
lesion = session.query(Lesion).filter(Lesion.id == 1).first()

# 综合评估
result = await service.comprehensive_assessment(lesion)

print(f"BI-RADS 分级：{result['birads_assessment']['birads_category']}")
print(f"分子分型：{result.get('molecular_subtype', {}).get('subtype', '未检测')}")
print(f"诊断结论：{result['conclusion']}")
```

### 综合报告结构

```json
{
  "lesion_id": 1,
  "lesion_no": "LSN20260103001",
  "assessment_time": "2026-01-03T10:30:00",
  
  "birads_assessment": {
    "birads_category": "4B",
    "malignancy_risk": "30%",
    "recommendation": "中度可疑，建议穿刺活检",
    "key_features": [
      "形状：不规则形",
      "边缘：成角",
      "回声：低回声"
    ]
  },
  
  "molecular_subtype": {
    "subtype": "Luminal B (HER2-)",
    "confidence": "85.0%",
    "treatment_plan": {
      "内分泌治疗": "必需",
      "化疗": "通常需要",
      "靶向治疗": "不需要"
    }
  },
  
  "conclusion": "病灶编号：LSN20260103001 | BI-RADS 分级：4B 类 | 恶性风险：30% | 分子分型：Luminal B (HER2-) | 处理建议：中度可疑，建议穿刺活检"
}
```

---

## 5. API 接口

### POST /api/v1/diagnosis/assess

**请求**

```json
{
  "lesion_id": 1,
  "include_ai_analysis": true,
  "image_urls": ["url1", "url2"]
}
```

**响应**

```json
{
  "code": 200,
  "data": {
    "lesion_id": 1,
    "birads_category": "4B",
    "malignancy_probability": 0.30,
    "molecular_subtype": "Luminal B (HER2-)",
    "treatment_recommendation": ["穿刺活检", "化疗", "内分泌治疗"],
    "ai_analysis": {
      "detected": true,
      "confidence": 0.87
    }
  }
}
```

---

## 6. 临床应用流程

### 标准诊断流程

```
1. 超声检查
   ↓
2. AI 影像分析 (可选)
   ↓
3. BI-RADS 智能分级
   ↓
4. 穿刺活检 (如 BI-RADS ≥4)
   ↓
5. 病理检查 + IHC
   ↓
6. 分子分型预测
   ↓
7. 综合诊断报告
   ↓
8. 个体化治疗方案
```

### BI-RADS 3 类管理

```
BI-RADS 3 类 → 3-6 个月短期随访
   ↓
连续 2-3 年稳定 → 降级为 BI-RADS 2
   ↓
随访期间进展 → 升级为 BI-RADS 4，穿刺活检
```

---

## 7. 系统配置

### 环境变量

```bash
# AI 服务配置
KIMI_API_KEY=sk-xxx
TONGYI_API_KEY=sk-yyy

# 服务配置
AI_SERVICE_URL=http://localhost:8001
```

### 依赖安装

```bash
pip install httpx numpy scipy
```

---

## 8. 参考资料

### 临床指南

1. **ACR BI-RADS Atlas, 5th Edition**
   - 超声评估标准
   - BI-RADS 分级定义

2. **St. Gallen International Consensus Guidelines**
   - 乳腺癌分子分型
   - 治疗推荐

3. **ASCO/CAP Guidelines**
   - ER/PR/HER2 检测标准
   - Ki-67 评分

### 算法依据

1. **恶性征象权重**: 基于 Meta 分析 (BMJ 2018)
2. **taller-than-wide**: OR=7.0 (最强恶性征象)
3. **毛刺状边缘**: OR=8.0
4. **应变比值>3.5**: 特异性 95%

---

## 9. 免责声明

本系统为辅助诊断工具，不能替代专业医师的临床判断。所有诊断决策应结合临床表现、其他检查结果和医师经验综合判断。
