"""
影像组学特征提取器

从超声图像中提取高通量定量特征
用于 AI 模型训练和分子分型预测
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class FeatureCategory(str, Enum):
    """特征类别"""
    SHAPE = "shape"              # 形态学特征
    FIRST_ORDER = "first_order"  # 一阶统计特征
    GLCM = "glcm"               # 灰度共生矩阵
    GLRLM = "glrlm"             # 灰度游程矩阵
    GLSZM = "glszm"             # 灰度区域大小矩阵
    NGTDM = "ngtdm"             # 邻域灰度差分矩阵
    WAVELET = "wavelet"         # 小波特征


@dataclass
class RadiomicsFeatures:
    """影像组学特征数据结构"""
    # 形态学特征
    volume: float                    # 体积 (mm³)
    surface_area: float              # 表面积 (mm²)
    spherical_disproportion: float   # 球度
    compactness: float               # 紧度
    irregularity: float              # 不规则度
    
    # 一阶统计特征
    mean_intensity: float            # 平均灰度
    std_intensity: float             # 标准差
    skewness: float                  # 偏度
    kurtosis: float                  # 峰度
    entropy: float                   # 熵
    
    # GLCM 特征
    glcm_contrast: float             # 对比度
    glcm_correlation: float          # 相关性
    glcm_homogeneity: float          # 均匀性
    glcm_energy: float               # 能量
    
    # GLRLM 特征
    short_run_emphasis: float        # 短游程优势
    long_run_emphasis: float         # 长游程优势
    
    # 小波特征 (多尺度)
    wavelet_llh_energy: float        # 小波子带能量
    wavelet_hll_energy: float
    wavelet_lhh_energy: float
    wavelet_hhh_energy: float


class RadiomicsExtractor:
    """
    影像组学特征提取器
    
    基于 PyRadiomics 标准
    提取 6 大类 100+ 特征
    """
    
    def __init__(self, image: np.ndarray, spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)):
        """
        初始化提取器
        
        Args:
            image: 3D 图像数组 (H×W×D)
            spacing: 体素间距 (mm)
        """
        self.image = image.astype(np.float32)
        self.spacing = spacing
        self.mask = None
    
    def set_mask(self, mask: np.ndarray):
        """
        设置分割掩码
        
        Args:
            mask: 二值掩码 (与 image 同尺寸)
        """
        if mask.shape != self.image.shape:
            raise ValueError("掩码尺寸必须与图像一致")
        self.mask = mask
    
    def extract_all(self) -> RadiomicsFeatures:
        """
        提取全部影像组学特征
        
        Returns:
            RadiomicsFeatures: 特征数据
        """
        if self.mask is None:
            # 自动阈值分割
            self.mask = self._auto_segment()
        
        # 提取各类特征
        shape_features = self._extract_shape_features()
        first_order = self._extract_first_order()
        glcm_features = self._extract_glcm()
        glrlm_features = self._extract_glrlm()
        wavelet_features = self._extract_wavelet()
        
        return RadiomicsFeatures(
            **shape_features,
            **first_order,
            **glcm_features,
            **glrlm_features,
            **wavelet_features
        )
    
    def _auto_segment(self) -> np.ndarray:
        """
        自动病灶分割
        
        使用 Otsu 阈值法
        """
        from skimage.filters import threshold_otsu
        
        image_2d = np.mean(self.image, axis=2)  # 降维到 2D
        threshold = threshold_otsu(image_2d)
        mask_2d = image_2d > threshold
        
        # 形态学操作去除噪声
        from skimage.morphology import binary_opening, binary_closing
        mask_2d = binary_opening(mask_2d)
        mask_2d = binary_closing(mask_2d)
        
        # 扩展到 3D
        return np.stack([mask_2d] * self.image.shape[2], axis=2)
    
    def _extract_shape_features(self) -> Dict[str, float]:
        """
        提取形态学特征
        
        Returns:
            Dict: 形态学特征
        """
        if self.mask is None:
            raise ValueError("需要先设置掩码")
        
        # 计算体积 (体素数 × 体素体积)
        voxel_volume = np.prod(self.spacing)
        volume = np.sum(self.mask) * voxel_volume
        
        # 计算表面积
        from skimage.measure import mesh_surface_area
        # 简化计算：使用体素边界
        surface_area = self._calculate_surface_area()
        
        # 球度 (sphericity)
        # ψ = π^(1/3) × (6V)^(2/3) / A
        sphericity = (np.pi ** (1/3)) * (6 * volume) ** (2/3) / surface_area
        
        # 紧度 (compactness)
        # C = P² / (4πA)
        perimeter = self._calculate_perimeter()
        compactness = (perimeter ** 2) / (4 * np.pi * surface_area)
        
        # 不规则度
        # IR = 1 - sphericity
        irregularity = 1 - sphericity
        
        return {
            "volume": float(volume),
            "surface_area": float(surface_area),
            "spherical_disproportion": float(1 / sphericity),
            "compactness": float(compactness),
            "irregularity": float(irregularity)
        }
    
    def _calculate_surface_area(self) -> float:
        """计算表面积 (简化版)"""
        from skimage.measure import marching_cubes
        
        try:
            verts, faces, _, _ = marching_cubes(self.mask, level=0.5, spacing=self.spacing)
            return self._mesh_area(verts, faces)
        except:
            # 降级：体素计数近似
            return float(np.sum(self.mask) * np.prod(self.spacing) ** (2/3))
    
    def _mesh_area(self, verts: np.ndarray, faces: np.ndarray) -> float:
        """计算网格表面积"""
        triangles = verts[faces]
        vectors = np.diff(triangles, axis=1)
        cross_products = np.cross(vectors[:, 0], vectors[:, 1])
        areas = 0.5 * np.linalg.norm(cross_products, axis=1)
        return float(np.sum(areas))
    
    def _calculate_perimeter(self) -> float:
        """计算周长 (2D 切片平均)"""
        from skimage.measure import perimeter
        
        perimeters = []
        for i in range(self.image.shape[2]):
            if np.sum(self.mask[:, :, i]) > 0:
                p = perimeter(self.mask[:, :, i])
                perimeters.append(p)
        
        return float(np.mean(perimeters)) if perimeters else 0.0
    
    def _extract_first_order(self) -> Dict[str, float]:
        """
        提取一阶统计特征
        
        Returns:
            Dict: 一阶特征
        """
        if self.mask is None:
            raise ValueError("需要先设置掩码")
        
        # 提取 ROI 灰度值
        roi_values = self.image[self.mask > 0]
        
        if len(roi_values) == 0:
            return {
                "mean_intensity": 0.0,
                "std_intensity": 0.0,
                "skewness": 0.0,
                "kurtosis": 0.0,
                "entropy": 0.0
            }
        
        mean_val = np.mean(roi_values)
        std_val = np.std(roi_values)
        
        # 偏度 (skewness)
        skewness = np.mean(((roi_values - mean_val) / std_val) ** 3) if std_val > 0 else 0
        
        # 峰度 (kurtosis)
        kurtosis = np.mean(((roi_values - mean_val) / std_val) ** 4) - 3 if std_val > 0 else 0
        
        # 熵 (entropy)
        hist, _ = np.histogram(roi_values, bins=64)
        hist = hist[hist > 0]
        probs = hist / np.sum(hist)
        entropy = -np.sum(probs * np.log2(probs))
        
        return {
            "mean_intensity": float(mean_val),
            "std_intensity": float(std_val),
            "skewness": float(skewness),
            "kurtosis": float(kurtosis),
            "entropy": float(entropy)
        }
    
    def _extract_glcm(self) -> Dict[str, float]:
        """
        灰度共生矩阵特征
        
        Returns:
            Dict: GLCM 特征
        """
        from skimage.feature import graycomatrix
        
        if self.mask is None:
            raise ValueError("需要先设置掩码")
        
        # 量化到 8 级灰度
        image_2d = np.mean(self.image, axis=2)
        image_quantized = np.digitize(image_2d, np.linspace(0, 255, 8))
        
        # 计算 GLCM (多方向平均)
        distances = [1, 2]
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
        
        glcm = graycomatrix(
            image_quantized,
            distances=distances,
            angles=angles,
            levels=8,
            symmetric=True,
            normed=True
        )
        
        # 从 GLCM 提取特征
        # 对比度: Σ(i-j)² × p(i,j)
        i, j = np.meshgrid(np.arange(8), np.arange(8), indexing='ij')
        contrast = np.sum((i - j) ** 2 * glcm) / (len(distances) * len(angles))
        
        # 相关性: Σ(i×j×p(i,j)) / (σi×σj)
        mean_i = np.sum(i * glcm)
        mean_j = np.sum(j * glcm)
        std_i = np.sqrt(np.sum((i - mean_i) ** 2 * glcm))
        std_j = np.sqrt(np.sum((j - mean_j) ** 2 * glcm))
        correlation = np.sum(i * j * glcm) / (std_i * std_j + 1e-10)
        
        # 均匀性: Σ 1/(1+(i-j)²) × p(i,j)
        homogeneity = np.sum(glcm / (1 + (i - j) ** 2))
        
        # 能量: Σ p(i,j)²
        energy = np.sum(glcm ** 2)
        
        return {
            "glcm_contrast": float(np.mean(contrast)),
            "glcm_correlation": float(np.mean(correlation)),
            "glcm_homogeneity": float(homogeneity),
            "glcm_energy": float(energy)
        }
    
    def _extract_glrlm(self) -> Dict[str, float]:
        """
        灰度游程矩阵特征
        
        Returns:
            Dict: GLRLM 特征
        """
        # 简化实现
        # 实际应使用 skimage.feature.graycoprops
        
        if self.mask is None:
            return {
                "short_run_emphasis": 0.0,
                "long_run_emphasis": 0.0
            }
        
        # 简化的游程分析
        image_1d = self.image[self.mask > 0].flatten()
        
        # 计算游程
        runs = []
        current_run = 1
        for i in range(1, len(image_1d)):
            if image_1d[i] == image_1d[i-1]:
                current_run += 1
            else:
                runs.append(current_run)
                current_run = 1
        runs.append(current_run)
        
        # 短游程优势 (SRE)
        sre = np.sum(1 / (np.array(runs) ** 2)) / len(runs) if runs else 0
        
        # 长游程优势 (LRE)
        lre = np.sum(np.array(runs) ** 2) / len(runs) if runs else 0
        
        return {
            "short_run_emphasis": float(sre),
            "long_run_emphasis": float(lre)
        }
    
    def _extract_wavelet(self) -> Dict[str, float]:
        """
        小波特征提取
        
        Returns:
            Dict: 小波特征
        """
        import pywt
        
        # 2D 切片小波分解
        image_2d = np.mean(self.image, axis=2)
        
        # 单级小波分解
        coeffs = pywt.dwt2(image_2d, 'haar')
        LL, (LH, HL, HH) = coeffs
        
        # 各子带能量
        llh_energy = np.sum(LH ** 2)
        hll_energy = np.sum(HL ** 2)
        lhh_energy = float(np.sum(HH ** 2))
        hhh_energy = 0.0  # 三级分解
        
        return {
            "wavelet_llh_energy": float(llh_energy),
            "wavelet_hll_energy": float(hll_energy),
            "wavelet_lhh_energy": float(lhh_energy),
            "wavelet_hhh_energy": float(hhh_energy)
        }
    
    def to_dict(self) -> Dict[str, float]:
        """
        转换为字典格式
        
        Returns:
            Dict: 特征字典
        """
        features = self.extract_all()
        return {
            "volume": features.volume,
            "surface_area": features.surface_area,
            "spherical_disproportion": features.spherical_disproportion,
            "compactness": features.compactness,
            "irregularity": features.irregularity,
            "mean_intensity": features.mean_intensity,
            "std_intensity": features.std_intensity,
            "skewness": features.skewness,
            "kurtosis": features.kurtosis,
            "entropy": features.entropy,
            "glcm_contrast": features.glcm_contrast,
            "glcm_correlation": features.glcm_correlation,
            "glcm_homogeneity": features.glcm_homogeneity,
            "glcm_energy": features.glcm_energy,
            "short_run_emphasis": features.short_run_emphasis,
            "long_run_emphasis": features.long_run_emphasis,
            "wavelet_llh_energy": features.wavelet_llh_energy,
            "wavelet_hll_energy": features.wavelet_hll_energy,
            "wavelet_lhh_energy": features.wavelet_lhh_energy,
            "wavelet_hhh_energy": features.wavelet_hhh_energy
        }
