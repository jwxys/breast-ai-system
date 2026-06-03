"""
模型校准与不确定性量化

提高 AI 预测的可靠性和可解释性
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CalibrationMetrics:
    """校准指标"""
    ece: float  # Expected Calibration Error
    mce: float  # Maximum Calibration Error
    brier_score: float
    reliability_diagram: List[Dict]


class ModelCalibrator:
    """
    模型校准器
    
    功能:
    1. 计算校准误差 (ECE/MCE)
    2. 绘制可靠性曲线
    3. 温度缩放校准
    4. 不确定性量化
    """
    
    def __init__(self, n_bins: int = 10):
        """
        初始化校准器
        
        Args:
            n_bins: 概率分箱数
        """
        self.n_bins = n_bins
    
    def calculate_ece(
        self,
        predicted_probabilities: np.ndarray,
        true_labels: np.ndarray
    ) -> float:
        """
        计算期望校准误差 (Expected Calibration Error)
        
        Args:
            predicted_probabilities: 预测概率 (0-1)
            true_labels: 真实标签 (0/1)
        
        Returns:
            float: ECE 值 (0-1，越小越好)
        """
        bin_boundaries = np.linspace(0, 1, self.n_bins + 1)
        ece = 0.0
        
        for i in range(self.n_bins):
            # 找到在当前 bin 的样本
            in_bin = (predicted_probabilities > bin_boundaries[i]) & \
                     (predicted_probabilities <= bin_boundaries[i + 1])
            
            prop_in_bin = np.mean(in_bin)
            
            if prop_in_bin > 0:
                # 计算该 bin 的平均预测概率和准确率
                avg_confidence = np.mean(predicted_probabilities[in_bin])
                avg_accuracy = np.mean(true_labels[in_bin])
                
                # 累加加权误差
                ece += np.abs(avg_accuracy - avg_confidence) * prop_in_bin
        
        return float(ece)
    
    def calculate_mce(
        self,
        predicted_probabilities: np.ndarray,
        true_labels: np.ndarray
    ) -> float:
        """
        计算最大校准误差 (Maximum Calibration Error)
        
        Args:
            predicted_probabilities: 预测概率
            true_labels: 真实标签
        
        Returns:
            float: MCE 值
        """
        bin_boundaries = np.linspace(0, 1, self.n_bins + 1)
        mce = 0.0
        
        for i in range(self.n_bins):
            in_bin = (predicted_probabilities > bin_boundaries[i]) & \
                     (predicted_probabilities <= bin_boundaries[i + 1])
            
            if np.sum(in_bin) > 0:
                avg_confidence = np.mean(predicted_probabilities[in_bin])
                avg_accuracy = np.mean(true_labels[in_bin])
                error = np.abs(avg_accuracy - avg_confidence)
                mce = max(mce, error)
        
        return float(mce)
    
    def calculate_brier_score(
        self,
        predicted_probabilities: np.ndarray,
        true_labels: np.ndarray
    ) -> float:
        """
        计算 Brier Score
        
        Args:
            predicted_probabilities: 预测概率
            true_labels: 真实标签
        
        Returns:
            float: Brier Score (0-1，越小越好)
        """
        return float(np.mean((predicted_probabilities - true_labels) ** 2))
    
    def generate_reliability_diagram(
        self,
        predicted_probabilities: np.ndarray,
        true_labels: np.ndarray
    ) -> List[Dict]:
        """
        生成可靠性曲线数据
        
        Args:
            predicted_probabilities: 预测概率
            true_labels: 真实标签
        
        Returns:
            List[Dict]: 可靠性曲线数据点
        """
        bin_boundaries = np.linspace(0, 1, self.n_bins + 1)
        diagram_data = []
        
        for i in range(self.n_bins):
            in_bin = (predicted_probabilities > bin_boundaries[i]) & \
                     (predicted_probabilities <= bin_boundaries[i + 1])
            
            count = np.sum(in_bin)
            
            diagram_data.append({
                "bin_center": (bin_boundaries[i] + bin_boundaries[i + 1]) / 2,
                "avg_confidence": float(np.mean(predicted_probabilities[in_bin])) if count > 0 else 0,
                "avg_accuracy": float(np.mean(true_labels[in_bin])) if count > 0 else 0,
                "count": int(count),
                "bin_range": f"{bin_boundaries[i]:.1f}-{bin_boundaries[i+1]:.1f}"
            })
        
        return diagram_data
    
    def temperature_scaling(
        self,
        logits: np.ndarray,
        true_labels: np.ndarray
    ) -> float:
        """
        温度缩放校准
        
        Args:
            logits: 模型输出的 logit 值
            true_labels: 真实标签
        
        Returns:
            float: 最优温度参数
        """
        from scipy.optimize import minimize_scalar
        
        def nll_loss(T: float) -> float:
            """负对数似然损失"""
            scaled_logits = logits / T
            probs = 1 / (1 + np.exp(-scaled_logits))
            probs = np.clip(probs, 1e-10, 1 - 1e-10)
            return -np.mean(true_labels * np.log(probs) + (1 - true_labels) * np.log(1 - probs))
        
        # 优化温度参数
        result = minimize_scalar(nll_loss, bounds=(0.1, 10.0), method='bounded')
        return float(result.x)


class UncertaintyQuantifier:
    """
    不确定性量化器
    
    方法：
    1. Monte Carlo Dropout
    2. Deep Ensemble
    3. Evidential Deep Learning
    """
    
    def __init__(self, n_samples: int = 50):
        """
        初始化量化器
        
        Args:
            n_samples: MC Dropout 采样次数
        """
        self.n_samples = n_samples
    
    def monte_carlo_dropout(
        self,
        model,
        image: np.ndarray
    ) -> Tuple[float, float]:
        """
        Monte Carlo Dropout 不确定性估计
        
        Args:
            model: 启用了 Dropout 的模型
            image: 输入图像
        
        Returns:
            Tuple: (预测概率，不确定性)
        """
        # 多次前向传播 (测试时保持 Dropout)
        predictions = []
        for _ in range(self.n_samples):
            pred = model.predict(image, training=True)  # 保持 Dropout
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # 均值作为预测
        mean_pred = np.mean(predictions, axis=0)
        
        # 标准差作为不确定性
        uncertainty = np.std(predictions, axis=0)
        
        return float(mean_pred[0]), float(uncertainty[0])
    
    def deep_ensemble(
        self,
        models: List,
        image: np.ndarray
    ) -> Tuple[float, float, float]:
        """
        Deep Ensemble 不确定性估计
        
        Args:
            models: 多个模型列表
            image: 输入图像
        
        Returns:
            Tuple: (预测概率，aleatoric 不确定性，epistemic 不确定性)
        """
        predictions = []
        for model in models:
            pred = model.predict(image)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # 平均预测
        mean_pred = np.mean(predictions, axis=0)
        
        # 认知不确定性 (epistemic): 模型间差异
        epistemic = np.var(predictions, axis=0)
        
        # 偶然不确定性 (aleatoric): 模型内部差异的平均
        aleatoric = np.mean([model.predict_variance(image) for model in models])
        
        return float(mean_pred[0]), float(aleatoric), float(epistemic)
    
    def get_uncertainty_level(self, uncertainty: float) -> str:
        """
        判断不确定性等级
        
        Args:
            uncertainty: 不确定性值
        
        Returns:
            str: 不确定性等级
        """
        if uncertainty < 0.1:
            "low"  # 低不确定性，可信度高
        elif uncertainty < 0.2:
            return "medium"  # 中不确定
        else:
            return "high"  # 高不确定性，需谨慎
    
    def generate_explanation(
        self,
        prediction: float,
        uncertainty: float,
        key_features: List[str]
    ) -> Dict:
        """
        生成可解释性说明
        
        Args:
            prediction: 预测概率
            uncertainty: 不确定性
            key_features: 关键特征
        
        Returns:
            Dict: 解释说明
        """
        # 判断预测倾向
        if prediction > 0.7:
            risk_level = "高"
            birads_suggestion = "4B-5 类"
        elif prediction > 0.4:
            risk_level = "中"
            birads_suggestion = "4A-4B 类"
        else:
            risk_level = "低"
            birads_suggestion = "2-3 类"
        
        # 不确定性等级
        uncertainty_level = self.get_uncertainty_level(uncertainty)
        
        # 可信度评估
        if uncertainty_level == "low":
            confidence_msg = "AI 预测可信度高"
        elif uncertainty_level == "medium":
            confidence_msg = "AI 预测可信度中等，建议结合临床判断"
        else:
            confidence_msg = "AI 预测不确定性高，建议谨慎参考"
        
        return {
            "risk_level": risk_level,
            "birads_suggestion": birads_suggestion,
            "prediction_probability": f"{prediction:.1%}",
            "uncertainty": f"{uncertainty:.3f}",
            "uncertainty_level": uncertainty_level,
            "confidence_message": confidence_msg,
            "key_features": key_features,
            "recommendation": self._generate_recommendation(prediction, uncertainty_level)
        }
    
    def _generate_recommendation(self, prediction: float, uncertainty: str) -> str:
        """生成建议"""
        if uncertainty == "high":
            return "AI 预测不确定性高，建议：1) 补充更多影像切面 2) 请上级医师会诊"
        
        if prediction > 0.7:
            return "建议穿刺活检以明确诊断"
        elif prediction > 0.4:
            return "建议短期随访 (3-6 个月) 或穿刺活检"
        else:
            return "建议常规随访 (6-12 个月)"
