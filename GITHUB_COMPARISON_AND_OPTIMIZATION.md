# 乳腺超声 AI 诊断系统 - GitHub 项目对比与优化建议

## 📊 调研项目总结

### 1. **YOLO-Breast-UltraSound-Images** (7⭐)
**链接**: https://github.com/sarah-antillia/YOLO-Breast-UltraSound-Images

**核心方法**:
- 使用 YOLO  format 处理 BUSI 数据集
- 数据增强：旋转 (0-330°) + 水平/垂直翻转
- 图像分割：从 mask 自动生成 YOLO 标注
- 数据集划分：train 50% / test 30% / valid 20%

**可借鉴点**:
- ✅ 系统化的数据增强流程
- ✅ 自动标注转换工具
- ✅ 多种格式支持 (YOLO/TFRecord/COCO)

---

### 2. **MultiTask_CNN_Pipeline** (2⭐)
**链接**: https://github.com/hijab1514/MultiTask_CNN_Pipeline

**核心方法**:
- **Approach 1**: Two-Stage Pipeline (U-Net 分割 → ResNet50 分类)
- **Approach 2**: Multi-task 模型 (共享 ResNet50 backbone)
- **Approach 3**: Multi-task CNN + Grad-CAM 可解释性

**性能指标**:
- 分割: Dice Score 0.65, IoU 0.51
- 分类: Accuracy 92.7%
- Multi-task + Grad-CAM: Accuracy 91.0%, Dice 0.65

**可借鉴点**:
- ✅ 多任务学习框架 (分割 + 分类联合训练)
- ✅ Grad-CAM 热力图可视化
- ✅ 五面板结果展示 (Input/GT Mask/Pred/Heatmap/Overlay)
- ✅ Kaggle Notebook 可复现

---

### 3. **前沿研究动态**

#### 北京大学 BUSGen 生成式基础模型
- **论文**: A foundation generative model for breast ultrasound image analysis
- **方法**: 生成式基础模型学习组织结构→合成训练数据→任务适配
- **优势**: 从"数据增强"到"训练资源"的范式转变

#### DeepHealth AI (Nature Health)
- **规模**: 57.9 万女性，109 个影像中心
- **效果**: 显著提升检出率，种族一致性
- **启示**: 真实世界验证的重要性

---

## 🎯 本项目现状分析

### ✅ 已有优势

| 功能模块 | 实现情况 | 对比优势 |
|---------|---------|---------|
| BI-RADS 智能分级 | ✅ 完整实现 | 符合 ACR 第 5 版标准 |
| 深度诊断功能 | ✅ 病灶标记/淋巴结/生长追踪 | 临床工作流整合 |
| 质控管理 | ✅ 置信度评估/人工复核 | 医疗安全闭环 |
| 工作流优化 | ✅ 历史对比/随访计划 | 长期管理视角 |
| 可视化增强 | ✅ 热图/标注/测量 | 医生友好界面 |

### ⚠️ 待改进点

| 改进方向 | 当前状态 | GitHub 项目参考 |
|---------|---------|----------------|
| **AI 模型训练** | ❌ 依赖外部 API | YOLO/ResNet 本地部署 |
| **数据增强** | ❌ 基础 | 旋转/翻转/多尺度 |
| **多任务学习** | ❌ 单一分类 | 分割 + 分类联合 |
| **可解释性** | ⚠️ 基础热图 | Grad-CAM 五面板 |
| **数据集管理** | ⚠️ 手动 | 自动化转换工具 |
| **性能指标** | ❌ 缺失 | Dice/IoU/Confusion Matrix |

---

## 🚀 优化方案

### 方案 1: 集成 Grad-CAM 可解释性模块 ⭐⭐⭐⭐⭐

**目标**: 实现临床可解释的 AI 决策可视化

**参考实现**: MultiTask_CNN_Pipeline 的 Grad-CAM

**实施步骤**:

