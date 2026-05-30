# BUSI 数据集下载说明

## 数据集信息

- **名称**: Breast Ultrasound Images Dataset (BUSI)
- **来源**: Kaggle
- **样本数**: 780 张超声图像
- **分类**:
  - Normal (正常): 133 张
  - Benign (良性): 437 张
  - Malignant (恶性): 210 张

## 下载方式

### 方式 1: Kaggle API (推荐)

```bash
# 1. 安装 Kaggle CLI
pip install kaggle

# 2. 配置 API 凭证
# 访问 https://www.kaggle.com/account 获取 API Token
# 下载 kaggle.json 文件
# 保存到 ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json

# 3. 下载数据集
cd /workspace/breast-ai-system/data/datasets/public/BUSI
kaggle datasets download -d aryashah2k/breast-ultrasound-images-dataset

# 4. 解压
unzip breast-ultrasound-images-dataset.zip

# 5. 清理
rm breast-ultrasound-images-dataset.zip
```

### 方式 2: 手动下载

1. 访问：https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset
2. 点击 "Download" 按钮
3. 下载完成后解压到当前目录
4. 确保文件结构如下：

```
BUSI/
├── normal/          # 133 张正常图像
│   ├── (1).png
│   ├── (2).png
│   └── ...
├── benign/          # 437 张良性肿瘤图像
│   ├── (1).png
│   ├── (1)_mask.png  # 对应分割掩码
│   └── ...
├── malignant/       # 210 张恶性肿瘤图像
│   ├── (1).png
│   ├── (1)_mask.png  # 对应分割掩码
│   └── ...
└── README.txt
```

## 验证下载

```bash
cd /workspace/breast-ai-system/data/datasets/public/BUSI
python /workspace/breast-ai-system/data/scripts/validate_datasets.py
```

## 使用数据集

下载完成后，可用于：
- 模型训练
- 模型验证
- 数据增强研究

## 引用

```bibtex
@dataset{al-dhabyani2020busi,
  title={Dataset of breast ultrasound images},
  author={Al-Dhabyani, Walid and Gomaa, Mohammed and Khaled, Hussien and Fahmy, Aly},
  year={2020},
  publisher={Elsevier}
}
```

## 注意事项

- 需要 Kaggle 账号才能下载
- 数据集约 200MB
- 仅限学术研究使用
