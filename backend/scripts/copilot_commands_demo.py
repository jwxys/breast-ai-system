"""
Copilot 系统命令演示脚本

展示如何通过聊天对话执行系统操作
"""

import asyncio
import json
from typing import Dict, Any


# 模拟对话场景
SCENARIOS = [
    {
        "name": "场景 1: 创建新患者",
        "对话": [
            {"role": "user", "content": "创建新患者，张三，女，35 岁，手机号 13812345678"},
            {"role": "assistant", "content": "好的，正在为您创建患者档案..."},
        ],
        "command": "create_patient",
        "params": {
            "name": "张三",
            "age": 35,
            "gender": "female",
            "phone": "13812345678",
        },
        "expected_result": {
            "success": True,
            "message": "患者 张三 创建成功",
            "patient_id": 1,
        },
    },
    {
        "name": "场景 2: 安排超声检查",
        "对话": [
            {"role": "user", "content": "给患者张三（ID: 1）安排今天的乳腺超声检查"},
            {"role": "assistant", "content": "好的，正在创建超声检查申请..."},
        ],
        "command": "create_ultrasound",
        "params": {
            "patient_id": 1,
            "exam_type": "乳腺超声",
        },
        "expected_result": {
            "success": True,
            "message": "超声检查已创建",
            "ultrasound_id": 1,
        },
    },
    {
        "name": "场景 3: 执行 AI 推理",
        "对话": [
            {"role": "user", "content": "对刚才的超声检查进行 AI 分析"},
            {"role": "assistant", "content": "好的，正在执行 AI 推理分析..."},
        ],
        "command": "run_ai_inference",
        "params": {
            "ultrasound_id": 1,
        },
        "expected_result": {
            "success": True,
            "message": "AI 推理已完成",
            "birads": "4a",
            "confidence": 0.85,
        },
    },
    {
        "name": "场景 4: 生成检查报告",
        "对话": [
            {"role": "user", "content": "生成张三的检查报告"},
            {"role": "assistant", "content": "好的，正在生成超声检查报告..."},
        ],
        "command": "generate_report",
        "params": {
            "patient_id": 1,
            "ultrasound_id": 1,
            "birads": "4a",
            "conclusion": "右乳低回声结节，BI-RADS 4a 类，建议穿刺活检",
        },
        "expected_result": {
            "success": True,
            "message": "报告已生成",
            "report_id": 1,
        },
    },
    {
        "name": "场景 5: 安排随访",
        "对话": [
            {"role": "user", "content": "给张三安排 3 个月后的随访"},
            {"role": "assistant", "content": "好的，正在安排随访计划..."},
        ],
        "command": "schedule_followup",
        "params": {
            "patient_id": 1,
            "visit_type": "随访",
            "purpose": "乳腺结节复查",
        },
        "expected_result": {
            "success": True,
            "message": "随访已安排",
            "visit_id": 1,
        },
    },
]


async def demo_copilot_commands():
    """演示 Copilot 命令执行"""
    from app.services.copilot_service import MedicalCopilotService
    
    print("=" * 80)
    print("医疗 Copilot 系统命令演示")
    print("=" * 80)
    print()
    
    # 创建 Copilot 服务实例（使用规则引擎模式）
    copilot = MedicalCopilotService(use_default_model=True)
    await copilot.initialize()
    
    # 创建会话
    session_id = await copilot.create_session(
        user_id=1,
        patient_id=None,
        mode="general",
    )
    
    print(f"✅ 会话已创建：{session_id}")
    print()
    
    # 遍历所有场景
    for scenario in SCENARIOS:
        print("-" * 80)
        print(f"📋 {scenario['name']}")
        print("-" * 80)
        
        # 显示对话
        for msg in scenario["对话"]:
            role = "👨‍⚕️ 医生" if msg["role"] == "user" else "🤖 Copilot"
            print(f"{role}: {msg['content']}")
        
        # 执行命令
        print()
        print("⚙️  执行系统命令:")
        print(f"   命令：{scenario['command']}")
        print(f"   参数：{json.dumps(scenario['params'], ensure_ascii=False)}")
        
        result = await copilot.execute_system_command(
            session_id=session_id,
            command=scenario["command"],
            params=scenario["params"],
        )
        
        # 显示结果
        print()
        print("📊 执行结果:")
        print(f"   成功：{result.get('success')}")
        print(f"   消息：{result.get('message')}")
        for key, value in result.items():
            if key not in ["success", "message"]:
                print(f"   {key}: {value}")
        print()
    
    print("=" * 80)
    print("✅ 所有场景演示完成!")
    print("=" * 80)
    
    # 关闭会话
    copilot.close_session(session_id)


def print_command_summary():
    """打印命令摘要"""
    print()
    print("=" * 80)
    print("支持的 Copilot 系统命令")
    print("=" * 80)
    print()
    
    commands = {
        "患者管理": [
            ("create_patient", "创建患者", ["name", "age", "gender"]),
            ("update_patient", "更新患者", ["patient_id"]),
            ("get_patient", "查询患者", ["patient_id"]),
        ],
        "超声检查": [
            ("create_ultrasound", "创建检查", ["patient_id"]),
            ("run_ai_inference", "AI 分析", ["ultrasound_id"]),
        ],
        "报告生成": [
            ("generate_report", "生成报告", ["patient_id", "ultrasound_id"]),
            ("list_reports", "查询报告", ["patient_id"]),
        ],
        "随访管理": [
            ("schedule_followup", "安排随访", ["patient_id", "visit_date"]),
            ("list_followups", "查询随访", ["patient_id"]),
        ],
        "数据导出": [
            ("export_data", "导出数据", ["type", "date_from", "date_to"]),
        ],
    }
    
    for category, cmds in commands.items():
        print(f"📁 {category}")
        for cmd, desc, params in cmds:
            print(f"  • {cmd:20s} - {desc:15s} 参数：{', '.join(params)}")
        print()
    
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # 运行演示
        asyncio.run(demo_copilot_commands())
    else:
        # 显示命令摘要
        print_command_summary()
        print()
        print("使用 --demo 参数运行完整演示")
        print()
        print("示例:")
        print("  python3 -m uvicorn app.main:app --reload  # 启动后端")
        print("  python3 scripts/copilot_commands_demo.py --demo  # 运行演示")
