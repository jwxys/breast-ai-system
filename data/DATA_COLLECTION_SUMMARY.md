# 数据收集总结

## 项目：乳腺癌超声 AI 辅助诊断系统

**收集日期**: 2026-05-28  
**负责人**: AI Coding Assistant

---

## 收集内容概览

| 类型 | 数量 | 存储位置 |
|------|------|----------|
| 公开数据集 | 4 个 | `data/datasets/public/` |
| 论文摘要 | 2 篇 | `data/papers/western/` |
| 调查报告 | 1 份 | `data/reports/` |
| 技术文档 | 3 份 | `data/documentation/` |
| 下载脚本 | 2 个 | `data/scripts/` |

---

## 已收集数据集

### 1. BUSI (Breast Ultrasound Images)
- **状态**: 📋 已记录下载方式
- **类型**: 乳腺超声图像
- **规模**: 780 张图像
- **用途**: 主训练集、分割任务
- **位置**: `data/datasets/public/BUSI/` (待下载)

### 2. UCI Breast Cancer
- **状态**: 📋 已记录下载方式
- **类型**: 结构化临床数据
- **规模**: 569 样本
- **用途**: 基线模型验证
- **位置**: `data/datasets/public/UCI-Breast-Cancer/` (待下载)

### 3. BUSGen 合成数据
- **状态**: 📋 已记录信息
- **类型**: 生成式合成图像
- **规模**: 100 万 + 图像
- **用途**: 数据增强、隐私保护
- **来源**: 北京大学智能学院

### 4. DDTI (Thyroid)
- **状态**: 📋 已记录信息
- **类型**: 甲状腺超声图像
- **规模**: 2,800+ 图像
- **用途**: 迁移学习、多器官拓展

---

## 已收集论文

### 1. BUSGen 论文
- **标题**: A foundation generative model for breast ultrasound image analysis
- **期刊**: Nature Biomedical Engineering (2026)
- **机构**: 北京大学智能学院等
- **位置**: `data/papers/western/busgen_paper_summary.md`

### 2. UCI 数据集论文
- **标题**: Breast cancer diagnosis and prognosis via linear programming
- **期刊**: Operations Research (1995)
- **机构**: University of Wisconsin
- **位置**: `data/papers/western/uci_dataset_guide.md`

---

## 已收集报告

### 1. 乳腺癌 AI 诊断领域调查报告 (2026)
**内容**:
- 市场规模与增长预测
- 关键技术方向分析
- 公开数据集对比
- 主流方法性能 benchmark
- 临床转化与监管要求
- 中医 AI 研究现状

**位置**: `data/reports/breast_cancer_ai_landscape_2026.md`

---

## 下载方式

### BUSI 数据集
```bash
# 方法 1: Kaggle API (推荐)
pip install kaggle
kaggle datasets download -d aryashah2k/breast-ultrasound-images-dataset
unzip breast-ultrasound-images-dataset.zip -d data/datasets/public/BUSI/

# 方法 2: 手动下载
# 访问：https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset
# 点击下载按钮，解压到 data/datasets/public/BUSI/
```

### UCI 数据集
```bash
# 使用 wget
wget -P data/datasets/public/UCI-Breast-Cancer/ \
  https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/wdbc.data

wget -P data/datasets/public/UCI-Breast-Cancer/ \
  https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/wdbc.names
```

### 使用自动脚本
```bash
cd /workspace/breast-ai-system/data/scripts
python download_public_datasets.py all
```

---

## 验证方式

```bash
# 验证数据集完整性
cd /workspace/breast-ai-system/data/scripts
python validate_datasets.py
```

---

## 数据使用建议

### 训练阶段
1. **预训练**: BUSI + BUSGen 合成数据
2. **微调**: 合作医院真实数据
3. **验证**: UCI + 独立测试集

### 增强策略
1. 几何变换
2. 弹性形变
3. 强度变化
4. 合成数据

---

## 合规事项

- ✅ 公开数据集：学术研究许可
- ⚠️ 合作医院数据：需签署协议
- ⚠️ 诊断用途：NMPA 二类医疗器械注册

---

## 文件清单

```
data/
├── README_datasets.md                          # 数据集总览
├── DATA_COLLECTION_SUMMARY.md                  # 本次收集总结
├── scripts/
│   ├── download_public_datasets.py             # 下载脚本
│   └── validate_datasets.py                    # 验证脚本
├── datasets/
│   └── public/
│       ├── BUSI/                               # BUSI 数据集 (待下载)
│       └── UCI-Breast-Cancer/                  # UCI 数据集 (待下载)
├── papers/
│   ├── western/
│   │   ├── busgen_paper_summary.md             # BUSGen 论文摘要
│   │   └── uci_dataset_guide.md                # UCI 数据集指南
│   └── tcm/                                    # (待补充)
├── reports/
│   └── breast_cancer_ai_landscape_2026.md      # 调查报告
└── documentation/                              # (待补充)
```

---

## 下一步计划

1. **下载数据集**: 执行下载脚本获取 BUSI 和 UCI 数据
2. **文献收集**: 继续收集中医证型相关论文
3. **数据标注**: 与合作医院协调数据标注工作
4. **数据脱敏**: 建立患者隐私保护机制
5. **数据集版本**: 建立数据集版本管理系统

---

**更新时间**: 2026-05-28
