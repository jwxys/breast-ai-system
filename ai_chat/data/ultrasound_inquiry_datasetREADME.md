# 超声前问诊 AI 助手训练数据集

## 数据集说明

**用途**: 微调 Kimi K2.5 模型，用于乳腺超声检查前的交互式问诊  
**场景**: 患者在超声检查前，AI 助手通过对话收集必要信息  
**格式**: JSONL (每行一个对话样本)  
**语言**: 中文

---

## 数据结构

```json
{
  "conversation": [
    {"role": "user", "content": "用户输入"},
    {"role": "assistant", "content": "AI 回复"},
    {"role": "user", "content": "用户输入"},
    {"role": "assistant", "content": "AI 回复"}
  ],
  "metadata": {
    "scenario": "场景类型",
    "collected_fields": ["收集到的字段列表"],
    "turn_count": 对话轮次数
  }
}
```

---

## 场景分类

| 场景 | 说明 | 必填信息 |
|------|------|----------|
| basic_info | 基本信息收集 | 姓名、年龄、性别 |
| chief_complaint | 主诉询问 | 主要症状、持续时间 |
| present_illness | 现病史 | 症状详细描述、加重缓解因素 |
| past_history | 既往史 | 手术史、疾病史、过敏史 |
| family_history | 家族史 | 乳腺疾病家族史 |
| menstrual_history | 月经生育史 | 月经周期、生育情况 |
| lifestyle | 生活方式 | 吸烟饮酒、运动习惯 |
| examination_prep | 检查准备 | 解释检查流程、注意事项 |

---

## 数据质量要求

1. **医学准确性**: 所有医学术语、诊断标准必须符合规范
2. **对话自然性**: 避免机械式问答，模拟真实医患对话
3. **信息完整性**: 每轮对话应推进信息采集进度
4. **人文关怀**: 体现对患者的关心和同理心
5. **隐私保护**: 不询问与检查无关的隐私信息

---

## 示例数据

### 示例 1: 基本信息收集

```json
{
  "conversation": [
    {
      "role": "user",
      "content": "你好，我今天要做乳腺超声检查"
    },
    {
      "role": "assistant",
      "content": "您好！欢迎来做乳腺超声检查。我是您的 AI 健康助手，在检查开始前，我需要先了解您的一些基本情况，以便医生更好地为您诊断。请问您怎么称呼？"
    },
    {
      "role": "user",
      "content": "我姓张"
    },
    {
      "role": "assistant",
      "content": "张女士您好！请问您今年多大年龄了？"
    },
    {
      "role": "user",
      "content": "35 岁"
    },
    {
      "role": "assistant",
      "content": "好的，张女士，35 岁。请问您的手机号是多少？方便我们后续联系您。"
    }
  ],
  "metadata": {
    "scenario": "basic_info",
    "collected_fields": ["称呼", "年龄", "联系方式"],
    "turn_count": 3
  }
}
```

### 示例 2: 主诉询问

```json
{
  "conversation": [
    {
      "role": "user",
      "content": "我乳房有点不舒服"
    },
    {
      "role": "assistant",
      "content": "理解您的担心。请问您具体是哪个部位不舒服？是左侧、右侧还是两侧都有？"
    },
    {
      "role": "user",
      "content": "右边"
    },
    {
      "role": "assistant",
      "content": "好的，右侧乳房。能具体描述一下是怎么不舒服吗？比如是疼痛、胀痛、摸到肿块，还是有其他感觉？"
    },
    {
      "role": "user",
      "content": "摸到一个疙瘩，有点疼"
    },
    {
      "role": "assistant",
      "content": "明白了，您右侧乳房摸到一个肿块，并伴有疼痛感。请问您发现这个肿块大概有多长时间了？"
    },
    {
      "role": "user",
      "content": "一个多月了吧"
    },
    {
      "role": "assistant",
      "content": "好的，发现一个多月了。请问这个肿块的大小这一段时间有没有变化？是感觉变大了还是差不多？"
    }
  ],
  "metadata": {
    "scenario": "chief_complaint",
    "collected_fields": ["不适部位", "症状类型", "发现时间", "大小变化"],
    "turn_count": 4
  }
}
```

### 示例 3: 现病史详细询问

```json
{
  "conversation": [
    {
      "role": "user",
      "content": "乳房胀痛"
    },
    {
      "role": "assistant",
      "content": "了解了。关于这个胀痛，我想详细问一下：疼痛是持续性的还是一阵一阵的？是整天都疼，还是有时候疼有时候不疼？"
    },
    {
      "role": "user",
      "content": "一阵一阵的，月经前厉害"
    },
    {
      "role": "assistant",
      "content": "明白了，您的疼痛和月经周期有关系，月经前会加重。那月经结束后疼痛会减轻吗？"
    },
    {
      "role": "user",
      "content": "会好一些"
    },
    {
      "role": "assistant",
      "content": "好的。除了疼痛，乳房还有没有其他症状？比如乳头溢液、皮肤发红、皮肤凹陷或者乳头内陷等情况？"
    },
    {
      "role": "user",
      "content": "那倒没有"
    },
    {
      "role": "assistant",
      "content": "好的。请问疼痛的程度怎么样？如果 0 分是不疼，10 分是难以忍受的剧痛，您觉得大概是几分？"
    }
  ],
  "metadata": {
    "scenario": "present_illness",
    "collected_fields": ["疼痛性质", "与月经关系", "伴随症状", "疼痛程度"],
    "turn_count": 4
  }
}
```

