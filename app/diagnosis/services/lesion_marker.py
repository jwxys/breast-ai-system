"""
病灶标记与定位服务

提供:
1. ROI 区域标记
2. 病灶定位 (象限/钟点)
3. 病灶 - 皮肤/胸肌距离测量
4. 多病灶空间关系
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class BreastQuadrant(str, Enum):
    """乳腺象限"""
    UOQ = "UOQ"  # 外上象限
    UIQ = "UIQ"  # 内上象限
    LOQ = "LOQ"  # 外下象限
    LIQ = "LIQ"  # 内下象限
    CENTRAL = "CENTRAL"  # 乳晕下中央


class ClockPosition(str, Enum):
    """钟点位置"""
    CLOCK_12 = "12 点"
    CLOCK_1 = "1 点"
    CLOCK_2 = "2 点"
    CLOCK_3 = "3 点"
    CLOCK_4 = "4 点"
    CLOCK_5 = "5 点"
    CLOCK_6 = "6 点"
    CLOCK_7 = "7 点"
    CLOCK_8 = "8 点"
    CLOCK_9 = "9 点"
    CLOCK_10 = "10 点"
    CLOCK_11 = "11 点"


@dataclass
class ROIMarkup:
    """ROI 标记数据"""
    lesion_id: str
    bounding_box: Dict[str, float]  # {x, y, width, height}
    centroid: Dict[str, float]  # {x, y}
    area_mm2: float
    perimeter_mm: float
    confidence: float


@dataclass
class LesionLocation:
    """病灶定位信息"""
    quadrant: BreastQuadrant  # 象限
    clock_position: ClockPosition  # 钟点
    distance_from_nipple_mm: float  # 距乳头距离
    depth_from_skin_mm: float  # 距皮肤深度
    distance_from_pectoral_mm: Optional[float]  # 距胸肌距离
    laterality: str  # L/R 左/右


@dataclass
class SpatialRelationship:
    """病灶与周围组织关系"""
    skin_involvement: bool  # 皮肤侵犯
    skin_distance_mm: Optional[float]  # 距皮肤距离
    pectoralis_involvement: bool  # 胸肌侵犯
    pectoralis_distance_mm: Optional[float]  # 距胸肌距离
    nipple_involvement: bool  # 乳头侵犯
    chest_wall_involvement: bool  # 胸壁侵犯


class LesionMarker:
    """
    病灶标记器
    
    处理超声图像中的病灶标记、定位和空间关系分析
    """
    
    # 乳腺象限角度范围 (以乳头为中心)
    QUADRANT_ANGLES = {
        BreastQuadrant.UOQ: (45, 135),    # 外上：45-135 度
        BreastQuadrant.UIQ: (135, 225),   # 内上：135-225 度
        BreastQuadrant.LIQ: (225, 315),   # 内下：225-315 度
        BreastQuadrant.LOQ: (315, 45),    # 外下：315-45 度 (跨越 0 度)
    }
    
    # 左右侧象限映射
    LATERALITY_MAP = {
        "L": {  # 左侧
            BreastQuadrant.UOQ: BreastQuadrant.UIQ,
            BreastQuadrant.UIQ: BreastQuadrant.UOQ,
            BreastQuadrant.LOQ: BreastQuadrant.LIQ,
            BreastQuadrant.LIQ: BreastQuadrant.LOQ,
        },
        "R": {  # 右侧
            BreastQuadrant.UOQ: BreastQuadrant.UOQ,
            BreastQuadrant.UIQ: BreastQuadrant.UIQ,
            BreastQuadrant.LOQ: BreastQuadrant.LOQ,
            BreastQuadrant.LIQ: BreastQuadrant.LIQ,
        }
    }
    
    @classmethod
    def create_roi_markup(
        cls,
        bounding_box: Dict[str, float],
        pixel_spacing: float = 0.1  # mm/pixel
    ) -> ROIMarkup:
        """
        创建 ROI 标记
        
        Args:
            bounding_box: 边界框 {x, y, width, height}
            pixel_spacing: 像素间距 (mm/pixel)
        
        Returns:
            ROIMarkup: ROI 标记数据
        """
        x = bounding_box.get("x", 0)
        y = bounding_box.get("y", 0)
        width = bounding_box.get("width", 0)
        height = bounding_box.get("height", 0)
        
        # 计算质心
        centroid_x = x + width / 2
        centroid_y = y + height / 2
        
        # 计算面积和周长 (mm², mm)
        area_mm2 = width * height * (pixel_spacing ** 2)
        perimeter_mm = 2 * (width + height) * pixel_spacing
        
        # 估算置信度 (基于形状规则度)
        aspect_ratio = width / height if height > 0 else 1
        shape_regularity = 1 - abs(1 - aspect_ratio)
        confidence = min(0.95, shape_regularity * 0.8 + 0.15)
        
        return ROIMarkup(
            lesion_id=f"lesion_{int(x)}_{int(y)}",
            bounding_box=bounding_box,
            centroid={"x": centroid_x, "y": centroid_y},
            area_mm2=round(area_mm2, 2),
            perimeter_mm=round(perimeter_mm, 2),
            confidence=round(confidence, 3)
        )
    
    @classmethod
    def determine_location(
        cls,
        centroid: Dict[str, float],
        image_dimensions: Dict[str, int],
        nipple_position: Optional[Dict[str, float]] = None,
        skin_line: Optional[List[Dict[str, float]]] = None,
        pectoralis_line: Optional[List[Dict[str, float]]] = None,
        laterality: str = "R"
    ) -> LesionLocation:
        """
        确定病灶位置
        
        Args:
            centroid: 病灶质心 {x, y}
            image_dimensions: 图像尺寸 {width, height}
            nipple_position: 乳头位置 {x, y}
            skin_line: 皮肤线坐标点列表
            pectoralis_line: 胸肌线坐标点列表
            laterality: 侧别 L/R
        
        Returns:
            LesionLocation: 病灶定位信息
        """
        img_w = image_dimensions.get("width", 100)
        img_h = image_dimensions.get("height", 100)
        cx = centroid.get("x", img_w / 2)
        cy = centroid.get("y", img_h / 2)
        
        # 1. 确定象限
        quadrant = cls._determine_quadrant(cx, cy, img_w, img_h, laterality)
        
        # 2. 确定钟点位置
        clock_position = cls._determine_clock_position(
            cx, cy, img_w, img_h, laterality, nipple_position
        )
        
        # 3. 计算距乳头距离
        if nipple_position:
            nipple_dist = math.sqrt(
                (cx - nipple_position["x"]) ** 2 + 
                (cy - nipple_position["y"]) ** 2
            )
        else:
            # 默认乳头在图像中央
            nipple_dist = math.sqrt((cx - img_w/2) ** 2 + (cy - img_h/2) ** 2)
        nipple_dist_mm = round(nipple_dist * 0.1, 1)  # 假设 0.1mm/pixel
        
        # 4. 计算距皮肤深度
        if skin_line:
            skin_dist = cls._point_to_line_distance(
                cx, cy, skin_line[0], skin_line[1]
            )
        else:
            # 默认皮肤线在图像顶部
            skin_dist = cy * 0.1
        skin_dist_mm = round(skin_dist, 1)
        
        # 5. 计算距胸肌距离
        pectoralis_dist_mm = None
        if pectoralis_line:
            pectoralis_dist = cls._point_to_line_distance(
                cx, cy, pectoralis_line[0], pectoralis_line[1]
            )
            pectoralis_dist_mm = round(pectoralis_dist * 0.1, 1)
        
        return LesionLocation(
            quadrant=quadrant,
            clock_position=clock_position,
            distance_from_nipple_mm=nipple_dist_mm,
            depth_from_skin_mm=skin_dist_mm,
            distance_from_pectoral_mm=pectoralis_dist_mm,
            laterality=laterality
        )
    
    @classmethod
    def analyze_spatial_relationship(
        cls,
        location: LesionLocation,
        skin_line: Optional[List[Dict[str, float]]] = None,
        pectoralis_line: Optional[List[Dict[str, float]]] = None
    ) -> SpatialRelationship:
        """
        分析病灶与周围组织关系
        
        Args:
            location: 病灶位置
            skin_line: 皮肤线
            pectoralis_line: 胸肌线
        
        Returns:
            SpatialRelationship: 空间关系
        """
        # 皮肤侵犯判断 (深度<5mm 或距皮肤<5mm)
        skin_involvement = location.depth_from_skin_mm < 5
        skin_distance = location.depth_from_skin_mm if not skin_involvement else None
        
        # 胸肌侵犯判断
        pectoralis_involvement = False
        pectoralis_distance = None
        if location.distance_from_pectoral_mm is not None:
            pectoralis_involvement = location.distance_from_pectoral_mm < 5
            if not pectoralis_involvement:
                pectoralis_distance = location.distance_from_pectoral_mm
        
        # 乳头侵犯 (距乳头<10mm)
        nipple_involvement = location.distance_from_nipple_mm < 10
        
        # 胸壁侵犯 (后缘与胸肌分界不清)
        chest_wall_involvement = pectoralis_involvement or (
            location.distance_from_pectoral_mm is not None and
            location.distance_from_pectoral_mm < 2
        )
        
        return SpatialRelationship(
            skin_involvement=skin_involvement,
            skin_distance_mm=skin_distance,
            pectoralis_involvement=pectoralis_involvement,
            pectoralis_distance_mm=pectoralis_distance,
            nipple_involvement=nipple_involvement,
            chest_wall_involvement=chest_wall_involvement
        )
    
    @classmethod
    def _determine_quadrant(
        cls, cx: float, cy: float, 
        img_w: float, img_h: float,
        laterality: str
    ) -> BreastQuadrant:
        """确定象限"""
        # 计算相对于图像中心的角度
        center_x = img_w / 2
        center_y = img_h / 2
        
        dx = cx - center_x
        dy = cy - center_y
        
        # 计算角度 (0-360 度)
        if dx == 0 and dy == 0:
            return BreastQuadrant.CENTRAL
        
        angle = math.degrees(math.atan2(dy, dx))
        angle = (angle + 360) % 360  # 转换为 0-360
        
        # 根据侧别映射象限
        if laterality == "L":
            # 左侧：角度需要镜像
            angle = (360 - angle) % 360
        
        # 确定象限
        for quadrant, (angle_min, angle_max) in cls.QUADRANT_ANGLES.items():
            if angle_min < angle_max:
                if angle_min <= angle <= angle_max:
                    return quadrant
            else:  # 跨越 0 度的情况 (LOQ)
                if angle >= angle_min or angle <= angle_max:
                    return quadrant
        
        return BreastQuadrant.CENTRAL
    
    @classmethod
    def _determine_clock_position(
        cls,
        cx: float, cy: float,
        img_w: float, img_h: float,
        laterality: str,
        nipple_position: Optional[Dict[str, float]] = None
    ) -> ClockPosition:
        """确定钟点位置"""
        if nipple_position:
            nx = nipple_position["x"]
            ny = nipple_position["y"]
        else:
            nx = img_w / 2
            ny = img_h / 2
        
        dx = cx - nx
        dy = cy - ny
        
        # 计算角度
        if dx == 0 and dy == 0:
            return ClockPosition.CLOCK_12
        
        angle = math.degrees(math.atan2(dy, dx))
        angle = (angle + 360) % 360
        
        # 调整角度以匹配钟点 (12 点在顶部)
        angle = (angle + 90) % 360
        
        # 左侧镜像
        if laterality == "L":
            angle = (360 - angle) % 360
        
        # 映射到钟点 (每 30 度一个钟点)
        clock_index = int((angle + 15) / 30) % 12
        
        clock_positions = [
            ClockPosition.CLOCK_12,
            ClockPosition.CLOCK_1,
            ClockPosition.CLOCK_2,
            ClockPosition.CLOCK_3,
            ClockPosition.CLOCK_4,
            ClockPosition.CLOCK_5,
            ClockPosition.CLOCK_6,
            ClockPosition.CLOCK_7,
            ClockPosition.CLOCK_8,
            ClockPosition.CLOCK_9,
            ClockPosition.CLOCK_10,
            ClockPosition.CLOCK_11,
        ]
        
        return clock_positions[clock_index]
    
    @classmethod
    def _point_to_line_distance(
        cls,
        px: float, py: float,
        line_p1: Dict[str, float],
        line_p2: Dict[str, float]
    ) -> float:
        """计算点到直线的距离"""
        x1, y1 = line_p1["x"], line_p1["y"]
        x2, y2 = line_p2["x"], line_p2["y"]
        
        # 点到直线距离公式
        numerator = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
        denominator = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
        
        if denominator == 0:
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
        
        return numerator / denominator
    
    @classmethod
    def calculate_multi_lesion_relationship(
        cls,
        lesions: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        计算多病灶空间关系
        
        Args:
            lesions: 病灶列表 [{id, centroid, size_mb}, ...]
        
        Returns:
            Dict: 多病灶关系信息
        """
        if len(lesions) < 2:
            return {"type": "single", "count": len(lesions)}
        
        # 计算病灶间距离
        distances = []
        for i in range(len(lesions)):
            for j in range(i + 1, len(lesions)):
                l1 = lesions[i]
                l2 = lesions[j]
                dist = math.sqrt(
                    (l1["centroid"]["x"] - l2["centroid"]["x"]) ** 2 +
                    (l1["centroid"]["y"] - l2["centroid"]["y"]) ** 2
                )
                distances.append({
                    "lesion_1": l1["id"],
                    "lesion_2": l2["id"],
                    "distance_mm": round(dist * 0.1, 1)
                })
        
        # 判断多灶性 vs 多中心性
        max_distance = max([d["distance_mm"] for d in distances])
        if max_distance <= 40:  # 同一象限内≤4cm
            type_name = "multifocal"  # 多灶性
        else:
            type_name = "multicentric"  # 多中心性
        
        return {
            "type": type_name,
            "count": len(lesions),
            "distances": distances,
            "max_distance_mm": max_distance,
            "clinical_significance": cls._get_multi_lesion_significance(type_name, max_distance)
        }
    
    @classmethod
    def _get_multi_lesion_significance(cls, type_name: str, max_dist: float) -> str:
        """获取多病灶临床意义"""
        if type_name == "multifocal":
            return "多灶性病变，同一象限内多个病灶，预后较好"
        else:
            return "多中心性病变，不同象限病灶，需全乳评估，可能影响手术方式"

