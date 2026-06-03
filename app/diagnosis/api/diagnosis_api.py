"""
诊断管理 API

提供完整的诊断决策功能:
- BI-RADS 智能评估
- 分子分型预测
- AI 影像分析
- 综合诊断报告
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict
from datetime import datetime

from app.core.database import get_db
from app.diagnosis.schemas.diagnosis_schema import (
    DiagnosisCreate,
    DiagnosisUpdate,
    DiagnosisResponse,
    DiagnosisListResponse,
    BIRADSAssessmentRequest,
    BIRADSAssessmentResponse,
    MolecularSubtypeRequest,
    MolecularSubtypeResponse,
    AIDiagnosisRequest,
    AIDiagnosisResponse,
    ComprehensiveAssessmentResponse,
    ConcordanceCheckRequest,
    ConcordanceCheckResponse,
    LesionMarkupRequest,
    LesionMarkupResponse,
    LNAssessmentRequest,
    LNAssessmentResponse,
    LesionTrackingRequest,
    GrowthAnalysisResponse,
    TreatmentResponseRequest,
    TreatmentResponseResponse,
)
from app.shared.services.diagnosis_service import DiagnosisService
from app.diagnosis.services.birads_engine import BIRADSEngine
from app.diagnosis.services.molecular_subtype_predictor import MolecularSubtypePredictor
from app.diagnosis.services.concordance_checker import ConcordanceChecker
from app.diagnosis.services.birads_visualization import BIRADSVisualization
from app.diagnosis.services.lesion_marker import LesionMarker
from app.diagnosis.services.lymph_node_assessment import LymphNodeAssessment
from app.diagnosis.services.lesion_tracker import LesionTracker


router = APIRouter(prefix="/api/v1/diagnosis", tags=["诊断管理"])


@router.post(
    "/",
    summary="创建诊断记录",
    description="基于超声征象和 AI 分析创建诊断记录",
    response_model=DiagnosisResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_diagnosis(
    request: DiagnosisCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建诊断记录
    
    支持以下场景：
    1. 手工创建诊断 (医师填写)
    2. AI 辅助诊断 (自动填充 AI 字段)
    3. BI-RADS 智能分级 (自动计算)
    
    示例：
    ```json
    {
        "patient_id": 1,
        "lesion_id": 1,
        "birads_category": "4B",
        "malignancy_risk": 0.30,
        "recommendation": "建议穿刺活检",
        "ai_assisted": true,
        "ai_birads_prediction": "4B",
        "ai_malignancy_probability": 0.35
    }
    ```
    """
    service = DiagnosisService(db)
    
    # 创建诊断
    from app.diagnosis.models.diagnosis_model import Diagnosis
    diagnosis = Diagnosis(
        report_no=f"D{datetime.now().strftime('%Y%m%d%H%M%S')}",
        **request.model_dump()
    )
    
    db.add(diagnosis)
    await db.commit()
    await db.refresh(diagnosis)
    
    return diagnosis