```python
# app/diagnosis/services/gradcam_explainer.py
import torch
import torch.nn.functional as F
import cv2
import numpy as np
from typing import Tuple

class GradCAMExplainer:
    """
    Grad-CAM 可解释性分析器
    
    生成五面板可视化:
    1. 原始输入
    2. 真实分割 mask
    3. 预测分割 mask
    4. Grad-CAM 热力图
    5. 热力图叠加
    """
    
    def __init__(self, model, target_layer=None):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # 注册 hook
        self._register_hooks()
    
    def _register_hooks(self):
        """注册反向传播 hook"""
        def forward_hook(module, input, output):
            self.activations = output
        
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]
        
        if self.target_layer:
            self.target_layer.register_forward_hook(forward_hook)
            self.target_layer.register_backward_hook(backward_hook)
    
    def generate_heatmap(
        self,
        image: np.ndarray,
        target_class: int = None
    ) -> np.ndarray:
        """
        生成 Grad-CAM 热力图
        
        Args:
            image: 输入图像 (H,W,3)
            target_class: 目标类别索引
        
        Returns:
            heatmap: 热力图 (H,W)
        """
        # 前向传播
        self.model.eval()
        img_tensor = self._preprocess(image)
        output = self.model(img_tensor)
        
        # 反向传播
        if target_class is None:
            target_class = output.argmax(dim=1)
        
        loss = output[0, target_class]
        self.model.zero_grad()
        loss.backward(retain_graph=True)
        
        # 计算 Grad-CAM
        pooled_gradients = torch.mean(self.gradients, dim=[2, 3])
        activations = self.activations[0]
        
        for i in range(activations.shape[0]):
            activations[i] *= pooled_gradients[i]
        
        heatmap = torch.sum(activations, dim=0).cpu().numpy()
        heatmap = np.maximum(heatmap, 0)
        heatmap /= np.max(heatmap) + 1e-8
        
        #  Resize 到原图尺寸
        heatmap = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
        
        return heatmap
    
    def create_five_panel_visual(
        self,
        original_image: np.ndarray,
        ground_truth_mask: np.ndarray,
        predicted_mask: np.ndarray,
        heatmap: np.ndarray
    ) -> np.ndarray:
        """
        创建五面板可视化结果
        
        布局:
        [原图] [GT Mask] [Pred Mask] [Heatmap] [Overlay]
        """
        panels = []
        
        # 1. 原始图像
        panels.append(original_image)
        
        # 2. Ground Truth Mask (如果可用)
        gt_color = cv2.applyColorMap(
            (ground_truth_mask * 255).astype(np.uint8),
            cv2.COLORMAP_VIRIDIS
        )
        panels.append(gt_color)
        
        # 3. Predicted Mask
        pred_color = cv2.applyColorMap(
            (predicted_mask * 255).astype(np.uint8),
            cv2.COLORMAP_VIRIDIS
        )
        panels.append(pred_color)
        
        # 4. Heatmap
        heatmap_color = cv2.applyColorMap(
            (heatmap * 255).astype(np.uint8),
            cv2.COLORMAP_JET
        )
        panels.append(heatmap_color)
        
        # 5. Overlay (Heatmap + 原图)
        overlay = cv2.addWeighted(
            original_image, 0.6,
            heatmap_color, 0.4,
            0
        )
        panels.append(overlay)
        
        # 水平拼接
        result = np.hstack(panels)
        
        # 添加标签
        labels = ["Input", "Ground Truth", "Prediction", "Grad-CAM", "Overlay"]
        for i, label in enumerate(labels):
            cv2.putText(
                result, label,
                (i * original_image.shape[1] + 10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (255, 255, 255), 2
            )
        
        return result
    
    def _preprocess(self, image: np.ndarray) -> torch.Tensor:
        """图像预处理"""
        # Resize
        img_resized = cv2.resize(image, (224, 224))
        # Normalize
        img_norm = img_resized / 255.0
        # HWC -> CHW
        img_chw = np.transpose(img_norm, (2, 0, 1))
        # To tensor
        img_tensor = torch.from_numpy(img_chw).float().unsqueeze(0)
        return img_tensor
```

**API 集成**:

```python
# app/diagnosis/api/advanced_diagnosis_api.py
@router.post(
    "/generate-gradcam",
    summary="生成 Grad-CAM 可解释性热力图",
    description="创建五面板可视化 (原图/GT/Pred/Heatmap/Overlay)"
)
async def generate_gradcam(request: GradCAMRequest):
    explainer = GradCAMExplainer(model, target_layer=model.layer4[-1])
    
    heatmap = explainer.generate_heatmap(
        image=request.image,
        target_class=request.target_class
    )
    
    visual = explainer.create_five_panel_visual(
        original_image=request.image,
        ground_truth_mask=request.gt_mask,
        predicted_mask=request.pred_mask,
        heatmap=heatmap
    )
    
    return {
        "heatmap": viz_service.to_base64(heatmap),
        "five_panel_visual": viz_service.to_base64(visual),
        "metrics": {
            "max_activation": float(heatmap.max()),
            "mean_activation": float(heatmap.mean())
        }
    }
```

---

### 方案 2: 实现多任务学习框架 ⭐⭐⭐⭐

**目标**: 分割 + 分类联合训练，提升特征提取能力

**架构设计**:

```python
# app/inference/models/multitask_network.py
import torch
import torch.nn as nn
from torchvision.models import resnet50, ResNet50_Weights

class MultiTaskBreastNet(nn.Module):
    """
    多任务乳腺超声分析网络
    
    共享 backbone + 两个任务头:
    - 分割头：U-Net decoder 结构
    - 分类头：FC layers
    """
    
    def __init__(self, pretrained=True):
        super().__init__()
        
        # 共享 backbone: ResNet50
        backbone = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1 if pretrained else None)
        self.backbone = nn.Sequential(*list(backbone.children())[:-2])
        
        # 分割头 (Decoder)
        self.segmentation_head = nn.Sequential(
            nn.ConvTranspose2d(2048, 512, kernel_size=2, stride=2),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(512, 128, kernel_size=2, stride=2),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 1, kernel_size=1),
            nn.Sigmoid()
        )
        
        # 分类头
        self.classification_head = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(2048, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, 3)  # Normal, Benign, Malignant
        )
    
    def forward(self, x):
        features = self.backbone(x)
        
        # 分割输出
        seg_mask = self.segmentation_head(features)
        
        # 分类输出
        class_logits = self.classification_head(features)
        
        return seg_mask, class_logits


class MultiTaskLoss(nn.Module):
    """多任务损失函数"""
    
    def __init__(self, seg_weight=1.0, cls_weight=1.0):
        super().__init__()
        self.seg_weight = seg_weight
        self.cls_weight = cls_weight
        
        # 分割损失：Dice + BCE
        self.dice_loss = DiceLoss()
        self.bce_loss = nn.BCELoss()
        
        # 分类损失：CrossEntropy
        self.ce_loss = nn.CrossEntropyLoss()
    
    def forward(self, seg_pred, seg_gt, cls_pred, cls_gt):
        seg_loss = self.seg_weight * (
            self.dice_loss(seg_pred, seg_gt) +
            self.bce_loss(seg_pred, seg_gt)
        )
        
        cls_loss = self.cls_weight * self.ce_loss(cls_pred, cls_gt)
        
        total_loss = seg_loss + cls_loss
        
        return total_loss, {
            'seg_loss': seg_loss.item(),
            'cls_loss': cls_loss.item(),
            'total_loss': total_loss.item()
        }


class DiceLoss(nn.Module):
    """Dice Loss for segmentation"""
    
    def __init__(self, smooth=1e-6):
        super().__init__()
        self.smooth = smooth
    
    def forward(self, pred, target):
        pred = pred.view(-1)
        target = target.view(-1)
        
        intersection = (pred * target).sum()
        dice = (2. * intersection) / (pred.sum() + target.sum() + self.smooth)
        
        return 1 - dice
```

**训练脚本**:

```python
# scripts/train_multitask.py
def train_one_epoch(model, dataloader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    seg_dice_scores = []
    
    for batch in tqdm(dataloader):
        images = batch['image'].to(device)
        seg_masks = batch['mask'].to(device)
        cls_labels = batch['label'].to(device)
        
        optimizer.zero_grad()
        
        seg_pred, cls_pred = model(images)
        
        loss, loss_dict = criterion(
            seg_pred, seg_masks,
            cls_pred, cls_labels
        )
        
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        
        # 计算 Dice Score
        dice = calculate_dice(seg_pred, seg_masks)
        seg_dice_scores.append(dice)
    
    return {
        'avg_loss': total_loss / len(dataloader),
        'avg_dice': np.mean(seg_dice_scores),
        'loss_components': loss_dict
    }
```

