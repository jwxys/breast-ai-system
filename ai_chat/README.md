# Kimi K2.5 超声前问诊微调项目

本项目使用 Kimi K2.5 大模型进行 LoRA 微调，实现乳腺超声检查前的智能交互式问诊功能。

## 项目结构

```
ai_chat/
├── data/                           # 数据目录
│   ├── training_conversations.jsonl    # 训练数据集 (JSONL 格式)
│   └── ultrasound_inquiry_dataset/     # 原始数据集目录
├── scripts/                        # 脚本目录
│   └── finetune_kimi_k2.py         # 微调训练脚本
├── service.py                      # 问诊服务实现
├── requirements.txt                # Python 依赖
└── README.md                       # 本文件
```

## 功能特性

### 8 大脑问场景
1. **基本信息** - 称呼、年龄、联系方式
2. **主诉** - 主要症状、发现时间
3. **现病史** - 症状详细描述、疼痛程度
4. **既往史** - 乳腺疾病史、手术史、药物过敏
5. **家族史** - 乳腺疾病家族史
6. **月经生育史** - 月经周期、生育情况
7. **生活方式** - 作息、饮食、运动习惯
8. **检查准备** - 解释检查流程、注意事项

### 对话特点
- **医学准确性** - 专业医疗术语 + 通俗解释
- **人文关怀** - 同理心回应、缓解焦虑
- **自然流畅** - 像真实医生一样的对话风格
- **信息完整** - 系统收集必要医疗信息
- **隐私保护** - 不询问与检查无关的信息

## 快速开始

### 环境要求

- **GPU**: NVIDIA GPU ≥ 24GB 显存 (RTX 3090/4090, A10, A100 等)
- **CUDA**: 11.8 或 12.0+
- **Python**: 3.10+
- **显存需求**: 
  - 1.8-bit 量化版：~24GB
  - 4-bit 量化版：~28GB
  - 全精度版：~64GB

### 安装依赖

```bash
cd /workspace/breast-ai-system/ai_chat

# 安装依赖
pip install -r requirements.txt

# 验证安装
python -c "import torch; print(torch.cuda.is_available())"
```

### 下载 Kimi K2.5 模型

```bash
# 使用 HuggingFace CLI 下载 1.8-bit 量化版
pip install huggingface_hub

huggingface-cli download moonshot/Kimi-K2.5 \
    --revision unsloth-1.8bit \
    --local-dir /workspace/models/kimi-k2-5-1.8bit
```

**其他版本**：
- 4-bit 量化版：`--revision unsloth-4bit` (~28GB)
- 全精度版：`--revision main` (~64GB)

### 生成训练数据

训练数据已预置在 `data/training_conversations.jsonl`，包含 8 个场景 400+ 轮对话。

如需扩展数据集：

```bash
# 使用数据生成脚本
python scripts/generate_training_data.py --num-samples 500
```

### 开始微调

```bash
# 执行微调训练
python scripts/finetune_kimi_k2.py
```

**训练参数**（在脚本中配置）：
- `num_train_epochs`: 3-5 个 epoch
- `per_device_train_batch_size`: 2
- `learning_rate`: 2e-4
- `lora_r`: 16 (LoRA 秩)
- `max_seq_length`: 8192 (Kimi K2.5 支持超长上下文)

### 训练输出

训练完成后，模型保存在：
```
ai_chat/results/kimi-k2-inquiry/
├── adapter/                    # LoRA 适配器权重
│   ├── adapter_config.json
│   ├── adapter_model.safetensors
│   └── tokenizer files...
└── checkpoints/                # 训练检查点
```

## 集成到后端系统

### API 端点

微调后的模型通过以下 API 端点提供服务：

```bash
# 创建问诊会话
POST /api/v1/inquiry/sessions
Content-Type: application/json

{
  "patient_id": 123,
  "visit_id": 456
}

Response:
{
  "session_id": "uuid-string",
  "welcome_message": "您好！我是您的 AI 健康助手小樱...",
  "created_at": "2024-01-01T10:00:00"
}

# 发送消息
POST /api/v1/inquiry/sessions/{session_id}/messages
Content-Type: application/json

{
  "message": "我姓张，今年 35 岁"
}

Response:
{
  "session_id": "uuid-string",
  "response": "张女士您好！请问您今天主要是哪里不舒服来做检查呢？",
  "collected_fields": {
    "称呼": "张",
    "年龄": 35
  },
  "updated_at": "2024-01-01T10:01:00"
}

# 获取会话状态
GET /api/v1/inquiry/sessions/{session_id}

# 关闭会话
POST /api/v1/inquiry/sessions/{session_id}/close
```

### 服务配置

编辑 `backend/app/services/inquiry_service.py`：

