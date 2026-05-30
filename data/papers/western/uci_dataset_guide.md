# UCI 乳腺癌数据集使用指南

## 数据集信息

| 属性 | 值 |
|------|-----|
| **名称** | Breast Cancer Wisconsin (Diagnostic) |
| **来源** | UCI Machine Learning Repository |
| **发布者** | Dr. William H. Wolberg, University of Wisconsin |
| **发布时间** | 1995 |
| **样本数** | 569 |
| **特征数** | 30 |
| **类别数** | 2 (良性/恶性) |
| **数据类型** | 结构化和数值型 |

---

## 数据获取

### 下载地址
1. **UCI 官方**: https://archive.ics.uci.edu/ml/datasets/breast+cancer+wisconsin+diagnostic
2. **scikit-learn**: `from sklearn.datasets import load_breast_cancer`
3. **Kaggle 镜像**: https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data

### 使用 scikit-learn 加载
```python
from sklearn.datasets import load_breast_cancer

# 加载数据集
data = load_breast_cancer()

print(f"样本数：{data.data.shape[0]}")
print(f"特征数：{data.data.shape[1]}")
print(f"类别数：{len(data.target_names)}")
print(f"特征名：{data.feature_names[:5]}...")
```

---

## 特征说明

### 特征分组（每组 10 个特征）

**1. 原始测量特征**:
- radius (半径)
- texture (纹理)
- perimeter (周长)
- area (面积)
- smoothness (平滑度)

**2. 标准误差特征**:
- radius error
- texture error
- perimeter error
- area error
- smoothness error

**3. 最差特征** (均值最大的 3 个邻居的均值):
- worst radius
- worst texture
- worst perimeter
- worst area
- worst smoothness

### 特征计算公式
每个特征都有 3 个变体：
- `mean`: 平均值
- `se`: 标准误差
- `worst`: 最大值（最严重的 3 个邻居的均值）

---

## 数据探索

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 创建 DataFrame
df = pd.DataFrame(data.data, columns=data.feature_names)
df['diagnosis'] = pd.Series(data.target).map({0: 'M', 1: 'B'})

# 基本统计
print(df.describe())

# 类别分布
sns.countplot(x='diagnosis', data=df)
plt.title('Diagnosis Distribution')
plt.show()

# 相关性热图
plt.figure(figsize=(20, 15))
sns.heatmap(df[data.feature_names].corr(), annot=False, cmap='coolwarm')
plt.title('Feature Correlation Matrix')
plt.show()
```

---

## 基线模型

### Logistic Regression
```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# 划分训练测试集
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

# 训练模型
model = LogisticRegression()
model.fit(X_train, y_train)

# 评估性能
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
```

**典型性能**:
- Accuracy: 0.96-0.98
- Precision: 0.96-0.98
- Recall: 0.95-0.98
- F1-Score: 0.96-0.98

---

## 与本项目的相关性

### 适用场景
1. **基线模型验证** - 验证分类流程正确性
2. **特征工程对比** - 与超声图像特征对比
3. **模型对比基准** - 与其他乳腺癌数据集对比

### 不适用场景
1. **医学影像训练** - 这是结构化数据，不是影像
2. **分割任务** - 无图像/掩码
3. **深度学习** - 数据量太小

---

## 引用

### BibTeX
```bibtex
@dataset{ Dua2017,
  author = "Dua, Dheema and Graeff, Casey",
  year = "2017",
  title = "{UCI} Machine Learning Repository",
  publisher = "University of California, Irvine, School of Information and {Computer Sciences}"
}

@article{Street1995,
  title="Breast cancer diagnosis and prognosis via linear programming",
  author="Street, W N and Wolberg, W H and Mangasarian, O L",
  journal="Operations Research",
  volume="43",
  number="4",
  pages="570--577",
  year="1995"
}
```

---

## 更新时间

2026-05-28
