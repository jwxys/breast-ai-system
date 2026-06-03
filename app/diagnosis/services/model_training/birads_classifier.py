"""
BI-RADS 分类模型训练

基于深度学习训练专用的乳腺超声 BI-RADS 分类模型
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import numpy as np
from PIL import Image


class BreastUltrasoundDataset(Dataset):
    """
    乳腺超声数据集
    
    支持数据增强和类别平衡
    """
    
    def __init__(
        self,
        image_paths: List[str],
        labels: List[int],
        transform=None,
        augment=False
    ):
        """
        初始化数据集
        
        Args:
            image_paths: 图像路径列表
            labels: BI-RADS 分级标签 (0-6)
            transform: 图像变换
            augment: 是否数据增强
        """
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
        self.augment = augment
        
        # 类别权重 (处理不平衡)
        self.class_weights = self._calculate_class_weights()
    
    def _calculate_class_weights(self) -> List[float]:
        """计算类别权重 (逆频率)"""
        from collections import Counter
        counts = Counter(self.labels)
        total = len(self.labels)
        n_classes = len(counts)
        weights = [total / (n_classes * counts.get(i, 1)) for i in range(n_classes)]
        return weights
    
    def __len__(self) -> int:
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        # 加载图像
        image = Image.open(self.image_paths[idx]).convert('RGB')
        
        # 数据增强
        if self.augment:
            image = self._augment(image)
        
        # 应用变换
        if self.transform:
            image = self.transform(image)
        
        return image, self.labels[idx]
    
    def _augment(self, image: Image.Image) -> Image.Image:
        """
        数据增强
        
        方法:
        - 随机旋转
        - 水平翻转
        - 亮度对比度调整
        - 弹性形变
        """
        import random
        from torchvision import transforms
        
        augmentations = transforms.Compose([
            transforms.RandomRotation(15),          # 随机旋转±15°
            transforms.RandomHorizontalFlip(0.5),   # 随机水平翻转
            transforms.ColorJitter(0.2, 0.2, 0.2),  # 亮度/对比度/饱和度扰动
            transforms.RandomAffine(0, translate=(0.1, 0.1)),  # 随机平移
        ])
        
        return augmentations(image)


class EfficientNetBI RADS(nn.Module):
    """
    基于 EfficientNet 的 BI-RADS 分类器
    """
    
    def __init__(
        self,
        model_name: str = 'efficientnet_b0',
        pretrained: bool = True,
        n_classes: int = 7
    ):
        """
        初始化分类器
        
        Args:
            model_name: EfficientNet 型号 (b0-b7)
            pretrained: 是否使用预训练权重
            n_classes: 分类数 (BI-RADS 0-6 共 7 类)
        """
        super().__init__()
        
        from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
        
        # 加载预训练模型
        if pretrained:
            self.backbone = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        else:
            self.backbone = efficientnet_b0()
        
        # 替换分类器
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(in_features, 256),
            nn.SiLU(),
            nn.Dropout(p=0.3),
            nn.Linear(256, n_classes)
        )
        
        # 冻结部分层 (可选)
        self._freeze_backbone(freeze_ratio=0.5)
    
    def _freeze_backbone(self, freeze_ratio: float):
        """冻结部分骨干网络参数"""
        total_layers = len(list(self.backbone.features.parameters()))
        freeze_layers = int(total_layers * freeze_ratio)
        
        for i, param in enumerate(self.backbone.features.parameters()):
            if i < freeze_layers:
                param.requires_grad = False
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)
    
    def predict_with_uncertainty(self, x: torch.Tensor, training: bool = True) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        预测并返回不确定性
        
        Args:
            x: 输入图像
            training: 是否启用 Dropout
        
        Returns:
            Tuple: (预测概率，不确定性)
        """
        if training:
            self.backbone.classifier.train()  # 启用 Dropout
        
        # MC Dropout: 多次前向传播
        n_samples = 10
        predictions = []
        
        for _ in range(n_samples):
            logits = self.backbone(x)
            probs = F.softmax(logits, dim=1)
            predictions.append(probs)
        
        predictions = torch.stack(predictions, dim=0)
        
        # 平均预测
        mean_pred = predictions.mean(dim=0)
        
        # 不确定性 (预测的标准差)
        uncertainty = predictions.std(dim=0)
        
        return mean_pred, uncertainty