```python
# 指定微调模型路径
service = InquiryService(
    model_path="ai_chat/results/kimi-k2-inquiry/adapter",
    use_default_model=False,  # 使用微调模型
)

# 或使用规则引擎降级方案（无 GPU 环境）
service = InquiryService(use_default_model=True)
```

## 推理示例

### Python 代码推理

```python
from unsloth import FastLanguageModel
import torch

# 加载微调后的模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="ai_chat/results/kimi-k2-inquiry/adapter",
    max_seq_length=4096,
    dtype=None,
    load_in_4bit=False,
)

FastLanguageModel.for_inference(model)

# 构建对话
messages = [
    {"role": "system", "content": "你是一名专业的乳腺超声检查前问诊助手..."},
    {"role": "user", "content": "你好，我今天要做乳腺超声检查"},
]

# 生成回复
inputs = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt",
).to("cuda")

outputs = model.generate(inputs, max_new_tokens=256)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

### API 调用示例

```bash
# 使用 curl 调用 API
curl -X POST http://localhost:8000/api/v1/inquiry/sessions \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'

# 保存返回的 session_id
SESSION_ID="your-session-id"

# 发送消息
curl -X POST "http://localhost:8000/api/v1/inquiry/sessions/$SESSION_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{"message": "我右边乳房摸到一个疙瘩"}'
```

## 数据格式说明

### 训练数据 JSONL 格式

```json
{
  "messages": [
    {"role": "user", "content": "你好，我今天要做乳腺超声检查"},
    {"role": "assistant", "content": "您好！欢迎来做乳腺超声检查..."},
    {"role": "user", "content": "我姓张"},
    {"role": "assistant", "content": "张女士您好！请问您今年多大年龄了？"}
  ],
  "metadata": {
    "scenario": "basic_info",
    "turn_count": 2
  }
}
```

**字段说明**：
- `messages`: 对话列表，按时间顺序排列
- `role`: 角色标识（user/assistant）
- `content`: 消息内容
- `metadata.scenario`: 对话场景类别
- `metadata.turn_count`: 对话轮次数

## 质量评估

### 数据质量 5 维度

1. **医学准确性** - 医学术语正确、病理描述准确
2. **对话自然性** - 流畅自然、符合真实医患对话
3. **信息完整性** - 完整收集必要医疗信息
4. **人文关怀** - 同理心回应、缓解患者焦虑
5. **隐私保护** - 不询问无关隐私信息

### 测试场景

```bash
# 运行测试脚本
python scripts/test_inquiry_flow.py
```

测试覆盖：
- 8 个场景的端到端对话
- 信息收集完整性验证
- 回复医学准确性检查
- 边界情况处理（中断、异常输入等）

## 故障排查

### 常见问题

#### 1. 显存不足

```
RuntimeError: CUDA out of memory
```

**解决方案**：
- 使用更低精度版本（1.8-bit → 4-bit）
- 减小 `per_device_train_batch_size`
- 减小 `max_seq_length`

#### 2. 模型下载失败

```
Error: Repository Not Found
```

**解决方案**：
- 确认 HuggingFace 账号有访问权限
- 使用 `huggingface-cli login` 登录
- 检查网络连接

#### 3. LoRA 适配器加载失败

```
ValueError: Model path does not exist
```

**解决方案**：
- 检查模型路径是否正确
- 确认训练脚本已成功完成
- 查看 `ai_chat/results/kimi-k2-inquiry/` 目录

## Docker 部署

使用 Docker Compose 一键部署：

```bash
cd /workspace/breast-ai-system/deploy/docker

# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f inquiry-service
```

## 性能优化

### 推理加速

1. **使用 vLLM** - 高性能推理框架
2. **批处理** - 合并多个请求
3. **缓存** - 重复查询缓存
4. **量化** - 使用 INT8/FP16 推理

### 显存优化

1. **梯度检查点** - 已启用
2. **8-bit AdamW** - 已配置
3. **LoRA 合并** - 推理时合并权重
4. **模型卸载** - CPU 卸载不活跃层

## 后续开发

- [ ] 增加更多问诊场景（术后随访、治疗咨询等）
- [ ] 集成语音识别（语音→文本→问诊）
- [ ] 多模态支持（超声图像 + 问诊联合推理）
- [ ] 知识图谱增强（症状 - 疾病关联推理）
- [ ] A/B 测试框架（不同模型版本对比）

## 参考资料

- [Kimi K2.5 官方文档](https://huggingface.co/moonshot/Kimi-K2.5)
- [Unsloth 框架文档](https://github.com/unslothai/unsloth)
- [LoRA 论文](https://arxiv.org/abs/2106.09685)
- [HuggingFace Trl 文档](https://huggingface.co/docs/trl)

## 许可证

本项目遵循 MIT 许可证。

## 联系方式

如有问题或建议，请联系：
- 项目负责人：[姓名]
- 邮箱：[email]
- 内部文档：[链接]
