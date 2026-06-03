"""
影像 - 中医病机分析服务
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.ultrasound.models.ultrasound_model import UltrasoundExam
from app.imaging_tcm.models.imaging_tcm_model import ImagingTCMCorrelation
from app.services.imaging_tcm_engine import ImagingTCMRuleEngine, TCMAnalysisResult


class ImagingTCMService:
    """影像 - 中医病机分析服务"""
    
    def __init__(self):
        self.rule_engine = ImagingTCMRuleEngine()
    
    async def analyze_ultrasound(
        self,
        db: AsyncSession,
        ultrasound_id: int
    ) -> Optional[ImagingTCMCorrelation]:
        """
        对超声检查进行中医病机分析
        
        Args:
            db: 数据库会话
            ultrasound_id: 超声检查 ID
            
        Returns:
            ImagingTCMCorrelation: 分析结果记录
        """
        # 获取超声检查
        ultrasound = await self._get_ultrasound(db, ultrasound_id)
        if not ultrasound:
            return None
        
        # 提取影像特征
        features = self._extract_features(ultrasound)
        
        # 执 行规则引擎分析
        analysis_result = self.rule_engine.analyze(features)
        
        # 创建或更新分析记录
        correlation = await self._save_analysis(
            db=db,
            ultrasound=ultrasound,
            features=features,
            result=analysis_result
        )
        
        return correlation
    
    async def _get_ultrasound(self, db: AsyncSession, ultrasound_id: int) -> Optional[UltrasoundExam]:
        """获取超声检查记录"""
        result = await db.execute(
            select(UltrasoundExam).where(UltrasoundExam.id == ultrasound_id)
        )
        return result.scalar_one_or_none()
    
    def _extract_features(self, ultrasound: UltrasoundExam) -> Dict[str, Any]:
        """从超声检查提取影像特征"""
        # TODO: 实际应用中应从 AI 分析结果提取详细特征
        # 这里使用示例特征
        
        # 从 AI 分析结果中提取
        ai_score = float(ultrasound.ai_score) if ultrasound.ai_score else 0.0
        
        # 模拟特征提取（实际应从结构化报告或 AI 模型获取）
        features = {
            # 1. 形态学特征（需要从报告或 AI 模型获取）
            "boundary_type": None,  # clear/unclear/spiculated/angular
            "morphology": None,  # regular/irregular/crab-claw
            "aspect_ratio": None,  # 数值
            "edge_type": None,  # smooth/blurred/microlobulated/macrol obulated
            "capsule_status": None,  # intact/broken/absent
            
            # 2. 内部回声特征
            "echo_type": None,  # anechoic/hypoechoic/isoechogenic/hyperechoic
            "echo_homogeneity": None,  # homogeneous/heterogeneous
            "calcification_type": None,  # none/coarse/micro/cluster/arc
            "liquefaction": None,  # True/False
            
            # 3. 血流动力学特征
            "cdfi_grade": None,  # grade_0/grade_1/grade_2/grade_3
            "blood_flow_distribution": None,  # peripheral/penetrating/reticular
            "resistive_index": None,  # RI 值
            
            # 4. 弹性成像特征
            "elasticity_score": None,  # 1-5
            "strain_ratio": None,  # 硬度比
            
            # 5. 生长动力学特征
            "growth_rate": None,  # stable/slow/moderate/fast
            "lesion_size_cm": None,  # 最大径
            "multifocality": None,  # True/False
        }
        
        # 根据 AI score 模拟一些特征（仅用于演示）
        if ai_score > 0.8:
            features["boundary_type"] = "spiculated"
            features["morphology"] = "irregular"
            features["aspect_ratio"] = 1.5
            features["echo_type"] = "hypoechoic"
            features["echo_homogeneity"] = "heterogeneous"
            features["calcification_type"] = "micro"
            features["cdfi_grade"] = "grade_2"
            features["blood_flow_distribution"] = "penetrating"
            features["resistive_index"] = 0.78
            features["elasticity_score"] = 4
            features["growth_rate"] = "moderate"
            features["lesion_size_cm"] = 2.5
        
        return features
    
    async def _save_analysis(
        self,
        db: AsyncSession,
        ultrasound: UltrasoundExam,
        features: Dict,
        result: TCMAnalysisResult
    ) -> ImagingTCMCorrelation:
        """保存分析结果"""
        correlation = ImagingTCMCorrelation(
            ultrasound_id=ultrasound.id,
            patient_id=ultrasound.visit.patient_id if ultrasound.visit else None,
            
            # 影像特征
            boundary_type=features.get("boundary_type"),
            morphology=features.get("morphology"),
            aspect_ratio=features.get("aspect_ratio"),
            edge_type=features.get("edge_type"),
            capsule_status=features.get("capsule_status"),
            echo_type=features.get("echo_type"),
            echo_homogeneity=features.get("echo_homogeneity"),
            calcification_type=features.get("calcification_type"),
            liquefaction=features.get("liquefaction"),
            cdfi_grade=features.get("cdfi_grade"),
            blood_flow_distribution=features.get("blood_flow_distribution"),
            resistive_index=features.get("resistive_index"),
            elasticity_score=features.get("elasticity_score"),
            strain_ratio=features.get("strain_ratio"),
            growth_rate=features.get("growth_rate"),
            lesion_size_cm=features.get("lesion_size_cm"),
            multifocality=features.get("multifocality"),
            
            # 病机评分
            stasis_score=result.scores.get("stasis", 0.0),
            stasis_evidence=result.evidence.get("stasis"),
            phlegm_score=result.scores.get("phlegm", 0.0),
            phlegm_evidence=result.evidence.get("phlegm"),
            toxin_score=result.scores.get("toxin", 0.0),
            toxin_evidence=result.evidence.get("toxin"),
            deficiency_score=result.scores.get("deficiency", 0.0),
            deficiency_evidence=result.evidence.get("deficiency"),
            
            # 综合判断
            primary_pathomechanism=result.primary,
            secondary_pathomechanism=", ".join(result.secondary) if result.secondary else None,
            pattern_combination=result.pattern,
            nature=result.nature,
            
            # 证据等级
            overall_evidence_level=result.evidence_level,
            confidence=result.confidence,
            
            # 治疗建议
            recommended_therapy=result.recommended_therapy,
            recommended_formula=result.recommended_formula,
            
            # 版本信息
            analysis_version=self.rule_engine.VERSION,
            rule_engine_version=self.rule_engine.VERSION,
        )
        
        db.add(correlation)
        await db.commit()
        await db.refresh(correlation)
        
        return correlation
    
    def interpret_score(self, score: float) -> str:
        """解读评分"""
        if score < 0.3:
            return "轻度/无提示"
        elif score < 0.5:
            return "中度倾向"
        elif score < 0.7:
            return "明显倾向"
        else:
            return "显著倾向"
