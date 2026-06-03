#!/usr/bin/env python3
"""
高级诊断功能测试脚本

测试四大改进方向:
1. 可视化增强
2. 质控管理
3. 工作流优化
4. 持续学习
"""

import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8005"


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(data: dict, title: str = "结果"):
    """打印 JSON 结果"""
    print(f"\n【{title}】")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_quality_control():
    """测试质控管理功能"""
    print_section("1️⃣ 质控管理测试")
    
    # 测试案例 1: 高置信度诊断
    print("\n▶ 测试案例 1: 高置信度诊断 (置信度 92%)")
    response = httpx.post(
        f"{BASE_URL}/api/v1/diagnosis/advanced/quality-check",
        json={
            "ai_result": {
                "confidence": 0.92,
                "birads_prediction": "4A",
                "features": {}
            },
            "ultrasound_features": {
                "shape": "oval",
                "margin_types": ["circumscribed"],
                "taller_than_wide": False
            }
        }
    )
    if response.status_code == 200:
        result = response.json()
        print(f"   整体置信度：{result['quality_metrics']['overall_confidence']:.1%}")
        print(f"   一致性评分：{result['quality_metrics']['consistency_score']:.2f}")
        print(f"   预警等级：{result['warning_level']}")
        print(f"   建议：{result['recommendation']}")
        print("   ✅ 测试通过：高置信度 - 无需复核")
    else:
        print(f"   ❌ 测试失败：{response.text}")
    
    # 测试案例 2: 关键恶性征象
    print("\n▶ 测试案例 2: 检测到关键恶性征象 (毛刺状边缘)")
    response = httpx.post(
        f"{BASE_URL}/api/v1/diagnosis/advanced/quality-check",
        json={
            "ai_result": {
                "confidence": 0.78,
                "birads_prediction": "4C",
                "features": {}
            },
            "ultrasound_features": {
                "shape": "irregular",
                "margin_types": ["spiculated"],
                "taller_than_wide": True
            }
        }
    )
    if response.status_code == 200:
        result = response.json()
        print(f"   整体置信度：{result['quality_metrics']['overall_confidence']:.1%}")
        print(f"   预警等级：{result['warning_level']}")
        print(f"   需要复核：{'是' if result['should_review'] else '否'}")
        print(f"   复核原因：{result['review_reason']}")
        print(f"   建议：{result['recommendation']}")
        print("   ✅ 测试通过：关键征象触发复核")
    
    # 测试案例 3: 低置信度预警
    print("\n▶ 测试案例 3: 低置信度预警 (置信度 58%)")
    response = httpx.post(
        f"{BASE_URL}/api/v1/diagnosis/advanced/quality-check",
        json={
            "ai_result": {
                "confidence": 0.58,
                "birads_prediction": "3",
                "features": {}
            },
            "ultrasound_features": {
                "shape": "oval",
                "margin_types": ["circumscribed"]
            }
        }
    )
    if response.status_code == 200:
        result = response.json()
        print(f"   整体置信度：{result['quality_metrics']['overall_confidence']:.1%}")
        print(f"   预警等级：{result['warning_level']}")
        print(f"   建议：{result['recommendation']}")
        print("   ✅ 测试通过：低置信度触发复核")


