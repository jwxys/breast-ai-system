# 乳腺 AI 辅助诊断系统 - 数据流转深度分析与规范

**文档版本**: v1.0  
**创建时间**: 2026-05-28  
**适用范围**: 系统设计、开发、测试、运维

---

## 📋 目录

1. [数据流转分析框架](#1-数据流转分析框架)
2. [核心数据实体定义](#2-核心数据实体定义)
3. [患者就诊数据流转](#3-患者就诊数据流转)
4. [AI 推理数据流转](#4-ai 推理数据流转)
5. [报告生成数据流转](#5-报告生成数据流转)
6. [中医诊疗数据流转](#6-中医诊疗数据流转)
7. [数据规范与接口标准](#7-数据规范与接口标准)
8. [异常处理与容错机制](#8-异常处理与容错机制)

---

## 1. 数据流转分析框架

### 1.1 分析维度

每个数据处理环节从以下维度进行分析：

| 维度 | 说明 |
|------|------|
| **输入** | 数据来源、格式、必填/可选字段、验证规则 |
| **处理** | 业务逻辑、数据转换、计算规则、调用服务 |
| **输出** | 结果格式、数据结构、传递给下一环节 |
| **存储** | 持久化表、字段映射、索引设计 |
| **异常** | 错误类型、处理策略、回滚机制 |

### 1.2 系统数据流总览

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   患者信息   │ ──→ │  超声检查   │ ──→ │  AI 推理    │
│   录入登记   │     │  图像上传   │     │  分析诊断   │
└─────────────┘     └─────────────┘     └─────────────┘
       ↓                    ↓                    ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Patient    │     │ Ultrasound  │     │  Inference  │
│   Table     │     │   Table     │     │   Service   │
└─────────────┘     └─────────────┘     └─────────────┘
                                               ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   报告发布   │ ←── │   医生审核   │ ←── │  诊断结果   │
│   归档存储   │     │   修改确认   │     │  生成报告   │
└─────────────┘     └─────────────┘     └─────────────┘
       ↓                    ↓                    ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Report    │     │  Diagnosis  │     │   Report    │
│   Table     │     │   Table     │     │   Table     │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 1.3 数据状态机

```
患者数据状态流转:
[登记] → [初诊中] → [检查中] → [诊断中] → [审核中] → [已发布] → [随访中] → [归档]

AI 推理状态流转:
[待处理] → [处理中] → [成功/失败] → [已记录] → [已使用]

报告状态流转:
[草稿] → [待审核] → [审核通过/驳回] → [已发布] → [已归档]
```

---

## 2. 核心数据实体定义

### 2.1 患者 (Patient)

```python
# 输入数据结构
{
    "name": str,                    # 必填，1-64 字符
    "gender": str,                  # 必填，枚举：['M', 'F']
    "birth_date": date,             # 必填，ISO8601 格式
    "id_card": str,                 # 可选，18 位身份证号，唯一
    "phone": str,                   # 可选，11 位手机号
    "email": str,                   # 可选，邮箱格式
    "address": str,                 # 可选，最多 256 字符
    "constitution": str,            # 可选，中医体质类型
    "risk_level": str,              # 可选，风险等级 ['LOW', 'MEDIUM', 'HIGH']
}

# 输出数据结构 (PatientResponse)
{
    "id": int,                      # 系统生成
    "patient_no": str,              # 自动生成，格式：P{YYYYMMDD}{4 位序号}
    "name": str,
    "gender": str,
    "age": int,                     # 根据 birth_date 计算
    "birth_date": str,              # ISO8601 格式
    "id_card": str | null,
    "phone": str | null,
    "email": str | null,
    "address": str | null,
    "constitution": str | null,
    "risk_level": str | null,
    "created_at": str,              # ISO8601 时间戳
    "updated_at": str,
}

# 数据库映射 (patient 表)
字段                  类型          约束
---------------------------------------------------------
id                   INTEGER       PK, AUTO INCREMENT
patient_no           VARCHAR(32)   UNIQUE, NOT NULL, INDEX
name                 VARCHAR(64)   NOT NULL
gender               VARCHAR(1)    NOT NULL, DEFAULT 'F'
birth_date           DATE          NOT NULL
age                  INTEGER       COMPUTED (可选缓存)
id_card              VARCHAR(18)   UNIQUE
phone                VARCHAR(20)   INDEX
email                VARCHAR(128)  -
address              TEXT          -
constitution         VARCHAR(32)   INDEX
risk_level           VARCHAR(16)   INDEX
created_by           INTEGER       FK -> users.id
created_at           TIMESTAMP     DEFAULT NOW()
updated_at           TIMESTAMP     ON UPDATE NOW()
is_deleted           BOOLEAN       DEFAULT FALSE
```

### 2.2 随访 (Visit)

```python
# 输入数据
{
    "patient_id": int,              # 必填，关联患者 ID
    "visit_type": str,              # 必填，枚举：['outpatient', 'emergency', 'inpatient', 'remote']
    "visit_date": date,             # 必填，就诊日期
    "chief_complaint": str,         # 必填，主诉
    "present_illness": str,         # 可选，现病史
    "past_history": str,            # 可选，既往史
    "family_history": str,          # 可选，家族史
}

# 输出数据
{
    "id": int,
    "visit_no": str,                # 格式：V{YYYYMMDD}{6 位序号}
    "patient_id": int,
    "patient_name": str,            # 关联查询
    "visit_type": str,
    "visit_date": str,
    "chief_complaint": str,
    "status": str,                  # ['pending', 'in_progress', 'completed']
    "created_at": str,
}

# 数据库映射 (visit 表)
字段                 类型           约束
---------------------------------------------------------
id                   INTEGER        PK, AUTO INCREMENT
visit_no             VARCHAR(32)    UNIQUE, NOT NULL
patient_id           INTEGER        FK -> patient.id, INDEX
visit_type           VARCHAR(16)    NOT NULL
visit_date           DATE           NOT NULL, INDEX
chief_complaint      TEXT           NOT NULL
present_illness      TEXT           -
past_history         TEXT           -
family_history       TEXT           -
status               VARCHAR(16)    DEFAULT 'pending'
created_by           INTEGER        FK -> users.id
created_at           TIMESTAMP      DEFAULT NOW()
```

### 2.3 超声检查 (Ultrasound)

```python
# 输入数据 (multipart/form-data)
{
    "visit_id": int,                # 必填，关联随访 ID
    "image_file": File,             # 必填，PNG/JPG/DICOM, max 50MB
    "modality_type": str,           # 必填，['b_mode', 'doppler', 'elastography']
    "body_part": str,               # 必填，['left_breast', 'right_breast', 'bilateral']
    "quadrant": str,                # 可选，['outer_upper', 'inner_upper', 'outer_lower', 'inner_lower', 'central']
    "finding_description": str,     # 可选，影像所见描述
}

# 输出数据
{
    "id": int,
    "ultrasound_no": str,           # 格式：US{YYYYMMDD}{6 位序号}
    "visit_id": int,
    "image_url": str,               # 存储路径/访问 URL
    "thumbnail_url": str,           # 缩略图 URL
    "modality_type": str,
    "body_part": str,
    "quadrant": str | null,
    "image_width": int,             # 图像宽度 (像素)
    "image_height": int,            # 图像高度 (像素)
    "file_size_kb": int,            # 文件大小 (KB)
    "upload_status": str,           # ['pending', 'processing', 'completed', 'failed']
    "created_at": str,
}

# 数据库映射 (ultrasound 表)
字段                   类型           约束
-----------------------------------------------------------
id                     INTEGER        PK, AUTO INCREMENT
ultrasound_no          VARCHAR(32)    UNIQUE, NOT NULL
visit_id               INTEGER        FK -> visit.id, INDEX
image_path             VARCHAR(512)   NOT NULL
thumbnail_path         VARCHAR(512)   -
modality_type          VARCHAR(32)    NOT NULL, INDEX
body_part              VARCHAR(32)    NOT NULL
quadrant               VARCHAR(16)    -
image_width            INTEGER        -
image_height           INTEGER        -
file_size_bytes        BIGINT         -
finding_description    TEXT           -
upload_status          VARCHAR(16)    DEFAULT 'pending'
created_at             TIMESTAMP      DEFAULT NOW()
```

---

## 3. 患者就诊数据流转

### 3.1 场景：初诊患者完整流程

```
时间线:
T0         T1           T2              T3              T4            T5
│          │            │               │               │             │
▼          ▼            ▼               ▼               ▼             ▼
患者    创建患者    创建随访       超声检查        AI 推理       医生诊断
登记    档案       记录           上传            分析          开具
│          │            │               │               │             │
│          │            │               │               │             │
│          ▼            ▼               ▼               ▼             ▼
│      Patient      Visit         Ultrasound    Inference     Diagnosis
│      Table        Table         Table         Service       Table
│          │            │               │               │             │
│          │            │               │               │             │
│          │            │               │               │             ▼
│          │            │               │               │         Report
│          │            │               │               │         Generate
│          │            │               │               │             │
│          │            │               │               │             ▼
│          │            │               │               │         医生审核
│          │            │               │               │             │
│          │            │               │               │             ▼
│          │            │               │               │         报告发布
```

### 3.2 环节详细分析

#### 环节 1: 患者登记

**输入**:
```json
POST /api/v1/patient/
{
  "name": "张三",
  "gender": "F",
  "birth_date": "1985-06-15",
  "phone": "13800138000",
  "id_card": "110101198506151234",
  "address": "北京市朝阳区某某街道",
  "constitution": "气虚质"
}
```

**处理流程**:
```
1. 接收请求 → API 层 (patient.py)
   ├─ 验证 Token (Auth Middleware)
   ├─ 验证字段格式 (Pydantic Schema)
   └─ 权限检查 (用户角色)

2. 业务逻辑 → Service 层 (patient_service.py)
   ├─ 检查身份证号是否重复
   ├─ 生成 patient_no (P202605280001)
   ├─ 计算年龄 (2026-1985=41)
   └─ 映射体质类型 (气虚质 → QI_DEFICIENT)

3. 数据持久化 → Model 层
   ├─ 开启数据库事务
   ├─ 插入 patient 表
   ├─ 创建索引记录
   └─ 提交事务

4. 响应处理
   ├─ 构建 PatientResponse
   ├─ 记录操作日志
   └─ 返回 201 Created
```

**验证规则**:
| 字段 | 规则 | 错误码 |
|------|------|--------|
| name | 1-64 字符，不能为空 | 422 |
| gender | 只能是 'M' 或 'F' | 422 |
| birth_date | 有效日期，不能大于今天 | 422 |
| id_card | 18 位，符合身份证校验算法 | 422/409 |
| phone | 11 位，1 开头 | 422 |
| email | 符合邮箱格式 | 422 |

**输出**:
```json
{
  "id": 1,
  "patient_no": "P202605280001",
  "name": "张三",
  "gender": "F",
  "age": 41,
  "birth_date": "1985-06-15",
  "phone": "13800138000",
  "id_card": "110101198506151234",
  "address": "北京市朝阳区某某街道",
  "constitution": "气虚质",
  "risk_level": null,
  "created_at": "2026-05-28T10:30:00Z",
  "updated_at": "2026-05-28T10:30:00Z"
}
```

**异常处理**:
```python
try:
    # 身份证号重复
    if db.query(Patient).filter(Patient.id_card == id_card).first():
        raise HTTPException(409, "身份证号已存在")
    
    # 数据库错误
    db.commit()
except IntegrityError:
    db.rollback()
    raise HTTPException(500, "数据库错误")
except Exception as e:
    db.rollback()
    raise HTTPException(500, f"创建失败：{str(e)}")
```

---

#### 环节 2: 创建随访记录

**输入**:
```json
POST /api/v1/visit/
{
  "patient_id": 1,
  "visit_type": "outpatient",
  "visit_date": "2026-05-28",
  "chief_complaint": "发现右乳肿块 3 天，无疼痛",
  "present_illness": "患者 3 天前洗澡时发现右乳外上象限可触及一肿块...",
  "past_history": "否认高血压、糖尿病史",
  "family_history": "母亲有乳腺增生病史"
}
```

**处理流程**:
```
1. 验证 patient_id 是否存在
   └─ SELECT * FROM patient WHERE id = 1

2. 生成 visit_no (V202605280001)
   └─ 基于日期 + 序列号

3. 验证 visit_type 枚举值
   └─ ['outpatient', 'emergency', 'inpatient', 'remote']

4. 插入 visit 表
   └─ 关联 patient_id

5. 触发事件
   ├─ 更新患者最近就诊时间
   └─ 创建随访提醒 (可选)
```

**输出**:
```json
{
  "id": 1,
  "visit_no": "V202605280001",
  "patient_id": 1,
  "patient_name": "张三",
  "visit_type": "outpatient",
  "visit_date": "2026-05-28",
  "chief_complaint": "发现右乳肿块 3 天，无疼痛",
  "status": "pending",
  "created_at": "2026-05-28T10:35:00Z"
}
```

---

#### 环节 3: 超声图像上传

**输入**:
```
POST /api/v1/ultrasound/
Content-Type: multipart/form-data

visit_id: 1
image_file: <binary data, ultrasound_001.png>
modality_type: "b_mode"
body_part: "right_breast"
quadrant: "outer_upper"
finding_description: "右乳外上象限可见一低回声结节..."
```

**处理流程**:
```
1. 文件验证
   ├─ 检查文件类型 (PNG/JPG/DICOM)
   ├─ 检查文件大小 (< 50MB)
   └─ 病毒扫描 (可选)

2. 文件存储
   ├─ 生成唯一文件名 (us_20260528_001.png)
   ├─ 存储到文件系统 (/data/images/2026/05/28/)
   ├─ 生成缩略图 (200x200)
   └─ 更新存储路径到数据库

3. 图像元数据提取
   ├─ 读取图像尺寸
   ├─ 读取 EXIF 信息 (如有)
   └─ 计算文件大小

4. 异步处理触发
   └─ 发送 AI 推理队列消息
```

**文件存储结构**:
```
/data/
├── images/
│   └── 2026/
│       └── 05/
│           └── 28/
│               ├── us_20260528_001.png      # 原图
│               ├── us_20260528_001_thumb.png # 缩略图
│               └── us_20260528_001_meta.json # 元数据
```

**输出**:
```json
{
  "id": 1,
  "ultrasound_no": "US202605280001",
  "visit_id": 1,
  "image_url": "/data/images/2026/05/28/us_20260528_001.png",
  "thumbnail_url": "/data/images/2026/05/28/us_20260528_001_thumb.png",
  "modality_type": "b_mode",
  "body_part": "right_breast",
  "quadrant": "outer_upper",
  "image_width": 1024,
  "image_height": 768,
  "file_size_kb": 256,
  "upload_status": "completed",
  "created_at": "2026-05-28T10:40:00Z"
}
```

---

## 4. AI 推理数据流转

### 4.1 场景：超声图像 AI 分析

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI 推理处理流程                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  输入图像 → 预处理 → 模型推理 → 后处理 → 结果解析 → 记录存储       │
│     │         │         │         │         │         │            │
│     ▼         ▼         ▼         ▼         ▼         ▼            │
│  [Original] [Resize]  [Tensor] [Mask/   [JSON]   [DB]             │
│   1024x768   224x224   Forward  Class]   Result   Insert           │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  环节            输入                  处理              输出       │
├─────────────────────────────────────────────────────────────────────┤
│  1. 图像接收    文件路径             验证存在          图像对象     │
│  2. 预处理      图像对象             缩放/归一化       Tensor       │
│  3. 模型加载    模型 ID              从磁盘/内存       PyTorch Model│
│  4. 推理执行    Tensor + Model       forward()         Output       │
│  5. 结果解析    Output Tensor        Sigmoid/Softmax   概率/掩码   │
│  6. 特征计算    掩码                 面积/周长等       特征字典     │
│  7. 记录存储    推理结果             插入数据库        记录 ID      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 分割推理详细流程

**输入**:
```json
POST /api/v1/ai/segmentation
{
  "ultrasound_id": 1,
  "save_to_record": true,
  "patient_id": 1,
  "visit_id": 1
}
```

**处理步骤**:

```python
def segment(self, image_path: str, **kwargs) -> Dict:
    """
    分割推理完整流程
    """
    # ========== 步骤 1: 图像加载与验证 ==========
    start_time = time.time()
    
    try:
        image = Image.open(image_path).convert('RGB')
    except Exception as e:
        return {"success": False, "error": f"图像加载失败：{e}"}
    
    # ========== 步骤 2: 图像预处理 ==========
    # 2.1 缩放至模型输入尺寸
    image = image.resize((224, 224))
    
    # 2.2 归一化到 [0, 1]
    image_array = np.array(image).astype(np.float32) / 255.0
    
    # 2.3 转置为 CHW 格式
    image_array = np.transpose(image_array, (2, 0, 1))
    
    # 2.4 添加 batch 维度
    input_tensor = torch.from_numpy(image_array).unsqueeze(0)
    
    # 2.5 移动到计算设备
    input_tensor = input_tensor.to(self.device)
    
    # ========== 步骤 3: 模型推理 ==========
    with torch.no_grad():
        # 3.1 前向传播
        output = self._pbsnet(input_tensor)
        
        # 3.2 Sigmoid 激活
        mask_prob = torch.sigmoid(output)
        
        # 3.3 阈值分割 (>0.5 为前景)
        mask = mask_prob > 0.5
    
    # ========== 步骤 4: 后处理 ==========
    # 4.1 转换为 numpy
    mask_np = mask.cpu().numpy()[0, 0].astype(np.uint8) * 255
    
    # 4.2 形态学操作 (去噪)
    kernel = np.ones((3,3),np.uint8)
    mask_np = cv2.morphologyEx(mask_np, cv2.MORPH_OPEN, kernel)
    
    # 4.3 保存分割结果
    mask_path = image_path.replace('.png', '_mask.png')
    Image.fromarray(mask_np).save(mask_path)
    
    # ========== 步骤 5: 特征计算 ==========
    # 5.1 计算面积 (像素数)
    area_pixels = np.sum(mask_np > 0)
    
    # 5.2 计算周长
    edges = cv2.Canny(mask_np, 100, 200)
    perimeter_pixels = np.sum(edges > 0)
    
    # 5.3 转换为实际尺寸 (假设 0.05mm/像素)
    area_mm2 = area_pixels * 0.05 * 0.05
    perimeter_mm = perimeter_pixels * 0.05
    
    # 5.4 计算纵横比
    contours, _ = cv2.findContours(mask_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x, y, w, h = cv2.boundingRect(contours[0])
        aspect_ratio = w / float(h)
    else:
        aspect_ratio = 1.0
    
    # ========== 步骤 6: 构建结果 ==========
    inference_time_ms = int((time.time() - start_time) * 1000)
    
    result = {
        "success": True,
        "segmentation": {
            "mask_path": mask_path,
            "area_mm2": round(area_mm2, 2),
            "perimeter_mm": round(perimeter_mm, 2),
            "aspect_ratio": round(aspect_ratio, 2),
            "contour_points": len(contours[0]) if contours else 0
        },
        "metrics": {
            "dice_score": 0.87,  # 模型置信度
            "inference_time_ms": inference_time_ms
        }
    }
    
    # ========== 步骤 7: 记录存储 ==========
    if kwargs.get("save_to_record"):
        record_id = self._save_inference_record(
            model_code='pbsnet',
            patient_id=kwargs.get('patient_id'),
            visit_id=kwargs.get('visit_id'),
            inference_type='segmentation',
            input_data=image_path,
            output_data=mask_path,
            result=result['segmentation'],
            confidence=result['metrics']['dice_score'],
            inference_time_ms=inference_time_ms,
            created_by=kwargs.get('created_by')
        )
        result['record_id'] = record_id
    
    return result
```

**输出**:
```json
{
  "success": true,
  "segmentation": {
    "mask_path": "/data/images/2026/05/28/us_20260528_001_mask.png",
    "area_mm2": 156.25,
    "perimeter_mm": 52.5,
    "aspect_ratio": 1.35,
    "contour_points": 128
  },
  "metrics": {
    "dice_score": 0.87,
    "inference_time_ms": 45
  },
  "record_id": 1
}
```

**数据传递链**:
```
超声图像 (US202605280001)
    ↓ [文件路径]
InferenceService.segment()
    ↓ [分割掩码路径 + 特征数据]
inference_record 表
    ↓ [record_id]
诊断模块 (作为诊断依据)
    ↓ [BI-RADS 特征]
Report 生成
```

---

### 4.3 诊断推理详细流程

**输入**:
```json
POST /api/v1/ai/diagnosis
{
  "ultrasound_id": 1,
  "save_to_record": true,
  "patient_id": 1,
  "visit_id": 1
}
```

**处理步骤**:

```python
def diagnose(self, image_path: str, **kwargs) -> Dict:
    """
    良恶性分类推理
    """
    start_time = time.time()
    
    # ========== 步骤 1: 图像加载 ==========
    image = Image.open(image_path).convert('RGB')
    
    # ========== 步骤 2: 预处理 ==========
    image = image.resize((224, 224))
    image_array = np.array(image).astype(np.float32) / 255.0
    image_array = np.transpose(image_array, (2, 0, 1))
    input_tensor = torch.from_numpy(image_array).unsqueeze(0).to(self.device)
    
    # ========== 步骤 3: 模型推理 ==========
    with torch.no_grad():
        output = self._dfmfi(input_tensor)
        probs = F.softmax(output, dim=1)
        confidence, pred = torch.max(probs, 1)
    
    # ========== 步骤 4: 结果映射 ==========
    # 0=benign, 1=malignant
    prediction = 'malignant' if pred.item() == 1 else 'benign'
    
    # BI-RADS 映射
    birads_map = {0: 3, 1: 4}  # benign->4a, malignant->4c
    birads_category = birads_map[pred.item()]
    
    # ========== 步骤 5: 构建结果 ==========
    inference_time_ms = int((time.time() - start_time) * 1000)
    
    result = {
        "success": True,
        "diagnosis": {
            "prediction": prediction,  # benign/malignant
            "birads_category": birads_category,  # 3/4/5
            "probabilities": {
                "benign": round(probs[0, 0].item(), 4),
                "malignant": round(probs[0, 1].item(), 4)
            },
            "confidence": round(confidence.item(), 4)
        },
        "metrics": {
            "inference_time_ms": inference_time_ms
        }
    }
    
    # ========== 步骤 6: 记录存储 ==========
    if kwargs.get("save_to_record"):
        record_id = self._save_inference_record(...)
        result['record_id'] = record_id
    
    return result
```

**输出**:
```json
{
  "success": true,
  "diagnosis": {
    "prediction": "benign",
    "birads_category": 3,
    "probabilities": {
      "benign": 0.9234,
      "malignant": 0.0766
    },
    "confidence": 0.9234
  },
  "metrics": {
    "inference_time_ms": 32
  },
  "record_id": 2
}
```

---

## 5. 报告生成数据流转

### 5.1 场景：AI 辅助诊断报告生成

**输入**:
```json
POST /api/v1/reports/generate-ai-diagnosis
{
  "patient_id": 1,
  "visit_id": 1,
  "diagnosis_id": 1,
  "created_by": 1
}
```

**处理流程**:

```
┌──────────────────────────────────────────────────────────────────────┐
│                        报告生成流程                                   │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. 数据收集                                                         │
│     ├─ SELECT * FROM patient WHERE id = 1                           │
│     ├─ SELECT * FROM visit WHERE id = 1                             │
│     ├─ SELECT * FROM diagnosis WHERE id = 1                         │
│     └─ SELECT * FROM ultrasound WHERE visit_id = 1                  │
│                        ↓                                             │
│  2. 内容生成                                                         │
│     ├─ 计算年龄 (当前日期 - birth_date)                             │
│     ├─ 填充 Markdown 模板                                           │
│     ├─ 生成 BI-RADS 建议                                            │
│     └─ 添加 AI 辅助信息                                             │
│                        ↓                                             │
│  3. 报告存储                                                         │
│     ├─ 生成 report_no (RPT202605280001)                             │
│     ├─ INSERT INTO report (...)                                     │
│     └─ UPDATE diagnosis SET report_id = ...                         │
│                        ↓                                             │
│  4. 响应返回                                                         │
│     └─ JSON with report data                                        │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**报告模板**:
```markdown
# 乳腺超声 AI 辅助诊断报告

## 基本信息
- 报告编号：{report_no}
- 报告日期：{current_date}
- 患者姓名：{patient.name}
- 患者性别：{patient.gender}
- 患者年龄：{age}岁
- 就诊编号：{visit.visit_no}

## 诊断结果
### BI-RADS 分级
{diagnosis.birads_category} 类

### 诊断结论
- 侧别：{diagnosis.laterality}
- 象限：{diagnosis.quadrant}
- 肿瘤特征：形态/边缘/回声/钙化/血流

## AI 辅助分析
- 使用模型：DFMFI v1.0
- AI 预测：{ai_result.prediction}
- 置信度：{ai_result.confidence * 100:.1f}%
- 推理时间：{ai_result.inference_time_ms}ms

## 建议
{birads_suggestion}

---
AI 辅助：是
生成时间：{timestamp}
```

**输出**:
```json
{
  "id": 1,
  "report_no": "RPT202605280001",
  "report_type": "ai_diagnosis",
  "patient_id": 1,
  "visit_id": 1,
  "diagnosis_id": 1,
  "title": "乳腺超声 AI 辅助诊断报告",
  "content": "# 乳腺超声 AI 辅助诊断报告\\n\\n## 基本信息\\n...",
  "summary": "患者张三，BI-RADS 3 类，AI 辅助诊断",
  "ai_assisted": true,
  "ai_model_used": "DFMFI v1.0",
  "ai_confidence": 0.92,
  "status": "draft",
  "created_at": "2026-05-28T11:00:00Z",
  "created_by": 1
}
```

---

## 6. 中医诊疗数据流转

### 6.1 场景：中医体质辨识

**输入**:
```json
POST /api/v1/tcm/constitution-identify
{
  "patient_id": 1,
  "questionnaire": [
    {"question_id": 1, "answer": 3},
    {"question_id": 2, "answer": 2},
    ...
  ],
  "symptoms": ["乏力", "气短", "自汗"],
  "tongue": "淡红",
  "pulse": "细弱"
}
```

**处理流程**:
```
1. 问卷评分
   └─ 计算 9 种体质原始分 → 转化分

2. 体质判定
   ├─ 平和质判定
   └─ 偏颇体质判定

3. 证型分析
   ├─ 症状映射 (乏力 → 气虚)
   ├─ 舌脉参合 (淡红 + 细弱 → 气血不足)
   └─ 证型确定 (气虚质 + 气血不足证)

4. 方剂推荐
   ├─ 根据证型检索知识图谱
   ├─ 匹配经典方剂
   └─ 个性化加减
```

**输出**:
```json
{
  "constitution": "气虚质",
  "constitution_score": 78.5,
  "zheng_type": "气血不足证",
  "zheng_severity": "中",
  "symptom_analysis": {
    "qi_deficiency": ["乏力", "气短", "自汗"],
    "blood_deficiency": ["面色萎黄", "心悸"]
  },
  "prescription": {
    "name": "八珍汤加减",
    "ingredients": [
      {"name": "人参", "dosage": "10g"},
      {"name": "白术", "dosage": "10g"},
      ...
    ],
    "dosage_instruction": "水煎服，日 1 剂"
  }
}
```

---

## 7. 数据规范与接口标准

### 7.1 通用数据格式

**时间格式**:
```
ISO 8601: 2026-05-28T10:30:00Z
日期：2026-05-28
时间戳：1685271000
```

**ID 编码规范**:
| 类型 | 格式 | 示例 |
|------|------|------|
| 患者 | P{YYYYMMDD}{4 位序号} | P202605280001 |
| 随访 | V{YYYYMMDD}{6 位序号} | V202605280001 |
| 超声 | US{YYYYMMDD}{6 位序号} | US202605280001 |
| 诊断 | D{YYYYMMDD}{6 位序号} | D202605280001 |
| 报告 | RPT{YYYYMMDD}{6 位序号} | RPT202605280001 |

**枚举值规范**:
```python
# 性别
GENDER = {'M': '男', 'F': '女'}

# 随访类型
VISIT_TYPE = {
    'outpatient': '门诊',
    'emergency': '急诊',
    'inpatient': '住院',
    'remote': '远程'
}

# 模态类型
MODALITY_TYPE = {
    'b_mode': 'B 超',
    'doppler': '多普勒',
    'elastography': '弹性成像'
}

# BI-RADS 分级
BIRADS = {
    0: '评估不完全',
    1: '阴性',
    2: '良性',
    3: '可能良性',
    4: '可疑恶性',
    5: '高度可疑恶性',
    6: '已活检证实恶性'
}
```

### 7.2 API 响应格式

**成功响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {...}
}
```

**错误响应**:
```json
{
  "code": 422,
  "message": "请求参数验证失败",
  "data": {
    "errors": [
      {
        "field": "gender",
        "message": "必须是 M 或 F"
      }
    ]
  }
}
```

**分页响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

---

## 8. 异常处理与容错机制

### 8.1 异常分级

| 级别 | 类型 | 处理策略 | 示例 |
|------|------|----------|------|
| P0 | 系统级 | 立即告警，自动回滚 | 数据库连接失败 |
| P1 | 业务级 | 记录日志，返回错误 | 参数验证失败 |
| P2 | 警告级 | 记录日志，降级处理 | AI 模型加载失败 |
| P3 | 提示级 | 用户提示，继续流程 | 非必填字段缺失 |

### 8.2 重试机制

```python
@retry(
    max_attempts=3,
    delay=1000,  # ms
    backoff=2,   # 指数退避
    exceptions=(ConnectionError, TimeoutError)
)
def call_ai_service(input_data):
    """AI 服务调用（带重试）"""
    pass
```

### 8.3 事务边界

```
患者创建:
├─ Begin Transaction
├─ INSERT patient
├─ INSERT audit_log
└─ Commit / Rollback

就诊流程:
├─ Create Patient (T1)
├─ Create Visit (T2)        # 独立事务
├─ Upload Ultrasound (T3)   # 独立事务
├─ AI Inference (T4)        # 独立事务
├─ Create Diagnosis (T5)    # 独立事务
└─ Generate Report (T6)     # 独立事务
```

---

**文档维护**:
- 每次接口变更需同步更新本文档
- 每月进行一次数据流转审计
- 新增业务场景需补充相应分析

**版本历史**:
| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-05-28 | 初始版本 |
