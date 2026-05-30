#!/usr/bin/env python3
"""
Kimi K2.5 超声前问诊模型微调脚本

使用 Unsloth 进行高效 LoRA 微调
适用于单卡 GPU (24GB+ 显存)
"""

import os
import json
import torch
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path

# Unsloth 导入
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset


# ============ 配置类 ============
@dataclass
class FinetuneConfig:
    """微调配置"""
    
    # 模型配置
    model_name: str = "moonshot/Kimi-K2.5"
    model_revision: str = "unslot-h-1.8bit"  # 1.8-bit 量化版本
    max_seq_length: int = 8192  # Kimi K2.5支持超长上下文
    
    # LoRA 配置
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])
    
    # 训练配置
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    num_train_epochs: int = 3
    learning_rate: float = 2e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1
    lr_scheduler_type: str = "cosine"
    
    # 数据配置
    data_path: str = "ai_chat/data/training_conversations.jsonl"
    test_split_ratio: float = 0.1
    
    # 输出配置
    output_dir: str = "ai_chat/results/kimi-k2-inquiry"
    logging_steps: int = 10
    save_steps: int = 100
    
    # 硬件配置
    fp16: bool = not torch.cuda.is_bf16_supported()
    bf16: bool = torch.cuda.is_bf16_supported()


# ============ 主函数 ============
def main():
    """主函数"""
    print("=" * 70)
    print("Kimi K2.5 超声前问诊模型微调")
    print("=" * 70)
    
    # 1. 检查 GPU
    print("\n1️⃣ 检查 GPU 资源")
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"   ✅ GPU: {gpu_name}")
        print(f"   ✅ 显存：{gpu_memory:.1f} GB")
    else:
        print("   ❌ 未检测到 GPU，请确认环境配置")
        return
    
    # 2. 加载模型
    print("\n2️⃣ 加载 Kimi K2.5 模型")
    print("   ℹ️ 使用 1.8-bit 量化版本，显存需求约 24GB")
    
    config = FinetuneConfig()
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=config.model_name,
        max_seq_length=config.max_seq_length,
        dtype=None,  # 自动选择
        load_in_4bit=False,  # Unsloth 已量化
        revision=config.model_revision,
        trust_remote_code=True,
    )
    
    print("   ✅ 模型加载完成")
    
    # 3. 配置 LoRA
    print("\n3️⃣ 配置 LoRA 适配器")
    print(f"   - LoRA R 秩：{config.lora_r}")
    print(f"   - LoRA Alpha: {config.lora_alpha}")
    print(f"   - 目标模块：{', '.join(config.target_modules)}")
    
    model = FastLanguageModel.get_peft_model(
        model,
        r=config.lora_r,
        target_modules=config.target_modules,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        bias="none",
        use_gradient_checkpointing="unsloth",  # Unsloth 优化版本
        random_state=42,
    )
    
    print("   ✅ LoRA 配置完成")
    
    # 4. 加载数据集
    print("\n4️⃣ 加载训练数据")
    print(f"   数据路径：{config.data_path}")
    
    if not os.path.exists(config.data_path):
        print(f"   ❌ 数据文件不存在：{config.data_path}")
        print("   请先创建训练数据集")
        return
    
    # 加载 JSONL 数据集
    dataset = load_dataset(
        "json",
        data_files=config.data_path,
        split="train"
    )
    
    # 划分训练集和验证集
    dataset = dataset.train_test_split(test_size=config.test_split_ratio)
    
    print(f"   ✅ 训练集：{len(dataset['train'])} 条")
    print(f"   ✅ 验证集：{len(dataset['test'])} 条")
    
    # 5. 格式化数据集
    print("\n5️⃣ 格式化数据")
    
    def format_conversation(example):
        """格式化对话数据"""
        messages = example["messages"]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        return {"text": text}
    
    dataset = dataset.map(
        format_conversation,
        remove_columns=[col for col in dataset["train"].column_names if col not in ["messages"]],
        desc="格式化对话"
    )
    
    print("   ✅ 数据格式化完成")
    
    # 6. 训练配置
    print("\n6️⃣ 配置训练参数")
    
    training_args = TrainingArguments(
        output_dir=config.output_dir,
        per_device_train_batch_size=config.per_device_train_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        num_train_epochs=config.num_train_epochs,
        learning_rate=config.learning_rate,
        weight_decay=config.weight_decay,
        warmup_ratio=config.warmup_ratio,
        lr_scheduler_type=config.lr_scheduler_type,
        fp16=config.fp16,
        bf16=config.bf16,
        logging_steps=config.logging_steps,
        save_steps=config.save_steps,
        save_total_limit=3,
        report_to="none",  # 不报告到 wandb 等
        dataloader_num_workers=4,
        optim="adamw_8bit",  # 8-bit AdamW
    )
    
    # 7. 创建 Trainer
    print("\n7️⃣ 创建 Trainer")
    
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        dataset_text_field="text",
        max_seq_length=config.max_seq_length,
        dataset_num_proc=4,
        packing=False,  # Kimi K2.5 不支持 packing
        args=training_args,
    )
    
    print("   ✅ Trainer 创建完成")
    
    # 8. 开始训练
    print("\n8️⃣ 开始训练")
    print(f"   - 训练轮次：{config.num_train_epochs}")
    print(f"   - 批次大小：{config.per_device_train_batch_size}")
    print(f"   - 学习率：{config.learning_rate}")
    print(f"   - 输出目录：{config.output_dir}")
    print("-" * 70)
    
    try:
        # 显示 GPU 使用情况
        print("\n开始监控 GPU 使用情况:\n")
        
        trainer_stats = trainer.train()
        
        print("-" * 70)
        print("\n9️⃣ 训练完成")
        print(f"   训练时长：{trainer_stats.metrics['train_runtime']:.2f} 秒")
        print(f"   每秒样本：{trainer_stats.metrics['train_samples_per_second']:.2f}")
        print(f"   最终损失：{trainer_stats.metrics['train_loss']:.4f}")
        
    except KeyboardInterrupt:
        print("\n⚠️  训练被中断")
        return
    
    # 9. 保存模型
    print("\n🔟 保存模型")
    
    # 保存 LoRA 适配器
    adapter_path = os.path.join(config.output_dir, "adapter")
    model.save_pretrained(adapter_path)
    tokenizer.save_pretrained(adapter_path)
    print(f"   ✅ 适配器已保存：{adapter_path}")
    
    # 保存完整合并后的模型 (可选)
    print("\n💡 如需保存完整模型 (合并 LoRA)，使用以下命令:")
    print("""
from unsloth import FastLanguageModel
model, tokenizer = FastLanguageModel.from_pretrained("ai_chat/results/kimi-k2-inquiry/adapter")
model.save_pretrained_merged("ai_chat/results/kimi-k2-inquiry/merged")
""")
    
    # 10. 打印使用示例
    print("\n" + "=" * 70)
    print("📚 使用微调后的模型")
    print("=" * 70)
    
    inference_example = '''
from unsloth import FastLanguageModel

# 加载微调后的模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="ai_chat/results/kimi-k2-inquiry/adapter",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=False,
)

FastLanguageModel.for_inference(model)

# 测试对话
messages = [
    {"role": "user", "content": "你好，我今天要做乳腺超声检查"},
]

inputs = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt",
).to("cuda")

outputs = model.generate(inputs, max_new_tokens=512)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
'''
    
    print(inference_example)
    
    print("\n✅ 所有步骤完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
