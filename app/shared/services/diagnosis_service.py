"""
诊断服务层 - 综合诊断决策

集成 BI-RADS 智能分级、分子分型预测、AI 影像分析
提供完整的乳腺病灶诊断决策支持
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx

from app.diagnosis.models.diagnosis_model import Diagnosis
from app.diagnosis.models.lesion_model import Lesion
from app.diagnosis.schemas.diagnosis_schema import DiagnosisCreate, DiagnosisUpdate
from app.diagnosis.services.birads_engine import BIRADSEngine, BIRADSCategory
from app.diagnosis.services.molecular_subtype_predictor import MolecularSubtypePredictor
from app.diagnosis.services.ai_diagnosis_service import AIDiagnosisService
from app.core.config import settings


class DiagnosisService:
    """
    综合诊断服务
    
    功能:
    1. BI-RADS 智能分级
    2. 分子分型预测
    3. AI 影像分析
    4. 治疗建议生成
    5. 预后评估
    """
    
    def __init__(self, db: AsyncSession):
        """
        初始化诊断服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.ai_service_url = settings.AI_SERVICE_URL
        
        # 初始化 AI 诊断服务
        if settings.KIMI_API_KEY:
            self.ai_diagnoser = AIDiagnosisService(
                api_key=settings.KIMI_API_KEY,
                model_name="kimi-vision"
            )
        elif settings.TONGYI_API_KEY:
            self.ai_diagnoser = AIDiagnosisService(
                api_key=settings.TONGYI_API_KEY,
                model_name="tongyi-vision"
            )
        else:
            self.ai_diagnoser = None
    
    async def create(self, data: DiagnosisCreate) -> Diagnosis:
        """创建诊断记录"""
        diagnosis = Diagnosis(**data.model_dump())
        
        self.db.add(diagnosis)
        await self.db.commit()
        await self.db.refresh(diagnosis)
        
        return diagnosis
    
    async def get_by_lesion(self, lesion_id: int) -> Optional[Diagnosis]:
        """根据病灶获取诊断"""
        result = await self.db.execute(
            select(Diagnosis).where(Diagnosis.lesion_id == lesion_id)
        )
        return result.scalar_one_or_none()
    
    async def update(self, diagnosis_id: int, data: DiagnosisUpdate) -> Diagnosis:
        """更新诊断"""
        result = await self.db.execute(
            select(Diagnosis).where(Diagnosis.id == diagnosis_id)
        )
        diagnosis = result.scalar_one_or_none()
        
        if not diagnosis:
            raise ValueError(f"Diagnosis {diagnosis_id} not found")
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(diagnosis, key, value)
        
        await self.db.commit()
        await self.db.refresh(diagnosis)
        
        return diagnosis
    
    async def comprehensive_assessment(self, lesion: Lesion) -> Dict[str, Any]:
        """
        综合诊断评估
        
        整合多项分析:
        1. BI-RADS 智能分级
        2. 恶性风险评估
        3. 分子分型预测 (如有病理数据)
        4. 治疗建议生成
        
        Args:
            lesion: 病灶对象
        
        Returns:
            Dict: 综合评估结果
        """
        result = {
            "lesion_id": lesion.id,
            "lesion_no": lesion.lesion_no,
            "assessment_time": datetime.utcnow().isoformat()
        }
        
        # 1. BI-RADS 智能分级
        birads_result = self.assess_birads(lesion)
        result["birads_assessment"] = birads_result
        
        # 2. 分子分型预测 (如有病理数据)
        if lesion.pathology_performed:
            subtype_result = self.predict_molecular_subtype(lesion)
            result["molecular_subtype"] = subtype_result
        
        # 3. 诊断结论
        result["conclusion"] = self.generate_conclusion(result)
        
        return result
    
    def assess_birads(self, lesion: Lesion) -> Dict[str, Any]:
        """
        BI-RADS 智能分级评估
        
        Args:
            lesion: 病灶对象
        
        Returns:
            Dict: BI-RADS 评估结果
        """
        # 构建超声征象字典
        ultrasound_features = {
            "shape": lesion.shape,
            "orientation": lesion.orientation,
            "margin_types": lesion.margin_types or [],
            "echo_pattern": lesion.echo_pattern,
            "echo_homogeneity": lesion.echo_homogeneity,
            "calcification_present": lesion.calcification_present,
            "calcification_types": lesion.calcification_types or [],
            "vascularity_grade": lesion.vascularity_grade,
            "vessel_pattern": lesion.vessel_pattern,
            "elastography": lesion.elasticity_score,
            "strain_ratio": float(lesion.strain_ratio) if lesion.strain_ratio else None,
            "posterior_features": lesion.posterior_features or []
        }
        
        # 调用 BI-RADS 引擎
        birads_result = BIRADSEngine.assess(ultrasound_features)
        
        return {
            "birads_category": birads_result.birads_category.value,
            "malignancy_risk": f"{birads_result.risk_percentage}%",
            "recommendation": birads_result.recommendation,
            "key_features": birads_result.key_features,
            "explanation": BIRADSEngine.get_birads_explanation(birads_result.birads_category)
        }
    
    def predict_molecular_subtype(self, lesion: Lesion) -> Dict[str, Any]:
        """
        分子分型预测
        
        Args:
            lesion: 病灶对象 (需有病理数据)
        
        Returns:
            Dict: 分子分型预测结果
        """
        if not lesion.er_status or not lesion.her2_status:
            return {"error": "病理数据不完整，无法预测分子分型"}
        
        # 转换 ER 状态为布尔值
        er_positive = lesion.er_status in ["阳性", "+", "++", "+++"]
        
        # 估算 PR 百分比 (实际应从数据库获取)
        pr_percentage = 50.0 if lesion.pr_status in ["阳性", "+", "++", "+++"] else 5.0
        
        # 转换 HER2 状态
        her2_map = {"0": 0, "1+": 1, "2+": 2, "3+": 3}
        her2_numeric = her2_map.get(lesion.her2_status, 0)
        
        # Ki-67 指数
        ki67 = float(lesion.ki67_value) if lesion.ki67_value else 20.0
        
        # 调用预测器
        prediction = MolecularSubtypePredictor.predict(
            er_status=er_positive,
            pr_percentage=pr_percentage,
            her2_status=her2_numeric,
            ki67_percentage=ki67,
            grade=lesion.pathology_grade
        )
        
        return {
            "subtype": prediction.subtype.value,
            "confidence": f"{prediction.confidence:.1%}",
            "er_status": prediction.er_status,
            "pr_status": prediction.pr_status,
            "her2_status": prediction.her2_status,
            "ki67_value": f"{prediction.ki67_value}%",
            "treatment_plan": prediction.treatment_plan,
            "description": MolecularSubtypePredictor.get_subtype_description(prediction.subtype)
        }
    
    async def ai_assisted_diagnosis(
        self,
        lesion: Lesion,
        image_urls: List[str],
        patient_info: Dict
    ) -> Dict[str, Any]:
        """
        AI 辅助诊断
        
        Args:
            lesion: 病灶对象
            image_urls: 超声图像 URLs
            patient_info: 患者临床信息
        
        Returns:
            Dict: AI 诊断结果
        """
        if not self.ai_diagnoser:
            return {"error": "AI 服务未配置，请设置 KIMI_API_KEY 或 TONGYI_API_KEY"}
        
        try:
            # 调用 AI 分析
            ai_result = await self.ai_diagnoser.analyze_ultrasound(
                image_urls=image_urls,
                patient_info=patient_info
            )
            
            # 整合结果
            return {
                "ai_detected": ai_result.detected,
                "ai_birads_prediction": ai_result.birads_prediction,
                "ai_malignancy_probability": f"{ai_result.malignancy_probability:.1%}",
                "ai_confidence": f"{ai_result.confidence:.1%}",
                "ai_features": ai_result.features,
                "ai_differential_diagnosis": ai_result.differential_diagnosis,
                "ai_highlighted_regions": ai_result.highlighted_regions
            }
            
        except Exception as e:
            return {"error": f"AI 分析失败：{str(e)}"}
    
    def generate_conclusion(self, assessment_result: Dict) -> str:
        """
        生成诊断结论
        
        Args:
            assessment_result: 综合评估结果
        
        Returns:
            str: 诊断结论
        """
        birads = assessment_result.get("birads_assessment", {})
        birads_cat = birads.get("birads_category", "0")
        
        conclusion_parts = [
            f"病灶编号：{assessment_result['lesion_no']}",
            f"BI-RADS 分级：{birads_cat} 类",
            f"恶性风险：{birads.get('malignancy_risk', '未知')}"
        ]
        
        # 如有分子分型，添加
        if "molecular_subtype" in assessment_result:
            subtype = assessment_result["molecular_subtype"]
            if "subtype" in subtype:
                conclusion_parts.append(f"分子分型：{subtype['subtype']}")
        
        # 添加处理建议
        conclusion_parts.append(f"处理建议：{birads.get('recommendation', '进一步评估')}")
        
        return " | ".join(conclusion_parts)
    
    async def predict_molecular_subtype(
        self, 
        lesion_id: int, 
        radiomics_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        基于影像组学的分子分型预测
        
        Args:
            lesion_id: 病灶 ID
            radiomics_features: 影像组学特征
        
        Returns:
            Dict: 预测结果
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ai_service_url}/api/v1/molecular-subtype",
                json={"radiomics_features": radiomics_features},
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception("分子分型预测失败")
            
            return response.json()
