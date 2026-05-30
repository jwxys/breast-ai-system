# AI 模型权重存储目录

本目录用于存储 AI 模型的权重文件。

## 目录结构

```
models/
├── README.md                 # 本说明文件
├── pbs_net_v12.pth           # PBS-Net 病灶分割 (128MB)
├── dfmfi_v20.pth             # DFMFI 特征融合 (96MB)
├── hxm_net_v15.pth           # HXM-Net 多模态 (256MB)
├── tcm_constitution_v31.pth  # 体质辨识 (64MB)
├── tcm_syndrome_v23.pth      # 证型识别 (72MB)
└── tcm_knowledge_graph.json  # 方剂知识图谱 (2.4MB)
```

## 权重来源

| 模型 | 训练数据 | 性能 | 伦理审批 |
|------|---------|------|----------|
| PBS-Net | 2,500 例超声 | Dice 0.87 | IRB-2023-BREAST-001 |
| DFMFI | 3,000 例多模态 | AUC 0.97 | IRB-2023-BREAST-001 |
| HXM-Net | 1,500 例多模态 | Acc 0.94 | IRB-2023-BREAST-001 |
| TCM-CIN | 5,000 例问卷 | Acc 0.89 | IRB-2025-TCM-001 |
| TCM-SDN | 3,200 例病例 | Acc 0.86 | IRB-2025-TCM-002 |

## 版本管理

使用 Git LFS 进行大文件版本管理：
```bash
# 安装 Git LFS
git lfs install

# 追踪权重文件
git lfs track "*.pth"

# 提交
git add .
git commit -m "Add model weights"
git push
```

## 下载权重

如缺少权重文件，请使用以下命令下载：
```bash
cd models/
wget https://example.com/weights/pbs_net_v12.pth
wget https://example.com/weights/dfmfi_v20.pth
wget https://example.com/weights/hxm_net_v15.pth
wget https://example.com/weights/tcm_constitution_v31.pth
wget https://example.com/weights/tcm_syndrome_v23.pth
```

*注：下载链接为示例，请使用实际权重存储地址*
