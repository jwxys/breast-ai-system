# 公开数据集与文献资料目录

本项目收集的乳腺癌超声 AI 诊断相关公开数据集、论文、文献和调查报告。

## 目录结构

```
data/
├── datasets/              # 数据集
│   ├── public/           # 公开数据集
│   │   ├── BUSI/                  # Breast Ultrasound Images Dataset
│   │   ├── UCI-Breast-Cancer/     # UCI 乳腺癌数据集
│   │   └── DDTI/                  # Digital Database of Thyroid Images
│   └── private/          # 私有/合作数据集
├── papers/               # 学术论文
│   ├── western/          # 西医/影像诊断论文
│   └── tcm/              # 中医证型论文
├── reports/              # 调查报告
└── documentation/        # 数据集文档
```

---

## 公开数据集

### 1. BUSI (Breast Ultrasound Images Dataset)

**来源**: Kaggle / 公开研究数据集  
**发布日期**: 2020  
**数据规模**: 780 张乳腺超声图像  
**数据内容**:
- 正常图像：133 张
- 良性肿瘤：437 张
- 恶性肿瘤：210 张
- 包含标注（分割掩码、分类标签）

**适用任务**:
- 乳腺肿瘤分类（正常/良性/恶性）
- 病灶分割
- 目标检测

**下载链接**:
- Kaggle: https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset
- PapersWithCode: https://paperswithcode.com/dataset/bus

**引用**:
```bibtex
@dataset{al-dhabyani2020busi,
  title={Dataset of breast ultrasound images},
  author={Al-Dhabyani, Walid and Gomaa, Mohammed and Khaled, Hussien and Fahmy, Aly},
  year={2020},
  publisher={Elsevier}
}
```

---

### 2. UCI Wisconsin Breast Cancer Dataset

**来源**: UCI Machine Learning Repository  
**发布日期**: 1995  
**数据规模**: 569 个样本  
**数据内容**:
- 特征：30 个细胞核特征（半径、纹理、周长、面积等）
- 标签：良性 (Benign) / 恶性 (Malignant)
- 数据来源：细针穿刺 (FNA) 图像分析

**适用任务**:
- 二分类（良性/恶性）
- 特征工程验证
- 基线模型对比

**下载链接**:
- UCI: https://archive.ics.uci.edu/ml/datasets/breast+cancer+wisconsin+diagnostic
- scikit-learn: `sklearn.datasets.load_breast_cancer()`

**引用**:
```bibtex
@dataset{ Dua2017,
  author = "Dua, Dheema and Graeff, Casey",
  year = "2017",
  title = "{UCI} Machine Learning Repository",
  publisher = "University of California, Irvine, School of Information and Computer Sciences",
  url = "http://archive.ics.uci.edu/ml"
}
```

---

### 3. DDTI (Digital Database of Thyroid Image)

**来源**: 公开医学影像数据集  
**发布日期**: 2019  
**数据规模**: 2,800+ 张甲状腺超声图像  
**数据内容**:
- 甲状腺结节图像
- 包含 TI-RADS 分级标注
- 多中心数据

**适用任务**:
- 甲状腺结节分类
- 迁移学习预训练
- 多器官 AI 模型拓展

**下载链接**:
- GitHub: https://github.com/haifangong/DDTI-Image

---

### 4. 合成数据 - BUSGen

**来源**: 北京大学智能学院王立威课题组 (Nature Biomedical Engineering, 2026)  
**数据规模**: 100 万 + 合成图像  
**数据内容**:
- 基于生成式基础模型 BUSGen 生成的乳腺超声合成数据
- 经过预训练验证（覆盖 5907 次检查、4636 名患者、3749 个病灶）
- 合成数据训练下游模型 AUC 可达 0.929

**适用任务**:
- 数据增强
- 隐私保护数据共享
- 罕见病灶模拟

**参考论文**: https://sai.pku.edu.cn/info/1088/9545.htm

---

## 数据集使用建议

### 训练阶段
1. **预训练**: 使用 BUSI + 合成数据（大规模）
2. **微调**: 使用合作医院真实数据（高质量标注）
3. **验证**: 使用独立测试集 + UCI 数据集

### 数据增强策略
1. 几何变换（旋转、翻转、缩放）
2. 弹性形变（模拟超声探头压力）
3. 强度变化（模拟不同设备参数）
4. 合成数据补充（BUSGen）

---

## 数据集统计

| 数据集 | 图像数 | 标注类型 | 用途 | 公开 |
|--------|--------|----------|------|------|
| BUSI | 780 | 分类 + 分割 | 主训练集 | ✅ |
| UCI | 569 | 分类 | 基线验证 | ✅ |
| DDTI | 2800+ | 分级 | 迁移学习 | ✅ |
| BUSGen 合成 | 1,000,000+ | 分类 + 分割 | 数据增强 | ✅ |

---

## 下载与使用

### 自动下载脚本
```bash
# 下载 BUSI 数据集
python scripts/download_busi.py

# 下载 UCI 数据集
python scripts/download_uci.py
```

### 数据集验证
```bash
# 验证数据集完整性
python scripts/validate_datasets.py
```

---

## 数据合规

- ✅ BUSI: 公开研究数据集，允许学术研究使用
- ✅ UCI: 公开机器学习数据集，允许学术使用
- ⚠️ 合作医院数据：需签署数据使用协议，仅限本项目使用
- ⚠️ 诊断数据：需符合 NMPA 二类医疗器械数据管理要求

---

## 更新日志

- 2026-05-28: 初始版本，收录 BUSI、UCI、DDTI 数据集信息
- 2026-05-28: 添加 BUSGen 合成数据信息
