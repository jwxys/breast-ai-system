"""
高级诊断 API

提供可视化增强、质控管理、工作流优化等高级功能
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel
import numpy as np

from app.core.database import get_db
from app.diagnosis.services.visualization_enhancement import VisualizationEnhancement, Measurement
from app.diagnosis.services.quality_control import QualityControlManager, ReviewWorkflow, ConfidenceLevel
from app.diagnosis.services.workflow_optimizer import WorkflowOptimizer, FollowUpStatus

router = APIRouter(prefix="/api/v1/diagnosis/advanced", tags=["高级诊断功能"])


class QualityCheckRequest(BaseModel):
    """质控评估请求"""
    ai_result: Dict
    ultrasound_features: Dict


class FollowUpPlanRequest(BaseModel):
    """随访计划请求"""
    patient_id: int
    lesion_id: int
    birads_category: str
    special_conditions: Optional[Dict] = None


@router.post(
    "/annotate-image",
    summary="病灶标注与可视化增强",
    description="在超声图像上叠加病灶边界框、分割掩码、热图、测量标注等",
)
async def annotate_ultrasound_image(image_url: str = Body(..., description="图像 URL")):
    """
    多模态病灶标注
    
    功能:
    1. 绘制病灶边界框 (根据 BI-RADS 分级着色)
    2. 叠加 AI 注意力热图
    3. 绘制分割掩码 (半透明)
    4. 添加测量标注 (大小/距皮肤距离等)
    5. 显示 AI 置信度指示器
    """
    viz_service = VisualizationEnhancement()
    
    # 使用示例图像 (实际应从 API 加载)
    try:
        # 创建示例图像
        example_image = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"图像处理失败：{e}")
    
    # 2. 提取病灶信息 (从 AI 结果或手动输入)
    # 这里假设已从 AI 分析获得相关信息
    bbox = {
        'x': 150,
        'y': 200,
        'width': 25,
        'height': 30,
    }
    
    # 3. 生成分割掩码 (简化示例，实际应用应从 AI 模型获取)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    mask[200:230, 150:175] = 1  # 示例区域
    
    # 4. 生成 AI 注意力热图 (示例)
    heatmap = np.random.rand(100, 100).astype(np.float32)  # 示例热图
    
    # 5. 创建测量标注
    measurements = [
        Measurement(
            label="长径",
            value=2.5,
            unit="cm",
            start_point=(150, 200),
            end_point=(175, 200)
        ),
        Measurement(
            label="宽",
            value=3.0,
            unit="cm",
            start_point=(150, 200),
            end_point=(150, 230)
        ),
    ]
    
    # 6. 多模态叠加
    annotated_image = viz_service.draw_multimodal_overlay(
        image=image,
        bbox=bbox,
        mask=mask,
        heatmap=heatmap,
        measurements=measurements,
        birads_category="4B",
        ai_confidence=0.87
    )
    
    # 7. 转换为 base64
    image_base64 = viz_service.to_base64(annotated_image)
    
    return {
        "image_data": image_base64,
        "format": "jpeg",
        "width": annotated_image.shape[1],
        "height": annotated_image.shape[0],
        "annotations": {
            "bbox": bbox,
            "measurements": [
                {
                    "label": m.label,
                    "value": m.value,
                    "unit": m.unit
                }
                for m in measurements
            ],
            "birads_category": "4B",
            "ai_confidence": 0.87
        }
    }


@router.post(
    "/quality-check",
    summary="AI 诊断质控评估",
    description="评估 AI 诊断质量，判断是否需要人工复核",
)
async def assess_diagnosis_quality(request: QualityCheckRequest):
    """
    质控评估
    
    评估维度:
    1. AI 置信度评分
    2. 征象识别一致性
    3. 关键征象检测
    4. 复核建议生成
    
    Returns:
        quality_metrics: 质量指标
        should_review: 是否需要复核
        review_reason: 复核原因
        warning_level: 预警等级 (green/yellow/orange/red)
    """
    qc_manager = QualityControlManager(auto_review_threshold=0.7)
    
    # 1. 评估质量
    quality_metrics = qc_manager.evaluate_confidence(
        ai_result=request.ai_result,
        ultrasound_features=request.ultrasound_features
    )
    
    # 2. 判断是否触发复核
    should_review, review_reason = qc_manager.should_trigger_review(quality_metrics)
    
    # 3. 确定预警等级
    if quality_metrics.overall_confidence >= 0.9:
        warning_level = "green"
    elif quality_metrics.overall_confidence >= 0.7:
        warning_level = "yellow"
    elif quality_metrics.overall_confidence >= 0.5:
        warning_level = "orange"
    else:
        warning_level = "red"
    
    return {
        "quality_metrics": {
            "overall_confidence": quality_metrics.overall_confidence,
            "feature_confidence": quality_metrics.feature_confidence,
            "consistency_score": quality_metrics.consistency_score,
            "uncertainty_level": quality_metrics.uncertainty_level
        },
        "should_review": should_review,
        "review_reason": review_reason,
        "warning_level": warning_level,
        "recommendation": quality_metrics.recommendation
    }
    
    # 1. 评估质量
    quality_metrics = qc_manager.evaluate_confidence(
        ai_result=ai_result,
        ultrasound_features=ai_result['features']
    )
    
    # 2. 判断是否触发复核
    should_review, review_reason = qc_manager.should_trigger_review(quality_metrics)
    
    # 3. 确定预警等级
    if quality_metrics.overall_confidence >= 0.9:
        warning_level = "green"
    elif quality_metrics.overall_confidence >= 0.7:
        warning_level = "yellow"
    elif quality_metrics.overall_confidence >= 0.5:
        warning_level = "orange"
    else:
        warning_level = "red"
    
    return {
        "quality_metrics": {
            "overall_confidence": quality_metrics.overall_confidence,
            "feature_confidence": quality_metrics.feature_confidence,
            "consistency_score": quality_metrics.consistency_score,
            "uncertainty_level": quality_metrics.uncertainty_level
        },
        "should_review": should_review,
        "review_reason": review_reason,
        "warning_level": warning_level,
        "recommendation": quality_metrics.recommendation
    }


@router.post(
    "/submit-for-review",
    summary="提交人工复核",
    description="将 AI 诊断提交到复核队列",
)
async def submit_for_review(
    diagnosis_id: int,
    reviewer_id: Optional[int] = None,
    reason: str = "低置信度预警"
):
    """
    提交复核
    
    工作流:
    1. 创建复核记录
    2. 分配到复核队列
    3. 通知复核医师
    4. 跟踪复核状态
    """
    qc_manager = QualityControlManager()
    workflow = ReviewWorkflow(qc_manager)
    
    # 模拟 AI 结果
    ai_result = {
        'diagnosis_id': diagnosis_id,
        'birads_prediction': '4B',
        'confidence': 0.68,
        'features': {}
    }
    
    # 提交复核
    result = workflow.submit_for_review(
        diagnosis_id=diagnosis_id,
        ai_result=ai_result,
        reason=reason
    )
    
    return result


@router.post(
    "/compare-examinations",
    summary="历史检查对比",
    description="对比当前与历史检查，分析病灶变化",
)
async def compare_historical_examinations(
    patient_id: int,
    lesion_id: int,
    current_exam_date: str,
    previous_exam_date: str
):
    """
    一键历史对比
    
    对比内容:
    1. 病灶大小变化 (绝对值/百分比)
    2. 体积变化与倍增时间
    3. BI-RADS 分级变化
    4. 征象演变 (新增/消失)
    5. 生长速度计算
    
    Returns:
        comparison_result: 对比结果
        visual_comparison: 对比图 (base64)
        growth_curve: 生长曲线数据
    """
    optimizer = WorkflowOptimizer()
    
    # 模拟获取历史数据 (实际应从数据库查询)
    previous_exam = {
        'exam_date': previous_exam_date,
        'lesion': {
            'id': lesion_id,
            'dimensions': {'length': 20, 'width': 15, 'height': 12},
            'birads_category': '3',
            'features': {
                'shape': 'oval',
                'margin_types': ['circumscribed'],
                'taller_than_wide': False,
            }
        }
    }
    
    current_exam = {
        'exam_date': current_exam_date,
        'lesion': {
            'id': lesion_id,
            'dimensions': {'length': 25, 'width': 18, 'height': 15},
            'birads_category': '4A',
            'features': {
                'shape': 'irregular',
                'margin_types': ['indistinct'],
                'taller_than_wide': True,
            }
        }
    }
    
    # 计算间隔天数
    days_interval = 180  # 示例：6 个月
    
    # 执行对比
    comparison = optimizer.compare_examinations(
        current_exam=current_exam,
        previous_exam=previous_exam,
        days_interval=days_interval
    )
    
    return {
        "comparison_result": {
            "lesion_id": comparison.lesion_id,
            "time_interval_days": days_interval,
            "size_change": {
                "absolute_mm": comparison.size_change_mm,
                "percent": f"{comparison.size_change_percent:.1f}%"
            },
            "volume_change": {
                "previous_mm3": f"{comparison.previous_exam['volume_mm3']:.1f}",
                "current_mm3": f"{comparison.current_exam['volume_mm3']:.1f}",
                "percent": f"{comparison.volume_change_percent:.1f}%"
            },
            "birads_change": comparison.birads_change,
            "new_features": comparison.new_features,
            "disappeared_features": comparison.disappeared_features,
            "growth_rate": f"{comparison.growth_rate_mm_per_month:.2f} mm/月",
            "doubling_time_days": f"{comparison.doubling_time_days:.0f} 天" if comparison.doubling_time_days else "N/A",
            "assessment": comparison.assessment,
            "recommendation": comparison.recommendation
        },
        "visual_comparison_available": True,  # 实际应生成对比图
        "growth_curve_data": [
            {"date": previous_exam_date, "size_mm": comparison.previous_exam['size_mm']},
            {"date": current_exam_date, "size_mm": comparison.current_exam['size_mm']}
        ]
    }


@router.post(
    "/generate-followup-plan",
    summary="生成随访计划",
    description="基于 BI-RADS 分级和病灶特征自动生成个性化随访计划",
)
async def generate_followup_plan(request: FollowUpPlanRequest):
    """
    智能随访计划
    
    考虑因素:
    1. BI-RADS 分级 (决定基础间隔)
    2. 生长速度 (快速生长缩短间隔)
    3. 体积倍增时间 (短倍增时间需密切随访)
    4. 新征象出现 (调整优先级)
    5. 患者个体因素 (年龄/家族史等)
    
    Returns:
        followup_plan: 随访计划详情
        reminders: 提醒设置
    """
    optimizer = WorkflowOptimizer()
    
    # 生成随访计划
    plan = optimizer.generate_followup_plan(
        patient_id=request.patient_id,
        lesion_id=request.lesion_id,
        birads_category=request.birads_category,
        exam_date=datetime.now(),
        special_conditions=request.special_conditions
    )
    
    return {
        "plan_id": plan.plan_id,
        "patient_id": plan.patient_id,
        "lesion_id": plan.lesion_id,
        "priority": plan.priority.value,
        "recommended_date": plan.recommended_date.strftime("%Y-%m-%d"),
        "latest_date": plan.latest_date.strftime("%Y-%m-%d"),
        "followup_type": plan.followUp_type,
        "reason": plan.reason,
        "birads_category": plan.birads_category,
        "reminder_settings": {
            "first_reminder": (plan.recommended_date - timedelta(days=7)).strftime("%Y-%m-%d"),
            "urgent_reminder": (plan.latest_date - timedelta(days=3)).strftime("%Y-%m-%d")
        }
    }


@router.get(
    "/followup-reminders",
    summary="获取随访提醒",
    description="查询即将到期或逾期的随访计划",
)
async def get_followup_reminders(
    patient_id: Optional[int] = None,
    days_ahead: int = 7,
    include_overdue: bool = True
):
    """
    随访提醒
    
    Returns:
        upcoming: 即将到期的随访
        overdue: 逾期的随访
        statistics: 统计信息
    """
    optimizer = WorkflowOptimizer()
    
    # 获取提醒
    upcoming = optimizer.get_followup_reminders(days_ahead=days_ahead)
    
    reminders = {
        "upcoming": [
            {
                "plan_id": plan.plan_id,
                "patient_id": plan.patient_id,
                "lesion_id": plan.lesion_id,
                "priority": plan.priority.value,
                "recommended_date": plan.recommended_date.strftime("%Y-%m-%d"),
                "followup_type": plan.followUp_type,
                "birads_category": plan.birads_category
            }
            for plan in upcoming
        ]
    }
    
    if include_overdue:
        overdue = optimizer.get_overdue_followups(patient_id=patient_id)
        reminders["overdue"] = [
            {
                "plan_id": plan.plan_id,
                "patient_id": plan.patient_id,
                "lesion_id": plan.lesion_id,
                "overdue_days": (datetime.now() - plan.latest_date).days,
                "birads_category": plan.birads_category
            }
            for plan in overdue
        ]
    
    reminders["statistics"] = {
        "upcoming_count": len(upcoming),
        "overdue_count": len(overdue) if include_overdue else 0
    }
    
    return reminders


@router.post(
    "/export-learning-data",
    summary="导出持续学习数据",
    description="导出医师修正数据，用于模型微调",
)
async def export_learning_data(
    format: str = Query(default="json", description="导出格式：json/jsonl/csv"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    持续学习数据导出
    
    数据内容:
    1. 原始 AI 预测
    2. 医师修正结果
    3. 修正幅度
    4. 修正原因
    
    用途:
    1. 模型微调训练
    2. 质控分析
    3. AI 性能评估
    """
    qc_manager = QualityControlManager()
    
    # 模拟导出 (实际应连接数据库)
    learning_data = qc_manager.get_learning_dataset()
    
    return {
        "format": format,
        "total_samples": len(learning_data),
        "date_range": {
            "start": start_date or "all",
            "end": end_date or "latest"
        },
        "data_summary": {
            "confirmed_cases": sum(1 for d in learning_data if d.get('confidence_delta', 0) == 0),
            "modified_cases": sum(1 for d in learning_data if d.get('confidence_delta', 0) != 0),
            "average_confidence_delta": np.mean([d.get('confidence_delta', 0) for d in learning_data]) if learning_data else 0
        },
        "export_status": "ready",
        "note": "实际实现将保存到文件并提供下载链接"
    }


@router.get(
    "/quality-statistics",
    summary="质控统计",
    description="查看 AI 诊断质量统计和趋势",
)
async def get_quality_statistics():
    """
    质量统计面板
    
    统计指标:
    1. 总复核数
    2. 确认率 vs 修改率
    3. 平均置信度
    4. 置信度变化趋势
    5. 质控改进建议
    """
    qc_manager = QualityControlManager()
    stats = qc_manager.get_quality_statistics()
    
    return {
        "statistics": stats,
        "quality_assessment": (
            "优秀" if stats['average_confidence'] > 0.85 and stats['modification_rate'] < 0.2
            else "良好" if stats['average_confidence'] > 0.75
            else "需改进"
        ),
        "recommendations": [
            "继续保持高置信度诊断" if stats['average_confidence'] > 0.85 else "建议加强 AI 训练",
            "修改率合理" if stats['modification_rate'] < 0.3 else "建议复核流程优化",
        ]
    }