---

### 方案 3: 数据增强管道 ⭐⭐⭐⭐

**目标**: 标准化数据增强流程，提升模型泛化能力

**实现**:

```python
# app/inference/data/data_augmentation.py
import albumentations as A
from albumentations.pytorch import ToTensorV2

class BreastUltrasoundAugmentor:
    """乳腺超声数据增强器"""
    
    def __init__(self, mode='train', img_size=512):
        self.mode = mode
        self.img_size = img_size
        
        # 训练集增强
        self.train_transform = A.Compose([
            A.Resize(img_size, img_size),
            
            # 几何变换
            A.RandomRotate90(p=0.5),
            A.Rotate(limit=30, p=0.5, border_mode=cv2.BORDER_REPLICATE),
            A.Flip(p=0.5),
            A.ShiftScaleRotate(
                shift_limit=0.1,
                scale_limit=0.2,
                rotate_limit=20,
                p=0.5
            ),
            
            # 光学变换
            A.RandomBrightnessContrast(
                brightness_limit=0.2,
                contrast_limit=0.2,
                p=0.5
            ),
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
            A.CLAHE(clip_limit=2.0, tile_grid_size=(8, 8), p=0.3),
            
            # 归一化
            A.Normalize(mean=(0.485,), std=(0.229,)),
            ToTensorV2()
        ], is_check_shapes=False)
        
        # 验证集增强 (仅 resize + normalize)
        self.val_transform = A.Compose([
            A.Resize(img_size, img_size),
            A.Normalize(mean=(0.485,), std=(0.229,)),
            ToTensorV2()
        ], is_check_shapes=False)
    
    def __call__(self, image, mask=None):
        transform = self.train_transform if self.mode == 'train' else self.val_transform
        
        if mask is not None:
            augmented = transform(image=image, mask=mask)
            return augmented['image'], augmented['mask']
        else:
            augmented = transform(image=image)
            return augmented['image']
    
    @staticmethod
    def create_dataset_folders(
        source_dir: str,
        output_dir: str,
        train_ratio=0.5,
        test_ratio=0.3,
        valid_ratio=0.2
    ):
        """
        创建训练/测试/验证数据集
        
        参考：YOLO-Breast-UltraSound-Images 的划分策略
        """
        from pathlib import Path
        import shutil
        from sklearn.model_selection import train_test_split
        
        source = Path(source_dir)
        output = Path(output_dir)
        
        # 收集所有图像
        all_images = list(source.glob('**/*.png')) + \
                    list(source.glob('**/*.jpg'))
        
        # 分层抽样
        train_imgs, temp_imgs = train_test_split(
            all_images,
            train_size=train_ratio,
            stratify=[img.parent.name for img in all_images]
        )
        
        test_imgs, valid_imgs = train_test_split(
            temp_imgs,
            train_size=test_ratio/(test_ratio + valid_ratio),
            stratify=[img.parent.name for img in temp_imgs]
        )
        
        # 复制文件
        for subset_name, subset_imgs in [
            ('train', train_imgs),
            ('test', test_imgs),
            ('valid', valid_imgs)
        ]:
            subset_dir = output / subset_name
            for img_path in subset_imgs:
                class_name = img_path.parent.name
                target_subdir = subset_dir / class_name
                target_subdir.mkdir(parents=True, exist_ok=True)
                shutil.copy(img_path, target_subdir / img_path.name)
        
        print(f"数据集划分完成:")
        print(f"  Train: {len(train_imgs)} images")
        print(f"  Test:  {len(test_imgs)} images")
        print(f"  Valid: {len(valid_imgs)} images")
```

**requirements.txt 更新**:

```txt
# 深度学习
torch>=2.0.0
torchvision>=0.15.0
torchmetrics>=1.0.0

# 数据处理
albumentations>=1.3.0
scikit-image>=0.21.0
scikit-learn>=1.2.0

# 可视化
matplotlib>=3.7.0
seaborn>=0.12.0
grad-cam>=1.4.0

# 模型导出
onnx>=1.14.0
onnxruntime>=1.15.0
```