@router.get(
    "/",
    summary="获取诊断列表",
    description="分页查询诊断记录，支持多种筛选条件"
)
async def list_diagnoses(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    patient_id: Optional[int] = Query(None, description="患者 ID"),
    birads_category: Optional[str] = Query(None, description="BI-RADS 分级"),
    report_status: Optional[str] = Query(None, description="报告状态"),
    db: AsyncSession = Depends(get_db)
):
    """
    诊断列表查询
    
    支持筛选：
    - 患者 ID
    - BI-RADS 分级
    - 报告状态
    - 时间范围
    
    返回分页结果
    """
    from app.diagnosis.models.diagnosis_model import Diagnosis
    
    query = select(Diagnosis)
    
    # 应用筛选条件
    if patient_id:
        query = query.where(Diagnosis.patient_id == patient_id)
    if birads_category:
        query = query.where(Diagnosis.birads_category == birads_category)
    if report_status:
        query = query.where(Diagnosis.report_status == report_status)
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    diagnoses = result.scalars().all()
    
    # 总数
    count_query = select(func.count()).select_from(Diagnosis)
    if patient_id:
        count_query = count_query.where(Diagnosis.patient_id == patient_id)
    if birads_category:
        count_query = count_query.where(Diagnosis.birads_category == birads_category)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    return {
        "code": 200,
        "data": diagnoses,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get(
    "/{diagnosis_id}",
    summary="获取诊断详情",
    description="获取单条诊断的完整信息",
    response_model=DiagnosisResponse
)
async def get_diagnosis(
    diagnosis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    诊断详情
    
    包含：
    - 基本信息
    - BI-RADS 评估
    - AI 分析结果
    - 病理数据 (如有)
    - 分子分型 (如有)
    """
    from app.diagnosis.models.diagnosis_model import Diagnosis
    
    result = await db.execute(
        select(Diagnosis).where(Diagnosis.id == diagnosis_id)
    )
    diagnosis = result.scalar_one_or_none()
    
    if not diagnosis:
        raise HTTPException(
            status_code=404,
            detail=f"诊断记录 {diagnosis_id} 不存在"
        )
    
    return diagnosis


@router.post(
    "/assess-birads",
    summary="BI-RADS 智能评估",
    description="基于超声征象自动计算 BI-RADS 分级和恶性风险",
    response_model=BIRADSAssessmentResponse
)
async def assess_birads(request: BIRADSAssessmentRequest):
    """
    BI-RADS 智能评估
    
    输入超声征象，自动输出：
    - BI-RADS 分级 (0-6)
    - 恶性风险 (0-100%)
    - 处理建议
    - 关键征象说明
    - 分级详细解释 (可选)
    
    示例：
    ```json
    {
        "ultrasound_features": {
            "shape": "irregular",
            "orientation": "not_parallel",
            "margin_types": ["angular", "spiculated"],
            "echo_pattern": "hypoechoic",
            "vascularity_grade": "grade_2"
        },
        "include_explanation": true
    }
    ```
    """
    # 调用 BI-RADS 引擎
    features_dict = request.ultrasound_features.model_dump()
    clinical_factors = request.clinical_factors
    result = BIRADSEngine.assess(features_dict, clinical_factors)
    
    response = BIRADSAssessmentResponse(
        birads_category=result.birads_category.value,
        malignancy_risk=result.risk_percentage,
        recommendation=result.recommendation,
        key_features=result.key_features
    )
    
    if request.include_explanation:
        response.explanation = BIRADSEngine.get_birads_explanation(
            result.birads_category
        )
    
    return response


@router.post(
    "/predict-subtype",
    summary="分子分型预测",
    description="基于 IHC 标志物预测乳腺癌分子分型",
    response_model=MolecularSubtypeResponse
)
async def predict_molecular_subtype(request: MolecularSubtypeRequest):
    """
    分子分型预测
    
    基于 St. Gallen 共识，使用 IHC4 标志物：
    - ER (雌激素受体)
    - PR (孕激素受体)
    - HER2 (人表皮生长因子受体 2)
    - Ki-67 (增殖指数)
    
    输出 6 种分子分型及治疗建议
    
    示例：
    ```json
    {
        "er_status": true,
        "pr_percentage": 80,
        "her2_status": 0,
        "ki67_percentage": 10,
        "grade": "G1"
    }
    ```
    """
    prediction = MolecularSubtypePredictor.predict(
        er_status=request.er_status,
        pr_percentage=request.pr_percentage,
        her2_status=request.her2_status,
        ki67_percentage=request.ki67_percentage,
        grade=request.grade
    )
    
    return MolecularSubtypeResponse(
        subtype=prediction.subtype.value,
        confidence=prediction.confidence,
        er_status=prediction.er_status,
        pr_status=prediction.pr_status,
        her2_status=prediction.her2_status,
        ki67_value=prediction.ki67_value,
        treatment_plan=prediction.treatment_plan,
        description=MolecularSubtypePredictor.get_subtype_description(
            prediction.subtype
        )
    )


@router.post(
    "/ai-analyze",
    summary="AI 影像分析",
    description="调用视觉大模型分析超声图像",
    response_model=AIDiagnosisResponse
)
async def ai_analyze(
    request: AIDiagnosisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    AI 影像分析
    
    集成 Kimi/通义视觉大模型，实现：
    - 病灶自动检测
    - 特征提取 (形状/边缘/回声/钙化/血流)
    - BI-RADS 智能预测
    - 恶性概率评估
    - 鉴别诊断建议
    
    需要配置 API Key：
    - KIMI_API_KEY 或
    - TONGYI_API_KEY
    """
    service = DiagnosisService(db)
    
    # 获取患者信息
    from app.patient.models.patient_model import Patient
    patient_result = await db.execute(
        select(Patient).where(Patient.id == request.patient_id)
    )
    patient = patient_result.scalar_one_or_none()
    
    patient_info = request.patient_info or {}
    if patient:
        patient_info["age"] = patient.age
        patient_info["gender"] = patient.gender
    
    # 调用 AI 分析
    result = await service.ai_assisted_diagnosis(
        lesion_id=request.lesion_id,
        image_urls=request.image_urls,
        patient_info=patient_info
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=500,
            detail=result["error"]
        )
    
    return AIDiagnosisResponse(**result)


@router.post(
    "/{diagnosis_id}/comprehensive",
    summary="综合诊断评估",
    description="整合多项分析生成综合诊断报告",
    response_model=ComprehensiveAssessmentResponse
)
async def comprehensive_assessment(
    diagnosis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    综合诊断评估
    
    整合：
    1. BI-RADS 智能分级
    2. 分子分型预测 (如有病理数据)
    3. AI 影像分析 (如有图像)
    4. 治疗建议生成
    
    输出完整诊断报告
    """
    from app.diagnosis.models.diagnosis_model import Diagnosis
    from app.diagnosis.models.diagnosis_model import Lesion
    
    # 获取诊断和病灶
    diagnosis_result = await db.execute(
        select(Diagnosis).where(Diagnosis.id == diagnosis_id)
    )
    diagnosis = diagnosis_result.scalar_one_or_none()
    
    if not diagnosis:
        raise HTTPException(
            status_code=404,
            detail=f"诊断记录 {diagnosis_id} 不存在"
        )
    
    lesion_result = await db.execute(
        select(Lesion).where(Lesion.id == diagnosis.lesion_id)
    )
    lesion = lesion_result.scalar_one_or_none()
    
    if not lesion:
        raise HTTPException(
            status_code=404,
            detail=f"病灶 {diagnosis.lesion_id} 不存在"
        )
    
    # 调用综合服务
    service = DiagnosisService(db)
    result = await service.comprehensive_assessment(lesion)
    
    # 构建 BI-RADS 响应
    birads_assessment = BIRADSAssessmentResponse(
        birads_category=diagnosis.birads_category,
        malignancy_risk=float(diagnosis.malignancy_risk) if diagnosis.malignancy_risk else 0,
        recommendation=diagnosis.recommendation or "",
        key_features=diagnosis.birads_key_features or []
    )
    
    # 构建分子分型响应 (如有)
    molecular_subtype = None
    if diagnosis.molecular_subtype:
        molecular_subtype = MolecularSubtypeResponse(
            subtype=diagnosis.molecular_subtype,
            confidence=float(diagnosis.molecular_subtype_confidence) if diagnosis.molecular_subtype_confidence else 0.8,
            er_status=diagnosis.er_status or "",
            pr_status=diagnosis.pr_status or "",
            her2_status=diagnosis.her2_status or "",
            ki67_value=float(diagnosis.ki67_value) if diagnosis.ki67_value else 0,
            treatment_plan=diagnosis.treatment_recommendations
        )
    
    # 构建 AI 分析响应 (如有)
    ai_analysis = None
    if diagnosis.ai_assisted:
        ai_analysis = AIDiagnosisResponse(
            detected=True,
            birads_prediction=diagnosis.ai_birads_prediction or "",
            malignancy_probability=float(diagnosis.ai_malignancy_probability) if diagnosis.ai_malignancy_probability else 0,
            confidence=float(diagnosis.ai_confidence) if diagnosis.ai_confidence else 0,
            extracted_features=diagnosis.ai_extracted_features
        )
    
    return ComprehensiveAssessmentResponse(
        lesion_id=lesion.id,
        lesion_no=lesion.lesion_no,
        assessment_time=datetime.utcnow().isoformat(),
        birads_assessment=birads_assessment,
        molecular_subtype=molecular_subtype,
        ai_analysis=ai_analysis,
        conclusion=result["conclusion"],
        treatment_recommendations=diagnosis.treatment_recommendations
    )


@router.put(
    "/{diagnosis_id}",
    summary="更新诊断",
    description="更新诊断记录信息"
)
async def update_diagnosis(
    diagnosis_id: int,
    request: DiagnosisUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新诊断记录"""
    from app.diagnosis.models.diagnosis_model import Diagnosis
    
    result = await db.execute(
        select(Diagnosis).where(Diagnosis.id == diagnosis_id)
    )
    diagnosis = result.scalar_one_or_none()
    
    if not diagnosis:
        raise HTTPException(
            status_code=404,
            detail=f"诊断记录 {diagnosis_id} 不存在"
        )
    
    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(diagnosis, key, value)
    
    await db.commit()
    await db.refresh(diagnosis)
    
    return diagnosis


@router.delete(
    "/{diagnosis_id}",
    summary="删除诊断",
    description="删除诊断记录 (软删除)"
)
async def delete_diagnosis(
    diagnosis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除诊断记录"""
    from app.diagnosis.models.diagnosis_model import Diagnosis
    
    result = await db.execute(
        select(Diagnosis).where(Diagnosis.id == diagnosis_id)
    )
    diagnosis = result.scalar_one_or_none()
    
    if not diagnosis:
        raise HTTPException(
            status_code=404,
            detail=f"诊断记录 {diagnosis_id} 不存在"
        )
    
    await db.delete(diagnosis)
    await db.commit()
    
    return {"code": 200, "message": "删除成功"}


@router.post(
    "/predict-subtype-ultrasound",
    summary="超声无创分子分型预测",
    description="基于超声特征无创预测分子分型概率分布 (术前评估)",
)
async def predict_subtype_from_ultrasound(request: BIRADSAssessmentRequest):
    """
    超声无创分子分型预测
    
    使用 radiomics 特征与分子分型的关联模型
    适合术前无创评估，无需 IHC 结果
    
    输出：各分子分型的概率分布
    """
    features = request.ultrasound_features.model_dump()
    probabilities = MolecularSubtypePredictor.predict_from_ultrasound(features)
    return probabilities


@router.post(
    "/check-concordance",
    summary="诊断一致性检查",
    description="比较 AI 评估与医师诊断的一致性",
    response_model=ConcordanceCheckResponse
)
async def check_diagnostic_concordance(request: ConcordanceCheckRequest):
    """
    诊断一致性检查
    
    比较 AI 评估与医师诊断的:
    1. BI-RADS 分级一致性
    2. 恶性风险评分一致性
    3. 超声征象识别一致性
    
    输出一致性等级、评分和分歧解释
    
    适用场景:
    - AI 辅助诊断质量控制
    - 多学科会诊 (MDT) 前评估
    - 医师培训与考核
    """
    result = ConcordanceChecker.check_concordance(
        ai_result=request.ai_result,
        physician_diagnosis=request.physician_diagnosis
    )
    
    return {
        "level": result.level.value,
        "score": result.score,
        "birads_diff": result.birads_diff,
        "agreement_details": result.agreement_details,
        "discordance_reasons": result.discordance_reasons,
        "recommendation": result.recommendation
    }


@router.post(
    "/birads-visualization",
    summary="BI-RADS 评估可视化",
    description="生成 BI-RADS 评估可视化数据 (仪表盘/特征贡献/决策树/雷达图)",
)
async def get_birads_visualization(request: BIRADSAssessmentRequest):
    """
    BI-RADS 评估可视化
    
    生成以下可视化数据:
    1. 恶性风险仪表盘 - 直观显示风险等级
    2. 特征贡献度 - 各征象的权重和贡献
    3. 决策树路径 - AI 推理过程
    4. 雷达图 - 多维度评估
    
    适用于:
    - 医师快速理解 AI 评估依据
    - 患者教育和沟通
    - 质量控制和培训
    """
    features = request.ultrasound_features.model_dump()
    
    # 调用 BI-RADS 引擎
    score = BIRADSEngine._calculate_malignant_score(features)
    birads = BIRADSEngine._score_to_birads(score).value
    
    # 生成可视化数据
    viz_data = BIRADSVisualization.generate_visualization_data(
        ultrasound_features=features,
        malignant_score=score,
        birads_category=birads
    )
    
    return viz_data.dict()


@router.post(
    "/mark-lesion",
    summary="病灶标记与定位",
    description="标记病灶 ROI 并确定位置 (象限/钟点/深度)",
    response_model=LesionMarkupResponse
)
async def mark_lesion(request: LesionMarkupRequest):
    """
    病灶标记与定位
    
    功能:
    1. 创建 ROI 标记 (边界框/质心/面积)
    2. 确定病灶位置 (象限/钟点位置)
    3. 测量距皮肤/乳头/胸肌距离
    4. 分析病灶与周围组织关系
    """
    # 创建 ROI 标记
    markup = LesionMarker.create_roi_markup(
        bounding_box=request.bounding_box
    )
    
    # 确定位置
    location = LesionMarker.determine_location(
        centroid=markup.centroid,
        image_dimensions=request.image_dimensions,
        nipple_position=request.nipple_position,
        skin_line=request.skin_line,
        pectoralis_line=request.pectoralis_line,
        laterality=request.laterality
    )
    
    # 分析空间关系
    spatial = LesionMarker.analyze_spatial_relationship(
        location=location,
        skin_line=request.skin_line,
        pectoralis_line=request.pectoralis_line
    )
    
    return {
        "roi": {
            "lesion_id": markup.lesion_id,
            "bounding_box": markup.bounding_box,
            "centroid": markup.centroid,
            "area_mm2": markup.area_mm2,
            "perimeter_mm": markup.perimeter_mm,
            "confidence": markup.confidence
        },
        "location": {
            "quadrant": location.quadrant.value,
            "clock_position": location.clock_position.value,
            "distance_from_nipple_mm": location.distance_from_nipple_mm,
            "depth_from_skin_mm": location.depth_from_skin_mm,
            "distance_from_pectoral_mm": location.distance_from_pectoral_mm,
            "laterality": location.laterality
        },
        "spatial_relationship": {
            "skin_involvement": spatial.skin_involvement,
            "skin_distance_mm": spatial.skin_distance_mm,
            "pectoralis_involvement": spatial.pectoralis_involvement,
            "pectoralis_distance_mm": spatial.pectoralis_distance_mm,
            "nipple_involvement": spatial.nipple_involvement,
            "chest_wall_involvement": spatial.chest_wall_involvement
        }
    }


@router.post(
    "/assess-lymph-node",
    summary="腋窝淋巴结评估",
    description="评估腋窝淋巴结良恶性及 N 分期",
    response_model=LNAssessmentResponse
)
async def assess_lymph_node(request: LNAssessmentRequest):
    """
    腋窝淋巴结评估
    
    评估标准:
    - 皮质厚度 (>3mm 可疑)
    - 淋巴门存在/消失
    - 形态 (L/S 比)
    - 内部回声和血流
    
    输出 N 分期建议
    """
    result = LymphNodeAssessment.assess(
        ultrasound_features=request.ultrasound_features,
        clinical_context=request.clinical_context
    )
    
    return {
        "status": result.status.value,
        "n_stage": result.n_stage.value if result.n_stage else None,
        "confidence": result.confidence,
        "suspicious_features": result.suspicious_features,
        "recommendation": result.recommendation,
        "metrics": result.metrics
    }


@router.post(
    "/analyze-growth",
    summary="病灶生长分析",
    description="基于多次测量分析病灶生长趋势",
    response_model=GrowthAnalysisResponse
)
async def analyze_lesion_growth(request: LesionTrackingRequest):
    """
    病灶生长分析
    
    基于 RECIST 1.1 标准:
    1. 计算生长速度 (mm/月)
    2. 估算倍增时间
    3. 识别形态变化
    4. 预测恶性风险
    
    需要至少 2 次测量数据
    """
    from datetime import datetime
    
    # 转换测量数据
    measurements = []
    for m in request.measurements:
        measurements.append({
            "date": datetime.fromisoformat(m["date"]),
            "longest_diameter_mm": m["longest_diameter_mm"],
            "short_axis_mm": m.get("short_axis_mm"),
            "area_mm2": m.get("area_mm2"),
            "volume_mm3": m.get("volume_mm3"),
            "birads_category": m.get("birads_category", "3"),
            "notes": m.get("notes")
        })
    
    # 分析生长
    from app.diagnosis.services.lesion_tracker import GrowthAnalysis
    growth = LesionTracker.analyze_growth(measurements)
    
    # 预测恶性风险
    malignancy_risk = LesionTracker.predict_malignancy_risk_from_growth(growth)
    
    return {
        "growth_rate": growth.growth_rate.value,
        "size_change_percent": growth.size_change_percent,
        "velocity_mm_per_month": growth.velocity_mm_per_month,
        "doubling_time_days": growth.doubling_time_days,
        "morphological_changes": growth.morphological_changes,
        "malignancy_risk": round(malignancy_risk, 3)
    }


@router.post(
    "/assess-treatment-response",
    summary="治疗反应评估",
    description="基于 RECIST 1.1 评估治疗反应 (CR/PR/SD/PD)",
    response_model=TreatmentResponseResponse
)
async def assess_treatment_response_api(request: TreatmentResponseRequest):
    """
    治疗反应评估 (RECIST 1.1)
    
    评估标准:
    - CR (完全缓解): 病灶消失
    - PR (部分缓解): 缩小≥30%
    - SD (疾病稳定): 介于 PR 和 PD 之间
    - PD (疾病进展): 增大≥20% 且≥5mm
    
    适用于新辅助治疗监测
    """
    from datetime import datetime
    from app.diagnosis.services.lesion_tracker import LesionMeasurement
    
    baseline = LesionMeasurement(
        date=datetime.fromisoformat(request.baseline_date),
        longest_diameter_mm=request.baseline_diameter,
        short_axis_mm=None,
        area_mm2=None,
        volume_mm3=None,
        birads_category="",
        notes=None
    )
    
    follow_up = LesionMeasurement(
        date=datetime.fromisoformat(request.follow_up_date),
        longest_diameter_mm=request.follow_up_diameter,
        short_axis_mm=None,
        area_mm2=None,
        volume_mm3=None,
        birads_category="",
        notes=None
    )
    
    result = LesionTracker.assess_treatment_response(baseline, follow_up)
    
    return {
        "response": result.response.value,
        "target_lesion_change": result.target_lesion_change,
        "summary_stage": result.summary_stage,
        "recommendation": result.recommendation
    }
