"""
图像预处理与增强

支持：
- DICOM 处理
- 图像增强
- 标准化
- 伪影去除
"""

import numpy as np
from typing import Dict, Optional, Tuple
from PIL import Image
import io


class ImageProcessor:
    """
    医学图像处理器
    
    功能：
    1. DICOM 读取
    2. 图像标准化
    3. 对比度增强
    4. 噪声去除
    """
    
    def __init__(self):
        self.default_size = (512, 512)
    
    def load_dicom(self, dicom_path: str) -> np.ndarray:
        """
        加载 DICOM 图像
        
        Args:
            dicom_path: DICOM 文件路径
        
        Returns:
            np.ndarray: 图像数组
        """
        try:
            import pydicom
            ds = pydicom.dcmread(dicom_path)
            
            # 获取像素数据
            pixel_array = ds.pixel_array
            
            # 应用 DICOM 窗宽窗位
            if hasattr(ds, 'WindowWidth') and hasattr(ds, 'WindowCenter'):
                ww = ds.WindowWidth
                wc = ds.WindowCenter
                pixel_array = self._apply_window(pixel_array, wc, ww)
            
            # 归一化到 0-1
            pixel_array = pixel_array.astype(np.float32)
            pixel_array = (pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min() + 1e-10)
            
            return pixel_array
            
        except Exception as e:
            raise ValueError(f"加载 DICOM 失败：{str(e)}")
    
    def _apply_window(self, image: np.ndarray, wc: float, ww: float) -> np.ndarray:
        """应用窗宽窗位"""
        wl = wc - ww / 2
        wh = wc + ww / 2
        
        image = np.clip(image, wl, wh)
        image = (image - wl) / (wh - wl + 1e-10)
        
        return image
    
    def preprocess(
        self,
        image: np.ndarray,
        resize: bool = True,
        normalize: bool = True,
        denoise: bool = True
    ) -> np.ndarray:
        """
        图像预处理
        
        Args:
            image: 输入图像
            resize: 是否调整大小
            normalize: 是否标准化
            denoise: 是否去噪
        
        Returns:
            np.ndarray: 处理后的图像
        """
        # 调整大小
        if resize:
            image = self._resize(image)
        
        # 去噪
        if denoise:
            image = self._denoise(image)
        
        # 标准化
        if normalize:
            image = self._normalize(image)
        
        return image
    
    def _resize(self, image: np.ndarray) -> np.ndarray:
        """调整图像大小"""
        if image.ndim == 2:
            # 2D 图像
            img_pil = Image.fromarray(image)
            img_resized = img_pil.resize(self.default_size, Image.Resampling.LANCZOS)
            return np.array(img_resized)
        else:
            # 3D 图像，调整每个切片
            resized_slices = []
            for i in range(image.shape[2]):
                slice_2d = image[:, :, i]
                img_pil = Image.fromarray(slice_2d)
                img_resized = img_pil.resize(self.default_size, Image.Resampling.LANCZOS)
                resized_slices.append(np.array(img_resized))
            return np.stack(resized_slices, axis=2)
    
    def _denoise(self, image: np.ndarray) -> np.ndarray:
        """
        图像去噪
        
        使用非局部均值去噪
        """
        try:
            from skimage.restoration import denoise_nl_means
            from skimage.util import img_as_float
            
            image_float = img_as_float(image)
            denoised = denoise_nl_means(
                image_float,
                h=0.1,
                fast_mode=True
            )
            return denoised
        except:
            # 降级：高斯滤波
            from scipy.ndimage import gaussian_filter
            return gaussian_filter(image, sigma=1)
    
    def _normalize(self, image: np.ndarray) -> np.ndarray:
        """标准化到 0-1"""
        min_val = image.min()
        max_val = image.max()
        
        if max_val - min_val > 1e-10:
            return (image - min_val) / (max_val - min_val)
        else:
            return np.zeros_like(image)
    
    def enhance_contrast(self, image: np.ndarray, method: str = 'clahe') -> np.ndarray:
        """
        对比度增强
        
        Args:
            image: 输入图像
            method: 方法 (clahe/he/ahe)
        
        Returns:
            np.ndarray: 增强后的图像
        """
        if method == 'clahe':
            return self._clahe(image)
        elif method == 'he':
            return self._histogram_equalization(image)
        elif method == 'ahe':
            return self._adaptive_he(image)
        else:
            return image
    
    def _clahe(self, image: np.ndarray) -> np.ndarray:
        """限制对比度自适应直方图均衡化"""
        try:
            import cv2
            
            # 转换到 0-255
            if image.max() <= 1.0:
                image_8bit = (image * 255).astype(np.uint8)
            else:
                image_8bit = image.astype(np.uint8)
            
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(image_8bit)
            
            # 归一化回 0-1
            return enhanced.astype(np.float32) / 255.0
            
        except:
            return self._histogram_equalization(image)
    
    def _histogram_equalization(self, image: np.ndarray) -> np.ndarray:
        """直方图均衡化"""
        from skimage import exposure
        return exposure.equalize_hist(image)
    
    def _adaptive_he(self, image: np.ndarray) -> np.ndarray:
        """自适应直方图均衡化"""
        from skimage import exposure
        return exposure.equalize_adapthist(image)
    
    def remove_artifacts(self, image: np.ndarray) -> np.ndarray:
        """
        去除伪影
        
        Args:
            image: 输入图像
        
        Returns:
            np.ndarray: 去伪影后的图像
        """
        # 检测并去除条带状伪影
        try:
            import cv2
            
            # 转换为 8bit
            if image.max() <= 1.0:
                image_8bit = (image * 255).astype(np.uint8)
            else:
                image_8bit = image.astype(np.uint8)
            
            # 中值滤波去除椒盐噪声
            denoised = cv2.medianBlur(image_8bit, 3)
            
            # 双边滤波保持边缘
            filtered = cv2.bilateralFilter(denoised, 9, 75, 75)
            
            return filtered.astype(np.float32) / 255.0
            
        except:
            return image
    
    def extract_roi(
        self,
        image: np.ndarray,
        bbox: Tuple[int, int, int, int],
        margin: int = 10
    ) -> np.ndarray:
        """
        提取感兴趣区域
        
        Args:
            image: 图像
            bbox: 边界框 (x1, y1, x2, y2)
            margin: 边距
        
        Returns:
            np.ndarray: ROI 区域
        """
        x1, y1, x2, y2 = bbox
        
        # 添加边距
        h, w = image.shape[:2]
        x1 = max(0, x1 - margin)
        y1 = max(0, y1 - margin)
        x2 = min(w, x2 + margin)
        y2 = min(h, y2 + margin)
        
        return image[y1:y2, x1:x2]
