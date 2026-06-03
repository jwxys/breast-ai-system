"""
数据集管理服务

支持:
- 数据标注管理
- 数据集划分
- 数据增强
- 质量检查
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class Annotation:
    """标注数据结构"""
    image_id: str
    birads_category: str
    lesion_bbox: Optional[List[float]]  # [x1, y1, x2, y2]
    lesion_mask_path: Optional[str]
    annotator_id: int
    annotated_at: datetime
    reviewed: bool
    reviewer_id: Optional[int]


class DatasetManager:
    """
    数据集管理器
    
    功能:
    1. 数据导入导出
    2. 标注管理
    3. 数据集划分
    4. 质量控制
    """
    
    def __init__(self, dataset_root: str):
        """
        初始化
        
        Args:
            dataset_root: 数据集根目录
        """
        self.dataset_root = Path(dataset_root)
        self.annotations: Dict[str, Annotation] = {}
    
    def load_annotations(self, annotation_file: str):
        """加载标注文件"""
        with open(annotation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data:
            self.annotations[item['image_id']] = Annotation(
                image_id=item['image_id'],
                birads_category=item['birads_category'],
                lesion_bbox=item.get('bbox'),
                lesion_mask_path=item.get('mask_path'),
                annotator_id=item['annotator_id'],
                annotated_at=datetime.fromisoformat(item['annotated_at']),
                reviewed=item.get('reviewed', False),
                reviewer_id=item.get('reviewer_id')
            )
    
    def split_dataset(
        self,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        stratify_by: str = 'birads'
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        数据集划分
        
        Args:
            train_ratio: 训练集比例
            val_ratio: 验证集比例
            test_ratio: 测试集比例
            stratify_by: 分层依据 (birads/annotator)
        
        Returns:
            Tuple: (训练集 IDs, 验证集 IDs, 测试集 IDs)
        """
        from sklearn.model_selection import train_test_split
        
        image_ids = list(self.annotations.keys())
        labels = [self.annotations[iid].birads_category for iid in image_ids]
        
        # 第一次划分：训练集 vs 临时集
        train_ids, temp_ids, train_labels, temp_labels = train_test_split(
            image_ids, labels,
            test_size=(1 - train_ratio),
            stratify=labels,
            random_state=42
        )
        
        # 第二次划分：验证集 vs 测试集
        val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
        val_ids, test_ids, _, _ = train_test_split(
            temp_ids, temp_labels,
            test_size=(1 - val_ratio_adjusted),
            stratify=temp_labels,
            random_state=42
        )
        
        return list(train_ids), list(val_ids), list(test_ids)
    
    def quality_check(self) -> Dict:
        """
        数据质量检查
        
        Returns:
            Dict: 质量报告
        """
        total = len(self.annotations)
        reviewed = sum(1 for a in self.annotations.values() if a.reviewed)
        with_bbox = sum(1 for a in self.annotations.values() if a.lesion_bbox is not None)
        with_mask = sum(1 for a in self.annotations.values() if a.lesion_mask_path is not None)
        
        # BI-RADS 分布
        birads_dist = {}
        for ann in self.annotations.values():
            birads = ann.birads_category
            birads_dist[birads] = birads_dist.get(birads, 0) + 1
        
        return {
            "total_images": total,
            "reviewed_count": reviewed,
            "review_rate": reviewed / total if total > 0 else 0,
            "with_bbox_count": with_bbox,
            "bbox_rate": with_bbox / total if total > 0 else 0,
            "with_mask_count": with_mask,
            "mask_rate": with_mask / total if total > 0 else 0,
            "birads_distribution": birads_dist,
            "completeness_score": self._calculate_completeness()
        }
    
    def _calculate_completeness(self) -> float:
        """计算数据完整度评分"""
        scores = []
        for ann in self.annotations.values():
            score = 0
            if ann.birads_category: score += 0.4
            if ann.lesion_bbox: score += 0.3
            if ann.lesion_mask_path: score += 0.3
            scores.append(score)
        return np.mean(scores) if scores else 0
    
    def export_dataset(
        self,
        output_dir: str,
        format: str = 'coco'
    ):
        """
        导出数据集
        
        Args:
            output_dir: 输出目录
            format: 导出格式 (coco/voc/yolo)
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if format == 'coco':
            self._export_coco(output_path)
        elif format == 'voc':
            self._export_voc(output_path)
        elif format == 'yolo':
            self._export_yolo(output_path)
    
    def _export_coco(self, output_path: Path):
        """导出为 COCO 格式"""
        coco_format = {
            "info": {
                "description": "Breast Ultrasound Dataset",
                "version": "1.0",
                "date_created": datetime.utcnow().isoformat()
            },
            "images": [],
            "annotations": [],
            "categories": [
                {"id": 1, "name": "breast_lesion"}
            ]
        }
        
        for i, (image_id, ann) in enumerate(self.annotations.items()):
            # 图像信息
            coco_format["images"].append({
                "id": i + 1,
                "file_name": f"{image_id}.jpg",
                "birads_category": ann.birads_category
            })
            
            # 标注信息
            if ann.lesion_bbox:
                x1, y1, x2, y2 = ann.lesion_bbox
                width = x2 - x1
                height = y2 - y1
                
                coco_format["annotations"].append({
                    "id": len(coco_format["annotations"]) + 1,
                    "image_id": i + 1,
                    "category_id": 1,
                    "bbox": [x1, y1, width, height],
                    "area": width * height,
                    "iscrowd": 0
                })
        
        # 保存
        output_file = output_path / "annotations.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(coco_format, f, ensure_ascii=False, indent=2)
    
    def _export_voc(self, output_path: Path):
        """导出为 Pascal VOC 格式"""
        voc_path = output_path / "VOC"
        voc_path.mkdir(parents=True, exist_ok=True)
        
        for image_id, ann in self.annotations.items():
            if not ann.lesion_bbox:
                continue
            
            x1, y1, x2, y2 = ann.lesion_bbox
            
            xml_content = f"""<?xml version="1.0"?>
<annotation>
    <folder>breast_ultrasound</folder>
    <filename>{image_id}.jpg</filename>
    <source>
        <database>Breast Cancer Database</database>
    </source>
    <size>
        <width>512</width>
        <height>512</height>
    </size>
    <object>
        <name>lesion</name>
        <bndbox>
            <xmin>{x1}</xmin>
            <ymin>{y1}</ymin>
            <xmax>{x2}</xmax>
            <ymax>{y2}</ymax>
        </bndbox>
        <birads>{ann.birads_category}</birads>
    </object>
</annotation>
"""
            (voc_path / f"{image_id}.xml").write_text(xml_content, encoding='utf-8')
    
    def _export_yolo(self, output_path: Path):
        """导出为 YOLO 格式"""
        labels_path = output_path / "labels"
        labels_path.mkdir(parents=True, exist_ok=True)
        
        for image_id, ann in self.annotations.items():
            if not ann.lesion_bbox:
                continue
            
            x1, y1, x2, y2 = ann.lesion_bbox
            
            # 归一化到 0-1
            x_center = (x1 + x2) / 2 / 512
            y_center = (y1 + y2) / 2 / 512
            width = (x2 - x1) / 512
            height = (y2 - y1) / 512
            
            # YOLO 格式：class x_center y_center width height
            label_line = f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
            
            (labels_path / f"{image_id}.txt").write_text(label_line, encoding='utf-8')
