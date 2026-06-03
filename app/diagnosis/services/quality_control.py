"""
质控管理服务

提供 AI 置信度评估、低置信度预警、人工复核工作流
确保诊断质量和安全性
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import numpy as np


class ConfidenceLevel(str, Enum):
    """置信度等级"""
    HIGH = "high"           # 高置信度 (≥0.9)
    MEDIUM = "medium"       # 中等置信度 (0.7-0.9)
    LOW = "low"             # 低置信度 (<0.7)
    VERY_LOW = "very_low"   # 极低置信度 (<0.5)


class ReviewStatus(str, Enum):
    """复核状态"""
    PENDING = "pending"         # 待复核
    IN_REVIEW = "in_review"     # 复核中
    CONFIRMED = "confirmed"     # 已确认
    MODIFIED = "modified"       # 已修改
    REJECTED = "rejected"       # 已拒绝


@dataclass
class QualityMetrics:
    """质量评估指标"""
    overall_confidence: float           # 整体置信度
    feature_confidence: Dict[str, float]  # 各征象置信度
    consistency_score: float            # 内部一致性评分
    uncertainty_level: float            # 不确定性水平
    recommendation: str                 # 质控建议


@dataclass
class ReviewRecord:
    """人工复核记录"""
    review_id: str
    diagnosis_id: int
    reviewer_id: int
    original_ai_result: Dict
    modified_result: Dict
    review_status: ReviewStatus
    review_time: datetime
    review_comments: str = ""
    confidence_before: float = 0.0
    confidence_after: float = 0.0


class QualityControlManager:
    """
    质控管理器
    
    功能:
    1. AI 置信度评估
    2. 低置信度预警
    3. 人工复核工作流
    4. 质量指标统计
    5. 持续学习数据收集
    """
    
    # 置信度阈值配置
    CONFIDENCE_THRESHOLDS = {
        'high': 0.9,      # 高置信度阈值
        'medium': 0.7,    # 中等置信度阈值
        'low': 0.5,       # 低置信度阈值
    }
    
    # 必须复核的征象组合
    MANDATORY_REVIEW_FEATURES = {
        'taller_than_wide': "纵横比>1 (taller-than-wide)",
        'spiculated_margin': "毛刺状边缘",
        'microlobulated_margin': "微小分叶",
        'fine_calcification': "细小钙化",
        'posterior_shadowing': "后方回声衰减",
    }
    
    # 征象一致性规则
    CONSISTENCY_RULES = {
        # 规则：如果形状不规则，边缘通常也不清晰
        ('irregular_shape', 'indistinct_margin'): 0.8,
        # 规则：如果是囊性，后方通常增强
        ('anechoic', 'posterior_enhancement'): 0.9,
        # 规则：如果血流丰富，通常不是良性
        ('rich_vascularity', 'no_vascularity'): 0.1,
    }
    
    def __init__(self, auto_review_threshold: float = 0.7):
        """
        初始化质控管理器
        
        Args:
            auto_review_threshold: 自动触发复核的阈值
        """
        self.auto_review_threshold = auto_review_threshold
        self.review_records: List[ReviewRecord] = []
    
    def evaluate_confidence(
        self,
        ai_result: Dict,
        ultrasound_features: Dict
    ) -> QualityMetrics:
        """
        评估 AI 诊断质量
        
        Args:
            ai_result: AI 分析结果
            ultrasound_features: 超声征象
        
        Returns:
            QualityMetrics: 质量评估指标
        """
        # 1. 计算整体置信度
        overall_confidence = self._calculate_overall_confidence(ai_result)
        
        # 2. 评估各征象置信度
        feature_confidence = self._evaluate_feature_confidence(ultrasound_features)
        
        # 3. 检查内部一致性
        consistency_score = self._check_consistency(ultrasound_features)
        
        # 4. 计算不确定性水平
        uncertainty_level = 1.0 - overall_confidence
        
        # 5. 生成质控建议
        recommendation = self._generate_qc_recommendation(
            overall_confidence,
            consistency_score,
            ultrasound_features
        )
        
        return QualityMetrics(
            overall_confidence=overall_confidence,
            feature_confidence=feature_confidence,
            consistency_score=consistency_score,
            uncertainty_level=uncertainty_level,
            recommendation=recommendation
        )
    
    def _calculate_overall_confidence(self, ai_result: Dict) -> float:
        """
        计算整体置信度
        
        综合考虑:
        - AI 模型输出的置信度
        - 征象识别的清晰度
        - 图像质量评分
        """
        # 从 AI 结果提取置信度
        ai_confidence = ai_result.get('confidence', 0.8)
        
        # 检查是否存在矛盾征象
        has_contradiction = self._detect_contradictions(ai_result.get('features', {}))
        if has_contradiction:
            ai_confidence *= 0.85
        
        # 检查图像质量 (如果有)
        image_quality = ai_result.get('image_quality_score', 1.0)
        overall = ai_confidence * image_quality
        
        return min(max(overall, 0.0), 1.0)
    
    def _evaluate_feature_confidence(self, features: Dict) -> Dict[str, float]:
        """
        评估各征象的识别置信度
        
        基于:
        - 征象的显著性
        - 征象之间的相关性
        - 历史统计准确性
        """
        confidence_map = {}
        
        # 形状置信度
        if 'shape' in features:
            confidence_map['shape'] = 0.95  # 形状识别通常较准确
        
        # 边缘置信度 (较难识别)
        if 'margin_types' in features:
            confidence_map['margin'] = 0.75
        
        # 钙化置信度 (依赖图像分辨率)
        if 'calcification_present' in features:
            confidence_map['calcification'] = 0.70
        
        # 血流置信度 (依赖 CDFI 质量)
        if 'vascularity_grade' in features:
            confidence_map['vascularity'] = 0.80
        
        # 后方回声置信度
        if 'posterior_features' in features:
            confidence_map['posterior'] = 0.85
        
        return confidence_map
    
    def _check_consistency(self, features: Dict) -> float:
        """
        检查征象内部一致性
        
        检测是否存在矛盾的征象组合
        """
        if not features:
            return 1.0
        
        inconsistencies = []
        
        # 应用一致性规则
        for (feature1, feature2), expected_correlation in self.CONSISTENCY_RULES.items():
            has_feature1 = self._has_feature(features, feature1)
            has_feature2 = self._has_feature(features, feature2)
            
            if has_feature1 and has_feature2:
                # 两者都存在，检查是否合理
                if expected_correlation < 0.3:  # 本应负相关
                    inconsistencies.append(f"{feature1} 与 {feature2} 同时存在，可能矛盾")
            elif has_feature1 and not has_feature2:
                # 只有一个存在，检查期望
                if expected_correlation > 0.8:  # 本应正相关
                    inconsistencies.append(f"{feature1} 存在但缺少 {feature2}")
        
        # 根据不一致性数量计算一致性评分
        if inconsistencies:
            penalty = 0.15 * len(inconsistencies)
            return max(1.0 - penalty, 0.3)
        
        return 1.0
    
    def _has_feature(self, features: Dict, feature: str) -> bool:
        """检查是否具备某征象"""
        if feature in features:
            value = features[feature]
            # 处理列表类型
            if isinstance(value, list):
                return len(value) > 0
            # 处理布尔类型
            elif isinstance(value, bool):
                return value
            # 处理字符串类型
            elif isinstance(value, str):
                return value != "" and value.lower() != "none"
            # 处理数值类型
            elif isinstance(value, (int, float)):
                return value > 0
        return False
    
    def _detect_contradictions(self, features: Dict) -> bool:
        """检测征象矛盾"""
        # 例如：同时存在"无回声"和"丰富血流"
        if (features.get('echo_pattern') == 'anechoic' and 
            features.get('vascularity_grade') in ['grade_2', 'grade_3']):
            return True
        
        # 例如：同时存在"边界清晰"和"毛刺状"
        margin_types = features.get('margin_types', [])
        if 'circumscribed' in margin_types and 'spiculated' in margin_types:
            return True
        
        return False
    
    def _generate_qc_recommendation(
        self,
        confidence: float,
        consistency: float,
        features: Dict
    ) -> str:
        """生成质控建议"""
        recommendations = []
        
        # 低置信度预警
        if confidence < self.CONFIDENCE_THRESHOLDS['low']:
            recommendations.append("⚠️ AI 置信度低，强烈建议人工复核")
        elif confidence < self.CONFIDENCE_THRESHOLDS['medium']:
            recommendations.append("⚡ AI 置信度中等，建议人工复核确认")
        
        # 一致性差预警
        if consistency < 0.7:
            recommendations.append("⚠️ 征象间存在矛盾，请复核")
        
        # 关键征象提示
        for feature, desc in self.MANDATORY_REVIEW_FEATURES.items():
            if self._has_feature(features, feature):
                recommendations.append(f"🔍 检测到关键征象：{desc}，建议重点复核")
        
        if not recommendations:
            recommendations.append("✅ AI 诊断质量良好，可直接采纳")
        
        return "; ".join(recommendations)
    
    def should_trigger_review(self, quality_metrics: QualityMetrics) -> Tuple[bool, str]:
        """
        判断是否应触发人工复核
        
        Args:
            quality_metrics: 质量评估指标
        
        Returns:
            (bool, str): (是否触发复核，触发原因)
        """
        # 规则 1: 置信度低于阈值
        if quality_metrics.overall_confidence < self.auto_review_threshold:
            return True, f"AI 置信度 {quality_metrics.overall_confidence:.1%} 低于阈值 {self.auto_review_threshold:.0%}"
        
        # 规则 2: 存在关键征象
        for feature in self.MANDATORY_REVIEW_FEATURES:
            if quality_metrics.feature_confidence.get(feature, 0) > 0:
                return True, f"检测到关键恶性征象：{self.MANDATORY_REVIEW_FEATURES[feature]}"
        
        # 规则 3: 一致性差
        if quality_metrics.consistency_score < 0.6:
            return True, f"征象一致性评分 {quality_metrics.consistency_score:.2f} 过低"
        
        return False, ""
    
    def create_review_record(
        self,
        diagnosis_id: int,
        reviewer_id: int,
        original_result: Dict,
        modified_result: Optional[Dict] = None,
        comments: str = ""
    ) -> ReviewRecord:
        """
        创建复核记录
        
        Args:
            diagnosis_id: 诊断 ID
            reviewer_id: 复核医师 ID
            original_result: 原始 AI 结果
            modified_result: 修改后的结果
            comments: 复核意见
        
        Returns:
            ReviewRecord: 复核记录
        """
        review_id = f"REV{datetime.now().strftime('%Y%m%d%H%M%S')}_{diagnosis_id}"
        
        status = ReviewStatus.MODIFIED if modified_result else ReviewStatus.CONFIRMED
        
        record = ReviewRecord(
            review_id=review_id,
            diagnosis_id=diagnosis_id,
            reviewer_id=reviewer_id,
            original_ai_result=original_result,
            modified_result=modified_result or original_result,
            review_status=status,
            review_time=datetime.now(),
            review_comments=comments,
            confidence_before=original_result.get('confidence', 0.0),
            confidence_after=modified_result.get('confidence', 0.0) if modified_result else original_result.get('confidence', 0.0)
        )
        
        self.review_records.append(record)
        return record
    
    def get_learning_dataset(self) -> List[Dict]:
        """
        生成持续学习数据集
        
        收集所有复核记录，用于模型微调
        
        Returns:
            List[Dict]: 学习数据集
        """
        learning_data = []
        
        for record in self.review_records:
            if record.review_status in [ReviewStatus.MODIFIED, ReviewStatus.REJECTED]:
                # 只收集有修正的数据
                sample = {
                    'diagnosis_id': record.diagnosis_id,
                    'original_prediction': record.original_ai_result,
                    'corrected_prediction': record.modified_result,
                    'reviewer_id': record.reviewer_id,
                    'review_time': record.review_time.isoformat(),
                    'comments': record.review_comments,
                    'confidence_delta': record.confidence_after - record.confidence_before
                }
                learning_data.append(sample)
        
        return learning_data
    
    def export_training_data(self, output_path: str, format: str = 'json'):
        """
        导出训练数据
        
        Args:
            output_path: 输出文件路径
            format: 文件格式 (json/jsonl/csv)
        """
        import json
        
        learning_data = self.get_learning_dataset()
        
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(learning_data, f, ensure_ascii=False, indent=2)
        elif format == 'jsonl':
            with open(output_path, 'w', encoding='utf-8') as f:
                for sample in learning_data:
                    f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        elif format == 'csv':
            import csv
            if learning_data:
                keys = learning_data[0].keys()
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(learning_data)
    
    def get_quality_statistics(self) -> Dict:
        """
        获取质量统计信息
        
        Returns:
            Dict: 质量统计
        """
        if not self.review_records:
            return {
                'total_reviews': 0,
                'average_confidence': 0.0,
                'review_rate': 0.0,
                'modification_rate': 0.0,
                'average_confidence_delta': 0.0
            }
        
        total = len(self.review_records)
        confirmed = sum(1 for r in self.review_records if r.review_status == ReviewStatus.CONFIRMED)
        modified = sum(1 for r in self.review_records if r.review_status == ReviewStatus.MODIFIED)
        
        avg_confidence = np.mean([r.confidence_before for r in self.review_records])
        avg_delta = np.mean([r.confidence_after - r.confidence_before for r in self.review_records])
        
        return {
            'total_reviews': total,
            'confirmed_count': confirmed,
            'modified_count': modified,
            'average_confidence': avg_confidence,
            'review_rate': total / max(total, 1),  # 复核率
            'modification_rate': modified / max(total, 1),  # 修改率
            'average_confidence_delta': avg_delta,
            'quality_trend': 'improving' if avg_delta > 0 else 'declining' if avg_delta < 0 else 'stable'
        }


class ReviewWorkflow:
    """
    复核工作流管理
    
    工作流状态:
    待复核 → 复核中 → 已确认/已修改/已拒绝
    """
    
    def __init__(self, qc_manager: QualityControlManager):
        """
        初始化复核工作流
        
        Args:
            qc_manager: 质控管理器
        """
        self.qc_manager = qc_manager
        self.pending_reviews: Dict[int, ReviewRecord] = {}
    
    def submit_for_review(self, diagnosis_id: int, ai_result: Dict, reason: str):
        """
        提交诊断到复核队列
        
        Args:
            diagnosis_id: 诊断 ID
            ai_result: AI 分析结果
            reason: 复核原因
        """
        # 创建待复核记录
        record = ReviewRecord(
            review_id=f"PENDING_{diagnosis_id}",
            diagnosis_id=diagnosis_id,
            reviewer_id=0,  # 待分配
            original_ai_result=ai_result,
            modified_result=ai_result,
            review_status=ReviewStatus.PENDING,
            review_time=datetime.now(),
            review_comments=reason
        )
        
        self.pending_reviews[diagnosis_id] = record
        
        return {
            'status': 'pending',
            'diagnosis_id': diagnosis_id,
            'reason': reason,
            'message': '已提交到复核队列'
        }
    
    def assign_reviewer(self, diagnosis_id: int, reviewer_id: int) -> Dict:
        """
        分配复核医师
        
        Args:
            diagnosis_id: 诊断 ID
            reviewer_id: 医师 ID
        
        Returns:
            Dict: 分配结果
        """
        if diagnosis_id not in self.pending_reviews:
            return {'error': '诊断不在复核队列中'}
        
        record = self.pending_reviews[diagnosis_id]
        record.reviewer_id = reviewer_id
        record.review_status = ReviewStatus.IN_REVIEW
        
        return {
            'status': 'assigned',
            'diagnosis_id': diagnosis_id,
            'reviewer_id': reviewer_id
        }
    
    def complete_review(
        self,
        diagnosis_id: int,
        modified_result: Optional[Dict] = None,
        comments: str = ""
    ) -> Dict:
        """
        完成复核
        
        Args:
            diagnosis_id: 诊断 ID
            modified_result: 修改后的结果
            comments: 复核意见
        
        Returns:
            Dict: 复核结果
        """
        if diagnosis_id not in self.pending_reviews:
            return {'error': '诊断不在复核队列中'}
        
        record = self.pending_reviews.pop(diagnosis_id)
        
        # 创建正式复核记录
        final_record = self.qc_manager.create_review_record(
            diagnosis_id=diagnosis_id,
            reviewer_id=record.reviewer_id,
            original_result=record.original_ai_result,
            modified_result=modified_result,
            comments=comments
        )
        
        return {
            'status': 'completed',
            'review_id': final_record.review_id,
            'final_status': final_record.review_status.value
        }
    
    def get_pending_count(self) -> int:
        """获取待复核数量"""
        return len(self.pending_reviews)
    
    def get_my_pending_reviews(self, reviewer_id: int) -> List[int]:
        """获取指定医师的待复核列表"""
        return [
            diag_id for diag_id, record in self.pending_reviews.items()
            if record.reviewer_id == reviewer_id and record.review_status == ReviewStatus.PENDING
        ]
    
    def get_review_queue(self) -> List[Dict]:
        """获取复核队列摘要"""
        return [
            {
                'diagnosis_id': record.diagnosis_id,
                'reviewer_id': record.reviewer_id,
                'status': record.review_status.value,
                'reason': record.review_comments,
                'submitted_time': record.review_time.isoformat()
            }
            for record in self.pending_reviews.values()
        ]
