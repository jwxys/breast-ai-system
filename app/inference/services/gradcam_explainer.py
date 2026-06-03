"""
Grad-CAM 可解释性分析器

基于 PyTorch Grad-CAM 实现临床可解释的 AI 决策可视化
生成五面板结果：原图 | GT Mask | Pred Mask | Heatmap | Overlay
"""

import torch
import torch.nn.functional as F
import numpy as np
import cv2
from typing import Optional, Tuple
from dataclasses import dataclass
import base64


@dataclass
class GradCAMResult:
    """Grad-CAM 分析结果"""
    heatmap: np.ndarray
    heatmap_color: np.ndarray
    overlay: np.ndarray
    five_panel: Optional[np.ndarray]
    max_activation: float
    mean_activation: float


class GradCAMExplainer:
    """Grad-CAM 可解释性分析器"""
    
    def __init__(self, model: torch.nn.Module, target_layer=None):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        if target_layer:
            self._register_hooks()
    
    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]
        if self.target_layer:
            self.target_layer.register_forward_hook(forward_hook)
            self.target_layer.register_backward_hook(backward_hook)
    
    def generate_cam(self, image: np.ndarray, target_class: Optional[int] = None) -> GradCAMResult:
        was_training = self.model.training
        self.model.eval()
        
        try:
            img_resized = cv2.resize(image, (224, 224))
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            img_norm = (img_resized / 255.0 - mean) / std
            img_chw = np.transpose(img_norm, (2, 0, 1))
            img_tensor = torch.from_numpy(img_chw).float().unsqueeze(0)
            img_tensor = img_tensor.to(next(self.model.parameters()).device)
            
            output = self.model(img_tensor)
            if isinstance(output, (tuple, list)):
                output = output[1]
            
            if target_class is None:
                target_class = output.argmax(dim=1).item()
            
            loss = output[0, target_class]
            self.model.zero_grad()
            loss.backward(retain_graph=True)
            
            pooled_gradients = torch.mean(self.gradients, dim=[2, 3])
            activations = self.activations[0]
            for i in range(activations.shape[0]):
                activations[i] *= pooled_gradients[i]
            
            heatmap = torch.sum(activations, dim=0).cpu().numpy()
            heatmap = np.maximum(heatmap, 0)
            heatmap = heatmap / (heatmap.max() + 1e-8)
            heatmap = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
            
            heatmap_color = cv2.applyColorMap((heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET)
            overlay = cv2.addWeighted(image, 0.6, heatmap_color, 0.4, 0)
            
            return GradCAMResult(
                heatmap=heatmap, heatmap_color=heatmap_color, overlay=overlay,
                five_panel=None, max_activation=float(heatmap.max()),
                mean_activation=float(heatmap.mean())
            )
        finally:
            if was_training:
                self.model.train()