class BIRADSTrainer:
    """
    BI-RADS 分类器训练器
    """
    
    def __init__(
        self,
        model: nn.Module,
        device: str = 'cuda',
        learning_rate: float = 1e-4,
        weight_decay: float = 1e-4
    ):
        """
        初始化训练器
        
        Args:
            model: 模型
            device: 训练设备
            learning_rate: 学习率
            weight_decay: 权重衰减
        """
        self.device = device
        self.model = model.to(device)
        
        # 损失函数 (带类别权重)
        self.criterion = nn.CrossEntropyLoss()
        
        # 优化器
        self.optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        # 学习率调度器
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=50,
            eta_min=1e-6
        )
        
        # 训练历史
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': []
        }
    
    def train_epoch(
        self,
        train_loader: DataLoader,
        epoch: int
    ) -> Dict:
        """
        训练一个 epoch
        
        Returns:
            Dict: 训练指标
        """
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs, targets = inputs.to(self.device), targets.to(self.device)
            
            # 前向传播
            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            
            # 计算损失
            loss = self.criterion(outputs, targets)
            loss.backward()
            
            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            # 统计
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
        
        avg_loss = running_loss / len(train_loader)
        accuracy = 100. * correct / total
        
        self.history['train_loss'].append(avg_loss)
        self.history['train_acc'].append(accuracy)
        
        return {'loss': avg_loss, 'accuracy': accuracy}
    
    @torch.no_grad()
    def validate(
        self,
        val_loader: DataLoader
    ) -> Dict:
        """验证"""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        all_preds = []
        all_targets = []
        
        for inputs, targets in val_loader:
            inputs, targets = inputs.to(self.device), targets.to(self.device)
            outputs = self.model(inputs)
            
            loss = self.criterion(outputs, targets)
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())
        
        avg_loss = running_loss / len(val_loader)
        accuracy = 100. * correct / total
        
        # 计算各类别 F1 分数
        from sklearn.metrics import f1_score
        f1 = f1_score(all_targets, all_preds, average='weighted')
        
        self.history['val_loss'].append(avg_loss)
        self.history['val_acc'].append(accuracy)
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'f1_score': f1
        }
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int,
        save_path: str
    ):
        """
        完整训练流程
        
        Args:
            train_loader: 训练数据加载器
            val_loader: 验证数据加载器
            epochs: 训练轮数
            save_path: 模型保存路径
        """
        best_acc = 0.0
        
        for epoch in range(epochs):
            # 训练
            train_metrics = self.train_epoch(train_loader, epoch)
            
            # 验证
            val_metrics = self.validate(val_loader)
            
            # 打印进度
            print(f"Epoch {epoch+1}/{epochs}")
            print(f"  Train Loss: {train_metrics['loss']:.4f}, Acc: {train_metrics['accuracy']:.2f}%")
            print(f"  Val Loss: {val_metrics['loss']:.4f}, Acc: {val_metrics['accuracy']:.2f}%, F1: {val_metrics['f1_score']:.3f}")
            
            # 保存最佳模型
            if val_metrics['accuracy'] > best_acc:
                best_acc = val_metrics['accuracy']
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'accuracy': best_acc
                }, save_path)
                print(f"  ✓ 保存最佳模型 (准确率：{best_acc:.2f}%)")
            
            # 更新学习率
            self.scheduler.step()
        
        print(f"\n训练完成！最佳验证准确率：{best_acc:.2f}%")
        return self.history
