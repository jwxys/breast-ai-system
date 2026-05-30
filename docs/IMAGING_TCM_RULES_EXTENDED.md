# 激进版：影像 - 中医病机关联规则（扩展版）

## 纳入的影像特征（扩展至 20+ 项）

### 1. 肿块形态学特征（8 项）

| 特征 | 取值 | 中医病机关联 | 权重 | 证据等级 |
|------|------|-------------|------|---------|
| **边界** | 清晰 | 痰湿凝结（偏 benign） | -0.2 | B |
| | 不清 | 瘀血内阻 | +0.4 | B |
| | 毛刺征 | 瘀毒互结 | +0.5 | B |
| | 角征/尖角 | 毒邪深陷 | +0.4 | C |
| **形态** | 规则（椭圆/圆） | 气滞为主 | +0.1 | B |
| | 不规则 | 气滞血瘀 | +0.3 | B |
| | 蟹足样 | 毒邪走窜 | +0.6 | C |
| **纵横比** | <1（平行生长） | 病位较浅 | +0.1 | C |
| | >1（垂直生长） | 毒邪内蕴深陷 | +0.4 | C |
| **边缘** | 光整 | 正气尚存 | -0.2 | C |
| | 模糊 | 痰瘀互结 | +0.3 | B |
| | 微分叶 | 气滞痰凝 | +0.2 | C |
| | 宏分叶 | 痰湿壅盛 | +0.3 | C |
| **包膜** | 完整 | 正气固摄 | -0.3 | C |
| | 不完整 | 正气亏虚 | +0.4 | C |
| | 无包膜 | 毒邪扩散 | +0.5 | C |

### 2. 内部回声特征（6 项）

| 特征 | 取值 | 中医病机关联 | 权重 | 证据等级 |
|------|------|-------------|------|---------|
| **回声类型** | 无回声（囊性） | 痰饮水湿 | +0.4 (phlegm) | B |
| | 低回声 | 血瘀/气滞 | +0.3 (stasis) | B |
| | 等回声 | 病机不显 | 0 | - |
| | 高回声 | 痰湿/脂肪 | +0.3 (phlegm) | C |
| **回声均匀度** | 均匀 | 病机单纯 | 0 | - |
| | 不均匀 | 痰瘀互结 | +0.3 | B |
| **钙化** | 无钙化 | - | 0 | - |
| | 粗大钙化 | 痰浊久凝 | +0.4 (phlegm) | B |
| | 点状微钙化 | 痰毒互结 | +0.5 (toxin) | B |
| | 簇状钙化 | 毒邪深重 | +0.6 (toxin) | B |
| | 弧形钙化 | 痰湿凝聚 | +0.3 (phlegm) | C |
| **液化坏死** | 无 | - | 0 | - |
| | 有 | 热毒炽盛，肉腐血败 | +0.6 (toxin) | C |

### 3. 血流动力学特征（4 项）

| 特征 | 取值 | 中医病机关联 | 权重 | 证据等级 |
|------|------|-------------|------|---------|
| **CDFI 分级** | 0 级（无血流） | 痰凝/阴寒 | +0.3 (phlegm) | C |
| | I 级（少量） | 轻度血瘀 | +0.2 (stasis) | C |
| | II 级（中等） | 血瘀明显 | +0.4 (stasis) | B |
| | III 级（丰富） | 热毒炽盛/血热 | +0.5 (toxin) | B |
| **血流分布** | 周边型 | 气滞血瘀（早期） | +0.3 (stasis) | C |
| | 穿入型 | 瘀血内阻（进展） | +0.5 (stasis) | B |
| | 网状型 | 热毒炽盛（晚期） | +0.6 (toxin) | C |
| **RI 阻力指数** | <0.7 | 病性偏良性 | -0.2 | C |
| | >0.7 | 瘀血/毒邪 | +0.3 (stasis/toxin) | C |

### 4. 弹性成像特征（2 项）

| 特征 | 取值 | 中医病机关联 | 权重 | 证据等级 |
|------|------|-------------|------|---------|
| **弹性评分** | 1-2 分（软） | 痰湿/气滞（偏实） | +0.2 (phlegm) | C |
| | 3 分（中等） | 气滞血瘀 | +0.3 (stasis) | B |
| | 4 分（硬） | 瘀毒内阻 | +0.5 (toxin) | B |
| | 5 分（很硬） | 毒邪深重 | +0.6 (toxin) | C |
| **硬度比** | <2.5 | 病性偏 benign | -0.2 | C |
| | >4.5 | 瘀毒深重 | +0.5 (toxin) | C |

