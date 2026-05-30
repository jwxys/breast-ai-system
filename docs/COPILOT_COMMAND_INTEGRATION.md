# Copilot 系统命令集成文档

## 概述

医疗 Copilot 现在支持通过自然语言对话执行系统操作，实现**半自主控制系统**。

## 支持的命令

### 1. 患者管理 👨‍⚕️

#### create_patient - 创建患者
```python
# 自然语言指令
"创建新患者，张三，女，35 岁，手机号 13812345678"

# API 调用
POST /api/v1/copilot/sessions/{session_id}/commands
{
  "command": "create_patient",
  "params": {
    "name": "张三",
    "age": 35,
    "gender": "female",
    "phone": "13812345678"
  }
}

# 响应
{
  "success": true,
  "message": "患者 张三 创建成功",
  "patient_id": 1,
  "patient_name": "张三"
}

# Copilot 反馈
✅ 患者 **张三** 创建成功！

📋 信息摘要:
- 患者 ID: 1
- 姓名：张三

下一步操作？
```

#### update_patient - 更新患者
```python
# 指令
"更新患者 1 的手机号为 13987654321"

# 调用
{
  "command": "update_patient",
  "params": {
    "patient_id": 1,
    "phone": "13987654321"
  }
}
```

#### get_patient - 查询患者
```python
# 指令
"查看患者 1 的信息"

# 调用
{
  "command": "get_patient",
  "params": {
    "patient_id": 1
  }
}

# 响应
{
  "success": true,
  "message": "找到患者：张三",
  "patient": {
    "id": 1,
    "name": "张三",
    "age": 35,
    "gender": "female",
    "phone": "13812345678"
  }
}
```

### 2. 超声检查 🔬

#### create_ultrasound - 创建检查
```python
# 指令
"给患者 1 安排今天的乳腺超声检查"

# 调用
{
  "command": "create_ultrasound",
  "params": {
    "patient_id": 1,
    "exam_type": "乳腺超声"
  }
}

# Copilot 反馈
✅ 超声检查已创建！

📋 检查信息:
- 检查 ID: 1
- 患者 ID: 1

需要立即执行 AI 分析吗？
```

#### run_ai_inference - AI 推理
```python
# 指令
"对检查 1 进行 AI 分析"

# 调用
{
  "command": "run_ai_inference",
  "params": {
    "ultrasound_id": 1
  }
}

# Copilot 反馈
🤖 AI 推理分析完成！

📊 分析结果:
- BI-RADS 分级：**4a**
- 置信度：85.0%

需要生成详细报告吗？
```

### 3. 报告生成 📝

#### generate_report - 生成报告
```python
# 指令
"生成患者 1 的检查报告"

# 调用
{
  "command": "generate_report",
  "params": {
    "patient_id": 1,
    "ultrasound_id": 1,
    "birads": "4a",
    "conclusion": "右乳低回声结节，BI-RADS 4a 类，建议穿刺活检"
  }
}

# Copilot 反馈
📝 报告已生成！

📋 报告信息:
- 报告 ID: 1
- 患者 ID: 1

需要查看或发送报告吗？
```

#### list_reports - 查询报告列表
```python
# 指令
"查看患者 1 的所有报告"

# 调用
{
  "command": "list_reports",
  "params": {
    "patient_id": 1,
    "limit": 10
  }
}
```

### 4. 随访管理 📅

#### schedule_followup - 安排随访
```python
# 指令
"给患者 1 安排 3 个月后的随访"

# 调用
{
  "command": "schedule_followup",
  "params": {
    "patient_id": 1,
    "visit_type": "随访",
    "purpose": "乳腺结节复查"
  }
}

# Copilot 反馈
📅 随访已安排！

📋 随访信息:
- 随访 ID: 1
- 随访日期：2026-08-29

需要设置提醒吗？
```

#### list_followups - 查询随访列表
```python
# 指令
"查看患者 1 的随访记录"

# 调用
{
  "command": "list_followups",
  "params": {
    "patient_id": 1
  }
}
```

### 5. 数据导出 📤

#### export_data - 导出数据
```python
# 指令
"导出上个月的患者数据"

# 调用
{
  "command": "export_data",
  "params": {
    "type": "patients",
    "date_from": "2026-05-01",
    "date_to": "2026-05-31",
    "format": "csv"
  }
}

# Copilot 反馈
📤 数据导出任务已创建！

📋 导出信息:
- 导出类型：patients
- 格式：csv
- 记录数：150

导出完成后会通知您。
```

## 完整对话流程示例

### 场景：从创建患者到生成报告的完整流程

