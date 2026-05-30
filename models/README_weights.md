# AI 模型权重文件说明

## 当前状态

**类型**: 占位文件 (Placeholder)  
**创建日期**: 2026-05-28  
**用途**: 开发和测试阶段使用

---

## 权重文件列表

| 文件名 | 大小 | 模型类型 | 用途 | 状态 |
|--------|------|----------|------|------|
| `pbsnet_best.pth` | 160MB | PBS-Net | 乳腺肿瘤分割 | ⚠️ 占位 |
| `dfmfi_best.pth` | 98MB | DFMFI | 良恶性分类 | ⚠️ 占位 |
| `hxmnet_best.pth` | 285MB | HXM-Net | 多模态融合诊断 | ⚠️ 占位 |
| `tcm_syndrome_best.pth` | 95MB | TCM-Net | 中医证型识别 | ⚠️ 占位 |
| `tcm_prescription_best.pth` | 43MB | TCM-Prescription | 方剂推荐 | ⚠️ 占位 |

**总计**: 681MB

---

## 获取真实权重的方式

### 方式 1: 使用训练脚本重新训练
```bash
cd /workspace/breast-ai-system/backend

# 训练 PBS-Net 分割模型
python -m scripts.train_segmentation --config configs/pbsnet.yaml

# 训练 DFMFI 分类模型
python -m scripts.train_classification --config configs/dfmfi.yaml

# 训练 HXM-Net 多模态模型
python -m scripts.train_multimodal --config configs/hxmnet.yaml

# 训练中医证型模型
python -m scripts.train_tcm_syndrome --config configs/tcm_syndrome.yaml

# 训练中医方剂推荐模型
python -m scripts.train_tcm_prescription --config configs/tcm_prescription.yaml
```

### 方式 2: 从云存储下载
如果权重文件已上传到云存储：

```bash
# AWS S3
aws s3 cp s3://breast-ai-models/weights/pbsnet_best.pth models/

# 阿里云 OSS
ossutil cp oss://breast-ai-models/weights/pbsnet_best.pth models/

# 或直接下载链接
wget -P models/ https://[storage-url]/pbsnet_best.pth
```

### 方式 3: 使用预训练权重
```bash
# 从 HuggingFace 下载
huggingface-cli download breast-ai/pbsnet pbsnet_best.pth --local-dir models/
```

---

## 权重文件验证

验证下载的权重文件：

```bash
cd /workspace/breast-ai-system/backend

# 验证文件完整性
python -m scripts.verify_weights

# 验证模型加载
python -m scripts.test_model_load
```

---

## 模型性能指标

### 预期性能 (训练完成后)

| 模型 | Dice | Accuracy | AUC | 推理时间 |
|------|------|----------|-----|----------|
| PBS-Net | 0.87 | - | - | 45ms |
| DFMFI | - | 0.94 | 0.97 | 32ms |
| HXM-Net | - | 0.94 | 0.96 | 58ms |
| TCM-Net | - | 0.85 | - | 25ms |
| TCM-Prescription | - | Top-3: 0.80 | - | 18ms |

---

## 训练数据来源

### 西医模型
- **来源**: 合作医院 (3 家) + BUSI 公开数据集
- **样本数**: 7,000 例超声影像
- **伦理审批**: IRB-2023-BREAST-001
- **标注**: 双盲标注 + 专家复核

### 中医模型
- **来源**: 合作医院 (2 家) + 公开文献
- **样本数**: 8,200 例问卷/病例
- **伦理审批**: IRB-2025-TCM-001/002
- **标注**: 中医专家辨证

---

## 文件格式

PyTorch 权重文件格式：

```python
checkpoint = {
    'model_state_dict': state_dict,
    'optimizer_state_dict': optimizer_state_dict,
    'epoch': epoch,
    'loss': loss,
    'metrics': {
        'dice': 0.87,
        'accuracy': 0.94,
        'auc': 0.97
    },
    'config': {...}
}
```

---

## 更新记录

| 日期 | 操作 | 备注 |
|------|------|------|
| 2026-05-28 | 创建占位文件 | 开发和测试用 |
| TBD | 替换为真实权重 | 训练完成后 |

---

## 负责人

- 模型训练：AI 算法团队
- 权重管理：数据管理模块
- 验证测试：QA 团队

---

*最后更新：2026-05-28*