### 5. 生长动力学特征（3 项）

| 特征 | 取值 | 中医病机关联 | 权重 | 证据等级 |
|------|------|-------------|------|---------|
| **生长速度** | 稳定（>1 年无变化） | 正气充足 | -0.3 (deficiency) | C |
| | 缓慢（倍增>300 天） | 痰湿凝结 | +0.3 (phlegm) | C |
| | 中等（100-300 天） | 正邪相争 | +0.2 (stasis) | C |
| | 快速（<100 天） | 热毒炽盛，正气不足 | +0.5 (toxin/deficiency) | C |
| **大小** | <1cm | 病位浅，邪气轻 | -0.2 | C |
| | 1-2cm | 病机中等 | 0 | - |
| | >3cm | 病深邪重 | +0.3 | C |
| **多灶性** | 单发 | 病机较单纯 | 0 | - |
| | 多发 | 痰瘀互结，病情复杂 | +0.3 (stasis/phlegm) | C |

---

## 规则引擎算法（激进阶）

### 权重计算公式

```python
# 基础分数（0-1）
score = Σ(feature_weight × evidence_modifier)

# 证据等级修正
evidence_modifier = {
    "A": 1.0,   # 多中心 RCT（暂无）
    "B": 0.8,   # 单中心对照研究
    "C": 0.6,   # 观察性研究/专家共识
}

# 最终倾向评分
tendency_score = min(1.0, base_score / max_possible_score)
```

### 病机倾向判定阈值

| 评分范围 | 倾向强度 | 临床意义 |
|---------|---------|---------|
| 0.0-0.3 | 轻度 | 可能相关，需进一步验证 |
| 0.3-0.5 | 中度 | 较明确，建议结合四诊 |
| 0.5-0.7 | 明显 | 高度提示，支持辨证 |
| 0.7-1.0 | 显著 | 强烈提示，重要参考 |

---

## 综合病机推导

### 基础病机组合

```python
# 主要病机（评分>0.5）
primary_pathomechanism = max(stasis, phlegm, toxin, deficiency)

# 次要病机（评分 0.3-0.5）
secondary_pathomechanism = [p for p in scores if 0.3 < p <= 0.5]

# 病机组合模式
patterns = {
    "stasis+phlegm": "痰瘀互结",
    "stasis+toxin": "瘀毒内阻",
    "phlegm+toxin": "痰毒互结",
    "stasis+phlegm+toxin": "痰瘀毒互结",
    "deficiency+stasis": "气虚血瘀",
    "deficiency+phlegm": "脾虚痰湿",
    "deficiency+toxin": "正虚毒盛",
}
```

### 病性虚实判断

```python
# 实证指标
excess_score = stasis + phlegm + toxin

# 虚证指标
deficiency_score = deficiency

# 虚实判断
if excess_score > deficiency_score * 2:
    nature = "实证为主"
elif deficiency_score > excess_score:
    nature = "虚证为主"
else:
    nature = "虚实夹杂"
```

---

## 示例计算

### 病例：典型恶性超声表现