---

### 方案 4: 性能评估指标系统 ⭐⭐⭐⭐⭐

**目标**: 标准化模型评估，提供临床可信的指标

**实现**:

```python
# app/inference/metrics/evaluation_metrics.py
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class BreastCancerMetrics:
    """乳腺超声 AI 评估指标"""
    
    @staticmethod
    def calculate_dice_score(pred_mask, true_mask, smooth=1e-6):
        """计算 Dice Score"""
        pred = pred_mask.flatten()
        true = true_mask.flatten()
        intersection = (pred * true).sum()
        dice = (2. * intersection) / (pred.sum() + true.sum() + smooth)
        return dice
    
    @staticmethod
    def calculate_iou(pred_mask, true_mask, smooth=1e-6):
        """计算 IoU (Intersection over Union)"""
        pred = pred_mask.flatten()
        true = true_mask.flatten()
        intersection = (pred * true).sum()
        union = pred.sum() + true.sum() - intersection
        iou = intersection / (union + smooth)
        return iou
    
    @staticmethod
    def plot_confusion_matrix(
        y_true,
        y_pred,
        class_names=['Normal', 'Benign', 'Malignant'],
        save_path=None
    ):
        """绘制混淆矩阵"""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names,
            yticklabels=class_names,
            annot_kws={'size': 12}
        )
        plt.title('Confusion Matrix', fontsize=16)
        plt.ylabel('True Label', fontsize=14)
        plt.xlabel('Predicted Label', fontsize=14)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return cm
    
    @staticmethod
    def generate_classification_report(
        y_true,
        y_pred,
        class_names=['Normal', 'Benign', 'Malignant']
    ):
        """生成分类报告"""
        report = classification_report(
            y_true, y_pred,
            target_names=class_names,
            output_dict=True
        )
        
        # 转换为美观格式
        summary = {
            'overall_accuracy': report['accuracy'],
            'macro_avg': {
                'precision': report['macro avg']['precision'],
                'recall': report['macro avg']['recall'],
                'f1_score': report['macro avg']['f1-score']
            },
            'weighted_avg': {
                'precision': report['weighted avg']['precision'],
                'recall': report['weighted avg']['recall'],
                'f1_score': report['weighted avg']['f1-score']
            },
            'per_class': {}
        }
        
        for cls_name in class_names:
            if cls_name in report:
                summary['per_class'][cls_name] = {
                    'precision': report[cls_name]['precision'],
                    'recall': report[cls_name]['recall'],
                    'f1_score': report[cls_name]['f1-score'],
                    'support': report[cls_name]['support']
                }
        
        return summary
    
    @staticmethod
    def plot_training_curves(
        train_losses,
        val_losses,
        train_metrics=None,
        val_metrics=None,
        save_path=None
    ):
        """绘制训练曲线"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Loss 曲线
        axes[0].plot(train_losses, label='Train Loss', linewidth=2)
        axes[0].plot(val_losses, label='Val Loss', linewidth=2)
        axes[0].set_title('Training & Validation Loss', fontsize=14)
        axes[0].set_xlabel('Epoch', fontsize=12)
        axes[0].set_ylabel('Loss', fontsize=12)
        axes[0].legend(fontsize=10)
        axes[0].grid(True, alpha=0.3)
        
        # Metric 曲线 (如 Accuracy/Dice)
        if train_metrics and val_metrics:
            axes[1].plot(train_metrics, label='Train Metric', linewidth=2)
            axes[1].plot(val_metrics, label='Val Metric', linewidth=2)
            axes[1].set_title('Training & Validation Metric', fontsize=14)
            axes[1].set_xlabel('Epoch', fontsize=12)
            axes[1].set_ylabel('Metric', fontsize=12)
            axes[1].legend(fontsize=10)
            axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig


class EvaluationPipeline:
    """完整评估流水线"""
    
    def __init__(self, model, device='cuda'):
        self.model = model
        self.device = device
        self.metrics_engine = BreastCancerMetrics()
    
    def evaluate(
        self,
        dataloader,
        class_names=['Normal', 'Benign', 'Malignant']
    ):
        """完整评估"""
        self.model.eval()
        
        all_preds = []
        all_labels = []
        all_masks_pred = []
        all_masks_true = []
        
        with torch.no_grad():
            for batch in tqdm(dataloader, desc='Evaluating'):
                images = batch['image'].to(self.device)
                labels = batch['label']
                masks = batch['mask']
                
                seg_pred, cls_pred = self.model(images)
                
                # 分类预测
                cls_preds = cls_pred.argmax(dim=1).cpu().numpy()
                all_preds.extend(cls_preds)
                all_labels.extend(labels.numpy())
                
                # 分割预测
                mask_preds = (seg_pred > 0.5).cpu().numpy()
                all_masks_pred.extend(mask_preds)
                all_masks_true.extend(masks.numpy())
        
        # 计算指标
        cls_report = self.metrics_engine.generate_classification_report(
            all_labels, all_preds, class_names
        )
        
        seg_dice = np.mean([
            self.metrics_engine.calculate_dice_score(pred, true)
            for pred, true in zip(all_masks_pred, all_masks_true)
        ])
        
        seg_iou = np.mean([
            self.metrics_engine.calculate_iou(pred, true)
            for pred, true in zip(all_masks_pred, all_masks_true)
        ])
        
        return {
            'classification': cls_report,
            'segmentation': {
                'dice_score': seg_dice,
                'iou': seg_iou
            },
            'confusion_matrix': self.metrics_engine.plot_confusion_matrix(
                all_labels, all_preds, class_names,
                save_path='results/confusion_matrix.png'
            )
        }
```

