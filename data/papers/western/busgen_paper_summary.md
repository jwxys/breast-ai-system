# BUSGen: 乳腺超声生成式基础模型

## 论文信息

**标题**: A foundation generative model for breast ultrasound image analysis

**机构**: 
- 北京大学智能学院
- 北京大学肿瘤医院
- 北京协和医院
- 中国医学科学院肿瘤医院
- 斯坦福大学

**期刊**: Nature Biomedical Engineering (2026)

**链接**: https://sai.pku.edu.cn/info/1088/9545.htm

---

## 研究背景

医学影像 AI 面临的挑战：
1. 高质量影像难以大规模获得
2. 罕见或早期病灶样本有限
3. 专家标注成本高
4. 不同医院、设备、医生操作习惯存在显著差异
5. 跨机构医学数据共享受隐私与合规要求约束

---

## 核心创新

### BUSGen 模型设计

**预训练数据规模**:
- 5,907 次检查
- 4,636 名患者
- 3,749 个病灶

**训练流程**:
1. **预训练**: 在大量乳腺超声图像上学习组织结构、病灶形态、设备差异和临床标签关系
2. **小样本适配**: 冻结预训练参数，通过 LoRA 适配具体任务
3. **合成数据生成**: 生成大规模、带有任务条件的合成数据
4. **下游训练**: 用合成数据训练诊断模型

---

## 实验结果

### Scaling Effect

合成数据规模扩大，下游模型性能持续提升：

| 合成数据规模 | BUS-DM AUC |
|--------------|------------|
| 10 万张 | 0.891 |
| 50 万张 | 0.912 |
| 100 万张 | **0.929** |

### 对比基线

- **BUSGen (100 万合成数据)**: AUC 0.929
- **NYU-AI (28.8 万真实数据)**: AUC 0.930（强基线）
- **传统数据增强**: AUC 0.856

---

## 关键发现

1. **合成数据可作为有效训练资源** - 不只是数据增强的补充
2. **存在 Scaling Effect** - 数据规模越大，模型越强
3. **医学语义建模** - 生成式模型能学习有效的医学影像语义

---

## 对本项目的价值

1. **数据增强**: 使用 BUSGen 生成的合成数据扩充训练集
2. **罕见病灶**: 生成罕见病例样本，平衡数据集
3. **隐私保护**: 使用合成数据进行模型开发和验证
4. **预训练**: 可使用 BUSGen 的预训练权重作为初始化

---

## 数据使用建议

```python
# 合成数据使用示例
from busgen import load_synthetic_data

# 加载预训练模型
model = load_busgen_pretrained()

# 生成合成数据
synthetic_images = model.generate(
    task="classification",
    category="malignant",
    num_samples=10000
)

# 训练下游模型
train_with_synthetic_data(model, synthetic_images)
```

---

## 引用

```bibtex
@article{wang2026busgen,
  title={A foundation generative model for breast ultrasound image analysis},
  author={Wang, Liwei and ...},
  journal={Nature Biomedical Engineering},
  year={2026}
}
```

---

## 更新时间

2026-05-28