```
👨‍⚕️ 医生：创建新患者，张三，女，35 岁

🤖 Copilot: [切换到系统控制模式]
✅ 患者 **张三** 创建成功！

📋 信息摘要:
- 患者 ID: 1
- 姓名：张三

下一步操作？

---

👨‍⚕️ 医生：给她安排乳腺超声检查

🤖 Copilot:
✅ 超声检查已创建！

📋 检查信息:
- 检查 ID: 1
- 患者 ID: 1

需要立即执行 AI 分析吗？

---

👨‍⚕️ 医生：好的，进行 AI 分析

🤖 Copilot:
🤖 AI 推理分析完成！

📊 分析结果:
- BI-RADS 分级：**4a**
- 置信度：85.0%

需要生成详细报告吗？

---

👨‍⚕️ 医生：生成报告

🤖 Copilot:
📝 报告已生成！

📋 报告信息:
- 报告 ID: 1
- 患者 ID: 1

需要查看或发送报告吗？

---

👨‍⚕️ 医生：发送报告给患者

🤖 Copilot:
📤 报告已发送给患者张三（138****5678）

📋 发送详情:
- 发送方式：短信 + 微信
- 发送时间：2026-05-29 10:30
- 状态：已送达

还需要安排随访吗？

---

👨‍⚕️ 医生：安排 3 个月后复查

🤖 Copilot:
📅 随访已安排！

📋 随访信息:
- 随访 ID: 1
- 随访日期：2026-08-29
- 随访类型：超声复查

需要设置提醒吗？

---

👨‍⚕️ 医生：好的，设置提醒

🤖 Copilot:
⏰ 随访提醒已设置

📋 提醒详情:
- 提醒时间：2026-08-22（随访前 7 天）
- 提醒方式：短信 + 微信
- 提醒对象：患者张三

所有操作已完成！还有其他需要帮助的吗？
```

## 错误处理

### 参数缺失
```
👨‍⚕️ 医生：创建患者

🤖 Copilot:
⚠️ 缺少必要参数

需要以下信息:
- 姓名
- 年龄
- 性别

请补充完整信息。
```

### 资源不存在
```
👨‍⚕️ 医生：查看患者 999 的信息

🤖 Copilot:
⚠️ 患者不存在

患者 ID 999 未找到，请检查 ID 是否正确。

可执行的操作:
- 查看患者列表
- 创建新患者
```

### 命令不支持
```
👨‍⚕️ 医生：删除患者 1

🤖 Copilot:
⚠️ 不支持的命令

出于数据安全考虑，删除操作需要手动执行。

我可以帮您:
- 查询患者信息
- 更新患者信息
- 安排检查
- 生成报告
```

## 实现细节

### 服务层调用链

```
Copilot API
    │
    ▼
CopilotService.execute_system_command()
    │
    ├─► _cmd_create_patient()
    │       │
    │       ▼
    │   PatientService.create()
    │
    ├─► _cmd_create_ultrasound()
    │       │
    │       ▼
    │   UltrasoundService.create()
    │
    ├─► _cmd_generate_report()
    │       │
    │       ▼
    │   ReportService.create()
    │
    └─► _cmd_schedule_followup()
            │
            ▼
        VisitService.create()
```

### 反馈消息生成

```python
def generate_feedback_message(command, result):
    """根据命令类型和结果生成友好反馈"""
    
    templates = {
        "create_patient": "...",
        "create_ultrasound": "...",
        "run_ai_inference": "...",
        "generate_report": "...",
        "schedule_followup": "...",
    }
    
    template = templates.get(command)
    if template:
        return template(result)
    
    return "命令执行成功"
```

## 测试方法

### 1. 单元测试
```bash
cd backend
pytest tests/test_copilot_commands.py -v
```

### 2. 集成测试
```bash
# 启动后端
python3 -m uvicorn app.main:app --reload

# 运行演示脚本
python3 scripts/copilot_commands_demo.py --demo
```

### 3. 手动测试
```bash
# 使用 curl 测试
curl -X POST http://localhost:8000/api/v1/copilot/sessions \
  -H "Content-Type: application/json" \
  -d '{}'

# 保存 session_id
SESSION_ID="xxx"

# 执行命令
curl -X POST "http://localhost:8000/api/v1/copilot/sessions/$SESSION_ID/commands" \
  -H "Content-Type: application/json" \
  -d '{"command": "create_patient", "params": {"name": "测试", "age": 30, "gender": "female"}}'
```

## 安全考虑

### 1. 权限验证
- 只有认证医生可执行命令
- 不同角色有不同权限（主治 > 住院 > 实习）

### 2. 操作审计
- 所有命令执行记录到审计日志
- 包含操作者、时间、命令、参数、结果

### 3. 数据安全
- 敏感操作需要二次确认（删除、导出大量数据）
- 患者隐私数据自动脱敏

### 4. 命令白名单
- 仅允许预定义的命令
- 防止命令注入攻击

## 性能优化

### 1. 异步执行
- 所有命令异步执行，不阻塞对话
- 长时间操作返回任务 ID，后台执行

### 2. 批量操作
- 支持批量创建、批量更新
- 减少数据库交互次数

### 3. 缓存
- 频繁查询的数据使用缓存
- 患者信息、报告列表等

## 后续扩展

### 计划命令

| 命令 | 功能 | 优先级 |
|------|------|--------|
| batch_create | 批量创建患者 | P1 |
| send_notification | 发送通知 | P1 |
| generate_statistics | 生成统计报表 | P2 |
| export_images | 导出影像数据 | P2 |
| schedule_surgery | 安排手术 | P3 |
| refer_patient | 转诊患者 | P3 |

### 智能增强

- **意图识别优化** - 使用微调模型提高识别准确率
- **上下文理解** - 记住多轮对话的上下文
- **主动建议** - 基于诊疗常规主动建议下一步操作
- **语音交互** - 集成语音识别和合成

## 相关文件

- `backend/app/services/copilot_service.py` - 核心服务实现
- `backend/app/routers/copilot.py` - API 路由
- `backend/scripts/copilot_commands_demo.py` - 演示脚本
- `docs/COPILOT_COMMAND_INTEGRATION.md` - 本文档

---

**文档版本**: v1.0  
**创建时间**: 2026-05-29  
**状态**: 已实现，待测试
