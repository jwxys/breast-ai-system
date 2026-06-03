"""
可视化增强服务

提供病灶热图叠加、边缘高亮、测量标注等功能
支持 DICOM 图像处理和标注渲染
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from dataclasses import dataclass
from io import BytesIO
import base64


@dataclass
class AnnotationConfig:
    """标注配置"""
    color: Tuple[int, int, int]  # RGB 颜色
    thickness: int = 2
    font_size: int = 12
    alpha: float = 0.5  # 透明度


@dataclass
class Measurement:
    """测量标注"""
    label: str
    value: float
    unit: str
    start_point: Tuple[int, int]
    end_point: Tuple[int, int]


class VisualizationEnhancement:
    """
    可视化增强服务
    
    功能:
    1. 病灶热图生成
    2. 边缘高亮标注
    3. 测量尺寸标注
    4. 多病灶标记
    5. 淋巴结标注
    """
    
    # 预定义颜色方案
    COLORS = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'white': (255, 255, 255),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
    }
    
    # BI-RADS 分级对应的颜色
    BIRADS_COLORS = {
        '1': COLORS['green'],
        '2': COLORS['green'],
        '3': COLORS['cyan'],
        '4A': COLORS['yellow'],
        '4B': COLORS['orange'],
        '4C': COLORS['magenta'],
        '5': COLORS['red'],
        '6': COLORS['red'],
    }
    
    def __init__(self):
        """初始化可视化服务"""
        pass
    
    def load_image(self, image_source) -> np.ndarray:
        """
        加载图像
        
        Args:
            image_source: 图像源 (文件路径/URL/numpy 数组/base64)
        
        Returns:
            np.ndarray: RGB 图像数组
        """
        if isinstance(image_source, np.ndarray):
            return image_source
        elif isinstance(image_source, str):
            if image_source.startswith('data:image'):
                # Base64 编码
                base64_data = image_source.split(',')[1]
                image_bytes = base64.b64decode(base64_data)
                image = Image.open(BytesIO(image_bytes)).convert('RGB')
                return np.array(image)
            else:
                # 文件路径
                image = Image.open(image_source).convert('RGB')
                return np.array(image)
        else:
            raise ValueError("不支持的图像源类型")
    
    def draw_bounding_box(
        self,
        image: np.ndarray,
        bbox: Dict[str, float],
        label: str = "",
        color: Tuple[int, int, int] = None,
        thickness: int = 3
    ) -> np.ndarray:
        """
        绘制边界框
        
        Args:
            image: 输入图像
            bbox: 边界框 {x, y, width, height}
            label: 标签文字
            color: 边框颜色
            thickness: 边框粗细
        
        Returns:
            np.ndarray: 标注后的图像
        """
        if color is None:
            color = self.COLORS['red']
        
        # 转换为 OpenCV 格式 (BGR)
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image
        
        # 绘制矩形
        x1, y1 = int(bbox['x']), int(bbox['y'])
        x2, y2 = x1 + int(bbox['width']), y1 + int(bbox['height'])
        cv2.rectangle(image_bgr, (x1, y1), (x2, y2), color, thickness)
        
        # 添加标签背景
        if label:
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(label, font, 0.6, 2)[0]
            cv2.rectangle(
                image_bgr,
                (x1, y1 - text_size[1] - 10),
                (x1 + text_size[0], y1),
                color,
                -1
            )
            cv2.putText(
                image_bgr,
                label,
                (x1, y1 - 5),
                font,
                0.6,
                (255, 255, 255),
                2
            )
        
        # 转回 RGB
        return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    
    def draw_segmentation_mask(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        color: Tuple[int, int, int] = None,
        alpha: float = 0.5
    ) -> np.ndarray:
        """
        绘制分割掩码 (半透明叠加)
        
        Args:
            image: 原始图像
            mask: 分割掩码 (二值图)
            color: 掩码颜色
            alpha: 透明度
        
        Returns:
            np.ndarray: 叠加后的图像
        """
        if color is None:
            color = self.COLORS['green']
        
        # 确保掩码是二值图
        if len(mask.shape) == 3:
            mask = mask[:, :, 0]
        
        # 创建彩色掩码
        colored_mask = np.zeros_like(image)
        colored_mask[mask > 0] = color
        
        # 半透明叠加
        result = image.copy()
        mask_bool = mask > 0
        result[mask_bool] = cv2.addWeighted(
            colored_mask,
            alpha,
            image,
            1 - alpha,
            0
        )[mask_bool]
        
        return result
    
    def draw_heatmap(
        self,
        image: np.ndarray,
        heatmap_data: np.ndarray,
        alpha: float = 0.6,
        colormap: str = 'jet'
    ) -> np.ndarray:
        """
        绘制热图叠加 (AI 注意力区域)
        
        Args:
            image: 原始图像
            heatmap_data: 热图数据 (0-1 的浮点数组)
            alpha: 透明度
            colormap: 颜色映射 (jet/heat/cool/hot)
        
        Returns:
            np.ndarray: 热图叠加结果
        """
        # 归一化热图数据
        heatmap_norm = (heatmap_data - heatmap_data.min()) / (heatmap_data.max() - heatmap_data.min() + 1e-8)
        heatmap_uint8 = (heatmap_norm * 255).astype(np.uint8)
        
        # 应用颜色映射
        if colormap == 'jet':
            heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        elif colormap == 'hot':
            heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_HOT)
        elif colormap == 'cool':
            heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_COOL)
        else:
            heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        
        # 调整大小以匹配原图
        if heatmap_color.shape[:2] != image.shape[:2]:
            heatmap_color = cv2.resize(heatmap_color, (image.shape[1], image.shape[0]))
        
        # 半透明叠加
        weighted = cv2.addWeighted(image, 1 - alpha, heatmap_color, alpha, 0)
        
        return weighted
    
    def draw_measurements(
        self,
        image: np.ndarray,
        measurements: List[Measurement]
    ) -> np.ndarray:
        """
        绘制测量标注
        
        Args:
            image: 原始图像
            measurements: 测量列表
        
        Returns:
            np.ndarray: 带测量标注的图像
        """
        result = image.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        for meas in measurements:
            p1 = tuple(map(int, meas.start_point))
            p2 = tuple(map(int, meas.end_point))
            
            # 绘制测量线
            cv2.line(result, p1, p2, self.COLORS['yellow'], 2)
            
            # 绘制端点标记
            cv2.circle(result, p1, 5, self.COLORS['cyan'], -1)
            cv2.circle(result, p2, 5, self.COLORS['cyan'], -1)
            
            # 添加文字标注
            label = f"{meas.label}: {meas.value}{meas.unit}"
            mid_point = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
            
            # 文字背景
            text_size = cv2.getTextSize(label, font, 0.6, 2)[0]
            bg_p1 = (mid_point[0] - 5, mid_point[1] - text_size[1] - 5)
            bg_p2 = (mid_point[0] + text_size[0] + 5, mid_point[1] + 5)
            cv2.rectangle(result, bg_p1, bg_p2, (0, 0, 0), -1)
            
            # 文字
            cv2.putText(
                result,
                label,
                (mid_point[0], mid_point[1] - 5),
                font,
                0.6,
                (255, 255, 255),
                2
            )
        
        return result
    
    def draw_ai_confidence(
        self,
        image: np.ndarray,
        confidence: float,
        threshold: float = 0.7
    ) -> np.ndarray:
        """
        绘制 AI 置信度指示器
        
        Args:
            image: 原始图像
            confidence: AI 置信度 (0-1)
            threshold: 低置信度阈值
        
        Returns:
            np.ndarray: 带置信度指示的图像
        """
        result = image.copy()
        
        # 根据置信度选择颜色
        if confidence >= 0.9:
            color = self.COLORS['green']
            status = "高置信度"
        elif confidence >= threshold:
            color = self.COLORS['yellow']
            status = "中等置信度"
        else:
            color = self.COLORS['red']
            status = "⚠️ 低置信度 - 建议人工复核"
        
        # 绘制置信度条背景
        bar_width = 200
        bar_height = 30
        bar_x, bar_y = 10, 10
        
        cv2.rectangle(
            result,
            (bar_x, bar_y),
            (bar_x + bar_width, bar_y + bar_height),
            (0, 0, 0),
            -1
        )
        
        # 绘制置信度填充
        fill_width = int(bar_width * confidence)
        cv2.rectangle(
            result,
            (bar_x + 2, bar_y + 2),
            (bar_x + fill_width, bar_y + bar_height - 2),
            color,
            -1
        )
        
        # 添加文字
        cv2.putText(
            result,
            f"AI 置信度：{confidence:.1%} {status}",
            (bar_x + 10, bar_y + bar_height + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        return result
    
    def draw_multimodal_overlay(
        self,
        image: np.ndarray,
        bbox: Dict,
        mask: np.ndarray = None,
        heatmap: np.ndarray = None,
        measurements: List[Measurement] = None,
        birads_category: str = None,
        ai_confidence: float = None
    ) -> np.ndarray:
        """
        多模态叠加标注 (综合所有可视化增强)
        
        Args:
            image: 原始图像
            bbox: 病灶边界框
            mask: 分割掩码
            heatmap: AI 注意力热图
            measurements: 测量标注
            birads_category: BI-RADS 分级
            ai_confidence: AI 置信度
        
        Returns:
            np.ndarray: 综合标注图像
        """
        result = image.copy()
        
        # 1. 叠加 AI 热图
        if heatmap is not None:
            result = self.draw_heatmap(result, heatmap, alpha=0.5)
        
        # 2. 叠加分割掩码
        if mask is not None:
            result = self.draw_segmentation_mask(result, mask, alpha=0.4)
        
        # 3. 绘制边界框 (根据 BI-RADS 分级着色)
        if bbox:
            color = self.BIRADS_COLORS.get(birads_category, self.COLORS['red']) if birads_category else self.COLORS['red']
            label = f"BI-RADS {birads_category}" if birads_category else "病灶"
            result = self.draw_bounding_box(result, bbox, label=label, color=color)
        
        # 4. 添加测量标注
        if measurements:
            result = self.draw_measurements(result, measurements)
        
        # 5. 添加 AI 置信度指示
        if ai_confidence is not None:
            result = self.draw_ai_confidence(result, ai_confidence)
        
        # 6. 添加图例
        result = self._draw_legend(result, birads_category, ai_confidence)
        
        return result
    
    def _draw_legend(
        self,
        image: np.ndarray,
        birads_category: str = None,
        ai_confidence: float = None
    ) -> np.ndarray:
        """绘制图例说明"""
        result = image.copy()
        
        # 图例位置 (右下角)
        legend_x = image.shape[1] - 250
        legend_y = image.shape[0] - 150
        
        # 图例背景
        cv2.rectangle(
            result,
            (legend_x, legend_y),
            (image.shape[1] - 10, image.shape[0] - 10),
            (0, 0, 0),
            -1
        )
        cv2.rectangle(
            result,
            (legend_x, legend_y),
            (image.shape[1] - 10, image.shape[0] - 10),
            (255, 255, 255),
            2
        )
        
        # 图例内容
        font = cv2.FONT_HERSHEY_SIMPLEX
        y_offset = legend_y + 30
        
        if birads_category:
            cv2.putText(
                result,
                f"BI-RADS: {birads_category} 类",
                (legend_x + 10, y_offset),
                font,
                0.6,
                self.COLORS['white'],
                2
            )
            y_offset += 30
        
        if ai_confidence is not None:
            cv2.putText(
                result,
                f"AI 置信度：{ai_confidence:.1%}",
                (legend_x + 10, y_offset),
                font,
                0.6,
                self.COLORS['white'],
                2
            )
            y_offset += 30
        
        cv2.putText(
            result,
            "黄色：测量线",
            (legend_x + 10, y_offset),
            font,
            0.6,
            self.COLORS['yellow'],
            2
        )
        y_offset += 30
        
        cv2.putText(
            result,
            "红色半透明：AI 注意力区域",
            (legend_x + 10, y_offset),
            font,
            0.6,
            self.COLORS['red'],
            2
        )
        
        return result
    
    def generate_comparison_view(
        self,
        images: List[np.ndarray],
        titles: List[str],
        alignment: str = 'horizontal'
    ) -> np.ndarray:
        """
        生成对比图 (用于历史检查对比)
        
        Args:
            images: 图像列表
            titles: 标题列表
            alignment: 排列方式 (horizontal/vertical)
        
        Returns:
            np.ndarray: 拼接后的对比图
        """
        if len(images) != len(titles):
            raise ValueError("图像数量和标题数量不匹配")
        
        # 统一图像尺寸
        max_height = max(img.shape[0] for img in images)
        max_width = max(img.shape[1] for img in images)
        
        resized_images = []
        for img in images:
            if img.shape[0] != max_height or img.shape[1] != max_width:
                img_resized = cv2.resize(img, (max_width, max_height))
                resized_images.append(img_resized)
            else:
                resized_images.append(img)
        
        if alignment == 'horizontal':
            # 水平拼接
            result = np.hstack(resized_images)
            
            # 添加标题栏
            title_height = 50
            full_result = np.zeros((max_height + title_height, max_width * len(images), 3), dtype=np.uint8)
            full_result[:title_height, :] = (50, 50, 50)
            full_result[title_height:, :] = result
            
            for i, title in enumerate(titles):
                cv2.putText(
                    full_result,
                    title,
                    (i * max_width + 20, title_height - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )
        else:
            # 垂直拼接
            result = np.vstack(resized_images)
            full_result = result
        
        return full_result
    
    def save_annotated_image(
        self,
        image: np.ndarray,
        output_path: str,
        format: str = 'jpeg',
        quality: int = 95
    ):
        """
        保存标注后的图像
        
        Args:
            image: 标注后的图像
            output_path: 输出路径
            format: 图像格式 (jpeg/png)
            quality: JPEG 质量 (1-100)
        """
        # 转 BGR (OpenCV 保存需要)
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # 保存
        if format.lower() == 'jpeg' or format.lower() == 'jpg':
            cv2.imwrite(output_path, image_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
        else:
            cv2.imwrite(output_path, image_bgr, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    
    def to_base64(self, image: np.ndarray, format: str = 'jpeg') -> str:
        """
        将图像转换为 base64 编码 (用于前端展示)
        
        Args:
            image: 图像数组
            format: 图像格式
        
        Returns:
            str: base64 编码字符串 (data:image/jpeg;base64,...)
        """
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode(f'.{format}', image_bgr)
        encoded = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/{format};base64,{encoded}"