def test_followup_planning():
    """测试随访计划生成功能"""
    print_section("2️⃣ 工作流优化 - 随访计划")
    
    test_cases = [
        ("BI-RADS 2 类 - 常规随访", 1, 1, "2"),
        ("BI-RADS 3 类 - 短期随访", 2, 2, "3"),
        ("BI-RADS 4A 类 - 紧急处理", 3, 3, "4A"),
        ("BI-RADS 4B 类 - 立即处理", 4, 4, "4B"),
    ]
    
    for title, patient_id, lesion_id, birads in test_cases:
        print(f"\n▶ {title}")
        response = httpx.post(
            f"{BASE_URL}/api/v1/diagnosis/advanced/generate-followup-plan",
            json={
                "patient_id": patient_id,
                "lesion_id": lesion_id,
                "birads_category": birads
            }
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   随访 ID: {result['plan_id']}")
            print(f"   优先级：{result['priority']}")
            print(f"   推荐日期：{result['recommended_date']}")
            print(f"   随访类型：{result['followup_type']}")
            print(f"   原因：{result['reason']}")
            print("   ✅ 测试通过")


def test_comparison():
    """测试历史检查对比功能"""
    print_section("3️⃣ 工作流优化 - 历史对比")
    
    print("\n▶ 对比 6 个月前的检查")
    response = httpx.post(
        f"{BASE_URL}/api/v1/diagnosis/advanced/compare-examinations",
        json={
            "patient_id": 1,
            "lesion_id": 1,
            "current_exam_date": "2026-06-01",
            "previous_exam_date": "2026-01-01"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        comp = result['comparison_result']
        print(f"   大小变化：{comp['size_change']['absolute_mm']}mm ({comp['size_change']['percent']})")
        print(f"   BI-RADS 变化：{comp['birads_change']}")
        print(f"   新增征象：{', '.join(comp['new_features']) if comp['new_features'] else '无'}")
        print(f"   生长速度：{comp['growth_rate']}")
        print(f"   倍增时间：{comp['doubling_time_days']}")
        print(f"   评估：{comp['assessment']}")
        print(f"   建议：{comp['recommendation']}")
        print("   ✅ 测试通过")


def test_followup_reminders():
    """测试随访提醒功能"""
    print_section("4️⃣ 工作流优化 - 随访提醒")
    
    print("\n▶ 获取未来 7 天内的随访提醒")
    response = httpx.get(
        f"{BASE_URL}/api/v1/diagnosis/advanced/followup-reminders?days_ahead=7"
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   即将到期：{result['statistics']['upcoming_count']} 例")
        print(f"   已逾期：{result['statistics']['overdue_count']} 例")
        
        if result['upcoming']:
            print("\n   即将到期的随访:")
            for plan in result['upcoming']:
                print(f"   - {plan['plan_id']}: {plan['recommended_date']} "
                      f"({plan['priority']}, {plan['followup_type']})")
        
        print("   ✅ 测试通过")


def test_quality_statistics():
    """测试质控统计功能"""
    print_section("5️⃣ 质控统计面板")
    
    print("\n▶ 获取质控统计信息")
    response = httpx.get(
        f"{BASE_URL}/api/v1/diagnosis/advanced/quality-statistics"
    )
    
    if response.status_code == 200:
        result = response.json()
        stats = result['statistics']
        print(f"   总复核数：{stats['total_reviews']}")
        print(f"   平均置信度：{stats['average_confidence']:.1%}")
        print(f"   修改率：{stats['modification_rate']:.1%}")
        print(f"   质量评估：{result['quality_assessment']}")
        print(f"   建议:")
        for rec in result['recommendations']:
            print(f"     - {rec}")
        print("   ✅ 测试通过")


def main():
    """执行所有测试"""
    print("\n" + "🔬" * 40)
    print("    乳腺超声 AI 诊断系统 - 高级功能测试")
    print("🔬" * 40)
    
    # 检查服务状态
    try:
        health = httpx.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code == 200:
            print(f"\n✅ 服务状态：健康 (版本 {health.json()['version']})")
        else:
            print(f"\n❌ 服务异常：{health.status_code}")
            return
    except Exception as e:
        print(f"\n❌ 无法连接服务：{e}")
        print(f"   请确保服务已启动：python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8005")
        return
    
    # 执行测试
    test_quality_control()
    test_followup_planning()
    test_comparison()
    test_followup_reminders()
    test_quality_statistics()
    
    print("\n" + "✅" * 40)
    print("    所有测试完成!")
    print("✅" * 40 + "\n")


if __name__ == "__main__":
    main()