```
超声特征：
┌────────────────────────────────────┐
│ 大小：2.3×1.8cm                    │
│ 边界：不清，有毛刺                   │
│ 形态：不规则                       │
│ 纵横比：1.4 (>1)                   │
│ 回声：低回声，不均匀                │
│ 钙化：点状微钙化（簇状）            │
│ CDFI: II 级（穿入型）                │
│ RI: 0.75                           │
│ 弹性评分：4 分                      │
│ 生长速度：中等（150 天倍增）          │
└────────────────────────────────────┘

逐项权重计算：
┌──────────────┬────────┬───────┬──────────┬──────────────┐
│ 特征          │ 取值    │ 权重   │ 证据修正  │ 贡献分数      │
├──────────────┼────────┼───────┼──────────┼──────────────┤
│ 边界          │ 毛刺    │ +0.5  │ B×0.8    │ stasis +0.40  │
│ 形态          │ 不规则  │ +0.3  │ B×0.8    │ stasis +0.24  │
│ 纵横比        │ >1     │ +0.4  │ C×0.6    │ toxin +0.24   │
│ 回声          │ 低回声  │ +0.3  │ B×0.8    │ stasis +0.24  │
│ 均匀度        │ 不均匀  │ +0.3  │ B×0.8    │ stasis +0.24  │
│ 钙化          │ 微钙化  │ +0.5  │ B×0.8    │ toxin +0.40   │
│ 血流分级      │ II 级    │ +0.4  │ B×0.8    │ stasis +0.32  │
│ 血流分布      │ 穿入型  │ +0.5  │ B×0.8    │ stasis +0.40  │
│ RI           │ >0.7   │ +0.3  │ C×0.6    │ stasis +0.18  │
│ 弹性评分      │ 4 分     │ +0.5  │ B×0.8    │ toxin +0.40   │
│ 生长速度      │ 中等    │ +0.2  │ C×0.6    │ stasis +0.12  │
└──────────────┴────────┴───────┴──────────┴──────────────┘

累加得分（原始）：
- stasis: 0.40+0.24+0.24+0.24+0.32+0.40+0.18+0.12 = 2.14
- phlegm: 0
- toxin: 0.24+0.40+0.40 = 1.04
- deficiency: 0

归一化（假设 max_possible=4.0）：
- stasis: 2.14/4.0 = 0.54 (明显)
- phlegm: 0 (无提示)
- toxin: 1.04/4.0 = 0.26 (轻度)
- deficiency: 0 (无提示)

综合判断：
主要病机：瘀血内阻（0.54）
次要病机：毒邪内蕴（0.26）
病机组合：瘀血为主，兼有毒邪
病性：实证（瘀血证明显）

建议治法：活血化瘀，解毒散结
参考方剂：血府逐瘀汤加减
```

---

## 实施注意事项

### 1. 权重 calibration

- 初始权重基于文献
- 需要临床数据校准
- 收集 300+ 病例进行回顾性验证
- 调整权重使与专家辨证一致性>0.6

### 2. 避免过度诊断

- 设置阈值：总分<0.3 时不显示病机倾向
- 标注"病机不显"
- 避免将所有病例都归为某病机

### 3. 动态更新

- 每 6 个月更新一次文献
- 新证据出现时调整权重
- 定期校准模型

---

## 代码实现框架

```python
class ImagingTCMRuleEngine:
    """影像 - 中医病机规则引擎"""
    
    # 证据等级修正系数
    EVIDENCE_MODIFIER = {
        "A": 1.0,
        "B": 0.8,
        "C": 0.6,
    }
    
    # 特征规则库
    FEATURE_RULES = {
        # 边界特征
        "boundary_spiculated": {
            "target": "stasis",
            "weight": 0.5,
            "evidence": "B",
            "description": "毛刺征 → 瘀毒互结"
        },
        "boundary_unclear": {
            "target": "stasis",
            "weight": 0.4,
            "evidence": "B",
            "description": "边界不清 → 瘀血内阻"
        },
        # 形态特征
        "morphology_irregular": {
            "target": "stasis",
            "weight": 0.3,
            "evidence": "B",
            "description": "形态不规则 → 气滞血瘀"
        },
        # ... (继续定义所有 20+ 项特征)
    }
    
    def calculate_tendencies(self, features: dict) -> dict:
        """计算病机倾向评分"""
        scores = {"stasis": 0.0, "phlegm": 0.0, "toxin": 0.0, "deficiency": 0.0}
        
        for feature_key, value in features.items():
            if value and feature_key in self.FEATURE_RULES:
                rule = self.FEATURE_RULES[feature_key]
                modifier = self.EVIDENCE_MODIFIER[rule["evidence"]]
                scores[rule["target"]] += rule["weight"] * modifier
        
        # 归一化
        max_score = self._calculate_max_possible_score(features)
        normalized = {k: min(1.0, v / max_score) for k, v in scores.items()}
        
        return normalized
    
    def interpret_results(self, scores: dict) -> TCMInterpretation:
        """解读结果"""
        primary = max(scores.items(), key=lambda x: x[1])
        secondary = [k for k, v in scores.items() if 0.3 < v <= 0.5 and k != primary[0]]
        
        # 病机组合
        pattern = self._identify_pattern(scores)
        
        # 虚实判断
        nature = self._determine_nature(scores)
        
        return TCMInterpretation(
            primary_pathomechanism=primary[0],
            primary_score=primary[1],
            secondary_pathomechanisms=secondary,
            pattern=pattern,
            nature=nature,
            recommendations=self._generate_recommendations(scores)
        )
```

---

**版本**: v2.0 (激进版)  
**特征数量**: 20+ 项  
**病机维度**: 4 个（瘀血/痰浊/毒邪/正虚）  
**证据等级**: B/C 级为主  
**状态**: 待实施