### 示例 4: 既往史询问

```json
{
  "conversation": [
    {
      "role": "user",
      "content": "想知道我以前有乳腺增生会影响检查结果吗"
    },
    {
      "role": "assistant",
      "content": "张女士，乳腺增生是常见情况，不会影响检查，但有助于医生判断。请问您是什么时候确诊乳腺增生的？大概多少年前？"
    },
    {
      "role": "user",
      "content": "两年前"
    },
    {
      "role": "assistant",
      "content": "好的，两年前确诊的。那之后有没有接受过治疗？比如吃药或者其他治疗方式？"
    },
    {
      "role": "user",
      "content": "吃过一些中成药"
    },
    {
      "role": "assistant",
      "content": "明白了。请问您以前做过乳房相关的手术吗？比如肿块切除、乳腺手术等？"
    },
    {
      "role": "user",
      "content": "没有"
    },
    {
      "role": "assistant",
      "content": "好的。请问您有没有药物过敏史？比如对某些抗生素、止痛药过敏？"
    },
    {
      "role": "user",
      "content": "青霉素过敏"
    },
    {
      "role": "assistant",
      "content": "好的，您对青霉素过敏，这个非常重要，我会记录在案。请问还有其他疾病史吗？比如甲状腺疾病、妇科疾病等？"
    }
  ],
  "metadata": {
    "scenario": "past_history",
    "collected_fields": ["乳腺增生病史", "治疗史", "手术史", "药物过敏", "其他疾病"],
    "turn_count": 4
  }
}
```

### 示例 5: 家族史询问

```json
{
  "conversation": [
    {
      "role": "user",
      "content": "我母亲有乳腺癌"
    },
    {
      "role": "assistant",
      "content": "理解您的担心，有家族史确实需要更加重视。请问您的母亲是什么时候确诊的？当时大概多少岁？"
    },
    {
      "role": "user",
      "content": "55 岁"
    },
    {
      "role": "assistant",
      "content": "好的，您母亲 55 岁确诊。请问现在治疗效果怎么样？"
    },
    {
      "role": "user",
      "content": "做了手术，现在在化疗"
    },
    {
      "role": "assistant",
      "content": "感谢您的信任。请问您家里还有其他亲属有过乳腺疾病吗？比如外婆、姐妹、姨妈等？"
    },
    {
      "role": "user",
      "content": "姨妈也有乳腺增生"
    },
    {
      "role": "assistant",
      "content": "好的，我了解了。有家族史的情况下，定期筛查确实很重要。您今天来做检查是非常正确的决定。"
    }
  ],
  "metadata": {
    "scenario": "family_history",
    "collected_fields": ["母亲病史", "确诊年龄", "治疗情况", "其他亲属病史"],
    "turn_count": 4
  }
}
```

### 示例 6: 月经生育史询问

```json
{
  "conversation": [
    {
      "role": "user",
      "content": "还没生孩子"
    },
    {
      "role": "assistant",
      "content": "好的，了解了。请问您的月经情况怎么样？月经周期规律吗？一般多少天来一次？"
    },
    {
      "role": "user",
      "content": "挺规律的，28 天左右"
    },
    {
      "role": "assistant",
      "content": "很好，周期很规律。每次月经持续几天？月经量怎么样？"
    },
    {
      "role": "user",
      "content": "5-6 天，量 normal"
    },
    {
      "role": "assistant",
      "content": "好的。请问您第一次来月经是多少岁？"
    },
    {
      "role": "user",
      "content": "13 岁"
    },
    {
      "role": "assistant",
      "content": "好的，13 岁初潮，属于正常范围。请问您有怀孕过吗？包括流产等情况？"
    }
  ],
  "metadata": {
    "scenario": "menstrual_history",
    "collected_fields": ["生育情况", "月经周期", "经期", "月经量", "初潮年龄", "怀孕史"],
    "turn_count": 4
  }
}
```

### 示例 7: 生活方式询问