---

## 📋 实施路线图

### 第一阶段：基础能力建设 (Week 1-2)
- [ ] 集成 Grad-CAM 可解释性模块
- [ ] 实现数据增强管道
- [ ] 添加性能评估指标系统
- [ ] 更新 requirements.txt

### 第二阶段：模型优化 (Week 3-4)
- [ ] 实现多任务学习框架
- [ ] 训练并对比 single-task vs multi-task
- [ ] 验证集评估 (Dice/IoU/Accuracy)
- [ ] 生成五面板可视化结果

### 第三阶段：API 集成 (Week 5)
- [ ] 新增 API 端点 `/generate-gradcam`
- [ ] 新增 API 端点 `/evaluate-model`
- [ ] 更新 Swagger 文档
- [ ] 编写使用示例

### 第四阶段：测试与部署 (Week 6)
- [ ] 单元测试覆盖率>80%
- [ ] 集成测试验证
- [ ] 性能基准测试
- [ ] 生产环境部署

---

## 📚 参考资源

### GitHub 项目
1. https://github.com/sarah-antillia/YOLO-Breast-UltraSound-Images
2. https://github.com/hijab1514/MultiTask_CNN_Pipeline
3. https://github.com/jxy1989/busi (BUSI 数据集官方)

### 论文
1. Al-Dhabyani W, et al. "Dataset of breast ultrasound images." Data in Brief (2020)
2. Wang L, et al. "A foundation generative model for breast ultrasound image analysis" Nature Engineering (2026)
3. DeepHealth Study. "AI-enhanced breast cancer screening" Nature Health (2026)

### 工具库
- Grad-CAM: https://github.com/jacobgil/pytorch-grad-cam
- Albumentations: https://albumentations.ai/
- TorchMetrics: https://torchmetrics.readthedocs.io/

---

## 🎯 预期效果

### 技术指标提升

| 指标 | 当前 | 目标 | 提升 |
|------|------|------|------|
| 分类 Accuracy | API 依赖 | 92%+ | 本地可训练 |
| 分割 Dice | - | 0.70+ | 达到 SOTA |
| 可解释性 | 基础热图 | 五面板 Grad-CAM | 临床信任度↑ |
| 训练数据 | 原始 | 增强×5-10 倍 | 泛化能力↑ |

### 临床价值
- ✅ 医生信任度提升 (可解释性)
- ✅ 诊断一致性提升 (>90%)
- ✅ 模型迭代效率提升 (本地训练)
- ✅ 多中心验证可行性 (标准化评估)

---

**版本**: v3.1.0  
**更新日期**: 2026-06-03  
**负责人**: AI 研发团队
