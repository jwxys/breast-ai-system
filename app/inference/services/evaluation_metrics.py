"""
模型评估指标系统

提供乳腺超声 AI 诊断的标准化评估指标：
- 分类指标：Accuracy, Precision, Recall, F1, Confusion Matrix
- 分割指标：Dice Score, IoU
- 训练曲线可视化
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)


class BreastCancerMetrics:
    """乳腺超声 AI 评估指标"""
    
    @staticmethod
    def dice_score(pred_mask: np.ndarray, true_mask: np.ndarray, smooth=1e-6) -> float:
        """计算 Dice Score"""
        pred = pred_mask.flatten()
        true = true_mask.flatten()
        intersection = (pred * true).sum()
        dice = (2. * intersection) / (pred.sum() + true.sum() + smooth)
        return float(dice)
    
    @staticmethod
    def iou_score(pred_mask: np.ndarray, true_mask: np.ndarray, smooth=1e-6) -> float:
        """计算 IoU (Intersection over Union)"""
        pred = pred_mask.flatten()
        true = true_mask.flatten()
        intersection = (pred * true).sum()
        union = pred.sum() + true.sum() - intersection
        iou = intersection / (union + smooth)
        return float(iou)
    
    @staticmethod
    def classification_metrics(
        y_true: List[int],
        y_pred: List[int],
        class_names: List[str] = ['Normal', 'Benign', 'Malignant']
    ) -> Dict:
        """生成完整分类评估报告"""
        report = classification_report(
            y_true, y_pred,
            target_names=class_names,
            output_dict=True
        )
        
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
                    'support': int(report[cls_name]['support'])
                }
        
        return summary
    
    @staticmethod
    def plot_confusion_matrix(
        y_true: List[int],
        y_pred: List[int],
        class_names: List[str] = ['Normal', 'Benign', 'Malignant'],
        save_path: str = 'results/confusion_matrix.png'
    ) -> np.ndarray:
        """绘制并保存混淆矩阵"""
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
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return cm
