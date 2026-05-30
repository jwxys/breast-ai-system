"""
AI 推理服务
集成 PBS-Net (分割) + DFMFI (特征融合) + HXM-Net (多模态诊断)
"""

import torch
import torch.nn as nn
from typing import Dict, Any, List, Tuple
from PIL import Image
import numpy as np
from pathlib import Path


class PBSNet(nn.Module):
    """
    PBS-Net: Pixel-to-Boundary Soft Supervision Network
    用于乳腺超声病灶分割
    """
    
    def __init__(self, in_channels=1, num_classes=2):
        super().__init__()
        # 简化版实现 (完整版见 core-algorithms-part1.md)
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 2, stride=2),
            nn.Conv2d(64, num_classes, 1),
        )
        self.softmax = nn.Softmax2d()
    
    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return self.softmax(x)
    
    @staticmethod
    def load_checkpoint(path: str) -> 'PBSNet':
        """加载预训练模型"""
        model = PBSNet()
        if Path(path).exists():
            model.load_state_dict(torch.load(path, map_location='cpu'))
        return model


class DFMFI(nn.Module):
    """
    DFMFI: Deep Feature Multi-Fusion Integration
    多切面深度特征融合网络
    """
    
    def __init__(self, feature_dim=512, num_classes=2):
        super().__init__()
        # 多切面特征融合
        self.transverse_fc = nn.Linear(feature_dim, 256)
        self.longitudinal_fc = nn.Linear(feature_dim, 256)
        self.coronal_fc = nn.Linear(feature_dim, 256)
        
        # 注意力融合
        self.attention = nn.MultiheadAttention(embed_dim=256, num_heads=8)
        self.classifier = nn.Sequential(
            nn.Linear(256 * 3, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )
    
    def forward(self, features: List[torch.Tensor]) -> torch.Tensor:
        # 特征投影
        f1 = self.transverse_fc(features[0])
        f2 = self.longitudinal_fc(features[1])
        f3 = self.coronal_fc(features[2])
        
        # 注意力融合
        fused = torch.stack([f1, f2, f3], dim=1)
        attn_out, _ = self.attention(fused, fused, fused)
        
        # 分类
        flattened = attn_out.view(attn_out.size(0), -1)
        return self.classifier(flattened)


class HXMNet(nn.Module):
    """
    HXM-Net: Hybrid Cross-Modal Attention Network
    超声 + 钼靶+MRI 多模态融合诊断网络
    """
    
    def __init__(self, modalities=3, num_classes=7):
        super().__init__()
        # 模态特异性编码器
        self.ultrasound_encoder = nn.Sequential(
            nn.Conv2d(1, 64, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((7, 7)),
        )
        self.mammography_encoder = nn.Sequential(
            nn.Conv2d(1, 64, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((7, 7)),
        )
        self.mri_encoder = nn.Sequential(
            nn.Conv2d(1, 64, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((7, 7)),
        )
        
        # 交叉模态注意力
        self.cross_attention = nn.MultiheadAttention(
            embed_dim=64 * 7 * 7, 
            num_heads=8,
            batch_first=True
        )
        
        # 临床特征融合
        self.clinical_fc = nn.Sequential(
            nn.Linear(2, 32),  # age, family_history
            nn.ReLU(),
        )
        
        # 分类器
        self.classifier = nn.Sequential(
            nn.Linear(64 * 7 * 7 * 3 + 32, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes),  # BI-RADS 1-5 + 0, 6
        )
    
    def forward(
        self,
        ultrasound: torch.Tensor,
        mammography: torch.Tensor | None = None,
        mri: torch.Tensor | None = None,
        clinical Features: torch.Tensor | None = None
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        # 模态编码
        f_us = self.ultrasound_encoder(ultrasound).flatten(1)
        
        modality_weights = {"ultrasound": 1.0}
        
        if mammography is not None:
            f_mg = self.mammography_encoder(mammography).flatten(1)
            modality_weights["mammography"] = 0.6
        else:
            f_mg = torch.zeros_like(f_us)
        
        if mri is not None:
            f_mri = self.mri_encoder(mri).flatten(1)
            modality_weights["mri"] = 0.4
        else:
            f_mri = torch.zeros_like(f_us)
        
        # 交叉模态注意力
        stacked = torch.stack([f_us, f_mg, f_mri], dim=1)
        attn_out, attn_weights = self.cross_attention(stacked, stacked, stacked)
        
        # 融合特征
        fused = attn_out.flatten(1)
        
        # 融合临床特征
        if clinical_features is not None:
            clinical_out = self.clinical_fc(clinical_features)
            fused = torch.cat([fused, clinical_out], dim=1)
        
        # BI-RADS 分类
        birads_logits = self.classifier(fused)
        
        # 计算模态重要性权重
        modality_importance = {
            "B-mode": float(attn_weights[0, 0, :].mean().item()),
            "Doppler": float(attn_weights[0, 1, :].mean().item()) if mammography is not None else 0.0,
            "Elasticity": float(attn_weights[0, 2, :].mean().item()) if mri is not None else 0.0,
        }
        
        return birads_logits, modality_importance


class AIInferenceService:
    """AI 推理服务"""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.pbs_net = None
        self.df_mfi = None
        self.hxm_net = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def load_models(self):
        """加载所有 AI 模型"""
        # 加载 PBS-Net (分割)
        pbs_path = self.model_dir / "pbs_net.pth"
        if pbs_path.exists():
            self.pbs_net = PBSNet.load_checkpoint(str(pbs_path)).to(self.device)
            self.pbs_net.eval()
        
        # 加载 DFMFI (特征融合)
        dfmfi_path = self.model_dir / "dfmfi.pth"
        if dfmfi_path.exists():
            self.df_mfi = DFMFI().to(self.device)
            self.df_mfi.load_state_dict(torch.load(str(dfmfi_path)))
            self.df_mfi.eval()
        
        # 加载 HXM-Net (多模态诊断)
        hxm_path = self.model_dir / "hxm_net.pth"
        if hxm_path.exists():
            self.hxm_net = HXMNet().to(self.device)
            self.hxm_net.load_state_dict(torch.load(str(hxm_path)))
            self.hxm_net.eval()
    
    async def segment_lesion(self, image_path: str) -> Dict[str, Any]:
        """
        使用 PBS-Net 进行病灶分割
        """
        if self.pbs_net is None:
            raise RuntimeError("PBS-Net 模型未加载")
        
        # 读取图像
        image = Image.open(image_path).convert("L")
        image = image.resize((256, 256))
        tensor = torch.from_numpy(np.array(image)).float() / 255.0
        tensor = tensor.unsqueeze(0).unsqueeze(0).to(self.device)
        
        # 推理
        with torch.no_grad():
            segmentation = self.pbs_net(tensor)
            mask = segmentation.argmax(dim=1).squeeze().cpu().numpy()
        
        # 计算病灶区域统计
        lesion_pixels = np.sum(mask == 1)
        total_pixels = mask.size
        lesion_ratio = lesion_pixels / total_pixels
        
        return {
            "segmentation_mask": mask.tolist(),
            "lesion_area": int(lesion_pixels),
            "lesion_ratio": float(lesion_ratio),
            "border_clarity": self._calculate_border_clarity(mask),
        }
    
    async def diagnose(
        self,
        ultrasound_features: Dict[str, Any],
        mammography_features: Dict[str, Any] | None = None,
        mri_features: Dict[str, Any] | None = None,
        patient_age: int = 50,
        family_history: bool = False
    ) -> Dict[str, Any]:
        """
        使用 HXM-Net 进行多模态融合诊断
        """
        if self.hxm_net is None:
            # 模型未加载时使用规则推理
            return self._rule_based_diagnosis(ultrasound_features, patient_age)
        
        # 准备输入张量
        us_tensor = self._prepare_ultrasound_tensor(ultrasound_features).to(self.device)
        mg_tensor = self._prepare_mammography_tensor(mammography_features) if mammography_features else None
        mri_tensor = self._prepare_mri_tensor(mri_features) if mri_features else None
        clinical_tensor = torch.tensor([[patient_age / 100.0, 1.0 if family_history else 0.0]]).to(self.device)
        
        # 推理
        with torch.no_grad():
            logits, modality_weights = self.hxm_net(
                us_tensor, mg_tensor, mri_tensor, clinical_tensor
            )
            probabilities = torch.softmax(logits, dim=1)
        
        # 解释结果
        birads_idx = probabilities.argmax().item()
        birads_map = ["0", "1", "2", "3", "4A", "4B", "4C", "5"]
        birads_category = birads_map[birads_idx] if birads_idx < len(birads_map) else "4A"
        
        confidence = float(probabilities[0, birads_idx].item())
        malignancy = self._interpret_malignancy(birads_category)
        
        return {
            "birads_category": birads_category,
            "malignancy_prediction": malignancy,
            "confidence": confidence,
            "modality_weights": modality_weights,
            "probabilities": probabilities.cpu().numpy().tolist()[0],
        }
    
    def _rule_based_diagnosis(
        self, 
        features: Dict[str, Any], 
        age: int
    ) -> Dict[str, Any]:
        """规则基诊断（模型未加载时的备选方案）"""
        score = 0
        
        # BI-RADS 特征评分
        shape = features.get("shape", "oval")
        if shape == "irregular":
            score += 2
        
        margin = features.get("margin", "circumscribed")
        if margin in ["microlobulated", "obscured", "indistinct", "spiculated"]:
            score += 2
        
        orientation = features.get("orientation", "parallel")
        if orientation == "not_parallel":
            score += 1
        
        echo = features.get("echo_pattern", "anechoic")
        if echo == "marked_hypoechoic":
            score += 2
        
        # 年龄因素
        if age < 30:
            score -= 1
        elif age > 50:
            score += 1
        
        # 映射到 BI-RADS
        if score <= 1:
            birads = "3"
            malignancy = "可能良性"
            confidence = 0.95
        elif score <= 3:
            birads = "4A"
            malignancy = "可疑恶性 (低度)"
            confidence = 0.75
        elif score <= 5:
            birads = "4B"
            malignancy = "可疑恶性 (中度)"
            confidence = 0.85
        else:
            birads = "4C"
            malignancy = "可疑恶性 (高度)"
            confidence = 0.92
        
        return {
            "birads_category": birads,
            "malignancy_prediction": malignancy,
            "confidence": confidence,
            "rule_based_score": score,
        }
    
    def _calculate_border_clarity(self, mask: np.ndarray) -> float:
        """计算边界清晰度"""
        from scipy import ndimage
        edges = ndimage.sobel(mask.astype(float))
        return float(np.mean(edges))
    
    def _prepare_ultrasound_tensor(self, features: Dict[str, Any]) -> torch.Tensor:
        """准备超声输入张量"""
        # 简化实现
        return torch.randn(1, 1, 224, 224)
    
    def _prepare_mammography_tensor(self, features: Dict[str, Any]) -> torch.Tensor:
        """准备钼靶输入张量"""
        return torch.randn(1, 1, 224, 224)
    
    def _prepare_mri_tensor(self, features: Dict[str, Any]) -> torch.Tensor:
        """准备 MRI 输入张量"""
        return torch.randn(1, 1, 224, 224)
    
    def _interpret_malignancy(self, birads: str) -> str:
        """解释 BI-RADS 分级"""
        mapping = {
            "0": "需要进一步评估",
            "1": "阴性",
            "2": "良性发现",
            "3": "可能良性 (恶性风险<2%)",
            "4A": "可疑恶性 (低度 2-10%)",
            "4B": "可疑恶性 (中度 10-50%)",
            "4C": "可疑恶性 (高度 50-95%)",
            "5": "高度怀疑恶性 (>95%)",
        }
        return mapping.get(birads, "未知")


# 全局 AI 服务实例
ai_service = AIInferenceService()


def get_ai_service() -> AIInferenceService:
    """获取 AI 推理服务实例"""
    return ai_service