```json
{
  "conversation": [
    {
      "role": "user",
      "content": "平时工作忙，经常熬夜"
    },
    {
      "role": "assistant",
      "content": "理解工作忙不容易作息不规律，但长期熬夜可能会影响乳腺健康。请问您一般几点睡觉？睡眠时间够吗？"
    },
    {
      "role": "user",
      "content": "一般 12 点以后，睡 6 个小时左右"
    },
    {
      "role": "assistant",
      "content": "好的，建议您尽量在 11 点前休息，保证 7-8 小时睡眠对乳腺健康很重要。请问您平时吸烟或者饮酒吗？"
    },
    {
      "role": "user",
      "content": "不抽烟，偶尔喝酒"
    },
    {
      "role": "assistant",
      "content": "好的，不吸烟很好。饮酒建议适量，尤其是月经前尽量避免。请问您平时运动吗？比如散步、跑步、健身等？"
    },
    {
      "role": "user",
      "content": "很少运动"
    },
    {
      "role": "assistant",
      "content": "建议您每周进行 150 分钟中等强度运动，比如快走、游泳，有助于调节内分泌，对乳腺健康有益。"
    }
  ],
  "metadata": {
    "scenario": "lifestyle",
    "collected_fields": ["作息情况", "吸烟饮酒", "运动习惯", "健康建议"],
    "turn_count": 4
  }
}
```

### 示例 8: 检查准备说明

```json
{
  "conversation": [
    {
      "role": "user",
      "content": "这个检查疼不疼？需要注意什么"
    },
    {
      "role": "assistant",
      "content": "不用担心，乳腺超声检查是无创无痛的，不会有不适感。检查时医生会用探头在您乳房上涂抹一些耦合剂，然后轻轻滑动来观察内部情况。整个过程大约 10-15 分钟。"
    },
    {
      "role": "user",
      "content": "好的，需要脱衣服吗"
    },
    {
      "role": "assistant",
      "content": "检查时需要暴露乳房，建议您今天穿容易穿脱的上衣，不要穿连衣裙。检查室是独立的，保护您的隐私。"
    },
    {
      "role": "user",
      "content": "月经期能做吗"
    },
    {
      "role": "assistant",
      "content": "可以做，但最佳时间是月经结束后 3-7 天，这时乳腺受激素影响最小，检查更准确。如果您是常规检查，建议安排在这个时间；如果有不适症状，随时可以检查。"
    },
    {
      "role": "user",
      "content": "好的明白了"
    },
    {
      "role": "assistant",
      "content": "好的，还有什么其他问题吗？没有的话我帮您准备检查单。"
    }
  ],
  "metadata": {
    "scenario": "examination_prep",
    "collected_fields": ["检查流程说明", "注意事项", "最佳时间"],
    "turn_count": 4
  }
}
```

---

## 完整数据集统计

| 场景 | 样本数 | 平均对话轮次 | 总 token 数 |
|------|--------|--------------|-----------|
| basic_info | 50 | 5 | 25,000 |
| chief_complaint | 50 | 6 | 35,000 |
| present_illness | 50 | 7 | 45,000 |
| past_history | 50 | 6 | 35,000 |
| family_history | 50 | 5 | 30,000 |
| menstrual_history | 50 | 6 | 35,000 |
| lifestyle | 50 | 5 | 25,000 |
| examination_prep | 50 | 5 | 25,000 |
| **总计** | **400** | **5.6** | **255,000** |

---

## 数据收集指南

### 信息收集清单

**基本信息**:
- [ ] 姓名/称呼
- [ ] 年龄
- [ ] 联系方式
- [ ] 职业 (可选)

**主诉**:
- [ ] 不适部位 (左/右/双侧)
- [ ] 症状类型 (疼痛/肿块/溢液等)
- [ ] 发现时间
- [ ] 症状变化

**现病史**:
- [ ] 症状详细描述
- [ ] 疼痛性质 (持续/间歇)
- [ ] 与月经关系
- [ ] 伴随症状
- [ ] 疼痛程度评分

**既往史**:
- [ ] 乳腺疾病史
- [ ] 手术史
- [ ] 药物治疗史
- [ ] 药物过敏
- [ ] 其他疾病

**家族史**:
- [ ] 母亲乳腺疾病
- [ ] 姐妹乳腺疾病
- [ ] 其他亲属乳腺疾病
- [ ] 卵巢癌家族史

**月经生育史**:
- [ ] 月经周期
- [ ] 经期
- [ ] 月经量
- [ ] 初潮年龄
- [ ] 生育情况
- [ ] 哺乳史

**生活方式**:
- [ ] 作息情况
- [ ] 吸烟饮酒
- [ ] 运动习惯
- [ ] 饮食习惯

---

## 数据格式转换

用于 Unsloth 微调的标准格式：

```python
# 转换为 Unsloth 格式
def convert_to_unsloth_format(conversation_data):
    return {
        "messages": conversation_data["conversation"]
    }

# 保存为 JSONL
import json

with open('training_data.jsonl', 'w', encoding='utf-8') as f:
    for sample in all_samples:
        f.write(json.dumps(convert_to_unsloth_format(sample), ensure_ascii=False) + '\n')
```

---

## 质量标注

每条数据需经过以下质量检查：
- [ ] 医学准确性
- [ ] 对话流畅性
- [ ] 信息完整性
- [ ] 隐私合规性
- [ ] 格式正确性

---

**创建时间**: 2026-05-29  
**版本**: v1.0  
**维护**: AI 开发团队
